from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from datetime import date, datetime

from .models import Lotacao, Militar
from .forms import LotacaoForm, LotacaoFilterForm
from .filtros_hierarquicos import aplicar_filtro_hierarquico_lotacoes
from .permissoes_hierarquicas import obter_funcao_militar_ativa
# from .decorators import permission_required


class LotacaoListView(LoginRequiredMixin, ListView):
    """Lista todas as lotações com filtros"""
    model = Lotacao
    template_name = 'militares/lotacao_list.html'
    context_object_name = 'lotacoes'
    paginate_by = 20
    
    def get_queryset(self):
        # Obter queryset base
        queryset = Lotacao.objects.select_related('militar', 'orgao', 'grande_comando', 'unidade', 'sub_unidade').order_by('-data_inicio', '-data_cadastro')
        
        # Aplicar controle de acesso hierárquico
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        queryset = aplicar_filtro_hierarquico_lotacoes(queryset, funcao_atual, self.request.user)
        
        # Aplicar filtros adicionais
        militar_id = self.request.GET.get('militar')
        organizacao = self.request.GET.get('organizacao')
        status = self.request.GET.get('status')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        # Filtro por militar específico
        if militar_id:
            queryset = queryset.filter(militar_id=militar_id)
        
        # Filtro hierárquico de organizações - mostra apenas a organização selecionada
        if organizacao:
            if organizacao.startswith('orgao_'):
                orgao_id = organizacao.replace('orgao_', '')
                # Mostra apenas lotações que estão diretamente no órgão (sem grande comando, unidade ou sub-unidade)
                queryset = queryset.filter(
                    orgao_id=orgao_id,
                    grande_comando__isnull=True,
                    unidade__isnull=True,
                    sub_unidade__isnull=True
                )
            elif organizacao.startswith('gc_'):
                gc_id = organizacao.replace('gc_', '')
                # Mostra apenas lotações que estão diretamente no grande comando (sem unidade ou sub-unidade)
                queryset = queryset.filter(
                    grande_comando_id=gc_id,
                    unidade__isnull=True,
                    sub_unidade__isnull=True
                )
            elif organizacao.startswith('unidade_'):
                unidade_id = organizacao.replace('unidade_', '')
                # Mostra apenas lotações que estão diretamente na unidade (sem sub-unidade)
                queryset = queryset.filter(
                    unidade_id=unidade_id,
                    sub_unidade__isnull=True
                )
            elif organizacao.startswith('sub_'):
                sub_unidade_id = organizacao.replace('sub_', '')
                # Mostra apenas lotações que estão diretamente na sub-unidade
                queryset = queryset.filter(sub_unidade_id=sub_unidade_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if data_inicio:
            queryset = queryset.filter(data_inicio__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data_inicio__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = LotacaoFilterForm(self.request.GET)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # Apenas adicionar permissões específicas de botões se necessário
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Estatísticas gerais
        queryset = self.get_queryset()
        context['total_lotacoes'] = queryset.count()
        context['lotacoes_atuais'] = queryset.filter(status='ATUAL').count()
        context['lotacoes_anteriores'] = queryset.filter(status='ANTERIOR').count()
        context['lotacoes_temporarias'] = queryset.filter(status='TEMPORARIA').count()
        context['lotacoes_comando'] = queryset.filter(status='COMANDO').count()
        context['lotacoes_afastamento'] = queryset.filter(status='AFASTAMENTO').count()
        
        # Calcular tempo médio de lotação
        lotacoes_com_fim = queryset.filter(data_fim__isnull=False)
        if lotacoes_com_fim.exists():
            total_dias = sum([(l.data_fim - l.data_inicio).days for l in lotacoes_com_fim])
            context['tempo_medio_lotacao'] = total_dias / lotacoes_com_fim.count()
            context['tempo_medio_meses'] = context['tempo_medio_lotacao'] / 30
            context['tempo_medio_anos'] = context['tempo_medio_lotacao'] / 365
        else:
            context['tempo_medio_lotacao'] = 0
            context['tempo_medio_meses'] = 0
            context['tempo_medio_anos'] = 0
        
        return context


class LotacaoCreateView(LoginRequiredMixin, CreateView):
    """Cria nova lotação"""
    model = Lotacao
    form_class = LotacaoForm
    template_name = 'militares/lotacao_form.html'
    success_url = reverse_lazy('militares:lotacao_list')
    
    def form_valid(self, form):
        with transaction.atomic():
            militar = form.cleaned_data['militar']
            
            # Se está criando uma lotação atual, marcar outras como anteriores
            if form.cleaned_data['status'] == 'ATUAL':
                lotacoes_atuais = Lotacao.objects.filter(
                    militar=militar,
                    status='ATUAL'
                )
                
                # Atualizar lotações atuais para anteriores
                for lotacao in lotacoes_atuais:
                    lotacao.status = 'ANTERIOR'
                    # Se a nova lotação tem data de início, usar como data de fim da anterior
                    if form.cleaned_data.get('data_inicio'):
                        lotacao.data_fim = form.cleaned_data['data_inicio']
                    lotacao.save()
            
            response = super().form_valid(form)
            messages.success(self.request, f'Lotação criada com sucesso para {self.object.militar.nome_guerra}!')
            return response
    
    def get_initial(self):
        initial = super().get_initial()
        militar_id = self.request.GET.get('militar')
        if militar_id:
            try:
                militar = Militar.objects.get(pk=militar_id)
                initial['militar'] = militar
                
                # Buscar a lotação atual do militar
                lotacao_atual = Lotacao.objects.filter(
                    militar=militar,
                    status='ATUAL'
                ).first()
                
                if lotacao_atual:
                    # Se há lotação atual, definir como data de fim da nova lotação
                    initial['data_fim'] = lotacao_atual.data_inicio
                    # Definir a nova lotação como atual por padrão
                    initial['status'] = 'ATUAL'
                else:
                    # Se não há lotação atual, definir como atual por padrão
                    initial['status'] = 'ATUAL'
            except Militar.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova Lotação'
        context['submit_text'] = 'Criar Lotação'
        return context


class LotacaoUpdateView(LoginRequiredMixin, UpdateView):
    """Edita lotação existente"""
    model = Lotacao
    form_class = LotacaoForm
    template_name = 'militares/lotacao_form.html'
    success_url = reverse_lazy('militares:lotacao_list')
    
    def get_initial(self):
        """Garantir que os dados iniciais sejam carregados corretamente"""
        initial = super().get_initial()
        # Os dados do objeto já são carregados automaticamente pelo Django
        # Este método é apenas para garantir que não há interferência
        return initial
    
    def form_valid(self, form):
        with transaction.atomic():
            # Se está alterando para lotação atual, marcar outras como anteriores
            if form.cleaned_data['status'] == 'ATUAL':
                Lotacao.objects.filter(
                    militar=form.cleaned_data['militar'],
                    status='ATUAL'
                ).exclude(pk=self.object.pk).update(status='ANTERIOR')
            
            response = super().form_valid(form)
            messages.success(self.request, f'Lotação atualizada com sucesso!')
            return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Lotação'
        context['submit_text'] = 'Atualizar Lotação'
        return context


class LotacaoDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui lotação"""
    model = Lotacao
    template_name = 'militares/lotacao_confirm_delete.html'
    success_url = reverse_lazy('militares:lotacao_list')
    
    def delete(self, request, *args, **kwargs):
        lotacao = self.get_object()
        militar_nome = lotacao.militar.nome_guerra
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Lotação de {militar_nome} excluída com sucesso!')
        return response


class LotacaoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes da lotação"""
    model = Lotacao
    template_name = 'militares/lotacao_detail.html'
    context_object_name = 'lotacao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, self.object.militar)
        
        return context


@login_required
def lotacao_create_ajax(request):
    """Cria lotação via AJAX"""
    if request.method == 'POST':
        form = LotacaoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Se está criando uma lotação atual, marcar outras como anteriores
                if form.cleaned_data['status'] == 'ATUAL':
                    Lotacao.objects.filter(
                        militar=form.cleaned_data['militar'],
                        status='ATUAL'
                    ).update(status='ANTERIOR')
                
                lotacao = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Lotação criada com sucesso para {lotacao.militar.nome_guerra}!',
                    'lotacao_id': lotacao.id
                })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def lotacao_update_ajax(request, pk):
    """Atualiza lotação via AJAX"""
    lotacao = get_object_or_404(Lotacao, pk=pk)
    
    if request.method == 'POST':
        form = LotacaoForm(request.POST, instance=lotacao)
        if form.is_valid():
            with transaction.atomic():
                # Se está alterando para lotação atual, marcar outras como anteriores
                if form.cleaned_data['status'] == 'ATUAL':
                    Lotacao.objects.filter(
                        militar=form.cleaned_data['militar'],
                        status='ATUAL'
                    ).exclude(pk=lotacao.pk).update(status='ANTERIOR')
                
                lotacao = form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Lotação atualizada com sucesso!',
                    'lotacao_id': lotacao.id
                })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def lotacao_delete_ajax(request, pk):
    """Exclui lotação via AJAX"""
    lotacao = get_object_or_404(Lotacao, pk=pk)
    
    if request.method == 'POST':
        militar_nome = lotacao.militar.nome_guerra
        lotacao.delete()
        return JsonResponse({
            'success': True,
            'message': f'Lotação de {militar_nome} excluída com sucesso!'
        })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def lotacao_militar_list(request, militar_id):
    """Lista lotações de um militar específico"""
    from .permissoes_militares import pode_editar_militar
    
    militar = get_object_or_404(Militar, pk=militar_id)
    
    # Verificar se o usuário pode editar este militar
    if not pode_editar_militar(request.user, militar):
        messages.error(request, 'Você não tem permissão para gerenciar as lotações deste militar.')
        return redirect('militares:militar_list')
    
    lotacoes = Lotacao.objects.filter(militar=militar).order_by('-data_inicio')
    
    context = {
        'militar': militar,
        'lotacoes': lotacoes,
        'title': f'Lotações de {militar.nome_guerra}'
    }
    
    return render(request, 'militares/lotacao_militar_list.html', context)


