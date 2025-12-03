from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Medalha, ConcessaoMedalha, Militar, POSTO_GRADUACAO_CHOICES, PropostaMedalha, UsuarioFuncaoMilitar, AssinaturaConcessaoMedalha, AssinaturaPropostaMedalha
from .forms import ConcessaoMedalhaMilitarForm, ConcessaoMedalhaExternoForm
# from .permissoes_simples import requer_funcao_especial


@login_required
@login_required
def medalha_dashboard(request):
    garantir_catalogo()
    total_concessoes = ConcessaoMedalha.objects.count()
    total_militares_agraciados = ConcessaoMedalha.objects.filter(militar__isnull=False).values('militar').distinct().count()
    total_externos_agraciados = ConcessaoMedalha.objects.filter(militar__isnull=True).count()
    return render(request, 'militares/medalhas/dashboard.html', {
        'total_concessoes': total_concessoes,
        'total_militares_agraciados': total_militares_agraciados,
        'total_externos_agraciados': total_externos_agraciados,
    })


def garantir_catalogo():
    try:
        from .models import garantir_medalhas_padrao
        garantir_medalhas_padrao()
    except Exception:
        pass


@login_required
@login_required
def assinar_concessao_medalha(request, pk):
    """Assina uma concessão de medalha eletronicamente"""
    try:
        concessao = ConcessaoMedalha.objects.get(pk=pk)
    except ConcessaoMedalha.DoesNotExist:
        messages.error(request, 'Concessão de medalha não encontrada.')
        return redirect('militares:concessoes_list')

    # Verificar se já existe assinatura do usuário
    assinatura_existente = AssinaturaConcessaoMedalha.objects.filter(
        concessao=concessao,
        assinado_por=request.user,
        tipo_assinatura='ELETRONICA'
    ).first()
    
    if assinatura_existente:
        messages.warning(request, 'Você já assinou esta concessão.')
        return redirect('militares:concessoes_list')

    # Verificar permissão para assinar
    if not request.user.is_superuser:
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            status='ATIVO',
            funcao_militar__nome__in=['Administrador do Sistema', 'Ajudante Geral', 'Comandante Geral']
        ).exists()
        
        if not funcoes_especiais:
            messages.error(request, 'Você não tem permissão para assinar concessões de medalhas.')
            return redirect('militares:concessoes_list')

    if request.method == 'POST':
        # Verificar senha do usuário
        senha = request.POST.get('senha')
        if not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            context = {
                'concessao': concessao,
                'assinatura_existente': assinatura_existente,
            }
            return render(request, 'militares/medalhas/assinar_concessao.html', context)
        
        # Criar assinatura
        try:
            # Obter dados do formulário
            funcao_assinatura = request.POST.get('funcao_assinatura', '')
            tipo_assinatura = request.POST.get('tipo_assinatura', 'ELETRONICA')
            observacoes = request.POST.get('observacoes', '')
            
            # Se não foi fornecida função, usar função padrão
            if not funcao_assinatura:
                funcao_ativa = UsuarioFuncaoMilitar.objects.filter(
                    usuario=request.user,
                    status='ATIVO'
                ).first()
                funcao_assinatura = funcao_ativa.funcao_militar.nome if funcao_ativa else "Usuário do Sistema"
            
            assinatura = AssinaturaConcessaoMedalha.objects.create(
                concessao=concessao,
                assinado_por=request.user,
                tipo_assinatura=tipo_assinatura,
                funcao_assinatura=funcao_assinatura,
                observacoes=observacoes
            )
            
            messages.success(request, f'Concessão assinada com sucesso por {request.user.get_full_name()}.')
            return redirect('militares:concessoes_list')
            
        except Exception as e:
            messages.error(request, f'Erro ao assinar concessão: {str(e)}')
    
    # Buscar funções ativas do usuário
    from militares.models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        status='ATIVO'
    ).select_related('funcao_militar').order_by('funcao_militar__nome')
    
    # Função atual selecionada (da sessão ou primeira disponível)
    funcao_atual = request.session.get('funcao_atual_nome', '')
    if not funcao_atual and funcoes_usuario.exists():
        funcao_atual = funcoes_usuario.first().funcao_militar.nome
    
    context = {
        'concessao': concessao,
        'assinatura_existente': assinatura_existente,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
    }
    
    return render(request, 'militares/medalhas/assinar_concessao.html', context)


@login_required
@login_required
def retirar_assinatura_concessao_medalha(request, pk, assinatura_pk):
    """Remove uma assinatura de concessão de medalha"""
    try:
        concessao = ConcessaoMedalha.objects.get(pk=pk)
        assinatura = AssinaturaConcessaoMedalha.objects.get(pk=assinatura_pk, concessao=concessao)
    except (ConcessaoMedalha.DoesNotExist, AssinaturaConcessaoMedalha.DoesNotExist):
        messages.error(request, 'Concessão ou assinatura não encontrada.')
        return redirect('militares:concessoes_list')

    # Verificar se o usuário pode remover a assinatura
    if not request.user.is_superuser and assinatura.assinado_por != request.user:
        messages.error(request, 'Você só pode remover suas próprias assinaturas.')
        return redirect('militares:concessoes_list')

    if request.method == 'POST':
        try:
            assinatura.delete()
            messages.success(request, 'Assinatura removida com sucesso.')
            return redirect('militares:concessoes_list')
        except Exception as e:
            messages.error(request, f'Erro ao remover assinatura: {str(e)}')
    
    context = {
        'concessao': concessao,
        'assinatura': assinatura,
    }
    
    return render(request, 'militares/medalhas/retirar_assinatura_concessao.html', context)


@login_required
@login_required
def assinar_proposta_medalha(request, pk):
    """Assina uma proposta de medalha eletronicamente"""
    try:
        proposta = PropostaMedalha.objects.get(pk=pk)
    except PropostaMedalha.DoesNotExist:
        messages.error(request, 'Proposta de medalha não encontrada.')
        return redirect('militares:lista_propostas')

    # Verificar se já existe assinatura do usuário
    assinatura_existente = AssinaturaPropostaMedalha.objects.filter(
        proposta=proposta,
        assinado_por=request.user,
        tipo_assinatura='ELETRONICA'
    ).first()
    
    if assinatura_existente:
        messages.warning(request, 'Você já assinou esta proposta.')
        return redirect('militares:lista_propostas')

    # Verificar permissão para assinar
    if not request.user.is_superuser:
        from militares.models import UsuarioFuncaoMilitar
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            status='ATIVO',
            funcao_militar__nome__in=['Administrador do Sistema', 'Ajudante Geral', 'Comandante Geral']
        ).exists()
        
        if not funcoes_especiais:
            messages.error(request, 'Você não tem permissão para assinar propostas de medalhas.')
            return redirect('militares:lista_propostas')

    if request.method == 'POST':
        # Verificar senha do usuário
        senha = request.POST.get('senha')
        if not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            context = {
                'proposta': proposta,
                'assinatura_existente': assinatura_existente,
            }
            return render(request, 'militares/medalhas/assinar_proposta.html', context)
        
        # Criar assinatura
        try:
            # Obter dados do formulário
            funcao_assinatura = request.POST.get('funcao_assinatura', '')
            tipo_assinatura = request.POST.get('tipo_assinatura', 'ELETRONICA')
            observacoes = request.POST.get('observacoes', '')
            
            # Se não foi fornecida função, usar função padrão
            if not funcao_assinatura:
                from militares.models import UsuarioFuncaoMilitar
                funcao_ativa = UsuarioFuncaoMilitar.objects.filter(
                    usuario=request.user,
                    status='ATIVO'
                ).first()
                funcao_assinatura = funcao_ativa.funcao_militar.nome if funcao_ativa else "Usuário do Sistema"
            
            assinatura = AssinaturaPropostaMedalha.objects.create(
                proposta=proposta,
                assinado_por=request.user,
                tipo_assinatura=tipo_assinatura,
                funcao_assinatura=funcao_assinatura,
                observacoes=observacoes
            )
            
            messages.success(request, f'Proposta assinada com sucesso por {request.user.get_full_name()}.')
            return redirect('militares:visualizar_proposta', pk=proposta.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao assinar proposta: {str(e)}')
    
    # Buscar funções ativas do usuário
    from militares.models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        status='ATIVO'
    ).select_related('funcao_militar').order_by('funcao_militar__nome')
    
    # Função atual selecionada (da sessão ou primeira disponível)
    funcao_atual = request.session.get('funcao_atual_nome', '')
    if not funcao_atual and funcoes_usuario.exists():
        funcao_atual = funcoes_usuario.first().funcao_militar.nome
    
    context = {
        'proposta': proposta,
        'assinatura_existente': assinatura_existente,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
    }
    
    return render(request, 'militares/medalhas/assinar_proposta.html', context)


