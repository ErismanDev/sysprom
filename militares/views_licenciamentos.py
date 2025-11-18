"""
Views para o módulo de Controle de Licenciamento de Viaturas
Gerencia o registro e controle de licenciamentos
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg, Count
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .models import LicenciamentoViatura, Viatura, Militar
from .forms import LicenciamentoViaturaForm


class LicenciamentoListView(LoginRequiredMixin, ListView):
    """Lista todos os licenciamentos"""
    model = LicenciamentoViatura
    template_name = 'militares/licenciamento_list.html'
    context_object_name = 'licenciamentos'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = LicenciamentoViatura.objects.select_related(
            'viatura', 'responsavel', 'criado_por'
        ).order_by('-ano_licenciamento', '-data_vencimento')
        
        # Filtros
        search = self.request.GET.get('search', '')
        viatura_id = self.request.GET.get('viatura', '')
        status = self.request.GET.get('status', '')
        ano = self.request.GET.get('ano', '')
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(viatura__placa__icontains=search) |
                Q(viatura__prefixo__icontains=search) |
                Q(observacoes__icontains=search)
            )
        
        if viatura_id:
            queryset = queryset.filter(viatura_id=viatura_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if ano:
            try:
                ano_int = int(ano)
                queryset = queryset.filter(ano_licenciamento=ano_int)
            except:
                pass
        
        if data_inicio:
            try:
                from datetime import datetime
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                queryset = queryset.filter(data_vencimento__gte=data_inicio_obj)
            except:
                pass
        
        if data_fim:
            try:
                from datetime import datetime
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                queryset = queryset.filter(data_vencimento__lte=data_fim_obj)
            except:
                pass
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['viatura_id'] = self.request.GET.get('viatura', '')
        context['status'] = self.request.GET.get('status', '')
        context['ano'] = self.request.GET.get('ano', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_licenciamentos'] = queryset.count()
        context['total_valor'] = queryset.aggregate(Sum('valor_licenciamento'))['valor_licenciamento__sum'] or 0
        context['media_valor'] = queryset.aggregate(Avg('valor_licenciamento'))['valor_licenciamento__avg'] or 0
        
        # Estatísticas por status
        context['total_pago'] = queryset.filter(status='PAGO').count()
        context['total_pendente'] = queryset.filter(status='PENDENTE').count()
        context['total_vencido'] = queryset.filter(status='VENCIDO').count()
        
        # Lista de viaturas para filtro
        context['viaturas'] = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Lista de status
        context['status_list'] = LicenciamentoViatura.STATUS_CHOICES
        
        # Lista de anos disponíveis
        anos = LicenciamentoViatura.objects.values_list('ano_licenciamento', flat=True).distinct().order_by('-ano_licenciamento')
        context['anos_disponiveis'] = anos
        
        # Identificar licenciamentos próximos ao vencimento (5 dias antes do proximo_vencimento)
        from datetime import date, timedelta
        hoje = date.today()
        data_alerta = hoje + timedelta(days=5)
        
        # Licenciamentos que estão próximos ao vencimento (proximo_vencimento entre hoje e 5 dias)
        licenciamentos_proximos_vencimento = []
        for licenciamento in queryset:
            if licenciamento.proximo_vencimento:
                # Verificar se está dentro do período de alerta (hoje até 5 dias no futuro)
                if hoje <= licenciamento.proximo_vencimento <= data_alerta:
                    # Verificar se ainda não foi licenciado novamente
                    # (não há um novo licenciamento com data_vencimento após o proximo_vencimento)
                    novo_licenciamento = LicenciamentoViatura.objects.filter(
                        viatura=licenciamento.viatura,
                        data_vencimento__gt=licenciamento.proximo_vencimento,
                        ativo=True
                    ).exists()
                    
                    if not novo_licenciamento:
                        licenciamentos_proximos_vencimento.append(licenciamento.pk)
        
        context['licenciamentos_proximos_vencimento'] = licenciamentos_proximos_vencimento
        
        return context


class LicenciamentoCreateView(LoginRequiredMixin, CreateView):
    """Cria novo licenciamento"""
    model = LicenciamentoViatura
    form_class = LicenciamentoViaturaForm
    template_name = 'militares/licenciamento_form.html'
    success_url = reverse_lazy('militares:licenciamento_list')
    
    def get_initial(self):
        """Define valores iniciais"""
        initial = super().get_initial()
        viatura_id = self.request.GET.get('viatura', '')
        if viatura_id:
            try:
                viatura = Viatura.objects.get(pk=viatura_id, ativo=True)
                initial['viatura'] = viatura
            except:
                pass
        
        # Definir responsável automaticamente como o militar logado
        try:
            if hasattr(self.request.user, 'militar'):
                initial['responsavel'] = self.request.user.militar
        except:
            pass
        
        return initial
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        # Se não houver responsável selecionado e o usuário estiver vinculado a um militar, usar o militar
        if not form.instance.responsavel:
            try:
                militar_usuario = form.instance.criado_por.militar if hasattr(form.instance.criado_por, 'militar') else None
                if militar_usuario:
                    form.instance.responsavel = militar_usuario
            except:
                pass
        
        messages.success(
            self.request, 
            f'Licenciamento registrado com sucesso! Ano {form.instance.ano_licenciamento} para {form.instance.viatura.placa}.'
        )
        return super().form_valid(form)


class LicenciamentoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um licenciamento"""
    model = LicenciamentoViatura
    template_name = 'militares/licenciamento_detail.html'
    context_object_name = 'licenciamento'


