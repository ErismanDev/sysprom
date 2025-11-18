"""
Views para o módulo de Processos e Procedimentos Administrativos
Gerencia o cadastro e controle de processos administrativos
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from .models import ProcessoAdministrativo, Orgao, GrandeComando, Unidade, SubUnidade
from .forms import ProcessoAdministrativoForm
from .permissoes_sistema import tem_permissao
from .permissoes_simples import obter_funcao_militar_ativa
from .filtros_hierarquicos import aplicar_filtro_hierarquico_processos


# ============================================================================
# VIEWS PARA PROCESSOS ADMINISTRATIVOS
# ============================================================================

class ProcessoAdministrativoListView(LoginRequiredMixin, ListView):
    model = ProcessoAdministrativo
    template_name = 'militares/processo_administrativo_list.html'
    context_object_name = 'processos'
    paginate_by = 20

    def get_queryset(self):
        queryset = ProcessoAdministrativo.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'criado_por'
        ).prefetch_related(
            'militares_envolvidos', 'militares_encarregados', 'escrivaos'
        ).order_by('-data_abertura', '-data_criacao')

        # Aplicar filtro hierárquico baseado na função militar
        funcao_usuario = obter_funcao_militar_ativa(self.request.user)
        queryset = aplicar_filtro_hierarquico_processos(queryset, funcao_usuario, self.request.user)

        search = self.request.GET.get('search', '')
        tipo = self.request.GET.get('tipo', '')
        status = self.request.GET.get('status', '')
        prioridade = self.request.GET.get('prioridade', '')

        if search:
            queryset = queryset.filter(
                Q(numero__icontains=search) |
                Q(assunto__icontains=search) |
                Q(descricao__icontains=search)
            )

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        if status:
            queryset = queryset.filter(status=status)

        if prioridade:
            queryset = queryset.filter(prioridade=prioridade)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['tipo'] = self.request.GET.get('tipo', '')
        context['status'] = self.request.GET.get('status', '')
        context['prioridade'] = self.request.GET.get('prioridade', '')

        context['tipos'] = ProcessoAdministrativo.TIPO_PROCESSO_CHOICES
        context['status_choices'] = ProcessoAdministrativo.STATUS_CHOICES
        context['prioridades'] = ProcessoAdministrativo.PRIORIDADE_CHOICES

        # Estatísticas - aplicar filtro hierárquico também nas estatísticas
        funcao_usuario = obter_funcao_militar_ativa(self.request.user)
        queryset_estatisticas = ProcessoAdministrativo.objects.all()
        queryset_estatisticas = aplicar_filtro_hierarquico_processos(queryset_estatisticas, funcao_usuario, self.request.user)
        
        context['total_processos'] = queryset_estatisticas.count()
        context['processos_em_andamento'] = queryset_estatisticas.filter(
            status='EM_ANDAMENTO'
        ).count()
        context['processos_vencidos'] = queryset_estatisticas.filter(
            ativo=True
        ).exclude(
            status__in=['DECIDIDO', 'ARQUIVADO', 'CANCELADO']
        ).count()

        return context


@login_required
def processo_administrativo_create(request):
    """Cria um novo processo administrativo"""
    if not tem_permissao(request.user, 'PROCESSOS', 'CRIAR'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Você não tem permissão para criar processos.'
            }, status=403)
        messages.error(request, "Você não tem permissão para criar processos.")
        return redirect('militares:processo_administrativo_list')

    if request.method == 'POST':
        form = ProcessoAdministrativoForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                processo = form.save(commit=False)
                processo.criado_por = request.user
                processo.save()
                form.save_m2m()  # Salvar relacionamentos ManyToMany
                
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Processo criado com sucesso!'
                })
            messages.success(request, 'Processo criado com sucesso!')
            return redirect('militares:processo_administrativo_detail', pk=processo.pk)
    else:
        form = ProcessoAdministrativoForm(request=request)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/processo_administrativo_form_modal.html', {
            'form': form,
            'is_create': True
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})

    return render(request, 'militares/processo_administrativo_form.html', {
        'form': form,
        'is_create': True
    })


@login_required
def processo_administrativo_update(request, pk):
    """Atualiza um processo administrativo"""
    if not tem_permissao(request.user, 'PROCESSOS', 'EDITAR'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Você não tem permissão para editar processos.'
            }, status=403)
        messages.error(request, "Você não tem permissão para editar processos.")
        return redirect('militares:processo_administrativo_list')

    processo = get_object_or_404(ProcessoAdministrativo, pk=pk)

    if request.method == 'POST':
        form = ProcessoAdministrativoForm(request.POST, instance=processo, request=request)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Processo atualizado com sucesso!'
                })
            messages.success(request, 'Processo atualizado com sucesso!')
            return redirect('militares:processo_administrativo_detail', pk=processo.pk)
    else:
        form = ProcessoAdministrativoForm(instance=processo, request=request)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/processo_administrativo_form_modal.html', {
            'form': form,
            'processo': processo,
            'is_create': False
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})

    return render(request, 'militares/processo_administrativo_form.html', {
        'form': form,
        'processo': processo,
        'is_create': False
    })


@login_required
def processo_administrativo_delete(request, pk):
    """Deleta um processo administrativo"""
    if not tem_permissao(request.user, 'PROCESSOS', 'EXCLUIR'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Você não tem permissão para excluir processos.'
            }, status=403)
        messages.error(request, "Você não tem permissão para excluir processos.")
        return redirect('militares:processo_administrativo_list')

    processo = get_object_or_404(ProcessoAdministrativo, pk=pk)

    if request.method == 'POST':
        processo.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Processo deletado com sucesso!'
            })
        messages.success(request, 'Processo deletado com sucesso!')
        return redirect('militares:processo_administrativo_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/processo_administrativo_delete_modal.html', {
            'processo': processo
        }, request=request)
        return JsonResponse({'status': 'success', 'html': html})
    
    return render(request, 'militares/processo_administrativo_delete.html', {'processo': processo})


@login_required
def processo_administrativo_detail(request, pk):
    """Detalhes de um processo administrativo"""
    if not tem_permissao(request.user, 'PROCESSOS', 'VISUALIZAR'):
        messages.error(request, "Você não tem permissão para visualizar processos.")
        return redirect('militares:processo_administrativo_list')

    processo = get_object_or_404(
        ProcessoAdministrativo.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'criado_por'
        ).prefetch_related(
            'militares_envolvidos', 'militares_encarregados', 'escrivaos'
        ),
        pk=pk
    )
    
    # Verificar se usuário pode fazer CRUD/PDF
    # Para processos, verificar se o usuário é um dos militares envolvidos
    from militares.permissoes_militares import pode_fazer_crud_pdf, tem_funcao_restrita
    
    pode_crud_pdf = True
    tem_funcao_restrita_user = tem_funcao_restrita(request.user)
    
    if tem_funcao_restrita_user:
        # Verificar se o usuário é um dos militares envolvidos no processo
        is_militar_envolvido = False
        if hasattr(request.user, 'militar') and request.user.militar:
            is_militar_envolvido = processo.militares_envolvidos.filter(pk=request.user.militar.pk).exists()
        
        # Se não é militar envolvido, não pode fazer CRUD/PDF
        if not is_militar_envolvido:
            pode_crud_pdf = False
    
    context = {
        'processo': processo,
        'pode_crud_pdf': pode_crud_pdf,
    }
    
    return render(request, 'militares/processo_administrativo_detail.html', context)


@login_required
def processo_administrativo_proximo_numero(request):
    """Retorna o próximo número disponível para um tipo de processo"""
    from django.http import JsonResponse
    from datetime import datetime
    
    tipo = request.GET.get('tipo', '').strip()
    
    if not tipo:
        return JsonResponse({
            'status': 'error',
            'message': 'Tipo de processo não informado'
        }, status=400)
    
    # Mapeamento de tipos para siglas
    tipo_siglas = {
        'SINDICANCIA': 'SIN',
        'INQUERITO_POLICIAL': 'IP',
        'INQUERITO_POLICIAL_MILITAR': 'IPM',
        'INQUERITO_TECNICO': 'IT',
        'PROCESSO_ADMINISTRATIVO_DISCIPLINAR_SUMARIO': 'PADS',
        'PROCESSO_ADMINISTRATIVO_DISCIPLINAR_ORDINARIO': 'PADO',
        'PROCESSO_CRIMINAL': 'PC',
        'PROCESSO_ADMINISTRATIVO': 'PA',
        'PROCEDIMENTO_ADMINISTRATIVO': 'PRAD',
        'REPRESENTACAO': 'REP',
        'OUTROS': 'OUT',
    }
    
    sigla = tipo_siglas.get(tipo, 'PROC')
    ano_atual = datetime.now().year
    
    # Buscar o último número do tipo no ano atual
    prefixo = f"{sigla}-{ano_atual}-"
    
    # Buscar todos os números que começam com o prefixo
    processos = ProcessoAdministrativo.objects.filter(
        numero__startswith=prefixo
    ).values_list('numero', flat=True)
    
    # Extrair os números sequenciais
    numeros = []
    for num in processos:
        try:
            # Formato esperado: SIGLA-ANO-NUMERO (ex: PA-2025-001)
            partes = num.split('-')
            if len(partes) == 3:
                numero_seq = int(partes[2])
                numeros.append(numero_seq)
        except (ValueError, IndexError):
            continue
    
    # Próximo número sequencial
    if numeros:
        proximo_numero = max(numeros) + 1
    else:
        proximo_numero = 1
    
    # Formatar com zeros à esquerda (3 dígitos)
    numero_formatado = f"{prefixo}{proximo_numero:03d}"
    
    return JsonResponse({
        'status': 'success',
        'numero': numero_formatado
    })


@login_required
def processo_administrativo_pdf(request, pk):
    """Gera PDF do processo administrativo individual"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import HttpResponse
    from django.conf import settings
    from datetime import datetime
    
    processo = get_object_or_404(
        ProcessoAdministrativo.objects.select_related(
            'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'criado_por'
        ).prefetch_related(
            'militares_envolvidos', 'militares_encarregados', 'escrivaos'
        ),
        pk=pk
    )
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20, fontName='Helvetica-Bold')
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=0, fontSize=14, spaceAfter=10, fontName='Helvetica-Bold')
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11, alignment=4)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo_cbmepi.png')
        if not os.path.exists(logo_path) and settings.STATICFILES_DIRS:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            elements.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            elements.append(Spacer(1, 0.3*cm))
        
        # Cabeçalho institucional
        elements.append(Paragraph("GOVERNO DO ESTADO DO PIAUÍ", ParagraphStyle('estado', parent=styles['Normal'], alignment=1, fontSize=12, fontName='Helvetica-Bold', spaceAfter=0)))
        elements.append(Paragraph("CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ", ParagraphStyle('cbm', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=0)))
        elements.append(Paragraph("COMANDO GERAL", ParagraphStyle('comando', parent=styles['Normal'], alignment=1, fontSize=10, spaceAfter=10)))
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.HexColor('#000000'), spaceAfter=15))
        
        # Título do documento
        elements.append(Paragraph("PROCESSO ADMINISTRATIVO", style_title))
        elements.append(Spacer(1, 0.5*cm))
        
        # Dados do processo
        dados_processo = []
        
        # Número e Tipo
        dados_processo.append([
            Paragraph("<b>Número:</b>", style_bold),
            Paragraph(processo.numero, style_normal)
        ])
        dados_processo.append([
            Paragraph("<b>Tipo:</b>", style_bold),
            Paragraph(processo.get_tipo_display(), style_normal)
        ])
        
        # Assunto
        dados_processo.append([
            Paragraph("<b>Assunto:</b>", style_bold),
            Paragraph(processo.assunto, style_normal)
        ])
        
        # Status e Prioridade
        dados_processo.append([
            Paragraph("<b>Status:</b>", style_bold),
            Paragraph(processo.get_status_display(), style_normal)
        ])
        dados_processo.append([
            Paragraph("<b>Prioridade:</b>", style_bold),
            Paragraph(processo.get_prioridade_display(), style_normal)
        ])
        
        # Datas
        dados_processo.append([
            Paragraph("<b>Data de Abertura:</b>", style_bold),
            Paragraph(processo.data_abertura.strftime('%d/%m/%Y'), style_normal)
        ])
        
        if processo.data_prazo:
            dados_processo.append([
                Paragraph("<b>Data de Prazo:</b>", style_bold),
                Paragraph(processo.data_prazo.strftime('%d/%m/%Y'), style_normal)
            ])
        
        if processo.data_conclusao:
            dados_processo.append([
                Paragraph("<b>Data de Conclusão:</b>", style_bold),
                Paragraph(processo.data_conclusao.strftime('%d/%m/%Y'), style_normal)
            ])
        
        if processo.data_arquivamento:
            dados_processo.append([
                Paragraph("<b>Data de Arquivamento:</b>", style_bold),
                Paragraph(processo.data_arquivamento.strftime('%d/%m/%Y'), style_normal)
            ])
        
        # Organograma
        if processo.orgao or processo.grande_comando or processo.unidade or processo.sub_unidade:
            org_text = []
            if processo.orgao:
                org_text.append(str(processo.orgao))
            if processo.grande_comando:
                org_text.append(str(processo.grande_comando))
            if processo.unidade:
                org_text.append(str(processo.unidade))
            if processo.sub_unidade:
                org_text.append(str(processo.sub_unidade))
            
            dados_processo.append([
                Paragraph("<b>Organização Militar:</b>", style_bold),
                Paragraph(" / ".join(org_text), style_normal)
            ])
        
        # Processos relacionados
        if processo.processo_origem:
            dados_processo.append([
                Paragraph("<b>Processo de Origem:</b>", style_bold),
                Paragraph(processo.processo_origem, style_normal)
            ])
        
        if processo.processo_procedimento:
            dados_processo.append([
                Paragraph("<b>Processo que Realizou o Procedimento:</b>", style_bold),
                Paragraph(processo.processo_procedimento, style_normal)
            ])
        
        # Tabela de dados
        tabela_dados = Table(dados_processo, colWidths=[5*cm, 12*cm])
        tabela_dados.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(tabela_dados)
        elements.append(Spacer(1, 0.5*cm))
        
        # Descrição
        if processo.descricao:
            elements.append(Paragraph("<b>Descrição:</b>", style_subtitle))
            elements.append(Paragraph(processo.descricao.replace('\n', '<br/>'), style_normal))
            elements.append(Spacer(1, 0.5*cm))
        
        # Militares Envolvidos
        if processo.militares_envolvidos.exists():
            elements.append(Paragraph("<b>Militares Envolvidos:</b>", style_subtitle))
            militares_text = []
            for militar in processo.militares_envolvidos.all():
                militares_text.append(f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}")
            elements.append(Paragraph("<br/>".join(militares_text), style_normal))
            elements.append(Spacer(1, 0.5*cm))
        
        # Militares Encarregados
        if processo.militares_encarregados.exists():
            elements.append(Paragraph("<b>Militares Encarregados:</b>", style_subtitle))
            militares_text = []
            for militar in processo.militares_encarregados.all():
                militares_text.append(f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}")
            elements.append(Paragraph("<br/>".join(militares_text), style_normal))
            elements.append(Spacer(1, 0.5*cm))
        
        # Escribões
        if processo.escrivaos.exists():
            elements.append(Paragraph("<b>Escribões:</b>", style_subtitle))
            militares_text = []
            for militar in processo.escrivaos.all():
                militares_text.append(f"{militar.get_posto_graduacao_display()} {militar.nome_completo} - {militar.matricula}")
            elements.append(Paragraph("<br/>".join(militares_text), style_normal))
            elements.append(Spacer(1, 0.5*cm))
        
        # Observações
        if processo.observacoes:
            elements.append(Paragraph("<b>Observações:</b>", style_subtitle))
            elements.append(Paragraph(processo.observacoes.replace('\n', '<br/>'), style_normal))
            elements.append(Spacer(1, 0.5*cm))
        
        # Rodapé
        elements.append(Spacer(1, 1*cm))
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.HexColor('#000000'), spaceAfter=10))
        data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        elements.append(Paragraph(f"Documento gerado em {data_geracao}", ParagraphStyle('rodape', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.grey)))
        
        # Gerar PDF
        doc.build(elements)
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        filename = f'processo_{processo.numero.replace("/", "_").replace("-", "_")}.pdf'
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
        
    except Exception as e:
        error_html = f"""
        <html>
        <head><title>Erro ao Gerar PDF</title></head>
        <body>
            <h1>Erro ao Gerar PDF</h1>
            <p>Ocorreu um erro ao gerar o PDF do processo administrativo.</p>
            <p><strong>Erro:</strong> {str(e)}</p>
            <p><a href="javascript:history.back()">Voltar</a></p>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')