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
from django.utils import timezone

from .models import PlanoFerias, Ferias, Militar, DocumentoFerias
from .forms import PlanoFeriasForm, FeriasForm, DocumentoFeriasForm
from .permissoes_hierarquicas import obter_funcao_militar_ativa
from .filtros_hierarquicos import aplicar_filtro_hierarquico_ferias, aplicar_filtro_hierarquico_militares


class PlanoFeriasListView(LoginRequiredMixin, ListView):
    """Lista todos os planos de férias"""
    model = PlanoFerias
    template_name = 'militares/ferias_list.html'
    context_object_name = 'planos'
    paginate_by = 20
    
    def get_queryset(self):
        # Obter queryset base de planos de férias
        queryset = PlanoFerias.objects.select_related('criado_por').prefetch_related('ferias').order_by('-ano_plano', '-ano_referencia', '-data_criacao')
        
        # Aplicar filtros
        ano_referencia = self.request.GET.get('ano_referencia')
        ano_plano = self.request.GET.get('ano_plano')
        status = self.request.GET.get('status')
        
        if ano_referencia:
            queryset = queryset.filter(ano_referencia=ano_referencia)
        
        if ano_plano:
            queryset = queryset.filter(ano_plano=ano_plano)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Estatísticas gerais
        queryset = self.get_queryset()
        context['total_planos'] = queryset.count()
        
        # Estatísticas de férias em todos os planos
        from .models import Ferias
        context['total_ferias_reprogramadas'] = Ferias.objects.filter(status='REPROGRAMADA').count()
        context['total_ferias_planejadas'] = Ferias.objects.filter(status='PLANEJADA').count()
        context['total_ferias_gozando'] = Ferias.objects.filter(status='GOZANDO').count()
        context['total_ferias_gozadas'] = Ferias.objects.filter(status='GOZADA').count()
        
        # Filtros aplicados
        context['filtro_ano_referencia'] = self.request.GET.get('ano_referencia', '')
        context['filtro_ano_plano'] = self.request.GET.get('ano_plano', '')
        context['filtro_status'] = self.request.GET.get('status', '')
        
        # Obter anos disponíveis para filtro
        context['anos_referencia_disponiveis'] = PlanoFerias.objects.values_list('ano_referencia', flat=True).distinct().order_by('-ano_referencia')
        context['anos_plano_disponiveis'] = PlanoFerias.objects.values_list('ano_plano', flat=True).distinct().order_by('-ano_plano')
        
        # Obter OMs disponíveis para filtro do PDF
        from .forms import get_organizacoes_hierarquicas
        context['oms_disponiveis'] = get_organizacoes_hierarquicas()
        
        # Obter meses disponíveis das férias (para filtro do PDF)
        meses_disponiveis = []
        ferias_existentes = Ferias.objects.filter(
            status__in=['PLANEJADA', 'GOZANDO', 'GOZADA']
        ).values_list('data_inicio', flat=True).distinct()
        
        meses_portugues = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        meses_anos = set()
        for data in ferias_existentes:
            meses_anos.add((data.month, data.year))
        
        meses_ordenados = sorted(meses_anos, key=lambda x: (x[1], x[0]), reverse=True)
        for mes_num, ano in meses_ordenados:
            meses_disponiveis.append({
                'valor': f"{ano}-{mes_num:02d}",
                'nome': f"{meses_portugues[mes_num]}/{ano}"
            })
        
        context['meses_disponiveis'] = meses_disponiveis
        
        # Adicionar informações de homologação para cada plano
        planos_com_homologacao = {}
        for plano in context['planos']:
            # Excluir férias reprogramadas do cálculo
            todas_ferias = plano.ferias.exclude(status='REPROGRAMADA')
            total_ferias = todas_ferias.count()
            ferias_homologadas = 0
            ferias_nao_homologadas_count = 0
            
            for ferias in todas_ferias:
                if ferias.observacoes and '✓ Homologado em' in ferias.observacoes:
                    ferias_homologadas += 1
                else:
                    ferias_nao_homologadas_count += 1
            
            planos_com_homologacao[plano.pk] = {
                'total_ferias': total_ferias,
                'ferias_homologadas': ferias_homologadas,
                'ferias_nao_homologadas': ferias_nao_homologadas_count,
                'todas_homologadas': ferias_nao_homologadas_count == 0 and total_ferias > 0
            }
        
        context['planos_homologacao'] = planos_com_homologacao
        
        return context


class PlanoFeriasCreateView(LoginRequiredMixin, CreateView):
    """Cria novo plano de férias"""
    model = PlanoFerias
    form_class = PlanoFeriasForm
    template_name = 'militares/plano_ferias_form.html'
    success_url = reverse_lazy('militares:ferias_list')
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(self.request, f'Plano de Férias criado com sucesso!')
        return super().form_valid(form)


class PlanoFeriasDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de um plano de férias"""
    model = PlanoFerias
    template_name = 'militares/plano_ferias_detail.html'
    context_object_name = 'plano'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Case, When, Value, IntegerField, Q
        
        # Obter filtros da URL
        filtro_nome = self.request.GET.get('filtro_nome', '').strip()
        filtro_cpf = self.request.GET.get('filtro_cpf', '').strip()
        filtro_om = self.request.GET.get('filtro_om', '').strip()
        filtro_status = self.request.GET.get('filtro_status', '').strip()
        filtro_mes = self.request.GET.get('filtro_mes', '').strip()
        
        # Construir filtros para férias do plano
        ferias_queryset = self.object.ferias.select_related(
            'militar'
        ).prefetch_related(
            'militar__lotacoes'
        )
        
        # Aplicar filtro hierárquico baseado na função militar
        funcao_usuario = obter_funcao_militar_ativa(self.request.user)
        ferias_queryset = aplicar_filtro_hierarquico_ferias(ferias_queryset, funcao_usuario, self.request.user)
        
        # Aplicar filtros
        if filtro_nome:
            ferias_queryset = ferias_queryset.filter(
                Q(militar__nome_completo__icontains=filtro_nome) |
                Q(militar__nome_guerra__icontains=filtro_nome)
            )
        
        if filtro_cpf:
            # Remove caracteres não numéricos do CPF para busca
            cpf_limpo = ''.join(filter(str.isdigit, filtro_cpf))
            if cpf_limpo:
                ferias_queryset = ferias_queryset.filter(militar__cpf__icontains=cpf_limpo)
        
        # Filtro por OM (Organização Militar) - deve coincidir com a lotação atual
        if filtro_om:
            from .models import Orgao, GrandeComando, Unidade, SubUnidade, Lotacao
            
            # Buscar IDs dos militares que têm lotação atual na OM selecionada
            militares_ids_om = []
            
            if filtro_om.startswith('orgao_'):
                orgao_id = filtro_om.replace('orgao_', '')
                try:
                    orgao = Orgao.objects.get(id=orgao_id)
                    lotacoes_om = Lotacao.objects.filter(
                        orgao=orgao,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except Orgao.DoesNotExist:
                    pass
            elif filtro_om.startswith('gc_'):
                gc_id = filtro_om.replace('gc_', '')
                try:
                    grande_comando = GrandeComando.objects.get(id=gc_id)
                    lotacoes_om = Lotacao.objects.filter(
                        grande_comando=grande_comando,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except GrandeComando.DoesNotExist:
                    pass
            elif filtro_om.startswith('unidade_'):
                unidade_id = filtro_om.replace('unidade_', '')
                try:
                    unidade = Unidade.objects.get(id=unidade_id)
                    lotacoes_om = Lotacao.objects.filter(
                        unidade=unidade,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except Unidade.DoesNotExist:
                    pass
            elif filtro_om.startswith('sub_'):
                sub_id = filtro_om.replace('sub_', '')
                try:
                    sub_unidade = SubUnidade.objects.get(id=sub_id)
                    lotacoes_om = Lotacao.objects.filter(
                        sub_unidade=sub_unidade,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except SubUnidade.DoesNotExist:
                    pass
            
            if militares_ids_om:
                ferias_queryset = ferias_queryset.filter(militar_id__in=militares_ids_om)
            else:
                # Se não encontrou nenhuma lotação, não retorna nada
                ferias_queryset = ferias_queryset.none()
        
        # Filtro por status
        if filtro_status:
            ferias_queryset = ferias_queryset.filter(status=filtro_status)
        
        # Filtro por mês (formato: YYYY-MM)
        if filtro_mes:
            try:
                ano, mes = filtro_mes.split('-')
                ano = int(ano)
                mes = int(mes)
                # Filtrar férias que começam no mês/ano especificado
                ferias_queryset = ferias_queryset.filter(
                    data_inicio__year=ano,
                    data_inicio__month=mes
                )
            except (ValueError, AttributeError):
                pass
        
        # Ordenar por hierarquia militar
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        
        ferias_queryset = ferias_queryset.annotate(
            ordem_hierarquia=hierarquia_ordem
        ).select_related('militar')
        
        ferias_list = list(ferias_queryset.order_by(
            'ordem_hierarquia',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo'
        ))
        
        # Extrair motivo de reprogramação para cada férias reprogramada
        import re
        ferias_com_motivo = {}
        for ferias in ferias_list:
            if ferias.status == 'REPROGRAMADA' and ferias.observacoes:
                # Procurar por "Reprogramada. Motivo: " nas observações
                match = re.search(r'Reprogramada\.\s*Motivo:\s*(.+?)(?:\n\n|\n|$)', ferias.observacoes, re.DOTALL)
                if match:
                    motivo = match.group(1).strip()
                    ferias_com_motivo[ferias.pk] = motivo
        
        context['ferias_do_plano'] = ferias_list
        context['motivos_reprogramacao'] = ferias_com_motivo
        
        # Lista de militares ativos para adicionar ao plano
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        
        militares_ativos = Militar.objects.filter(
            classificacao='ATIVO'
        ).prefetch_related(
            'lotacoes'
        ).annotate(
            ordem_hierarquia=hierarquia_ordem
        )
        
        # Aplicar filtro hierárquico aos militares ativos
        militares_ativos = aplicar_filtro_hierarquico_militares(militares_ativos, funcao_usuario, self.request.user)
        
        # Aplicar filtros aos militares ativos
        if filtro_nome:
            militares_ativos = militares_ativos.filter(
                Q(nome_completo__icontains=filtro_nome) |
                Q(nome_guerra__icontains=filtro_nome)
            )
        
        if filtro_cpf:
            cpf_limpo = ''.join(filter(str.isdigit, filtro_cpf))
            if cpf_limpo:
                militares_ativos = militares_ativos.filter(cpf__icontains=cpf_limpo)
        
        # Filtro por OM (Organização Militar) - deve coincidir com a lotação atual
        if filtro_om:
            from .models import Orgao, GrandeComando, Unidade, SubUnidade, Lotacao
            
            # Buscar IDs dos militares que têm lotação atual na OM selecionada
            militares_ids_om = []
            
            if filtro_om.startswith('orgao_'):
                orgao_id = filtro_om.replace('orgao_', '')
                try:
                    orgao = Orgao.objects.get(id=orgao_id)
                    lotacoes_om = Lotacao.objects.filter(
                        orgao=orgao,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except Orgao.DoesNotExist:
                    pass
            elif filtro_om.startswith('gc_'):
                gc_id = filtro_om.replace('gc_', '')
                try:
                    grande_comando = GrandeComando.objects.get(id=gc_id)
                    lotacoes_om = Lotacao.objects.filter(
                        grande_comando=grande_comando,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except GrandeComando.DoesNotExist:
                    pass
            elif filtro_om.startswith('unidade_'):
                unidade_id = filtro_om.replace('unidade_', '')
                try:
                    unidade = Unidade.objects.get(id=unidade_id)
                    lotacoes_om = Lotacao.objects.filter(
                        unidade=unidade,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except Unidade.DoesNotExist:
                    pass
            elif filtro_om.startswith('sub_'):
                sub_id = filtro_om.replace('sub_', '')
                try:
                    sub_unidade = SubUnidade.objects.get(id=sub_id)
                    lotacoes_om = Lotacao.objects.filter(
                        sub_unidade=sub_unidade,
                        status='ATUAL',
                        ativo=True
                    ).values_list('militar_id', flat=True).distinct()
                    militares_ids_om = list(lotacoes_om)
                except SubUnidade.DoesNotExist:
                    pass
            
            if militares_ids_om:
                militares_ativos = militares_ativos.filter(id__in=militares_ids_om)
            else:
                # Se não encontrou nenhuma lotação, não retorna nada
                militares_ativos = militares_ativos.none()
        
        militares_ativos = militares_ativos.order_by(
            'ordem_hierarquia',
            'data_promocao_atual',
            'numeracao_antiguidade',
            'nome_completo'
        )
        
        # Militares que já têm férias no plano
        militares_com_ferias = set(self.object.ferias.values_list('militar_id', flat=True))
        
        # Separar militares com e sem férias no plano
        context['militares_sem_ferias'] = [m for m in militares_ativos if m.id not in militares_com_ferias]
        context['militares_com_ferias_ids'] = militares_com_ferias
        
        # Adicionar valores dos filtros ao contexto
        context['filtro_nome'] = filtro_nome
        context['filtro_cpf'] = filtro_cpf
        context['filtro_om'] = filtro_om
        context['filtro_status'] = filtro_status
        context['filtro_mes'] = filtro_mes
        
        # Calcular meses disponíveis para filtro (baseado nas férias do plano)
        meses_disponiveis = []
        todas_ferias = self.object.ferias.exclude(data_inicio__isnull=True).values_list('data_inicio', flat=True).distinct()
        meses_anos = set()
        for data_inicio in todas_ferias:
            if data_inicio:
                meses_anos.add((data_inicio.year, data_inicio.month))
        
        # Ordenar por ano e mês (mais recente primeiro)
        meses_ordenados = sorted(meses_anos, key=lambda x: (x[0], x[1]), reverse=True)
        
        meses_portugues = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        for ano, mes in meses_ordenados:
            meses_disponiveis.append({
                'valor': f"{ano}-{mes:02d}",
                'nome': f"{meses_portugues[mes]}/{ano}"
            })
        
        context['meses_disponiveis'] = meses_disponiveis
        
        # Obter lista de OMs para o filtro
        from .forms import get_organizacoes_hierarquicas
        context['oms_disponiveis'] = get_organizacoes_hierarquicas()
        
        # Adicionar status disponíveis para filtro
        from .models import Ferias
        context['status_disponiveis'] = Ferias.STATUS_CHOICES
        
        # Obter função atual para contexto
        funcao_atual = obter_funcao_militar_ativa(self.request.user)
        context['funcao_atual'] = funcao_atual
        
        # NÃO sobrescrever menu_permissions do context processor
        # O menu_permissions já vem do context processor com todas as permissões
        
        # Verificar status de homologação das férias para aprovação do plano
        # Excluir férias reprogramadas do cálculo
        todas_ferias_plano = self.object.ferias.exclude(status='REPROGRAMADA')
        total_ferias = todas_ferias_plano.count()
        ferias_homologadas = 0
        ferias_nao_homologadas_count = 0
        
        for ferias in todas_ferias_plano:
            if ferias.observacoes and '✓ Homologado em' in ferias.observacoes:
                ferias_homologadas += 1
            else:
                ferias_nao_homologadas_count += 1
        
        context['total_ferias_plano'] = total_ferias
        context['ferias_homologadas_count'] = ferias_homologadas
        context['ferias_nao_homologadas_count'] = ferias_nao_homologadas_count
        context['todas_ferias_homologadas'] = ferias_nao_homologadas_count == 0 and total_ferias > 0
        
        return context


class PlanoFeriasUpdateView(LoginRequiredMixin, UpdateView):
    """Edita plano de férias"""
    model = PlanoFerias
    form_class = PlanoFeriasForm
    template_name = 'militares/plano_ferias_form.html'
    success_url = reverse_lazy('militares:ferias_list')
    
    def form_valid(self, form):
        # Garantir que o status não seja alterado na edição
        # Salvar o status atual antes de salvar o formulário
        status_original = self.object.status
        
        # Salvar o formulário
        response = super().form_valid(form)
        
        # Restaurar o status original se foi alterado
        self.object.refresh_from_db()
        if self.object.status != status_original:
            self.object.status = status_original
            self.object.save(update_fields=['status'])
        
        messages.success(self.request, f'Plano de Férias atualizado com sucesso!')
        return response


class PlanoFeriasDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui plano de férias"""
    model = PlanoFerias
    template_name = 'militares/plano_ferias_confirm_delete.html'
    success_url = reverse_lazy('militares:ferias_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Contar férias que serão excluídas (o CASCADE já faz isso automaticamente, mas vamos avisar)
        total_ferias = self.object.ferias.count()
        
        # Coletar militares que têm férias ativas neste plano antes de excluir
        militares_em_ferias = set()
        for ferias in self.object.ferias.filter(status='GOZANDO'):
            if ferias.militar:
                militares_em_ferias.add(ferias.militar)
        
        # Excluir o plano (o CASCADE excluirá automaticamente todas as férias relacionadas)
        messages.success(self.request, f'Plano de Férias excluído com sucesso! {total_ferias} férias associadas também foram excluídas.')
        response = super().delete(request, *args, **kwargs)
        
        # Após excluir, verificar se os militares precisam voltar para PRONTO
        for militar in militares_em_ferias:
            if militar.situacao == 'AFASTAMENTO_FERIAS':
                # Verificar se ainda há outras férias ativas (GOZANDO) para este militar
                ferias_ativas = Ferias.objects.filter(
                    militar=militar,
                    status='GOZANDO'
                ).exists()
                
                # Se não há outras férias ativas, voltar o militar para PRONTO
                if not ferias_ativas:
                    militar.situacao = 'PRONTO'
                    militar.save(update_fields=['situacao'])
        
        return response


class FeriasCreateParaPlanoView(LoginRequiredMixin, CreateView):
    """Cria novas férias vinculadas a um plano específico"""
    model = Ferias
    form_class = FeriasForm
    template_name = 'militares/ferias_form.html'
    
    def get_success_url(self):
        return reverse_lazy('militares:plano_ferias_detail', kwargs={'pk': self.kwargs['plano_id']})
    
    def get_initial(self):
        initial = super().get_initial()
        plano_id = self.kwargs.get('plano_id')
        militar_id = self.kwargs.get('militar_id')
        
        if plano_id:
            plano = PlanoFerias.objects.get(pk=plano_id)
            initial['plano'] = plano
            initial['ano_referencia'] = plano.ano_referencia
        
        if militar_id:
            initial['militar'] = Militar.objects.get(pk=militar_id)
        
        # Definir valores padrão
        from datetime import datetime, timedelta
        ano_atual = datetime.now().year
        initial['status'] = 'PLANEJADA'
        initial['tipo'] = 'INTEGRAL'
        # quantidade_dias já vem com 30 por padrão no formulário
        
        # Calcular datas padrão (início e fim do mês atual)
        hoje = datetime.now()
        initial['data_inicio'] = hoje.replace(day=1).date()
        # Último dia do mês
        if hoje.month == 12:
            initial['data_fim'] = hoje.replace(year=hoje.year + 1, month=1, day=1).date() - timedelta(days=1)
        else:
            initial['data_fim'] = hoje.replace(month=hoje.month + 1, day=1).date() - timedelta(days=1)
        
        return initial
    
    def form_valid(self, form):
        plano_id = self.kwargs.get('plano_id')
        form.instance.plano_id = plano_id
        form.instance.cadastrado_por = self.request.user
        
        # Se o plano já tem documento de aprovação, replicar para a nova férias
        if plano_id:
            try:
                plano = PlanoFerias.objects.get(pk=plano_id)
                if plano.documento_referencia and plano.numero_documento:
                    if not form.instance.documento_referencia:
                        form.instance.documento_referencia = plano.documento_referencia
                    if not form.instance.numero_documento:
                        form.instance.numero_documento = plano.numero_documento
            except PlanoFerias.DoesNotExist:
                pass
        
        response = super().form_valid(form)
        messages.success(self.request, f'Férias registradas com sucesso para {self.object.militar.nome_guerra}!')
        return response


class FeriasCreateView(LoginRequiredMixin, CreateView):
    """Cria novas férias"""
    model = Ferias
    form_class = FeriasForm
    template_name = 'militares/ferias_form.html'
    success_url = reverse_lazy('militares:ferias_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documento_form'] = DocumentoFeriasForm()
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            # Definir quem cadastrou
            form.instance.cadastrado_por = self.request.user
            
            # Garantir que o tipo tenha um valor válido se não foi preenchido
            if not form.cleaned_data.get('tipo'):
                form.instance.tipo = 'INTEGRAL'
            
            response = super().form_valid(form)
            
            # Processar upload de documento se houver
            if self.request.FILES.get('arquivo'):
                documento_form = DocumentoFeriasForm(self.request.POST, self.request.FILES)
                
                if documento_form.is_valid():
                    documento = documento_form.save(commit=False)
                    documento.ferias = self.object
                    documento.upload_por = self.request.user
                    documento.save()
                    messages.success(self.request, 'Documento enviado com sucesso!')
                else:
                    error_msg = 'Férias criadas, mas houve um problema ao processar o documento: '
                    error_msg += ', '.join([str(error) for errors in documento_form.errors.values() for error in errors])
                    messages.warning(self.request, error_msg)
            
            messages.success(self.request, f'Férias registradas com sucesso para {self.object.militar.nome_guerra}!')
            return response
    
    def get_initial(self):
        initial = super().get_initial()
        initial['status'] = 'PLANEJADA'
        initial['tipo'] = 'INTEGRAL'  # Sempre definir tipo como INTEGRAL por padrão
        from datetime import datetime
        initial['ano_referencia'] = datetime.now().year
        
        # Se houver militar_id na URL, pré-selecionar o militar
        militar_id = self.kwargs.get('militar_id')
        if militar_id:
            try:
                initial['militar'] = Militar.objects.get(pk=militar_id)
            except Militar.DoesNotExist:
                pass
        
        return initial
    
    def get_success_url(self):
        # Se houver militar_id, redirecionar para a ficha do militar
        militar_id = self.kwargs.get('militar_id')
        if militar_id:
            return reverse_lazy('militares:militar_detail', kwargs={'pk': militar_id})
        return self.success_url


class FeriasDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de férias"""
    model = Ferias
    template_name = 'militares/ferias_detail.html'
    context_object_name = 'ferias'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar documentos das férias
        context['documentos'] = self.object.documentos.all().order_by('-data_upload')
        # Calcular dias
        context['dias_ferias'] = self.object.duracao_dias
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, self.object.militar)
        
        return context


class FeriasUpdateView(LoginRequiredMixin, UpdateView):
    """Edita férias"""
    model = Ferias
    form_class = FeriasForm
    template_name = 'militares/ferias_form.html'
    success_url = reverse_lazy('militares:ferias_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o plano está aprovado
        self.object = self.get_object()
        # Permitir edição para superusuários mesmo quando o plano está aprovado
        if self.object.plano and self.object.plano.status in ['APROVADO', 'PUBLICADO'] and not request.user.is_superuser:
            messages.error(request, 'Não é possível editar férias de um plano aprovado. Use a função de reprogramar se necessário.')
            if self.object.plano:
                return redirect('militares:plano_ferias_detail', pk=self.object.plano.pk)
            return redirect('militares:ferias_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documento_form'] = DocumentoFeriasForm()
        # Adicionar documentos existentes das férias
        context['documentos'] = self.object.documentos.all().order_by('-data_upload')
        return context
    
    def get_success_url(self):
        """Redireciona para a página de detalhes do plano se houver plano associado"""
        if self.object.plano:
            return reverse('militares:plano_ferias_detail', kwargs={'pk': self.object.plano.pk})
        return super().get_success_url()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Processar upload de documento se houver (permitido na edição)
        if self.request.FILES.get('arquivo'):
            documento_form = DocumentoFeriasForm(self.request.POST, self.request.FILES)
            
            if documento_form.is_valid():
                documento = documento_form.save(commit=False)
                documento.ferias = self.object
                documento.upload_por = self.request.user
                documento.save()
                messages.success(self.request, 'Documento enviado com sucesso!')
            else:
                error_msg = 'Férias atualizadas, mas houve um problema ao processar o documento: '
                error_msg += ', '.join([str(error) for errors in documento_form.errors.values() for error in errors])
                messages.warning(self.request, error_msg)
        
        # Redirecionar para o plano se houver
        if self.object.plano:
            return redirect('militares:plano_ferias_detail', pk=self.object.plano.pk)
        
        messages.success(self.request, f'Férias atualizadas com sucesso!')
        return response


class FeriasDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui férias"""
    model = Ferias
    template_name = 'militares/ferias_confirm_delete.html'
    success_url = reverse_lazy('militares:ferias_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar se o plano está aprovado
        self.object = self.get_object()
        if self.object.plano and self.object.plano.status in ['APROVADO', 'PUBLICADO']:
            messages.error(request, 'Não é possível excluir férias de um plano aprovado. Use a função de reprogramar se necessário.')
            if self.object.plano:
                return redirect('militares:plano_ferias_detail', pk=self.object.plano.pk)
            return redirect('militares:ferias_detail', pk=self.object.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Salvar referências antes de excluir
        militar = self.object.militar
        plano_pk = None
        if self.object.plano:
            plano_pk = self.object.plano.pk
        
        # Excluir a férias
        messages.success(self.request, 'Férias excluídas com sucesso!')
        response = super().delete(request, *args, **kwargs)
        
        # Após excluir, verificar se o militar precisa voltar para PRONTO
        if militar and militar.situacao == 'AFASTAMENTO_FERIAS':
            # Verificar se ainda há outras férias ativas (GOZANDO) para este militar
            ferias_ativas = Ferias.objects.filter(
                militar=militar,
                status='GOZANDO'
            ).exists()
            
            # Se não há outras férias ativas, voltar o militar para PRONTO
            if not ferias_ativas:
                militar.situacao = 'PRONTO'
                militar.save(update_fields=['situacao'])
        
        # Redirecionar para o plano se houver
        if plano_pk:
            return redirect('militares:plano_ferias_detail', pk=plano_pk)
        
        return response


@login_required
@require_http_methods(["POST"])
def documento_ferias_upload(request, pk):
    """Upload de documento para férias"""
    try:
        ferias = get_object_or_404(Ferias, pk=pk)
        form = DocumentoFeriasForm(request.POST, request.FILES)
        
        if form.is_valid():
            documento = form.save(commit=False)
            documento.ferias = ferias
            documento.upload_por = request.user
            documento.save()
            messages.success(request, 'Documento enviado com sucesso!')
        else:
            messages.error(request, 'Erro ao enviar documento. Verifique os dados.')
            
    except Exception as e:
        messages.error(request, f'Erro ao processar documento: {str(e)}')
    
    return redirect('militares:ferias_detail', pk=pk)


@login_required
@require_http_methods(["POST"])
def documento_ferias_delete(request, documento_id):
    """Excluir documento de férias"""
    try:
        documento = get_object_or_404(DocumentoFerias, pk=documento_id)
        ferias_pk = documento.ferias.pk
        documento.delete()
        messages.success(request, 'Documento excluído com sucesso!')
        return redirect('militares:ferias_detail', pk=ferias_pk)
    except Exception as e:
        messages.error(request, f'Erro ao excluir documento: {str(e)}')
        return redirect('militares:ferias_list')


@login_required
@require_http_methods(["POST"])
def ferias_homologar(request, pk):
    """Homologa férias - apenas registra a homologação sem alterar o status"""
    try:
        ferias = get_object_or_404(Ferias, pk=pk)
        
        # Verificar se já foi homologada
        if ferias.observacoes and '✓ Homologado em' in ferias.observacoes:
            messages.warning(request, f'Estas férias já foram homologadas!')
            if ferias.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Verificar se o plano está em RASCUNHO, APROVADO ou PUBLICADO
        if ferias.plano and ferias.plano.status in ['RASCUNHO', 'APROVADO', 'PUBLICADO']:
            from django.utils import timezone
            
            # Registrar homologação nas observações sem alterar o status
            data_homologacao = timezone.now().strftime('%d/%m/%Y %H:%M')
            homologador = request.user.get_full_name() or request.user.username
            
            if ferias.observacoes:
                ferias.observacoes = f"{ferias.observacoes}\n\n✓ Homologado em {data_homologacao} por {homologador}"
            else:
                ferias.observacoes = f"✓ Homologado em {data_homologacao} por {homologador}"
            
            # NÃO ALTERAR O STATUS - salvar APENAS as observações
            # Isso evita que as regras automáticas do save() alterem o status
            status_atual = ferias.status
            ferias.save(update_fields=['observacoes'])
            
            messages.success(request, f'Férias de {ferias.militar.nome_guerra} homologada com sucesso! Status atual: {ferias.get_status_display()}.')
        else:
            messages.error(request, 'Não é possível homologar férias deste plano no status atual!')
        
        # Redirecionar para o plano se houver
        if ferias.plano:
            return redirect('militares:plano_ferias_detail', pk=ferias.plano.pk)
        return redirect('militares:ferias_detail', pk=pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao homologar férias: {str(e)}')
        return redirect('militares:ferias_list')


@login_required
@require_http_methods(["POST"])
def ferias_desomologar(request, pk):
    """Desomologa férias removendo a marcação de homologação das observações"""
    try:
        ferias = get_object_or_404(Ferias, pk=pk)
        
        # Verificar se está homologada
        if not ferias.observacoes or '✓ Homologado em' not in ferias.observacoes:
            messages.warning(request, f'Estas férias não estão homologadas!')
            if ferias.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Verificar se o plano está em RASCUNHO, APROVADO ou PUBLICADO
        if ferias.plano and ferias.plano.status in ['RASCUNHO', 'APROVADO', 'PUBLICADO']:
            # Remover a linha de homologação das observações
            linhas = ferias.observacoes.split('\n')
            linhas_filtradas = [linha for linha in linhas if '✓ Homologado em' not in linha]
            nova_observacao = '\n'.join(linhas_filtradas).strip()
            
            # Se ficou vazio, deixar None
            if not nova_observacao:
                ferias.observacoes = None
            else:
                ferias.observacoes = nova_observacao
            
            # Salvar APENAS as observações sem alterar o status
            ferias.save(update_fields=['observacoes'])
            
            messages.success(request, f'Férias de {ferias.militar.nome_guerra} desomologada com sucesso!')
        else:
            messages.error(request, 'Não é possível desomologar férias deste plano no status atual!')
        
        # Redirecionar para o plano se houver
        if ferias.plano:
            return redirect('militares:plano_ferias_detail', pk=ferias.plano.pk)
        return redirect('militares:ferias_detail', pk=pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao desomologar férias: {str(e)}')
        return redirect('militares:ferias_list')


@login_required
@require_http_methods(["POST"])
def ferias_homologar_em_massa(request, plano_id):
    """Homologa múltiplas férias de uma vez - apenas registra a homologação sem alterar o status"""
    try:
        plano = get_object_or_404(PlanoFerias, pk=plano_id)
        
        # Verificar se o plano está em RASCUNHO, APROVADO ou PUBLICADO
        if plano.status not in ['RASCUNHO', 'APROVADO', 'PUBLICADO']:
            messages.error(request, 'Não é possível homologar férias deste plano no status atual!')
            return redirect('militares:plano_ferias_detail', pk=plano_id)
        
        # Obter IDs das férias selecionadas
        ferias_ids = request.POST.getlist('ferias_ids')
        
        if not ferias_ids:
            messages.warning(request, 'Nenhuma férias foi selecionada para homologação!')
            return redirect('militares:plano_ferias_detail', pk=plano_id)
        
        # Buscar férias do plano (qualquer status)
        ferias_selecionadas = Ferias.objects.filter(
            pk__in=ferias_ids,
            plano=plano
        )
        
        if not ferias_selecionadas.exists():
            messages.warning(request, 'Nenhuma férias encontrada para homologação!')
            return redirect('militares:plano_ferias_detail', pk=plano_id)
        
        # Homologar todas sem alterar o status
        from django.utils import timezone
        total_homologadas = 0
        total_ja_homologadas = 0
        
        data_homologacao = timezone.now().strftime('%d/%m/%Y %H:%M')
        homologador = request.user.get_full_name() or request.user.username
        
        for ferias in ferias_selecionadas:
            # Verificar se já foi homologada - pular se já tiver sido
            if ferias.observacoes and '✓ Homologado em' in ferias.observacoes:
                total_ja_homologadas += 1
                continue  # Pular férias já homologadas
            
            # Registrar homologação nas observações sem alterar o status
            # Usar update_fields para salvar APENAS as observações, evitando que o save() altere o status
            if ferias.observacoes:
                ferias.observacoes = f"{ferias.observacoes}\n\n✓ Homologado em {data_homologacao} por {homologador}"
            else:
                ferias.observacoes = f"✓ Homologado em {data_homologacao} por {homologador}"
            
            # NÃO ALTERAR O STATUS - salvar APENAS as observações
            # Isso evita que as regras automáticas do save() alterem o status
            ferias.save(update_fields=['observacoes'])
            total_homologadas += 1
        
        # Mensagens de resultado
        if total_homologadas == 1:
            messages.success(request, f'{total_homologadas} férias homologada com sucesso!')
        elif total_homologadas > 1:
            messages.success(request, f'{total_homologadas} férias homologadas com sucesso!')
        
        if total_ja_homologadas > 0:
            if total_ja_homologadas == 1:
                messages.info(request, f'{total_ja_homologadas} férias já estava homologada e foi ignorada.')
            else:
                messages.info(request, f'{total_ja_homologadas} férias já estavam homologadas e foram ignoradas.')
        
        return redirect('militares:plano_ferias_detail', pk=plano_id)
        
    except Exception as e:
        messages.error(request, f'Erro ao homologar férias: {str(e)}')
        return redirect('militares:plano_ferias_detail', pk=plano_id)


@login_required
@require_http_methods(["POST"])
def ferias_reprogramar(request, pk):
    """Reprograma férias: desativa a atual e cria uma nova"""
    try:
        ferias_original = get_object_or_404(Ferias, pk=pk)
        
        # Verificar se o plano está aprovado - só permite reprogramar após aprovação
        if not ferias_original.plano or ferias_original.plano.status not in ['APROVADO', 'PUBLICADO']:
            messages.error(request, 'A reprogramação só é permitida após o plano estar aprovado!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Verificar se a férias está em status que permite reprogramação
        if ferias_original.status not in ['PLANEJADA', 'GOZANDO']:
            messages.error(request, f'A reprogramação só é permitida para férias em status "Planejada" ou "Gozando"! Status atual: {ferias_original.get_status_display()}.')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Verificar se a férias já foi usufruída - não permitir reprogramar
        if ferias_original.status == 'GOZADA':
            messages.error(request, 'Não é possível reprogramar férias já usufruídas!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Também não permitir reprogramar férias canceladas ou já reprogramadas
        if ferias_original.status in ['CANCELADA', 'REPROGRAMADA']:
            messages.error(request, f'Não é possível reprogramar férias com status: {ferias_original.get_status_display()}!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        motivo_reprogramacao = request.POST.get('motivo_reprogramacao', '').strip()
        nova_data_inicio = request.POST.get('nova_data_inicio', '').strip()
        nova_data_fim = request.POST.get('nova_data_fim', '').strip()
        nova_quantidade_dias = request.POST.get('nova_quantidade_dias', '').strip()
        
        # Validar campos obrigatórios
        if not motivo_reprogramacao:
            messages.error(request, 'É obrigatório informar o motivo da reprogramação!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        if not nova_data_inicio:
            messages.error(request, 'É obrigatório informar a nova data de início!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Converter data de início
        from datetime import datetime, date, timedelta
        try:
            data_inicio_obj = datetime.strptime(nova_data_inicio, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de data inválido!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Se a férias está GOZANDO, calcular dias já gozados e reprogramar apenas o restante
        dias_ja_gozados = 0
        dias_restantes = 0
        if ferias_original.status == 'GOZANDO':
            from datetime import date
            hoje = date.today()
            
            # Obter data fim da férias em andamento informada pelo usuário
            data_fim_gozando_str = request.POST.get('data_fim_gozando', '').strip()
            if data_fim_gozando_str:
                try:
                    data_fim_gozando = datetime.strptime(data_fim_gozando_str, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, 'Formato de data de término da férias em andamento inválido!')
                    if ferias_original.plano:
                        return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
                    return redirect('militares:ferias_detail', pk=pk)
            else:
                # Se não informou, usar hoje como padrão
                data_fim_gozando = hoje
            
            # Calcular dias já gozados (desde data_inicio até data_fim_gozando, inclusive)
            if ferias_original.data_inicio:
                # Salvar valor original antes de modificar
                quantidade_dias_original = ferias_original.quantidade_dias
                dias_ja_gozados = (data_fim_gozando - ferias_original.data_inicio).days + 1
                # Não pode ser maior que quantidade_dias total
                dias_ja_gozados = min(dias_ja_gozados, quantidade_dias_original)
                # Não pode ser negativo
                dias_ja_gozados = max(dias_ja_gozados, 0)
                dias_restantes = quantidade_dias_original - dias_ja_gozados
            else:
                # Se não tem data_inicio, não pode calcular
                messages.error(request, 'Férias em andamento sem data de início definida!')
                if ferias_original.plano:
                    return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
                return redirect('militares:ferias_detail', pk=pk)
            
            # Se todos os dias já foram gozados, apenas marcar como GOZADA e ajustar dias
            if dias_restantes <= 0:
                # Ajustar quantidade de dias da original para os dias já gozados
                ferias_original.quantidade_dias = dias_ja_gozados
                ferias_original.data_fim = data_fim_gozando  # Ajustar data_fim para a data informada
                ferias_original.status = 'GOZADA'
                observacao_gozada = f"Férias concluída ao reprogramar. Período gozado: {ferias_original.data_inicio.strftime('%d/%m/%Y')} a {data_fim_gozando.strftime('%d/%m/%Y')} ({dias_ja_gozados} dias). Motivo da reprogramação: {motivo_reprogramacao}"
                if ferias_original.observacoes:
                    ferias_original.observacoes = f"{ferias_original.observacoes}\n\n{observacao_gozada}"
                else:
                    ferias_original.observacoes = observacao_gozada
                ferias_original.save()
                
                messages.success(request, f'Férias de {ferias_original.militar.nome_guerra} já estava concluída ({dias_ja_gozados} dias gozados). Status atualizado para GOZADA.')
                if ferias_original.plano:
                    return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
                return redirect('militares:ferias_detail', pk=pk)
            
            # Ainda há dias restantes - reprogramar apenas os dias restantes
            # Usar automaticamente os dias restantes (não permitir informar manualmente)
            quantidade_dias_nova = dias_restantes
            
            # Calcular data_fim automaticamente baseada na nova data_inicio e quantidade de dias restantes
            data_fim_ajustada = data_inicio_obj + timedelta(days=quantidade_dias_nova - 1)
            
            # Salvar valor original da data_fim antes de modificar
            data_fim_original = ferias_original.data_fim
            
            # Ajustar férias original: reduzir quantidade_dias para apenas os dias já gozados e ajustar data_fim
            ferias_original.quantidade_dias = dias_ja_gozados
            ferias_original.data_fim = data_fim_gozando  # Data fim passa a ser a data informada pelo usuário
            ferias_original.status = 'GOZADA'
            observacao_gozada = f"Parte da férias gozada. Período gozado: {ferias_original.data_inicio.strftime('%d/%m/%Y')} a {data_fim_gozando.strftime('%d/%m/%Y')} ({dias_ja_gozados} dias de {quantidade_dias_original} totais). {dias_restantes} dias restantes reprogramados. Motivo da reprogramação: {motivo_reprogramacao}"
            if ferias_original.observacoes:
                ferias_original.observacoes = f"{ferias_original.observacoes}\n\n{observacao_gozada}"
            else:
                ferias_original.observacoes = observacao_gozada
            ferias_original.save()
            
            # Criar nova férias apenas com os dias restantes
            observacoes_nova = f"Reprogramação da férias anterior (ID: {ferias_original.pk}). {dias_ja_gozados} dias já foram gozados, reprogramando {dias_restantes} dias restantes. Motivo: {motivo_reprogramacao}."
            observacoes_nova += f"\nPeríodo original: {ferias_original.data_inicio.strftime('%d/%m/%Y')} a {data_fim_original.strftime('%d/%m/%Y')} ({quantidade_dias_original} dias)"
            observacoes_nova += f"\nPeríodo gozado: {ferias_original.data_inicio.strftime('%d/%m/%Y')} a {data_fim_gozando.strftime('%d/%m/%Y')} ({dias_ja_gozados} dias)"
            
            nova_ferias = Ferias.objects.create(
                plano=ferias_original.plano,
                militar=ferias_original.militar,
                tipo=ferias_original.tipo,
                ano_referencia=ferias_original.ano_referencia,
                data_inicio=data_inicio_obj,
                data_fim=data_fim_ajustada,
                quantidade_dias=quantidade_dias_nova,
                status='PLANEJADA',  # Nova situação começa como planejada, será atualizada automaticamente pelo save()
                observacoes=observacoes_nova,
                documento_referencia=ferias_original.documento_referencia,
                numero_documento=ferias_original.numero_documento,
                cadastrado_por=request.user
            )
            # Salvar novamente para que o método save() atualize o status automaticamente conforme as datas
            # (pode entrar em GOZANDO ou GOZADA automaticamente se as datas já passaram)
            nova_ferias.save()
            
            messages.success(request, f'Férias de {ferias_original.militar.nome_guerra} reprogramada com sucesso! {dias_ja_gozados} dias já gozados foram registrados, {dias_restantes} dias restantes foram reprogramados.')
            
            # Redirecionar para o plano
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=nova_ferias.pk)
        
        # Se está PLANEJADA, usar o fluxo normal de reprogramação
        # Validar data de fim para férias PLANEJADAS
        if not nova_data_fim:
            messages.error(request, 'É obrigatório informar a nova data de fim!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Converter data de fim para férias PLANEJADAS
        try:
            data_fim_obj = datetime.strptime(nova_data_fim, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de data de fim inválido!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Validar que data fim é posterior à data início
        if data_fim_obj < data_inicio_obj:
            messages.error(request, 'A data de fim deve ser posterior à data de início!')
            if ferias_original.plano:
                return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
            return redirect('militares:ferias_detail', pk=pk)
        
        # Validar quantidade de dias
        try:
            quantidade_dias = int(nova_quantidade_dias) if nova_quantidade_dias else ferias_original.quantidade_dias
            if quantidade_dias <= 0:
                quantidade_dias = ferias_original.quantidade_dias
        except ValueError:
            quantidade_dias = ferias_original.quantidade_dias
        
        # Desativar/cancelar a férias original - mudar status para REPROGRAMADA
        ferias_original.status = 'REPROGRAMADA'
        if ferias_original.observacoes:
            ferias_original.observacoes = f"{ferias_original.observacoes}\n\nReprogramada. Motivo: {motivo_reprogramacao}"
        else:
            ferias_original.observacoes = f"Reprogramada. Motivo: {motivo_reprogramacao}"
        ferias_original.save()
        
        # Criar nova férias com os novos dados
        observacoes_nova = f"Reprogramação da férias anterior (ID: {ferias_original.pk}). Motivo: {motivo_reprogramacao}."
        observacoes_nova += f"\nPeríodo anterior: {ferias_original.data_inicio.strftime('%d/%m/%Y')} a {ferias_original.data_fim.strftime('%d/%m/%Y')}"
        if ferias_original.observacoes:
            observacoes_nova = f"{observacoes_nova}\n\nObservações anteriores: {ferias_original.observacoes}"
        
        nova_ferias = Ferias.objects.create(
            plano=ferias_original.plano,
            militar=ferias_original.militar,
            tipo=ferias_original.tipo,
            ano_referencia=ferias_original.ano_referencia,
            data_inicio=data_inicio_obj,
            data_fim=data_fim_obj,
            quantidade_dias=quantidade_dias,
            status='PLANEJADA',  # Nova situação começa como planejada, será atualizada automaticamente pelo save()
            observacoes=observacoes_nova,
            documento_referencia=ferias_original.documento_referencia,
            numero_documento=ferias_original.numero_documento,
            cadastrado_por=request.user
        )
        # Salvar novamente para que o método save() atualize o status automaticamente conforme as datas
        # (pode entrar em GOZANDO ou GOZADA automaticamente se as datas já passaram)
        nova_ferias.save()
        
        messages.success(request, f'Férias de {ferias_original.militar.nome_guerra} reprogramadas com sucesso!')
        
        # Redirecionar para o plano
        if ferias_original.plano:
            return redirect('militares:plano_ferias_detail', pk=ferias_original.plano.pk)
        return redirect('militares:ferias_detail', pk=nova_ferias.pk)
        
    except Exception as e:
        messages.error(request, f'Erro ao reprogramar férias: {str(e)}')
        return redirect('militares:ferias_list')


@login_required
@require_http_methods(["POST"])
def plano_ferias_aprovar(request, pk):
    """Aprova um plano de férias com dados do documento"""
    try:
        plano = get_object_or_404(PlanoFerias, pk=pk)
        
        # Verificar se já está aprovado
        if plano.status in ['APROVADO', 'PUBLICADO']:
            messages.warning(request, 'Este plano já está aprovado!')
            return redirect('militares:ferias_list')
        
        # Verificar se todas as férias do plano estão homologadas
        # Excluir férias reprogramadas do cálculo (não contam no total)
        todas_ferias = plano.ferias.exclude(status='REPROGRAMADA')
        ferias_nao_homologadas = []
        
        for ferias in todas_ferias:
            # Verificar se tem marcação de homologação nas observações
            tem_homologacao = False
            if ferias.observacoes and '✓ Homologado em' in ferias.observacoes:
                tem_homologacao = True
            
            if not tem_homologacao:
                ferias_nao_homologadas.append(ferias)
        
        if ferias_nao_homologadas:
            total_nao_homologadas = len(ferias_nao_homologadas)
            total_ferias = todas_ferias.count()
            messages.error(
                request, 
                f'Não é possível aprovar o plano! {total_nao_homologadas} de {total_ferias} férias ainda não foram homologadas. '
                f'Por favor, homologue todas as férias antes de aprovar o plano.'
            )
            return redirect('militares:plano_ferias_detail', pk=pk)
        
        # Obter dados do formulário
        documento_referencia = request.POST.get('documento_referencia', '').strip()
        numero_documento = request.POST.get('numero_documento', '').strip()
        
        if not documento_referencia or not numero_documento:
            messages.error(request, 'É necessário informar o documento de referência e o número do documento para aprovar o plano!')
            return redirect('militares:ferias_list')
        
        # Atualizar o plano
        plano.documento_referencia = documento_referencia
        plano.numero_documento = numero_documento
        plano.status = 'APROVADO'
        plano.save()
        
        # Replicar o documento para TODAS as férias do plano (atualiza mesmo se já tiver algum documento)
        ferias_do_plano = plano.ferias.all()
        férias_atualizadas = 0
        for ferias in ferias_do_plano:
            # Sempre atualizar com o documento do plano
            ferias.documento_referencia = documento_referencia
            ferias.numero_documento = numero_documento
            ferias.save()
            férias_atualizadas += 1
        
        if férias_atualizadas > 0:
            messages.success(request, f'Plano de Férias {plano.titulo} aprovado com sucesso! Documento replicado para {férias_atualizadas} férias do plano.')
        else:
            messages.success(request, f'Plano de Férias {plano.titulo} aprovado com sucesso!')
        
        return redirect('militares:ferias_list')
        
    except Exception as e:
        messages.error(request, f'Erro ao aprovar plano: {str(e)}')
        return redirect('militares:ferias_list')


@login_required
def ferias_certidao_pdf(request, militar_id):
    """Gera PDF com certidão de férias de um militar"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse
    
    militar = get_object_or_404(Militar, pk=militar_id)
    
    # Busca férias ordenadas por ano de referência e data de início
    ferias_list = Ferias.objects.filter(militar=militar).order_by('-ano_referencia', '-data_inicio')
    
    if not ferias_list.exists():
        from django.http import HttpResponse
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Certidão de Férias</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                .error-box { border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }
                h2 { color: #721c24; }
                p { color: #721c24; }
                button { background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }
                button:hover { background-color: #c82333; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Certidão de Férias</h2>
                <p><strong>Este militar não possui histórico de férias para gerar certidão.</strong></p>
                <p>Por favor, cadastre férias para este militar antes de gerar a certidão.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=400, content_type='text/html')
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA DE GESTÃO DE PESSOAS",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>CERTIDÃO DE FÉRIAS</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Texto de certificação com dados do militar
        posto_display = militar.get_posto_graduacao_display()
        texto_certificacao = (
            f"Certifico para os devidos fins que conforme os registros funcionais desta instituição, "
            f"foi encontrado que o servidor <b>{posto_display} BM {militar.nome_completo}</b>, "
            f"CPF: <b>{militar.cpf or 'Não informado'}</b>, Matrícula: <b>{militar.matricula}</b>, "
            f"usufruiu férias regulamentares conforme segue:"
        )
        story.append(Paragraph(texto_certificacao, ParagraphStyle('certificacao', parent=styles['Normal'], fontSize=11, alignment=4, spaceAfter=15)))
        story.append(Spacer(1, 10))
        
        # Tabela única com todas as férias
        # Cabeçalho da tabela
        ferias_data = [
            ['Ano de Referência', 'Data Início', 'Data Fim', 'Tipo', 'Duração', 'Status', 'Documento']
        ]
        
        # Adicionar dados de todas as férias
        for ferias in ferias_list:
            documento = ''
            if ferias.documento_referencia and ferias.numero_documento:
                documento = f"{ferias.documento_referencia}\n{ferias.numero_documento}"
            elif ferias.documento_referencia:
                documento = ferias.documento_referencia
            elif ferias.numero_documento:
                documento = ferias.numero_documento
            else:
                documento = '-'
            
            ferias_data.append([
                str(ferias.ano_referencia),
                ferias.data_inicio.strftime("%d/%m/%Y"),
                ferias.data_fim.strftime("%d/%m/%Y"),
                ferias.get_tipo_display(),
                f"{ferias.quantidade_dias} dia{'s' if ferias.quantidade_dias > 1 else ''}",
                ferias.get_status_display(),
                documento
            ])
        
        # Criar tabela - ajustar títulos para caberem melhor
        cabecalho_curto = ['Ano Ref.', 'Início', 'Fim', 'Tipo', 'Dias', 'Status', 'Documento']
        ferias_data[0] = cabecalho_curto
        
        ferias_table = Table(ferias_data, colWidths=[2.2*cm, 2.3*cm, 2.3*cm, 1.8*cm, 1.8*cm, 2.2*cm, 5.4*cm], repeatRows=1)
        ferias_table.setStyle(TableStyle([
            # Cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
            ('TOPPADDING', (0, 0), (-1, 0), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            # Linhas de dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        
        story.append(ferias_table)
        story.append(Spacer(1, 20))
        
        # Texto final
        texto_final = "A presente certidão é emitida a pedido do(a) interessado(a), para fins de comprovação e demais usos legais que se fizerem necessários."
        story.append(Paragraph(texto_final, ParagraphStyle('texto_final', parent=styles['Normal'], fontSize=11, alignment=4, spaceAfter=20)))
        story.append(Spacer(1, 30))
        
        # Cidade e Data por extenso (centralizada)
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter cidade
            if militar_logado and militar_logado.cidade:
                cidade_doc = militar_logado.cidade
            else:
                cidade_doc = "Teresina"
            cidade_estado = f"{cidade_doc} - PI"
        except:
            cidade_estado = "Teresina - PI"
        
        # Data por extenso - usar timezone de Brasília
        import pytz
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
        
        # Obter função do formulário ou função atual
        funcao_selecionada = request.GET.get('funcao', '')
        if not funcao_selecionada:
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_selecionada = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta)
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Adicionar espaço para assinatura física
                story.append(Spacer(1, 1*cm))
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                
                # 2ª linha: Função
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                story.append(Spacer(1, 1*cm))
                story.append(Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Usar função selecionada do formulário
                funcao_display = funcao_selecionada
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_selecionada
            
            # Data e hora da assinatura
            agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M')
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_posto_quadro} - {funcao_display}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
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
            
            story.append(assinatura_table)
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        # Usar o militar como objeto para gerar o autenticador
        autenticador = gerar_autenticador_veracidade(militar, request, tipo_documento='certidao_ferias')
        
        # Tabela do rodapé: QR + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        buffer.seek(0)
        
        # Retornar PDF para visualização no navegador (sem download automático)
        filename = f'certidao_ferias_{militar.matricula}_{militar.nome_guerra.replace(" ", "_")}.pdf'
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_details = str(e)
        # Log do erro completo para debug (remover traceback em produção se necessário)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar certidão de férias para militar {militar.pk}: {error_details}\n{traceback.format_exc()}')
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Certidão de Férias</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                .error-detail {{ background-color: #fff; padding: 10px; border-radius: 3px; 
                               margin: 10px 0; font-size: 12px; text-align: left; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Certidão de Férias</h2>
                <p><strong>Ocorreu um erro ao gerar a certidão de férias.</strong></p>
                <div class="error-detail">
                    <strong>Detalhes do erro:</strong><br>
                    {error_details}
                </div>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def ferias_list_pdf(request):
    """Gera PDF listando férias agrupadas por mês e ordenadas por antiguidade"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    from datetime import datetime
    from django.db.models import Case, When, Value, IntegerField
    from collections import defaultdict
    import pytz
    
    try:
        # Obter parâmetros de filtro
        ano_referencia = request.GET.get('ano_referencia', '')
        ano_plano = request.GET.get('ano_plano', '')
        mes_filtro = request.GET.get('mes', '')
        om_filtro = request.GET.get('om', '')
        
        # Buscar férias
        ferias_queryset = Ferias.objects.select_related(
            'militar', 'plano'
        ).prefetch_related(
            'militar__lotacoes'
        ).filter(
            status__in=['PLANEJADA', 'GOZANDO', 'GOZADA']
        )
        
        # Aplicar filtros
        if ano_referencia:
            ferias_queryset = ferias_queryset.filter(ano_referencia=ano_referencia)
        
        if ano_plano:
            ferias_queryset = ferias_queryset.filter(plano__ano_plano=ano_plano)
        
        # Filtro por mês
        if mes_filtro:
            try:
                ano_mes, mes_num = mes_filtro.split('-')
                ano_mes = int(ano_mes)
                mes_num = int(mes_num)
                from django.db.models import Q
                ferias_queryset = ferias_queryset.filter(
                    Q(data_inicio__year=ano_mes, data_inicio__month=mes_num) |
                    Q(data_fim__year=ano_mes, data_fim__month=mes_num)
                )
            except:
                pass
        
        # Filtro por OM - apenas a instância selecionada (sem ascendência e sem descendência)
        if om_filtro:
            from .models import Lotacao, Orgao, GrandeComando, Unidade, SubUnidade
            from django.db.models import Q
            
            # Identificar tipo de OM e ID - filtrar apenas pela instância exata
            militares_ids = []
            if om_filtro.startswith('orgao_'):
                om_id = int(om_filtro.replace('orgao_', ''))
                # Apenas lotações onde o órgão é o selecionado E não há grande_comando, unidade ou sub_unidade
                lotacoes = Lotacao.objects.filter(
                    orgao_id=om_id,
                    grande_comando__isnull=True,
                    unidade__isnull=True,
                    sub_unidade__isnull=True,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            elif om_filtro.startswith('gc_'):
                gc_id = int(om_filtro.replace('gc_', ''))
                # Apenas lotações onde o grande_comando é o selecionado E não há unidade ou sub_unidade
                lotacoes = Lotacao.objects.filter(
                    grande_comando_id=gc_id,
                    unidade__isnull=True,
                    sub_unidade__isnull=True,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            elif om_filtro.startswith('unidade_'):
                unidade_id = int(om_filtro.replace('unidade_', ''))
                # Apenas lotações onde a unidade é a selecionada E não há sub_unidade
                lotacoes = Lotacao.objects.filter(
                    unidade_id=unidade_id,
                    sub_unidade__isnull=True,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            elif om_filtro.startswith('sub_'):
                sub_id = int(om_filtro.replace('sub_', ''))
                # Apenas lotações onde a sub_unidade é a selecionada
                lotacoes = Lotacao.objects.filter(
                    sub_unidade_id=sub_id,
                    status='ATUAL',
                    ativo=True
                ).values_list('militar_id', flat=True)
                militares_ids = list(lotacoes)
            
            if militares_ids:
                ferias_queryset = ferias_queryset.filter(militar_id__in=militares_ids)
        
        # Ordenar por antiguidade
        ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(len(ordem_hierarquica)),
            output_field=IntegerField()
        )
        
        ferias_lista = list(ferias_queryset.annotate(
            ordem_hierarquia=hierarquia_ordem
        ).order_by(
            'data_inicio',
            'ordem_hierarquia',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade'
        ))
        
        if not ferias_lista:
            error_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nenhuma Férias Encontrada</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .info-box { border: 2px solid #17a2b8; border-radius: 5px; padding: 20px; 
                               max-width: 600px; margin: 0 auto; background-color: #d1ecf1; }
                    h2 { color: #0c5460; }
                    p { color: #0c5460; }
                    .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; 
                           text-decoration: none; border-radius: 5px; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="info-box">
                    <h2>ℹ️ Nenhuma Férias Encontrada</h2>
                    <p>Não foram encontradas férias para os filtros selecionados.</p>
                    <a href="javascript:history.back()" class="btn">Voltar</a>
                </div>
            </body>
            </html>
            """
            return HttpResponse(error_html, content_type='text/html')
        
        # Obter nome do(s) plano(s) relacionado(s) e anos
        planos_ids = set([ferias.plano_id for ferias in ferias_lista if ferias.plano_id])
        planos = PlanoFerias.objects.filter(id__in=planos_ids)
        nome_planos = ", ".join([p.titulo for p in planos if p.titulo]) or "Plano de Férias"
        
        # Obter anos dos planos ou das férias
        if planos.exists():
            # Usar o primeiro plano para obter os anos
            primeiro_plano = planos.first()
            ano_ref = primeiro_plano.ano_referencia if primeiro_plano else None
            ano_gozo = primeiro_plano.ano_plano if primeiro_plano else None
        else:
            # Se não houver plano, tentar pegar dos parâmetros ou das férias
            ano_ref = ano_referencia if ano_referencia else None
            ano_gozo = ano_plano if ano_plano else None
            if not ano_ref and ferias_lista:
                # Pegar o primeiro ano_referencia das férias
                ano_ref = ferias_lista[0].ano_referencia
            if not ano_gozo and ferias_lista and ferias_lista[0].plano:
                ano_gozo = ferias_lista[0].plano.ano_plano
        
        # Agrupar por mês
        ferias_por_mes = defaultdict(list)
        meses_portugues = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        for ferias in ferias_lista:
            mes_ano = ferias.data_inicio.strftime('%Y-%m')
            mes_numero = ferias.data_inicio.month
            mes_nome = meses_portugues.get(mes_numero, ferias.data_inicio.strftime('%B'))
            ferias_por_mes[mes_ano].append({
                'ferias': ferias,
                'mes_nome': mes_nome
            })
        
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                                rightMargin=1.5*cm, leftMargin=1.5*cm, 
                                topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos (padrão certidão de férias)
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        style_header = ParagraphStyle('header', parent=styles['Normal'], 
                                     fontSize=9, fontName='Helvetica-Bold', alignment=1)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional (padrão certidão)
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA DE GESTÃO DE PESSOAS",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        titulo = "PLANO DE FÉRIAS"
        if ano_ref:
            titulo += f" REFERENTE A {ano_ref}"
        if ano_gozo:
            titulo += f" PARA GOZO EM {ano_gozo}"
        
        story.append(Paragraph(f"<u>{titulo}</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Processar cada mês
        meses_ordenados = sorted(ferias_por_mes.keys())
        
        for mes_ano in meses_ordenados:
            ferias_mes = ferias_por_mes[mes_ano]
            mes_nome = ferias_mes[0]['mes_nome']
            
            # Título do mês (apenas o nome do mês, sem ano)
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(f"{mes_nome.upper()}", style_subtitle))
            story.append(Spacer(1, 0.2*cm))
            
            # Cabeçalho da tabela
            table_data = [[
                Paragraph('Nº', style_header),
                Paragraph('Posto/Graduação', style_header),
                Paragraph('Nome', style_header),
                Paragraph('CPF', style_header),
                Paragraph('Lotação', style_header),
                Paragraph('Período', style_header),
                Paragraph('Dias', style_header),
                Paragraph('Status', style_header),
            ]]
            
            # Adicionar férias do mês
            for idx, item in enumerate(ferias_mes, 1):
                ferias = item['ferias']
                militar = ferias.militar
                
                # Obter lotação atual
                lotacao = militar.lotacao_atual()
                lotacao_nome = lotacao.instancia_om_nome if lotacao else "-"
                
                # Período
                periodo = f"{ferias.data_inicio.strftime('%d/%m/%Y')} a {ferias.data_fim.strftime('%d/%m/%Y')}"
                
                # Status
                status_display = ferias.get_status_display()
                
                linha = [
                    Paragraph(str(idx), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(militar.get_posto_graduacao_display(), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(militar.nome_completo, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=0)),
                    Paragraph(militar.cpf[:11] if militar.cpf else "-", ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(lotacao_nome, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=0)),
                    Paragraph(periodo, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(str(ferias.quantidade_dias), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                    Paragraph(status_display, ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                ]
                table_data.append(linha)
            
            # Criar tabela (ajustado para landscape A4)
            largura_total = landscape(A4)[0] - 3*cm  # Margens laterais
            col_widths = [
                1*cm,    # Nº
                3*cm,    # Posto
                4.5*cm,  # Nome
                2.5*cm,  # CPF
                6.5*cm,  # Lotação (aumentado para nomes completos)
                4*cm,    # Período
                1.5*cm,  # Dias
                2.5*cm,  # Status
            ]
            
            mes_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            mes_table.setStyle(TableStyle([
                # Cabeçalho (padrão certidão)
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 3),
                ('TOPPADDING', (0, 0), (-1, 0), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                # Linhas de dados
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                # Bordas
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            story.append(mes_table)
            story.append(Spacer(1, 0.3*cm))
            
            # Total do mês
            total_mes = len(ferias_mes)
            story.append(Paragraph(f"<b>Total: {total_mes} férias</b>", 
                                   ParagraphStyle('total', parent=styles['Normal'], fontSize=9, alignment=2)))
            
            # Espaçamento após cada mês
            if mes_ano != meses_ordenados[-1]:
                story.append(Spacer(1, 0.5*cm))
        
        # Assinaturas e autenticador (padrão certidão) - alinhados com a tabela
        story.append(Spacer(1, 20))
        
        # Calcular largura total (mesma da tabela principal)
        largura_total_tabela = landscape(A4)[0] - 3*cm
        
        # Preparar dados
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter cidade
            if militar_logado and militar_logado.cidade:
                cidade_doc = militar_logado.cidade
            else:
                cidade_doc = "Teresina"
            cidade_estado = f"{cidade_doc} - PI"
        except:
            cidade_estado = "Teresina - PI"
        
        # Data por extenso - usar timezone de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Obter função do formulário ou função atual
        funcao_assinatura = request.GET.get('funcao_assinatura', '')
        if not funcao_assinatura:
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_assinatura = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Preparar assinatura física
        if militar_logado:
            nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
        else:
            nome_usuario = request.user.get_full_name() or request.user.username
            nome_posto = nome_usuario
        
        # Preparar assinatura eletrônica
        try:
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                funcao_display = funcao_assinatura
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_assinatura
            
            # Data e hora da assinatura
            agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M')
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_posto_quadro} - {funcao_display}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path_assinatura = obter_caminho_assinatura_eletronica()
            logo_img = Image(logo_path_assinatura, width=3.0*cm, height=2.0*cm)
        except Exception as e:
            logo_img = None
            texto_assinatura = ""
        
        # Preparar autenticador
        class HistoricoFake:
            def __init__(self, ano_referencia, ano_plano):
                self.id = f"listagem_ferias_{ano_referencia}_{ano_plano}"
                hash_valor = abs(hash(f"{ano_referencia}_{ano_plano}"))
                self.pk = hash_valor % 100000000
                self.tipo_documento = 'listagem_ferias'
        
        historico_fake = HistoricoFake(ano_referencia or 'todos', ano_plano or 'todos')
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(historico_fake, request, tipo_documento='listagem_ferias')
        
        # Criar tabela única para todas as assinaturas e autenticador (mesma largura da tabela principal)
        assinaturas_finais_data = []
        
        # Cidade e data
        assinaturas_finais_data.append([Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica'))])
        
        # Espaço
        assinaturas_finais_data.append([Spacer(1, 1*cm)])
        
        # Assinatura física
        assinaturas_finais_data.append([Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold'))])
        assinaturas_finais_data.append([Paragraph(funcao_assinatura, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica'))])
        assinaturas_finais_data.append([Spacer(1, 0.5*cm)])
        
        # Assinatura eletrônica (dentro de célula)
        if logo_img:
            assinatura_eletronica_interna = Table(
                [[logo_img, Paragraph(texto_assinatura, style_small)]],
                colWidths=[3*cm, largura_total_tabela - 3*cm]
            )
            assinatura_eletronica_interna.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            assinaturas_finais_data.append([assinatura_eletronica_interna])
        
        # Autenticador (dentro de célula)
        autenticador_interno = Table(
            [[autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]],
            colWidths=[3*cm, largura_total_tabela - 3*cm]
        )
        autenticador_interno.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        assinaturas_finais_data.append([autenticador_interno])
        
        # Tabela principal (uma coluna, mesma largura da tabela de dados)
        assinaturas_table_final = Table(assinaturas_finais_data, colWidths=[largura_total_tabela])
        assinaturas_table_final.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(assinaturas_table_final)
        
        # Construir PDF
        doc.build(story)
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        
        # Nome do arquivo
        filename = "planos_ferias_listagem"
        if ano_referencia:
            filename += f"_ref_{ano_referencia}"
        if ano_plano:
            filename += f"_plano_{ano_plano}"
        filename += ".pdf"
        
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"ERRO ao gerar PDF de férias: {str(e)}")
        print(f"Traceback completo:\n{error_traceback}")
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Férias</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; text-align: left; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                pre {{ background-color: #fff; padding: 10px; border-radius: 3px; overflow-x: auto; font-size: 11px; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; 
                       text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF de Férias</h2>
                <p><strong>Ocorreu um erro:</strong></p>
                <p><code>{str(e)}</code></p>
                <details>
                    <summary style="cursor: pointer; color: #721c24; margin-top: 10px;"><strong>Detalhes do Erro (clique para expandir)</strong></summary>
                    <pre>{error_traceback}</pre>
                </details>
                <div style="text-align: center;">
                    <a href="javascript:history.back()" class="btn">Voltar</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')

