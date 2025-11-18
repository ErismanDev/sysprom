#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views para o módulo de Publicações
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Publicacao, TituloPublicacaoConfig, Orgao, GrandeComando, Unidade, SubUnidade, AnexoNota
from .forms import PublicacaoForm
from .permissoes_simples import pode_acessar_configuracoes, pode_acessar_publicacoes


def redirect_to_correct_list(tipo_publicacao):
    """Redireciona para a lista correta baseada no tipo da publicação"""
    tipo_redirect_map = {
        'NOTA': 'militares:notas_list',
        'BOLETIM_OSTENSIVO': 'militares:boletins_ostensivos_list',
        'BOLETIM_RESERVADO': 'militares:boletins_reservados_list',
        'BOLETIM_ESPECIAL': 'militares:boletins_especiais_list',
        'AVISO': 'militares:avisos_list',
        'ORDEM_SERVICO': 'militares:ordens_servico_list',
    }
    
    # Se não encontrar o tipo, redireciona para notas como padrão
    return redirect(tipo_redirect_map.get(tipo_publicacao, 'militares:notas_list'))


# View publicacoes_list removida - usar listas específicas por tipo


@login_required
def publicacao_create(request, tipo=None):
    """Criar nova publicação"""
    
    # Verificar se o usuário tem permissão para criar publicações
    from .permissoes_simples import pode_criar_publicacoes
    
    if not pode_criar_publicacoes(request.user):
        messages.error(request, 'Você não tem permissão para criar publicações. Apenas funções com permissão de publicação podem acessar este módulo.')
        return redirect('militares:dashboard')
    
    # Definir tipos válidos
    tipos_validos = ['nota', 'boletim-ostensivo', 'boletim-reservado', 'boletim-especial', 'aviso', 'ordem-servico']
    
    if tipo and tipo not in tipos_validos:
        messages.error(request, 'Tipo de publicação inválido.')
        return redirect('militares:notas_list')
    
    # Mapear tipo da URL para tipo do modelo
    tipo_mapping = {
        'nota': 'NOTA',
        'boletim-ostensivo': 'BOLETIM_OSTENSIVO',
        'boletim-reservado': 'BOLETIM_RESERVADO',
        'boletim-especial': 'BOLETIM_ESPECIAL',
        'aviso': 'AVISO',
        'ordem-servico': 'ORDEM_SERVICO',
    }
    
    if request.method == 'POST':
        form = PublicacaoForm(request.POST)
        
        if form.is_valid():
            try:
                publicacao = form.save(commit=False)
                publicacao.criado_por = request.user
                
                # Definir tipo como NOTA (fixo)
                publicacao.tipo = 'NOTA'
                
                # O número será gerado automaticamente pelo método save() do modelo
                
                # Processar origem da publicação
                origem_publicacao = request.POST.get('origem_publicacao', '')
                if origem_publicacao:
                    publicacao.origem_publicacao = origem_publicacao
                
                # Processar tópicos se fornecidos
                topicos = request.POST.get('topicos', '')
                if topicos:
                    publicacao.topicos = topicos
                
                publicacao.save()
                
                # Se for uma requisição AJAX (criação via modal), retornar JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Nota criada com sucesso!',
                        'nota_id': publicacao.id,
                        'redirect_url': '/militares/notas/'
                    })
                
                messages.success(request, 'Publicação criada com sucesso!')
                # Redirecionar para a lista correta baseada no tipo
                return redirect_to_correct_list(publicacao.tipo)
            except Exception as e:
                print(f"Erro ao salvar publicação: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Se for uma requisição AJAX, retornar JSON com erro
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Erro ao salvar publicação: {str(e)}'
                    })
                
                messages.error(request, f'Erro ao salvar publicação: {str(e)}')
        else:
            # Log dos erros do formulário para debug
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            
            error_text = f'Erro ao criar publicação. Verifique os dados informados. Erros: {", ".join(error_messages)}'
            print(f"Erro de validação do formulário: {error_text}")
            
            # Se for uma requisição AJAX, retornar JSON com erro
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_text
                })
            
            messages.error(request, error_text)
    else:
        form = PublicacaoForm()
        
        # Pré-preencher origem baseada na lotação atual do militar (opcional - pode ser alterada)
        try:
            from militares.models import Militar, Lotacao
            
            # Buscar o militar associado ao usuário
            militar = Militar.objects.filter(user=request.user).first()
            
            if militar:
                # Buscar a lotação ativa do militar
                lotacao_atual = Lotacao.objects.filter(
                    militar=militar, 
                    status='ATUAL', 
                    ativo=True
                ).first()
                
                if lotacao_atual:
                    # Construir origem baseada na lotação atual do militar
                    def construir_origem_organograma(item, tipo):
                        if tipo == 'ORGAO':
                            return f"{item.nome}"
                        elif tipo == 'GRANDE_COMANDO':
                            return f"{item.orgao.nome} | {item.nome}"
                        elif tipo == 'UNIDADE':
                            return f"{item.grande_comando.orgao.nome} | {item.grande_comando.nome} | {item.nome}"
                        elif tipo == 'SUBUNIDADE':
                            return f"{item.unidade.grande_comando.orgao.nome} | {item.unidade.grande_comando.nome} | {item.nome} | {item.nome}"
                        return item.nome
                
                    # Determinar a origem baseada na lotação atual (apenas como sugestão)
                    origem_preenchida = ""
                    if lotacao_atual.orgao:
                        origem_preenchida = construir_origem_organograma(lotacao_atual.orgao, 'ORGAO')
                    elif lotacao_atual.grande_comando:
                        origem_preenchida = construir_origem_organograma(lotacao_atual.grande_comando, 'GRANDE_COMANDO')
                    elif lotacao_atual.unidade:
                        origem_preenchida = construir_origem_organograma(lotacao_atual.unidade, 'UNIDADE')
                    elif lotacao_atual.sub_unidade:
                        origem_preenchida = construir_origem_organograma(lotacao_atual.sub_unidade, 'SUBUNIDADE')
                
                    if origem_preenchida:
                        form.fields['origem_publicacao'].initial = origem_preenchida
        except Exception as e:
            print(f"Erro ao pré-preencher origem: {e}")
    
        # Buscar organizações para o dropdown
        from .models import Orgao, GrandeComando, Unidade, SubUnidade
        
        orgaos = Orgao.objects.filter(ativo=True).order_by('ordem', 'nome')
        grandes_comandos = GrandeComando.objects.filter(ativo=True).order_by('orgao__ordem', 'orgao__nome', 'ordem', 'nome')
        unidades = Unidade.objects.filter(ativo=True).order_by('grande_comando__orgao__ordem', 'grande_comando__orgao__nome', 'grande_comando__ordem', 'grande_comando__nome', 'ordem', 'nome')
        subunidades = SubUnidade.objects.filter(ativo=True).order_by('unidade__grande_comando__orgao__ordem', 'unidade__grande_comando__orgao__nome', 'unidade__grande_comando__ordem', 'unidade__grande_comando__nome', 'unidade__ordem', 'unidade__nome', 'ordem', 'nome')
    
    # Determinar o tipo de display baseado no tipo
    tipo_display_mapping = {
        'nota': 'Nova Nota',
        'boletim-ostensivo': 'Novo Boletim Ostensivo',
        'boletim-reservado': 'Novo Boletim Reservado',
        'boletim-especial': 'Novo Boletim Especial',
        'aviso': 'Novo Aviso',
        'ordem-servico': 'Nova Ordem de Serviço',
    }
    
    tipo_display = tipo_display_mapping.get(tipo, 'Nova Publicação')
    
    context = {
        'form': form,
        'tipo': tipo,
        'tipo_display': tipo_display,
        'orgaos': orgaos,
        'grandes_comandos': grandes_comandos,
        'unidades': unidades,
        'subunidades': subunidades,
    }
    
    return render(request, 'militares/publicacao_form.html', context)


