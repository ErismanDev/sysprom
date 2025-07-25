from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import date
from django import forms
from django.db import models
from .models import Militar, FichaConceitoPracas, QuadroAcesso, QuadroFixacaoVagas, ItemQuadroFixacaoVagas, PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, Documento
from .forms import MilitarForm, FichaConceitoPracasForm, DocumentoForm, QuadroAcessoForm, QuadroFixacaoVagasForm
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models import Q
from django.conf import settings


def calcular_proxima_data_promocao_pracas(data_atual=None):
    """
    Calcula a próxima data de promoção para praças baseada nas datas oficiais:
    - 18 de julho
    - 25 de dezembro
    
    Se a data atual for antes de 18 de julho, retorna 18 de julho do ano atual
    Se a data atual for entre 18 de julho e 25 de dezembro, retorna 25 de dezembro do ano atual
    Se a data atual for após 25 de dezembro, retorna 18 de julho do próximo ano
    """
    if data_atual is None:
        data_atual = date.today()
    
    ano_atual = data_atual.year
    mes_atual = data_atual.month
    dia_atual = data_atual.day
    
    # Datas oficiais de promoção para praças
    data_julho = date(ano_atual, 7, 18)
    data_dezembro = date(ano_atual, 12, 25)
    
    # Se estamos antes de 18 de julho, próxima promoção é 18 de julho
    if data_atual < data_julho:
        return data_julho
    
    # Se estamos entre 18 de julho e 25 de dezembro, próxima promoção é 25 de dezembro
    elif data_atual <= data_dezembro:
        return data_dezembro
    
    # Se passamos de 25 de dezembro, próxima promoção é 18 de julho do próximo ano
    else:
        return date(ano_atual + 1, 7, 18)


# ============================================================================
# VIEWS ESPECÍFICAS PARA PRACAS
# ============================================================================

@login_required
def ficha_conceito_pracas_list(request):
    """Lista ficha de conceito de praças"""
    militar_id = request.GET.get('militar')
    query = request.GET.get('q', '')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas_oficiais = list(militar.fichaconceitooficiais_set.all())
        fichas_pracas = list(militar.fichaconceitopracas_set.all())
        fichas = fichas_oficiais + fichas_pracas
        fichas.sort(key=lambda x: x.data_registro, reverse=True)
        pracas_sem_ficha = []
        pracas_com_ficha = fichas
    else:
        militar = None
        pracas = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
        )
        if query:
            pracas = pracas.filter(
                Q(nome_completo__icontains=query) |
                Q(nome_guerra__icontains=query) |
                Q(matricula__icontains=query) |
                Q(cpf__icontains=query) |
                Q(email__icontains=query)
            )
        pracas_com_ficha = list(FichaConceitoPracas.objects.filter(militar__in=pracas))
        pracas_sem_ficha = list(pracas.exclude(
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        ))
        hierarquia_pracas = {
            'ST': 1, '1S': 2, '2S': 3, '3S': 4, 'CAB': 5, 'SD': 6,
        }
        pracas_com_ficha.sort(key=lambda x: (
            hierarquia_pracas.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,
            x.militar.nome_completo
        ))
        pracas_sem_ficha.sort(key=lambda x: (
            hierarquia_pracas.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,
            x.nome_completo
        ))
    total_pracas_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    ).count()
    # Montar lista final: primeiro os sem ficha, depois os com ficha
    fichas_final = pracas_sem_ficha + pracas_com_ficha
    
    context = {
        'militar': militar,
        'fichas': fichas_final,
        'pracas_com_ficha': pracas_com_ficha,
        'pracas_sem_ficha': pracas_sem_ficha,
        'total_pracas_ativos': total_pracas_ativos,
        'total_fichas_pracas': len(pracas_com_ficha),
        'pracas_sem_ficha_count': len(pracas_sem_ficha),
        'is_pracas': True,
        'query': query,
    }
    return render(request, 'militares/ficha_conceito_pracas_list.html', context)


@login_required
def gerar_fichas_conceito_pracas_todos(request):
    """Gera fichas de conceito para todas as praças que não possuem"""
    if request.method == 'POST':
        # Buscar praças sem ficha de conceito
        pracas_sem_ficha = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
        ).exclude(
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        )
        
        print(f"DEBUG: Encontradas {pracas_sem_ficha.count()} praças sem ficha")
        
        fichas_criadas = 0
        for militar in pracas_sem_ficha:
            print(f"DEBUG: Criando ficha para {militar.nome_completo} - Posto: {militar.posto_graduacao}")
            
            # Verificar se o militar é realmente uma praça
            if militar.is_oficial():
                print(f"DEBUG: ERRO - {militar.nome_completo} é oficial mas está sendo processado como praça!")
                continue
                
            # Verificar se já existe ficha para este militar
            ficha_existente_oficiais = militar.fichaconceitooficiais_set.first()
            ficha_existente_pracas = militar.fichaconceitopracas_set.first()
            
            if ficha_existente_oficiais or ficha_existente_pracas:
                print(f"DEBUG: {militar.nome_completo} já possui ficha - pulando")
                continue
            
            try:
                ficha = FichaConceitoPracas.objects.create(militar=militar)
                print(f"DEBUG: Ficha criada com sucesso para {militar.nome_completo} - Tempo no posto: {ficha.tempo_posto}")
                fichas_criadas += 1
            except Exception as e:
                print(f"DEBUG: Erro ao criar ficha para {militar.nome_completo}: {e}")
        
        print(f"DEBUG: Total de fichas criadas: {fichas_criadas}")
        messages.success(request, f'{fichas_criadas} fichas de conceito criadas para praças!')
        return redirect('militares:ficha_conceito_pracas_list')
    
    return redirect('militares:ficha_conceito_pracas_list')


@login_required
@user_passes_test(lambda u: u.is_staff)
def limpar_pontos_fichas_conceito_pracas(request):
    """Limpa pontos de todas as fichas de conceito de praças"""
    if request.method == 'POST':
        # Buscar fichas de praças
        pracas = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
        )
        fichas = FichaConceitoPracas.objects.filter(militar__in=pracas)
        
        fichas_atualizadas = 0
        for ficha in fichas:
            # Limpar todos os campos de pontos
            ficha.tempo_posto = 0
            ficha.cursos_especializacao = 0
            ficha.cursos_csbm = 0
            ficha.cursos_cfsd = 0
            ficha.cursos_chc = 0
            ficha.cursos_chsgt = 0
            ficha.cursos_cas = 0
            ficha.cursos_cho = 0
            ficha.cursos_cfo = 0
            ficha.cursos_cao = 0
            ficha.cursos_instrutor_csbm = 0
            ficha.cursos_civis_superior = 0
            ficha.cursos_civis_especializacao = 0
            ficha.cursos_civis_mestrado = 0
            ficha.cursos_civis_doutorado = 0
            ficha.medalha_federal = 0
            ficha.medalha_estadual = 0
            ficha.medalha_cbmepi = 0
            ficha.elogio_individual = 0
            ficha.elogio_coletivo = 0
            ficha.punicao_repreensao = 0
            ficha.punicao_detencao = 0
            ficha.punicao_prisao = 0
            ficha.falta_aproveitamento = 0
            ficha.save()
            fichas_atualizadas += 1
        
        messages.success(request, f'{fichas_atualizadas} fichas de conceito de praças limpas!')
        return redirect('militares:ficha_conceito_pracas_list')
    
    return redirect('militares:ficha_conceito_pracas_list')


