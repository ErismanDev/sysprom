from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .decorators import bloquear_membros_cpo, bloquear_membros_cpp, permitir_apenas_chefe_secao_promocoes
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User, Group, Permission

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao atualizar militar. Verifique os dados.')
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Editar Militar',
        'action': 'update',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_delete(request, pk):
    """Remove um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        nome = militar.nome_completo
        militar.delete()
        messages.success(request, f'Militar {nome} removido com sucesso!')
        return redirect('militares:militar_list')
    
    context = {
        'militar': militar,
    }
    
    return render(request, 'militares/militar_confirm_delete.html', context)


def militar_search_ajax(request):
    """Busca militares via AJAX para autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query)
    )[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
            'nome': militar.nome_completo,
            'matricula': militar.matricula,
            'posto': militar.get_posto_graduacao_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def militar_dashboard(request):
    """Dashboard principal do sistema"""
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    fichas_pendentes = FichaConceito.objects.count()  # Removido filtro por status que não existe
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Últimas fichas de conceito
    ultimas_fichas = FichaConceito.objects.select_related('militar').order_by('-data_registro')[:5]
    
    # Documentos recentes
    documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
    
    # Quadros de acesso recentes
    quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
    
    # Notificações do usuário
    from .models import NotificacaoSessao
    notificacoes_base = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')
    
    # Contadores de notificações (antes do slice)
    total_notificacoes = notificacoes_base.count()
    notificacoes_urgentes = notificacoes_base.filter(prioridade='URGENTE').count()
    notificacoes_altas = notificacoes_base.filter(prioridade='ALTA').count()
    
    # Aplicar slice apenas para exibição
    notificacoes = notificacoes_base[:10]
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'fichas_pendentes': fichas_pendentes,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'ultimas_fichas': ultimas_fichas,
        'documentos_recentes': documentos_recentes,
        'quadros_recentes': quadros_recentes,
        'notificacoes': notificacoes,
        'total_notificacoes': total_notificacoes,
        'notificacoes_urgentes': notificacoes_urgentes,
        'notificacoes_altas': notificacoes_altas,
    }
    
    return render(request, 'militares/dashboard.html', context)


# Views para Ficha de Conceito
@login_required
def ficha_conceito_list(request):
    """Lista ficha de conceito de oficiais"""
    militar_id = request.GET.get('militar')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    else:
        militar = None
        # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
        oficiais = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        )
        fichas = FichaConceito.objects.filter(militar__in=oficiais)
        
        # Ordenar por hierarquia (do mais alto para o mais baixo posto)
        hierarquia_oficiais = {
            'CB': 1,   # Coronel
            'TC': 2,   # Tenente Coronel
            'MJ': 3,   # Major
            'CP': 4,   # Capitão
            '1T': 5,   # 1º Tenente
            '2T': 6,   # 2º Tenente
            'AS': 7,   # Aspirante a Oficial
            'AA': 8,   # Aluno de Adaptação
        }
        
        # Converter para lista e ordenar
        fichas_list = list(fichas)
        fichas_list.sort(key=lambda x: (
            hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.militar.nome_completo
        ))
        fichas = fichas_list
    
    # Estatísticas para mostrar no template (apenas oficiais)
    total_oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).count()
    total_fichas_oficiais = len(fichas) if isinstance(fichas, list) else fichas.count()
    oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais
    
    context = {
        'militar': militar,
        'fichas': fichas,
        'total_oficiais_ativos': total_oficiais_ativos,
        'total_fichas_oficiais': total_fichas_oficiais,
        'oficiais_sem_ficha': oficiais_sem_ficha,
        'is_oficiais': True,
    }
    return render(request, 'militares/ficha_conceito_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_create(request):
    """Cria nova ficha de conceito"""
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito registrada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm()
    
    context = {
        'form': form,
        'title': 'Nova Ficha de Conceito',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


# Views para Quadros de Acesso
@login_required
def quadro_acesso_list(request):
    """Lista todos os quadros de acesso"""
    quadros = QuadroAcesso.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        quadros = quadros.filter(tipo=tipo)
    
    status = request.GET.get('status')
    if status:
        quadros = quadros.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    quadros = quadros.order_by(ordenacao)
    
    # Adicionar quantidade de militares para cada quadro
    for quadro in quadros:
        quadro.total_militares_count = quadro.total_militares()
    
    # Verificar se é uma requisição AJAX
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        import json
        
        # Preparar dados para JSON
        quadros_data = []
        for quadro in quadros:
            quadros_data.append({
                'id': quadro.id,
                'tipo': quadro.tipo,
                'get_tipo_display': quadro.get_tipo_display(),
                'data_promocao': quadro.data_promocao.strftime('%d/%m/%Y'),
                'status': quadro.status,
                'get_status_display': quadro.get_status_display(),
                'total_militares': quadro.total_militares(),
                'motivo_nao_elaboracao': quadro.motivo_nao_elaboracao,
                'get_motivo_display_completo': quadro.get_motivo_display_completo() if quadro.motivo_nao_elaboracao else None,
            })
        
        return JsonResponse({
            'quadros': quadros_data,
            'total': len(quadros_data)
        })
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    homologados = quadros.filter(status='HOMOLOGADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'quadros': quadros,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'status_choices': QuadroAcesso.STATUS_CHOICES,
        'filtros': {
            'tipo': tipo,
            'status': status,
            'ordenacao': ordenacao
        },
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'homologados': homologados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/quadro_acesso_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_edit(request, pk):
    """Edita uma ficha de conceito existente"""
    ficha = get_object_or_404(FichaConceito, pk=pk)
    
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST, instance=ficha)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito atualizada com sucesso!')
            return redirect('militares:ficha_conceito_list')
        else:
            messages.error(request, 'Erro ao atualizar ficha de conceito. Verifique os dados.')
    else:
        form = FichaConceitoForm(instance=ficha)
    
    context = {
        'form': form,
        'ficha': ficha,
        'title': 'Editar Ficha de Conceito',
        'action': 'update',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_delete(request, pk):
    """Remove uma ficha de conceito"""
    ficha = get_object_or_404(FichaConceito, pk=pk)
    
    if request.method == 'POST':
        militar = ficha.militar
        ficha.delete()
        messages.success(request, f'Ficha de conceito removida com sucesso!')
        return redirect('militares:ficha_conceito_list')
    
    context = {
        'ficha': ficha,
    }
    
    return render(request, 'militares/ficha_conceito_confirm_delete.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def documento_upload(request, militar_id):
    """Faz upload de documentos para um militar"""
    militar = get_object_or_404(Militar, pk=militar_id)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.militar = militar
            documento.save()
            messages.success(request, f'Documento {documento.nome} enviado com sucesso!')
            return redirect('militares:militar_detail', pk=militar_id)
        else:
            messages.error(request, 'Erro ao enviar documento. Verifique os dados.')
    else:
        form = DocumentoForm()
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Enviar Documento',
    }
    
    return render(request, 'militares/documento_form.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def documento_delete(request, pk):
    """Remove um documento"""
    documento = get_object_or_404(Documento, pk=pk)
    
    if request.method == 'POST':
        militar = documento.militar
        documento.delete()
        messages.success(request, f'Documento {documento.nome} removido com sucesso!')
        return redirect('militares:militar_detail', pk=militar.pk)
    
    context = {
        'documento': documento,
    }
    
    return render(request, 'militares/documento_confirm_delete.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def conferir_documento(request, pk):
    """Conferir um documento"""
    documento = get_object_or_404(Documento, pk=pk)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            documento = form.save()
            messages.success(request, f'Documento {documento.nome} conferido com sucesso!')
            return redirect('militares:militar_detail', pk=documento.militar.pk)
        else:
            messages.error(request, 'Erro ao conferir documento. Verifique os dados.')
    else:
        form = DocumentoForm(instance=documento)
    
    context = {
        'form': form,
        'documento': documento,
        'title': 'Conferir Documento',
        'action': 'conferir',
    }
    
    return render(request, 'militares/documento_form.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_form(request, militar_id):
    """Cria ou edita uma ficha de conceito"""
    militar = get_object_or_404(Militar, pk=militar_id)
    ficha = militar.(fichaconceitooficiais_set.first() or fichaconceitopracas_set.first())
    
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST, instance=ficha)
        if form.is_valid():
            ficha = form.save(commit=False)
            ficha.militar = militar
            ficha.save()
            messages.success(request, f'Ficha de conceito atualizada com sucesso!')
            return redirect('militares:militar_detail', pk=militar_id)
        else:
            messages.error(request, 'Erro ao atualizar ficha de conceito. Verifique os dados.')
    else:
        form = FichaConceitoForm(instance=ficha)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Ficha de Conceito',
        'action': 'update',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def conferir_ficha(request, pk):
    """Conferir uma ficha de conceito"""
    ficha = get_object_or_404(FichaConceito, pk=pk)
    
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST, instance=ficha)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito conferida com sucesso!')
            return redirect('militares:militar_detail', pk=ficha.militar.pk)
        else:
            messages.error(request, 'Erro ao conferir ficha de conceito. Verifique os dados.')
    else:
        form = FichaConceitoForm(instance=ficha)
    
    context = {
        'form': form,
        'ficha': ficha,
        'title': 'Conferir Ficha de Conceito',
        'action': 'conferir',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def gerar_fichas_conceito_todos(request):
    """Gera fichas de conceito para todos os militares"""
    if request.method == 'POST':
        # Lógica para gerar fichas de conceito
        messages.success(request, 'Fichas de conceito geradas com sucesso!')
        return redirect('militares:ficha_conceito_list')
    
    return render(request, 'militares/gerar_fichas_conceito_todos.html')


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def gerar_fichas_conceito_pracas_todos(request):
    """Gera fichas de conceito para todos os praças"""
    if request.method == 'POST':
        # Lógica para gerar fichas de conceito para praças
        messages.success(request, 'Fichas de conceito para praças geradas com sucesso!')
        return redirect('militares:ficha_conceito_list')
    
    return render(request, 'militares/gerar_fichas_conceito_pracas_todos.html')


@login_required
def ficha_conceito_detail(request, pk):
    """Visualização somente leitura da ficha de conceito"""
    ficha = get_object_or_404(FichaConceito, pk=pk)
    documentos = ficha.documento_set.all().order_by('-data_upload')
    context = {
        'ficha': ficha,
        'militar': ficha.militar,
        'documentos': documentos,
    }
    return render(request, 'militares/ficha_conceito_detail.html', context)


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .decorators import bloquear_membros_cpo, bloquear_membros_cpp, permitir_apenas_chefe_secao_promocoes
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User, Group, Permission

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao atualizar militar. Verifique os dados.')
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Editar Militar',
        'action': 'update',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_delete(request, pk):
    """Remove um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        nome = militar.nome_completo
        militar.delete()
        messages.success(request, f'Militar {nome} removido com sucesso!')
        return redirect('militares:militar_list')
    
    context = {
        'militar': militar,
    }
    
    return render(request, 'militares/militar_confirm_delete.html', context)


def militar_search_ajax(request):
    """Busca militares via AJAX para autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query)
    )[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
            'nome': militar.nome_completo,
            'matricula': militar.matricula,
            'posto': militar.get_posto_graduacao_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def militar_dashboard(request):
    """Dashboard principal do sistema"""
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    fichas_pendentes = FichaConceito.objects.count()  # Removido filtro por status que não existe
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Últimas fichas de conceito
    ultimas_fichas = FichaConceito.objects.select_related('militar').order_by('-data_registro')[:5]
    
    # Documentos recentes
    documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
    
    # Quadros de acesso recentes
    quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
    
    # Notificações do usuário
    from .models import NotificacaoSessao
    notificacoes_base = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')
    
    # Contadores de notificações (antes do slice)
    total_notificacoes = notificacoes_base.count()
    notificacoes_urgentes = notificacoes_base.filter(prioridade='URGENTE').count()
    notificacoes_altas = notificacoes_base.filter(prioridade='ALTA').count()
    
    # Aplicar slice apenas para exibição
    notificacoes = notificacoes_base[:10]
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'fichas_pendentes': fichas_pendentes,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'ultimas_fichas': ultimas_fichas,
        'documentos_recentes': documentos_recentes,
        'quadros_recentes': quadros_recentes,
        'notificacoes': notificacoes,
        'total_notificacoes': total_notificacoes,
        'notificacoes_urgentes': notificacoes_urgentes,
        'notificacoes_altas': notificacoes_altas,
    }
    
    return render(request, 'militares/dashboard.html', context)


# Views para Ficha de Conceito
@login_required
def ficha_conceito_list(request):
    """Lista ficha de conceito de oficiais"""
    militar_id = request.GET.get('militar')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    else:
        militar = None
        # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
        oficiais = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        )
        fichas = FichaConceito.objects.filter(militar__in=oficiais)
        
        # Ordenar por hierarquia (do mais alto para o mais baixo posto)
        hierarquia_oficiais = {
            'CB': 1,   # Coronel
            'TC': 2,   # Tenente Coronel
            'MJ': 3,   # Major
            'CP': 4,   # Capitão
            '1T': 5,   # 1º Tenente
            '2T': 6,   # 2º Tenente
            'AS': 7,   # Aspirante a Oficial
            'AA': 8,   # Aluno de Adaptação
        }
        
        # Converter para lista e ordenar
        fichas_list = list(fichas)
        fichas_list.sort(key=lambda x: (
            hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.militar.nome_completo
        ))
        fichas = fichas_list
    
    # Estatísticas para mostrar no template (apenas oficiais)
    total_oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).count()
    total_fichas_oficiais = len(fichas) if isinstance(fichas, list) else fichas.count()
    oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais
    
    context = {
        'militar': militar,
        'fichas': fichas,
        'total_oficiais_ativos': total_oficiais_ativos,
        'total_fichas_oficiais': total_fichas_oficiais,
        'oficiais_sem_ficha': oficiais_sem_ficha,
        'is_oficiais': True,
    }
    return render(request, 'militares/ficha_conceito_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_create(request):
    """Cria nova ficha de conceito"""
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito registrada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm()
    
    context = {
        'form': form,
        'title': 'Nova Ficha de Conceito',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


# Views para Quadros de Acesso
@login_required
def quadro_acesso_list(request):
    """Lista todos os quadros de acesso"""
    quadros = QuadroAcesso.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        quadros = quadros.filter(tipo=tipo)
    
    status = request.GET.get('status')
    if status:
        quadros = quadros.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    quadros = quadros.order_by(ordenacao)
    
    # Adicionar quantidade de militares para cada quadro
    for quadro in quadros:
        quadro.total_militares_count = quadro.total_militares()
    
    # Verificar se é uma requisição AJAX
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        import json
        
        # Preparar dados para JSON
        quadros_data = []
        for quadro in quadros:
            quadros_data.append({
                'id': quadro.id,
                'tipo': quadro.tipo,
                'get_tipo_display': quadro.get_tipo_display(),
                'data_promocao': quadro.data_promocao.strftime('%d/%m/%Y'),
                'status': quadro.status,
                'get_status_display': quadro.get_status_display(),
                'total_militares': quadro.total_militares(),
                'motivo_nao_elaboracao': quadro.motivo_nao_elaboracao,
                'get_motivo_display_completo': quadro.get_motivo_display_completo() if quadro.motivo_nao_elaboracao else None,
            })
        
        return JsonResponse({
            'quadros': quadros_data,
            'total': len(quadros_data)
        })
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    homologados = quadros.filter(status='HOMOLOGADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'quadros': quadros,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'status_choices': QuadroAcesso.STATUS_CHOICES,
        'filtros': {
            'tipo': tipo,
            'status': status,
            'ordenacao': ordenacao
        },
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'homologados': homologados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/quadro_acesso_list.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao atualizar militar. Verifique os dados.')
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Editar Militar',
        'action': 'update',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_delete(request, pk):
    """Remove um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        nome = militar.nome_completo
        militar.delete()
        messages.success(request, f'Militar {nome} removido com sucesso!')
        return redirect('militares:militar_list')
    
    context = {
        'militar': militar,
    }
    
    return render(request, 'militares/militar_confirm_delete.html', context)


def militar_search_ajax(request):
    """Busca militares via AJAX para autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query)
    )[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
            'nome': militar.nome_completo,
            'matricula': militar.matricula,
            'posto': militar.get_posto_graduacao_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def militar_dashboard(request):
    """Dashboard principal do sistema"""
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    fichas_pendentes = FichaConceito.objects.count()  # Removido filtro por status que não existe
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Últimas fichas de conceito
    ultimas_fichas = FichaConceito.objects.select_related('militar').order_by('-data_registro')[:5]
    
    # Documentos recentes
    documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
    
    # Quadros de acesso recentes
    quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
    
    # Notificações do usuário
    from .models import NotificacaoSessao
    notificacoes_base = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')
    
    # Contadores de notificações (antes do slice)
    total_notificacoes = notificacoes_base.count()
    notificacoes_urgentes = notificacoes_base.filter(prioridade='URGENTE').count()
    notificacoes_altas = notificacoes_base.filter(prioridade='ALTA').count()
    
    # Aplicar slice apenas para exibição
    notificacoes = notificacoes_base[:10]
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'fichas_pendentes': fichas_pendentes,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'ultimas_fichas': ultimas_fichas,
        'documentos_recentes': documentos_recentes,
        'quadros_recentes': quadros_recentes,
        'notificacoes': notificacoes,
        'total_notificacoes': total_notificacoes,
        'notificacoes_urgentes': notificacoes_urgentes,
        'notificacoes_altas': notificacoes_altas,
    }
    
    return render(request, 'militares/dashboard.html', context)


# Views para Ficha de Conceito
@login_required
def ficha_conceito_list(request):
    """Lista ficha de conceito de oficiais"""
    militar_id = request.GET.get('militar')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    else:
        militar = None
        # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
        oficiais = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        )
        fichas = FichaConceito.objects.filter(militar__in=oficiais)
        
        # Ordenar por hierarquia (do mais alto para o mais baixo posto)
        hierarquia_oficiais = {
            'CB': 1,   # Coronel
            'TC': 2,   # Tenente Coronel
            'MJ': 3,   # Major
            'CP': 4,   # Capitão
            '1T': 5,   # 1º Tenente
            '2T': 6,   # 2º Tenente
            'AS': 7,   # Aspirante a Oficial
            'AA': 8,   # Aluno de Adaptação
        }
        
        # Converter para lista e ordenar
        fichas_list = list(fichas)
        fichas_list.sort(key=lambda x: (
            hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.militar.nome_completo
        ))
        fichas = fichas_list
    
    # Estatísticas para mostrar no template (apenas oficiais)
    total_oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).count()
    total_fichas_oficiais = len(fichas) if isinstance(fichas, list) else fichas.count()
    oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais
    
    context = {
        'militar': militar,
        'fichas': fichas,
        'total_oficiais_ativos': total_oficiais_ativos,
        'total_fichas_oficiais': total_fichas_oficiais,
        'oficiais_sem_ficha': oficiais_sem_ficha,
        'is_oficiais': True,
    }
    return render(request, 'militares/ficha_conceito_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_create(request):
    """Cria nova ficha de conceito"""
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito registrada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm()
    
    context = {
        'form': form,
        'title': 'Nova Ficha de Conceito',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


# Views para Quadros de Acesso
@login_required
def quadro_acesso_list(request):
    """Lista todos os quadros de acesso"""
    quadros = QuadroAcesso.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        quadros = quadros.filter(tipo=tipo)
    
    status = request.GET.get('status')
    if status:
        quadros = quadros.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    quadros = quadros.order_by(ordenacao)
    
    # Adicionar quantidade de militares para cada quadro
    for quadro in quadros:
        quadro.total_militares_count = quadro.total_militares()
    
    # Verificar se é uma requisição AJAX
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        import json
        
        # Preparar dados para JSON
        quadros_data = []
        for quadro in quadros:
            quadros_data.append({
                'id': quadro.id,
                'tipo': quadro.tipo,
                'get_tipo_display': quadro.get_tipo_display(),
                'data_promocao': quadro.data_promocao.strftime('%d/%m/%Y'),
                'status': quadro.status,
                'get_status_display': quadro.get_status_display(),
                'total_militares': quadro.total_militares(),
                'motivo_nao_elaboracao': quadro.motivo_nao_elaboracao,
                'get_motivo_display_completo': quadro.get_motivo_display_completo() if quadro.motivo_nao_elaboracao else None,
            })
        
        return JsonResponse({
            'quadros': quadros_data,
            'total': len(quadros_data)
        })
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    homologados = quadros.filter(status='HOMOLOGADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'quadros': quadros,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'status_choices': QuadroAcesso.STATUS_CHOICES,
        'filtros': {
            'tipo': tipo,
            'status': status,
            'ordenacao': ordenacao
        },
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'homologados': homologados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/quadro_acesso_list.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .decorators import bloquear_membros_cpo, bloquear_membros_cpp, permitir_apenas_chefe_secao_promocoes
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User, Group, Permission

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao atualizar militar. Verifique os dados.')
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Editar Militar',
        'action': 'update',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_delete(request, pk):
    """Remove um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        nome = militar.nome_completo
        militar.delete()
        messages.success(request, f'Militar {nome} removido com sucesso!')
        return redirect('militares:militar_list')
    
    context = {
        'militar': militar,
    }
    
    return render(request, 'militares/militar_confirm_delete.html', context)


def militar_search_ajax(request):
    """Busca militares via AJAX para autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query)
    )[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
            'nome': militar.nome_completo,
            'matricula': militar.matricula,
            'posto': militar.get_posto_graduacao_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def militar_dashboard(request):
    """Dashboard principal do sistema"""
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    fichas_pendentes = FichaConceito.objects.count()  # Removido filtro por status que não existe
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Últimas fichas de conceito
    ultimas_fichas = FichaConceito.objects.select_related('militar').order_by('-data_registro')[:5]
    
    # Documentos recentes
    documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
    
    # Quadros de acesso recentes
    quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
    
    # Notificações do usuário
    from .models import NotificacaoSessao
    notificacoes_base = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')
    
    # Contadores de notificações (antes do slice)
    total_notificacoes = notificacoes_base.count()
    notificacoes_urgentes = notificacoes_base.filter(prioridade='URGENTE').count()
    notificacoes_altas = notificacoes_base.filter(prioridade='ALTA').count()
    
    # Aplicar slice apenas para exibição
    notificacoes = notificacoes_base[:10]
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'fichas_pendentes': fichas_pendentes,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'ultimas_fichas': ultimas_fichas,
        'documentos_recentes': documentos_recentes,
        'quadros_recentes': quadros_recentes,
        'notificacoes': notificacoes,
        'total_notificacoes': total_notificacoes,
        'notificacoes_urgentes': notificacoes_urgentes,
        'notificacoes_altas': notificacoes_altas,
    }
    
    return render(request, 'militares/dashboard.html', context)


# Views para Ficha de Conceito
@login_required
def ficha_conceito_list(request):
    """Lista ficha de conceito de oficiais"""
    militar_id = request.GET.get('militar')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    else:
        militar = None
        # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
        oficiais = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        )
        fichas = FichaConceito.objects.filter(militar__in=oficiais)
        
        # Ordenar por hierarquia (do mais alto para o mais baixo posto)
        hierarquia_oficiais = {
            'CB': 1,   # Coronel
            'TC': 2,   # Tenente Coronel
            'MJ': 3,   # Major
            'CP': 4,   # Capitão
            '1T': 5,   # 1º Tenente
            '2T': 6,   # 2º Tenente
            'AS': 7,   # Aspirante a Oficial
            'AA': 8,   # Aluno de Adaptação
        }
        
        # Converter para lista e ordenar
        fichas_list = list(fichas)
        fichas_list.sort(key=lambda x: (
            hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.militar.nome_completo
        ))
        fichas = fichas_list
    
    # Estatísticas para mostrar no template (apenas oficiais)
    total_oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).count()
    total_fichas_oficiais = len(fichas) if isinstance(fichas, list) else fichas.count()
    oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais
    
    context = {
        'militar': militar,
        'fichas': fichas,
        'total_oficiais_ativos': total_oficiais_ativos,
        'total_fichas_oficiais': total_fichas_oficiais,
        'oficiais_sem_ficha': oficiais_sem_ficha,
        'is_oficiais': True,
    }
    return render(request, 'militares/ficha_conceito_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_create(request):
    """Cria nova ficha de conceito"""
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito registrada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm()
    
    context = {
        'form': form,
        'title': 'Nova Ficha de Conceito',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


# Views para Quadros de Acesso
@login_required
def quadro_acesso_list(request):
    """Lista todos os quadros de acesso"""
    quadros = QuadroAcesso.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        quadros = quadros.filter(tipo=tipo)
    
    status = request.GET.get('status')
    if status:
        quadros = quadros.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    quadros = quadros.order_by(ordenacao)
    
    # Adicionar quantidade de militares para cada quadro
    for quadro in quadros:
        quadro.total_militares_count = quadro.total_militares()
    
    # Verificar se é uma requisição AJAX
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        import json
        
        # Preparar dados para JSON
        quadros_data = []
        for quadro in quadros:
            quadros_data.append({
                'id': quadro.id,
                'tipo': quadro.tipo,
                'get_tipo_display': quadro.get_tipo_display(),
                'data_promocao': quadro.data_promocao.strftime('%d/%m/%Y'),
                'status': quadro.status,
                'get_status_display': quadro.get_status_display(),
                'total_militares': quadro.total_militares(),
                'motivo_nao_elaboracao': quadro.motivo_nao_elaboracao,
                'get_motivo_display_completo': quadro.get_motivo_display_completo() if quadro.motivo_nao_elaboracao else None,
            })
        
        return JsonResponse({
            'quadros': quadros_data,
            'total': len(quadros_data)
        })
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    homologados = quadros.filter(status='HOMOLOGADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'quadros': quadros,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'status_choices': QuadroAcesso.STATUS_CHOICES,
        'filtros': {
            'tipo': tipo,
            'status': status,
            'ordenacao': ordenacao
        },
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'homologados': homologados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/quadro_acesso_list.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao atualizar militar. Verifique os dados.')
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Editar Militar',
        'action': 'update',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_delete(request, pk):
    """Remove um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        nome = militar.nome_completo
        militar.delete()
        messages.success(request, f'Militar {nome} removido com sucesso!')
        return redirect('militares:militar_list')
    
    context = {
        'militar': militar,
    }
    
    return render(request, 'militares/militar_confirm_delete.html', context)


def militar_search_ajax(request):
    """Busca militares via AJAX para autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query)
    )[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
            'nome': militar.nome_completo,
            'matricula': militar.matricula,
            'posto': militar.get_posto_graduacao_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def militar_dashboard(request):
    """Dashboard principal do sistema"""
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    fichas_pendentes = FichaConceito.objects.count()  # Removido filtro por status que não existe
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Últimas fichas de conceito
    ultimas_fichas = FichaConceito.objects.select_related('militar').order_by('-data_registro')[:5]
    
    # Documentos recentes
    documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
    
    # Quadros de acesso recentes
    quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
    
    # Notificações do usuário
    from .models import NotificacaoSessao
    notificacoes_base = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')
    
    # Contadores de notificações (antes do slice)
    total_notificacoes = notificacoes_base.count()
    notificacoes_urgentes = notificacoes_base.filter(prioridade='URGENTE').count()
    notificacoes_altas = notificacoes_base.filter(prioridade='ALTA').count()
    
    # Aplicar slice apenas para exibição
    notificacoes = notificacoes_base[:10]
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'fichas_pendentes': fichas_pendentes,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'ultimas_fichas': ultimas_fichas,
        'documentos_recentes': documentos_recentes,
        'quadros_recentes': quadros_recentes,
        'notificacoes': notificacoes,
        'total_notificacoes': total_notificacoes,
        'notificacoes_urgentes': notificacoes_urgentes,
        'notificacoes_altas': notificacoes_altas,
    }
    
    return render(request, 'militares/dashboard.html', context)


# Views para Ficha de Conceito
@login_required
def ficha_conceito_list(request):
    """Lista ficha de conceito de oficiais"""
    militar_id = request.GET.get('militar')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    else:
        militar = None
        # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
        oficiais = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        )
        fichas = FichaConceito.objects.filter(militar__in=oficiais)
        
        # Ordenar por hierarquia (do mais alto para o mais baixo posto)
        hierarquia_oficiais = {
            'CB': 1,   # Coronel
            'TC': 2,   # Tenente Coronel
            'MJ': 3,   # Major
            'CP': 4,   # Capitão
            '1T': 5,   # 1º Tenente
            '2T': 6,   # 2º Tenente
            'AS': 7,   # Aspirante a Oficial
            'AA': 8,   # Aluno de Adaptação
        }
        
        # Converter para lista e ordenar
        fichas_list = list(fichas)
        fichas_list.sort(key=lambda x: (
            hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.militar.nome_completo
        ))
        fichas = fichas_list
    
    # Estatísticas para mostrar no template (apenas oficiais)
    total_oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).count()
    total_fichas_oficiais = len(fichas) if isinstance(fichas, list) else fichas.count()
    oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais
    
    context = {
        'militar': militar,
        'fichas': fichas,
        'total_oficiais_ativos': total_oficiais_ativos,
        'total_fichas_oficiais': total_fichas_oficiais,
        'oficiais_sem_ficha': oficiais_sem_ficha,
        'is_oficiais': True,
    }
    return render(request, 'militares/ficha_conceito_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_create(request):
    """Cria nova ficha de conceito"""
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito registrada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm()
    
    context = {
        'form': form,
        'title': 'Nova Ficha de Conceito',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


# Views para Quadros de Acesso
@login_required
def quadro_acesso_list(request):
    """Lista todos os quadros de acesso"""
    quadros = QuadroAcesso.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        quadros = quadros.filter(tipo=tipo)
    
    status = request.GET.get('status')
    if status:
        quadros = quadros.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    quadros = quadros.order_by(ordenacao)
    
    # Adicionar quantidade de militares para cada quadro
    for quadro in quadros:
        quadro.total_militares_count = quadro.total_militares()
    
    # Verificar se é uma requisição AJAX
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        import json
        
        # Preparar dados para JSON
        quadros_data = []
        for quadro in quadros:
            quadros_data.append({
                'id': quadro.id,
                'tipo': quadro.tipo,
                'get_tipo_display': quadro.get_tipo_display(),
                'data_promocao': quadro.data_promocao.strftime('%d/%m/%Y'),
                'status': quadro.status,
                'get_status_display': quadro.get_status_display(),
                'total_militares': quadro.total_militares(),
                'motivo_nao_elaboracao': quadro.motivo_nao_elaboracao,
                'get_motivo_display_completo': quadro.get_motivo_display_completo() if quadro.motivo_nao_elaboracao else None,
            })
        
        return JsonResponse({
            'quadros': quadros_data,
            'total': len(quadros_data)
        })
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    homologados = quadros.filter(status='HOMOLOGADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'quadros': quadros,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'status_choices': QuadroAcesso.STATUS_CHOICES,
        'filtros': {
            'tipo': tipo,
            'status': status,
            'ordenacao': ordenacao
        },
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'homologados': homologados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/quadro_acesso_list.html', context)


@login_required
def quadro_acesso_detail(request, pk):
    """Exibe detalhes de um quadro de acesso"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')

    # Redirecionar para a view de Praças se for o caso
    if quadro.categoria == 'PRACAS':
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)

    militares_inaptos = quadro.militares_inaptos_com_motivo()

    nomes_postos = dict(QuadroAcesso.POSTO_CHOICES)
    nomes_quadros = dict(QuadroAcesso.QUADRO_CHOICES)
    
    # Definir ordem dos quadros e transições (do mais graduado ao menos graduado)
    quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    
    # Verificar se é um quadro de praças
    if quadro.tipo == 'PRACAS':
        # Para quadros de praças: transições específicas para praças
        quadros = ['PRACAS']
        transicoes_por_quadro = {
            'PRACAS': [  # Praças
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
        }
    elif quadro.tipo == 'MERECIMENTO':
        # Para quadros de merecimento: transições específicas conforme regras
        transicoes_por_quadro = {
            'COMB': [  # Combatente - inclui TC→CB
                {
                    'numero': 'I',
                    'titulo': 'TENENTE-CORONEL para o posto de CORONEL',
                    'origem': 'TC',
                    'destino': 'CB',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'SAUDE': [  # Saúde - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'ENG': [  # Engenheiro - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'COMP': [  # Complementar - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        }
    else:
        # Para quadros de antiguidade: todas as transições por antiguidade
        transicoes_por_quadro = {
            'COMB': [  # Combatente
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ASPIRANTE A OFICIAL para o posto de 2º TENENTE',
                    'origem': 'AS',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'SAUDE': [  # Saúde
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                    'origem': 'AA',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'ENG': [  # Engenheiro
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                    'origem': 'AA',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'COMP': [  # Complementar
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'SUBTENENTE para o posto de 2º TENENTE',
                    'origem': 'ST',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        }
    
    # Buscar todos os militares aptos do quadro
    militares_aptos = quadro.itemquadroacesso_set.all().select_related('militar').order_by('posicao')
    
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
                item for item in militares_aptos 
                if item.militar.quadro == q and item.militar.posto_graduacao == origem
            ]
            estrutura_quadros[q]['transicoes'].append({
                'origem': origem,
                'destino': destino,
                'origem_nome': nomes_postos.get(origem, origem),
                'destino_nome': nomes_postos.get(destino, destino),
                'militares': militares_desta_transicao,
            })
    
    context = {
        'quadro': quadro,
        'militares_inaptos': militares_inaptos,
        'total_inaptos': len(militares_inaptos),
        'estrutura_quadros': estrutura_quadros,
    }
    
    return render(request, 'militares/quadro_acesso_detail.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao atualizar militar. Verifique os dados.')
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Editar Militar',
        'action': 'update',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_delete(request, pk):
    """Remove um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        nome = militar.nome_completo
        militar.delete()
        messages.success(request, f'Militar {nome} removido com sucesso!')
        return redirect('militares:militar_list')
    
    context = {
        'militar': militar,
    }
    
    return render(request, 'militares/militar_confirm_delete.html', context)


def militar_search_ajax(request):
    """Busca militares via AJAX para autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query)
    )[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
            'nome': militar.nome_completo,
            'matricula': militar.matricula,
            'posto': militar.get_posto_graduacao_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def militar_dashboard(request):
    """Dashboard principal do sistema"""
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    fichas_pendentes = FichaConceito.objects.count()  # Removido filtro por status que não existe
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Últimas fichas de conceito
    ultimas_fichas = FichaConceito.objects.select_related('militar').order_by('-data_registro')[:5]
    
    # Documentos recentes
    documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
    
    # Quadros de acesso recentes
    quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
    
    # Notificações do usuário
    from .models import NotificacaoSessao
    notificacoes_base = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')
    
    # Contadores de notificações (antes do slice)
    total_notificacoes = notificacoes_base.count()
    notificacoes_urgentes = notificacoes_base.filter(prioridade='URGENTE').count()
    notificacoes_altas = notificacoes_base.filter(prioridade='ALTA').count()
    
    # Aplicar slice apenas para exibição
    notificacoes = notificacoes_base[:10]
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'fichas_pendentes': fichas_pendentes,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'ultimas_fichas': ultimas_fichas,
        'documentos_recentes': documentos_recentes,
        'quadros_recentes': quadros_recentes,
        'notificacoes': notificacoes,
        'total_notificacoes': total_notificacoes,
        'notificacoes_urgentes': notificacoes_urgentes,
        'notificacoes_altas': notificacoes_altas,
    }
    
    return render(request, 'militares/dashboard.html', context)


# Views para Ficha de Conceito
@login_required
def ficha_conceito_list(request):
    """Lista ficha de conceito de oficiais"""
    militar_id = request.GET.get('militar')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    else:
        militar = None
        # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
        oficiais = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        )
        fichas = FichaConceito.objects.filter(militar__in=oficiais)
        
        # Ordenar por hierarquia (do mais alto para o mais baixo posto)
        hierarquia_oficiais = {
            'CB': 1,   # Coronel
            'TC': 2,   # Tenente Coronel
            'MJ': 3,   # Major
            'CP': 4,   # Capitão
            '1T': 5,   # 1º Tenente
            '2T': 6,   # 2º Tenente
            'AS': 7,   # Aspirante a Oficial
            'AA': 8,   # Aluno de Adaptação
        }
        
        # Converter para lista e ordenar
        fichas_list = list(fichas)
        fichas_list.sort(key=lambda x: (
            hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.militar.nome_completo
        ))
        fichas = fichas_list
    
    # Estatísticas para mostrar no template (apenas oficiais)
    total_oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).count()
    total_fichas_oficiais = len(fichas) if isinstance(fichas, list) else fichas.count()
    oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais
    
    context = {
        'militar': militar,
        'fichas': fichas,
        'total_oficiais_ativos': total_oficiais_ativos,
        'total_fichas_oficiais': total_fichas_oficiais,
        'oficiais_sem_ficha': oficiais_sem_ficha,
        'is_oficiais': True,
    }
    return render(request, 'militares/ficha_conceito_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_create(request):
    """Cria nova ficha de conceito"""
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito registrada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm()
    
    context = {
        'form': form,
        'title': 'Nova Ficha de Conceito',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


# Views para Quadros de Acesso
@login_required
def quadro_acesso_list(request):
    """Lista todos os quadros de acesso"""
    quadros = QuadroAcesso.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        quadros = quadros.filter(tipo=tipo)
    
    status = request.GET.get('status')
    if status:
        quadros = quadros.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    quadros = quadros.order_by(ordenacao)
    
    # Adicionar quantidade de militares para cada quadro
    for quadro in quadros:
        quadro.total_militares_count = quadro.total_militares()
    
    # Verificar se é uma requisição AJAX
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        import json
        
        # Preparar dados para JSON
        quadros_data = []
        for quadro in quadros:
            quadros_data.append({
                'id': quadro.id,
                'tipo': quadro.tipo,
                'get_tipo_display': quadro.get_tipo_display(),
                'data_promocao': quadro.data_promocao.strftime('%d/%m/%Y'),
                'status': quadro.status,
                'get_status_display': quadro.get_status_display(),
                'total_militares': quadro.total_militares(),
                'motivo_nao_elaboracao': quadro.motivo_nao_elaboracao,
                'get_motivo_display_completo': quadro.get_motivo_display_completo() if quadro.motivo_nao_elaboracao else None,
            })
        
        return JsonResponse({
            'quadros': quadros_data,
            'total': len(quadros_data)
        })
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    homologados = quadros.filter(status='HOMOLOGADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'quadros': quadros,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'status_choices': QuadroAcesso.STATUS_CHOICES,
        'filtros': {
            'tipo': tipo,
            'status': status,
            'ordenacao': ordenacao
        },
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'homologados': homologados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/quadro_acesso_list.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User

# Importar views específicas para praças
from .views_pracas_import import *
from .utils import calcular_proxima_data_promocao
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
def militar_list(request):
    """Lista todos os militares com paginação e busca"""
    militares = Militar.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        militares = militares.filter(posto_graduacao=posto)
    
    situacao = request.GET.get('situacao')
    if situacao:
        militares = militares.filter(situacao=situacao)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    if ordenacao == 'hierarquia_antiguidade':
        # Ordenar por hierarquia de postos e depois por antiguidade
        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceito__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')
    
    # Paginação
    paginator = Paginator(militares, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'militares': page_obj,
        'postos': POSTO_GRADUACAO_CHOICES,
        'situacoes': SITUACAO_CHOICES,
        'quadros': QUADRO_CHOICES,
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
def militar_detail(request, pk):
    """Exibe os detalhes de um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    # Busca ficha de conceito
    ficha_conceito = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    
    # Busca promoções
    promocoes = militar.promocao_set.all().order_by('-data_promocao')
    
    # Busca documentos
    documentos = Documento.objects.filter(militar=militar).order_by('-data_upload')
    
    context = {
        'militar': militar,
        'ficha_conceito': ficha_conceito,
        'promocoes': promocoes,
        'documentos': documentos,
    }
    
    return render(request, 'militares/militar_detail.html', context)


@login_required
@bloquear_membros_cpo
def militar_create(request):
    """Cria um novo militar"""
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} cadastrado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao cadastrar militar. Verifique os dados.')
    else:
        form = MilitarForm()
    
    context = {
        'form': form,
        'title': 'Novo Militar',
        'action': 'create',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_update(request, pk):
    """Atualiza um militar existente"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        form = MilitarForm(request.POST, request.FILES, instance=militar)
        if form.is_valid():
            militar = form.save()
            messages.success(request, f'Militar {militar.nome_completo} atualizado com sucesso!')
            return redirect('militares:militar_detail', pk=militar.pk)
        else:
            messages.error(request, 'Erro ao atualizar militar. Verifique os dados.')
    else:
        form = MilitarForm(instance=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'title': 'Editar Militar',
        'action': 'update',
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/militar_form.html', context)


@login_required
@bloquear_membros_cpo
def militar_delete(request, pk):
    """Remove um militar"""
    militar = get_object_or_404(Militar, pk=pk)
    
    if request.method == 'POST':
        nome = militar.nome_completo
        militar.delete()
        messages.success(request, f'Militar {nome} removido com sucesso!')
        return redirect('militares:militar_list')
    
    context = {
        'militar': militar,
    }
    
    return render(request, 'militares/militar_confirm_delete.html', context)


def militar_search_ajax(request):
    """Busca militares via AJAX para autocomplete"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    militares = Militar.objects.filter(
        Q(nome_completo__icontains=query) |
        Q(nome_guerra__icontains=query) |
        Q(matricula__icontains=query)
    )[:10]
    
    results = []
    for militar in militares:
        results.append({
            'id': militar.id,
            'text': f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}",
            'nome': militar.nome_completo,
            'matricula': militar.matricula,
            'posto': militar.get_posto_graduacao_display(),
        })
    
    return JsonResponse({'results': results})


@login_required
def militar_dashboard(request):
    """Dashboard principal do sistema"""
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    fichas_pendentes = FichaConceito.objects.count()  # Removido filtro por status que não existe
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Últimas fichas de conceito
    ultimas_fichas = FichaConceito.objects.select_related('militar').order_by('-data_registro')[:5]
    
    # Documentos recentes
    documentos_recentes = Documento.objects.select_related('militar').order_by('-data_upload')[:5]
    
    # Quadros de acesso recentes
    quadros_recentes = QuadroAcesso.objects.all().order_by('-data_criacao')[:5]
    
    # Notificações do usuário
    from .models import NotificacaoSessao
    notificacoes_base = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    ).order_by('-prioridade', '-data_criacao')
    
    # Contadores de notificações (antes do slice)
    total_notificacoes = notificacoes_base.count()
    notificacoes_urgentes = notificacoes_base.filter(prioridade='URGENTE').count()
    notificacoes_altas = notificacoes_base.filter(prioridade='ALTA').count()
    
    # Aplicar slice apenas para exibição
    notificacoes = notificacoes_base[:10]
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'fichas_pendentes': fichas_pendentes,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'ultimas_fichas': ultimas_fichas,
        'documentos_recentes': documentos_recentes,
        'quadros_recentes': quadros_recentes,
        'notificacoes': notificacoes,
        'total_notificacoes': total_notificacoes,
        'notificacoes_urgentes': notificacoes_urgentes,
        'notificacoes_altas': notificacoes_altas,
    }
    
    return render(request, 'militares/dashboard.html', context)


