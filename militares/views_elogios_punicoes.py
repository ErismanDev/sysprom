from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from .models import Elogio, Punicao, Militar, PermissaoFuncao, UsuarioFuncaoMilitar
from .forms import ElogioForm, PunicaoForm
from .permissoes_militares import obter_filtros_hierarquia_usuario, obter_sessao_ativa_usuario, pode_editar_militares
from .permissoes_hierarquicas import obter_funcao_militar_ativa


def _get_pode_criar_permissao(user, modulo_criar):
    """Verifica se o usuário tem permissão para criar baseado nas permissões granulares"""
    if user.is_superuser:
        return True
    
    modulo_base = modulo_criar.replace('_CRIAR', '') if '_CRIAR' in modulo_criar else modulo_criar
    
    sessao = obter_sessao_ativa_usuario(user)
    if sessao and sessao.funcao_militar_usuario:
        funcao_militar = sessao.funcao_militar_usuario.funcao_militar
        if PermissaoFuncao.objects.filter(
            funcao_militar=funcao_militar,
            modulo=modulo_base, acesso='CRIAR', ativo=True
        ).exists():
            return True
        if PermissaoFuncao.objects.filter(
            funcao_militar=funcao_militar,
            modulo=modulo_base, acesso='EXECUTAR', ativo=True
        ).exists():
            return True
    
    funcoes_ativas_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=user, ativo=True
    ).select_related('funcao_militar')
    
    for uf in funcoes_ativas_usuario:
        if PermissaoFuncao.objects.filter(
            funcao_militar=uf.funcao_militar,
            modulo=modulo_base, acesso='CRIAR', ativo=True
        ).exists():
            return True
        if PermissaoFuncao.objects.filter(
            funcao_militar=uf.funcao_militar,
            modulo=modulo_base, acesso='EXECUTAR', ativo=True
        ).exists():
            return True
    return False


def _get_pode_editar_permissao(user, modulo_editar):
    """Verifica se o usuário tem permissão para editar baseado nas permissões granulares"""
    if user.is_superuser:
        return True
    
    modulo_base = modulo_editar.replace('_EDITAR', '') if '_EDITAR' in modulo_editar else modulo_editar
    
    sessao = obter_sessao_ativa_usuario(user)
    if sessao and sessao.funcao_militar_usuario:
        funcao_militar = sessao.funcao_militar_usuario.funcao_militar
        if PermissaoFuncao.objects.filter(
            funcao_militar=funcao_militar,
            modulo=modulo_base, acesso='EDITAR', ativo=True
        ).exists():
            return True
        if PermissaoFuncao.objects.filter(
            funcao_militar=funcao_militar,
            modulo=modulo_base, acesso='EXECUTAR', ativo=True
        ).exists():
            return True
    
    funcoes_ativas_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=user, ativo=True
    ).select_related('funcao_militar')
    
    for uf in funcoes_ativas_usuario:
        if PermissaoFuncao.objects.filter(
            funcao_militar=uf.funcao_militar,
            modulo=modulo_base, acesso='EDITAR', ativo=True
        ).exists():
            return True
        if PermissaoFuncao.objects.filter(
            funcao_militar=uf.funcao_militar,
            modulo=modulo_base, acesso='EXECUTAR', ativo=True
        ).exists():
            return True
    return False


# ==================== ELOGIOS ====================