@login_required
@login_required
def retirar_assinatura_proposta_medalha(request, pk, assinatura_pk):
    """Remove uma assinatura de proposta de medalha"""
    try:
        proposta = PropostaMedalha.objects.get(pk=pk)
        assinatura = AssinaturaPropostaMedalha.objects.get(pk=assinatura_pk, proposta=proposta)
    except (PropostaMedalha.DoesNotExist, AssinaturaPropostaMedalha.DoesNotExist):
        messages.error(request, 'Proposta ou assinatura não encontrada.')
        return redirect('militares:lista_propostas')

    # Verificar se o usuário pode remover a assinatura
    if not request.user.is_superuser and assinatura.assinado_por != request.user:
        messages.error(request, 'Você só pode remover suas próprias assinaturas.')
        return redirect('militares:lista_propostas')

    if request.method == 'POST':
        try:
            assinatura.delete()
            messages.success(request, 'Assinatura removida com sucesso.')
            return redirect('militares:visualizar_proposta', pk=proposta.pk)
        except Exception as e:
            messages.error(request, f'Erro ao remover assinatura: {str(e)}')
    
    # Buscar funções ativas do usuário
    from militares.models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        status='ATIVO'
    ).select_related('funcao_militar').order_by('funcao_militar__nome')
    
    # Função atual selecionada (da sessão ou primeira disponível)
    funcao_atual = request.session.get('funcao_atual_nome', '')
    if not funcao_atual and funcoes_usuario.exists():
        funcao_atual = funcoes_usuario.first().funcao_militar.nome
    
    context = {
        'proposta': proposta,
        'assinatura': assinatura,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
    }
    
    return render(request, 'militares/medalhas/retirar_assinatura_proposta.html', context)


@login_required
def excluir_proposta_medalha(request, pk):
    """Exclui uma proposta de medalha e todas as suas concessões e assinaturas"""
    print(f"DEBUG: excluir_proposta_medalha chamada com pk={pk}")
    print(f"DEBUG: Método da requisição: {request.method}")
    print(f"DEBUG: Usuário: {request.user}")
    print(f"DEBUG: Usuário autenticado: {request.user.is_authenticated}")
    print(f"DEBUG: Usuário superuser: {request.user.is_superuser}")
    
    # Verificar permissões
    from militares.models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        status='ATIVO'
    ).select_related('funcao_militar')
    
    print(f"DEBUG: Funções do usuário: {[f.funcao_militar.nome for f in funcoes_usuario]}")
    
    try:
        proposta = PropostaMedalha.objects.get(pk=pk)
        print(f"DEBUG: Proposta encontrada: {proposta.titulo}")
        print(f"DEBUG: Status da proposta: {proposta.status}")
    except PropostaMedalha.DoesNotExist:
        print(f"DEBUG: Proposta não encontrada com pk={pk}")
        messages.error(request, 'Proposta não encontrada.')
        return redirect('militares:lista_propostas')

    if request.method == 'POST':
        print(f"DEBUG: Processando exclusão da proposta {proposta.titulo}")
        print(f"DEBUG: ID da proposta: {proposta.pk}")
        print(f"DEBUG: Tipo da proposta: {type(proposta)}")
        
        try:
            # Verificar se a proposta ainda existe antes de excluir
            proposta_refresh = PropostaMedalha.objects.get(pk=pk)
            print(f"DEBUG: Proposta ainda existe no banco: {proposta_refresh.titulo}")
            
            # IMPORTANTE: Limpar o relacionamento ManyToMany primeiro
            print(f"DEBUG: Limpando relacionamento ManyToMany...")
            proposta.concessoes.clear()
            print(f"DEBUG: Relacionamento ManyToMany limpo")
            
            # Verificar se as concessões foram removidas do relacionamento
            concessoes_apos_clear = proposta.concessoes.count()
            print(f"DEBUG: Concessões após clear(): {concessoes_apos_clear}")
            
            # Excluir todas as assinaturas relacionadas
            assinaturas = AssinaturaPropostaMedalha.objects.filter(proposta=proposta)
            total_assinaturas = assinaturas.count()
            print(f"DEBUG: Encontradas {total_assinaturas} assinaturas para excluir")
            if total_assinaturas > 0:
                print(f"DEBUG: IDs das assinaturas: {list(assinaturas.values_list('pk', flat=True))}")
                assinaturas.delete()
                print(f"DEBUG: Assinaturas excluídas com sucesso")
                # Verificar se foram realmente excluídas
                assinaturas_apos = AssinaturaPropostaMedalha.objects.filter(proposta=proposta)
                print(f"DEBUG: Assinaturas após exclusão: {assinaturas_apos.count()}")
            
            # Excluir a proposta
            titulo_proposta = proposta.titulo
            proposta_id = proposta.pk
            print(f"DEBUG: Tentando excluir proposta ID: {proposta_id}")
            
            # Verificar se há alguma proteção no modelo
            print(f"DEBUG: Verificando se há proteções no modelo...")
            
            # Usar delete() com force_delete=True se necessário
            proposta.delete()
            print(f"DEBUG: Proposta {titulo_proposta} excluída com sucesso")
            
            # Verificar se foi realmente excluída
            try:
                proposta_verificacao = PropostaMedalha.objects.get(pk=proposta_id)
                print(f"DEBUG: ERRO: Proposta ainda existe após delete: {proposta_verificacao.titulo}")
            except PropostaMedalha.DoesNotExist:
                print(f"DEBUG: SUCESSO: Proposta foi realmente excluída do banco")
            
            messages.success(
                request, 
                f'Proposta "{titulo_proposta}" excluída com sucesso. '
                f'Foram removidas {total_assinaturas} assinaturas.'
            )
            print(f"DEBUG: Redirecionando para lista_propostas após sucesso")
            return redirect('militares:lista_propostas')
            
        except Exception as e:
            print(f"DEBUG: Erro ao excluir proposta: {str(e)}")
            print(f"DEBUG: Tipo do erro: {type(e).__name__}")
            import traceback
            print(f"DEBUG: Traceback completo: {traceback.format_exc()}")
            messages.error(request, f'Erro ao excluir proposta: {str(e)}')
            return redirect('militares:lista_propostas')
    else:
        print(f"DEBUG: Método não é POST, redirecionando")
    
    # Se não for POST, redirecionar para a lista
    print(f"DEBUG: Redirecionando para lista_propostas (método não POST)")
    return redirect('militares:lista_propostas')


