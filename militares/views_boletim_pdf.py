from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from militares.models import Publicacao, AssinaturaNota
import os
import locale
from datetime import datetime
from io import BytesIO
import qrcode
import re
from html import unescape
import hashlib

# Imports do ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable, PageBreak, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def gerar_hash_documento(boletim_id, conteudo, timestamp):
    """Gera hash SHA-256 do documento para assinatura eletrônica"""
    dados = f"{boletim_id}-{conteudo}-{timestamp}"
    return hashlib.sha256(dados.encode('utf-8')).hexdigest()


def gerar_assinatura_digital(boletim_id, funcao, observacoes, timestamp):
    """Gera assinatura digital baseada no conteúdo do documento"""
    dados = f"{boletim_id}-{funcao}-{observacoes}-{timestamp}"
    return hashlib.sha256(dados.encode('utf-8')).hexdigest()


def gerar_codigo_verificador(boletim_id):
    """Gera código verificador único para o boletim"""
    return f"{boletim_id:08d}"


def gerar_codigo_crc(boletim_id):
    """Gera código CRC para verificação de integridade"""
    return f"{hash(str(boletim_id)) % 0xFFFFFFF:07X}"


def add_page_number(canvas, doc, boletim=None, data_edicao=None, data_geracao_pdf=None, user=None):
    """Adiciona numeração de páginas no rodapé com informações da edição"""
    canvas.saveState()
    
    # Configurar fonte
    try:
        canvas.setFont("Arial", 9)
    except:
        canvas.setFont("Helvetica", 9)
    
    # Posição do número da página (centro inferior)
    # Começar numeração após a capa (página 1)
    page_num = canvas.getPageNumber()
    if page_num == 1 and boletim:  # Página da capa - mostrar editores no rodapé
        # Buscar editores para a capa
        from militares.models import AssinaturaNota
        # Usar o ID do boletim em vez do número formatado
        assinaturas = AssinaturaNota.objects.filter(nota_id=boletim.id).order_by('-data_assinatura')
        
        editores_texto = []
        for assinatura in assinaturas[:3]:  # Limitar a 3 editores
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                if "BM" not in posto:
                    posto = f"{posto} BM"
                funcao = assinatura.funcao_assinatura or assinatura.get_tipo_assinatura_display() or "Função não registrada"
                editores_texto.append(f"{posto} {militar.nome_completo} - {funcao}")
            else:
                funcao = assinatura.funcao_assinatura or assinatura.get_tipo_assinatura_display() or "Função não registrada"
                editores_texto.append(f"{assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username} - {funcao}")
        
        # Desenhar editores no rodapé da capa (formato original em colunas)
        if editores_texto:
            try:
                canvas.setFont("Arial", 7)
            except:
                canvas.setFont("Helvetica", 7)
            
            # Desenhar linha separadora
            canvas.setStrokeColor(colors.grey)
            canvas.setLineWidth(0.5)
            canvas.line(1*cm, 2*cm, A4[0] - 1*cm, 2*cm)
            
            # Desenhar informações organizadas em 3 linhas
            canvas.setFillColor(colors.black)
            y_pos = 1.5*cm
            
            # Preparar dados dos editores organizados em 3 colunas
            # Coluna 1: Editor Geral, Coluna 2: Editor Adjunto, Coluna 3: Editor Chefe
            editores_colunas = ["", "", ""]  # [Geral, Adjunto, Chefe]
            funcoes_colunas = ["", "", ""]
            
            # Debug: verificar quantas assinaturas foram encontradas
            print(f"DEBUG: Encontradas {len(assinaturas)} assinaturas")
            
            # Distribuir as assinaturas sequencialmente nas 3 colunas
            for i, assinatura in enumerate(assinaturas[:3]):  # Limitar a 3 editores
                funcao = assinatura.funcao_assinatura or assinatura.get_tipo_assinatura_display() or "Função não registrada"
                
                # Usar posição sequencial (0, 1, 2) para garantir que todas apareçam
                coluna = i
                
                # Preencher dados do editor
                if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                    militar = assinatura.assinado_por.militar
                    posto = militar.get_posto_graduacao_display()
                    if "BM" not in posto:
                        posto = f"{posto} BM"
                    editores_colunas[coluna] = f"{posto} {militar.nome_completo}"
                else:
                    editores_colunas[coluna] = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                
                funcoes_colunas[coluna] = funcao
                
                print(f"DEBUG: Editor {i+1}: {editores_colunas[coluna]} - {funcao}")
            
            # Calcular largura das colunas
            col_width = (A4[0] - 2*cm) / 3  # 3 colunas com margens de 1cm
            
            # Linha 1: Nomes dos editores em 3 colunas (centralizados)
            for i, editor in enumerate(editores_colunas):
                if editor:  # Só desenhar se houver editor
                    x_pos = 1*cm + (i * col_width) + (col_width / 2)  # Centralizar na coluna
                    # Calcular largura do texto para centralizar
                    try:
                        text_width = canvas.stringWidth(editor, "Arial", 8)
                    except:
                        text_width = canvas.stringWidth(editor, "Helvetica", 8)
                    x_pos -= text_width / 2  # Centralizar o texto
                    canvas.drawString(x_pos, y_pos, editor)
            
            y_pos -= 0.4*cm
            
            # Linha 2: Funções dos editores em 3 colunas (centralizados)
            for i, funcao in enumerate(funcoes_colunas):
                if funcao:  # Só desenhar se houver função
                    x_pos = 1*cm + (i * col_width) + (col_width / 2)  # Centralizar na coluna
                    # Calcular largura do texto para centralizar
                    try:
                        text_width = canvas.stringWidth(funcao, "Arial", 8)
                    except:
                        text_width = canvas.stringWidth(funcao, "Helvetica", 8)
                    x_pos -= text_width / 2  # Centralizar o texto
                    canvas.drawString(x_pos, y_pos, funcao)
            
            y_pos -= 0.4*cm
            
            # Linha 3: Dados do boletim e PDF
            # Data de publicação
            if boletim.data_publicacao:
                data_pub = boletim.data_publicacao.strftime('%d-%m-%Y %H:%M:%S')
            elif boletim.data_criacao:
                data_pub = boletim.data_criacao.strftime('%d-%m-%Y %H:%M:%S')
            else:
                data_pub = "Data não informada"
            
            # Total de assinaturas
            total_assinaturas = assinaturas.count()
            total_notas = total_assinaturas
            
            # Status
            status = "Publicado" if boletim.data_publicacao else "Rascunho"
            
            # Data de geração - garantir que sempre tenha uma data
            from datetime import datetime
            try:
                data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
                # Verificar se a data foi gerada corretamente
                if not data_geracao or data_geracao.strip() == "":
                    data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            except:
                # Fallback se houver erro
                data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Obter CPF do usuário
            cpf_usuario = ""
            if user:
                if hasattr(user, 'militar') and user.militar and hasattr(user.militar, 'cpf'):
                    cpf_usuario = user.militar.cpf
                    if cpf_usuario and cpf_usuario != "CPF não informado":
                        cpf_digits = ''.join(filter(str.isdigit, cpf_usuario))
                        if len(cpf_digits) == 11:
                            cpf_usuario = f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
                    else:
                        cpf_usuario = "CPF não informado"
                else:
                    cpf_usuario = "CPF não informado"
            else:
                cpf_usuario = "CPF não informado"
            
            # Dados do boletim e PDF (centralizados)
            dados_boletim = f"Publicado em: {data_pub} | Total de assinaturas: {total_assinaturas} | Total de notas: {total_notas} | Status: {status} | Gerado em: {data_geracao} | CPF: {cpf_usuario}"
            
            # Centralizar os dados
            try:
                canvas.setFont("Arial", 8)
                text_width = canvas.stringWidth(dados_boletim, "Arial", 8)
            except:
                canvas.setFont("Helvetica", 8)
                text_width = canvas.stringWidth(dados_boletim, "Helvetica", 8)
            
            x_pos = (A4[0] - text_width) / 2  # Centralizar na página
            
            # Garantir que a cor seja preta
            canvas.setFillColor(colors.black)
            canvas.drawString(x_pos, y_pos, dados_boletim)
    if page_num > 1:  # Só numerar a partir da segunda página (após a capa)
        print(f"DEBUG - Processando página {page_num} (não é capa)")
        
        # Usar a mesma lógica da capa para todas as páginas
        # Obter CPF do usuário
        cpf_usuario = ""
        if user:
            if hasattr(user, 'militar') and user.militar and hasattr(user.militar, 'cpf'):
                cpf_usuario = user.militar.cpf
                if cpf_usuario and cpf_usuario != "CPF não informado":
                    cpf_digits = ''.join(filter(str.isdigit, cpf_usuario))
                    if len(cpf_digits) == 11:
                        cpf_usuario = f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"
                else:
                    cpf_usuario = "CPF não informado"
            else:
                cpf_usuario = "CPF não informado"
        else:
            cpf_usuario = "CPF não informado"
        
        # Data de geração - mesma lógica da capa
        from datetime import datetime
        try:
            data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
            if not data_geracao or data_geracao.strip() == "":
                data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        except:
            data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Montar texto com todas as informações (igual à capa)
        dados_boletim = f"Página {page_num - 1} | Edição Nº {boletim.numero if boletim and boletim.numero else 'N/A'} | CPF: {cpf_usuario} | Gerado em: {data_geracao}"
        
        # Desenhar linha separadora
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(0.5)
        canvas.line(1*cm, 2*cm, A4[0] - 1*cm, 2*cm)
        
        # Centralizar os dados (mesma lógica da capa)
        try:
            canvas.setFont("Arial", 8)
            text_width = canvas.stringWidth(dados_boletim, "Arial", 8)
        except:
            canvas.setFont("Helvetica", 8)
            text_width = canvas.stringWidth(dados_boletim, "Helvetica", 8)
        
        x_pos = (A4[0] - text_width) / 2  # Centralizar na página
        
        # Garantir que a cor seja preta
        canvas.setFillColor(colors.black)
        canvas.drawString(x_pos, 1.5*cm, dados_boletim)
    
    canvas.restoreState()