class ElogioListView(LoginRequiredMixin, ListView):
    """Lista todos os elogios com filtros"""
    model = Elogio
    template_name = 'militares/elogio_list.html'
    context_object_name = 'elogios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Elogio.objects.select_related('militar').filter(ativo=True).order_by('-data_elogio', '-data_registro')
        
        # Aplicar filtros de hierarquia
        filtros_hierarquia = obter_filtros_hierarquia_usuario(self.request.user)
        if filtros_hierarquia:
            queryset = queryset.filter(**{f"militar__{k}": v for k, v in filtros_hierarquia.items()})
        
        # Filtro por militar específico
        militar_id = self.request.GET.get('militar')
        militar_nome = self.request.GET.get('militar_nome')
        if militar_id:
            queryset = queryset.filter(militar_id=militar_id)
        elif militar_nome:
            queryset = queryset.filter(
                Q(militar__nome_completo__icontains=militar_nome) |
                Q(militar__nome_guerra__icontains=militar_nome) |
                Q(militar__matricula__icontains=militar_nome)
            )
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por data
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if data_inicio:
            queryset = queryset.filter(data_elogio__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_elogio__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # Permissões para botões
        context['pode_criar_elogios'] = _get_pode_criar_permissao(self.request.user, 'ELOGIOS_CRIAR')
        context['pode_editar_elogios'] = _get_pode_editar_permissao(self.request.user, 'ELOGIOS_EDITAR')
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_elogios'] = queryset.count()
        context['elogios_individual'] = queryset.filter(tipo='INDIVIDUAL').count()
        context['elogios_coletivo'] = queryset.filter(tipo='COLETIVO').count()
        
        # Filtros aplicados
        context['filtro_militar'] = self.request.GET.get('militar', '')
        context['filtro_militar_nome'] = self.request.GET.get('militar_nome', '')
        context['filtro_tipo'] = self.request.GET.get('tipo', '')
        context['filtro_data_inicio'] = self.request.GET.get('data_inicio', '')
        context['filtro_data_fim'] = self.request.GET.get('data_fim', '')
        
        # Tipos de elogio
        from .models import Elogio
        context['tipos_elogio'] = Elogio.TIPO_CHOICES
        
        return context


class ElogioCreateView(LoginRequiredMixin, CreateView):
    """Cria novo elogio"""
    model = Elogio
    form_class = ElogioForm
    template_name = 'militares/elogio_form.html'
    success_url = reverse_lazy('militares:elogio_list')
    
    def get_initial(self):
        initial = super().get_initial()
        # Preencher militar se passado via GET
        militar_id = self.request.GET.get('militar')
        if militar_id:
            try:
                initial['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            messages.success(self.request, f'Elogio registrado com sucesso para {self.object.militar.nome_guerra}!')
            return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        militar_id = self.request.GET.get('militar')
        if militar_id:
            try:
                context['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        return context


class ElogioDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de um elogio"""
    model = Elogio
    template_name = 'militares/elogio_detail.html'
    context_object_name = 'elogio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pode_editar_elogios'] = _get_pode_editar_permissao(self.request.user, 'ELOGIOS_EDITAR')
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, self.object.militar)
        
        return context


class ElogioUpdateView(LoginRequiredMixin, UpdateView):
    """Edita um elogio"""
    model = Elogio
    form_class = ElogioForm
    template_name = 'militares/elogio_form.html'
    success_url = reverse_lazy('militares:elogio_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Elogio atualizado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['militar'] = self.object.militar
        return context


class ElogioDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui um elogio - apenas superusuários"""
    model = Elogio
    template_name = 'militares/elogio_confirm_delete.html'
    success_url = reverse_lazy('militares:elogio_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Apenas superusuários podem excluir elogios.')
            return redirect('militares:elogio_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Elogio excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


# ==================== PUNIÇÕES ====================

class PunicaoListView(LoginRequiredMixin, ListView):
    """Lista todas as punições com filtros"""
    model = Punicao
    template_name = 'militares/punicao_list.html'
    context_object_name = 'punicoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Punicao.objects.select_related('militar').filter(ativo=True).order_by('-data_punicao', '-data_registro')
        
        # Aplicar filtros de hierarquia
        filtros_hierarquia = obter_filtros_hierarquia_usuario(self.request.user)
        if filtros_hierarquia:
            queryset = queryset.filter(**{f"militar__{k}": v for k, v in filtros_hierarquia.items()})
        
        # Restringir visualização de punições de oficiais conforme função ativa
        sessao = obter_sessao_ativa_usuario(self.request.user)
        funcao_nome = sessao.funcao_militar_usuario.funcao_militar.nome if sessao and sessao.funcao_militar_usuario else None
        funcoes_permitidas = [
            'Comandante Geral',
            'Subcomandante Geral',
            'Diretor de Gestão de Pessoas',
            'Chefe da Seção de Inteligencia e Contra Inteligencia',
        ]
        if not self.request.user.is_superuser and funcao_nome not in funcoes_permitidas:
            postos_oficiais = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
            queryset = queryset.exclude(militar__posto_graduacao__in=postos_oficiais)
        
        # Filtro por militar específico
        militar_id = self.request.GET.get('militar')
        militar_nome = self.request.GET.get('militar_nome')
        if militar_id:
            queryset = queryset.filter(militar_id=militar_id)
        elif militar_nome:
            queryset = queryset.filter(
                Q(militar__nome_completo__icontains=militar_nome) |
                Q(militar__nome_guerra__icontains=militar_nome) |
                Q(militar__matricula__icontains=militar_nome)
            )
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtro por data
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        if data_inicio:
            queryset = queryset.filter(data_punicao__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_punicao__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # Permissões para botões
        context['pode_criar_punicoes'] = _get_pode_criar_permissao(self.request.user, 'PUNICOES_CRIAR')
        context['pode_editar_punicoes'] = _get_pode_editar_permissao(self.request.user, 'PUNICOES_EDITAR')
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_punicoes'] = queryset.count()
        
        # Filtros aplicados
        context['filtro_militar'] = self.request.GET.get('militar', '')
        context['filtro_militar_nome'] = self.request.GET.get('militar_nome', '')
        context['filtro_tipo'] = self.request.GET.get('tipo', '')
        context['filtro_data_inicio'] = self.request.GET.get('data_inicio', '')
        context['filtro_data_fim'] = self.request.GET.get('data_fim', '')
        
        # Tipos de punição
        from .models import Punicao
        context['tipos_punicao'] = Punicao.TIPO_CHOICES
        
        return context


class PunicaoCreateView(LoginRequiredMixin, CreateView):
    """Cria nova punição"""
    model = Punicao
    form_class = PunicaoForm
    template_name = 'militares/punicao_form.html'
    success_url = reverse_lazy('militares:punicao_list')
    
    def get_initial(self):
        initial = super().get_initial()
        # Preencher militar se passado via GET
        militar_id = self.request.GET.get('militar')
        if militar_id:
            try:
                initial['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            messages.success(self.request, f'Punição registrada com sucesso para {self.object.militar.nome_guerra}!')
            return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        militar_id = self.request.GET.get('militar')
        if militar_id:
            try:
                context['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        return context


class PunicaoDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma punição"""
    model = Punicao
    template_name = 'militares/punicao_detail.html'
    context_object_name = 'punicao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pode_editar_punicoes'] = _get_pode_editar_permissao(self.request.user, 'PUNICOES_EDITAR')
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, self.object.militar)
        
        return context


class PunicaoUpdateView(LoginRequiredMixin, UpdateView):
    """Edita uma punição"""
    model = Punicao
    form_class = PunicaoForm
    template_name = 'militares/punicao_form.html'
    success_url = reverse_lazy('militares:punicao_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Punição atualizada com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['militar'] = self.object.militar
        return context


class PunicaoDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui uma punição - apenas superusuários"""
    model = Punicao
    template_name = 'militares/punicao_confirm_delete.html'
    success_url = reverse_lazy('militares:punicao_list')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Apenas superusuários podem excluir punições.')
            return redirect('militares:punicao_list')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Punição excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# ==================== REDIRECIONAMENTOS PARA URLs ANTIGAS ====================

@login_required
def elogios_oficiais_list_redirect(request):
    """Redireciona URL antiga de elogios de oficiais para lista geral"""
    return redirect('militares:elogio_list')


@login_required
def elogios_pracas_list_redirect(request):
    """Redireciona URL antiga de elogios de praças para lista geral"""
    return redirect('militares:elogio_list')


@login_required
def punicoes_oficiais_list_redirect(request):
    """Redireciona URL antiga de punições de oficiais para lista geral"""
    return redirect('militares:punicao_list')


@login_required
def punicoes_pracas_list_redirect(request):
    """Redireciona URL antiga de punições de praças para lista geral"""
    return redirect('militares:punicao_list')