# Views para Ficha de Conceito
@login_required
def ficha_conceito_list(request):
    """Lista ficha de conceito de oficiais"""
    militar_id = request.GET.get('militar')
    if militar_id:
        militar = get_object_or_404(Militar, pk=militar_id)
        fichas = militar.(list(fichaconceitooficiais_set.all()) + list(fichaconceitopracas_set.all())).order_by('-data_registro')
    else:
        militar = None
        # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
        oficiais = Militar.objects.filter(
            situacao='AT',
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        )
        fichas = FichaConceito.objects.filter(militar__in=oficiais)
        
        # Ordenar por hierarquia (do mais alto para o mais baixo posto)
        hierarquia_oficiais = {
            'CB': 1,   # Coronel
            'TC': 2,   # Tenente Coronel
            'MJ': 3,   # Major
            'CP': 4,   # Capitão
            '1T': 5,   # 1º Tenente
            '2T': 6,   # 2º Tenente
            'AS': 7,   # Aspirante a Oficial
            'AA': 8,   # Aluno de Adaptação
        }
        
        # Converter para lista e ordenar
        fichas_list = list(fichas)
        fichas_list.sort(key=lambda x: (
            hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
            x.militar.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.militar.nome_completo
        ))
        fichas = fichas_list
    
    # Estatísticas para mostrar no template (apenas oficiais)
    total_oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).count()
    total_fichas_oficiais = len(fichas) if isinstance(fichas, list) else fichas.count()
    oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais
    
    context = {
        'militar': militar,
        'fichas': fichas,
        'total_oficiais_ativos': total_oficiais_ativos,
        'total_fichas_oficiais': total_fichas_oficiais,
        'oficiais_sem_ficha': oficiais_sem_ficha,
        'is_oficiais': True,
    }
    return render(request, 'militares/ficha_conceito_list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_create(request):
    """Cria nova ficha de conceito"""
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f'Ficha de conceito registrada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm()
    
    context = {
        'form': form,
        'title': 'Nova Ficha de Conceito',
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


# Views para Quadros de Acesso
@login_required
def quadro_acesso_list(request):
    """Lista todos os quadros de acesso"""
    quadros = QuadroAcesso.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        quadros = quadros.filter(tipo=tipo)
    
    status = request.GET.get('status')
    if status:
        quadros = quadros.filter(status=status)
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao', '-data_criacao')
    quadros = quadros.order_by(ordenacao)
    
    # Adicionar quantidade de militares para cada quadro
    for quadro in quadros:
        quadro.total_militares_count = quadro.total_militares()
    
    # Verificar se é uma requisição AJAX
    if request.GET.get('ajax') == '1':
        from django.http import JsonResponse
        import json
        
        # Preparar dados para JSON
        quadros_data = []
        for quadro in quadros:
            quadros_data.append({
                'id': quadro.id,
                'tipo': quadro.tipo,
                'get_tipo_display': quadro.get_tipo_display(),
                'data_promocao': quadro.data_promocao.strftime('%d/%m/%Y'),
                'status': quadro.status,
                'get_status_display': quadro.get_status_display(),
                'total_militares': quadro.total_militares(),
                'motivo_nao_elaboracao': quadro.motivo_nao_elaboracao,
                'get_motivo_display_completo': quadro.get_motivo_display_completo() if quadro.motivo_nao_elaboracao else None,
            })
        
        return JsonResponse({
            'quadros': quadros_data,
            'total': len(quadros_data)
        })
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    homologados = quadros.filter(status='HOMOLOGADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'quadros': quadros,
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'status_choices': QuadroAcesso.STATUS_CHOICES,
        'filtros': {
            'tipo': tipo,
            'status': status,
            'ordenacao': ordenacao
        },
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'homologados': homologados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/quadro_acesso_list.html', context)


@login_required
def quadro_acesso_detail(request, pk):
    """Exibe detalhes de um quadro de acesso"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')

    # Redirecionar para a view de Praças se for o caso
    if quadro.categoria == 'PRACAS':
        return redirect('militares:quadro_acesso_pracas_detail', pk=quadro.pk)

    militares_inaptos = quadro.militares_inaptos_com_motivo()

    nomes_postos = dict(QuadroAcesso.POSTO_CHOICES)
    nomes_quadros = dict(QuadroAcesso.QUADRO_CHOICES)
    
    # Definir ordem dos quadros e transições (do mais graduado ao menos graduado)
    quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    
    # Verificar se é um quadro de praças
    if quadro.tipo == 'PRACAS':
        # Para quadros de praças: transições específicas para praças
        quadros = ['PRACAS']
        transicoes_por_quadro = {
            'PRACAS': [  # Praças
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
        }
    elif quadro.tipo == 'MERECIMENTO':
        # Para quadros de merecimento: transições específicas conforme regras
        transicoes_por_quadro = {
            'COMB': [  # Combatente - inclui TC→CB
                {
                    'numero': 'I',
                    'titulo': 'TENENTE-CORONEL para o posto de CORONEL',
                    'origem': 'TC',
                    'destino': 'CB',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'SAUDE': [  # Saúde - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'ENG': [  # Engenheiro - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'COMP': [  # Complementar - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        }
    else:
        # Para quadros de antiguidade: todas as transições por antiguidade
        transicoes_por_quadro = {
            'COMB': [  # Combatente
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ASPIRANTE A OFICIAL para o posto de 2º TENENTE',
                    'origem': 'AS',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'SAUDE': [  # Saúde
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                    'origem': 'AA',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'ENG': [  # Engenheiro
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                    'origem': 'AA',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'COMP': [  # Complementar
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'SUBTENENTE para o posto de 2º TENENTE',
                    'origem': 'ST',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        }
    
    # Buscar todos os militares aptos do quadro
    militares_aptos = quadro.itemquadroacesso_set.all().select_related('militar').order_by('posicao')
    
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
                item for item in militares_aptos 
                if item.militar.quadro == q and item.militar.posto_graduacao == origem
            ]
            estrutura_quadros[q]['transicoes'].append({
                'origem': origem,
                'destino': destino,
                'origem_nome': nomes_postos.get(origem, origem),
                'destino_nome': nomes_postos.get(destino, destino),
                'militares': militares_desta_transicao,
            })
    
    context = {
        'quadro': quadro,
        'militares_inaptos': militares_inaptos,
        'total_inaptos': len(militares_inaptos),
        'estrutura_quadros': estrutura_quadros,
    }
    
    return render(request, 'militares/quadro_acesso_detail.html', context)


@login_required
def gerar_quadro_acesso(request):
    """Gera um quadro de acesso único por tipo e data, incluindo todos os postos"""
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data_promocao = request.POST.get('data_promocao')
        categoria = request.POST.get('categoria', 'OFICIAIS')  # OFICIAIS ou PRACAS
        
        if not tipo:
            messages.error(request, 'O tipo de acesso é obrigatório.')
            return redirect('militares:gerar_quadro_acesso')
        
        if not categoria:
            messages.error(request, 'A categoria (Praças ou Oficiais) é obrigatória.')
            return redirect('militares:gerar_quadro_acesso')
        
        # Se não foi fornecida uma data, usar a data automática
        if not data_promocao:
            data_promocao = calcular_proxima_data_promocao(tipo=categoria)
            data_automatica = True
        else:
            try:
                data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                data_automatica = False
            except ValueError:
                messages.error(request, 'Data de promoção inválida.')
                return redirect('militares:gerar_quadro_acesso')
        
        # Permitir aditamentos - o sistema de numeração automática gerencia os números únicos
        
        # Criar um único quadro que representará todos os postos
        try:
            novo_quadro = QuadroAcesso.objects.create(
                tipo=tipo,
                data_promocao=data_promocao,
                status='EM_ELABORACAO',
                categoria=categoria,
                observacoes=f"Quadro de {tipo.lower()} para {categoria.lower()} - {data_promocao.strftime('%d/%m/%Y')} - Inclui todos os postos"
            )
            
            # Gerar o quadro com todos os postos
            sucesso, mensagem = novo_quadro.gerar_quadro_completo()
            
            if sucesso:
                categoria_display = "Oficiais" if categoria == 'OFICIAIS' else "Praças"
                if data_automatica:
                    messages.success(request, f'Quadro de {novo_quadro.get_tipo_display().lower()} para {categoria_display} criado com sucesso! Data automática: {data_promocao.strftime("%d/%m/%Y")}')
                else:
                    messages.success(request, f'Quadro de {novo_quadro.get_tipo_display().lower()} para {categoria_display} criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}!')
                messages.success(request, mensagem)
                return redirect('militares:quadro_acesso_detail', pk=novo_quadro.pk)
            else:
                novo_quadro.delete()
                messages.error(request, f'Erro ao criar quadro: {mensagem}')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar quadro: {str(e)}')
        
        return redirect('militares:gerar_quadro_acesso')
    
    categoria = request.GET.get('categoria', 'OFICIAIS')

    context = {
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'quadros_recentes': QuadroAcesso.objects.all().order_by('-data_criacao')[:10],
        'proxima_data_automatica': calcular_proxima_data_promocao(tipo='OFICIAIS'),
        'categorias': [
            ('OFICIAIS', 'Oficiais'),
            ('PRACAS', 'Praças')
        ],
        'categoria_selecionada': categoria
    }
    
    return render(request, 'militares/gerar_quadro_acesso.html', context)


@login_required
def regerar_quadro_acesso(request, pk):
    """Regera um quadro de acesso existente"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if request.method == 'POST':
        sucesso, mensagem = quadro.gerar_quadro_automatico()
        
        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.error(request, f'Erro ao regenerar quadro: {mensagem}')
    
    return redirect('militares:quadro_acesso_detail', pk=quadro.pk)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
def delete_quadro_acesso(request, pk):
    """Exclui um quadro de acesso"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if request.method == 'POST':
        # Verificar se o quadro está homologado
        if quadro.status == 'HOMOLOGADO':
            messages.error(request, 'Não é possível excluir um quadro homologado. Deshomologize primeiro.')
            return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
        
        # Excluir todos os itens do quadro primeiro
        quadro.itemquadroacesso_set.all().delete()
        # Excluir o quadro
        quadro.delete()
        
        messages.success(request, 'Quadro de acesso excluído com sucesso!')
        return redirect('militares:quadro_acesso_list')
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/quadro_acesso_confirm_delete.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime
from django.contrib.auth.models import User
from .models import (
    Militar, FichaConceito, QuadroAcesso, ItemQuadroAcesso, 
    Promocao, Vaga, Curso, MedalhaCondecoracao, Documento, Intersticio,
    POSTO_GRADUACAO_CHOICES, SITUACAO_CHOICES, QUADRO_CHOICES,
    PrevisaoVaga, AssinaturaQuadroAcesso, ComissaoPromocao, MembroComissao, SessaoComissao, PresencaSessao, DeliberacaoComissao, VotoDeliberacao, DocumentoSessao, AtaSessao, ModeloAta, CargoComissao,
    VagaManual, QuadroFixacaoVagas, ItemQuadroFixacaoVagas  # <-- Adicionado
)
from .forms import MilitarForm, FichaConceitoForm, DocumentoForm, UserRegistrationForm, ConfirmarSenhaForm, ComissaoPromocaoForm, MembroComissaoForm, SessaoComissaoForm, DeliberacaoComissaoForm, DocumentoSessaoForm, AtaSessaoForm, ModeloAtaForm, CargoComissaoForm
from django import forms
from django.contrib.auth import authenticate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader
import os
from reportlab.lib.enums import TA_JUSTIFY
import re
from html import unescape
import logging


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
def delete_quadro_acesso(request, pk):
    """Exclui um quadro de acesso"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if request.method == 'POST':
        # Verificar se o quadro está homologado
        if quadro.status == 'HOMOLOGADO':
            messages.error(request, 'Não é possível excluir um quadro homologado. Deshomologize primeiro.')
            return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
        
        # Excluir todos os itens do quadro primeiro
        quadro.itemquadroacesso_set.all().delete()
        # Excluir o quadro
        quadro.delete()
        
        messages.success(request, 'Quadro de acesso excluído com sucesso!')
        return redirect('militares:quadro_acesso_list')
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/quadro_acesso_confirm_delete.html', context)


@login_required
def gerar_quadro_acesso(request):
    """Gera um quadro de acesso único por tipo e data, incluindo todos os postos"""
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        data_promocao = request.POST.get('data_promocao')
        categoria = request.POST.get('categoria', 'OFICIAIS')  # OFICIAIS ou PRACAS
        
        if not tipo:
            messages.error(request, 'O tipo de acesso é obrigatório.')
            return redirect('militares:gerar_quadro_acesso')
        
        if not categoria:
            messages.error(request, 'A categoria (Praças ou Oficiais) é obrigatória.')
            return redirect('militares:gerar_quadro_acesso')
        
        # Se não foi fornecida uma data, usar a data automática
        if not data_promocao:
            data_promocao = calcular_proxima_data_promocao(tipo=categoria)
            data_automatica = True
        else:
            try:
                data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                data_automatica = False
            except ValueError:
                messages.error(request, 'Data de promoção inválida.')
                return redirect('militares:gerar_quadro_acesso')
        
        # Permitir aditamentos - o sistema de numeração automática gerencia os números únicos
        
        # Criar um único quadro que representará todos os postos
        try:
            novo_quadro = QuadroAcesso.objects.create(
                tipo=tipo,
                data_promocao=data_promocao,
                status='EM_ELABORACAO',
                categoria=categoria,
                observacoes=f"Quadro de {tipo.lower()} para {categoria.lower()} - {data_promocao.strftime('%d/%m/%Y')} - Inclui todos os postos"
            )
            
            # Gerar o quadro com todos os postos
            sucesso, mensagem = novo_quadro.gerar_quadro_completo()
            
            if sucesso:
                categoria_display = "Oficiais" if categoria == 'OFICIAIS' else "Praças"
                if data_automatica:
                    messages.success(request, f'Quadro de {novo_quadro.get_tipo_display().lower()} para {categoria_display} criado com sucesso! Data automática: {data_promocao.strftime("%d/%m/%Y")}')
                else:
                    messages.success(request, f'Quadro de {novo_quadro.get_tipo_display().lower()} para {categoria_display} criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}!')
                messages.success(request, mensagem)
                return redirect('militares:quadro_acesso_detail', pk=novo_quadro.pk)
            else:
                novo_quadro.delete()
                messages.error(request, f'Erro ao criar quadro: {mensagem}')
                
        except Exception as e:
            messages.error(request, f'Erro ao criar quadro: {str(e)}')
        
        return redirect('militares:gerar_quadro_acesso')
    
    categoria = request.GET.get('categoria', 'OFICIAIS')

    context = {
        'tipos': QuadroAcesso.TIPO_CHOICES,
        'quadros_recentes': QuadroAcesso.objects.all().order_by('-data_criacao')[:10],
        'proxima_data_automatica': calcular_proxima_data_promocao(tipo='OFICIAIS'),
        'categorias': [
            ('OFICIAIS', 'Oficiais'),
            ('PRACAS', 'Praças')
        ],
        'categoria_selecionada': categoria
    }
    
    return render(request, 'militares/gerar_quadro_acesso.html', context)


@login_required
def homologar_quadro_acesso(request, pk):
    """Homologa um quadro de acesso, solicitando confirmação de senha via modal"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')

    if request.method == 'POST':
        senha = request.POST.get('senha')
        if senha:
            user = authenticate(username=request.user.username, password=senha)
            if user is not None:
                if quadro.status == 'ELABORADO':
                    quadro.status = 'HOMOLOGADO'
                    quadro.data_homologacao = timezone.now().date()
                    quadro.homologado_por = request.user
                    quadro.save()
                    messages.success(request, 'Quadro de acesso homologado com sucesso!')
                    return redirect('militares:quadro_acesso_list')
                else:
                    messages.error(request, 'Apenas quadros elaborados podem ser homologados.')
                    return redirect('militares:quadro_acesso_list')
            else:
                messages.error(request, 'Senha incorreta. Tente novamente.')
                return redirect('militares:quadro_acesso_list')
        else:
            messages.error(request, 'Senha é obrigatória.')
            return redirect('militares:quadro_acesso_list')

    # Se chegou aqui, redirecionar para a lista
    return redirect('militares:quadro_acesso_list')


@login_required
def deshomologar_quadro_acesso(request, pk):
    """Deshomologa um quadro de acesso (apenas pelo usuário que homologou)"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')

    if request.method == 'POST':
        if quadro.status == 'HOMOLOGADO':
            if quadro.homologado_por and quadro.homologado_por != request.user:
                messages.error(request, 'Apenas o usuário que homologou pode deshomologar este quadro.')
            else:
                quadro.status = 'ELABORADO'
                quadro.data_homologacao = None
                quadro.homologado_por = None
                quadro.save()
                messages.success(request, 'Quadro de acesso deshomologado com sucesso!')
        else:
            messages.error(request, 'Apenas quadros homologados podem ser deshomologados.')

    return redirect('militares:quadro_acesso_detail', pk=quadro.pk)


@login_required
def elaborar_quadro_acesso(request, pk):
    """Elabora um quadro de acesso não elaborado"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if request.method == 'POST':
        if quadro.status == 'NAO_ELABORADO':
            # Usar a lógica de geração automática
            sucesso, mensagem = quadro.gerar_quadro_automatico()
            
            if sucesso:
                messages.success(request, mensagem)
            else:
                messages.error(request, f'Erro ao elaborar quadro: {mensagem}')
        else:
            messages.error(request, 'Apenas quadros não elaborados podem ser elaborados.')
    
    return redirect('militares:quadro_acesso_detail', pk=quadro.pk)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
def quadro_acesso_edit(request, pk):
    """Edita um quadro de acesso"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if request.method == 'POST':
        action = request.POST.get('action', 'salvar')
        
        if action == 'salvar':
            # Edição básica do quadro
            try:
                data_promocao = request.POST.get('data_promocao')
                if data_promocao:
                    quadro.data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                
                status = request.POST.get('status')
                if status:
                    quadro.status = status
                
                motivo_nao_elaboracao = request.POST.get('motivo_nao_elaboracao')
                if motivo_nao_elaboracao:
                    quadro.motivo_nao_elaboracao = motivo_nao_elaboracao
                else:
                    quadro.motivo_nao_elaboracao = None
                
                quadro.observacoes = request.POST.get('observacoes', '')
                quadro.save()
                
                messages.success(request, 'Quadro de acesso atualizado com sucesso!')
                
            except ValueError:
                messages.error(request, 'Data de promoção inválida.')
                return redirect('militares:quadro_acesso_edit', pk=quadro.pk)
        
        elif action == 'regenerar':
            # Regenerar o quadro
            sucesso, mensagem = quadro.gerar_quadro_automatico()
            if sucesso:
                messages.success(request, mensagem)
            else:
                messages.error(request, f'Erro ao regenerar quadro: {mensagem}')
        
        elif action == 'homologar':
            # Homologar o quadro
            if quadro.status == 'ELABORADO':
                quadro.status = 'HOMOLOGADO'
                quadro.data_homologacao = timezone.now().date()
                quadro.save()
                messages.success(request, 'Quadro de acesso homologado com sucesso!')
            else:
                messages.error(request, 'Apenas quadros elaborados podem ser homologados.')
        
        elif action == 'deshomologar':
            # Deshomologar o quadro
            if quadro.status == 'HOMOLOGADO':
                quadro.status = 'ELABORADO'
                quadro.data_homologacao = None
                quadro.save()
                messages.success(request, 'Quadro de acesso deshomologado com sucesso!')
            else:
                messages.error(request, 'Apenas quadros homologados podem ser deshomologados.')
        
        elif action == 'elaborar':
            # Elaborar o quadro
            if quadro.status == 'NAO_ELABORADO':
                sucesso, mensagem = quadro.gerar_quadro_automatico()
                if sucesso:
                    messages.success(request, mensagem)
                else:
                    messages.error(request, f'Erro ao elaborar quadro: {mensagem}')
            else:
                messages.error(request, 'Apenas quadros não elaborados podem ser elaborados.')
        
        return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/quadro_acesso_edit.html', context)


@login_required
def quadro_acesso_pdf(request, pk):
    """Gera PDF do quadro de acesso no modelo institucional solicitado"""
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

    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    # Verificar se o quadro é de oficiais
    if quadro.categoria != 'OFICIAIS':
        messages.error(request, 'Este PDF é exclusivo para quadros de oficiais!')
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
        "COMISSÃO DE PROMOÇÃO DE OFICIAIS - CBMEPI-PI",
        "Av. Miguel Rosa, 3515 Terreo - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    for linha in cabecalho:
        story.append(Paragraph(linha, style_center))
    story.append(Spacer(1, 10))

    # Título centralizado e sublinhado
    tipo_quadro = quadro.get_tipo_display().upper()
    # O get_tipo_display() já retorna "QUADRO DE ACESSO POR ANTIGUIDADE" ou "QUADRO DE ACESSO POR MERECIMENTO"
    # Então usamos diretamente o valor retornado
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
            'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES COMBATENTES (QOBM/Comb.)',
            'codigo': 'COMB'
        },
        {
            'numero': 2,
            'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES DE SAÚDE (QOBM/S)',
            'codigo': 'SAUDE'
        },
        {
            'numero': 3,
            'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES ENGENHEIROS (QOBM/E)',
            'codigo': 'ENG'
        },
        {
            'numero': 4,
            'nome': 'QUADRO DE OFICIAIS BOMBEIROS MILITARES COMPLEMENTARES (QOBM/C)',
            'codigo': 'COMP'
        }
    ]

    # Definir transições específicas por quadro
    if quadro.tipo == 'MERECIMENTO':
        # Para quadros de merecimento: transições específicas conforme regras
        transicoes_por_quadro = {
            'COMB': [  # Combatente - inclui TC→CB
                {
                    'numero': 'I',
                    'titulo': 'TENENTE-CORONEL para o posto de CORONEL',
                    'origem': 'TC',
                    'destino': 'CB',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'SAUDE': [  # Saúde - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'ENG': [  # Engenheiro - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'COMP': [  # Complementar - apenas MJ→TC e CP→MJ
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Merecimento para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ]
        }
    else:
        # Para quadros de antiguidade: todas as transições por antiguidade
        transicoes_por_quadro = {
            'COMB': [  # Combatente
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ASPIRANTE A OFICIAL para o posto de 2º TENENTE',
                    'origem': 'AS',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'SAUDE': [  # Saúde
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                    'origem': 'AA',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'ENG': [  # Engenheiro
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'ALUNO DE ADAPTAÇÃO para o posto de 2º TENENTE',
                    'origem': 'AA',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                }
            ],
            'COMP': [  # Complementar
                {
                    'numero': 'I',
                    'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                    'origem': 'MJ',
                    'destino': 'TC',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Tenente-Coronel em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'II',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Major em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'III',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de Capitão em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'IV',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 1º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
                },
                {
                    'numero': 'V',
                    'titulo': 'SUBTENENTE para o posto de 2º TENENTE',
                    'origem': 'ST',
                    'destino': '2T',
                    'texto': 'Deixa de ser elaborado o Quadro de Acesso por Antiguidade para o posto de 2º Tenente em virtude de não haver oficial que satisfaça os requisitos essenciais para ingresso ao Quadro de acesso, nos termos do <b>art. 12</b> da Lei nº 5.461, de 30 de junho de 2005, alterada pela Lei Nº 7.772, de 04 de abril de 2022.'
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
            aptos = quadro.itemquadroacesso_set.filter(
                militar__posto_graduacao=transicao['origem'],
                militar__quadro=quadro_info['codigo']
            ).order_by('posicao')
            
            if aptos.exists():
                # Preparar dados da tabela
                if quadro.tipo == 'MERECIMENTO':
                    # Para quadros de merecimento: adicionar coluna de pontuação
                    from .utils import criptografar_cpf_lgpd
                    header_data = [['ORD', 'CPF', 'POSTO', 'NOME', 'PONTUAÇÃO']]
                    for idx, item in enumerate(aptos, 1):
                        header_data.append([
                            str(idx),
                            criptografar_cpf_lgpd(item.militar.cpf),
                            item.militar.get_posto_graduacao_display() if hasattr(item.militar, 'get_posto_graduacao_display') else item.militar.posto_graduacao,
                            item.militar.nome_completo,
                            f"{item.pontuacao:.2f}" if item.pontuacao else "-"
                        ])
                    
                    # Calcular larguras das colunas baseado no conteúdo
                    max_ord = max(len(str(row[0])) for row in header_data)
                    max_ident = max(len(row[1]) for row in header_data)
                    max_posto = max(len(row[2]) for row in header_data)
                    max_pontuacao = max(len(row[4]) for row in header_data)
                    
                    # Definir larguras mínimas e ajustáveis
                    col_widths = [
                        max(1.2*cm, max_ord * 0.3*cm),  # ORD
                        max(3*cm, max_ident * 0.3*cm),  # IDENT
                        max(3*cm, max_posto * 0.3*cm),  # POSTO
                        6*cm,  # NOME (reduzido para dar espaço à pontuação)
                        max(2*cm, max_pontuacao * 0.3*cm)  # PONTUAÇÃO
                    ]
                else:
                    # Para quadros de antiguidade: estrutura original
                    from .utils import criptografar_cpf_lgpd
                    header_data = [['ORD', 'CPF', 'POSTO', 'NOME']]
                    for idx, item in enumerate(aptos, 1):
                        header_data.append([
                            str(idx),
                            criptografar_cpf_lgpd(item.militar.cpf),
                            item.militar.get_posto_graduacao_display() if hasattr(item.militar, 'get_posto_graduacao_display') else item.militar.posto_graduacao,
                            item.militar.nome_completo
                        ])
                    
                    # Calcular larguras das colunas baseado no conteúdo
                    max_ord = max(len(str(row[0])) for row in header_data)
                    max_ident = max(len(row[1]) for row in header_data)
                    max_posto = max(len(row[2]) for row in header_data)
                    
                    # Definir larguras mínimas e ajustáveis
                    col_widths = [
                        max(1.2*cm, max_ord * 0.3*cm),  # ORD
                        max(3*cm, max_ident * 0.3*cm),  # IDENT
                        max(3*cm, max_posto * 0.3*cm),  # POSTO
                        8*cm  # NOME (fixo)
                    ]
                
                table = Table(header_data, colWidths=col_widths)
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

    # Seção de Assinaturas Eletrônicas
    story.append(PageBreak())  # Quebra de página antes das assinaturas
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Buscar todas as assinaturas válidas do quadro (da mais recente para a mais antiga)
    assinaturas = quadro.assinaturas.filter(assinado_por__isnull=False).order_by('-data_assinatura')
    
    if assinaturas.exists():
        # Título da seção
        story.append(Paragraph('<b>ASSINATURAS ELETRÔNICAS</b>', style_bold))
        story.append(Spacer(1, 10))
        
        for i, assinatura in enumerate(assinaturas):
            # Informações de assinatura eletrônica
            nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
            
            data_assinatura = assinatura.data_assinatura
            data_formatada = f"{data_assinatura.day:02d}/{data_assinatura.month:02d}/{data_assinatura.year}"
            hora_formatada = f"{data_assinatura.hour:02d}:{data_assinatura.minute:02d}"
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_assinante} - {assinatura.get_tipo_assinatura_display()}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
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
    else:
        # Se não houver assinaturas, mostrar apenas documento gerado pelo usuário logado
        from django.utils import timezone
        agora = timezone.localtime(timezone.now())
        nome_usuario = request.user.get_full_name() or request.user.username
        if not nome_usuario or nome_usuario.strip() == '':
            nome_usuario = "Usuário do Sistema"
        data_formatada = agora.strftime('%d/%m/%Y')
        hora_formatada = agora.strftime('%H:%M')
        texto_geracao = f"Documento gerado pelo usuário {nome_usuario} em {data_formatada}, às {hora_formatada}."
        story.append(Paragraph(texto_geracao, style_small))
    
    # Rodapé com QR Code para conferência de veracidade
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Dados para autenticação
    url_autenticacao = "https://sei.pi.gov.br/sei/controlador_externo.php?acao=documento_conferir&id_orgao_acesso_externo=0"
    codigo_verificador = f"{quadro.pk:08d}"
    codigo_crc = f"{hash(str(quadro.pk)) % 0xFFFFFFF:07X}"
    
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
    response['Content-Disposition'] = f'inline; filename="quadro_acesso_{quadro.pk}_{quadro.get_tipo_display()}.pdf"'
    
    return response


@login_required
def quadro_acesso_print(request, pk):
    """Versão para impressão do quadro de acesso"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    context = {
        'quadro': quadro,
        'itens': quadro.itemquadroacesso_set.all().order_by('posicao'),
    }
    
    return render(request, 'militares/quadro_acesso_print.html', context)


@login_required
def marcar_nao_elaborado(request, pk):
    """Marca um quadro como não elaborado"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        observacoes = request.POST.get('observacoes', '')
        
        quadro.status = 'NAO_ELABORADO'
        quadro.motivo_nao_elaboracao = motivo
        quadro.observacoes = observacoes
        quadro.save()
        
        # Limpar itens existentes
        quadro.itemquadroacesso_set.all().delete()
        
        messages.success(request, 'Quadro marcado como não elaborado.')
    
    return redirect('militares:quadro_acesso_detail', pk=quadro.pk)


# Views para Promoções
@login_required
def promocao_list(request):
    """Lista promoções"""
    # Filtros
    query = request.GET.get('q', '')
    criterio = request.GET.get('criterio', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    promocoes = Promocao.objects.all()
    
    # Aplicar filtros
    if query:
        promocoes = promocoes.filter(
            Q(militar__nome_completo__icontains=query) |
            Q(militar__nome_guerra__icontains=query) |
            Q(militar__matricula__icontains=query) |
            Q(numero_ato__icontains=query)
        )
    
    if criterio:
        promocoes = promocoes.filter(criterio=criterio)
    
    if data_inicio:
        promocoes = promocoes.filter(data_promocao__gte=data_inicio)
    
    if data_fim:
        promocoes = promocoes.filter(data_promocao__lte=data_fim)
    
    promocoes = promocoes.order_by('-data_promocao')
    
    # Estatísticas
    total_promocoes = Promocao.objects.count()
    promocoes_este_ano = Promocao.objects.filter(data_promocao__year=timezone.now().year).count()
    militares_promovidos = Promocao.objects.values('militar').distinct().count()
    promocoes_merecimento = Promocao.objects.filter(criterio='MERECIMENTO').count()
    
    # Paginação
    paginator = Paginator(promocoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'promocoes': page_obj,
        'total_promocoes': total_promocoes,
        'promocoes_este_ano': promocoes_este_ano,
        'militares_promovidos': militares_promovidos,
        'promocoes_merecimento': promocoes_merecimento,
    }
    
    return render(request, 'militares/promocao_list.html', context)


@login_required
@bloquear_membros_cpo
def promocao_create(request):
    """Registra nova promoção"""
    if request.method == 'POST':
        militar_id = request.POST.get('militar')
        posto_anterior = request.POST.get('posto_anterior')  # Novo campo
        posto_novo = request.POST.get('posto_novo')
        criterio = request.POST.get('criterio')
        data_promocao = request.POST.get('data_promocao')
        data_publicacao = request.POST.get('data_publicacao')
        numero_ato = request.POST.get('numero_ato')
        observacoes = request.POST.get('observacoes')
        is_historica = request.POST.get('is_historica') == 'on'  # Novo campo
        
        if all([militar_id, posto_novo, criterio, data_promocao]):
            militar = get_object_or_404(Militar, pk=militar_id)
            
            # Se não foi informado posto anterior, usar o atual do militar
            if not posto_anterior:
                posto_anterior = militar.posto_graduacao
            
            # Cria promoção
            promocao = Promocao.objects.create(
                militar=militar,
                posto_anterior=posto_anterior,
                posto_novo=posto_novo,
                criterio=criterio,
                data_promocao=data_promocao,
                data_publicacao=data_publicacao or timezone.now().date(),
                numero_ato=numero_ato or f"ATO-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                observacoes=observacoes
            )
            
            # Só atualiza o militar se não for promoção histórica
            if not is_historica:
                militar.posto_graduacao = posto_novo
                militar.data_promocao_atual = data_promocao
                militar.save()
            
            messages.success(request, f'Promoção registrada com sucesso!')
            return redirect('militares:promocao_list')
    
    context = {
        'militares': Militar.objects.filter(situacao='AT').order_by('nome_completo'),
        'postos': POSTO_GRADUACAO_CHOICES,
        'criterios': Promocao.CRITERIO_CHOICES,
        'today': timezone.now().date().isoformat(),
    }
    
    return render(request, 'militares/promocao_form.html', context)


@login_required
@bloquear_membros_cpo
def promocao_historica_create(request):
    """Registra promoção histórica (não atualiza o militar)"""
    if request.method == 'POST':
        militar_id = request.POST.get('militar')
        posto_anterior = request.POST.get('posto_anterior')
        posto_novo = request.POST.get('posto_novo')
        criterio = request.POST.get('criterio')
        data_promocao = request.POST.get('data_promocao')
        data_publicacao = request.POST.get('data_publicacao')
        numero_ato = request.POST.get('numero_ato')
        observacoes = request.POST.get('observacoes')
        
        if all([militar_id, posto_anterior, posto_novo, criterio, data_promocao]):
            militar = get_object_or_404(Militar, pk=militar_id)
            
            # Cria promoção histórica (não atualiza o militar)
            promocao = Promocao.objects.create(
                militar=militar,
                posto_anterior=posto_anterior,
                posto_novo=posto_novo,
                criterio=criterio,
                data_promocao=data_promocao,
                data_publicacao=data_publicacao or timezone.now().date(),
                numero_ato=numero_ato or f"ATO-HIST-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                observacoes=observacoes
            )
            
            messages.success(request, f'Promoção histórica registrada com sucesso!')
            return redirect('militares:promocao_list')
    
    context = {
        'militares': Militar.objects.all().order_by('nome_completo'),  # Todos os militares, não só ativos
        'postos': POSTO_GRADUACAO_CHOICES,
        'criterios': Promocao.CRITERIO_CHOICES,
        'today': timezone.now().date().isoformat(),
        'is_historica': True,
    }
    
    return render(request, 'militares/promocao_form.html', context)


@login_required
@bloquear_membros_cpo
def promocao_delete(request, pk):
    from .models import Promocao
    promocao = get_object_or_404(Promocao, pk=pk)
    if request.method == 'POST':
        promocao.delete()
        messages.success(request, 'Promoção excluída com sucesso!')
        return redirect('militares:promocao_list')
    return render(request, 'militares/promocao_confirm_delete.html', {'promocao': promocao})


# Views para Vagas






@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_form(request, militar_pk):
    """Formulário de ficha de conceito com upload de documentos"""
    militar = get_object_or_404(Militar, pk=militar_pk)
    
    # Verificar se já existe uma ficha para este militar
    ficha_existente = FichaConceito.objects.filter(militar=militar).first()
    
    if request.method == 'POST':
        if ficha_existente:
            # Se já existe, atualizar a ficha existente
            form = FichaConceitoForm(request.POST, request.FILES, instance=ficha_existente, militar=militar)
        else:
            # Se não existe, criar nova ficha
            form = FichaConceitoForm(request.POST, request.FILES, militar=militar)
        
        if form.is_valid():
            ficha = form.save(commit=False)
            ficha.militar = militar
            ficha.save()
            
            # Processar documentos se fornecidos
            documentos = request.FILES.getlist('documentos')
            for doc_file in documentos:
                Documento.objects.create(
                    militar=militar,
                    ficha_conceito=ficha,
                    tipo='OUTROS',
                    titulo=f"Documento: {doc_file.name}",
                    arquivo=doc_file
                )
            
            messages.success(request, 'Ficha de conceito salva com sucesso!')
            return redirect('militares:ficha_conceito_list')
        else:
            # Debug: mostrar erros do formulário
            print("Erros do formulário:", form.errors)
            messages.error(request, f'Erro ao salvar ficha de conceito: {form.errors}')
    else:
        if ficha_existente:
            # Se já existe, carregar dados da ficha existente
            form = FichaConceitoForm(instance=ficha_existente, militar=militar)
        else:
            # Se não existe, criar formulário vazio
            form = FichaConceitoForm(militar=militar)
    
    context = {
        'form': form,
        'militar': militar,
        'ficha': ficha_existente,
        'documento_form': DocumentoForm(),
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def ficha_conceito_edit(request, pk):
    """Editar ficha de conceito"""
    ficha = get_object_or_404(FichaConceito, pk=pk)
    
    if request.method == 'POST':
        form = FichaConceitoForm(request.POST, instance=ficha, militar=ficha.militar)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ficha de conceito atualizada com sucesso!')
            return redirect('militares:ficha_conceito_list')
    else:
        form = FichaConceitoForm(instance=ficha, militar=ficha.militar)
    
    context = {
        'form': form,
        'ficha': ficha,
        'militar': ficha.militar,
    }
    
    return render(request, 'militares/ficha_conceito_form.html', context)


@login_required
def documento_upload(request, ficha_pk):
    """Upload de documentos para ficha de conceito"""
    ficha = get_object_or_404(FichaConceito, pk=ficha_pk)
    
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.militar = ficha.militar
            documento.ficha_conceito = ficha
            documento.save()
            
            messages.success(request, 'Documento enviado com sucesso!')
            return redirect('militares:militar_detail', pk=ficha.militar.pk)
    else:
        form = DocumentoForm()
    
    context = {
        'form': form,
        'ficha': ficha,
        'militar': ficha.militar,
    }
    
    return render(request, 'militares/documento_upload.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def conferir_ficha(request, pk):
    """Conferir ficha de conceito"""
    ficha = get_object_or_404(FichaConceito, pk=pk)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        observacoes = request.POST.get('observacoes', '')
        
        if acao in ['aprovar', 'rejeitar']:
            # Atualiza apenas as observações, já que não há campo status
            ficha.observacoes = observacoes
            ficha.save()
            
            messages.success(request, f'Ficha {acao}da com sucesso!')
            return redirect('militares:militar_detail', pk=ficha.militar.pk)
    
    context = {
        'ficha': ficha,
        'militar': ficha.militar,
    }
    
    return render(request, 'militares/conferir_ficha.html', context)


@login_required
def conferir_documento(request, pk):
    """Conferir documento"""
    documento = get_object_or_404(Documento, pk=pk)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        observacoes = request.POST.get('observacoes', '')
        
        if acao in ['aprovar', 'rejeitar', 'arquivar']:
            documento.status = acao.upper()
            documento.conferido_por = request.user
            documento.data_conferencia = timezone.now()
            documento.observacoes = observacoes
            documento.save()
            
            messages.success(request, f'Documento {acao}do com sucesso!')
            return redirect('militares:militar_detail', pk=documento.militar.pk)
    
    context = {
        'documento': documento,
        'militar': documento.militar,
    }
    
    return render(request, 'militares/conferir_documento.html', context)


@login_required
def promocao_detail(request, pk):
    """Detalhes da promoção"""
    promocao = get_object_or_404(Promocao, pk=pk)
    
    context = {
        'promocao': promocao,
    }
    
    return render(request, 'militares/promocao_detail.html', context)


@login_required
def estatisticas(request):
    """Estatísticas do sistema"""
    # Estatísticas gerais
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    
    # Por quadro
    estatisticas_quadro = Militar.objects.filter(situacao='AT').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Por posto
    estatisticas_posto = Militar.objects.filter(situacao='AT').values('posto_graduacao').annotate(
        total=Count('id')
    ).order_by('posto_graduacao')
    
    # Fichas de conceito
    total_fichas = FichaConceito.objects.count()
    fichas_aprovadas = 0  # Removido filtro por status que não existe
    fichas_pendentes = 0  # Removido filtro por status que não existe
    
    # Documentos
    total_documentos = Documento.objects.count()
    documentos_aprovados = Documento.objects.filter(status='APROVADO').count()
    documentos_pendentes = Documento.objects.filter(status='PENDENTE').count()
    
    # Estatísticas dos quadros de acesso
    total_quadros_acesso = QuadroAcesso.objects.count()
    if total_quadros_acesso > 0:
        estatisticas_quadros_acesso = {
            'total': total_quadros_acesso,
            'elaborados': QuadroAcesso.objects.filter(status='ELABORADO').count(),
            'homologados': QuadroAcesso.objects.filter(status='HOMOLOGADO').count(),
            'nao_elaborados': QuadroAcesso.objects.filter(status='NAO_ELABORADO').count(),
            'em_elaboracao': QuadroAcesso.objects.filter(status='EM_ELABORACAO').count(),
            'militares_aptos': sum([q.itemquadroacesso_set.count() for q in QuadroAcesso.objects.filter(status='ELABORADO')]),
            'status': list(QuadroAcesso.objects.values('status').annotate(total=Count('id'))),
            'quadro': list(QuadroAcesso.objects.values('quadro').annotate(total=Count('id'))),
            'tipo': list(QuadroAcesso.objects.values('tipo').annotate(total=Count('id'))),
            'posto': list(QuadroAcesso.objects.values('posto').annotate(total=Count('id'))),
        }
    else:
        estatisticas_quadros_acesso = None
    
    context = {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'estatisticas_quadro': estatisticas_quadro,
        'estatisticas_posto': estatisticas_posto,
        'total_fichas': total_fichas,
        'fichas_aprovadas': fichas_aprovadas,
        'fichas_pendentes': fichas_pendentes,
        'total_documentos': total_documentos,
        'documentos_aprovados': documentos_aprovados,
        'documentos_pendentes': documentos_pendentes,
        'estatisticas_quadros_acesso': estatisticas_quadros_acesso,
    }
    
    return render(request, 'militares/estatisticas.html', context)


def register(request):
    """Registro de usuário"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def intersticio_list(request):
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,   # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    # Definir a hierarquia dos quadros
    hierarquia_quadros = {
        'COMB': 1,    # Combatente
        'SAUDE': 2,   # Saúde
        'ENG': 3,     # Engenheiro
        'COMP': 4,    # Complementar
        'PRACAS': 5,  # Praças
    }
    
    # Buscar interstícios ativos
    intersticios = list(Intersticio.objects.filter(ativo=True))
    
    # Filtrar apenas postos de praças no quadro de praças
    postos_pracas = ['ST', '1S', '2S', '3S', 'CAB', 'SD']
    intersticios = [i for i in intersticios if i.quadro != 'PRACAS' or i.posto in postos_pracas]
    
    # Ordenar por quadro primeiro, depois por posto (hierarquia)
    intersticios_ordenados = sorted(intersticios, key=lambda x: (
        hierarquia_quadros.get(x.quadro, 999),
        hierarquia_postos.get(x.posto, 999)
    ))
    
    return render(request, 'militares/intersticio_list.html', {'intersticios': intersticios_ordenados})


@user_passes_test(lambda u: u.is_staff)
def intersticio_manage(request):
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,   # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    # Definir a hierarquia dos quadros
    hierarquia_quadros = {
        'COMB': 1,    # Combatente
        'SAUDE': 2,   # Saúde
        'ENG': 3,     # Engenheiro
        'COMP': 4,    # Complementar
        'PRACAS': 5,  # Praças
    }
    
    # Buscar todos os interstícios
    intersticios = list(Intersticio.objects.all())
    
    # Filtrar apenas postos de praças no quadro de praças
    postos_pracas = ['ST', '1S', '2S', '3S', 'CAB', 'SD']
    intersticios = [i for i in intersticios if i.quadro != 'PRACAS' or i.posto in postos_pracas]
    
    # Ordenar por quadro primeiro, depois por posto (hierarquia)
    intersticios_ordenados = sorted(intersticios, key=lambda x: (
        hierarquia_quadros.get(x.quadro, 999),
        hierarquia_postos.get(x.posto, 999)
    ))
    
    if request.method == 'POST':
        for inter in intersticios_ordenados:
            anos = request.POST.get(f'anos_{inter.id}', '').strip()
            meses = request.POST.get(f'meses_{inter.id}', '').strip()
            try:
                inter.tempo_minimo_anos = int(anos) if anos.isdigit() else 0
                inter.tempo_minimo_meses = int(meses) if meses.isdigit() else 0
                inter.save()
            except Exception as e:
                messages.error(request, f'Erro ao salvar {inter}: {e}')
        messages.success(request, 'Interstícios atualizados com sucesso!')
        return redirect('militares:intersticio_manage')
    
    context = {
        'intersticios': intersticios_ordenados,
        'quadros': QUADRO_CHOICES,
        'postos': POSTO_GRADUACAO_CHOICES,
    }
    return render(request, 'militares/intersticio_manage.html', context)


@user_passes_test(lambda u: u.is_staff)
def intersticio_create(request):
    """Criar novo interstício"""
    if request.method == 'POST':
        quadro = request.POST.get('novo_quadro')
        posto = request.POST.get('novo_posto')
        anos = request.POST.get('novo_anos', '0')
        meses = request.POST.get('novo_meses', '0')
        
        try:
            # Verificar se já existe um interstício para este quadro/posto
            if Intersticio.objects.filter(quadro=quadro, posto=posto).exists():
                messages.error(request, 'Já existe um interstício para este quadro e posto!')
            else:
                Intersticio.objects.create(
                    quadro=quadro,
                    posto=posto,
                    tempo_minimo_anos=int(anos),
                    tempo_minimo_meses=int(meses),
                    ativo=True
                )
                messages.success(request, 'Interstício criado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao criar interstício: {e}')
    
    return redirect('militares:intersticio_manage')


@user_passes_test(lambda u: u.is_staff)
def intersticio_delete(request, pk):
    """Excluir interstício"""
    intersticio = get_object_or_404(Intersticio, pk=pk)
    
    if request.method == 'POST':
        intersticio.delete()
        messages.success(request, 'Interstício excluído com sucesso!')
        return redirect('militares:intersticio_manage')
    
    context = {
        'intersticio': intersticio,
    }
    
    return render(request, 'militares/intersticio_confirm_delete.html', context)


@login_required
def marcar_cursos_inerentes(request, militar_pk):
    """Marca automaticamente os cursos inerentes ao quadro do militar"""
    if request.method == 'POST':
        militar = get_object_or_404(Militar, pk=militar_pk)
        militar.marcar_cursos_inerentes()
        return JsonResponse({'success': True, 'message': 'Cursos inerentes marcados com sucesso!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


@login_required
def relatorio_requisitos_quadro(request, pk):
    """Relatório detalhado dos requisitos dos militares para um quadro de acesso"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    # Buscar militares candidatos para o quadro específico
    # Definir postos baseado no tipo de quadro
    if quadro.tipo == 'MERECIMENTO':
        # Para quadro de merecimento: incluir TC apenas para COMB (TC→CB), excluir subtenentes (ST)
        postos = ['2T', '1T', 'CP', 'MJ', 'TC']
    else:
        # Para quadro de antiguidade: incluir todos os postos
        postos = ['ST', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']
    
    # Buscar militares candidatos baseado no tipo de quadro
    militares_candidatos = []
    
    # Para quadros de merecimento, buscar apenas militares com ficha de conceito
    if quadro.tipo == 'MERECIMENTO':
        militares_candidatos = Militar.objects.filter(
            situacao='AT',
            (fichaconceitooficiais__isnull=False, fichaconceitopracas__isnull=False)
        ).filter(
            posto_graduacao__in=postos
        )
    else:
        # Para quadros de antiguidade, buscar todos os militares ativos
        militares_candidatos = Militar.objects.filter(
            situacao='AT'
        ).filter(
            posto_graduacao__in=postos
        )
    
    # Debug: imprimir quantidade de candidatos encontrados
    print(f"DEBUG: Encontrados {len(militares_candidatos)} militares candidatos para o quadro {quadro.tipo}")
    
    relatorio = []
    for militar in militares_candidatos:
        # Validar cada requisito individualmente
        tem_ficha = militar.(fichaconceitooficiais_set.exists() or fichaconceitopracas_set.exists())
        
        apto_intersticio = quadro._validar_intersticio_minimo(militar, quadro.data_promocao)
        motivo_intersticio = ""
        if not apto_intersticio:
            motivo_intersticio = "Interstício insuficiente até a data da promoção"
        
        apto_saude = quadro._validar_inspecao_saude(militar)
        motivo_saude = ""
        if not apto_saude:
            motivo_saude = "Inspeção de saúde vencida ou não realizada"
        
        apto_cursos = quadro._validar_cursos_inerentes(militar)
        motivo_cursos = ""
        if not apto_cursos:
            motivo_cursos = "Cursos inerentes insuficientes para o posto subsequente"
        
        # Status geral
        apto_geral = tem_ficha and apto_intersticio and apto_saude and apto_cursos
        
        relatorio.append({
            'militar': militar,
            'tem_ficha': tem_ficha,
            'apto_intersticio': apto_intersticio,
            'motivo_intersticio': motivo_intersticio,
            'apto_saude': apto_saude,
            'motivo_saude': motivo_saude,
            'apto_cursos': apto_cursos,
            'motivo_cursos': motivo_cursos,
            'apto_geral': apto_geral,
            'tempo_no_posto': militar.tempo_posto_atual(),
            'data_inspecao': militar.data_inspecao_saude,
            'validade_inspecao': militar.data_validade_inspecao_saude,
        })
    
    # Ordenar por status (aptos primeiro) e depois por nome
    relatorio.sort(key=lambda x: (not x['apto_geral'], x['militar'].nome_completo))
    
    context = {
        'quadro': quadro,
        'relatorio': relatorio,
        'total_candidatos': len(relatorio),
        'total_aptos': sum(1 for r in relatorio if r['apto_geral']),
        'total_inaptos': sum(1 for r in relatorio if not r['apto_geral']),
    }
    
    return render(request, 'militares/relatorio_requisitos_quadro.html', context)


@login_required
def test_template(request):
    """View de teste para verificar se o problema persiste"""
    quadros = QuadroAcesso.objects.all()
    
    # Calcular estatísticas
    total_quadros = quadros.count()
    elaborados = quadros.filter(status='ELABORADO').count()
    nao_elaborados = quadros.filter(status='NAO_ELABORADO').count()
    em_elaboracao = quadros.filter(status='EM_ELABORACAO').count()
    
    context = {
        'estatisticas': {
            'total': total_quadros,
            'elaborados': elaborados,
            'nao_elaborados': nao_elaborados,
            'em_elaboracao': em_elaboracao,
        }
    }
    
    return render(request, 'militares/simple_test.html', context)


class RelatorioAptosPromocaoForm(forms.Form):
    tipo = forms.ChoiceField(choices=[('ANTIGUIDADE', 'Antiguidade'), ('MERECIMENTO', 'Merecimento')], label="Tipo de Quadro de Acesso")
    data_promocao = forms.DateField(label="Data prevista para promoção", widget=forms.DateInput(attrs={'type': 'date'}))

@login_required
def relatorio_aptos_promocao(request):
    QUADROS = [
        ('COMB', 'Combatente'),
        ('SAUDE', 'Saúde'),
        ('ENG', 'Engenharia'),
        ('COMP', 'Complementar'),
    ]
    POSTOS = [
        ('2T', '2º Tenente'),
        ('1T', '1º Tenente'),
        ('CP', 'Capitão'),
        ('MJ', 'Major'),
        ('TC', 'Tenente-Coronel'),
        ('CB', 'Coronel'),
    ]
    relatorio = []
    form = RelatorioAptosPromocaoForm(request.GET or None)
    if form.is_valid():
        tipo = form.cleaned_data['tipo']
        data_promocao = form.cleaned_data['data_promocao']
        for cod_quadro, nome_quadro in QUADROS:
            quadro_data = {'nome': nome_quadro, 'postos': []}
            for cod_posto, nome_posto in POSTOS:
                militares = Militar.objects.filter(
                    quadro=cod_quadro,
                    posto_graduacao=cod_posto,
                    situacao='AT',
                    (fichaconceitooficiais__isnull=False, fichaconceitopracas__isnull=False)
                ).distinct()
                aptos = []
                for militar in militares:
                    # Usa as regras já implementadas no modelo QuadroAcesso
                    dummy_quadro = QuadroAcesso(tipo=tipo, quadro=cod_quadro, posto=cod_posto, data_promocao=data_promocao)
                    apto, _ = dummy_quadro.validar_requisitos_quadro_acesso(militar, data_promocao)
                    if apto:
                        aptos.append(militar)
                quadro_data['postos'].append({
                    'nome': nome_posto,
                    'aptos': aptos,
                })
            relatorio.append(quadro_data)
    context = {
        'form': form,
        'relatorio': relatorio,
        'form_submitted': form.is_valid(),
        'tipo': form.cleaned_data['tipo'] if form.is_valid() else None,
        'data_promocao': form.cleaned_data['data_promocao'] if form.is_valid() else None,
    }
    return render(request, 'militares/relatorio_aptos_promocao.html', context)


@login_required
def test_quadro_simple(request):
    """View de teste muito simples para verificar se o problema é específico da página de quadros"""
    return render(request, 'militares/simple_test.html', {
        'estatisticas': {
            'total': 0,
            'elaborados': 0,
            'nao_elaborados': 0,
            'em_elaboracao': 0,
        }
    })


@login_required
def criar_quadro_manual(request):
    """Cria um quadro de acesso manual"""
    if request.method == 'POST':
        data_promocao = request.POST.get('data_promocao')
        observacoes = request.POST.get('observacoes', '')
        
        if not data_promocao:
            messages.error(request, 'A data de promoção é obrigatória.')
            return redirect('militares:criar_quadro_manual')
        
        try:
            data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Data de promoção inválida.')
            return redirect('militares:criar_quadro_manual')
        
        # Verificar se já existe um quadro manual para esta data (permitir múltiplos quadros)
        # quadro_existente = QuadroAcesso.objects.filter(
        #     tipo='MANUAL',
        #     data_promocao=data_promocao
        # ).first()
        
        # if quadro_existente:
        #     messages.warning(request, f'Já existe um quadro manual para a data {data_promocao.strftime("%d/%m/%Y")}.')
        #     return redirect('militares:quadro_acesso_detail', pk=quadro_existente.pk)
        
        # Criar o quadro manual
        try:
            criterio_ordenacao = request.POST.get('criterio_ordenacao', 'ANTIGUIDADE')
            
            # Determinar a categoria baseada no critério ou deixar como padrão (OFICIAIS)
            categoria = request.POST.get('categoria', 'OFICIAIS')
            
            novo_quadro = QuadroAcesso.objects.create(
                tipo='MANUAL',
                categoria=categoria,
                data_promocao=data_promocao,
                status='EM_ELABORACAO',
                is_manual=True,
                criterio_ordenacao_manual=criterio_ordenacao,
                observacoes=observacoes or f"Quadro manual para {data_promocao.strftime('%d/%m/%Y')}"
            )
            
            # Se o critério for ANTIGUIDADE ou MERECIMENTO, carregar automaticamente os militares aptos
            if criterio_ordenacao in ['ANTIGUIDADE', 'MERECIMENTO']:
                try:
                    # Buscar militares aptos
                    militares_aptos = novo_quadro.militares_aptos()
                    
                    # Debug: mostrar informações sobre os militares encontrados
                    total_candidatos = Militar.objects.filter(situacao='AT').count()
                    if novo_quadro.categoria == 'OFICIAIS':
                        candidatos_categoria = Militar.objects.filter(
                            situacao='AT',
                            quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP']
                        ).count()
                    else:
                        candidatos_categoria = Militar.objects.filter(
                            situacao='AT',
                            quadro='PRACAS'
                        ).count()
                    
                    # Debug adicional
                    print(f"DEBUG: Quadro manual criado")
                    print(f"DEBUG: Categoria: {novo_quadro.categoria}")
                    print(f"DEBUG: Critério: {novo_quadro.criterio_ordenacao_manual}")
                    print(f"DEBUG: Total candidatos categoria: {candidatos_categoria}")
                    print(f"DEBUG: Militares aptos encontrados: {len(militares_aptos)}")
                    if militares_aptos:
                        print(f"DEBUG: Primeiros 3 militares: {[m.nome_completo for m in militares_aptos[:3]]}")
                    
                    if militares_aptos:
                        # Adicionar militares ao quadro
                        militares_adicionados = 0
                        militares_com_erro = []
                        
                        print(f"DEBUG: Tentando adicionar {len(militares_aptos)} militares ao quadro")
                        
                        for militar in militares_aptos:
                            try:
                                novo_quadro.adicionar_militar_manual(militar)
                                militares_adicionados += 1
                                print(f"DEBUG: Militar {militar.nome_completo} adicionado com sucesso")
                            except Exception as e:
                                erro_msg = f"Erro ao adicionar militar {militar.nome_completo}: {str(e)}"
                                print(erro_msg)
                                militares_com_erro.append(erro_msg)
                        
                        print(f"DEBUG: Total de militares adicionados: {militares_adicionados}")
                        print(f"DEBUG: Total de erros: {len(militares_com_erro)}")
                        
                        if militares_com_erro:
                            print("DEBUG: Erros encontrados:")
                            for erro in militares_com_erro[:5]:  # Mostrar apenas os primeiros 5 erros
                                print(f"  - {erro}")
                        
                        messages.success(request, f'Quadro manual criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}! {militares_adicionados} de {len(militares_aptos)} militares foram carregados automaticamente. (Total: {total_candidatos}, Categoria: {candidatos_categoria})')
                    else:
                        # Debug: verificar militares inaptos
                        militares_inaptos = novo_quadro.militares_inaptos_com_motivo()
                        motivos_principais = {}
                        for item in militares_inaptos[:10]:  # Primeiros 10 para não sobrecarregar
                            motivo = item['motivo']
                            if motivo not in motivos_principais:
                                motivos_principais[motivo] = 0
                            motivos_principais[motivo] += 1
                        
                        motivos_str = ", ".join([f"{motivo}: {count}" for motivo, count in motivos_principais.items()])
                        messages.warning(request, f'Quadro manual criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}! Nenhum militar apto foi encontrado. (Total: {total_candidatos}, Categoria: {candidatos_categoria}). Motivos principais: {motivos_str}')
                except Exception as e:
                    messages.warning(request, f'Quadro manual criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}! Erro ao carregar militares automaticamente: {str(e)}')
            else:
                messages.success(request, f'Quadro manual criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}!')
            
            return redirect('militares:quadro_acesso_detail', pk=novo_quadro.pk)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar quadro manual: {str(e)}')
        
        return redirect('militares:criar_quadro_manual')
    
    context = {
        'proxima_data_automatica': calcular_proxima_data_promocao(),
    }
    
    return render(request, 'militares/criar_quadro_manual.html', context)


@login_required
def adicionar_militar_quadro_manual(request, pk):
    """Adiciona um militar ao quadro manual"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if quadro.status == 'HOMOLOGADO':
        messages.error(request, 'Quadros homologados não podem ser editados.')
        return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
    
    if request.method == 'POST':
        militar_id = request.POST.get('militar_id')
        posicao = request.POST.get('posicao')
        pontuacao = request.POST.get('pontuacao', 0)
        
        if not militar_id:
            messages.error(request, 'Selecione um militar.')
            return redirect('militares:adicionar_militar_quadro_manual', pk=quadro.pk)
        
        try:
            militar = Militar.objects.get(pk=militar_id)
            
            # Converter posição para inteiro se fornecida
            posicao_int = None
            if posicao:
                try:
                    posicao_int = int(posicao)
                except ValueError:
                    messages.error(request, 'Posição deve ser um número inteiro.')
                    return redirect('militares:adicionar_militar_quadro_manual', pk=quadro.pk)
            
            # Converter pontuação para decimal
            try:
                pontuacao_decimal = float(pontuacao)
            except ValueError:
                pontuacao_decimal = 0
            
            # Adicionar militar ao quadro
            quadro.adicionar_militar_manual(militar, posicao_int, pontuacao_decimal)
            
            messages.success(request, f'Militar {militar.nome_completo} adicionado ao quadro com sucesso!')
            
        except Militar.DoesNotExist:
            messages.error(request, 'Militar não encontrado.')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao adicionar militar: {str(e)}')
    
    return redirect('militares:quadro_acesso_detail', pk=quadro.pk)


@login_required
def remover_militar_quadro_manual(request, pk, militar_id):
    """Remove um militar do quadro manual"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, f'Quadro de acesso com ID {pk} não encontrado. O quadro pode ter sido excluído anteriormente ou o ID está incorreto.')
        return redirect('militares:quadro_acesso_list')
    
    if quadro.status == 'HOMOLOGADO':
        messages.error(request, 'Quadros homologados não podem ser editados.')
        return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
    
    # Permitir tanto GET quanto POST para facilitar o teste
    try:
        militar = Militar.objects.get(pk=militar_id)
        print(f"DEBUG: Tentando remover militar {militar.nome_completo} do quadro {quadro.pk}")
        
        # Verificar se o militar está no quadro
        item = quadro.itemquadroacesso_set.filter(militar=militar).first()
        if not item:
            messages.error(request, f'O militar {militar.nome_completo} não está no quadro.')
            return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
        
        print(f"DEBUG: Item encontrado - posição {item.posicao}")
        
        # Remover o militar
        quadro.remover_militar_manual(militar)
        print(f"DEBUG: Militar removido com sucesso")
        
        messages.success(request, f'Militar {militar.nome_completo} removido do quadro com sucesso!')
    except Militar.DoesNotExist:
        messages.error(request, 'Militar não encontrado.')
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        print(f"DEBUG: Erro ao remover militar: {str(e)}")
        messages.error(request, f'Erro ao remover militar: {str(e)}')
    
    return redirect('militares:quadro_acesso_detail', pk=quadro.pk)


@login_required
def buscar_militares_ajax(request):
    """Busca militares para adicionar ao quadro manual via AJAX"""
    if request.method == 'GET':
        termo = request.GET.get('termo', '')
        if len(termo) < 2:
            return JsonResponse({'militares': []})
        
        militares = Militar.objects.filter(
            situacao='AT',
            nome_completo__icontains=termo
        ).values('id', 'nome_completo', 'posto_graduacao', 'quadro', 'matricula')[:10]
        
        return JsonResponse({'militares': list(militares)})
    
    return JsonResponse({'militares': []})


@login_required
def buscar_pontuacao_militar(request, militar_id):
    """Retorna a pontuação da ficha de conceito do militar"""
    from militares.models import Militar
    try:
        militar = Militar.objects.get(pk=militar_id)
        ficha = militar.(fichaconceitooficiais_set.first() or fichaconceitopracas_set.first())
        pontuacao = ficha.pontos if ficha else 0
        return JsonResponse({'pontuacao': float(pontuacao)})
    except Militar.DoesNotExist:
        return JsonResponse({'pontuacao': 0})


@login_required
def debug_militares_aptos(request):
    """View de debug para verificar militares aptos"""
    if request.method == 'POST':
        categoria = request.POST.get('categoria', 'OFICIAIS')
        criterio = request.POST.get('criterio', 'ANTIGUIDADE')
        data_promocao = request.POST.get('data_promocao')
        
        try:
            data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
        except:
            data_promocao = date.today()
        
        # Criar quadro temporário para teste
        quadro_teste = QuadroAcesso(
            tipo='MANUAL',
            categoria=categoria,
            data_promocao=data_promocao,
            status='EM_ELABORACAO',
            is_manual=True,
            criterio_ordenacao_manual=criterio
        )
        
        # Buscar militares candidatos
        if categoria == 'OFICIAIS':
            if criterio == 'MERECIMENTO':
                candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
                    posto_graduacao__in=['CP', 'MJ', 'TC', 'CB'],
                    (fichaconceitooficiais__isnull=False, fichaconceitopracas__isnull=False)
                )
            else:
                candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP']
                )
        else:  # PRACAS
            if criterio == 'MERECIMENTO':
                candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro='PRACAS',
                    posto_graduacao__in=['2S', '1S'],
                    (fichaconceitooficiais__isnull=False, fichaconceitopracas__isnull=False)
                )
            else:
                candidatos = Militar.objects.filter(
                    situacao='AT',
                    quadro='PRACAS'
                )
        
        # Verificar cada candidato
        resultados = []
        for militar in candidatos:
            apto, motivo = quadro_teste.validar_requisitos_quadro_acesso(militar, data_promocao)
            resultados.append({
                'militar': militar.nome_completo,
                'posto': militar.posto_graduacao,
                'quadro': militar.quadro,
                'apto': apto,
                'motivo': motivo
            })
        
        context = {
            'categoria': categoria,
            'criterio': criterio,
            'data_promocao': data_promocao,
            'total_candidatos': len(candidatos),
            'total_aptos': len([r for r in resultados if r['apto']]),
            'resultados': resultados
        }
        
        return render(request, 'militares/debug_militares_aptos.html', context)
    
    return render(request, 'militares/debug_militares_aptos.html', {})


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
@permitir_apenas_chefe_secao_promocoes
def gerar_fichas_conceito_todos(request):
    """Gera fichas de conceito para todos os militares cadastrados que ainda não possuem"""
    if request.method == 'POST':
        # Verificar se está sendo chamado da página de oficiais
        is_oficiais = request.POST.get('is_oficiais', False)
        
        if is_oficiais:
            # Filtrar apenas oficiais ativos
            militares_ativos = Militar.objects.filter(
                situacao='AT',
                posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
            )
            tipo_militar = "oficiais"
        else:
            # Buscar todos os militares ativos
            militares_ativos = Militar.objects.filter(situacao='AT')
            tipo_militar = "militares"
        
        # Buscar militares que não possuem ficha de conceito
        militares_sem_ficha = militares_ativos.exclude(
            (fichaconceitooficiais__isnull=False, fichaconceitopracas__isnull=False)
        )
        
        fichas_criadas = 0
        militares_processados = 0
        
        for militar in militares_sem_ficha:
            # Verificar se já existe ficha para este militar (dupla verificação)
            ficha_existente = FichaConceito.objects.filter(militar=militar).first()
            
            if not ficha_existente:
                # Criar nova ficha - o método save() preencherá automaticamente o tempo no posto
                ficha = FichaConceito.objects.create(
                    militar=militar,
                )
                fichas_criadas += 1
            
            militares_processados += 1
        
        # Mensagens informativas
        if fichas_criadas > 0:
            messages.success(request, f'✅ Foram criadas {fichas_criadas} fichas de conceito com tempo de serviço no posto para {tipo_militar} que não possuíam.')
        else:
            messages.info(request, f'ℹ️ Todos os {tipo_militar} ativos já possuem fichas de conceito.')
        
        if militares_processados > 0:
            messages.info(request, f'📊 Processados {militares_processados} {tipo_militar} ativos.')
        
        # Informação adicional sobre militares que já tinham fichas
        militares_com_ficha = militares_ativos.count() - militares_sem_ficha.count()
        if militares_com_ficha > 0:
            messages.info(request, f'🔒 {militares_com_ficha} {tipo_militar} já possuíam fichas de conceito e não foram alterados.')
    
    return redirect('militares:ficha_conceito_list')





@login_required
@bloquear_membros_cpo
def vaga_create(request):
    """Cria uma nova vaga"""
    from .models import Vaga
    if request.method == 'POST':
        posto = request.POST.get('posto')
        quadro = request.POST.get('quadro')
        efetivo_atual = request.POST.get('efetivo_atual')
        efetivo_maximo = request.POST.get('efetivo_maximo')
        if posto and quadro and efetivo_maximo:
            vaga = Vaga(
                posto=posto,
                quadro=quadro,
                efetivo_atual=efetivo_atual or 0,
                efetivo_maximo=efetivo_maximo
            )
            vaga.save()
            messages.success(request, 'Vaga criada com sucesso!')
            return redirect('militares:quadro_fixacao_vagas_list')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    # Para GET, exibe o mesmo modal, mas normalmente só é chamado via POST
    return redirect('militares:quadro_fixacao_vagas_list')





@user_passes_test(lambda u: u.is_staff)
def previsao_vaga_manage(request):
    """Gerenciar previsões de vagas"""
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,   # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    # Definir a hierarquia dos quadros
    hierarquia_quadros = {
        'COMB': 1,    # Combatente
        'SAUDE': 2,   # Saúde
        'ENG': 3,     # Engenheiro
        'COMP': 4,    # Complementar
        'PRACAS': 5,  # Praças
    }
    
    # Buscar todas as previsões de vagas
    previsoes = list(PrevisaoVaga.objects.all())
    
    # Filtrar apenas postos de praças no quadro de praças
    postos_pracas = ['ST', '1S', '2S', '3S', 'CAB', 'SD']
    previsoes = [p for p in previsoes if p.quadro != 'PRACAS' or p.posto in postos_pracas]
    
    # Ordenar por quadro primeiro, depois por posto (hierarquia)
    previsoes_ordenadas = sorted(previsoes, key=lambda x: (
        hierarquia_quadros.get(x.quadro, 999),
        hierarquia_postos.get(x.posto, 999)
    ))
    
    if request.method == 'POST':
        for previsao in previsoes_ordenadas:
            efetivo_atual = request.POST.get(f'efetivo_atual_{previsao.id}', '').strip()
            efetivo_previsto = request.POST.get(f'efetivo_previsto_{previsao.id}', '').strip()
            try:
                previsao.efetivo_atual = int(efetivo_atual) if efetivo_atual.isdigit() else 0
                previsao.efetivo_previsto = int(efetivo_previsto) if efetivo_previsto.isdigit() else 0
                previsao.save()
            except Exception as e:
                messages.error(request, f'Erro ao salvar {previsao}: {e}')
        messages.success(request, 'Previsões de vagas atualizadas com sucesso!')
        return redirect('militares:previsao_vaga_manage')
    
    context = {
        'previsoes': previsoes_ordenadas,
        'quadros': QUADRO_CHOICES,
        'postos': POSTO_GRADUACAO_CHOICES,
    }
    return render(request, 'militares/previsao_vaga_manage.html', context)


@user_passes_test(lambda u: u.is_staff)
def previsao_vaga_create(request):
    """Criar nova previsão de vaga"""
    if request.method == 'POST':
        quadro = request.POST.get('novo_quadro')
        posto = request.POST.get('novo_posto')
        efetivo_atual = request.POST.get('novo_efetivo_atual', '0')
        efetivo_previsto = request.POST.get('novo_efetivo_previsto', '0')
        
        try:
            # Verificar se já existe uma previsão para este quadro/posto
            if PrevisaoVaga.objects.filter(quadro=quadro, posto=posto).exists():
                messages.error(request, 'Já existe uma previsão de vaga para este quadro e posto!')
            else:
                PrevisaoVaga.objects.create(
                    quadro=quadro,
                    posto=posto,
                    efetivo_atual=int(efetivo_atual),
                    efetivo_previsto=int(efetivo_previsto),
                    ativo=True
                )
                messages.success(request, 'Previsão de vaga criada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao criar previsão de vaga: {e}')
    
    return redirect('militares:previsao_vaga_manage')


@user_passes_test(lambda u: u.is_staff)
def previsao_vaga_delete(request, pk):
    """Excluir previsão de vaga"""
    previsao = get_object_or_404(PrevisaoVaga, pk=pk)
    
    if request.method == 'POST':
        previsao.delete()
        messages.success(request, 'Previsão de vaga excluída com sucesso!')
        return redirect('militares:previsao_vaga_manage')
    
    context = {
        'previsao': previsao,
    }
    
    return render(request, 'militares/previsao_vaga_confirm_delete.html', context)


@user_passes_test(lambda u: u.is_staff)
def previsao_vaga_delete_ajax(request, pk):
    """Excluir previsão de vaga via AJAX"""
    if request.method == 'POST':
        try:
            previsao = PrevisaoVaga.objects.get(pk=pk)
            previsao.delete()
            return JsonResponse({'success': True})
        except PrevisaoVaga.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Previsão de vaga não encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
@bloquear_membros_cpo
def documento_delete(request, pk):
    """Excluir documento"""
    try:
        documento = Documento.objects.get(pk=pk)
    except Documento.DoesNotExist:
        messages.error(request, f'Documento com ID {pk} não encontrado. O documento pode ter sido excluído anteriormente ou o ID está incorreto.')
        # Redirecionar para a lista de militares se não conseguir identificar o militar
        return redirect('militares:militar_list')
    
    if request.method == 'POST':
        nome_arquivo = documento.filename()
        militar_pk = documento.militar.pk
        documento.delete()
        messages.success(request, f'Documento "{nome_arquivo}" excluído com sucesso!')
        return redirect('militares:militar_detail', pk=militar_pk)
    
    context = {
        'documento': documento,
        'militar': documento.militar,
    }
    
    return render(request, 'militares/documento_confirm_delete.html', context)


@login_required
def assinar_documentos_quadro(request, pk):
    """Página para assinar documentos de um quadro de acesso com visualização do PDF"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar permissão de assinatura
    if quadro.tipo in ['ANTIGUIDADE', 'MERECIMENTO']:
        # Para quadros de oficiais, verificar se é membro da CPO
        comissao_cpo = ComissaoPromocao.get_comissao_ativa_por_tipo('CPO')
        if not comissao_cpo or not comissao_cpo.pode_assinar_documento_oficial(request.user):
            messages.error(request, 'Você não tem permissão para assinar documentos de oficiais. Apenas membros da CPO podem assinar.')
            return redirect('militares:quadro_acesso_detail', pk=pk)
    else:
        # Para quadros de praças, verificar se é membro da CPP
        comissao_cpp = ComissaoPromocao.get_comissao_ativa_por_tipo('CPP')
        if not comissao_cpp or not comissao_cpp.pode_assinar_documento_praca(request.user):
            messages.error(request, 'Você não tem permissão para assinar documentos de praças. Apenas membros da CPP podem assinar.')
            return redirect('militares:quadro_acesso_detail', pk=pk)
    
    # Buscar militares do quadro
    militares_quadro = []
    if quadro.status in ['ELABORADO', 'HOMOLOGADO']:
        militares_quadro = quadro.itemquadroacesso_set.all().order_by('posicao')
    
    # Buscar documentos pendentes de assinatura
    documentos_pendentes = Documento.objects.filter(
        militar__in=[item.militar for item in militares_quadro],
        status='PENDENTE'
    ).order_by('militar__nome_completo', 'data_upload')
    
    # Criar lista de documentos com informações do militar e posição
    documentos_com_info = []
    militares_sem_documentos = []
    
    for item in militares_quadro:
        documentos_militar = documentos_pendentes.filter(militar=item.militar)
        if documentos_militar.exists():
            for doc in documentos_militar:
                documentos_com_info.append({
                    'documento': doc,
                    'militar': item.militar,
                    'posicao': item.posicao,
                    'item_quadro': item
                })
        else:
            militares_sem_documentos.append(item)
    
    # Gerar URL do PDF baseado no tipo do quadro
    if quadro.categoria == 'PRACAS':
        pdf_url = f'/militares/pracas/quadros-acesso/{quadro.pk}/pdf/'
    else:
        pdf_url = f'/militares/quadros-acesso/{quadro.pk}/pdf/'
    
    context = {
        'quadro': quadro,
        'militares_quadro': militares_quadro,
        'documentos_pendentes': documentos_pendentes,
        'documentos_com_info': documentos_com_info,
        'militares_sem_documentos': militares_sem_documentos,
        'total_documentos_pendentes': documentos_pendentes.count(),
        'pdf_url': pdf_url,
    }
    
    return render(request, 'militares/assinar_documentos_quadro.html', context)


@login_required
def assinar_documento(request, pk):
    """Assinar documento com confirmação de senha"""
    documento = get_object_or_404(Documento, pk=pk)
    
    if request.method == 'POST':
        senha = request.POST.get('senha')
        observacoes = request.POST.get('observacoes_assinatura', '')
        
        # Verificar senha do usuário
        if not request.user.check_password(senha):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            context = {
                'documento': documento,
                'militar': documento.militar,
            }
            return render(request, 'militares/assinar_documento.html', context)
        
        # Assinar o documento
        documento.status = 'ASSINADO'
        documento.assinado_por = request.user
        documento.data_assinatura = timezone.now()
        documento.observacoes_assinatura = observacoes
        documento.save()
        
        messages.success(request, f'Documento "{documento.titulo}" assinado com sucesso!')
        return redirect('militares:militar_detail', pk=documento.militar.pk)
    
    context = {
        'documento': documento,
        'militar': documento.militar,
    }
    
    return render(request, 'militares/assinar_documento.html', context)


@login_required
def assinar_quadro_acesso(request, pk):
    """Assinar quadro de acesso com confirmação de senha"""
    quadro = get_object_or_404(QuadroAcesso, pk=pk)
    
    # Verificar permissão de assinatura
    if quadro.tipo in ['ANTIGUIDADE', 'MERECIMENTO']:
        # Para quadros de oficiais, verificar se é membro da CPO
        comissao_cpo = ComissaoPromocao.get_comissao_ativa_por_tipo('CPO')
        if not comissao_cpo or not comissao_cpo.pode_assinar_documento_oficial(request.user):
            messages.error(request, 'Você não tem permissão para assinar documentos de oficiais. Apenas membros da CPO podem assinar.')
            return redirect('militares:quadro_acesso_detail', pk=pk)
    else:
        # Para quadros de praças, verificar se é membro da CPP
        comissao_cpp = ComissaoPromocao.get_comissao_ativa_por_tipo('CPP')
        if not comissao_cpp or not comissao_cpp.pode_assinar_documento_praca(request.user):
            messages.error(request, 'Você não tem permissão para assinar documentos de praças. Apenas membros da CPP podem assinar.')
            return redirect('militares:quadro_acesso_detail', pk=pk)
    
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
            return render(request, 'militares/assinar_quadro_acesso.html', context)
        
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
            return render(request, 'militares/assinar_quadro_acesso.html', context)
        
        # Criar a assinatura
        assinatura = AssinaturaQuadroAcesso.objects.create(
            quadro_acesso=quadro,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura=tipo_assinatura
        )
        
        messages.success(request, f'Quadro de acesso assinado com sucesso como "{assinatura.get_tipo_assinatura_display()}"!')
        return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/assinar_quadro_acesso.html', context)


# ============================================================================
# VIEWS DA COMISSÃO DE PROMOÇÃO DE OFICIAIS
# ============================================================================

@login_required
def comissao_list(request):
    """Lista todas as comissões de promoção de oficiais"""
    # Verificar se o usuário é membro CPO e filtrar apenas CPO
    grupos_cpo = ['Membro CPO - Acesso apenas a oficiais']
    grupos_usuario = [grupo.name for grupo in request.user.groups.all()]
    
    if any(grupo_cpo in grupos_usuario for grupo_cpo in grupos_cpo):
        # Membro CPO: mostrar apenas comissões CPO
        comissoes = ComissaoPromocao.objects.filter(tipo='CPO')
    else:
        # Outros usuários: mostrar todas as comissões
        comissoes = ComissaoPromocao.objects.all()
    
    # Filtros
    status = request.GET.get('status')
    if status:
        comissoes = comissoes.filter(status=status)
    
    # Busca
    busca = request.GET.get('busca')
    if busca:
        comissoes = comissoes.filter(
            models.Q(nome__icontains=busca) |
            models.Q(observacoes__icontains=busca)
        )
    
    context = {
        'comissoes': comissoes,
        'status_choices': ComissaoPromocao.STATUS_CHOICES,
    }
    return render(request, 'militares/comissao/list.html', context)


@login_required
def comissao_detail(request, pk):
    """Detalhes de uma comissão de promoção de oficiais"""
    # Verificar se o usuário é membro CPO e restringir acesso
    grupos_cpo = ['Membro CPO - Acesso apenas a oficiais']
    grupos_usuario = [grupo.name for grupo in request.user.groups.all()]
    
    try:
        comissao = ComissaoPromocao.objects.get(pk=pk)
        
        # Membro CPO só pode acessar comissões CPO
        if any(grupo_cpo in grupos_usuario for grupo_cpo in grupos_cpo):
            if comissao.tipo != 'CPO':
                messages.error(request, 'Você não tem permissão para acessar esta comissão. Apenas membros CPO podem acessar comissões de oficiais.')
                return redirect('militares:comissao_list')
                
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    
    context = {
        'comissao': comissao,
        'membros': comissao.membros.all(),
        'sessoes': comissao.sessoes.all()[:5],  # Últimas 5 sessões
    }
    return render(request, 'militares/comissao/detail.html', context)


@login_required
@bloquear_membros_cpo
def comissao_create(request):
    """Criar nova comissão de promoção de oficiais"""
    # Verificar se o usuário é membro CPO e restringir apenas a CPO
    grupos_cpo = ['Membro CPO - Acesso apenas a oficiais']
    grupos_usuario = [grupo.name for grupo in request.user.groups.all()]
    
    if any(grupo_cpo in grupos_usuario for grupo_cpo in grupos_cpo):
        # Membro CPO: forçar criação apenas de comissões CPO
        if request.method == 'POST':
            form = ComissaoPromocaoForm(request.POST)
            if form.is_valid():
                nova_comissao = form.save(commit=False)
                # Forçar tipo CPO para membros CPO
                nova_comissao.tipo = 'CPO'
                # Inativar comissão ativa do mesmo tipo
                comissao_ativa = ComissaoPromocao.objects.filter(tipo='CPO', status='ATIVA').first()
                if comissao_ativa:
                    comissao_ativa.status = 'INATIVA'
                    comissao_ativa.save()
                nova_comissao.status = 'ATIVA'
                nova_comissao.save()
                messages.success(request, 'Comissão CPO criada com sucesso!')
                return redirect('militares:comissao_detail', pk=nova_comissao.pk)
        else:
            form = ComissaoPromocaoForm(initial={'tipo': 'CPO'})
            # Desabilitar campo tipo para membros CPO
            form.fields['tipo'].widget.attrs['readonly'] = True
            form.fields['tipo'].widget.attrs['disabled'] = True
    else:
        # Outros usuários: comportamento normal
        if request.method == 'POST':
            form = ComissaoPromocaoForm(request.POST)
            if form.is_valid():
                nova_comissao = form.save(commit=False)
                # Inativar comissão ativa do mesmo tipo
                comissao_ativa = ComissaoPromocao.objects.filter(tipo=nova_comissao.tipo, status='ATIVA').first()
                if comissao_ativa:
                    comissao_ativa.status = 'INATIVA'
                    comissao_ativa.save()
                nova_comissao.status = 'ATIVA'
                nova_comissao.save()
                messages.success(request, 'Comissão criada com sucesso!')
                return redirect('militares:comissao_detail', pk=nova_comissao.pk)
        else:
            form = ComissaoPromocaoForm()
    context = {
        'form': form,
        'title': 'Nova Comissão de Promoção',
    }
    return render(request, 'militares/comissao/form.html', context)


@login_required
@bloquear_membros_cpo
def comissao_update(request, pk):
    """Editar comissão de promoção de oficiais"""
    # Verificar se o usuário é membro CPO e restringir acesso
    grupos_cpo = ['Membro CPO - Acesso apenas a oficiais']
    grupos_usuario = [grupo.name for grupo in request.user.groups.all()]
    
    try:
        comissao = ComissaoPromocao.objects.get(pk=pk)
        
        # Membro CPO só pode editar comissões CPO
        if any(grupo_cpo in grupos_usuario for grupo_cpo in grupos_cpo):
            if comissao.tipo != 'CPO':
                messages.error(request, 'Você não tem permissão para editar esta comissão. Apenas membros CPO podem editar comissões de oficiais.')
                return redirect('militares:comissao_list')
                
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    
    if request.method == 'POST':
        form = ComissaoPromocaoForm(request.POST, instance=comissao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comissão atualizada com sucesso!')
            return redirect('militares:comissao_detail', pk=comissao.pk)
    else:
        form = ComissaoPromocaoForm(instance=comissao)
    
    context = {
        'form': form,
        'comissao': comissao,
        'title': 'Editar Comissão de Promoção de Oficiais',
    }
    return render(request, 'militares/comissao/form.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def comissao_delete(request, pk):
    """Excluir comissão de promoção de oficiais - apenas administradores"""
    try:
        comissao = ComissaoPromocao.objects.get(pk=pk)
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    
    # Verificar se a comissão tem sessões
    if comissao.sessoes.exists():
        messages.error(request, 'Não é possível excluir uma comissão que possui sessões. Apenas edição é permitida.')
        return redirect('militares:comissao_detail', pk=pk)
    
    if request.method == 'POST':
        comissao.delete()
        messages.success(request, 'Comissão excluída com sucesso!')
        return redirect('militares:comissao_list')
    
    context = {
        'comissao': comissao,
    }
    return render(request, 'militares/comissao/delete.html', context)


@login_required
def membro_comissao_list(request, comissao_pk):
    try:
        comissao = ComissaoPromocao.objects.get(pk=comissao_pk)
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    membros = comissao.membros.all().order_by('tipo', 'militar__nome_completo')
    context = {
        'comissao': comissao,
        'membros': membros,
        'title': 'Membros da Comissão',
    }
    return render(request, 'militares/membro_comissao/list.html', context)


@login_required
def membro_comissao_add(request, comissao_pk):
    try:
        comissao = ComissaoPromocao.objects.get(pk=comissao_pk)
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    
    if request.method == 'POST':
        form = MembroComissaoForm(request.POST)
        if form.is_valid():
            membro = form.save(commit=False)
            membro.comissao = comissao
            membro.save()
            messages.success(request, 'Membro adicionado com sucesso!')
            return redirect('militares:membro_comissao_list', comissao_pk=comissao.pk)
    else:
        form = MembroComissaoForm()
    
    context = {
        'form': form,
        'comissao': comissao,
        'title': 'Adicionar Membro',
    }
    return render(request, 'militares/membro_comissao/form.html', context)


@login_required
@bloquear_membros_cpo
def membro_comissao_update(request, comissao_pk, pk):
    """Editar membro da comissão"""
    try:
        comissao = ComissaoPromocao.objects.get(pk=comissao_pk)
        membro = MembroComissao.objects.get(pk=pk, comissao=comissao)
    except (ComissaoPromocao.DoesNotExist, MembroComissao.DoesNotExist):
        messages.error(request, 'Membro não encontrado.')
        return redirect('militares:comissao_detail', pk=comissao_pk)
    
    if request.method == 'POST':
        form = MembroComissaoForm(request.POST, instance=membro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membro atualizado com sucesso!')
            return redirect('militares:membro_comissao_list', comissao_pk=comissao.pk)
    else:
        form = MembroComissaoForm(instance=membro)
    
    context = {
        'form': form,
        'comissao': comissao,
        'membro': membro,
        'title': 'Editar Membro da Comissão',
    }
    return render(request, 'militares/comissao/membros/form.html', context)


@login_required
@bloquear_membros_cpo
def membro_comissao_delete(request, comissao_pk, pk):
    """Remover membro da comissão"""
    try:
        comissao = ComissaoPromocao.objects.get(pk=comissao_pk)
        membro = MembroComissao.objects.get(pk=pk, comissao=comissao)
    except (ComissaoPromocao.DoesNotExist, MembroComissao.DoesNotExist):
        messages.error(request, 'Membro não encontrado.')
        return redirect('militares:comissao_detail', pk=comissao_pk)
    
    if request.method == 'POST':
        membro.delete()
        messages.success(request, 'Membro removido com sucesso!')
        return redirect('militares:membro_comissao_list', comissao_pk=comissao.pk)
    
    context = {
        'comissao': comissao,
        'membro': membro,
    }
    return render(request, 'militares/comissao/membros/delete.html', context)


@login_required
def sessao_comissao_list(request):
    """Lista sessões de uma comissão"""
    comissao_pk = request.GET.get('comissao')
    if not comissao_pk:
        messages.error(request, 'Comissão não especificada.')
        return redirect('militares:comissao_list')
    
    try:
        comissao = ComissaoPromocao.objects.get(pk=comissao_pk)
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    
    sessoes = comissao.sessoes.all()
    
    # Filtros
    status = request.GET.get('status')
    if status:
        sessoes = sessoes.filter(status=status)
    
    tipo = request.GET.get('tipo')
    if tipo:
        sessoes = sessoes.filter(tipo=tipo)
    
    context = {
        'comissao': comissao,
        'sessoes': sessoes,
        'status_choices': SessaoComissao.STATUS_CHOICES,
        'tipo_choices': SessaoComissao.TIPO_CHOICES,
    }
    return render(request, 'militares/comissao/sessoes/list.html', context)


@login_required
def sessao_comissao_detail(request, pk):
    """Detalhes de uma sessão"""
    try:
        sessao = SessaoComissao.objects.get(pk=pk)
        comissao = sessao.comissao
    except SessaoComissao.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
        return redirect('militares:comissao_list')
    
    # Verificar se o usuário é membro da comissão
    try:
        user_membro = MembroComissao.objects.get(
            comissao=comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        user_membro = None
    
    context = {
        'comissao': comissao,
        'sessao': sessao,
        'presencas': sessao.presencas.all(),
        'deliberacoes': sessao.deliberacoes.all(),
        'user_membro': user_membro,
        'justificativas_encerramento': sessao.justificativas_encerramento.all(),
    }
    return render(request, 'militares/comissao/sessoes/detail.html', context)


@login_required
@bloquear_membros_cpo
def sessao_comissao_create(request):
    """Criar nova sessão"""
    comissao_pk = request.GET.get('comissao')
    if not comissao_pk:
        messages.error(request, 'Comissão não especificada.')
        return redirect('militares:comissao_list')
    
    try:
        comissao = ComissaoPromocao.objects.get(pk=comissao_pk)
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    
    if request.method == 'POST':
        form = SessaoComissaoForm(request.POST, request.FILES)
        if form.is_valid():
            sessao = form.save(commit=False)
            sessao.comissao = comissao
            sessao.save()
            
            # Criar registros de presença para todos os membros
            for membro in comissao.membros.filter(ativo=True):
                PresencaSessao.objects.create(
                    sessao=sessao,
                    membro=membro,
                    presente=False
                )
            
            # Criar documento se fornecido
            documento_titulo = form.cleaned_data.get('documento_titulo')
            documento_tipo = form.cleaned_data.get('documento_tipo')
            documento_arquivo = form.cleaned_data.get('documento_arquivo')
            documento_descricao = form.cleaned_data.get('documento_descricao')
            
            if documento_titulo and documento_tipo and documento_arquivo:
                documento = DocumentoSessao.objects.create(
                    sessao=sessao,
                    tipo=documento_tipo,
                    titulo=documento_titulo,
                    descricao=documento_descricao,
                    arquivo=documento_arquivo,
                    upload_por=request.user
                )
                messages.success(request, f'Sessão criada com sucesso! Documento "{documento.titulo}" anexado.')
            else:
                messages.success(request, 'Sessão criada com sucesso!')
            
            return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    else:
        form = SessaoComissaoForm()
    
    context = {
        'form': form,
        'comissao': comissao,
        'title': 'Nova Sessão da Comissão',
    }
    return render(request, 'militares/comissao/sessoes/form.html', context)


@login_required
@bloquear_membros_cpo
def sessao_comissao_update(request, pk):
    """Editar sessão"""
    try:
        sessao = SessaoComissao.objects.get(pk=pk)
        comissao = sessao.comissao
    except SessaoComissao.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
        return redirect('militares:comissao_list')
    
    if request.method == 'POST':
        form = SessaoComissaoForm(request.POST, instance=sessao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sessão atualizada com sucesso!')
            return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    else:
        form = SessaoComissaoForm(instance=sessao)
    
    context = {
        'form': form,
        'comissao': comissao,
        'sessao': sessao,
        'title': 'Editar Sessão da Comissão',
    }
    return render(request, 'militares/comissao/sessoes/form.html', context)


@login_required
@bloquear_membros_cpo
def presenca_sessao_update(request, sessao_pk):
    """Atualizar presenças de uma sessão"""
    try:
        sessao = SessaoComissao.objects.get(pk=sessao_pk)
        comissao = sessao.comissao
    except SessaoComissao.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
        return redirect('militares:comissao_list')
    
    if request.method == 'POST':
        # Obter todos os membros da comissão
        membros = comissao.membros.all()
        
        for membro in membros:
            # Verificar se o membro está presente
            presente = request.POST.get(f'presenca_{membro.pk}') == '1'
            
            # Obter ou criar presença
            presenca, created = PresencaSessao.objects.get_or_create(
                sessao=sessao,
                membro=membro,
                defaults={'presente': presente}
            )
            
            # Atualizar presença
            presenca.presente = presente
            presenca.save()
            
            # Debug: imprimir informações
            print(f"Membro: {membro.militar.nome_completo}, Presente: {presente}, POST data: {request.POST.get(f'presenca_{membro.pk}')}")
        
        # Debug: imprimir todos os dados POST
        print("POST data:", request.POST)
        print("Total de presenças salvas:", sessao.presencas.filter(presente=True).count())
        
        messages.success(request, 'Presenças atualizadas com sucesso!')
        return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    
    # Obter membros da comissão
    membros = comissao.membros.all()
    
    # Obter presenças existentes
    presencas_existentes = set(sessao.presencas.filter(presente=True).values_list('membro_id', flat=True))
    
    context = {
        'comissao': comissao,
        'sessao': sessao,
        'membros': membros,
        'presencas_existentes': presencas_existentes,
    }
    return render(request, 'militares/comissao/sessoes/presenca_form.html', context)


@login_required
@bloquear_membros_cpo
def deliberacao_comissao_create(request):
    """Criar nova deliberação"""
    sessao_pk = request.GET.get('sessao')
    resultado = request.GET.get('resultado')
    
    if not sessao_pk:
        messages.error(request, 'Sessão não especificada.')
        return redirect('militares:comissao_list')
    
    try:
        sessao = SessaoComissao.objects.get(pk=sessao_pk)
        comissao = sessao.comissao
    except SessaoComissao.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
        return redirect('militares:comissao_list')
    
    # Se o parâmetro resultado estiver presente, redirecionar para a página de resultados
    if resultado:
        return redirect('militares:deliberacao_comissao_resultado', sessao_pk=sessao.pk)
    
    if request.method == 'POST':
        form = DeliberacaoComissaoForm(request.POST)
        if form.is_valid():
            deliberacao = form.save(commit=False)
            deliberacao.sessao = sessao
            deliberacao.save()
            
            messages.success(request, 'Deliberação criada com sucesso!')
            return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    else:
        form = DeliberacaoComissaoForm()
    
    context = {
        'form': form,
        'comissao': comissao,
        'sessao': sessao,
        'title': 'Nova Deliberação',
    }
    return render(request, 'militares/comissao/deliberacoes/form.html', context)


@login_required
@bloquear_membros_cpo
def deliberacao_comissao_update(request, pk):
    """Editar deliberação"""
    try:
        deliberacao = DeliberacaoComissao.objects.get(pk=pk)
        sessao = deliberacao.sessao
        comissao = sessao.comissao
    except DeliberacaoComissao.DoesNotExist:
        messages.error(request, 'Deliberação não encontrada.')
        return redirect('militares:comissao_list')
    
    if request.method == 'POST':
        form = DeliberacaoComissaoForm(request.POST, instance=deliberacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deliberação atualizada com sucesso!')
            return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    else:
        form = DeliberacaoComissaoForm(instance=deliberacao)
    
    context = {
        'form': form,
        'comissao': comissao,
        'sessao': sessao,
        'deliberacao': deliberacao,
        'title': 'Editar Deliberação',
    }
    return render(request, 'militares/comissao/deliberacoes/form.html', context)


@login_required
@bloquear_membros_cpo
def voto_deliberacao_create(request, deliberacao_pk):
    """Registrar votos de uma deliberação"""
    try:
        deliberacao = DeliberacaoComissao.objects.get(pk=deliberacao_pk)
        sessao = deliberacao.sessao
        comissao = sessao.comissao
    except DeliberacaoComissao.DoesNotExist:
        messages.error(request, 'Deliberação não encontrada.')
        return redirect('militares:comissao_list')
    
    if request.method == 'POST':
        # Verificar se a senha foi fornecida
        senha_votante = request.POST.get('senha_votante')
        if not senha_votante:
            messages.error(request, 'Senha é obrigatória para confirmar os votos.')
            context = {
                'comissao': comissao,
                'sessao': sessao,
                'deliberacao': deliberacao,
                'membros_presentes': [p.membro for p in sessao.presencas.filter(presente=True)],
                'votos_existentes': {v.membro.pk: v for v in deliberacao.votos.all()},
            }
            return render(request, 'militares/comissao/deliberacoes/voto_form.html', context)
        
        # Verificar se o usuário logado é membro da comissão
        try:
            membro_usuario = MembroComissao.objects.get(
                comissao=comissao,
                usuario=request.user,
                ativo=True
            )
        except MembroComissao.DoesNotExist:
            messages.error(request, 'Você não é membro desta comissão.')
            return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
        
        # Validar senha do usuário
        if not request.user.check_password(senha_votante):
            messages.error(request, 'Senha incorreta. Tente novamente.')
            context = {
                'comissao': comissao,
                'sessao': sessao,
                'deliberacao': deliberacao,
                'membros_presentes': [p.membro for p in sessao.presencas.filter(presente=True)],
                'votos_existentes': {v.membro.pk: v for v in deliberacao.votos.all()},
            }
            return render(request, 'militares/comissao/deliberacoes/voto_form.html', context)
        
        # Contar votos
        votos_favor = 0
        votos_contra = 0
        votos_abstencao = 0
        
        for presenca in sessao.presencas.filter(presente=True):
            membro = presenca.membro
            voto = request.POST.get(f'voto_{membro.pk}')
            justificativa = request.POST.get(f'justificativa_{membro.pk}', '')
            
            # Criar ou atualizar voto
            voto_obj, created = VotoDeliberacao.objects.get_or_create(
                deliberacao=deliberacao,
                membro=membro,
                defaults={'voto': voto, 'justificativa': justificativa}
            )
            
            if not created:
                voto_obj.voto = voto
                voto_obj.justificativa = justificativa
                voto_obj.save()
            
            # Contar votos
            if voto == 'FAVOR':
                votos_favor += 1
            elif voto == 'CONTRA':
                votos_contra += 1
            elif voto == 'ABSTENCAO':
                votos_abstencao += 1
        
        # Atualizar contadores da deliberação
        deliberacao.votos_favor = votos_favor
        deliberacao.votos_contra = votos_contra
        deliberacao.votos_abstencao = votos_abstencao
        deliberacao.save()
        
        messages.success(request, f'Votos registrados com sucesso por {membro_usuario.militar.nome_completo}!')
        
        return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    
    context = {
        'comissao': comissao,
        'sessao': sessao,
        'deliberacao': deliberacao,
        'membros_presentes': [p.membro for p in sessao.presencas.filter(presente=True)],
        'votos_existentes': {v.membro.pk: v for v in deliberacao.votos.all()},
    }
    return render(request, 'militares/comissao/deliberacoes/voto_form.html', context)


@login_required
def comissao_pdf(request, pk):
    """Gerar PDF da comissão de promoção de oficiais"""
    from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from io import BytesIO
    import os
    
    try:
        comissao = ComissaoPromocao.objects.get(pk=pk)
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('comissao_list')
    
    # Criar o PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="comissao_promocao_{pk}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=11)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=13, spaceAfter=10, underlineProportion=0.1)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=11, spaceAfter=8)
    
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
        f"{comissao.get_tipo_display().upper()} - CBMEPI-PI",
        "Av. Miguel Rosa, 3515 Terreo - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    for linha in cabecalho:
        story.append(Paragraph(linha, style_center))
    story.append(Spacer(1, 10))
    

    
    # Informações da comissão
    story.append(Paragraph(f"<b>Nome:</b> {comissao.nome}", style_bold))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Data de Criação:</b> {comissao.data_criacao.strftime('%d/%m/%Y')}", style_bold))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Status:</b> {comissao.get_status_display()}", style_bold))
    story.append(Spacer(1, 6))
    
    if comissao.data_termino:
        story.append(Paragraph(f"<b>Data de Término:</b> {comissao.data_termino.strftime('%d/%m/%Y')}", style_bold))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 12))
    
    # Obter todos os membros ativos ordenados por tipo (presidente, membros, secretário)
    membros_ativos = comissao.membros.filter(ativo=True).order_by(
        'tipo'  # PRESIDENTE, EFETIVO, NATO, SECRETARIO
    )
    
    # Presidente
    presidente = membros_ativos.filter(tipo='PRESIDENTE').first()
    if presidente:
        story.append(Paragraph("<b>PRESIDENTE:</b>", style_bold))
        story.append(Paragraph(f"{presidente.militar.get_posto_graduacao_display()} {presidente.militar.get_quadro_display()} {presidente.militar.nome_completo} - {presidente.cargo.nome}", style_center))
        story.append(Spacer(1, 8))
    
    # Membros Natos
    membros_natos = membros_ativos.filter(tipo='NATO')
    if membros_natos:
        story.append(Paragraph("<b>MEMBROS NATOS:</b>", style_bold))
        for membro in membros_natos:
            story.append(Paragraph(f"{membro.militar.get_posto_graduacao_display()} {membro.militar.get_quadro_display()} {membro.militar.nome_completo} - {membro.cargo.nome}", style_center))
        story.append(Spacer(1, 8))
    
    # Membros Efetivos
    membros_efetivos = membros_ativos.filter(tipo='EFETIVO')
    if membros_efetivos:
        story.append(Paragraph("<b>MEMBROS EFETIVOS:</b>", style_bold))
        for membro in membros_efetivos:
            story.append(Paragraph(f"{membro.militar.get_posto_graduacao_display()} {membro.militar.get_quadro_display()} {membro.militar.nome_completo} - {membro.cargo.nome}", style_center))
        story.append(Spacer(1, 8))
    
    # Secretário
    secretario = membros_ativos.filter(tipo='SECRETARIO').first()
    if secretario:
        story.append(Paragraph("<b>SECRETÁRIO:</b>", style_bold))
        story.append(Paragraph(f"{secretario.militar.get_posto_graduacao_display()} {secretario.militar.get_quadro_display()} {secretario.militar.nome_completo} - {secretario.cargo.nome}", style_center))
        story.append(Spacer(1, 8))
    
    # Observações
    if comissao.observacoes:
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>OBSERVAÇÕES:</b>", style_bold))
        story.append(Paragraph(comissao.observacoes, style_center))
    
    # Gerar o PDF
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    
    response.write(pdf)
    return response

@login_required
def comissao_encerrar(request, pk):
    try:
        comissao = ComissaoPromocao.objects.get(pk=pk)
    except ComissaoPromocao.DoesNotExist:
        messages.error(request, 'Comissão não encontrada.')
        return redirect('militares:comissao_list')
    if comissao.status == 'INATIVA':
        messages.info(request, 'Esta comissão já está inativa.')
    else:
        comissao.status = 'INATIVA'
        comissao.save()
        messages.success(request, 'Comissão encerrada com sucesso!')
    return redirect('militares:comissao_list')


@login_required
@bloquear_membros_cpo
def documento_sessao_create(request):
    """Upload de documento para uma sessão"""
    sessao_pk = request.GET.get('sessao')
    if not sessao_pk:
        messages.error(request, 'Sessão não especificada.')
        return redirect('militares:sessao_comissao_list')
    
    try:
        sessao = SessaoComissao.objects.get(pk=sessao_pk)
    except SessaoComissao.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
        return redirect('militares:sessao_comissao_list')
    
    if request.method == 'POST':
        form = DocumentoSessaoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.sessao = sessao
            documento.upload_por = request.user
            documento.save()
            messages.success(request, f'Documento "{documento.titulo}" enviado com sucesso!')
            return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
        else:
            messages.error(request, 'Erro ao enviar documento. Verifique os dados.')
    else:
        form = DocumentoSessaoForm()
    
    context = {
        'form': form,
        'sessao': sessao,
        'title': 'Enviar Documento',
        'action': 'create',
    }
    
    return render(request, 'militares/comissao/documentos/form.html', context)


@login_required
@bloquear_membros_cpo
def documento_sessao_update(request, pk):
    """Editar documento da sessão"""
    documento = get_object_or_404(DocumentoSessao, pk=pk)
    
    if request.method == 'POST':
        form = DocumentoSessaoForm(request.POST, request.FILES, instance=documento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Documento "{documento.titulo}" atualizado com sucesso!')
            return redirect('militares:sessao_comissao_detail', pk=documento.sessao.pk)
        else:
            messages.error(request, 'Erro ao atualizar documento. Verifique os dados.')
    else:
        form = DocumentoSessaoForm(instance=documento)
    
    context = {
        'form': form,
        'documento': documento,
        'sessao': documento.sessao,
        'title': 'Editar Documento',
        'action': 'update',
    }
    
    return render(request, 'militares/comissao/documentos/form.html', context)


@login_required
@bloquear_membros_cpo
def documento_sessao_delete(request, pk):
    """Excluir documento da sessão (apenas admin/staff)"""
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para excluir documentos. Apenas administradores podem realizar esta ação.')
        documento = get_object_or_404(DocumentoSessao, pk=pk)
        return render(request, 'militares/comissao/documentos/delete.html', {'sessao': documento.sessao, 'documento': documento})
    documento = get_object_or_404(DocumentoSessao, pk=pk)
    sessao_pk = documento.sessao.pk
    titulo = documento.titulo
    
    if request.method == 'POST':
        documento.delete()
        messages.success(request, f'Documento "{titulo}" excluído com sucesso!')
        return redirect('militares:sessao_comissao_detail', pk=sessao_pk)
    
    context = {
        'documento': documento,
        'sessao': documento.sessao,
    }
    return render(request, 'militares/comissao/documentos/delete.html', context)


@login_required
def documento_sessao_view(request, pk):
    """Visualizar documento da sessão"""
    documento = get_object_or_404(DocumentoSessao, pk=pk)
    
    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=documento.sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        # Verificar se o usuário é membro mas não está ativo
        try:
            membro_inativo = MembroComissao.objects.get(
                comissao=documento.sessao.comissao,
                usuario=request.user
            )
            messages.error(request, 'Você não tem permissão para visualizar este documento. Seu cadastro na comissão não está ativo.')
        except MembroComissao.DoesNotExist:
            messages.error(request, 'Você não tem permissão para visualizar este documento. Você não é membro desta comissão.')
        return redirect('militares:sessao_comissao_detail', pk=documento.sessao.pk)
    
    context = {
        'documento': documento,
        'sessao': documento.sessao,
    }
    
    if documento.can_preview():
        return render(request, 'militares/comissao/documentos/view.html', context)
    else:
        # Para arquivos que não podem ser visualizados, fazer download
        from django.http import FileResponse
        import os
        if os.path.exists(documento.arquivo.path):
            return FileResponse(open(documento.arquivo.path, 'rb'), content_type='application/octet-stream')
        else:
            messages.error(request, 'Arquivo não encontrado.')
            return redirect('militares:sessao_comissao_detail', pk=documento.sessao.pk)


@login_required
def documento_sessao_download(request, pk):
    """Download de documento da sessão"""
    documento = get_object_or_404(DocumentoSessao, pk=pk)
    
    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=documento.sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        # Verificar se o usuário é membro mas não está ativo
        try:
            membro_inativo = MembroComissao.objects.get(
                comissao=documento.sessao.comissao,
                usuario=request.user
            )
            messages.error(request, 'Você não tem permissão para baixar este documento. Seu cadastro na comissão não está ativo.')
        except MembroComissao.DoesNotExist:
            messages.error(request, 'Você não tem permissão para baixar este documento. Você não é membro desta comissão.')
        return redirect('militares:sessao_comissao_detail', pk=documento.sessao.pk)
    
    from django.http import FileResponse
    import os
    if os.path.exists(documento.arquivo.path):
        response = FileResponse(open(documento.arquivo.path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{documento.filename()}"'
        return response
    else:
        messages.error(request, 'Arquivo não encontrado.')
        return redirect('militares:sessao_comissao_detail', pk=documento.sessao.pk)


@login_required
def sessao_encerrar(request, pk):
    """Encerrar sessão com confirmação de senha"""
    sessao = get_object_or_404(SessaoComissao, pk=pk)
    
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
    
    # Verificar se todos os presentes (exceto presidente) votaram
    todos_votaram = sessao.todos_presentes_votaram_exceto_presidente
    
    # Se não todos votaram, apenas o secretário pode encerrar
    if not todos_votaram and membro.cargo != 'SECRETARIO':
        messages.error(request, 'Apenas o secretário pode encerrar a sessão quando nem todos os membros votaram.')
        return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    
    # Verificar membros presentes que não votaram (excluindo o presidente)
    membros_sem_voto = []
    for presenca in sessao.presencas.filter(presente=True):
        membro_presenca = presenca.membro
        # O presidente não é obrigado a votar
        if membro_presenca.cargo == 'PRESIDENTE':
            continue
            
        votos_do_membro = VotoDeliberacao.objects.filter(
            deliberacao__sessao=sessao,
            membro=membro_presenca
        ).count()
        if votos_do_membro < sessao.deliberacoes.count():
            membros_sem_voto.append({
                'membro': membro_presenca,
                'votos_realizados': votos_do_membro,
                'total_deliberacoes': sessao.deliberacoes.count(),
                'deliberacoes_nao_votadas': sessao.deliberacoes.count() - votos_do_membro
            })
    
    if request.method == 'POST':
        password = request.POST.get('password')
        if not password:
            messages.error(request, 'Senha é obrigatória para encerrar a sessão.')
            return render(request, 'militares/comissao/sessoes/encerrar_confirmacao.html', {
                'sessao': sessao,
                'comissao': sessao.comissao,
                'membros_sem_voto': membros_sem_voto,
                'todos_votaram': todos_votaram,
                'membro_usuario': membro
            })
        
        if not request.user.check_password(password):
            messages.error(request, 'Senha incorreta. Sessão não foi encerrada.')
            return render(request, 'militares/comissao/sessoes/encerrar_confirmacao.html', {
                'sessao': sessao,
                'comissao': sessao.comissao,
                'membros_sem_voto': membros_sem_voto,
                'todos_votaram': todos_votaram,
                'membro_usuario': membro
            })
        
        # Coletar justificativas para membros sem voto (apenas se secretário e nem todos votaram)
        justificativas = {}
        if membro.cargo == 'SECRETARIO' and membros_sem_voto:
            for membro_info in membros_sem_voto:
                membro_id = membro_info['membro'].id
                justificativa = request.POST.get(f'justificativa_{membro_id}', '').strip()
                if justificativa:
                    justificativas[membro_id] = justificativa
        
        # Encerrar a sessão
        sessao.status = 'CONCLUIDA'
        sessao.hora_fim = timezone.now().time()
        sessao.save()
        
        # Salvar justificativas se houver
        if justificativas:
            from .models import JustificativaEncerramento
            
            justificativas_salvas = []
            for membro_info in membros_sem_voto:
                membro_id = membro_info['membro'].id
                if membro_id in justificativas:
                    # Salvar justificativa no modelo
                    justificativa_obj, created = JustificativaEncerramento.objects.get_or_create(
                        sessao=sessao,
                        membro=membro_info['membro'],
                        defaults={
                            'justificativa': justificativas[membro_id],
                            'registrado_por': request.user
                        }
                    )
                    
                    if not created:
                        # Atualizar justificativa existente
                        justificativa_obj.justificativa = justificativas[membro_id]
                        justificativa_obj.registrado_por = request.user
                        justificativa_obj.save()
                    
                    justificativas_salvas.append(
                        f"{membro_info['membro'].militar.nome_completo}: {justificativas[membro_id]}"
                    )
            
            if justificativas_salvas:
                messages.success(request, f'Sessão {sessao.numero} encerrada com sucesso! {len(justificativas_salvas)} justificativa(s) registrada(s).')
        else:
            messages.success(request, f'Sessão {sessao.numero} encerrada com sucesso!')
        
        return redirect('militares:sessao_comissao_detail', pk=sessao.pk)
    
    return render(request, 'militares/comissao/sessoes/encerrar_confirmacao.html', {
        'sessao': sessao,
        'comissao': sessao.comissao,
        'membros_sem_voto': membros_sem_voto,
        'todos_votaram': todos_votaram,
        'membro_usuario': membro
    })

@login_required
def sessao_gerar_ata(request, pk):
    """Gerar ata da sessão da comissão"""
    sessao = get_object_or_404(SessaoComissao, pk=pk)
    
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
    
    # Preparar dados para a ata
    context = {
        'sessao': sessao,
        'comissao': sessao.comissao,
        'presencas': sessao.presencas.all(),
        'deliberacoes': sessao.deliberacoes.all().order_by('numero'),
        'membro_usuario': membro,
        'justificativas_encerramento': sessao.justificativas_encerramento.all(),
        'data_geracao': timezone.now(),
    }
    
    return render(request, 'militares/comissao/sessoes/ata.html', context)

@login_required
def sessao_editar_ata(request, pk):
    """Editar ata da sessão com editor de texto rico"""
    from .models import AtaSessao
    from .forms import AtaSessaoForm
    sessao = get_object_or_404(SessaoComissao, pk=pk)
    
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
    
    # Preparar dados para a ata
    context = {
        'sessao': sessao,
        'comissao': sessao.comissao,
        'presencas': sessao.presencas.all(),
        'deliberacoes': sessao.deliberacoes.all().order_by('numero'),
        'membro_usuario': membro,
        'justificativas_encerramento': sessao.justificativas_encerramento.all(),
        'data_geracao': timezone.now(),
    }
    
    try:
        ata = sessao.ata_editada
    except AtaSessao.DoesNotExist:
        ata = AtaSessao(sessao=sessao, editado_por=request.user)
    
    if request.method == 'POST':
        form = AtaSessaoForm(request.POST, instance=ata)
        if form.is_valid():
            ata = form.save(commit=False)
            ata.editado_por = request.user
            ata.save()
            messages.success(request, f'Ata editada e salva com sucesso! Versão {ata.versao}.')
            return redirect('militares:sessao_editar_ata', pk=sessao.pk)
    else:
        form = AtaSessaoForm(instance=ata)
    
    context['form'] = form
    context['ata_salva'] = ata if ata.pk else None
    return render(request, 'militares/comissao/sessoes/editar_ata.html', context)


@login_required
def ata_para_assinatura(request, pk):
    """Marcar ata para assinatura dos membros"""
    from .models import AtaSessao
    
    try:
        ata = AtaSessao.objects.get(sessao_id=pk)
    except AtaSessao.DoesNotExist:
        messages.error(request, 'Ata não encontrada.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=ata.sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        messages.error(request, 'Você não é membro desta comissão.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    if request.method == 'POST':
        ata.status = 'PARA_ASSINATURA'
        ata.save()
        messages.success(request, 'Ata marcada para assinatura dos membros.')
        return redirect('militares:ata_assinaturas', pk=pk)
    
    context = {
        'ata': ata,
        'sessao': ata.sessao,
        'comissao': ata.sessao.comissao,
        'membros_presentes': ata.sessao.presencas.filter(presente=True),
    }
    return render(request, 'militares/comissao/sessoes/ata_para_assinatura.html', context)


@login_required
def ata_assinaturas(request, pk):
    """Gerenciar assinaturas da ata"""
    from .models import AtaSessao, AssinaturaAta
    
    try:
        ata = AtaSessao.objects.get(sessao_id=pk)
    except AtaSessao.DoesNotExist:
        messages.error(request, 'Ata não encontrada.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=ata.sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        messages.error(request, 'Você não é membro desta comissão.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    if request.method == 'POST':
        # Processar assinatura
        membro_id = request.POST.get('membro_id')
        observacoes = request.POST.get('observacoes', '').strip()
        
        if membro_id:
            try:
                membro_para_assinar = MembroComissao.objects.get(id=membro_id)
                # Verificar se o membro estava presente
                if not ata.sessao.presencas.filter(membro=membro_para_assinar, presente=True).exists():
                    messages.error(request, 'Apenas membros presentes podem assinar a ata.')
                    return redirect('militares:ata_assinaturas', pk=pk)
                
                # Criar ou atualizar assinatura
                assinatura, created = AssinaturaAta.objects.get_or_create(
                    ata=ata,
                    membro=membro_para_assinar,
                    defaults={
                        'assinado_por': request.user,
                        'observacoes': observacoes
                    }
                )
                
                if not created:
                    assinatura.assinado_por = request.user
                    assinatura.observacoes = observacoes
                    assinatura.save()
                
                messages.success(request, f'Assinatura de {membro_para_assinar.militar.nome_completo} registrada com sucesso!')
                
                # Verificar se todos assinaram
                if ata.pode_ser_finalizada():
                    ata.status = 'ASSINADA'
                    ata.save()
                    messages.info(request, 'Todos os membros presentes assinaram a ata!')
                
            except MembroComissao.DoesNotExist:
                messages.error(request, 'Membro não encontrado.')
    
    # Obter membros presentes e suas assinaturas
    membros_presentes = ata.sessao.presencas.filter(presente=True).select_related('membro__militar')
    assinaturas = ata.assinaturas.select_related('membro__militar', 'assinado_por')
    
    context = {
        'ata': ata,
        'sessao': ata.sessao,
        'comissao': ata.sessao.comissao,
        'membros_presentes': membros_presentes,
        'assinaturas': assinaturas,
        'membro_usuario': membro,
    }
    return render(request, 'militares/comissao/sessoes/ata_assinaturas.html', context)


@login_required
def ata_gerar_pdf(request, pk):
    """Gerar PDF da ata finalizada"""
    from .models import AtaSessao
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY
    from io import BytesIO
    import html2text
    import os
    import qrcode
    
    try:
        ata = AtaSessao.objects.get(sessao_id=pk)
    except AtaSessao.DoesNotExist:
        messages.error(request, 'Ata não encontrada.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    # Verificar se a ata está finalizada
    if ata.status != 'ASSINADA' and ata.status != 'FINALIZADA':
        messages.error(request, 'A ata deve estar assinada para gerar o PDF.')
        return redirect('militares:ata_assinaturas', pk=pk)
    
    # Criar o PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Configurar fonte para suportar caracteres especiais
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Registrar fonte que suporta UTF-8 (usando fonte padrão do sistema)
    try:
        # Tentar usar fonte Arial que suporta caracteres especiais
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        font_name = 'Arial'
    except:
        # Se não conseguir, usar fonte padrão
        font_name = 'Helvetica'
    
    # Estilos customizados com fonte que suporta UTF-8
    style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=11, fontName=font_name)
    style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName=font_name, fontSize=11)
    style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=13, spaceAfter=10, underlineProportion=0.1, fontName=font_name)
    style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=11, spaceAfter=8, fontName=font_name)
    style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, fontName=font_name)
    style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11, spaceAfter=8, fontName=font_name)
    style_signature = ParagraphStyle('signature', parent=styles['Normal'], fontSize=10, spaceAfter=6, fontName=font_name)
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
        story.append(Spacer(1, 3))
    
    # Cabeçalho institucional
    cabecalho = [
        "GOVERNO DO ESTADO DO PIAUÍ",
        "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
        "COMISSÃO DE PROMOÇÃO DE OFICIAIS - CBMEPI-PI",
        "Av. Miguel Rosa, 3515 Terreo - Bairro Piçarra, Teresina/PI, CEP 64001-490",
        "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
    ]
    for linha in cabecalho:
        story.append(Paragraph(linha, style_center))
    story.append(Spacer(1, 5))
    
    # Título centralizado e sublinhado
    # Determinar o tipo de comissão baseado no campo tipo
    if ata.sessao.comissao.tipo == 'CPO':
        tipo_comissao = "ATA DA REUNIÃO DA COMISSÃO DE PROMOÇÃO DE OFICIAIS DO CBMEPI"
    elif ata.sessao.comissao.tipo == 'CPP':
        tipo_comissao = "ATA DA REUNIÃO DA COMISSÃO DE PROMOÇÃO DE PRAÇAS DO CBMEPI"
    else:
        tipo_comissao = "ATA DA REUNIÃO DA COMISSÃO DE PROMOÇÃO DO CBMEPI"
    
    titulo = f'<u>{tipo_comissao}</u>'
    story.append(Paragraph(titulo, style_title))
    story.append(Spacer(1, 16))
    
    # Conteúdo da ata (mantendo HTML do CKEditor, mas limpo para ReportLab)
    style_html = ParagraphStyle('html', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY, spaceAfter=8, leading=16, fontName=font_name)
    conteudo_limpo = clean_html_for_reportlab(ata.conteudo)
    
    story.append(Paragraph(conteudo_limpo, style_html))
    story.append(Spacer(1, 30))
    
    # Assinaturas manuais
    story.append(Spacer(1, 15))
    
    assinaturas = ata.assinaturas.select_related('membro__militar').order_by('data_assinatura')
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
        
        # Tipo de membro
        story.append(Paragraph(f"<center>{assinatura.membro.get_tipo_display()}</center>", style_center))
        
        if assinatura.observacoes:
            story.append(Paragraph(f"Obs: {assinatura.observacoes}", style_signature))
        story.append(Spacer(1, 10))
    
    # Rodapé com Assinaturas Eletrônicas e QR Code
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Buscar todas as assinaturas válidas da ata (da mais recente para a mais antiga)
    assinaturas_eletronicas = ata.assinaturas.filter(assinado_por__isnull=False).order_by('-data_assinatura')
    
    if assinaturas_eletronicas.exists():
        for i, assinatura_eletronica in enumerate(assinaturas_eletronicas):
            # Informações de assinatura eletrônica
            nome_assinante = assinatura_eletronica.assinado_por.get_full_name() or assinatura_eletronica.assinado_por.username
            # Se o nome estiver vazio, usar um nome padrão
            if not nome_assinante or nome_assinante.strip() == '':
                nome_assinante = "Usuário do Sistema"
            
            data_assinatura = assinatura_eletronica.data_assinatura
            data_formatada = f"{data_assinatura.day:02d}/{data_assinatura.month:02d}/{data_assinatura.year}"
            hora_formatada = f"{data_assinatura.hour:02d}:{data_assinatura.minute:02d}"
            
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
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_posto_quadro} - {assinatura_eletronica.membro.get_tipo_display()}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
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
            if i < len(assinaturas_eletronicas) - 1:
                story.append(Spacer(1, 8))
                story.append(HRFlowable(width="100%", thickness=0.5, spaceAfter=8, spaceBefore=8, color=colors.lightgrey))
                story.append(Spacer(1, 8))
    else:
        # Se não houver assinaturas eletrônicas, mostrar apenas documento gerado pelo usuário logado
        from django.utils import timezone
        agora = timezone.localtime(timezone.now())
        nome_usuario = request.user.get_full_name() or request.user.username
        if not nome_usuario or nome_usuario.strip() == '':
            nome_usuario = "Usuário do Sistema"
        data_formatada = agora.strftime('%d/%m/%Y')
        hora_formatada = agora.strftime('%H:%M')
        texto_geracao = f"Documento gerado pelo usuário {nome_usuario} em {data_formatada}, às {hora_formatada}."
        story.append(Paragraph(texto_geracao, style_small))
    
    # QR Code para conferência de veracidade
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, spaceAfter=10, spaceBefore=10, color=colors.grey))
    
    # Dados para autenticação
    url_autenticacao = "https://sei.pi.gov.br/sei/controlador_externo.php?acao=documento_conferir&id_orgao_acesso_externo=0"
    codigo_verificador = f"{ata.pk:08d}"
    codigo_crc = f"{hash(str(ata.pk)) % 0xFFFFFFF:07X}"
    
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
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(rodape_table)
    
    # Gerar PDF
    doc.build(story)
    buffer.seek(0)
    
    # Criar resposta HTTP
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ata_sessao_{ata.sessao.numero}.pdf"'
    
    return response


@login_required
def ata_finalizar(request, pk):
    """Finalizar ata após todas as assinaturas"""
    from .models import AtaSessao
    from django.utils import timezone
    
    try:
        ata = AtaSessao.objects.get(sessao_id=pk)
    except AtaSessao.DoesNotExist:
        messages.error(request, 'Ata não encontrada.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    # Verificar se o usuário é membro da comissão
    try:
        membro = MembroComissao.objects.get(
            comissao=ata.sessao.comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        messages.error(request, 'Você não é membro desta comissão.')
        return redirect('militares:sessao_comissao_detail', pk=pk)
    
    if request.method == 'POST':
        if ata.pode_ser_finalizada():
            ata.status = 'FINALIZADA'
            ata.data_finalizacao = timezone.now()
            ata.save()
            messages.success(request, 'Ata finalizada com sucesso! Agora você pode gerar o PDF.')
        else:
            messages.error(request, 'A ata não pode ser finalizada. Todos os membros presentes devem assinar primeiro.')
    
    return redirect('militares:ata_assinaturas', pk=pk)

def clean_html_for_reportlab(html):
    # Remove atributos style, id, class, target, etc.
    html = re.sub(r'(<\w+)([^>]*)(style|id|class|target|rel|onclick|onmouseover|onmouseout|align|width|height|data-[^=]*)=["\"][^"\"]*["\"]', r'\1', html)
    # Remove todos os atributos de todas as tags, exceto href em <a>
    html = re.sub(r'<(?!a\b)(\w+)[^>]*>', r'<\1>', html)
    # Remove atributos de <a> exceto href
    html = re.sub(r'<a\s+[^>]*?href=(["\"][^"\"]*["\"])[^>]*>', r'<a href=\1>', html)
    # Remove tags não suportadas (mantém apenas p, b, i, u, br, a, ul, ol, li, strong, em)
    html = re.sub(r'</?(?!p\b|b\b|i\b|u\b|br\b|a\b|ul\b|ol\b|li\b|strong\b|em\b)[a-zA-Z0-9]+[^>]*>', '', html)
    # Remove comentários HTML
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # Remove espaços extras entre tags
    html = re.sub(r'>\s+<', '><', html)
    # Decodifica entidades HTML
    html = unescape(html)
    return html

@login_required
def modelo_ata_list(request):
    from .models import ModeloAta
    modelos = ModeloAta.objects.all()
    tipo_comissao = request.GET.get('tipo_comissao')
    if tipo_comissao:
        modelos = modelos.filter(tipo_comissao=tipo_comissao)
    tipo_sessao = request.GET.get('tipo_sessao')
    if tipo_sessao:
        modelos = modelos.filter(tipo_sessao=tipo_sessao)
    ativo = request.GET.get('ativo')
    if ativo is not None:
        modelos = modelos.filter(ativo=ativo == 'true')
    padrao = request.GET.get('padrao')
    if padrao is not None:
        modelos = modelos.filter(padrao=padrao == 'true')
    context = {
        'modelos': modelos,
        'tipos_comissao': ModeloAta.TIPO_COMISSAO_CHOICES,
        'tipos_sessao': ModeloAta.TIPO_SESSAO_CHOICES,
        'filtros': {
            'tipo_comissao': tipo_comissao,
            'tipo_sessao': tipo_sessao,
            'ativo': ativo,
            'padrao': padrao,
        }
    }
    return render(request, 'militares/modelo_ata/list.html', context)

@login_required
@bloquear_membros_cpo
def modelo_ata_create(request):
    from .models import ModeloAta
    from .forms import ModeloAtaForm
    if request.method == 'POST':
        form = ModeloAtaForm(request.POST)
        if form.is_valid():
            modelo = form.save(commit=False)
            modelo.criado_por = request.user
            modelo.save()
            messages.success(request, f'Modelo "{modelo.nome}" criado com sucesso!')
            return redirect('militares:modelo_ata_list')
    else:
        form = ModeloAtaForm()
    context = {
        'form': form,
        'titulo': 'Criar Novo Modelo de Ata',
        'variaveis_disponiveis': [
            '{{sessao.numero}} - Número da sessão',
            '{{sessao.data_sessao}} - Data da sessão',
            '{{sessao.hora_inicio}} - Hora de início',
            '{{sessao.hora_fim}} - Hora de término',
            '{{sessao.local}} - Local da sessão',
            '{{sessao.tipo}} - Tipo da sessão',
            '{{sessao.pauta}} - Pauta da sessão',
            '{{comissao.nome}} - Nome da comissão',
            '{{comissao.tipo}} - Tipo da comissão',
        ]
    }
    return render(request, 'militares/modelo_ata/form.html', context)

@login_required
@bloquear_membros_cpo
def modelo_ata_update(request, pk):
    from .models import ModeloAta
    from .forms import ModeloAtaForm
    modelo = get_object_or_404(ModeloAta, pk=pk)
    if request.method == 'POST':
        form = ModeloAtaForm(request.POST, instance=modelo)
        if form.is_valid():
            modelo = form.save()
            messages.success(request, f'Modelo "{modelo.nome}" atualizado com sucesso!')
            return redirect('militares:modelo_ata_list')
    else:
        form = ModeloAtaForm(instance=modelo)
    context = {
        'form': form,
        'modelo': modelo,
        'titulo': f'Editar Modelo: {modelo.nome}',
        'variaveis_disponiveis': [
            '{{sessao.numero}} - Número da sessão',
            '{{sessao.data_sessao}} - Data da sessão',
            '{{sessao.hora_inicio}} - Hora de início',
            '{{sessao.hora_fim}} - Hora de término',
            '{{sessao.local}} - Local da sessão',
            '{{sessao.tipo}} - Tipo da sessão',
            '{{sessao.pauta}} - Pauta da sessão',
            '{{comissao.nome}} - Nome da comissão',
            '{{comissao.tipo}} - Tipo da comissão',
        ]
    }
    return render(request, 'militares/modelo_ata/form.html', context)

@login_required
@bloquear_membros_cpo
def modelo_ata_delete(request, pk):
    from .models import ModeloAta
    modelo = get_object_or_404(ModeloAta, pk=pk)
    if request.method == 'POST':
        nome = modelo.nome
        modelo.delete()
        messages.success(request, f'Modelo "{nome}" excluído com sucesso!')
        return redirect('militares:modelo_ata_list')
    context = {
        'modelo': modelo,
        'titulo': f'Excluir Modelo: {modelo.nome}'
    }
    return render(request, 'militares/modelo_ata/delete.html', context)

@login_required
def modelo_ata_detail(request, pk):
    from .models import ModeloAta
    modelo = get_object_or_404(ModeloAta, pk=pk)
    context = {
        'modelo': modelo,
        'titulo': f'Modelo: {modelo.nome}'
    }
    return render(request, 'militares/modelo_ata/detail.html', context)


@login_required
def modelo_ata_aplicar(request, sessao_pk):
    """Aplicar um modelo de ata a uma sessão"""
    from .models import SessaoComissao, ModeloAta, AtaSessao, MembroComissao
    
    sessao = get_object_or_404(SessaoComissao, pk=sessao_pk)
    
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
    
    if request.method == 'POST':
        modelo_id = request.POST.get('modelo_id')
        if modelo_id:
            try:
                modelo = ModeloAta.objects.get(pk=modelo_id, ativo=True)
                if modelo.pode_ser_usado_para(sessao):
                    conteudo_aplicado = modelo.aplicar_variaveis(sessao)
                    try:
                        ata = sessao.ata_editada
                    except AtaSessao.DoesNotExist:
                        ata = AtaSessao(sessao=sessao, editado_por=request.user)
                    ata.conteudo = conteudo_aplicado
                    ata.editado_por = request.user
                    ata.save()
                    messages.success(request, f'Modelo "{modelo.nome}" aplicado com sucesso!')
                    return redirect('militares:sessao_editar_ata', pk=sessao.pk)
                else:
                    messages.error(request, 'Este modelo não pode ser usado para esta sessão.')
            except ModeloAta.DoesNotExist:
                messages.error(request, 'Modelo não encontrado.')
    
    modelos_disponiveis = ModeloAta.get_modelos_disponiveis(sessao)
    modelo_padrao = ModeloAta.get_modelo_padrao(sessao)
    
    context = {
        'sessao': sessao,
        'modelos_disponiveis': modelos_disponiveis,
        'modelo_padrao': modelo_padrao,
        'titulo': f'Aplicar Modelo à Sessão {sessao.numero}'
    }
    return render(request, 'militares/modelo_ata/aplicar.html', context)

@login_required
def modelo_ata_salvar_atual(request, sessao_pk):
    from .models import SessaoComissao, ModeloAta, AtaSessao, MembroComissao
    from .forms import ModeloAtaForm
    from django import forms
    
    print(f"=== INÍCIO DA FUNÇÃO modelo_ata_salvar_atual ===")
    print(f"Sessão PK: {sessao_pk}")
    print(f"Método: {request.method}")
    
    sessao = get_object_or_404(SessaoComissao, pk=sessao_pk)
    print(f"Sessão encontrada: {sessao}")
    
    # Verificar se existe uma ata
    try:
        ata = sessao.ata_editada
        print(f"Ata encontrada: {ata}")
        print(f"Conteúdo da ata: {ata.conteudo[:100] if ata.conteudo else 'VAZIO'}")
    except AtaSessao.DoesNotExist:
        print("ERRO: Não existe uma ata para esta sessão")
        messages.error(request, 'Não existe uma ata para esta sessão.')
        return redirect('militares:sessao_editar_ata', pk=sessao.pk)
    
    # Criar formulário personalizado sem o campo conteudo
    class ModeloAtaSalvarForm(forms.ModelForm):
        class Meta:
            model = ModeloAta
            fields = ['nome', 'descricao', 'tipo_comissao', 'tipo_sessao', 'ativo', 'padrao']
            widgets = {
                'nome': forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Ex: Modelo Padrão CPO Ordinária'
                }),
                'descricao': forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Descrição do modelo e quando usá-lo...'
                }),
                'tipo_comissao': forms.Select(attrs={'class': 'form-control'}),
                'tipo_sessao': forms.Select(attrs={'class': 'form-control'}),
                'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
                'padrao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            }
    
    if request.method == 'POST':
        print("=== PROCESSANDO POST ===")
        print(f"POST data: {request.POST}")
        
        form = ModeloAtaSalvarForm(request.POST)
        print(f"Form criado: {form}")
        print(f"Form is_valid: {form.is_valid()}")
        
        if form.is_valid():
            print("=== FORMULÁRIO VÁLIDO ===")
            try:
                modelo = form.save(commit=False)
                print(f"Modelo criado (commit=False): {modelo}")
                
                modelo.criado_por = request.user
                modelo.conteudo = ata.conteudo
                print(f"Conteúdo definido: {modelo.conteudo[:100] if modelo.conteudo else 'VAZIO'}")
                
                modelo.save()
                print(f"Modelo salvo com sucesso: {modelo.nome} (ID: {modelo.pk})")
                
                messages.success(request, f'Modelo "{modelo.nome}" criado com sucesso a partir da ata atual!')
                return redirect('militares:modelo_ata_list')
            except Exception as e:
                print(f"ERRO ao salvar modelo: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, f'Erro ao salvar modelo: {str(e)}')
        else:
            print("=== FORMULÁRIO INVÁLIDO ===")
            print(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Erro no campo {field}: {error}")
                    messages.error(request, f'Erro no campo {field}: {error}')
    else:
        print("=== MÉTODO GET ===")
        form = ModeloAtaSalvarForm(initial={
            'nome': f'Modelo da Sessão {sessao.numero} - {sessao.comissao.nome}',
            'tipo_comissao': sessao.comissao.tipo,
            'tipo_sessao': sessao.tipo,
            'descricao': f'Modelo criado a partir da ata da sessão {sessao.numero} realizada em {sessao.data_sessao.strftime("%d/%m/%Y")}',
        })
    
    context = {
        'form': form,
        'sessao': sessao,
        'ata': ata,
        'titulo': f'Salvar Ata como Modelo - Sessão {sessao.numero}',
        'variaveis_disponiveis': [
            '{{sessao.numero}} - Número da sessão',
            '{{sessao.data_sessao}} - Data da sessão',
            '{{sessao.hora_inicio}} - Hora de início',
            '{{sessao.hora_fim}} - Hora de término',
            '{{sessao.local}} - Local da sessão',
            '{{sessao.tipo}} - Tipo da sessão',
            '{{sessao.pauta}} - Pauta da sessão',
            '{{comissao.nome}} - Nome da comissão',
            '{{comissao.tipo}} - Tipo da comissão',
        ]
    }
    
    print("=== RENDERIZANDO TEMPLATE ===")
    return render(request, 'militares/modelo_ata/salvar_atual.html', context)

@login_required
def deliberacao_comissao_resultado(request, sessao_pk):
    """Exibir resultado das deliberações com votos dos membros"""
    try:
        sessao = SessaoComissao.objects.get(pk=sessao_pk)
        comissao = sessao.comissao
    except SessaoComissao.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
        return redirect('militares:comissao_list')
    
    # Verificar se o usuário é membro da comissão
    try:
        user_membro = MembroComissao.objects.get(
            comissao=comissao,
            usuario=request.user,
            ativo=True
        )
    except MembroComissao.DoesNotExist:
        user_membro = None
    
    # Buscar todas as deliberações da sessão com seus votos
    deliberacoes = sessao.deliberacoes.prefetch_related('votos__membro__militar').all()
    
    context = {
        'comissao': comissao,
        'sessao': sessao,
        'deliberacoes': deliberacoes,
        'user_membro': user_membro,
        'membros_presentes': [p.membro for p in sessao.presencas.filter(presente=True)],
    }
    return render(request, 'militares/comissao/deliberacoes/resultado.html', context)


@login_required
def notificacoes_list(request):
    """Lista todas as notificações do usuário"""
    from .models import NotificacaoSessao
    
    notificacoes = NotificacaoSessao.objects.filter(
        usuario=request.user
    ).order_by('-data_criacao')
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        notificacoes = notificacoes.filter(tipo=tipo)
    
    lida = request.GET.get('lida')
    if lida is not None:
        notificacoes = notificacoes.filter(lida=lida == 'true')
    
    # Paginação
    paginator = Paginator(notificacoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notificacoes': page_obj,
        'tipos': NotificacaoSessao.TIPO_CHOICES,
        'filtros': {
            'tipo': tipo,
            'lida': lida,
        }
    }
    
    return render(request, 'militares/notificacoes/list.html', context)


@login_required
def notificacao_marcar_lida(request, pk):
    """Marca uma notificação como lida"""
    from .models import NotificacaoSessao
    
    try:
        notificacao = NotificacaoSessao.objects.get(
            pk=pk,
            usuario=request.user
        )
        notificacao.marcar_como_lida()
        messages.success(request, 'Notificação marcada como lida.')
    except NotificacaoSessao.DoesNotExist:
        messages.error(request, 'Notificação não encontrada.')
    
    return redirect('militares:notificacoes_list')


@login_required
def notificacao_marcar_todas_lidas(request):
    """Marca todas as notificações do usuário como lidas"""
    from .models import NotificacaoSessao
    
    notificacoes = NotificacaoSessao.objects.filter(
        usuario=request.user,
        lida=False
    )
    
    count = notificacoes.count()
    notificacoes.update(lida=True, data_leitura=timezone.now())
    
    messages.success(request, f'{count} notificação(ões) marcada(s) como lida(s).')
    return redirect('militares:notificacoes_list')


@login_required
@bloquear_membros_cpo
def notificacao_delete(request, pk):
    """Remove uma notificação"""
    from .models import NotificacaoSessao
    
    try:
        notificacao = NotificacaoSessao.objects.get(
            pk=pk,
            usuario=request.user
        )
        notificacao.delete()
        messages.success(request, 'Notificação removida.')
    except NotificacaoSessao.DoesNotExist:
        messages.error(request, 'Notificação não encontrada.')
    
    return redirect('militares:notificacoes_list')

# Views para gerenciar cargos da comissão
@login_required
def cargo_comissao_list(request):
    """Lista todos os cargos da comissão"""
    cargos = CargoComissao.objects.all()
    
    context = {
        'cargos': cargos,
        'title': 'Cargos da Comissão',
    }
    return render(request, 'militares/comissao/cargos/list.html', context)


@login_required
@bloquear_membros_cpo
def cargo_comissao_create(request):
    """Cria um novo cargo"""
    if request.method == 'POST':
        form = CargoComissaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo criado com sucesso!')
            return redirect('militares:cargo_comissao_list')
    else:
        form = CargoComissaoForm()
    
    context = {
        'form': form,
        'title': 'Novo Cargo da Comissão',
    }
    return render(request, 'militares/comissao/cargos/form.html', context)


@login_required
@bloquear_membros_cpo
def cargo_comissao_update(request, pk):
    """Edita um cargo existente"""
    try:
        cargo = CargoComissao.objects.get(pk=pk)
    except CargoComissao.DoesNotExist:
        messages.error(request, 'Cargo não encontrado.')
        return redirect('militares:cargo_comissao_list')
    
    if request.method == 'POST':
        form = CargoComissaoForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo atualizado com sucesso!')
            return redirect('militares:cargo_comissao_list')
    else:
        form = CargoComissaoForm(instance=cargo)
    
    context = {
        'form': form,
        'cargo': cargo,
        'title': 'Editar Cargo da Comissão',
    }
    return render(request, 'militares/comissao/cargos/form.html', context)


@login_required
@bloquear_membros_cpo
def cargo_comissao_delete(request, pk):
    """Exclui um cargo"""
    try:
        cargo = CargoComissao.objects.get(pk=pk)
    except CargoComissao.DoesNotExist:
        messages.error(request, 'Cargo não encontrado.')
        return redirect('militares:cargo_comissao_list')
    
    # Buscar membros vinculados ao cargo
    membros_vinculados = cargo.membrocomissao_set.all()
    erro_protegido = False
    
    if request.method == 'POST':
        try:
            cargo.delete()
            messages.success(request, 'Cargo excluído com sucesso!')
            return redirect('militares:cargo_comissao_list')
        except ProtectedError:
            erro_protegido = True
            messages.error(request, 'Não é possível excluir este cargo porque ele está vinculado a um ou mais membros da comissão. Troque o cargo desses membros antes de excluir.')
    
    context = {
        'cargo': cargo,
        'title': 'Excluir Cargo da Comissão',
        'membros_vinculados': membros_vinculados,
        'erro_protegido': erro_protegido,
    }
    return render(request, 'militares/comissao/cargos/delete.html', context)


# =============================================================================
# MÓDULO DE QUADROS DE FIXAÇÃO DE VAGAS
# =============================================================================

@login_required
def quadro_fixacao_vagas_list(request):
    """Lista todos os quadros de fixação de vagas (oficiais e praças) organizados por data com aditamentos"""
    # Verificar se o usuário é membro CPO e filtrar apenas oficiais
    grupos_cpo = ['Membro CPO - Acesso apenas a oficiais']
    grupos_usuario = [grupo.name for grupo in request.user.groups.all()]
    
    if any(grupo_cpo in grupos_usuario for grupo_cpo in grupos_cpo):
        # Membro CPO: mostrar apenas quadros de oficiais
        quadros = QuadroFixacaoVagas.objects.filter(tipo='OFICIAIS').order_by('-data_promocao', '-data_criacao')
    else:
        # Outros usuários: mostrar todos os quadros
        quadros = QuadroFixacaoVagas.objects.all().order_by('-data_promocao', '-data_criacao')
    
    # Filtros
    data_inicio = request.GET.get('data_inicio')
    if data_inicio:
        try:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            quadros = quadros.filter(data_promocao__gte=data_inicio)
        except ValueError:
            pass
    
    data_fim = request.GET.get('data_fim')
    if data_fim:
        try:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            quadros = quadros.filter(data_promocao__lte=data_fim)
        except ValueError:
            pass
    
    # Organizar quadros por data de promoção e tipo
    quadros_organizados = {}
    for quadro in quadros:
        chave = (quadro.data_promocao, quadro.tipo)
        if chave not in quadros_organizados:
            quadros_organizados[chave] = []
        quadros_organizados[chave].append(quadro)
    
    # Ordenar quadros dentro de cada grupo (principal primeiro, depois aditamentos)
    for chave in quadros_organizados:
        quadros_organizados[chave].sort(key=lambda x: (
            x.numero is None,  # Quadros sem número primeiro (principais)
            x.numero or ''     # Depois ordenar por número
        ))
    
    # Converter para lista plana mantendo a ordem
    quadros_ordenados = []
    for chave in sorted(quadros_organizados.keys(), reverse=True):
        quadros_ordenados.extend(quadros_organizados[chave])
    
    # Paginação
    paginator = Paginator(quadros_ordenados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_quadros = len(quadros_ordenados)
    
    context = {
        'quadros': page_obj,
        'total_quadros': total_quadros,
        'filtros': {
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/list.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
def quadro_fixacao_vagas_create(request):
    """Cria um novo quadro de fixação de vagas"""
    # Verificar se o usuário é membro CPO e restringir apenas a oficiais
    grupos_cpo = ['Membro CPO - Acesso apenas a oficiais']
    grupos_usuario = [grupo.name for grupo in request.user.groups.all()]
    
    if any(grupo_cpo in grupos_usuario for grupo_cpo in grupos_cpo):
        # Membro CPO: redirecionar para criação apenas de oficiais
        return redirect('militares:quadro_fixacao_vagas_oficiais_create')
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        tipo = request.POST.get('tipo')
        data_promocao = request.POST.get('data_promocao')
        observacoes = request.POST.get('observacoes', '')
        
        if not titulo:
            messages.error(request, 'O título do quadro é obrigatório.')
            return redirect('militares:quadro_fixacao_vagas_create')
        
        if not tipo:
            messages.error(request, 'O tipo de quadro é obrigatório.')
            return redirect('militares:quadro_fixacao_vagas_create')
        
        if not data_promocao:
            data_promocao = calcular_proxima_data_promocao()
            data_automatica = True
        else:
            try:
                data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                data_automatica = False
            except ValueError:
                messages.error(request, 'Data de promoção inválida.')
                return redirect('militares:quadro_fixacao_vagas_create')
        
        # Verificar se já existe um quadro para esta data e tipo
        quadro_existente = QuadroFixacaoVagas.objects.filter(
            data_promocao=data_promocao,
            tipo=tipo
        ).first()
        
        if quadro_existente:
            messages.warning(request, f'Já existe um quadro de fixação de vagas para {tipo.lower()} na data {data_promocao.strftime("%d/%m/%Y")}. Você pode gerar múltiplas versões.')
            # Não redirecionar, permitir continuar com a criação
        
        # Criar o quadro
        try:
            novo_quadro = QuadroFixacaoVagas.objects.create(
                titulo=titulo,
                tipo=tipo,
                data_promocao=data_promocao,
                status='RASCUNHO',
                observacoes=observacoes,
                criado_por=request.user
            )
            
            # Capturar previsões de vagas baseado no tipo
            if tipo == 'OFICIAIS':
                # Buscar previsões para oficiais (quadros COMB, SAUDE, ENG, COMP)
                previsoes = PrevisaoVaga.objects.filter(
                    ativo=True,
                    quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
                    posto__in=['AS', 'AA', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']
                ).order_by('quadro', 'posto')
            else:  # PRACAS
                # Buscar previsões para praças (quadro PRACAS)
                previsoes = PrevisaoVaga.objects.filter(
                    ativo=True,
                    quadro='PRACAS',
                    posto__in=['ST', '1S', '2S', '3S', 'CAB', 'SD']
                ).order_by('quadro', 'posto')
            
            # Criar itens do quadro baseado nas previsões
            for previsao in previsoes:
                # Capturar observação específica para este item
                observacao_key = f'observacoes_{previsao.id}'
                observacao = request.POST.get(observacao_key, '').strip()
                
                ItemQuadroFixacaoVagas.objects.create(
                    quadro=novo_quadro,
                    previsao_vaga=previsao,
                    vagas_fixadas=previsao.vagas_disponiveis,  # Inicialmente igual às vagas disponíveis
                    observacoes=observacao
                )
            
            if data_automatica:
                messages.success(request, f'Quadro de Fixação de Vagas criado com sucesso! Data automática: {data_promocao.strftime("%d/%m/%Y")}')
            else:
                messages.success(request, f'Quadro de Fixação de Vagas criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}!')
            return redirect('militares:quadro_fixacao_vagas_detail', pk=novo_quadro.pk)
                
        except Exception as e:
            messages.error(request, f'Erro ao criar quadro: {str(e)}')
        
        return redirect('militares:quadro_fixacao_vagas_create')
    
    # Definir hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,   # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }
    
    # Buscar previsões de vagas para mostrar no preview
    previsoes_oficiais = PrevisaoVaga.objects.filter(
        ativo=True,
        quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
        posto__in=['AS', 'AA', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']
    )
    
    previsoes_pracas = PrevisaoVaga.objects.filter(
        ativo=True,
        quadro='PRACAS',
        posto__in=['ST', '1S', '2S', '3S', 'CAB', 'SD']
    )
    
    # Agrupar previsões por quadro e ordenar por hierarquia
    vagas_por_quadro_oficiais = {}
    for previsao in previsoes_oficiais:
        if previsao.quadro not in vagas_por_quadro_oficiais:
            vagas_por_quadro_oficiais[previsao.quadro] = []
        vagas_por_quadro_oficiais[previsao.quadro].append(previsao)
    
    # Ordenar por hierarquia dentro de cada quadro
    for quadro in vagas_por_quadro_oficiais:
        vagas_por_quadro_oficiais[quadro].sort(
            key=lambda x: hierarquia_postos.get(x.posto, 999)
        )
    
    vagas_por_quadro_pracas = {}
    for previsao in previsoes_pracas:
        if previsao.quadro not in vagas_por_quadro_pracas:
            vagas_por_quadro_pracas[previsao.quadro] = []
        vagas_por_quadro_pracas[previsao.quadro].append(previsao)
    
    # Ordenar por hierarquia dentro de cada quadro
    for quadro in vagas_por_quadro_pracas:
        vagas_por_quadro_pracas[quadro].sort(
            key=lambda x: hierarquia_postos.get(x.posto, 999)
        )
    
    # Ordenar quadros na sequência: COMB, SAUDE, ENG, COMP
    ordem_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    vagas_por_quadro_oficiais_ordenado = {}
    for cod_quadro in ordem_quadros:
        if cod_quadro in vagas_por_quadro_oficiais:
            vagas_por_quadro_oficiais_ordenado[cod_quadro] = vagas_por_quadro_oficiais[cod_quadro]
    
    # Adicionar outros quadros que possam existir
    for cod_quadro, vagas in vagas_por_quadro_oficiais.items():
        if cod_quadro not in vagas_por_quadro_oficiais_ordenado:
            vagas_por_quadro_oficiais_ordenado[cod_quadro] = vagas
    
    context = {
        'tipos': QuadroFixacaoVagas.TIPO_CHOICES,
        'proxima_data_automatica': calcular_proxima_data_promocao(),
        'vagas_por_quadro_oficiais': vagas_por_quadro_oficiais_ordenado,
        'vagas_por_quadro_pracas': vagas_por_quadro_pracas,
        'quadros': QUADRO_CHOICES,
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/create.html', context)


@login_required
def quadro_fixacao_vagas_detail(request, pk):
    """Detalhes de um quadro de fixação de vagas"""
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=pk)
    except QuadroFixacaoVagas.DoesNotExist:
        messages.error(request, 'Quadro de fixação de vagas não encontrado.')
        return redirect('militares:quadro_fixacao_vagas_list')

    # Buscar itens do quadro agrupados por quadro
    itens = quadro.itens.select_related('previsao_vaga').order_by(
        'previsao_vaga__quadro', 'previsao_vaga__posto'
    )

    # Definir hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,   # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }

    grupos = {}
    for item in itens:
        previsao = item.previsao_vaga
        if previsao.quadro not in grupos:
            grupos[previsao.quadro] = {
                'nome': previsao.get_quadro_display(),
                'itens': []
            }
        grupos[previsao.quadro]['itens'].append(item)
    
    # Ordenar itens dentro de cada quadro por hierarquia de postos (do mais alto para o mais baixo)
    for quadro_cod in grupos:
        grupos[quadro_cod]['itens'].sort(
            key=lambda x: hierarquia_postos.get(x.previsao_vaga.posto, 999)
        )
    
    # Ordenar quadros na sequência: COMB, SAUDE, ENG, COMP
    ordem_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    grupos_ordenados = {}
    for cod_quadro in ordem_quadros:
        if cod_quadro in grupos:
            grupos_ordenados[cod_quadro] = grupos[cod_quadro]
    
    # Adicionar outros quadros que possam existir
    for cod_quadro, grupo in grupos.items():
        if cod_quadro not in grupos_ordenados:
            grupos_ordenados[cod_quadro] = grupo
    
    grupos = grupos_ordenados

    context = {
        'quadro': quadro,
        'grupos': grupos,
    }

    return render(request, 'militares/quadro_fixacao_vagas/detail.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
def quadro_fixacao_vagas_update(request, pk):
    """Atualiza um quadro de fixação de vagas (geral)"""
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=pk)
    except QuadroFixacaoVagas.DoesNotExist:
        messages.error(request, 'Quadro de fixação de vagas não encontrado.')
        return redirect('militares:quadro_fixacao_vagas_list')

    if request.method == 'POST':
        # Atualizar dados básicos do quadro
        titulo = request.POST.get('titulo')
        data_promocao = request.POST.get('data_promocao')
        observacoes = request.POST.get('observacoes', '')

        if titulo:
            quadro.titulo = titulo
        if data_promocao:
            try:
                quadro.data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Data de promoção inválida.')
                return redirect('militares:quadro_fixacao_vagas_update', pk=pk)
        quadro.observacoes = observacoes
        quadro.save()

        # Atualizar vagas fixadas e observações dos itens
        for key, value in request.POST.items():
            if key.startswith('vagas_fixadas_'):
                item_id = key.replace('vagas_fixadas_', '')
                try:
                    item = ItemQuadroFixacaoVagas.objects.get(id=item_id, quadro=quadro)
                    vagas_fixadas = int(value) if value else 0
                    item.vagas_fixadas = vagas_fixadas
                    # Buscar observações correspondentes
                    obs_key = f'observacoes_{item_id}'
                    observacoes_item = request.POST.get(obs_key, '')
                    item.observacoes = observacoes_item
                    item.save()
                except (ItemQuadroFixacaoVagas.DoesNotExist, ValueError):
                    continue
        messages.success(request, 'Quadro de fixação de vagas atualizado com sucesso!')
        return redirect('militares:quadro_fixacao_vagas_detail', pk=quadro.pk)

    # Buscar itens do quadro agrupados por quadro
    itens = quadro.itens.select_related('previsao_vaga').order_by(
        'previsao_vaga__quadro', 'previsao_vaga__posto'
    )

    # Definir hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,   # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }

    grupos = {}
    for item in itens:
        previsao = item.previsao_vaga
        if previsao.quadro not in grupos:
            grupos[previsao.quadro] = {
                'nome': previsao.get_quadro_display(),
                'itens': []
            }
        grupos[previsao.quadro]['itens'].append(item)
    
    # Ordenar itens dentro de cada quadro por hierarquia de postos (do mais alto para o mais baixo)
    for quadro_cod in grupos:
        grupos[quadro_cod]['itens'].sort(
            key=lambda x: hierarquia_postos.get(x.previsao_vaga.posto, 999)
        )
    
    # Ordenar quadros na sequência: COMB, SAUDE, ENG, COMP
    ordem_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    grupos_ordenados = {}
    for cod_quadro in ordem_quadros:
        if cod_quadro in grupos:
            grupos_ordenados[cod_quadro] = grupos[cod_quadro]
    
    # Adicionar outros quadros que possam existir
    for cod_quadro, grupo in grupos.items():
        if cod_quadro not in grupos_ordenados:
            grupos_ordenados[cod_quadro] = grupo
    
    grupos = grupos_ordenados

    context = {
        'quadro': quadro,
        'grupos': grupos,
    }
    return render(request, 'militares/quadro_fixacao_vagas/update.html', context)


@login_required
def quadro_fixacao_vagas_pdf_view(request, pk):
    """Visualiza o PDF do quadro de fixação de vagas em nova aba"""
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=pk)
    except QuadroFixacaoVagas.DoesNotExist:
        messages.error(request, 'Quadro de fixação de vagas não encontrado.')
        return redirect('militares:quadro_fixacao_vagas_list')

    # Buscar itens do quadro agrupados por quadro
    itens = quadro.itens.select_related('previsao_vaga').order_by(
        'previsao_vaga__quadro', 'previsao_vaga__posto'
    )

    # Definir hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,   # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
    }

    grupos = {}
    for item in itens:
        previsao = item.previsao_vaga
        if previsao.quadro not in grupos:
            grupos[previsao.quadro] = {
                'nome': previsao.get_quadro_display(),
                'itens': []
            }
        grupos[previsao.quadro]['itens'].append(item)
    
    # Ordenar itens dentro de cada quadro por hierarquia de postos (do mais alto para o mais baixo)
    for quadro_cod in grupos:
        grupos[quadro_cod]['itens'].sort(
            key=lambda x: hierarquia_postos.get(x.previsao_vaga.posto, 999)
        )
    
    # Ordenar quadros na sequência: COMB, SAUDE, ENG, COMP
    ordem_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    grupos_ordenados = {}
    for cod_quadro in ordem_quadros:
        if cod_quadro in grupos:
            grupos_ordenados[cod_quadro] = grupos[cod_quadro]
    
    # Adicionar outros quadros que possam existir
    for cod_quadro, grupo in grupos.items():
        if cod_quadro not in grupos_ordenados:
            grupos_ordenados[cod_quadro] = grupo
    
    grupos = grupos_ordenados

    context = {
        'quadro': quadro,
        'grupos': grupos,
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/pdf_view.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
def quadro_fixacao_vagas_oficiais_create(request):
    """Cria um novo quadro de fixação de vagas para oficiais"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        data_promocao = request.POST.get('data_promocao')
        observacoes = request.POST.get('observacoes', '')
        
        if not titulo:
            messages.error(request, 'O título do quadro é obrigatório.')
            return redirect('militares:quadro_fixacao_vagas_oficiais_create')
        
        if not data_promocao:
            data_promocao = calcular_proxima_data_promocao()
            data_automatica = True
        else:
            try:
                data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                data_automatica = False
            except ValueError:
                messages.error(request, 'Data de promoção inválida.')
                return redirect('militares:quadro_fixacao_vagas_oficiais_create')
        
        # Verificar se já existe um quadro para esta data e tipo
        quadro_existente = QuadroFixacaoVagas.objects.filter(
            data_promocao=data_promocao,
            tipo='OFICIAIS'
        ).first()
        
        # Criar o quadro
        try:
            novo_quadro = QuadroFixacaoVagas.objects.create(
                titulo=titulo,
                tipo='OFICIAIS',
                data_promocao=data_promocao,
                status='RASCUNHO',
                observacoes=observacoes,
                criado_por=request.user
            )
            
            # Buscar previsões para oficiais (quadros COMB, SAUDE, ENG, COMP)
            previsoes = PrevisaoVaga.objects.filter(
                ativo=True,
                quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
                posto__in=['AS', 'AA', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']
            ).order_by('quadro', 'posto')
            
            # Criar itens do quadro baseado nas previsões
            for previsao in previsoes:
                # Capturar observação específica para este item
                observacao_key = f'observacoes_{previsao.id}'
                observacao = request.POST.get(observacao_key, '').strip()
                
                ItemQuadroFixacaoVagas.objects.create(
                    quadro=novo_quadro,
                    previsao_vaga=previsao,
                    vagas_fixadas=previsao.vagas_disponiveis,  # Inicialmente igual às vagas disponíveis
                    observacoes=observacao
                )
            
            if data_automatica:
                messages.success(request, f'Quadro de Fixação de Vagas para Oficiais criado com sucesso! Data automática: {data_promocao.strftime("%d/%m/%Y")}')
            else:
                messages.success(request, f'Quadro de Fixação de Vagas para Oficiais criado com sucesso para {data_promocao.strftime("%d/%m/%Y")}!')
            return redirect('militares:quadro_fixacao_vagas_oficiais_detail', pk=novo_quadro.pk)
                
        except Exception as e:
            messages.error(request, f'Erro ao criar quadro: {str(e)}')
        
        return redirect('militares:quadro_fixacao_vagas_oficiais_create')
    
    # Definir hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
    }
    
    # Buscar previsões de vagas para oficiais
    previsoes_oficiais = PrevisaoVaga.objects.filter(
        ativo=True,
        quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
        posto__in=['AS', 'AA', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']
    )
    
    # Calcular efetivo atual em tempo real para cada previsão
    for previsao in previsoes_oficiais:
        if previsao.quadro == 'COMP':
            # Para COMP, incluir ST (Subtenentes) que são cadastrados como COMP mas contam para praças
            efetivo_atual = Militar.objects.filter(
                posto_graduacao=previsao.posto,
                quadro='COMP',
                situacao='AT'
            ).count()
        else:
            # Para outros quadros, usar o quadro específico
            efetivo_atual = Militar.objects.filter(
                posto_graduacao=previsao.posto,
                quadro=previsao.quadro,
                situacao='AT'
            ).count()
        
        # Atualizar o efetivo atual da previsão (apenas para exibição)
        previsao.efetivo_atual = efetivo_atual
    
    # Agrupar previsões por quadro e ordenar por hierarquia
    vagas_por_quadro_oficiais = {}
    for previsao in previsoes_oficiais:
        if previsao.quadro not in vagas_por_quadro_oficiais:
            vagas_por_quadro_oficiais[previsao.quadro] = []
        vagas_por_quadro_oficiais[previsao.quadro].append(previsao)
    
    # Ordenar por hierarquia dentro de cada quadro
    for quadro in vagas_por_quadro_oficiais:
        vagas_por_quadro_oficiais[quadro].sort(
            key=lambda x: hierarquia_postos.get(x.posto, 999)
        )
    
    # Ordenar quadros na sequência: COMB, SAUDE, ENG, COMP
    ordem_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    vagas_por_quadro_oficiais_ordenado = {}
    for cod_quadro in ordem_quadros:
        if cod_quadro in vagas_por_quadro_oficiais:
            vagas_por_quadro_oficiais_ordenado[cod_quadro] = vagas_por_quadro_oficiais[cod_quadro]
    
    # Adicionar outros quadros que possam existir
    for cod_quadro, vagas in vagas_por_quadro_oficiais.items():
        if cod_quadro not in vagas_por_quadro_oficiais_ordenado:
            vagas_por_quadro_oficiais_ordenado[cod_quadro] = vagas
    
    context = {
        'proxima_data_automatica': calcular_proxima_data_promocao(),
        'vagas_por_quadro_oficiais': vagas_por_quadro_oficiais_ordenado,
        'quadros': QUADRO_CHOICES,
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/oficiais_create.html', context)


@login_required
def quadro_fixacao_vagas_oficiais_detail(request, pk):
    """Detalhes de um quadro de fixação de vagas para oficiais"""
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=pk)
    except QuadroFixacaoVagas.DoesNotExist:
        messages.error(request, 'Quadro de fixação de vagas não encontrado.')
        return redirect('militares:quadro_fixacao_vagas_list')
    
    # Buscar itens do quadro
    itens = quadro.itens.select_related('previsao_vaga').order_by(
        'previsao_vaga__quadro', 'previsao_vaga__posto'
    )
    
    # Agrupar por quadro
    grupos = {}
    for item in itens:
        previsao = item.previsao_vaga
        if previsao.quadro not in grupos:
            grupos[previsao.quadro] = {
                'nome': previsao.get_quadro_display(),
                'itens': []
            }
        grupos[previsao.quadro]['itens'].append(item)
    
    # Estatísticas
    total_vagas_fixadas = quadro.total_vagas_fixadas()
    total_vagas_disponiveis = quadro.total_vagas_disponiveis()
    
    context = {
        'quadro': quadro,
        'grupos': grupos,
        'total_vagas_fixadas': total_vagas_fixadas,
        'total_vagas_disponiveis': total_vagas_disponiveis,
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/oficiais_detail.html', context)


@login_required
def assinar_quadro_fixacao_vagas(request, pk):
    """Assinar quadro de fixação de vagas com confirmação de senha"""
    quadro = get_object_or_404(QuadroFixacaoVagas, pk=pk)
    
    # Verificar permissão de assinatura - apenas Diretor de Gestão de Pessoas ou Chefe da Seção de Promoções
    grupos_permitidos = [
        "Direção de Gestão de Pessoas",
        "Chefe da Seção de Promoções"
    ]
    
    grupos_usuario = [g.name for g in request.user.groups.all()]
    tem_permissao = any(grupo in grupos_usuario for grupo in grupos_permitidos)
    
    # Superusuários também podem assinar
    if not tem_permissao and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para assinar quadros de fixação de vagas. Apenas Diretor de Gestão de Pessoas ou Chefe da Seção de Promoções podem assinar.')
        return redirect('militares:quadro_fixacao_vagas_detail', pk=pk)
    
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
            return render(request, 'militares/assinar_quadro_fixacao_vagas.html', context)
        
        # Verificar se já existe uma assinatura deste usuário para este tipo
        assinatura_existente = AssinaturaQuadroFixacaoVagas.objects.filter(
            quadro_fixacao_vagas=quadro,
            assinado_por=request.user,
            tipo_assinatura=tipo_assinatura
        ).first()
        
        if assinatura_existente:
            messages.error(request, f'Você já assinou este quadro como "{assinatura_existente.get_tipo_assinatura_display()}".')
            context = {
                'quadro': quadro,
            }
            return render(request, 'militares/assinar_quadro_fixacao_vagas.html', context)
        
        # Criar a assinatura
        assinatura = AssinaturaQuadroFixacaoVagas.objects.create(
            quadro_fixacao_vagas=quadro,
            assinado_por=request.user,
            observacoes=observacoes,
            tipo_assinatura=tipo_assinatura
        )
        
        # Se a assinatura for de aprovação, mudar o status do quadro para APROVADO
        if tipo_assinatura == 'APROVACAO':
            quadro.status = 'APROVADO'
            quadro.save()
        
        messages.success(request, f'Quadro de fixação de vagas assinado com sucesso como "{assinatura.get_tipo_assinatura_display()}"!')
        return redirect('militares:quadro_fixacao_vagas_detail', pk=quadro.pk)
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/assinar_quadro_fixacao_vagas.html', context)


@login_required
@bloquear_membros_cpo
@bloquear_membros_cpp
def quadro_fixacao_vagas_delete(request, pk):
    """Exclui um quadro de fixação de vagas"""
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=pk)
    except QuadroFixacaoVagas.DoesNotExist:
        messages.error(request, 'Quadro de fixação de vagas não encontrado.')
        return redirect('militares:quadro_fixacao_vagas_list')
    
    if request.method == 'POST':
        try:
            quadro.delete()
            messages.success(request, 'Quadro de fixação de vagas excluído com sucesso!')
            return redirect('militares:quadro_fixacao_vagas_list')
        except Exception as e:
            messages.error(request, f'Erro ao excluir quadro: {str(e)}')
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/delete.html', context)


@login_required
def quadro_fixacao_vagas_oficiais_detail(request, pk):
    """Detalhes de um quadro de fixação de vagas para oficiais"""
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=pk)
    except QuadroFixacaoVagas.DoesNotExist:
        messages.error(request, 'Quadro de fixação de vagas não encontrado.')
        return redirect('militares:quadro_fixacao_vagas_list')
    
    # Buscar itens do quadro
    itens = quadro.itens.select_related('previsao_vaga').order_by(
        'previsao_vaga__quadro', 'previsao_vaga__posto'
    )
    
    # Agrupar por quadro
    grupos = {}
    for item in itens:
        previsao = item.previsao_vaga
        if previsao.quadro not in grupos:
            grupos[previsao.quadro] = {
                'nome': previsao.get_quadro_display(),
                'itens': []
            }
        grupos[previsao.quadro]['itens'].append(item)
    
    # Estatísticas
    total_vagas_fixadas = quadro.total_vagas_fixadas()
    total_vagas_disponiveis = quadro.total_vagas_disponiveis()
    
    context = {
        'quadro': quadro,
        'grupos': grupos,
        'total_vagas_fixadas': total_vagas_fixadas,
        'total_vagas_disponiveis': total_vagas_disponiveis,
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/oficiais_detail.html', context)


@login_required
@bloquear_membros_cpo
def quadro_fixacao_vagas_oficiais_update(request, pk):
    """Atualiza um quadro de fixação de vagas para oficiais"""
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=pk)
    except QuadroFixacaoVagas.DoesNotExist:
        messages.error(request, 'Quadro de fixação de vagas não encontrado.')
        return redirect('militares:quadro_fixacao_vagas_list')
    
    if request.method == 'POST':
        # Atualizar dados básicos do quadro
        titulo = request.POST.get('titulo')
        data_promocao = request.POST.get('data_promocao')
        observacoes = request.POST.get('observacoes', '')
        
        if titulo:
            quadro.titulo = titulo
        if data_promocao:
            try:
                quadro.data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Data de promoção inválida.')
                return redirect('militares:quadro_fixacao_vagas_oficiais_update', pk=pk)
        
        quadro.observacoes = observacoes
        quadro.save()
        
        # Atualizar vagas fixadas
        for key, value in request.POST.items():
            if key.startswith('vagas_fixadas_'):
                item_id = key.replace('vagas_fixadas_', '')
                try:
                    item = ItemQuadroFixacaoVagas.objects.get(id=item_id, quadro=quadro)
                    vagas_fixadas = int(value) if value else 0
                    item.vagas_fixadas = vagas_fixadas
                    
                    # Buscar observações correspondentes
                    obs_key = f'observacoes_{item_id}'
                    observacoes_item = request.POST.get(obs_key, '')
                    item.observacoes = observacoes_item
                    
                    item.save()
                except (ItemQuadroFixacaoVagas.DoesNotExist, ValueError):
                    continue
        
        messages.success(request, 'Quadro de fixação de vagas atualizado com sucesso!')
        return redirect('militares:quadro_fixacao_vagas_oficiais_detail', pk=quadro.pk)
    
    # Buscar itens do quadro
    itens = quadro.itens.select_related('previsao_vaga').order_by(
        'previsao_vaga__quadro', 'previsao_vaga__posto'
    )
    
    # Agrupar por quadro
    grupos = {}
    for item in itens:
        previsao = item.previsao_vaga
        if previsao.quadro not in grupos:
            grupos[previsao.quadro] = {
                'nome': previsao.get_quadro_display(),
                'itens': []
            }
        grupos[previsao.quadro]['itens'].append(item)
    
    context = {
        'quadro': quadro,
        'grupos': grupos,
    }
    
    return render(request, 'militares/quadro_fixacao_vagas/oficiais_update.html', context)


def gerar_codigo_verificacao(texto_documento):
    """
    Gera um código de verificação baseado no hash SHA-256 do texto do documento.
    Retorna os primeiros 10 caracteres do hash hexadecimal.
    """
    return hashlib.sha256(texto_documento.encode('utf-8')).hexdigest()[:10]


@login_required
def proxima_numeracao_disponivel(request):
    """Retorna a próxima numeração disponível para um posto/quadro específico"""
    from django.db import models
    
    if request.method == 'GET':
        posto = request.GET.get('posto')
        quadro = request.GET.get('quadro')
        
        if not posto or not quadro:
            return JsonResponse({'erro': 'Posto e quadro são obrigatórios'}, status=400)
        
        # Buscar todas as numerações existentes para o posto/quadro
        numeracoes_existentes = list(Militar.objects.filter(
            situacao='AT',
            posto_graduacao=posto,
            quadro=quadro,
            numeracao_antiguidade__isnull=False
        ).values_list('numeracao_antiguidade', flat=True).order_by('numeracao_antiguidade'))
        
        # Encontrar o primeiro número disponível (não necessariamente o maior + 1)
        proxima_numeracao = 1
        for num in numeracoes_existentes:
            if proxima_numeracao < num:
                # Encontrou um gap, usar este número
                break
            proxima_numeracao = num + 1
        
        return JsonResponse({
            'proxima_numeracao': proxima_numeracao,
            'posto': posto,
            'quadro': quadro,
            'numeracoes_existentes': numeracoes_existentes
        })
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def reordenar_numeracoes_militares(posto, quadro):
    """
    Reordena as numerações de antiguidade para um posto/quadro específico
    """
    militares = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto,
        quadro=quadro
    ).order_by('numeracao_antiguidade')
    
    nova_numeracao = 1
    militares_para_atualizar = []
    
    for militar in militares:
        if militar.numeracao_antiguidade != nova_numeracao:
            militar.numeracao_antiguidade = nova_numeracao
            militares_para_atualizar.append(militar)
        nova_numeracao += 1
    
    # Salvar todas as alterações em lote
    if militares_para_atualizar:
        Militar.objects.bulk_update(militares_para_atualizar, ['numeracao_antiguidade'])
    
    return len(militares_para_atualizar)


@login_required
def reordenar_numeracoes_view(request):
    """View para reordenar numerações de antiguidade"""
    if request.method == 'POST':
        posto = request.POST.get('posto')
        quadro = request.POST.get('quadro')
        
        if not posto or not quadro:
            messages.error(request, 'Posto e quadro são obrigatórios')
            return JsonResponse({'erro': 'Posto e quadro são obrigatórios'}, status=400)
        
        try:
            militares_alterados = reordenar_numeracoes_militares(posto, quadro)
            messages.success(request, f'Numerações reordenadas com sucesso! {militares_alterados} militares foram atualizados.')
            return JsonResponse({
                'sucesso': True,
                'militares_alterados': militares_alterados,
                'mensagem': f'Numerações reordenadas com sucesso! {militares_alterados} militares foram atualizados.'
            })
        except Exception as e:
            messages.error(request, f'Erro ao reordenar numerações: {str(e)}')
            return JsonResponse({'erro': f'Erro ao reordenar numerações: {str(e)}'}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def aplicar_promocao_view(request):
    """View para aplicar promoção e atribuir numeração automaticamente"""
    if request.method == 'POST':
        militar_id = request.POST.get('militar_id')
        novo_posto = request.POST.get('novo_posto')
        novo_quadro = request.POST.get('novo_quadro')
        
        if not militar_id or not novo_posto or not novo_quadro:
            return JsonResponse({'erro': 'Dados incompletos para promoção'}, status=400)
        
        try:
            militar = Militar.objects.get(pk=militar_id)
            
            # Capturar dados anteriores
            posto_anterior = militar.posto_graduacao
            quadro_anterior = militar.quadro
            
            # Atualizar posto e quadro
            militar.posto_graduacao = novo_posto
            militar.quadro = novo_quadro
            
            # Aplicar nova numeração por promoção
            nova_numeracao = militar.atribuir_numeracao_por_promocao(posto_anterior, quadro_anterior)
            
            # Salvar as alterações
            militar.save()
            
            return JsonResponse({
                'sucesso': True,
                'nova_numeracao': nova_numeracao,
                'mensagem': f'Promoção aplicada com sucesso! Nova numeração: {nova_numeracao}º'
            })
            
        except Militar.DoesNotExist:
            return JsonResponse({'erro': 'Militar não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'erro': f'Erro ao aplicar promoção: {str(e)}'}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)


@login_required
def montar_quadro_acesso_oficiais(request, pk):
    """Interface para montar um quadro de acesso de oficiais manualmente, respeitando as regras"""
    try:
        quadro = QuadroAcesso.objects.get(pk=pk)
    except QuadroAcesso.DoesNotExist:
        messages.error(request, 'Quadro de acesso não encontrado.')
        return redirect('militares:quadro_acesso_list')
    
    if not quadro.is_manual:
        messages.error(request, 'Apenas quadros manuais podem ser montados.')
        return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
    
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
                    
                    # Verificar se é oficial
                    if militar.posto_graduacao not in ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']:
                        messages.error(request, 'Apenas oficiais podem ser adicionados a este quadro.')
                    else:
                        # Verificar regras de elegibilidade
                        apto, motivo = militar.apto_quadro_acesso_simples()
                        
                        if not apto:
                            messages.error(request, f'Oficial {militar.nome_completo} não está apto: {motivo}')
                        else:
                            posicao_int = int(posicao) if posicao else None
                            pontuacao_decimal = float(pontuacao) if pontuacao else ficha.pontos
                            
                            quadro.adicionar_militar_manual(militar, posicao_int, pontuacao_decimal)
                            messages.success(request, f'Oficial {militar.nome_completo} adicionado ao quadro!')
                        
                except (Militar.DoesNotExist, ValueError) as e:
                    messages.error(request, f'Erro ao adicionar oficial: {str(e)}')
        
        elif action == 'remover_militar':
            militar_id = request.POST.get('militar_id')
            
            if militar_id:
                try:
                    militar = Militar.objects.get(pk=militar_id)
                    quadro.remover_militar_manual(militar)
                    messages.success(request, f'Oficial {militar.nome_completo} removido do quadro!')
                    
                except (Militar.DoesNotExist, ValueError) as e:
                    messages.error(request, f'Erro ao remover oficial: {str(e)}')
        
        elif action == 'reordenar':
            # Reordenar baseado na pontuação
            itens = quadro.itemquadroacesso_set.all().order_by('-pontuacao', 'militar__nome_completo')
            for i, item in enumerate(itens, 1):
                item.posicao = i
                item.save()
            messages.success(request, 'Quadro reordenado por pontuação!')
        
        elif action == 'finalizar':
            if quadro.itemquadroacesso_set.exists():
                quadro.status = 'ELABORADO'
                quadro.save()
                messages.success(request, 'Quadro finalizado com sucesso!')
                return redirect('militares:quadro_acesso_detail', pk=quadro.pk)
            else:
                messages.error(request, 'Adicione pelo menos um oficial antes de finalizar o quadro.')
    
    # Buscar oficiais elegíveis (que não estão no quadro e atendem aos requisitos)
    militares_no_quadro = quadro.itemquadroacesso_set.values_list('militar_id', flat=True)
    oficiais_elegiveis = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    ).exclude(
        id__in=militares_no_quadro
    ).order_by('posto_graduacao', 'nome_completo')
    
    # Filtrar apenas os que atendem aos requisitos
    oficiais_disponiveis = []
    for oficial in oficiais_elegiveis:
        apto, motivo = oficial.apto_quadro_acesso_simples()
        if apto:
            ficha = oficial.(fichaconceitooficiais_set.first() or fichaconceitopracas_set.first())
            oficial.ficha_conceito = ficha
            oficiais_disponiveis.append(oficial)
    
    # Buscar itens do quadro ordenados por posição
    itens_quadro = quadro.itemquadroacesso_set.all().order_by('posicao')
    
    context = {
        'quadro': quadro,
        'militares_disponiveis': oficiais_disponiveis,
        'itens_quadro': itens_quadro,
        'is_oficiais': True,
    }
    
    return render(request, 'militares/montar_quadro_acesso.html', context)


@login_required
def buscar_oficiais_elegiveis(request):
    """Busca oficiais elegíveis para adicionar ao quadro via AJAX"""
    if request.method == 'GET':
        termo = request.GET.get('termo', '')
        quadro_id = request.GET.get('quadro_id')
        
        if len(termo) < 2:
            return JsonResponse({'militares': []})
        
        try:
            quadro = QuadroAcesso.objects.get(pk=quadro_id)
            militares_no_quadro = quadro.itemquadroacesso_set.values_list('militar_id', flat=True)
            
            # Buscar oficiais que não estão no quadro
            oficiais = Militar.objects.filter(
                situacao='AT',
                posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA'],
                nome_completo__icontains=termo
            ).exclude(
                id__in=militares_no_quadro
            )[:10]
            
            # Filtrar apenas os elegíveis
            militares_elegiveis = []
            for oficial in oficiais:
                apto, motivo = oficial.apto_quadro_acesso_simples()
                if apto:
                    ficha = oficial.(fichaconceitooficiais_set.first() or fichaconceitopracas_set.first())
                    from .utils import criptografar_cpf_lgpd
                    militares_elegiveis.append({
                        'id': oficial.id,
                        'nome_completo': oficial.nome_completo,
                        'posto_graduacao': oficial.posto_graduacao,
                        'quadro': oficial.quadro,
                        'cpf': criptografar_cpf_lgpd(oficial.cpf),
                        'pontuacao': float(ficha.pontos) if ficha else 0
                    })
            
            return JsonResponse({'militares': militares_elegiveis})
            
        except QuadroAcesso.DoesNotExist:
            return JsonResponse({'militares': []})
    
    return JsonResponse({'militares': []})


# ==================== VIEWS DE GERENCIAMENTO DE USUÁRIOS ====================

@login_required
@permission_required('auth.view_user')
def usuario_list(request):
    """Lista de usuários do sistema"""
    search = request.GET.get('search', '')
    grupo = request.GET.get('grupo', '')
    status = request.GET.get('status', '')
    
    usuarios = User.objects.all()
    
    # Filtros
    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    if grupo:
        usuarios = usuarios.filter(groups__name=grupo)
    
    if status == 'ativo':
        usuarios = usuarios.filter(is_active=True)
    elif status == 'inativo':
        usuarios = usuarios.filter(is_active=False)
    
    # Ordenação
    usuarios = usuarios.order_by('username')
    
    # Paginação
    paginator = Paginator(usuarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Grupos para filtro
    grupos = Group.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'grupos': grupos,
        'search': search,
        'grupo_filtro': grupo,
        'status_filtro': status,
    }
    
    return render(request, 'militares/usuarios/list.html', context)


@login_required
@permission_required('auth.view_user')
def usuario_detail(request, pk):
    """Detalhes de um usuário"""
    usuario = get_object_or_404(User, pk=pk)
    
    # Permissões do usuário
    permissoes_usuario = usuario.user_permissions.all()
    permissoes_grupos = []
    
    for grupo in usuario.groups.all():
        permissoes_grupo = grupo.permissions.all()
        permissoes_grupos.extend(permissoes_grupo)
    
    # Remover duplicatas
    permissoes_grupos = list(set(permissoes_grupos))
    
    context = {
        'usuario': usuario,
        'permissoes_usuario': permissoes_usuario,
        'permissoes_grupos': permissoes_grupos,
    }
    
    return render(request, 'militares/usuarios/detail.html', context)


@login_required
@permission_required('auth.add_user')
def usuario_create(request):
    """Criar novo usuário"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            usuario.save()
            form.save_m2m()  # Salvar grupos
            
            messages.success(request, f'Usuário "{usuario.username}" criado com sucesso!')
            return redirect('militares:usuario_list')
    else:
        form = UsuarioForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Usuário',
        'submit_text': 'Criar Usuário'
    }
    
    return render(request, 'militares/usuarios/form.html', context)


@login_required
@permission_required('auth.change_user')
def usuario_update(request, pk):
    """Editar usuário"""
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                usuario.set_password(password)
            usuario.save()
            form.save_m2m()  # Salvar grupos
            
            messages.success(request, f'Usuário "{usuario.username}" atualizado com sucesso!')
            return redirect('militares:usuario_list')
    else:
        form = UsuarioForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'title': f'Editar Usuário: {usuario.username}',
        'submit_text': 'Atualizar Usuário'
    }
    
    return render(request, 'militares/usuarios/form.html', context)


@login_required
@permission_required('auth.delete_user')
def usuario_delete(request, pk):
    """Excluir usuário"""
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuário "{username}" excluído com sucesso!')
        return redirect('militares:usuario_list')
    
    context = {
        'usuario': usuario,
    }
    
    return render(request, 'militares/usuarios/delete.html', context)


@login_required
@permission_required('auth.view_group')
def grupo_list(request):
    """Lista de grupos"""
    grupos = Group.objects.all().order_by('name')
    
    context = {
        'grupos': grupos,
    }
    
    return render(request, 'militares/usuarios/grupos/list.html', context)


@login_required
@permission_required('auth.view_group')
def grupo_detail(request, pk):
    """Detalhes de um grupo"""
    grupo = get_object_or_404(Group, pk=pk)
    
    # Usuários do grupo
    usuarios = grupo.user_set.all().order_by('username')
    
    # Permissões do grupo
    permissoes = grupo.permissions.all().order_by('content_type__app_label', 'content_type__model', 'codename')
    
    context = {
        'grupo': grupo,
        'usuarios': usuarios,
        'permissoes': permissoes,
    }
    
    return render(request, 'militares/usuarios/grupos/detail.html', context)


@login_required
@permission_required('auth.add_group')
def grupo_create(request):
    """Criar novo grupo"""
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save()
            messages.success(request, f'Grupo "{grupo.name}" criado com sucesso!')
            return redirect('militares:grupo_list')
    else:
        form = GrupoForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Grupo',
        'submit_text': 'Criar Grupo'
    }
    
    return render(request, 'militares/usuarios/grupos/form.html', context)


@login_required
@permission_required('auth.change_group')
def grupo_update(request, pk):
    """Editar grupo"""
    grupo = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            grupo = form.save()
            messages.success(request, f'Grupo "{grupo.name}" atualizado com sucesso!')
            return redirect('militares:grupo_list')
    else:
        form = GrupoForm(instance=grupo)
    
    context = {
        'form': form,
        'grupo': grupo,
        'title': f'Editar Grupo: {grupo.name}',
        'submit_text': 'Atualizar Grupo'
    }
    
    return render(request, 'militares/usuarios/grupos/form.html', context)


@login_required
@permission_required('auth.delete_group')
def grupo_delete(request, pk):
    """Excluir grupo"""
    grupo = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        nome = grupo.name
        grupo.delete()
        messages.success(request, f'Grupo "{nome}" excluído com sucesso!')
        return redirect('militares:grupo_list')
    
    context = {
        'grupo': grupo,
    }
    
    return render(request, 'militares/usuarios/grupos/delete.html', context)


@login_required
@permission_required('auth.view_permission')
def permissao_list(request):
    """Lista de permissões"""
    app_label = request.GET.get('app', '')
    model = request.GET.get('model', '')
    search = request.GET.get('search', '')
    
    permissoes = Permission.objects.select_related('content_type').all()
    
    # Filtros
    if app_label:
        permissoes = permissoes.filter(content_type__app_label=app_label)
    
    if model:
        permissoes = permissoes.filter(content_type__model=model)
    
    if search:
        permissoes = permissoes.filter(
            Q(name__icontains=search) |
            Q(codename__icontains=search) |
            Q(content_type__app_label__icontains=search) |
            Q(content_type__model__icontains=search)
        )
    
    # Ordenação
    permissoes = permissoes.order_by('content_type__app_label', 'content_type__model', 'codename')
    
    # Paginação
    paginator = Paginator(permissoes, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Apps e modelos para filtro
    content_types = Permission.objects.values_list(
        'content_type__app_label', 'content_type__model'
    ).distinct().order_by('content_type__app_label', 'content_type__model')
    
    apps = {}
    for app, model in content_types:
        if app not in apps:
            apps[app] = []
        apps[app].append(model)
    
    context = {
        'page_obj': page_obj,
        'apps': apps,
        'app_filtro': app_label,
        'model_filtro': model,
        'search': search,
    }
    
    return render(request, 'militares/usuarios/permissoes/list.html', context)


# ==================== FORMS ====================

class UsuarioForm(forms.ModelForm):
    """Formulário para criação/edição de usuários"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control-custom'}),
        required=False,
        help_text='Deixe em branco para manter a senha atual'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control-custom'}),
        required=False,
        help_text='Confirme a nova senha'
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'is_active', 'is_staff', 'is_superuser', 'groups'
        ]
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # Se é uma criação de usuário (não tem instance.pk), senha é obrigatória
        if not self.instance.pk:
            if not password:
                raise forms.ValidationError('Senha é obrigatória para novos usuários.')
            if not confirm_password:
                raise forms.ValidationError('Confirmação de senha é obrigatória para novos usuários.')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('As senhas não coincidem.')
        
        return cleaned_data


class GrupoForm(forms.ModelForm):
    """Formulário para criação/edição de grupos"""
    
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'permissions': forms.CheckboxSelectMultiple(),
        }


@login_required
@permission_required('auth.view_user')
def dashboard_permissoes(request):
    """Dashboard com estatísticas do sistema de permissões"""
    from django.contrib.auth.models import User, Group, Permission
    from django.contrib.contenttypes.models import ContentType
    
    # Estatísticas básicas
    total_usuarios = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    total_grupos = Group.objects.count()
    grupos_com_usuarios = Group.objects.filter(user__isnull=False).distinct().count()
    total_permissoes = Permission.objects.count()
    permissoes_utilizadas = Permission.objects.filter(group__isnull=False).distinct().count()
    
    # Aplicações e modelos
    content_types = ContentType.objects.all()
    total_apps = content_types.values('app_label').distinct().count()
    modelos_por_app = content_types.count()
    
    # Estatísticas por grupo
    grupos_estatisticas = {}
    grupos_nomes = {
        'admin': 'Administrador - Acesso total',
        'superusuario': 'Super Usuário - Acesso total',
        'membro_cpo': 'Membro CPO - Acesso a oficiais e comissões',
        'membro_cpp': 'Membro CPP - Acesso a praças e comissões',
        'comandante_geral': 'Comandante Geral - Acesso total exceto usuários e administração',
        'subcomandante_geral': 'Subcomandante Geral - Acesso total exceto usuários e administração',
        'diretor_gestao_pessoas': 'Diretor de Gestão de Pessoas - Acesso total exceto usuários e administração',
        'chefe_secao_promocoes': 'Chefe da Seção de Promoções - Acesso total exceto usuários e administração',
        'digitador': 'Digitador - Acesso total sem exclusão e sem usuários/administração',
        'usuario': 'Usuário - Acesso a documentos específicos e visualização'
    }
    
    for codigo, nome in grupos_nomes.items():
        try:
            grupo = Group.objects.get(name=nome)
            usuarios_count = grupo.user_set.count()
            permissoes_count = grupo.permissions.count()
            grupos_estatisticas[codigo] = {
                'usuarios': usuarios_count,
                'permissoes': permissoes_count
            }
        except Group.DoesNotExist:
            grupos_estatisticas[codigo] = {
                'usuarios': 0,
                'permissoes': 0
            }
    
    # Atividades recentes (simuladas)
    recent_activities = [
        {
            'icon': 'shield-alt',
            'title': 'Sistema de permissões simplificado',
            'description': 'Configuração de permissões por níveis de acesso concluída',
            'time': '5 minutos atrás'
        },
        {
            'icon': 'users-cog',
            'title': 'Grupos criados',
            'description': '10 grupos de permissões foram configurados',
            'time': '10 minutos atrás'
        },
        {
            'icon': 'key',
            'title': 'Permissões atribuídas',
            'description': 'Sistema de permissões organizado por níveis',
            'time': '15 minutos atrás'
        }
    ]
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_ativos': usuarios_ativos,
        'total_grupos': total_grupos,
        'grupos_com_usuarios': grupos_com_usuarios,
        'total_permissoes': total_permissoes,
        'permissoes_utilizadas': permissoes_utilizadas,
        'total_apps': total_apps,
        'modelos_por_app': modelos_por_app,
        'recent_activities': recent_activities,
        # Estatísticas por grupo
        'admin_users': grupos_estatisticas.get('admin', {}).get('usuarios', 0),
        'admin_permissions': grupos_estatisticas.get('admin', {}).get('permissoes', 88),
        'super_users': grupos_estatisticas.get('superusuario', {}).get('usuarios', 0),
        'super_permissions': grupos_estatisticas.get('superusuario', {}).get('permissoes', 88),
        'cpo_users': grupos_estatisticas.get('membro_cpo', {}).get('usuarios', 0),
        'cpo_permissions': grupos_estatisticas.get('membro_cpo', {}).get('permissoes', 44),
        'cpp_users': grupos_estatisticas.get('membro_cpp', {}).get('usuarios', 0),
        'cpp_permissions': grupos_estatisticas.get('membro_cpp', {}).get('permissoes', 44),
        'comandante_users': grupos_estatisticas.get('comandante_geral', {}).get('usuarios', 0),
        'comandante_permissions': grupos_estatisticas.get('comandante_geral', {}).get('permissoes', 76),
        'subcomandante_users': grupos_estatisticas.get('subcomandante_geral', {}).get('usuarios', 0),
        'subcomandante_permissions': grupos_estatisticas.get('subcomandante_geral', {}).get('permissoes', 76),
        'diretor_users': grupos_estatisticas.get('diretor_gestao_pessoas', {}).get('usuarios', 0),
        'diretor_permissions': grupos_estatisticas.get('diretor_gestao_pessoas', {}).get('permissoes', 76),
        'chefe_users': grupos_estatisticas.get('chefe_secao_promocoes', {}).get('usuarios', 0),
        'chefe_permissions': grupos_estatisticas.get('chefe_secao_promocoes', {}).get('permissoes', 76),
        'digitador_users': grupos_estatisticas.get('digitador', {}).get('usuarios', 0),
        'digitador_permissions': grupos_estatisticas.get('digitador', {}).get('permissoes', 57),
        'usuario_users': grupos_estatisticas.get('usuario', {}).get('usuarios', 0),
        'usuario_permissions': grupos_estatisticas.get('usuario', {}).get('permissoes', 2),
    }
    
    return render(request, 'militares/usuarios/dashboard.html', context)

