"""
Views para o módulo de Controle de Manutenção de Viaturas
Gerencia o registro e controle de manutenções
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

from .models import ManutencaoViatura, Viatura, Militar
from .forms import ManutencaoViaturaForm


class ManutencaoListView(LoginRequiredMixin, ListView):
    """Lista todas as manutenções"""
    model = ManutencaoViatura
    template_name = 'militares/manutencao_list.html'
    context_object_name = 'manutencoes'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = ManutencaoViatura.objects.select_related(
            'viatura', 'responsavel', 'criado_por'
        ).order_by('-data_manutencao', '-km_manutencao')
        
        # Filtros
        search = self.request.GET.get('search', '')
        viatura_id = self.request.GET.get('viatura', '')
        tipo_manutencao = self.request.GET.get('tipo_manutencao', '')
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(viatura__placa__icontains=search) |
                Q(viatura__prefixo__icontains=search) |
                Q(fornecedor_oficina__icontains=search) |
                Q(descricao_servico__icontains=search) |
                Q(observacoes__icontains=search)
            )
        
        if viatura_id:
            queryset = queryset.filter(viatura_id=viatura_id)
        
        if tipo_manutencao:
            queryset = queryset.filter(tipo_manutencao=tipo_manutencao)
        
        if data_inicio:
            try:
                from datetime import datetime
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                queryset = queryset.filter(data_manutencao__gte=data_inicio_obj)
            except:
                pass
        
        if data_fim:
            try:
                from datetime import datetime
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
                # Incluir o dia inteiro
                data_fim_obj = data_fim_obj.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(data_manutencao__lte=data_fim_obj)
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
        context['tipo_manutencao'] = self.request.GET.get('tipo_manutencao', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_manutencoes'] = queryset.count()
        context['total_valor'] = queryset.aggregate(Sum('valor_manutencao'))['valor_manutencao__sum'] or 0
        context['media_valor'] = queryset.aggregate(Avg('valor_manutencao'))['valor_manutencao__avg'] or 0
        
        # Lista de viaturas para filtro
        context['viaturas'] = Viatura.objects.filter(ativo=True).order_by('placa')
        
        # Lista de tipos de manutenção
        context['tipos_manutencao'] = ManutencaoViatura.TIPO_MANUTENCAO_CHOICES
        
        # Identificar manutenções próximas (viatura próxima do próximo_km_revisao)
        # Considerar "próximo" quando faltam menos de 1000 km ou quando já passou
        manutencoes_proximas = []
        for manutencao in queryset:
            if manutencao.proximo_km_revisao and manutencao.viatura:
                km_atual = manutencao.viatura.km_atual
                km_proximo = manutencao.proximo_km_revisao
                diferenca_km = km_proximo - km_atual
                
                # Alertar se faltam menos de 1000 km ou se já passou
                if diferenca_km <= 1000:
                    # Verificar se ainda não foi feita uma nova manutenção após o próximo_km_revisao
                    nova_manutencao = ManutencaoViatura.objects.filter(
                        viatura=manutencao.viatura,
                        km_manutencao__gte=km_proximo,
                        ativo=True
                    ).exclude(pk=manutencao.pk).exists()
                    
                    if not nova_manutencao:
                        manutencoes_proximas.append(manutencao.pk)
        
        context['manutencoes_proximas'] = manutencoes_proximas
        
        return context


class ManutencaoCreateView(LoginRequiredMixin, CreateView):
    """Cria uma nova manutenção"""
    model = ManutencaoViatura
    form_class = ManutencaoViaturaForm
    template_name = 'militares/manutencao_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        viatura_id = self.request.GET.get('viatura')
        if viatura_id:
            initial['viatura'] = viatura_id
        
        # Definir responsável automaticamente como o militar logado
        try:
            if hasattr(self.request.user, 'militar'):
                initial['responsavel'] = self.request.user.militar
        except:
            pass
        
        return initial
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(
            self.request, 
            f'Manutenção registrada com sucesso! {form.instance.get_tipo_manutencao_display()} para {form.instance.viatura.placa}.'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('militares:manutencao_detail', kwargs={'pk': self.object.pk})


class ManutencaoDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma manutenção"""
    model = ManutencaoViatura
    template_name = 'militares/manutencao_detail.html'
    context_object_name = 'manutencao'


class ManutencaoUpdateView(LoginRequiredMixin, UpdateView):
    """Edita uma manutenção"""
    model = ManutencaoViatura
    form_class = ManutencaoViaturaForm
    template_name = 'militares/manutencao_form.html'
    success_url = reverse_lazy('militares:manutencao_list')
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Manutenção atualizada com sucesso!'
        )
        return super().form_valid(form)


class ManutencaoDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """Exclui uma manutenção - Apenas para superusuários"""
    model = ManutencaoViatura
    template_name = 'militares/manutencao_confirm_delete.html'
    success_url = reverse_lazy('militares:manutencao_list')
    
    def test_func(self):
        """Apenas superusuários podem excluir"""
        return self.request.user.is_superuser
    
    def delete(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("Apenas superusuários podem excluir manutenções.")
        manutencao = self.get_object()
        placa = manutencao.viatura.placa
        messages.success(request, f'Manutenção da viatura {placa} excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def manutencao_por_viatura(request, viatura_id):
    """Lista manutenções de uma viatura específica"""
    viatura = get_object_or_404(Viatura, pk=viatura_id)
    
    # Filtros de período
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    # Ordenar do último (mais recente) para o primeiro (mais antigo)
    # Filtrar apenas manutenções ativas
    manutencoes = ManutencaoViatura.objects.filter(
        viatura=viatura,
        ativo=True
    ).select_related('responsavel', 'criado_por')
    
    # Aplicar filtros de data
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            # Usar __date para comparar apenas a parte da data
            manutencoes = manutencoes.filter(data_manutencao__date__gte=data_inicio_obj)
        except (ValueError, AttributeError) as e:
            pass
    
    if data_fim:
        try:
            from datetime import datetime, time
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            # Usar __date para comparar apenas a parte da data
            manutencoes = manutencoes.filter(data_manutencao__date__lte=data_fim_obj)
        except (ValueError, AttributeError) as e:
            pass
    
    manutencoes = manutencoes.order_by('-data_manutencao', '-km_manutencao')
    
    # Estatísticas
    total_valor = manutencoes.aggregate(Sum('valor_manutencao'))['valor_manutencao__sum'] or 0
    media_valor = manutencoes.aggregate(Avg('valor_manutencao'))['valor_manutencao__avg'] or 0
    total_manutencoes = manutencoes.count()
    
    paginator = Paginator(manutencoes, 30)
    page = request.GET.get('page')
    manutencoes_page = paginator.get_page(page)
    
    # Obter funções do usuário para assinatura
    from .models import UsuarioFuncaoMilitar
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=request.user,
        ativo=True
    ).select_related('funcao_militar')
    
    context = {
        'viatura': viatura,
        'manutencoes': manutencoes_page,
        'total_valor': total_valor,
        'media_valor': media_valor,
        'total_manutencoes': total_manutencoes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'funcoes_usuario': funcoes_usuario,
    }
    
    return render(request, 'militares/manutencao_por_viatura.html', context)


@login_required
def manutencao_pdf(request, manutencao_id):
    """
    Gera PDF da manutenção de viatura no formato de cupom fiscal
    """
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    
    manutencao = get_object_or_404(ManutencaoViatura, pk=manutencao_id)
    
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
        om_viatura = manutencao.viatura.get_organizacao_instancia()
        if om_viatura and om_viatura != "Não definido":
            textos_cabecalho.append(Paragraph(om_viatura.upper(), style_header))
        
        # Obter endereço da OM (instância mais específica)
        endereco_om = None
        if manutencao.viatura.sub_unidade and manutencao.viatura.sub_unidade.endereco:
            endereco_om = manutencao.viatura.sub_unidade.endereco
        elif manutencao.viatura.unidade and manutencao.viatura.unidade.endereco:
            endereco_om = manutencao.viatura.unidade.endereco
        elif manutencao.viatura.grande_comando and manutencao.viatura.grande_comando.endereco:
            endereco_om = manutencao.viatura.grande_comando.endereco
        elif manutencao.viatura.orgao and manutencao.viatura.orgao.endereco:
            endereco_om = manutencao.viatura.orgao.endereco
        
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
        story.append(Paragraph("COMPROVANTE DE MANUTENÇÃO", style_title))
        story.append(Spacer(1, 6))
        
        # Converter data/hora para timezone local (Brasil)
        import pytz
        from django.utils import timezone as django_timezone
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        if django_timezone.is_aware(manutencao.data_manutencao):
            data_manutencao_local = manutencao.data_manutencao.astimezone(brasilia_tz)
        else:
            data_manutencao_local = brasilia_tz.localize(manutencao.data_manutencao)
        
        data_hora_formatada = data_manutencao_local.strftime("%d/%m/%Y %H:%M")
        
        # Dados da manutenção em formato cupom fiscal (linhas simples)
        largura_disponivel_cupom = cupom_width - (0.5*cm * 2)
        
        # Criar tabela com duas colunas: label e valor
        cupom_data = []
        
        # Linha: Viatura
        viatura_info = f"{manutencao.viatura.placa}"
        if manutencao.viatura.prefixo:
            viatura_info += f" - {manutencao.viatura.prefixo}"
        cupom_data.append([
            Paragraph("<b>Viatura:</b>", style_line),
            Paragraph(viatura_info, style_line_value)
        ])
        
        # Linha: Data/Hora
        cupom_data.append([
            Paragraph("<b>Data/Hora:</b>", style_line),
            Paragraph(data_hora_formatada, style_line_value)
        ])
        
        # Linha: Tipo de Manutenção
        cupom_data.append([
            Paragraph("<b>Tipo Manutenção:</b>", style_line),
            Paragraph(manutencao.get_tipo_manutencao_display(), style_line_value)
        ])
        
        # Linha: KM
        cupom_data.append([
            Paragraph("<b>KM:</b>", style_line),
            Paragraph(f"{manutencao.km_manutencao} km", style_line_value)
        ])
        
        if manutencao.fornecedor_oficina:
            cupom_data.append([
                Paragraph("<b>Oficina:</b>", style_line),
                Paragraph(manutencao.fornecedor_oficina, style_line_value)
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
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=5, spaceBefore=0, color=colors.black))
        
        # Descrição do Serviço (se houver)
        if manutencao.descricao_servico:
            story.append(Spacer(1, 3))
            style_descricao_title = ParagraphStyle('descricao_title', parent=styles['Normal'], alignment=0, fontSize=8, fontName='Helvetica-Bold', spaceAfter=3)
            story.append(Paragraph("<b>DESCRIÇÃO DO SERVIÇO:</b>", style_descricao_title))
            story.append(Paragraph(manutencao.descricao_servico, style_small))
            story.append(Spacer(1, 3))
        
        # Peças Trocadas (se houver)
        if manutencao.pecas_trocadas:
            story.append(Spacer(1, 3))
            style_pecas_title = ParagraphStyle('pecas_title', parent=styles['Normal'], alignment=0, fontSize=8, fontName='Helvetica-Bold', spaceAfter=3)
            story.append(Paragraph("<b>PEÇAS TROCADAS:</b>", style_pecas_title))
            story.append(Paragraph(manutencao.pecas_trocadas, style_small))
            story.append(Spacer(1, 3))
        
        # Valor Total
        story.append(Paragraph(f"<b>TOTAL: R$ {manutencao.valor_manutencao:.2f}</b>", style_total))
        
        # Próximo KM Revisão (se houver e se for tipo Revisão)
        if manutencao.tipo_manutencao == 'REVISAO' and manutencao.proximo_km_revisao:
            style_proximo_km = ParagraphStyle('proximo_km', parent=styles['Normal'], alignment=1, fontSize=8, fontName='Helvetica', spaceAfter=5, leading=9)
            story.append(Spacer(1, 3))
            story.append(Paragraph(f"<b>Próxima Revisão: {manutencao.proximo_km_revisao} km</b>", style_proximo_km))
        
        # Responsável após o valor total em uma linha
        if manutencao.responsavel:
            responsavel_texto = f"{manutencao.responsavel.get_posto_graduacao_display()} {manutencao.responsavel.nome_completo}"
            style_responsavel = ParagraphStyle('responsavel', parent=styles['Normal'], alignment=1, fontSize=8, fontName='Helvetica', spaceAfter=5, leading=9)
            story.append(Paragraph(responsavel_texto, style_responsavel))
        
        story.append(Spacer(1, 5))
        
        if manutencao.observacoes:
            story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=3, spaceBefore=0, color=colors.grey))
            story.append(Paragraph("<b>Observações:</b>", style_line))
            story.append(Paragraph(manutencao.observacoes, style_small))
            story.append(Spacer(1, 5))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=3, spaceBefore=0, color=colors.black))
        story.append(Spacer(1, 3))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        
        # Criar um objeto fake para a manutenção (para o autenticador)
        class ManutencaoFake:
            def __init__(self, manutencao):
                self.id = f"manutencao_{manutencao.pk}"
                self.pk = manutencao.pk
                self.tipo_documento = 'manutencao'
        
        manutencao_fake = ManutencaoFake(manutencao)
        autenticador = gerar_autenticador_veracidade(manutencao_fake, request, tipo_documento='manutencao')
        
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
        response['Content-Disposition'] = f'inline; filename="cupom_fiscal_manutencao_{manutencao.viatura.placa}_{manutencao.pk}.pdf"'
        
        return response
        
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Manutenção</title>
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
                <p><strong>Ocorreu um erro ao gerar o PDF da manutenção.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <p><small>{str(e)}</small></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def historico_manutencao_pdf(request, viatura_id):
    """
    Gera PDF do histórico de manutenções com assinatura eletrônica
    """
    # TODO: Implementar função completa baseada em historico_abastecimento_pdf
    # Por enquanto, retornar mensagem de erro
    from django.http import HttpResponse
    error_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Função em Desenvolvimento</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h2>Função em Desenvolvimento</h2>
        <p>Esta função será implementada em breve.</p>
    </body>
    </html>
    """
    return HttpResponse(error_html, status=501, content_type='text/html')
