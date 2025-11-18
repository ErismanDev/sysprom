"""
Views para o módulo de Viaturas
Gerencia o cadastro e controle de viaturas do CBMEPI
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
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
import qrcode
import base64
import tempfile
import os
from io import BytesIO
from PIL import Image as PILImage

from .models import Viatura, Orgao, GrandeComando, Unidade, SubUnidade, TransferenciaViatura, HistoricoAlteracaoViatura
from .forms import ViaturaForm, ViaturaTransferenciaForm


class ViaturaListView(LoginRequiredMixin, ListView):
    """Lista todas as viaturas"""
    model = Viatura
    template_name = 'militares/viatura_list.html'
    context_object_name = 'viaturas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Viatura.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'criado_por'
        ).order_by('placa')
        
        # Filtros
        search = self.request.GET.get('search', '')
        tipo = self.request.GET.get('tipo', '')
        status = self.request.GET.get('status', '')
        organizacao = self.request.GET.get('organizacao', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(placa__icontains=search) |
                Q(marca__icontains=search) |
                Q(modelo__icontains=search) |
                Q(chassi__icontains=search) |
                Q(renavam__icontains=search)
            )
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if status:
            queryset = queryset.filter(status=status)
        
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
        context['status'] = self.request.GET.get('status', '')
        context['organizacao'] = self.request.GET.get('organizacao', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        context['total_viaturas'] = Viatura.objects.count()
        context['viaturas_disponiveis'] = Viatura.objects.filter(status='DISPONIVEL', ativo=True).count()
        context['viaturas_em_uso'] = Viatura.objects.filter(status='EM_USO', ativo=True).count()
        context['viaturas_manutencao'] = Viatura.objects.filter(status='MANUTENCAO', ativo=True).count()
        
        # Listas para filtros
        context['tipos'] = Viatura.TIPO_CHOICES
        context['status_list'] = Viatura.STATUS_CHOICES
        
        # Lista de organizações para filtro
        organizacoes = []
        organizacoes.extend([(o.id, f"Órgão: {o.nome}") for o in Orgao.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(gc.id, f"GC: {gc.nome}") for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(u.id, f"Unidade: {u.nome}") for u in Unidade.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(su.id, f"Sub-Unidade: {su.nome}") for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
        context['organizacoes'] = organizacoes
        
        return context


class ViaturaCreateView(LoginRequiredMixin, CreateView):
    """Cria nova viatura"""
    model = Viatura
    form_class = ViaturaForm
    template_name = 'militares/viatura_form.html'
    success_url = reverse_lazy('militares:viatura_list')
    
    def form_valid(self, form):
        # Processar seleção do organograma se fornecido
        organograma_id = self.request.POST.get('organograma-select', '')
        if organograma_id:
            self._processar_organograma(form, organograma_id)
        
        form.instance.criado_por = self.request.user
        messages.success(self.request, f'Viatura {form.instance.placa} cadastrada com sucesso!')
        return super().form_valid(form)
    
    def _processar_organograma(self, form, organograma_id):
        """Processa a seleção do organograma e preenche os campos de organização"""
        from .models import Orgao, GrandeComando, Unidade, SubUnidade
        
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
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)


class ViaturaDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma viatura"""
    model = Viatura
    template_name = 'militares/viatura_detail.html'
    context_object_name = 'viatura'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viatura = self.object
        
        # Estatísticas de abastecimentos
        from django.db.models import Sum, Count, Avg, Q
        from decimal import Decimal
        from .models import AbastecimentoViatura, ManutencaoViatura, TrocaOleoViatura
        
        abastecimentos = AbastecimentoViatura.objects.filter(viatura=viatura, ativo=True)
        context['total_abastecimentos'] = abastecimentos.count()
        
        # Total de litros (somando apenas valores não nulos)
        total_litros = abastecimentos.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum']
        context['total_litros'] = float(total_litros) if total_litros else 0.0
        
        # Total investido em abastecimentos (usando valor_total_nota se disponível, senão valor_total)
        # valor_total_nota já inclui combustível + aditivos
        total_valor_abastecimentos = abastecimentos.aggregate(
            Sum('valor_total_nota')
        )['valor_total_nota__sum']
        
        # Se não tiver valor_total_nota, soma valor_total e valor_total_aditivo separadamente
        if total_valor_abastecimentos is None:
            total_combustivel = abastecimentos.aggregate(Sum('valor_total'))['valor_total__sum'] or Decimal('0')
            total_aditivos = abastecimentos.aggregate(Sum('valor_total_aditivo'))['valor_total_aditivo__sum'] or Decimal('0')
            context['total_valor_abastecimentos'] = float(total_combustivel + total_aditivos)
        else:
            context['total_valor_abastecimentos'] = float(total_valor_abastecimentos)
        
        # Total de aditivos (apenas para exibição separada)
        total_valor_aditivos = abastecimentos.aggregate(Sum('valor_total_aditivo'))['valor_total_aditivo__sum']
        context['total_valor_aditivos'] = float(total_valor_aditivos) if total_valor_aditivos else 0.0
        
        # Estatísticas de manutenções
        manutencoes = ManutencaoViatura.objects.filter(viatura=viatura, ativo=True)
        context['total_manutencoes'] = manutencoes.count()
        
        total_valor_manutencoes = manutencoes.aggregate(Sum('valor_manutencao'))['valor_manutencao__sum']
        context['total_valor_manutencoes'] = float(total_valor_manutencoes) if total_valor_manutencoes else 0.0
        
        # Estatísticas de trocas de óleo
        trocas_oleo = TrocaOleoViatura.objects.filter(viatura=viatura, ativo=True)
        context['total_trocas_oleo'] = trocas_oleo.count()
        
        # Para trocas de óleo, usar valor_total_nota que já inclui tudo (óleo + filtros + aditivo + outras peças)
        total_valor_trocas_oleo = trocas_oleo.aggregate(Sum('valor_total_nota'))['valor_total_nota__sum']
        
        # Se não tiver valor_total_nota, calcular manualmente somando todos os componentes
        if total_valor_trocas_oleo is None:
            # Calcular manualmente somando todos os valores
            total_manual = Decimal('0')
            for troca in trocas_oleo:
                valor = Decimal('0')
                if troca.valor_total:
                    valor += troca.valor_total
                if troca.valor_filtro_oleo:
                    valor += troca.valor_filtro_oleo
                if troca.valor_filtro_combustivel:
                    valor += troca.valor_filtro_combustivel
                if troca.valor_filtro_ar:
                    valor += troca.valor_filtro_ar
                if troca.valor_aditivo_arrefecimento:
                    valor += troca.valor_aditivo_arrefecimento
                if troca.valor_outras_pecas:
                    valor += troca.valor_outras_pecas
                total_manual += valor
            context['total_valor_trocas_oleo'] = float(total_manual)
        else:
            context['total_valor_trocas_oleo'] = float(total_valor_trocas_oleo)
        
        context['ultima_troca_oleo'] = trocas_oleo.order_by('-data_troca').first()
        
        # Histórico de alterações
        from .models import HistoricoAlteracaoViatura
        context['historico_alteracoes'] = HistoricoAlteracaoViatura.objects.filter(
            viatura=viatura
        ).select_related('alterado_por').order_by('-data_alteracao')[:20]  # Últimas 20 alterações
        
        return context