@login_required
def concessoes_list(request):
    garantir_catalogo()
    from militares.filtros_hierarquicos_adicionais import aplicar_filtro_hierarquico_medalhas
    from militares.permissoes_hierarquicas import obter_funcao_militar_ativa
    
    # Obter função militar ativa
    funcao_usuario = obter_funcao_militar_ativa(request.user)
    
    # Base QS com ordenação (inclui internas e externas; filtros abaixo controlam a exibição)
    qs_base = (
        ConcessaoMedalha.objects
        .select_related('medalha', 'militar')
        .order_by('-data_concessao', '-criado_em')
    )
    
    # Aplicar filtro hierárquico baseado no acesso da função
    if request.user.is_superuser:
        pass  # Superusuário vê tudo
    elif funcao_usuario:
        # Aplicar filtro hierárquico apenas para concessões de militares (militar não nulo)
        # Para externos (militar nulo), manter visíveis se o usuário tiver acesso
        qs_base = aplicar_filtro_hierarquico_medalhas(qs_base, funcao_usuario, request.user)

    # Filtros
    aba = request.GET.get('aba', '')  # '', 'dom_pedro', '10', '20', '30'
    medalha = request.GET.get('medalha')
    beneficiario = request.GET.get('beneficiario')  # 'interno' ou 'externo'
    data_ini = request.GET.get('data_ini')
    data_fim = request.GET.get('data_fim')
    query = request.GET.get('q', '').strip()  # Busca por texto

    # Aplicar filtros comuns (para contadores por aba também)
    qs_filtrado = qs_base
    
    # Busca por texto
    if query:
        qs_filtrado = qs_filtrado.filter(
            Q(medalha__nome__icontains=query) |
            Q(medalha__codigo__icontains=query) |
            Q(militar__nome_completo__icontains=query) |
            Q(militar__matricula__icontains=query) |
            Q(nome_externo__icontains=query) |
            Q(documento_externo__icontains=query)
        )
    
    if beneficiario == 'interno':
        qs_filtrado = qs_filtrado.filter(militar__isnull=False)
    elif beneficiario == 'externo':
        qs_filtrado = qs_filtrado.filter(militar__isnull=True)
    if data_ini:
        qs_filtrado = qs_filtrado.filter(data_concessao__gte=data_ini)
    if data_fim:
        qs_filtrado = qs_filtrado.filter(data_concessao__lte=data_fim)

    # Contadores por aba com base nos filtros acima
    count_dom_pedro = qs_filtrado.filter(medalha__codigo='IDPII').count()
    count_ts10 = qs_filtrado.filter(medalha__codigo='TS_10').count()
    count_ts20 = qs_filtrado.filter(medalha__codigo='TS_20').count()
    count_ts30 = qs_filtrado.filter(medalha__codigo='TS_30').count()

    # Aplicar filtro de medalha específico (caso seleção direta por código)
    if medalha:
        qs_filtrado = qs_filtrado.filter(medalha__codigo=medalha)

    # Aplicar filtro por aba (sobrepõe medalha específica quando presente)
    if aba == 'dom_pedro':
        qs_final = qs_filtrado.filter(medalha__codigo='IDPII')
    elif aba == '10':
        qs_final = qs_filtrado.filter(medalha__codigo='TS_10')
    elif aba == '20':
        qs_final = qs_filtrado.filter(medalha__codigo='TS_20')
    elif aba == '30':
        qs_final = qs_filtrado.filter(medalha__codigo='TS_30')
    else:
        # Por padrão, mostrar Dom Pedro II quando nenhuma aba estiver selecionada
        qs_final = qs_filtrado.filter(medalha__codigo='IDPII')
        aba = 'dom_pedro'  # Definir aba padrão

    # Exportação CSV do resultado final
    if request.GET.get('export') == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="concessoes_medalhas.csv"'
        writer = csv.writer(response)
        writer.writerow(['Data', 'Código Medalha', 'Medalha', 'Beneficiário', 'Documento/Matricula', 'Portaria'])
        for c in qs_final:
            if c.militar:
                beneficiario_str = f"{c.militar.get_posto_graduacao_display()} {c.militar.nome_completo}"
                doc = c.militar.matricula
            else:
                beneficiario_str = c.nome_externo or ''
                doc = c.documento_externo or ''
            portaria = c.portaria_numero or ''
            if c.portaria_data:
                portaria = f"{portaria} - {c.portaria_data.strftime('%d/%m/%Y')}" if portaria else c.portaria_data.strftime('%d/%m/%Y')
            writer.writerow([
                c.data_concessao.strftime('%d/%m/%Y'),
                c.medalha.codigo,
                c.medalha.nome,
                beneficiario_str,
                doc,
                portaria,
            ])
        return response

    # Paginação
    registros_por_pagina = request.GET.get('registros', '20')
    try:
        registros_por_pagina = int(registros_por_pagina)
        if registros_por_pagina not in [10, 20, 50, 100]:
            registros_por_pagina = 20
    except ValueError:
        registros_por_pagina = 20

    paginator = Paginator(qs_final, registros_por_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    opcoes_registros = [10, 20, 50, 100]

    # Estatísticas gerais (como em promoções)
    total_concessoes = ConcessaoMedalha.objects.count()
    concessoes_este_ano = ConcessaoMedalha.objects.filter(data_concessao__year=timezone.now().year).count()
    militares_agraciados = ConcessaoMedalha.objects.filter(militar__isnull=False).values('militar').distinct().count()
    externos_agraciados = ConcessaoMedalha.objects.filter(militar__isnull=True).count()

    medalhas = Medalha.objects.filter(ativo=True).order_by('nome')
    context = {
        'concessoes': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'registros_por_pagina': registros_por_pagina,
        'query': query,
        'opcoes_registros': opcoes_registros,
        'medalhas': medalhas,
        'filtros': {
            'aba': aba or '',
            'medalha': medalha or '',
            'beneficiario': beneficiario or '',
            'data_ini': data_ini or '',
            'data_fim': data_fim or '',
        },
        'contadores_abas': {
            'dom_pedro': count_dom_pedro,
            'ts10': count_ts10,
            'ts20': count_ts20,
            'ts30': count_ts30,
        },
        'total_concessoes': total_concessoes,
        'total_propostas': PropostaMedalha.objects.count(),
        'concessoes_este_ano': concessoes_este_ano,
        'militares_agraciados': militares_agraciados,
        'externos_agraciados': externos_agraciados,
    }
    return render(request, 'militares/medalhas/concessoes_list.html', context)


@login_required
def configurar_pdf_medalhas(request):
    """Página para configurar filtros e gerar PDF de medalhas"""
    garantir_catalogo()
    
    # Obter filtros atuais da URL (se houver)
    filtros_atuais = {
        'aba': request.GET.get('aba', ''),
        'medalha': request.GET.get('medalha', ''),
        'beneficiario': request.GET.get('beneficiario', ''),
        'data_ini': request.GET.get('data_ini', ''),
        'data_fim': request.GET.get('data_fim', ''),
    }
    
    # Obter opções para os filtros
    medalhas = Medalha.objects.filter(ativo=True).order_by('nome')
    
    # Estatísticas para mostrar quantos registros serão incluídos
    qs_base = ConcessaoMedalha.objects.select_related('medalha', 'militar')
    
    # Aplicar filtros para contagem
    qs_filtrado = qs_base
    if filtros_atuais['beneficiario'] == 'interno':
        qs_filtrado = qs_filtrado.filter(militar__isnull=False)
    elif filtros_atuais['beneficiario'] == 'externo':
        qs_filtrado = qs_filtrado.filter(militar__isnull=True)
    
    if filtros_atuais['data_ini']:
        qs_filtrado = qs_filtrado.filter(data_concessao__gte=filtros_atuais['data_ini'])
    if filtros_atuais['data_fim']:
        qs_filtrado = qs_filtrado.filter(data_concessao__lte=filtros_atuais['data_fim'])
    
    if filtros_atuais['medalha']:
        qs_filtrado = qs_filtrado.filter(medalha__codigo=filtros_atuais['medalha'])
    
    # Aplicar filtro de aba
    if filtros_atuais['aba'] == 'dom_pedro':
        qs_final = qs_filtrado.filter(medalha__codigo='IDPII')
    elif filtros_atuais['aba'] == '10':
        qs_final = qs_filtrado.filter(medalha__codigo='TS_10')
    elif filtros_atuais['aba'] == '20':
        qs_final = qs_filtrado.filter(medalha__codigo='TS_20')
    elif filtros_atuais['aba'] == '30':
        qs_final = qs_filtrado.filter(medalha__codigo='TS_30')
    else:
        qs_final = qs_filtrado
    
    total_registros = qs_final.count()
    
    context = {
        'filtros': filtros_atuais,
        'medalhas': medalhas,
        'total_registros': total_registros,
    }
    
    return render(request, 'militares/medalhas/configurar_pdf.html', context)


@login_required
def concessoes_pdf(request):
    """Gera um PDF da lista de concessões de medalhas com os filtros atuais e abre em nova guia"""
    garantir_catalogo()
    # Se IDs foram enviados (selecionados), priorizar eles
    ids_selecionados = request.POST.getlist('selecionados') or request.GET.getlist('ids')
    aba = request.GET.get('aba', '')
    
    # Verificar se os IDs são de propostas ou concessões
    if ids_selecionados:
        # Primeiro, tentar buscar por propostas
        propostas = PropostaMedalha.objects.filter(pk__in=ids_selecionados)
        if propostas.exists():
            # Se encontrou propostas, usar as concessões das propostas
            concessoes_das_propostas = []
            for proposta in propostas:
                concessoes_das_propostas.extend(proposta.concessoes.all())
            
            if concessoes_das_propostas:
                qs_final = (
                    ConcessaoMedalha.objects
                    .select_related('medalha', 'militar')
                    .filter(pk__in=[c.pk for c in concessoes_das_propostas])
                    .order_by('-data_concessao', '-criado_em')
                )
                # Marcar que estamos trabalhando com propostas
                usando_propostas = True
                propostas_originais = propostas
            else:
                # Proposta sem concessões
                qs_final = ConcessaoMedalha.objects.none()
                usando_propostas = True
                propostas_originais = propostas
        else:
            # Se não encontrou propostas, tentar como concessões diretas
            qs_final = (
                ConcessaoMedalha.objects
                .select_related('medalha', 'militar')
                .filter(pk__in=ids_selecionados)
                .order_by('-data_concessao', '-criado_em')
            )
            usando_propostas = False
            propostas_originais = None
    else:
        # Base QS com ordenação (inclui internas e externas; filtros abaixo controlam a exibição)
        qs_base = (
            ConcessaoMedalha.objects
            .select_related('medalha', 'militar')
            .order_by('-data_concessao', '-criado_em')
        )

        # Filtros
        medalha = request.GET.get('medalha')
        beneficiario = request.GET.get('beneficiario')  # 'interno' ou 'externo'
        data_ini = request.GET.get('data_ini')
        data_fim = request.GET.get('data_fim')

        qs_filtrado = qs_base
        if beneficiario == 'interno':
            qs_filtrado = qs_filtrado.filter(militar__isnull=False)
        elif beneficiario == 'externo':
            qs_filtrado = qs_filtrado.filter(militar__isnull=True)
        if data_ini:
            qs_filtrado = qs_filtrado.filter(data_concessao__gte=data_ini)
        if data_fim:
            qs_filtrado = qs_filtrado.filter(data_concessao__lte=data_fim)
        if medalha:
            qs_filtrado = qs_filtrado.filter(medalha__codigo=medalha)

        if aba == 'dom_pedro':
            qs_final = qs_filtrado.filter(medalha__codigo='IDPII')
        elif aba == '10':
            qs_final = qs_filtrado.filter(medalha__codigo='TS_10')
        elif aba == '20':
            qs_final = qs_filtrado.filter(medalha__codigo='TS_20')
        elif aba == '30':
            qs_final = qs_filtrado.filter(medalha__codigo='TS_30')
        else:
            qs_final = qs_filtrado
        
        usando_propostas = False
        propostas_originais = None
    


    # Montar PDF com reportlab
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    import os

    # DEBUG: Log das variáveis principais
    print(f"DEBUG: ids_selecionados = {ids_selecionados}")
    print(f"DEBUG: usando_propostas = {usando_propostas}")
    print(f"DEBUG: propostas_originais = {propostas_originais}")
    print(f"DEBUG: qs_final.count() = {qs_final.count() if qs_final else 'None'}")
    print(f"DEBUG: Condição usando_propostas and propostas_originais = {usando_propostas and propostas_originais}")
    print(f"DEBUG: Tipo de propostas_originais = {type(propostas_originais)}")
    if propostas_originais:
        print(f"DEBUG: propostas_originais.exists() = {propostas_originais.exists()}")
        print(f"DEBUG: propostas_originais.count() = {propostas_originais.count()}")
        print(f"DEBUG: IDs das propostas = {[p.pk for p in propostas_originais]}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=36, bottomMargin=36, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading2'], alignment=1)
    normal = styles['Normal']
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)

    elementos = []
    
    # Logo do CBMEPI
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        elementos.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
        elementos.append(Spacer(1, 6))
    
    # Cabeçalho institucional padrão do sistema
    cabecalho_institucional = [
        "GOVERNO DO ESTADO DO PIAUÍ",
        "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
        "COMANDO GERAL",
        "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    
    # Estilo para o cabeçalho
    style_cabecalho = ParagraphStyle('Cabecalho', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=2)
    
    for linha in cabecalho_institucional:
        elementos.append(Paragraph(linha, style_cabecalho))
    
    elementos.append(Spacer(1, 10))
    
    # Título centralizado e sublinhado
    if usando_propostas and propostas_originais:
        proposta_principal = propostas_originais.first()
        titulo_formatado = f'<u>PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA "IMPERADOR DOM PEDRO II" Nº {proposta_principal.numero_proposta}/2025</u>'
    else:
        titulo_formatado = f'<u>PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA "IMPERADOR DOM PEDRO II"</u>'
    elementos.append(Paragraph(titulo_formatado, ParagraphStyle('Titulo', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=16)))

    # Se for Dom Pedro II, agrupar por categoria em ordem: Civis, FFAA, Coirmãs, CBMEPI
    somente_dom_pedro = qs_final.exists() and qs_final.filter(medalha__codigo='IDPII').count() == qs_final.count()
    if aba == 'dom_pedro' or somente_dom_pedro:
        # 1) Personalidades Civis
        civis = list(qs_final.filter(militar__isnull=True, categoria_externa='CIVIL'))
        if civis:
            elementos.append(Spacer(1, 12))
            elementos.append(Paragraph('PERSONALIDADES CIVIS', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
            dados = [['Nº', 'Nome', 'Função', 'Instituição']]
            for i, c in enumerate(civis, 1):
                dados.append([
                    str(i),
                    c.nome_externo or '',
                    c.funcao_externa or '',
                    c.orgao_externo or '',
                ])
            tabela = Table(dados, repeatRows=1, colWidths=[25, 200, 130, 145])
            tabela.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
                ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
                ('ALIGN', (2,1), (2,-1), 'LEFT'),    # Função alinhada à esquerda
                ('ALIGN', (3,1), (3,-1), 'LEFT'),    # Instituição alinhada à esquerda
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
                ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
                ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
                ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
                ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
            ]))
            elementos.append(tabela)
            elementos.append(Spacer(1, 16))

        # 2) Membros das Forças Armadas (ordenar por posto texto, depois nome)
        ffaa = list(qs_final.filter(militar__isnull=True, categoria_externa='MILITAR_FFAA'))
        if ffaa:
            elementos.append(Spacer(1, 12))
            elementos.append(Paragraph('MILITARES DAS FORÇAS ARMADAS', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
            ffaa_sorted = sorted(ffaa, key=lambda c: (c.posto_graduacao_externo or '', c.nome_externo or ''))
            dados = [['Nº', 'Nome', 'Posto/Graduação', 'Função']]
            for i, c in enumerate(ffaa_sorted, 1):
                dados.append([
                    str(i),
                    c.nome_externo or '',
                    c.posto_graduacao_externo or '',
                    c.funcao_externa or '',
                ])
            tabela = Table(dados, repeatRows=1, colWidths=[25, 200, 130, 145])
            tabela.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
                ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
                ('ALIGN', (2,1), (2,-1), 'LEFT'),    # Posto/Graduação alinhado à esquerda
                ('ALIGN', (3,1), (3,-1), 'LEFT'),    # Função alinhada à esquerda
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
                ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
                ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
                ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
                ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
            ]))
            elementos.append(tabela)
            elementos.append(Spacer(1, 16))

        # 3) Membros das Coirmãs (PM/CBM) por UF e posto
        coirmas = list(qs_final.filter(militar__isnull=True, categoria_externa='MILITAR_COIRMA'))
        if coirmas:
            elementos.append(Spacer(1, 12))
            elementos.append(Paragraph('MILITARES DE INSTITUIÇÕES COIRMÃS', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
            coirmas_sorted = sorted(coirmas, key=lambda c: (c.uf_externa or '', c.posto_graduacao_externo or '', c.nome_externo or ''))
            dados = [['Nº', 'Nome', 'Força', 'UF', 'Posto/Graduação', 'Função']]
            for i, c in enumerate(coirmas_sorted, 1):
                dados.append([
                    str(i),
                    c.nome_externo or '',
                    c.get_forca_externa_display() if c.forca_externa else '',
                    c.uf_externa or '',
                    c.posto_graduacao_externo or '',
                    c.funcao_externa or '',
                ])
            tabela = Table(dados, repeatRows=1, colWidths=[25, 140, 80, 25, 100, 130])
            tabela.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
                ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
                ('ALIGN', (2,1), (2,-1), 'CENTER'),  # Força centralizada
                ('ALIGN', (3,1), (3,-1), 'CENTER'),  # UF centralizada
                ('ALIGN', (4,1), (4,-1), 'LEFT'),    # Posto/Graduação alinhado à esquerda
                ('ALIGN', (5,1), (5,-1), 'LEFT'),    # Função alinhada à esquerda
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
                ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
                ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
                ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
                ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
            ]))
            elementos.append(tabela)
            elementos.append(Spacer(1, 16))

        # 4) Militares do CBMEPI
        militares_cbmepi = list(qs_final.filter(militar__isnull=False))
        if militares_cbmepi:
            elementos.append(Spacer(1, 12))
            elementos.append(Paragraph('MILITARES DO CBMEPI', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
            # Ordenar por posto (hierarquia) e depois por nome
            from .models import POSTO_GRADUACAO_CHOICES
            hierarquia_ordem = {codigo: idx for idx, (codigo, _nome) in enumerate(POSTO_GRADUACAO_CHOICES)}
            militares_cbmepi_sorted = sorted(militares_cbmepi, key=lambda c: (hierarquia_ordem.get(c.militar.posto_graduacao, 999), c.militar.nome_completo))
            
            dados = [['Nº', 'Nome', 'Posto/Graduação', 'Matrícula']]
            for i, c in enumerate(militares_cbmepi_sorted, 1):
                dados.append([
                    str(i),
                    c.militar.nome_completo,
                    c.militar.get_posto_graduacao_display(),
                    c.militar.matricula,
                ])
            tabela = Table(dados, repeatRows=1, colWidths=[25, 200, 130, 145])
            tabela.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
                ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
                ('ALIGN', (2,1), (2,-1), 'LEFT'),    # Posto/Graduação alinhado à esquerda
                ('ALIGN', (3,1), (3,-1), 'CENTER'),  # Matrícula centralizada
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
                ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
                ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
                ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
                ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
            ]))
            elementos.append(tabela)
            elementos.append(Spacer(1, 16))
    else:
        # Para outras medalhas (tempo de serviço), mostrar em uma única tabela
        if qs_final.exists():
            elementos.append(Spacer(1, 12))
            elementos.append(Paragraph('CONCESSÕES DE MEDALHAS', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
            
            dados = [['Nº', 'Data', 'Medalha', 'Beneficiário', 'Ato']]
            for i, c in enumerate(qs_final, 1):
                # Determinar o beneficiário
                if c.militar:
                    beneficiario_str = f"{c.militar.get_posto_graduacao_display()} {c.militar.nome_completo}"
                else:
                    beneficiario_str = c.nome_externo or 'N/A'
                
                # Determinar o ato
                ato_str = ""
                if c.portaria_numero:
                    ato_str = f"{ato_str} - Nº {c.portaria_numero}" if ato_str else f"Nº {c.portaria_numero}"
                if c.portaria_data:
                    ato_str = f"{ato_str} - {c.portaria_data.strftime('%d/%m/%Y')}`" if ato_str else c.portaria_data.strftime('%d/%m/%Y')

                dados.append([
                    c.data_concessao.strftime('%d/%m/%Y'),
                    c.medalha.codigo,
                    c.medalha.get_grau_tempo_servico_display() if c.medalha.tipo == 'TEMPO_SERVICO' else c.medalha.nome,
                    beneficiario_str,
                    ato_str,
                ])

            tabela = Table(dados, repeatRows=1, colWidths=[60, 60, 140, 180, 120])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elementos.append(tabela)

    # Finalizar o PDF
    doc.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="concessoes_medalhas.pdf"'
    return response

@login_required
@login_required
def elegiveis_tempo_servico(request):
    garantir_catalogo()
    hoje = timezone.now().date()
    
    # Filtros
    query = request.GET.get('q', '').strip()
    posto = request.GET.get('posto', '').strip()
    quadro = request.GET.get('quadro', '').strip()
    
    # Base query
    militares = Militar.objects.filter(classificacao='ATIVO')
    
    # Aplicar filtros
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(posto_graduacao__icontains=query) |
            Q(matricula__icontains=query)
        )
    
    if posto:
        militares = militares.filter(posto_graduacao__iexact=posto)
    
    if quadro:
        militares = militares.filter(quadro__iexact=quadro)
    
    # Obter militares que já receberam medalhas de tempo de serviço
    militares_com_medalha_10 = set(ConcessaoMedalha.objects.filter(
        medalha__codigo='TS_10', 
        militar__isnull=False
    ).values_list('militar_id', flat=True))
    
    militares_com_medalha_20 = set(ConcessaoMedalha.objects.filter(
        medalha__codigo='TS_20', 
        militar__isnull=False
    ).values_list('militar_id', flat=True))
    
    militares_com_medalha_30 = set(ConcessaoMedalha.objects.filter(
        medalha__codigo='TS_30', 
        militar__isnull=False
    ).values_list('militar_id', flat=True))
    
    elegiveis_10 = []
    elegiveis_20 = []
    elegiveis_30 = []
    
    # Mapa de hierarquia baseado na ordem definida nas choices
    hierarquia_ordem = {codigo: idx for idx, (codigo, _nome) in enumerate(POSTO_GRADUACAO_CHOICES)}
    
    for m in militares:
        anos = m.tempo_servico()
        
        # Elegibilidade cumulativa: 10 → 10; 20 → 10 e 20; 30 → 10, 20 e 30
        # Mas apenas se ainda não recebeu a medalha específica
        if anos >= 10 and m.id not in militares_com_medalha_10:
            elegiveis_10.append(m)
        if anos >= 20 and m.id not in militares_com_medalha_20:
            elegiveis_20.append(m)
        if anos >= 30 and m.id not in militares_com_medalha_30:
            elegiveis_30.append(m)
    
    # Ordenar por hierarquia (posto) e, em seguida, por numeração de antiguidade e nome
    def sort_hierarquia(lista):
        return sorted(
            lista,
            key=lambda x: (
                hierarquia_ordem.get(x.posto_graduacao, 999),
                x.numeracao_antiguidade if x.numeracao_antiguidade is not None else 999999,
                x.nome_completo
            )
        )
    
    elegiveis_10 = sort_hierarquia(elegiveis_10)
    elegiveis_20 = sort_hierarquia(elegiveis_20)
    elegiveis_30 = sort_hierarquia(elegiveis_30)
    
    return render(request, 'militares/medalhas/elegiveis_tempo_servico.html', {
        'elegiveis_10': elegiveis_10,
        'elegiveis_20': elegiveis_20,
        'elegiveis_30': elegiveis_30,
        'query': query,
        'filtros': {
            'posto': posto,
            'quadro': quadro,
        },
    })


@login_required
@login_required
def conceder_medalha_militar(request):
    garantir_catalogo()
    initial = {'data_concessao': timezone.now().date()}
    medalha_id = request.GET.get('medalha')
    # Garantir militar fixo tanto em GET quanto em POST (para manter nome após validação)
    militar_id = request.GET.get('militar') or request.POST.get('militar')
    
    # Detectar se veio da lista de elegíveis (medalhas de tempo de serviço)
    veio_dos_elegiveis = False
    if medalha_id and medalha_id in ['TS_10', 'TS_20', 'TS_30']:
        veio_dos_elegiveis = True
    
    if medalha_id:
        # Ajustar inicial para o PK quando vier código (ex.: TS_10)
        try:
            _med = Medalha.objects.get(codigo=medalha_id)
            initial['medalha'] = _med.id
        except Medalha.DoesNotExist:
            pass
    if militar_id:
        initial['militar'] = militar_id
    
    if request.method == 'POST':
        form = ConcessaoMedalhaMilitarForm(request.POST)
        if form.is_valid():
            try:
                concessao = form.save(commit=False)
                concessao.criado_por = request.user
                # Forçar medalha pré-definida quando vier de elegíveis (medalha no GET)
                if medalha_id:
                    try:
                        medalha_obj = Medalha.objects.get(codigo=medalha_id)
                        concessao.medalha = medalha_obj
                    except Medalha.DoesNotExist:
                        pass
                
                # Se veio dos elegíveis, os campos de indicação são opcionais (podem ficar vazios)
                # Não preenchemos automaticamente, deixamos o usuário decidir
                
                concessao.save()
                messages.success(request, 'Concessão registrada com sucesso!')
                return redirect('militares:concessoes_list')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {str(e)}')
                # Log do erro para debug
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao salvar concessão: {str(e)}')
        else:
            # Se o formulário não for válido, mostrar erros
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo {field}: {error}')
    else:
        form = ConcessaoMedalhaMilitarForm(initial=initial)
        
        # Se veio dos elegíveis, tornar os campos de indicação não obrigatórios
        if veio_dos_elegiveis:
            form.fields['indicado_por_nome'].required = False
            form.fields['indicado_por_funcao'].required = False
            # Campos podem ficar vazios - não preenchemos automaticamente
    
    medalha_predefinida = None
    if medalha_id:
        try:
            medalha_predefinida = Medalha.objects.get(codigo=medalha_id)
        except Medalha.DoesNotExist:
            medalha_predefinida = None
    
    # Se veio da ficha do militar, ocultar área de elegíveis (não usada aqui) e marcar militar fixo
    militar_fixo = None
    if militar_id:
        militar_fixo = Militar.objects.filter(pk=militar_id).first()
    
    # Buscar funções ativas do usuário para o sistema de assinatura
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        status='ATIVO'
    ).select_related('funcao_militar').order_by('funcao_militar__nome')
    
    # Função atual selecionada (da sessão ou primeira disponível)
    funcao_atual = request.session.get('funcao_atual_nome', '')
    if not funcao_atual and funcoes_usuario.exists():
        funcao_atual = funcoes_usuario.first().funcao_militar.nome
    
    return render(request, 'militares/medalhas/conceder_militar.html', {
        'form': form,
        'medalha_predefinida': medalha_predefinida,
        'militar_fixo': militar_fixo,
        'veio_dos_elegiveis': veio_dos_elegiveis,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
    })