class LicenciamentoUpdateView(LoginRequiredMixin, UpdateView):
    """Edita um licenciamento"""
    model = LicenciamentoViatura
    form_class = LicenciamentoViaturaForm
    template_name = 'militares/licenciamento_form.html'
    success_url = reverse_lazy('militares:licenciamento_list')
    
    def get_form(self, form_class=None):
        """Garantir que o formulário seja inicializado com a instância correta"""
        form = super().get_form(form_class)
        # O DateInput customizado já deve formatar corretamente via format_value
        # Mas vamos garantir que os formatos estejam corretos
        if self.object and not self.request.POST:
            # Definir o formato dos widgets para garantir conversão correta
            form.fields['data_vencimento'].widget.format = '%Y-%m-%d'
            form.fields['data_pagamento'].widget.format = '%Y-%m-%d'
            form.fields['proximo_vencimento'].widget.format = '%Y-%m-%d'
        return form
    
    def get_context_data(self, **kwargs):
        """Garantir que o objeto esteja no contexto"""
        context = super().get_context_data(**kwargs)
        # O 'object' já está no contexto pelo UpdateView
        # Mas vamos garantir que está disponível também como 'licenciamento'
        if 'object' in context:
            context['licenciamento'] = context['object']
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Licenciamento atualizado com sucesso!'
        )
        return super().form_valid(form)


class LicenciamentoDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """Exclui um licenciamento - Apenas para superusuários"""
    model = LicenciamentoViatura
    template_name = 'militares/licenciamento_confirm_delete.html'
    success_url = reverse_lazy('militares:licenciamento_list')
    
    def test_func(self):
        """Apenas superusuários podem excluir"""
        return self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas superusuários podem excluir licenciamentos.")
        licenciamento = self.get_object()
        placa = licenciamento.viatura.placa
        messages.success(request, f'Licenciamento da viatura {placa} excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def licenciamento_por_viatura(request, viatura_id):
    """Lista licenciamentos de uma viatura específica"""
    viatura = get_object_or_404(Viatura, pk=viatura_id)
    
    # Filtros de período e status
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    status = request.GET.get('status', '')
    ano = request.GET.get('ano', '')
    
    # Ordenar do mais recente para o mais antigo
    licenciamentos = LicenciamentoViatura.objects.filter(
        viatura=viatura
    ).select_related('responsavel', 'criado_por')
    
    # Aplicar filtros
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            licenciamentos = licenciamentos.filter(data_vencimento__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            from datetime import datetime
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            licenciamentos = licenciamentos.filter(data_vencimento__lte=data_fim_obj)
        except:
            pass
    
    if status:
        licenciamentos = licenciamentos.filter(status=status)
    
    if ano:
        try:
            ano_int = int(ano)
            licenciamentos = licenciamentos.filter(ano_licenciamento=ano_int)
        except:
            pass
    
    licenciamentos = licenciamentos.order_by('-ano_licenciamento', '-data_vencimento')
    
    # Estatísticas
    total_valor = licenciamentos.aggregate(Sum('valor_licenciamento'))['valor_licenciamento__sum'] or 0
    media_valor = licenciamentos.aggregate(Avg('valor_licenciamento'))['valor_licenciamento__avg'] or 0
    
    # Estatísticas por status
    total_pago = licenciamentos.filter(status='PAGO').count()
    total_pendente = licenciamentos.filter(status='PENDENTE').count()
    total_vencido = licenciamentos.filter(status='VENCIDO').count()
    
    paginator = Paginator(licenciamentos, 30)
    page = request.GET.get('page')
    licenciamentos_page = paginator.get_page(page)
    
    context = {
        'viatura': viatura,
        'licenciamentos': licenciamentos_page,
        'total_valor': total_valor,
        'media_valor': media_valor,
        'total_pago': total_pago,
        'total_pendente': total_pendente,
        'total_vencido': total_vencido,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'status': status,
        'ano': ano,
        'status_list': LicenciamentoViatura.STATUS_CHOICES,
    }
    
    return render(request, 'militares/licenciamento_por_viatura.html', context)