class ViaturaUpdateView(LoginRequiredMixin, UpdateView):
    """Edita viatura"""
    model = Viatura
    form_class = ViaturaForm
    template_name = 'militares/viatura_form.html'
    
    def get_form_kwargs(self):
        """Passa o request para o formulário"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse('militares:viatura_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Determinar qual opção do organograma está selecionada
        viatura = self.object
        organograma_id = None
        
        if viatura.sub_unidade:
            organograma_id = f'sub_{viatura.sub_unidade.id}'
        elif viatura.unidade:
            organograma_id = f'unidade_{viatura.unidade.id}'
        elif viatura.grande_comando:
            organograma_id = f'gc_{viatura.grande_comando.id}'
        elif viatura.orgao:
            organograma_id = f'orgao_{viatura.orgao.id}'
        
        context['organograma_selecionado'] = organograma_id
        return context
    
    def form_valid(self, form):
        # Registrar alterações antes de salvar
        viatura_antiga = Viatura.objects.get(pk=form.instance.pk) if form.instance.pk else None
        
        # Processar seleção do organograma se fornecido
        organograma_id = self.request.POST.get('organograma-select', '')
        if organograma_id:
            self._processar_organograma(form, organograma_id)
        
        # Salvar a viatura
        response = super().form_valid(form)
        
        # Registrar alterações após salvar
        if viatura_antiga:
            self._registrar_alteracoes(viatura_antiga, form.instance)
        
        messages.success(self.request, f'Viatura {form.instance.placa} atualizada com sucesso!')
        return response
    
    def _registrar_alteracoes(self, viatura_antiga, viatura_nova):
        """Registra as alterações realizadas na viatura"""
        from .models import HistoricoAlteracaoViatura
        
        # Lista de campos para monitorar alterações
        campos_monitorados = [
            'prefixo', 'placa', 'tipo', 'marca', 'modelo', 'ano_fabricacao', 'ano_modelo',
            'chassi', 'renavam', 'cor', 'km_atual', 'status', 'combustivel', 'capacidade_tanque',
            'cartao_abastecimento', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'observacoes', 'data_aquisicao', 'valor_aquisicao', 'fornecedor', 'ativo'
        ]
        
        for campo in campos_monitorados:
            try:
                valor_antigo = getattr(viatura_antiga, campo, None)
                valor_novo = getattr(viatura_nova, campo, None)
            except:
                continue  # Campo não existe, pular
            
            # Formatar valores None, ForeignKeys, datas, etc
            def formatar_valor(valor):
                if valor is None:
                    return ''
                # Verificar se é ForeignKey (modelo)
                if hasattr(valor, '_meta'):  # É um modelo Django
                    return str(valor)
                elif hasattr(valor, 'strftime'):  # Datetime/Date
                    return valor.strftime('%d/%m/%Y')
                elif isinstance(valor, bool):
                    return 'Sim' if valor else 'Não'
                elif isinstance(valor, (int, float)) or (hasattr(valor, '__float__') and not isinstance(valor, bool)):
                    # Formatar valores monetários (Decimal)
                    try:
                        from decimal import Decimal as DecimalType
                        if isinstance(valor, DecimalType):
                            # Formatar como moeda brasileira
                            valor_str = f"{valor:,.2f}"
                            return f"R$ {valor_str.replace(',', 'X').replace('.', ',').replace('X', '.')}"
                    except:
                        pass
                    return str(valor)
                else:
                    return str(valor)
            
            valor_antigo_formatado = formatar_valor(valor_antigo)
            valor_novo_formatado = formatar_valor(valor_novo)
            
            # Registrar apenas se houver alteração
            if valor_antigo_formatado != valor_novo_formatado:
                # Obter nome legível do campo
                try:
                    field = viatura_nova._meta.get_field(campo)
                    nome_campo = field.verbose_name
                except:
                    nome_campo = campo.replace('_', ' ').title()
                
                HistoricoAlteracaoViatura.objects.create(
                    viatura=viatura_nova,
                    alterado_por=self.request.user,
                    campo_alterado=nome_campo,
                    valor_anterior=valor_antigo_formatado,
                    valor_novo=valor_novo_formatado
                )
    
    def _processar_organograma(self, form, organograma_id):
        """Processa a seleção do organograma e preenche os campos de organização"""
        from .models import Orgao, GrandeComando, Unidade, SubUnidade
        
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
        messages.error(self.request, 'Por favor, corrija os erros no formulário.')
        return super().form_invalid(form)


class ViaturaDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui viatura"""
    model = Viatura
    template_name = 'militares/viatura_confirm_delete.html'
    success_url = reverse_lazy('militares:viatura_list')
    
    def delete(self, request, *args, **kwargs):
        viatura = self.get_object()
        messages.success(request, f'Viatura {viatura.placa} excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def viatura_qrcode(request, pk):
    """Gera QR Code da viatura com informações básicas e URL de acesso"""
    viatura = get_object_or_404(Viatura, pk=pk)
    
    # Criar URL completa para a viatura
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    url_viatura = f"{protocol}://{current_site.domain}{reverse('militares:viatura_detail', kwargs={'pk': viatura.pk})}"
    
    # Criar URL completa para o formulário mobile (abastecimento/manutenção)
    # URL direta que será impressa no QR Code para facilitar acesso quando fixado na viatura
    url_frota_mobile = f"{protocol}://{current_site.domain}{reverse('militares:frota_create_mobile', kwargs={'viatura_id': viatura.pk})}"
    
    # Colocar APENAS a URL completa no QR Code para que os leitores reconheçam como link direto
    # A URL completa ficará visível quando o QR Code for impresso e fixado na viatura
    qr_data = url_frota_mobile
    
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
        response['Content-Disposition'] = f'inline; filename="viatura_{viatura.placa}_qrcode.png"'
        return response
    
    # Gerar PDF para visualização
    if format_param == 'pdf' or format_param == '':
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, 
                                rightMargin=2*cm, leftMargin=2*cm, 
                                topMargin=3*cm, bottomMargin=2*cm)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Estilo para URL (monospace, menor)
        url_style = ParagraphStyle('URL', parent=styles['Normal'], 
                                   alignment=TA_CENTER, fontSize=9,
                                   fontName='Courier', leading=12,
                                   textColor=(0.2, 0.2, 0.2))
        
        # Estilo para prefixo (grande, centralizado)
        prefixo_style = ParagraphStyle('Prefixo', parent=styles['Normal'],
                                       alignment=TA_CENTER, fontSize=24,
                                       fontName='Helvetica-Bold',
                                       textColor=(1.0, 0.42, 0.21),  # Cor laranja
                                       spaceAfter=15, spaceBefore=10)
        
        # Salvar QR Code temporariamente para usar no PDF
        buffer.seek(0)
        # Criar arquivo temporário com extensão .png para o reportlab detectar o formato
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(buffer.getvalue())
            temp_qr_path = temp_file.name
        
        try:
            # Adicionar QR Code ao PDF usando o arquivo temporário
            qr_img = Image(temp_qr_path, width=10*cm, height=10*cm)
            qr_img.hAlign = 'CENTER'
            story.append(qr_img)
            story.append(Spacer(1, 1*cm))
            
            # Adicionar prefixo se existir
            if viatura.prefixo:
                story.append(Paragraph(viatura.prefixo, prefixo_style))
                story.append(Spacer(1, 1*cm))
            
            # Adicionar URL
            story.append(Paragraph(url_frota_mobile, url_style))
            
            # Usar função utilitária para criar rodapé do sistema
            from .utils import criar_rodape_sistema_pdf
            add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
            
            # Construir PDF com rodapé em todas as páginas
            doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        finally:
            # Remover arquivo temporário após usar
            if os.path.exists(temp_qr_path):
                try:
                    os.unlink(temp_qr_path)
                except:
                    pass
        
        pdf_buffer.seek(0)
        
        # Retornar PDF para visualização (inline, sem download automático)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="viatura_{viatura.placa}_qrcode.pdf"'
        return response
    
    # Fallback: renderizar HTML (para compatibilidade)
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    context = {
        'viatura': viatura,
        'url_frota_mobile': url_frota_mobile,
        'qr_base64': qr_base64,
        'protocol': protocol,
        'domain': current_site.domain,
    }
    
    return render(request, 'militares/viatura_qrcode_print.html', context)


