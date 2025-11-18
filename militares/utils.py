from datetime import date
import hashlib
import re
from django.utils import timezone
from datetime import datetime
import pytz

def calcular_proxima_data_promocao(tipo='OFICIAIS', data_atual=None):
    """
    Calcula a próxima data de promoção baseada no tipo:
    - Para OFICIAIS: 18 de julho e 23 de dezembro
    - Para PRACAS: 18 de julho e 25 de dezembro
    
    Se a data atual for antes de 18 de julho, retorna 18 de julho do ano atual
    Se a data atual for entre 18 de julho e a data de dezembro, retorna a data de dezembro do ano atual
    Se a data atual for após a data de dezembro, retorna 18 de julho do próximo ano
    """
    if data_atual is None:
        data_atual = date.today()
    
    ano_atual = data_atual.year
    
    # Datas oficiais de promoção
    data_julho = date(ano_atual, 7, 18)
    
    if tipo == 'PRACAS':
        data_dezembro = date(ano_atual, 12, 25)
    else:  # OFICIAIS
        data_dezembro = date(ano_atual, 12, 23)
    
    # Se estamos antes de 18 de julho, próxima promoção é 18 de julho
    if data_atual < data_julho:
        return data_julho
    
    # Se estamos entre 18 de julho e a data de dezembro, próxima promoção é a data de dezembro
    elif data_atual <= data_dezembro:
        return data_dezembro
    
    # Se passamos da data de dezembro, próxima promoção é 18 de julho do próximo ano
    else:
        return date(ano_atual + 1, 7, 18) 

def criptografar_cpf_lgpd(cpf):
    """
    Criptografa CPF conforme LGPD, mantendo apenas os 3 primeiros e 2 últimos dígitos visíveis.
    Exemplo: 123.456.789-01 -> 123.***.***-01
    """
    if not cpf:
        return ""
    
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'[^\d]', '', cpf)
    
    if len(cpf_limpo) != 11:
        return cpf  # Retorna original se não for um CPF válido
    
    # Mantém os 3 primeiros e 2 últimos dígitos, substitui o resto por asteriscos
    cpf_criptografado = f"{cpf_limpo[:3]}.***.***-{cpf_limpo[-2:]}"
    
    return cpf_criptografado

def hash_cpf_lgpd(cpf):
    """
    Gera hash do CPF para verificação de unicidade sem expor o CPF completo.
    """
    if not cpf:
        return ""
    
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'[^\d]', '', cpf)
    
    if len(cpf_limpo) != 11:
        return ""
    
    # Gera hash SHA-256 do CPF
    return hashlib.sha256(cpf_limpo.encode()).hexdigest()[:16] 

def calcular_proxima_numeracao_antiguidade(posto_graduacao, militar_excluir=None):
    """
    Calcula a próxima numeração de antiguidade disponível para um posto/graduação
    
    Args:
        posto_graduacao: Código do posto/graduação
        militar_excluir: Militar a ser excluído da contagem (opcional)
    
    Returns:
        int: Próxima numeração disponível
    """
    from .models import Militar
    
    # Buscar militares do mesmo posto
    militares_mesmo_posto = Militar.objects.filter(
        posto_graduacao=posto_graduacao,
        classificacao='ATIVO'
    )
    
    # Excluir militar específico se fornecido
    if militar_excluir:
        militares_mesmo_posto = militares_mesmo_posto.exclude(pk=militar_excluir.pk)
    
    if not militares_mesmo_posto.exists():
        return 1
    
    # Buscar numerações existentes
    numeracoes_existentes = militares_mesmo_posto.values_list(
        'numeracao_antiguidade', flat=True
    ).filter(numeracao_antiguidade__isnull=False).order_by('numeracao_antiguidade')
    
    if not numeracoes_existentes:
        return 1
    
    # Encontrar a primeira lacuna ou usar o próximo número
    numeracoes_list = list(numeracoes_existentes)
    proxima_numeracao = 1
    
    for i, num in enumerate(numeracoes_list):
        if num != i + 1:
            proxima_numeracao = i + 1
            break
    else:
        # Se não há lacunas, usar o próximo número
        proxima_numeracao = len(numeracoes_list) + 1
    
    return proxima_numeracao 

