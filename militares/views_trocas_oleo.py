"""
Views para o módulo de Controle de Troca de Óleo de Viaturas
Gerencia o registro e controle de trocas de óleo
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

from .models import TrocaOleoViatura, Viatura, Militar
from .forms import TrocaOleoViaturaForm


class TrocaOleoListView(LoginRequiredMixin, ListView):
    """Lista todas as trocas de óleo"""
    model = TrocaOleoViatura
    template_name = 'militares/troca_oleo_list.html'
    context_object_name = 'trocas_oleo'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = TrocaOleoViatura.objects.select_related(
            'viatura', 'responsavel', 'criado_por'
        ).order_by('-data_troca', '-km_troca')
        
        # Filtros
        search = self.request.GET.get('search', '')
        viatura_id = self.request.GET.get('viatura', '')
        tipo_oleo = self.request.GET.get('tipo_oleo', '')
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(viatura__placa__icontains=search) |
                Q(viatura__prefixo__icontains=search) |
                Q(fornecedor_oficina__icontains=search) |
                Q(observacoes__icontains=search)
            )
        
        if viatura_id:
            queryset = queryset.filter(viatura_id=viatura_id)
        
        if tipo_oleo:
            queryset = queryset.filter(tipo_oleo=tipo_oleo)
        
        if data_inicio:
            try:
                from datetime import datetime
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                queryset = queryset.filter(data_troca__gte=data_inicio_obj)
            except:
                pass
        
        if data_fim:
            try:
                from datetime import datetime
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
                # Incluir o dia inteiro
                data_fim_obj = data_fim_obj.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(data_troca__lte=data_fim_obj)
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
        context['tipo_oleo'] = self.request.GET.get('tipo_oleo', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_trocas'] = queryset.count()
        context['total_litros'] = queryset.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum'] or 0
        context['total_valor'] = queryset.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        context['media_valor'] = queryset.aggregate(Avg('valor_total'))['valor_total__avg'] or 0
        
        # Lista de viaturas para filtro
        context['viaturas'] = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Lista de tipos de óleo
        context['tipos_oleo'] = TrocaOleoViatura.TIPO_OLEO_CHOICES
        
        # Identificar trocas de óleo próximas (viatura próxima do proximo_km_troca)
        # Considerar "próximo" quando faltam menos de 1000 km ou quando já passou
        trocas_proximas = []
        for troca in queryset:
            if troca.proximo_km_troca and troca.viatura:
                km_atual = troca.viatura.km_atual
                km_proximo = troca.proximo_km_troca
                diferenca_km = km_proximo - km_atual
                
                # Alertar se faltam menos de 1000 km ou se já passou
                if diferenca_km <= 1000:
                    # Verificar se ainda não foi feita uma nova troca após o proximo_km_troca
                    nova_troca = TrocaOleoViatura.objects.filter(
                        viatura=troca.viatura,
                        km_troca__gte=km_proximo,
                        ativo=True
                    ).exclude(pk=troca.pk).exists()
                    
                    if not nova_troca:
                        trocas_proximas.append(troca.pk)
        
        context['trocas_proximas'] = trocas_proximas
        
        return context


class TrocaOleoCreateView(LoginRequiredMixin, CreateView):
    """Cria nova troca de óleo"""
    model = TrocaOleoViatura
    form_class = TrocaOleoViaturaForm
    template_name = 'militares/troca_oleo_form.html'
    success_url = reverse_lazy('militares:troca_oleo_list')
    
    def get_initial(self):
        """Define valores iniciais"""
        initial = super().get_initial()
        viatura_id = self.request.GET.get('viatura', '')
        if viatura_id:
            try:
                viatura = Viatura.objects.get(pk=viatura_id, ativo=True)
                initial['viatura'] = viatura
                initial['km_troca'] = viatura.km_atual
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
            f'Troca de óleo registrada com sucesso! {form.instance.quantidade_litros}L de {form.instance.get_tipo_oleo_display()} para {form.instance.viatura.placa}.'
        )
        return super().form_valid(form)


class TrocaOleoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma troca de óleo"""
    model = TrocaOleoViatura
    template_name = 'militares/troca_oleo_detail.html'
    context_object_name = 'troca_oleo'