@login_required
def publicacao_edit(request, pk):
    """Editar publicação"""
    publicacao = get_object_or_404(Publicacao, pk=pk)
    
    # Verificar permissões
    if not publicacao.can_edit(request.user):
        messages.error(request, 'Você não tem permissão para editar esta publicação.')
        return redirect('militares:publicacoes_list')
    
    if request.method == 'POST':
        form = PublicacaoForm(request.POST, instance=publicacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicação atualizada com sucesso!')
            return redirect('militares:publicacoes_list')
    else:
        form = PublicacaoForm(instance=publicacao)
    
    context = {
        'form': form,
        'publicacao': publicacao,
    }
    
    return render(request, 'militares/publicacao_form.html', context)


@login_required
def publicacao_detail(request, pk):
    """Visualizar detalhes da publicação"""
    publicacao = get_object_or_404(Publicacao, pk=pk)
    
    # Adicionar permissões ao contexto
    can_edit = publicacao.can_edit(request.user)
    can_publish = publicacao.can_publish(request.user)
    
    context = {
        'publicacao': publicacao,
        'can_edit': can_edit,
        'can_publish': can_publish,
    }
    
    return render(request, 'militares/publicacao_detail.html', context)


@login_required
def nota_detail(request, pk):
    """Visualizar detalhes da nota"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário pode visualizar a nota baseado no status
    can_view = True
    is_militar_indexado = False
    
    # Verificar se o usuário é um militar indexado nesta nota
    if hasattr(request.user, 'militar') and request.user.militar:
        is_militar_indexado = nota.militares_indexados.filter(id=request.user.militar.id).exists()
    
    # Se a nota não está publicada, verificar permissões especiais
    if nota.status != 'PUBLICADA':
        # Superusuários sempre podem visualizar
        if request.user.is_superuser:
            can_view = True
        # Usuários com permissão de edição podem visualizar
        elif nota.can_edit(request.user):
            can_view = True
        # Usuários com permissão de publicação podem visualizar
        elif nota.can_publish(request.user):
            can_view = True
        # Criador da nota pode visualizar
        elif nota.criado_por == request.user:
            can_view = True
        # Militares indexados podem visualizar
        elif is_militar_indexado:
            can_view = True
        # NOVO: Qualquer usuário autenticado pode visualizar modelos de notas
        elif nota.titulo and 'MODELO' in nota.titulo.upper():
            can_view = True
        # Operadores de planejadas podem visualizar notas para copiar links
        elif request.user.is_authenticated:
            from .permissoes_simples import obter_funcao_militar_ativa
            funcao_usuario = obter_funcao_militar_ativa(request.user)
            if funcao_usuario and funcao_usuario.funcao_militar.publicacao == 'OPERADOR_PLANEJADAS':
                can_view = True
            else:
                can_view = False
        else:
            can_view = False
    
    if not can_view:
        from django.contrib import messages
        messages.error(request, f'Você não tem permissão para visualizar esta nota. Apenas notas publicadas podem ser visualizadas por todos os usuários.')
        return redirect('militares:notas_list')
    
    # Adicionar permissões ao contexto
    can_edit = nota.can_edit(request.user)
    can_publish = nota.can_publish(request.user)
    
    # Militares indexados podem apenas visualizar, não editar
    # A edição é feita apenas por usuários com funções militares apropriadas
    
    context = {
        'nota': nota,
        'can_edit': can_edit,
        'can_publish': can_publish,
        'is_militar_indexado': is_militar_indexado,
    }
    
    return render(request, 'militares/nota_detail.html', context)


@login_required
def nota_edit(request, pk):
    """Editar nota"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se a nota está publicada e se o boletim foi disponibilizado
    if nota.status == 'PUBLICADA':
        # Verificar se o boletim foi disponibilizado
        boletim = None
        if nota.numero_boletim:
            boletim = Publicacao.objects.filter(
                tipo='BOLETIM_OSTENSIVO',
                numero=nota.numero_boletim
            ).first()
        
        if boletim and boletim.data_disponibilizacao:
            messages.error(request, 'Esta nota não pode mais ser editada pois o boletim já foi disponibilizado.')
            return redirect('militares:nota_detail', pk=nota.pk)
        else:
            # Nota publicada, mas boletim ainda não foi disponibilizado - permitir edição
            pass
    else:
        # Nota não publicada - permitir edição
        pass
    
    # Verificar permissões de edição (apenas usuários com funções militares apropriadas)
    can_edit = nota.can_edit(request.user)
    
    if not can_edit and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para editar esta nota. Apenas usuários com funções militares apropriadas podem editar.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    
    if request.method == 'POST':
        form = PublicacaoForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            
            # Atualizar conteúdo do boletim se a nota estiver publicada
            if nota.status == 'PUBLICADA' and nota.numero_boletim:
                boletim = Publicacao.objects.filter(
                    tipo='BOLETIM_OSTENSIVO',
                    numero=nota.numero_boletim
                ).first()
                
                if boletim:
                    boletim.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim)
                    boletim.save(update_fields=['conteudo'])
                else:
                    # Boletim não encontrado - continuar normalmente
                    pass
            
            messages.success(request, 'Nota atualizada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
    else:
        form = PublicacaoForm(instance=nota)
    
    context = {
        'form': form,
        'nota': nota,
    }
    
    return render(request, 'militares/nota_form.html', context)




@login_required
def nota_delete(request, pk):
    """Excluir nota"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se a nota está publicada
    if nota.status == 'PUBLICADA':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Notas publicadas não podem ser excluídas.'
            }, status=403)
        messages.error(request, 'Notas publicadas não podem ser excluídas.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if not nota.can_edit(request.user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para excluir esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para excluir esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        try:
            nota_titulo = nota.titulo
            nota.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota "{nota_titulo}" excluída com sucesso!'
                })
            
            messages.success(request, 'Nota excluída com sucesso!')
            return redirect('militares:notas_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao excluir nota: {str(e)}'
                }, status=500)
            
            messages.error(request, f'Erro ao excluir nota: {str(e)}')
            return redirect('militares:nota_detail', pk=nota.pk)
    
    context = {
        'nota': nota,
    }
    
    return render(request, 'militares/nota_confirm_delete.html', context)


@login_required
def publicacao_publish(request, pk):
    """Publicar publicação"""
    publicacao = get_object_or_404(Publicacao, pk=pk)
    
    if not publicacao.can_edit(request.user):
        messages.error(request, 'Você não tem permissão para publicar esta publicação.')
        return redirect_to_correct_list(publicacao.tipo)
    
    if request.method == 'POST':
        publicacao.status = 'PUBLICADO'
        publicacao.data_publicacao = timezone.now()
        publicacao.publicado_por = request.user
        publicacao.save()
        
        messages.success(request, 'Publicação publicada com sucesso!')
        return redirect_to_correct_list(publicacao.tipo)
    
    context = {
        'publicacao': publicacao,
    }
    
    return render(request, 'militares/publicacao_confirm_publish.html', context)


@login_required
def publicacao_delete(request, pk):
    """Excluir publicação"""
    publicacao = get_object_or_404(Publicacao, pk=pk)
    
    if not publicacao.can_edit(request.user):
        messages.error(request, 'Você não tem permissão para excluir esta publicação.')
        # Redirecionar para a lista correta baseada no tipo
        return redirect_to_correct_list(publicacao.tipo)
    
    if request.method == 'POST':
        # Se for um boletim, voltar as notas para EM_EDICAO antes de excluir
        if publicacao.tipo == 'BOLETIM_OSTENSIVO':
            notas_no_boletim = Publicacao.objects.filter(
                tipo='NOTA',
                numero_boletim=publicacao.numero
            )
            
            # Atualizar status das notas para EM_EDICAO
            notas_atualizadas = 0
            for nota in notas_no_boletim:
                nota.status = 'EM_EDICAO'
                nota.numero_boletim = None  # Remover referência ao boletim
                nota.save(update_fields=['status', 'numero_boletim'])
                notas_atualizadas += 1
            
            if notas_atualizadas > 0:
                messages.info(request, f'{notas_atualizadas} nota(s) foram devolvidas para edição.')
        
        publicacao.delete()
        messages.success(request, 'Publicação excluída com sucesso!')
        # Redirecionar para a lista correta baseada no tipo
        return redirect_to_correct_list(publicacao.tipo)
    
    context = {
        'publicacao': publicacao,
    }
    
    return render(request, 'militares/publicacao_confirm_delete.html', context)


# ==================== VIEWS ESPECÍFICAS POR TIPO ====================

@login_required
def notas_list(request):
    """Listar apenas Notas com filtro hierárquico baseado no acesso da função"""
    
    # Verificar se o usuário tem permissão para acessar notas
    from .permissoes_simples import pode_acessar_publicacoes
    
    if not pode_acessar_publicacoes(request.user):
        messages.error(request, 'Você não tem permissão para acessar as notas. Apenas funções com permissão de publicação podem acessar este módulo.')
        return redirect('militares:militar_dashboard')
    
    # Buscar dados para o modal
    from .models import Unidade, SubUnidade, GrandeComando, Orgao, TituloPublicacaoConfig
    from .filtros_hierarquicos import aplicar_filtro_hierarquico_notas
    from .permissoes_simples import obter_funcao_militar_ativa
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_militar_ativa(request.user)
    
    
    # Obter parâmetros de filtro
    origem = request.GET.get('origem')
    numero_nota = request.GET.get('numero_nota')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    hierarquia_id = request.GET.get('hierarquia')
    
    # Parâmetros de pesquisa avançada
    pesquisa_origem_dropdown = request.GET.get('pesquisa_origem_dropdown', '')
    pesquisa_titulo = request.GET.get('pesquisa_titulo', '')
    pesquisa_numero = request.GET.get('pesquisa_numero', '')
    pesquisa_data_inicial = request.GET.get('pesquisa_data_inicial', '')
    pesquisa_data_final = request.GET.get('pesquisa_data_final', '')
    pesquisa_status = request.GET.get('pesquisa_status', '')
    pesquisa_tipo_boletim = request.GET.get('pesquisa_tipo_boletim', '')
    
    # Remover filtros hierárquicos - manter apenas pesquisa por origem
    
    # Remover lógica de filtros hierárquicos
    
    
    # Remover lógica de filtros hierárquicos
    
    
    titulos_publicacao = TituloPublicacaoConfig.objects.filter(ativo=True).order_by('titulo')
    
    # Aplicar filtro hierárquico baseado no acesso da função
    from django.db.models import Case, When, Value, CharField, Prefetch, Q
    from django.db.models.functions import Coalesce
    
    # QuerySet base para notas
    publicacoes_base = Publicacao.objects.all()
    
    # Verificar se há filtro de origem - se houver, usar filtro completo
    tem_filtro_origem = bool(origem)
    
    # Aplicar filtro hierárquico baseado no acesso da função
    # Verificar se há filtros de pesquisa ativos
    tem_filtros_pesquisa = any([
        pesquisa_origem_dropdown and pesquisa_origem_dropdown.strip(),
        pesquisa_titulo and pesquisa_titulo.strip(),
        pesquisa_numero and pesquisa_numero.strip(),
        pesquisa_data_inicial and pesquisa_data_inicial.strip(),
        pesquisa_data_final and pesquisa_data_final.strip(),
        pesquisa_status and pesquisa_status.strip(),
        pesquisa_tipo_boletim and pesquisa_tipo_boletim.strip()
    ])
    
    
    
    
    
    # Aplicar filtros hierárquicos baseado na presença de filtros de pesquisa
    if request.user.is_superuser:
        # Superusuário vê todas as notas (ostensivas e reservadas)
        publicacoes = publicacoes_base.filter(tipo__in=['NOTA', 'NOTA_RESERVADA'], ativo=True)
    elif funcao_atual:
        # Verificar se há filtro de origem específico selecionado
        origem_selecionada = request.GET.get('pesquisa_origem_dropdown', '').strip()
        
        if origem_selecionada:
            # Se há origem selecionada no filtro, mostrar apenas notas dessa origem específica
            from .filtros_hierarquicos_pesquisa import aplicar_filtro_hierarquico_notas_especifico
            publicacoes = aplicar_filtro_hierarquico_notas_especifico(publicacoes_base, funcao_atual, request.user, origem_selecionada)
        else:
            # Sem filtro específico, usar filtro restritivo (apenas o próprio nível)
            from .filtros_hierarquicos_pesquisa import aplicar_filtro_hierarquico_notas_restritivo
            publicacoes = aplicar_filtro_hierarquico_notas_restritivo(publicacoes_base, funcao_atual, request.user)
    else:
        # Se não há função ativa, mostrar apenas notas do próprio usuário
        publicacoes = publicacoes_base.filter(
            tipo__in=['NOTA', 'NOTA_RESERVADA'], 
            ativo=True,
            criado_por=request.user
        )
        
    # Aplicar filtros adicionais
    status = request.GET.get('status')
    tipo_publicacao = request.GET.get('tipo_publicacao')
    
    if status:
        publicacoes = publicacoes.filter(status=status)
    
    # Filtro por tipo de publicação
    if tipo_publicacao:
        publicacoes = publicacoes.filter(tipo_publicacao=tipo_publicacao)
        
    # Filtro por origem (destino) - filtro básico
    if origem and origem.strip():
        # Filtrar por origem específica (busca exata)
        origem_limpa = origem.strip()
        
        # Buscar exatamente a origem selecionada
        publicacoes = publicacoes.filter(origem_publicacao__iexact=origem_limpa)
        
    # Filtro por número da nota
    if numero_nota and numero_nota.strip():
        numero_pesquisa = numero_nota.strip()
        try:
            # Tentar converter para inteiro se for um número simples
            numero_int = int(numero_pesquisa)
            # Buscar por número exato ou com formato 001/2024
            publicacoes = publicacoes.filter(
                Q(numero=f"{numero_int:03d}") |  # Busca exata: "001"
                Q(numero__startswith=f"{numero_int:03d}/") |  # Busca: "001/2024"
                Q(numero__icontains=numero_pesquisa)  # Busca parcial
            )
        except ValueError:
            # Se não for um número, buscar como string (incluindo formato 001/2024)
            publicacoes = publicacoes.filter(numero__icontains=numero_pesquisa)
    
    # Filtro por data de início - filtro básico
    if data_inicio and data_inicio.strip():
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio.strip(), '%Y-%m-%d').date()
            publicacoes = publicacoes.filter(data_criacao__date__gte=data_inicio_obj)
        except ValueError:
            messages.warning(request, f'Data de início inválida: {data_inicio}. Use o formato YYYY-MM-DD.')
        
    # Filtro por data de fim - filtro básico
    if data_fim and data_fim.strip():
        try:
            from datetime import datetime
            data_fim_obj = datetime.strptime(data_fim.strip(), '%Y-%m-%d').date()
            publicacoes = publicacoes.filter(data_criacao__date__lte=data_fim_obj)
        except ValueError:
            messages.warning(request, f'Data de fim inválida: {data_fim}. Use o formato YYYY-MM-DD.')
    
    # Validação adicional para filtros básicos de data
    if (data_inicio and data_inicio.strip() and 
        data_fim and data_fim.strip()):
        try:
            data_inicio_obj = datetime.strptime(data_inicio.strip(), '%Y-%m-%d').date()
            data_fim_obj = datetime.strptime(data_fim.strip(), '%Y-%m-%d').date()
            if data_inicio_obj > data_fim_obj:
                messages.warning(request, 'A data de início não pode ser maior que a data de fim.')
        except ValueError:
            pass
    
    # Aplicar filtros de pesquisa avançada
    
    if pesquisa_origem_dropdown and pesquisa_origem_dropdown.strip():
        # Filtrar por origem específica (busca exata)
        origem_selecionada = pesquisa_origem_dropdown.strip()
        
        # Buscar exatamente a origem selecionada
        publicacoes = publicacoes.filter(origem_publicacao__iexact=origem_selecionada)
    
    if pesquisa_titulo and pesquisa_titulo.strip():
        publicacoes = publicacoes.filter(titulo__icontains=pesquisa_titulo.strip())
    
    
    if pesquisa_numero and pesquisa_numero.strip():
        numero_pesquisa = pesquisa_numero.strip()
        try:
            # Tentar converter para inteiro se for um número simples
            numero_int = int(numero_pesquisa)
            # Buscar por número exato ou com formato 001/2024
            publicacoes = publicacoes.filter(
                Q(numero=f"{numero_int:03d}") |  # Busca exata: "001"
                Q(numero__startswith=f"{numero_int:03d}/") |  # Busca: "001/2024"
                Q(numero__icontains=numero_pesquisa)  # Busca parcial
            )
        except ValueError:
            # Se não for um número, buscar como string (incluindo formato 001/2024)
            publicacoes = publicacoes.filter(numero__icontains=numero_pesquisa)
    
    if pesquisa_data_inicial and pesquisa_data_inicial.strip():
        try:
            from datetime import datetime
            data_inicial_obj = datetime.strptime(pesquisa_data_inicial.strip(), '%Y-%m-%d').date()
            publicacoes = publicacoes.filter(data_criacao__date__gte=data_inicial_obj)
        except ValueError:
            messages.warning(request, f'Data inicial inválida: {pesquisa_data_inicial}. Use o formato YYYY-MM-DD.')
    
    if pesquisa_data_final and pesquisa_data_final.strip():
        try:
            from datetime import datetime
            data_final_obj = datetime.strptime(pesquisa_data_final.strip(), '%Y-%m-%d').date()
            publicacoes = publicacoes.filter(data_criacao__date__lte=data_final_obj)
        except ValueError:
            messages.warning(request, f'Data final inválida: {pesquisa_data_final}. Use o formato YYYY-MM-DD.')
    
    if pesquisa_status and pesquisa_status.strip():
        publicacoes = publicacoes.filter(status=pesquisa_status.strip())
    
    if pesquisa_tipo_boletim and pesquisa_tipo_boletim.strip():
        publicacoes = publicacoes.filter(tipo_publicacao=pesquisa_tipo_boletim.strip())
    
    
    # Validação adicional: se ambas as datas estão preenchidas, verificar se data inicial <= data final
    if (pesquisa_data_inicial and pesquisa_data_inicial.strip() and 
        pesquisa_data_final and pesquisa_data_final.strip()):
        try:
            data_inicial_obj = datetime.strptime(pesquisa_data_inicial.strip(), '%Y-%m-%d').date()
            data_final_obj = datetime.strptime(pesquisa_data_final.strip(), '%Y-%m-%d').date()
            if data_inicial_obj > data_final_obj:
                messages.warning(request, 'A data inicial não pode ser maior que a data final.')
        except ValueError:
            pass
    
    # Aplicar ordenação priorizando status das notas
    # Ordem de prioridade: devolvidas > rascunho > revisadas > aprovadas > editadas > publicadas
    from django.db.models import Case, When, BooleanField, Value, IntegerField
    
    publicacoes = publicacoes.annotate(
        is_devolvida=Case(
            When(
                assinaturas__isnull=True,
                status='RASCUNHO',
                editada_apos_devolucao=False,
                # Verificar se tem histórico de devolução para confirmar que é realmente devolvida
                historicos_devolucao__isnull=False,
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField()
        ),
        status_priority=Case(
            # Em edição (prioridade 1)
            When(status='EM_EDICAO', then=Value(1)),
            # Aprovadas (prioridade 2)
            When(status='APROVADA', then=Value(2)),
            # Revisadas (prioridade 3)
            When(status='REVISADA', then=Value(3)),
            # Notas devolvidas (prioridade 4 - antes dos rascunhos normais)
            When(
                assinaturas__isnull=True,
                status='RASCUNHO',
                editada_apos_devolucao=False,
                historicos_devolucao__isnull=False,
                then=Value(4)
            ),
            # Rascunhos normais (prioridade 5 - apenas os que NÃO são devolvidas)
            When(
                status='RASCUNHO',
                then=Value(5)
            ),
            # Editadas (prioridade 6)
            When(status='EDITADA', then=Value(6)),
            # Publicadas (prioridade 7)
            When(status='PUBLICADA', then=Value(7)),
            # Arquivadas (prioridade 8)
            When(status='ARQUIVADA', then=Value(8)),
            # Outros status
            default=Value(9),
            output_field=IntegerField()
        )
    ).distinct().order_by('status_priority', '-data_criacao')
    
    # Estatísticas já foram calculadas antes do union (se aplicável)
    if not hasattr(locals(), 'stats'):
        stats = {
            'total': 0,
            'publicadas': 0,
            'editadas': 0,
            'aprovadas': 0,
            'revisadas': 0,
            'rascunhos': 0,
            'arquivadas': 0,
        }
    
    # Paginação
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
        if per_page not in [5, 10, 20, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    paginator = Paginator(publicacoes, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Adicionar can_publish individual para cada publicação
    for publicacao in page_obj:
        publicacao.can_publish = publicacao.can_publish(request.user)
    
    # Verificar se o usuário tem permissão de EDITOR para mostrar botão de publicação
    can_publish = False
    if funcao_atual and funcao_atual.funcao_militar:
        can_publish = funcao_atual.funcao_militar.publicacao in ['EDITOR', 'EDITOR_ADJUNTO', 'EDITOR_GERAL']
    
    # Buscar notas arquivadas separadamente (após paginação das ativas)
    publicacoes_arquivadas = publicacoes_base.filter(tipo='NOTA', ativo=False, status='ARQUIVADA')
    
    # Aplicar filtro hierárquico também nas notas arquivadas
    if request.user.is_superuser:
        # Superusuário vê todas as notas arquivadas
        pass  # Já filtrado acima
    elif funcao_atual:
        # Aplicar filtro hierárquico nas notas arquivadas
        publicacoes_arquivadas = aplicar_filtro_hierarquico_notas(publicacoes_arquivadas, funcao_atual, request.user)
    else:
        # Se não há função ativa, mostrar apenas notas arquivadas do próprio usuário
        publicacoes_arquivadas = publicacoes_arquivadas.filter(criado_por=request.user)
    
    # Aplicar filtros adicionais para notas arquivadas
    # Filtro por origem (destino)
    if origem:
        publicacoes_arquivadas = publicacoes_arquivadas.filter(origem_publicacao__iexact=origem)
    
    
    # Aplicar filtro de hierarquia para notas arquivadas (se especificado)
    if hierarquia_id and (request.user.is_superuser or funcao_atual):
        # Aplicar filtro hierárquico baseado no item selecionado
        from .models import Orgao, GrandeComando, Unidade, SubUnidade
        from django.db.models import Q
        
        filtro_hierarquia_arquivadas = None
        
        try:
            # Tentar como órgão primeiro
            item = Orgao.objects.get(id=hierarquia_id, ativo=True)
            # Para órgão, buscar por toda a hierarquia (órgão + todos os descendentes)
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao=item, ativo=True)
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
            
            # Criar filtros para toda a hierarquia
            filtros_orgao = []
            
            # Adicionar filtro para o órgão principal
            filtros_orgao.append(Q(origem_publicacao__icontains=item.nome))
            filtros_orgao.append(Q(origem_publicacao__icontains=item.sigla))
            
            # Adicionar filtros para grandes comandos
            for gc in grandes_comandos:
                filtros_orgao.append(Q(origem_publicacao__icontains=gc.nome))
                filtros_orgao.append(Q(origem_publicacao__icontains=gc.sigla))
            
            # Adicionar filtros para unidades
            for u in unidades:
                filtros_orgao.append(Q(origem_publicacao__icontains=u.nome))
                filtros_orgao.append(Q(origem_publicacao__icontains=u.sigla))
            
            # Adicionar filtros para subunidades
            for s in subunidades:
                filtros_orgao.append(Q(origem_publicacao__icontains=s.nome))
                filtros_orgao.append(Q(origem_publicacao__icontains=s.sigla))
            
            # Combinar todos os filtros com OR
            if filtros_orgao:
                filtro_hierarquia_arquivadas = filtros_orgao[0]
                for filtro in filtros_orgao[1:]:
                    filtro_hierarquia_arquivadas |= filtro
                    
        except Orgao.DoesNotExist:
            try:
                # Tentar como grande comando
                item = GrandeComando.objects.get(id=hierarquia_id, ativo=True)
                # Para grande comando, buscar por toda a hierarquia (GC + unidades + subunidades)
                
                # Buscar todas as unidades do grande comando
                unidades = Unidade.objects.filter(grande_comando=item, ativo=True)
                
                # Buscar todas as subunidades das unidades
                subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
                
                # Criar filtros para toda a hierarquia
                filtros_gc = []
                
                # Adicionar filtro para o grande comando principal
                filtros_gc.append(Q(origem_publicacao__icontains=item.nome))
                filtros_gc.append(Q(origem_publicacao__icontains=item.sigla))
                
                # Adicionar filtros para unidades
                for u in unidades:
                    filtros_gc.append(Q(origem_publicacao__icontains=u.nome))
                    filtros_gc.append(Q(origem_publicacao__icontains=u.sigla))
                
                # Adicionar filtros para subunidades
                for s in subunidades:
                    filtros_gc.append(Q(origem_publicacao__icontains=s.nome))
                    filtros_gc.append(Q(origem_publicacao__icontains=s.sigla))
                
                # Combinar todos os filtros com OR
                if filtros_gc:
                    filtro_hierarquia_arquivadas = filtros_gc[0]
                    for filtro in filtros_gc[1:]:
                        filtro_hierarquia_arquivadas |= filtro
                        
            except GrandeComando.DoesNotExist:
                try:
                    # Tentar como unidade
                    item = Unidade.objects.get(id=hierarquia_id, ativo=True)
                    # Para unidade, buscar por toda a hierarquia (unidade + subunidades)
                    
                    # Buscar todas as subunidades da unidade
                    subunidades = SubUnidade.objects.filter(unidade=item, ativo=True)
                    
                    # Criar filtros para toda a hierarquia
                    filtros_unidade = []
                    
                    # Adicionar filtro para a unidade principal
                    filtros_unidade.append(Q(origem_publicacao__icontains=item.nome))
                    filtros_unidade.append(Q(origem_publicacao__icontains=item.sigla))
                    
                    # Adicionar filtros para subunidades
                    for s in subunidades:
                        filtros_unidade.append(Q(origem_publicacao__icontains=s.nome))
                        filtros_unidade.append(Q(origem_publicacao__icontains=s.sigla))
                    
                    # Combinar todos os filtros com OR
                    if filtros_unidade:
                        filtro_hierarquia_arquivadas = filtros_unidade[0]
                        for filtro in filtros_unidade[1:]:
                            filtro_hierarquia_arquivadas |= filtro
                            
                except Unidade.DoesNotExist:
                    try:
                        # Tentar como subunidade
                        item = SubUnidade.objects.get(id=hierarquia_id, ativo=True)
                        # Para subunidade, buscar apenas pela subunidade específica
                        filtro_hierarquia_arquivadas = Q(origem_publicacao__icontains=item.nome) | Q(origem_publicacao__icontains=item.sigla)
                    except SubUnidade.DoesNotExist:
                        pass
        
        if filtro_hierarquia_arquivadas:
            publicacoes_arquivadas = publicacoes_arquivadas.filter(filtro_hierarquia_arquivadas)
    
    # Filtro por número da nota
    if numero_nota:
        publicacoes_arquivadas = publicacoes_arquivadas.filter(numero__icontains=numero_nota)
    
    # Filtro por data
    if data_inicio:
        publicacoes_arquivadas = publicacoes_arquivadas.filter(data_criacao__date__gte=data_inicio)
    
    if data_fim:
        publicacoes_arquivadas = publicacoes_arquivadas.filter(data_criacao__date__lte=data_fim)
    
    # Ordenar notas arquivadas por data de arquivamento (mais recente primeiro)
    publicacoes_arquivadas = publicacoes_arquivadas.order_by('-data_atualizacao')
    
    
    # Buscar histórico de arquivamento para cada nota arquivada
    from .models import HistoricoArquivamentoNota
    historicos_arquivamento = {}
    for nota in publicacoes_arquivadas:
        try:
            historico = HistoricoArquivamentoNota.objects.filter(nota=nota).first()
            if historico:
                historicos_arquivamento[nota.pk] = historico
        except:
            pass
    
    # Obter opções de filtro hierárquico baseadas no organograma específico para notas
    from .filtros_hierarquicos_pesquisa import obter_opcoes_filtro_hierarquico_notas
    
    opcoes_filtro_hierarquico = []
    if funcao_atual:
        opcoes_filtro_hierarquico = obter_opcoes_filtro_hierarquico_notas(funcao_atual, request.user)
    
    # Converter para lista de origens no formato hierárquico
    origens_unicas = []
    if opcoes_filtro_hierarquico:
        for opcao in opcoes_filtro_hierarquico:
            origens_unicas.append(opcao['nome'])
    else:
        # Se não há opções hierárquicas, usar todas as origens existentes
        if request.user.is_superuser:
            # Superusuário vê todas as origens
            origens_unicas = Publicacao.objects.filter(
                tipo='NOTA', 
                ativo=True
            ).values_list('origem_publicacao', flat=True).distinct().order_by('origem_publicacao')
        else:
            # Usuário comum vê apenas suas origens
            origens_unicas = Publicacao.objects.filter(
                tipo='NOTA', 
                ativo=True,
                criado_por=request.user
            ).values_list('origem_publicacao', flat=True).distinct().order_by('origem_publicacao')
    
    context = {
        'publicacoes': page_obj,
        'page_obj': page_obj,  # Adicionar page_obj explicitamente
        'publicacoes_arquivadas': publicacoes_arquivadas,
        'historicos_arquivamento': historicos_arquivamento,
        'tipo': 'nota',
        'tipo_display': 'Notas',
        'stats': stats,
        'titulos_publicacao': titulos_publicacao,
        'funcao_atual': funcao_atual,
        'hierarquia_info': locals().get('hierarquia_info', None),
        'can_publish': can_publish,
        'per_page': per_page,
        'origens_unicas': origens_unicas,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'militares/notas_list.html', context)

@login_required
def boletins_ostensivos_list(request):
    """Listar apenas Boletins Ostensivos"""
    
    # Verificar se o usuário tem permissão para acessar boletins
    from .permissoes_simples import pode_acessar_boletins
    
    if not pode_acessar_boletins(request.user):
        messages.error(request, 'Você não tem permissão para acessar boletins. Apenas editores podem acessar este módulo.')
        return redirect('militares:militar_dashboard')
    
    from .filtros_hierarquicos import aplicar_filtro_hierarquico_publicacoes
    from .permissoes import obter_funcao_atual
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Aplicar filtro hierárquico baseado no acesso da função
    if request.user.is_superuser:
        # Superusuário vê todas as publicações
        publicacoes = Publicacao.objects.filter(tipo='BOLETIM_OSTENSIVO', ativo=True)
    elif funcao_atual:
        publicacoes = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.all(), 
            funcao_atual, 
            request.user, 
            'BOLETIM_OSTENSIVO'
        )
    else:
        # Se não há função ativa, mostrar apenas publicações do próprio usuário
        publicacoes = Publicacao.objects.filter(
            tipo='BOLETIM_OSTENSIVO', 
            ativo=True, 
            criado_por=request.user
        )
    
    publicacoes = publicacoes.prefetch_related('assinaturas').order_by('-data_publicacao', '-data_criacao')
    
    # Adicionar flags de assinatura para cada boletim
    for publicacao in publicacoes:
        publicacao.tem_assinatura_editor_chefe = publicacao.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
        publicacao.tem_assinatura_editor_adjunto = publicacao.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
        publicacao.tem_assinatura_editor_geral = publicacao.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
    
    paginator = Paginator(publicacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'publicacoes': page_obj,
        'tipo': 'boletim-ostensivo',
        'tipo_display': 'Boletins Ostensivos',
    }
    return render(request, 'militares/boletins_ostensivos_list.html', context)

@login_required
def nota_publicar_boletim(request, pk):
    """Publicar nota no boletim ostensivo do dia"""
    if request.method == 'POST':
        try:
            from datetime import date
            from .permissoes_simples import obter_funcao_militar_ativa
            from .models import AssinaturaNota
            
            # Buscar a nota
            nota = Publicacao.objects.get(pk=pk, tipo='NOTA')
            
            # Verificar se a nota já foi publicada
            if nota.status == 'PUBLICADA':
                return JsonResponse({
                    'success': False,
                    'message': 'Esta nota já foi publicada!'
                })
            
            # Verificar permissão do usuário (apenas funções com publicação EDITOR)
            # Superusuários têm acesso total
            if not request.user.is_superuser:
                funcao_usuario = obter_funcao_militar_ativa(request.user)
                if not funcao_usuario or funcao_usuario.funcao_militar.publicacao not in ['EDITOR', 'EDITOR_ADJUNTO', 'EDITOR_GERAL']:
                    return JsonResponse({
                        'success': False,
                        'message': 'Apenas funções com permissão de EDITOR podem enviar notas para publicação!'
                    })
            
            # Verificar se a nota tem todas as assinaturas necessárias
            assinaturas = AssinaturaNota.objects.filter(nota=nota)
            
            tem_revisao = assinaturas.filter(tipo_assinatura='REVISAO').exists()
            tem_aprovacao = assinaturas.filter(tipo_assinatura='APROVACAO').exists()
            tem_edicao = assinaturas.filter(tipo_assinatura='EDICAO').exists()
            
            # Verificar se é uma nota devolvida que não foi editada após devolução
            is_devolvida_nao_editada = (not assinaturas.exists() and 
                                       nota.status == 'RASCUNHO' and 
                                       not nota.editada_apos_devolucao)
            
            if is_devolvida_nao_editada:
                return JsonResponse({
                    'success': False,
                    'message': 'Esta nota foi devolvida e precisa ser editada e assinada novamente antes de ser enviada para publicação. Edite a nota primeiro e processe as assinaturas necessárias (Revisão, Aprovação e Edição).'
                })
            
            if not tem_revisao:
                return JsonResponse({
                    'success': False,
                    'message': 'A nota deve estar assinada por um REVISOR antes de ser enviada para publicação!'
                })
            
            if not tem_aprovacao:
                return JsonResponse({
                    'success': False,
                    'message': 'A nota deve estar assinada por um APROVADOR antes de ser enviada para publicação!'
                })
            
            if not tem_edicao:
                return JsonResponse({
                    'success': False,
                    'message': 'A nota deve estar assinada por um EDITOR antes de ser enviada para publicação!'
                })
            
            # Verificar se existe boletim do dia atual baseado no tipo da nota
            data_hoje = date.today()
            
            # Determinar o tipo de boletim baseado no tipo_publicacao da nota
            if nota.tipo_publicacao == 'Reservado':
                tipo_boletim = 'BOLETIM_RESERVADO'
                campo_boletim = 'numero_boletim_reservado'
            elif nota.tipo_publicacao == 'Especial':
                tipo_boletim = 'BOLETIM_ESPECIAL'
                campo_boletim = 'numero_boletim_especial'
            else:
                tipo_boletim = 'BOLETIM_OSTENSIVO'
                campo_boletim = 'numero_boletim'
            
            # Buscar boletim do dia atual (usando data_boletim)
            boletim_hoje = Publicacao.objects.filter(
                tipo=tipo_boletim,
                data_boletim=data_hoje,
                status__in=['RASCUNHO', 'REVISADA', 'APROVADA', 'EDITADA']
            ).first()
            
            if not boletim_hoje:
                if nota.tipo_publicacao == 'Reservado':
                    tipo_boletim_display = 'Reservado'
                elif nota.tipo_publicacao == 'Especial':
                    tipo_boletim_display = 'Especial'
                else:
                    tipo_boletim_display = 'Ostensivo'
                return JsonResponse({
                    'success': False,
                    'message': f'Não é possível publicar notas. Não existe boletim {tipo_boletim_display} do dia atual. Crie um boletim {tipo_boletim_display} para hoje antes de publicar notas.'
                })
            
            # Publicar nota e incluir no boletim
            nota.status = 'PUBLICADA'
            nota.data_publicacao = timezone.localtime(timezone.now())
            nota.publicado_por = request.user
            
            # Atualizar o campo correto baseado no tipo de boletim
            if campo_boletim == 'numero_boletim_reservado':
                nota.numero_boletim_reservado = boletim_hoje.numero
                nota.boletim_reservado = boletim_hoje
                print(f"🔧 DEBUG: Nota {nota.numero} -> Boletim Reservado {boletim_hoje.numero}")
            elif campo_boletim == 'numero_boletim_especial':
                nota.numero_boletim_especial = boletim_hoje.numero
                nota.boletim_especial = boletim_hoje
                print(f"🔧 DEBUG: Nota {nota.numero} -> Boletim Especial {boletim_hoje.numero}")
            else:
                nota.numero_boletim = boletim_hoje.numero
                print(f"🔧 DEBUG: Nota {nota.numero} -> Boletim Ostensivo {boletim_hoje.numero}")
            
            # Preparar campos para atualização
            campos_atualizacao = ['status', 'data_publicacao', 'publicado_por', campo_boletim]
            if campo_boletim == 'numero_boletim_reservado':
                campos_atualizacao.append('boletim_reservado')
            elif campo_boletim == 'numero_boletim_especial':
                campos_atualizacao.append('boletim_especial')
            
            nota.save(update_fields=campos_atualizacao)
            print(f"🔧 DEBUG: Nota salva com status: {nota.status}, numero_boletim: {nota.numero_boletim}, numero_boletim_reservado: {getattr(nota, 'numero_boletim_reservado', 'N/A')}, numero_boletim_especial: {getattr(nota, 'numero_boletim_especial', 'N/A')}")
            
            # Atualizar conteúdo do boletim
            if tipo_boletim == 'BOLETIM_RESERVADO':
                boletim_hoje.conteudo = boletim_hoje.gerar_conteudo_final_reservado()
            elif tipo_boletim == 'BOLETIM_ESPECIAL':
                boletim_hoje.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim_hoje)
            else:
                boletim_hoje.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim_hoje)
            boletim_hoje.save(update_fields=['conteudo'])
            
            return JsonResponse({
                'success': True,
                'message': f'Nota {nota.numero} publicada e incluída no boletim {boletim_hoje.numero} com sucesso!'
            })
            
        except Publicacao.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Nota não encontrada!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao publicar nota: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido!'
    })


@login_required
def disponibilizar_boletim(request, pk):
    """Disponibilizar boletim ostensivo"""
    if request.method == 'POST':
        try:
            from datetime import datetime
            from .models import AssinaturaNota
            
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_OSTENSIVO')
            
            # Verificar se já foi disponibilizado
            if boletim.data_disponibilizacao:
                messages.warning(request, 'Este boletim já foi disponibilizado!')
                return redirect('militares:boletins_ostensivos_list')
            
            # Verificar se o boletim tem as 3 assinaturas necessárias
            assinaturas = AssinaturaNota.objects.filter(nota=boletim)
            
            tem_editor_chefe = assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
            tem_editor_adjunto = assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
            tem_editor_geral = assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
            
            # Contar quantos editores assinaram
            editores_assinados = sum([tem_editor_chefe, tem_editor_adjunto, tem_editor_geral])
            
            if editores_assinados < 3:
                messages.error(request, f'Boletim deve ser assinado pelos 3 editores antes de ser disponibilizado! Assinaturas atuais: {editores_assinados}/3')
                return redirect('militares:boletins_ostensivos_list')
            
            # Definir data de disponibilização
            boletim.data_disponibilizacao = timezone.localtime(timezone.now())
            boletim.save(update_fields=['data_disponibilizacao'])
            
            messages.success(request, f'BCBMEPI {boletim.numero} disponibilizado com sucesso!')
            return redirect('militares:boletins_ostensivos_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_ostensivos_list')
        except Exception as e:
            messages.error(request, f'Erro ao disponibilizar boletim: {str(e)}')
            return redirect('militares:boletins_ostensivos_list')
    
    return redirect('militares:boletins_ostensivos_list')


@login_required
def retornar_boletim_ostensivo(request, pk):
    """Retornar boletim ostensivo de disponibilizado para aguardando (apenas superusuários)"""
    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem executar esta ação!')
        return redirect('militares:boletins_ostensivos_list')
    
    if request.method == 'POST':
        try:
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_OSTENSIVO')
            
            # Verificar se foi disponibilizado
            if not boletim.data_disponibilizacao:
                messages.warning(request, 'Este boletim não foi disponibilizado!')
                return redirect('militares:boletins_ostensivos_list')
            
            # Retornar para aguardando
            boletim.data_disponibilizacao = None
            boletim.save(update_fields=['data_disponibilizacao'])
            
            messages.success(request, f'BCBMEPI {boletim.numero} retornado para aguardando!')
            return redirect('militares:boletins_ostensivos_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_ostensivos_list')
        except Exception as e:
            messages.error(request, f'Erro ao retornar boletim: {str(e)}')
            return redirect('militares:boletins_ostensivos_list')
    
    return redirect('militares:boletins_ostensivos_list')


@login_required
def deletar_boletim_ostensivo(request, pk):
    """Deletar boletim ostensivo (apenas superusuários)"""
    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem executar esta ação!')
        return redirect('militares:boletins_ostensivos_list')
    
    if request.method == 'POST':
        try:
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_OSTENSIVO')
            numero_boletim = boletim.numero
            
            # Deletar boletim
            boletim.delete()
            
            messages.success(request, f'BCBMEPI {numero_boletim} deletado com sucesso!')
            return redirect('militares:boletins_ostensivos_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_ostensivos_list')
        except Exception as e:
            messages.error(request, f'Erro ao deletar boletim: {str(e)}')
            return redirect('militares:boletins_ostensivos_list')
    
    return redirect('militares:boletins_ostensivos_list')


@login_required
def disponibilizar_boletim_especial(request, pk):
    """Disponibilizar boletim especial para visualização"""
    if request.method == 'POST':
        try:
            from .models import AssinaturaNota
            
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_ESPECIAL')
            
            # Verificar se já foi disponibilizado
            if boletim.data_disponibilizacao:
                messages.warning(request, 'Este boletim já foi disponibilizado!')
                return redirect('militares:boletins_especiais_list')
            
            # Verificar se o boletim tem as 3 assinaturas necessárias
            assinaturas = AssinaturaNota.objects.filter(nota=boletim)
            
            tem_editor_chefe = assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
            tem_editor_adjunto = assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
            tem_editor_geral = assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
            
            # Contar quantos editores assinaram
            editores_assinados = sum([tem_editor_chefe, tem_editor_adjunto, tem_editor_geral])
            
            if editores_assinados < 3:
                messages.error(request, f'Boletim deve ser assinado pelos 3 editores antes de ser disponibilizado! Assinaturas atuais: {editores_assinados}/3')
                return redirect('militares:boletins_especiais_list')
            
            # Definir data de disponibilização
            boletim.data_disponibilizacao = timezone.localtime(timezone.now())
            boletim.save(update_fields=['data_disponibilizacao'])
            
            messages.success(request, f'Boletim Especial {boletim.numero} disponibilizado com sucesso!')
            return redirect('militares:boletins_especiais_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_especiais_list')
        except Exception as e:
            messages.error(request, f'Erro ao disponibilizar boletim: {str(e)}')
            return redirect('militares:boletins_especiais_list')
    
    return redirect('militares:boletins_especiais_list')


@login_required
def retornar_boletim_especial(request, pk):
    """Retornar boletim especial de disponibilizado para aguardando (apenas superusuários)"""
    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem executar esta ação!')
        return redirect('militares:boletins_especiais_list')
    
    if request.method == 'POST':
        try:
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_ESPECIAL')
            
            # Verificar se foi disponibilizado
            if not boletim.data_disponibilizacao:
                messages.warning(request, 'Este boletim não foi disponibilizado!')
                return redirect('militares:boletins_especiais_list')
            
            # Retornar para aguardando
            boletim.data_disponibilizacao = None
            boletim.save(update_fields=['data_disponibilizacao'])
            
            messages.success(request, f'Boletim Especial {boletim.numero} retornado para aguardando!')
            return redirect('militares:boletins_especiais_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_especiais_list')
        except Exception as e:
            messages.error(request, f'Erro ao retornar boletim: {str(e)}')
            return redirect('militares:boletins_especiais_list')
    
    return redirect('militares:boletins_especiais_list')


@login_required
def deletar_boletim_especial(request, pk):
    """Deletar boletim especial (apenas superusuários)"""
    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem executar esta ação!')
        return redirect('militares:boletins_especiais_list')
    
    if request.method == 'POST':
        try:
            boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_ESPECIAL')
            numero_boletim = boletim.numero
            
            # Deletar boletim
            boletim.delete()
            
            messages.success(request, f'Boletim Especial {numero_boletim} deletado com sucesso!')
            return redirect('militares:boletins_especiais_list')
            
        except Publicacao.DoesNotExist:
            messages.error(request, 'Boletim não encontrado!')
            return redirect('militares:boletins_especiais_list')
        except Exception as e:
            messages.error(request, f'Erro ao deletar boletim: {str(e)}')
            return redirect('militares:boletins_especiais_list')
    
    return redirect('militares:boletins_especiais_list')


@login_required
def boletins_reservados_list(request):
    """Listar apenas Boletins Reservados"""
    
    # Verificar se o usuário tem permissão para acessar boletins
    from .permissoes_simples import pode_acessar_boletins
    
    if not pode_acessar_boletins(request.user):
        messages.error(request, 'Você não tem permissão para acessar boletins. Apenas editores podem acessar este módulo.')
        return redirect('militares:militar_dashboard')
    
    from .filtros_hierarquicos import aplicar_filtro_hierarquico_publicacoes
    from .permissoes import obter_funcao_atual
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Aplicar filtro hierárquico baseado no acesso da função
    if request.user.is_superuser:
        # Superusuário vê todas as publicações
        publicacoes = Publicacao.objects.filter(tipo='BOLETIM_RESERVADO', ativo=True)
    elif funcao_atual:
        publicacoes = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.all(), 
            funcao_atual, 
            request.user, 
            'BOLETIM_RESERVADO'
        )
    else:
        # Se não há função ativa, mostrar apenas publicações do próprio usuário
        publicacoes = Publicacao.objects.filter(
            tipo='BOLETIM_RESERVADO', 
            ativo=True, 
            criado_por=request.user
        )
    
    publicacoes = publicacoes.order_by('-data_publicacao', '-data_criacao')
    paginator = Paginator(publicacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'publicacoes': page_obj,
        'tipo': 'boletim-reservado',
        'tipo_display': 'Boletins Reservados',
    }
    return render(request, 'militares/boletins_reservados_list.html', context)

@login_required
def boletins_especiais_list(request):
    """Listar apenas Boletins Especiais"""
    
    # Verificar se o usuário tem permissão para acessar boletins
    from .permissoes_simples import pode_acessar_boletins
    
    if not pode_acessar_boletins(request.user):
        messages.error(request, 'Você não tem permissão para acessar boletins. Apenas editores podem acessar este módulo.')
        return redirect('militares:militar_dashboard')
    
    from .filtros_hierarquicos import aplicar_filtro_hierarquico_publicacoes
    from .permissoes import obter_funcao_atual
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Aplicar filtro hierárquico baseado no acesso da função
    if request.user.is_superuser:
        # Superusuário vê todas as publicações
        publicacoes = Publicacao.objects.filter(tipo='BOLETIM_ESPECIAL', ativo=True)
    elif funcao_atual:
        publicacoes = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.all(), 
            funcao_atual, 
            request.user, 
            'BOLETIM_ESPECIAL'
        )
    else:
        # Se não há função ativa, mostrar apenas publicações do próprio usuário
        publicacoes = Publicacao.objects.filter(
            tipo='BOLETIM_ESPECIAL', 
            ativo=True, 
            criado_por=request.user
        )
    
    publicacoes = publicacoes.order_by('-data_publicacao', '-data_criacao')
    paginator = Paginator(publicacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'publicacoes': page_obj,
        'tipo': 'boletim-especial',
        'tipo_display': 'Boletins Especiais',
    }
    return render(request, 'militares/boletins_especiais_list.html', context)

@login_required
def boletim_especial_detail(request, pk):
    """Visualizar e gerenciar Boletim Especial"""
    try:
        boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_ESPECIAL')
    except Publicacao.DoesNotExist:
        messages.error(request, 'Boletim especial não encontrado.')
        return redirect('militares:boletins_especiais_list')
    
    # Buscar notas que podem ser adicionadas ao boletim
    notas_disponiveis = Publicacao.objects.filter(
        tipo='NOTA',
        status='PUBLICADA',
        numero_boletim_especial__isnull=True,  # Ainda não incluída em boletim especial
        numero_boletim__isnull=True,  # Não incluída em boletim ostensivo
        numero_boletim_reservado__isnull=True  # Não incluída em boletim reservado
    ).order_by('-data_publicacao')
    
    # Buscar notas já incluídas no boletim
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim_especial=boletim.numero
    ).order_by('data_publicacao')
    
    # Adicionar flags de assinatura para o boletim
    boletim.tem_assinatura_editor_chefe = boletim.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
    boletim.tem_assinatura_editor_adjunto = boletim.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
    boletim.tem_assinatura_editor_geral = boletim.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
    
    context = {
        'boletim': boletim,
        'notas_disponiveis': notas_disponiveis,
        'notas_incluidas': notas_incluidas,
    }
    return render(request, 'militares/boletim_especial_detail.html', context)

@login_required
def boletim_especial_detail(request, pk):
    """Visualizar e gerenciar Boletim Especial"""
    try:
        boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_ESPECIAL')
    except Publicacao.DoesNotExist:
        messages.error(request, 'Boletim especial não encontrado.')
        return redirect('militares:boletins_especiais_list')
    
    # Buscar notas que podem ser adicionadas ao boletim
    notas_disponiveis = Publicacao.objects.filter(
        tipo='NOTA',
        status='PUBLICADA',
        numero_boletim_especial__isnull=True,  # Ainda não incluída em boletim especial
        topicos=boletim.topicos  # Mesmo tópico do boletim
    ).order_by('-data_publicacao')
    
    # Buscar notas já incluídas no boletim
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim_especial=boletim.numero
    ).order_by('data_publicacao')
    
    # Adicionar flags de assinatura para o boletim
    boletim.tem_assinatura_editor_chefe = boletim.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
    boletim.tem_assinatura_editor_adjunto = boletim.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
    boletim.tem_assinatura_editor_geral = boletim.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
    
    context = {
        'boletim': boletim,
        'notas_disponiveis': notas_disponiveis,
        'notas_incluidas': notas_incluidas,
    }
    return render(request, 'militares/boletim_especial_detail.html', context)

@login_required
def adicionar_nota_boletim_especial(request, boletim_pk, nota_pk):
    """Adicionar nota ao boletim especial"""
    from datetime import date, datetime, time
    
    # Verificar se é uma requisição AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    try:
        boletim = Publicacao.objects.get(pk=boletim_pk, tipo='BOLETIM_ESPECIAL')
        nota = Publicacao.objects.get(pk=nota_pk, tipo='NOTA')
    except Publicacao.DoesNotExist:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Boletim especial ou nota não encontrado.'
            })
        messages.error(request, 'Boletim especial ou nota não encontrado.')
        return redirect('militares:boletins_especiais_list')
    
    # Verificar se a nota já está em um boletim especial
    if nota.numero_boletim_especial:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Esta nota já está incluída em outro boletim especial.'
            })
        messages.warning(request, 'Esta nota já está incluída em outro boletim especial.')
        return redirect('militares:boletim_especial_detail', pk=boletim_pk)
    
    # Adicionar nota ao boletim especial
    nota.numero_boletim_especial = boletim.numero
    nota.boletim_especial = boletim
    nota.save(update_fields=['numero_boletim_especial', 'boletim_especial'])
    
    # Atualizar conteúdo do boletim
    boletim.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim)
    boletim.save(update_fields=['conteudo'])
    
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'Nota {nota.numero} adicionada ao boletim especial com sucesso!'
        })
    
    messages.success(request, f'Nota {nota.numero} adicionada ao boletim especial com sucesso!')
    return redirect('militares:boletim_especial_detail', pk=boletim_pk)

@login_required
def remover_nota_boletim_especial(request, boletim_pk, nota_pk):
    """Remover nota do boletim especial"""
    # Verificar se é uma requisição AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    try:
        boletim = Publicacao.objects.get(pk=boletim_pk, tipo='BOLETIM_ESPECIAL')
        nota = Publicacao.objects.get(pk=nota_pk, tipo='NOTA')
    except Publicacao.DoesNotExist:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Boletim especial ou nota não encontrado.'
            })
        messages.error(request, 'Boletim especial ou nota não encontrado.')
        return redirect('militares:boletins_especiais_list')
    
    # Remover nota do boletim especial
    nota.numero_boletim_especial = None
    nota.boletim_especial = None
    nota.save(update_fields=['numero_boletim_especial', 'boletim_especial'])
    
    # Atualizar conteúdo do boletim
    boletim.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim)
    boletim.save(update_fields=['conteudo'])
    
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'Nota {nota.numero} removida do boletim especial com sucesso!'
        })
    
    messages.success(request, f'Nota {nota.numero} removida do boletim especial com sucesso!')
    return redirect('militares:boletim_especial_detail', pk=boletim_pk)

@login_required
def avisos_list(request):
    """Listar apenas Avisos"""
    from .filtros_hierarquicos import aplicar_filtro_hierarquico_publicacoes
    from .permissoes import obter_funcao_atual
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Aplicar filtro hierárquico baseado no acesso da função
    if request.user.is_superuser:
        # Superusuário vê todas as publicações
        publicacoes = Publicacao.objects.filter(tipo='AVISO', ativo=True)
    elif funcao_atual:
        publicacoes = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.all(), 
            funcao_atual, 
            request.user, 
            'AVISO'
        )
    else:
        # Se não há função ativa, mostrar apenas publicações do próprio usuário
        publicacoes = Publicacao.objects.filter(
            tipo='AVISO', 
            ativo=True, 
            criado_por=request.user
        )
    
    publicacoes = publicacoes.order_by('-data_publicacao', '-data_criacao')
    paginator = Paginator(publicacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'publicacoes': page_obj,
        'tipo': 'aviso',
        'tipo_display': 'Avisos',
    }
    return render(request, 'militares/avisos_list.html', context)

@login_required
def ordens_servico_list(request):
    """Listar apenas Ordens de Serviço"""
    from .filtros_hierarquicos import aplicar_filtro_hierarquico_publicacoes
    from .permissoes import obter_funcao_atual
    
    # Obter função atual do usuário
    funcao_atual = obter_funcao_atual(request)
    
    # Aplicar filtro hierárquico baseado no acesso da função
    if request.user.is_superuser:
        # Superusuário vê todas as publicações
        publicacoes = Publicacao.objects.filter(tipo='ORDEM_SERVICO', ativo=True)
    elif funcao_atual:
        publicacoes = aplicar_filtro_hierarquico_publicacoes(
            Publicacao.objects.all(), 
            funcao_atual, 
            request.user, 
            'ORDEM_SERVICO'
        )
    else:
        # Se não há função ativa, mostrar apenas publicações do próprio usuário
        publicacoes = Publicacao.objects.filter(
            tipo='ORDEM_SERVICO', 
            ativo=True, 
            criado_por=request.user
        )
    
    publicacoes = publicacoes.order_by('-data_publicacao', '-data_criacao')
    paginator = Paginator(publicacoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'publicacoes': page_obj,
        'tipo': 'ordem-servico',
        'tipo_display': 'Ordens de Serviço',
    }
    return render(request, 'militares/ordens_servico_list.html', context)

@login_required
def notas_create(request):
    """Criar nova Nota"""
    return publicacao_create(request, tipo='nota')

@login_required
def boletins_ostensivos_create(request):
    """Criar novo Boletim Ostensivo automaticamente"""
    if request.method == 'POST':
        try:
            from datetime import datetime, date
            
            # Verificar se já existe um boletim para o dia atual
            data_hoje = date.today()
            boletim_existente = Publicacao.objects.filter(
                tipo='BOLETIM_OSTENSIVO',
                data_boletim=data_hoje,
                ativo=True
            ).first()
            
            if boletim_existente:
                messages.warning(request, f'Já existe um BCBMEPI para hoje ({data_hoje.strftime("%d/%m/%Y")}): {boletim_existente.numero}')
                return redirect('militares:boletins_ostensivos_list')
            
            # Criar boletim com dados automáticos e estrutura das 4 partes
            conteudo_inicial = '''<h2>Boletim do Corpo de Bombeiros Militar do Estado do Piauí</h2>

<h3>1ª PARTE - SERVIÇOS DIÁRIOS</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>2ª PARTE - INSTRUÇÃO</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>3ª PARTE - ASSUNTOS GERAIS</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>3ª PARTE - ADMINISTRATIVOS</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>4ª PARTE - JUSTIÇA</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>4ª PARTE - DISCIPLINA</h3>
<p>Nenhuma nota incluída ainda.</p>'''

            boletim = Publicacao(
                tipo='BOLETIM_OSTENSIVO',
                titulo='BCBMEPI',
                topicos='',  # Será preenchido conforme as notas forem adicionadas
                status='RASCUNHO',
                conteudo=conteudo_inicial,
                criado_por=request.user,
                data_boletim=data_hoje,
                ativo=True,
                numero=''  # Forçar string vazia para acionar geração automática
            )
            
            boletim.save()  # Isso vai acionar o método save() que gera o número automaticamente
            
            messages.success(request, f'BCBMEPI {boletim.numero} criado com sucesso!')
            return redirect('militares:boletins_ostensivos_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar boletim: {str(e)}')
            return redirect('militares:boletins_ostensivos_list')
    
    return redirect('militares:boletins_ostensivos_list')

@login_required
def boletim_ostensivo_detail(request, pk):
    """Visualizar e gerenciar Boletim Ostensivo"""
    try:
        boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_OSTENSIVO')
    except Publicacao.DoesNotExist:
        messages.error(request, 'Boletim não encontrado.')
        return redirect('militares:boletins_ostensivos_list')
    
    # Buscar notas que podem ser adicionadas ao boletim
    notas_disponiveis = Publicacao.objects.filter(
        tipo='NOTA',
        status='PUBLICADA',
        numero_boletim__isnull=True,  # Ainda não incluída em boletim
        topicos=boletim.topicos  # Mesmo tópico do boletim
    ).order_by('-data_publicacao')
    
    # Buscar notas já incluídas no boletim
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim=boletim.numero
    ).order_by('data_publicacao')
    
    # Adicionar flags de assinatura para o boletim
    boletim.tem_assinatura_editor_chefe = boletim.assinaturas.filter(tipo_assinatura='EDITOR_CHEFE').exists()
    boletim.tem_assinatura_editor_adjunto = boletim.assinaturas.filter(tipo_assinatura='EDITOR_ADJUNTO').exists()
    boletim.tem_assinatura_editor_geral = boletim.assinaturas.filter(tipo_assinatura='EDITOR_GERAL').exists()
    
    context = {
        'boletim': boletim,
        'notas_disponiveis': notas_disponiveis,
        'notas_incluidas': notas_incluidas,
    }
    return render(request, 'militares/boletim_ostensivo_detail.html', context)

@login_required
def boletim_ostensivo_visualizar(request, pk):
    """Visualizar Boletim Ostensivo em nova página com visual de modal"""
    try:
        boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_OSTENSIVO')
    except Publicacao.DoesNotExist:
        messages.error(request, 'Boletim não encontrado.')
        return redirect('militares:boletins_ostensivos_list')
    
    # Buscar notas incluídas no boletim
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim=boletim.numero
    ).order_by('data_publicacao')
    
    # Buscar assinaturas do boletim
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    context = {
        'boletim': boletim,
        'notas_incluidas': notas_incluidas,
        'assinaturas': assinaturas,
    }
    return render(request, 'militares/boletim_ostensivo_visualizar.html', context)

@login_required
def boletim_especial_visualizar(request, pk):
    """Visualizar Boletim Especial em nova página com visual de modal"""
    try:
        boletim = Publicacao.objects.get(pk=pk, tipo='BOLETIM_ESPECIAL')
    except Publicacao.DoesNotExist:
        messages.error(request, 'Boletim especial não encontrado.')
        return redirect('militares:boletins_especiais_list')
    
    # Buscar notas incluídas no boletim especial
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim_especial=boletim.numero
    ).order_by('data_publicacao')
    
    # Buscar assinaturas do boletim
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    context = {
        'boletim': boletim,
        'notas_incluidas': notas_incluidas,
        'assinaturas': assinaturas,
    }
    return render(request, 'militares/boletim_especial_visualizar.html', context)

@login_required
def nota_visualizar(request, pk):
    """Visualizar Nota em nova página com visual de modal"""
    try:
        nota = Publicacao.objects.select_related(
            'orgao', 
            'grande_comando', 
            'unidade', 
            'sub_unidade'
        ).get(pk=pk, tipo='NOTA')
    except Publicacao.DoesNotExist:
        messages.error(request, 'Nota não encontrada.')
        return redirect('militares:notas_list')
    
    # Verificar se o usuário pode visualizar a nota baseado no status
    can_view = True
    is_militar_indexado = False
    
    # Verificar se o usuário é um militar indexado nesta nota
    if hasattr(request.user, 'militar') and request.user.militar:
        is_militar_indexado = nota.militares_indexados.filter(id=request.user.militar.id).exists()
    
    # Se a nota não está publicada, verificar permissões especiais
    if nota.status != 'PUBLICADA':
        # Superusuários sempre podem visualizar
        if request.user.is_superuser:
            can_view = True
        # Usuários com permissão de edição podem visualizar
        elif nota.can_edit(request.user):
            can_view = True
        # Usuários com permissão de publicação podem visualizar
        elif nota.can_publish(request.user):
            can_view = True
        # Criador da nota pode visualizar
        elif nota.criado_por == request.user:
            can_view = True
        # Militares indexados podem visualizar
        elif is_militar_indexado:
            can_view = True
        # Qualquer usuário autenticado pode visualizar modelos de notas
        elif nota.titulo and 'MODELO' in nota.titulo.upper():
            can_view = True
        # Operadores de planejadas podem visualizar notas para copiar links
        elif request.user.is_authenticated:
            from .permissoes_simples import obter_funcao_militar_ativa
            funcao_usuario = obter_funcao_militar_ativa(request.user)
            if funcao_usuario and funcao_usuario.funcao_militar.publicacao == 'OPERADOR_PLANEJADAS':
                can_view = True
            else:
                can_view = False
        else:
            can_view = False
    
    if not can_view:
        messages.error(request, f'Você não tem permissão para visualizar esta nota. Apenas notas publicadas podem ser visualizadas por todos os usuários.')
        return redirect('militares:notas_list')
    
    # Buscar assinaturas da nota
    assinaturas = nota.assinaturas.all().order_by('-data_assinatura')
    
    context = {
        'nota': nota,
        'assinaturas': assinaturas,
    }
    return render(request, 'militares/nota_visualizar.html', context)

@login_required
def nota_modal_content(request, pk):
    """Retorna apenas o conteúdo do modal para visualização de notas"""
    try:
        nota = Publicacao.objects.select_related(
            'orgao', 
            'grande_comando', 
            'unidade', 
            'sub_unidade'
        ).get(pk=pk, tipo='NOTA')
    except Publicacao.DoesNotExist:
        return JsonResponse({'error': 'Nota não encontrada.'}, status=404)
    
    # Verificar se o usuário pode visualizar a nota baseado no status
    can_view = True
    is_militar_indexado = False
    
    # Verificar se o usuário é um militar indexado nesta nota
    if hasattr(request.user, 'militar') and request.user.militar:
        is_militar_indexado = nota.militares_indexados.filter(id=request.user.militar.id).exists()
    
    # Se a nota não está publicada, verificar permissões especiais
    if nota.status != 'PUBLICADA':
        # Superusuários sempre podem visualizar
        if request.user.is_superuser:
            can_view = True
        # Usuários com permissão de edição podem visualizar
        elif nota.can_edit(request.user):
            can_view = True
        # Usuários com permissão de publicação podem visualizar
        elif nota.can_publish(request.user):
            can_view = True
        # Criador da nota pode visualizar
        elif nota.criado_por == request.user:
            can_view = True
        # Militares indexados podem visualizar
        elif is_militar_indexado:
            can_view = True
        # Qualquer usuário autenticado pode visualizar modelos de notas
        elif nota.titulo and 'MODELO' in nota.titulo.upper():
            can_view = True
        # Operadores de planejadas podem visualizar notas para copiar links
        elif request.user.is_authenticated:
            from .permissoes_simples import obter_funcao_militar_ativa
            funcao_usuario = obter_funcao_militar_ativa(request.user)
            if funcao_usuario and funcao_usuario.funcao_militar.publicacao == 'OPERADOR_PLANEJADAS':
                can_view = True
            else:
                can_view = False
        else:
            can_view = False
    
    if not can_view:
        return JsonResponse({'error': 'Você não tem permissão para visualizar esta nota.'}, status=403)
    
    # Buscar assinaturas da nota
    assinaturas = nota.assinaturas.all()
    
    # Ordenar assinaturas por hierarquia militar (do mais alto para o mais baixo)
    def obter_prioridade_hierarquica(assinatura):
        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
            militar = assinatura.assinado_por.militar
            posto = militar.posto_graduacao
            
            # Definir prioridades hierárquicas (menor número = maior hierarquia)
            prioridades = {
                'CORONEL': 1,
                'TENENTE_CORONEL': 2,
                'MAJOR': 3,
                'CAPITAO': 4,
                'PRIMEIRO_TENENTE': 5,
                'SEGUNDO_TENENTE': 6,
                'ASPIRANTE_A_OFICIAL': 7,
                'SUBTENENTE': 8,
                'PRIMEIRO_SARGENTO': 9,
                'SEGUNDO_SARGENTO': 10,
                'TERCEIRO_SARGENTO': 11,
                'CABO': 12,
                'SOLDADO': 13,
            }
            return prioridades.get(posto, 99)  # Se não encontrar, colocar no final
        return 99  # Se não for militar, colocar no final
    
    # Ordenar assinaturas por hierarquia
    assinaturas_ordenadas = sorted(assinaturas, key=obter_prioridade_hierarquica)
    
    context = {
        'nota': nota,
        'assinaturas': assinaturas_ordenadas,
    }
    return render(request, 'militares/nota_modal_content.html', context)

@login_required
def adicionar_nota_boletim(request, boletim_pk, nota_pk):
    """Adicionar nota ao boletim"""
    from datetime import date, datetime, time
    
    # Verificar se é uma requisição AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    try:
        boletim = Publicacao.objects.get(pk=boletim_pk, tipo='BOLETIM_OSTENSIVO')
        nota = Publicacao.objects.get(pk=nota_pk, tipo='NOTA')
    except Publicacao.DoesNotExist:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Boletim ou nota não encontrado.'
            })
        messages.error(request, 'Boletim ou nota não encontrado.')
        return redirect('militares:boletins_ostensivos_list')
    
    # Verificar se a nota já está em um boletim
    if nota.numero_boletim:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Esta nota já está incluída em outro boletim.'
            })
        messages.warning(request, 'Esta nota já está incluída em outro boletim.')
        return redirect('militares:boletim_ostensivo_detail', pk=boletim_pk)
    
    # Obter data e hora atual
    agora = datetime.now()
    data_hoje = agora.date()
    hora_atual = agora.time()
    
    # Obter data do boletim
    data_boletim = boletim.data_boletim if boletim.data_boletim else boletim.data_criacao.date()
    
    # VALIDAÇÃO CRÍTICA: Só permitir adicionar notas ao boletim do dia atual
    if data_boletim != data_hoje:
        mensagem_erro = f'Não é possível adicionar notas a boletins de datas diferentes de hoje. Boletim é de {data_boletim.strftime("%d/%m/%Y")} e hoje é {data_hoje.strftime("%d/%m/%Y")}. As notas só podem ser adicionadas ao boletim do dia atual.'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': mensagem_erro
            })
        messages.error(request, mensagem_erro)
        return redirect('militares:boletim_ostensivo_detail', pk=boletim_pk)
    
    # VALIDAÇÃO: Verificar se ainda é possível adicionar notas (até 23:59 do dia do boletim)
    limite_horario = time(23, 59)  # 23:59
    if hora_atual > limite_horario:
        mensagem_erro = f'Não é possível adicionar notas após as 23:59 do dia do boletim. Horário atual: {hora_atual.strftime("%H:%M")}. As notas ficam disponíveis para boletins futuros.'
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': mensagem_erro
            })
        messages.error(request, mensagem_erro)
        return redirect('militares:boletim_ostensivo_detail', pk=boletim_pk)
    
    # Adicionar nota ao boletim
    nota.numero_boletim = boletim.numero
    nota.save(update_fields=['numero_boletim'])
    
    # Atualizar conteúdo do boletim
    boletim.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim)
    boletim.save(update_fields=['conteudo'])
    
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': f'Nota {nota.numero} adicionada ao boletim com sucesso!'
        })
    
    messages.success(request, f'Nota {nota.numero} adicionada ao boletim com sucesso!')
    return redirect('militares:boletim_ostensivo_detail', pk=boletim_pk)

@login_required
def remover_nota_boletim(request, boletim_pk, nota_pk):
    """Remover nota do boletim"""
    try:
        boletim = Publicacao.objects.get(pk=boletim_pk, tipo='BOLETIM_OSTENSIVO')
        nota = Publicacao.objects.get(pk=nota_pk, tipo='NOTA')
    except Publicacao.DoesNotExist:
        messages.error(request, 'Boletim ou nota não encontrado.')
        return redirect('militares:boletins_ostensivos_list')
    
    # Remover nota do boletim
    nota.numero_boletim = None
    nota.save(update_fields=['numero_boletim'])
    
    # Atualizar conteúdo do boletim
    boletim.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim)
    boletim.save(update_fields=['conteudo'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Nota {nota.numero} removida do boletim com sucesso!'
        })
    
    messages.success(request, f'Nota {nota.numero} removida do boletim com sucesso!')
    return redirect('militares:boletim_ostensivo_detail', pk=boletim_pk)

@login_required
def ajax_notas_disponiveis_boletim(request):
    """AJAX: Buscar notas disponíveis para adicionar ao boletim"""
    from datetime import date, datetime, time
    
    boletim_id = request.GET.get('boletim_id')
    topicos = request.GET.get('topicos', '')
    
    try:
        boletim = Publicacao.objects.get(pk=boletim_id, tipo='BOLETIM_OSTENSIVO')
        
        # Obter data e hora atual
        agora = datetime.now()
        data_hoje = agora.date()
        hora_atual = agora.time()
        
        # Obter data do boletim
        data_boletim = boletim.data_boletim if boletim.data_boletim else boletim.data_criacao.date()
        
        # Buscar notas que podem ser adicionadas ao boletim
        notas = Publicacao.objects.filter(
            tipo='NOTA',
            status='PUBLICADA',
            numero_boletim__isnull=True,  # Ainda não incluída em boletim
            topicos=topicos  # Mesmo tópico do boletim
        ).order_by('-data_publicacao')
        
        notas_data = []
        for nota in notas:
            # Obter data da nota
            data_nota = nota.data_publicacao.date() if nota.data_publicacao else nota.data_criacao.date()
            
            # VALIDAÇÃO: Só incluir notas que atendem aos critérios de data e horário
            pode_incluir = True
            motivo_rejeicao = ""
            
            # VALIDAÇÃO CRÍTICA: Só permitir adicionar notas ao boletim do dia atual
            if data_boletim != data_hoje:
                pode_incluir = False
                motivo_rejeicao = f"Boletim é de {data_boletim.strftime('%d/%m/%Y')}, não é do dia atual. Notas só podem ser adicionadas ao boletim de hoje ({data_hoje.strftime('%d/%m/%Y')})."
            # Verificar se ainda é possível adicionar notas (até 23:59 do dia do boletim)
            elif data_boletim == data_hoje:
                limite_horario = time(23, 59)  # 23:59
                if hora_atual > limite_horario:
                    pode_incluir = False
                    motivo_rejeicao = f"Horário limite para adicionar notas (23:59) já passou. Horário atual: {hora_atual.strftime('%H:%M')}. Nota ficará disponível para boletins futuros."
            
            notas_data.append({
                'id': nota.id,
                'numero': nota.numero,
                'titulo': nota.titulo,
                'data_publicacao': nota.data_publicacao.isoformat() if nota.data_publicacao else None,
                'origem_publicacao': nota.origem_publicacao or '',
                'pode_incluir': pode_incluir,
                'motivo_rejeicao': motivo_rejeicao,
            })
        
        return JsonResponse({
            'success': True,
            'notas': notas_data
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Boletim não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar notas: {str(e)}'
        })

@login_required
def ajax_verificar_boletim_hoje(request):
    """AJAX: Verificar se existe boletim do dia atual"""
    from datetime import date
    
    data_hoje = date.today()
    
    # Buscar boletim do dia atual
    boletim_hoje = Publicacao.objects.filter(
        tipo='BOLETIM_OSTENSIVO',
        data_boletim=data_hoje,
        status__in=['RASCUNHO', 'REVISADA', 'APROVADA', 'EDITADA']
    ).first()
    
    # Se não encontrar boletim com data_boletim de hoje, buscar por data_criacao
    if not boletim_hoje:
        boletim_hoje = Publicacao.objects.filter(
            tipo='BOLETIM_OSTENSIVO',
            data_criacao__date=data_hoje,
            status__in=['RASCUNHO', 'REVISADA', 'APROVADA', 'EDITADA']
        ).first()
    
    existe_boletim = boletim_hoje is not None
    
    return JsonResponse({
        'success': True,
        'existe_boletim': existe_boletim,
        'data_hoje': data_hoje.strftime('%d/%m/%Y'),
        'boletim_numero': boletim_hoje.numero if boletim_hoje else None
    })

@login_required
def ajax_proximo_numero_boletim(request):
    """AJAX: Buscar próximo número de boletim para o ano"""
    ano = request.GET.get('ano')
    
    try:
        # Buscar último boletim do ano
        ultimo_boletim = Publicacao.objects.filter(
            tipo='BOLETIM_OSTENSIVO',
            numero__startswith=f"B.O. {ano}/"
        ).order_by('-numero').first()
        
        if ultimo_boletim and ultimo_boletim.numero:
            try:
                # Extrair o número sequencial (ex: "B.O. 2024/001" -> 1)
                partes = ultimo_boletim.numero.split('/')
                if len(partes) >= 2:
                    numero_str = partes[-1]
                    numero_atual = int(numero_str)
                    proximo_numero = numero_atual + 1
                else:
                    proximo_numero = 1
            except (ValueError, IndexError):
                proximo_numero = 1
        else:
            proximo_numero = 1
        
        # Formatar o número (ex: "B.O. 2024/001")
        numero_formatado = f"B.O. {ano}/{proximo_numero:03d}"
        
        return JsonResponse({
            'success': True,
            'numero': numero_formatado
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar próximo número: {str(e)}'
        })

@login_required
def ajax_notas_incluidas_boletim(request):
    """AJAX: Buscar notas já incluídas no boletim"""
    boletim_id = request.GET.get('boletim_id')
    
    try:
        # Buscar boletim (ostensivo ou especial)
        boletim = Publicacao.objects.get(pk=boletim_id)
        
        # Determinar campo de busca baseado no tipo
        if boletim.tipo == 'BOLETIM_OSTENSIVO':
            notas = Publicacao.objects.filter(
                tipo='NOTA',
                numero_boletim=boletim.numero
            ).order_by('data_publicacao')
        elif boletim.tipo == 'BOLETIM_ESPECIAL':
            notas = Publicacao.objects.filter(
                tipo='NOTA',
                numero_boletim_especial=boletim.numero
            ).order_by('data_publicacao')
        else:
            notas = Publicacao.objects.none()
        
        notas_data = []
        for nota in notas:
            notas_data.append({
                'id': nota.id,
                'numero': nota.numero,
                'titulo': nota.titulo,
                'conteudo': nota.conteudo or '',
                'topicos': nota.topicos or '',
                'data_publicacao': nota.data_publicacao.strftime('%d/%m/%Y %H:%M') if nota.data_publicacao else '',
                'origem_publicacao': nota.origem_publicacao or '',
                'criado_por_nome': nota.criado_por.get_full_name() if nota.criado_por else 'Sistema',
                'status': nota.get_status_display(),
            })
        
        return JsonResponse({
            'success': True,
            'notas': notas_data
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Boletim não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar notas: {str(e)}'
        })

@login_required
def ajax_assinaturas_boletim(request):
    """AJAX: Buscar assinaturas do boletim"""
    boletim_id = request.GET.get('boletim_id')
    
    try:
        boletim = Publicacao.objects.get(pk=boletim_id)
        
        # Buscar assinaturas do boletim
        assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
        
        assinaturas_data = []
        for assinatura in assinaturas:
            # Nome do assinante
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{militar.nome_completo} - {posto}"
            else:
                nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            
            assinaturas_data.append({
                'id': assinatura.id,
                'assinado_por_nome': nome_completo,
                'funcao_assinatura': assinatura.funcao_assinatura or 'Função não registrada',
                'tipo_assinatura': assinatura.get_tipo_assinatura_display() or 'Tipo não registrado',
                'data_assinatura': assinatura.data_assinatura.isoformat() if assinatura.data_assinatura else None,
            })
        
        return JsonResponse({
            'success': True,
            'assinaturas': assinaturas_data
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Boletim não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar assinaturas: {str(e)}'
        })


@login_required
def ajax_notas_incluidas_boletim_especial(request, boletim_pk):
    """AJAX para buscar notas incluídas no boletim especial"""
    try:
        boletim = Publicacao.objects.get(pk=boletim_pk, tipo='BOLETIM_ESPECIAL')
        print(f"DEBUG: Boletim especial encontrado - ID: {boletim.pk}, Número: {boletim.numero}")
        
        notas = Publicacao.objects.filter(
            tipo='NOTA',
            numero_boletim_especial=boletim.numero
        ).order_by('data_publicacao')
        
        print(f"DEBUG: Notas encontradas: {notas.count()}")
        for nota in notas:
            print(f"  - Nota {nota.numero}: {nota.titulo} (tópico: {nota.topicos})")
        
        notas_data = []
        for nota in notas:
            notas_data.append({
                'id': nota.id,
                'numero': nota.numero,
                'titulo': nota.titulo,
                'conteudo': nota.conteudo or '',
                'topicos': nota.topicos or '',
                'status': nota.status,
                'data_publicacao': nota.data_publicacao.strftime('%Y-%m-%dT%H:%M:%S') if nota.data_publicacao else '',
                'criado_por_nome': nota.criado_por.get_full_name() if nota.criado_por else 'Sistema',
            })
        
        return JsonResponse({
            'success': True,
            'notas': notas_data
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Boletim especial não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})

@login_required
def boletins_reservados_create(request):
    """Criar novo Boletim Reservado"""
    return publicacao_create(request, tipo='boletim-reservado')

@login_required
def boletins_especiais_create(request):
    """Criar novo Boletim Especial automaticamente"""
    if request.method == 'POST':
        try:
            from datetime import datetime, date
            
            # Verificar se já existe um boletim especial para o dia atual
            data_hoje = date.today()
            boletim_existente = Publicacao.objects.filter(
                tipo='BOLETIM_ESPECIAL',
                data_boletim=data_hoje,
                ativo=True
            ).first()
            
            if boletim_existente:
                messages.warning(request, f'Já existe um Boletim Especial para hoje ({data_hoje.strftime("%d/%m/%Y")}): {boletim_existente.numero}')
                return redirect('militares:boletins_especiais_list')
            
            # Criar boletim especial com dados automáticos e estrutura das 4 partes
            conteudo_inicial = '''<h2>Boletim Especial do Corpo de Bombeiros Militar do Estado do Piauí</h2>

<h3>1ª PARTE - SERVIÇOS DIÁRIOS</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>2ª PARTE - INSTRUÇÃO</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>3ª PARTE - ASSUNTOS GERAIS</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>3ª PARTE - ADMINISTRATIVOS</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>4ª PARTE - JUSTIÇA</h3>
<p>Nenhuma nota incluída ainda.</p>

<h3>4ª PARTE - DISCIPLINA</h3>
<p>Nenhuma nota incluída ainda.</p>'''

            boletim = Publicacao(
                tipo='BOLETIM_ESPECIAL',
                titulo='Boletim Especial',
                topicos='',  # Será preenchido conforme as notas forem adicionadas
                status='RASCUNHO',
                conteudo=conteudo_inicial,
                criado_por=request.user,
                data_boletim=data_hoje,
                ativo=True,
                numero=''  # Forçar string vazia para acionar geração automática
            )
            
            boletim.save()  # Isso vai acionar o método save() que gera o número automaticamente
            
            messages.success(request, f'Boletim Especial {boletim.numero} criado com sucesso!')
            return redirect('militares:boletins_especiais_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar boletim especial: {str(e)}')
            return redirect('militares:boletins_especiais_list')
    
    return redirect('militares:boletins_especiais_list')

@login_required
def avisos_create(request):
    """Criar novo Aviso"""
    return publicacao_create(request, tipo='aviso')

@login_required
def ordens_servico_create(request):
    """Criar nova Ordem de Serviço"""
    return publicacao_create(request, tipo='ordem-servico')

# ==================== VIEWS DE REORDENAÇÃO ====================

@login_required
def reordenar_notas(request):
    """Reordenar números das notas - apenas para superusuários"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas superusuários podem reordenar as notas.')
        return redirect('militares:notas_list')
    
    if request.method == 'POST':
        try:
            numero_inicial = int(request.POST.get('numero_inicial', 1))
            numero_apartir = int(request.POST.get('numero_apartir', 1))
            
            from django.utils import timezone
            from django.db import transaction
            
            ano_atual = timezone.localtime(timezone.now()).year
            
            # Buscar todas as notas ordenadas por data de criação
            notas = Publicacao.objects.filter(
                tipo='NOTA',
                ativo=True
            ).order_by('data_criacao')
            
            print(f"🔧 REORDENAR: Encontradas {notas.count()} notas")
            
            # Filtrar notas a partir do número especificado
            notas_para_reordenar = []
            for nota in notas:
                print(f"🔧 REORDENAR: Analisando nota {nota.id}: numero='{nota.numero}'")
                
                # Verificar se o número está no formato correto
                if '/' in nota.numero and nota.numero.endswith(f"/{ano_atual}"):
                    # Já está no formato correto, extrair número
                    try:
                        numero_atual = int(nota.numero.split('/')[0])
                        if numero_atual >= numero_apartir:
                            notas_para_reordenar.append(nota)
                    except (ValueError, IndexError):
                        notas_para_reordenar.append(nota)
                else:
                    # Formato incorreto, incluir na reordenação
                    notas_para_reordenar.append(nota)
            
            print(f"🔧 REORDENAR: {len(notas_para_reordenar)} notas para reordenar")
            
            # Atualizar os números sequencialmente apenas das notas selecionadas
            with transaction.atomic():
                for i, nota in enumerate(notas_para_reordenar):
                    novo_numero = numero_inicial + i
                    numero_formatado = f"{novo_numero:03d}/{ano_atual}"
                    print(f"🔧 REORDENAR: Nota {nota.id}: '{nota.numero}' -> '{numero_formatado}'")
                    nota.numero = numero_formatado
                    nota.save()
            
            total_reordenadas = len(notas_para_reordenar)
            messages.success(request, f'{total_reordenadas} notas reordenadas com sucesso! Iniciando do número {numero_inicial:03d}')
            return redirect('militares:notas_list')
            
        except ValueError:
            messages.error(request, 'Números devem ser valores válidos.')
        except Exception as e:
            messages.error(request, f'Erro ao reordenar notas: {str(e)}')
    
    # Buscar estatísticas das notas
    total_notas = Publicacao.objects.filter(tipo='NOTA', ativo=True).count()
    primeira_nota = Publicacao.objects.filter(tipo='NOTA', ativo=True).order_by('data_criacao').first()
    ultima_nota = Publicacao.objects.filter(tipo='NOTA', ativo=True).order_by('-data_criacao').first()
    
    # Buscar números das notas para mostrar lacunas
    numeros_existentes = []
    for nota in Publicacao.objects.filter(tipo='NOTA', ativo=True).order_by('data_criacao'):
        try:
            numeros_existentes.append(int(nota.numero))
        except (ValueError, TypeError):
            continue
    
    context = {
        'total_notas': total_notas,
        'primeira_nota': primeira_nota,
        'ultima_nota': ultima_nota,
        'numeros_existentes': sorted(numeros_existentes),
    }
    
    return render(request, 'militares/reordenar_notas.html', context)


@login_required
def corrigir_formatos_notas(request):
    """Corrigir formatos incorretos das notas - apenas para superusuários"""
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas superusuários podem corrigir formatos.')
        return redirect('militares:notas_list')
    
    if request.method == 'POST':
        try:
            from django.utils import timezone
            from django.db import transaction
            
            ano_atual = timezone.localtime(timezone.now()).year
            
            # Buscar todas as notas com formato incorreto
            notas_incorretas = Publicacao.objects.filter(
                tipo='NOTA',
                ativo=True
            ).exclude(numero__endswith=f"/{ano_atual}")
            
            # Debug: mostrar informações na interface
            total_notas = Publicacao.objects.filter(tipo='NOTA', ativo=True).count()
            messages.info(request, f"Total de notas: {total_notas}")
            messages.info(request, f"Notas com formato incorreto: {notas_incorretas.count()}")
            
            for nota in notas_incorretas[:10]:  # Mostrar as primeiras 10
                messages.info(request, f"Nota {nota.id}: '{nota.numero}'")
            
            if len(notas_incorretas) > 10:
                messages.info(request, f"... e mais {len(notas_incorretas) - 10} notas")
            
            corrigidas = 0
            with transaction.atomic():
                for nota in notas_incorretas:
                    print(f"🔧 CORRIGIR: Nota {nota.id}: '{nota.numero}'")
                    
                    # Tentar extrair o número da nota
                    try:
                        if '/' in nota.numero:
                            # Formato "001/2025/2025" -> extrair "001"
                            partes = nota.numero.split('/')
                            if len(partes) >= 2 and partes[0].isdigit():
                                # Usar apenas o número, não o ano existente
                                numero_corrigido = f"{int(partes[0]):03d}/{ano_atual}"
                            else:
                                # Formato estranho, usar 001
                                numero_corrigido = f"001/{ano_atual}"
                        else:
                            # Formato "001" -> adicionar ano
                            if nota.numero.isdigit():
                                numero_corrigido = f"{int(nota.numero):03d}/{ano_atual}"
                            else:
                                # Formato estranho, usar 001
                                numero_corrigido = f"001/{ano_atual}"
                        
                        print(f"🔧 CORRIGIR: Corrigindo para: '{numero_corrigido}'")
                        nota.numero = numero_corrigido
                        nota.save()
                        corrigidas += 1
                        
                    except Exception as e:
                        print(f"🔧 CORRIGIR: Erro ao corrigir nota {nota.id}: {e}")
                        # Se der erro, usar formato padrão
                        nota.numero = f"001/{ano_atual}"
                        nota.save()
                        corrigidas += 1
            
            messages.success(request, f'{corrigidas} notas corrigidas com sucesso!')
            return redirect('militares:notas_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao corrigir formatos: {str(e)}')
    
    return render(request, 'militares/corrigir_formatos_notas.html')

# ==================== VIEWS AJAX ====================

@login_required
def ajax_titulos_publicacao(request):
    """
    Retorna os títulos de publicação cadastrados para seleção no modal
    """
    try:
        # Verificar permissão para acessar configurações (títulos de publicação)
        if not pode_acessar_configuracoes(request.user):
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para acessar títulos de publicação'
            }, status=403)
        
        titulos = TituloPublicacaoConfig.objects.filter(ativo=True).order_by('ordem', 'titulo')
        
        titulos_data = []
        for titulo in titulos:
            titulos_data.append({
                'id': titulo.id,
                'titulo': titulo.titulo,
                'tipo': titulo.tipo,
                'tipo_display': titulo.get_tipo_display(),
                'topicos': titulo.topicos,
                'ordem': titulo.ordem
            })
        
        return JsonResponse({
            'success': True,
            'titulos': titulos_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def arquivar_nota(request, pk):
    """Arquivar nota com justificativa"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário tem permissão para arquivar a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para arquivar esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para arquivar esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_arquivamento = request.POST.get('motivo_arquivamento', '').strip()
        
        if not motivo_arquivamento:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo do arquivamento é obrigatório.'
                })

            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Arquivar a nota
                nota.status = 'ARQUIVADA'
                nota.ativo = False
                nota.save()
                
                # Salvar histórico do arquivamento
                from .models import HistoricoArquivamentoNota
                HistoricoArquivamentoNota.objects.create(
                    nota=nota,
                    arquivado_por=request.user,
                    motivo_arquivamento=motivo_arquivamento
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} arquivada com sucesso!'
                })
            
            messages.success(request, f'Nota {nota.numero} arquivada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao arquivar nota: {str(e)}'
                }, status=500)


@login_required
def ajax_titulo_publicacao_detail(request, pk):
    """
    Retorna os detalhes de um título de publicação específico
    """
    try:
        print(f"AJAX: Buscando título ID {pk} para usuário {request.user.username}")
        
        # Verificar permissão para acessar publicações (mais específica que configurações)
        # Temporariamente desabilitado para permitir funcionamento da funcionalidade
        # if not pode_acessar_publicacoes(request.user):
        #     print(f"❌ AJAX: Usuário {request.user.username} não tem permissão para acessar publicações")
        #     return JsonResponse({
        #         'success': False,
        #         'error': 'Você não tem permissão para acessar títulos de publicação. Verifique suas permissões em Publicações.'
        #     }, status=403)
        
        titulo = TituloPublicacaoConfig.objects.get(pk=pk, ativo=True)
        print(f"AJAX: Título encontrado - {titulo.titulo}, Tópicos: {titulo.topicos}")
        
        response_data = {
            'success': True,
            'titulo': {
                'id': titulo.id,
                'titulo': titulo.titulo,
                'tipo': titulo.tipo,
                'tipo_display': titulo.get_tipo_display(),
                'topicos': titulo.topicos,
                'topicos_display': titulo.get_topicos_display() if titulo.topicos else '',
                'ordem': titulo.ordem
            }
        }
        
        print(f"AJAX: Enviando resposta: {response_data}")
        return JsonResponse(response_data)
        
    except TituloPublicacaoConfig.DoesNotExist:
        print(f"AJAX: Título ID {pk} não encontrado")
        return JsonResponse({
            'success': False,
            'error': 'Título de publicação não encontrado'
        }, status=404)
        
    except Exception as e:
        print(f"AJAX: Erro inesperado: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def arquivar_nota(request, pk):
    """Arquivar nota com justificativa"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário tem permissão para arquivar a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para arquivar esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para arquivar esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_arquivamento = request.POST.get('motivo_arquivamento', '').strip()
        
        if not motivo_arquivamento:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo do arquivamento é obrigatório.'
                })

            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Arquivar a nota
                nota.status = 'ARQUIVADA'
                nota.ativo = False
                nota.save()
                
                # Salvar histórico do arquivamento
                from .models import HistoricoArquivamentoNota
                HistoricoArquivamentoNota.objects.create(
                    nota=nota,
                    arquivado_por=request.user,
                    motivo_arquivamento=motivo_arquivamento
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} arquivada com sucesso!'
                })
            
            messages.success(request, f'Nota {nota.numero} arquivada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao arquivar nota: {str(e)}'
                }, status=500)


