"""
Views para o módulo de Material Bélico
Gerencia o cadastro e controle de armas da instituição e de uso particular
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from io import BytesIO
import qrcode
import base64

from .models import Arma, ArmaParticular, MovimentacaoArma, Militar, Orgao, GrandeComando, Unidade, SubUnidade, ConfiguracaoArma, ConfiguracaoMunicao, HistoricoAlteracaoArma, AssinaturaMovimentacaoArma, TransferenciaArma, CautelaArma, CautelaArmaColetiva, CautelaArmaColetivaItem
from .forms import ArmaForm, ArmaParticularForm, MovimentacaoArmaForm, ConfiguracaoArmaForm, ConfiguracaoMunicaoForm, TransferenciaArmaForm, CautelaArmaForm, DevolucaoCautelaArmaForm


class ArmaListView(LoginRequiredMixin, ListView):
    """Lista todas as armas da instituição"""
    model = Arma
    template_name = 'militares/arma_list.html'
    context_object_name = 'armas'
    paginate_by = 20
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX para autocomplete
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('ajax') == '1':
            q = request.GET.get('q', '').strip()
            situacao = request.GET.get('situacao', '')
            
            # Listar todas as armas ativas do sistema
            queryset = Arma.objects.filter(ativo=True).order_by('numero_serie')
            
            # Se foi especificada uma situação, filtrar por ela
            if situacao:
                queryset = queryset.filter(situacao=situacao)
            
            # Se há busca, filtrar
            if q:
                queryset = queryset.filter(
                    Q(numero_serie__icontains=q) |
                    Q(marca__icontains=q) |
                    Q(modelo__icontains=q)
                )
            
            results = []
            for arma in queryset[:100]:  # Aumentar limite para 100 resultados
                text_display = f"{arma.numero_serie} - {arma.get_tipo_display()} - {arma.marca} {arma.modelo} ({arma.get_calibre_display()})"
                results.append({
                    'id': arma.id,
                    'text': text_display
                })
            
            return JsonResponse({'results': results})
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        from django.db.models import Case, When, IntegerField
        
        queryset = Arma.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'militar_responsavel', 'criado_por'
        ).annotate(
            situacao_ordem=Case(
                When(situacao='EM_MANUTENCAO', then=1),
                When(situacao='CAUTELA_INDIVIDUAL', then=2),
                When(situacao='RESERVA_ARMAMENTO', then=3),
                When(situacao='INSERVIVEL', then=4),
                default=5,
                output_field=IntegerField()
            )
        ).order_by('situacao_ordem', 'numero_serie')
        
        # Filtros
        search = self.request.GET.get('search', '')
        tipo = self.request.GET.get('tipo', '')
        situacao = self.request.GET.get('situacao', '')
        organizacao = self.request.GET.get('organizacao', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(numero_serie__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search) |
                Q(numero_registro_policia__icontains=search)
            )
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if situacao:
            queryset = queryset.filter(situacao=situacao)
        
        if organizacao:
            # Buscar em qualquer nível da organização
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
        context['tipo'] = self.request.GET.get('tipo', '')
        context['situacao'] = self.request.GET.get('situacao', '')
        context['organizacao'] = self.request.GET.get('organizacao', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        context['total_armas'] = Arma.objects.count()
        context['armas_cautela'] = Arma.objects.filter(situacao='CAUTELA_INDIVIDUAL', ativo=True).count()
        context['armas_reserva'] = Arma.objects.filter(situacao='RESERVA_ARMAMENTO', ativo=True).count()
        context['armas_manutencao'] = Arma.objects.filter(situacao='EM_MANUTENCAO', ativo=True).count()
        
        # Listas para filtros
        context['tipos'] = Arma.TIPO_CHOICES
        context['situacao_list'] = Arma.SITUACAO_CHOICES
        
        # Lista de organizações para filtro
        organizacoes = []
        organizacoes.extend([(o.id, f"Órgão: {o.nome}") for o in Orgao.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(gc.id, f"GC: {gc.nome}") for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(u.id, f"Unidade: {u.nome}") for u in Unidade.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(su.id, f"Sub-Unidade: {su.nome}") for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
        context['organizacoes'] = organizacoes
        
        # Buscar cautelas ativas para as armas em cautela
        armas_em_cautela = [arma.pk for arma in context['object_list'] if arma.situacao == 'CAUTELA_INDIVIDUAL']
        cautelas_ativas = {}
        if armas_em_cautela:
            for cautela in CautelaArma.objects.filter(arma_id__in=armas_em_cautela, ativa=True).select_related('arma'):
                cautelas_ativas[cautela.arma_id] = cautela
        context['cautelas_ativas'] = cautelas_ativas
        
        # Buscar cautelas coletivas ativas para as armas em cautela
        armas_em_cautela_coletiva = {}
        if armas_em_cautela:
            # Buscar itens de cautela coletiva ativos (não devolvidos) para essas armas
            itens_coletivos = CautelaArmaColetivaItem.objects.filter(
                arma_id__in=armas_em_cautela,
                devolvida=False,
                cautela__ativa=True
            ).select_related('cautela', 'arma')
            
            for item in itens_coletivos:
                armas_em_cautela_coletiva[item.arma_id] = item.cautela
        context['cautelas_coletivas_ativas'] = armas_em_cautela_coletiva
        
        return context


class ArmaCreateView(LoginRequiredMixin, CreateView):
    """Cria nova arma"""
    model = Arma
    form_class = ArmaForm
    template_name = 'militares/arma_form.html'
    success_url = reverse_lazy('militares:arma_list')
    
    def form_valid(self, form):
        # Processar seleção do organograma se fornecido
        organograma_id = self.request.POST.get('organograma-select', '')
        if organograma_id:
            self._processar_organograma(form, organograma_id)
        
        form.instance.criado_por = self.request.user
        
        # Se o estado de conservação for "Inservível", desativar a arma e definir situação
        if form.instance.estado_conservacao == 'INSERVIVEL':
            form.instance.ativo = False
            form.instance.situacao = 'INSERVIVEL'
        
        # Salvar o objeto primeiro
        response = super().form_valid(form)
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Arma {form.instance.numero_serie} cadastrada com sucesso!',
                'redirect_url': str(self.success_url)
            })
        
        messages.success(self.request, f'Arma {form.instance.numero_serie} cadastrada com sucesso!')
        return response
    
    def _processar_organograma(self, form, organograma_id):
        """Processa a seleção do organograma e preenche os campos de organização"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            form.instance.orgao = get_object_or_404(Orgao, pk=orgao_id)
            form.instance.grande_comando = None
            form.instance.unidade = None
            form.instance.sub_unidade = None
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            gc = get_object_or_404(GrandeComando, pk=gc_id)
            form.instance.orgao = gc.orgao
            form.instance.grande_comando = gc
            form.instance.unidade = None
            form.instance.sub_unidade = None
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            unidade = get_object_or_404(Unidade, pk=unidade_id)
            form.instance.orgao = unidade.grande_comando.orgao
            form.instance.grande_comando = unidade.grande_comando
            form.instance.unidade = unidade
            form.instance.sub_unidade = None
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            sub = get_object_or_404(SubUnidade, pk=sub_id)
            form.instance.orgao = sub.unidade.grande_comando.orgao
            form.instance.grande_comando = sub.unidade.grande_comando
            form.instance.unidade = sub.unidade
            form.instance.sub_unidade = sub
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = None
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/arma_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ArmaDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma arma"""
    model = Arma
    template_name = 'militares/arma_detail.html'
    context_object_name = 'arma'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        arma = self.object
        
        # Histórico de movimentações com assinaturas (sem limite para mostrar todas)
        movimentacoes = MovimentacaoArma.objects.filter(
            arma=arma
        ).select_related('militar_origem', 'militar_destino', 'responsavel_movimentacao').prefetch_related('assinaturas__militar', 'assinaturas__assinado_por').order_by('-data_movimentacao')
        
        # Adicionar flags para verificar se já tem assinaturas
        for mov in movimentacoes:
            mov.tem_assinatura_entregando = mov.assinaturas.filter(tipo_assinatura='ENTREGANDO').exists()
            mov.tem_assinatura_recebendo = mov.assinaturas.filter(tipo_assinatura='RECEBENDO').exists()
        
        context['movimentacoes'] = movimentacoes
        
        # Histórico de transferências (tipo TRANSFERENCIA)
        transferencias_mov = movimentacoes.filter(tipo_movimentacao='TRANSFERENCIA')
        context['transferencias'] = transferencias_mov
        
        # Histórico de manutenções (tipo MANUTENCAO e RETORNO_MANUTENCAO)
        movimentacoes_manutencao = movimentacoes.filter(
            tipo_movimentacao__in=['MANUTENCAO', 'RETORNO_MANUTENCAO']
        ).select_related(
            'militar_recebeu_manutencao',
            'orgao_manutencao',
            'grande_comando_manutencao',
            'unidade_manutencao',
            'sub_unidade_manutencao',
            'responsavel_movimentacao'
        ).order_by('-data_movimentacao')
        context['movimentacoes_manutencao'] = movimentacoes_manutencao
        
        # Histórico de cautelas/descautelas (usar MovimentacaoArma)
        movimentacoes_cautela = arma.movimentacoes.filter(
            tipo_movimentacao__in=['ENTREGA', 'DEVOLUCAO']
        ).select_related('militar_origem', 'militar_destino', 'responsavel_movimentacao').order_by('-data_movimentacao')
        context['movimentacoes_cautela'] = movimentacoes_cautela
        
        # Histórico de cautelas (CautelaArma)
        historico_cautelas = CautelaArma.objects.filter(
            arma=arma
        ).select_related(
            'militar', 'entregue_por', 'devolvido_por',
            'orgao', 'grande_comando', 'unidade', 'sub_unidade'
        ).order_by('-data_entrega')
        context['historico_cautelas'] = historico_cautelas
        
        # Histórico de cautelas coletivas (CautelaArmaColetivaItem)
        historico_cautelas_coletivas = CautelaArmaColetivaItem.objects.filter(
            arma=arma
        ).select_related(
            'cautela__responsavel',
            'cautela__orgao',
            'cautela__grande_comando',
            'cautela__unidade',
            'cautela__sub_unidade'
        ).order_by('-data_entrega')
        context['historico_cautelas_coletivas'] = historico_cautelas_coletivas
        
        # Verificar se a arma está em cautela coletiva ativa
        cautela_coletiva_ativa = CautelaArmaColetivaItem.objects.filter(
            arma=arma,
            devolvida=False,
            cautela__ativa=True
        ).select_related('cautela').first()
        context['cautela_coletiva_ativa'] = cautela_coletiva_ativa
        
        # Cautela ativa (última movimentação de ENTREGA sem DEVOLUCAO)
        if arma.situacao == 'CAUTELA_INDIVIDUAL' and arma.militar_responsavel:
            ultima_entrega = movimentacoes_cautela.filter(tipo_movimentacao='ENTREGA').first()
            context['cautela_ativa'] = ultima_entrega
        else:
            context['cautela_ativa'] = None
        
        # Histórico de alterações
        context['historico_alteracoes'] = HistoricoAlteracaoArma.objects.filter(
            arma=arma
        ).select_related('alterado_por').order_by('-data_alteracao')[:50]
        
        return context


@login_required
def arma_qrcode(request, pk):
    """Gera QR Code da arma com informações básicas e URL de acesso"""
    arma = get_object_or_404(Arma, pk=pk)
    
    # Criar URL completa para a arma
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    url_arma = f"{protocol}://{current_site.domain}{reverse('militares:arma_detail', kwargs={'pk': arma.pk})}"
    
    # Colocar a URL completa no QR Code
    qr_data = url_arma
    
    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Criar imagem do QR Code
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para BytesIO
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Verificar se é uma requisição para baixar apenas a imagem (usado no template como src)
    format_param = request.GET.get('format', '')
    if format_param == 'image':
        # Retornar apenas a imagem PNG
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="arma_{arma.numero_serie}_qrcode.png"'
        return response
    
    # Retornar imagem por padrão
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="arma_{arma.numero_serie}_qrcode.png"'
    return response


class ArmaUpdateView(LoginRequiredMixin, UpdateView):
    """Edita arma"""
    model = Arma
    form_class = ArmaForm
    template_name = 'militares/arma_form.html'
    
    def get_success_url(self):
        return reverse('militares:arma_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determinar qual opção do organograma está selecionada
        arma = self.object
        organograma_id = None
        
        if arma:
            if arma.sub_unidade:
                organograma_id = f'sub_{arma.sub_unidade.id}'
            elif arma.unidade:
                organograma_id = f'unidade_{arma.unidade.id}'
            elif arma.grande_comando:
                organograma_id = f'gc_{arma.grande_comando.id}'
            elif arma.orgao:
                organograma_id = f'orgao_{arma.orgao.id}'
        
        context['organograma_selecionado'] = organograma_id
        return context
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                self.object = self.get_object()
                # O get_form() já usa get_form_kwargs() que inclui instance=self.object automaticamente
                form = self.get_form()
                context = self.get_context_data(form=form)
                # Garantir que o objeto esteja no contexto
                if 'object' not in context:
                    context['object'] = self.object
                from django.template.loader import render_to_string
                html = render_to_string('militares/arma_form_modal_content.html', context, request=request)
                return JsonResponse({'html': html})
            except Exception as e:
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                error_trace = traceback.format_exc()
                logger.error(f"Erro ao carregar formulário de edição de arma: {str(e)}\n{error_trace}")
                print(f"Erro ao carregar formulário de edição de arma: {str(e)}")
                print(error_trace)
                return JsonResponse({
                    'error': str(e),
                    'message': f'Erro ao carregar formulário: {str(e)}',
                    'traceback': error_trace if request.user.is_staff else None
                }, status=500)
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Salvar estado anterior para comparar alterações
        arma_antiga = Arma.objects.get(pk=self.object.pk)
        estado_conservacao_antigo = arma_antiga.estado_conservacao
        estado_conservacao_novo = form.instance.estado_conservacao
        
        # Processar seleção do organograma se fornecido
        organograma_id = self.request.POST.get('organograma-select', '')
        if organograma_id:
            self._processar_organograma(form, organograma_id)
        
        # Se o estado de conservação for "Inservível", desativar a arma e definir situação
        if estado_conservacao_novo == 'INSERVIVEL':
            form.instance.ativo = False
            form.instance.situacao = 'INSERVIVEL'
        # Se o estado de conservação mudar de "Inservível" para outro, reativar a arma e voltar situação para "Reserva de Armamento"
        elif estado_conservacao_antigo == 'INSERVIVEL' and estado_conservacao_novo and estado_conservacao_novo != 'INSERVIVEL':
            # Forçar reativação da arma (sobrescrever qualquer valor do formulário)
            form.instance.ativo = True
            # Se a situação for "Inservível", voltar para "Reserva de Armamento"
            if form.instance.situacao == 'INSERVIVEL':
                form.instance.situacao = 'RESERVA_ARMAMENTO'
        
        # Salvar a instância
        response = super().form_valid(form)
        
        # Garantir que a reativação foi aplicada (caso o save() não tenha respeitado)
        if estado_conservacao_antigo == 'INSERVIVEL' and estado_conservacao_novo and estado_conservacao_novo != 'INSERVIVEL':
            arma_atualizada = Arma.objects.get(pk=self.object.pk)
            if not arma_atualizada.ativo:
                arma_atualizada.ativo = True
                arma_atualizada.save(update_fields=['ativo'])
        
        # Registrar alterações após salvar
        self._registrar_alteracoes(arma_antiga, form.instance)
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Arma {form.instance.numero_serie} atualizada com sucesso!',
                'redirect_url': str(self.get_success_url())
            })
        
        messages.success(self.request, f'Arma {form.instance.numero_serie} atualizada com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def _processar_organograma(self, form, organograma_id):
        """Processa a seleção do organograma e preenche os campos de organização"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            form.instance.orgao = get_object_or_404(Orgao, pk=orgao_id)
            form.instance.grande_comando = None
            form.instance.unidade = None
            form.instance.sub_unidade = None
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            gc = get_object_or_404(GrandeComando, pk=gc_id)
            form.instance.orgao = gc.orgao
            form.instance.grande_comando = gc
            form.instance.unidade = None
            form.instance.sub_unidade = None
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            unidade = get_object_or_404(Unidade, pk=unidade_id)
            form.instance.orgao = unidade.grande_comando.orgao
            form.instance.grande_comando = unidade.grande_comando
            form.instance.unidade = unidade
            form.instance.sub_unidade = None
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            sub = get_object_or_404(SubUnidade, pk=sub_id)
            form.instance.orgao = sub.unidade.grande_comando.orgao
            form.instance.grande_comando = sub.unidade.grande_comando
            form.instance.unidade = sub.unidade
            form.instance.sub_unidade = sub
    
    def _registrar_alteracoes(self, arma_antiga, arma_nova):
        """Registra as alterações realizadas na arma"""
        # Campos a serem monitorados
        campos_monitorados = [
            'numero_serie',
            'tipo',
            'marca',
            'modelo',
            'calibre',
            'alma_raiada',
            'quantidade_raias',
            'direcao_raias',
            'capacidade_carregador',
            'situacao',
            'orgao',
            'grande_comando',
            'unidade',
            'sub_unidade',
            'militar_responsavel',
            'numero_inquerito_pm',
            'encarregado_inquerito_pm',
            'numero_inquerito_pc',
            'delegado_inquerito_pc',
            'numero_registro_policia',
            'numero_guia_transito',
            'data_aquisicao',
            'fornecedor',
            'valor_aquisicao',
            'observacoes',
            'ativo',
        ]
        
        for campo in campos_monitorados:
            try:
                valor_anterior = getattr(arma_antiga, campo, None)
                valor_novo = getattr(arma_nova, campo, None)
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
                if isinstance(valor, bool):
                    return 'Sim' if valor else 'Não'
                return str(valor)
            
            valor_anterior_formatado = formatar_valor(valor_anterior)
            valor_novo_formatado = formatar_valor(valor_novo)
            
            # Registrar apenas se houver alteração
            if valor_anterior_formatado != valor_novo_formatado:
                # Obter nome legível do campo
                try:
                    field = arma_nova._meta.get_field(campo)
                    nome_campo = field.verbose_name
                except:
                    nome_campo = campo.replace('_', ' ').title()
                
                # Tratamento especial para mudança de situação - limpar campos não relacionados
                if campo == 'situacao':
                    # Quando mudar a situação, limpar campos da situação anterior
                    if valor_anterior == 'CAUTELA_INDIVIDUAL':
                        # Se saiu de cautela individual, limpar militar responsável e data
                        if arma_nova.militar_responsavel:
                            arma_nova.militar_responsavel = None
                            arma_nova.data_entrega_responsavel = None
                            arma_nova.save(update_fields=['militar_responsavel', 'data_entrega_responsavel'])
                    elif valor_anterior == 'ANEXADO_INQUERITO_PM':
                        # Se saiu de inquérito PM, limpar campos
                        if arma_nova.numero_inquerito_pm or arma_nova.encarregado_inquerito_pm:
                            arma_nova.numero_inquerito_pm = None
                            arma_nova.encarregado_inquerito_pm = None
                            arma_nova.save(update_fields=['numero_inquerito_pm', 'encarregado_inquerito_pm'])
                    elif valor_anterior == 'ANEXADO_INQUERITO_PC':
                        # Se saiu de inquérito PC, limpar campos
                        if arma_nova.numero_inquerito_pc or arma_nova.delegado_inquerito_pc:
                            arma_nova.numero_inquerito_pc = None
                            arma_nova.delegado_inquerito_pc = None
                            arma_nova.save(update_fields=['numero_inquerito_pc', 'delegado_inquerito_pc'])
                    
                    # Se entrou em cautela individual, atualizar data automaticamente
                    if valor_novo == 'CAUTELA_INDIVIDUAL' and arma_nova.militar_responsavel:
                        arma_nova.data_entrega_responsavel = timezone.now().date()
                        arma_nova.save(update_fields=['data_entrega_responsavel'])
                        # Registrar também a alteração da data
                        HistoricoAlteracaoArma.objects.create(
                            arma=arma_nova,
                            alterado_por=self.request.user,
                            campo_alterado='Data de Entrega ao Responsável',
                            valor_anterior=formatar_valor(arma_antiga.data_entrega_responsavel),
                            valor_novo=formatar_valor(arma_nova.data_entrega_responsavel),
                            observacao='Atualizada automaticamente ao alterar para Cautela Individual'
                        )
                
                # Tratamento especial para data_entrega_responsavel quando militar_responsavel muda
                if campo == 'militar_responsavel':
                    # Se mudou o militar, atualizar data_entrega_responsavel automaticamente
                    if valor_novo:
                        arma_nova.data_entrega_responsavel = timezone.now().date()
                        arma_nova.save(update_fields=['data_entrega_responsavel'])
                        # Registrar também a alteração da data
                        HistoricoAlteracaoArma.objects.create(
                            arma=arma_nova,
                            alterado_por=self.request.user,
                            campo_alterado='Data de Entrega ao Responsável',
                            valor_anterior=formatar_valor(arma_antiga.data_entrega_responsavel),
                            valor_novo=formatar_valor(arma_nova.data_entrega_responsavel),
                            observacao='Atualizada automaticamente ao alterar militar responsável'
                        )
                    else:
                        # Se removeu o militar, limpar a data
                        arma_nova.data_entrega_responsavel = None
                        arma_nova.save(update_fields=['data_entrega_responsavel'])
                
                # Registrar alteração no histórico (histórico não pode ser alterado)
                HistoricoAlteracaoArma.objects.create(
                    arma=arma_nova,
                    alterado_por=self.request.user,
                    campo_alterado=nome_campo,
                    valor_anterior=valor_anterior_formatado,
                    valor_novo=valor_novo_formatado
                )
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)


class ArmaDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui arma"""
    model = Arma
    template_name = 'militares/arma_confirm_delete.html'
    success_url = reverse_lazy('militares:arma_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f'Arma {self.get_object().numero_serie} excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# ========== ARMAS PARTICULARES ==========

class ArmaParticularListView(LoginRequiredMixin, ListView):
    """Lista todas as armas particulares"""
    model = ArmaParticular
    template_name = 'militares/arma_particular_list.html'
    context_object_name = 'armas_particulares'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ArmaParticular.objects.select_related(
            'militar', 'autorizado_por', 'criado_por'
        ).order_by('militar__nome_completo', 'numero_serie')
        
        # Filtros
        search = self.request.GET.get('search', '')
        tipo = self.request.GET.get('tipo', '')
        status = self.request.GET.get('status', '')
        autorizado = self.request.GET.get('autorizado', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(numero_serie__icontains=search) |
                Q(militar__nome_completo__icontains=search) |
                Q(militar__matricula__icontains=search) |
                Q(numero_registro_policia__icontains=search)
            )
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if autorizado == '1':
            queryset = queryset.filter(autorizado_uso_servico=True)
        elif autorizado == '0':
            queryset = queryset.filter(autorizado_uso_servico=False)
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['tipo'] = self.request.GET.get('tipo', '')
        context['status'] = self.request.GET.get('status', '')
        context['autorizado'] = self.request.GET.get('autorizado', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        context['total_armas'] = ArmaParticular.objects.count()
        context['armas_regulares'] = ArmaParticular.objects.filter(status='REGULAR', ativo=True).count()
        context['armas_autorizadas'] = ArmaParticular.objects.filter(autorizado_uso_servico=True, ativo=True).count()
        context['armas_vencidas'] = ArmaParticular.objects.filter(status='VENCIDO', ativo=True).count()
        
        # Listas para filtros
        context['tipos'] = ArmaParticular.TIPO_CHOICES
        context['status_list'] = ArmaParticular.STATUS_CHOICES
        
        return context


class ArmaParticularCreateView(LoginRequiredMixin, CreateView):
    """Cria nova arma particular"""
    model = ArmaParticular
    form_class = ArmaParticularForm
    template_name = 'militares/arma_particular_form.html'
    success_url = reverse_lazy('militares:arma_particular_list')
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        
        # Se for requisição AJAX, retornar JSON
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Arma particular {form.instance.numero_serie} cadastrada com sucesso!',
                'redirect_url': str(self.success_url)
            })
        
        messages.success(self.request, f'Arma particular {form.instance.numero_serie} cadastrada com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = None
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/arma_particular_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ArmaParticularDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma arma particular"""
    model = ArmaParticular
    template_name = 'militares/arma_particular_detail.html'
    context_object_name = 'arma_particular'
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            context = self.get_context_data()
            from django.template.loader import render_to_string
            html = render_to_string('militares/arma_particular_detail_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ArmaParticularUpdateView(LoginRequiredMixin, UpdateView):
    """Edita arma particular"""
    model = ArmaParticular
    form_class = ArmaParticularForm
    template_name = 'militares/arma_particular_form.html'
    
    def get_success_url(self):
        return reverse('militares:arma_particular_list')
    
    def form_valid(self, form):
        # Se for requisição AJAX, retornar JSON
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Arma particular {form.instance.numero_serie} atualizada com sucesso!',
                'redirect_url': str(self.get_success_url())
            })
        
        messages.success(self.request, f'Arma particular {form.instance.numero_serie} atualizada com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/arma_particular_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ArmaParticularDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui arma particular"""
    model = ArmaParticular
    template_name = 'militares/arma_particular_confirm_delete.html'
    success_url = reverse_lazy('militares:arma_particular_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, f'Arma particular {self.get_object().numero_serie} excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# ========== MOVIMENTAÇÕES ==========

class MovimentacaoArmaListView(LoginRequiredMixin, ListView):
    """Lista todas as movimentações de armas"""
    model = MovimentacaoArma
    template_name = 'militares/movimentacao_arma_list.html'
    context_object_name = 'movimentacoes'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = MovimentacaoArma.objects.select_related(
            'arma', 'militar_origem', 'militar_destino', 'responsavel_movimentacao',
            'militar_recebeu_manutencao',
            'orgao_manutencao', 'grande_comando_manutencao', 'unidade_manutencao', 'sub_unidade_manutencao'
        ).prefetch_related('assinaturas__militar', 'assinaturas__assinado_por').order_by('-data_movimentacao')
        
        # Filtros
        search = self.request.GET.get('search', '')
        arma_id = self.request.GET.get('arma', '')
        tipo_movimentacao = self.request.GET.get('tipo_movimentacao', '')
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        militar_id = self.request.GET.get('militar', '')
        
        if search:
            queryset = queryset.filter(
                Q(arma__numero_serie__icontains=search) |
                Q(arma__marca__icontains=search) |
                Q(arma__modelo__icontains=search) |
                Q(militar_origem__nome_completo__icontains=search) |
                Q(militar_destino__nome_completo__icontains=search) |
                Q(observacoes__icontains=search)
            )
        
        if arma_id:
            queryset = queryset.filter(arma_id=arma_id)
        
        if tipo_movimentacao:
            queryset = queryset.filter(tipo_movimentacao=tipo_movimentacao)
        
        if militar_id:
            queryset = queryset.filter(
                Q(militar_origem_id=militar_id) |
                Q(militar_destino_id=militar_id)
            )
        
        if data_inicio:
            try:
                from datetime import datetime
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                queryset = queryset.filter(data_movimentacao__gte=data_inicio_obj)
            except:
                pass
        
        if data_fim:
            try:
                from datetime import datetime
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
                data_fim_obj = data_fim_obj.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(data_movimentacao__lte=data_fim_obj)
            except:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['arma_id'] = self.request.GET.get('arma', '')
        context['tipo_movimentacao'] = self.request.GET.get('tipo_movimentacao', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['militar_id'] = self.request.GET.get('militar', '')
        
        # Estatísticas - usar queryset completo antes da paginação
        queryset_completo = self.get_queryset()
        context['total_movimentacoes'] = queryset_completo.count()
        
        # Contar por tipo
        context['total_entregas'] = queryset_completo.filter(tipo_movimentacao='ENTREGA').count()
        context['total_devolucoes'] = queryset_completo.filter(tipo_movimentacao='DEVOLUCAO').count()
        context['total_manutencoes'] = queryset_completo.filter(tipo_movimentacao='MANUTENCAO').count()
        
        # Lista de armas para filtro
        context['armas'] = Arma.objects.filter(ativo=True).order_by('numero_serie')[:100]
        
        # Lista de tipos de movimentação
        context['tipos_movimentacao'] = MovimentacaoArma.TIPO_MOVIMENTACAO_CHOICES
        
        # Lista de militares para filtro (apenas ativos)
        context['militares'] = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')[:100]
        
        return context


class MovimentacaoArmaCreateView(LoginRequiredMixin, CreateView):
    """Registra movimentação de arma"""
    model = MovimentacaoArma
    form_class = MovimentacaoArmaForm
    template_name = 'militares/movimentacao_arma_form.html'
    
    def get_success_url(self):
        return reverse('militares:arma_detail', kwargs={'pk': self.object.arma.pk})
    
    def get_initial(self):
        initial = super().get_initial()
        from django.utils import timezone
        initial['data_movimentacao'] = timezone.now()
        arma_id = self.request.GET.get('arma', '')
        if arma_id:
            try:
                arma = Arma.objects.get(pk=arma_id)
                initial['arma'] = arma
            except Arma.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        form.instance.responsavel_movimentacao = self.request.user
        # Definir data/hora atual automaticamente
        from django.utils import timezone
        form.instance.data_movimentacao = timezone.now()
        
        # Preencher campos de organização ANTES de salvar
        arma = form.instance.arma
        tipo_mov = form.instance.tipo_movimentacao
        
        # Preencher organização de origem se não estiver preenchido
        if tipo_mov == 'ENTREGA' and not form.instance.organizacao_origem:
            org_text = ''
            if arma.orgao:
                org_text = str(arma.orgao)
                if arma.grande_comando:
                    org_text += f" > {arma.grande_comando}"
                if arma.unidade:
                    org_text += f" > {arma.unidade}"
                if arma.sub_unidade:
                    org_text += f" > {arma.sub_unidade}"
            form.instance.organizacao_origem = org_text
        
        # Para devolução, buscar organização de origem da última entrega
        elif tipo_mov == 'DEVOLUCAO' and not form.instance.organizacao_destino:
            ultima_mov = arma.movimentacoes.filter(
                tipo_movimentacao='ENTREGA'
            ).order_by('-data_movimentacao').first()
            
            if ultima_mov and ultima_mov.organizacao_origem:
                form.instance.organizacao_destino = ultima_mov.organizacao_origem
        
        # Salvar a movimentação
        response = super().form_valid(form)
        
        # Atualizar situação da arma e militar responsável baseado no tipo de movimentação
        if tipo_mov == 'ENTREGA' and form.instance.militar_destino:
            arma.militar_responsavel = form.instance.militar_destino
            arma.data_entrega_responsavel = form.instance.data_movimentacao.date()
            arma.situacao = 'CAUTELA_INDIVIDUAL'
            arma.save()
        elif tipo_mov == 'DEVOLUCAO':
            arma.militar_responsavel = None
            arma.data_entrega_responsavel = None
            arma.situacao = 'RESERVA_ARMAMENTO'
            arma.save()
        elif tipo_mov == 'MANUTENCAO':
            arma.militar_responsavel = None
            arma.data_entrega_responsavel = None
            arma.situacao = 'EM_MANUTENCAO'
            arma.save()
        elif tipo_mov == 'RETORNO_MANUTENCAO':
            arma.situacao = 'RESERVA_ARMAMENTO'
            arma.save()
        
        messages.success(self.request, 'Movimentação registrada com sucesso!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)


class MovimentacaoArmaDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma movimentação de arma"""
    model = MovimentacaoArma
    template_name = 'militares/movimentacao_arma_detail.html'
    context_object_name = 'movimentacao'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movimentacao = self.object
        context['arma'] = movimentacao.arma
        return context


class MovimentacaoArmaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edita uma movimentação de arma (apenas superusuários)"""
    model = MovimentacaoArma
    form_class = MovimentacaoArmaForm
    template_name = 'militares/movimentacao_arma_form.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_success_url(self):
        return reverse('militares:arma_detail', kwargs={'pk': self.object.arma.pk})
    
    def get_form_kwargs(self):
        """Passar a arma para o formulário"""
        kwargs = super().get_form_kwargs()
        kwargs['arma'] = self.object.arma
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        # Manter a data/hora original da movimentação formatada corretamente
        if self.object.data_movimentacao:
            # Formatar para datetime-local (YYYY-MM-DDTHH:MM)
            initial['data_movimentacao'] = self.object.data_movimentacao.strftime('%Y-%m-%dT%H:%M')
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['arma'] = self.object.arma
        return context
    
    def form_valid(self, form):
        form.instance.responsavel_movimentacao = self.request.user
        
        # Preencher campos de organização se não estiverem preenchidos
        arma = form.instance.arma
        tipo_mov = form.instance.tipo_movimentacao
        
        # Preencher organização de origem se não estiver preenchido
        if tipo_mov == 'ENTREGA' and not form.instance.organizacao_origem:
            org_text = ''
            if arma.orgao:
                org_text = str(arma.orgao)
                if arma.grande_comando:
                    org_text += f" > {arma.grande_comando}"
                if arma.unidade:
                    org_text += f" > {arma.unidade}"
                if arma.sub_unidade:
                    org_text += f" > {arma.sub_unidade}"
            form.instance.organizacao_origem = org_text
        
        # Salvar a movimentação
        response = super().form_valid(form)
        
        # Atualizar situação da arma baseado no tipo de movimentação
        if tipo_mov == 'ENTREGA' and form.instance.militar_destino:
            arma.militar_responsavel = form.instance.militar_destino
            arma.data_entrega_responsavel = form.instance.data_movimentacao.date()
            arma.situacao = 'CAUTELA_INDIVIDUAL'
            arma.save()
        elif tipo_mov == 'DEVOLUCAO':
            arma.militar_responsavel = None
            arma.data_entrega_responsavel = None
            arma.situacao = 'RESERVA_ARMAMENTO'
            arma.save()
        elif tipo_mov == 'MANUTENCAO':
            arma.militar_responsavel = None
            arma.data_entrega_responsavel = None
            arma.situacao = 'EM_MANUTENCAO'
            arma.save()
        elif tipo_mov == 'RETORNO_MANUTENCAO':
            arma.situacao = 'RESERVA_ARMAMENTO'
            arma.save()
        
        messages.success(self.request, 'Movimentação atualizada com sucesso!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)


class MovimentacaoArmaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Exclui uma movimentação de arma (apenas superusuários)"""
    model = MovimentacaoArma
    template_name = 'militares/movimentacao_arma_confirm_delete.html'
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def get_success_url(self):
        return reverse('militares:arma_detail', kwargs={'pk': self.object.arma.pk})
    
    def delete(self, request, *args, **kwargs):
        # Capturar a movimentação antes de excluir
        movimentacao = self.get_object()
        arma = movimentacao.arma
        tipo_mov = movimentacao.tipo_movimentacao
        
        # Excluir a movimentação
        response = super().delete(request, *args, **kwargs)
        
        # Verificar se há outras movimentações mais recentes
        movimentacoes_restantes = MovimentacaoArma.objects.filter(
            arma=arma
        ).exclude(pk=movimentacao.pk).order_by('-data_movimentacao')
        
        if movimentacoes_restantes.exists():
            # Se há movimentações mais recentes, usar a mais recente para determinar a situação
            ultima_mov = movimentacoes_restantes.first()
            if ultima_mov.tipo_movimentacao == 'ENTREGA' and ultima_mov.militar_destino:
                arma.militar_responsavel = ultima_mov.militar_destino
                arma.data_entrega_responsavel = ultima_mov.data_movimentacao.date()
                arma.situacao = 'CAUTELA_INDIVIDUAL'
            elif ultima_mov.tipo_movimentacao == 'DEVOLUCAO':
                arma.militar_responsavel = None
                arma.data_entrega_responsavel = None
                arma.situacao = 'RESERVA_ARMAMENTO'
            elif ultima_mov.tipo_movimentacao == 'MANUTENCAO':
                arma.militar_responsavel = None
                arma.data_entrega_responsavel = None
                arma.situacao = 'EM_MANUTENCAO'
            elif ultima_mov.tipo_movimentacao == 'RETORNO_MANUTENCAO':
                arma.situacao = 'RESERVA_ARMAMENTO'
            arma.save()
        else:
            # Se não há mais movimentações, voltar para situação padrão
            arma.militar_responsavel = None
            arma.data_entrega_responsavel = None
            arma.situacao = 'RESERVA_ARMAMENTO'
            arma.save()
        
        messages.success(self.request, 'Movimentação excluída com sucesso!')
        return response


@login_required
@require_http_methods(["GET"])
def configuracao_arma_dados(request, pk):
    """View AJAX para retornar dados de uma configuração de arma"""
    try:
        configuracao = get_object_or_404(ConfiguracaoArma, pk=pk, ativo=True)
        return JsonResponse({
            'success': True,
            'tipo': configuracao.tipo,
            'calibre': configuracao.calibre,
            'marca': configuracao.marca,
            'modelo': configuracao.modelo,
            'imagem_url': configuracao.imagem.url if configuracao.imagem else None,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def configuracao_arma_buscar(request):
    """View AJAX para buscar configuração de arma pelos dados (tipo, calibre, marca, modelo)"""
    try:
        tipo = request.GET.get('tipo', '')
        calibre = request.GET.get('calibre', '')
        marca = request.GET.get('marca', '').strip()
        modelo = request.GET.get('modelo', '').strip()
        
        if not (tipo and calibre and marca and modelo):
            return JsonResponse({
                'success': False,
                'error': 'Parâmetros incompletos'
            }, status=400)
        
        # Buscar configuração que corresponda aos dados
        configuracao = ConfiguracaoArma.objects.filter(
            tipo=tipo,
            calibre=calibre,
            marca__iexact=marca,
            modelo__iexact=modelo,
            ativo=True
        ).first()
        
        if configuracao:
            return JsonResponse({
                'success': True,
                'id': configuracao.id,
                'tipo': configuracao.tipo,
                'calibre': configuracao.calibre,
                'marca': configuracao.marca,
                'modelo': configuracao.modelo,
                'imagem_url': configuracao.imagem.url if configuracao.imagem else None,
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Configuração não encontrada'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def militar_lotacao_atual(request, pk):
    """View AJAX para retornar a lotação atual de um militar"""
    try:
        from militares.models import Militar
        militar = get_object_or_404(Militar, pk=pk)
        lotacao = militar.lotacao_atual()
        
        if lotacao:
            org_parts = []
            if lotacao.orgao:
                org_parts.append(str(lotacao.orgao))
            if lotacao.grande_comando:
                org_parts.append(str(lotacao.grande_comando))
            if lotacao.unidade:
                org_parts.append(str(lotacao.unidade))
            if lotacao.sub_unidade:
                org_parts.append(str(lotacao.sub_unidade))
            
            return JsonResponse({
                'success': True,
                'organizacao': ' > '.join(org_parts) if org_parts else '',
                'lotacao_texto': lotacao.lotacao,
                'orgao_id': lotacao.orgao.id if lotacao.orgao else None,
                'grande_comando_id': lotacao.grande_comando.id if lotacao.grande_comando else None,
                'unidade_id': lotacao.unidade.id if lotacao.unidade else None,
                'sub_unidade_id': lotacao.sub_unidade.id if lotacao.sub_unidade else None,
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Militar não possui lotação atual cadastrada'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


class MovimentacaoArmaCreateView(LoginRequiredMixin, CreateView):
    """Cria nova movimentação de arma"""
    model = MovimentacaoArma
    form_class = MovimentacaoArmaForm
    template_name = 'militares/movimentacao_arma_form.html'
    
    def get_arma(self):
        """Obtém a arma a partir do pk na URL ou GET"""
        arma_id = self.kwargs.get('pk') or self.request.GET.get('arma', '')
        if arma_id:
            return get_object_or_404(Arma, pk=arma_id, ativo=True)
        return None
    
    def get_success_url(self):
        """Redireciona para a página de detalhes da arma"""
        return reverse('militares:arma_detail', kwargs={'pk': self.object.arma.pk})
    
    def get_initial(self):
        """Define valores iniciais baseado na arma"""
        initial = super().get_initial()
        arma = self.get_arma()
        if arma:
            initial['arma'] = arma.pk  # Passar apenas o ID
            # Formatar data para datetime-local (YYYY-MM-DDTHH:MM)
            now = timezone.now()
            initial['data_movimentacao'] = now.strftime('%Y-%m-%dT%H:%M')
            
            # Verificar se há parâmetro tipo na URL (para manutenção ou retorno de manutenção)
            tipo_param = self.request.GET.get('tipo', '')
            if tipo_param == 'RETORNO_MANUTENCAO':
                initial['tipo_movimentacao'] = 'RETORNO_MANUTENCAO'
            elif tipo_param == 'MANUTENCAO':
                initial['tipo_movimentacao'] = 'MANUTENCAO'
            # Caso contrário, deixar o usuário escolher
            
            # Preencher organização de origem com base na organização da arma
            if arma.orgao:
                org_text = str(arma.orgao)
                if arma.grande_comando:
                    org_text += f" > {arma.grande_comando}"
                if arma.unidade:
                    org_text += f" > {arma.unidade}"
                if arma.sub_unidade:
                    org_text += f" > {arma.sub_unidade}"
                initial['organizacao_origem'] = org_text
        
        return initial
    
    def get_context_data(self, **kwargs):
        """Adiciona a arma ao contexto"""
        # Para requisições AJAX, criar contexto manualmente para evitar problemas com self.object
        if hasattr(self, 'request') and self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Criar contexto básico manualmente para AJAX
            context = {}
            if 'form' in kwargs:
                context['form'] = kwargs['form']
            elif hasattr(self, 'form_class'):
                context['form'] = self.get_form()
        else:
            # Chamar super() normalmente para requisições normais
            context = super().get_context_data(**kwargs)
        
        arma = self.get_arma()
        context['arma'] = arma
        
        # Adicionar militar responsável para o template (se houver)
        if arma and arma.militar_responsavel:
            context['militar_cautela'] = arma.militar_responsavel
        else:
            context['militar_cautela'] = None
        
        # Listas para o select de organograma (para manutenção interna) - apenas nomes, sem prefixos
        organizacoes = []
        organizacoes.extend([(f"orgao_{o.id}", o.nome) for o in Orgao.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"gc_{gc.id}", gc.nome) for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"unidade_{u.id}", u.nome) for u in Unidade.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"sub_{su.id}", su.nome) for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
        context['organizacoes'] = organizacoes
        
        return context
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            import logging
            logger = logging.getLogger(__name__)
            print("=" * 50)
            print("INICIANDO CARREGAMENTO DO MODAL DE MANUTENÇÃO")
            print("=" * 50)
            logger.info("Iniciando carregamento do modal de manutenção via AJAX")
            
            # Garantir que self.object seja None para CreateView em requisições AJAX
            self.object = None
            try:
                print("1. Verificando arma...")
                # Garantir que a arma existe
                print("2. Obtendo arma...")
                arma = self.get_arma()
                print(f"   Arma obtida: {arma}")
                if not arma:
                    print("   ERRO: Arma não encontrada!")
                    return JsonResponse({
                        'error': 'Arma não encontrada',
                        'message': 'A arma especificada não foi encontrada ou está inativa.'
                    }, status=404)
                print(f"   Arma encontrada: {arma.numero_serie if arma else 'None'}")
                
                # Criar formulário com valores iniciais
                try:
                    print("3. Criando formulário...")
                    # get_form() já usa get_initial() internamente, não precisa passar initial
                    form = self.get_form()
                    print(f"   Formulário criado: {form}")
                    
                    # Aplicar valores iniciais manualmente se necessário
                    initial = self.get_initial()
                    if initial:
                        # Atualizar o initial do formulário
                        if hasattr(form, 'initial'):
                            form.initial.update(initial)
                        else:
                            form.initial = initial
                    
                    # Verificar se o formulário foi criado corretamente
                    if not form:
                        return JsonResponse({
                            'error': 'Erro ao criar formulário',
                            'message': 'Não foi possível criar o formulário de movimentação.'
                        }, status=500)
                except Exception as form_error:
                    import traceback
                    import logging
                    logger = logging.getLogger(__name__)
                    error_trace = traceback.format_exc()
                    logger.error(f"Erro ao criar formulário de movimentação: {str(form_error)}\n{error_trace}")
                    return JsonResponse({
                        'error': f'Erro ao criar formulário: {str(form_error)}',
                        'message': 'Erro ao preparar formulário. Verifique os logs do servidor.'
                    }, status=500)
                
                # Garantir que o formulário tenha todos os campos necessários
                try:
                    print("4. Criando contexto...")
                    # Para requisições AJAX, criar contexto manualmente
                    context = {}
                    context['form'] = form
                    context['arma'] = arma
                    print(f"   Contexto criado com form e arma")
                    
                    # Adicionar militar responsável para o template (se houver)
                    if arma and arma.militar_responsavel:
                        context['militar_cautela'] = arma.militar_responsavel
                    else:
                        context['militar_cautela'] = None
                    
                    # Listas para o select de organograma (para manutenção interna)
                    from .models import Orgao, GrandeComando, Unidade, SubUnidade
                    organizacoes = []
                    organizacoes.extend([(f"orgao_{o.id}", o.nome) for o in Orgao.objects.filter(ativo=True).order_by('nome')])
                    organizacoes.extend([(f"gc_{gc.id}", gc.nome) for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
                    organizacoes.extend([(f"unidade_{u.id}", u.nome) for u in Unidade.objects.filter(ativo=True).order_by('nome')])
                    organizacoes.extend([(f"sub_{su.id}", su.nome) for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
                    context['organizacoes'] = organizacoes
                except Exception as context_error:
                    import traceback
                    import logging
                    logger = logging.getLogger(__name__)
                    error_trace = traceback.format_exc()
                    logger.error(f"Erro ao criar contexto: {str(context_error)}\n{error_trace}")
                    return JsonResponse({
                        'error': f'Erro ao criar contexto: {str(context_error)}',
                        'message': 'Erro ao preparar formulário. Verifique os logs do servidor.'
                    }, status=500)
                
                from django.template.loader import render_to_string
                
                # Garantir que todos os campos necessários estão no contexto
                if 'form' not in context:
                    return JsonResponse({
                        'error': 'Formulário não encontrado no contexto',
                        'message': 'Erro ao preparar formulário. Tente novamente.'
                    }, status=500)
                
                # Verificar se o formulário tem todos os campos necessários
                form = context['form']
                campos_necessarios = [
                    'tipo_movimentacao', 'data_movimentacao', 'tipo_manutencao',
                    'militar_recebeu_manutencao', 'empresa_manutencao', 'cnpj_empresa_manutencao',
                    'endereco_empresa_manutencao', 'responsavel_empresa_manutencao',
                    'quantidade_carregadores', 'numeracao_carregadores', 'quantidade_municoes_catalogadas', 'observacoes'
                ]
                
                campos_faltando = []
                for campo in campos_necessarios:
                    if campo not in form.fields:
                        campos_faltando.append(campo)
                
                if campos_faltando:
                    print(f"Aviso: Campos faltando no formulário: {campos_faltando}")
                
                # Garantir que o request está no contexto para as tags {% url %} funcionarem
                context['request'] = request
                print("5. Request adicionado ao contexto")
                
                # Garantir que arma existe antes de renderizar
                if 'arma' not in context or context['arma'] is None:
                    print("   ERRO: Arma não encontrada no contexto!")
                    return JsonResponse({
                        'error': 'Arma não encontrada no contexto',
                        'message': 'Erro ao preparar formulário. A arma não foi encontrada.'
                    }, status=500)
                
                # Tentar renderizar o template
                try:
                    print("6. Renderizando template...")
                    html = render_to_string('militares/movimentacao_arma_modal_content.html', context, request=request)
                    print(f"   Template renderizado com sucesso! Tamanho: {len(html) if html else 0} caracteres")
                    
                    if not html:
                        return JsonResponse({
                            'error': 'Template não foi renderizado',
                            'message': 'Erro ao carregar formulário. O template não foi renderizado corretamente.'
                        }, status=500)
                    
                    return JsonResponse({'html': html})
                except Exception as render_error:
                    # Se houver erro ao renderizar, tentar identificar o problema
                    import traceback
                    import logging
                    logger = logging.getLogger(__name__)
                    error_trace = traceback.format_exc()
                    logger.error(f"Erro ao renderizar template: {str(render_error)}\n{error_trace}")
                    print(f"Erro ao renderizar template: {str(render_error)}")
                    print(error_trace)
                    
                    # Verificar se é erro de template ou de contexto
                    error_message = str(render_error)
                    if 'url' in error_message.lower() or 'reverse' in error_message.lower():
                        # Problema com URLs
                        return JsonResponse({
                            'error': f'Erro ao processar URLs no template: {error_message}',
                            'message': 'Erro ao carregar formulário. Problema com processamento de URLs.',
                            'traceback': error_trace if request.user.is_staff else None,
                            'details': error_message[:500] if request.user.is_staff else None
                        }, status=500)
                    elif 'object' in error_message.lower() and 'has no attribute' in error_message.lower():
                        # Problema com objeto não encontrado
                        return JsonResponse({
                            'error': f'Erro ao acessar objeto: {error_message}',
                            'message': 'Erro ao carregar formulário. Objeto não encontrado.',
                            'traceback': error_trace if request.user.is_staff else None,
                            'details': error_message[:500] if request.user.is_staff else None
                        }, status=500)
                    else:
                        return JsonResponse({
                            'error': f'Erro ao renderizar template: {error_message}',
                            'message': f'Erro ao carregar formulário: {error_message[:200]}',
                            'traceback': error_trace if request.user.is_staff else None,
                            'details': error_message[:500] if request.user.is_staff else None
                        }, status=500)
            except Exception as e:
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                error_trace = traceback.format_exc()
                logger.error(f"Erro ao carregar modal de movimentação: {str(e)}\n{error_trace}")
                print(f"Erro ao carregar modal de movimentação: {str(e)}")
                print(error_trace)
                
                # Retornar erro detalhado para debug
                return JsonResponse({
                    'error': str(e),
                    'message': f'Erro ao carregar formulário: {str(e)}',
                    'traceback': error_trace if request.user.is_staff else None,
                    'arma_id': self.kwargs.get('pk', 'N/A'),
                    'error_type': type(e).__name__
                }, status=500)
        return super().get(request, *args, **kwargs)
    
    @transaction.atomic
    def form_valid(self, form):
        """Processa o formulário válido - Cautela (OM -> Militar) ou Descautelar (Militar -> OM)"""
        movimentacao = form.save(commit=False)
        movimentacao.responsavel_movimentacao = self.request.user
        
        # Definir data/hora apenas se não foi preenchida no formulário
        if not movimentacao.data_movimentacao:
            movimentacao.data_movimentacao = timezone.now()
        
        arma = movimentacao.arma
        tipo_mov = movimentacao.tipo_movimentacao
        
        # ENTREGA e DEVOLUCAO não são mais suportadas neste formulário
        if tipo_mov in ['ENTREGA', 'DEVOLUCAO']:
            messages.error(
                self.request, 
                'Este tipo de movimentação não é mais suportado neste formulário.'
            )
            form.add_error('tipo_movimentacao', 'Este tipo de movimentação não é mais suportado.')
            return self.form_invalid(form)
        
        # MANUTENCAO e RETORNO_MANUTENCAO
        elif tipo_mov == 'MANUTENCAO':
            # Validar se a arma pode ir para manutenção
            if arma.situacao != 'RESERVA_ARMAMENTO':
                messages.error(
                    self.request,
                    f'A arma {arma.numero_serie} não pode ser enviada para manutenção. '
                    f'A arma deve estar em "Reserva de Armamento" para poder ser enviada para manutenção. '
                    f'Situação atual: {arma.get_situacao_display()}'
                )
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'A arma não pode ser enviada para manutenção. A arma deve estar em "Reserva de Armamento". Situação atual: {arma.get_situacao_display()}',
                        'errors': {'tipo_movimentacao': ['A arma deve estar em Reserva de Armamento para poder ser enviada para manutenção.']}
                    }, status=400)
                form.add_error('tipo_movimentacao', 'A arma deve estar em Reserva de Armamento para poder ser enviada para manutenção.')
                return self.form_invalid(form)
            
            # Verificar se já existe uma manutenção em andamento (sem retorno)
            # Buscar a última manutenção
            ultima_manutencao = arma.movimentacoes.filter(
                tipo_movimentacao='MANUTENCAO'
            ).order_by('-data_movimentacao').first()
            
            if ultima_manutencao:
                # Verificar se existe retorno para esta manutenção
                retorno_existente = arma.movimentacoes.filter(
                    tipo_movimentacao='RETORNO_MANUTENCAO',
                    data_movimentacao__gt=ultima_manutencao.data_movimentacao
                ).exists()
                
                if not retorno_existente:
                    # Existe manutenção sem retorno
                    manutencao_em_andamento = ultima_manutencao
                else:
                    manutencao_em_andamento = None
            else:
                manutencao_em_andamento = None
            
            if manutencao_em_andamento:
                messages.error(
                    self.request,
                    f'A arma {arma.numero_serie} já está em manutenção desde {manutencao_em_andamento.data_movimentacao.strftime("%d/%m/%Y %H:%M")}. '
                    f'É necessário registrar o retorno da manutenção antes de enviar para outra manutenção.'
                )
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'A arma já está em manutenção desde {manutencao_em_andamento.data_movimentacao.strftime("%d/%m/%Y %H:%M")}. É necessário registrar o retorno antes de enviar para outra manutenção.',
                        'errors': {'tipo_movimentacao': ['A arma já está em manutenção. Registre o retorno antes de enviar para outra manutenção.']}
                    }, status=400)
                form.add_error('tipo_movimentacao', 'A arma já está em manutenção. Registre o retorno antes de enviar para outra manutenção.')
                return self.form_invalid(form)
            
            # Processar organograma de manutenção se for interna
            tipo_manutencao = movimentacao.tipo_manutencao
            if tipo_manutencao == 'INTERNA':
                organograma_manutencao_id = self.request.POST.get('organograma_manutencao', '')
                if organograma_manutencao_id:
                    self._processar_organograma_manutencao(movimentacao, organograma_manutencao_id)
            
            movimentacao.save()
            arma.militar_responsavel = None
            arma.data_entrega_responsavel = None
            arma.situacao = 'EM_MANUTENCAO'
            arma.save()
            
            tipo_msg = 'interna' if tipo_manutencao == 'INTERNA' else 'externa'
            messages.success(
                self.request, 
                f'Arma {arma.numero_serie} enviada para manutenção {tipo_msg} com sucesso!'
            )
        elif tipo_mov == 'RETORNO_MANUTENCAO':
            # Validar se a arma está em manutenção
            if arma.situacao != 'EM_MANUTENCAO':
                messages.error(
                    self.request,
                    f'A arma {arma.numero_serie} não pode retornar de manutenção. '
                    f'A arma deve estar em "Em Manutenção" para poder retornar. '
                    f'Situação atual: {arma.get_situacao_display()}'
                )
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'A arma não pode retornar de manutenção. A arma deve estar em "Em Manutenção". Situação atual: {arma.get_situacao_display()}',
                        'errors': {'tipo_movimentacao': ['A arma deve estar em Manutenção para poder retornar.']}
                    }, status=400)
                form.add_error('tipo_movimentacao', 'A arma deve estar em Manutenção para poder retornar.')
                return self.form_invalid(form)
            
            # Verificar se existe uma manutenção sem retorno
            ultima_manutencao = arma.movimentacoes.filter(
                tipo_movimentacao='MANUTENCAO'
            ).order_by('-data_movimentacao').first()
            
            if not ultima_manutencao:
                messages.error(
                    self.request,
                    f'Não foi encontrada uma manutenção para a arma {arma.numero_serie}.'
                )
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Não foi encontrada uma manutenção para esta arma.',
                        'errors': {'tipo_movimentacao': ['Não foi encontrada uma manutenção para esta arma.']}
                    }, status=400)
                form.add_error('tipo_movimentacao', 'Não foi encontrada uma manutenção para esta arma.')
                return self.form_invalid(form)
            
            # Verificar se já existe retorno para esta manutenção
            retorno_existente = arma.movimentacoes.filter(
                tipo_movimentacao='RETORNO_MANUTENCAO',
                data_movimentacao__gt=ultima_manutencao.data_movimentacao
            ).exists()
            
            if retorno_existente:
                messages.error(
                    self.request,
                    f'A arma {arma.numero_serie} já retornou da manutenção iniciada em {ultima_manutencao.data_movimentacao.strftime("%d/%m/%Y %H:%M")}.'
                )
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'A arma já retornou desta manutenção.',
                        'errors': {'tipo_movimentacao': ['A arma já retornou desta manutenção.']}
                    }, status=400)
                form.add_error('tipo_movimentacao', 'A arma já retornou desta manutenção.')
                return self.form_invalid(form)
            
            movimentacao.save()
            arma.situacao = 'RESERVA_ARMAMENTO'
            arma.save()
            messages.success(
                self.request, 
                f'Arma {arma.numero_serie} retornou de manutenção e está em Reserva de Armamento.'
            )
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Movimentação registrada com sucesso!',
                'redirect_url': str(reverse('militares:arma_detail', kwargs={'pk': arma.pk}))
            })
        
        return redirect('militares:arma_detail', pk=arma.pk)
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def _processar_organograma_manutencao(self, movimentacao, organograma_id):
        """Processa a seleção do organograma de manutenção e preenche os campos"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            movimentacao.orgao_manutencao = get_object_or_404(Orgao, pk=orgao_id)
            movimentacao.grande_comando_manutencao = None
            movimentacao.unidade_manutencao = None
            movimentacao.sub_unidade_manutencao = None
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            gc = get_object_or_404(GrandeComando, pk=gc_id)
            movimentacao.orgao_manutencao = gc.orgao
            movimentacao.grande_comando_manutencao = gc
            movimentacao.unidade_manutencao = None
            movimentacao.sub_unidade_manutencao = None
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            unidade = get_object_or_404(Unidade, pk=unidade_id)
            movimentacao.orgao_manutencao = unidade.grande_comando.orgao
            movimentacao.grande_comando_manutencao = unidade.grande_comando
            movimentacao.unidade_manutencao = unidade
            movimentacao.sub_unidade_manutencao = None
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            sub = get_object_or_404(SubUnidade, pk=sub_id)
            movimentacao.orgao_manutencao = sub.unidade.grande_comando.orgao
            movimentacao.grande_comando_manutencao = sub.unidade.grande_comando
            movimentacao.unidade_manutencao = sub.unidade
            movimentacao.sub_unidade_manutencao = sub
    
    def _processar_organograma_destino(self, arma, organograma_id):
        """Processa a seleção do organograma e atualiza os campos de organização da arma"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            arma.orgao = get_object_or_404(Orgao, pk=orgao_id)
            arma.grande_comando = None
            arma.unidade = None
            arma.sub_unidade = None
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            gc = get_object_or_404(GrandeComando, pk=gc_id)
            arma.orgao = gc.orgao
            arma.grande_comando = gc
            arma.unidade = None
            arma.sub_unidade = None
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            unidade = get_object_or_404(Unidade, pk=unidade_id)
            arma.orgao = unidade.grande_comando.orgao
            arma.grande_comando = unidade.grande_comando
            arma.unidade = unidade
            arma.sub_unidade = None
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            sub = get_object_or_404(SubUnidade, pk=sub_id)
            arma.orgao = sub.unidade.grande_comando.orgao
            arma.grande_comando = sub.unidade.grande_comando
            arma.unidade = sub.unidade
            arma.sub_unidade = sub
    
    def _processar_organograma_para_instancia(self, organograma_id):
        """Processa a seleção do organograma e retorna a instância correspondente"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            return get_object_or_404(Orgao, pk=orgao_id)
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            return get_object_or_404(GrandeComando, pk=gc_id)
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            return get_object_or_404(Unidade, pk=unidade_id)
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            return get_object_or_404(SubUnidade, pk=sub_id)
        return None
    
    def _formatar_organizacao(self, org_instancia):
        """Formata a organização em texto hierárquico"""
        if not org_instancia:
            return ''
        
        if isinstance(org_instancia, SubUnidade):
            return f"{org_instancia.unidade.grande_comando.orgao} > {org_instancia.unidade.grande_comando} > {org_instancia.unidade} > {org_instancia}"
        elif isinstance(org_instancia, Unidade):
            return f"{org_instancia.grande_comando.orgao} > {org_instancia.grande_comando} > {org_instancia}"
        elif isinstance(org_instancia, GrandeComando):
            return f"{org_instancia.orgao} > {org_instancia}"
        elif isinstance(org_instancia, Orgao):
            return str(org_instancia)
        return ''


class ArmaTransferenciaView(LoginRequiredMixin, FormView):
    """View para transferir uma arma de uma organização para outra"""
    form_class = TransferenciaArmaForm
    template_name = 'militares/arma_transferencia.html'
    
    def get_arma(self):
        """Obtém a arma a ser transferida"""
        return get_object_or_404(Arma, pk=self.kwargs['pk'], ativo=True)
    
    def get_form_kwargs(self):
        """Passa a arma para o formulário"""
        kwargs = super().get_form_kwargs()
        kwargs['arma'] = self.get_arma()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        arma = self.get_arma()
        
        # Organização atual (origem) - preencher ID para o select
        if arma.sub_unidade:
            organizacao_origem_id = f"sub_{arma.sub_unidade.id}"
        elif arma.unidade:
            organizacao_origem_id = f"unidade_{arma.unidade.id}"
        elif arma.grande_comando:
            organizacao_origem_id = f"gc_{arma.grande_comando.id}"
        elif arma.orgao:
            organizacao_origem_id = f"orgao_{arma.orgao.id}"
        else:
            organizacao_origem_id = None
        
        context['organizacao_origem_id'] = organizacao_origem_id
        context['arma'] = arma
        
        # Listas para o select de organograma
        organizacoes = []
        organizacoes.extend([(f"orgao_{o.id}", f"Órgão: {o.nome}") for o in Orgao.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"gc_{gc.id}", f"GC: {gc.nome}") for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"unidade_{u.id}", f"Unidade: {u.nome}") for u in Unidade.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"sub_{su.id}", f"Sub-Unidade: {su.nome}") for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
        context['organizacoes'] = organizacoes
        
        return context
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                form = self.get_form()
                context = self.get_context_data(form=form)
                from django.template.loader import render_to_string
                html = render_to_string('militares/arma_transferencia_modal_content.html', context, request=request)
                return JsonResponse({'html': html})
            except Exception as e:
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                error_trace = traceback.format_exc()
                logger.error(f"Erro ao carregar formulário de transferência de arma: {str(e)}\n{error_trace}")
                print(f"Erro ao carregar formulário de transferência de arma: {str(e)}")
                print(error_trace)
                return JsonResponse({
                    'error': str(e),
                    'message': f'Erro ao carregar formulário: {str(e)}',
                    'traceback': error_trace if request.user.is_staff else None
                }, status=500)
        return super().get(request, *args, **kwargs)
    
    @transaction.atomic
    def form_valid(self, form):
        """Processa transferência de arma entre OMs (apenas OM -> OM)"""
        arma = self.get_arma()
        
        # Validar que a arma não está em cautela individual
        if arma.situacao == 'CAUTELA_INDIVIDUAL':
            error_msg = 'Não é possível transferir uma arma que está em cautela individual. É necessário descautelar antes.'
            # Se for requisição AJAX, retornar JSON com erro
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_msg
                }, status=400)
            messages.error(self.request, error_msg)
            return redirect('militares:arma_detail', pk=arma.pk)
        
        # Processar organograma de origem
        organograma_origem_id = self.request.POST.get('organograma_origem', '')
        if organograma_origem_id:
            org_origem_instancia = self._processar_organograma_para_instancia(organograma_origem_id)
            
            # Extrair instâncias para salvar no TransferenciaArma
            if isinstance(org_origem_instancia, SubUnidade):
                orgao_origem = org_origem_instancia.unidade.grande_comando.orgao
                grande_comando_origem = org_origem_instancia.unidade.grande_comando
                unidade_origem = org_origem_instancia.unidade
                sub_unidade_origem = org_origem_instancia
            elif isinstance(org_origem_instancia, Unidade):
                orgao_origem = org_origem_instancia.grande_comando.orgao
                grande_comando_origem = org_origem_instancia.grande_comando
                unidade_origem = org_origem_instancia
                sub_unidade_origem = None
            elif isinstance(org_origem_instancia, GrandeComando):
                orgao_origem = org_origem_instancia.orgao
                grande_comando_origem = org_origem_instancia
                unidade_origem = None
                sub_unidade_origem = None
            elif isinstance(org_origem_instancia, Orgao):
                orgao_origem = org_origem_instancia
                grande_comando_origem = None
                unidade_origem = None
                sub_unidade_origem = None
            else:
                orgao_origem = None
                grande_comando_origem = None
                unidade_origem = None
                sub_unidade_origem = None
        else:
            # Se não foi selecionado, usar a organização atual da arma
            orgao_origem = arma.orgao
            grande_comando_origem = arma.grande_comando
            unidade_origem = arma.unidade
            sub_unidade_origem = arma.sub_unidade
        
        # Processar seleção do organograma de destino e atualizar a arma
        organograma_destino_id = self.request.POST.get('organograma_destino', '')
        if organograma_destino_id:
            self._processar_organograma_destino(arma, organograma_destino_id)
        
        # Atualizar a arma com a nova organização
        arma.save()
        arma.situacao = 'RESERVA_ARMAMENTO'
        arma.militar_responsavel = None
        arma.data_entrega_responsavel = None
        arma.save()
        
        # Criar registro de transferência
        transferencia = TransferenciaArma.objects.create(
            arma=arma,
            orgao_origem=orgao_origem,
            grande_comando_origem=grande_comando_origem,
            unidade_origem=unidade_origem,
            sub_unidade_origem=sub_unidade_origem,
            orgao_destino=arma.orgao,
            grande_comando_destino=arma.grande_comando,
            unidade_destino=arma.unidade,
            sub_unidade_destino=arma.sub_unidade,
            transferido_por=self.request.user,
            quantidade_carregadores=form.cleaned_data.get('quantidade_carregadores'),
            numeracao_carregadores=form.cleaned_data.get('numeracao_carregadores', ''),
            quantidade_municoes_catalogadas=form.cleaned_data.get('quantidade_municoes_catalogadas'),
            observacoes=form.cleaned_data.get('observacoes', '')
        )
        
        # Criar movimentação para histórico
        movimentacao = MovimentacaoArma.objects.create(
            arma=arma,
            tipo_movimentacao='TRANSFERENCIA',
            data_movimentacao=timezone.now(),
            organizacao_origem=transferencia.get_organizacao_origem(),
            organizacao_destino=transferencia.get_organizacao_destino(),
            quantidade_carregadores=form.cleaned_data.get('quantidade_carregadores'),
            numeracao_carregadores=form.cleaned_data.get('numeracao_carregadores', ''),
            quantidade_municoes_catalogadas=form.cleaned_data.get('quantidade_municoes_catalogadas'),
            observacoes=f"Transferência realizada. Justificativa: {form.cleaned_data['justificativa']}",
            responsavel_movimentacao=self.request.user
        )
        
        # Não registrar no histórico de alterações - apenas no histórico de transferências
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Arma {arma.numero_serie} transferida com sucesso de {transferencia.get_organizacao_origem()} para {transferencia.get_organizacao_destino()}!',
                'redirect_url': str(reverse('militares:arma_detail', kwargs={'pk': arma.pk}))
            })
        
        messages.success(
            self.request, 
            f'Arma {arma.numero_serie} transferida com sucesso de {transferencia.get_organizacao_origem()} para {transferencia.get_organizacao_destino()}!'
        )
        return redirect('militares:arma_detail', pk=arma.pk)
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        return super().form_invalid(form)
    
    def _processar_organograma_destino(self, arma, organograma_id):
        """Processa a seleção do organograma e atualiza os campos de organização da arma"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            arma.orgao = get_object_or_404(Orgao, pk=orgao_id)
            arma.grande_comando = None
            arma.unidade = None
            arma.sub_unidade = None
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            gc = get_object_or_404(GrandeComando, pk=gc_id)
            arma.orgao = gc.orgao
            arma.grande_comando = gc
            arma.unidade = None
            arma.sub_unidade = None
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            unidade = get_object_or_404(Unidade, pk=unidade_id)
            arma.orgao = unidade.grande_comando.orgao
            arma.grande_comando = unidade.grande_comando
            arma.unidade = unidade
            arma.sub_unidade = None
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            sub = get_object_or_404(SubUnidade, pk=sub_id)
            arma.orgao = sub.unidade.grande_comando.orgao
            arma.grande_comando = sub.unidade.grande_comando
            arma.unidade = sub.unidade
            arma.sub_unidade = sub
    
    def _processar_organograma_para_instancia(self, organograma_id):
        """Processa a seleção do organograma e retorna a instância correspondente"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            return get_object_or_404(Orgao, pk=orgao_id)
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            return get_object_or_404(GrandeComando, pk=gc_id)
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            return get_object_or_404(Unidade, pk=unidade_id)
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            return get_object_or_404(SubUnidade, pk=sub_id)
        return None
    
    def _processar_organograma_manutencao(self, movimentacao, organograma_id):
        """Processa a seleção do organograma de manutenção e preenche os campos"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            movimentacao.orgao_manutencao = get_object_or_404(Orgao, pk=orgao_id)
            movimentacao.grande_comando_manutencao = None
            movimentacao.unidade_manutencao = None
            movimentacao.sub_unidade_manutencao = None
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            gc = get_object_or_404(GrandeComando, pk=gc_id)
            movimentacao.orgao_manutencao = gc.orgao
            movimentacao.grande_comando_manutencao = gc
            movimentacao.unidade_manutencao = None
            movimentacao.sub_unidade_manutencao = None
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            unidade = get_object_or_404(Unidade, pk=unidade_id)
            movimentacao.orgao_manutencao = unidade.grande_comando.orgao
            movimentacao.grande_comando_manutencao = unidade.grande_comando
            movimentacao.unidade_manutencao = unidade
            movimentacao.sub_unidade_manutencao = None
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            sub = get_object_or_404(SubUnidade, pk=sub_id)
            movimentacao.orgao_manutencao = sub.unidade.grande_comando.orgao
            movimentacao.grande_comando_manutencao = sub.unidade.grande_comando
            movimentacao.unidade_manutencao = sub.unidade
            movimentacao.sub_unidade_manutencao = sub



# Views para Configuração de Armas
class ConfiguracaoArmaListView(LoginRequiredMixin, ListView):
    """Lista todas as configurações de armas"""
    model = ConfiguracaoArma
    template_name = 'militares/configuracao_arma_list.html'
    context_object_name = 'configuracoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ConfiguracaoArma.objects.all().order_by('marca', 'modelo')
        
        # Filtros
        search = self.request.GET.get('search', '')
        tipo = self.request.GET.get('tipo', '')
        calibre = self.request.GET.get('calibre', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(marca__icontains=search) |
                Q(modelo__icontains=search)
            )
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if calibre:
            queryset = queryset.filter(calibre=calibre)
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['tipo'] = self.request.GET.get('tipo', '')
        context['calibre'] = self.request.GET.get('calibre', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Listas para filtros
        context['tipos'] = ConfiguracaoArma.TIPO_CHOICES
        context['calibres'] = ConfiguracaoArma.CALIBRE_CHOICES
        
        return context


class ConfiguracaoArmaCreateView(LoginRequiredMixin, CreateView):
    """Criar nova configuração de arma"""
    model = ConfiguracaoArma
    form_class = ConfiguracaoArmaForm
    template_name = 'militares/configuracao_arma_form.html'
    success_url = reverse_lazy('militares:configuracao_arma_list')
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        
        # Se for requisição AJAX, retornar JSON
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Configuração de arma cadastrada com sucesso!',
                'redirect_url': str(self.success_url)
            })
        
        messages.success(self.request, 'Configuração de arma cadastrada com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = None
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/configuracao_arma_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ConfiguracaoArmaDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma configuração de arma"""
    model = ConfiguracaoArma
    template_name = 'militares/configuracao_arma_detail.html'
    context_object_name = 'configuracao'


