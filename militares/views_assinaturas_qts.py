#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views para assinaturas de Quadros de Trabalho Semanal
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import QuadroTrabalhoSemanal, AssinaturaQTS, UsuarioFuncaoMilitar


def atualizar_status_qts(quadro):
    """Atualiza o status do QTS baseado na hierarquia das assinaturas"""
    # Por enquanto, apenas salvar o quadro (o status será verificado dinamicamente)
    # Se no futuro for necessário um campo status, ele pode ser adicionado ao modelo
    quadro.save()


@login_required
def dados_assinatura_qts(request, pk):
    """Buscar dados do QTS para assinatura via AJAX"""
    try:
        quadro = get_object_or_404(QuadroTrabalhoSemanal, pk=pk)
        
        # Obter funções ativas do usuário
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user
        ).select_related('funcao_militar')
        
        funcoes_data = []
        for ufm in funcoes_usuario:
            funcoes_data.append({
                'nome': ufm.funcao_militar.nome,
                'ativo': ufm.ativo
            })
        
        # Obter assinaturas do QTS e ordenar por hierarquia militar
        assinaturas = quadro.assinaturas.all()
        
        # Ordenar assinaturas por hierarquia militar (de coronel a soldado)
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
        
        assinaturas_data = []
        for assinatura in assinaturas_ordenadas:
            # Obter nome completo com posto se for militar
            nome_completo = assinatura.assinado_por.get_full_name()
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{militar.nome_completo} - {posto}"
            
            assinaturas_data.append({
                'tipo_assinatura': assinatura.tipo_assinatura,
                'tipo_assinatura_display': assinatura.get_tipo_assinatura_display(),
                'assinado_por': nome_completo,
                'data_assinatura': assinatura.data_assinatura.isoformat(),
                'funcao_assinatura': assinatura.funcao_assinatura,
                'observacoes': assinatura.observacoes
            })
        
        return JsonResponse({
            'success': True,
            'quadro': {
                'numero': quadro.numero_quadro,
                'turma': quadro.turma.identificacao,
                'data_inicio': quadro.data_inicio_semana.isoformat() if quadro.data_inicio_semana else None,
                'status': getattr(quadro, 'status', 'RASCUNHO'),
            },
            'assinaturas': assinaturas_data,
            'funcoes_usuario': funcoes_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def assinar_qts_revisao(request, pk):
    """Assinar QTS como revisor"""
    quadro = get_object_or_404(QuadroTrabalhoSemanal, pk=pk)
    
    # Verificar permissão de revisão baseada na função militar
    from .permissoes_simples import obter_funcao_militar_ativa
    funcao_usuario = obter_funcao_militar_ativa(request.user)
    if not funcao_usuario or funcao_usuario.funcao_militar.publicacao in ['DIGITADOR', 'NENHUM']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sua função não tem permissão para revisar QTS.'})
        messages.error(request, 'Sua função não tem permissão para revisar QTS.')
        return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        
        # Verificar se já existe uma assinatura de revisão deste usuário
        assinatura_existente = AssinaturaQTS.objects.filter(
            quadro=quadro,
            assinado_por=request.user,
            tipo_assinatura='REVISAO'
        ).first()
        
        if assinatura_existente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você já assinou este QTS como Revisor.'})
            messages.error(request, 'Você já assinou este QTS como Revisor.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Validar função selecionada
        if not funcao_assinatura:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Por favor, selecione uma função para a assinatura.'})
            messages.error(request, 'Por favor, selecione uma função para a assinatura.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Verificar se o usuário tem a função selecionada ativa
        funcao_usuario_selecionada = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            funcao_militar__nome=funcao_assinatura,
            ativo=True
        ).first()
        
        if not funcao_usuario_selecionada:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você não tem permissão para usar a função selecionada.'})
            messages.error(request, 'Você não tem permissão para usar a função selecionada.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Verificar se a função tem permissão para revisar
        if funcao_usuario_selecionada.funcao_militar.publicacao in ['DIGITADOR', 'NENHUM']:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'A função selecionada não tem permissão para revisar QTS.'})
            messages.error(request, 'A função selecionada não tem permissão para revisar QTS.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Criar a assinatura
        assinatura = AssinaturaQTS.objects.create(
            quadro=quadro,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura='REVISAO',
            funcao_assinatura=funcao_assinatura
        )
        
        # Atualizar status do QTS baseado na hierarquia das assinaturas
        atualizar_status_qts(quadro)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'QTS assinado como Revisor com sucesso!'})
        
        messages.success(request, 'QTS assinado como Revisor com sucesso!')
        return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
    
    # Obter funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user
    ).select_related('funcao_militar')
    
    # Obter função atual do usuário
    funcao_atual = None
    funcao_ativa = funcoes_usuario.filter(ativo=True).first()
    if funcao_ativa:
        funcao_atual = funcao_ativa.funcao_militar.nome
    
    context = {
        'quadro': quadro,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
        'tipo_assinatura': 'REVISAO',
    }
    
    return render(request, 'militares/assinar_qts.html', context)