@login_required
def viatura_autocomplete(request):
    """View para autocomplete de viaturas"""
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    
    if len(q) < 2:
        return JsonResponse({'results': []})
    
    # Buscar viaturas ativas por padrão
    viaturas = Viatura.objects.filter(ativo=True)
    
    if status_filter:
        viaturas = viaturas.filter(status=status_filter)
    
    viaturas = viaturas.filter(
        Q(placa__icontains=q) |
        Q(marca__icontains=q) |
        Q(modelo__icontains=q)
    ).order_by('placa')[:20]
    
    results = []
    for viatura in viaturas:
        results.append({
            'id': viatura.id,
            'text': f"{viatura.placa} - {viatura.get_tipo_display()} ({viatura.marca} {viatura.modelo}) - {viatura.get_status_display()}",
        })
    
    return JsonResponse({'results': results})


class ViaturaTransferenciaView(LoginRequiredMixin, FormView):
    """View para transferir uma viatura de uma unidade para outra"""
    form_class = ViaturaTransferenciaForm
    template_name = 'militares/viatura_transferencia.html'
    
    def get_viatura(self):
        """Obtém a viatura a ser transferida"""
        return get_object_or_404(Viatura, pk=self.kwargs['pk'])
    
    def get_form_kwargs(self):
        """Passa a viatura para o formulário"""
        kwargs = super().get_form_kwargs()
        kwargs['viatura'] = self.get_viatura()
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viatura = self.get_viatura()
        
        # Organização atual (origem)
        context['organizacao_origem'] = viatura.get_organizacao_instancia()
        context['viatura'] = viatura
        
        # Listas para o select de organograma
        organizacoes = []
        organizacoes.extend([(f"orgao_{o.id}", f"Órgão: {o.nome}") for o in Orgao.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"gc_{gc.id}", f"GC: {gc.nome}") for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"unidade_{u.id}", f"Unidade: {u.nome}") for u in Unidade.objects.filter(ativo=True).order_by('nome')])
        organizacoes.extend([(f"sub_{su.id}", f"Sub-Unidade: {su.nome}") for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
        context['organizacoes'] = organizacoes
        
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        viatura = self.get_viatura()
        
        # Salvar organização de origem antes de alterar
        orgao_origem = viatura.orgao
        grande_comando_origem = viatura.grande_comando
        unidade_origem = viatura.unidade
        sub_unidade_origem = viatura.sub_unidade
        
        # Processar seleção do organograma de destino
        organograma_id = self.request.POST.get('organograma_destino', '')
        if organograma_id:
            self._processar_organograma_destino(viatura, organograma_id)
        
        # Atualizar a viatura com a nova organização
        viatura.save()
        
        # Criar registro de transferência
        transferencia = TransferenciaViatura.objects.create(
            viatura=viatura,
            orgao_origem=orgao_origem,
            grande_comando_origem=grande_comando_origem,
            unidade_origem=unidade_origem,
            sub_unidade_origem=sub_unidade_origem,
            orgao_destino=viatura.orgao,
            grande_comando_destino=viatura.grande_comando,
            unidade_destino=viatura.unidade,
            sub_unidade_destino=viatura.sub_unidade,
            transferido_por=self.request.user,
            justificativa=form.cleaned_data['justificativa'],
            observacoes=form.cleaned_data.get('observacoes', '')
        )
        
        # Registrar no histórico de alterações
        HistoricoAlteracaoViatura.objects.create(
            viatura=viatura,
            alterado_por=self.request.user,
            campo_alterado='Organização (Transferência)',
            valor_anterior=transferencia.get_organizacao_origem(),
            valor_novo=transferencia.get_organizacao_destino(),
            observacao=f"Transferência realizada. Justificativa: {form.cleaned_data['justificativa']}"
        )
        
        messages.success(
            self.request, 
            f'Viatura {viatura.placa} transferida com sucesso de {transferencia.get_organizacao_origem()} para {transferencia.get_organizacao_destino()}!'
        )
        return redirect('militares:viatura_detail', pk=viatura.pk)
    
    def _processar_organograma_destino(self, viatura, organograma_id):
        """Processa a seleção do organograma e preenche os campos de organização de destino"""
        if organograma_id.startswith('orgao_'):
            orgao_id = int(organograma_id.split('_')[1])
            viatura.orgao = get_object_or_404(Orgao, pk=orgao_id)
            viatura.grande_comando = None
            viatura.unidade = None
            viatura.sub_unidade = None
        elif organograma_id.startswith('gc_'):
            gc_id = int(organograma_id.split('_')[1])
            gc = get_object_or_404(GrandeComando, pk=gc_id)
            viatura.orgao = gc.orgao
            viatura.grande_comando = gc
            viatura.unidade = None
            viatura.sub_unidade = None
        elif organograma_id.startswith('unidade_'):
            unidade_id = int(organograma_id.split('_')[1])
            unidade = get_object_or_404(Unidade, pk=unidade_id)
            viatura.orgao = unidade.grande_comando.orgao
            viatura.grande_comando = unidade.grande_comando
            viatura.unidade = unidade
            viatura.sub_unidade = None
        elif organograma_id.startswith('sub_'):
            sub_id = int(organograma_id.split('_')[1])
            sub = get_object_or_404(SubUnidade, pk=sub_id)
            viatura.orgao = sub.unidade.grande_comando.orgao
            viatura.grande_comando = sub.unidade.grande_comando
            viatura.unidade = sub.unidade
            viatura.sub_unidade = sub