class ConfiguracaoArmaUpdateView(LoginRequiredMixin, UpdateView):
    """Editar configuração de arma"""
    model = ConfiguracaoArma
    form_class = ConfiguracaoArmaForm
    template_name = 'militares/configuracao_arma_form.html'
    success_url = reverse_lazy('militares:configuracao_arma_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Configuração de arma atualizada com sucesso!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)


class ConfiguracaoArmaDeleteView(LoginRequiredMixin, DeleteView):
    """Excluir configuração de arma"""
    model = ConfiguracaoArma
    template_name = 'militares/configuracao_arma_confirm_delete.html'
    success_url = reverse_lazy('militares:configuracao_arma_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Configuração de arma excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


# Views para Configuração de Munições
class ConfiguracaoMunicaoListView(LoginRequiredMixin, ListView):
    """Lista todas as configurações de munições"""
    model = ConfiguracaoMunicao
    template_name = 'militares/configuracao_municao_list.html'
    context_object_name = 'configuracoes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ConfiguracaoMunicao.objects.all().order_by('calibre', 'marca', 'modelo')
        
        # Filtros
        search = self.request.GET.get('search', '')
        calibre = self.request.GET.get('calibre', '')
        tipo_municao = self.request.GET.get('tipo_municao', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(marca__icontains=search) |
                Q(modelo__icontains=search)
            )
        
        if calibre:
            queryset = queryset.filter(calibre=calibre)
        
        if tipo_municao:
            queryset = queryset.filter(tipo_municao=tipo_municao)
        
        if ativo == '1':
            queryset = queryset.filter(ativo=True)
        elif ativo == '0':
            queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['calibre'] = self.request.GET.get('calibre', '')
        context['tipo_municao'] = self.request.GET.get('tipo_municao', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Listas para filtros
        context['calibres'] = ConfiguracaoMunicao.CALIBRE_CHOICES
        context['tipos_municao'] = ConfiguracaoMunicao.TIPO_MUNICAO_CHOICES
        
        return context


class ConfiguracaoMunicaoCreateView(LoginRequiredMixin, CreateView):
    """Criar nova configuração de munição"""
    model = ConfiguracaoMunicao
    form_class = ConfiguracaoMunicaoForm
    template_name = 'militares/configuracao_municao_form.html'
    success_url = reverse_lazy('militares:configuracao_municao_list')
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        
        # Se for requisição AJAX, retornar JSON
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Configuração de munição cadastrada com sucesso!',
                'redirect_url': str(self.success_url)
            })
        
        messages.success(self.request, 'Configuração de munição cadastrada com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = None
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/configuracao_municao_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ConfiguracaoMunicaoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma configuração de munição"""
    model = ConfiguracaoMunicao
    template_name = 'militares/configuracao_municao_detail.html'
    context_object_name = 'configuracao'
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do modal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            context = self.get_context_data()
            from django.template.loader import render_to_string
            html = render_to_string('militares/configuracao_municao_detail_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ConfiguracaoMunicaoUpdateView(LoginRequiredMixin, UpdateView):
    """Editar configuração de munição"""
    model = ConfiguracaoMunicao
    form_class = ConfiguracaoMunicaoForm
    template_name = 'militares/configuracao_municao_form.html'
    success_url = reverse_lazy('militares:configuracao_municao_list')
    
    def form_valid(self, form):
        # Se for requisição AJAX, retornar JSON
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Configuração de munição atualizada com sucesso!',
                'redirect_url': str(self.success_url)
            })
        messages.success(self.request, 'Configuração de munição atualizada com sucesso!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = self.get_object()
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/configuracao_municao_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class ConfiguracaoMunicaoDeleteView(LoginRequiredMixin, DeleteView):
    """Excluir configuração de munição"""
    model = ConfiguracaoMunicao
    template_name = 'militares/configuracao_municao_confirm_delete.html'
    success_url = reverse_lazy('militares:configuracao_municao_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Configuração de munição excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def assinar_movimentacao_entregando(request, pk):
    """Assinar movimentação como quem está entregando"""
    movimentacao = get_object_or_404(MovimentacaoArma, pk=pk)
    
    if request.method == 'POST':
        senha = request.POST.get('senha')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        observacoes = request.POST.get('observacoes', '')
        
        # Verificar senha do usuário
        if not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
        
        # Verificar se já existe uma assinatura deste tipo
        assinatura_existente = AssinaturaMovimentacaoArma.objects.filter(
            movimentacao=movimentacao,
            tipo_assinatura='ENTREGANDO'
        ).first()
        
        if assinatura_existente:
            messages.error(request, 'Esta movimentação já possui assinatura de entregador.')
            return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
        
        # Buscar militar associado ao usuário (relacionamento reverso)
        militar = None
        try:
            militar = request.user.militar
        except:
            pass
        
        # Usar função selecionada ou função padrão
        if not funcao_assinatura:
            funcao_assinatura = request.session.get('funcao_atual_nome', 'Usuário do Sistema')
        
        # Criar a assinatura
        try:
            assinatura = AssinaturaMovimentacaoArma.objects.create(
                movimentacao=movimentacao,
                assinado_por=request.user,
                militar=militar,
                tipo_assinatura='ENTREGANDO',
                funcao_assinatura=funcao_assinatura,
                observacoes=observacoes
            )
            messages.success(request, 'Assinatura registrada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao assinar movimentação: {str(e)}')
        
        return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
    
    return redirect('militares:arma_detail', pk=movimentacao.arma.pk)


@login_required
def assinar_movimentacao_recebendo(request, pk):
    """Assinar movimentação como quem está recebendo"""
    movimentacao = get_object_or_404(MovimentacaoArma, pk=pk)
    
    if request.method == 'POST':
        senha = request.POST.get('senha')
        funcao_assinatura = request.POST.get('funcao_assinatura', '')
        observacoes = request.POST.get('observacoes', '')
        
        # Verificar se há um militar de destino
        if not movimentacao.militar_destino:
            messages.error(request, 'Esta movimentação não possui militar de destino definido.')
            return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
        
        # Verificar se o usuário atual é o militar de destino ou tem permissão
        militar_destino = movimentacao.militar_destino
        user_destino = militar_destino.user if militar_destino.user else None
        
        # Verificar se o usuário atual pode assinar
        pode_assinar = False
        if user_destino == request.user:
            pode_assinar = True
        elif request.user.is_superuser:
            pode_assinar = True
        
        if not pode_assinar:
            messages.error(request, 'Você não tem permissão para assinar como recebedor. Apenas o militar de destino pode assinar.')
            return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
        
        # Verificar senha (apenas se não for superuser)
        if not request.user.is_superuser and not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
        
        # Verificar se já existe uma assinatura deste tipo
        assinatura_existente = AssinaturaMovimentacaoArma.objects.filter(
            movimentacao=movimentacao,
            tipo_assinatura='RECEBENDO'
        ).first()
        
        if assinatura_existente:
            messages.error(request, 'Esta movimentação já possui assinatura de recebedor.')
            return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
        
        # Usar função selecionada ou função padrão
        if not funcao_assinatura:
            funcao_assinatura = request.session.get('funcao_atual_nome', 'Bombeiro Militar')
        
        # Criar a assinatura
        try:
            assinatura = AssinaturaMovimentacaoArma.objects.create(
                movimentacao=movimentacao,
                assinado_por=user_destino if user_destino else request.user,
                militar=militar_destino,
                tipo_assinatura='RECEBENDO',
                funcao_assinatura=funcao_assinatura,
                observacoes=observacoes
            )
            messages.success(request, 'Assinatura registrada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao assinar movimentação: {str(e)}')
        
        return redirect('militares:arma_detail', pk=movimentacao.arma.pk)
    
    return redirect('militares:arma_detail', pk=movimentacao.arma.pk)


@login_required
def armas_pdf(request):
    """Gera PDF com lista de armas no padrão das certidões de tempo de serviço"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    from django.db.models import Case, When, IntegerField
    import pytz
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
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
        from django.conf import settings
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo_cbmepi.png')
        if not os.path.exists(logo_path) and settings.STATICFILES_DIRS:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'logo_cbmepi.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA ADMINISTRATIVA E FINANCEIRA",
            "SEÇÃO DE CONTROLE DE ARMAS E MUNIÇÕES",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>RELATÓRIO DE ARMAS</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Obter filtros da URL
        search = request.GET.get('search', '').strip()
        tipo = request.GET.get('tipo', '').strip()
        situacao = request.GET.get('situacao', '').strip()
        organizacao = request.GET.get('organizacao', '').strip()
        ativo = request.GET.get('ativo', '').strip()
        
        # Buscar armas com os mesmos filtros da lista
        queryset = Arma.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'militar_responsavel', 'criado_por'
        ).annotate(
            situacao_ordem=Case(
                When(situacao='EM_MANUTENCAO', then=1),
                When(situacao='CAUTELA_INDIVIDUAL', then=2),
                When(situacao='RESERVA_ARMAMENTO', then=3),
                When(situacao='INSERVIVEL', then=4),
                default=5,
                output_field=IntegerField()
            )
        ).order_by('situacao_ordem', 'numero_serie')
        
        # Aplicar filtros
        if search:
            queryset = queryset.filter(
                Q(numero_serie__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search) |
                Q(numero_registro_policia__icontains=search)
            )
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if situacao:
            queryset = queryset.filter(situacao=situacao)
        
        if organizacao:
            try:
                org_id = int(organizacao)
                queryset = queryset.filter(
                    Q(orgao_id=org_id) |
                    Q(grande_comando_id=org_id) |
                    Q(unidade_id=org_id) |
                    Q(sub_unidade_id=org_id)
                )
            except ValueError:
                pass
        
        if ativo:
            queryset = queryset.filter(ativo=(ativo == '1'))
        
        # Criar tabela com as armas
        if queryset.exists():
            # Estilo para células da tabela com word wrap (ajustado para paisagem)
            style_cell = ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=0, leading=9)
            style_header = ParagraphStyle('header', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', alignment=1)
            
            dados = []
            # Cabeçalho
            dados.append([
                Paragraph('Nº Série', style_header),
                Paragraph('Tipo', style_header),
                Paragraph('Marca/Modelo', style_header),
                Paragraph('Calibre', style_header),
                Paragraph('Situação', style_header),
                Paragraph('Organização', style_header)
            ])
            
            for arma in queryset:
                tipo_display = arma.get_tipo_display()
                marca_modelo = f"{arma.marca} {arma.modelo}".strip()
                calibre_display = arma.get_calibre_display()
                situacao_display = arma.get_situacao_display()
                organizacao_display = arma.get_organizacao_instancia()
                
                # Truncar textos para caber nas células (ajustado para paisagem)
                numero_serie = (arma.numero_serie or 'N/A')[:20]
                tipo_trunc = tipo_display[:18]
                marca_modelo_trunc = marca_modelo[:30]
                calibre_trunc = calibre_display[:12]
                situacao_trunc = situacao_display[:25]
                organizacao_trunc = organizacao_display[:35]
                
                dados.append([
                    Paragraph(numero_serie, style_cell),
                    Paragraph(tipo_trunc, style_cell),
                    Paragraph(marca_modelo_trunc, style_cell),
                    Paragraph(calibre_trunc, style_cell),
                    Paragraph(situacao_trunc, style_cell),
                    Paragraph(organizacao_trunc, style_cell)
                ])
            
            # Criar tabela com larguras ajustadas para paisagem
            # Total: ~24cm (A4 landscape com margens de 1.5cm = 29.7cm - 3cm = 26.7cm, mas deixamos 24cm para segurança)
            tabela = Table(dados, repeatRows=1, colWidths=[3.5*cm, 3*cm, 5*cm, 2.5*cm, 4.5*cm, 5.5*cm])
            tabela.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('FONTSIZE', (0,1), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('LEFTPADDING', (0,0), (-1,-1), 3),
                ('RIGHTPADDING', (0,0), (-1,-1), 3),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('WORDWRAP', (0,0), (-1,-1), True),  # Habilitar quebra de linha
            ]))
            story.append(tabela)
        else:
            story.append(Paragraph("Nenhuma arma encontrada com os filtros aplicados.", ParagraphStyle('sem_dados', parent=styles['Normal'], fontSize=11, alignment=1, spaceAfter=10)))
        
        story.append(Spacer(1, 10))
        
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
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=5)))
        
        # Obter função do formulário ou função atual
        from .permissoes_hierarquicas import obter_funcao_militar_ativa
        funcao_selecionada = request.GET.get('funcao', '')
        if not funcao_selecionada:
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_selecionada = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta)
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Adicionar espaço para assinatura física
                story.append(Spacer(1, 0.3*cm))
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=3)))
                
                # 2ª linha: Função
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=5)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=3)))
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=5)))
                story.append(Spacer(1, 0.1*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 0.3*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.2*cm))
        
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
            
            # Tabela das assinaturas: Logo + Texto de assinatura (estendida até as margens)
            # Em paisagem A4: 29.7cm - 3cm (margens) = 26.7cm disponível
            largura_disponivel = 26.7*cm
            largura_logo = 3.0*cm
            largura_texto = largura_disponivel - largura_logo
            
            assinatura_data = [
                [Image(logo_path, width=largura_logo, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[largura_logo, largura_texto])
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
        
        # Criar um objeto temporário para o autenticador (usar a primeira arma ou criar um objeto genérico)
        # Como não temos um objeto específico, vamos criar um objeto simples para o autenticador
        class ObjetoCertidaoArmas:
            def __init__(self):
                self.pk = hash(f"certidao_armas_{timezone.now().isoformat()}") % 100000000
        
        objeto_certidao = ObjetoCertidaoArmas()
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(objeto_certidao, request, tipo_documento='certidao_armas')
        
        # Tabela do rodapé: QR + Texto de autenticação (estendida até as margens)
        # Em paisagem A4: 29.7cm - 3cm (margens) = 26.7cm disponível
        largura_disponivel_rodape = 26.7*cm
        largura_qr = 3.0*cm
        largura_texto_rodape = largura_disponivel_rodape - largura_qr
        
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[largura_qr, largura_texto_rodape])
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
        data_atual_str = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'certidao_armas_{data_atual_str}.pdf'
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_details = str(e)
        # Log do erro completo para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar certidão de armas: {error_details}\n{traceback.format_exc()}')
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Certidão de Armas</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Certidão de Armas</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def arma_ficha_pdf(request, pk):
    """Gera PDF da ficha individual da arma com todos os dados"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    import pytz
    
    arma = get_object_or_404(Arma, pk=pk)
    
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
        from django.conf import settings
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo_cbmepi.png')
        if not os.path.exists(logo_path) and settings.STATICFILES_DIRS:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'logo_cbmepi.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA ADMINISTRATIVA E FINANCEIRA",
            "SEÇÃO DE CONTROLE DE ARMAS E MUNIÇÕES",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>FICHA DE ARMA</u>", style_title))
        story.append(Spacer(1, 10))
        
        # Adicionar QR Code e Código de Barras
        try:
            # Gerar QR Code da arma
            from django.contrib.sites.shortcuts import get_current_site
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            url_arma = f"{protocol}://{current_site.domain}{reverse('militares:arma_detail', kwargs={'pk': arma.pk})}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(url_arma)
            qr.make(fit=True)
            qr_img_pil = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = BytesIO()
            qr_img_pil.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            qr_img = Image(qr_buffer, width=3*cm, height=3*cm)
            
            # Gerar Código de Barras CODE128
            barcode_img = None
            try:
                from reportlab.graphics.barcode import code128
                from reportlab.graphics.shapes import Drawing
                from reportlab.graphics import renderPM
                import tempfile
                
                barcode = code128.Code128(arma.numero_serie or 'N/A', barWidth=0.8, barHeight=1.5*cm)
                barcode_drawing = Drawing(6*cm, 2*cm)
                barcode_drawing.add(barcode)
                
                # Converter Drawing para imagem PNG
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                    renderPM.drawToFile(barcode_drawing, temp_path, fmt='PNG', dpi=72)
                    barcode_img = Image(temp_path, width=6*cm, height=1.5*cm)
                    # Remover arquivo temporário após usar
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            except ImportError:
                # Se não tiver reportlab.graphics.barcode, usar alternativa python-barcode
                try:
                    import barcode
                    from barcode.writer import ImageWriter
                    code128_barcode = barcode.get_barcode_class('code128')
                    barcode_instance = code128_barcode(arma.numero_serie or 'N/A', writer=ImageWriter())
                    barcode_buffer = BytesIO()
                    barcode_instance.write(barcode_buffer)
                    barcode_buffer.seek(0)
                    barcode_img = Image(barcode_buffer, width=6*cm, height=1.5*cm)
                except:
                    barcode_img = None
            except Exception as e:
                barcode_img = None
            
            # QR Code com número de série abaixo, alinhado à direita da página
            if barcode_img:
                # Tabela com QR Code + Nº Série à direita e Código de Barras à esquerda
                # Criar uma tabela aninhada para QR Code + Nº Série
                qr_nserie_data = [
                    [qr_img],
                    [Paragraph(arma.numero_serie or 'N/A', style_bold)]
                ]
                qr_nserie_table = Table(qr_nserie_data, colWidths=[3*cm])
                qr_nserie_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                codigos_data = [
                    [Paragraph('<b>Código de Barras:</b>', style_normal), qr_nserie_table],
                    [barcode_img, '']
                ]
                codigos_table = Table(codigos_data, colWidths=[11*cm, 3*cm])
                codigos_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                    ('ALIGN', (0, 1), (0, 1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
            else:
                # Apenas QR Code com número de série abaixo, alinhado à direita
                # Usar uma tabela com espaço vazio à esquerda para alinhar à direita
                codigos_data = [
                    ['', qr_img],
                    ['', Paragraph(arma.numero_serie or 'N/A', style_bold)]
                ]
                codigos_table = Table(codigos_data, colWidths=[11*cm, 3*cm])
                codigos_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
            
            story.append(codigos_table)
            story.append(Spacer(1, 10))
        except Exception as e:
            # Se houver erro, apenas continuar sem os códigos
            pass
        
        # Informações da Arma
        info_data = []
        
        # Estilo para células com word wrap
        style_cell_label = ParagraphStyle('cell_label', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=0)
        style_cell_value = ParagraphStyle('cell_value', parent=styles['Normal'], fontSize=10, alignment=0, leading=12)
        
        # Dados Básicos
        info_data.append([Paragraph('Número de Série:', style_cell_label), Paragraph(arma.numero_serie or 'N/A', style_cell_value)])
        info_data.append([Paragraph('Tipo:', style_cell_label), Paragraph(arma.get_tipo_display(), style_cell_value)])
        info_data.append([Paragraph('Marca:', style_cell_label), Paragraph(arma.marca or 'N/A', style_cell_value)])
        info_data.append([Paragraph('Modelo:', style_cell_label), Paragraph(arma.modelo or 'N/A', style_cell_value)])
        info_data.append([Paragraph('Calibre:', style_cell_label), Paragraph(arma.get_calibre_display(), style_cell_value)])
        info_data.append([Paragraph('Situação:', style_cell_label), Paragraph(arma.get_situacao_display(), style_cell_value)])
        if arma.estado_conservacao:
            info_data.append([Paragraph('Estado de Conservação:', style_cell_label), Paragraph(arma.get_estado_conservacao_display(), style_cell_value)])
        
        # Informações de Tombamento
        if arma.nome_tombamento:
            info_data.append([Paragraph('Nome do Tombamento:', style_cell_label), Paragraph(arma.nome_tombamento[:80] + ('...' if len(arma.nome_tombamento) > 80 else ''), style_cell_value)])
        if arma.numero_tombamento:
            info_data.append([Paragraph('Nº Tombamento:', style_cell_label), Paragraph(arma.numero_tombamento, style_cell_value)])
        if arma.cod_tombamento:
            info_data.append([Paragraph('COD Tombamento:', style_cell_label), Paragraph(arma.cod_tombamento, style_cell_value)])
        if arma.local_tombamento:
            info_data.append([Paragraph('Local Tombamento:', style_cell_label), Paragraph(arma.local_tombamento, style_cell_value)])
        
        # Características Técnicas
        if arma.alma_raiada:
            info_data.append([Paragraph('Alma Raiada:', style_cell_label), Paragraph('Sim', style_cell_value)])
            if arma.quantidade_raias:
                info_data.append([Paragraph('Quantidade de Raias:', style_cell_label), Paragraph(str(arma.quantidade_raias), style_cell_value)])
            if arma.direcao_raias:
                direcao_display = 'Direita' if arma.direcao_raias == 'DIREITA' else 'Esquerda'
                info_data.append([Paragraph('Direção das Raias:', style_cell_label), Paragraph(direcao_display, style_cell_value)])
        else:
            info_data.append([Paragraph('Alma Raiada:', style_cell_label), Paragraph('Não', style_cell_value)])
        if arma.capacidade_carregador:
            info_data.append([Paragraph('Capacidade do Carregador:', style_cell_label), Paragraph(f"{arma.capacidade_carregador} munições", style_cell_value)])
        
        # Organização
        org_instancia = arma.get_organizacao_instancia()
        if org_instancia != "Não definido":
            info_data.append([Paragraph('Organização:', style_cell_label), Paragraph(org_instancia[:60] + ('...' if len(org_instancia) > 60 else ''), style_cell_value)])
        
        # Militar Responsável (se houver)
        if arma.militar_responsavel:
            posto_display = arma.militar_responsavel.get_posto_graduacao_display()
            militar_str = f"{posto_display} BM {arma.militar_responsavel.nome_completo}"
            info_data.append([Paragraph('Militar Responsável:', style_cell_label), Paragraph(militar_str[:60] + ('...' if len(militar_str) > 60 else ''), style_cell_value)])
            info_data.append([Paragraph('Matrícula:', style_cell_label), Paragraph(arma.militar_responsavel.matricula or 'N/A', style_cell_value)])
            if arma.data_entrega_responsavel:
                info_data.append([Paragraph('Data de Entrega:', style_cell_label), Paragraph(arma.data_entrega_responsavel.strftime("%d/%m/%Y"), style_cell_value)])
        
        # Dados para Inquérito PM
        if arma.situacao == 'ANEXADO_INQUERITO_PM':
            if arma.numero_inquerito_pm:
                info_data.append([Paragraph('Nº Inquérito PM:', style_cell_label), Paragraph(arma.numero_inquerito_pm, style_cell_value)])
            if arma.encarregado_inquerito_pm:
                posto_enc = arma.encarregado_inquerito_pm.get_posto_graduacao_display()
                enc_str = f"{posto_enc} BM {arma.encarregado_inquerito_pm.nome_completo}"
                info_data.append([Paragraph('Encarregado:', style_cell_label), Paragraph(enc_str[:60] + ('...' if len(enc_str) > 60 else ''), style_cell_value)])
        
        # Dados para Inquérito PC
        if arma.situacao == 'ANEXADO_INQUERITO_PC':
            if arma.numero_inquerito_pc:
                info_data.append([Paragraph('Nº Inquérito PC:', style_cell_label), Paragraph(arma.numero_inquerito_pc, style_cell_value)])
            if arma.delegado_inquerito_pc:
                info_data.append([Paragraph('Delegado Responsável:', style_cell_label), Paragraph(arma.delegado_inquerito_pc[:60] + ('...' if len(arma.delegado_inquerito_pc) > 60 else ''), style_cell_value)])
        
        # Documentação
        if arma.numero_registro_policia:
            info_data.append([Paragraph('Nº Registro SIGMA:', style_cell_label), Paragraph(arma.numero_registro_policia, style_cell_value)])
        if arma.numero_guia_transito:
            info_data.append([Paragraph('Nº Guia de Trânsito:', style_cell_label), Paragraph(arma.numero_guia_transito, style_cell_value)])
        if arma.data_aquisicao:
            info_data.append([Paragraph('Data de Aquisição:', style_cell_label), Paragraph(arma.data_aquisicao.strftime("%d/%m/%Y"), style_cell_value)])
        if arma.fornecedor:
            info_data.append([Paragraph('Fornecedor:', style_cell_label), Paragraph(arma.fornecedor[:60] + ('...' if len(arma.fornecedor) > 60 else ''), style_cell_value)])
        if arma.valor_aquisicao:
            valor_str = f"R$ {arma.valor_aquisicao:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            info_data.append([Paragraph('Valor de Aquisição:', style_cell_label), Paragraph(valor_str, style_cell_value)])
        
        # Observações
        if arma.observacoes:
            obs_trunc = arma.observacoes[:200] + ('...' if len(arma.observacoes) > 200 else '')
            info_data.append([Paragraph('Observações:', style_cell_label), Paragraph(obs_trunc, style_cell_value)])
        
        # Status
        status = "Ativa" if arma.ativo else "Inativa"
        info_data.append([Paragraph('Status:', style_cell_label), Paragraph(status, style_cell_value)])
        if arma.data_criacao:
            info_data.append([Paragraph('Data de Cadastro:', style_cell_label), Paragraph(arma.data_criacao.strftime("%d/%m/%Y %H:%M"), style_cell_value)])
        if arma.criado_por:
            criado_por_str = arma.criado_por.get_full_name() or arma.criado_por.username
            info_data.append([Paragraph('Cadastrado por:', style_cell_label), Paragraph(criado_por_str[:60] + ('...' if len(criado_por_str) > 60 else ''), style_cell_value)])
        
        # Criar tabela de informações
        info_table = Table(info_data, colWidths=[5*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('WORDWRAP', (0, 0), (-1, -1), True),  # Habilitar quebra de linha
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Quebra de página para iniciar histórico na 2ª página
        story.append(PageBreak())
        
        # Histórico da Arma
        story.append(Paragraph("<b>HISTÓRICO DA ARMA</b>", ParagraphStyle('titulo_historico', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', alignment=1, spaceAfter=10)))
        story.append(Spacer(1, 5))
        
        # Estilo para células do histórico
        style_hist_cell = ParagraphStyle('hist_cell', parent=styles['Normal'], fontSize=7, alignment=0, leading=8)
        style_hist_header = ParagraphStyle('hist_header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)
        
        # Histórico de Movimentações
        movimentacoes = MovimentacaoArma.objects.filter(
            arma=arma
        ).select_related('militar_origem', 'militar_destino', 'responsavel_movimentacao').order_by('-data_movimentacao')[:20]
        
        if movimentacoes.exists():
            story.append(Paragraph("<b>Movimentações:</b>", ParagraphStyle('subtitulo_historico', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=1, spaceAfter=5)))
            
            hist_mov_data = []
            hist_mov_data.append([
                Paragraph('Data', style_hist_header),
                Paragraph('Tipo', style_hist_header),
                Paragraph('Origem', style_hist_header),
                Paragraph('Destino', style_hist_header),
                Paragraph('Observações', style_hist_header)
            ])
            for mov in movimentacoes:
                tipo = mov.get_tipo_movimentacao_display()
                origem = ''
                if mov.militar_origem:
                    origem = f"{mov.militar_origem.get_posto_graduacao_display()} {mov.militar_origem.nome_guerra}"[:22]
                elif mov.organizacao_origem:
                    origem = mov.organizacao_origem[:22]
                else:
                    origem = 'N/A'
                
                destino = ''
                if mov.militar_destino:
                    destino = f"{mov.militar_destino.get_posto_graduacao_display()} {mov.militar_destino.nome_guerra}"[:22]
                elif mov.organizacao_destino:
                    destino = mov.organizacao_destino[:22]
                else:
                    destino = 'N/A'
                
                obs = (mov.observacoes or '')[:25]
                
                hist_mov_data.append([
                    Paragraph(mov.data_movimentacao.strftime("%d/%m/%Y %H:%M"), style_hist_cell),
                    Paragraph(tipo[:18], style_hist_cell),
                    Paragraph(origem, style_hist_cell),
                    Paragraph(destino, style_hist_cell),
                    Paragraph(obs, style_hist_cell)
                ])
            
            hist_mov_table = Table(hist_mov_data, repeatRows=1, colWidths=[3*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm])
            hist_mov_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('FONTSIZE', (0,1), (-1,-1), 7),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('WORDWRAP', (0,0), (-1,-1), True),
            ]))
            story.append(hist_mov_table)
            story.append(Spacer(1, 10))
        
        # Histórico de Cautelas
        historico_cautelas = CautelaArma.objects.filter(
            arma=arma
        ).select_related('militar', 'entregue_por', 'devolvido_por').order_by('-data_entrega')[:20]
        
        if historico_cautelas.exists():
            story.append(Paragraph("<b>Cautelas Individuais:</b>", ParagraphStyle('subtitulo_historico', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=1, spaceAfter=5)))
            
            hist_caut_data = []
            hist_caut_data.append([
                Paragraph('Data Entrega', style_hist_header),
                Paragraph('Militar', style_hist_header),
                Paragraph('Data Devolução', style_hist_header),
                Paragraph('Status', style_hist_header)
            ])
            for cautela in historico_cautelas:
                militar_str = ''
                if cautela.militar:
                    militar_str = f"{cautela.militar.get_posto_graduacao_display()} {cautela.militar.nome_guerra}"[:28]
                else:
                    militar_str = 'N/A'
                
                data_devol = cautela.data_devolucao.strftime("%d/%m/%Y %H:%M") if cautela.data_devolucao else 'Em aberto'
                status = 'Ativa' if cautela.ativa else 'Devolvida'
                
                hist_caut_data.append([
                    Paragraph(cautela.data_entrega.strftime("%d/%m/%Y %H:%M") if cautela.data_entrega else 'N/A', style_hist_cell),
                    Paragraph(militar_str, style_hist_cell),
                    Paragraph(data_devol, style_hist_cell),
                    Paragraph(status, style_hist_cell)
                ])
            
            hist_caut_table = Table(hist_caut_data, repeatRows=1, colWidths=[3*cm, 5*cm, 3*cm, 3*cm])
            hist_caut_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('FONTSIZE', (0,1), (-1,-1), 7),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('WORDWRAP', (0,0), (-1,-1), True),
            ]))
            story.append(hist_caut_table)
            story.append(Spacer(1, 10))
        
        # Histórico de Cautelas Coletivas
        historico_cautelas_coletivas = CautelaArmaColetivaItem.objects.filter(
            arma=arma
        ).select_related('cautela__responsavel').order_by('-data_entrega')[:20]
        
        if historico_cautelas_coletivas.exists():
            story.append(Paragraph("<b>Cautelas Coletivas:</b>", ParagraphStyle('subtitulo_historico', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=1, spaceAfter=5)))
            
            hist_caut_colet_data = []
            hist_caut_colet_data.append([
                Paragraph('Data Entrega', style_hist_header),
                Paragraph('Responsável', style_hist_header),
                Paragraph('Data Devolução', style_hist_header),
                Paragraph('Status', style_hist_header)
            ])
            for item in historico_cautelas_coletivas:
                responsavel_str = ''
                if item.cautela and item.cautela.responsavel:
                    responsavel_str = f"{item.cautela.responsavel.get_posto_graduacao_display()} {item.cautela.responsavel.nome_guerra}"[:28]
                else:
                    responsavel_str = 'N/A'
                
                data_devol = item.data_devolucao.strftime("%d/%m/%Y %H:%M") if item.data_devolucao else 'Em aberto'
                status = 'Devolvida' if item.devolvida else 'Ativa'
                
                hist_caut_colet_data.append([
                    Paragraph(item.data_entrega.strftime("%d/%m/%Y %H:%M") if item.data_entrega else 'N/A', style_hist_cell),
                    Paragraph(responsavel_str, style_hist_cell),
                    Paragraph(data_devol, style_hist_cell),
                    Paragraph(status, style_hist_cell)
                ])
            
            hist_caut_colet_table = Table(hist_caut_colet_data, repeatRows=1, colWidths=[3*cm, 5*cm, 3*cm, 3*cm])
            hist_caut_colet_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 8),
                ('FONTSIZE', (0,1), (-1,-1), 7),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('WORDWRAP', (0,0), (-1,-1), True),
            ]))
            story.append(hist_caut_colet_table)
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 10))
        
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
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=5)))
        
        # Obter função do formulário ou função atual
        from .permissoes_hierarquicas import obter_funcao_militar_ativa
        funcao_selecionada = request.GET.get('funcao', '')
        if not funcao_selecionada:
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_selecionada = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=3)))
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=5)))
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=3)))
                story.append(Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=5)))
                story.append(Spacer(1, 0.1*cm))
        except Exception as e:
            story.append(Spacer(1, 0.3*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.2*cm))
        
        # Adicionar assinatura eletrônica com logo
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                funcao_display = funcao_selecionada
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_selecionada
            
            agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M')
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_posto_quadro} - {funcao_display}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura (estendida até as margens)
            largura_disponivel = 16*cm
            largura_logo = 3.0*cm
            largura_texto = largura_disponivel - largura_logo
            
            assinatura_data = [
                [Image(logo_path, width=largura_logo, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[largura_logo, largura_texto])
            assinatura_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            story.append(assinatura_table)
        except Exception as e:
            story.append(Spacer(1, 1*cm))
        
        # Rodapé com QR Code
        story.append(Spacer(1, 0.1*cm))
        
        class ObjetoFichaArma:
            def __init__(self):
                self.pk = arma.pk
        
        objeto_ficha = ObjetoFichaArma()
        
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(objeto_ficha, request, tipo_documento='ficha_arma')
        
        largura_disponivel_rodape = 16*cm
        largura_qr = 3.0*cm
        largura_texto_rodape = largura_disponivel_rodape - largura_qr
        
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[largura_qr, largura_texto_rodape])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        buffer.seek(0)
        
        # Retornar PDF
        filename = f'ficha_arma_{arma.numero_serie.replace(" ", "_")}.pdf'
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_details = str(e)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar ficha da arma {arma.pk}: {error_details}\n{traceback.format_exc()}')
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Ficha de Arma</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar Ficha da Arma</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')