def gerar_texto_assinatura_eletronica(usuario, tipo_assinatura, data_assinatura=None, fundamento_legal=None):
    """
    Gera o texto padrão de assinatura eletrônica
    
    Args:
        usuario: User object do Django
        tipo_assinatura: string com o tipo de assinatura (ex: "Aprovação")
        data_assinatura: datetime da assinatura (opcional, usa agora se não fornecido)
        fundamento_legal: string com o fundamento legal (opcional, usa padrão se não fornecido)
    
    Returns:
        string: texto formatado da assinatura eletrônica
    """
    
    # Se não foi fornecida data, usar agora
    if data_assinatura is None:
        data_assinatura = timezone.now()
    
    # Converter para timezone de Brasília se necessário
    if timezone.is_naive(data_assinatura):
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_assinatura = brasilia_tz.localize(data_assinatura)
    else:
        data_assinatura = data_assinatura.astimezone(pytz.timezone('America/Sao_Paulo'))
    
    # Formatar data e hora
    data_formatada = data_assinatura.strftime('%d/%m/%Y')
    hora_formatada = data_assinatura.strftime('%H:%M')
    
    # Obter nome do usuário
    nome_usuario = usuario.get_full_name() or usuario.username
    if not nome_usuario or nome_usuario.strip() == '':
        nome_usuario = "Usuário do Sistema"
    
    # Se o usuário tem militar associado, incluir informações do militar
    if hasattr(usuario, 'militar') and usuario.militar:
        militar = usuario.militar
        nome_completo = f"{militar.get_posto_graduacao_display()} {militar.nome_completo}"
    else:
        nome_completo = nome_usuario
    
    # Fundamentos legais padrão
    if fundamento_legal is None:
        fundamento_legal = "Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025"
    
    # Obter a função atual do usuário
    funcao_atual = 'Usuário do Sistema'  # Função será obtida da sessão
    
    # Gerar texto da assinatura no formato solicitado
    texto = f"Documento assinado eletronicamente por {nome_completo} - {funcao_atual}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na {fundamento_legal}"
    
    return texto

def gerar_texto_assinatura_comissao(membro_comissao, tipo_assinatura, data_assinatura=None, fundamento_legal=None):
    """
    Gera o texto de assinatura eletrônica específico para membros de comissão
    
    Args:
        membro_comissao: MembroComissao object
        tipo_assinatura: string com o tipo de assinatura
        data_assinatura: datetime da assinatura (opcional)
        fundamento_legal: string com o fundamento legal (opcional)
    
    Returns:
        string: texto formatado da assinatura eletrônica
    """
    
    # Se não foi fornecida data, usar agora
    if data_assinatura is None:
        data_assinatura = timezone.now()
    
    # Converter para timezone de Brasília se necessário
    if timezone.is_naive(data_assinatura):
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_assinatura = brasilia_tz.localize(data_assinatura)
    else:
        data_assinatura = data_assinatura.astimezone(pytz.timezone('America/Sao_Paulo'))
    
    # Formatar data e hora
    data_formatada = data_assinatura.strftime('%d/%m/%Y')
    hora_formatada = data_assinatura.strftime('%H:%M')
    
    # Informações do militar
    militar = membro_comissao.militar
    nome_completo = f"{militar.get_posto_graduacao_display()} {militar.nome_completo}"
    
    # Fundamentos legais padrão
    if fundamento_legal is None:
        fundamento_legal = "Portaria XXX/2025 Gab. Cmdo. Geral/CBMEPI de XX de XXXXX de 2025"
    
    # Obter a função atual do usuário
    funcao_atual = 'Usuário do Sistema'  # Função será obtida da sessão
    
    # Gerar texto da assinatura no formato padronizado
    texto = f"Documento assinado eletronicamente por {nome_completo} - {funcao_atual}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, com fundamento na {fundamento_legal}"
    
    return texto 

