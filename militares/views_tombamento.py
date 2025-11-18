"""
Views para o módulo de Tombamento de Bens Móveis
Gerencia o cadastro e controle de tombamento de bens móveis do CBMEPI
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.template.loader import render_to_string

from .models import BemMovel, TombamentoBemMovel, HistoricoTombamento, Orgao, GrandeComando, Unidade, SubUnidade, Militar
from .forms import BemMovelForm, TombamentoBemMovelForm


class BemMovelListView(LoginRequiredMixin, ListView):
    """Lista todos os bens móveis"""
    model = BemMovel
    template_name = 'militares/bem_movel_list.html'
    context_object_name = 'bens_moveis'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BemMovel.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 
            'responsavel_atual', 'criado_por'
        ).order_by('numero_tombamento')
        
        # Filtros
        search = self.request.GET.get('search', '')
        categoria = self.request.GET.get('categoria', '')
        situacao = self.request.GET.get('situacao', '')
        organizacao = self.request.GET.get('organizacao', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(numero_tombamento__icontains=search) |
                Q(descricao__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search) |
                Q(numero_serie__icontains=search) |
                Q(patrimonio__icontains=search)
            )
        
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        if situacao:
            queryset = queryset.filter(situacao=situacao)
        
        if organizacao:
            queryset = queryset.filter(
                Q(orgao_id=organizacao) |
                Q(grande_comando_id=organizacao) |
                Q(unidade_id=organizacao) |
                Q(sub_unidade_id=organizacao)
            )
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['categoria'] = self.request.GET.get('categoria', '')
        context['situacao'] = self.request.GET.get('situacao', '')
        context['organizacao'] = self.request.GET.get('organizacao', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        context['total_bens'] = BemMovel.objects.count()
        context['bens_em_uso'] = BemMovel.objects.filter(situacao='EM_USO', ativo=True).count()
        context['bens_disponiveis'] = BemMovel.objects.filter(situacao='DISPONIVEL', ativo=True).count()
        context['bens_manutencao'] = BemMovel.objects.filter(situacao='MANUTENCAO', ativo=True).count()
        
        # Listas para filtros
        context['categorias'] = BemMovel.CATEGORIA_CHOICES
        context['situacoes'] = BemMovel.SITUACAO_CHOICES
        
        # Lista de organizações para filtro
        organizacoes = []
        organizacoes.extend([(o.id, f"Órgão: {o.nome}") for o in Orgao.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(gc.id, f"Grande Comando: {gc.nome}") for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(u.id, f"Unidade: {u.nome}") for u in Unidade.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(su.id, f"Sub-Unidade: {su.nome}") for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
        context['organizacoes'] = organizacoes
        
        return context


@login_required
def bem_movel_create(request):
    """Cria um novo bem móvel via modal"""
    if request.method == 'POST':
        form = BemMovelForm(request.POST, request=request)
        if form.is_valid():
            bem_movel = form.save(commit=False)
            bem_movel.criado_por = request.user
            bem_movel.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Bem móvel criado com sucesso!',
                    'redirect': reverse('militares:bem_movel_list')
                })
            messages.success(request, 'Bem móvel criado com sucesso!')
            return redirect('militares:bem_movel_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/bem_movel_form_modal.html', {
                    'form': form,
                    'title': 'Criar Bem Móvel',
                    'action_url': reverse('militares:bem_movel_create')
                }, request=request)
                return JsonResponse({'html': html, 'success': False})
    else:
        form = BemMovelForm(request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/bem_movel_form_modal.html', {
            'form': form,
            'title': 'Criar Bem Móvel',
            'action_url': reverse('militares:bem_movel_create')
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/bem_movel_form.html', {'form': form})


@login_required
def bem_movel_update(request, pk):
    """Atualiza um bem móvel via modal"""
    bem_movel = get_object_or_404(BemMovel, pk=pk)
    
    if request.method == 'POST':
        form = BemMovelForm(request.POST, instance=bem_movel, request=request)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Bem móvel atualizado com sucesso!',
                    'redirect': reverse('militares:bem_movel_list')
                })
            messages.success(request, 'Bem móvel atualizado com sucesso!')
            return redirect('militares:bem_movel_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/bem_movel_form_modal.html', {
                    'form': form,
                    'bem_movel': bem_movel,
                    'title': 'Editar Bem Móvel',
                    'action_url': reverse('militares:bem_movel_update', args=[pk])
                }, request=request)
                return JsonResponse({'html': html, 'success': False})
    else:
        form = BemMovelForm(instance=bem_movel, request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/bem_movel_form_modal.html', {
            'form': form,
            'bem_movel': bem_movel,
            'title': 'Editar Bem Móvel',
            'action_url': reverse('militares:bem_movel_update', args=[pk])
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/bem_movel_form.html', {'form': form, 'bem_movel': bem_movel})


@login_required
def bem_movel_delete(request, pk):
    """Deleta um bem móvel"""
    bem_movel = get_object_or_404(BemMovel, pk=pk)
    
    if request.method == 'POST':
        bem_movel.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Bem móvel deletado com sucesso!'
            })
        messages.success(request, 'Bem móvel deletado com sucesso!')
        return redirect('militares:bem_movel_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/bem_movel_delete_modal.html', {
            'bem_movel': bem_movel
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/bem_movel_delete.html', {'bem_movel': bem_movel})


@login_required
def bem_movel_detail(request, pk):
    """Detalhes de um bem móvel"""
    bem_movel = get_object_or_404(BemMovel, pk=pk)
    tombamentos = TombamentoBemMovel.objects.filter(bem_movel=bem_movel).order_by('-data_tombamento')
    
    context = {
        'bem_movel': bem_movel,
        'tombamentos': tombamentos,
    }
    
    return render(request, 'militares/bem_movel_detail.html', context)


class TombamentoBemMovelListView(LoginRequiredMixin, ListView):
    """Lista todos os tombamentos"""
    model = TombamentoBemMovel
    template_name = 'militares/tombamento_list.html'
    context_object_name = 'tombamentos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TombamentoBemMovel.objects.select_related(
            'bem_movel', 'orgao_origem', 'grande_comando_origem', 
            'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino',
            'unidade_destino', 'sub_unidade_destino',
            'responsavel_origem', 'responsavel_destino', 'criado_por'
        ).order_by('-data_tombamento', '-data_criacao')
        
        # Filtros
        search = self.request.GET.get('search', '')
        tipo = self.request.GET.get('tipo', '')
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        
        if search:
            queryset = queryset.filter(
                Q(bem_movel__numero_tombamento__icontains=search) |
                Q(bem_movel__descricao__icontains=search) |
                Q(observacoes__icontains=search)
            )
        
        if tipo:
            queryset = queryset.filter(tipo_tombamento=tipo)
        
        if data_inicio:
            queryset = queryset.filter(data_tombamento__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data_tombamento__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['tipo'] = self.request.GET.get('tipo', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        
        # Estatísticas
        context['total_tombamentos'] = TombamentoBemMovel.objects.count()
        context['tombamentos_entrada'] = TombamentoBemMovel.objects.filter(tipo_tombamento='ENTRADA').count()
        context['tombamentos_transferencia'] = TombamentoBemMovel.objects.filter(tipo_tombamento='TRANSFERENCIA').count()
        context['tombamentos_baixa'] = TombamentoBemMovel.objects.filter(tipo_tombamento='BAIXA').count()
        
        # Listas para filtros
        context['tipos'] = TombamentoBemMovel.TIPO_TOMBAMENTO_CHOICES
        
        return context


@login_required
def tombamento_create(request):
    """Cria um novo tombamento via modal"""
    if request.method == 'POST':
        form = TombamentoBemMovelForm(request.POST, request=request)
        if form.is_valid():
            tombamento = form.save(commit=False)
            tombamento.criado_por = request.user
            tombamento.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Tombamento registrado com sucesso!',
                    'redirect': reverse('militares:tombamento_list')
                })
            messages.success(request, 'Tombamento registrado com sucesso!')
            return redirect('militares:tombamento_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/tombamento_form_modal.html', {
                    'form': form,
                    'title': 'Registrar Tombamento',
                    'action_url': reverse('militares:tombamento_create')
                }, request=request)
                return JsonResponse({'html': html, 'success': False})
    else:
        form = TombamentoBemMovelForm(request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/tombamento_form_modal.html', {
            'form': form,
            'title': 'Registrar Tombamento',
            'action_url': reverse('militares:tombamento_create')
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/tombamento_form.html', {'form': form})


@login_required
def tombamento_update(request, pk):
    """Atualiza um tombamento via modal"""
    tombamento = get_object_or_404(TombamentoBemMovel, pk=pk)
    
    if request.method == 'POST':
        form = TombamentoBemMovelForm(request.POST, instance=tombamento, request=request)
        if form.is_valid():
            form.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Tombamento atualizado com sucesso!',
                    'redirect': reverse('militares:tombamento_list')
                })
            messages.success(request, 'Tombamento atualizado com sucesso!')
            return redirect('militares:tombamento_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/tombamento_form_modal.html', {
                    'form': form,
                    'tombamento': tombamento,
                    'title': 'Editar Tombamento',
                    'action_url': reverse('militares:tombamento_update', args=[pk])
                }, request=request)
                return JsonResponse({'html': html, 'success': False})
    else:
        form = TombamentoBemMovelForm(instance=tombamento, request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/tombamento_form_modal.html', {
            'form': form,
            'tombamento': tombamento,
            'title': 'Editar Tombamento',
            'action_url': reverse('militares:tombamento_update', args=[pk])
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/tombamento_form.html', {'form': form, 'tombamento': tombamento})


@login_required
def tombamento_delete(request, pk):
    """Deleta um tombamento"""
    tombamento = get_object_or_404(TombamentoBemMovel, pk=pk)
    
    if request.method == 'POST':
        tombamento.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Tombamento deletado com sucesso!'
            })
        messages.success(request, 'Tombamento deletado com sucesso!')
        return redirect('militares:tombamento_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/tombamento_delete_modal.html', {
            'tombamento': tombamento
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/tombamento_delete.html', {'tombamento': tombamento})

