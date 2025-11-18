"""
Views para o módulo de Controle de Rodagem de Viaturas
Gerencia o registro e controle de rodagens/uso das viaturas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Avg, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from .models import RodagemViatura, Viatura, Militar, Unidade
from .forms import RodagemViaturaForm


class RodagemListView(LoginRequiredMixin, ListView):
    """Lista todas as rodagens"""
    model = RodagemViatura
    template_name = 'militares/rodagem_list.html'
    context_object_name = 'rodagens'
    paginate_by = 30
    
    def get_queryset(self):
        queryset = RodagemViatura.objects.select_related(
            'viatura', 'condutor', 'criado_por'
        ).order_by('-data_saida', '-hora_saida')
        
        # Filtros
        search = self.request.GET.get('search', '')
        viatura_id = self.request.GET.get('viatura', '')
        status = self.request.GET.get('status', '')
        objetivo = self.request.GET.get('objetivo', '')
        data_inicio = self.request.GET.get('data_inicio', '')
        data_fim = self.request.GET.get('data_fim', '')
        ativo = self.request.GET.get('ativo', '')
        
        if search:
            queryset = queryset.filter(
                Q(viatura__placa__icontains=search) |
                Q(viatura__prefixo__icontains=search) |
                Q(destino__icontains=search) |
                Q(observacoes__icontains=search) |
                Q(condutor__nome_completo__icontains=search)
            )
        
        if viatura_id:
            queryset = queryset.filter(viatura_id=viatura_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if objetivo:
            queryset = queryset.filter(objetivo=objetivo)
        
        if data_inicio:
            queryset = queryset.filter(data_saida__gte=data_inicio)
        
        if data_fim:
            queryset = queryset.filter(data_saida__lte=data_fim)
        
        if ativo != '':
            if ativo == 'True' or ativo == 'true':
                queryset = queryset.filter(ativo=True)
            elif ativo == 'False' or ativo == 'false':
                queryset = queryset.filter(ativo=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas
        queryset = self.get_queryset()
        context['total_rodagens'] = queryset.count()
        context['total_km_rodado'] = queryset.aggregate(Sum('km_rodado'))['km_rodado__sum'] or 0
        
        # Filtros aplicados
        context['search'] = self.request.GET.get('search', '')
        context['viatura_id'] = self.request.GET.get('viatura', '')
        context['status'] = self.request.GET.get('status', '')
        context['objetivo'] = self.request.GET.get('objetivo', '')
        context['data_inicio'] = self.request.GET.get('data_inicio', '')
        context['data_fim'] = self.request.GET.get('data_fim', '')
        context['ativo'] = self.request.GET.get('ativo', '')
        
        # Lista de viaturas para filtro
        from .models import Viatura
        context['viaturas'] = Viatura.objects.filter(ativo=True).order_by('placa')
        
        return context


class RodagemCreateView(LoginRequiredMixin, CreateView):
    """Cria nova rodagem"""
    model = RodagemViatura
    form_class = RodagemViaturaForm
    template_name = 'militares/rodagem_form.html'
    success_url = reverse_lazy('militares:rodagem_list')

    def get_form_kwargs(self):
        """Passa o request para o formulário"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        """Define valores iniciais do formulário"""
        initial = super().get_initial()
        # Definir o condutor como o militar do usuário logado
        try:
            if hasattr(self.request.user, 'militar') and self.request.user.militar:
                initial['condutor'] = self.request.user.militar
        except:
            pass
        
        # Se vier viatura via GET, passar para o initial
        viatura_id = self.request.GET.get('viatura')
        if viatura_id:
            try:
                from .models import Viatura
                viatura = Viatura.objects.get(pk=viatura_id, ativo=True)
                initial['viatura'] = viatura
            except Viatura.DoesNotExist:
                pass
        
        return initial

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        # Sempre definir o condutor como o militar do usuário logado
        try:
            if hasattr(self.request.user, 'militar') and self.request.user.militar:
                form.instance.condutor = self.request.user.militar
        except:
            pass
        messages.success(self.request, f'Rodagem registrada com sucesso!')
        return super().form_valid(form)

    def get_success_url(self):
        # Se houver viatura no formulário, redirecionar para o histórico da viatura
        viatura_id = self.request.POST.get('viatura')
        if viatura_id:
            return reverse('militares:rodagem_por_viatura', kwargs={'viatura_id': viatura_id})
        return super().get_success_url()


class RodagemDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma rodagem"""
    model = RodagemViatura
    template_name = 'militares/rodagem_detail.html'
    context_object_name = 'rodagem'


class RodagemUpdateView(LoginRequiredMixin, UpdateView):
    """Edita uma rodagem"""
    model = RodagemViatura
    form_class = RodagemViaturaForm
    template_name = 'militares/rodagem_form.html'

    def get_form_kwargs(self):
        """Passa o request para o formulário"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f'Rodagem atualizada com sucesso!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('militares:rodagem_detail', kwargs={'pk': self.object.pk})


class RodagemDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui uma rodagem"""
    model = RodagemViatura
    template_name = 'militares/rodagem_confirm_delete.html'
    success_url = reverse_lazy('militares:rodagem_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Rodagem excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def viatura_ultimo_km(request, viatura_id):
    """Retorna o último KM da viatura (última rodagem finalizada)"""
    from .models import Viatura, RodagemViatura
    from django.http import JsonResponse

    try:
        viatura = get_object_or_404(Viatura, pk=viatura_id)

        # Buscar a última rodagem finalizada desta viatura
        ultima_rodagem = RodagemViatura.objects.filter(
            viatura=viatura,
            status='FINALIZADA',
            ativo=True
        ).order_by('-data_retorno', '-hora_retorno', '-data_saida', '-hora_saida').first()

        # Se houver última rodagem com KM final, usar esse valor
        # IMPORTANTE: Não usar km_atual da viatura para manter independência do controle de combustível
        if ultima_rodagem and ultima_rodagem.km_final:
            km_sugerido = ultima_rodagem.km_final
        else:
            # Se não houver rodagens anteriores, não sugerir KM (deixar vazio)
            km_sugerido = None

        return JsonResponse({
            'km_sugerido': km_sugerido,
            'tem_rodagens': ultima_rodagem is not None
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def rodagem_encerrar(request, pk):
    """Encerra uma rodagem em andamento"""
    from django.http import JsonResponse
    from datetime import datetime
    import pytz

    rodagem = get_object_or_404(RodagemViatura, pk=pk, status='EM_ANDAMENTO', ativo=True)

    if request.method == 'POST':
        try:
            data_retorno = request.POST.get('data_retorno')
            hora_retorno = request.POST.get('hora_retorno')
            km_final = request.POST.get('km_final')

            if not data_retorno or not hora_retorno or not km_final:
                messages.error(request, 'Todos os campos são obrigatórios!')
                return redirect('militares:rodagem_por_viatura', viatura_id=rodagem.viatura.pk)

            # Validar KM final
            try:
                km_final = int(km_final)
                if km_final < rodagem.km_inicial:
                    messages.error(request, f'O KM final ({km_final}) não pode ser menor que o KM inicial ({rodagem.km_inicial})!')
                    return redirect('militares:rodagem_por_viatura', viatura_id=rodagem.viatura.pk)
            except ValueError:
                messages.error(request, 'KM final inválido!')
                return redirect('militares:rodagem_por_viatura', viatura_id=rodagem.viatura.pk)

            # Atualizar rodagem
            rodagem.data_retorno = datetime.strptime(data_retorno, '%Y-%m-%d').date()
            rodagem.hora_retorno = datetime.strptime(hora_retorno, '%H:%M').time()
            rodagem.km_final = km_final
            rodagem.status = 'FINALIZADA'
            rodagem.save()

            messages.success(request, f'Rodagem encerrada com sucesso! KM rodado: {rodagem.km_rodado} km')

            # Redirecionar para a página de origem (lista geral ou por viatura)
            referer = request.META.get('HTTP_REFERER', '')
            if 'rodagens/' in referer and '/viaturas/' not in referer:
                # Veio da lista geral
                return redirect('militares:rodagem_list')
            else:
                # Veio da página por viatura
                return redirect('militares:rodagem_por_viatura', viatura_id=rodagem.viatura.pk)

        except Exception as e:
            messages.error(request, f'Erro ao encerrar rodagem: {str(e)}')
            return redirect('militares:rodagem_por_viatura', viatura_id=rodagem.viatura.pk)

    return redirect('militares:rodagem_por_viatura', viatura_id=rodagem.viatura.pk)


def rodagem_por_viatura(request, viatura_id):
    """Lista rodagens de uma viatura específica"""
    viatura = get_object_or_404(Viatura, pk=viatura_id)
    
    rodagens = RodagemViatura.objects.filter(
        viatura=viatura,
        ativo=True
    ).select_related(
        'condutor', 'criado_por'
    ).order_by('-data_saida', '-hora_saida')
    
    # Estatísticas
    total_rodagens = rodagens.count()
    total_km_rodados = rodagens.aggregate(Sum('km_rodado'))['km_rodado__sum'] or 0
    rodagens_em_andamento = rodagens.filter(status='EM_ANDAMENTO').count()
    rodagens_finalizadas = rodagens.filter(status='FINALIZADA').count()
    
    # Paginação
    paginator = Paginator(rodagens, 20)
    page_number = request.GET.get('page')
    rodagens_page = paginator.get_page(page_number)
    
    # Obter funções do usuário para assinatura do PDF
    funcoes_usuario = []
    try:
        from .models import UsuarioFuncaoMilitar
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True
        ).select_related('funcao_militar').order_by('-data_inicio')
    except:
        pass
    
    context = {
        'viatura': viatura,
        'rodagens': rodagens_page,
        'total_rodagens': total_rodagens,
        'total_km_rodados': total_km_rodados,
        'rodagens_em_andamento': rodagens_em_andamento,
        'rodagens_finalizadas': rodagens_finalizadas,
        'funcoes_usuario': funcoes_usuario,
    }
    
    return render(request, 'militares/rodagem_por_viatura.html', context)


@login_required
def historico_rodagem_pdf(request, viatura_id):
    """
    Gera PDF do histórico de rodagens com assinatura eletrônica e autenticador de documentos
    """
    import os
    import hashlib
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from datetime import datetime, time
    import pytz
    from django.db import transaction
    
    try:
        viatura = get_object_or_404(Viatura, pk=viatura_id)
        
        # Obter parâmetros
        data_inicio_str = request.GET.get('data_inicio', '')
        data_fim_str = request.GET.get('data_fim', '')
        funcao_assinatura = request.GET.get('funcao_assinatura', '')
        
        if not data_inicio_str or not data_fim_str:
            messages.error(request, 'Período de datas não fornecido.')
            return redirect('militares:rodagem_por_viatura', viatura_id=viatura_id)
        
        try:
            data_inicio_date = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim_date = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de data inválido.')
            return redirect('militares:rodagem_por_viatura', viatura_id=viatura_id)
        
        # Filtrar rodagens pelo período - BUSCAR TODAS AS RODAGENS
        rodagens_queryset = RodagemViatura.objects.filter(
            viatura=viatura
        ).select_related('condutor')
        
        # Filtrar por data início (inclui todos os registros a partir desta data)
        rodagens_queryset = rodagens_queryset.filter(
            data_saida__gte=data_inicio_date
        )
        
        # Filtrar por data fim (inclui todos os registros até esta data)
        rodagens_queryset = rodagens_queryset.filter(
            data_saida__lte=data_fim_date
        )
        
        # Ordenar por data de saída e hora de saída
        rodagens_queryset = rodagens_queryset.order_by('data_saida', 'hora_saida')
        
        # Converter para lista ANTES de qualquer processamento
        rodagens_lista = list(rodagens_queryset.all())
        
        if not rodagens_lista:
            # Retornar página informativa em vez de redirecionar
            url_voltar = reverse('militares:rodagem_por_viatura', args=[viatura_id])
            
            primeiro_rodagem = RodagemViatura.objects.filter(
                viatura=viatura
            ).order_by('data_saida').first()
            
            ultimo_rodagem = RodagemViatura.objects.filter(
                viatura=viatura
            ).order_by('-data_saida').first()
            
            info_periodo = ""
            if primeiro_rodagem and ultimo_rodagem:
                info_periodo = f"""
                    <p><strong>Período das rodagens existentes:</strong></p>
                    <ul>
                        <li>Primeira rodagem: {primeiro_rodagem.data_saida.strftime('%d/%m/%Y')} ({'Ativo' if primeiro_rodagem.ativo else 'Inativo'})</li>
                        <li>Última rodagem: {ultimo_rodagem.data_saida.strftime('%d/%m/%Y')} ({'Ativo' if ultimo_rodagem.ativo else 'Inativo'})</li>
                    </ul>
                """
            
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Nenhuma Rodagem Encontrada</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 50px; }}
                    .info-box {{ border: 2px solid #ffc107; border-radius: 5px; padding: 20px; 
                                max-width: 700px; margin: 0 auto; background-color: #fff3cd; }}
                    h2 {{ color: #856404; }}
                    p {{ color: #856404; }}
                    ul {{ color: #856404; }}
                    .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; 
                           text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="info-box">
                    <h2>⚠️ Nenhuma Rodagem Encontrada</h2>
                    <p><strong>Período selecionado:</strong> {data_inicio_date.strftime('%d/%m/%Y')} a {data_fim_date.strftime('%d/%m/%Y')}</p>
                    <p><strong>Viatura:</strong> {viatura.placa}</p>
                    <hr>
                    {info_periodo if primeiro_rodagem else '<p><em>Nenhuma rodagem registrada para esta viatura.</em></p>'}
                    <div style="text-align: center;">
                        <a href="{url_voltar}" class="btn">Voltar para Rodagens</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HttpResponse(error_html, status=200, content_type='text/html')
        
        # Calcular estatísticas usando a lista completa
        quantidade_rodagens = len(rodagens_lista)
        total_km_rodado = sum(float(r.km_rodado) for r in rodagens_lista if r.km_rodado)
        
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos - seguindo padrão da certidão de férias
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional dinâmico com OM da viatura
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
        ]
        
        # Adicionar OM da viatura (apenas a instância mais específica, sem hierarquia)
        om_viatura = viatura.get_organizacao_instancia()
        if om_viatura and om_viatura != "Não definido":
            cabecalho.append(om_viatura.upper())
        
        # Obter endereço da OM (instância mais específica)
        endereco_om = None
        if viatura.sub_unidade and viatura.sub_unidade.endereco:
            endereco_om = viatura.sub_unidade.endereco
        elif viatura.unidade and viatura.unidade.endereco:
            endereco_om = viatura.unidade.endereco
        elif viatura.grande_comando and viatura.grande_comando.endereco:
            endereco_om = viatura.grande_comando.endereco
        elif viatura.orgao and viatura.orgao.endereco:
            endereco_om = viatura.orgao.endereco
        
        # Adicionar endereço da OM se disponível
        if endereco_om:
            cabecalho.append(endereco_om)
        else:
            # Fallback para endereço padrão se não houver endereço na OM
            cabecalho.append("Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490")
        
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal sublinhado
        story.append(Paragraph("<u>HISTÓRICO DE RODAGENS</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Dados da viatura e período
        viatura_info = f"{viatura.placa}"
        if viatura.prefixo:
            viatura_info += f" - {viatura.prefixo}"
        if viatura.modelo:
            viatura_info += f" ({viatura.marca} {viatura.modelo})" if viatura.marca else f" ({viatura.modelo})"
        
        texto_dados = (
            f"<b>Viatura:</b> {viatura_info}<br/>"
            f"<b>Período:</b> {data_inicio_date.strftime('%d/%m/%Y')} a {data_fim_date.strftime('%d/%m/%Y')}"
        )
        story.append(Paragraph(texto_dados, style_normal))
        story.append(Spacer(1, 15))
        
        # Tabela de rodagens - padrão certidão de férias
        table_data = []
        
        # Cabeçalho com Paragraph
        table_data.append([
            Paragraph('Data Saída', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Hora Saída', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Data Retorno', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Hora Retorno', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('KM Inicial', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('KM Final', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('KM Rodado', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Objetivo', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('Responsável', ParagraphStyle('header', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1)),
        ])
        
        # Processar TODAS as rodagens da lista
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        
        # Iterar sobre TODAS as rodagens e adicionar à tabela
        for rodagem in rodagens_lista:
            data_saida = rodagem.data_saida.strftime("%d/%m/%Y")
            hora_saida = rodagem.hora_saida.strftime("%H:%M") if rodagem.hora_saida else "-"
            
            data_retorno = rodagem.data_retorno.strftime("%d/%m/%Y") if rodagem.data_retorno else "-"
            hora_retorno = rodagem.hora_retorno.strftime("%H:%M") if rodagem.hora_retorno else "-"
            
            km_inicial = str(rodagem.km_inicial) if rodagem.km_inicial else "-"
            km_final = str(rodagem.km_final) if rodagem.km_final else "-"
            km_rodado = str(rodagem.km_rodado) if rodagem.km_rodado else "-"
            
            objetivo = rodagem.get_objetivo_display() if rodagem.objetivo else "-"
            responsavel = f"{rodagem.condutor.get_posto_graduacao_display()} {rodagem.condutor.nome_completo}" if rodagem.condutor else "-"
            
            # Criar cada célula da linha como Paragraph separado
            linha_tabela = [
                Paragraph(str(data_saida), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(hora_saida), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(data_retorno), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(hora_retorno), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(km_inicial), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(km_final), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(km_rodado), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(objetivo), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
                Paragraph(str(responsavel), ParagraphStyle('cell', parent=styles['Normal'], fontSize=8, alignment=1)),
            ]
            
            # Adicionar linha à tabela
            table_data.append(linha_tabela)
        
        # Larguras das colunas (ajustadas para A4)
        col_widths = [2.2*cm, 1.8*cm, 2.2*cm, 1.8*cm, 1.6*cm, 1.6*cm, 1.6*cm, 2.0*cm, 3.2*cm]
        
        # Criar tabela
        rodagens_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        rodagens_table.setStyle(TableStyle([
            # Cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Linhas de dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(rodagens_table)
        story.append(Spacer(1, 20))
        
        # Estatísticas resumo
        texto_estatisticas = (
            f"<b>Total de Rodagens:</b> {quantidade_rodagens} | "
            f"<b>Total de KM Rodados:</b> {total_km_rodado:.0f} km"
        )
        story.append(Paragraph(texto_estatisticas, ParagraphStyle('estatisticas', parent=styles['Normal'], fontSize=11, alignment=1, spaceAfter=20)))
        story.append(Spacer(1, 30))
        
        # Cidade e Data por extenso (centralizada) - padrão certidão de férias
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
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
        
        # Obter função do formulário ou função atual
        if not funcao_assinatura:
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_assinatura = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta) - padrão certidão
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Adicionar espaço para assinatura física
                story.append(Spacer(1, 1*cm))
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                story.append(Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                
                # 2ª linha: Função
                story.append(Paragraph(funcao_assinatura, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                story.append(Spacer(1, 1*cm))
                story.append(Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5)))
                story.append(Paragraph(funcao_assinatura, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo - padrão certidão
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                funcao_display = funcao_assinatura
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_assinatura
            
            # Data e hora da assinatura
            agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M')
            
            texto_assinatura = f"Documento assinado eletronicamente por {nome_posto_quadro} - {funcao_display}, em {data_formatada}, às {hora_formatada}, conforme horário oficial de Brasília, conforme portaria comando geral nº59/2020 publicada em boletim geral nº26/2020"
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
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
        except Exception as e:
            # Se houver erro na assinatura, continuar sem ela
            pass
        
        # Adicionar autenticador de documentos ANTES de construir o PDF
        # Espaçamento de 0,10cm entre assinatura e autenticador
        story.append(Spacer(1, 0.10*cm))
        
        # Criar um objeto fake para o histórico (será usado pelo autenticador)
        class HistoricoFake:
            def __init__(self, viatura_id, data_inicio_date, data_fim_date):
                # Criar um ID único baseado nos parâmetros
                data_inicio_str = data_inicio_date.strftime('%Y-%m-%d')
                data_fim_str = data_fim_date.strftime('%Y-%m-%d')
                self.id = f"historico_rodagem_{viatura_id}_{data_inicio_str}_{data_fim_str}"
                # Gerar um PK numérico baseado no hash dos parâmetros
                hash_valor = abs(hash(f"{viatura_id}_{data_inicio_str}_{data_fim_str}"))
                self.pk = hash_valor % 100000000  # PK numérico de até 8 dígitos
                self.tipo_documento = 'historico_rodagem'
        
        historico_fake = HistoricoFake(viatura_id, data_inicio_date, data_fim_date)
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        autenticador = gerar_autenticador_veracidade(historico_fake, request, tipo_documento='historico_rodagem')
        
        # Tabela do rodapé: QR Code + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
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
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        # Preparar resposta
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="historico_rodagens_{viatura.placa}_{data_inicio_date.strftime("%Y%m%d")}_a_{data_fim_date.strftime("%Y%m%d")}.pdf"'
        
        return response
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        # Log do erro completo para debug
        print(f"ERRO ao gerar PDF do histórico de rodagens: {str(e)}")
        print(f"Traceback completo:\n{error_traceback}")
        
        # Retornar página de erro em vez de redirecionar
        url_voltar = reverse('militares:rodagem_por_viatura', args=[viatura_id])
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF Histórico de Rodagens</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 600px; margin: 0 auto; background-color: #f8d7da; text-align: left; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                pre {{ background-color: #fff; padding: 10px; border-radius: 3px; overflow-x: auto; font-size: 11px; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; 
                       text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .btn:hover {{ background-color: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF do Histórico de Rodagens</h2>
                <p><strong>Ocorreu um erro ao gerar o PDF:</strong></p>
                <p><code>{str(e)}</code></p>
                <details>
                    <summary style="cursor: pointer; color: #721c24; margin-top: 10px;"><strong>Detalhes do Erro (clique para expandir)</strong></summary>
                    <pre>{error_traceback}</pre>
                </details>
                <div style="text-align: center;">
                    <a href="{url_voltar}" class="btn">Voltar para Rodagens</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


def painel_guarda_login(request):
    """
    Página pública de login para acessar o painel de guarda
    Após login, redireciona para o painel em tela cheia
    """
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    
    # Se já está autenticado e autorizado, redirecionar direto para o painel
    if request.user.is_authenticated and request.session.get('painel_guarda_authorized', False):
        return redirect('militares:painel_guarda')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Marcar como autorizado na sessão
                    request.session['painel_guarda_authorized'] = True
                    # Redirecionar para o painel
                    return redirect('militares:painel_guarda')
                else:
                    messages.error(request, 'Sua conta está desativada.')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    return render(request, 'militares/painel_guarda_login.html')


def painel_guarda(request):
    """
    Painel em tela cheia para controle de entrada e saída na guarda
    Mostra viaturas fora (em andamento) e viaturas no pátio
    Login integrado na própria página
    Filtra automaticamente por unidade do militar logado e mesmo endereço
    """
    from datetime import datetime
    import pytz
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    from .permissoes_hierarquicas import obter_funcao_militar_ativa
    
    # Se não está autenticado, mostrar página de login
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if username and password:
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        # Redirecionar para a mesma página (agora autenticado)
                        return redirect('militares:painel_guarda')
                    else:
                        messages.error(request, 'Sua conta está desativada.')
                else:
                    messages.error(request, 'Usuário ou senha incorretos.')
            else:
                messages.error(request, 'Por favor, preencha todos os campos.')
        
        # Renderizar página de login
        return render(request, 'militares/painel_guarda.html', {'show_login': True})
    
    # Buscar todas as viaturas ativas
    viaturas = Viatura.objects.filter(ativo=True).select_related(
        'unidade', 'sub_unidade', 'grande_comando', 'orgao'
    )
    
    # Se for superusuário, mostrar todas as viaturas sem filtro
    if request.user.is_superuser:
        # Não aplicar nenhum filtro - mostrar todas as viaturas
        pass
    else:
        # Obter a lotação atual do militar do usuário logado
        unidade_usuario = None
        endereco_usuario = None
        
        if hasattr(request.user, 'militar') and request.user.militar:
            # Buscar lotação atual do militar
            lotacao_atual = request.user.militar.lotacoes.filter(status='ATUAL', ativo=True).first()
            
            if lotacao_atual:
                # Priorizar sub_unidade, depois unidade da lotação
                if lotacao_atual.sub_unidade:
                    unidade_usuario = lotacao_atual.sub_unidade.unidade
                    endereco_usuario = lotacao_atual.sub_unidade.endereco or unidade_usuario.endereco if unidade_usuario else None
                elif lotacao_atual.unidade:
                    unidade_usuario = lotacao_atual.unidade
                    endereco_usuario = lotacao_atual.unidade.endereco
        
        # Aplicar filtro automático baseado na unidade e endereço do usuário
        if unidade_usuario:
            if endereco_usuario and endereco_usuario.strip():
                # Normalizar endereço para comparação (remover espaços extras)
                endereco_usuario_normalizado = endereco_usuario.strip()
                
                # Filtrar viaturas que estão em unidades ou sub_unidades com o mesmo endereço
                # Usar __icontains para ser mais flexível na comparação
                # A viatura pode estar:
                # 1. Diretamente em uma unidade com o mesmo endereço
                # 2. Em uma sub_unidade que tem o mesmo endereço
                # 3. Em uma sub_unidade cuja unidade pai tem o mesmo endereço
                # Também incluir viaturas sem endereço cadastrado na mesma unidade
                viaturas = viaturas.filter(
                    Q(unidade=unidade_usuario, unidade__ativo=True) |  # Mesma unidade (independente de endereço)
                    Q(sub_unidade__unidade=unidade_usuario, sub_unidade__unidade__ativo=True, sub_unidade__ativo=True) |  # Sub-unidade da mesma unidade
                    Q(unidade__endereco__icontains=endereco_usuario_normalizado, unidade__ativo=True, unidade__endereco__isnull=False) |  # Unidade direta com mesmo endereço
                    Q(sub_unidade__endereco__icontains=endereco_usuario_normalizado, sub_unidade__ativo=True, sub_unidade__endereco__isnull=False) |  # Sub-unidade com mesmo endereço
                    Q(sub_unidade__unidade__endereco__icontains=endereco_usuario_normalizado, sub_unidade__unidade__ativo=True, sub_unidade__unidade__endereco__isnull=False, sub_unidade__ativo=True)  # Sub-unidade cuja unidade pai tem mesmo endereço
                )
            else:
                # Se não houver endereço, filtrar apenas pela unidade específica
                viaturas = viaturas.filter(
                    Q(unidade=unidade_usuario, unidade__ativo=True) | 
                    Q(sub_unidade__unidade=unidade_usuario, sub_unidade__unidade__ativo=True, sub_unidade__ativo=True)
                )
        else:
            # Se não houver unidade cadastrada, não mostrar nenhuma viatura
            # (usuário precisa ter unidade associada para ver viaturas)
            viaturas = viaturas.none()
    
    # Continuar apenas se houver viaturas (ou se for superusuário)
    if not request.user.is_superuser and not viaturas.exists():
        # Se não há viaturas e não é superusuário, mostrar mensagem
        pass
    
    viaturas = viaturas.order_by('placa')
    
    # Buscar rodagens em andamento apenas das viaturas filtradas
    viatura_ids = list(viaturas.values_list('id', flat=True))
    rodagens_em_andamento = RodagemViatura.objects.filter(
        status='EM_ANDAMENTO',
        ativo=True,
        viatura_id__in=viatura_ids
    ).select_related('viatura', 'condutor').order_by('-data_saida', '-hora_saida')
    
    # Criar dicionário de rodagens por viatura
    rodagens_por_viatura = {}
    for rodagem in rodagens_em_andamento:
        rodagens_por_viatura[rodagem.viatura_id] = rodagem
    
    # Separar viaturas
    viaturas_fora = []
    viaturas_no_patio = []
    
    for viatura in viaturas:
        if viatura.id in rodagens_por_viatura:
            # Viatura está fora
            rodagem = rodagens_por_viatura[viatura.id]
            viaturas_fora.append({
                'viatura': viatura,
                'rodagem': rodagem,
                'tempo_fora': calcular_tempo_fora(rodagem)
            })
        else:
            # Viatura está no pátio
            viaturas_no_patio.append(viatura)
    
    # Ordenar viaturas fora por data/hora de saída (mais recentes primeiro)
    viaturas_fora.sort(key=lambda x: (
        x['rodagem'].data_saida,
        x['rodagem'].hora_saida
    ), reverse=True)
    
    # Estatísticas
    total_viaturas = viaturas.count()
    total_fora = len(viaturas_fora)
    total_no_patio = len(viaturas_no_patio)
    
    # Data/hora atual
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
    
    # Informações da unidade do usuário para exibição
    unidade_info = None
    if request.user.is_superuser:
        unidade_info = {
            'nome': 'Superusuário',
            'endereco': None,
            'total_unidades': 'Todas',
            'unidades': [],
        }
    elif unidade_usuario:
        if endereco_usuario:
            unidades_no_endereco = Unidade.objects.filter(
                endereco__iexact=endereco_usuario,
                ativo=True
            ).order_by('nome')
            total_unidades = unidades_no_endereco.count()
        else:
            unidades_no_endereco = [unidade_usuario]
            total_unidades = 1
        
        unidade_info = {
            'nome': unidade_usuario.nome,
            'endereco': endereco_usuario,
            'total_unidades': total_unidades,
            'unidades': unidades_no_endereco,
        }
    
    # Informações do militar logado
    militar_info = None
    if hasattr(request.user, 'militar') and request.user.militar:
        militar_info = {
            'posto': request.user.militar.get_posto_graduacao_display(),
            'nome_guerra': request.user.militar.nome_guerra,
        }
    
    context = {
        'viaturas_fora': viaturas_fora,
        'viaturas_no_patio': viaturas_no_patio,
        'total_viaturas': total_viaturas,
        'total_fora': total_fora,
        'total_no_patio': total_no_patio,
        'data_hora_atual': agora,
        'show_login': False,
        'unidade_info': unidade_info,
        'militar_info': militar_info,
    }
    
    return render(request, 'militares/painel_guarda.html', context)


def calcular_tempo_fora(rodagem):
    """Calcula o tempo que a viatura está fora"""
    from datetime import datetime, timedelta
    import pytz
    
    try:
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        # Combinar data e hora de saída
        data_saida = rodagem.data_saida
        hora_saida = rodagem.hora_saida
        
        # Criar datetime de saída
        if isinstance(data_saida, str):
            data_saida = datetime.strptime(data_saida, '%Y-%m-%d').date()
        if isinstance(hora_saida, str):
            hora_saida = datetime.strptime(hora_saida, '%H:%M:%S').time()
        
        saida_datetime = brasilia_tz.localize(
            datetime.combine(data_saida, hora_saida)
        )
        
        # Calcular diferença
        diferenca = agora - saida_datetime
        
        # Formatar tempo
        horas = diferenca.total_seconds() // 3600
        minutos = (diferenca.total_seconds() % 3600) // 60
        
        if horas > 0:
            return f"{int(horas)}h {int(minutos)}min"
        else:
            return f"{int(minutos)}min"
    except Exception as e:
        return "N/A"


@login_required
def painel_guarda_ajax(request):
    """
    Endpoint AJAX para buscar dados atualizados do painel de guarda
    Retorna JSON com viaturas fora e no pátio
    Aplica filtro automático baseado na unidade do usuário logado
    """
    from datetime import datetime
    import pytz
    from .permissoes_hierarquicas import obter_funcao_militar_ativa
    
    try:
        # Buscar todas as viaturas ativas
        viaturas = Viatura.objects.filter(ativo=True).select_related(
            'unidade', 'sub_unidade', 'grande_comando', 'orgao'
        )
        
        # Se for superusuário, mostrar todas as viaturas sem filtro
        if request.user.is_superuser:
            # Não aplicar nenhum filtro - mostrar todas as viaturas
            pass
        else:
            # Obter a lotação atual do militar do usuário logado
            unidade_usuario = None
            endereco_usuario = None
            
            if hasattr(request.user, 'militar') and request.user.militar:
                # Buscar lotação atual do militar
                lotacao_atual = request.user.militar.lotacoes.filter(status='ATUAL', ativo=True).first()
                
                if lotacao_atual:
                    # Priorizar sub_unidade, depois unidade da lotação
                    if lotacao_atual.sub_unidade:
                        unidade_usuario = lotacao_atual.sub_unidade.unidade
                        endereco_usuario = lotacao_atual.sub_unidade.endereco or unidade_usuario.endereco if unidade_usuario else None
                    elif lotacao_atual.unidade:
                        unidade_usuario = lotacao_atual.unidade
                        endereco_usuario = lotacao_atual.unidade.endereco
            
            # Aplicar filtro automático baseado na unidade e endereço do usuário
            if unidade_usuario:
                if endereco_usuario and endereco_usuario.strip():
                    # Normalizar endereço para comparação (remover espaços extras)
                    endereco_usuario_normalizado = endereco_usuario.strip()
                    
                    # Filtrar viaturas que estão em unidades ou sub_unidades com o mesmo endereço
                    # Usar __icontains para ser mais flexível na comparação
                    # A viatura pode estar:
                    # 1. Diretamente em uma unidade com o mesmo endereço
                    # 2. Em uma sub_unidade que tem o mesmo endereço
                    # 3. Em uma sub_unidade cuja unidade pai tem o mesmo endereço
                    # Também incluir viaturas sem endereço cadastrado na mesma unidade
                    viaturas = viaturas.filter(
                        Q(unidade=unidade_usuario, unidade__ativo=True) |  # Mesma unidade (independente de endereço)
                        Q(sub_unidade__unidade=unidade_usuario, sub_unidade__unidade__ativo=True, sub_unidade__ativo=True) |  # Sub-unidade da mesma unidade
                        Q(unidade__endereco__icontains=endereco_usuario_normalizado, unidade__ativo=True, unidade__endereco__isnull=False) |  # Unidade direta com mesmo endereço
                        Q(sub_unidade__endereco__icontains=endereco_usuario_normalizado, sub_unidade__ativo=True, sub_unidade__endereco__isnull=False) |  # Sub-unidade com mesmo endereço
                        Q(sub_unidade__unidade__endereco__icontains=endereco_usuario_normalizado, sub_unidade__unidade__ativo=True, sub_unidade__unidade__endereco__isnull=False, sub_unidade__ativo=True)  # Sub-unidade cuja unidade pai tem mesmo endereço
                    )
                else:
                    # Se não houver endereço, filtrar apenas pela unidade específica
                    viaturas = viaturas.filter(
                        Q(unidade=unidade_usuario, unidade__ativo=True) | 
                        Q(sub_unidade__unidade=unidade_usuario, sub_unidade__unidade__ativo=True, sub_unidade__ativo=True)
                    )
            else:
                # Se não houver unidade cadastrada, não mostrar nenhuma viatura
                viaturas = viaturas.none()
        
        viaturas = viaturas.order_by('placa')
        
        # Buscar rodagens em andamento apenas das viaturas filtradas
        viatura_ids = list(viaturas.values_list('id', flat=True))
        rodagens_em_andamento = RodagemViatura.objects.filter(
            status='EM_ANDAMENTO',
            ativo=True,
            viatura_id__in=viatura_ids
        ).select_related('viatura', 'condutor').order_by('-data_saida', '-hora_saida')
        
        # Criar dicionário de rodagens por viatura
        rodagens_por_viatura = {}
        for rodagem in rodagens_em_andamento:
            rodagens_por_viatura[rodagem.viatura_id] = rodagem
        
        # Separar viaturas
        viaturas_fora = []
        viaturas_no_patio = []
        
        for viatura in viaturas:
            if viatura.id in rodagens_por_viatura:
                # Viatura está fora
                rodagem = rodagens_por_viatura[viatura.id]
                tempo_fora = calcular_tempo_fora(rodagem)
                viaturas_fora.append({
                    'viatura_id': viatura.id,
                    'placa': viatura.placa,
                    'prefixo': viatura.prefixo or '',
                    'marca': viatura.marca or '',
                    'modelo': viatura.modelo or '',
                    'tipo': viatura.get_tipo_display() if viatura.tipo else '',
                    'data_saida': rodagem.data_saida.strftime('%d/%m/%Y'),
                    'hora_saida': rodagem.hora_saida.strftime('%H:%M'),
                    'condutor_nome': f"{rodagem.condutor.get_posto_graduacao_display()} {rodagem.condutor.nome_completo}" if rodagem.condutor else '',
                    'destino': rodagem.destino or '',
                    'objetivo': rodagem.get_objetivo_display(),
                    'km_inicial': str(rodagem.km_inicial) if rodagem.km_inicial else '',
                    'tempo_fora': tempo_fora,
                })
            else:
                # Viatura está no pátio
                viaturas_no_patio.append({
                    'viatura_id': viatura.id,
                    'placa': viatura.placa,
                    'prefixo': viatura.prefixo or '',
                    'marca': viatura.marca or '',
                    'modelo': viatura.modelo or '',
                    'tipo': viatura.get_tipo_display() if viatura.tipo else '',
                    'ano_fabricacao': str(viatura.ano_fabricacao) if viatura.ano_fabricacao else '',
                    'ano_modelo': str(viatura.ano_modelo) if viatura.ano_modelo else '',
                    'km_atual': str(viatura.km_atual) if viatura.km_atual else '',
                    'status': viatura.get_status_display() if viatura.status else '',
                    'combustivel': viatura.get_combustivel_display() if viatura.combustivel else '',
                })
        
        # Ordenar viaturas fora por data/hora de saída (mais recentes primeiro)
        # Converter para formato comparável primeiro
        from datetime import datetime
        def sort_key(v):
            try:
                data = datetime.strptime(v['data_saida'], '%d/%m/%Y')
                hora_parts = v['hora_saida'].split(':')
                hora = datetime.combine(data.date(), datetime.min.time().replace(
                    hour=int(hora_parts[0]), 
                    minute=int(hora_parts[1])
                ))
                return hora
            except:
                return datetime.min
        viaturas_fora.sort(key=sort_key, reverse=True)
        
        # Estatísticas
        total_viaturas = viaturas.count()
        total_fora = len(viaturas_fora)
        total_no_patio = len(viaturas_no_patio)
        
        return JsonResponse({
            'success': True,
            'total_viaturas': total_viaturas,
            'total_fora': total_fora,
            'total_no_patio': total_no_patio,
            'viaturas_fora': viaturas_fora,
            'viaturas_no_patio': viaturas_no_patio,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def painel_guarda_enderecos_ajax(request):
    """
    Endpoint AJAX para buscar endereços baseados na cidade selecionada
    """
    try:
        cidade = request.GET.get('cidade', '')
        
        if not cidade:
            return JsonResponse({
                'success': True,
                'enderecos': []
            })
        
        # Buscar endereços únicos das unidades na cidade
        enderecos_unidades = Unidade.objects.filter(
            cidade=cidade, 
            ativo=True, 
            endereco__isnull=False
        ).exclude(endereco='').values_list('endereco', flat=True).distinct()
        
        enderecos = [{'value': end, 'label': end} for end in sorted(enderecos_unidades)]
        
        return JsonResponse({
            'success': True,
            'enderecos': enderecos
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def painel_guarda_unidades_ajax(request):
    """
    Endpoint AJAX para buscar unidades baseadas na cidade e endereço selecionados
    """
    try:
        cidade = request.GET.get('cidade', '')
        endereco = request.GET.get('endereco', '')
        
        unidades_query = Unidade.objects.filter(ativo=True)
        
        if cidade:
            unidades_query = unidades_query.filter(cidade=cidade)
        
        if endereco:
            unidades_query = unidades_query.filter(endereco__icontains=endereco)
        
        unidades = unidades_query.order_by('nome')
        
        unidades_list = [{'id': un.id, 'nome': un.nome, 'sigla': un.sigla or ''} for un in unidades]
        
        return JsonResponse({
            'success': True,
            'unidades': unidades_list
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