def obter_funcao_atual_usuario(usuario, request=None):
    """
    Obtém a função atual do usuário que está fazendo login
    
    Args:
        usuario: User object do Django
        request: HttpRequest object (opcional, para acessar a sessão)
    
    Returns:
        string: função atual do usuário (ex: "Secretário da CPP", "Presidente da CPO", etc.)
    """
    
    # DEBUG: Verificar se temos request e sessão
    if request and hasattr(request, 'session'):
        funcao_atual_nome = request.session.get('funcao_atual_nome')
        print(f"DEBUG: Função da sessão: {funcao_atual_nome}")
        if funcao_atual_nome:
            return funcao_atual_nome
        else:
            print(f"DEBUG: Nenhuma função encontrada na sessão")
    
    # Se não temos request ou não há função na sessão, usar a lógica anterior
    print(f"DEBUG: Usando lógica de fallback para usuário: {usuario.username}")
    
    # Verificar se o usuário tem militar associado
    if hasattr(usuario, 'militar') and usuario.militar:
        # Buscar membros de comissão ativos do militar
        from .models import MembroComissao
        membros_ativos = MembroComissao.objects.filter(
            militar=usuario.militar,
            ativo=True
        ).select_related('comissao')
        
        if membros_ativos.exists():
            # Priorizar presidente e secretário
            membro_presidente = membros_ativos.filter(tipo='PRESIDENTE').first()
            if membro_presidente:
                tipo_comissao = membro_presidente.comissao.get_tipo_display()
                return f"Presidente da {tipo_comissao}"
            
            membro_secretario = membros_ativos.filter(tipo='SECRETARIO').first()
            if membro_secretario:
                tipo_comissao = membro_secretario.comissao.get_tipo_display()
                return f"Secretário da {tipo_comissao}"
            
            # Se não for presidente nem secretário, pegar o primeiro membro
            membro = membros_ativos.first()
            tipo_comissao = membro.comissao.get_tipo_display()
            
            # Determinar a função do membro
            if membro.tipo == 'EFETIVO':
                return f"Membro Efetivo da {tipo_comissao}"
            elif membro.tipo == 'NATO':
                return f"Membro Nato da {tipo_comissao}"
            else:
                return f"Membro da {tipo_comissao}"
    
    # Se não tem militar ou não é membro de comissão, verificar funções diretas do usuário
    from .models import UsuarioFuncaoMilitar
    funcoes_ativas = UsuarioFuncaoMilitar.objects.filter(
        usuario=usuario,
        ativo=True
    ).select_related('funcao_militar')
    
    if funcoes_ativas.exists():
        # Pegar a primeira função ativa
        funcao = funcoes_ativas.first()
        return funcao.funcao_militar.nome
    
    # Se não tem função específica, retornar função genérica
    return "Usuário do Sistema" 

def debug_funcoes_usuario(usuario):
    """
    Função de debug para verificar todas as funções do usuário
    """
    print(f"=== DEBUG FUNÇÕES DO USUÁRIO: {usuario.username} ===")
    
    if hasattr(usuario, 'militar') and usuario.militar:
        print(f"Militar: {usuario.militar.nome_completo}")
        
        from .models import MembroComissao
        membros_ativos = MembroComissao.objects.filter(
            militar=usuario.militar,
            ativo=True
        ).select_related('comissao')
        
        print(f"Total de membros ativos: {membros_ativos.count()}")
        
        for membro in membros_ativos:
            print(f"- Tipo: {membro.tipo}, Comissão: {membro.comissao.get_tipo_display()}")
    
    from .models import UsuarioFuncaoMilitar
    funcoes_ativas = UsuarioFuncaoMilitar.objects.filter(
        usuario=usuario,
        ativo=True
    ).select_related('funcao_militar')
    
    print(f"Total de funções ativas: {funcoes_ativas.count()}")
    
    for funcao in funcoes_ativas:
        print(f"- Função: {funcao.funcao_militar.nome}")
    
    print("=== FIM DEBUG ===") 

def formatar_data_assinatura(data_assinatura):
    """
    Formata data de assinatura de forma consistente para HTML e PDF
    
    Args:
        data_assinatura: datetime da assinatura
    
    Returns:
        tuple: (data_formatada, hora_formatada) no formato brasileiro
    """
    import pytz
    from django.utils import timezone
    
    # Se não foi fornecida data, usar agora
    if data_assinatura is None:
        data_assinatura = timezone.now()
    
    # Converter para timezone de Brasília se necessário
    if timezone.is_naive(data_assinatura):
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_assinatura = brasilia_tz.localize(data_assinatura)
    else:
        data_assinatura = data_assinatura.astimezone(pytz.timezone('America/Sao_Paulo'))
    
    # Formatar data e hora no formato brasileiro
    data_formatada = data_assinatura.strftime('%d/%m/%Y')
    hora_formatada = data_assinatura.strftime('%H:%M')
    
    return data_formatada, hora_formatada 