def add_watermark_cpf(canvas, user):
    """Adiciona marca d'água com CPF do usuário que imprimiu o boletim"""
    canvas.saveState()
    
    # Obter dimensões da página
    page_width = canvas._pagesize[0]
    page_height = canvas._pagesize[1]
    
    # Configurar fonte e cor para marca d'água
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.lightgrey)
    
    # Obter CPF do usuário
    cpf_usuario = ""
    if hasattr(user, 'militar') and user.militar and hasattr(user.militar, 'cpf'):
        cpf_usuario = user.militar.cpf
    elif hasattr(user, 'cpf'):
        cpf_usuario = user.cpf
    else:
        cpf_usuario = "CPF não informado"
    
    # Texto da marca d'água
    watermark_text = f"Impresso por: {cpf_usuario}"
    
    # Posicionar no centro da página com rotação
    canvas.translate(page_width/2, page_height/2)
    canvas.rotate(45)  # Rotacionar 45 graus
    
    # Desenhar texto com transparência
    canvas.setFillColor(colors.lightgrey)
    canvas.drawString(-100, 0, watermark_text)
    
    # Adicionar mais texto para cobrir melhor a página
    canvas.drawString(-200, 50, watermark_text)
    canvas.drawString(100, -50, watermark_text)
    canvas.drawString(-300, -100, watermark_text)
    canvas.drawString(200, 100, watermark_text)
    
    canvas.restoreState()