@login_required
def ajax_organograma_publicacoes(request):
    """
    Retorna a hierarquia completa do organograma para seleção de origem da publicação
    """
    try:
        from .models import Orgao, GrandeComando, Unidade, SubUnidade

        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Usuário não autenticado'
            }, status=401)
        
        # Buscar todos os órgãos com suas hierarquias
        orgaos = Orgao.objects.filter(ativo=True).prefetch_related(
            'grandes_comandos__unidades__sub_unidades'
        ).order_by('nome')

        hierarquia = []

        for orgao in orgaos:
            # Adicionar órgão
            hierarquia.append({
                'id': f'orgao_{orgao.id}',
                'tipo': 'orgao',
                'nivel': 1,
                'texto': f"{orgao.nome}",
                'valor': {
                    'orgao_id': orgao.id,
                    'grande_comando_id': None,
                    'unidade_id': None,
                    'sub_unidade_id': None
                }
            })

            # Adicionar grandes comandos
            for gc in orgao.grandes_comandos.filter(ativo=True).order_by('nome'):
                hierarquia.append({
                    'id': f'gc_{gc.id}',
                    'tipo': 'grande_comando',
                    'nivel': 2,
                    'texto': f"{orgao.nome} | {gc.nome}",
                    'valor': {
                        'orgao_id': orgao.id,
                        'grande_comando_id': gc.id,
                        'unidade_id': None,
                        'sub_unidade_id': None
                    }
                })

                # Adicionar unidades
                for unidade in gc.unidades.filter(ativo=True).order_by('nome'):
                    hierarquia.append({
                        'id': f'unidade_{unidade.id}',
                        'tipo': 'unidade',
                        'nivel': 3,
                        'texto': f"{orgao.nome} | {gc.nome} | {unidade.nome}",
                        'valor': {
                            'orgao_id': orgao.id,
                            'grande_comando_id': gc.id,
                            'unidade_id': unidade.id,
                            'sub_unidade_id': None
                        }
                    })

                    # Adicionar sub-unidades
                    for sub_unidade in unidade.sub_unidades.filter(ativo=True).order_by('nome'):
                        hierarquia.append({
                            'id': f'sub_{sub_unidade.id}',
                            'tipo': 'sub_unidade',
                            'nivel': 4,
                            'texto': f"{orgao.nome} | {gc.nome} | {unidade.nome} | {sub_unidade.nome}",
                            'valor': {
                                'orgao_id': orgao.id,
                                'grande_comando_id': gc.id,
                                'unidade_id': unidade.id,
                                'sub_unidade_id': sub_unidade.id
                            }
                        })

        return JsonResponse({
            'success': True,
            'hierarquia': hierarquia
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def arquivar_nota(request, pk):
    """Arquivar nota com justificativa"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário tem permissão para arquivar a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para arquivar esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para arquivar esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_arquivamento = request.POST.get('motivo_arquivamento', '').strip()
        
        if not motivo_arquivamento:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo do arquivamento é obrigatório.'
                })

            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Arquivar a nota
                nota.status = 'ARQUIVADA'
                nota.ativo = False
                nota.save()
                
                # Salvar histórico do arquivamento
                from .models import HistoricoArquivamentoNota
                HistoricoArquivamentoNota.objects.create(
                    nota=nota,
                    arquivado_por=request.user,
                    motivo_arquivamento=motivo_arquivamento
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} arquivada com sucesso!'
                })
            
            messages.success(request, f'Nota {nota.numero} arquivada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao arquivar nota: {str(e)}'
                }, status=500)


@login_required
def ajax_nota_detail(request, pk):
    """
    Retorna os detalhes de uma nota específica para edição
    """
    try:
        nota = Publicacao.objects.get(pk=pk, tipo='NOTA')
        
        # Verificar se o usuário pode visualizar a nota
        can_view = True
        is_militar_indexado = False
        
        # Verificar se o usuário é um militar indexado nesta nota
        try:
            if hasattr(request.user, 'militar') and request.user.militar:
                is_militar_indexado = nota.militares_indexados.filter(id=request.user.militar.id).exists()
        except Exception as e:
            is_militar_indexado = False
        
        # Se a nota não está publicada, verificar permissões especiais
        if nota.status != 'PUBLICADA':
            # Superusuários sempre podem visualizar
            if request.user.is_superuser:
                can_view = True
            # Usuários com permissão de edição podem visualizar
            elif nota.can_edit(request.user):
                can_view = True
            # Usuários com permissão de publicação podem visualizar
            elif nota.can_publish(request.user):
                can_view = True
            # Criador da nota pode visualizar
            elif nota.criado_por == request.user:
                can_view = True
            # Militares indexados podem visualizar
            elif is_militar_indexado:
                can_view = True
            # NOVO: Qualquer usuário autenticado pode visualizar modelos de notas
            elif nota.titulo and 'MODELO' in nota.titulo.upper():
                can_view = True
            # Operadores de planejadas podem visualizar notas para copiar links
            elif request.user.is_authenticated:
                from .permissoes_simples import obter_funcao_militar_ativa
                funcao_usuario = obter_funcao_militar_ativa(request.user)
                if funcao_usuario and funcao_usuario.funcao_militar.publicacao == 'OPERADOR_PLANEJADAS':
                    can_view = True
                else:
                    can_view = False
            else:
                can_view = False
        
        if not can_view:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para visualizar esta nota'
            }, status=403)
        
        return JsonResponse({
            'success': True,
            'nota': {
                'id': nota.id,
                'titulo': nota.titulo,
                'origem_publicacao': nota.origem_publicacao or '',
                'tipo_publicacao': nota.tipo_publicacao or '',
                'topicos': nota.topicos or '',
                'conteudo': nota.conteudo or '',
                'status': nota.status,
                'numero': nota.numero
            }
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Nota não encontrada'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def arquivar_nota(request, pk):
    """Arquivar nota com justificativa"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário tem permissão para arquivar a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para arquivar esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para arquivar esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_arquivamento = request.POST.get('motivo_arquivamento', '').strip()
        
        if not motivo_arquivamento:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo do arquivamento é obrigatório.'
                })

            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Arquivar a nota
                nota.status = 'ARQUIVADA'
                nota.ativo = False
                nota.save()
                
                # Salvar histórico do arquivamento
                from .models import HistoricoArquivamentoNota
                HistoricoArquivamentoNota.objects.create(
                    nota=nota,
                    arquivado_por=request.user,
                    motivo_arquivamento=motivo_arquivamento
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} arquivada com sucesso!'
                })
            
            messages.success(request, f'Nota {nota.numero} arquivada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao arquivar nota: {str(e)}'
                }, status=500)


