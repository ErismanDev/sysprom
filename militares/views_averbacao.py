from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from .models import Averbacao, Militar, HistoricoAlteracaoAverbacao
from .forms import AverbacaoForm
from .permissoes_hierarquicas import obter_funcao_militar_ativa


class AverbacaoListView(LoginRequiredMixin, ListView):
    """Lista todas as averbações com filtros"""
    model = Averbacao
    template_name = 'militares/averbacao_list.html'
    context_object_name = 'averbacoes'
    paginate_by = 20
    
    def get_queryset(self):
        # Obter queryset base
        queryset = Averbacao.objects.select_related('militar', 'cadastrado_por').order_by('-data_averbacao', '-data_cadastro')
        
        # Aplicar filtros
        militar_id = self.request.GET.get('militar')
        militar_nome = self.request.GET.get('militar_nome')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        # Filtro por militar
        if militar_id:
            queryset = queryset.filter(militar_id=militar_id)
        elif militar_nome:
            queryset = queryset.filter(
                Q(militar__nome_completo__icontains=militar_nome) |
                Q(militar__nome_guerra__icontains=militar_nome) |
                Q(militar__matricula__icontains=militar_nome)
            )
        
        # Filtro por período
        if data_inicio:
            queryset = queryset.filter(data_averbacao__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data_averbacao__lte=data_fim)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_averbacoes'] = queryset.count()
        
        # Filtros aplicados
        context['filtro_militar'] = self.request.GET.get('militar', '')
        context['filtro_data_inicio'] = self.request.GET.get('data_inicio', '')
        context['filtro_data_fim'] = self.request.GET.get('data_fim', '')
        
        return context


class AverbacaoCreateView(LoginRequiredMixin, CreateView):
    """Cria nova averbação"""
    model = Averbacao
    form_class = AverbacaoForm
    template_name = 'militares/averbacao_form.html'
    success_url = reverse_lazy('militares:averbacao_list')
    
    def form_valid(self, form):
        with transaction.atomic():
            form.instance.cadastrado_por = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, f'Averbação registrada com sucesso para {self.object.militar.nome_guerra}!')
            return response
    
    def get_initial(self):
        initial = super().get_initial()
        # Se vier um parâmetro militar na URL, pré-selecionar
        militar_id = self.request.GET.get('militar')
        if militar_id:
            try:
                initial['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        return initial


class AverbacaoUpdateView(LoginRequiredMixin, UpdateView):
    """Atualiza uma averbação existente"""
    model = Averbacao
    form_class = AverbacaoForm
    template_name = 'militares/averbacao_form.html'
    success_url = reverse_lazy('militares:averbacao_list')
    
    def form_valid(self, form):
        # Obter o objeto antes de salvar para comparar valores
        # Precisamos fazer uma cópia dos valores antes de salvar
        averbacao_antiga = Averbacao.objects.get(pk=self.object.pk)
        
        # Salvar o formulário (isso atualiza self.object)
        response = super().form_valid(form)
        
        # Recarregar o objeto atualizado do banco
        averbacao_nova = Averbacao.objects.get(pk=self.object.pk)
        
        # Registrar alterações
        self._registrar_alteracoes(averbacao_antiga, averbacao_nova)
        
        messages.success(self.request, f'Averbação atualizada com sucesso!')
        return response
    
    def _registrar_alteracoes(self, averbacao_antiga, averbacao_nova):
        """Registra as alterações realizadas na averbação"""
        # Campos a serem monitorados
        campos_monitorados = [
            'militar',
            'tempo_contribuicao_dias',
            'aproveitamento_dias',
            'numero_ctc_inss',
            'documento_publicacao',
            'assinado_por_nome',
            'assinado_por_cargo',
            'orgao_local',
            'endereco_orgao',
            'cep_orgao',
            'cidade_estado_orgao',
            'data_averbacao',
            'observacoes',
        ]
        
        for campo in campos_monitorados:
            try:
                valor_anterior = getattr(averbacao_antiga, campo, None)
                valor_novo = getattr(averbacao_nova, campo, None)
            except:
                continue  # Campo não existe, pular
            
            # Formatar valores None, ForeignKeys, datas, etc
            def formatar_valor(valor):
                if valor is None:
                    return ''
                if hasattr(valor, 'strftime'):  # Datetime/Date
                    if hasattr(valor, 'time'):  # DateTime
                        return valor.strftime('%d/%m/%Y %H:%M')
                    else:  # Date
                        return valor.strftime('%d/%m/%Y')
                if hasattr(valor, '__str__') and not isinstance(valor, (str, int, float, bool)):
                    return str(valor)
                return str(valor)
            
            valor_anterior_formatado = formatar_valor(valor_anterior)
            valor_novo_formatado = formatar_valor(valor_novo)
            
            # Registrar apenas se houver alteração
            if valor_anterior_formatado != valor_novo_formatado:
                # Obter nome legível do campo
                try:
                    field = averbacao_nova._meta.get_field(campo)
                    nome_campo = field.verbose_name
                except:
                    nome_campo = campo.replace('_', ' ').title()
                
                HistoricoAlteracaoAverbacao.objects.create(
                    averbacao=averbacao_nova,
                    alterado_por=self.request.user,
                    campo_alterado=nome_campo,
                    valor_anterior=valor_anterior_formatado,
                    valor_novo=valor_novo_formatado
                )


class AverbacaoDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma averbação"""
    model = Averbacao
    template_name = 'militares/averbacao_detail.html'
    context_object_name = 'averbacao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # Adicionar permissões
        if funcao_atual and funcao_atual.funcao_militar:
            context['menu_permissions'] = funcao_atual.funcao_militar.get_menu_permissions()
        else:
            if self.request.user.is_superuser:
                context['menu_permissions'] = {
                    'BOTAO_AVERBACAO_EDITAR': True,
                    'BOTAO_AVERBACAO_EXCLUIR': True,
                }
            else:
                context['menu_permissions'] = {}
        
        # Adicionar histórico de alterações
        context['historico_alteracoes'] = self.object.historico_alteracoes.all().select_related('alterado_por')
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, self.object.militar)
        
        return context


class AverbacaoDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui uma averbação"""
    model = Averbacao
    template_name = 'militares/averbacao_confirm_delete.html'
    success_url = reverse_lazy('militares:averbacao_list')
    
    def delete(self, request, *args, **kwargs):
        averbacao = self.get_object()
        militar_nome = averbacao.militar.nome_guerra
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Averbação de {militar_nome} excluída com sucesso!')
        return response