@login_required
def boletim_gerar_pdf(request, pk):
    """Gera PDF do boletim ostensivo no modelo institucional"""
    
    # Configurar locale para português brasileiro
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass  # Usar formato padrão se não conseguir configurar

    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_OSTENSIVO')
    except Publicacao.DoesNotExist:
        messages.error(request, f'Boletim ostensivo com ID {pk} não encontrado.')
        return redirect('militares:boletins_ostensivos_list')

    buffer = BytesIO()
    
    # Obter assinaturas
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=0.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Configurar fonte para suportar caracteres especiais
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        font_name = 'Arial'
    except:
        font_name = 'Helvetica'

    # Estilos customizados seguindo ABNT
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, spaceAfter=3, spaceBefore=3, fontName=font_name)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName=font_name, fontSize=12, spaceAfter=3, spaceBefore=3)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=14, spaceAfter=6, spaceBefore=6, fontName=font_name)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=12, spaceAfter=4, spaceBefore=4, fontName=font_name)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=10, spaceAfter=2, spaceBefore=2, fontName=font_name)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=12, spaceAfter=3, spaceBefore=3, leading=12, fontName=font_name)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=11, spaceAfter=4, spaceBefore=4, leading=11, fontName=font_name)
    style_paragraph = ParagraphStyle('paragraph', parent=styles['Normal'], fontSize=12, spaceAfter=3, spaceBefore=3, leading=12, alignment=TA_JUSTIFY, fontName=font_name)

    story = []

    # ===== CAPA DO BOLETIM =====
    # Cores institucionais
    vermelho_cbm = colors.HexColor('#DC2626')  # Vermelho institucional
    dourado_cbm = colors.HexColor('#D97706')   # Dourado institucional
    preto = colors.black
    
    # Margens laterais douradas (início)
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    story.append(Spacer(1, 20))
    
    # Logo CBMEPI no topo (maior na capa)
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=4*cm, height=4*cm, hAlign='CENTER'))
        story.append(Spacer(1, 20))

    # Título principal do Boletim (grande na capa)
    story.append(Paragraph(f"BOLETIM DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ", ParagraphStyle('titulo_principal', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=10, spaceBefore=10)))
    story.append(Paragraph(f"EDIÇÃO Nº {boletim.numero}", ParagraphStyle('edicao', parent=styles['Normal'], alignment=TA_CENTER, fontSize=20, fontName=font_name, spaceAfter=20, spaceBefore=0)))
    
    # Faixa diagonal com cores institucionais
    story.append(HRFlowable(width="100%", thickness=8, spaceAfter=0, spaceBefore=0, color=vermelho_cbm))
    story.append(HRFlowable(width="100%", thickness=4, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    story.append(Spacer(1, 30))
    
    # Textura sutil com linhas geométricas (simulando fogo estilizado)
    for i in range(3):
        # Linhas diagonais alternadas em tons de dourado
        cor_textura = colors.HexColor('#F59E0B') if i % 2 == 0 else colors.HexColor('#D97706')
        story.append(HRFlowable(width="80%", thickness=0.5, spaceAfter=2, spaceBefore=2, color=cor_textura, hAlign='CENTER'))
    
    story.append(Spacer(1, 20))
    
    # Data de criação do boletim (mesma data da coluna "Dia" na tabela)
    # Usar data_publicacao se disponível, senão usar data_criacao como fallback
    data_para_usar = boletim.data_publicacao if boletim.data_publicacao else boletim.data_criacao
    
    if data_para_usar:
        # Formatação manual para garantir mês correto
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        # Converter para timezone local para obter a data correta
        from django.utils import timezone
        from datetime import date
        
        from datetime import datetime as dt
        if isinstance(data_para_usar, dt):
            # Converter datetime UTC para timezone local e extrair a data
            data_local = timezone.localtime(data_para_usar)
            data_obj = data_local.date()
        else:
            # Já é uma data
            data_obj = data_para_usar
        
        dia = data_obj.day
        mes = meses[data_obj.month]
        ano = data_obj.year
        data_criacao = f"{dia:02d} de {mes} de {ano}"
    else:
        data_criacao = "Data não informada"
    story.append(Paragraph(f"Teresina - PI, {data_criacao}", ParagraphStyle('data_capa', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=25, spaceBefore=10)))
    
    # Espaço final na capa - 6 espaços adicionais
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    
    # Caixa de texto de acesso restrito (apenas para boletim reservado)
    if boletim.tipo == 'BOLETIM_RESERVADO':
        story.append(Spacer(1, 1*cm))
        
        # Criar parágrafos para o texto de acesso restrito
        story.append(Paragraph("<b><font color='#DC2626'>ACESSO RESTRITO</font></b>", ParagraphStyle('acesso_restrito_titulo', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=5, spaceBefore=5)))
        story.append(Paragraph("<font color='#DC2626'>Art 325 do Decreto-Lei nº 2.848/1940 - Código Penal Brasileiro</font>", ParagraphStyle('acesso_restrito_texto', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=3, spaceBefore=3)))
        story.append(Paragraph("<font color='#DC2626'>Art. 22 da LEI Nº 12.527, DE 18 DE NOVEMBRO DE 2011 - Regula o acesso a informações</font>", ParagraphStyle('acesso_restrito_texto', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=5, spaceBefore=3)))
        story.append(Spacer(1, 1*cm))
        story.append(Spacer(1, 1*cm))
        story.append(Spacer(1, 1*cm))
    
    # Margens laterais douradas (fechamento)
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    
    # Editores e informações do boletim agora aparecem no rodapé da capa
    
    
    # Quebra de página para o conteúdo
    story.append(PageBreak())

    # ===== CONTEÚDO DO BOLETIM =====
    # Logo CBMEPI no topo (menor no conteúdo)
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2*cm, height=2*cm, hAlign='CENTER'))
        story.append(Spacer(1, 2))

    # Cabeçalho Oficial (menor no conteúdo)
    story.append(Paragraph("ESTADO DO PIAUÍ", ParagraphStyle('estado', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("CORPO DE BOMBEIROS MILITAR DO PIAUÍ", ParagraphStyle('cbmepi', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("COMANDO GERAL", ParagraphStyle('comando', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("AJUDÂNCIA GERAL", ParagraphStyle('ajudancia', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490", ParagraphStyle('endereco', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br", ParagraphStyle('contato', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=3, spaceBefore=1)))
    
    
    # Linha separadora
    story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black, spaceAfter=6, spaceBefore=6))

    # Data de criação (mesma data da coluna "Dia" na tabela)
    story.append(Paragraph(f"Teresina - PI, {data_criacao}", style_center))
    story.append(Spacer(1, 12))

    # Título do Boletim na primeira linha
    story.append(Paragraph(f"BOLETIM DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ Nº {boletim.numero}", style_title))
    story.append(Spacer(1, 12))

    # Remover o tópico duplicado - será processado no loop abaixo

    # Buscar notas incluídas no boletim
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim=boletim.numero
    ).order_by('data_publicacao')

    # Organizar notas por tópicos/partes
    topicos_organizados = {
        '1ª PARTE - SERVIÇOS DIÁRIOS': [],
        '2ª PARTE - INSTRUÇÃO': [],
        '3ª PARTE - ASSUNTOS GERAIS': [],
        '3ª PARTE - ADMINISTRATIVOS': [],
        '4ª PARTE - JUSTIÇA': [],
        '4ª PARTE - DISCIPLINA': [],
    }
    
    # Agrupar notas por tópico
    for nota in notas_incluidas:
        if nota.topicos and nota.topicos.strip() in topicos_organizados:
            topicos_organizados[nota.topicos.strip()].append(nota)
        else:
            # Se o tópico não estiver mapeado, adicionar à primeira parte
            topicos_organizados['1ª PARTE - SERVIÇOS DIÁRIOS'].append(nota)
    
    # Ordenar notas dentro de cada tópico por número
    for topico, notas in topicos_organizados.items():
        topicos_organizados[topico] = sorted(notas, key=lambda x: x.numero or '')

    # Processar cada tópico na ordem correta
    ordem_topicos = [
        '1ª PARTE - SERVIÇOS DIÁRIOS',
        '2ª PARTE - INSTRUÇÃO',
        '3ª PARTE - ASSUNTOS GERAIS',
        '3ª PARTE - ADMINISTRATIVOS',
        '4ª PARTE - JUSTIÇA',
        '4ª PARTE - DISCIPLINA',
    ]
    
    for topico in ordem_topicos:
        notas_do_topico = topicos_organizados[topico]
        
        # Não adicionar quebra de página - partes sequenciais
        
        # Título do tópico
        story.append(Paragraph(topico, ParagraphStyle('topico', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=6, spaceBefore=6)))
        story.append(Spacer(1, 6))
        
        # Verificar se tem notas no tópico
        if notas_do_topico:
            # Processar notas do tópico
            for nota in notas_do_topico:
                story.append(Spacer(1, 8))
                
                # Número da Nota
                story.append(Paragraph(f"NOTA N° {nota.numero}", ParagraphStyle('numero', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=3, spaceBefore=0)))
                
                # Título da Nota
                story.append(Paragraph(nota.titulo.upper(), ParagraphStyle('titulo', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=12, spaceBefore=0)))
                
                # Conteúdo da nota (usando a mesma lógica do PDF individual)
                if nota.conteudo:
                    # Importar a função de processamento das notas
                    from .views_assinaturas_notas import processar_formato_html_modal
                    
                    conteudo_html = nota.conteudo
                    conteudo_processado = processar_formato_html_modal(conteudo_html)
                    
                    # Dividir o conteúdo em parágrafos individuais para preservar alinhamento
                    paragrafos = conteudo_processado.split('</para>')
                    
                    for paragrafo in paragrafos:
                        if paragrafo.strip():
                            # Adicionar tag de fechamento se foi removida pelo split
                            if not paragrafo.strip().endswith('>'):
                                paragrafo = paragrafo.strip() + '</para>'
                            
                            # Determinar alinhamento baseado na tag
                            if 'align="center"' in paragrafo:
                                align = TA_CENTER
                            elif 'align="right"' in paragrafo:
                                align = 2  # TA_RIGHT
                            elif 'align="justify"' in paragrafo:
                                align = 4  # TA_JUSTIFY
                            else:
                                align = 0  # TA_LEFT
                            
                            # Remover tags para processamento
                            import re
                            paragrafo_limpo = re.sub(r'<para[^>]*>', '', paragrafo)
                            paragrafo_limpo = re.sub(r'</para>', '', paragrafo_limpo)
                            
                            if paragrafo_limpo.strip():
                                story.append(Paragraph(paragrafo_limpo.strip(), ParagraphStyle('conteudo', parent=styles['Normal'], fontSize=11, fontName=font_name, alignment=align, spaceAfter=6, spaceBefore=0, leading=14)))
                else:
                    story.append(Paragraph("Conteúdo não disponível", ParagraphStyle('conteudo', parent=styles['Normal'], fontSize=11, fontName=font_name, spaceAfter=6, spaceBefore=0, textColor=colors.grey)))
                
                # Adicionar assinaturas da nota (igual ao PDF individual)
                assinaturas_nota = nota.assinaturas.all().order_by('-data_assinatura')
                if assinaturas_nota.exists():
                    story.append(Spacer(1, 12))
                    
                    # Separar assinaturas físicas e eletrônicas
                    assinaturas_fisicas = assinaturas_nota.filter(tipo_midia='FISICA')
                    assinaturas_eletronicas = assinaturas_nota.filter(tipo_midia='ELETRONICA')
                    
                    # Assinaturas físicas primeiro
                    for assinatura in assinaturas_fisicas:
                        # Nome e posto
                        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                            militar = assinatura.assinado_por.militar
                            posto = militar.get_posto_graduacao_display()
                            if "BM" not in posto:
                                posto = f"{posto} BM"
                            nome_completo = f"{militar.nome_completo} - {posto}"
                        else:
                            nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                        
                        # Função
                        funcao = assinatura.funcao_assinatura or "Função não registrada"
                        
                        # Tipo de assinatura
                        tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
                        
                        story.append(Paragraph(f"<b>{nome_completo}</b>", ParagraphStyle('assinante', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=2, spaceBefore=2)))
                        story.append(Paragraph(f"{funcao}", ParagraphStyle('funcao', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=2, spaceBefore=2)))
                        story.append(Paragraph(f"<b>{tipo}</b>", ParagraphStyle('tipo_assinatura', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, fontName=font_name, spaceAfter=6, spaceBefore=2)))
                    
                    # Assinaturas eletrônicas depois
                    for assinatura in assinaturas_eletronicas:
                        data_formatada = assinatura.data_assinatura.strftime("%d/%m/%Y") if assinatura.data_assinatura else "Data não informada"
                        hora_formatada = assinatura.data_assinatura.strftime("%H:%M") if assinatura.data_assinatura else "Hora não informada"
                        
                        # Nome e posto
                        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                            militar = assinatura.assinado_por.militar
                            posto = militar.get_posto_graduacao_display()
                            if "BM" not in posto:
                                posto = f"{posto} BM"
                            nome_completo = f"{militar.nome_completo} - {posto}"
                        else:
                            nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                        
                        # Função
                        funcao = assinatura.funcao_assinatura or "Função não registrada"
                        
                        # Texto da assinatura eletrônica
                        texto_assinatura = f"Documento assinado eletronicamente por {nome_completo} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025."
                        
                        # Adicionar logo da assinatura eletrônica
                        from .utils import obter_caminho_assinatura_eletronica
                        logo_assinatura_path = obter_caminho_assinatura_eletronica()
                        
                        # Tabela das assinaturas: Logo + Texto de assinatura
                        assinatura_data = [
                            [Image(logo_assinatura_path, width=1.5*cm, height=1*cm), Paragraph(texto_assinatura, ParagraphStyle('assinatura_texto', parent=styles['Normal'], fontSize=8, spaceAfter=1, spaceBefore=1, leading=6, alignment=TA_JUSTIFY, fontName=font_name))]
                        ]
                        
                        assinatura_table = Table(assinatura_data, colWidths=[2*cm, 14*cm])
                        assinatura_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 1),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                            ('TOPPADDING', (0, 0), (-1, -1), 1),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        
                        story.append(assinatura_table)
                        story.append(Spacer(1, 4))
                
                # Verificar se há anexos na nota
                anexos_nota = nota.anexos.all() if hasattr(nota, 'anexos') else []
                if anexos_nota.exists():
                    story.append(Spacer(1, 6))
                    story.append(Paragraph("Anexos:", ParagraphStyle('anexos_titulo', parent=styles['Normal'], fontSize=9, fontName=font_name, spaceAfter=3, spaceBefore=0, textColor=colors.black)))
                    
                    for anexo in anexos_nota:
                        nome_anexo = anexo.arquivo.name.split('/')[-1] if anexo.arquivo else "Anexo sem nome"
                        # Criar URL completa para o anexo
                        url_anexo = f"/media/{anexo.arquivo.name}" if anexo.arquivo else "#"
                        
                        # Criar link clicável usando tag <a> do ReportLab
                        link_text = f'• <a href="{url_anexo}" color="blue">{nome_anexo}</a>'
                        story.append(Paragraph(link_text, ParagraphStyle('anexo_item', parent=styles['Normal'], fontSize=8, fontName=font_name, spaceAfter=2, spaceBefore=0, textColor=colors.blue, leftIndent=20)))
                
                # Transcrição da nota com origem e data (no final, discreta)
                origem_formatada = nota.origem_publicacao if nota.origem_publicacao and nota.origem_publicacao != '-' else "Origem não informada"
                
                # Formatação manual da data para garantir mês correto
                if nota.data_criacao:
                    from django.utils import timezone
                    from datetime import date
                    
                    # Converter para timezone local se for datetime
                    if isinstance(nota.data_criacao, date):
                        data_obj = nota.data_criacao
                    else:
                        data_local = timezone.localtime(nota.data_criacao)
                        data_obj = data_local.date()
                    
                    meses = {
                        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                    }
                    
                    dia = data_obj.day
                    mes = meses[data_obj.month]
                    ano = data_obj.year
                    data_formatada = f"{dia} de {mes} de {ano}"
                else:
                    data_formatada = "Data não informada"
                
                transcricao = f"(Transcrição da nota {nota.titulo.upper()} de Nº {nota.numero} com origem {origem_formatada}, datada de {data_formatada}.)"
                story.append(Paragraph(transcricao, ParagraphStyle('transcricao', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=8, fontName=font_name, spaceAfter=8, spaceBefore=4, textColor=colors.black)))
                
                # Espaçamento entre notas
                story.append(Spacer(1, 12))
        else:
            # Se não tem notas, mostrar "Sem Alterações"
            story.append(Paragraph("Sem Alterações", ParagraphStyle('sem_alteracoes', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, fontName=font_name, spaceAfter=12, spaceBefore=6, textColor=colors.grey)))

    # ===== ASSINATURAS DO BOLETIM =====
    if assinaturas.exists():
        story.append(Spacer(1, 20))
        
        # Data do boletim
        data_para_usar = boletim.data_publicacao if boletim.data_publicacao else boletim.data_criacao
        if data_para_usar:
            meses = {
                1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
            }
            
            from django.utils import timezone
            from datetime import datetime as dt
            if isinstance(data_para_usar, dt):
                data_local = timezone.localtime(data_para_usar)
                data_obj = data_local.date()
            else:
                data_obj = data_para_usar
            
            dia = data_obj.day
            mes = meses[data_obj.month]
            ano = data_obj.year
            data_extenso = f"Teresina - PI, {dia} de {mes} de {ano}"
        else:
            data_extenso = "Teresina - PI, data não informada"
        
        story.append(Paragraph(data_extenso, style_center))
        
        # Seção de Assinaturas Físicas (sem título)
        story.append(Spacer(1, 8))

        # Buscar todas as assinaturas válidas do boletim (da mais recente para a mais antiga)
        assinaturas_boletim = assinaturas.filter(assinado_por__isnull=False).order_by('-data_assinatura')
        
        for assinatura in assinaturas_boletim:
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
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            # Tipo de assinatura
            tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
            
            # Exibir no formato físico: Nome - Posto BM (negrito), Função (normal), Tipo (negrito menor)
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<b>{nome_completo}</b>", style_center))
            story.append(Paragraph(f"{funcao}", style_center))
            story.append(Paragraph(f"<b>{tipo}</b>", style_center))
            story.append(Spacer(1, 8))

        # Seção de Assinaturas Eletrônicas (sem título)
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=8, spaceBefore=8, color=colors.lightgrey))
        story.append(Spacer(1, 8))
        
        # Buscar todas as assinaturas para exibir na seção eletrônica
        assinaturas_eletronicas = assinaturas.filter(
            assinado_por__isnull=False
        ).order_by('-data_assinatura')
        
        for i, assinatura in enumerate(assinaturas_eletronicas):
            # Informações de assinatura eletrônica - seguir exatamente o padrão dos outros PDFs
            nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
            
            # Se o usuário tem militar associado, incluir posto com BM
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_assinante = f"{posto} {militar.nome_completo}"
            
            from .utils import formatar_data_assinatura
            data_formatada, hora_formatada = formatar_data_assinatura(assinatura.data_assinatura)
            
            # Função
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_assinante} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(obter_caminho_assinatura_eletronica(), width=2.5*cm, height=1.8*cm), Paragraph(texto_assinatura, style_small)]
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

    # Rodapé com QR Code para conferência de veracidade (padrão dos outros PDFs)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(boletim, request, tipo_documento='boletim')
    
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

    # Preparar informações para o rodapé
    print(f"DEBUG - boletim.data_criacao: {boletim.data_criacao}")
    print(f"DEBUG - boletim.data_publicacao: {boletim.data_publicacao}")
    
    if boletim.data_criacao:
        data_edicao = boletim.data_criacao.strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como: {data_edicao}")
    elif boletim.data_publicacao:
        data_edicao = boletim.data_publicacao.strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como: {data_edicao}")
    else:
        # Usar data atual como fallback
        from datetime import datetime
        data_edicao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como fallback: {data_edicao}")
    
    # Data e hora atual de geração do PDF
    from datetime import datetime
    data_geracao_pdf = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    
    # Funções lambda para capturar informações do boletim
    def add_page_number_first(canvas, doc):
        add_page_number(canvas, doc, boletim, data_edicao, data_geracao_pdf, request.user)
    
    def add_page_number_later(canvas, doc):
        add_page_number(canvas, doc, boletim, data_edicao, data_geracao_pdf, request.user)
    
    # Construir PDF com numeração de páginas
    doc.build(story, onFirstPage=add_page_number_first, onLaterPages=add_page_number_later)
    buffer.seek(0)

    # Resposta HTTP - abrir na nova guia para visualização
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="boletim_{boletim.numero}_2025.pdf"'
    
    return response


