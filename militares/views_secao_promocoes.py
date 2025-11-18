from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import SecaoPromocoes, Militar
from .forms_secao_promocoes import SecaoPromocoesForm, SecaoPromocoesSearchForm
from .permissoes_secao_promocoes import (
    pode_gerenciar_secao_promocoes,
    pode_criar_secao_promocoes,
    pode_editar_secao_promocoes,
    pode_excluir_secao_promocoes,
    pode_ativar_desativar_secao_promocoes,
    pode_acessar_dashboard_secao_promocoes,
    obter_funcoes_secao_promocoes
)


@login_required
def secao_promocoes_list(request):
    """Lista todas as seções de promoções"""
    # Verificar permissão
    if not pode_gerenciar_secao_promocoes(request.user):
        messages.error(request, 'Você não tem permissão para visualizar seções de promoções.')
        return redirect('militares:militar_list')
    
    # Filtros
    form = SecaoPromocoesSearchForm(request.GET)
    secoes = SecaoPromocoes.objects.all()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        status = form.cleaned_data.get('status')
        chefe = form.cleaned_data.get('chefe')
        
        if query:
            secoes = secoes.filter(
                Q(nome__icontains=query) |
                Q(sigla__icontains=query) |
                Q(descricao__icontains=query)
            )
        
        if status:
            secoes = secoes.filter(status=status)
        
        if chefe:
            secoes = secoes.filter(chefe=chefe)
    
    # Ordenação
    secoes = secoes.order_by('nome')
    
    # Paginação
    paginator = Paginator(secoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_secoes': secoes.count(),
        'can_edit': pode_gerenciar_secao_promocoes(request.user),
    }
    
    return render(request, 'militares/secao_promocoes/secao_promocoes_list.html', context)


@login_required
def secao_promocoes_detail(request, pk):
    """Detalhes de uma seção de promoções"""
    # Verificar permissão
    if not pode_gerenciar_secao_promocoes(request.user):
        messages.error(request, 'Você não tem permissão para visualizar seções de promoções.')
        return redirect('militares:militar_list')
    
    secao = get_object_or_404(SecaoPromocoes, pk=pk)
    
    context = {
        'secao': secao,
        'can_edit': pode_gerenciar_secao_promocoes(request.user),
    }
    
    return render(request, 'militares/secao_promocoes/secao_promocoes_detail.html', context)


@login_required
def secao_promocoes_create(request):
    """Criar nova seção de promoções"""
    # Verificar permissão
    if not pode_criar_secao_promocoes(request.user):
        messages.error(request, 'Você não tem permissão para criar seções de promoções.')
        return redirect('militares:secao_promocoes_list')
    
    if request.method == 'POST':
        form = SecaoPromocoesForm(request.POST)
        if form.is_valid():
            secao = form.save()
            messages.success(request, f'Seção de promoções "{secao.nome}" criada com sucesso!')
            return redirect('militares:secao_promocoes_detail', pk=secao.pk)
    else:
        form = SecaoPromocoesForm()
    
    context = {
        'form': form,
        'title': 'Nova Seção de Promoções',
        'action': 'create'
    }
    
    return render(request, 'militares/secao_promocoes/secao_promocoes_form.html', context)


@login_required
def secao_promocoes_edit(request, pk):
    """Editar seção de promoções"""
    # Verificar permissão
    if not pode_editar_secao_promocoes(request.user):
        messages.error(request, 'Você não tem permissão para editar seções de promoções.')
        return redirect('militares:secao_promocoes_list')
    
    secao = get_object_or_404(SecaoPromocoes, pk=pk)
    
    if request.method == 'POST':
        form = SecaoPromocoesForm(request.POST, instance=secao)
        if form.is_valid():
            secao = form.save()
            messages.success(request, f'Seção de promoções "{secao.nome}" atualizada com sucesso!')
            return redirect('militares:secao_promocoes_detail', pk=secao.pk)
    else:
        form = SecaoPromocoesForm(instance=secao)
    
    context = {
        'form': form,
        'secao': secao,
        'title': f'Editar Seção de Promoções - {secao.nome}',
        'action': 'update'
    }
    
    return render(request, 'militares/secao_promocoes/secao_promocoes_form.html', context)


@login_required
def secao_promocoes_delete(request, pk):
    """Excluir seção de promoções"""
    # Verificar permissão
    if not pode_excluir_secao_promocoes(request.user):
        messages.error(request, 'Você não tem permissão para excluir seções de promoções.')
        return redirect('militares:secao_promocoes_list')
    
    secao = get_object_or_404(SecaoPromocoes, pk=pk)
    
    if request.method == 'POST':
        nome_secao = secao.nome
        secao.delete()
        messages.success(request, f'Seção de promoções "{nome_secao}" excluída com sucesso!')
        return redirect('militares:secao_promocoes_list')
    
    context = {
        'secao': secao,
    }
    
    return render(request, 'militares/secao_promocoes/secao_promocoes_confirm_delete.html', context)


@login_required
@require_http_methods(["POST"])
def secao_promocoes_ativar(request, pk):
    """Ativar seção de promoções"""
    # Verificar permissão
    if not pode_ativar_desativar_secao_promocoes(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    secao = get_object_or_404(SecaoPromocoes, pk=pk)
    secao.ativar(request.user)
    
    return JsonResponse({
        'success': True, 
        'message': f'Seção "{secao.nome}" ativada com sucesso!',
        'status': secao.status
    })


@login_required
@require_http_methods(["POST"])
def secao_promocoes_desativar(request, pk):
    """Desativar seção de promoções"""
    # Verificar permissão
    if not pode_ativar_desativar_secao_promocoes(request.user):
        return JsonResponse({'success': False, 'message': 'Sem permissão'})
    
    secao = get_object_or_404(SecaoPromocoes, pk=pk)
    secao.desativar(request.user)
    
    return JsonResponse({
        'success': True, 
        'message': f'Seção "{secao.nome}" desativada com sucesso!',
        'status': secao.status
    })


@login_required
def secao_promocoes_dashboard(request):
    """Dashboard da seção de promoções"""
    # Verificar permissão
    if not pode_acessar_dashboard_secao_promocoes(request.user):
        messages.error(request, 'Você não tem permissão para acessar o dashboard da seção de promoções.')
        return redirect('militares:militar_list')
    
    # Estatísticas
    total_secoes = SecaoPromocoes.objects.count()
    secoes_ativas = SecaoPromocoes.objects.filter(status='ATIVA').count()
    secoes_inativas = SecaoPromocoes.objects.filter(status='INATIVA').count()
    secoes_suspensas = SecaoPromocoes.objects.filter(status='SUSPENSA').count()
    
    # Seções recentes
    secoes_recentes = SecaoPromocoes.objects.order_by('-data_criacao')[:5]
    
    # Militares com funções relacionadas
    militares_chefes = Militar.objects.filter(
        funcoes_militares__funcao_militar__nome__in=[
            'Chefe da Seção de Promoções',
            'Auxiliar da Seção de Promoções'
        ],
        funcoes_militares__ativo=True
    ).distinct().order_by('nome_completo')
    
    context = {
        'total_secoes': total_secoes,
        'secoes_ativas': secoes_ativas,
        'secoes_inativas': secoes_inativas,
        'secoes_suspensas': secoes_suspensas,
        'secoes_recentes': secoes_recentes,
        'militares_chefes': militares_chefes,
    }
    
    return render(request, 'militares/secao_promocoes/secao_promocoes_dashboard.html', context)