class TrocaOleoUpdateView(LoginRequiredMixin, UpdateView):
    """Edita uma troca de óleo"""
    model = TrocaOleoViatura
    form_class = TrocaOleoViaturaForm
    template_name = 'militares/troca_oleo_form.html'
    success_url = reverse_lazy('militares:troca_oleo_list')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Troca de óleo atualizada com sucesso!'
        )
        return super().form_valid(form)


class TrocaOleoDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """Exclui uma troca de óleo - Apenas para superusuários"""
    model = TrocaOleoViatura
    template_name = 'militares/troca_oleo_confirm_delete.html'
    success_url = reverse_lazy('militares:troca_oleo_list')
    
    def test_func(self):
        """Apenas superusuários podem excluir"""
        return self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas superusuários podem excluir trocas de óleo.")
        troca_oleo = self.get_object()
        placa = troca_oleo.viatura.placa
        messages.success(request, f'Troca de óleo da viatura {placa} excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def troca_oleo_por_viatura(request, viatura_id):
    """Lista trocas de óleo de uma viatura específica"""
    viatura = get_object_or_404(Viatura, pk=viatura_id)
    
    # Filtros de período
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Ordenar do último (mais recente) para o primeiro (mais antigo)
    trocas_oleo = TrocaOleoViatura.objects.filter(
        viatura=viatura
    ).select_related('responsavel', 'criado_por')
    
    # Aplicar filtros de data
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            trocas_oleo = trocas_oleo.filter(data_troca__date__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            from datetime import datetime, time
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            data_fim_completa = datetime.combine(data_fim_obj, time.max)
            trocas_oleo = trocas_oleo.filter(data_troca__lte=data_fim_completa)
        except:
            pass
    
    trocas_oleo = trocas_oleo.order_by('-data_troca', '-km_troca')
    
    # Estatísticas
    total_litros = trocas_oleo.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum'] or 0
    total_valor = trocas_oleo.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    media_valor = trocas_oleo.aggregate(Avg('valor_total'))['valor_total__avg'] or 0
    
    paginator = Paginator(trocas_oleo, 30)
    page = request.GET.get('page')
    trocas_oleo_page = paginator.get_page(page)
    
    context = {
        'viatura': viatura,
        'trocas_oleo': trocas_oleo_page,
        'total_litros': total_litros,
        'total_valor': total_valor,
        'media_valor': media_valor,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    
    return render(request, 'militares/troca_oleo_por_viatura.html', context)


@login_required
def troca_oleo_pdf(request, troca_oleo_id):
    """
    Gera PDF da troca de óleo de viatura no formato de cupom fiscal
    """
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    
    troca_oleo = get_object_or_404(TrocaOleoViatura, pk=troca_oleo_id)
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        # Tamanho de cupom fiscal (80mm de largura - papel térmico)
        from reportlab.lib.pagesizes import letter
        # 80mm = 3.15 polegadas (inches), altura padrão 11 polegadas
        cupom_width = 80 * 2.83465  # 80mm em pontos (1mm = 2.83465 pontos)
        cupom_height = 11 * 72  # 11 polegadas em pontos
        
        # Criar tamanho customizado para cupom fiscal
        cupom_size = (cupom_width, cupom_height)
        
        # Margens menores para formato cupom fiscal
        doc = SimpleDocTemplate(buffer, pagesize=cupom_size, rightMargin=0.5*cm, leftMargin=0.5*cm, topMargin=0.5*cm, bottomMargin=0.5*cm)
        story = []
        
        # Estilos para cupom fiscal (compacto, tamanho menor)
        styles = getSampleStyleSheet()
        style_header = ParagraphStyle('header', parent=styles['Normal'], alignment=1, fontSize=7, fontName='Helvetica-Bold', spaceAfter=1, leading=8)
        style_header_small = ParagraphStyle('header_small', parent=styles['Normal'], alignment=1, fontSize=6, fontName='Helvetica', spaceAfter=1, leading=7)
        style_title = ParagraphStyle('title', parent=styles['Normal'], alignment=1, fontSize=9, fontName='Helvetica-Bold', spaceAfter=5)
        style_line = ParagraphStyle('line', parent=styles['Normal'], fontSize=8, alignment=0, spaceAfter=3, leftIndent=0)
        style_line_value = ParagraphStyle('line_value', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=2, spaceAfter=3)
        style_total = ParagraphStyle('total', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=1, spaceAfter=5, textColor=colors.HexColor('#000000'))
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=7, alignment=0, spaceAfter=3)
        style_center_small = ParagraphStyle('center_small', parent=styles['Normal'], fontSize=7, alignment=1, spaceAfter=2)
        
        # Logo/Brasão (menor para cupom)
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        logo_img = None
        if os.path.exists(logo_path):
            logo_img = Image(logo_path, width=1.5*cm, height=1.5*cm)
        
        # Cabeçalho com logo ao lado - formato cupom fiscal
        largura_disponivel = cupom_width - (0.5*cm * 2)  # Largura do cupom menos margens
        largura_logo = 1.5*cm if logo_img else 0  # Logo menor para cupom
        largura_texto = largura_disponivel - largura_logo - 0.3*cm
        
        # Textos do cabeçalho (fonte menor para caber em uma linha)
        textos_cabecalho = [
            Paragraph("GOVERNO DO ESTADO DO PIAUÍ", style_header),
            Paragraph("CORPO DE BOMBEIROS MILITAR", style_header),
        ]
        
        # Adicionar OM da viatura (apenas a instância mais específica, sem hierarquia) em maiúsculo
        om_viatura = troca_oleo.viatura.get_organizacao_instancia()
        if om_viatura and om_viatura != "Não definido":
            textos_cabecalho.append(Paragraph(om_viatura.upper(), style_header))
        
        # Obter endereço da OM (instância mais específica)
        endereco_om = None
        if troca_oleo.viatura.sub_unidade and troca_oleo.viatura.sub_unidade.endereco:
            endereco_om = troca_oleo.viatura.sub_unidade.endereco
        elif troca_oleo.viatura.unidade and troca_oleo.viatura.unidade.endereco:
            endereco_om = troca_oleo.viatura.unidade.endereco
        elif troca_oleo.viatura.grande_comando and troca_oleo.viatura.grande_comando.endereco:
            endereco_om = troca_oleo.viatura.grande_comando.endereco
        elif troca_oleo.viatura.orgao and troca_oleo.viatura.orgao.endereco:
            endereco_om = troca_oleo.viatura.orgao.endereco
        
        # Adicionar apenas o endereço (sem telefone e site fixos)
        if endereco_om:
            textos_cabecalho.append(Paragraph(endereco_om, style_header_small))
        
        # Logo centralizada acima do cabeçalho
        if logo_img:
            # Criar tabela para centralizar a logo
            logo_table = Table([[logo_img]], colWidths=[largura_disponivel])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(logo_table)
        
        # Adicionar textos do cabeçalho centralizados (já formatados com estilos menores)
        for texto in textos_cabecalho:
            story.append(texto)
        
        story.append(Spacer(1, 5))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Título
        story.append(Paragraph("COMPROVANTE DE TROCA DE ÓLEO", style_title))
        story.append(Spacer(1, 6))
        
        # Converter data/hora para timezone local (Brasil)
        import pytz
        from django.utils import timezone as django_timezone
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if django_timezone.is_aware(troca_oleo.data_troca):
            data_troca_local = troca_oleo.data_troca.astimezone(brasilia_tz)
        else:
            data_troca_local = brasilia_tz.localize(troca_oleo.data_troca)
        
        data_hora_formatada = data_troca_local.strftime("%d/%m/%Y %H:%M")
        
        # Dados da troca de óleo em formato cupom fiscal (linhas simples)
        largura_disponivel_cupom = cupom_width - (0.5*cm * 2)
        
        # Criar tabela com duas colunas: label e valor
        cupom_data = []
        
        # Linha: Viatura
        viatura_info = f"{troca_oleo.viatura.placa}"
        if troca_oleo.viatura.prefixo:
            viatura_info += f" - {troca_oleo.viatura.prefixo}"
        cupom_data.append([
            Paragraph("<b>Viatura:</b>", style_line),
            Paragraph(viatura_info, style_line_value)
        ])
        
        # Linha: Data/Hora
        cupom_data.append([
            Paragraph("<b>Data/Hora:</b>", style_line),
            Paragraph(data_hora_formatada, style_line_value)
        ])
        
        # Linha: Tipo de Óleo
        cupom_data.append([
            Paragraph("<b>Tipo de Óleo:</b>", style_line),
            Paragraph(troca_oleo.get_tipo_oleo_display(), style_line_value)
        ])
        
        # Nome do Óleo (se houver)
        if troca_oleo.nome_oleo:
            cupom_data.append([
                Paragraph("<b>Nome do Óleo:</b>", style_line),
                Paragraph(troca_oleo.nome_oleo, style_line_value)
            ])
        
        # Linha: Quantidade
        cupom_data.append([
            Paragraph("<b>Quantidade:</b>", style_line),
            Paragraph(f"{troca_oleo.quantidade_litros:.2f} L", style_line_value)
        ])
        
        # Linha: Valor Unitário (se houver)
        if troca_oleo.valor_litro:
            cupom_data.append([
                Paragraph("<b>Valor Unitário:</b>", style_line),
                Paragraph(f"R$ {troca_oleo.valor_litro:.2f}", style_line_value)
            ])
        
        # Linha: KM
        cupom_data.append([
            Paragraph("<b>KM:</b>", style_line),
            Paragraph(f"{troca_oleo.km_troca} km", style_line_value)
        ])
        
        if troca_oleo.fornecedor_oficina:
            cupom_data.append([
                Paragraph("<b>Oficina:</b>", style_line),
                Paragraph(troca_oleo.fornecedor_oficina, style_line_value)
            ])
        
        # Criar tabela (ajustada para largura do cupom)
        largura_label = largura_disponivel_cupom * 0.5
        largura_valor = largura_disponivel_cupom * 0.5
        cupom_table = Table(cupom_data, colWidths=[largura_label, largura_valor])
        cupom_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(cupom_table)
        story.append(Spacer(1, 3))
        
        # Valor Total do Óleo
        style_oleo_total = ParagraphStyle('oleo_total', parent=styles['Normal'], alignment=2, fontSize=9, fontName='Helvetica-Bold', spaceAfter=5, textColor=colors.HexColor('#000000'))
        story.append(Paragraph(f"<b>Total Óleo: R$ {troca_oleo.valor_total:.2f}</b>", style_oleo_total))
        story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Seção de Filtros e Aditivos (se houver)
        tem_filtros_aditivos = False
        if troca_oleo.trocou_filtro_oleo or troca_oleo.trocou_filtro_combustivel or troca_oleo.trocou_filtro_ar or troca_oleo.adicionou_aditivo_arrefecimento:
            tem_filtros_aditivos = True
            story.append(Spacer(1, 3))
            style_filtros_title = ParagraphStyle('filtros_title', parent=styles['Normal'], alignment=0, fontSize=8, fontName='Helvetica-Bold', spaceAfter=3, textColor=colors.HexColor('#0066cc'))
            story.append(Paragraph("<b>FILTROS E ADITIVOS:</b>", style_filtros_title))
            
            filtros_data = []
            if troca_oleo.trocou_filtro_oleo and troca_oleo.valor_filtro_oleo:
                filtros_data.append([
                    Paragraph("<b>Filtro de Óleo:</b>", style_line),
                    Paragraph(f"R$ {troca_oleo.valor_filtro_oleo:.2f}", style_line_value)
                ])
            if troca_oleo.trocou_filtro_combustivel and troca_oleo.valor_filtro_combustivel:
                filtros_data.append([
                    Paragraph("<b>Filtro Combustível:</b>", style_line),
                    Paragraph(f"R$ {troca_oleo.valor_filtro_combustivel:.2f}", style_line_value)
                ])
            if troca_oleo.trocou_filtro_ar and troca_oleo.valor_filtro_ar:
                filtros_data.append([
                    Paragraph("<b>Filtro de Ar:</b>", style_line),
                    Paragraph(f"R$ {troca_oleo.valor_filtro_ar:.2f}", style_line_value)
                ])
            if troca_oleo.adicionou_aditivo_arrefecimento and troca_oleo.valor_aditivo_arrefecimento:
                filtros_data.append([
                    Paragraph("<b>Aditivo Arrefecimento:</b>", style_line),
                    Paragraph(f"R$ {troca_oleo.valor_aditivo_arrefecimento:.2f}", style_line_value)
                ])
            
            if filtros_data:
                filtros_table = Table(filtros_data, colWidths=[largura_label, largura_valor])
                filtros_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(filtros_table)
                story.append(Spacer(1, 3))
                story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Outras Peças (se houver)
        if troca_oleo.outras_pecas:
            story.append(Spacer(1, 3))
            style_outras_pecas_title = ParagraphStyle('outras_pecas_title', parent=styles['Normal'], alignment=0, fontSize=8, fontName='Helvetica-Bold', spaceAfter=3)
            story.append(Paragraph("<b>OUTRAS PEÇAS:</b>", style_outras_pecas_title))
            story.append(Paragraph(troca_oleo.outras_pecas, style_small))
            story.append(Spacer(1, 3))
            story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Valor Total da Nota (se houver, senão valor do óleo)
        valor_total_final = troca_oleo.valor_total_nota if troca_oleo.valor_total_nota else troca_oleo.valor_total
        story.append(Paragraph(f"<b>TOTAL DA NOTA: R$ {valor_total_final:.2f}</b>", style_total))
        
        # Próximo KM Troca (se houver)
        if troca_oleo.proximo_km_troca:
            style_proximo_km = ParagraphStyle('proximo_km', parent=styles['Normal'], alignment=1, fontSize=8, fontName='Helvetica', spaceAfter=5, leading=9)
            story.append(Spacer(1, 3))
            story.append(Paragraph(f"<b>Próxima Troca: {troca_oleo.proximo_km_troca} km</b>", style_proximo_km))
        
        # Responsável após o valor total em uma linha
        if troca_oleo.responsavel:
            responsavel_texto = f"{troca_oleo.responsavel.get_posto_graduacao_display()} {troca_oleo.responsavel.nome_completo}"
            style_responsavel = ParagraphStyle('responsavel', parent=styles['Normal'], alignment=1, fontSize=8, fontName='Helvetica', spaceAfter=5, leading=9)
            story.append(Paragraph(responsavel_texto, style_responsavel))
        
        story.append(Spacer(1, 5))
        
        if troca_oleo.observacoes:
            story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=3, spaceBefore=0, color=colors.grey))
            story.append(Paragraph("<b>Observações:</b>", style_line))
            story.append(Paragraph(troca_oleo.observacoes, style_small))
            story.append(Spacer(1, 5))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=3, spaceBefore=0, color=colors.black))
        story.append(Spacer(1, 3))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        
        # Criar um objeto fake para a troca de óleo (para o autenticador)
        class TrocaOleoFake:
            def __init__(self, troca_oleo):
                self.id = f"troca_oleo_{troca_oleo.pk}"
                self.pk = troca_oleo.pk
                self.tipo_documento = 'troca_oleo'
        
        troca_oleo_fake = TrocaOleoFake(troca_oleo)
        autenticador = gerar_autenticador_veracidade(troca_oleo_fake, request, tipo_documento='troca_oleo')
        
        # Redimensionar QR code para cupom (menor)
        from reportlab.platypus import Image as RLImage
        import qrcode
        from io import BytesIO
        
        # Gerar QR code menor para cupom
        url_autenticacao_base = autenticador.get('url_autenticacao', autenticador.get('url', ''))
        
        qr_cupom = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,  # Menor para cupom
            border=2,
        )
        qr_cupom.add_data(url_autenticacao_base)
        qr_cupom.make(fit=True)
        
        qr_img_pil_cupom = qr_cupom.make_image(fill_color="black", back_color="white")
        qr_buffer_cupom = BytesIO()
        qr_img_pil_cupom.save(qr_buffer_cupom, format='PNG')
        qr_buffer_cupom.seek(0)
        qr_img_cupom = RLImage(qr_buffer_cupom, width=1.8*cm, height=1.8*cm)
        
        # Tabela do rodapé: QR + Texto de autenticação (compacto para cupom)
        largura_disponivel_qr = cupom_width - (0.5*cm * 2) - 0.04*cm
        largura_qr_cupom = 1.8*cm  # QR menor para cupom
        largura_texto_qr = largura_disponivel_qr - largura_qr_cupom - 0.2*cm
        
        rodape_data = [
            [qr_img_cupom, Paragraph(autenticador['texto_autenticacao'], style_center_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[largura_qr_cupom, largura_texto_qr])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="cupom_fiscal_troca_oleo_{troca_oleo.viatura.placa}_{troca_oleo.pk}.pdf"'
        
        return response
        
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Troca de Óleo</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF da troca de óleo.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <p><small>{str(e)}</small></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')