def gerar_autenticador_veracidade(objeto, request=None, url_personalizada=None, tipo_documento=None):
    """
    Gera o autenticador de veracidade para documentos
    
    Args:
        objeto: O objeto do documento (quadro, ata, voto, etc.)
        request: Objeto request do Django (opcional)
        url_personalizada: URL personalizada para autenticação (opcional)
        tipo_documento: Tipo do documento para personalizar a URL (opcional)
    
    Returns:
        dict: Dicionário com dados do autenticador
    """
    import hashlib
    import qrcode
    from io import BytesIO
    from reportlab.platypus import Image
    from reportlab.lib.units import cm
    
    # Gerar códigos de verificação
    codigo_verificador = f"{objeto.pk:08d}"
    codigo_crc = f"{hash(str(objeto.pk)) % 0xFFFFFFF:07X}"
    
    # URL de autenticação baseada no tipo de documento
    if url_personalizada:
        url_autenticacao = url_personalizada
    elif tipo_documento:
        # URLs específicas para cada tipo de documento
        if tipo_documento == 'quadro':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'quadro_fixacao':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'voto':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'almanaque':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'ata':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'documento':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'calendario_promocao':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'proposta':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        elif tipo_documento == 'historico_abastecimento':
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
        else:
            from django.urls import reverse
            from django.contrib.sites.shortcuts import get_current_site
            if request:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
            else:
                url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
    else:
        from django.urls import reverse
        from django.contrib.sites.shortcuts import get_current_site
        if request:
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            url_autenticacao = f"{protocol}://{current_site.domain}{reverse('militares:verificar_autenticidade')}"
        else:
            url_autenticacao = f"http://127.0.0.1:8000{reverse('militares:verificar_autenticidade')}"
    
    # Gerar texto de autenticação
    texto_autenticacao = f"A autenticidade deste documento pode ser conferida no site <a href='{url_autenticacao}' color='blue'>{url_autenticacao}</a>, informando o código verificador <b>{codigo_verificador}</b> e o código CRC <b>{codigo_crc}</b>."
    
    # Gerar QR Code com configurações otimizadas
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_autenticacao)
    qr.make(fit=True)
    
    qr_img_pil = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img_pil.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_img = Image(qr_buffer, width=2*cm, height=2*cm)
    # Não fechar o buffer aqui - o ReportLab precisa acessá-lo
    
    return {
        'qr_img': qr_img,
        'texto_autenticacao': texto_autenticacao,
        'url_autenticacao': url_autenticacao,
        'codigo_verificador': codigo_verificador,
        'codigo_crc': codigo_crc
    }

def adicionar_autenticador_pdf(story, objeto, request=None, url_personalizada=None, tipo_documento=None):
    """
    Adiciona o autenticador de veracidade ao PDF
    
    Args:
        story: Lista de elementos do PDF
        objeto: O objeto do documento
        request: Objeto request do Django (opcional)
        url_personalizada: URL personalizada para autenticação (opcional)
        tipo_documento: Tipo do documento para personalizar a URL (opcional)
    """
    from reportlab.platypus import Spacer, HRFlowable, Paragraph, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    
    # Gerar dados do autenticador
    autenticador = gerar_autenticador_veracidade(objeto, request, url_personalizada, tipo_documento)
    
    # Adicionar separador mínimo
    story.append(Spacer(1, 1))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=1, spaceBefore=1, color=colors.grey))
    
    # Criar estilo para texto pequeno
    style_small = ParagraphStyle('small', fontSize=9)
    
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
    
    # Sem espaçamento final - autenticador colado no fim da folha 