@login_required
def boletim_especial_gerar_pdf(request, pk):
    """Gera PDF do boletim especial no modelo institucional"""
    
    # Configurar locale para português brasileiro
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass  # Usar formato padrão se não conseguir configurar

    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_ESPECIAL')
    except Publicacao.DoesNotExist:
        messages.error(request, f'Boletim especial com ID {pk} não encontrado.')
        return redirect('militares:boletins_especiais_list')

    buffer = BytesIO()
    
    # Obter assinaturas
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=0.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Configurar fonte para suportar caracteres especiais
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        font_name = 'Arial'
    except:
        font_name = 'Helvetica'

    # Estilos customizados seguindo ABNT
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, spaceAfter=3, spaceBefore=3, fontName=font_name)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName=font_name, fontSize=12, spaceAfter=3, spaceBefore=3)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=14, spaceAfter=6, spaceBefore=6, fontName=font_name)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=12, spaceAfter=4, spaceBefore=4, fontName=font_name)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=10, spaceAfter=2, spaceBefore=2, fontName=font_name)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=12, spaceAfter=3, spaceBefore=3, leading=12, fontName=font_name)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=11, spaceAfter=4, spaceBefore=4, leading=11, fontName=font_name)
    style_paragraph = ParagraphStyle('paragraph', parent=styles['Normal'], fontSize=12, spaceAfter=3, spaceBefore=3, leading=12, alignment=TA_JUSTIFY, fontName=font_name)

    story = []

    # ===== CAPA DO BOLETIM =====
    # Cores institucionais
    vermelho_cbm = colors.HexColor('#DC2626')  # Vermelho institucional
    dourado_cbm = colors.HexColor('#D97706')   # Dourado institucional
    preto = colors.black
    
    # Margens laterais douradas (início)
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    story.append(Spacer(1, 20))
    
    # Logo CBMEPI no topo (maior na capa)
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=4*cm, height=4*cm, hAlign='CENTER'))
        story.append(Spacer(1, 20))

    # Título principal do Boletim (grande na capa)
    story.append(Paragraph(f"BOLETIM ESPECIAL DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ", ParagraphStyle('titulo_principal', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=10, spaceBefore=10)))
    story.append(Paragraph(f"EDIÇÃO Nº {boletim.numero}", ParagraphStyle('edicao', parent=styles['Normal'], alignment=TA_CENTER, fontSize=20, fontName=font_name, spaceAfter=20, spaceBefore=0)))
    
    # Faixa diagonal com cores institucionais
    story.append(HRFlowable(width="100%", thickness=8, spaceAfter=0, spaceBefore=0, color=vermelho_cbm))
    story.append(HRFlowable(width="100%", thickness=4, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    story.append(Spacer(1, 30))
    
    # Textura sutil com linhas geométricas (simulando fogo estilizado)
    for i in range(3):
        # Linhas diagonais alternadas em tons de dourado
        cor_textura = colors.HexColor('#F59E0B') if i % 2 == 0 else colors.HexColor('#D97706')
        story.append(HRFlowable(width="80%", thickness=0.5, spaceAfter=2, spaceBefore=2, color=cor_textura, hAlign='CENTER'))
    
    story.append(Spacer(1, 20))
    
    # Data de criação do boletim (mesma data da coluna "Dia" na tabela)
    # Usar data_publicacao se disponível, senão usar data_criacao como fallback
    data_para_usar = boletim.data_publicacao if boletim.data_publicacao else boletim.data_criacao
    
    if data_para_usar:
        # Formatação manual para garantir mês correto
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        # Converter para timezone local para obter a data correta
        from django.utils import timezone
        from datetime import date
        
        from datetime import datetime as dt
        if isinstance(data_para_usar, dt):
            # Converter datetime UTC para timezone local e extrair a data
            data_local = timezone.localtime(data_para_usar)
            data_obj = data_local.date()
        else:
            # Já é uma data
            data_obj = data_para_usar
        
        dia = data_obj.day
        mes = meses[data_obj.month]
        ano = data_obj.year
        data_criacao = f"{dia:02d} de {mes} de {ano}"
    else:
        data_criacao = "Data não informada"
    story.append(Paragraph(f"Teresina - PI, {data_criacao}", ParagraphStyle('data_capa', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=25, spaceBefore=10)))
    
    # Espaço final na capa - 6 espaços adicionais
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    
    # Margens laterais douradas (fechamento)
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    
    # Quebra de página para o conteúdo
    story.append(PageBreak())

    # ===== CONTEÚDO DO BOLETIM =====
    # Logo CBMEPI no topo (menor no conteúdo)
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2*cm, height=2*cm, hAlign='CENTER'))
        story.append(Spacer(1, 2))

    # Cabeçalho Oficial (menor no conteúdo)
    story.append(Paragraph("ESTADO DO PIAUÍ", ParagraphStyle('estado', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("CORPO DE BOMBEIROS MILITAR DO PIAUÍ", ParagraphStyle('cbmepi', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("COMANDO GERAL", ParagraphStyle('comando', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("AJUDÂNCIA GERAL", ParagraphStyle('ajudancia', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490", ParagraphStyle('endereco', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br", ParagraphStyle('contato', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=3, spaceBefore=1)))
    
    
    # Linha separadora
    story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black, spaceAfter=6, spaceBefore=6))

    # Data de criação (mesma data da coluna "Dia" na tabela)
    story.append(Paragraph(f"Teresina - PI, {data_criacao}", style_center))
    story.append(Spacer(1, 12))

    # Título do Boletim na primeira linha
    story.append(Paragraph(f"BOLETIM ESPECIAL DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ Nº {boletim.numero}", style_title))
    story.append(Spacer(1, 12))

    # Buscar notas incluídas no boletim especial
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim_especial=boletim.numero
    ).order_by('data_publicacao')

    # Organizar notas por tópicos/partes
    topicos_organizados = {
        '1ª PARTE - SERVIÇOS DIÁRIOS': [],
        '2ª PARTE - INSTRUÇÃO': [],
        '3ª PARTE - ASSUNTOS GERAIS': [],
        '3ª PARTE - ADMINISTRATIVOS': [],
        '4ª PARTE - JUSTIÇA': [],
        '4ª PARTE - DISCIPLINA': [],
    }
    
    # Agrupar notas por tópico
    for nota in notas_incluidas:
        if nota.topicos and nota.topicos.strip() in topicos_organizados:
            topicos_organizados[nota.topicos.strip()].append(nota)
        else:
            # Se o tópico não estiver mapeado, adicionar à primeira parte
            topicos_organizados['1ª PARTE - SERVIÇOS DIÁRIOS'].append(nota)
    
    # Ordenar notas dentro de cada tópico por número
    for topico, notas in topicos_organizados.items():
        topicos_organizados[topico] = sorted(notas, key=lambda x: x.numero or '')

    # Processar cada tópico na ordem correta
    ordem_topicos = [
        '1ª PARTE - SERVIÇOS DIÁRIOS',
        '2ª PARTE - INSTRUÇÃO',
        '3ª PARTE - ASSUNTOS GERAIS',
        '3ª PARTE - ADMINISTRATIVOS',
        '4ª PARTE - JUSTIÇA',
        '4ª PARTE - DISCIPLINA',
    ]
    
    for topico in ordem_topicos:
        notas_do_topico = topicos_organizados[topico]
        
        # Título do tópico
        story.append(Paragraph(topico, ParagraphStyle('topico', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=6, spaceBefore=6)))
        story.append(Spacer(1, 6))
        
        # Verificar se tem notas no tópico
        if notas_do_topico:
            # Processar notas do tópico
            for nota in notas_do_topico:
                story.append(Spacer(1, 8))
                
                # Número da Nota
                story.append(Paragraph(f"NOTA N° {nota.numero}", ParagraphStyle('numero', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=3, spaceBefore=0)))
                
                # Título da Nota
                story.append(Paragraph(nota.titulo.upper(), ParagraphStyle('titulo', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=12, spaceBefore=0)))
                
                # Conteúdo da nota (usando a mesma lógica do PDF individual)
                if nota.conteudo:
                    # Importar a função de processamento das notas
                    from .views_assinaturas_notas import processar_formato_html_modal
                    
                    conteudo_html = nota.conteudo
                    conteudo_processado = processar_formato_html_modal(conteudo_html)
                    
                    # Dividir o conteúdo em parágrafos individuais para preservar alinhamento
                    paragrafos = conteudo_processado.split('</para>')
                    
                    for paragrafo in paragrafos:
                        if paragrafo.strip():
                            # Adicionar tag de fechamento se foi removida pelo split
                            if not paragrafo.strip().endswith('>'):
                                paragrafo = paragrafo.strip() + '</para>'
                            
                            # Determinar alinhamento baseado na tag
                            if 'align="center"' in paragrafo:
                                align = TA_CENTER
                            elif 'align="right"' in paragrafo:
                                align = 2  # TA_RIGHT
                            elif 'align="justify"' in paragrafo:
                                align = 4  # TA_JUSTIFY
                            else:
                                align = 0  # TA_LEFT
                            
                            # Remover tags para processamento
                            import re
                            paragrafo_limpo = re.sub(r'<para[^>]*>', '', paragrafo)
                            paragrafo_limpo = re.sub(r'</para>', '', paragrafo_limpo)
                            
                            if paragrafo_limpo.strip():
                                story.append(Paragraph(paragrafo_limpo.strip(), ParagraphStyle('conteudo', parent=styles['Normal'], fontSize=11, fontName=font_name, alignment=align, spaceAfter=6, spaceBefore=0, leading=14)))
                else:
                    story.append(Paragraph("Conteúdo não disponível", ParagraphStyle('conteudo', parent=styles['Normal'], fontSize=11, fontName=font_name, spaceAfter=6, spaceBefore=0, textColor=colors.grey)))
                
                # Adicionar assinaturas da nota (igual ao PDF individual)
                assinaturas_nota = nota.assinaturas.all().order_by('-data_assinatura')
                if assinaturas_nota.exists():
                    story.append(Spacer(1, 12))
                    
                    # Separar assinaturas físicas e eletrônicas
                    assinaturas_fisicas = assinaturas_nota.filter(tipo_midia='FISICA')
                    assinaturas_eletronicas = assinaturas_nota.filter(tipo_midia='ELETRONICA')
                    
                    # Assinaturas físicas primeiro
                    for assinatura in assinaturas_fisicas:
                        # Nome e posto
                        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                            militar = assinatura.assinado_por.militar
                            posto = militar.get_posto_graduacao_display()
                            if "BM" not in posto:
                                posto = f"{posto} BM"
                            nome_completo = f"{militar.nome_completo} - {posto}"
                        else:
                            nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                        
                        # Função
                        funcao = assinatura.funcao_assinatura or "Função não registrada"
                        
                        # Tipo de assinatura
                        tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
                        
                        story.append(Paragraph(f"<b>{nome_completo}</b>", ParagraphStyle('assinante', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=2, spaceBefore=2)))
                        story.append(Paragraph(f"{funcao}", ParagraphStyle('funcao', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=2, spaceBefore=2)))
                        story.append(Paragraph(f"<b>{tipo}</b>", ParagraphStyle('tipo_assinatura', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, fontName=font_name, spaceAfter=6, spaceBefore=2)))
                    
                    # Assinaturas eletrônicas depois
                    for assinatura in assinaturas_eletronicas:
                        data_formatada = assinatura.data_assinatura.strftime("%d/%m/%Y") if assinatura.data_assinatura else "Data não informada"
                        hora_formatada = assinatura.data_assinatura.strftime("%H:%M") if assinatura.data_assinatura else "Hora não informada"
                        
                        # Nome e posto
                        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                            militar = assinatura.assinado_por.militar
                            posto = militar.get_posto_graduacao_display()
                            if "BM" not in posto:
                                posto = f"{posto} BM"
                            nome_completo = f"{militar.nome_completo} - {posto}"
                        else:
                            nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                        
                        # Função
                        funcao = assinatura.funcao_assinatura or "Função não registrada"
                        
                        # Texto da assinatura eletrônica
                        texto_assinatura = f"Documento assinado eletronicamente por {nome_completo} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025."
                        
                        # Adicionar logo da assinatura eletrônica
                        from .utils import obter_caminho_assinatura_eletronica
                        logo_assinatura_path = obter_caminho_assinatura_eletronica()
                        
                        # Tabela das assinaturas: Logo + Texto de assinatura
                        assinatura_data = [
                            [Image(logo_assinatura_path, width=1.5*cm, height=1*cm), Paragraph(texto_assinatura, ParagraphStyle('assinatura_texto', parent=styles['Normal'], fontSize=8, spaceAfter=1, spaceBefore=1, leading=6, alignment=TA_JUSTIFY, fontName=font_name))]
                        ]
                        
                        assinatura_table = Table(assinatura_data, colWidths=[2*cm, 14*cm])
                        assinatura_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 1),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                            ('TOPPADDING', (0, 0), (-1, -1), 1),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        
                        story.append(assinatura_table)
                        story.append(Spacer(1, 4))
                
                # Verificar se há anexos na nota
                anexos_nota = nota.anexos.all() if hasattr(nota, 'anexos') else []
                if anexos_nota.exists():
                    story.append(Spacer(1, 6))
                    story.append(Paragraph("Anexos:", ParagraphStyle('anexos_titulo', parent=styles['Normal'], fontSize=9, fontName=font_name, spaceAfter=3, spaceBefore=0, textColor=colors.black)))
                    
                    for anexo in anexos_nota:
                        nome_anexo = anexo.arquivo.name.split('/')[-1] if anexo.arquivo else "Anexo sem nome"
                        # Criar URL completa para o anexo
                        url_anexo = f"/media/{anexo.arquivo.name}" if anexo.arquivo else "#"
                        
                        # Criar link clicável usando tag <a> do ReportLab
                        link_text = f'• <a href="{url_anexo}" color="blue">{nome_anexo}</a>'
                        story.append(Paragraph(link_text, ParagraphStyle('anexo_item', parent=styles['Normal'], fontSize=8, fontName=font_name, spaceAfter=2, spaceBefore=0, textColor=colors.blue, leftIndent=20)))
                
                # Transcrição da nota com origem e data (no final, discreta)
                origem_formatada = nota.origem_publicacao if nota.origem_publicacao and nota.origem_publicacao != '-' else "Origem não informada"
                
                # Formatação manual da data para garantir mês correto
                if nota.data_criacao:
                    from django.utils import timezone
                    from datetime import date
                    
                    # Converter para timezone local se for datetime
                    if isinstance(nota.data_criacao, date):
                        data_obj = nota.data_criacao
                    else:
                        data_local = timezone.localtime(nota.data_criacao)
                        data_obj = data_local.date()
                    
                    meses = {
                        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                    }
                    
                    dia = data_obj.day
                    mes = meses[data_obj.month]
                    ano = data_obj.year
                    data_formatada = f"{dia} de {mes} de {ano}"
                else:
                    data_formatada = "Data não informada"
                
                transcricao = f"(Transcrição da nota {nota.titulo.upper()} de Nº {nota.numero} com origem {origem_formatada}, datada de {data_formatada}.)"
                story.append(Paragraph(transcricao, ParagraphStyle('transcricao', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=8, fontName=font_name, spaceAfter=8, spaceBefore=4, textColor=colors.black)))
                
                # Espaçamento entre notas
                story.append(Spacer(1, 12))
        else:
            # Se não tem notas, mostrar "Sem Alterações"
            story.append(Paragraph("Sem Alterações", ParagraphStyle('sem_alteracoes', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, fontName=font_name, spaceAfter=12, spaceBefore=6, textColor=colors.grey)))

    # ===== ASSINATURAS DO BOLETIM =====
    if assinaturas.exists():
        story.append(Spacer(1, 20))
        
        # Data do boletim
        data_para_usar = boletim.data_publicacao if boletim.data_publicacao else boletim.data_criacao
        if data_para_usar:
            meses = {
                1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
            }
            
            from django.utils import timezone
            from datetime import datetime as dt
            if isinstance(data_para_usar, dt):
                data_local = timezone.localtime(data_para_usar)
                data_obj = data_local.date()
            else:
                data_obj = data_para_usar
            
            dia = data_obj.day
            mes = meses[data_obj.month]
            ano = data_obj.year
            data_extenso = f"Teresina - PI, {dia} de {mes} de {ano}"
        else:
            data_extenso = "Teresina - PI, data não informada"
        
        story.append(Paragraph(data_extenso, style_center))
        
        # Seção de Assinaturas Físicas (sem título)
        story.append(Spacer(1, 8))

        # Buscar todas as assinaturas válidas do boletim (da mais recente para a mais antiga)
        assinaturas_boletim = assinaturas.filter(assinado_por__isnull=False).order_by('-data_assinatura')
        
        for assinatura in assinaturas_boletim:
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
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            # Tipo de assinatura
            tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
            
            # Exibir no formato físico: Nome - Posto BM (negrito), Função (normal), Tipo (negrito menor)
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<b>{nome_completo}</b>", style_center))
            story.append(Paragraph(f"{funcao}", style_center))
            story.append(Paragraph(f"<b>{tipo}</b>", style_center))
            story.append(Spacer(1, 8))

        # Seção de Assinaturas Eletrônicas (sem título)
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=8, spaceBefore=8, color=colors.lightgrey))
        story.append(Spacer(1, 8))
        
        # Buscar todas as assinaturas para exibir na seção eletrônica
        assinaturas_eletronicas = assinaturas.filter(
            assinado_por__isnull=False
        ).order_by('-data_assinatura')
        
        for i, assinatura in enumerate(assinaturas_eletronicas):
            # Informações de assinatura eletrônica - seguir exatamente o padrão dos outros PDFs
            nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
            
            # Se o usuário tem militar associado, incluir posto com BM
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_assinante = f"{posto} {militar.nome_completo}"
            
            from .utils import formatar_data_assinatura
            data_formatada, hora_formatada = formatar_data_assinatura(assinatura.data_assinatura)
            
            # Função
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_assinante} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(obter_caminho_assinatura_eletronica(), width=2.5*cm, height=1.8*cm), Paragraph(texto_assinatura, style_small)]
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

    # Rodapé com QR Code para conferência de veracidade (padrão dos outros PDFs)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(boletim, request, tipo_documento='boletim_especial')
    
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

    # Preparar informações para o rodapé
    print(f"DEBUG - boletim.data_criacao: {boletim.data_criacao}")
    print(f"DEBUG - boletim.data_publicacao: {boletim.data_publicacao}")
    
    if boletim.data_criacao:
        data_edicao = boletim.data_criacao.strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como: {data_edicao}")
    elif boletim.data_publicacao:
        data_edicao = boletim.data_publicacao.strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como: {data_edicao}")
    else:
        # Usar data atual como fallback
        from datetime import datetime
        data_edicao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como fallback: {data_edicao}")
    
    # Data e hora atual de geração do PDF
    from datetime import datetime
    data_geracao_pdf = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    
    # Funções lambda para capturar informações do boletim
    def add_page_number_first(canvas, doc):
        add_page_number(canvas, doc, boletim, data_edicao, data_geracao_pdf, request.user)
    
    def add_page_number_later(canvas, doc):
        add_page_number(canvas, doc, boletim, data_edicao, data_geracao_pdf, request.user)
    
    # Construir PDF com numeração de páginas
    doc.build(story, onFirstPage=add_page_number_first, onLaterPages=add_page_number_later)
    buffer.seek(0)

    # Resposta HTTP - abrir na nova guia para visualização
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="boletim_especial_{boletim.numero}_2025.pdf"'
    
    return response