@login_required
def nota_edit_ajax(request, pk):
    """
    Edita uma nota via AJAX
    """
    
    try:
        nota = Publicacao.objects.get(pk=pk, tipo='NOTA')
        
        # Verificar se a nota está publicada e se o boletim foi disponibilizado
        if nota.status == 'PUBLICADA':
            # Verificar se o boletim foi disponibilizado
            boletim = None
            if nota.numero_boletim:
                boletim = Publicacao.objects.filter(
                    tipo='BOLETIM_OSTENSIVO',
                    numero=nota.numero_boletim
                ).first()
            
            if boletim and boletim.data_disponibilizacao:
                return JsonResponse({
                    'success': False,
                    'error': 'Esta nota não pode mais ser editada pois o boletim já foi disponibilizado.'
                }, status=403)
            else:
                # Usuário tem permissão para editar
                pass
        else:
            # Usuário não tem permissão para editar
            pass
        
        # Verificar permissões de edição (apenas usuários com funções militares apropriadas)
        can_edit = nota.can_edit(request.user)
        
        # Verificar permissão de edição
        if not can_edit and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para editar esta nota. Apenas usuários com funções militares apropriadas podem editar.'
            }, status=403)
        
        if request.method == 'POST':
            
            # Atualizar campos
            nota.titulo = request.POST.get('titulo', nota.titulo)
            nota.origem_publicacao = request.POST.get('origem_publicacao', nota.origem_publicacao)
            nota.tipo_publicacao = request.POST.get('tipo_publicacao', nota.tipo_publicacao)
            nota.topicos = request.POST.get('topicos', nota.topicos)
            nota.conteudo = request.POST.get('conteudo', nota.conteudo)
            nota.data_atualizacao = timezone.now()
            
            # Marcar como editada após devolução se foi devolvida anteriormente
            if HistoricoDevolucaoNota.objects.filter(nota=nota).exists():
                nota.editada_apos_devolucao = True
            
            nota.save()
            
            # Atualizar conteúdo do boletim se a nota estiver publicada
            if nota.status == 'PUBLICADA' and nota.numero_boletim:
                boletim = Publicacao.objects.filter(
                    tipo='BOLETIM_OSTENSIVO',
                    numero=nota.numero_boletim
                ).first()
                
                if boletim:
                    boletim.conteudo = Publicacao._gerar_conteudo_boletim_atualizado(boletim)
                    boletim.save(update_fields=['conteudo'])
                else:
                    # Boletim não encontrado - continuar normalmente
                    pass
            
            return JsonResponse({
                'success': True,
                'message': 'Nota atualizada com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Método não permitido'
            }, status=405)
            
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Nota não encontrada'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def arquivar_nota(request, pk):
    """Arquivar nota com justificativa"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário tem permissão para arquivar a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para arquivar esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para arquivar esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_arquivamento = request.POST.get('motivo_arquivamento', '').strip()
        
        if not motivo_arquivamento:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo do arquivamento é obrigatório.'
                })

            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Arquivar a nota
                nota.status = 'ARQUIVADA'
                nota.ativo = False
                nota.save()
                
                # Salvar histórico do arquivamento
                from .models import HistoricoArquivamentoNota
                HistoricoArquivamentoNota.objects.create(
                    nota=nota,
                    arquivado_por=request.user,
                    motivo_arquivamento=motivo_arquivamento
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} arquivada com sucesso!'
                })
            
            messages.success(request, f'Nota {nota.numero} arquivada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao arquivar nota: {str(e)}'
                }, status=500)


@login_required
def publicacao_visualizar_ajax(request, pk):
    """Visualizar publicação via AJAX"""
    try:
        publicacao = get_object_or_404(Publicacao, pk=pk)
        
        # Buscar informações hierárquicas do criador da publicação
        orgao_nome = '-'
        grande_comando_nome = '-'
        unidade_nome = '-'
        subunidade_nome = '-'
        
        if publicacao.criado_por and hasattr(publicacao.criado_por, 'militar'):
            try:
                # Buscar lotação atual do militar
                lotacao_atual = publicacao.criado_por.militar.lotacoes.filter(
                    status='ATUAL',
                    ativo=True
                ).first()
                
                if lotacao_atual:
                    orgao_nome = lotacao_atual.orgao.nome if lotacao_atual.orgao else '-'
                    grande_comando_nome = lotacao_atual.grande_comando.nome if lotacao_atual.grande_comando else '-'
                    unidade_nome = lotacao_atual.unidade.nome if lotacao_atual.unidade else '-'
                    subunidade_nome = lotacao_atual.sub_unidade.nome if lotacao_atual.sub_unidade else '-'
            except Exception as e:
                print(f"Erro ao buscar informações hierárquicas: {e}")
        
        # Buscar anexos da publicação
        anexos = []
        for anexo in publicacao.anexos.filter(ativo=True):
            anexos.append({
                'id': anexo.id,
                'nome_original': anexo.nome_original,
                'descricao': anexo.descricao or '',
                'tamanho': anexo.get_tamanho_display(),
                'url_download': anexo.arquivo.url if anexo.arquivo else None,
                'data_upload': anexo.data_upload.strftime('%d/%m/%Y %H:%M'),
                'upload_por': anexo.upload_por.get_full_name() if anexo.upload_por else 'Usuário removido',
                'icone_tipo': anexo.get_icone_tipo()
            })
        
        # Preparar dados da publicação
        dados_publicacao = {
            'id': publicacao.id,
            'numero': publicacao.numero,
            'titulo': publicacao.titulo,
            'origem_publicacao': publicacao.origem_publicacao,
            'tipo_publicacao': publicacao.tipo_publicacao,
            'topicos': publicacao.topicos,
            'status': publicacao.status,
            'status_display': publicacao.get_status_display(),
            'numero_boletim': publicacao.numero_boletim,
            'conteudo': publicacao.conteudo,
            'criado_em': publicacao.data_criacao.strftime('%d/%m/%Y %H:%M') if publicacao.data_criacao else None,
            'atualizado_em': publicacao.data_atualizacao.strftime('%d/%m/%Y %H:%M') if publicacao.data_atualizacao else None,
            'criado_por': publicacao.criado_por.get_full_name() if publicacao.criado_por else 'N/A',
            'orgao': orgao_nome,
            'grande_comando': grande_comando_nome,
            'unidade': unidade_nome,
            'subunidade': subunidade_nome,
            'anexos': anexos
        }
        
        return JsonResponse({
            'success': True,
            'publicacao': dados_publicacao
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Publicação não encontrada'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def arquivar_nota(request, pk):
    """Arquivar nota com justificativa"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário tem permissão para arquivar a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para arquivar esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para arquivar esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_arquivamento = request.POST.get('motivo_arquivamento', '').strip()
        
        if not motivo_arquivamento:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo do arquivamento é obrigatório.'
                })

            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Arquivar a nota
                nota.status = 'ARQUIVADA'
                nota.ativo = False
                nota.save()
                
                # Salvar histórico do arquivamento
                from .models import HistoricoArquivamentoNota
                HistoricoArquivamentoNota.objects.create(
                    nota=nota,
                    arquivado_por=request.user,
                    motivo_arquivamento=motivo_arquivamento
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} arquivada com sucesso!'
                })
            
            messages.success(request, f'Nota {nota.numero} arquivada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao arquivar nota: {str(e)}'
                }, status=500)