@login_required
def lotacao_militar_ajax(request, militar_id):
    """Retorna lotações de um militar em JSON"""
    militar = get_object_or_404(Militar, pk=militar_id)
    lotacoes = Lotacao.objects.filter(militar=militar).order_by('-data_inicio')
    
    lotacoes_data = []
    for lotacao in lotacoes:
        lotacoes_data.append({
            'id': lotacao.id,
            'funcao': lotacao.funcao,
            'lotacao': lotacao.lotacao,
            'tipo_funcao': lotacao.tipo_funcao,
            'status': lotacao.status,
            'data_inicio': lotacao.data_inicio.strftime('%Y-%m-%d'),
            'data_fim': lotacao.data_fim.strftime('%Y-%m-%d') if lotacao.data_fim else None,
            'observacoes': lotacao.observacoes,
            'ativo': lotacao.ativo
        })
    
    return JsonResponse({
        'success': True,
        'militar': {
            'id': militar.id,
            'nome_guerra': militar.nome_guerra,
            'nome_completo': militar.nome_completo
        },
        'lotacoes': lotacoes_data
    })


@login_required
def lotacao_estatisticas(request):
    """Estatísticas das lotações"""
    total_lotacoes = Lotacao.objects.count()
    lotacoes_atuais = Lotacao.objects.filter(status='ATUAL').count()
    lotacoes_por_tipo = Lotacao.objects.values('tipo_funcao').annotate(
        total=Count('id')
    ).order_by('-total')
    
    lotacoes_por_status = Lotacao.objects.values('status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Top 5 militares com mais lotações
    top_militares = Lotacao.objects.values(
        'militar__nome_guerra', 'militar__posto_graduacao'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    context = {
        'total_lotacoes': total_lotacoes,
        'lotacoes_atuais': lotacoes_atuais,
        'lotacoes_por_tipo': lotacoes_por_tipo,
        'lotacoes_por_status': lotacoes_por_status,
        'top_militares': top_militares,
        'title': 'Estatísticas de Lotações'
    }
    
    return render(request, 'militares/lotacao_estatisticas.html', context)


@login_required
def ajax_buscar_militares(request):
    """Retorna militares para autocomplete no filtro de lotações"""
    from django.http import JsonResponse
    from django.db.models import Q
    
    q = request.GET.get('q', '')
    
    if q:
        militares = Militar.objects.filter(
            Q(nome_completo__icontains=q) |
            Q(nome_guerra__icontains=q) |
            Q(matricula__icontains=q)
        ).filter(classificacao='ATIVO').order_by('nome_guerra')[:20]
        
        data = [{
            'id': militar.id, 
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_guerra} - {militar.matricula}"
        } for militar in militares]
    else:
        data = []
    
    return JsonResponse({'results': data})