@login_required
def buscar_militares_api(request):
    """API para buscar militares via AJAX"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'militares': []})
    
    # Buscar militares ativos com busca mais abrangente
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query) |
        Q(cpf__icontains=query) |
        Q(nome_completo__istartswith=query)  # Busca por início do nome
    ).filter(classificacao='ATIVO').order_by('nome_completo')[:25]  # Aumentar limite e ordenar
    
    # Preparar dados para JSON
    militares_data = []
    for militar in militares:
        militares_data.append({
            'id': militar.id,
            'nome_completo': militar.nome_completo,
            'nome_guerra': militar.nome_guerra or '',
            'matricula': militar.matricula,
            'cpf': militar.cpf or '',
            'posto_display': militar.get_posto_graduacao_display(),
            'quadro_display': militar.get_quadro_display(),
            'situacao': militar.situacao,
            'situacao_display': militar.get_situacao_display(),
        })
    
    return JsonResponse({'militares': militares_data})


@login_required
@login_required
def conceder_medalha_externo(request):
    garantir_catalogo()
    initial = {}
    medalha_id = request.GET.get('medalha')
    categoria = request.GET.get('categoria')
    if medalha_id:
        initial['medalha'] = medalha_id
    if categoria:
        initial['categoria_externa'] = categoria
    if request.method == 'POST':
        form = ConcessaoMedalhaExternoForm(request.POST)
        if form.is_valid():
            concessao = form.save(commit=False)
            concessao.criado_por = request.user
            concessao.save()
            messages.success(request, 'Concessão registrada com sucesso!')
            return redirect('militares:concessoes_list')
    else:
        form = ConcessaoMedalhaExternoForm(initial=initial)
    return render(request, 'militares/medalhas/conceder_externo.html', {'form': form})


@login_required
@login_required
@require_POST
def cancelar_concessao(request, pk):
    concessao = get_object_or_404(ConcessaoMedalha, pk=pk)
    motivo = request.POST.get('motivo', '').strip()
    if not motivo:
        messages.error(request, 'Informe o motivo do cancelamento.')
        return redirect('militares:concessoes_list')
    concessao.cancelar(request.user, motivo)
    messages.success(request, 'Outorga cancelada com sucesso.')
    return redirect('militares:concessoes_list')


@login_required
@login_required
@require_POST
def deletar_concessao(request, pk):
    concessao = get_object_or_404(ConcessaoMedalha, pk=pk)
    concessao.delete()
    messages.success(request, 'Outorga excluída com sucesso.')
    return redirect('militares:concessoes_list')


@login_required
@login_required
def editar_concessao(request, pk):
    concessao = get_object_or_404(ConcessaoMedalha, pk=pk)
    is_interno = concessao.militar_id is not None
    FormClass = ConcessaoMedalhaMilitarForm if is_interno else ConcessaoMedalhaExternoForm
    if request.method == 'POST':
        form = FormClass(request.POST, instance=concessao)
        if form.is_valid():
            concessao = form.save()
            messages.success(request, 'Outorga atualizada com sucesso!')
            return redirect('militares:concessoes_list')
    else:
        form = FormClass(instance=concessao)
    template = 'militares/medalhas/conceder_militar.html' if is_interno else 'militares/medalhas/conceder_externo.html'
    return render(request, template, {'form': form})


@login_required
@login_required
@require_POST
def confirmar_outorga(request, pk):
    concessao = get_object_or_404(ConcessaoMedalha, pk=pk)
    concessao.outorgar(request.user)
    messages.success(request, 'Outorga confirmada com sucesso.')
    return redirect('militares:concessoes_list')


@login_required
@login_required
@require_POST
def reverter_proposta(request, pk):
    concessao = get_object_or_404(ConcessaoMedalha, pk=pk)
    concessao.reverter_para_proposta(request.user)
    messages.success(request, 'Status revertido para Proposta.')
    return redirect('militares:concessoes_list')


@login_required
@login_required
@require_POST
def confirmar_outorga_em_lote(request):
    ids = request.POST.getlist('selecionados')
    doc_tipo = request.POST.get('documento_tipo') or ''
    numero = (request.POST.get('portaria_numero') or '').strip()
    data_pub_raw = request.POST.get('portaria_data') or ''
    if not ids:
        messages.warning(request, 'Selecione ao menos um registro em Proposta para outorgar.')
        return redirect('militares:concessoes_list')
    # Validar campos do documento
    if doc_tipo not in ['PORTARIA', 'BOLETIM', 'DOE_PI']:
        messages.error(request, 'Informe o tipo de documento (Portaria, Boletim ou DOE-PI).')
        return redirect('militares:concessoes_list')
    if not numero:
        messages.error(request, 'Informe o número do documento.')
        return redirect('militares:concessoes_list')
    from datetime import datetime as _dt
    try:
        data_pub = _dt.strptime(data_pub_raw, '%Y-%m-%d').date()
    except Exception:
        messages.error(request, 'Informe uma data de publicação válida (YYYY-MM-DD).')
        return redirect('militares:concessoes_list')
    sucesso = 0
    qs = ConcessaoMedalha.objects.filter(pk__in=ids, status='PROPOSTA', cancelado=False)
    for concessao in qs:
        concessao.documento_tipo = doc_tipo
        concessao.portaria_numero = numero
        concessao.portaria_data = data_pub
        # Salvar campos do ato antes de alterar o status
        concessao.save(update_fields=['documento_tipo', 'portaria_numero', 'portaria_data'])
        concessao.outorgar(request.user)
        sucesso += 1
    if sucesso:
        messages.success(request, f'Outorga confirmada para {sucesso} registro(s).')
    else:
        messages.warning(request, 'Nenhum registro elegível selecionado para outorga.')
    return redirect('militares:concessoes_list')


@login_required
@login_required
@require_POST
def salvar_proposta(request):
    """Salva uma nova proposta com as concessões selecionadas"""
    ids_concessoes = request.POST.getlist('selecionados')
    
    if not ids_concessoes:
        messages.error(request, 'Selecione ao menos uma medalha para gerar a proposta.')
        return redirect('militares:concessoes_list')
    
    try:
        # Buscar as concessões selecionadas
        concessoes = ConcessaoMedalha.objects.filter(pk__in=ids_concessoes)
        
        # Verificar se é proposta por tempo de serviço
        is_tempo_servico = concessoes.filter(medalha__tipo='TEMPO_SERVICO').exists()
        
        # Definir título e número da proposta baseado no tipo
        if is_tempo_servico:
            # Determinar o grau mais alto entre as medalhas de tempo de serviço
            medalhas_tempo_servico = concessoes.filter(medalha__tipo='TEMPO_SERVICO')
            grau_mais_alto = None
            anos_mais_alto = 0
            
            for concessao in medalhas_tempo_servico:
                if concessao.medalha.grau_tempo_servico:
                    if '30' in concessao.medalha.grau_tempo_servico:
                        grau_mais_alto = 'OURO_30'
                        anos_mais_alto = 30
                    elif '20' in concessao.medalha.grau_tempo_servico:
                        if anos_mais_alto < 20:
                            grau_mais_alto = 'PRATA_20'
                            anos_mais_alto = 20
                    elif '10' in concessao.medalha.grau_tempo_servico:
                        if anos_mais_alto < 10:
                            grau_mais_alto = 'BRONZE_10'
                            anos_mais_alto = 10
            
            # Definir título baseado no grau
            if grau_mais_alto == 'OURO_30':
                titulo = "PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA DE TEMPO DE SERVIÇO - OURO (30 ANOS)"
                codigo_proposta = "MTS 30 - 01/2025"
            elif grau_mais_alto == 'PRATA_20':
                titulo = "PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA DE TEMPO DE SERVIÇO - PRATA (20 ANOS)"
                codigo_proposta = "MTS 20 - 01/2025"
            elif grau_mais_alto == 'BRONZE_10':
                titulo = "PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA DE TEMPO DE SERVIÇO - BRONZE (10 ANOS)"
                codigo_proposta = "MTS 10 - 01/2025"
            else:
                titulo = "PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA DE TEMPO DE SERVIÇO"
                codigo_proposta = "MTS GERAL - 01/2025"
        else:
            titulo = "PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA 'IMPERADOR DOM PEDRO II'"
            codigo_proposta = None
        
        # Criar nova proposta
        if is_tempo_servico and codigo_proposta:
            # Se for proposta por tempo de serviço, definir número personalizado antes de criar
            proposta = PropostaMedalha.objects.create(
                criado_por=request.user,
                titulo=titulo,
                numero_proposta=codigo_proposta
            )
        else:
            # Para outras propostas, deixar o modelo gerar o número automaticamente
            proposta = PropostaMedalha.objects.create(
                criado_por=request.user,
                titulo=titulo
            )
        
        # Adicionar as concessões selecionadas
        proposta.concessoes.set(concessoes)
        
        messages.success(
            request, 
            f'Proposta {proposta.numero_proposta} gerada com sucesso! '
            f'Total de {proposta.get_total_concessoes()} concessões incluídas.'
        )
        
        return redirect('militares:lista_propostas')
        
    except Exception as e:
        messages.error(request, f'Erro ao criar proposta: {str(e)}')
        return redirect('militares:lista_propostas')


@login_required
def visualizar_proposta_teste(request, pk):
    """View de teste para verificar se o problema é com o decorator"""
    try:
        proposta = PropostaMedalha.objects.get(pk=pk)
        return render(request, 'militares/medalhas/visualizar_proposta_teste.html', {
            'proposta': proposta,
            'concessoes_por_categoria': proposta.get_concessoes_por_categoria()
        })
    except PropostaMedalha.DoesNotExist:
        return render(request, 'militares/medalhas/visualizar_proposta_teste.html', {
            'proposta': None,
            'concessoes_por_categoria': {},
            'erro': f'Proposta com ID {pk} não encontrada'
        })


@login_required
@login_required
def visualizar_proposta(request, pk):
    """Visualiza uma proposta salva"""
    proposta = get_object_or_404(PropostaMedalha, pk=pk)
    
    # Buscar funções ativas do usuário
    from militares.models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        status='ATIVO'
    ).select_related('funcao_militar').order_by('funcao_militar__nome')
    
    # Função atual selecionada (da sessão ou primeira disponível)
    funcao_atual = request.session.get('funcao_atual_nome', '')
    if not funcao_atual and funcoes_usuario.exists():
        funcao_atual = funcoes_usuario.first().funcao_militar.nome
    
    return render(request, 'militares/medalhas/visualizar_proposta.html', {
        'proposta': proposta,
        'concessoes_por_categoria': proposta.get_concessoes_por_categoria(),
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
    })


@login_required
@login_required
def proposta_pdf(request, pk):
    """Gera PDF da proposta no mesmo formato das concessões"""
    garantir_catalogo()
    
    proposta = get_object_or_404(PropostaMedalha, pk=pk)
    concessoes_por_categoria = proposta.get_concessoes_por_categoria()
    
    # Importar modelo de assinatura
    from .models import AssinaturaPropostaMedalha
    
    # Montar PDF com reportlab
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    import os

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=36, bottomMargin=36, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading2'], alignment=1)
    normal = styles['Normal']
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)

    elementos = []
    
    # Logo do CBMEPI
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        elementos.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
        elementos.append(Spacer(1, 6))
    
    # Cabeçalho institucional padrão do sistema
    cabecalho_institucional = [
        "GOVERNO DO ESTADO DO PIAUÍ",
        "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
        "COMANDO GERAL",
        "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    
    # Estilo para o cabeçalho
    style_cabecalho = ParagraphStyle('Cabecalho', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=2)
    
    for linha in cabecalho_institucional:
        elementos.append(Paragraph(linha, style_cabecalho))
    
    elementos.append(Spacer(1, 10))
    
    # Título centralizado e sublinhado
    # Usar o título da proposta se for de tempo de serviço, senão usar o padrão
    if 'TEMPO DE SERVIÇO' in proposta.titulo:
        titulo_formatado = f'<u>{proposta.titulo} Nº {proposta.numero_proposta}/2025</u>'
    else:
        titulo_formatado = f'<u>PROPOSTA PARA CONCESSÃO DA OUTORGA DE MEDALHA "IMPERADOR DOM PEDRO II" Nº {proposta.numero_proposta}/2025</u>'
    elementos.append(Paragraph(titulo_formatado, ParagraphStyle('Titulo', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=16)))

    # Agrupar por categoria em ordem: Civis, FFAA, Coirmãs, CBMEPI
    # 1) Personalidades Civis
    if concessoes_por_categoria.get('civis'):
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph('PERSONALIDADES CIVIS', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
        dados = [['Nº', 'Nome', 'Função', 'Instituição']]
        for i, c in enumerate(concessoes_por_categoria['civis'], 1):
            dados.append([
                str(i),
                c.nome_externo or '',
                c.funcao_externa or '',
                c.orgao_externo or '',
            ])
        tabela = Table(dados, repeatRows=1, colWidths=[25, 200, 130, 145])
        tabela.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
            ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
            ('ALIGN', (2,1), (2,-1), 'LEFT'),    # Função alinhada à esquerda
            ('ALIGN', (3,1), (3,-1), 'LEFT'),    # Instituição alinhada à esquerda
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
            ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
            ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
            ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
            ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 16))

    # 2) Membros das Forças Armadas (ordenar por posto texto, depois nome)
    if concessoes_por_categoria.get('ffaa'):
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph('MILITARES DAS FORÇAS ARMADAS', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
        ffaa_sorted = sorted(concessoes_por_categoria['ffaa'], key=lambda c: (c.posto_graduacao_externo or '', c.nome_externo or ''))
        dados = [['Nº', 'Nome', 'Posto/Graduação', 'Função']]
        for i, c in enumerate(ffaa_sorted, 1):
            dados.append([
                str(i),
                c.nome_externo or '',
                c.posto_graduacao_externo or '',
                c.funcao_externa or '',
            ])
        tabela = Table(dados, repeatRows=1, colWidths=[25, 200, 130, 145])
        tabela.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
            ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
            ('ALIGN', (2,1), (2,-1), 'LEFT'),    # Posto/Graduação alinhado à esquerda
            ('ALIGN', (3,1), (3,-1), 'LEFT'),    # Função alinhada à esquerda
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
            ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
            ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
            ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
            ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 16))

    # 3) Membros das Coirmãs (PM/CBM) por UF e posto
    if concessoes_por_categoria.get('coirmas'):
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph('MILITARES DE INSTITUIÇÕES COIRMÃS', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
        coirmas_sorted = sorted(concessoes_por_categoria['coirmas'], key=lambda c: (c.uf_externa or '', c.posto_graduacao_externo or '', c.nome_externo or ''))
        dados = [['Nº', 'Nome', 'Força', 'UF', 'Posto/Graduação', 'Função']]
        for i, c in enumerate(coirmas_sorted, 1):
            dados.append([
                str(i),
                c.nome_externo or '',
                c.get_forca_externa_display() if c.forca_externa else '',
                c.uf_externa or '',
                c.posto_graduacao_externo or '',
                c.funcao_externa or '',
            ])
        tabela = Table(dados, repeatRows=1, colWidths=[25, 140, 80, 25, 100, 130])
        tabela.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
            ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
            ('ALIGN', (2,1), (2,-1), 'CENTER'),  # Força centralizada
            ('ALIGN', (3,1), (3,-1), 'CENTER'),  # UF centralizada
            ('ALIGN', (4,1), (4,-1), 'LEFT'),    # Posto/Graduação alinhado à esquerda
            ('ALIGN', (5,1), (5,-1), 'LEFT'),    # Função alinhada à esquerda
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
            ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
            ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
            ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
            ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 16))

    # 4) Militares do CBMEPI
    if concessoes_por_categoria.get('internos'):
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph('MILITARES DO CBMEPI', ParagraphStyle('TituloTabela', parent=styles['Heading4'], alignment=1, fontSize=12, spaceAfter=12)))
        # Ordenar por posto (hierarquia) e depois por nome
        from .models import POSTO_GRADUACAO_CHOICES
        hierarquia_ordem = {codigo: idx for idx, (codigo, _nome) in enumerate(POSTO_GRADUACAO_CHOICES)}
        militares_cbmepi_sorted = sorted(concessoes_por_categoria['internos'], key=lambda c: (hierarquia_ordem.get(c.militar.posto_graduacao, 999), c.militar.nome_completo))
        
        dados = [['Nº', 'Nome', 'Posto/Graduação', 'CPF']]
        for i, c in enumerate(militares_cbmepi_sorted, 1):
            # Criptografar CPF para exibição (mostrar apenas os primeiros 3 e últimos 2 dígitos)
            cpf = c.militar.cpf or ''
            if len(cpf) >= 11:
                cpf_criptografado = f"{cpf[:3]}.***.***-{cpf[-2:]}"
            else:
                cpf_criptografado = cpf
            dados.append([
                str(i),
                c.militar.nome_completo,
                c.militar.get_posto_graduacao_display(),
                cpf_criptografado,
            ])
        tabela = Table(dados, repeatRows=1, colWidths=[25, 200, 130, 145])
        tabela.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),  # Número centralizado
            ('ALIGN', (1,1), (1,-1), 'LEFT'),    # Nome alinhado à esquerda
            ('ALIGN', (2,1), (2,-1), 'LEFT'),    # Posto/Graduação alinhado à esquerda
            ('ALIGN', (3,1), (3,-1), 'CENTER'),  # Matrícula centralizada
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Alinhamento vertical centralizado
            ('TOPPADDING', (0,0), (-1,-1), 4),   # Padding superior
            ('BOTTOMPADDING', (0,0), (-1,-1), 4), # Padding inferior
            ('LEFTPADDING', (0,0), (-1,-1), 6),   # Padding esquerdo
            ('RIGHTPADDING', (0,0), (-1,-1), 6),  # Padding direito
        ]))
        elementos.append(tabela)
        elementos.append(Spacer(1, 16))

    # Cidade e Data por extenso (padrão dos outros PDFs do sistema)
    elementos.append(Spacer(1, 20))
    
    # Função para converter data para extenso
    def data_por_extenso(data):
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        return f"{data.day} de {meses[data.month]} de {data.year}"
    
    # Data atual para o documento
    from django.utils import timezone
    data_atual = timezone.now().date()
    data_extenso = f"Teresina, {data_por_extenso(data_atual)}"
    
    # Adicionar cidade e data centralizada
    elementos.append(Paragraph(f"<center><b>{data_extenso}</b></center>", ParagraphStyle('DataExtenso', parent=styles['Normal'], alignment=1, fontSize=11, spaceAfter=20)))
    
    # Buscar assinaturas da proposta
    assinaturas_propostas = AssinaturaPropostaMedalha.objects.filter(
        proposta=proposta
    ).order_by('-data_assinatura')
    
    if assinaturas_propostas.exists():
        # Ordenar por data de assinatura (mais recente primeiro)
        assinaturas_ordenadas = assinaturas_propostas.order_by('-data_assinatura')
        
        # PRIMEIRO: Mostrar todos os nomes e funções
        elementos.append(Spacer(1, 8))
        
        for i, assinatura in enumerate(assinaturas_ordenadas):
            # Nome e posto - seguir o mesmo padrão dos quadros de fixação
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{posto} {militar.nome_completo}"
            else:
                nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            
            # Função
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            # Adicionar nome e função centralizados
            elementos.append(Paragraph(f"<b>{nome_completo}</b>", ParagraphStyle('Assinante', parent=styles['Normal'], alignment=1, fontSize=11, spaceAfter=4)))
            elementos.append(Paragraph(f"{funcao}", ParagraphStyle('Funcao', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=8)))
        
        # SEGUNDO: Mostrar as assinaturas eletrônicas sem linhas divisórias
        elementos.append(Spacer(1, 16))
        
        for assinatura in assinaturas_ordenadas:
            # Nome e posto - seguir o mesmo padrão dos quadros de fixação
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{posto} {militar.nome_completo}"
            else:
                nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            
            # Função
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            # Data da assinatura
            from .utils import formatar_data_assinatura
            data_formatada, hora_formatada = formatar_data_assinatura(assinatura.data_assinatura)
            data_assinatura = f"{data_formatada} {hora_formatada}"
            
            # Texto da assinatura eletrônica no padrão dos outros PDFs do sistema
            texto_assinatura = (
                f"Documento assinado eletronicamente por {nome_completo}, em {data_assinatura}, "
                f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
            )
            
            # Tabela das assinaturas: Logo + Texto de assinatura (estilo SICAD)
            from .utils import obter_caminho_assinatura_eletronica
            assinatura_data = [
                [Image(obter_caminho_assinatura_eletronica(), width=2.5*cm, height=1.8*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[3*cm, 13*cm])
            assinatura_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizado
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
            ]))
            
            elementos.append(assinatura_table)
            elementos.append(Spacer(1, 10))  # Espaçamento simples entre assinaturas (sem linhas divisórias)
    else:
        # Se não houver assinaturas, mostrar mensagem
        elementos.append(Paragraph("Nenhuma assinatura eletrônica registrada", ParagraphStyle('Assinatura', parent=styles['Normal'], fontSize=9, alignment=1)))

    # Adicionar identificador de veracidade do documento
    from .utils import adicionar_autenticador_pdf
    adicionar_autenticador_pdf(elementos, proposta, request, tipo_documento='proposta')

    doc.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="proposta_{proposta.numero_proposta}.pdf"'
    return response


@login_required
def lista_propostas_teste(request):
    """View de teste para verificar se o problema é com o decorator"""
    return render(request, 'militares/medalhas/lista_propostas_teste.html', {
        'propostas': [],
        'total_propostas': 0,
        'status_choices': [],
        'status_atual': '',
    })


@login_required
@login_required
def lista_propostas(request):
    """Lista todas as propostas salvas"""
    propostas = PropostaMedalha.objects.all().order_by('-criado_em')
    
    # Filtros
    status = request.GET.get('status', '')
    if status:
        propostas = propostas.filter(status=status)
    
    # Paginação
    paginator = Paginator(propostas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'militares/medalhas/lista_propostas.html', {
        'propostas': page_obj,
        'total_propostas': propostas.count(),
        'status_choices': PropostaMedalha.STATUS_CHOICES,
        'status_atual': status,
    })