@login_required
def assinar_qts_aprovacao(request, pk):
    """Assinar QTS como aprovador"""
    quadro = get_object_or_404(QuadroTrabalhoSemanal, pk=pk)
    
    # Verificar permissão de aprovação baseada na função militar
    from .permissoes_simples import obter_funcao_militar_ativa
    funcao_usuario = obter_funcao_militar_ativa(request.user)
    if not funcao_usuario or funcao_usuario.funcao_militar.publicacao in ['REVISOR', 'DIGITADOR', 'NENHUM']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sua função não tem permissão para aprovar QTS.'})
        messages.error(request, 'Sua função não tem permissão para aprovar QTS.')
        return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        
        # Verificar se já existe uma assinatura de aprovação deste usuário
        assinatura_existente = AssinaturaQTS.objects.filter(
            quadro=quadro,
            assinado_por=request.user,
            tipo_assinatura='APROVACAO'
        ).first()
        
        if assinatura_existente:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você já assinou este QTS como Aprovador.'})
            messages.error(request, 'Você já assinou este QTS como Aprovador.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Verificar se o QTS já foi revisado antes de permitir aprovação
        assinatura_revisao = AssinaturaQTS.objects.filter(
            quadro=quadro,
            tipo_assinatura='REVISAO'
        ).first()
        
        if not assinatura_revisao:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'O QTS precisa ser revisado antes de ser aprovado.'})
            messages.error(request, 'O QTS precisa ser revisado antes de ser aprovado.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Validar função selecionada
        if not funcao_assinatura:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Por favor, selecione uma função para a assinatura.'})
            messages.error(request, 'Por favor, selecione uma função para a assinatura.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Verificar se o usuário tem a função selecionada ativa
        funcao_usuario_selecionada = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            funcao_militar__nome=funcao_assinatura,
            ativo=True
        ).first()
        
        if not funcao_usuario_selecionada:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Você não tem permissão para usar a função selecionada.'})
            messages.error(request, 'Você não tem permissão para usar a função selecionada.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Verificar se a função tem permissão para aprovar
        if funcao_usuario_selecionada.funcao_militar.publicacao in ['DIGITADOR', 'NENHUM']:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'A função selecionada não tem permissão para aprovar QTS.'})
            messages.error(request, 'A função selecionada não tem permissão para aprovar QTS.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Criar a assinatura
        assinatura = AssinaturaQTS.objects.create(
            quadro=quadro,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura='APROVACAO',
            funcao_assinatura=funcao_assinatura
        )
        
        # Atualizar status do QTS baseado na hierarquia das assinaturas
        atualizar_status_qts(quadro)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'QTS assinado como Aprovador com sucesso!'})
        
        messages.success(request, 'QTS assinado como Aprovador com sucesso!')
        return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
    
    # Obter funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user
    ).select_related('funcao_militar')
    
    # Obter função atual do usuário
    funcao_atual = None
    funcao_ativa = funcoes_usuario.filter(ativo=True).first()
    if funcao_ativa:
        funcao_atual = funcao_ativa.funcao_militar.nome
    
    context = {
        'quadro': quadro,
        'funcoes_usuario': funcoes_usuario,
        'funcao_atual': funcao_atual,
        'tipo_assinatura': 'APROVACAO',
    }
    
    return render(request, 'militares/assinar_qts.html', context)


@login_required
def retirar_assinatura_qts(request, pk, assinatura_pk):
    """Retirar assinatura de um QTS"""
    quadro = get_object_or_404(QuadroTrabalhoSemanal, pk=pk)
    assinatura = get_object_or_404(AssinaturaQTS, pk=assinatura_pk, quadro=quadro)
    
    # Verificar se o usuário pode retirar a assinatura (apenas superusuário)
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para retirar esta assinatura.')
        return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
    
    if request.method == 'POST':
        tipo_assinatura = assinatura.tipo_assinatura
        assinatura.delete()
        
        # Atualizar status do QTS baseado nas assinaturas restantes
        atualizar_status_qts(quadro)
        
        messages.success(request, f'Assinatura de {assinatura.get_tipo_assinatura_display()} retirada com sucesso!')
        return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
        'assinatura': assinatura,
    }
    
    return render(request, 'militares/retirar_assinatura_qts.html', context)