@login_required
def quadro_acesso_pracas_detail(request, pk):
    """Detalhes do quadro de acesso de praças"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar se o quadro tem militares que são praças
    itens_pracas = quadro.itemquadroacesso_set.filter(
        militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    if not itens_pracas.exists():
        messages.error(request, 'Este quadro não contém praças!')
        return redirect('militares:quadro_acesso_list')
    
    militares_inaptos = quadro.militares_inaptos_com_motivo()
    
    nomes_postos = dict(QuadroAcesso.POSTO_CHOICES)
    nomes_quadros = dict(QuadroAcesso.QUADRO_CHOICES)
    
    # Para quadros de praças: transições específicas para praças
    quadros = ['PRACAS']
    transicoes_todas = [  # Praças
        {
            'numero': 'I',
            'titulo': '1º SARGENTO para o posto de SUBTENENTE',
            'origem': '1S',
            'destino': 'ST',
            'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Subtenente em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
        },
        {
            'numero': 'II',
            'titulo': '2º SARGENTO para o posto de 1º SARGENTO',
            'origem': '2S',
            'destino': '1S',
            'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
        },
        {
            'numero': 'III',
            'titulo': '3º SARGENTO para o posto de 2º SARGENTO',
            'origem': '3S',
            'destino': '2S',
            'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
        },
        {
            'numero': 'IV',
            'titulo': 'CABO para o posto de 3º SARGENTO',
            'origem': 'CAB',
            'destino': '3S',
            'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 3º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
        },
        {
            'numero': 'V',
            'titulo': 'SOLDADO para o posto de CABO',
            'origem': 'SD',
            'destino': 'CAB',
            'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Cabo em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
        }
    ]

    # Filtrar transições conforme o tipo do quadro
    if quadro.tipo == 'MERECIMENTO':
        # Para merecimento, incluir 1S→ST e 2S→1S
        transicoes_filtradas = [
            t for t in transicoes_todas 
            if (t['origem'], t['destino']) in [('1S','ST'), ('2S','1S')]
        ]
    elif quadro.tipo == 'ANTIGUIDADE':
        # Para antiguidade, todas as transições
        transicoes_filtradas = transicoes_todas
    elif quadro.tipo == 'AMBOS':
        # Para ambos, todas as transições
        transicoes_filtradas = transicoes_todas
    else:
        # Para outros tipos, todas as transições
        transicoes_filtradas = transicoes_todas

    transicoes_por_quadro = {
        'PRACAS': transicoes_filtradas
    }
    
    # Buscar apenas militares praças aptos do quadro
    militares_aptos_pracas = quadro.itemquadroacesso_set.filter(
        militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    ).select_related('militar')
    
    # Organizar militares por quadro e transição
    estrutura_quadros = {}
    for q in quadros:
        estrutura_quadros[q] = {
            'nome': nomes_quadros.get(q, q),
            'transicoes': []
        }
        transicoes_do_quadro = transicoes_por_quadro.get(q, [])
        for transicao in transicoes_do_quadro:
            origem = transicao['origem']
            destino = transicao['destino']
            militares_desta_transicao = [
                item for item in militares_aptos_pracas 
                if item.militar.quadro == q and item.militar.posto_graduacao == origem
            ]
            # ORDENAR CORRETAMENTE POR PONTUAÇÃO SE MERECIMENTO
            if quadro.tipo == 'MERECIMENTO':
                militares_desta_transicao = sorted(militares_desta_transicao, key=lambda x: float(x.pontuacao), reverse=True)
                # Atualizar posição conforme ordenação
                for idx, item in enumerate(militares_desta_transicao, 1):
                    item.posicao = idx
            else:
                militares_desta_transicao = sorted(militares_desta_transicao, key=lambda x: x.posicao)
            estrutura_quadros[q]['transicoes'].append({
                'numero': transicao['numero'],
                'titulo': transicao['titulo'],
                'origem': origem,
                'destino': destino,
                'origem_nome': nomes_postos.get(origem, origem),
                'destino_nome': nomes_postos.get(destino, destino),
                'militares': militares_desta_transicao,
                'texto': transicao['texto']
            })
    
    # Filtrar apenas militares inaptos que são praças
    militares_inaptos_pracas = [
        inapto for inapto in militares_inaptos 
        if inapto['militar'].posto_graduacao in ['SD', 'CAB', '3S', '2S', '1S', 'ST']
    ]
    
    # Total de praças aptas para exibir no template (estatísticas)
    total_pracas_aptas = militares_aptos_pracas.count()
    
    # Buscar praças disponíveis para adicionar ao quadro
    militares_no_quadro = quadro.itemquadroacesso_set.values_list('militar_id', flat=True)
    pracas_disponiveis = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST'],
        apto_inspecao_saude=True
    ).exclude(
        id__in=militares_no_quadro
    ).order_by('posto_graduacao', 'nome_completo')
    
    context = {
        'quadro': quadro,
        'militares_inaptos': militares_inaptos_pracas,
        'total_inaptos': len(militares_inaptos_pracas),
        'estrutura_quadros': estrutura_quadros,
        'is_pracas': True,
        'total_pracas_aptas': total_pracas_aptas,
        'militares_disponiveis': pracas_disponiveis,
    }
    return render(request, 'militares/quadro_acesso_pracas_detail.html', context)


@login_required
def quadro_acesso_pracas_edit(request, pk):
    """Editar quadro de acesso de praças"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar se o quadro tem militares que são praças
    itens_pracas = quadro.itemquadroacesso_set.filter(
        militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    if not itens_pracas.exists():
        messages.error(request, 'Este quadro não contém praças!')
        return redirect('militares:quadro_acesso_list')
    
    if request.method == 'POST':
        form = QuadroAcessoForm(request.POST, instance=quadro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quadro de acesso atualizado com sucesso!')
            return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    else:
        form = QuadroAcessoForm(instance=quadro)
    
    context = {
        'form': form,
        'quadro': quadro,
        'is_pracas': True,
    }
    return render(request, 'militares/quadro_acesso_pracas_form.html', context)


@login_required
def quadro_acesso_pracas_pdf(request, pk):
    """Gera PDF do quadro de acesso de praças com botões de assinatura integrados"""
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from io import BytesIO
    import os
    import qrcode
    import locale
    from datetime import datetime

    # Configurar locale para português brasileiro
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except:
            pass  # Usar formato padrão se não conseguir configurar

    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar se o quadro é de praças
    if quadro.categoria != 'PRACAS':
        messages.error(request, 'Este PDF é exclusivo para quadros de praças!')
        return redirect('militares:quadro_acesso_list')
    
    # Verificar se o quadro tem militares
    if not quadro.itemquadroacesso_set.exists():
        messages.error(request, 'Este quadro não contém militares!')
        return redirect('militares:quadro_acesso_list')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Estilos customizados
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
        "COMISSÃO DE PROMOÇÕES DE PRAÇAS - CBMEPI-PI",
        "Av. Miguel Rosa, 3515 Terreo - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    for linha in cabecalho:
        story.append(Paragraph(linha, style_center))
    story.append(Spacer(1, 10))

    # Título centralizado e sublinhado
    tipo_quadro = quadro.get_tipo_display().upper()
    titulo = f'<u>{tipo_quadro}</u>'
    story.append(Paragraph(titulo, style_title))
    story.append(Spacer(1, 16))

    # Texto introdutório com data em português
    meses_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril', 5: 'maio', 6: 'junho',
        7: 'julho', 8: 'agosto', 9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    data_formatada = f"{quadro.data_promocao.day} de {meses_pt[quadro.data_promocao.month]} de {quadro.data_promocao.year}"
    
    # Definir tipo e sigla do quadro
    if quadro.tipo == 'ANTIGUIDADE':
        tipo_quadro = 'por Antiguidade'
        sigla_quadro = 'QAA'
    elif quadro.tipo == 'MERECIMENTO':
        tipo_quadro = 'por Merecimento'
        sigla_quadro = 'QAM'
    else:
        tipo_quadro = 'Manual'
        sigla_quadro = 'QAM'
    
    # Definir texto introdutório baseado no tipo de quadro
    if quadro.tipo == 'MERECIMENTO':
        texto_intro = (
            f"Fica organizado o Quadro de Acesso {tipo_quadro} ({sigla_quadro}) "
            f"que visa às promoções do dia {data_formatada}, tudo com fulcro no parágrafo único do art. 6º c/c o § 2° do art. 20 da Lei n° 5.462, de 30 de junho de 2005 "
            "c/c o art. 10 da Lei 7.772 de 04 de abril de 2022."
        )
    else:
        texto_intro = (
            f"Fica organizado o Quadro de Acesso {tipo_quadro} ({sigla_quadro}) "
            f"que visa às promoções do dia {data_formatada}, com fulcro nos artigos 12, 13, c/c § 3º do Art. 20, da Lei nº 5.461, de 30 de junho de 2005, "
            "alterada pela Lei Nº 7.772, de 04 de abril de 2022."
        )
    
    story.append(Paragraph(texto_intro, style_just))
    story.append(Spacer(1, 12))

    # Definir todos os quadros
    quadros_info = [
        {
            'numero': 1,
            'nome': 'QUADRO DE PRAÇAS BOMBEIROS MILITARES (QPBM)',
            'codigo': 'PRACAS'
        }
    ]

    # Definir transições específicas por quadro
    if quadro.tipo == 'MERECIMENTO':
        # Para quadros de merecimento: transições específicas conforme regras
        transicoes_por_quadro = {
            'PRACAS': [  # Praças - incluir 1S→ST e 2S→1S
                {
                    'numero': 'I',
                    'titulo': '1º SARGENTO para a graduação de SUBTENENTE',
                    'origem': '1S',
                    'destino': 'ST',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para a graduação de Subtenente em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': '2º SARGENTO para a graduação de 1º SARGENTO',
                    'origem': '2S',
                    'destino': '1S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para a graduação de 1º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        }
    else:
        # Para quadros de antiguidade: todas as transições por antiguidade
        transicoes_por_quadro = {
            'PRACAS': [  # Praças
                {
                    'numero': 'I',
                    'titulo': '1º SARGENTO para a graduação de SUBTENENTE',
                    'origem': '1S',
                    'destino': 'ST',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de Subtenente em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': '2º SARGENTO para a graduação de 1º SARGENTO',
                    'origem': '2S',
                    'destino': '1S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de 1º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '3º SARGENTO para a graduação de 2º SARGENTO',
                    'origem': '3S',
                    'destino': '2S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de 2º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': 'CABO para a graduação de 3º SARGENTO',
                    'origem': 'CAB',
                    'destino': '3S',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de 3º Sargento em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'SOLDADO para a graduação de CABO',
                    'origem': 'SD',
                    'destino': 'CAB',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para a graduação de Cabo em virtude de não haver praça que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        }
    
    # Processar cada quadro
    for quadro_info in quadros_info:
        story.append(Spacer(1, 16))
        story.append(Paragraph(f'<b>{quadro_info["numero"]}. {quadro_info["nome"]}</b>', style_center))
        story.append(Spacer(1, 10))

        # Processar cada transição de posto específica do quadro
        transicoes_do_quadro = transicoes_por_quadro.get(quadro_info['codigo'], [])
        for transicao in transicoes_do_quadro:
            story.append(Spacer(1, 12))
            story.append(Paragraph(f'<b>{transicao["numero"]} – {transicao["titulo"]}</b>', style_bold))
            story.append(Spacer(1, 6))
            
            # Buscar militares aptos para esta transição neste quadro
            # Usar a mesma lógica do HTML: buscar em todos os militares do quadro
            todos_militares = quadro.itemquadroacesso_set.all()
            
            aptos = todos_militares.filter(
                militar__posto_graduacao=transicao['origem'],
                militar__quadro=quadro_info['codigo']
            ).order_by('posicao')
            
            if aptos.exists():
                # Preparar dados da tabela
                from .utils import criptografar_cpf_lgpd
                if quadro.tipo == 'MERECIMENTO':
                    # Para quadros de merecimento: adicionar coluna de pontuação
                    header_data = [['ORD', 'CPF', 'GRADUAÇÃO', 'NOME', 'PONTUAÇÃO']]
                    for idx, item in enumerate(aptos, 1):
                        header_data.append([
                            str(idx),
                            criptografar_cpf_lgpd(item.militar.cpf),
                            item.militar.get_posto_graduacao_display() if hasattr(item.militar, 'get_posto_graduacao_display') else item.militar.posto_graduacao,
                            item.militar.nome_completo,
                            f"{item.pontuacao:.2f}" if item.pontuacao else "-"
                        ])
                    
                    # Calcular larguras das colunas baseado no conteúdo
                    max_ord = max([len(str(row[0])) for row in header_data])
                    max_ident = max([len(row[1]) for row in header_data])
                    max_graduacao = max([len(row[2]) for row in header_data])
                    max_pontuacao = max([len(row[4]) for row in header_data])
                    
                    # Definir larguras mínimas e ajustáveis
                    col_widths = [
                        max(1.2*cm, max_ord * 0.3*cm),  # ORD
                        max(3*cm, max_ident * 0.3*cm),  # IDENT
                        max(3*cm, max_graduacao * 0.3*cm),  # GRADUAÇÃO
                        6*cm,  # NOME (reduzido para dar espaço à pontuação)
                        max(2*cm, max_pontuacao * 0.3*cm)  # PONTUAÇÃO
                    ]
                else:
                    # Para quadros de antiguidade: estrutura original
                    header_data = [['ORD', 'CPF', 'GRADUAÇÃO', 'NOME']]
                    for idx, item in enumerate(aptos, 1):
                        header_data.append([
                            str(idx),
                            criptografar_cpf_lgpd(item.militar.cpf),
                            item.militar.get_posto_graduacao_display() if hasattr(item.militar, 'get_posto_graduacao_display') else item.militar.posto_graduacao,
                            item.militar.nome_completo
                        ])
                    
                    # Calcular larguras das colunas baseado no conteúdo
                    max_ord = max([len(str(row[0])) for row in header_data])
                    max_ident = max([len(row[1]) for row in header_data])
                    max_graduacao = max([len(row[2]) for row in header_data])
                    
                    # Definir larguras mínimas e ajustáveis
                    col_widths = [
                        max(1.2*cm, max_ord * 0.3*cm),  # ORD
                        max(3*cm, max_ident * 0.3*cm),  # IDENT
                        max(3*cm, max_graduacao * 0.3*cm),  # GRADUAÇÃO
                        8*cm  # NOME (fixo)
                    ]
                
                table = Table(header_data, colWidths=col_widths)
                # Aplicar estilo diferente baseado no tipo de quadro
                if quadro.tipo == 'MERECIMENTO':
                    table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('ALIGN', (0, 1), (2, -1), 'CENTER'),
                        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
                        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Alinhar coluna de pontuação ao centro
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                else:
                    table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('ALIGN', (0, 1), (2, -1), 'CENTER'),
                        ('ALIGN', (3, 1), (3, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                story.append(table)
            else:
                story.append(Paragraph(transicao['texto'], style_just))
            
            story.append(Spacer(1, 8))

    # Data e local por extenso, centralizado
    meses_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril', 5: 'maio', 6: 'junho',
        7: 'julho', 8: 'agosto', 9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    # Buscar a primeira assinatura eletrônica para usar sua data
    primeira_assinatura = quadro.assinaturas.filter(assinado_por__isnull=False).order_by('data_assinatura').first()
    if primeira_assinatura:
        data_assinatura = primeira_assinatura.data_assinatura
        data_extenso = f"Teresina - PI, {data_assinatura.day} de {meses_pt[data_assinatura.month]} de {data_assinatura.year}"
    else:
        # Se não houver assinatura, usar a data do quadro
        data_extenso = f"Teresina - PI, {quadro.data_promocao.day} de {meses_pt[quadro.data_promocao.month]} de {quadro.data_promocao.year}"
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(data_extenso, style_center))
    
    # Seção de Assinaturas Físicas (sem título)
    story.append(Spacer(1, 20))

    # Buscar todas as assinaturas válidas do quadro (da mais recente para a mais antiga)
    assinaturas = quadro.assinaturas.filter(assinado_por__isnull=False).order_by('-data_assinatura')
    print(f"DEBUG: Encontradas {assinaturas.count()} assinaturas para o quadro {quadro.pk}")
    
    for assinatura in assinaturas:
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
        
        print(f"DEBUG: Processando assinatura física - Nome: {nome_completo}, Função: {funcao}, Tipo: {tipo}")
        
        # Exibir no formato físico: Nome - Posto BM (negrito), Função (normal), Tipo (negrito menor)
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>{nome_completo}</b>", style_center))
        story.append(Paragraph(f"{funcao}", style_center))
        story.append(Paragraph(f"<b>{tipo}</b>", style_center))
        story.append(Spacer(1, 12))

    # Seção de Assinaturas Eletrônicas (sem título)
    story.append(Spacer(1, 20))
    
    # Processar assinaturas eletrônicas
    print(f"DEBUG: Processando {assinaturas.count()} assinaturas eletrônicas")
    for i, assinatura in enumerate(assinaturas):
        # Informações de assinatura eletrônica
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
        
        print(f"DEBUG: Assinatura eletrônica {i+1} - Nome: {nome_assinante}, Função: {funcao}")
        
        # Adicionar logo do CBMEPI
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo_cbmepi.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'logo_cbmepi.png') if settings.STATICFILES_DIRS else os.path.join(settings.BASE_DIR, 'static', 'logo_cbmepi.png')
        
        # Tabela das assinaturas: Logo + Texto de assinatura
        assinatura_data = [
            [Image(logo_path, width=1.5*cm, height=1.5*cm), Paragraph(texto_assinatura, style_small)]
        ]
        
        assinatura_table = Table(assinatura_data, colWidths=[2*cm, 14*cm])
        assinatura_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        story.append(assinatura_table)
        
        # Adicionar linha separadora entre assinaturas (exceto na última)
        if i < len(assinaturas) - 1:
            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=8, spaceBefore=8, color=colors.lightgrey))
            story.append(Spacer(1, 8))
    
    # Se não houver assinaturas, mostrar mensagem
    if not assinaturas.exists():
        print("DEBUG: Nenhuma assinatura encontrada para exibir")
        story.append(Paragraph("Nenhuma assinatura registrada", style_center))
    
    # Rodapé com QR Code para conferência de veracidade
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Usar a função utilitária para gerar o autenticador
    from .utils import gerar_autenticador_veracidade
    autenticador = gerar_autenticador_veracidade(quadro, request, tipo_documento='quadro')
    
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
    
    # Gerar PDF
    doc.build(story)
    
    # Configurar resposta para visualização no navegador
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="quadro_acesso_pracas_{quadro.pk}_{quadro.get_tipo_display()}.pdf"'
    
    return response


@login_required
def quadro_acesso_pracas_print(request, pk):
    """Versão para impressão do quadro de acesso de praças"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar se o quadro tem militares que são praças
    itens_pracas = quadro.itemquadroacesso_set.filter(
        militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    if not itens_pracas.exists():
        messages.error(request, 'Este quadro não contém praças!')
        return redirect('militares:quadro_acesso_list')
    
    # Usar a mesma lógica da view original, mas com template específico
    from .views import quadro_acesso_print
    return quadro_acesso_print(request, pk)


@login_required
def gerar_quadro_acesso_pracas(request):
    """Gera quadro de acesso para praças"""
    if request.method == 'POST':
        form = QuadroAcessoForm(request.POST)
        if form.is_valid():
            # Removida a validação que bloqueava quadros para a mesma data/tipo
            # (permitir múltiplos quadros na mesma data)
            tipo = form.cleaned_data['tipo']
            data_promocao = form.cleaned_data['data_promocao']
            
            quadro = form.save(commit=False)
            quadro.status = 'EM_ELABORACAO'  # Define o status padrão
            
            # Se for quadro manual, definir critério de ordenação
            if tipo == 'MANUAL':
                criterio_ordenacao = request.POST.get('criterio_ordenacao_manual', 'ANTIGUIDADE')
                quadro.tipo = criterio_ordenacao
            
            quadro.save()
            
            # Se for quadro manual, redirecionar para a página de montar
            if tipo == 'MANUAL':
                messages.success(request, 'Quadro manual criado! Agora você pode montar o quadro manualmente.')
                return redirect('militares:montar_quadro_acesso_pracas', pk=quadro.pk)
            
            # Gerar o quadro automaticamente
            try:
                sucesso, mensagem = quadro.gerar_quadro_completo()
                if sucesso:
                    messages.success(request, 'Quadro de acesso de praças gerado com sucesso!')
                    return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
                else:
                    messages.warning(request, f'Quadro criado, mas com avisos: {mensagem}')
                    return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
            except Exception as e:
                messages.error(request, f'Erro ao gerar quadro: {str(e)}')
                return redirect('militares:quadro_acesso_list')
    else:
        form = QuadroAcessoForm()
        # Definir valores padrão para praças
        form.fields['tipo'].initial = 'ANTIGUIDADE'
    
    context = {
        'form': form,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'proxima_data_automatica': calcular_proxima_data_promocao_pracas(),
        'is_pracas': True,
    }
    return render(request, 'militares/quadro_acesso_pracas_form.html', context)


@login_required
def regerar_quadro_acesso_pracas(request, pk):
    """Regera quadro de acesso de praças"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar se o quadro tem militares que são praças
    itens_pracas = quadro.itemquadroacesso_set.filter(
        militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    if not itens_pracas.exists():
        messages.error(request, 'Este quadro não contém praças!')
        return redirect('militares:quadro_acesso_list')
    
    try:
        # Limpar itens existentes
        quadro.itemquadroacesso_set.all().delete()
        
        # Regenerar o quadro
        quadro.gerar_quadro_completo()
        
        messages.success(request, 'Quadro de acesso de praças regenerado com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao regenerar quadro: {str(e)}')
    
    return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)


@login_required
def delete_quadro_acesso_pracas(request, pk):
    """Exclui quadro de acesso de praças"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    if request.method == 'POST':
        # Verificar se o quadro está homologado (apenas para usuários não administradores)
        if quadro.status == 'HOMOLOGADO' and not request.user.is_superuser:
            messages.error(request, 'Não é possível excluir um quadro homologado. Apenas administradores podem excluir quadros homologados.')
            return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
        
        # Excluir todos os itens do quadro primeiro
        quadro.itemquadroacesso_set.all().delete()
        # Excluir o quadro
        quadro.delete()
        
        if quadro.status == 'HOMOLOGADO':
            messages.success(request, 'Quadro de acesso de praças homologado excluído com sucesso pelo administrador!')
        else:
            messages.success(request, 'Quadro de acesso de praças excluído com sucesso!')
        return redirect('militares:quadro_acesso_list')
    
    context = {
        'quadro': quadro,
        'is_pracas': True,
    }
    return render(request, 'militares/quadro_acesso_pracas_confirm_delete.html', context)


@login_required
def homologar_quadro_acesso_pracas(request, pk):
    """Homologa quadro de acesso de praças"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar permissão de homologação - apenas presidente da CPP pode homologar
    comissao_cpp = ComissaoPromocao.get_comissao_ativa_por_tipo('CPP')
    if not comissao_cpp or not comissao_cpp.eh_presidente(request.user):
        messages.error(request, 'Você não tem permissão para homologar quadros de praças. Apenas o presidente da CPP pode homologar.')
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    
    if request.method == 'POST':
        quadro.status = 'HOMOLOGADO'
        quadro.data_homologacao = timezone.now().date()
        quadro.homologado_por = request.user
        quadro.save()
        
        messages.success(request, 'Quadro de acesso de praças homologado com sucesso!')
        
        # Verificar se há um parâmetro 'next' para redirecionar para a página anterior
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
        'is_pracas': True,
    }
    return render(request, 'militares/quadro_acesso_pracas_confirm_homologar.html', context)


@login_required
def deshomologar_quadro_acesso_pracas(request, pk):
    """Deshomologa quadro de acesso de praças, solicitando confirmação de senha e função via modal"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    if request.method == 'POST':
        senha = request.POST.get('senha')
        funcao_id = request.POST.get('funcao_deshomologacao')
        
        # Verificar se a senha foi fornecida
        if not senha:
            messages.error(request, 'Senha é obrigatória.')
            return redirect('militares:quadro_acesso_list')
        
        # Verificar se a função foi selecionada
        if not funcao_id:
            messages.error(request, 'Função é obrigatória.')
            return redirect('militares:quadro_acesso_list')
        
        # Verificar se a senha está correta
        user = authenticate(username=request.user.username, password=senha)
        if user is None:
            messages.error(request, 'Senha incorreta. Tente novamente.')
            return redirect('militares:quadro_acesso_list')
        
        # Verificar se a função existe e pertence ao usuário
        try:
            funcao = UsuarioFuncao.objects.get(id=funcao_id, usuario=request.user)
        except UsuarioFuncao.DoesNotExist:
            messages.error(request, 'Função inválida.')
            return redirect('militares:quadro_acesso_list')
        
        # Verificar se o usuário é quem homologou o quadro
        if quadro.homologado_por and quadro.homologado_por != request.user:
            messages.error(request, 'Apenas o usuário que homologou pode deshomologar este quadro.')
            return redirect('militares:quadro_acesso_list')
        
        # Deshomologar o quadro
        if quadro.status == 'HOMOLOGADO':
            quadro.status = 'ELABORADO'
            quadro.data_homologacao = None
            quadro.homologado_por = None
            quadro.save()
            messages.success(request, 'Quadro de acesso de praças deshomologado com sucesso!')
            return redirect('militares:quadro_acesso_list')
        else:
            messages.error(request, 'Apenas quadros homologados podem ser deshomologados.')
            return redirect('militares:quadro_acesso_list')

    # Se chegou aqui, redirecionar para a lista
    return redirect('militares:quadro_acesso_list')


@login_required
def elaborar_quadro_acesso_pracas(request, pk):
    """Elabora quadro de acesso de praças com geração automática e possibilidade de inserções manuais"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    if request.method == 'POST':
        try:
            # Gerar quadro automaticamente primeiro
            quadro.gerar_quadro_completo()
            
            # Marcar todos os itens existentes como automáticos
            quadro.itemquadroacesso_set.update(
                inserido_manualmente=False,
                motivo_insercao='AUTOMATICO'
            )
            
            messages.success(request, 'Quadro de acesso de praças elaborado automaticamente! Agora você pode adicionar militares específicos por motivos especiais.')
        except Exception as e:
            messages.error(request, f'Erro ao elaborar quadro: {str(e)}')
        
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
        'is_pracas': True,
    }
    return render(request, 'militares/quadro_acesso_pracas_confirm_elaborar.html', context)


@login_required
def marcar_nao_elaborado_pracas(request, pk):
    """Marca quadro de acesso de praças como não elaborado"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        observacoes = request.POST.get('observacoes', '')
        
        quadro.status = 'NAO_ELABORADO'
        quadro.motivo_nao_elaboracao = motivo
        quadro.observacoes = observacoes
        quadro.save()
        
        messages.success(request, 'Quadro de acesso de praças marcado como não elaborado!')
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
        'is_pracas': True,
    }
    return render(request, 'militares/quadro_acesso_pracas_nao_elaborado.html', context)


@login_required
def relatorio_requisitos_quadro_pracas(request, pk):
    """Relatório de requisitos do quadro de acesso de praças"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Usar a mesma lógica da view original, mas com template específico
    from .views import relatorio_requisitos_quadro
    return relatorio_requisitos_quadro(request, pk)


# Views para Quadros de Fixação de Vagas de Praças (removidas - redundantes com views principais)


# View removida - redundante com view principal


# Views removidas - redundantes com views principais


@login_required
def regras_requisitos_pracas(request):
    """Exibe as regras e requisitos para promoção de praças"""
    return render(request, 'militares/regras_requisitos_pracas.html')


@login_required
def criar_quadro_manual_pracas(request):
    """Cria um quadro de acesso manual para praças"""
    from datetime import datetime
    
    if request.method == 'POST':
        data_promocao = request.POST.get('data_promocao')
        observacoes = request.POST.get('observacoes', '')
        
        if not data_promocao:
            messages.error(request, 'A data de promoção é obrigatória.')
            return redirect('militares:criar_quadro_manual_pracas')
        
        try:
            data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Data de promoção inválida.')
            return redirect('militares:criar_quadro_manual_pracas')
        
        # Verificar se já existe um quadro manual para esta data
        # Remover o bloqueio de quadro manual existente para a mesma data
        # (permitir múltiplos quadros manuais/aditamentos na mesma data)
        # quadro_existente = QuadroAcesso.objects.filter(
        #     tipo='MANUAL',
        #     data_promocao=data_promocao
        # ).first()
        # 
        # if quadro_existente:
        #     messages.warning(request, f'Já existe um quadro manual para a data {data_promocao.strftime("%d/%m/%Y")} para praças.')
        #     return redirect('militares:quadro_acesso_pracas_detail', pk=quadro_existente.pk)
        
        # Criar o quadro manual
        try:
            criterio = request.POST.get('criterio_ordenacao', 'ANTIGUIDADE')
            
            # Para quadros manuais, usar o critério selecionado mas manter flexibilidade
            novo_quadro = QuadroAcesso.objects.create(
                tipo=criterio,
                data_promocao=data_promocao,
                status='EM_ELABORACAO',
                observacoes=observacoes or f"Quadro manual para praças - {data_promocao.strftime('%d/%m/%Y')} - Critério: {criterio}"
            )
            
            messages.success(request, f'Quadro manual para praças criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}!')
            return redirect('militares:quadro_acesso_pracas_detail', pk=novo_quadro.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar quadro manual: {str(e)}')
        
        return redirect('militares:criar_quadro_manual_pracas')
    
    # Calcular próxima data de promoção para praças
    from militares.views import calcular_proxima_data_promocao
    proxima_data = calcular_proxima_data_promocao()
    
    context = {
        'proxima_data_automatica': proxima_data,
        'is_pracas': True,
    }
    
    return render(request, 'militares/criar_quadro_manual_pracas.html', context) 


@login_required
def montar_quadro_acesso_pracas(request, pk):
    """Interface para montar um quadro de acesso de praças manualmente, respeitando as regras"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, 'Quadro de acesso não encontrado.')
        return redirect('militares:quadro_acesso_list')
    
    # Remover verificação de is_manual - agora qualquer quadro pode ser montado manualmente
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'adicionar_militar':
            militar_id = request.POST.get('militar_id')
            posicao = request.POST.get('posicao')
            pontuacao = request.POST.get('pontuacao', 0)
            
            if not militar_id:
                messages.error(request, 'Selecione um militar.')
            else:
                try:
                    militar = Militar.objects.get(pk=militar_id)
                    
                    # Verificar se é praça
                    if militar.posto_graduacao not in ['SD', 'CAB', '3S', '2S', '1S', 'ST']:
                        messages.error(request, 'Apenas praças podem ser adicionadas a este quadro.')
                    else:
                        # Verificar regras básicas de elegibilidade
                        if militar.situacao != 'AT':
                            messages.error(request, f'Praça {militar.nome_completo} não está em situação ativa.')
                        elif not militar.apto_inspecao_saude:
                            messages.error(request, f'Praça {militar.nome_completo} não está apto em inspeção de saúde.')
                        else:
                            # Para merecimento, usar valores da ficha de conceito automaticamente
                            if quadro.tipo == 'MERECIMENTO':
                                ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
                                if not ficha:
                                    messages.error(request, f'Praça {militar.nome_completo} não possui ficha de conceito (obrigatória para merecimento).')
                                else:
                                    # Para merecimento: não usar posição manual, pontuação vem da ficha
                                    pontuacao_decimal = float(ficha.pontos) if ficha.pontos else 0.0
                                    
                                    quadro.adicionar_militar_manual(militar, None, pontuacao_decimal)
                                    messages.success(request, f'Praça {militar.nome_completo} adicionada ao quadro com pontuação {pontuacao_decimal}!')
                            else:  # ANTIGUIDADE
                                posicao_int = int(posicao) if posicao else None
                                pontuacao_decimal = float(pontuacao) if pontuacao else 0
                                
                                quadro.adicionar_militar_manual(militar, posicao_int, pontuacao_decimal)
                                messages.success(request, f'Praça {militar.nome_completo} adicionada ao quadro!')
                        
                except (Militar.DoesNotExist, ValueError) as e:
                    messages.error(request, f'Erro ao adicionar praça: {str(e)}')
        
        elif action == 'remover_militar':
            militar_id = request.POST.get('militar_id')
            
            if militar_id:
                try:
                    militar = Militar.objects.get(pk=militar_id)
                    quadro.remover_militar_manual(militar)
                    messages.success(request, f'Praça {militar.nome_completo} removida do quadro!')
                    
                except (Militar.DoesNotExist, ValueError) as e:
                    messages.error(request, f'Erro ao remover praça: {str(e)}')
        
        elif action == 'carregar_aptos':
            # Carregar automaticamente apenas militares aptos para ingresso
            militares_aptos = []
            pracas_ativos = Militar.objects.filter(
                situacao='AT',
                posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST'],
                apto_inspecao_saude=True
            )
            print(f"DEBUG: Encontrados {pracas_ativos.count()} praças ativos e aptos em inspeção de saúde")
            for i, praca in enumerate(pracas_ativos, 1):
                try:
                    if not quadro.itemquadroacesso_set.filter(militar=praca).exists():
                        if quadro.tipo == 'MERECIMENTO':
                            ficha = praca.fichaconceitooficiais_set.first() or praca.fichaconceitopracas_set.first()
                            if ficha:
                                militares_aptos.append((praca, ficha.pontos))
                                print(f"DEBUG: {praca.nome_completo} adicionado para merecimento com {ficha.pontos} pontos")
                            else:
                                print(f"DEBUG: {praca.nome_completo} não possui ficha de conceito e não será adicionado automaticamente")
                        else:  # ANTIGUIDADE
                            militares_aptos.append((praca, 0))
                            print(f"DEBUG: {praca.nome_completo} adicionado para antiguidade")
                    else:
                        print(f"DEBUG: {praca.nome_completo} já está no quadro")
                except Exception as e:
                    print(f"DEBUG: Erro ao processar {praca.nome_completo}: {str(e)}")
                    messages.warning(request, f'Erro ao processar {praca.nome_completo}: {str(e)}')
            print(f"DEBUG: Total de militares aptos para adicionar: {len(militares_aptos)}")
            adicionados = 0
            for i, (militar, pontuacao) in enumerate(militares_aptos, 1):
                try:
                    quadro.adicionar_militar_manual(militar, i, pontuacao)
                    adicionados += 1
                    print(f"DEBUG: Adicionado {militar.nome_completo} na posição {i}")
                except Exception as e:
                    print(f"DEBUG: Erro ao adicionar {militar.nome_completo}: {str(e)}")
                    messages.warning(request, f'Erro ao adicionar {militar.nome_completo}: {str(e)}')
            if adicionados > 0:
                messages.success(request, f'{adicionados} militares aptos foram carregados automaticamente!')
            else:
                messages.info(request, 'Nenhum militar apto foi adicionado. Verifique se já estão no quadro ou se há erros.')
        
        elif action == 'reordenar':
            # Reordenar baseado no critério selecionado
            if quadro.tipo == 'ANTIGUIDADE':
                # Ordenar por data de promoção (mais antiga primeiro)
                itens = quadro.itemquadroacesso_set.all().order_by('militar__data_promocao_atual', 'militar__nome_completo')
                criterio_nome = 'antiguidade'
            elif quadro.tipo == 'MERECIMENTO':
                # Ordenar por pontuação (maior pontuação primeiro)
                itens = quadro.itemquadroacesso_set.all().order_by('-pontuacao', 'militar__nome_completo')
                criterio_nome = 'merecimento'
            else:
                # Ordem manual - não reordenar automaticamente
                messages.info(request, 'Para quadros com ordem manual, você deve definir as posições manualmente.')
                return redirect('militares:montar_quadro_acesso_pracas', pk=quadro.pk)
            
            # Aplicar a nova ordenação
            for i, item in enumerate(itens, 1):
                item.posicao = i
                item.save()
            
            messages.success(request, f'Quadro reordenado por {criterio_nome}!')
        
        elif action == 'finalizar':
            if quadro.itemquadroacesso_set.exists():
                quadro.status = 'ELABORADO'
                quadro.save()
                messages.success(request, 'Quadro finalizado com sucesso!')
                return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
            else:
                messages.error(request, 'Adicione pelo menos uma praça antes de finalizar o quadro.')
    
    # Buscar praças ativos que podem ser adicionados ao quadro
    if quadro.tipo == 'MERECIMENTO':
        # Para merecimento: apenas 2º e 1º sargentos
        pracas_ativos = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['2S', '1S'],  # Apenas 2º e 1º sargentos
            apto_inspecao_saude=True
        ).order_by('posto_graduacao', 'nome_completo')
    else:
        # Para antiguidade: todas as praças
        pracas_ativos = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST'],
            apto_inspecao_saude=True
        ).order_by('posto_graduacao', 'nome_completo')

    pracas_disponiveis = []
    militares_no_quadro = set(quadro.itemquadroacesso_set.values_list('militar_id', flat=True))
    
    for praca in pracas_ativos:
        ficha = praca.fichaconceitooficiais_set.first() or praca.fichaconceitopracas_set.first()
        
        # Para merecimento, só incluir se tiver ficha de conceito
        if quadro.tipo == 'MERECIMENTO':
            if ficha:
                praca.ficha_conceito = ficha
                praca.pontuacao_ficha = float(ficha.pontos) if ficha.pontos else 0.0
                praca.ja_no_quadro = praca.id in militares_no_quadro
                pracas_disponiveis.append(praca)
        else:  # ANTIGUIDADE - incluir todos os aptos
            praca.ficha_conceito = ficha  # pode ser None
            praca.pontuacao_ficha = float(ficha.pontos) if ficha and ficha.pontos else 0.0
            praca.ja_no_quadro = praca.id in militares_no_quadro
            pracas_disponiveis.append(praca)
    
    # Ordenar por pontuação da ficha de conceito (maior pontuação primeiro)
    if quadro.tipo == 'MERECIMENTO':
        pracas_disponiveis.sort(key=lambda x: x.pontuacao_ficha, reverse=True)
    else:  # ANTIGUIDADE - ordenar por data de promoção e numeração de antiguidade
        pracas_disponiveis.sort(key=lambda x: (x.data_promocao_atual, x.numeracao_antiguidade or 999999))

    # Buscar itens do quadro ordenados por posição
    itens_quadro = quadro.itemquadroacesso_set.all().order_by('posicao')

    context = {
        'quadro': quadro,
        'militares_disponiveis': pracas_disponiveis,
        'itens_quadro': itens_quadro,
        'is_pracas': True,
    }
    
    return render(request, 'militares/montar_quadro_acesso.html', context)


@login_required
def buscar_pracas_elegiveis(request):
    """Busca praças elegíveis para adicionar ao quadro via AJAX"""
    if request.method == 'GET':
        termo = request.GET.get('termo', '')
        quadro_id = request.GET.get('quadro_id')
        
        if len(termo) < 2:
            return JsonResponse({'militares': []})
        
        try:
            quadro = QuadroAcesso.objects.get(pk=quadro_id)
            militares_no_quadro = quadro.itemquadroacesso_set.values_list('militar_id', flat=True)
            
            # Buscar praças que não estão no quadro
            if quadro.tipo == 'MERECIMENTO':
                # Para merecimento: apenas 2º e 1º sargentos
                pracas = Militar.objects.filter(
                    situacao='AT',
                    posto_graduacao__in=['2S', '1S'],  # Apenas 2º e 1º sargentos
                    apto_inspecao_saude=True,
                    nome_completo__icontains=termo
                ).exclude(
                    id__in=militares_no_quadro
                )[:10]
            else:
                # Para antiguidade: todas as praças
                pracas = Militar.objects.filter(
                    situacao='AT',
                    posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST'],
                    apto_inspecao_saude=True,
                    nome_completo__icontains=termo
                ).exclude(
                    id__in=militares_no_quadro
                )[:10]
            
            # Filtrar apenas as elegíveis
            militares_elegiveis = []
            for praca in pracas:
                ficha = praca.fichaconceitooficiais_set.first() or praca.fichaconceitopracas_set.first()
                
                # Para merecimento, só incluir se tiver ficha de conceito
                if quadro.criterio_ordenacao_manual == 'MERECIMENTO':
                    if ficha:
                        from .utils import criptografar_cpf_lgpd
                        militares_elegiveis.append({
                            'id': praca.id,
                            'nome_completo': praca.nome_completo,
                            'posto_graduacao': praca.posto_graduacao,
                            'quadro': praca.quadro,
                            'cpf': criptografar_cpf_lgpd(praca.cpf),
                            'pontuacao': float(ficha.pontos) if ficha else 0
                        })
                else:  # ANTIGUIDADE - incluir todos os aptos
                    militares_elegiveis.append({
                        'id': praca.id,
                        'nome_completo': praca.nome_completo,
                        'posto_graduacao': praca.posto_graduacao,
                        'quadro': praca.quadro,
                        'cpf': criptografar_cpf_lgpd(praca.cpf),
                        'pontuacao': float(ficha.pontos) if ficha else 0
                    })
            
            return JsonResponse({'militares': militares_elegiveis})
            
        except QuadroAcesso.DoesNotExist:
            return JsonResponse({'militares': []})
    
    return JsonResponse({'militares': []}) 


@login_required
def quadros_manuais_pracas_list(request):
    """Lista todos os quadros de acesso de praças criados manualmente"""
    quadros = QuadroAcesso.objects.filter(status='EM_ELABORACAO').order_by('-data_promocao', '-data_criacao')
    context = {
        'quadros': quadros,
        'is_pracas': True,
    }
    return render(request, 'militares/quadros_manuais_pracas_list.html', context) 


@login_required
def assinar_quadro_acesso_pracas(request, pk):
    """Assinar quadro de acesso de praças com confirmação de senha"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar se o quadro é de praças
    if quadro.categoria != 'PRACAS':
        messages.error(request, 'Este quadro não é de praças!')
        return redirect('militares:quadro_acesso_list')
    
    # Verificar permissão de assinatura para praças
    comissao_cpp = ComissaoPromocao.get_comissao_ativa_por_tipo('CPP')
    if not comissao_cpp or not comissao_cpp.pode_assinar_documento_praca(request.user):
        messages.error(request, 'Você não tem permissão para assinar documentos de praças. Apenas membros da CPP podem assinar.')
        return redirect('militares:quadro_acesso_pracas_detail', pk=pk)
    
    if request.method == 'POST':
        senha = request.POST.get('senha')
        observacoes = request.POST.get('observacoes', '')
        tipo_assinatura = request.POST.get('tipo_assinatura', 'APROVACAO')
        
        # Verificar senha do usuário
        if not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            context = {
                'quadro': quadro,
            }
            return render(request, 'militares/assinar_quadro_acesso_pracas.html', context)
        
        # Verificar se já existe uma assinatura deste usuário para este tipo
        assinatura_existente = AssinaturaQuadroAcesso.objects.filter(
            quadro_acesso=quadro,
            assinado_por=request.user,
            tipo_assinatura=tipo_assinatura
        ).first()
        
        if assinatura_existente:
            messages.error(request, f'Você já assinou este quadro como "{assinatura_existente.get_tipo_assinatura_display()}".')
            context = {
                'quadro': quadro,
            }
            return render(request, 'militares/assinar_quadro_acesso_pracas.html', context)
        
        # Obter função atual do usuário
        from militares.models import UsuarioFuncao, MembroComissao
        
        # Primeiro, tentar buscar função na comissão
        membro_comissao = MembroComissao.objects.filter(
            usuario=request.user,
            ativo=True
        ).first()
        
        if membro_comissao and membro_comissao.cargo:
            funcao_atual = f"{membro_comissao.get_tipo_display()} - {membro_comissao.cargo.nome}"
        elif membro_comissao:
            funcao_atual = membro_comissao.get_tipo_display()
        else:
            # Se não for membro de comissão, buscar função ativa do usuário
            funcao_usuario = UsuarioFuncao.objects.filter(
                usuario=request.user,
                status='ATIVO'
            ).first()
            
            if funcao_usuario:
                funcao_atual = funcao_usuario.cargo_funcao.nome
            else:
                funcao_atual = "Usuário do Sistema"
        
        # Capturar função/cargo da sessão
        funcao_atual = request.session.get('funcao_atual_nome', 'Usuário do Sistema')
        
        # Criar a assinatura
        assinatura = AssinaturaQuadroAcesso.objects.create(
            quadro_acesso=quadro,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura=tipo_assinatura,
            funcao_assinatura=funcao_atual
        )
        
        messages.success(request, f'Quadro de acesso de praças assinado com sucesso como "{assinatura.get_tipo_assinatura_display()}"!')
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/assinar_quadro_acesso_pracas.html', context)





@login_required
def adicionar_militar_quadro_pracas(request, pk):
    """Adiciona um militar ao quadro de acesso de praças via modal"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado.')
        return redirect('militares:quadro_acesso_pracas_list')
    
    # Verificar se o quadro é de praças
    if quadro.categoria != 'PRACAS':
        messages.error(request, 'Este quadro não é de praças!')
        return redirect('militares:quadro_acesso_list')
    
    if quadro.status == 'HOMOLOGADO':
        messages.error(request, 'Quadros homologados não podem ser editados.')
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    
    if request.method == 'POST':
        militar_id = request.POST.get('militar_id')
        posicao = request.POST.get('posicao')
        pontuacao = request.POST.get('pontuacao', 0)
        motivo_insercao = request.POST.get('motivo_insercao', 'AUTOMATICO')
        observacoes_insercao = request.POST.get('observacoes_insercao', '')
        documento_referencia = request.POST.get('documento_referencia', '')
        data_documento = request.POST.get('data_documento', '')
        
        if not militar_id:
            messages.error(request, 'Selecione um militar.')
            return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
        
        try:
            militar = Militar.objects.get(pk=militar_id)
            
            # Permitir adicionar qualquer militar (praças e oficiais) por motivos especiais
            # Apenas verificar se está ativo
            if militar.situacao != 'AT':
                messages.error(request, 'Apenas militares em situação ativa podem ser adicionados ao quadro.')
                return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
            
            # Verificar se está apto em inspeção de saúde (apenas aviso, não impede)
            if not militar.apto_inspecao_saude:
                messages.warning(request, f'ATENÇÃO: {militar.nome_completo} não está apto em inspeção de saúde, mas pode ser adicionado por motivos especiais.')
            
            # Converter posição para inteiro se fornecida
            posicao_int = None
            if posicao:
                try:
                    posicao_int = int(posicao)
                except ValueError:
                    messages.error(request, 'Posição deve ser um número inteiro.')
                    return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
            
            # Converter pontuação para decimal
            try:
                pontuacao_decimal = float(pontuacao)
            except ValueError:
                pontuacao_decimal = 0
            
            # Converter data do documento se fornecida
            data_documento_obj = None
            if data_documento:
                try:
                    from datetime import datetime
                    data_documento_obj = datetime.strptime(data_documento, '%Y-%m-%d').date()
                except ValueError:
                    messages.error(request, 'Data do documento deve estar no formato AAAA-MM-DD.')
                    return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
            
            # Adicionar militar ao quadro com os novos campos
            quadro.adicionar_militar_manual(
                militar, 
                posicao_int, 
                pontuacao_decimal,
                motivo_insercao,
                observacoes_insercao,
                documento_referencia,
                data_documento_obj
            )
            
            # Mensagem específica baseada no motivo
            if motivo_insercao == 'AUTOMATICO':
                messages.success(request, f'Militar {militar.nome_completo} adicionado ao quadro automaticamente!')
            else:
                messages.success(request, f'Militar {militar.nome_completo} adicionado ao quadro por {dict(ItemQuadroAcesso.MOTIVO_INSERCAO_CHOICES)[motivo_insercao]}!')
            
        except Militar.DoesNotExist:
            messages.error(request, 'Militar não encontrado.')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao adicionar militar: {str(e)}')
    
    return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)


@login_required
def buscar_pracas_disponiveis_modal(request, pk):
    """Busca militares elegíveis para adicionar ao quadro via modal, mas permite busca manual para outros."""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        return JsonResponse({'militares': []})

    militares_no_quadro = quadro.itemquadroacesso_set.values_list('militar_id', flat=True)
    termo = request.GET.get('termo', '').strip()

    # Determinar filtro base conforme categoria do quadro
    if quadro.categoria == 'PRACAS':
        # Para quadros de praças, filtrar por posto específico se for merecimento
        if quadro.tipo == 'MERECIMENTO':
            # Para merecimento: apenas 2º e 1º sargentos
            base_qs = Militar.objects.filter(
                situacao='AT', 
                quadro='PRACAS',
                posto_graduacao__in=['2S', '1S']  # Apenas 2º e 1º sargentos
            ).exclude(id__in=militares_no_quadro)
        else:
            # Para antiguidade: todas as praças
            base_qs = Militar.objects.filter(situacao='AT', quadro='PRACAS').exclude(id__in=militares_no_quadro)
    elif quadro.categoria == 'OFICIAIS':
        # Oficiais elegíveis: ativos, quadro diferente de 'PRACAS', não estão no quadro
        base_qs = Militar.objects.filter(situacao='AT').exclude(quadro='PRACAS').exclude(id__in=militares_no_quadro)
    else:
        return JsonResponse({'militares': []})

    # Se termo de busca, permitir buscar qualquer militar ativo (praça ou oficial), exceto já no quadro
    if termo:
        qs = Militar.objects.filter(situacao='AT').exclude(id__in=militares_no_quadro)
        qs = qs.filter(
            Q(nome_completo__icontains=termo) |
            Q(matricula__icontains=termo)
        )
    else:
        qs = base_qs

    qs = qs.order_by('posto_graduacao', 'nome_completo')

    militares_data = []
    for militar in qs:
        ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
        pontuacao = float(ficha.pontos) if ficha else 0
        tipo_militar = "Praça" if militar.posto_graduacao in ['SD', 'CAB', '3S', '2S', '1S', 'ST'] else "Oficial"
        militares_data.append({
            'id': militar.id,
            'nome_completo': militar.nome_completo,
            'posto_graduacao': militar.get_posto_graduacao_display(),
            'quadro': militar.get_quadro_display(),
            'matricula': militar.matricula,
            'pontuacao': pontuacao,
            'numeracao_antiguidade': militar.numeracao_antiguidade or 0,
            'tempo_posto': militar.tempo_posto_atual(),
            'tempo_servico': militar.tempo_servico(),
            'idade': militar.idade(),
            'cpf_mascarado': f"{militar.cpf[:3]}.***.***-{militar.cpf[-2:]}",
            'tipo_militar': tipo_militar,
            'apto_inspecao': militar.apto_inspecao_saude
        })

    return JsonResponse({'militares': militares_data})


@login_required
def remover_militar_quadro_pracas(request, pk, militar_id):
    """Remove um militar do quadro de acesso de praças"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado.')
        return redirect('militares:quadro_acesso_pracas_list')
    
    # Verificar se o quadro é de praças
    if quadro.categoria != 'PRACAS':
        messages.error(request, 'Este quadro não é de praças!')
        return redirect('militares:quadro_acesso_list')
    
    if quadro.status == 'HOMOLOGADO':
        messages.error(request, 'Quadros homologados não podem ser editados.')
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
    
    try:
        militar = Militar.objects.get(pk=militar_id)
        
        # Verificar se o militar está no quadro
        item = quadro.itemquadroacesso_set.filter(militar=militar).first()
        if not item:
            messages.error(request, f'A praça {militar.nome_completo} não está no quadro.')
            return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)
        
        # Remover o militar
        quadro.remover_militar_manual(militar)
        
        messages.success(request, f'Praça {militar.nome_completo} removida do quadro com sucesso!')
    except Militar.DoesNotExist:
        messages.error(request, 'Militar não encontrado.')
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Erro ao remover militar: {str(e)}')
    
    return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)


from .decorators import can_edit_ficha_conceito

@login_required
def ficha_conceito_pracas_form(request, militar_pk):
    """Formulário de ficha de conceito de praças com upload de documentos"""
    # Verificar permissão
    if not can_edit_ficha_conceito(request.user):
        messages.error(request, 'Você não tem permissão para editar fichas de conceito. Apenas administradores, chefes da seção de promoções e diretores de gestão de pessoas podem editar.')
        return redirect('militares:ficha_conceito_pracas_list')
    militar = get_object_or_404(Militar, pk=militar_pk)
    
    # Verificar se o militar é realmente uma praça
    if militar.is_oficial():
        messages.error(request, 'Este militar é um oficial. Use o formulário de oficiais.')
        return redirect('militares:militar_detail', pk=militar_pk)
    
    # Verificar se já existe uma ficha para este militar
    ficha_existente = FichaConceitoPracas.objects.filter(militar=militar).first()
    
    if request.method == 'POST':
        
        if ficha_existente:
            # Se já existe, atualizar a ficha existente
            form = FichaConceitoPracasForm(request.POST, request.FILES, instance=ficha_existente, militar=militar)
        else:
            # Se não existe, criar nova ficha
            form = FichaConceitoPracasForm(request.POST, request.FILES, militar=militar)
        
        if form.is_valid():
            ficha = form.save(commit=False)
            ficha.militar = militar
            ficha.save()
            
            # Processar documentos se fornecidos
            documentos = request.FILES.getlist('documentos')
            for doc_file in documentos:
                Documento.objects.create(
                    militar=militar,
                    ficha_conceito_pracas=ficha,
                    tipo='OUTROS',
                    titulo=f"Documento: {doc_file.name}",
                    arquivo=doc_file
                )
            
            messages.success(request, 'Ficha de conceito de praças salva com sucesso!')
            return redirect('militares:ficha_conceito_pracas_list')
        else:
            # Debug: mostrar erros do formulário
            print("Erros do formulário:", form.errors)
            messages.error(request, f'Erro ao salvar ficha de conceito: {form.errors}')
    else:
        if ficha_existente:
            # Se já existe, carregar dados da ficha existente
            form = FichaConceitoPracasForm(instance=ficha_existente, militar=militar)
        else:
            # Se não existe, criar formulário vazio
            form = FichaConceitoPracasForm(militar=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'ficha': ficha_existente,
        'documento_form': DocumentoForm(),
        'is_pracas': True,
    }
    
    return render(request, 'militares/ficha_conceito_pracas_form.html', context)


@login_required
def ficha_conceito_pracas_delete(request, pk):
    """Excluir ficha de conceito de praças"""
    try:
        ficha = get_object_or_404(FichaConceitoPracas, pk=pk)
    except:
        messages.error(request, 'Ficha de conceito de praças não encontrada.')
        return redirect('militares:ficha_conceito_pracas_list')
    
    if request.method == 'POST':
        ficha.delete()
        messages.success(request, 'Ficha de conceito de praças excluída com sucesso!')
        return redirect('militares:ficha_conceito_pracas_list')
    
    context = {
        'ficha': ficha,
        'militar': ficha.militar,
    }
    
    return render(request, 'militares/ficha_conceito_pracas_confirm_delete.html', context)


@login_required
def ficha_conceito_pracas_detail(request, pk):
    """Detalhes da ficha de conceito de praças"""
    ficha = get_object_or_404(FichaConceitoPracas, pk=pk)
    
    # Calcular pontos detalhados para exibição
    pontos_detalhados = {
        'tempo_posto': {
            'valor': ficha.tempo_posto,
            'pontos': ficha.tempo_posto * 1.0,
            'limite': None,
            'descricao': 'Tempo de Serviço no Posto Atual'
        },
        'cursos_militares': {
            'valor': ficha.cursos_especializacao,
            'pontos': min((ficha.cursos_especializacao * 2.0), 4.0),
            'limite': 4.0,
            'descricao': 'Conclusão de Cursos Militares'
        },
        'instrutor': {
            'valor': (ficha.cursos_cfsd + ficha.cursos_chc + ficha.cursos_chsgt +
                     ficha.cursos_cas + ficha.cursos_cho),
            'pontos': min((ficha.cursos_cfsd * 0.50 + ficha.cursos_chc * 0.75 +
                          ficha.cursos_chsgt * 1.00 + ficha.cursos_cas * 1.25 +
                          ficha.cursos_cho * 1.50), 5.0),
            'limite': 5.0,
            'descricao': 'Monitor em Cursos Militares'
        },
        'cursos_civis': {
            'valor': (ficha.cursos_civis_tecnico + ficha.cursos_civis_superior + 
                     ficha.cursos_civis_especializacao + ficha.cursos_civis_mestrado + 
                     ficha.cursos_civis_doutorado),
            'pontos': (ficha.cursos_civis_tecnico * 1.75 + ficha.cursos_civis_superior * 3.00 +
                      ficha.cursos_civis_especializacao * 4.00 + ficha.cursos_civis_mestrado * 9.00 +
                      ficha.cursos_civis_doutorado * 15.00),
            'limite': None,
            'descricao': 'Conclusão em Cursos Civis'
        },
        'medalhas': {
            'valor': ficha.medalha_federal + ficha.medalha_estadual + ficha.medalha_cbmepi,
            'pontos': min((ficha.medalha_federal * 0.50 + ficha.medalha_estadual * 0.30 +
                          ficha.medalha_cbmepi * 0.20), 1.0),
            'limite': 1.0,
            'descricao': 'Medalhas e Condecorações'
        },
        'elogios': {
            'valor': ficha.elogio_individual + ficha.elogio_coletivo,
            'pontos': min((ficha.elogio_individual * 0.15 + ficha.elogio_coletivo * 0.10), 0.25), 
            'limite': 0.25,
            'descricao': 'Elogios'
        },
        'punicoes': {
            'valor': ficha.punicao_repreensao + ficha.punicao_detencao + ficha.punicao_prisao,
            'pontos': -(ficha.punicao_repreensao * 1.0 + ficha.punicao_detencao * 2.0 +
                       ficha.punicao_prisao * 5.0),
            'limite': None,
            'descricao': 'Punições'
        },
        'falta_aproveitamento': {
            'valor': ficha.falta_aproveitamento,
            'pontos': -(ficha.falta_aproveitamento * 10.0),
            'limite': None,
            'descricao': 'Falta de Aproveitamento em Cursos Militares'
        }
    }
    
    context = {
        'ficha': ficha,
        'militar': ficha.militar,
        'pontos_detalhados': pontos_detalhados,
        'total_pontos': ficha.calcular_pontos(),
        'tipo_ficha': 'pracas',
    }
    
    response = render(request, 'militares/ficha_conceito_pracas_detail.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