@login_required
def ajax_boletins_disponiveis(request):
    """AJAX para buscar boletins disponíveis para transferência"""
    try:
        boletins = Publicacao.objects.filter(
            tipo='BOLETIM_OSTENSIVO',
            status__in=['RASCUNHO', 'AGUARDANDO_APROVACAO']
        ).order_by('-data_publicacao')[:20]  # Limitar a 20 boletins
        
        boletins_data = []
        for boletim in boletins:
            boletins_data.append({
                'id': boletim.pk,
                'numero': boletim.numero,
                'titulo': boletim.titulo,
                'data_publicacao': boletim.data_publicacao.strftime('%d/%m/%Y') if boletim.data_publicacao else 'N/A',
                'status': boletim.get_status_display()
            })
        
        return JsonResponse({
            'success': True,
            'boletins': boletins_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def arquivar_nota(request, pk):
    """Arquivar nota com justificativa"""
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se o usuário tem permissão para arquivar a nota
    if not nota.can_edit(request.user) and not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'error': 'Você não tem permissão para arquivar esta nota.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para arquivar esta nota.')
        return redirect('militares:nota_detail', pk=nota.pk)
    
    if request.method == 'POST':
        motivo_arquivamento = request.POST.get('motivo_arquivamento', '').strip()
        
        if not motivo_arquivamento:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Motivo do arquivamento é obrigatório.'
                })

            return redirect('militares:nota_detail', pk=nota.pk)
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Arquivar a nota
                nota.status = 'ARQUIVADA'
                nota.ativo = False
                nota.save()
                
                # Salvar histórico do arquivamento
                from .models import HistoricoArquivamentoNota
                HistoricoArquivamentoNota.objects.create(
                    nota=nota,
                    arquivado_por=request.user,
                    motivo_arquivamento=motivo_arquivamento
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Nota {nota.numero} arquivada com sucesso!'
                })
            
            messages.success(request, f'Nota {nota.numero} arquivada com sucesso!')
            return redirect('militares:nota_detail', pk=nota.pk)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao arquivar nota: {str(e)}'
                }, status=500)
@login_required
def devolver_nota(request, pk):
    """Devolver nota para rascunho com justificativa"""
    from django.shortcuts import get_object_or_404, redirect, render
    from django.contrib import messages
    from django.http import JsonResponse
    from django.db import transaction
    from .models import Publicacao, AssinaturaNota, HistoricoDevolucaoNota
    
    nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
    
    # Verificar se a nota está em um boletim disponibilizado
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
                pass  # Se o middleware de mensagens não estiver disponível
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
                nota.numero_boletim = None  # Remover do boletim
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
