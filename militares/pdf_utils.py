"""
Utilitários para geração de PDF a partir de HTML
"""

def gerar_pdf_from_html(html_content):
    """Gera PDF a partir do conteúdo HTML do almanaque"""
    try:
        # Por enquanto, usar o método direto sem importação circular
        return gerar_pdf_almanaque_direct_old('GERAL')
    except Exception as e:
        print(f"Erro ao gerar PDF do HTML: {e}")
        # Fallback para o método direto
        return gerar_pdf_almanaque_direct_old('GERAL')

def gerar_pdf_almanaque_direct(almanaque, request=None):
    """Função para gerar PDF de um almanaque específico"""
    import datetime
    import os
    from django.utils import timezone
    
    # Definir ordem hierárquica dos postos
    ordem_postos_oficiais = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ordem_postos_pracas = ['ST', '1S', '2S', '3S', 'CAB', 'SD']
    
    # Buscar todos os militares ativos (excluindo NVRR)
    from .models import Militar
    militares_ativos = Militar.objects.filter(classificacao='ATIVO').exclude(quadro='NVRR')
    
    # Separar oficiais e praças
    oficiais = [m for m in militares_ativos if m.is_oficial()]
    pracas = [m for m in militares_ativos if not m.is_oficial()]
    
    # Filtrar por tipo do almanaque
    tipo = almanaque.tipo
    if tipo == 'OFICIAIS':
        militares_filtrados = oficiais
        ordem_postos = ordem_postos_oficiais
        titulo = "ALMANAQUE DOS OFICIAIS DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
    elif tipo == 'PRACAS':
        militares_filtrados = pracas
        ordem_postos = ordem_postos_pracas
        titulo = "ALMANAQUE DAS PRAÇAS DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
    else:  # GERAL
        militares_filtrados = list(militares_ativos)
        ordem_postos = ordem_postos_oficiais + ordem_postos_pracas
        titulo = "ALMANAQUE GERAL DOS MILITARES DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
    
    # Organizar por hierarquia
    dados_organizados = {}
    for posto in ordem_postos:
        militares_posto = [m for m in militares_filtrados if m.posto_graduacao == posto]
        if militares_posto:
            militares_posto.sort(key=lambda x: (x.numeracao_antiguidade or 999999, x.data_promocao_atual or datetime.date.max))
            dados_organizados[posto] = militares_posto
    
    # Função para criptografar CPF
    def criptografar_cpf(cpf):
        if not cpf:
            return '-'
        cpf_limpo = cpf.replace('.', '').replace('-', '')
        if len(cpf_limpo) != 11:
            return cpf
        return f"{cpf_limpo[:3]}.***.***-{cpf_limpo[-2:]}"
    
    # Gerar PDF usando reportlab
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    
    # Estilos customizados
    styles = getSampleStyleSheet()
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=11)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=13, spaceAfter=10, underlineProportion=0.1)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=11, spaceAfter=8)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    
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
    story.append(Spacer(1, 10))
    
    # Título centralizado e sublinhado
    titulo_formatado = f'<u>{titulo}</u>'
    story.append(Paragraph(titulo_formatado, style_title))
    story.append(Spacer(1, 16))
    
    # Texto introdutório
    story.append(Paragraph("O DIRETOR DE GESTÃO DE PESSOAS DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ, no uso de suas atribuições que lhe confere o Art. 18, da lei 5.949, de 17 de dezembro de 2009, alterado pelo Art. 1° da lei 7.772, de 04 de abril de 2022;", style_just))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>RESOLVE:</b>", style_bold))
    story.append(Spacer(1, 12))
    
    # Artigo 1º com destaque conforme tipo e data de geração
    tipo_almanaque = almanaque.tipo
    data_geracao = almanaque.data_geracao
    
    if tipo_almanaque == 'OFICIAIS':
        tipo_militar = '<b><u>OFICIAIS</u></b>'
        # Se gerado entre 18/07 e 23/12: usar 18/07/2025
        # Se gerado entre 23/12 e 18/07: usar 23/12/2025
        if (data_geracao.month == 7 and data_geracao.day >= 18) or (data_geracao.month > 7 and data_geracao.month < 12) or (data_geracao.month == 12 and data_geracao.day < 23):
            data_promocao = "18/07/2025"
        else:
            data_promocao = "23/12/2025"
    elif tipo_almanaque == 'PRACAS':
        tipo_militar = '<b><u>PRAÇAS</u></b>'
        # Se gerado entre 18/07 e 25/12: usar 18/07/2025
        # Se gerado entre 25/12 e 18/07: usar 25/12/2025
        if (data_geracao.month == 7 and data_geracao.day >= 18) or (data_geracao.month > 7 and data_geracao.month < 12) or (data_geracao.month == 12 and data_geracao.day < 25):
            data_promocao = "18/07/2025"
        else:
            data_promocao = "25/12/2025"
    else:
        tipo_militar = "Militares"
        data_promocao = "18/07/2025"
    
    story.append(Paragraph(f"<b>Art. 1º</b> Fica fixada a antiguidade dos {tipo_militar} do Corpo de Bombeiros Militar do Estado do Piauí, após as promoções ocorridas em {data_promocao}, conforme segue:", style_just))
    story.append(Spacer(1, 16))
    
    # Gerar tabela com dados
    for posto, militares in dados_organizados.items():
        if militares:
            # Cabeçalho da seção
            story.append(Paragraph(f"<b>{militares[0].get_posto_graduacao_display()}</b>", style_subtitle))
            story.append(Spacer(1, 8))
            
            # Dados dos militares
            data = [['CPF', 'Nome Completo', 'Antiguidade', 'Data Promoção']]
            for militar in militares:
                data.append([
                    criptografar_cpf(militar.cpf),
                    militar.nome_completo,
                    str(militar.numeracao_antiguidade or '-'),
                    militar.data_promocao_atual.strftime('%d/%m/%Y') if militar.data_promocao_atual else '-'
                ])
            
            # Colunas expandidas para evitar quebra de texto
            table = Table(data, colWidths=[3*cm, 7*cm, 2*cm, 2.5*cm])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Nome alinhado à esquerda
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
    
    # Função para converter data para extenso
    def data_por_extenso(data):
        meses = [
            'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]
        return f"{data.day} de {meses[data.month - 1]} de {data.year}"
    
    # Cidade, UF e Data por extenso
    story.append(Spacer(1, 20))
    data_atual = timezone.now().date()
    story.append(Paragraph(f"Teresina - PI, {data_por_extenso(data_atual)}.", style_center))
    story.append(Spacer(1, 30))
    
    # Buscar assinaturas do almanaque
    assinaturas = almanaque.get_assinaturas_ordenadas()
    
    # Adicionar assinaturas se existirem (mesmo padrão dos quadros de fixação)
    if assinaturas.exists():
        # Seção de Assinaturas Físicas (sem título)
        story.append(Spacer(1, 13))

        # Buscar todas as assinaturas válidas do almanaque (da mais recente para a mais antiga)
        assinaturas_ordenadas = assinaturas.order_by('-data_assinatura')
        
        for assinatura in assinaturas_ordenadas:
            # Nome e posto
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{militar.nome_completo} - {posto}"
            else:
                nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            
            # Função
            funcao = assinatura.cargo_funcao or "Função não registrada"
            
            # Tipo de assinatura
            tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
            
            # Exibir no formato físico: Nome - Posto BM (negrito), Função (normal), Tipo (negrito menor)
            story.append(Spacer(1, 13))
            story.append(Paragraph(f"<b>{nome_completo}</b>", style_center))
            story.append(Paragraph(f"{funcao}", style_center))
            story.append(Paragraph(f"<b>{tipo}</b>", style_center))
            story.append(Spacer(1, 13))

        # Seção de Assinaturas Eletrônicas (sem título)
        story.append(Spacer(1, 13))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=13, spaceBefore=13, color=colors.lightgrey))
        story.append(Spacer(1, 13))
        
        # Buscar todas as assinaturas para exibir na seção eletrônica
        assinaturas_eletronicas = assinaturas.filter(
            assinado_por__isnull=False
        ).order_by('-data_assinatura')
        
        for i, assinatura in enumerate(assinaturas_eletronicas):
            # Nome e posto - seguir o mesmo padrão dos quadros de acesso
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_completo = f"{posto} {militar.nome_completo}"
            else:
                nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            
            # Função
            funcao = assinatura.cargo_funcao or "Função não registrada"
            
            # Tipo de assinatura
            tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
            
            # Data da assinatura
            from .utils import formatar_data_assinatura
            data_formatada, hora_formatada = formatar_data_assinatura(assinatura.data_assinatura)
            data_assinatura = f"{data_formatada} {hora_formatada}"
            
            # Texto da assinatura eletrônica no padrão solicitado
            texto_assinatura = (
                f"Documento assinado eletronicamente por {nome_completo}, em {data_assinatura}, "
                f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
            )
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            from .utils import obter_caminho_assinatura_eletronica
            logo_assinatura_path = obter_caminho_assinatura_eletronica()
            assinatura_data = [
                [Image(logo_assinatura_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
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
            story.append(Spacer(1, 10))  # Espaçamento entre assinaturas
        
        # Se não houver assinaturas, mostrar mensagem
        if not assinaturas_ordenadas.exists() and not assinaturas_eletronicas.exists():
            story.append(Paragraph("Nenhuma assinatura registrada", style_center))
    
    # Rodapé com QR Code para conferência de veracidade
    story.append(Spacer(1, 13))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(almanaque, request, tipo_documento='almanaque')
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)
    
    doc.build(story)
    return buffer.getvalue()

def gerar_pdf_almanaque_direct_old(tipo):
    """Função auxiliar para gerar PDF sem importação circular (mantida para compatibilidade)"""
    import datetime
    import os
    from django.utils import timezone
    
    # Definir ordem hierárquica dos postos
    ordem_postos_oficiais = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ordem_postos_pracas = ['ST', '1S', '2S', '3S', 'CAB', 'SD']
    
    # Buscar todos os militares ativos (excluindo NVRR)
    from .models import Militar
    militares_ativos = Militar.objects.filter(classificacao='ATIVO').exclude(quadro='NVRR')
    
    # Separar oficiais e praças
    oficiais = [m for m in militares_ativos if m.is_oficial()]
    pracas = [m for m in militares_ativos if not m.is_oficial()]
    
    # Filtrar por tipo
    if tipo == 'OFICIAIS':
        militares_filtrados = oficiais
        ordem_postos = ordem_postos_oficiais
        titulo = "ALMANAQUE DOS OFICIAIS DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
    elif tipo == 'PRACAS':
        militares_filtrados = pracas
        ordem_postos = ordem_postos_pracas
        titulo = "ALMANAQUE DAS PRAÇAS DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
    else:  # GERAL
        militares_filtrados = list(militares_ativos)
        ordem_postos = ordem_postos_oficiais + ordem_postos_pracas
        titulo = "ALMANAQUE GERAL DOS MILITARES DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
    
    # Organizar por hierarquia
    dados_organizados = {}
    for posto in ordem_postos:
        militares_posto = [m for m in militares_filtrados if m.posto_graduacao == posto]
        if militares_posto:
            militares_posto.sort(key=lambda x: (x.numeracao_antiguidade or 999999, x.data_promocao_atual or datetime.date.max))
            dados_organizados[posto] = militares_posto
    
    # Função para criptografar CPF
    def criptografar_cpf(cpf):
        if not cpf:
            return '-'
        cpf_limpo = cpf.replace('.', '').replace('-', '')
        if len(cpf_limpo) != 11:
            return cpf
        return f"{cpf_limpo[:3]}.***.***-{cpf_limpo[-2:]}"
    
    # Gerar PDF usando reportlab
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    
    # Estilos customizados
    styles = getSampleStyleSheet()
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=11)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=13, spaceAfter=10, underlineProportion=0.1)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=11, spaceAfter=8)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    
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
    story.append(Spacer(1, 10))
    
    # Título centralizado e sublinhado
    titulo_formatado = f'<u>{titulo}</u>'
    story.append(Paragraph(titulo_formatado, style_title))
    story.append(Spacer(1, 16))
    
    # Texto introdutório
    story.append(Paragraph("O DIRETOR DE GESTÃO DE PESSOAS DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ, no uso de suas atribuições que lhe confere o Art. 18, da lei 5.949, de 17 de dezembro de 2009, alterado pelo Art. 1° da lei 7.772, de 04 de abril de 2022;", style_just))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>RESOLVE:</b>", style_bold))
    story.append(Spacer(1, 12))
    
    # Artigo 1º com destaque conforme tipo e data atual
    data_atual = timezone.now()
    
    if tipo == 'OFICIAIS':
        tipo_militar = '<b><u>OFICIAIS</u></b>'
        # Se gerado entre 18/07 e 23/12: usar 18/07/2025
        # Se gerado entre 23/12 e 18/07: usar 23/12/2025
        if (data_atual.month == 7 and data_atual.day >= 18) or (data_atual.month > 7 and data_atual.month < 12) or (data_atual.month == 12 and data_atual.day < 23):
            data_promocao = "18/07/2025"
        else:
            data_promocao = "23/12/2025"
    elif tipo == 'PRACAS':
        tipo_militar = '<b><u>PRAÇAS</u></b>'
        # Se gerado entre 18/07 e 25/12: usar 18/07/2025
        # Se gerado entre 25/12 e 18/07: usar 25/12/2025
        if (data_atual.month == 7 and data_atual.day >= 18) or (data_atual.month > 7 and data_atual.month < 12) or (data_atual.month == 12 and data_atual.day < 25):
            data_promocao = "18/07/2025"
        else:
            data_promocao = "25/12/2025"
    else:
        tipo_militar = "Militares"
        data_promocao = "18/07/2025"
    
    story.append(Paragraph(f"<b>Art. 1º</b> Fica fixada a antiguidade dos {tipo_militar} do Corpo de Bombeiros Militar do Estado do Piauí, após as promoções ocorridas em {data_promocao}, conforme segue:", style_just))
    story.append(Spacer(1, 16))
    
    # Gerar tabela com dados
    for posto, militares in dados_organizados.items():
        if militares:
            # Cabeçalho da seção
            story.append(Paragraph(f"<b>{militares[0].get_posto_graduacao_display()}</b>", style_subtitle))
            story.append(Spacer(1, 8))
            
            # Dados dos militares
            data = [['CPF', 'Nome Completo', 'Antiguidade', 'Data Promoção']]
            for militar in militares:
                data.append([
                    criptografar_cpf(militar.cpf),
                    militar.nome_completo,
                    str(militar.numeracao_antiguidade or '-'),
                    militar.data_promocao_atual.strftime('%d/%m/%Y') if militar.data_promocao_atual else '-'
                ])
            
            # Colunas expandidas para evitar quebra de texto
            table = Table(data, colWidths=[3*cm, 7*cm, 2*cm, 2.5*cm])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Nome alinhado à esquerda
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
    
    # Função para converter data para extenso
    def data_por_extenso(data):
        meses = [
            'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]
        return f"{data.day} de {meses[data.month - 1]} de {data.year}"
    
    # Cidade, UF e Data por extenso
    story.append(Spacer(1, 20))
    data_atual = timezone.now().date()
    story.append(Paragraph(f"Teresina - PI, {data_por_extenso(data_atual)}.", style_center))
    story.append(Spacer(1, 30))
    
    doc.build(story)
    return buffer.getvalue() 
