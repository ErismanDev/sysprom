"""
Views para gerenciamento de Boletins Reservados
Sistema independente dos boletins ostensivos
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date
from .models import Publicacao
from .permissoes_simples import pode_acessar_boletins
from .filtros_hierarquicos import aplicar_filtro_hierarquico_publicacoes
from .permissoes import obter_funcao_atual


def atualizar_status_boletim_reservado(boletim):
    """Atualiza o status do boletim reservado baseado na hierarquia das assinaturas"""
    # Para boletins reservados, usar a mesma lógica dos ostensivos
    if boletim.tipo == 'BOLETIM_RESERVADO':
        # Verificar se tem assinatura de Editor Geral (mais alta hierarquia)
        if boletim.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists():
            boletim.status = 'EDITADA'
        # Se não tem Editor Geral, verificar Editor Adjunto
        elif boletim.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists():
            boletim.status = 'EDITADA'
        # Se não tem Editor Adjunto, verificar Editor Chefe
        elif boletim.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists():
            boletim.status = 'EDITADA'
        # Se não tem nenhuma assinatura, manter como rascunho
        else:
            boletim.status = 'RASCUNHO'
    else:
        # Para outros tipos de publicação, usar lógica original
        # Verificar se tem assinatura de edição (status mais recente)
        if boletim.assinaturas.filter(tipo_assinatura='EDICAO').exists():
            boletim.status = 'EM_EDICAO'
        # Se não tem edição, verificar se tem aprovação
        elif boletim.assinaturas.filter(tipo_assinatura='APROVACAO').exists():
            boletim.status = 'APROVADA'
        # Se não tem aprovação, verificar se tem revisão
        elif boletim.assinaturas.filter(tipo_assinatura='REVISAO').exists():
            boletim.status = 'REVISADA'
        # Se não tem nenhuma assinatura, manter como rascunho
        else:
            boletim.status = 'RASCUNHO'
    boletim.save()


@login_required
def boletins_reservados_list(request):
    """Listar apenas Boletins Reservados"""
    
    # Verificar se o usuário tem permissão para acessar boletins
    if not pode_acessar_boletins(request.user):
        messages.error(request, 'Você não tem permissão para acessar boletins. Apenas editores podem acessar este módulo.')
        return redirect('militares:militar_dashboard')
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Aplicar filtro hierárquico baseado no acesso da função
    if request.user.is_superuser:
        # Superusuário vê todas as publicações
        publicacoes = Publicacao.objects.filter(tipo='BOLETIM_RESERVADO', ativo=True)
    elif funcao_atual:
        # Aplicar filtro hierárquico
        publicacoes = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.filter(tipo='BOLETIM_RESERVADO', ativo=True),
            funcao_atual
        )
    else:
        # Usuário sem função definida - sem acesso
        messages.error(request, 'Você não possui função militar definida para acessar boletins.')
        return redirect('militares:militar_dashboard')
    
    # Filtros de busca
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    ano_filter = request.GET.get('ano', '')
    
    if search:
        publicacoes = publicacoes.filter(
            Q(numero__icontains=search) |
            Q(titulo__icontains=search) |
            Q(origem_publicacao__icontains=search)
        )
    
    if status_filter:
        publicacoes = publicacoes.filter(status=status_filter)
    
    if ano_filter:
        publicacoes = publicacoes.filter(data_boletim__year=ano_filter)
    
    # Ordenar por data de criação (mais recentes primeiro)
    publicacoes = publicacoes.order_by('-data_criacao')
    
    # Adicionar flags de assinatura para cada boletim
    for publicacao in publicacoes:
        publicacao.tem_assinatura_editor_chefe = publicacao.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
        publicacao.tem_assinatura_editor_adjunto = publicacao.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
        publicacao.tem_assinatura_editor_geral = publicacao.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
    
    # Estatísticas
    total_boletins = publicacoes.count()
    boletins_publicados = publicacoes.filter(status='PUBLICADA').count()
    boletins_rascunho = publicacoes.filter(status='RASCUNHO').count()
    
    # Anos disponíveis para filtro
    anos_disponiveis = Publicacao.objects.filter(
        tipo='BOLETIM_RESERVADO',
        ativo=True,
        data_boletim__isnull=False
    ).values_list('data_boletim__year', flat=True).distinct().order_by('-data_boletim__year')
    
    context = {
        'publicacoes': publicacoes,
        'total_boletins': total_boletins,
        'boletins_publicados': boletins_publicados,
        'boletins_rascunho': boletins_rascunho,
        'anos_disponiveis': anos_disponiveis,
        'search': search,
        'status_filter': status_filter,
        'ano_filter': ano_filter,
        'tipo_publicacao': 'BOLETIM_RESERVADO',
        'titulo_pagina': 'Boletins Reservados',
    }
    
    return render(request, 'militares/boletins_reservados/boletins_reservados_list.html', context)


@login_required
def boletins_reservados_create(request):
    """Criar novo Boletim Reservado automaticamente"""
    
    # Verificar permissão
    if not pode_acessar_boletins(request.user):
        messages.error(request, 'Você não tem permissão para criar boletins.')
        return redirect('militares:militar_dashboard')
    
    if request.method == 'POST':
        try:
            # Verificar se já existe um boletim reservado para o dia atual
            data_hoje = date.today()
            boletim_existente = Publicacao.objects.filter(
                tipo='BOLETIM_RESERVADO',
                data_boletim=data_hoje,
                ativo=True
            ).first()
            
            if boletim_existente:
                messages.warning(request, f'Já existe um Boletim Reservado para hoje ({data_hoje.strftime("%d/%m/%Y")}): {boletim_existente.numero}')
                return redirect('militares:boletins_reservados_list')
            
            # Criar boletim com dados automáticos e estrutura das 4 partes
            conteudo_inicial = '''<h2>Boletim Reservado do Corpo de Bombeiros Militar do Estado do Piauí</h2>

<h3>1ª PARTE - SERVIÇOS DIÁRIOS</h3>
<p>Conteúdo reservado dos serviços diários...</p>

<h3>2ª PARTE - INSTRUÇÃO</h3>
<p>Conteúdo reservado de instrução...</p>

<h3>3ª PARTE - ASSUNTOS GERAIS</h3>
<p>Conteúdo reservado de assuntos gerais...</p>

<h3>4ª PARTE - JUSTIÇA E DISCIPLINA</h3>
<p>Conteúdo reservado de justiça e disciplina...</p>'''
            
            # Obter origem da publicação baseada na função do usuário
            funcao_atual = obter_funcao_atual(request)
            origem = funcao_atual.orgao.nome if funcao_atual and funcao_atual.orgao else 'Comando Geral'
            
            # Criar o boletim
            boletim = Publicacao.objects.create(
                titulo=f'Boletim Reservado - {data_hoje.strftime("%d/%m/%Y")}',
                tipo='BOLETIM_RESERVADO',
                conteudo=conteudo_inicial,
                origem_publicacao=origem,
                data_boletim=data_hoje,
                status='RASCUNHO',
                criado_por=request.user,
                ativo=True
            )
            
            messages.success(request, f'Boletim Reservado {boletim.numero} criado com sucesso!')
            return redirect('militares:boletim_reservado_detail', pk=boletim.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar boletim reservado: {str(e)}')
            return redirect('militares:boletins_reservados_list')
    
    # Para GET, criar o boletim automaticamente
    try:
        # Verificar se já existe um boletim reservado para o dia atual
        data_hoje = date.today()
        boletim_existente = Publicacao.objects.filter(
            tipo='BOLETIM_RESERVADO',
            data_boletim=data_hoje,
            ativo=True
        ).first()
        
        if boletim_existente:
            messages.warning(request, f'Já existe um Boletim Reservado para hoje ({data_hoje.strftime("%d/%m/%Y")}): {boletim_existente.numero}')
            return redirect('militares:boletim_reservado_detail', pk=boletim_existente.pk)
        
        # Criar boletim com dados automáticos e estrutura das 4 partes
        conteudo_inicial = '''<h2>Boletim Reservado do Corpo de Bombeiros Militar do Estado do Piauí</h2>

<h3>1ª PARTE - SERVIÇOS DIÁRIOS</h3>
<p>Conteúdo reservado dos serviços diários...</p>

<h3>2ª PARTE - INSTRUÇÃO</h3>
<p>Conteúdo reservado de instrução...</p>

<h3>3ª PARTE - ASSUNTOS GERAIS</h3>
<p>Conteúdo reservado de assuntos gerais...</p>

<h3>4ª PARTE - JUSTIÇA E DISCIPLINA</h3>
<p>Conteúdo reservado de justiça e disciplina...</p>'''
        
        # Obter origem da publicação baseada na função do usuário
        funcao_atual = obter_funcao_atual(request)
        origem = funcao_atual.orgao.nome if funcao_atual and funcao_atual.orgao else 'Comando Geral'
        
        # Criar o boletim
        boletim = Publicacao.objects.create(
            titulo=f'Boletim Reservado - {data_hoje.strftime("%d/%m/%Y")}',
            tipo='BOLETIM_RESERVADO',
            conteudo=conteudo_inicial,
            origem_publicacao=origem,
            data_boletim=data_hoje,
            status='RASCUNHO',
            criado_por=request.user,
            ativo=True
        )
        
        messages.success(request, f'Boletim Reservado {boletim.numero} criado com sucesso!')
        return redirect('militares:boletim_reservado_detail', pk=boletim.pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao criar boletim reservado: {str(e)}')
        return redirect('militares:boletins_reservados_list')


@login_required
def boletim_reservado_detail(request, pk):
    """Detalhes do Boletim Reservado"""
    
    # Verificar permissão
    if not pode_acessar_boletins(request.user):
        messages.error(request, 'Você não tem permissão para acessar boletins.')
        return redirect('militares:militar_dashboard')
    
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_RESERVADO', ativo=True)
    
    # Verificar acesso hierárquico
    funcao_atual = obter_funcao_atual(request)
    if not request.user.is_superuser and funcao_atual:
        publicacoes_filtradas = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.filter(pk=pk),
            funcao_atual
        )
        if not publicacoes_filtradas.exists():
            messages.error(request, 'Você não tem permissão para acessar este boletim.')
            return redirect('militares:boletins_reservados_list')
    
    # Buscar notas reservadas disponíveis para incluir no boletim
    notas_disponiveis = Publicacao.objects.filter(
        tipo='NOTA_RESERVADA',
        status='PUBLICADA',
        ativo=True,
        boletim_reservado__isnull=True  # Notas que ainda não foram incluídas em boletim
    ).order_by('-data_publicacao')
    
    # Aplicar filtro hierárquico nas notas disponíveis
    if not request.user.is_superuser and funcao_atual:
        notas_disponiveis = aplicar_filtro_hierarquico_publicacoes(notas_disponiveis, funcao_atual)
    
    # Notas já incluídas no boletim
    notas_incluidas = boletim.notas_incluidas_reservadas.all()
    
    # Adicionar flags de assinatura para o boletim
    boletim.tem_assinatura_editor_chefe = boletim.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
    boletim.tem_assinatura_editor_adjunto = boletim.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
    boletim.tem_assinatura_editor_geral = boletim.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
    
    context = {
        'boletim': boletim,
        'notas_disponiveis': notas_disponiveis,
        'notas_incluidas': notas_incluidas,
        'tipo_publicacao': 'BOLETIM_RESERVADO',
    }
    
    return render(request, 'militares/boletins_reservados/boletim_reservado_detail.html', context)


@login_required
def adicionar_nota_boletim_reservado(request, boletim_pk, nota_pk):
    """Adicionar nota reservada ao boletim reservado"""
    
    if not pode_acessar_boletins(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    try:
        boletim = get_object_or_404(Publicacao, pk=boletim_pk, tipo='BOLETIM_RESERVADO')
        nota = get_object_or_404(Publicacao, pk=nota_pk, tipo='NOTA_RESERVADA')
        
        # Verificar se a nota já está no boletim
        if nota in boletim.notas_incluidas_reservadas.all():
            return JsonResponse({'success': False, 'message': 'Nota já está incluída no boletim'})
        
        # Adicionar a nota ao boletim
        boletim.notas_incluidas_reservadas.add(nota)
        
        return JsonResponse({'success': True, 'message': 'Nota adicionada ao boletim com sucesso'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


@login_required
def remover_nota_boletim_reservado(request, boletim_pk, nota_pk):
    """Remover nota reservada do boletim reservado"""
    
    if not pode_acessar_boletins(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    try:
        boletim = get_object_or_404(Publicacao, pk=boletim_pk, tipo='BOLETIM_RESERVADO')
        nota = get_object_or_404(Publicacao, pk=nota_pk, tipo='NOTA_RESERVADA')
        
        # Remover a nota do boletim
        boletim.notas_incluidas_reservadas.remove(nota)
        
        return JsonResponse({'success': True, 'message': 'Nota removida do boletim com sucesso'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


@login_required
def disponibilizar_boletim_reservado(request, pk):
    """Disponibilizar boletim reservado para visualização"""
    if request.method == 'POST':
        try:
            from .models import AssinaturaNota
            
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_RESERVADO')
            
            # Verificar se já foi disponibilizado
            if boletim.data_disponibilizacao:
                messages.warning(request, 'Este boletim já foi disponibilizado!')
                return redirect('militares:boletins_reservados_list')
            
            # Verificar se o boletim tem as 3 assinaturas necessárias
            assinaturas = AssinaturaNota.objects.filter(nota=boletim)
            
            tem_editor_chefe = assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
            tem_editor_adjunto = assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
            tem_editor_geral = assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
            
            # Contar quantos editores assinaram
            editores_assinados = sum([tem_editor_chefe, tem_editor_adjunto, tem_editor_geral])
            
            if editores_assinados < 3:
                messages.error(request, f'Boletim deve ser assinado pelos 3 editores antes de ser disponibilizado! Assinaturas atuais: {editores_assinados}/3')
                return redirect('militares:boletins_reservados_list')
            
            # Definir data de disponibilização
            boletim.data_disponibilizacao = timezone.localtime(timezone.now())
            boletim.save(update_fields=['data_disponibilizacao'])
            
            messages.success(request, f'Boletim Reservado {boletim.numero} disponibilizado com sucesso!')
            return redirect('militares:boletins_reservados_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_reservados_list')
        except Exception as e:
            messages.error(request, f'Erro ao disponibilizar boletim: {str(e)}')
            return redirect('militares:boletins_reservados_list')
    
    return redirect('militares:boletins_reservados_list')


@login_required
def retornar_boletim_reservado(request, pk):
    """Retornar boletim reservado de disponibilizado para aguardando (apenas superusuários)"""
    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem executar esta ação!')
        return redirect('militares:boletins_reservados_list')
    
    if request.method == 'POST':
        try:
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_RESERVADO')
            
            # Verificar se foi disponibilizado
            if not boletim.data_disponibilizacao:
                messages.warning(request, 'Este boletim não foi disponibilizado!')
                return redirect('militares:boletins_reservados_list')
            
            # Retornar para aguardando
            boletim.data_disponibilizacao = None
            boletim.save(update_fields=['data_disponibilizacao'])
            
            messages.success(request, f'Boletim Reservado {boletim.numero} retornado para aguardando!')
            return redirect('militares:boletins_reservados_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_reservados_list')
        except Exception as e:
            messages.error(request, f'Erro ao retornar boletim: {str(e)}')
            return redirect('militares:boletins_reservados_list')
    
    return redirect('militares:boletins_reservados_list')


@login_required
def deletar_boletim_reservado(request, pk):
    """Deletar boletim reservado (apenas superusuários)"""
    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem executar esta ação!')
        return redirect('militares:boletins_reservados_list')
    
    if request.method == 'POST':
        try:
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_RESERVADO')
            numero_boletim = boletim.numero
            
            # Deletar boletim
            boletim.delete()
            
            messages.success(request, f'Boletim Reservado {numero_boletim} deletado com sucesso!')
            return redirect('militares:boletins_reservados_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_reservados_list')
        except Exception as e:
            messages.error(request, f'Erro ao deletar boletim: {str(e)}')
            return redirect('militares:boletins_reservados_list')
    
    return redirect('militares:boletins_reservados_list')


@login_required
def boletim_reservado_visualizar(request, pk):
    """Visualizar boletim reservado (versão final)"""
    
    # Verificar permissão
    if not pode_acessar_boletins(request.user):
        messages.error(request, 'Você não tem permissão para visualizar boletins.')
        return redirect('militares:militar_dashboard')
    
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_RESERVADO')
    
    # Verificar acesso hierárquico
    funcao_atual = obter_funcao_atual(request)
    if not request.user.is_superuser and funcao_atual:
        publicacoes_filtradas = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.filter(pk=pk),
            funcao_atual
        )
        if not publicacoes_filtradas.exists():
            messages.error(request, 'Você não tem permissão para visualizar este boletim.')
            return redirect('militares:boletins_reservados_list')
    
    # Gerar conteúdo final do boletim com as notas incluídas
    conteudo_final = boletim.gerar_conteudo_final_reservado()
    
    context = {
        'boletim': boletim,
        'conteudo_final': conteudo_final,
        'tipo_publicacao': 'BOLETIM_RESERVADO',
    }
    
    return render(request, 'militares/boletins_reservados/boletim_reservado_visualizar.html', context)


# AJAX Views
@login_required
def ajax_verificar_boletim_reservado_hoje(request):
    """Verificar se já existe boletim reservado para hoje"""
    
    if not pode_acessar_boletins(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    data_hoje = date.today()
    boletim_existente = Publicacao.objects.filter(
        tipo='BOLETIM_RESERVADO',
        data_boletim=data_hoje,
        ativo=True
    ).first()
    
    if boletim_existente:
        return JsonResponse({
            'success': True,
            'existe': True,
            'numero': boletim_existente.numero,
            'url': f'/militares/boletins-reservados/{boletim_existente.pk}/'
        })
    
    return JsonResponse({'success': True, 'existe': False})


@login_required
def ajax_proximo_numero_boletim_reservado(request):
    """Obter próximo número de boletim reservado"""
    
    if not pode_acessar_boletins(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    try:
        ano_atual = date.today().year
        
        # Buscar último boletim reservado do ano
        ultimo_boletim = Publicacao.objects.filter(
            tipo='BOLETIM_RESERVADO',
            numero__endswith=f'/{ano_atual}',
            ativo=True
        ).order_by('-numero').first()
        
        if ultimo_boletim:
            # Extrair número e incrementar
            numero_atual = int(ultimo_boletim.numero.split('/')[0])
            proximo_numero = numero_atual + 1
        else:
            proximo_numero = 1
        
        numero_formatado = f"{proximo_numero:03d}/{ano_atual}"
        
        return JsonResponse({
            'success': True,
            'numero': numero_formatado
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


@login_required
def ajax_notas_disponiveis_boletim_reservado(request, boletim_pk):
    """Obter notas reservadas disponíveis para o boletim"""
    
    if not pode_acessar_boletins(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    try:
        boletim = get_object_or_404(Publicacao, pk=boletim_pk, tipo='BOLETIM_RESERVADO')
        
        # Buscar notas reservadas disponíveis
        notas_disponiveis = Publicacao.objects.filter(
            tipo='NOTA_RESERVADA',
            status='PUBLICADA',
            ativo=True,
            boletim_reservado__isnull=True
        ).order_by('-data_publicacao')
        
        # Aplicar filtro hierárquico
        funcao_atual = obter_funcao_atual(request)
        if not request.user.is_superuser and funcao_atual:
            notas_disponiveis = aplicar_filtro_hierarquico_publicacoes(notas_disponiveis, funcao_atual)
        
        notas_data = []
        for nota in notas_disponiveis:
            notas_data.append({
                'id': nota.id,
                'numero': nota.numero,
                'titulo': nota.titulo,
                'data_publicacao': nota.data_publicacao.strftime('%d/%m/%Y %H:%M') if nota.data_publicacao else 'N/A',
                'origem': nota.origem_publicacao or 'N/A'
            })
        
        return JsonResponse({
            'success': True,
            'notas': notas_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


@login_required
def ajax_notas_incluidas_boletim_reservado(request, boletim_pk):
    """Obter notas reservadas incluídas no boletim"""
    
    if not pode_acessar_boletins(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    try:
        boletim = get_object_or_404(Publicacao, pk=boletim_pk, tipo='BOLETIM_RESERVADO')
        
        notas_incluidas = boletim.notas_incluidas_reservadas.all().order_by('-data_publicacao')
        
        notas_data = []
        for nota in notas_incluidas:
            notas_data.append({
                'id': nota.id,
                'numero': nota.numero,
                'titulo': nota.titulo,
                'conteudo': nota.conteudo or '',
                'topicos': nota.topicos or '',
                'data_publicacao': nota.data_publicacao.strftime('%d/%m/%Y %H:%M') if nota.data_publicacao else 'N/A',
                'origem': nota.origem_publicacao or 'N/A'
            })
        
        return JsonResponse({
            'success': True,
            'notas': notas_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


@login_required
def ajax_boletins_reservados_disponiveis(request):
    """Obter boletins reservados disponibilizados"""
    
    if not pode_acessar_boletins(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    try:
        boletins = Publicacao.objects.filter(
            tipo='BOLETIM_RESERVADO',
            data_disponibilizacao__isnull=False,
            ativo=True
        ).order_by('-data_disponibilizacao')[:10]
        
        boletins_data = []
        for boletim in boletins:
            boletins_data.append({
                'id': boletim.id,
                'numero': boletim.numero,
                'titulo': boletim.titulo,
                'data_disponibilizacao': boletim.data_disponibilizacao.strftime('%d/%m/%Y %H:%M'),
                'notas_count': boletim.notas_incluidas_reservadas.count()
            })
        
        return JsonResponse({
            'success': True,
            'boletins': boletins_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


# ==================== VIEWS DE ASSINATURA ====================

@login_required
def dados_assinatura_boletim_reservado(request, pk):
    """Obter dados para assinatura do boletim reservado"""
    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_RESERVADO')
        
        # Obter função atual do usuário (opcional)
        try:
            funcao_atual = obter_funcao_atual(request)
        except Exception:
            funcao_atual = None
        
        # Buscar funções do usuário que podem assinar
        from .models import UsuarioFuncaoMilitar
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True
        ).select_related('funcao_militar')
        
        funcoes_data = []
        for funcao in funcoes_usuario:
            funcoes_data.append({
                'id': funcao.id,
                'nome': funcao.funcao_militar.nome,
                'publicacao': funcao.funcao_militar.publicacao,
                'nivel': funcao.funcao_militar.nivel,
            })
        
        # Buscar assinaturas existentes
        assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
        assinaturas_data = []
        for assinatura in assinaturas:
            assinaturas_data.append({
                'id': assinatura.id,
                'assinado_por': assinatura.assinado_por.get_full_name(),
                'tipo_assinatura': assinatura.get_tipo_assinatura_display(),
                'data_assinatura': assinatura.data_assinatura.isoformat(),
                'funcao_assinatura': assinatura.funcao_assinatura or 'N/A',
                'observacoes': assinatura.observacoes or '',
            })
        
        # Dados do boletim
        boletim_data = {
            'id': boletim.id,
            'numero': boletim.numero,
            'titulo': boletim.titulo,
            'status': boletim.get_status_display(),
            'data_criacao': boletim.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'criado_por': boletim.criado_por.get_full_name() if boletim.criado_por else 'Sistema',
            'conteudo': boletim.conteudo or '',
            'topicos': boletim.topicos or '',
        }
        
        return JsonResponse({
            'success': True,
            'boletim': boletim_data,
            'funcoes_usuario': funcoes_data,
            'assinaturas': assinaturas_data,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})


@login_required
def assinaturas_boletim_reservado(request, pk):
    """Página de assinaturas do boletim reservado"""
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_RESERVADO')
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Buscar funções do usuário que podem assinar
    from .models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        ativo=True
    ).select_related('funcao_militar')
    
    # Buscar assinaturas existentes
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    context = {
        'boletim': boletim,
        'funcao_atual': funcao_atual,
        'funcoes_usuario': funcoes_usuario,
        'assinaturas': assinaturas,
    }
    
    return render(request, 'militares/boletins_reservados/assinaturas_boletim_reservado.html', context)


@login_required
def assinar_boletim_reservado(request, pk):
    """Assinar boletim reservado"""
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_RESERVADO')
    
    if request.method == 'POST':
        try:
            # Verificar se é requisição JSON
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
                funcao_id = data.get('funcao_id')
                tipo_assinatura = data.get('tipo_assinatura')
                observacoes = data.get('observacoes', '')
                tipo_midia = data.get('tipo_midia', 'FISICA')
                
                # Dados para assinatura eletrônica
                hash_documento = data.get('hash_documento')
                timestamp = data.get('timestamp')
                assinatura_digital = data.get('assinatura_digital')
                certificado = data.get('certificado')
            else:
                funcao_id = request.POST.get('funcao_id')
                tipo_assinatura = request.POST.get('tipo_assinatura')
                observacoes = request.POST.get('observacoes', '')
                tipo_midia = request.POST.get('tipo_midia', 'FISICA')
                
                # Dados para assinatura física
                assinatura_fisica = request.FILES.get('assinatura_fisica')
            
            if not funcao_id or not tipo_assinatura or funcao_id == 'undefined':
                return JsonResponse({
                    'success': False,
                    'message': 'Função e tipo de assinatura são obrigatórios!'
                })
            
            # Buscar a função do usuário
            from .models import UsuarioFuncaoMilitar
            funcao_usuario = get_object_or_404(UsuarioFuncaoMilitar, id=funcao_id, usuario=request.user)
            
            # Verificar se já existe assinatura deste tipo para este usuário
            from .models import AssinaturaNota
            assinatura_existente = AssinaturaNota.objects.filter(
                nota=boletim,
                assinado_por=request.user,
                tipo_assinatura=tipo_assinatura
            ).first()
            
            if assinatura_existente:
                return JsonResponse({
                    'success': False,
                    'message': f'Você já assinou este boletim como {assinatura_existente.get_tipo_assinatura_display()}!'
                })
            
            # Criar assinatura
            assinatura = AssinaturaNota.objects.create(
                nota=boletim,
                assinado_por=request.user,
                tipo_assinatura=tipo_assinatura,
                funcao_assinatura=funcao_usuario.funcao_militar.nome,
                observacoes=observacoes,
                tipo_midia=tipo_midia,
                assinatura_fisica=assinatura_fisica if 'assinatura_fisica' in locals() else None,
                hash_documento=hash_documento,
                timestamp=timestamp,
                assinatura_digital=assinatura_digital,
                certificado=certificado,
            )
            
            # Atualizar status do boletim
            atualizar_status_boletim_reservado(boletim)
            
            return JsonResponse({
                'success': True,
                'message': f'Boletim assinado com sucesso como {assinatura.get_tipo_assinatura_display()}!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao assinar boletim: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido!'
    })


@login_required
def retirar_assinatura_boletim_reservado(request, pk, assinatura_pk):
    """Retirar assinatura do boletim reservado"""
    boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_RESERVADO')
    
    try:
        from .models import AssinaturaNota
        assinatura = get_object_or_404(AssinaturaNota, pk=assinatura_pk, nota=boletim)
        
        # Verificar se o usuário pode retirar a assinatura (apenas o próprio usuário ou superusuário)
        if assinatura.assinado_por != request.user and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para retirar esta assinatura!'
            })
        
        # Deletar assinatura
        assinatura.delete()
        
        # Atualizar status do boletim
        atualizar_status_boletim_reservado(boletim)
        
        return JsonResponse({
            'success': True,
            'message': 'Assinatura retirada com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao retirar assinatura: {str(e)}'
        })


@login_required
def devolver_nota_reservada(request, pk):
    """Devolver nota de um boletim para rascunho com justificativa"""
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
    from django.http import JsonResponse
    from django.db import transaction
    from .models import Publicacao, AssinaturaNota, HistoricoDevolucaoNota
    
    # Buscar a nota (tipo NOTA)
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se a nota está em um boletim disponibilizado
    if nota.numero_boletim or nota.numero_boletim_reservado:
        # Verificar se é boletim ostensivo disponibilizado
        if nota.numero_boletim:
            boletim = Publicacao.objects.filter(
                numero=nota.numero_boletim,
                tipo='BOLETIM_OSTENSIVO'
            ).first()
            
            if boletim and boletim.data_disponibilizacao:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': 'Esta nota não pode ser devolvida pois o boletim já foi disponibilizado.'
                    }, status=403)
                try:
                    messages.error(request, 'Esta nota não pode ser devolvida pois o boletim já foi disponibilizado.')
                except:
                    pass
                return redirect('militares:nota_detail', pk=nota.pk)
        
        # Verificar se é boletim reservado disponibilizado
        if nota.boletim_reservado:
            boletim = nota.boletim_reservado
            
            if boletim and boletim.data_disponibilizacao:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'error': 'Esta nota não pode ser devolvida pois o boletim já foi disponibilizado.'
                    }, status=403)
                try:
                    messages.error(request, 'Esta nota não pode ser devolvida pois o boletim já foi disponibilizado.')
                except:
                    pass
                return redirect('militares:nota_detail', pk=nota.pk)
    
    # Verificar se o usuário tem permissão para devolver a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para devolver esta nota.'
            }, status=403)
        try:
            messages.error(request, 'Você não tem permissão para devolver esta nota.')
        except:
            pass  # Se o middleware de mensagens não estiver disponível
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_devolucao = request.POST.get('motivo_devolucao', '').strip()
        
        if not motivo_devolucao:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo da devolução é obrigatório.'
                })
            try:
                messages.error(request, 'Motivo da devolução é obrigatório.')
            except:
                pass  # Se o middleware de mensagens não estiver disponível
            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            with transaction.atomic():
                # Contar assinaturas antes de remover
                assinaturas_removidas = AssinaturaNota.objects.filter(nota=nota).count()
                
                # Remover todas as assinaturas da nota
                AssinaturaNota.objects.filter(nota=nota).delete()
                
                # Devolver a nota para rascunho e remover do boletim
                nota.status = 'RASCUNHO'
                nota.ativo = True
                nota.numero_boletim = None  # Limpar número do boletim ostensivo
                nota.numero_boletim_reservado = None  # Limpar número do boletim reservado
                nota.boletim_reservado = None  # Remover do boletim reservado
                nota.editada_apos_devolucao = False  # Resetar flag de edição
                nota.save()
                
                # Salvar histórico da devolução
                HistoricoDevolucaoNota.objects.create(
                    nota=nota,
                    devolvido_por=request.user,
                    motivo_devolucao=motivo_devolucao,
                    assinaturas_removidas=assinaturas_removidas
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} devolvida para rascunho com sucesso! {assinaturas_removidas} assinatura(s) removida(s).'
                })
            
            try:
                messages.success(request, f'Nota {nota.numero} devolvida para rascunho com sucesso! {assinaturas_removidas} assinatura(s) removida(s).')
            except:
                pass  # Se o middleware de mensagens não estiver disponível
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao devolver nota: {str(e)}'
                }, status=500)
            
            try:
                messages.error(request, f'Erro ao devolver nota: {str(e)}')
            except:
                pass  # Se o middleware de mensagens não estiver disponível
            return redirect('militares:nota_detail', pk=nota.pk)
    
    # Se não for POST, mostrar formulário
    context = {
        'nota': nota,
    }
    return render(request, 'militares/devolver_nota.html', context)