def processar_conteudo_html(html_content):
    """Processar conteúdo HTML para texto limpo para PDF"""
    if not html_content:
        return ""
    
    # Remover tags HTML
    import re
    from html import unescape
    
    # Decodificar entidades HTML
    texto = unescape(html_content)
    
    # Remover tags HTML
    texto = re.sub(r'<[^>]+>', '', texto)
    
    # Limpar espaços extras
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\n\s*\n', '\n\n', texto)
    
    return texto.strip()


@login_required
def boletim_reservado_gerar_pdf(request, pk):
    """Gera PDF do boletim reservado no modelo institucional"""
    
    # Configurar locale para português brasileiro
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass  # Usar formato padrão se não conseguir configurar

    try:
        boletim = get_object_or_404(Publicacao, pk=pk, tipo='BOLETIM_RESERVADO')
    except Publicacao.DoesNotExist:
        messages.error(request, f'Boletim reservado com ID {pk} não encontrado.')
        return redirect('militares:boletins_reservados_list')

    buffer = BytesIO()
    
    # Obter assinaturas
    assinaturas = boletim.assinaturas.all().order_by('-data_assinatura')
    
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=0.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Configurar fonte para suportar caracteres especiais
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        font_name = 'Arial'
    except:
        font_name = 'Helvetica'

    # Estilos customizados seguindo ABNT
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, spaceAfter=3, spaceBefore=3, fontName=font_name)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName=font_name, fontSize=12, spaceAfter=3, spaceBefore=3)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=14, spaceAfter=6, spaceBefore=6, fontName=font_name)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=12, spaceAfter=4, spaceBefore=4, fontName=font_name)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=10, spaceAfter=2, spaceBefore=2, fontName=font_name)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=12, spaceAfter=3, spaceBefore=3, leading=12, fontName=font_name)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=11, spaceAfter=4, spaceBefore=4, leading=11, fontName=font_name)
    style_paragraph = ParagraphStyle('paragraph', parent=styles['Normal'], fontSize=12, spaceAfter=3, spaceBefore=3, leading=12, alignment=TA_JUSTIFY, fontName=font_name)

    story = []

    # ===== CAPA DO BOLETIM =====
    # Cores institucionais
    vermelho_cbm = colors.HexColor('#DC2626')  # Vermelho institucional
    dourado_cbm = colors.HexColor('#D97706')   # Dourado institucional
    preto = colors.black
    
    # Margens laterais douradas (início)
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    story.append(Spacer(1, 20))
    
    # Logo CBMEPI no topo (maior na capa)
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=4*cm, height=4*cm, hAlign='CENTER'))
        story.append(Spacer(1, 20))

    # Título principal do Boletim (grande na capa)
    story.append(Paragraph("CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ", ParagraphStyle('titulo_principal', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=10, spaceBefore=10)))
    story.append(Paragraph("BOLETIM RESERVADO", ParagraphStyle('titulo_principal_vermelho', parent=styles['Normal'], alignment=TA_CENTER, fontSize=16, fontName=font_name, spaceAfter=10, spaceBefore=0, textColor=vermelho_cbm)))
    story.append(Paragraph(f"EDIÇÃO Nº {boletim.numero}", ParagraphStyle('edicao', parent=styles['Normal'], alignment=TA_CENTER, fontSize=20, fontName=font_name, spaceAfter=20, spaceBefore=0)))
    
    # Faixa diagonal com cores institucionais
    story.append(HRFlowable(width="100%", thickness=8, spaceAfter=0, spaceBefore=0, color=vermelho_cbm))
    story.append(HRFlowable(width="100%", thickness=4, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    story.append(Spacer(1, 30))
    
    # Textura sutil com linhas geométricas (simulando fogo estilizado)
    for i in range(3):
        # Linhas diagonais alternadas em tons de dourado
        cor_textura = colors.HexColor('#F59E0B') if i % 2 == 0 else colors.HexColor('#D97706')
        story.append(HRFlowable(width="80%", thickness=0.5, spaceAfter=2, spaceBefore=2, color=cor_textura, hAlign='CENTER'))
    
    story.append(Spacer(1, 20))
    
    # Data de criação do boletim (mesma data da coluna "Dia" na tabela)
    # Usar data_publicacao se disponível, senão usar data_criacao como fallback
    data_para_usar = boletim.data_publicacao if boletim.data_publicacao else boletim.data_criacao
    
    if data_para_usar:
        # Formatação manual para garantir mês correto
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        # Converter para timezone local para obter a data correta
        from django.utils import timezone
        from datetime import date
        
        from datetime import datetime as dt
        if isinstance(data_para_usar, dt):
            # Converter datetime UTC para timezone local e extrair a data
            data_local = timezone.localtime(data_para_usar)
            data_obj = data_local.date()
        else:
            # Já é uma data
            data_obj = data_para_usar
        
        dia = data_obj.day
        mes = meses[data_obj.month]
        ano = data_obj.year
        data_criacao = f"{dia:02d} de {mes} de {ano}"
    else:
        data_criacao = "Data não informada"
    story.append(Paragraph(f"Teresina - PI, {data_criacao}", ParagraphStyle('data_capa', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=25, spaceBefore=10)))
    
    # Espaço final na capa - 6 espaços adicionais
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    story.append(Spacer(1, 20))
    
    # Caixa de texto de acesso restrito (apenas para boletim reservado)
    if boletim.tipo == 'BOLETIM_RESERVADO':
        story.append(Spacer(1, 1*cm))
        
        # Criar parágrafos para o texto de acesso restrito
        story.append(Paragraph("<b><font color='#DC2626'>ACESSO RESTRITO</font></b>", ParagraphStyle('acesso_restrito_titulo', parent=styles['Normal'], alignment=TA_CENTER, fontSize=14, fontName=font_name, spaceAfter=5, spaceBefore=5)))
        story.append(Paragraph("<font color='#DC2626'>Art 325 do Decreto-Lei nº 2.848/1940 - Código Penal Brasileiro</font>", ParagraphStyle('acesso_restrito_texto', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=3, spaceBefore=3)))
        story.append(Paragraph("<font color='#DC2626'>Art. 22 da LEI Nº 12.527, DE 18 DE NOVEMBRO DE 2011 - Regula o acesso a informações</font>", ParagraphStyle('acesso_restrito_texto', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=5, spaceBefore=3)))
        story.append(Spacer(1, 1*cm))
        story.append(Spacer(1, 1*cm))
        story.append(Spacer(1, 1*cm))
    
    # Margens laterais douradas (fechamento)
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=0, spaceBefore=0, color=dourado_cbm))
    
    # Editores e informações do boletim agora aparecem no rodapé da capa
    
    
    # Quebra de página para o conteúdo
    story.append(PageBreak())

    # ===== CONTEÚDO DO BOLETIM =====
    # Logo CBMEPI no topo (menor no conteúdo)
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2*cm, height=2*cm, hAlign='CENTER'))
        story.append(Spacer(1, 2))

    # Cabeçalho Oficial (menor no conteúdo)
    story.append(Paragraph("ESTADO DO PIAUÍ", ParagraphStyle('estado', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("CORPO DE BOMBEIROS MILITAR DO PIAUÍ", ParagraphStyle('cbmepi', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("COMANDO GERAL", ParagraphStyle('comando', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("AJUDÂNCIA GERAL", ParagraphStyle('ajudancia', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490", ParagraphStyle('endereco', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=1, spaceBefore=1)))
    story.append(Paragraph("Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br", ParagraphStyle('contato', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=3, spaceBefore=1)))
    
    
    # Linha separadora
    story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black, spaceAfter=6, spaceBefore=6))

    # Título do Boletim na primeira linha
    story.append(Paragraph(f"BOLETIM RESERVADO DO CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ Nº {boletim.numero}", style_title))
    story.append(Spacer(1, 12))

    # Data de criação (mesma data da coluna "Dia" na tabela)
    story.append(Paragraph(f"Teresina - PI, {data_criacao}", style_center))
    story.append(Spacer(1, 12))
    
    # Texto de conhecimento e execução após a data (justificado)
    story.append(Spacer(1, 0.5*cm))  # 0,5cm de espaço
    story.append(Paragraph("Para conhecimento do Corpo de Bombeiros Militar do Estado do Piauí e devida execução, publica-se o seguinte:", ParagraphStyle('conhecimento', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=12, fontName=font_name, spaceAfter=20, spaceBefore=0)))

    # Buscar notas incluídas no boletim reservado
    notas_incluidas = Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim_reservado=boletim.numero
    ).order_by('data_publicacao')

    # Organizar notas por tópicos/partes
    topicos_organizados = {
        '1ª PARTE - SERVIÇOS DIÁRIOS': [],
        '2ª PARTE - INSTRUÇÃO': [],
        '3ª PARTE - ASSUNTOS GERAIS': [],
        '3ª PARTE - ADMINISTRATIVOS': [],
        '4ª PARTE - JUSTIÇA': [],
        '4ª PARTE - DISCIPLINA': [],
    }
    
    # Agrupar notas por tópico
    for nota in notas_incluidas:
        if nota.topicos and nota.topicos.strip() in topicos_organizados:
            topicos_organizados[nota.topicos.strip()].append(nota)
        else:
            # Se o tópico não estiver mapeado, adicionar à primeira parte
            topicos_organizados['1ª PARTE - SERVIÇOS DIÁRIOS'].append(nota)
    
    # Ordenar notas dentro de cada tópico por número
    for topico, notas in topicos_organizados.items():
        topicos_organizados[topico] = sorted(notas, key=lambda x: x.numero or '')

    # Processar cada tópico na ordem correta
    ordem_topicos = [
        '1ª PARTE - SERVIÇOS DIÁRIOS',
        '2ª PARTE - INSTRUÇÃO',
        '3ª PARTE - ASSUNTOS GERAIS',
        '3ª PARTE - ADMINISTRATIVOS',
        '4ª PARTE - JUSTIÇA',
        '4ª PARTE - DISCIPLINA',
    ]
    
    for topico in ordem_topicos:
        notas_do_topico = topicos_organizados[topico]
        
        # Não adicionar quebra de página - partes sequenciais
        
        # Título do tópico
        story.append(Paragraph(topico, ParagraphStyle('topico', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=6, spaceBefore=6)))
        story.append(Spacer(1, 6))
        
        # Verificar se tem notas no tópico
        if notas_do_topico:
            # Processar notas do tópico
            for nota in notas_do_topico:
                story.append(Spacer(1, 8))
                
                # Número da Nota
                story.append(Paragraph(f"NOTA N° {nota.numero}", ParagraphStyle('numero', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=3, spaceBefore=0)))
                
                # Título da Nota
                story.append(Paragraph(nota.titulo.upper(), ParagraphStyle('titulo', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, fontName=font_name, spaceAfter=12, spaceBefore=0)))
                
                # Conteúdo da nota (usando a mesma lógica do PDF individual)
                if nota.conteudo:
                    # Importar a função de processamento das notas
                    from .views_assinaturas_notas import processar_formato_html_modal
                    
                    conteudo_html = nota.conteudo
                    conteudo_processado = processar_formato_html_modal(conteudo_html)
                    
                    # Dividir o conteúdo em parágrafos individuais para preservar alinhamento
                    paragrafos = conteudo_processado.split('</para>')
                    
                    for paragrafo in paragrafos:
                        if paragrafo.strip():
                            # Adicionar tag de fechamento se foi removida pelo split
                            if not paragrafo.strip().endswith('>'):
                                paragrafo = paragrafo.strip() + '</para>'
                            
                            # Determinar alinhamento baseado na tag
                            if 'align="center"' in paragrafo:
                                align = TA_CENTER
                            elif 'align="right"' in paragrafo:
                                align = 2  # TA_RIGHT
                            elif 'align="justify"' in paragrafo:
                                align = 4  # TA_JUSTIFY
                            else:
                                align = 0  # TA_LEFT
                            
                            # Remover tags para processamento
                            import re
                            paragrafo_limpo = re.sub(r'<para[^>]*>', '', paragrafo)
                            paragrafo_limpo = re.sub(r'</para>', '', paragrafo_limpo)
                            
                            if paragrafo_limpo.strip():
                                story.append(Paragraph(paragrafo_limpo.strip(), ParagraphStyle('conteudo', parent=styles['Normal'], fontSize=11, fontName=font_name, alignment=align, spaceAfter=6, spaceBefore=0, leading=14)))
                else:
                    story.append(Paragraph("Conteúdo não disponível", ParagraphStyle('conteudo', parent=styles['Normal'], fontSize=11, fontName=font_name, spaceAfter=6, spaceBefore=0, textColor=colors.grey)))
                
                # Adicionar assinaturas da nota (igual ao PDF individual)
                assinaturas_nota = nota.assinaturas.all().order_by('-data_assinatura')
                if assinaturas_nota.exists():
                    story.append(Spacer(1, 12))
                    
                    # Separar assinaturas físicas e eletrônicas
                    assinaturas_fisicas = assinaturas_nota.filter(tipo_midia='FISICA')
                    assinaturas_eletronicas = assinaturas_nota.filter(tipo_midia='ELETRONICA')
                    
                    # Assinaturas físicas primeiro
                    for assinatura in assinaturas_fisicas:
                        # Nome e posto
                        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                            militar = assinatura.assinado_por.militar
                            posto = militar.get_posto_graduacao_display()
                            if "BM" not in posto:
                                posto = f"{posto} BM"
                            nome_completo = f"{militar.nome_completo} - {posto}"
                        else:
                            nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                        
                        # Função
                        funcao = assinatura.funcao_assinatura or "Função não registrada"
                        
                        # Tipo de assinatura
                        tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
                        
                        story.append(Paragraph(f"<b>{nome_completo}</b>", ParagraphStyle('assinante', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, fontName=font_name, spaceAfter=2, spaceBefore=2)))
                        story.append(Paragraph(f"{funcao}", ParagraphStyle('funcao', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, fontName=font_name, spaceAfter=2, spaceBefore=2)))
                        story.append(Paragraph(f"<b>{tipo}</b>", ParagraphStyle('tipo_assinatura', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, fontName=font_name, spaceAfter=6, spaceBefore=2)))
                    
                    # Assinaturas eletrônicas depois
                    for assinatura in assinaturas_eletronicas:
                        data_formatada = assinatura.data_assinatura.strftime("%d/%m/%Y") if assinatura.data_assinatura else "Data não informada"
                        hora_formatada = assinatura.data_assinatura.strftime("%H:%M") if assinatura.data_assinatura else "Hora não informada"
                        
                        # Nome e posto
                        if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                            militar = assinatura.assinado_por.militar
                            posto = militar.get_posto_graduacao_display()
                            if "BM" not in posto:
                                posto = f"{posto} BM"
                            nome_completo = f"{militar.nome_completo} - {posto}"
                        else:
                            nome_completo = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                        
                        # Função
                        funcao = assinatura.funcao_assinatura or "Função não registrada"
                        
                        # Texto da assinatura eletrônica
                        texto_assinatura = f"Documento assinado eletronicamente por {nome_completo} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025."
                        
                        # Adicionar logo da assinatura eletrônica
                        from .utils import obter_caminho_assinatura_eletronica
                        logo_assinatura_path = obter_caminho_assinatura_eletronica()
                        
                        # Tabela das assinaturas: Logo + Texto de assinatura
                        assinatura_data = [
                            [Image(logo_assinatura_path, width=1.5*cm, height=1*cm), Paragraph(texto_assinatura, ParagraphStyle('assinatura_texto', parent=styles['Normal'], fontSize=8, spaceAfter=1, spaceBefore=1, leading=6, alignment=TA_JUSTIFY, fontName=font_name))]
                        ]
                        
                        assinatura_table = Table(assinatura_data, colWidths=[2*cm, 14*cm])
                        assinatura_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 1),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                            ('TOPPADDING', (0, 0), (-1, -1), 1),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                            ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        
                        story.append(assinatura_table)
                        story.append(Spacer(1, 4))
                
                # Verificar se há anexos na nota
                anexos_nota = nota.anexos.all() if hasattr(nota, 'anexos') else []
                if anexos_nota.exists():
                    story.append(Spacer(1, 6))
                    story.append(Paragraph("Anexos:", ParagraphStyle('anexos_titulo', parent=styles['Normal'], fontSize=9, fontName=font_name, spaceAfter=3, spaceBefore=0, textColor=colors.black)))
                    
                    for anexo in anexos_nota:
                        nome_anexo = anexo.arquivo.name.split('/')[-1] if anexo.arquivo else "Anexo sem nome"
                        # Criar URL completa para o anexo
                        url_anexo = f"/media/{anexo.arquivo.name}" if anexo.arquivo else "#"
                        
                        # Criar link clicável usando tag <a> do ReportLab
                        link_text = f'• <a href="{url_anexo}" color="blue">{nome_anexo}</a>'
                        story.append(Paragraph(link_text, ParagraphStyle('anexo_item', parent=styles['Normal'], fontSize=8, fontName=font_name, spaceAfter=2, spaceBefore=0, textColor=colors.blue, leftIndent=20)))
                
                # Transcrição da nota com origem e data (no final, discreta)
                origem_formatada = nota.origem_publicacao if nota.origem_publicacao and nota.origem_publicacao != '-' else "Origem não informada"
                
                # Formatação manual da data para garantir mês correto
                if nota.data_criacao:
                    from django.utils import timezone
                    from datetime import date
                    
                    # Converter para timezone local se for datetime
                    if isinstance(nota.data_criacao, date):
                        data_obj = nota.data_criacao
                    else:
                        data_local = timezone.localtime(nota.data_criacao)
                        data_obj = data_local.date()
                    
                    meses = {
                        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
                    }
                    
                    dia = data_obj.day
                    mes = meses[data_obj.month]
                    ano = data_obj.year
                    data_formatada = f"{dia} de {mes} de {ano}"
                else:
                    data_formatada = "Data não informada"
                
                transcricao = f"(Transcrição da nota {nota.titulo.upper()} de Nº {nota.numero} com origem {origem_formatada}, datada de {data_formatada}.)"
                story.append(Paragraph(transcricao, ParagraphStyle('transcricao', parent=styles['Normal'], alignment=TA_JUSTIFY, fontSize=8, fontName=font_name, spaceAfter=8, spaceBefore=4, textColor=colors.black)))
                
                # Espaçamento entre notas
                story.append(Spacer(1, 12))
        else:
            # Se não tem notas, mostrar "Sem Alterações"
            story.append(Paragraph("Sem Alterações", ParagraphStyle('sem_alteracoes', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, fontName=font_name, spaceAfter=12, spaceBefore=6, textColor=colors.grey)))

    # ===== ASSINATURAS DO BOLETIM =====
    if assinaturas.exists():
        story.append(Spacer(1, 20))
        
        # Data do boletim
        data_para_usar = boletim.data_publicacao if boletim.data_publicacao else boletim.data_criacao
        if data_para_usar:
            meses = {
                1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
                5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
                9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
            }
            
            from django.utils import timezone
            from datetime import datetime as dt
            if isinstance(data_para_usar, dt):
                data_local = timezone.localtime(data_para_usar)
                data_obj = data_local.date()
            else:
                data_obj = data_para_usar
            
            dia = data_obj.day
            mes = meses[data_obj.month]
            ano = data_obj.year
            data_extenso = f"Teresina - PI, {dia} de {mes} de {ano}"
        else:
            data_extenso = "Teresina - PI, data não informada"
        
        story.append(Paragraph(data_extenso, style_center))
        
        # Seção de Assinaturas Físicas (sem título)
        story.append(Spacer(1, 8))

        # Buscar todas as assinaturas válidas do boletim (da mais recente para a mais antiga)
        assinaturas_boletim = assinaturas.filter(assinado_por__isnull=False).order_by('-data_assinatura')
        
        for assinatura in assinaturas_boletim:
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
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            # Tipo de assinatura
            tipo = assinatura.get_tipo_assinatura_display() or "Tipo não registrado"
            
            # Exibir no formato físico: Nome - Posto BM (negrito), Função (normal), Tipo (negrito menor)
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<b>{nome_completo}</b>", style_center))
            story.append(Paragraph(f"{funcao}", style_center))
            story.append(Paragraph(f"<b>{tipo}</b>", style_center))
            story.append(Spacer(1, 8))

        # Seção de Assinaturas Eletrônicas (sem título)
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=8, spaceBefore=8, color=colors.lightgrey))
        story.append(Spacer(1, 8))
        
        # Buscar todas as assinaturas para exibir na seção eletrônica
        assinaturas_eletronicas = assinaturas.filter(
            assinado_por__isnull=False
        ).order_by('-data_assinatura')
        
        for i, assinatura in enumerate(assinaturas_eletronicas):
            # Informações de assinatura eletrônica - seguir exatamente o padrão dos outros PDFs
            nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
            
            # Se o usuário tem militar associado, incluir posto com BM
            if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                militar = assinatura.assinado_por.militar
                posto = militar.get_posto_graduacao_display()
                # Adicionar BM após o posto se não já estiver presente
                if "BM" not in posto:
                    posto = f"{posto} BM"
                nome_assinante = f"{posto} {militar.nome_completo}"
            
            from .utils import formatar_data_assinatura
            data_formatada, hora_formatada = formatar_data_assinatura(assinatura.data_assinatura)
            
            # Função
            funcao = assinatura.funcao_assinatura or "Função não registrada"
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_assinante} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(obter_caminho_assinatura_eletronica(), width=2.5*cm, height=1.8*cm), Paragraph(texto_assinatura, style_small)]
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

    # Rodapé com QR Code para conferência de veracidade (padrão dos outros PDFs)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(boletim, request, tipo_documento='boletim_reservado')
    
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

    # Preparar informações para o rodapé
    print(f"DEBUG - boletim.data_criacao: {boletim.data_criacao}")
    print(f"DEBUG - boletim.data_publicacao: {boletim.data_publicacao}")
    
    if boletim.data_criacao:
        data_edicao = boletim.data_criacao.strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como: {data_edicao}")
    elif boletim.data_publicacao:
        data_edicao = boletim.data_publicacao.strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como: {data_edicao}")
    else:
        # Usar data atual como fallback
        from datetime import datetime
        data_edicao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        print(f"DEBUG - data_edicao definida como fallback: {data_edicao}")
    
    # Data e hora atual de geração do PDF
    from datetime import datetime
    data_geracao_pdf = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    
    # Funções lambda para capturar informações do boletim
    def add_page_number_first(canvas, doc):
        add_page_number(canvas, doc, boletim, data_edicao, data_geracao_pdf, request.user)
        # Adicionar marca d'água com CPF
        add_watermark_cpf(canvas, request.user)
    
    def add_page_number_later(canvas, doc):
        add_page_number(canvas, doc, boletim, data_edicao, data_geracao_pdf, request.user)
        # Adicionar marca d'água com CPF
        add_watermark_cpf(canvas, request.user)
    
    # Construir PDF com numeração de páginas
    doc.build(story, onFirstPage=add_page_number_first, onLaterPages=add_page_number_later)
    buffer.seek(0)

    # Resposta HTTP - abrir na nova guia para visualização
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="boletim_reservado_{boletim.numero}_2025.pdf"'
    
    return response
