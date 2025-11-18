from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import FileResponse, JsonResponse
from django.conf import settings
from .models import SessaoComissao, MembroComissao, AtaSessao, VotoDeliberacao, DocumentoSessao
from reportlab.platypus import (
    SimpleDocTemplate, Image, Spacer, Paragraph, Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from io import BytesIO
import os
import locale
import unicodedata
from datetime import datetime
from PyPDF2 import PdfMerger

@login_required
def upload_arquivos_sessao(request, pk):
    """Processa seleção de documentos existentes para o PDF completo"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})
    
    try:
        sessao = SessaoComissao.objects.get(pk=pk)
    except SessaoComissao.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sessão não encontrada'})
    
    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Você não é membro desta comissão'})
    
    # Processar seleção de documentos
    documentos_selecionados = {
        'incluir_documento_origem': request.POST.get('incluir_documento_origem') == 'on',
        'deliberacoes_selecionadas': request.POST.getlist('deliberacoes_selecionadas'),
        'votos_selecionados': request.POST.getlist('votos_selecionados'),
        'documentos_selecionados': request.POST.getlist('documentos_selecionados'),
    }
    
    # Salvar seleção na sessão (pode ser usado para gerar o PDF)
    request.session[f'documentos_selecionados_sessao_{pk}'] = documentos_selecionados
    
    return JsonResponse({
        'success': True,
        'message': 'Seleção de documentos processada com sucesso',
        'documentos_selecionados': documentos_selecionados
    })

def testar_pdf(request):
    """View para testar acesso direto ao PDF"""
    from django.http import FileResponse
    import os
    
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs', 'documentacao_completa_sessao_404_20250721_125247.pdf')
    
    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    else:
        from django.http import HttpResponse
        return HttpResponse('PDF não encontrado', status=404)

@login_required
def sessao_gerar_pdf_completo(request, pk):
    """Gera PDF completo da sessão com documentos selecionados"""
    
    # Configurar locale para português brasileiro
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass

    try:
        sessao = SessaoComissao.objects.get(pk=pk)
    except SessaoComissao.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
        return redirect('militares:sessao_comissao_list')

    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        messages.error(request, 'Você não é membro desta comissão.')
        return redirect('militares:sessao_comissao_detail', pk=sessao.pk)

    # Se for GET, usar todos os documentos disponíveis
    if request.method == 'GET':
        documentos_selecionados = {
            'incluir_documento_origem': True,
            'deliberacoes_selecionadas': [d.id for d in sessao.deliberacoes.all()],
            'votos_selecionados': [v.id for v in VotoDeliberacao.objects.filter(deliberacao__sessao=sessao)],
            'documentos_selecionados': [d.id for d in sessao.documentos.all()],
        }
    else:
        # Se for POST, obter seleção da sessão
        documentos_selecionados = request.session.get(f'documentos_selecionados_sessao_{pk}', {})
        
        # Se não há seleção salva, usar todos os documentos por padrão
        if not documentos_selecionados:
            documentos_selecionados = {
                'incluir_documento_origem': True,
                'deliberacoes_selecionadas': [d.id for d in sessao.deliberacoes.all()],
                'votos_selecionados': [v.id for v in VotoDeliberacao.objects.filter(deliberacao__sessao=sessao)],
                'documentos_selecionados': [d.id for d in sessao.documentos.all()],
            }
    
    # VALIDAÇÃO: Verificar se há documentos sem assinatura
    votos_selecionados = documentos_selecionados.get('votos_selecionados', [])
    votos_sem_assinatura = []
    
    if votos_selecionados:
        votos = VotoDeliberacao.objects.filter(id__in=votos_selecionados)
        for voto in votos:
            if not voto.assinado:
                votos_sem_assinatura.append(f"Voto do {voto.membro.militar.nome_completo} na Deliberação {voto.deliberacao.numero}")
    
    # Verificar se a ata está selecionada e se tem assinaturas
    ata_sem_assinatura = None
    try:
        ata = AtaSessao.objects.get(sessao=sessao)
        # Se a ata existe mas não tem assinaturas eletrônicas
        if not ata.assinaturas.filter(assinado_por__isnull=False).exists():
            ata_sem_assinatura = "Ata da sessão"
    except AtaSessao.DoesNotExist:
        pass
    
    # Se há documentos sem assinatura, mostrar erro
    if votos_sem_assinatura or ata_sem_assinatura:
        mensagem_erro = "Não é possível gerar o PDF completo. Os seguintes documentos não estão assinados:\n\n"
        
        if votos_sem_assinatura:
            mensagem_erro += "Votos sem assinatura:\n"
            for voto in votos_sem_assinatura:
                mensagem_erro += f"• {voto}\n"
            mensagem_erro += "\n"
        
        if ata_sem_assinatura:
            mensagem_erro += f"• {ata_sem_assinatura}\n"
        
        mensagem_erro += "\nAssine todos os documentos antes de gerar o PDF completo."
        
        messages.error(request, mensagem_erro)
        return redirect('militares:sessao_comissao_detail', pk=sessao.pk)

    # Criar buffer para o PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Definir estilos
    styles = getSampleStyleSheet()
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=11)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=13, spaceAfter=10, underlineProportion=0.1)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=11, spaceAfter=8)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    style_heading = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=10,
        textColor=colors.black
    )
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    style_just = ParagraphStyle(
        'Justified',
        parent=styles['Normal'],
        fontSize=10,
        alignment=4,  # Justificado
        spaceAfter=6
    )
    style_center = ParagraphStyle(
        'Center',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,  # Centralizado
        spaceAfter=6
    )

    # Logo/Brasão centralizado
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
        story.append(Spacer(1, 6))

    # Cabeçalho institucional
    # Determinar o nome da comissão baseado no tipo
    if sessao.comissao.tipo == 'CPO':
        nome_comissao = "COMISSÃO DE PROMOÇÕES DE OFICIAIS - CBMEPI-PI"
    else:  # CPP
        nome_comissao = "COMISSÃO DE PROMOÇÕES DE PRAÇAS - CBMEPI-PI"
    
    cabecalho = [
        "GOVERNO DO ESTADO DO PIAUÍ",
        "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
        nome_comissao,
        "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    for linha in cabecalho:
        story.append(Paragraph(linha, style_center))
    story.append(Spacer(1, 10))

    # Título centralizado e sublinhado
    # Determinar o título baseado no tipo da comissão
    if sessao.comissao.tipo == 'CPO':
        titulo = f'<u>SESSÃO DA COMISSÃO DE PROMOÇÕES DE OFICIAIS Nº {sessao.numero}</u>'
    else:  # CPP
        titulo = f'<u>SESSÃO DA COMISSÃO DE PROMOÇÕES DE PRAÇAS Nº {sessao.numero}</u>'
    
    story.append(Paragraph(titulo, style_title))
    story.append(Spacer(1, 16))



    # Informações da sessão
    story.append(Paragraph("INFORMAÇÕES DA SESSÃO", style_heading))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    info_data = [
        ['Número:', str(sessao.numero)],
        ['Tipo:', sessao.get_tipo_display()],
        ['Status:', sessao.get_status_display()],
        ['Data:', sessao.data_sessao.strftime('%d/%m/%Y')],
        ['Horário:', f"{sessao.hora_inicio.strftime('%H:%M')} - {sessao.hora_fim.strftime('%H:%M') if sessao.hora_fim else 'Não definido'}"],
        ['Local:', sessao.local],
    ]
    
    # Adicionar pauta e observações com quebra de linha
    if sessao.pauta:
        # Criar Paragraph para a pauta para permitir quebra de linha
        pauta_paragraph = Paragraph(sessao.pauta, style_normal)
        info_data.append(['Pauta:', pauta_paragraph])
    if sessao.observacoes:
        # Criar Paragraph para as observações para permitir quebra de linha
        obs_paragraph = Paragraph(sessao.observacoes, style_normal)
        info_data.append(['Observações:', obs_paragraph])

    info_table = Table(info_data, colWidths=[4*cm, 11*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('WORDWRAP', (1, 0), (1, -1), True),  # Permitir quebra de palavras
    ]))
    story.append(info_table)
    story.append(Spacer(1, 40))

    # Presentes
    story.append(Paragraph("PRESENTES", style_heading))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    presencas = sessao.presencas.filter(presente=True).select_related('membro__militar', 'membro__cargo')
    if presencas.exists():
        # Definir ordem hierárquica dos postos (do mais alto ao mais baixo)
        ordem_postos = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
        
        # Ordenar presenças por posto/graduação (antiguidade)
        presencas_ordenadas = []
        for presenca in presencas:
            militar = presenca.membro.militar
            indice_posto = ordem_postos.index(militar.posto_graduacao) if militar.posto_graduacao in ordem_postos else 999
            presencas_ordenadas.append((indice_posto, presenca))
        
        # Ordenar por índice do posto (menor índice = posto mais alto)
        presencas_ordenadas.sort(key=lambda x: x[0])
        
        presenca_data = [['Nome', 'Posto', 'Função']]
        for indice, presenca in presencas_ordenadas:
            militar = presenca.membro.militar
            cargo = presenca.membro.cargo.nome if presenca.membro.cargo else "Não definida"
            presenca_data.append([
                militar.nome_completo,
                f"{militar.get_posto_graduacao_display()} BM",
                cargo
            ])
        
        presenca_table = Table(presenca_data, colWidths=[6*cm, 3*cm, 6*cm])
        presenca_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        story.append(presenca_table)
    else:
        story.append(Paragraph("Nenhuma presença registrada.", style_normal))
    
    story.append(Spacer(1, 40))

    # Verificar se a pauta é sobre aprovação de quadros de acesso
    
    def normalizar(texto):
        if not texto:
            return ''
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').upper()
    
    pauta_normalizada = normalizar(sessao.pauta)
    pauta_aprovacao_quadro = (
        'APROVACAO DE QUADRO DE ACESSO' in pauta_normalizada or
        'APROVACAO DE QUADROS DE ACESSO' in pauta_normalizada or
        'APROVACAO DE QUADROS DE ACESSOS' in pauta_normalizada
    )
    
    # Se a pauta é sobre aprovação de quadros, buscar quadros para incluir no PDF
    if pauta_aprovacao_quadro:
        from .models import QuadroAcesso
        
        # Buscar quadros de acesso da comissão específica
        if sessao.comissao.tipo == 'CPO':
            quadros_acesso_sessao = QuadroAcesso.objects.filter(
                categoria='OFICIAIS',
                status__in=['ELABORADO', 'HOMOLOGADO', 'ASSINADO']
            ).order_by('-data_promocao')
        else:
            quadros_acesso_sessao = QuadroAcesso.objects.filter(
                categoria='PRACAS',
                status__in=['ELABORADO', 'HOMOLOGADO', 'ASSINADO']
            ).order_by('-data_promocao')

    # Buscar documento de origem (primeiro do tipo PAUTA, MEMORANDO, OFICIO, REQUERIMENTO)
    documento_origem = DocumentoSessao.objects.filter(
        sessao=sessao,
        tipo__in=['PAUTA', 'MEMORANDO', 'OFICIO', 'REQUERIMENTO']
    ).order_by('data_upload').first()

    # Documento de origem (se selecionado)
    if documentos_selecionados.get('incluir_documento_origem') and documento_origem:
        story.append(Paragraph("DOCUMENTO DE ORIGEM", style_heading))
        story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
        
        story.append(Paragraph(f"<b>Título:</b> {documento_origem.titulo or 'Documento de Origem'}", style_normal))
        if documento_origem.descricao:
            story.append(Paragraph(f"<b>Descrição:</b> {documento_origem.descricao}", style_normal))
        story.append(Paragraph(f"<b>Data de Upload:</b> {documento_origem.data_upload.strftime('%d/%m/%Y %H:%M')}", style_normal))
        story.append(Spacer(1, 40))





    # Gerar PDF principal em memória
    doc.build(story)
    buffer.seek(0)

    # --- NOVO: Mesclar PDFs anexos ---
    merger = PdfMerger()
    # Adiciona o PDF principal
    merger.append(buffer)

    # 1. PDF da ata da sessão (PRIMEIRO - logo após dados da sessão e presentes)
    try:
        ata = AtaSessao.objects.get(sessao=sessao)
        # Gerar PDF da ata usando a mesma lógica da view original
        ata_buffer = gerar_pdf_ata_original(ata)
        if ata_buffer:
            merger.append(ata_buffer)
    except AtaSessao.DoesNotExist:
        pass
    except Exception as e:
        print(f"Erro ao gerar PDF da ata: {e}")

    # 2. PDFs dos votos dos membros (usando a mesma lógica da view original)
    votos_selecionados = documentos_selecionados.get('votos_selecionados', [])
    if votos_selecionados:
        for voto in VotoDeliberacao.objects.filter(id__in=votos_selecionados):
            try:
                # Gerar PDF do voto usando a mesma lógica da view original
                voto_buffer = gerar_pdf_voto_original(voto)
                if voto_buffer:
                    merger.append(voto_buffer)
            except Exception as e:
                print(f"Erro ao gerar PDF do voto {voto.pk}: {e}")

    # 3. PDFs dos documentos adicionais anexados (apenas arquivos PDF existentes)
    documentos_adicionais = documentos_selecionados.get('documentos_selecionados', [])
    if documentos_adicionais:
        documentos = DocumentoSessao.objects.filter(id__in=documentos_adicionais)
        for doc_adicional in documentos:
            # Verificar se é um arquivo PDF e se existe
            if (doc_adicional.arquivo and 
                hasattr(doc_adicional.arquivo, 'path') and 
                doc_adicional.arquivo.path and 
                os.path.exists(doc_adicional.arquivo.path) and
                doc_adicional.arquivo.name.lower().endswith('.pdf')):
                try:
                    merger.append(doc_adicional.arquivo.path)
                except Exception as e:
                    print(f"Erro ao anexar PDF {doc_adicional.arquivo.name}: {e}")
                    pass

    # 4. PDFs dos quadros de acesso (se a pauta for sobre aprovação de quadros)
    if pauta_aprovacao_quadro and quadros_acesso_sessao.exists():
        from .views import quadro_acesso_pdf
        from .views_pracas import quadro_acesso_pracas_pdf
        
        for quadro in quadros_acesso_sessao:
            try:
                # Gerar PDF do quadro baseado na categoria
                if quadro.categoria == 'PRACAS':
                    quadro_response = quadro_acesso_pracas_pdf(request, quadro.pk)
                else:
                    quadro_response = quadro_acesso_pdf(request, quadro.pk)
                
                if quadro_response and hasattr(quadro_response, 'content'):
                    # Criar buffer temporário para o PDF do quadro
                    temp_buffer = BytesIO(quadro_response.content)
                    merger.append(temp_buffer)
                    print(f"PDF do quadro {quadro.numero} anexado com sucesso")
                else:
                    print(f"Erro: PDF do quadro {quadro.numero} não foi gerado corretamente")
                    
            except Exception as e:
                print(f"Erro ao anexar PDF do quadro {quadro.numero}: {e}")
                pass

    # Gerar PDF final mesclado
    output_buffer = BytesIO()
    merger.write(output_buffer)
    merger.close()
    output_buffer.seek(0)

    # Criar nome único para o arquivo
    from django.utils import timezone
    timestamp = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M%S")
    filename = f'documentacao_completa_sessao_{sessao.numero}_{timestamp}.pdf'
    
    # Salvar arquivo temporário
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)
    
    with open(temp_path, 'wb') as f:
        f.write(output_buffer.getvalue())
    
            # Retornar o PDF diretamente como FileResponse
        from django.http import FileResponse
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'PDF gerado com sucesso: {temp_path}')
        logger.info(f'Tamanho do arquivo: {os.path.getsize(temp_path)} bytes')
        
        # Retornar o PDF diretamente
        response = FileResponse(open(temp_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        response['Content-Length'] = str(os.path.getsize(temp_path))
        logger.info('PDF enviado como FileResponse')
        return response


def gerar_pdf_voto_original(voto):
    """Gera PDF do voto usando exatamente a mesma lógica da view original"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    import qrcode
    from django.urls import reverse
    from django.contrib.sites.shortcuts import get_current_site
    from django.utils import timezone
    import locale
    
    # Configurar locale para português brasileiro
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Estilos customizados (exatamente como na view original)
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=11)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=13, spaceAfter=10, underlineProportion=0.1)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=11, spaceAfter=8)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, spaceAfter=6)

    story = []

    # Logo/Brasão centralizado
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
        story.append(Spacer(1, 6))

    # Cabeçalho institucional
    cabecalho = [
        "GOVERNO DO ESTADO DO PIAUÍ",
        "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
        f"{voto.deliberacao.sessao.comissao.nome.upper()} - CBMEPI-PI",
        "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    for linha in cabecalho:
        story.append(Paragraph(linha, style_center))
    story.append(Spacer(1, 10))

    # Título centralizado e sublinhado
    titulo = '<u>VOTO PROFERIDO EM DELIBERAÇÃO DE COMISSÃO</u>'
    story.append(Paragraph(titulo, style_title))
    story.append(Spacer(1, 16))

    # Informações do voto (alinhadas à esquerda)
    info_data = [
        [Paragraph('<b>Deliberação:</b>', style_bold), Paragraph(f"{voto.deliberacao.numero} - {voto.deliberacao.assunto}", styles['Normal'])],
        [Paragraph('<b>Comissão:</b>', style_bold), Paragraph(voto.deliberacao.sessao.comissao.nome, styles['Normal'])],
        [Paragraph('<b>Data da Sessão:</b>', style_bold), Paragraph(voto.deliberacao.sessao.data_sessao.strftime('%d/%m/%Y'), styles['Normal'])],
        [Paragraph('<b>Membro:</b>', style_bold), Paragraph(voto.membro.militar.nome_completo, styles['Normal'])],
        [Paragraph('<b>Função:</b>', style_bold), Paragraph(voto.membro.cargo.nome if hasattr(voto.membro, 'cargo') and voto.membro.cargo else 'Membro da Comissão', styles['Normal'])],
        [Paragraph('<b>Opção de Voto:</b>', style_bold), Paragraph(voto.get_voto_display(), styles['Normal'])],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 11*cm], hAlign='LEFT')
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 40))

    # Voto proferido (espaçamento 1,15 e justificado)
    if voto.voto_proferido:
        story.append(Paragraph('<b>Voto Proferido:</b>', style_bold))
        story.append(Spacer(1, 4))
        # Criar estilo com espaçamento 1,15 e justificado
        style_voto = ParagraphStyle('voto', parent=styles['Normal'], leading=15, alignment=4)
        story.append(Paragraph(voto.voto_proferido, style_voto))
        story.append(Spacer(1, 40))

    # Assinatura Eletrônica (padrão dos quadros)
    if voto.assinado and voto.data_assinatura:
        # Informações de assinatura eletrônica
        nome_assinante = voto.membro.militar.nome_completo
        
        # Se o usuário tem militar associado, incluir posto com BM
        if hasattr(voto.membro.militar, 'get_posto_graduacao_display'):
            posto = voto.membro.militar.get_posto_graduacao_display()
            # Adicionar BM após o posto se não já estiver presente
            if "BM" not in posto:
                posto = f"{posto} BM"
            nome_assinante = f"{posto} {voto.membro.militar.nome_completo}"
        
        # Função da assinatura
        funcao = voto.funcao_assinatura or voto.membro.cargo.nome if hasattr(voto.membro, 'cargo') and voto.membro.cargo else "Membro da Comissão"
        
        # Data e hora da assinatura
        agora = timezone.localtime(voto.data_assinatura)
        data_formatada = agora.strftime('%d/%m/%Y')
        hora_formatada = agora.strftime('%H:%M')
        
        texto_assinatura = f"Documento assinado eletronicamente por {nome_assinante} - {funcao}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
        
        # Adicionar logo da assinatura eletrônica
        from .utils import obter_caminho_assinatura_eletronica
        logo_path = obter_caminho_assinatura_eletronica()
        
        # Tabela das assinaturas: Logo + Texto de assinatura
        assinatura_data = [
                            [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
        ]
        
        assinatura_table = Table(assinatura_data, colWidths=[2*cm, 14*cm])
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
        story.append(Spacer(1, 10))  # Espaçamento após assinatura
        story.append(Spacer(1, 40))

    # Rodapé com QR Code (padrão dos quadros)
    # Gerar URL de autenticação
    url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:voto_visualizar_assinar', kwargs={'pk': voto.pk})}"
    
    # Gerar códigos de verificação
    import hashlib
    codigo_verificador = f"{hashlib.md5(str(voto.pk).encode()).hexdigest()[:8].upper()}"
    codigo_crc = f"{hash(str(voto.pk)) % 0xFFFFFFF:07X}"
    
    texto_autenticacao = f"A autenticidade deste documento pode ser conferida no site <a href='{url_autenticacao}' color='blue'>{url_autenticacao}</a>, informando o código verificador <b>{codigo_verificador}</b> e o código CRC <b>{codigo_crc}</b>."
    
    # Gerar QR Code
    qr = qrcode.make(url_autenticacao)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_img = Image(qr_buffer, width=2*cm, height=2*cm)
    
    # Tabela do rodapé: QR + Texto de autenticação
    rodape_data = [
        [qr_img, Paragraph(texto_autenticacao, style_small)]
    ]
    
    rodape_table = Table(rodape_data, colWidths=[2*cm, 14*cm])
    rodape_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    
    story.append(rodape_table)

    # Construir o PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def gerar_pdf_ata_original(ata):
    """Gera PDF da ata usando exatamente a mesma lógica da view original"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY
    import qrcode
    import re
    from html import unescape
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Configurar fonte para suportar caracteres especiais
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        font_name = 'Arial'
    except:
        font_name = 'Helvetica'
    
    # Estilos customizados com fonte que suporta UTF-8
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=11, fontName=font_name)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName=font_name, fontSize=11)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=13, spaceAfter=10, underlineProportion=0.1, fontName=font_name)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=11, spaceAfter=8, fontName=font_name)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, fontName=font_name)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11, spaceAfter=8, fontName=font_name)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, spaceAfter=6, fontName=font_name)
    
    # Estilos para cabeçalho institucional (padrão do sistema)
    style_header = ParagraphStyle('header', parent=styles['Heading1'], fontSize=12, alignment=1, spaceAfter=8, spaceBefore=12, fontName=font_name)
    style_subheader = ParagraphStyle('subheader', parent=styles['Heading2'], fontSize=11, alignment=1, spaceAfter=6, spaceBefore=10, fontName=font_name)
    
    # Novos estilos para formatação avançada
    style_heading1 = ParagraphStyle('heading1', parent=styles['Heading1'], fontSize=12, spaceAfter=8, spaceBefore=12, fontName=font_name)
    style_heading2 = ParagraphStyle('heading2', parent=styles['Heading2'], fontSize=11, spaceAfter=6, spaceBefore=10, fontName=font_name)
    style_heading3 = ParagraphStyle('heading3', parent=styles['Heading3'], fontSize=10, spaceAfter=4, spaceBefore=8, fontName=font_name)
    style_paragraph = ParagraphStyle('paragraph', parent=styles['Normal'], fontSize=10, spaceAfter=6, alignment=4, firstLineIndent=20, fontName=font_name)
    style_list_item = ParagraphStyle('list_item', parent=styles['Normal'], fontSize=10, spaceAfter=4, leftIndent=20, firstLineIndent=-10, fontName=font_name)
    style_quote = ParagraphStyle('quote', parent=styles['Normal'], fontSize=10, spaceAfter=6, leftIndent=30, rightIndent=30, fontName=font_name)
    
    story = []
    
    # Logo/Brasão centralizado
    logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
        story.append(Spacer(1, 6))

    # Cabeçalho institucional (igual aos quadros)
    cabecalho = [
        "GOVERNO DO ESTADO DO PIAUÍ",
        "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
    ]
    
    # Determinar o tipo de comissão baseado no campo tipo
    if ata.sessao.comissao.tipo == 'CPO':
        tipo_comissao = "COMISSÃO DE PROMOÇÕES DE OFICIAIS - CBMEPI-PI"
    else:
        tipo_comissao = "COMISSÃO DE PROMOÇÕES DE PRAÇAS - CBMEPI-PI"
    
    cabecalho.extend([
        tipo_comissao,
        "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ])
    
    for linha in cabecalho:
        story.append(Paragraph(linha, style_center))
    story.append(Spacer(1, 10))
    
    # Título centralizado e sublinhado (mesma visualização do HTML)
    if ata.sessao.comissao.tipo == 'CPO':
        tipo_comissao = "ATA DA REUNIÃO DA COMISSÃO DE PROMOÇÃO DE OFICIAIS DO CBMEPI"
    elif ata.sessao.comissao.tipo == 'CPP':
        tipo_comissao = "ATA DA REUNIÃO DA COMISSÃO DE PROMOÇÃO DE PRAÇAS DO CBMEPI"
    else:
        tipo_comissao = "ATA DA REUNIÃO DA COMISSÃO DE PROMOÇÃO DO CBMEPI"
    
    titulo = f'<u>{tipo_comissao}</u>'
    story.append(Paragraph(titulo, style_title))
    story.append(Spacer(1, 56.7))  # 2cm de espaçamento após o título
    
    # Conteúdo da ata (mantendo HTML do CKEditor, mas limpo para ReportLab)
    style_html = ParagraphStyle('html', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY, spaceAfter=8, leading=16, fontName=font_name)
    
    # Função para limpar HTML (exatamente como na view original)
    def clean_html_for_reportlab(html_content):
        if not html_content:
            return ""
        
        # Remover tags HTML problemáticas para ReportLab
        import re
        # Remover tags de estilo e script
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        
        # Converter tags HTML para formato ReportLab
        html_content = html_content.replace('<p>', '').replace('</p>', '<br/>')
        html_content = html_content.replace('<br>', '<br/>').replace('<br/>', '<br/>')
        html_content = html_content.replace('<strong>', '<b>').replace('</strong>', '</b>')
        html_content = html_content.replace('<em>', '<i>').replace('</em>', '</i>')
        
        # Remover outras tags HTML não suportadas
        html_content = re.sub(r'<[^>]*>', '', html_content)
        
        # Decodificar entidades HTML
        html_content = unescape(html_content)
        
        return html_content
    
    conteudo_limpo = clean_html_for_reportlab(ata.conteudo)
    
    try:
        story.append(Paragraph(conteudo_limpo, style_html))
    except Exception as e:
        print(f"Erro ao processar HTML da ata: {str(e)}")
        import re
        texto_simples = re.sub(r'<[^>]+>', '', ata.conteudo or '')
        texto_simples = unescape(texto_simples)
        story.append(Paragraph(texto_simples, style_html))
    
    story.append(Spacer(1, 40))
    
    # Data da sessão centralizada após o conteúdo (sistema automático)
    if ata.sessao.data_sessao:
        # Converter data para extenso
        from datetime import datetime
        data_sessao = ata.sessao.data_sessao
        
        # Mapeamento de meses
        meses = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        dia = data_sessao.day
        mes = meses[data_sessao.month]
        ano = data_sessao.year
        
        # Formatar data por extenso
        data_extenso = f"Teresina, {dia} de {mes} de {ano}"
        story.append(Paragraph(f"<center><b>{data_extenso}</b></center>", style_center))
    
    story.append(Spacer(1, 30))
    
    # Assinaturas manuais
    story.append(Spacer(1, 15))
    
    assinaturas = ata.assinaturas.select_related('membro__militar').order_by('data_assinatura')
    if assinaturas.exists():
        for assinatura in assinaturas:
            # Função para obter a abreviação correta do quadro
            def get_quadro_abreviado(quadro):
                if quadro == 'Complementar':
                    return 'QOBM/C'
                elif quadro == 'Combatente':
                    return 'QOBM/Comb.'
                elif quadro == 'Engenheiro':
                    return 'QOBM/E'
                elif quadro == 'Saúde':
                    return 'QOBM/S'
                else:
                    return quadro
            
            # Nome, posto e quadro na mesma linha
            quadro_abreviado = get_quadro_abreviado(assinatura.membro.militar.get_quadro_display())
            nome_posto_quadro = f"{assinatura.membro.militar.nome_completo} - {assinatura.membro.militar.get_posto_graduacao_display()} {quadro_abreviado}"
            story.append(Paragraph(f"<center>{nome_posto_quadro}</center>", style_center))
            
            # Tipo de membro e função
            tipo_membro = assinatura.membro.get_tipo_display()
            cargo_membro = assinatura.membro.cargo.nome if assinatura.membro.cargo else ""
            if cargo_membro:
                story.append(Paragraph(f"<center>{tipo_membro} - {cargo_membro}</center>", style_center))
            else:
                story.append(Paragraph(f"<center>{tipo_membro}</center>", style_center))
            
            if assinatura.observacoes:
                story.append(Paragraph(f"Obs: {assinatura.observacoes}", style_signature))
            story.append(Spacer(1, 10))
    
    # Rodapé com Assinaturas Eletrônicas e QR Code
    story.append(Spacer(1, 40))
    
    # Buscar todas as assinaturas válidas da ata (da mais recente para a mais antiga)
    assinaturas_eletronicas = ata.assinaturas.filter(assinado_por__isnull=False).order_by('-data_assinatura')
    
    if assinaturas_eletronicas.exists():
        for i, assinatura_eletronica in enumerate(assinaturas_eletronicas):
            # Informações de assinatura eletrônica
            nome_assinante = assinatura_eletronica.assinado_por.get_full_name() or assinatura_eletronica.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
            
            from django.utils import timezone
            agora = timezone.localtime(assinatura_eletronica.data_assinatura)
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M')
            
            # Função para obter a abreviação correta do quadro
            def get_quadro_abreviado(quadro):
                if quadro == 'Complementar':
                    return 'QOBM/C'
                elif quadro == 'Combatente':
                    return 'QOBM/Comb.'
                elif quadro == 'Engenheiro':
                    return 'QOBM/E'
                elif quadro == 'Saúde':
                    return 'QOBM/S'
                else:
                    return quadro
            
            # Nome, posto e quadro do militar
            quadro_abreviado = get_quadro_abreviado(assinatura_eletronica.membro.militar.get_quadro_display())
            nome_posto_quadro = f"{assinatura_eletronica.membro.militar.nome_completo} - {assinatura_eletronica.membro.militar.get_posto_graduacao_display()} {quadro_abreviado}"
            
            # Obter a função da assinatura (que foi capturada durante a assinatura)
            funcao_atual = assinatura_eletronica.funcao_assinatura or 'Usuário do Sistema'
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_posto_quadro} - {funcao_atual}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[2*cm, 14*cm])
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
    else:
        # Se não houver assinaturas eletrônicas, mostrar apenas documento gerado pelo usuário logado
        from django.utils import timezone
        agora = timezone.localtime(timezone.now())
        nome_usuario = "Usuário do Sistema"  # Como não temos request, usar padrão
        data_formatada = agora.strftime('%d/%m/%Y')
        hora_formatada = agora.strftime('%H:%M')
        texto_geracao = f"Documento gerado pelo usuário {nome_usuario} em {data_formatada}, às {hora_formatada}."
        story.append(Paragraph(texto_geracao, style_small))
    
    # QR Code para conferência de veracidade
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Gerar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer 