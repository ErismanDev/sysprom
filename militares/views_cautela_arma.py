"""
Views para o módulo de Cautela de Armas
Gerencia o registro de cautelas (entregas temporárias) de armas institucionais
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone

from .models import Arma, Militar, Orgao, GrandeComando, Unidade, SubUnidade, CautelaArma, MovimentacaoArma, CautelaArmaColetiva, CautelaArmaColetivaItem, AssinaturaCautelaArma, AssinaturaCautelaArmaColetiva, Municao, SaidaMunicao
from .forms import CautelaArmaForm, DevolucaoCautelaArmaForm, CautelaArmaColetivaForm, CautelaArmaColetivaItemForm


class CautelaArmaListView(LoginRequiredMixin, ListView):
    """Lista todas as cautelas de armas (individuais e coletivas)"""
    template_name = 'militares/cautela_arma_list.html'
    context_object_name = 'cautelas'
    paginate_by = 20
    
    def get_queryset(self):
        # Filtros
        status = self.request.GET.get('status', '')
        militar_id = self.request.GET.get('militar', '')
        arma_id = self.request.GET.get('arma', '')
        tipo_cautela = self.request.GET.get('tipo_cautela', '')
        
        # Cautelas Individuais
        cautelas_individuais = CautelaArma.objects.select_related(
            'arma', 'militar', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
            'entregue_por', 'devolvido_por'
        ).order_by('-data_entrega')
        
        if status == 'ativa':
            cautelas_individuais = cautelas_individuais.filter(ativa=True)
        elif status == 'devolvida':
            cautelas_individuais = cautelas_individuais.filter(ativa=False)
        
        if militar_id:
            cautelas_individuais = cautelas_individuais.filter(militar_id=militar_id)
        
        if arma_id:
            cautelas_individuais = cautelas_individuais.filter(arma_id=arma_id)
        
        # Cautelas Coletivas (as cautelas em si, não os itens)
        cautelas_coletivas = CautelaArmaColetiva.objects.select_related(
            'responsavel', 'orgao', 'grande_comando',
            'unidade', 'sub_unidade', 'criado_por', 'finalizado_por'
        ).prefetch_related('armas').order_by('-data_inicio')
        
        if status == 'ativa':
            cautelas_coletivas = cautelas_coletivas.filter(ativa=True)
        elif status == 'devolvida':
            cautelas_coletivas = cautelas_coletivas.filter(ativa=False)
        
        if militar_id:
            cautelas_coletivas = cautelas_coletivas.filter(responsavel_id=militar_id)
        
        if arma_id:
            # Filtrar cautelas coletivas que contêm a arma especificada
            cautelas_coletivas = cautelas_coletivas.filter(armas__arma_id=arma_id).distinct()
        
        # Filtrar por tipo de cautela
        if tipo_cautela == 'individual':
            return cautelas_individuais
        elif tipo_cautela == 'coletiva':
            return cautelas_coletivas
        
        # Combinar ambas as listas (marcar cada item com seu tipo)
        lista_combinada = []
        
        # Adicionar cautelas individuais (converter QuerySet para lista)
        for cautela in list(cautelas_individuais):
            cautela.tipo_cautela = 'individual'
            lista_combinada.append(cautela)
        
        # Adicionar cautelas coletivas (converter QuerySet para lista)
        for cautela_coletiva in list(cautelas_coletivas):
            cautela_coletiva.tipo_cautela = 'coletiva'
            lista_combinada.append(cautela_coletiva)
        
        # Ordenar: primeiro por status (ativas primeiro), depois por data (mais recente primeiro)
        def get_sort_key(x):
            # Primeiro critério: status (0 para ativas, 1 para finalizadas)
            # Assim, ativas (0) vêm antes de finalizadas (1)
            status_key = 0 if (hasattr(x, 'ativa') and x.ativa) else 1
            
            # Segundo critério: data (mais recente primeiro)
            # Usar timestamp negativo para ordenar do mais recente para o mais antigo
            data_value = None
            if hasattr(x, 'data_entrega') and x.data_entrega:
                data_value = x.data_entrega
            elif hasattr(x, 'data_inicio') and x.data_inicio:
                data_value = x.data_inicio
            else:
                data_value = timezone.now()
            
            # Retornar tupla: (status_key, -timestamp)
            # status_key: 0 (ativa) vem antes de 1 (finalizada)
            # timestamp negativo: mais recente primeiro
            timestamp = data_value.timestamp() if hasattr(data_value, 'timestamp') else 0
            return (status_key, -timestamp)
        
        lista_combinada.sort(key=get_sort_key)
        
        return lista_combinada
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['militares'] = Militar.objects.filter(situacao='ATIVO').order_by('nome_completo')
        context['armas'] = Arma.objects.filter(ativo=True).order_by('numero_serie')
        context['tipo_cautela'] = self.request.GET.get('tipo_cautela', '')
        
        # Verificar quais cautelas individuais já têm assinatura
        cautelas_com_assinatura = set()
        # Verificar quais cautelas coletivas já têm assinatura
        cautelas_coletivas_com_assinatura = set()
        
        # Usar object_list (paginação) ou cautelas (context_object_name)
        cautelas_lista = list(context.get('object_list', [])) or list(context.get('cautelas', []))
        
        # Buscar IDs de cautelas individuais e coletivas ativas na página atual
        cautelas_individuais_ids = [item.pk for item in cautelas_lista if hasattr(item, 'tipo_cautela') and item.tipo_cautela == 'individual' and item.ativa]
        cautelas_coletivas_ids = [item.pk for item in cautelas_lista if hasattr(item, 'tipo_cautela') and item.tipo_cautela == 'coletiva' and item.ativa]
        
        # Verificar assinaturas em lote para melhor performance
        if cautelas_individuais_ids:
            assinadas_individuais = AssinaturaCautelaArma.objects.filter(
                cautela_id__in=cautelas_individuais_ids,
                tipo_assinatura='RECEBENDO'
            ).values_list('cautela_id', flat=True)
            cautelas_com_assinatura.update(assinadas_individuais)
        
        if cautelas_coletivas_ids:
            assinadas_coletivas = AssinaturaCautelaArmaColetiva.objects.filter(
                cautela_id__in=cautelas_coletivas_ids,
                tipo_assinatura='RECEBENDO'
            ).values_list('cautela_id', flat=True)
            cautelas_coletivas_com_assinatura.update(assinadas_coletivas)
        
        context['cautelas_com_assinatura'] = cautelas_com_assinatura
        context['cautelas_coletivas_com_assinatura'] = cautelas_coletivas_com_assinatura
        return context


class CautelaArmaCreateView(LoginRequiredMixin, CreateView):
    """Cria nova cautela de arma"""
    model = CautelaArma
    form_class = CautelaArmaForm
    template_name = 'militares/cautela_arma_form.html'
    success_url = reverse_lazy('militares:cautela_arma_list')
    
    def get_initial(self):
        """Preenche o formulário com a arma se fornecida via GET"""
        initial = super().get_initial()
        arma_id = self.request.GET.get('arma')
        if arma_id:
            try:
                arma = Arma.objects.get(pk=arma_id, ativo=True)
                # Verificar se a arma não está inservível
                if arma.estado_conservacao != 'INSERVIVEL':
                    initial['arma'] = arma
            except Arma.DoesNotExist:
                pass
        return initial
    
    def get_context_data(self, **kwargs):
        """Adiciona a arma ao contexto se fornecida via GET"""
        context = super().get_context_data(**kwargs)
        arma_id = self.request.GET.get('arma')
        if arma_id:
            try:
                arma = Arma.objects.get(pk=arma_id, ativo=True)
                # Verificar se a arma não está inservível antes de adicionar ao contexto
                if arma.estado_conservacao != 'INSERVIVEL':
                    context['arma_selecionada'] = arma
                # Preencher organização automaticamente no formulário
                if 'form' in context and context['form']:
                    if arma.orgao:
                        context['form'].fields['orgao'].initial = arma.orgao
                    if arma.grande_comando:
                        context['form'].fields['grande_comando'].initial = arma.grande_comando
                    if arma.unidade:
                        context['form'].fields['unidade'].initial = arma.unidade
                    if arma.sub_unidade:
                        context['form'].fields['sub_unidade'].initial = arma.sub_unidade
            except Arma.DoesNotExist:
                pass
        return context
    
    def form_valid(self, form):
        arma = form.instance.arma
        militar = form.instance.militar
        
        # Validar se a arma pode ser cautelada
        if not arma.ativo:
            form.add_error('arma', 'Apenas armas ativas podem ser cauteladas.')
            return self.form_invalid(form)
        
        if arma.estado_conservacao == 'INSERVIVEL':
            form.add_error('arma', 'Armas inservíveis não podem ser cauteladas.')
            return self.form_invalid(form)
        
        if arma.situacao == 'CAUTELA_INDIVIDUAL':
            form.add_error('arma', 'Esta arma já está em cautela individual.')
            return self.form_invalid(form)
        
        # Preencher organização da arma automaticamente se não estiver preenchida
        if not form.instance.orgao and arma.orgao:
            form.instance.orgao = arma.orgao
            form.instance.grande_comando = arma.grande_comando
            form.instance.unidade = arma.unidade
            form.instance.sub_unidade = arma.sub_unidade
        
        # Garantir que a data de entrega seja a atual
        form.instance.data_entrega = timezone.now()
        form.instance.entregue_por = self.request.user
        form.instance.ativa = True
        
        with transaction.atomic():
            response = super().form_valid(form)
            cautela = form.instance
            
            # Atualizar situação da arma
            arma.militar_responsavel = militar
            arma.data_entrega_responsavel = cautela.data_entrega.date()
            arma.situacao = 'CAUTELA_INDIVIDUAL'
            arma.save()
            
            # Criar movimentação de entrega
            MovimentacaoArma.objects.create(
                arma=arma,
                tipo_movimentacao='ENTREGA',
                militar_destino=militar,
                organizacao_origem=cautela.get_organizacao(),
                quantidade_carregadores=cautela.quantidade_carregadores,
                numeracao_carregadores=cautela.numeracao_carregadores,
                quantidade_municoes_catalogadas=cautela.quantidade_municoes_catalogadas,
                observacoes=f"Cautela registrada por {self.request.user.get_full_name() or self.request.user.username}. {cautela.observacoes or ''}",
                responsavel_movimentacao=self.request.user
            )
            
            # Criar saída de munição se houver munições na cautela
            if cautela.quantidade_municoes_catalogadas and cautela.quantidade_municoes_catalogadas > 0:
                try:
                    # Buscar ou criar munição no estoque
                    municao, created = Municao.objects.get_or_create(
                        calibre=arma.calibre,
                        orgao=cautela.orgao,
                        grande_comando=cautela.grande_comando,
                        unidade=cautela.unidade,
                        sub_unidade=cautela.sub_unidade,
                        defaults={'quantidade_estoque': 0, 'criado_por': self.request.user}
                    )
                    
                    # Criar saída de munição
                    SaidaMunicao.objects.create(
                        municao=municao,
                        quantidade=cautela.quantidade_municoes_catalogadas,
                        tipo_saida='CAUTELA_INDIVIDUAL',
                        cautela_individual=cautela,
                        data_saida=cautela.data_entrega,
                        responsavel=self.request.user,
                        observacoes=f"Saída automática para cautela individual de {arma.numero_serie} - {militar.nome_completo}"
                    )
                except Exception as e:
                    # Log do erro mas não impede a criação da cautela
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Erro ao criar saída de munição para cautela {cautela.pk}: {str(e)}')
                    messages.warning(
                        self.request, 
                        f'Cautela criada com sucesso, mas houve erro ao registrar saída de munição: {str(e)}'
                    )
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Cautela de arma {arma.numero_serie} registrada com sucesso para {militar.nome_completo}!'
            })
        
        messages.success(self.request, f'Cautela de arma {arma.numero_serie} registrada com sucesso para {militar.nome_completo}!')
        return response
    
    def form_invalid(self, form):
        # Se for requisição AJAX e houver erros, retornar JSON com erros
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        # Se for requisição AJAX (GET), retornar HTML do formulário
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = None
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/cautela_arma_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class CautelaArmaDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma cautela"""
    model = CautelaArma
    template_name = 'militares/cautela_arma_detail.html'
    context_object_name = 'cautela'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Buscar assinaturas eletrônicas da cautela
        # Ordenar: primeiro RECEBENDO, depois ENTREGANDO, depois por data
        from django.db.models import Case, When, IntegerField
        context['assinaturas'] = AssinaturaCautelaArma.objects.filter(
            cautela=self.object
        ).select_related('assinado_por', 'militar').annotate(
            ordem_tipo=Case(
                When(tipo_assinatura='RECEBENDO', then=1),
                When(tipo_assinatura='ENTREGANDO', then=2),
                default=3,
                output_field=IntegerField()
            )
        ).order_by('ordem_tipo', 'data_assinatura')
        
        # Verificar se usuário pode fazer CRUD/PDF
        from militares.permissoes_militares import pode_fazer_crud_pdf
        context['pode_crud_pdf'] = pode_fazer_crud_pdf(self.request.user, self.object.militar)
        
        return context


@login_required
def cautela_arma_pdf(request, pk):
    """Gera PDF da cautela de arma no padrão das certidões"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    import pytz
    
    cautela = get_object_or_404(CautelaArma, pk=pk)
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        from django.conf import settings
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo_cbmepi.png')
        if not os.path.exists(logo_path) and settings.STATICFILES_DIRS:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'logo_cbmepi.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA ADMINISTRATIVA E FINANCEIRA",
            "SEÇÃO DE CONTROLE DE ARMAS E MUNIÇÕES",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>CAUTELA DE ARMA</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Informações da Cautela
        info_data = []
        
        # Dados do Militar
        if cautela.militar:
            posto_display = cautela.militar.get_posto_graduacao_display()
            info_data.append(['Militar:', f"{posto_display} BM {cautela.militar.nome_completo}"])
            info_data.append(['Matrícula:', cautela.militar.matricula or 'N/A'])
            info_data.append(['CPF:', cautela.militar.cpf or 'N/A'])
        else:
            info_data.append(['Militar:', 'N/A'])
        
        # Dados da Arma
        if cautela.arma:
            info_data.append(['Arma - Número de Série:', cautela.arma.numero_serie])
            info_data.append(['Tipo:', cautela.arma.get_tipo_display()])
            info_data.append(['Marca/Modelo:', f"{cautela.arma.marca} {cautela.arma.modelo}"])
            info_data.append(['Calibre:', cautela.arma.get_calibre_display()])
        else:
            info_data.append(['Arma:', 'N/A'])
        
        # Datas
        info_data.append(['Data de Entrega:', cautela.data_entrega.strftime("%d/%m/%Y %H:%M") if cautela.data_entrega else 'N/A'])
        if cautela.data_devolucao:
            info_data.append(['Data de Devolução:', cautela.data_devolucao.strftime("%d/%m/%Y %H:%M")])
        
        # Organização
        if cautela.get_organizacao():
            info_data.append(['Organização:', cautela.get_organizacao()])
        
        # Status
        status = "Ativa" if cautela.ativa else "Devolvida"
        info_data.append(['Status:', status])
        
        # Criar tabela de informações
        info_table = Table(info_data, colWidths=[5*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 15))
        
        # Texto de Declaração de Responsabilidade
        story.append(Paragraph("<b>DECLARAÇÃO DE RESPONSABILIDADE</b>", style_bold))
        story.append(Spacer(1, 8))
        
        texto_responsabilidade = (
            "<b>Declaro, sob minha inteira responsabilidade,</b> que recebi a arma descrita neste documento, "
            "em perfeitas condições de conservação e funcionamento, e que a utilizarei conforme legislação vigente, "
            "normas internas e ordens superiores."
        )
        story.append(Paragraph(texto_responsabilidade, style_just))
        story.append(Spacer(1, 5))
        story.append(Paragraph("<b>Comprometo-me a:</b>", style_bold))
        story.append(Spacer(1, 8))
        
        # Lista de compromissos
        compromissos = [
            "Zelar pela guarda, integridade e segurança da arma;",
            "Comunicar imediatamente qualquer pane, avaria, extravio, furto ou uso indevido;",
            "Devolver a arma no prazo e condições estabelecidos;",
            "Responder disciplinar, civil e criminalmente por qualquer irregularidade decorrente do uso ou guarda."
        ]
        
        for compromisso in compromissos:
            story.append(Paragraph(f"• {compromisso}", ParagraphStyle('compromisso', parent=styles['Normal'], fontSize=11, alignment=0, leftIndent=20, spaceAfter=3)))
        
        story.append(Spacer(1, 10))
        
        # Observações (se houver)
        if cautela.observacoes:
            story.append(Paragraph("<b>OBSERVAÇÕES:</b>", style_bold))
            story.append(Spacer(1, 5))
            story.append(Paragraph(cautela.observacoes, style_normal))
            story.append(Spacer(1, 10))
        
        # Cidade e Data por extenso (centralizada)
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
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=10)))
        
        # Adicionar assinaturas eletrônicas se houver
        # Ordenar: primeiro RECEBENDO, depois ENTREGANDO, depois por data
        from django.db.models import Case, When, IntegerField
        assinaturas = AssinaturaCautelaArma.objects.filter(
            cautela=cautela
        ).select_related('assinado_por', 'militar').annotate(
            ordem_tipo=Case(
                When(tipo_assinatura='RECEBENDO', then=1),
                When(tipo_assinatura='ENTREGANDO', then=2),
                default=3,
                output_field=IntegerField()
            )
        ).order_by('ordem_tipo', 'data_assinatura')
        
        if assinaturas.exists():
            story.append(Spacer(1, 10))
            
            for assinatura in assinaturas:
                # Data e hora da assinatura
                data_assinatura = assinatura.data_assinatura.astimezone(brasilia_tz) if timezone.is_aware(assinatura.data_assinatura) else brasilia_tz.localize(assinatura.data_assinatura)
                data_formatada = data_assinatura.strftime('%d/%m/%Y')
                hora_formatada = data_assinatura.strftime('%H:%M:%S')
                
                nome_assinante = ""
                if assinatura.militar:
                    nome_assinante = f"{assinatura.militar.get_posto_graduacao_display()} BM {assinatura.militar.nome_completo}"
                else:
                    nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                
                texto_assinatura = (
                    f"Documento assinado eletronicamente por <b>{nome_assinante}</b>, em {data_formatada} {hora_formatada}, "
                    f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
                )
                
                # Adicionar logo da assinatura eletrônica
                from .utils import obter_caminho_assinatura_eletronica
                logo_path_assinatura = obter_caminho_assinatura_eletronica()
                
                # Tabela das assinaturas: Logo + Texto de assinatura
                assinatura_data = [
                    [Image(logo_path_assinatura, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
                ]
                
                assinatura_table = Table(assinatura_data, colWidths=[3*cm, 13*cm])
                assinatura_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BOX', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                
                story.append(assinatura_table)
                story.append(Spacer(1, 5))
        
        # Informação de Devolução (se a cautela foi devolvida) - DEPOIS das assinaturas
        if not cautela.ativa and cautela.devolvido_por:
            # Buscar assinatura de devolução (ENTREGANDO) para obter data/hora exata
            assinatura_devolucao = AssinaturaCautelaArma.objects.filter(
                cautela=cautela,
                tipo_assinatura='ENTREGANDO'
            ).order_by('-data_assinatura').first()
            
            # Obter nome completo do responsável
            nome_responsavel = ""
            if assinatura_devolucao and assinatura_devolucao.militar:
                nome_responsavel = f"{assinatura_devolucao.militar.get_posto_graduacao_display()} BM {assinatura_devolucao.militar.nome_completo}"
            elif cautela.devolvido_por:
                if hasattr(cautela.devolvido_por, 'militar') and cautela.devolvido_por.militar:
                    nome_responsavel = f"{cautela.devolvido_por.militar.get_posto_graduacao_display()} BM {cautela.devolvido_por.militar.nome_completo}"
                else:
                    nome_responsavel = cautela.devolvido_por.get_full_name() or cautela.devolvido_por.username
            
            # Usar data da assinatura de devolução ou data_devolucao
            data_devolucao = None
            if assinatura_devolucao:
                data_devolucao = assinatura_devolucao.data_assinatura
            elif cautela.data_devolucao:
                data_devolucao = cautela.data_devolucao
            
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>DEVOLUÇÃO DA ARMA</b>", style_bold))
            story.append(Spacer(1, 5))
            texto_devolucao = f"A arma foi devolvida e recebida por <b>{nome_responsavel}</b>"
            if data_devolucao:
                data_formatada = data_devolucao.astimezone(brasilia_tz) if timezone.is_aware(data_devolucao) else brasilia_tz.localize(data_devolucao)
                texto_devolucao += f" em <b>{data_formatada.strftime('%d/%m/%Y %H:%M')}</b>."
            else:
                texto_devolucao += "."
            story.append(Paragraph(texto_devolucao, style_normal))
            story.append(Spacer(1, 10))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(cautela, request, tipo_documento='cautela_arma')
        
        # Tabela do rodapé: QR + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        buffer.seek(0)
        
        # Retornar PDF para visualização no navegador
        nome_arquivo = f"cautela_arma_{cautela.arma.numero_serie if cautela.arma else 'N/A'}_{cautela.militar.nome_guerra.replace(' ', '_') if cautela.militar and cautela.militar.nome_guerra else 'N/A'}.pdf"
        response = FileResponse(buffer, as_attachment=False, filename=nome_arquivo, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nome_arquivo}"'
        return response
        
    except Exception as e:
        import traceback
        error_details = str(e)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar PDF de cautela de arma {cautela.pk}: {error_details}\n{traceback.format_exc()}')
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Cautela de Arma</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                .error-detail {{ background-color: #fff; padding: 10px; border-radius: 3px; 
                               margin: 10px 0; font-size: 12px; text-align: left; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF da cautela de arma.</strong></p>
                <div class="error-detail">
                    <strong>Detalhes do erro:</strong><br>
                    {error_details}
                </div>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def cautela_arma_coletiva_pdf(request, pk):
    """Gera PDF da cautela coletiva de arma no padrão das certidões"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    import pytz
    
    cautela = get_object_or_404(CautelaArmaColetiva, pk=pk)
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        from django.conf import settings
        logo_path = os.path.join(settings.STATIC_ROOT, 'logo_cbmepi.png')
        if not os.path.exists(logo_path) and settings.STATICFILES_DIRS:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'logo_cbmepi.png')
        if not os.path.exists(logo_path):
            logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA ADMINISTRATIVA E FINANCEIRA",
            "SEÇÃO DE CONTROLE DE ARMAS E MUNIÇÕES",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>CAUTELA DE ARMAS</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Informações da Cautela Coletiva
        info_data = []
        
        # Dados do Responsável
        if cautela.responsavel:
            posto_display = cautela.responsavel.get_posto_graduacao_display()
            info_data.append(['Responsável:', f"{posto_display} BM {cautela.responsavel.nome_completo}"])
            info_data.append(['Matrícula:', cautela.responsavel.matricula or 'N/A'])
            info_data.append(['CPF:', cautela.responsavel.cpf or 'N/A'])
        else:
            info_data.append(['Responsável:', 'N/A'])
        
        # Descrição e Tipo
        info_data.append(['Descrição/Finalidade:', cautela.descricao])
        info_data.append(['Tipo de Finalidade:', cautela.get_tipo_finalidade_display()])
        
        # Datas
        info_data.append(['Data de Início:', cautela.data_inicio.strftime("%d/%m/%Y %H:%M") if cautela.data_inicio else 'N/A'])
        if cautela.data_fim:
            info_data.append(['Data de Fim:', cautela.data_fim.strftime("%d/%m/%Y %H:%M")])
        
        # Organização
        if cautela.get_organizacao():
            info_data.append(['Organização:', cautela.get_organizacao()])
        
        # Documento de Referência
        if cautela.documento_referencia:
            info_data.append(['Documento de Referência:', cautela.documento_referencia])
        
        # Total de Armas
        total_armas = cautela.get_total_armas()
        info_data.append(['Total de Armas:', f"{total_armas} arma(s)"])
        
        # Status
        status = "Ativa" if cautela.ativa else "Finalizada"
        info_data.append(['Status:', status])
        
        # Criar tabela de informações
        info_table = Table(info_data, colWidths=[5*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 15))
        
        # Lista de Armas
        story.append(Paragraph("<b>ARMAS CAUTELADAS</b>", ParagraphStyle('armas_titulo', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', alignment=1)))
        story.append(Spacer(1, 8))
        
        # Buscar todas as armas da cautela
        armas_cautela = cautela.armas.select_related('arma').order_by('arma__numero_serie')
        
        if armas_cautela.exists():
            # Estilos para células da tabela
            style_cell_header = ParagraphStyle('cell_header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)
            style_cell = ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)
            
            # Cabeçalho da tabela de armas
            armas_data = [
                [
                    Paragraph('Nº Série', style_cell_header),
                    Paragraph('Tipo', style_cell_header),
                    Paragraph('Marca/Modelo', style_cell_header),
                    Paragraph('Calibre', style_cell_header),
                    Paragraph('Status', style_cell_header)
                ]
            ]
            
            for item in armas_cautela:
                arma = item.arma
                status_arma = "Devolvida" if item.devolvida else "Ativa"
                armas_data.append([
                    Paragraph(str(arma.numero_serie), style_cell),
                    Paragraph(str(arma.get_tipo_display()), style_cell),
                    Paragraph(f"{arma.marca} {arma.modelo}", style_cell),
                    Paragraph(str(arma.get_calibre_display()), style_cell),
                    Paragraph(status_arma, style_cell)
                ])
            
            # Criar tabela de armas - ajustar larguras para caber na página
            # Largura total disponível: 16cm (A4 - margens)
            armas_table = Table(armas_data, colWidths=[3.5*cm, 2.5*cm, 4.5*cm, 2.5*cm, 3*cm], repeatRows=1)
            armas_table.setStyle(TableStyle([
                # Cabeçalho
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('TOPPADDING', (0, 0), (-1, 0), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                # Linhas de dados
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                # Bordas
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]))
            
            story.append(armas_table)
        else:
            story.append(Paragraph("Nenhuma arma cadastrada nesta cautela.", style_normal))
        
        story.append(Spacer(1, 15))
        
        # Texto de Declaração de Responsabilidade
        story.append(Paragraph("<b>DECLARAÇÃO DE RESPONSABILIDADE</b>", style_bold))
        story.append(Spacer(1, 8))
        
        texto_responsabilidade = (
            "<b>Declaro, sob minha inteira responsabilidade,</b> que recebi as armas descritas neste documento, "
            "em perfeitas condições de conservação e funcionamento, e que as utilizarei conforme legislação vigente, "
            "normas internas e ordens superiores."
        )
        story.append(Paragraph(texto_responsabilidade, style_just))
        story.append(Spacer(1, 5))
        story.append(Paragraph("<b>Comprometo-me a:</b>", style_bold))
        story.append(Spacer(1, 8))
        
        # Lista de compromissos
        compromissos = [
            "Zelar pela guarda, integridade e segurança das armas;",
            "Comunicar imediatamente qualquer pane, avaria, extravio, furto ou uso indevido;",
            "Devolver as armas no prazo e condições estabelecidos;",
            "Responder disciplinar, civil e criminalmente por qualquer irregularidade decorrente do uso ou guarda."
        ]
        
        for compromisso in compromissos:
            story.append(Paragraph(f"• {compromisso}", ParagraphStyle('compromisso', parent=styles['Normal'], fontSize=11, alignment=0, leftIndent=20, spaceAfter=3)))
        
        story.append(Spacer(1, 10))
        
        # Observações (se houver)
        if cautela.observacoes:
            story.append(Paragraph("<b>OBSERVAÇÕES:</b>", style_bold))
            story.append(Spacer(1, 5))
            story.append(Paragraph(cautela.observacoes, style_normal))
            story.append(Spacer(1, 10))
        
        # Cidade e Data por extenso (centralizada)
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
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=10)))
        
        # Adicionar assinaturas eletrônicas se houver
        # Ordenar: primeiro RECEBENDO, depois ENTREGANDO, depois por data
        from django.db.models import Case, When, IntegerField
        assinaturas = AssinaturaCautelaArmaColetiva.objects.filter(
            cautela=cautela
        ).select_related('assinado_por', 'militar').annotate(
            ordem_tipo=Case(
                When(tipo_assinatura='RECEBENDO', then=1),
                When(tipo_assinatura='ENTREGANDO', then=2),
                default=3,
                output_field=IntegerField()
            )
        ).order_by('ordem_tipo', 'data_assinatura')
        
        if assinaturas.exists():
            story.append(Spacer(1, 10))
            
            for assinatura in assinaturas:
                # Data e hora da assinatura
                data_assinatura = assinatura.data_assinatura.astimezone(brasilia_tz) if timezone.is_aware(assinatura.data_assinatura) else brasilia_tz.localize(assinatura.data_assinatura)
                data_formatada = data_assinatura.strftime('%d/%m/%Y')
                hora_formatada = data_assinatura.strftime('%H:%M:%S')
                
                nome_assinante = ""
                if assinatura.militar:
                    nome_assinante = f"{assinatura.militar.get_posto_graduacao_display()} BM {assinatura.militar.nome_completo}"
                else:
                    nome_assinante = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                
                funcao_display = assinatura.funcao_assinatura or "Bombeiro Militar"
                
                texto_assinatura = (
                    f"Documento assinado eletronicamente por <b>{nome_assinante}</b>, "
                    f"em {data_formatada} {hora_formatada}, conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
                )
                
                # Adicionar logo da assinatura eletrônica
                from .utils import obter_caminho_assinatura_eletronica
                logo_path_assinatura = obter_caminho_assinatura_eletronica()
                
                # Tabela das assinaturas: Logo + Texto de assinatura
                assinatura_data = [
                    [Image(logo_path_assinatura, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
                ]
                
                assinatura_table = Table(assinatura_data, colWidths=[3*cm, 13*cm])
                assinatura_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BOX', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                
                story.append(assinatura_table)
                story.append(Spacer(1, 5))
        
        # Informação de Devolução (se a cautela foi finalizada) - DEPOIS das assinaturas
        if not cautela.ativa and cautela.finalizado_por:
            # Buscar assinatura de devolução (ENTREGANDO) para obter data/hora exata
            assinatura_devolucao = AssinaturaCautelaArmaColetiva.objects.filter(
                cautela=cautela,
                tipo_assinatura='ENTREGANDO'
            ).order_by('-data_assinatura').first()
            
            # Obter nome completo do responsável
            nome_responsavel = ""
            if assinatura_devolucao and assinatura_devolucao.militar:
                nome_responsavel = f"{assinatura_devolucao.militar.get_posto_graduacao_display()} BM {assinatura_devolucao.militar.nome_completo}"
            elif cautela.finalizado_por:
                if hasattr(cautela.finalizado_por, 'militar') and cautela.finalizado_por.militar:
                    nome_responsavel = f"{cautela.finalizado_por.militar.get_posto_graduacao_display()} BM {cautela.finalizado_por.militar.nome_completo}"
                else:
                    nome_responsavel = cautela.finalizado_por.get_full_name() or cautela.finalizado_por.username
            
            # Usar data da assinatura de devolução ou data_fim
            data_devolucao = None
            if assinatura_devolucao:
                data_devolucao = assinatura_devolucao.data_assinatura
            elif cautela.data_fim:
                data_devolucao = cautela.data_fim
            
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>DEVOLUÇÃO DAS ARMAS</b>", style_bold))
            story.append(Spacer(1, 5))
            texto_devolucao = f"Todas as armas desta cautela foram devolvidas e recebidas por <b>{nome_responsavel}</b>"
            if data_devolucao:
                data_formatada = data_devolucao.astimezone(brasilia_tz) if timezone.is_aware(data_devolucao) else brasilia_tz.localize(data_devolucao)
                texto_devolucao += f" em <b>{data_formatada.strftime('%d/%m/%Y %H:%M')}</b>."
            else:
                texto_devolucao += "."
            story.append(Paragraph(texto_devolucao, style_normal))
            story.append(Spacer(1, 10))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(cautela, request, tipo_documento='cautela_arma_coletiva')
        
        # Tabela do rodapé: QR + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        buffer.seek(0)
        
        # Retornar PDF para visualização no navegador
        nome_arquivo = f"cautela_coletiva_{cautela.pk}_{cautela.responsavel.nome_guerra.replace(' ', '_') if cautela.responsavel and cautela.responsavel.nome_guerra else 'N/A'}.pdf"
        response = FileResponse(buffer, as_attachment=False, filename=nome_arquivo, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{nome_arquivo}"'
        return response
        
    except Exception as e:
        import traceback
        error_details = str(e)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao gerar PDF de cautela coletiva de arma {cautela.pk}: {error_details}\n{traceback.format_exc()}')
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Cautela Coletiva de Arma</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                .error-detail {{ background-color: #fff; padding: 10px; border-radius: 3px; 
                               margin: 10px 0; font-size: 12px; text-align: left; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF da cautela coletiva de arma.</strong></p>
                <div class="error-detail">
                    <strong>Detalhes do erro:</strong><br>
                    {error_details}
                </div>
                <p>Por favor, tente novamente ou entre em contato com o suporte técnico.</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def arma_dados_organizacao(request, pk):
    """Retorna dados da organização da arma via AJAX"""
    arma = get_object_or_404(Arma, pk=pk)
    
    # Determinar qual organização está selecionada
    organograma_id = None
    if arma.sub_unidade:
        organograma_id = f'sub_{arma.sub_unidade.id}'
    elif arma.unidade:
        organograma_id = f'unidade_{arma.unidade.id}'
    elif arma.grande_comando:
        organograma_id = f'gc_{arma.grande_comando.id}'
    elif arma.orgao:
        organograma_id = f'orgao_{arma.orgao.id}'
    
    # Obter texto da organização
    organizacao_texto = ''
    if hasattr(arma, 'get_organizacao_display'):
        organizacao_texto = str(arma.get_organizacao_display())
    else:
        # Fallback: construir manualmente se o método não existir
        hierarquia = []
        if arma.orgao:
            hierarquia.append(arma.orgao.nome)
        if arma.grande_comando:
            hierarquia.append(arma.grande_comando.nome)
        if arma.unidade:
            hierarquia.append(arma.unidade.nome)
        if arma.sub_unidade:
            hierarquia.append(arma.sub_unidade.nome)
        if hierarquia:
            organizacao_texto = " | ".join(hierarquia)
        else:
            organizacao_texto = "Não definido"
    
    dados = {
        'orgao_id': arma.orgao.id if arma.orgao else None,
        'grande_comando_id': arma.grande_comando.id if arma.grande_comando else None,
        'unidade_id': arma.unidade.id if arma.unidade else None,
        'sub_unidade_id': arma.sub_unidade.id if arma.sub_unidade else None,
        'organograma_id': organograma_id,
        'organizacao_texto': organizacao_texto
    }
    
    return JsonResponse(dados)


@login_required
def devolver_cautela_arma(request, pk):
    """Devolve uma cautela de arma"""
    cautela = get_object_or_404(CautelaArma, pk=pk, ativa=True)
    
    if request.method == 'POST':
        form = DevolucaoCautelaArmaForm(request.POST, instance=cautela)
        if form.is_valid():
            with transaction.atomic():
                cautela.ativa = False
                cautela.data_devolucao = timezone.now()
                cautela.devolvido_por = request.user
                if form.cleaned_data.get('observacoes'):
                    if cautela.observacoes:
                        cautela.observacoes += f"\n\nDevolução: {form.cleaned_data['observacoes']}"
                    else:
                        cautela.observacoes = f"Devolução: {form.cleaned_data['observacoes']}"
                cautela.save()
                
                # Atualizar situação da arma
                arma = cautela.arma
                arma.militar_responsavel = None
                arma.data_entrega_responsavel = None
                arma.situacao = 'RESERVA_ARMAMENTO'
                arma.save()
                
                # Criar movimentação de devolução
                MovimentacaoArma.objects.create(
                    arma=arma,
                    tipo_movimentacao='DEVOLUCAO',
                    militar_origem=cautela.militar,
                    organizacao_destino=cautela.get_organizacao(),
                    quantidade_carregadores=cautela.quantidade_carregadores,
                    numeracao_carregadores=cautela.numeracao_carregadores,
                    quantidade_municoes_catalogadas=cautela.quantidade_municoes_catalogadas,
                    observacoes=f"Devolução de cautela registrada por {request.user.get_full_name() or request.user.username}. {form.cleaned_data.get('observacoes', '')}",
                    responsavel_movimentacao=request.user
                )
                
                # Criar assinatura automática de quem está recebendo a arma de volta (ENTREGANDO)
                militar_devolvido = None
                if hasattr(request.user, 'militar') and request.user.militar:
                    militar_devolvido = request.user.militar
                
                # Obter função do usuário
                funcao_assinatura = None
                try:
                    from .permissoes_hierarquicas import obter_funcao_militar_ativa
                    funcao_usuario = obter_funcao_militar_ativa(request.user)
                    if funcao_usuario and funcao_usuario.funcao_militar:
                        funcao_assinatura = funcao_usuario.funcao_militar.nome
                except:
                    pass
                
                # Criar assinatura do tipo ENTREGANDO (quem está recebendo a arma de volta)
                # Verificar se já existe para evitar duplicatas
                filtro_assinatura = {
                    'cautela': cautela,
                    'tipo_assinatura': 'ENTREGANDO'
                }
                if militar_devolvido:
                    filtro_assinatura['militar'] = militar_devolvido
                else:
                    filtro_assinatura['militar__isnull'] = True
                    filtro_assinatura['assinado_por'] = request.user
                
                assinatura_existente = AssinaturaCautelaArma.objects.filter(**filtro_assinatura).first()
                
                if not assinatura_existente:
                    AssinaturaCautelaArma.objects.create(
                        cautela=cautela,
                        assinado_por=request.user,
                        militar=militar_devolvido,
                        tipo_assinatura='ENTREGANDO',
                        funcao_assinatura=funcao_assinatura,
                        observacoes=f"Arma devolvida em {timezone.now().strftime('%d/%m/%Y %H:%M')}. {form.cleaned_data.get('observacoes', '')}"
                    )
            
            # Se for requisição AJAX, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Cautela de arma {arma.numero_serie} devolvida com sucesso!'
                })
            
            messages.success(request, f'Cautela de arma {arma.numero_serie} devolvida com sucesso!')
            return redirect('militares:cautela_arma_detail', pk=cautela.pk)
        else:
            # Se for requisição AJAX e houver erros, retornar JSON com erros
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Erro ao processar devolução. Verifique os campos.'
                }, status=400)
    else:
        form = DevolucaoCautelaArmaForm(instance=cautela)
    
    # Se for requisição AJAX (GET), retornar HTML do formulário
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('militares/cautela_arma_devolver_modal_content.html', {
            'cautela': cautela,
            'form': form
        }, request=request)
        return JsonResponse({'html': html})
    
    context = {
        'cautela': cautela,
        'form': form,
        'title': f'Devolver Cautela: {cautela.arma.numero_serie}'
    }
    return render(request, 'militares/cautela_arma_devolver.html', context)


# ========== CAUTELA COLETIVA ==========

# View removida - as cautelas coletivas agora são listadas junto com as individuais em CautelaArmaListView
# class CautelaArmaColetivaListView(LoginRequiredMixin, ListView):
#     """Lista todas as cautelas coletivas de armas"""
#     model = CautelaArmaColetiva
#     template_name = 'militares/cautela_arma_coletiva_list.html'
#     context_object_name = 'cautelas'
#     paginate_by = 20
#     
#     def get_queryset(self):
#         queryset = CautelaArmaColetiva.objects.select_related(
#             'responsavel', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
#             'criado_por', 'finalizado_por'
#         ).prefetch_related('armas').order_by('-data_inicio')
#         
#         # Filtros
#         status = self.request.GET.get('status', '')
#         tipo = self.request.GET.get('tipo', '')
#         responsavel_id = self.request.GET.get('responsavel', '')
#         
#         if status == 'ativa':
#             queryset = queryset.filter(ativa=True)
#         elif status == 'finalizada':
#             queryset = queryset.filter(ativa=False)
#         
#         if tipo:
#             queryset = queryset.filter(tipo_finalidade=tipo)
#         
#         if responsavel_id:
#             queryset = queryset.filter(responsavel_id=responsavel_id)
#         
#         return queryset
#     
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['militares'] = Militar.objects.filter(classificacao='ATIVO').order_by('nome_completo')
#         return context


class CautelaArmaColetivaCreateView(LoginRequiredMixin, CreateView):
    """Cria nova cautela coletiva de armas"""
    model = CautelaArmaColetiva
    form_class = CautelaArmaColetivaForm
    template_name = 'militares/cautela_arma_coletiva_form.html'
    success_url = reverse_lazy('militares:cautela_arma_list')
    
    def get_initial(self):
        """Define valores iniciais do formulário"""
        initial = super().get_initial()
        # Formatar data/hora no formato correto para datetime-local
        now = timezone.now()
        initial['data_inicio'] = now.strftime('%Y-%m-%dT%H:%M')
        return initial
    
    def form_valid(self, form):
        # Verificar se pelo menos uma arma foi selecionada
        armas_selecionadas = self.request.POST.getlist('armas_selecionadas')
        armas_validas = [arma_id for arma_id in armas_selecionadas if arma_id]
        
        if not armas_validas:
            # Se for requisição AJAX, retornar JSON com erro
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'armas_selecionadas': ['É obrigatório selecionar pelo menos uma arma para a cautela coletiva.']},
                    'message': 'É obrigatório selecionar pelo menos uma arma para a cautela coletiva.'
                }, status=400)
            
            # Se não for AJAX, adicionar erro ao formulário
            form.add_error(None, 'É obrigatório selecionar pelo menos uma arma para a cautela coletiva.')
            return self.form_invalid(form)
        
        form.instance.criado_por = self.request.user
        form.instance.ativa = True
        form.instance.data_inicio = timezone.now()
        
        with transaction.atomic():
            response = super().form_valid(form)
            cautela = form.instance
            
            # Criar itens de cautela para cada arma selecionada
            armas_processadas = 0
            for arma_id in armas_validas:
                try:
                    arma = Arma.objects.get(pk=arma_id, ativo=True, situacao='RESERVA_ARMAMENTO')
                    
                    # Verificar se a arma não está inservível
                    if arma.estado_conservacao == 'INSERVIVEL':
                        continue  # Pular esta arma
                    
                    item = CautelaArmaColetivaItem.objects.create(
                        cautela=cautela,
                        arma=arma,
                        data_entrega=timezone.now(),
                        devolvida=False
                    )
                    
                    # Atualizar situação da arma
                    arma.situacao = 'CAUTELA_INDIVIDUAL'
                    arma.save()
                    armas_processadas += 1
                except (Arma.DoesNotExist, ValueError) as e:
                    # Ignorar armas inválidas ou que não podem ser cauteladas
                    pass
            
            # Verificar se pelo menos uma arma foi processada com sucesso
            if armas_processadas == 0:
                # Reverter a criação da cautela se nenhuma arma foi processada
                cautela.delete()
                error_msg = 'Nenhuma arma válida foi selecionada. A cautela não foi criada.'
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'armas_selecionadas': [error_msg]},
                        'message': error_msg
                    }, status=400)
                form.add_error(None, error_msg)
                return self.form_invalid(form)
        
        # Se for requisição AJAX, retornar JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Cautela coletiva "{form.instance.descricao}" criada com sucesso!',
                'redirect_url': reverse('militares:cautela_arma_coletiva_detail', kwargs={'pk': form.instance.pk})
            })
        
        messages.success(self.request, f'Cautela coletiva "{form.instance.descricao}" criada com sucesso!')
        return redirect('militares:cautela_arma_coletiva_detail', pk=form.instance.pk)
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao processar formulário. Verifique os campos.'
            }, status=400)
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Buscar todas as armas ativas e não inservíveis (mostrar todas, mas apenas as em RESERVA_ARMAMENTO podem ser selecionadas)
        context['armas_disponiveis'] = Arma.objects.filter(
            ativo=True
        ).exclude(
            estado_conservacao='INSERVIVEL'
        ).order_by('numero_serie')
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object = None
            form = self.get_form()
            context = self.get_context_data(form=form)
            from django.template.loader import render_to_string
            html = render_to_string('militares/cautela_arma_coletiva_form_modal_content.html', context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)


class CautelaArmaColetivaDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma cautela coletiva"""
    model = CautelaArmaColetiva
    template_name = 'militares/cautela_arma_coletiva_detail.html'
    context_object_name = 'cautela'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_item'] = CautelaArmaColetivaItemForm(cautela=self.object)
        # Buscar assinaturas eletrônicas da cautela coletiva
        # Ordenar: primeiro RECEBENDO, depois ENTREGANDO, depois por data
        from django.db.models import Case, When, IntegerField
        context['assinaturas'] = AssinaturaCautelaArmaColetiva.objects.filter(
            cautela=self.object
        ).select_related('assinado_por', 'militar').annotate(
            ordem_tipo=Case(
                When(tipo_assinatura='RECEBENDO', then=1),
                When(tipo_assinatura='ENTREGANDO', then=2),
                default=3,
                output_field=IntegerField()
            )
        ).order_by('ordem_tipo', 'data_assinatura')
        
        # Verificar se usuário pode fazer CRUD/PDF
        # Para cautelas coletivas, verificar se o usuário é o responsável
        from militares.permissoes_militares import pode_fazer_crud_pdf, tem_funcao_restrita
        
        pode_crud_pdf = True
        tem_funcao_restrita_user = tem_funcao_restrita(self.request.user)
        
        if tem_funcao_restrita_user:
            # Verificar se o usuário é o responsável pela cautela coletiva
            is_responsavel = False
            if hasattr(self.request.user, 'militar') and self.request.user.militar:
                is_responsavel = (self.object.responsavel and 
                                 self.object.responsavel.pk == self.request.user.militar.pk)
            
            # Se não é responsável, não pode fazer CRUD/PDF
            if not is_responsavel:
                pode_crud_pdf = False
        
        context['pode_crud_pdf'] = pode_crud_pdf
        
        return context


@login_required
@require_http_methods(["POST"])
def adicionar_arma_cautela_coletiva(request, pk):
    """Adiciona uma arma a uma cautela coletiva"""
    cautela = get_object_or_404(CautelaArmaColetiva, pk=pk, ativa=True)
    
    form = CautelaArmaColetivaItemForm(request.POST, cautela=cautela)
    
    if form.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            item.cautela = cautela
            item.data_entrega = timezone.now()
            item.devolvida = False
            item.save()
            
            # Atualizar situação da arma apenas se estiver em RESERVA_ARMAMENTO
            arma = item.arma
            if arma.situacao == 'RESERVA_ARMAMENTO':
                arma.situacao = 'CAUTELA_INDIVIDUAL'
                arma.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Arma {arma.numero_serie} adicionada à cautela coletiva com sucesso!'
            })
        
        messages.success(request, f'Arma {arma.numero_serie} adicionada à cautela coletiva com sucesso!')
        return redirect('militares:cautela_arma_coletiva_detail', pk=cautela.pk)
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao adicionar arma. Verifique os campos.'
            }, status=400)
        
        messages.error(request, 'Erro ao adicionar arma. Verifique os campos.')
        return redirect('militares:cautela_arma_coletiva_detail', pk=cautela.pk)


@login_required
@require_http_methods(["POST"])
def remover_arma_cautela_coletiva(request, pk, item_id):
    """Remove uma arma de uma cautela coletiva (devolve)"""
    cautela = get_object_or_404(CautelaArmaColetiva, pk=pk, ativa=True)
    item = get_object_or_404(CautelaArmaColetivaItem, pk=item_id, cautela=cautela, devolvida=False)
    
    with transaction.atomic():
        item.devolvida = True
        item.data_devolucao = timezone.now()
        item.save()
        
        # Atualizar situação da arma
        arma = item.arma
        arma.situacao = 'RESERVA_ARMAMENTO'
        arma.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Arma {arma.numero_serie} devolvida com sucesso!'
        })
    
    messages.success(request, f'Arma {arma.numero_serie} devolvida com sucesso!')
    return redirect('militares:cautela_arma_coletiva_detail', pk=cautela.pk)


@login_required
def finalizar_cautela_coletiva(request, pk):
    """Finaliza uma cautela coletiva (devolve todas as armas)"""
    cautela = get_object_or_404(CautelaArmaColetiva, pk=pk, ativa=True)
    
    # Se for requisição GET (AJAX), retornar HTML do formulário
    if request.method == 'GET':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            html = render_to_string('militares/cautela_arma_coletiva_finalizar_modal_content.html', {
                'cautela': cautela
            }, request=request)
            return JsonResponse({'html': html})
        # Se não for AJAX, redirecionar para a página de detalhes
        return redirect('militares:cautela_arma_coletiva_detail', pk=cautela.pk)
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '').strip()
        
        try:
            with transaction.atomic():
                # Devolver todas as armas que ainda não foram devolvidas
                itens_ativos = cautela.armas.filter(devolvida=False)
                for item in itens_ativos:
                    item.devolvida = True
                    item.data_devolucao = timezone.now()
                    item.save()
                    
                    # Atualizar situação da arma
                    arma = item.arma
                    arma.situacao = 'RESERVA_ARMAMENTO'
                    arma.save()
                
                # Finalizar cautela
                cautela.ativa = False
                cautela.data_fim = timezone.now()
                cautela.finalizado_por = request.user
                if observacoes:
                    if cautela.observacoes:
                        cautela.observacoes += f"\n\nFinalização: {observacoes}"
                    else:
                        cautela.observacoes = f"Finalização: {observacoes}"
                cautela.save()
                
                # Criar assinatura automática de quem está recebendo as armas de volta (ENTREGANDO)
                militar_finalizador = None
                if hasattr(request.user, 'militar') and request.user.militar:
                    militar_finalizador = request.user.militar
                
                # Obter função do usuário
                funcao_assinatura = None
                try:
                    from .permissoes_hierarquicas import obter_funcao_militar_ativa
                    funcao_usuario = obter_funcao_militar_ativa(request.user)
                    if funcao_usuario and funcao_usuario.funcao_militar:
                        funcao_assinatura = funcao_usuario.funcao_militar.nome
                except:
                    pass
                
                # Criar assinatura do tipo ENTREGANDO (quem está recebendo as armas de volta)
                # Verificar se já existe para evitar duplicatas
                filtro_assinatura = {
                    'cautela': cautela,
                    'tipo_assinatura': 'ENTREGANDO'
                }
                if militar_finalizador:
                    filtro_assinatura['militar'] = militar_finalizador
                else:
                    filtro_assinatura['militar__isnull'] = True
                    filtro_assinatura['assinado_por'] = request.user
                
                assinatura_existente = AssinaturaCautelaArmaColetiva.objects.filter(**filtro_assinatura).first()
                
                if not assinatura_existente:
                    AssinaturaCautelaArmaColetiva.objects.create(
                        cautela=cautela,
                        assinado_por=request.user,
                        militar=militar_finalizador,
                        tipo_assinatura='ENTREGANDO',
                        funcao_assinatura=funcao_assinatura,
                        observacoes=f"Armas devolvidas em {timezone.now().strftime('%d/%m/%Y %H:%M')}. {observacoes if observacoes else ''}"
                    )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Cautela coletiva "{cautela.descricao}" finalizada com sucesso!'
                })
            
            messages.success(request, f'Cautela coletiva "{cautela.descricao}" finalizada com sucesso!')
            return redirect('militares:cautela_arma_coletiva_detail', pk=cautela.pk)
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Erro ao finalizar cautela coletiva: {error_trace}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': [str(e)]},
                    'message': f'Erro ao finalizar cautela coletiva: {str(e)}'
                }, status=400)
            
        messages.error(request, f'Erro ao finalizar cautela coletiva: {str(e)}')
        return redirect('militares:cautela_arma_list')


def assinar_cautela_arma(request, pk):
    """Assinar cautela como militar que recebe a arma - permite login do militar"""
    from django.contrib import messages
    
    cautela = get_object_or_404(CautelaArma, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        senha = request.POST.get('senha', '')
        
        # Verificar se há um militar na cautela
        if not cautela.militar:
            error_msg = 'Esta cautela não possui militar definido.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Verificar se o militar tem usuário vinculado
        militar_cautela = cautela.militar
        user_militar = militar_cautela.user if militar_cautela.user else None
        
        if not user_militar:
            error_msg = 'O militar desta cautela não possui usuário vinculado no sistema.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Verificar senha do usuário do militar
        if not user_militar.check_password(senha):
            error_msg = 'Senha incorreta. Tente novamente.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Verificar se já existe uma assinatura deste tipo
        assinatura_existente = AssinaturaCautelaArma.objects.filter(
            cautela=cautela,
            militar=militar_cautela,
            tipo_assinatura='RECEBENDO'
        ).first()
        
        if assinatura_existente:
            error_msg = 'Esta cautela já possui assinatura do militar.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Usar função padrão
        funcao_assinatura = 'Bombeiro Militar'
        
        # Criar a assinatura
        try:
            assinatura = AssinaturaCautelaArma.objects.create(
                cautela=cautela,
                assinado_por=user_militar,
                militar=militar_cautela,
                tipo_assinatura='RECEBENDO',
                funcao_assinatura=funcao_assinatura,
                observacoes=''
            )
            success_msg = 'Assinatura registrada com sucesso!'
            if is_ajax:
                return JsonResponse({'success': True, 'message': success_msg})
            messages.success(request, success_msg)
        except Exception as e:
            error_msg = f'Erro ao assinar cautela: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        
        if not is_ajax:
            return redirect('militares:cautela_arma_list')
        return JsonResponse({'success': True, 'message': success_msg})
    
    # Se for GET, retornar para a lista
    return redirect('militares:cautela_arma_list')


@login_required
def assinar_cautela_arma_coletiva(request, pk):
    """Assinar cautela coletiva como responsável - permite login do militar"""
    from django.contrib import messages
    
    cautela = get_object_or_404(CautelaArmaColetiva, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        senha = request.POST.get('senha', '')
        
        # Verificar se há um responsável na cautela
        if not cautela.responsavel:
            error_msg = 'Esta cautela coletiva não possui responsável definido.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Verificar se o responsável tem usuário vinculado
        responsavel_cautela = cautela.responsavel
        user_responsavel = responsavel_cautela.user if responsavel_cautela.user else None
        
        if not user_responsavel:
            error_msg = 'O responsável desta cautela coletiva não possui usuário vinculado no sistema.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Verificar senha do usuário do responsável
        if not user_responsavel.check_password(senha):
            error_msg = 'Senha incorreta. Tente novamente.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Verificar se já existe uma assinatura deste tipo
        assinatura_existente = AssinaturaCautelaArmaColetiva.objects.filter(
            cautela=cautela,
            militar=responsavel_cautela,
            tipo_assinatura='RECEBENDO'
        ).first()
        
        if assinatura_existente:
            error_msg = 'Esta cautela coletiva já possui assinatura do responsável.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('militares:cautela_arma_list')
        
        # Usar função padrão
        funcao_assinatura = 'Bombeiro Militar'
        
        # Criar a assinatura
        try:
            assinatura = AssinaturaCautelaArmaColetiva.objects.create(
                cautela=cautela,
                assinado_por=user_responsavel,
                militar=responsavel_cautela,
                tipo_assinatura='RECEBENDO',
                funcao_assinatura=funcao_assinatura,
                observacoes=''
            )
            success_msg = 'Assinatura registrada com sucesso!'
            if is_ajax:
                return JsonResponse({'success': True, 'message': success_msg})
            messages.success(request, success_msg)
        except Exception as e:
            error_msg = f'Erro ao assinar cautela coletiva: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
        
        if not is_ajax:
            return redirect('militares:cautela_arma_list')
        return JsonResponse({'success': True, 'message': success_msg})
    
    # Se for GET, retornar para a lista
    return redirect('militares:cautela_arma_list')


@login_required
@require_http_methods(["POST"])
def deletar_cautela_arma(request, pk):
    """Deletar cautela individual - apenas para superusuários"""
    if not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Apenas superusuários podem excluir cautelas.'}, status=403)
        messages.error(request, 'Apenas superusuários podem excluir cautelas.')
        return redirect('militares:cautela_arma_list')
    
    cautela = get_object_or_404(CautelaArma, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        arma_info = f"{cautela.arma.numero_serie}"
        cautela.delete()
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Cautela da arma {arma_info} excluída com sucesso!'
            })
        
        messages.success(request, f'Cautela da arma {arma_info} excluída com sucesso!')
        return redirect('militares:cautela_arma_list')
    except Exception as e:
        error_msg = f'Erro ao excluir cautela: {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('militares:cautela_arma_list')


@login_required
@require_http_methods(["POST"])
def deletar_cautela_arma_coletiva(request, pk):
    """Deletar cautela coletiva - apenas para superusuários"""
    if not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Apenas superusuários podem excluir cautelas.'}, status=403)
        messages.error(request, 'Apenas superusuários podem excluir cautelas.')
        return redirect('militares:cautela_arma_list')
    
    cautela = get_object_or_404(CautelaArmaColetiva, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        descricao = cautela.descricao
        cautela.delete()
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'Cautela coletiva "{descricao}" excluída com sucesso!'
            })
        
        messages.success(request, f'Cautela coletiva "{descricao}" excluída com sucesso!')
        return redirect('militares:cautela_arma_list')
    except Exception as e:
        error_msg = f'Erro ao excluir cautela coletiva: {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('militares:cautela_arma_list')

