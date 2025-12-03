"""
Funções para geração de PDFs de entradas, saídas e itens do almoxarifado
Seguindo o padrão de cupom fiscal usado para veículos
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Prefetch
from io import BytesIO
import os
import pytz
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
import qrcode
from django.utils import timezone as django_timezone
from decimal import Decimal

from .models import (
    EntradaAlmoxarifado, SaidaAlmoxarifado, ProdutoAlmoxarifado,
    EntradaAlmoxarifadoProduto, SaidaAlmoxarifadoProduto
)
from .utils import gerar_autenticador_veracidade, criar_rodape_sistema_pdf
from .permissoes_sistema import tem_permissao


def _obter_om_item(item):
    """Obtém a OM (Organização Militar) de um item"""
    if item.sub_unidade:
        return item.sub_unidade
    elif item.unidade:
        return item.unidade
    elif item.grande_comando:
        return item.grande_comando
    elif item.orgao:
        return item.orgao
    return None


def _obter_om_entrada(entrada):
    """Obtém a OM de destino de uma entrada"""
    if entrada.sub_unidade_destino:
        return entrada.sub_unidade_destino
    elif entrada.unidade_destino:
        return entrada.unidade_destino
    elif entrada.grande_comando_destino:
        return entrada.grande_comando_destino
    elif entrada.orgao_destino:
        return entrada.orgao_destino
    # Se não houver destino, verificar no primeiro produto
    if entrada.produtos_entrada.exists():
        produto = entrada.produtos_entrada.first().produto
        return _obter_om_item(produto)
    elif entrada.produto:
        return _obter_om_item(entrada.produto)
    return None


def _obter_om_saida(saida):
    """Obtém a OM de destino de uma saída"""
    if saida.sub_unidade_destino:
        return saida.sub_unidade_destino
    elif saida.unidade_destino:
        return saida.unidade_destino
    elif saida.grande_comando_destino:
        return saida.grande_comando_destino
    elif saida.orgao_destino:
        return saida.orgao_destino
    # Se não houver destino, verificar no primeiro produto
    if saida.produtos_saida.exists():
        produto = saida.produtos_saida.first().produto
        return _obter_om_item(produto)
    elif saida.produto:
        return _obter_om_item(saida.produto)
    return None


@login_required
def entrada_almoxarifado_pdf(request, pk):
    """
    Gera PDF da entrada de almoxarifado no formato de cupom fiscal
    """
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
        return HttpResponse('Permissão negada', status=403)
    
    entrada = get_object_or_404(
        EntradaAlmoxarifado.objects.select_related(
            'produto', 'responsavel', 'criado_por',
            'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
        ).prefetch_related(
            Prefetch(
                'produtos_entrada',
                queryset=EntradaAlmoxarifadoProduto.objects.select_related('produto')
            )
        ),
        pk=pk
    )
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        # Formato A4 padrão - seguindo padrão de férias
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos - seguindo padrão de férias
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        style_table_header = ParagraphStyle('table_header', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', alignment=1, textColor=colors.white)
        style_table_cell = ParagraphStyle('table_cell', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=0)
        style_table_cell_center = ParagraphStyle('table_cell_center', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=1)
        
        # Logo/Brasão centralizado - seguindo padrão de férias
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional - seguindo padrão do sistema
        # Usar a função ativa do usuário para determinar a OM (padrão do sistema)
        from .permissoes_hierarquicas import obter_funcao_militar_ativa
        funcao_usuario = obter_funcao_militar_ativa(request.user)
        
        local_geracao = "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
        endereco_organizacao = None
        
        if funcao_usuario:
            # Determinar organização baseada na função do usuário conforme tipo de acesso
            # Prioridade: sub_unidade > unidade > grande_comando > orgao
            if funcao_usuario.sub_unidade:
                local_geracao = funcao_usuario.sub_unidade.nome.upper()
                endereco_organizacao = funcao_usuario.sub_unidade.endereco
            elif funcao_usuario.unidade:
                local_geracao = funcao_usuario.unidade.nome.upper()
                endereco_organizacao = funcao_usuario.unidade.endereco
            elif funcao_usuario.grande_comando:
                local_geracao = funcao_usuario.grande_comando.nome.upper()
                endereco_organizacao = funcao_usuario.grande_comando.endereco
            elif funcao_usuario.orgao:
                local_geracao = funcao_usuario.orgao.nome.upper()
                endereco_organizacao = funcao_usuario.orgao.endereco
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            local_geracao
        ]
        
        # Adicionar endereço se existir
        if endereco_organizacao:
            cabecalho.append(endereco_organizacao)
        
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal - seguindo padrão de férias
        story.append(Paragraph("<u>COMPROVANTE DE ENTRADA DE ALMOXARIFADO</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Converter data/hora para timezone local
        from datetime import datetime, date
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        # Verificar se é date ou datetime
        if isinstance(entrada.data_entrada, date) and not isinstance(entrada.data_entrada, datetime):
            # É apenas date, sem hora
            data_hora_formatada = entrada.data_entrada.strftime("%d/%m/%Y")
        else:
            # É datetime
            if django_timezone.is_aware(entrada.data_entrada):
                data_entrada_local = entrada.data_entrada.astimezone(brasilia_tz)
            else:
                data_entrada_local = brasilia_tz.localize(entrada.data_entrada)
            data_hora_formatada = data_entrada_local.strftime("%d/%m/%Y %H:%M")
        
        # Origem (de onde veio)
        origem_texto = ""
        if entrada.sub_unidade_origem:
            origem_texto = str(entrada.sub_unidade_origem)
        elif entrada.unidade_origem:
            origem_texto = str(entrada.unidade_origem)
        elif entrada.grande_comando_origem:
            origem_texto = str(entrada.grande_comando_origem)
        elif entrada.orgao_origem:
            origem_texto = str(entrada.orgao_origem)
        
        # Destino (para onde foi)
        destino_texto = ""
        if entrada.sub_unidade_destino:
            destino_texto = str(entrada.sub_unidade_destino)
        elif entrada.unidade_destino:
            destino_texto = str(entrada.unidade_destino)
        elif entrada.grande_comando_destino:
            destino_texto = str(entrada.grande_comando_destino)
        elif entrada.orgao_destino:
            destino_texto = str(entrada.orgao_destino)
        elif entrada.produtos_entrada.exists():
            # Se não houver destino, verificar no primeiro produto da entrada
            produto = entrada.produtos_entrada.first().produto
            if produto.sub_unidade:
                destino_texto = str(produto.sub_unidade)
            elif produto.unidade:
                destino_texto = str(produto.unidade)
            elif produto.grande_comando:
                destino_texto = str(produto.grande_comando)
            elif produto.orgao:
                destino_texto = str(produto.orgao)
        elif entrada.produto:
            # Fallback para entrada legada
            if entrada.produto.sub_unidade:
                destino_texto = str(entrada.produto.sub_unidade)
            elif entrada.produto.unidade:
                destino_texto = str(entrada.produto.unidade)
            elif entrada.produto.grande_comando:
                destino_texto = str(entrada.produto.grande_comando)
            elif entrada.produto.orgao:
                destino_texto = str(entrada.produto.orgao)
        
        # Nome do responsável (sem posto, apenas nome)
        nome_responsavel = ""
        if entrada.responsavel:
            nome_responsavel = entrada.responsavel.nome_completo
        
        # Criar layout moderno com cards/tabela para dados básicos
        largura_disponivel_dados = A4[0] - (1.5*cm * 2)
        
        # Criar dados em formato de grid moderno (2 colunas)
        dados_grid = []
        
        # Linha 1: Responsável (se houver) e Número da Entrada
        linha1_col1 = Paragraph("", style_table_cell)
        if nome_responsavel:
            linha1_col1 = Paragraph(f"<b>Responsável:</b><br/>{nome_responsavel}", style_table_cell)
        dados_grid.append([
            linha1_col1,
            Paragraph(f"<b>Número da Entrada:</b><br/>{entrada.pk}", style_table_cell)
        ])
        
        # Linha 2: Data/Hora e Tipo de Entrada
        dados_grid.append([
            Paragraph(f"<b>Data/Hora:</b><br/>{data_hora_formatada}", style_table_cell),
            Paragraph(f"<b>Tipo de Entrada:</b><br/>{entrada.get_tipo_entrada_display()}", style_table_cell)
        ])
        
        # Linha 3: Origem (se houver)
        if origem_texto:
            dados_grid.append([
                Paragraph(f"<b>Origem:</b><br/>{origem_texto}", style_table_cell),
                Paragraph("", style_table_cell)
            ])
        
        # Linha 4: Destino (se houver)
        if destino_texto:
            dados_grid.append([
                Paragraph(f"<b>Destino:</b><br/>{destino_texto}", style_table_cell),
                Paragraph("", style_table_cell)
            ])
        
        # Criar tabela moderna com estilo de cards
        dados_table = Table(dados_grid, colWidths=[largura_disponivel_dados * 0.5, largura_disponivel_dados * 0.5])
        dados_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
            ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.HexColor('#e9ecef')),
        ]))
        
        story.append(dados_table)
        story.append(Spacer(1, 15))
        
        # Tabela de produtos
        # Se for COMPRA, adicionar colunas de valor
        if entrada.tipo_entrada == 'COMPRA':
            produtos_data = [
                ['Código', 'Descrição', 'Tamanho', 'Quantidade', 'Unidade', 'Valor Unitário', 'Valor Total']
            ]
        else:
            produtos_data = [
                ['Código', 'Descrição', 'Tamanho', 'Quantidade', 'Unidade']
            ]
        
        total_valor_compra = Decimal('0')
        if entrada.produtos_entrada.exists():
            for produto_entrada in entrada.produtos_entrada.all():
                tamanho = produto_entrada.produto.tamanho if produto_entrada.produto.tamanho else '-'
                qtd_formatada = produto_entrada.produto.formatar_quantidade_unidade(produto_entrada.quantidade)
                # Separar quantidade e unidade
                partes = qtd_formatada.split(' ', 1)
                quantidade_num = partes[0] if partes else qtd_formatada
                unidade = partes[1] if len(partes) > 1 else produto_entrada.produto.get_unidade_medida_display()
                
                if entrada.tipo_entrada == 'COMPRA':
                    # Formatar valores em BRL (formato brasileiro: R$ 1.234,56)
                    if produto_entrada.valor_unitario:
                        valor_unitario_str = f"{produto_entrada.valor_unitario:,.2f}"
                        valor_unitario = f"R$ {valor_unitario_str.replace(',', 'X').replace('.', ',').replace('X', '.')}"
                    else:
                        valor_unitario = '-'
                    
                    if produto_entrada.valor_total:
                        valor_total_str = f"{produto_entrada.valor_total:,.2f}"
                        valor_total = f"R$ {valor_total_str.replace(',', 'X').replace('.', ',').replace('X', '.')}"
                        total_valor_compra += produto_entrada.valor_total
                    else:
                        valor_total = '-'
                    
                    produtos_data.append([
                        produto_entrada.produto.codigo,
                        produto_entrada.produto.descricao[:50],  # Limitar tamanho
                        tamanho,
                        quantidade_num,
                        unidade,
                        valor_unitario,
                        valor_total
                    ])
                else:
                    produtos_data.append([
                        produto_entrada.produto.codigo,
                        produto_entrada.produto.descricao[:50],  # Limitar tamanho
                        tamanho,
                        quantidade_num,
                        unidade
                    ])
        
        # Adicionar linha de total se for COMPRA
        tem_linha_total = False
        if entrada.tipo_entrada == 'COMPRA' and entrada.produtos_entrada.exists() and total_valor_compra > 0:
            total_valor_str = f"{total_valor_compra:,.2f}"
            total_valor_formatado = f"R$ {total_valor_str.replace(',', 'X').replace('.', ',').replace('X', '.')}"
            produtos_data.append([
                '',
                'TOTAL',
                '',
                '',
                '',
                '',
                total_valor_formatado
            ])
            tem_linha_total = True
        
        if not entrada.produtos_entrada.exists() and entrada.produto:
            tamanho = entrada.produto.tamanho if entrada.produto.tamanho else '-'
            qtd_formatada = entrada.produto.formatar_quantidade_unidade(entrada.quantidade)
            # Separar quantidade e unidade
            partes = qtd_formatada.split(' ', 1)
            quantidade_num = partes[0] if partes else qtd_formatada
            unidade = partes[1] if len(partes) > 1 else entrada.produto.get_unidade_medida_display()
            
            produtos_data.append([
                entrada.produto.codigo,
                entrada.produto.descricao[:50],  # Limitar tamanho
                tamanho,
                quantidade_num,
                unidade
            ])
        
        # Criar tabela de produtos
        largura_disponivel = A4[0] - (1.5*cm * 2)
        if entrada.tipo_entrada == 'COMPRA':
            col_widths = [
                largura_disponivel * 0.10,  # Código
                largura_disponivel * 0.25,  # Descrição
                largura_disponivel * 0.10,  # Tamanho
                largura_disponivel * 0.10,  # Quantidade
                largura_disponivel * 0.10,  # Unidade
                largura_disponivel * 0.12,  # Valor Unitário
                largura_disponivel * 0.13   # Valor Total
            ]
        else:
            col_widths = [
                largura_disponivel * 0.15,  # Código
                largura_disponivel * 0.40,  # Descrição
                largura_disponivel * 0.15,  # Tamanho
                largura_disponivel * 0.15,  # Quantidade
                largura_disponivel * 0.15   # Unidade
            ]
        
        produtos_table = Table(produtos_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da tabela
        estilo_tabela = [
            # Cabeçalho
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, 0), 4),
            ('RIGHTPADDING', (0, 0), (-1, 0), 4),
            # Dados - alinhamento específico por coluna
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Código - centro
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),     # Descrição - esquerda
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),   # Tamanho - centro
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),   # Quantidade - centro
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 1), (-1, -1), 4),
            ('RIGHTPADDING', (0, 1), (-1, -1), 4),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]
        
        # Se for COMPRA, adicionar alinhamento para colunas de valor
        if entrada.tipo_entrada == 'COMPRA':
            estilo_tabela.extend([
                ('ALIGN', (4, 1), (4, -1), 'CENTER'),   # Unidade - centro
                ('ALIGN', (5, 1), (5, -1), 'RIGHT'),    # Valor Unitário - direita
                ('ALIGN', (6, 1), (6, -1), 'RIGHT'),    # Valor Total - direita
            ])
            
            # Estilo para linha de total (última linha) - apenas se houver linha de total
            if len(produtos_data) > 1 and tem_linha_total:
                ultima_linha = len(produtos_data) - 1
                # Verificar se a última linha é realmente a linha de total
                if ultima_linha > 0 and len(produtos_data[ultima_linha]) > 1 and produtos_data[ultima_linha][1] == 'TOTAL':
                    estilo_tabela.extend([
                        ('FONTNAME', (1, ultima_linha), (1, ultima_linha), 'Helvetica-Bold'),
                        ('FONTNAME', (6, ultima_linha), (6, ultima_linha), 'Helvetica-Bold'),
                        ('BACKGROUND', (1, ultima_linha), (6, ultima_linha), colors.lightgrey),
                    ])
        else:
            estilo_tabela.append(('ALIGN', (4, 1), (4, -1), 'CENTER'))  # Unidade - centro
        
        # Linhas alternadas (exceto cabeçalho e linha de total)
        if entrada.tipo_entrada == 'COMPRA' and len(produtos_data) > 2:
            # Excluir cabeçalho (linha 0) e linha de total (última linha)
            # Aplicar linhas alternadas apenas nas linhas de dados (1 até penúltima)
            num_linhas_dados = len(produtos_data) - 2  # Excluir cabeçalho e linha de total
            if num_linhas_dados > 0:
                estilo_tabela.append(('ROWBACKGROUNDS', (0, 1), (-1, len(produtos_data) - 2), [colors.white, colors.HexColor('#f8f9fa')]))
        elif len(produtos_data) > 1:
            estilo_tabela.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]))
        
        produtos_table.setStyle(TableStyle(estilo_tabela))
        
        story.append(produtos_table)
        story.append(Spacer(1, 10))
        
        # Informações do fornecedor (se houver)
        if entrada.fornecedor or entrada.cnpj_fornecedor or entrada.nota_fiscal:
            fornecedor_texto = ""
            if entrada.fornecedor:
                fornecedor_texto += f"<b>Fornecedor:</b> {entrada.fornecedor}<br/>"
            if entrada.cnpj_fornecedor:
                fornecedor_texto += f"<b>CNPJ:</b> {entrada.cnpj_fornecedor}<br/>"
            if entrada.endereco_fornecedor:
                fornecedor_texto += f"<b>Endereço:</b> {entrada.endereco_fornecedor}<br/>"
            if entrada.nota_fiscal:
                fornecedor_texto += f"<b>Nota Fiscal:</b> {entrada.nota_fiscal}<br/>"
            if entrada.tipo_entrada == 'DOACAO':
                if entrada.numero_processo:
                    fornecedor_texto += f"<b>Processo:</b> {entrada.numero_processo}<br/>"
                if entrada.numero_convenio:
                    fornecedor_texto += f"<b>Convênio:</b> {entrada.numero_convenio}<br/>"
            if fornecedor_texto:
                story.append(Paragraph(fornecedor_texto, style_normal))
        
        # Responsável
        if entrada.responsavel:
            responsavel_texto = f"<b>Responsável:</b> {entrada.responsavel.get_posto_graduacao_display()} {entrada.responsavel.nome_completo}"
            story.append(Paragraph(responsavel_texto, style_normal))
        
        # Observações
        if entrada.observacoes:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>Observações:</b> {entrada.observacoes}", style_normal))
        
        story.append(Spacer(1, 20))
        
        # Cidade e Data por extenso (centralizada) - seguindo padrão de férias
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
        data_atual = django_timezone.now().astimezone(brasilia_tz) if django_timezone.is_aware(django_timezone.now()) else brasilia_tz.localize(django_timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
        
        # Assinatura física de quem registrou
        try:
            # Usar responsável se existir, caso contrário usar criado_por
            assinante = None
            funcao_assinante = ""
            
            if entrada.responsavel:
                assinante = entrada.responsavel
            elif entrada.criado_por and hasattr(entrada.criado_por, 'militar'):
                assinante = entrada.criado_por.militar
            
            if assinante:
                nome_posto = f"{assinante.nome_completo} - {assinante.get_posto_graduacao_display()} BM"
                
                # Obter função do assinante
                from .permissoes_hierarquicas import obter_funcao_militar_ativa
                funcao_obj = obter_funcao_militar_ativa(entrada.criado_por if entrada.criado_por else request.user)
                if funcao_obj and funcao_obj.funcao_militar:
                    funcao_assinante = funcao_obj.funcao_militar.nome
                else:
                    funcao_assinante = "Responsável pela Entrada"
                
                # Adicionar espaço para assinatura física
                story.append(Spacer(1, 1*cm))
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                
                # 2ª linha: Função
                story.append(Paragraph(funcao_assinante, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo - seguindo padrão de férias
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Obter função do usuário logado
                from .permissoes_hierarquicas import obter_funcao_militar_ativa
                funcao_obj = obter_funcao_militar_ativa(request.user)
                if funcao_obj and funcao_obj.funcao_militar:
                    funcao_display = funcao_obj.funcao_militar.nome
                else:
                    funcao_display = "Usuário do Sistema"
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = "Usuário do Sistema"
            
            # Data e hora da assinatura
            agora = django_timezone.now().astimezone(brasilia_tz) if django_timezone.is_aware(django_timezone.now()) else brasilia_tz.localize(django_timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M:%S')
            
            texto_assinatura = (
                f"Documento assinado eletronicamente por {nome_posto_quadro}, em {data_formatada} {hora_formatada}, "
                f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
            )
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            largura_disponivel_assinatura = A4[0] - (1.5*cm * 2)
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[3*cm, largura_disponivel_assinatura - 3*cm])
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
        
        # Rodapé com QR Code para verificação de autenticidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador de veracidade
        from .utils import gerar_autenticador_veracidade
        
        # Criar um objeto fake para a entrada (para o autenticador)
        class EntradaFake:
            def __init__(self, entrada):
                self.id = f"entrada_almoxarifado_{entrada.pk}"
                self.pk = entrada.pk
                self.tipo_documento = 'entrada_almoxarifado'
        
        entrada_fake = EntradaFake(entrada)
        autenticador = gerar_autenticador_veracidade(entrada_fake, request, tipo_documento='entrada_almoxarifado')
        
        # Tabela do rodapé: QR + Texto de autenticação
        largura_disponivel_qr = A4[0] - (1.5*cm * 2)
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[2*cm, largura_disponivel_qr - 2*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
        ]))
        
        story.append(rodape_table)
        
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="entrada_almoxarifado_{entrada.pk}.pdf"'
        
        return response
        
    except Exception as e:
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Entrada</title>
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
                <p><strong>Ocorreu um erro ao gerar o PDF da entrada.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <p><small>{str(e)}</small></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def saida_almoxarifado_pdf(request, pk):
    """
    Gera PDF da saída de almoxarifado no formato de cupom fiscal
    """
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
        return HttpResponse('Permissão negada', status=403)
    
    # Não incluir requisicao_origem no select_related pois pode não existir
    # O campo será acessado de forma segura usando getattr mais abaixo
    saida = get_object_or_404(
        SaidaAlmoxarifado.objects.select_related(
            'produto', 'requisitante', 'responsavel_entrega', 'criado_por',
            'orgao_origem', 'grande_comando_origem', 'unidade_origem', 'sub_unidade_origem',
            'orgao_destino', 'grande_comando_destino', 'unidade_destino', 'sub_unidade_destino'
        ).prefetch_related(
            Prefetch(
                'produtos_saida',
                queryset=SaidaAlmoxarifadoProduto.objects.select_related('produto')
            )
        ),
        pk=pk
    )
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        # Formato A4 padrão - seguindo padrão de férias
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos - seguindo padrão de férias
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        style_center_small = ParagraphStyle('center_small', parent=styles['Normal'], fontSize=9, alignment=1, spaceAfter=5)
        style_table_header = ParagraphStyle('table_header', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', alignment=1, textColor=colors.white)
        style_table_cell = ParagraphStyle('table_cell', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=0)
        style_table_cell_center = ParagraphStyle('table_cell_center', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=1)
        
        # Logo/Brasão centralizado - seguindo padrão de férias
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional - seguindo padrão do sistema
        # Usar a função ativa do usuário para determinar a OM (padrão do sistema)
        from .permissoes_hierarquicas import obter_funcao_militar_ativa
        funcao_usuario = obter_funcao_militar_ativa(request.user)
        
        local_geracao = "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ"
        endereco_organizacao = None
        
        if funcao_usuario:
            # Determinar organização baseada na função do usuário conforme tipo de acesso
            # Prioridade: sub_unidade > unidade > grande_comando > orgao
            if funcao_usuario.sub_unidade:
                local_geracao = funcao_usuario.sub_unidade.nome.upper()
                endereco_organizacao = funcao_usuario.sub_unidade.endereco
            elif funcao_usuario.unidade:
                local_geracao = funcao_usuario.unidade.nome.upper()
                endereco_organizacao = funcao_usuario.unidade.endereco
            elif funcao_usuario.grande_comando:
                local_geracao = funcao_usuario.grande_comando.nome.upper()
                endereco_organizacao = funcao_usuario.grande_comando.endereco
            elif funcao_usuario.orgao:
                local_geracao = funcao_usuario.orgao.nome.upper()
                endereco_organizacao = funcao_usuario.orgao.endereco
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            local_geracao
        ]
        
        # Adicionar endereço se existir
        if endereco_organizacao:
            cabecalho.append(endereco_organizacao)
        
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal - seguindo padrão de férias
        story.append(Paragraph("<u>COMPROVANTE DE SAÍDA DE ALMOXARIFADO</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Converter data/hora para timezone local
        from datetime import datetime, date
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        # Verificar se é date ou datetime
        if isinstance(saida.data_saida, date) and not isinstance(saida.data_saida, datetime):
            # É apenas date, sem hora
            data_hora_formatada = saida.data_saida.strftime("%d/%m/%Y")
        else:
            # É datetime
            if django_timezone.is_aware(saida.data_saida):
                data_saida_local = saida.data_saida.astimezone(brasilia_tz)
            else:
                data_saida_local = brasilia_tz.localize(saida.data_saida)
            data_hora_formatada = data_saida_local.strftime("%d/%m/%Y %H:%M")
        
        # Origem (de onde saiu)
        origem_texto = ""
        if saida.sub_unidade_origem:
            origem_texto = str(saida.sub_unidade_origem)
        elif saida.unidade_origem:
            origem_texto = str(saida.unidade_origem)
        elif saida.grande_comando_origem:
            origem_texto = str(saida.grande_comando_origem)
        elif saida.orgao_origem:
            origem_texto = str(saida.orgao_origem)
        else:
            # Tentar obter origem da requisição se existir (campo relacionado reverso)
            # Usar query reversa de forma segura
            try:
                from .models import RequisicaoAlmoxarifado
                requisicao_origem = RequisicaoAlmoxarifado.objects.filter(transferencia_criada=saida).first()
                if requisicao_origem:
                    if requisicao_origem.sub_unidade_requisitante:
                        origem_texto = str(requisicao_origem.sub_unidade_requisitante)
                    elif requisicao_origem.unidade_requisitante:
                        origem_texto = str(requisicao_origem.unidade_requisitante)
                    elif requisicao_origem.grande_comando_requisitante:
                        origem_texto = str(requisicao_origem.grande_comando_requisitante)
                    elif requisicao_origem.orgao_requisitante:
                        origem_texto = str(requisicao_origem.orgao_requisitante)
            except (AttributeError, Exception):
                pass
        
        # Destino (para onde foi)
        destino_texto = ""
        if saida.sub_unidade_destino:
            destino_texto = str(saida.sub_unidade_destino)
        elif saida.unidade_destino:
            destino_texto = str(saida.unidade_destino)
        elif saida.grande_comando_destino:
            destino_texto = str(saida.grande_comando_destino)
        elif saida.orgao_destino:
            destino_texto = str(saida.orgao_destino)
        else:
            # Tentar obter destino da requisição se existir (campo relacionado reverso)
            # Usar query reversa de forma segura
            try:
                from .models import RequisicaoAlmoxarifado
                requisicao_origem = RequisicaoAlmoxarifado.objects.filter(transferencia_criada=saida).first()
                if requisicao_origem:
                    if requisicao_origem.sub_unidade_requisitada:
                        destino_texto = str(requisicao_origem.sub_unidade_requisitada)
                    elif requisicao_origem.unidade_requisitada:
                        destino_texto = str(requisicao_origem.unidade_requisitada)
                    elif requisicao_origem.grande_comando_requisitada:
                        destino_texto = str(requisicao_origem.grande_comando_requisitada)
                    elif requisicao_origem.orgao_requisitada:
                        destino_texto = str(requisicao_origem.orgao_requisitada)
            except (AttributeError, Exception):
                pass
        
        # Nome do requisitante (sem posto, apenas nome)
        nome_requisitante = ""
        if saida.requisitante:
            nome_requisitante = saida.requisitante.nome_completo
        
        # Criar layout moderno com cards/tabela para dados básicos
        largura_disponivel_dados = A4[0] - (1.5*cm * 2)
        
        # Criar dados em formato de grid moderno (2 colunas)
        dados_grid = []
        
        # Linha 1: Requisitante (se houver) e Número da Saída
        linha1_col1 = Paragraph("", style_table_cell)
        if nome_requisitante:
            linha1_col1 = Paragraph(f"<b>Requisitante:</b><br/>{nome_requisitante}", style_table_cell)
        dados_grid.append([
            linha1_col1,
            Paragraph(f"<b>Número da Saída:</b><br/>{saida.pk}", style_table_cell)
        ])
        
        # Linha 2: Data/Hora e Tipo de Saída
        dados_grid.append([
            Paragraph(f"<b>Data/Hora:</b><br/>{data_hora_formatada}", style_table_cell),
            Paragraph(f"<b>Tipo de Saída:</b><br/>{saida.get_tipo_saida_display()}", style_table_cell)
        ])
        
        # Linha 3: Origem (se houver)
        if origem_texto:
            dados_grid.append([
                Paragraph(f"<b>Origem:</b><br/>{origem_texto}", style_table_cell),
                Paragraph("", style_table_cell)
            ])
        
        # Linha 4: Destino (se houver)
        if destino_texto:
            dados_grid.append([
                Paragraph(f"<b>Destino:</b><br/>{destino_texto}", style_table_cell),
                Paragraph("", style_table_cell)
            ])
        
        # Criar tabela moderna com estilo de cards
        dados_table = Table(dados_grid, colWidths=[largura_disponivel_dados * 0.5, largura_disponivel_dados * 0.5])
        dados_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
            ('LINEAFTER', (0, 0), (0, -1), 0.5, colors.HexColor('#e9ecef')),
        ]))
        
        story.append(dados_table)
        story.append(Spacer(1, 15))
        
        # Tabela de produtos
        produtos_data = [
            ['Código', 'Descrição', 'Tamanho', 'Quantidade', 'Unidade']
        ]
        
        if saida.produtos_saida.exists():
            for produto_saida in saida.produtos_saida.all():
                tamanho = produto_saida.produto.tamanho if produto_saida.produto.tamanho else '-'
                qtd_formatada = produto_saida.produto.formatar_quantidade_unidade(produto_saida.quantidade)
                # Separar quantidade e unidade
                partes = qtd_formatada.split(' ', 1)
                quantidade_num = partes[0] if partes else qtd_formatada
                unidade = partes[1] if len(partes) > 1 else produto_saida.produto.get_unidade_medida_display()
                
                produtos_data.append([
                    produto_saida.produto.codigo,
                    produto_saida.produto.descricao[:50],  # Limitar tamanho
                    tamanho,
                    quantidade_num,
                    unidade
                ])
        elif saida.produto:
            tamanho = saida.produto.tamanho if saida.produto.tamanho else '-'
            qtd_formatada = saida.produto.formatar_quantidade_unidade(saida.quantidade)
            # Separar quantidade e unidade
            partes = qtd_formatada.split(' ', 1)
            quantidade_num = partes[0] if partes else qtd_formatada
            unidade = partes[1] if len(partes) > 1 else saida.produto.get_unidade_medida_display()
            
            produtos_data.append([
                saida.produto.codigo,
                saida.produto.descricao[:50],  # Limitar tamanho
                tamanho,
                quantidade_num,
                unidade
            ])
        
        # Criar tabela de produtos
        largura_disponivel = A4[0] - (1.5*cm * 2)
        col_widths = [
            largura_disponivel * 0.15,  # Código
            largura_disponivel * 0.40,  # Descrição
            largura_disponivel * 0.15,  # Tamanho
            largura_disponivel * 0.15,  # Quantidade
            largura_disponivel * 0.15   # Unidade
        ]
        
        produtos_table = Table(produtos_data, colWidths=col_widths, repeatRows=1)
        produtos_table.setStyle(TableStyle([
            # Cabeçalho
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True),
            # Linhas alternadas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        story.append(produtos_table)
        story.append(Spacer(1, 10))
        
        # Responsável entrega
        if saida.responsavel_entrega:
            responsavel_texto = f"<b>Responsável pela Entrega:</b> {saida.responsavel_entrega.get_posto_graduacao_display()} {saida.responsavel_entrega.nome_completo}"
            story.append(Paragraph(responsavel_texto, style_normal))
        
        # Observações
        if saida.observacoes:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>Observações:</b> {saida.observacoes}", style_normal))
        
        story.append(Spacer(1, 20))
        
        # Cidade e Data por extenso (centralizada) - seguindo padrão de férias
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
        data_atual = django_timezone.now().astimezone(brasilia_tz) if django_timezone.is_aware(django_timezone.now()) else brasilia_tz.localize(django_timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
        
        # Assinatura física de quem transferiu
        try:
            # Usar responsável pela entrega se existir, caso contrário usar criado_por
            assinante = None
            funcao_assinante = ""
            
            if saida.responsavel_entrega:
                assinante = saida.responsavel_entrega
            elif saida.criado_por and hasattr(saida.criado_por, 'militar'):
                assinante = saida.criado_por.militar
            
            if assinante:
                nome_posto = f"{assinante.nome_completo} - {assinante.get_posto_graduacao_display()} BM"
                
                # Obter função do assinante
                from .permissoes_hierarquicas import obter_funcao_militar_ativa
                funcao_obj = obter_funcao_militar_ativa(saida.criado_por if saida.criado_por else request.user)
                if funcao_obj and funcao_obj.funcao_militar:
                    funcao_assinante = funcao_obj.funcao_militar.nome
                else:
                    funcao_assinante = "Responsável pela Transferência"
                
                # Adicionar espaço para assinatura física
                story.append(Spacer(1, 1*cm))
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                
                # 2ª linha: Função
                story.append(Paragraph(funcao_assinante, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo - seguindo padrão de férias
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Obter função do usuário logado
                from .permissoes_hierarquicas import obter_funcao_militar_ativa
                funcao_obj = obter_funcao_militar_ativa(request.user)
                if funcao_obj and funcao_obj.funcao_militar:
                    funcao_display = funcao_obj.funcao_militar.nome
                else:
                    funcao_display = "Usuário do Sistema"
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = "Usuário do Sistema"
            
            # Data e hora da assinatura
            agora = django_timezone.now().astimezone(brasilia_tz) if django_timezone.is_aware(django_timezone.now()) else brasilia_tz.localize(django_timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M:%S')
            
            texto_assinatura = (
                f"Documento assinado eletronicamente por {nome_posto_quadro}, em {data_formatada} {hora_formatada}, "
                f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
            )
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            largura_disponivel_assinatura = A4[0] - (1.5*cm * 2)
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[3*cm, largura_disponivel_assinatura - 3*cm])
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
        
        # Adicionar assinatura de recebimento se existir
        try:
            from .models import AssinaturaSaidaAlmoxarifado
            assinatura_recebimento = AssinaturaSaidaAlmoxarifado.objects.filter(
                saida=saida,
                tipo_assinatura='RECEBIMENTO'
            ).first()
            
            if assinatura_recebimento:
                story.append(Spacer(1, 20))
                
                # Título da assinatura de recebimento
                story.append(Paragraph("<b>ASSINATURA DE RECEBIMENTO</b>", ParagraphStyle('titulo_recebimento', parent=styles['Normal'], alignment=1, fontSize=12, fontName='Helvetica-Bold', spaceAfter=10)))
                
                # Informações do recebedor
                if assinatura_recebimento.militar:
                    nome_recebedor = f"{assinatura_recebimento.militar.nome_completo} - {assinatura_recebimento.militar.get_posto_graduacao_display()} BM"
                else:
                    nome_recebedor = assinatura_recebimento.assinado_por.get_full_name() or assinatura_recebimento.assinado_por.username
                
                funcao_recebedor = assinatura_recebimento.funcao_assinatura or "Requisitante"
                
                # Data e hora da assinatura de recebimento
                if django_timezone.is_aware(assinatura_recebimento.data_assinatura):
                    data_recebimento = assinatura_recebimento.data_assinatura.astimezone(brasilia_tz)
                else:
                    data_recebimento = brasilia_tz.localize(assinatura_recebimento.data_assinatura)
                
                data_formatada_receb = data_recebimento.strftime('%d/%m/%Y')
                hora_formatada_receb = data_recebimento.strftime('%H:%M:%S')
                
                # Espaço para assinatura física do recebedor
                story.append(Spacer(1, 1*cm))
                
                # Nome e posto do recebedor
                story.append(Paragraph(nome_recebedor, ParagraphStyle('assinatura_recebedor', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                
                # Função do recebedor
                story.append(Paragraph(funcao_recebedor, ParagraphStyle('funcao_recebedor', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
                
                # Assinatura eletrônica de recebimento
                story.append(Spacer(1, 0.5*cm))
                
                texto_assinatura_receb = (
                    f"Material recebido conforme registro acima. Documento assinado eletronicamente por {nome_recebedor}, em {data_formatada_receb} {hora_formatada_receb}, "
                    f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
                )
                
                # Adicionar logo da assinatura eletrônica
                from .utils import obter_caminho_assinatura_eletronica
                logo_path = obter_caminho_assinatura_eletronica()
                
                # Tabela da assinatura de recebimento: Logo + Texto
                largura_disponivel_assinatura_receb = A4[0] - (1.5*cm * 2)
                assinatura_receb_data = [
                    [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura_receb, style_small)]
                ]
                
                assinatura_receb_table = Table(assinatura_receb_data, colWidths=[3*cm, largura_disponivel_assinatura_receb - 3*cm])
                assinatura_receb_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizado
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
                ]))
                
                story.append(assinatura_receb_table)
        except Exception as e:
            # Se houver erro, apenas continuar
            pass
        
        # Rodapé com QR Code para verificação de autenticidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador de veracidade
        from .utils import gerar_autenticador_veracidade
        
        # Criar um objeto fake para a saída (para o autenticador)
        class SaidaFake:
            def __init__(self, saida):
                self.id = f"saida_almoxarifado_{saida.pk}"
                self.pk = saida.pk
                self.tipo_documento = 'saida_almoxarifado'
        
        saida_fake = SaidaFake(saida)
        autenticador = gerar_autenticador_veracidade(saida_fake, request, tipo_documento='saida_almoxarifado')
        
        # Tabela do rodapé: QR + Texto de autenticação
        largura_disponivel_qr = A4[0] - (1.5*cm * 2)
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[2*cm, largura_disponivel_qr - 2*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
        ]))
        
        story.append(rodape_table)
        
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="saida_almoxarifado_{saida.pk}.pdf"'
        
        return response
        
    except Exception as e:
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Saída</title>
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
                <p><strong>Ocorreu um erro ao gerar o PDF da saída.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <p><small>{str(e)}</small></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def produto_almoxarifado_pdf(request, pk):
    """
    Gera PDF moderno do item de almoxarifado com histórico de movimentações
    """
    if not tem_permissao(request.user, 'ALMOXARIFADO', 'VISUALIZAR'):
        return HttpResponse('Permissão negada', status=403)
    
    produto = get_object_or_404(ProdutoAlmoxarifado, pk=pk)
    
    # Buscar movimentações do item (mesma lógica da view detail)
    from django.db.models import Prefetch
    from .models import EntradaAlmoxarifadoProduto, SaidaAlmoxarifadoProduto
    
    entradas_legadas = EntradaAlmoxarifado.objects.filter(
        produto=produto, ativo=True
    ).select_related('responsavel', 'criado_por').order_by('-data_entrada')
    
    entradas_itens = EntradaAlmoxarifado.objects.filter(
        produtos_entrada__produto=produto, ativo=True
    ).select_related('responsavel', 'criado_por').prefetch_related(
        Prefetch('produtos_entrada', queryset=EntradaAlmoxarifadoProduto.objects.filter(produto=produto).select_related('produto'))
    ).distinct().order_by('-data_entrada')
    
    saidas_legadas = SaidaAlmoxarifado.objects.filter(
        produto=produto, ativo=True
    ).select_related('requisitante', 'responsavel_entrega', 'criado_por').order_by('-data_saida')
    
    saidas_itens = SaidaAlmoxarifado.objects.filter(
        produtos_saida__produto=produto, ativo=True
    ).select_related('requisitante', 'responsavel_entrega', 'criado_por').prefetch_related(
        Prefetch('produtos_saida', queryset=SaidaAlmoxarifadoProduto.objects.filter(produto=produto).select_related('produto'))
    ).distinct().order_by('-data_saida')
    
    todas_entradas = list(entradas_legadas) + list(entradas_itens)
    todas_saidas = list(saidas_legadas) + list(saidas_itens)
    
    movimentacoes = []
    for entrada in todas_entradas:
        if entrada.produtos_entrada.exists():
            produto_entrada = entrada.produtos_entrada.filter(produto=produto).first()
            if produto_entrada:
                quantidade = produto_entrada.quantidade
            else:
                continue
        else:
            quantidade = entrada.quantidade if entrada.quantidade else 0
        
        movimentacoes.append({
            'tipo': 'ENTRADA',
            'data': entrada.data_entrada,
            'quantidade': quantidade,
            'objeto': entrada,
            'tipo_mov': entrada.get_tipo_entrada_display(),
        })
    
    for saida in todas_saidas:
        if saida.produtos_saida.exists():
            produto_saida = saida.produtos_saida.filter(produto=produto).first()
            if produto_saida:
                quantidade = produto_saida.quantidade
            else:
                continue
        else:
            quantidade = saida.quantidade if saida.quantidade else 0
        
        movimentacoes.append({
            'tipo': 'SAIDA',
            'data': saida.data_saida,
            'quantidade': quantidade,
            'objeto': saida,
            'tipo_mov': saida.get_tipo_saida_display(),
        })
    
    movimentacoes.sort(key=lambda x: x['data'], reverse=True)
    
    try:
        buffer = BytesIO()
        # Formato A4 padrão
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Estilos modernos
        style_header = ParagraphStyle('header', parent=styles['Normal'], alignment=1, fontSize=14, fontName='Helvetica-Bold', spaceAfter=3, leading=16, textColor=colors.HexColor('#1a1a1a'))
        style_header_small = ParagraphStyle('header_small', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=2, leading=13, textColor=colors.HexColor('#666666'))
        style_title = ParagraphStyle('title', parent=styles['Normal'], alignment=1, fontSize=20, fontName='Helvetica-Bold', spaceAfter=15, textColor=colors.HexColor('#2c3e50'))
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Normal'], alignment=0, fontSize=14, fontName='Helvetica-Bold', spaceAfter=8, spaceBefore=10, textColor=colors.HexColor('#34495e'))
        style_field_label = ParagraphStyle('field_label', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', spaceAfter=3, textColor=colors.HexColor('#555555'))
        style_field_value = ParagraphStyle('field_value', parent=styles['Normal'], fontSize=11, fontName='Helvetica', spaceAfter=6, textColor=colors.HexColor('#2c3e50'))
        style_descricao = ParagraphStyle('descricao', parent=styles['Normal'], fontSize=13, fontName='Helvetica-Bold', alignment=1, spaceAfter=12, textColor=colors.HexColor('#2c3e50'))
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=4)
        style_table_header = ParagraphStyle('table_header', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', alignment=1, textColor=colors.white)
        style_table_cell = ParagraphStyle('table_cell', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=0)
        style_table_cell_center = ParagraphStyle('table_cell_center', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=1)
        style_center_small = ParagraphStyle('center_small', parent=styles['Normal'], fontSize=9, alignment=1, spaceAfter=5)
        
        # Logo
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        logo_img = None
        if os.path.exists(logo_path):
            logo_img = Image(logo_path, width=3*cm, height=3*cm)
        
        largura_disponivel = A4[0] - (2*cm * 2)
        
        # Cabeçalho moderno
        textos_cabecalho = [
            Paragraph("GOVERNO DO ESTADO DO PIAUÍ", style_header),
            Paragraph("CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ", style_header),
        ]
        
        om_produto = _obter_om_item(produto)
        if om_produto:
            textos_cabecalho.append(Paragraph(str(om_produto).upper(), style_header))
        
        endereco_om = None
        if om_produto and hasattr(om_produto, 'endereco') and om_produto.endereco:
            endereco_om = om_produto.endereco
        
        if endereco_om:
            textos_cabecalho.append(Paragraph(endereco_om, style_header_small))
        
        # Logo centralizada
        if logo_img:
            logo_table = Table([[logo_img]], colWidths=[largura_disponivel])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(logo_table)
        
        for texto in textos_cabecalho:
            story.append(texto)
        
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=2, spaceAfter=15, spaceBefore=0, color=colors.HexColor('#2c3e50')))
        
        # Título principal
        story.append(Paragraph("FICHA TÉCNICA DO ITEM", style_title))
        story.append(Spacer(1, 20))
        
        # Foto e Código de Barras lado a lado
        foto_codigo_data = []
        
        # Foto do produto (se existir)
        foto_img = None
        if produto.imagem:
            try:
                foto_path = produto.imagem.path
                if os.path.exists(foto_path):
                    # Redimensionar foto para caber no PDF (máximo 6cm de largura)
                    foto_img = Image(foto_path, width=6*cm, height=6*cm, kind='proportional')
            except Exception:
                foto_img = None
        
        # Código de barras (usar código de barras ou código do produto)
        codigo_barras_img = None
        codigo_barras_texto = None
        codigo = produto.codigo_barras or produto.codigo
        if codigo:
            # Tentar gerar código de barras usando python-barcode
            try:
                import barcode
                from barcode.writer import ImageWriter
                
                code128 = barcode.get_barcode_class('code128')
                barcode_instance = code128(codigo, writer=ImageWriter())
                
                barcode_buffer = BytesIO()
                barcode_instance.write(barcode_buffer)
                barcode_buffer.seek(0)
                
                # Criar imagem do código de barras
                codigo_barras_img = RLImage(barcode_buffer, width=8*cm, height=2.5*cm)
                codigo_barras_texto = codigo
            except ImportError:
                # Se barcode não estiver disponível, usar QR Code
                try:
                    qr_barcode = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=6, border=2)
                    qr_barcode.add_data(codigo)
                    qr_barcode.make(fit=True)
                    qr_img_pil = qr_barcode.make_image(fill_color="black", back_color="white")
                    qr_buffer = BytesIO()
                    qr_img_pil.save(qr_buffer, format='PNG')
                    qr_buffer.seek(0)
                    codigo_barras_img = RLImage(qr_buffer, width=4*cm, height=4*cm)
                    codigo_barras_texto = codigo
                except Exception:
                    codigo_barras_img = None
                    codigo_barras_texto = codigo
            except Exception:
                codigo_barras_img = None
                codigo_barras_texto = codigo
        
        # Criar tabela com foto e código de barras
        if foto_img or codigo_barras_img or codigo_barras_texto:
            foto_codigo_row = []
            
            # Coluna da foto
            if foto_img:
                foto_codigo_row.append(foto_img)
            else:
                foto_codigo_row.append(Spacer(1, 1))
            
            # Coluna do código de barras (com imagem e texto)
            if codigo_barras_img:
                # Criar uma tabela interna para código de barras + texto
                codigo_barras_inner = Table([
                    [codigo_barras_img],
                    [Paragraph(f"<b>Código de Barras:</b> {codigo_barras_texto or produto.codigo_barras}", style_small)]
                ], colWidths=[8*cm])
                codigo_barras_inner.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                foto_codigo_row.append(codigo_barras_inner)
            elif codigo_barras_texto:
                # Se não conseguiu gerar imagem, mostrar apenas o texto
                foto_codigo_row.append(Paragraph(f"<b>Código de Barras:</b> {codigo_barras_texto}", style_small))
            else:
                foto_codigo_row.append(Spacer(1, 1))
            
            # Larguras das colunas
            if foto_img and (codigo_barras_img or codigo_barras_texto):
                col_widths_foto = [7*cm, 9*cm]
            elif foto_img:
                col_widths_foto = [largura_disponivel]
            elif codigo_barras_img or codigo_barras_texto:
                col_widths_foto = [largura_disponivel]
            else:
                col_widths_foto = [largura_disponivel]
            
            foto_codigo_table = Table([foto_codigo_row], colWidths=col_widths_foto)
            foto_codigo_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(foto_codigo_table)
            story.append(Spacer(1, 10))
        
        # Card de informações principais
        info_data = []
        
        # Código e Descrição em destaque
        story.append(Paragraph(f"<b>{produto.descricao}</b>", style_descricao))
        story.append(Spacer(1, 5))
        
        info_data.append([
            Paragraph("<b>Código:</b>", style_field_label),
            Paragraph(produto.codigo, style_field_value)
        ])
        
        if produto.codigo_barras:
            info_data.append([
                Paragraph("<b>Código de Barras:</b>", style_field_label),
                Paragraph(produto.codigo_barras, style_field_value)
            ])
        
        if produto.categoria:
            info_data.append([
                Paragraph("<b>Categoria:</b>", style_field_label),
                Paragraph(str(produto.categoria), style_field_value)
            ])
        
        if produto.marca:
            info_data.append([
                Paragraph("<b>Marca:</b>", style_field_label),
                Paragraph(produto.marca, style_field_value)
            ])
        
        if produto.modelo:
            info_data.append([
                Paragraph("<b>Modelo:</b>", style_field_label),
                Paragraph(produto.modelo, style_field_value)
            ])
        
        if produto.tamanho:
            info_data.append([
                Paragraph("<b>Tamanho/Numeração:</b>", style_field_label),
                Paragraph(produto.tamanho, style_field_value)
            ])
        
        info_data.append([
            Paragraph("<b>Unidade de Medida:</b>", style_field_label),
            Paragraph(produto.get_unidade_medida_display(), style_field_value)
        ])
        
        # Tabela de informações
        largura_label = largura_disponivel * 0.45
        largura_valor = largura_disponivel * 0.55
        
        if info_data:
            info_table = Table(info_data, colWidths=[largura_label, largura_valor])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
            ]))
            story.append(info_table)
        
        # Informações de estoque em destaque - duas colunas
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, spaceAfter=8, spaceBefore=0, color=colors.HexColor('#3498db')))
        story.append(Paragraph("<b>ESTOQUE</b>", style_subtitle))
        
        # Preparar dados do estoque em duas colunas
        estoque_linhas = []
        
        # Linha 1: Quantidade Atual e Estoque Mínimo
        linha1_col1 = Paragraph(f"<b>Quantidade Atual:</b> <font color='#27ae60'><b>{produto.formatar_quantidade_unidade(produto.quantidade_atual)}</b></font>", style_field_value)
        linha1_col2 = ""
        if produto.estoque_minimo:
            linha1_col2 = Paragraph(f"<b>Estoque Mínimo:</b> {produto.formatar_quantidade_unidade(produto.estoque_minimo)}", style_field_value)
        else:
            linha1_col2 = Paragraph("", style_field_value)
        estoque_linhas.append([linha1_col1, linha1_col2])
        
        # Linha 2: Estoque Máximo e Status
        linha2_col1 = ""
        if produto.estoque_maximo:
            linha2_col1 = Paragraph(f"<b>Estoque Máximo:</b> {produto.formatar_quantidade_unidade(produto.estoque_maximo)}", style_field_value)
        else:
            linha2_col1 = Paragraph("", style_field_value)
        
        status_estoque = produto.get_status_estoque_display()
        cor_status = '#27ae60' if produto.quantidade_atual > produto.estoque_minimo else '#e74c3c' if produto.quantidade_atual < produto.estoque_minimo else '#f39c12'
        linha2_col2 = Paragraph(f"<b>Status do Estoque:</b> <font color='{cor_status}'><b>{status_estoque}</b></font>", style_field_value)
        estoque_linhas.append([linha2_col1, linha2_col2])
        
        # Criar tabela de estoque com duas colunas
        if estoque_linhas:
            largura_col_estoque = largura_disponivel * 0.5
            estoque_table = Table(estoque_linhas, colWidths=[largura_col_estoque, largura_col_estoque])
            estoque_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ]))
            story.append(estoque_table)
        
        # Informações adicionais
        if produto.localizacao or produto.fornecedor_principal:
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=1, spaceAfter=8, spaceBefore=0, color=colors.HexColor('#95a5a6')))
            
            info_adicional = []
            if produto.localizacao:
                info_adicional.append([
                    Paragraph("<b>Localização:</b>", style_field_label),
                    Paragraph(produto.localizacao, style_field_value)
                ])
            if produto.fornecedor_principal:
                info_adicional.append([
                    Paragraph("<b>Fornecedor Principal:</b>", style_field_label),
                    Paragraph(produto.fornecedor_principal, style_field_value)
                ])
            
            if info_adicional:
                info_adicional_table = Table(info_adicional, colWidths=[largura_label, largura_valor])
                info_adicional_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(info_adicional_table)
        
        if produto.observacoes:
            story.append(Spacer(1, 12))
            story.append(HRFlowable(width="100%", thickness=1, spaceAfter=8, spaceBefore=0, color=colors.HexColor('#95a5a6')))
            story.append(Paragraph("<b>OBSERVAÇÕES</b>", style_subtitle))
            story.append(Spacer(1, 5))
            story.append(Paragraph(produto.observacoes, style_small))
        
        # Histórico de Movimentações
        if movimentacoes:
            story.append(Spacer(1, 15))
            story.append(HRFlowable(width="100%", thickness=2, spaceAfter=10, spaceBefore=0, color=colors.HexColor('#3498db')))
            story.append(Paragraph("<b>HISTÓRICO DE MOVIMENTAÇÕES</b>", style_subtitle))
            story.append(Spacer(1, 8))
            
            # Cabeçalho da tabela
            mov_data = [[
                Paragraph("<b>Data</b>", style_table_header),
                Paragraph("<b>Tipo</b>", style_table_header),
                Paragraph("<b>Quantidade</b>", style_table_header),
                Paragraph("<b>Movimentação</b>", style_table_header),
                Paragraph("<b>Detalhes</b>", style_table_header),
            ]]
            
            # Dados das movimentações (limitar a 50 mais recentes)
            for mov in movimentacoes[:50]:
                data_str = mov['data'].strftime("%d/%m/%Y")
                tipo_badge = "ENTRADA" if mov['tipo'] == 'ENTRADA' else "SAÍDA"
                cor_tipo = '#27ae60' if mov['tipo'] == 'ENTRADA' else '#e74c3c'
                
                detalhes = ""
                if mov['tipo'] == 'ENTRADA':
                    entrada = mov['objeto']
                    if entrada.fornecedor:
                        detalhes += f"Fornecedor: {entrada.fornecedor[:30]}\n"
                    if entrada.nota_fiscal:
                        detalhes += f"NF: {entrada.nota_fiscal}\n"
                    if entrada.responsavel:
                        detalhes += f"Resp: {entrada.responsavel.nome_guerra[:25]}"
                else:
                    saida = mov['objeto']
                    if saida.requisitante:
                        detalhes += f"Req: {saida.requisitante.nome_guerra[:30]}\n"
                    if saida.responsavel_entrega:
                        detalhes += f"Entrega: {saida.responsavel_entrega.nome_guerra[:25]}"
                
                mov_data.append([
                    Paragraph(data_str, style_table_cell_center),
                    Paragraph(f"<font color='{cor_tipo}'><b>{tipo_badge}</b></font>", style_table_cell_center),
                    Paragraph(f"{produto.formatar_quantidade_unidade(mov['quantidade'])}", style_table_cell_center),
                    Paragraph(mov['tipo_mov'][:25], style_table_cell),
                    Paragraph(detalhes[:40] if detalhes else "-", style_table_cell),
                ])
            
            # Larguras das colunas
            col_widths = [2.5*cm, 2*cm, 2.5*cm, 3.5*cm, 5.5*cm]
            
            mov_table = Table(mov_data, colWidths=col_widths, repeatRows=1)
            mov_table.setStyle(TableStyle([
                # Cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                # Dados
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                # Bordas
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Linhas alternadas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            
            story.append(mov_table)
            
            if len(movimentacoes) > 50:
                story.append(Spacer(1, 5))
                story.append(Paragraph(f"<i>Mostrando as 50 movimentações mais recentes de um total de {len(movimentacoes)}</i>", style_small))
        
        # Rodapé com QR Code
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=2, spaceAfter=12, spaceBefore=0, color=colors.HexColor('#2c3e50')))
        
        class ProdutoFake:
            def __init__(self, produto):
                self.id = f"produto_{produto.pk}"
                self.pk = produto.pk
                self.tipo_documento = 'produto_almoxarifado'
        
        produto_fake = ProdutoFake(produto)
        autenticador = gerar_autenticador_veracidade(produto_fake, request, tipo_documento='produto_almoxarifado')
        
        url_autenticacao_base = autenticador.get('url_autenticacao', autenticador.get('url', ''))
        qr_cupom = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=8, border=2)
        qr_cupom.add_data(url_autenticacao_base)
        qr_cupom.make(fit=True)
        qr_img_pil_cupom = qr_cupom.make_image(fill_color="black", back_color="white")
        qr_buffer_cupom = BytesIO()
        qr_img_pil_cupom.save(qr_buffer_cupom, format='PNG')
        qr_buffer_cupom.seek(0)
        qr_img_cupom = RLImage(qr_buffer_cupom, width=3*cm, height=3*cm)
        
        largura_disponivel_qr = A4[0] - (2*cm * 2)
        largura_qr_cupom = 3*cm
        largura_texto_qr = largura_disponivel_qr - largura_qr_cupom - 0.5*cm
        
        rodape_data = [
            [qr_img_cupom, Paragraph(autenticador['texto_autenticacao'], style_center_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[largura_qr_cupom, largura_texto_qr])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(rodape_table)
        
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ficha_produto_{produto.codigo.replace(" ", "_")}.pdf"'
        
        return response
        
    except Exception as e:
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Item</title>
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
                <p><strong>Ocorreu um erro ao gerar o PDF do item.</strong></p>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <p><small>{str(e)}</small></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')