def criar_rodape_sistema_pdf(request):
    """
    Cria funções de callback para adicionar rodapé com dados do sistema em todas as páginas do PDF.
    
    Retorna uma tupla (add_rodape_first, add_rodape_later) que pode ser usada em:
    doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
    
    Args:
        request: Objeto request do Django para obter informações do usuário
        
    Returns:
        tuple: (função para primeira página, função para páginas seguintes)
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    import pytz
    
    # Preparar informações para o rodapé
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    data_geracao_pdf = timezone.now().astimezone(brasilia_tz).strftime('%d/%m/%Y às %H:%M:%S')
    usuario_geracao = request.user.get_full_name() or request.user.username
    if hasattr(request.user, 'militar') and request.user.militar:
        usuario_geracao = f"{request.user.militar.get_posto_graduacao_display()} {request.user.militar.nome_completo}"
    
    def add_rodape_sistema(canvas, doc):
        """Adiciona rodapé com dados do sistema em todas as páginas"""
        canvas.saveState()
        
        # Configurar fonte
        try:
            canvas.setFont("Arial", 7)
        except:
            canvas.setFont("Helvetica", 7)
        
        # Posição do rodapé (inferior)
        page_num = canvas.getPageNumber()
        y_pos = 0.8*cm
        
        # Linha separadora
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(0.5)
        canvas.line(1.5*cm, 1.2*cm, A4[0] - 1.5*cm, 1.2*cm)
        
        # Informações do sistema
        canvas.setFillColor(colors.black)
        
        # Data de geração
        texto_data = f"Gerado em: {data_geracao_pdf}"
        canvas.drawString(1.5*cm, y_pos, texto_data)
        
        # Usuário que gerou
        texto_usuario = f"Por: {usuario_geracao}"
        canvas.drawString(1.5*cm, y_pos - 0.3*cm, texto_usuario)
        
        # Número da página (centro)
        texto_pagina = f"Página {page_num}"
        try:
            text_width = canvas.stringWidth(texto_pagina, "Arial", 7)
        except:
            text_width = canvas.stringWidth(texto_pagina, "Helvetica", 7)
        x_pos_pagina = (A4[0] - text_width) / 2
        canvas.drawString(x_pos_pagina, y_pos, texto_pagina)
        
        # Sistema (direita)
        texto_sistema = "SYSGABOM-CBMEPI"
        try:
            text_width = canvas.stringWidth(texto_sistema, "Arial", 7)
        except:
            text_width = canvas.stringWidth(texto_sistema, "Helvetica", 7)
        x_pos_sistema = A4[0] - 1.5*cm - text_width
        canvas.drawString(x_pos_sistema, y_pos, texto_sistema)
        
        canvas.restoreState()
    
    def add_rodape_first(canvas, doc):
        add_rodape_sistema(canvas, doc)
    
    def add_rodape_later(canvas, doc):
        add_rodape_sistema(canvas, doc)
    
    return (add_rodape_first, add_rodape_later)


def obter_caminho_assinatura_eletronica():
    """
    Retorna o caminho para a imagem de assinatura eletrônica.
    Usa assinasyspro.png para assinaturas eletrônicas e logo_cbmepi.png para cabeçalhos.
    """
    import os
    from django.conf import settings
    
    # Primeiro tenta encontrar assinasyspro.png
    logo_path = os.path.join(settings.STATIC_ROOT, 'assinasyspro.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'assinasyspro.png') if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, 'static', 'assinasyspro.png')
    
    # Se não encontrar assinasyspro.png, usa logo_cbmepi.png como fallback
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo_cbmepi.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'logo_cbmepi.png') if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, 'static', 'logo_cbmepi.png')
    
    return logo_path


def get_user_permissions(request):
    """
    Obtém as permissões do usuário para o módulo de Notas
    """
    if not request.user.is_authenticated:
        return {}
    
    try:
        from .models import UsuarioFuncaoMilitar
        
        # Obter função ativa do usuário
        usuario_funcao = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True
        ).first()
        
        if not usuario_funcao:
            return {}
        
        funcao = usuario_funcao.funcao_militar
        
        # Obter permissões da função
        permissoes = funcao.get_menu_permissions()
        
        return {}
        
    except Exception as e:
        print(f"Erro ao obter permissões do usuário: {e}")
        return {}


def check_permission(request, permission_name):
    """
    Verifica se o usuário tem uma permissão específica
    """
    permissoes = get_user_permissions(request)
    return permissoes.get(permission_name, False) 