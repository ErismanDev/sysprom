"""
Views para o módulo de Equipamentos Operacionais
Gerencia o cadastro e controle de equipamentos operacionais do CBMEPI
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.template.loader import render_to_string
from django.forms.models import model_to_dict
from decimal import Decimal

from .models import (
    EquipamentoOperacional, TempoUsoEquipamento, TransferenciaEquipamento,
    HistoricoAlteracaoEquipamento, Orgao, GrandeComando, Unidade, SubUnidade,
    AbastecimentoEquipamento, ManutencaoEquipamento, TrocaOleoEquipamento
)
from .forms import (
    EquipamentoOperacionalForm, TempoUsoEquipamentoForm, EquipamentoTransferenciaForm,
    AbastecimentoEquipamentoForm, ManutencaoEquipamentoForm, TrocaOleoEquipamentoForm
)


@login_required
def equipamento_operacional_list(request):
    """Lista todos os equipamentos operacionais com modais"""
    equipamentos = EquipamentoOperacional.objects.select_related(
        'orgao', 'grande_comando', 'unidade', 'sub_unidade', 'criado_por'
    ).order_by('codigo')
    
    # Filtros
    search = request.GET.get('search', '')
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    organizacao = request.GET.get('organizacao', '')
    ativo = request.GET.get('ativo', '')
    
    if search:
        equipamentos = equipamentos.filter(
            Q(codigo__icontains=search) |
            Q(marca__icontains=search) |
            Q(modelo__icontains=search) |
            Q(numero_serie__icontains=search)
        )
    
    if tipo:
        equipamentos = equipamentos.filter(tipo=tipo)
    
    if status:
        equipamentos = equipamentos.filter(status=status)
    
    if organizacao:
        equipamentos = equipamentos.filter(
            Q(orgao_id=organizacao) |
            Q(grande_comando_id=organizacao) |
            Q(unidade_id=organizacao) |
            Q(sub_unidade_id=organizacao)
        )
    
    if ativo == '1':
        equipamentos = equipamentos.filter(ativo=True)
    elif ativo == '0':
        equipamentos = equipamentos.filter(ativo=False)
    
    # Paginação
    paginator = Paginator(equipamentos, 20)
    page = request.GET.get('page')
    equipamentos = paginator.get_page(page)
    
    # Estatísticas
    total_equipamentos = EquipamentoOperacional.objects.count()
    equipamentos_disponiveis = EquipamentoOperacional.objects.filter(status='DISPONIVEL', ativo=True).count()
    equipamentos_em_uso = EquipamentoOperacional.objects.filter(status='EM_USO', ativo=True).count()
    equipamentos_manutencao = EquipamentoOperacional.objects.filter(status='MANUTENCAO', ativo=True).count()
    
    # Listas para filtros
    tipos = EquipamentoOperacional.TIPO_CHOICES
    status_list = EquipamentoOperacional.STATUS_CHOICES
    
    # Lista de organizações para filtro
    organizacoes = []
    organizacoes.extend([(o.id, f"Órgão: {o.nome}") for o in Orgao.objects.filter(ativo=True).order_by('nome')])
    organizacoes.extend([(gc.id, f"GC: {gc.nome}") for gc in GrandeComando.objects.filter(ativo=True).order_by('nome')])
    organizacoes.extend([(u.id, f"Unidade: {u.nome}") for u in Unidade.objects.filter(ativo=True).order_by('nome')])
    organizacoes.extend([(su.id, f"Sub-Unidade: {su.nome}") for su in SubUnidade.objects.filter(ativo=True).order_by('nome')])
    
    context = {
        'equipamentos': equipamentos,
        'search': search,
        'tipo': tipo,
        'status': status,
        'organizacao': organizacao,
        'ativo': ativo,
        'total_equipamentos': total_equipamentos,
        'equipamentos_disponiveis': equipamentos_disponiveis,
        'equipamentos_em_uso': equipamentos_em_uso,
        'equipamentos_manutencao': equipamentos_manutencao,
        'tipos': tipos,
        'status_list': status_list,
        'organizacoes': organizacoes,
    }
    
    return render(request, 'militares/equipamento_operacional_list.html', context)


@login_required
def equipamento_operacional_create(request):
    """Cria novo equipamento operacional via modal"""
    if request.method == 'POST':
        form = EquipamentoOperacionalForm(request.POST, request=request)
        if form.is_valid():
            with transaction.atomic():
                equipamento = form.save(commit=False)
                
                # Processar seleção do organograma se fornecido
                organograma_id = request.POST.get('organograma-select', '')
                if organograma_id:
                    _processar_organograma(equipamento, organograma_id)
                
                equipamento.criado_por = request.user
                equipamento.save()
                
                # Registrar histórico
                HistoricoAlteracaoEquipamento.objects.create(
                    equipamento=equipamento,
                    alterado_por=request.user,
                    campo_alterado='Criação',
                    valor_anterior='',
                    valor_novo=f'Equipamento criado: {equipamento.codigo}'
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'Equipamento {equipamento.codigo} cadastrado com sucesso!',
                    'redirect': reverse('militares:equipamento_operacional_list')
                })
            messages.success(request, f'Equipamento {equipamento.codigo} cadastrado com sucesso!')
            return redirect('militares:equipamento_operacional_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/equipamento_operacional_form_modal.html', {
                    'form': form,
                    'is_create': True
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = EquipamentoOperacionalForm(request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/equipamento_operacional_form_modal.html', {
            'form': form,
            'is_create': True
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/equipamento_operacional_form_modal.html', {
        'form': form,
        'is_create': True
    })


@login_required
def equipamento_operacional_update(request, pk):
    """Atualiza equipamento operacional via modal"""
    equipamento = get_object_or_404(EquipamentoOperacional, pk=pk)
    
    if request.method == 'POST':
        form = EquipamentoOperacionalForm(request.POST, instance=equipamento, request=request)
        if form.is_valid():
            with transaction.atomic():
                # Registrar alterações antes de salvar
                alteracoes = _registrar_alteracoes(equipamento, form, request.user)
                
                equipamento_atualizado = form.save(commit=False)
                
                # Processar seleção do organograma se fornecido
                organograma_id = request.POST.get('organograma-select', '')
                if organograma_id:
                    _processar_organograma(equipamento_atualizado, organograma_id)
                
                equipamento_atualizado.save()
                
                # Registrar histórico de alterações
                for campo, valor_anterior, valor_novo in alteracoes:
                    HistoricoAlteracaoEquipamento.objects.create(
                        equipamento=equipamento_atualizado,
                        alterado_por=request.user,
                        campo_alterado=campo,
                        valor_anterior=valor_anterior,
                        valor_novo=valor_novo
                    )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'Equipamento {equipamento.codigo} atualizado com sucesso!',
                    'redirect': reverse('militares:equipamento_operacional_list')
                })
            messages.success(request, f'Equipamento {equipamento.codigo} atualizado com sucesso!')
            return redirect('militares:equipamento_operacional_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/equipamento_operacional_form_modal.html', {
                    'form': form,
                    'equipamento': equipamento,
                    'is_create': False
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = EquipamentoOperacionalForm(instance=equipamento, request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/equipamento_operacional_form_modal.html', {
            'form': form,
            'equipamento': equipamento,
            'is_create': False
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/equipamento_operacional_form_modal.html', {
        'form': form,
        'equipamento': equipamento,
        'is_create': False
    })


@login_required
def equipamento_operacional_detail(request, pk):
    """Visualiza detalhes de um equipamento operacional via modal"""
    equipamento = get_object_or_404(EquipamentoOperacional, pk=pk)
    
    # Estatísticas de tempo de uso
    tempos_uso = TempoUsoEquipamento.objects.filter(equipamento=equipamento, ativo=True)
    total_tempos_uso = tempos_uso.count()
    
    # Total de horas usadas
    total_horas_usadas = tempos_uso.aggregate(Sum('horas_usadas'))['horas_usadas__sum']
    total_horas_usadas = float(total_horas_usadas) if total_horas_usadas else 0.0
    
    # Últimos tempos de uso
    ultimos_tempos_uso = tempos_uso.order_by('-data_inicio', '-hora_inicio')[:10]
    
    # Histórico de alterações
    historico = HistoricoAlteracaoEquipamento.objects.filter(equipamento=equipamento).order_by('-data_alteracao')[:20]
    
    # Transferências
    transferencias = TransferenciaEquipamento.objects.filter(equipamento=equipamento).order_by('-data_transferencia')
    
    context = {
        'equipamento': equipamento,
        'total_tempos_uso': total_tempos_uso,
        'total_horas_usadas': total_horas_usadas,
        'ultimos_tempos_uso': ultimos_tempos_uso,
        'historico': historico,
        'transferencias': transferencias,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/equipamento_operacional_detail_modal.html', context, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/equipamento_operacional_detail_modal.html', context)


@login_required
@require_http_methods(["POST"])
def equipamento_operacional_delete(request, pk):
    """Exclui equipamento operacional via modal"""
    equipamento = get_object_or_404(EquipamentoOperacional, pk=pk)
    codigo = equipamento.codigo
    
    try:
        equipamento.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Equipamento {codigo} excluído com sucesso!'
            })
        messages.success(request, f'Equipamento {codigo} excluído com sucesso!')
        return redirect('militares:equipamento_operacional_list')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao excluir equipamento: {str(e)}'
            }, status=400)
        messages.error(request, f'Erro ao excluir equipamento: {str(e)}')
        return redirect('militares:equipamento_operacional_list')


@login_required
def tempo_uso_por_equipamento(request, equipamento_id):
    """Lista tempos de uso de um equipamento específico"""
    equipamento = get_object_or_404(EquipamentoOperacional, pk=equipamento_id)
    tempos_uso = TempoUsoEquipamento.objects.filter(
        equipamento=equipamento,
        ativo=True
    ).select_related('operador', 'criado_por').order_by('-data_inicio', '-hora_inicio')
    
    # Paginação
    paginator = Paginator(tempos_uso, 20)
    page = request.GET.get('page')
    tempos_uso = paginator.get_page(page)
    
    context = {
        'equipamento': equipamento,
        'tempos_uso': tempos_uso,
    }
    
    return render(request, 'militares/tempo_uso_por_equipamento.html', context)


@login_required
def tempo_uso_create(request, equipamento_id=None):
    """Cria novo tempo de uso via modal"""
    if request.method == 'POST':
        form = TempoUsoEquipamentoForm(request.POST, request=request, equipamento_id=equipamento_id)
        if form.is_valid():
            tempo_uso = form.save(commit=False)
            tempo_uso.criado_por = request.user
            tempo_uso.save()
            
            # Atualizar status do equipamento se estiver em uso
            if tempo_uso.status == 'EM_ANDAMENTO':
                tempo_uso.equipamento.status = 'EM_USO'
                tempo_uso.equipamento.save(update_fields=['status'])
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Tempo de uso registrado com sucesso!',
                    'redirect': reverse('militares:tempo_uso_por_equipamento', args=[tempo_uso.equipamento.pk])
                })
            messages.success(request, 'Tempo de uso registrado com sucesso!')
            return redirect('militares:tempo_uso_por_equipamento', equipamento_id=tempo_uso.equipamento.pk)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/tempo_uso_form_modal.html', {
                    'form': form,
                    'is_create': True,
                    'equipamento_id': equipamento_id
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
    else:
        form = TempoUsoEquipamentoForm(request=request, equipamento_id=equipamento_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/tempo_uso_form_modal.html', {
            'form': form,
            'is_create': True,
            'equipamento_id': equipamento_id
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/tempo_uso_form_modal.html', {
        'form': form,
        'is_create': True,
        'equipamento_id': equipamento_id
    })


@login_required
def tempo_uso_update(request, pk):
    """Atualiza tempo de uso via modal"""
    tempo_uso = get_object_or_404(TempoUsoEquipamento, pk=pk)
    
    if request.method == 'POST':
        form = TempoUsoEquipamentoForm(request.POST, instance=tempo_uso, request=request)
        if form.is_valid():
            tempo_uso_atualizado = form.save()
            
            # Atualizar status do equipamento
            if tempo_uso_atualizado.status == 'FINALIZADA':
                tempo_uso_atualizado.equipamento.status = 'DISPONIVEL'
                tempo_uso_atualizado.equipamento.save(update_fields=['status'])
            elif tempo_uso_atualizado.status == 'EM_ANDAMENTO':
                tempo_uso_atualizado.equipamento.status = 'EM_USO'
                tempo_uso_atualizado.equipamento.save(update_fields=['status'])
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Tempo de uso atualizado com sucesso!',
                    'redirect': reverse('militares:tempo_uso_por_equipamento', args=[tempo_uso.equipamento.pk])
                })
            messages.success(request, 'Tempo de uso atualizado com sucesso!')
            return redirect('militares:tempo_uso_por_equipamento', equipamento_id=tempo_uso.equipamento.pk)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                html = render_to_string('militares/tempo_uso_form_modal.html', {
                    'form': form,
                    'tempo_uso': tempo_uso,
                    'is_create': False
                }, request=request)
                return JsonResponse({'status': 'error', 'message': 'Erro de validação', 'html': html}, status=400)
    else:
        form = TempoUsoEquipamentoForm(instance=tempo_uso, request=request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('militares/tempo_uso_form_modal.html', {
            'form': form,
            'tempo_uso': tempo_uso,
            'is_create': False
        }, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/tempo_uso_form_modal.html', {
        'form': form,
        'tempo_uso': tempo_uso,
        'is_create': False
    })


@login_required
@require_http_methods(["POST"])
def tempo_uso_delete(request, pk):
    """Exclui tempo de uso via modal"""
    tempo_uso = get_object_or_404(TempoUsoEquipamento, pk=pk)
    equipamento_id = tempo_uso.equipamento.pk
    
    try:
        tempo_uso.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Tempo de uso excluído com sucesso!'
            })
        messages.success(request, 'Tempo de uso excluído com sucesso!')
        return redirect('militares:tempo_uso_por_equipamento', equipamento_id=equipamento_id)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao excluir tempo de uso: {str(e)}'
            }, status=400)
        messages.error(request, f'Erro ao excluir tempo de uso: {str(e)}')
        return redirect('militares:tempo_uso_por_equipamento', equipamento_id=equipamento_id)


@login_required
def equipamento_ultimas_horas(request, equipamento_id):
    """Retorna as últimas horas de uso de um equipamento (AJAX)"""
    equipamento = get_object_or_404(EquipamentoOperacional, pk=equipamento_id)
    
    ultimo_tempo_uso = TempoUsoEquipamento.objects.filter(
        equipamento=equipamento,
        ativo=True,
        status='FINALIZADA'
    ).order_by('-data_fim', '-hora_fim').first()
    
    if ultimo_tempo_uso and ultimo_tempo_uso.horas_final:
        return JsonResponse({
            'horas': float(ultimo_tempo_uso.horas_final),
            'data': ultimo_tempo_uso.data_fim.strftime('%d/%m/%Y') if ultimo_tempo_uso.data_fim else ''
        })
    
    return JsonResponse({
        'horas': float(equipamento.horas_uso),
        'data': ''
    })


# Funções auxiliares

def _processar_organograma(equipamento, organograma_id):
    """Processa a seleção do organograma e preenche os campos de organização"""
    if organograma_id.startswith('orgao_'):
        orgao_id = int(organograma_id.split('_')[1])
        equipamento.orgao = get_object_or_404(Orgao, pk=orgao_id)
        equipamento.grande_comando = None
        equipamento.unidade = None
        equipamento.sub_unidade = None
    elif organograma_id.startswith('gc_'):
        gc_id = int(organograma_id.split('_')[1])
        gc = get_object_or_404(GrandeComando, pk=gc_id)
        equipamento.orgao = gc.orgao
        equipamento.grande_comando = gc
        equipamento.unidade = None
        equipamento.sub_unidade = None
    elif organograma_id.startswith('unidade_'):
        unidade_id = int(organograma_id.split('_')[1])
        unidade = get_object_or_404(Unidade, pk=unidade_id)
        equipamento.orgao = unidade.grande_comando.orgao
        equipamento.grande_comando = unidade.grande_comando
        equipamento.unidade = unidade
        equipamento.sub_unidade = None
    elif organograma_id.startswith('sub_'):
        sub_id = int(organograma_id.split('_')[1])
        sub = get_object_or_404(SubUnidade, pk=sub_id)
        equipamento.orgao = sub.unidade.grande_comando.orgao
        equipamento.grande_comando = sub.unidade.grande_comando
        equipamento.unidade = sub.unidade
        equipamento.sub_unidade = sub


def _registrar_alteracoes(equipamento, form, user):
    """Registra as alterações feitas no equipamento"""
    alteracoes = []
    campos_verificar = [
        'codigo', 'tipo', 'marca', 'modelo', 'numero_serie', 'ano_fabricacao',
        'horas_uso', 'status', 'orgao', 'grande_comando', 'unidade', 'sub_unidade',
        'observacoes', 'data_aquisicao', 'valor_aquisicao', 'fornecedor', 'ativo'
    ]
    
    for campo in campos_verificar:
        if campo in form.changed_data:
            valor_anterior = getattr(equipamento, campo, None)
            valor_novo = form.cleaned_data.get(campo, None)
            
            # Converter valores para string para comparação
            if valor_anterior is not None:
                valor_anterior = str(valor_anterior)
            if valor_novo is not None:
                valor_novo = str(valor_novo)
            
            if valor_anterior != valor_novo:
                alteracoes.append((campo, valor_anterior or '', valor_novo or ''))
    
    return alteracoes


# ==================== VIEWS PARA ABASTECIMENTOS DE EQUIPAMENTOS ====================

@login_required
def equipamento_abastecimento_list(request):
    """Lista todos os abastecimentos de equipamentos operacionais"""
    abastecimentos = AbastecimentoEquipamento.objects.select_related(
        'equipamento', 'responsavel', 'criado_por'
    ).order_by('-data_abastecimento', '-horas_uso_abastecimento')
    
    # Filtros
    search = request.GET.get('search', '')
    equipamento_id = request.GET.get('equipamento', '')
    tipo_combustivel = request.GET.get('tipo_combustivel', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    ativo = request.GET.get('ativo', '')
    
    if search:
        abastecimentos = abastecimentos.filter(
            Q(equipamento__codigo__icontains=search) |
            Q(posto_fornecedor__icontains=search) |
            Q(observacoes__icontains=search)
        )
    
    if equipamento_id:
        abastecimentos = abastecimentos.filter(equipamento_id=equipamento_id)
    
    if tipo_combustivel:
        abastecimentos = abastecimentos.filter(tipo_combustivel=tipo_combustivel)
    
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            abastecimentos = abastecimentos.filter(data_abastecimento__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            from datetime import datetime
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_obj = data_fim_obj.replace(hour=23, minute=59, second=59)
            abastecimentos = abastecimentos.filter(data_abastecimento__lte=data_fim_obj)
        except:
            pass
    
    if ativo == '1':
        abastecimentos = abastecimentos.filter(ativo=True)
    elif ativo == '0':
        abastecimentos = abastecimentos.filter(ativo=False)
    
    # Estatísticas
    total_abastecimentos = abastecimentos.count()
    total_litros = abastecimentos.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum'] or 0
    total_valor_combustivel = abastecimentos.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    total_valor_aditivo = abastecimentos.aggregate(Sum('valor_total_aditivo'))['valor_total_aditivo__sum'] or 0
    total_valor_nota = abastecimentos.aggregate(Sum('valor_total_nota'))['valor_total_nota__sum'] or 0
    total_valor = total_valor_nota or total_valor_combustivel
    
    # Calcular média do valor por litro
    media_valor_litro = abastecimentos.aggregate(Avg('valor_litro'))['valor_litro__avg'] or 0
    
    # Paginação
    paginator = Paginator(abastecimentos, 30)
    page = request.GET.get('page')
    abastecimentos = paginator.get_page(page)
    
    # Lista de equipamentos para filtro
    equipamentos = EquipamentoOperacional.objects.filter(ativo=True).order_by('codigo')
    
    context = {
        'abastecimentos': abastecimentos,
        'equipamentos': equipamentos,
        'search': search,
        'equipamento_id': equipamento_id,
        'tipo_combustivel': tipo_combustivel,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ativo': ativo,
        'total_abastecimentos': total_abastecimentos,
        'total_litros': total_litros,
        'total_valor_combustivel': total_valor_combustivel,
        'total_valor_aditivo': total_valor_aditivo,
        'total_valor_nota': total_valor_nota,
        'total_valor': total_valor,
        'media_valor_litro': media_valor_litro,
    }
    
    return render(request, 'militares/equipamento_abastecimento_list.html', context)


@login_required
def equipamento_abastecimento_create(request):
    """Cria novo abastecimento de equipamento via modal"""
    if request.method == 'POST':
        form = AbastecimentoEquipamentoForm(request.POST)
        if form.is_valid():
            abastecimento = form.save(commit=False)
            abastecimento.criado_por = request.user
            if not abastecimento.responsavel and hasattr(request.user, 'militar'):
                abastecimento.responsavel = request.user.militar
            abastecimento.save()
            messages.success(request, f'Abastecimento registrado com sucesso! {abastecimento.quantidade_litros}L de {abastecimento.get_tipo_combustivel_display()} para {abastecimento.equipamento.codigo}.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Abastecimento registrado com sucesso!'})
            return redirect('militares:equipamento_abastecimento_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    form = AbastecimentoEquipamentoForm()
    equipamento_id = request.GET.get('equipamento', '')
    if equipamento_id:
        try:
            equipamento = EquipamentoOperacional.objects.get(pk=equipamento_id, ativo=True)
            form.fields['equipamento'].initial = equipamento
            form.fields['horas_uso_abastecimento'].initial = equipamento.horas_uso
        except:
            pass
    
    if hasattr(request.user, 'militar'):
        form.fields['responsavel'].initial = request.user.militar
    
    return render(request, 'militares/equipamento_abastecimento_form_modal.html', {'form': form})


@login_required
def equipamento_abastecimento_update(request, pk):
    """Atualiza abastecimento de equipamento via modal"""
    abastecimento = get_object_or_404(AbastecimentoEquipamento, pk=pk)
    
    if request.method == 'POST':
        form = AbastecimentoEquipamentoForm(request.POST, instance=abastecimento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Abastecimento atualizado com sucesso!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Abastecimento atualizado com sucesso!'})
            return redirect('militares:equipamento_abastecimento_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    form = AbastecimentoEquipamentoForm(instance=abastecimento)
    return render(request, 'militares/equipamento_abastecimento_form_modal.html', {'form': form, 'abastecimento': abastecimento})


@login_required
def equipamento_abastecimento_detail(request, pk):
    """Detalhes de um abastecimento de equipamento via modal"""
    abastecimento = get_object_or_404(AbastecimentoEquipamento, pk=pk)
    return render(request, 'militares/equipamento_abastecimento_detail_modal.html', {'abastecimento': abastecimento})


@login_required
def equipamento_abastecimento_delete(request, pk):
    """Exclui um abastecimento de equipamento - Apenas para superusuários"""
    if not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Apenas superusuários podem excluir abastecimentos.'})
        messages.error(request, 'Apenas superusuários podem excluir abastecimentos.')
        return redirect('militares:equipamento_abastecimento_list')
    
    abastecimento = get_object_or_404(AbastecimentoEquipamento, pk=pk)
    codigo = abastecimento.equipamento.codigo
    
    if request.method == 'POST':
        abastecimento.delete()
        messages.success(request, f'Abastecimento do equipamento {codigo} excluído com sucesso!')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Abastecimento excluído com sucesso!'})
        return redirect('militares:equipamento_abastecimento_list')
    
    return render(request, 'militares/equipamento_abastecimento_confirm_delete_modal.html', {'abastecimento': abastecimento})


@login_required
def equipamento_abastecimento_por_equipamento(request, equipamento_id):
    """Lista abastecimentos de um equipamento específico"""
    equipamento = get_object_or_404(EquipamentoOperacional, pk=equipamento_id)
    
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    abastecimentos = AbastecimentoEquipamento.objects.filter(
        equipamento=equipamento
    ).select_related('responsavel', 'criado_por')
    
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            abastecimentos = abastecimentos.filter(data_abastecimento__date__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            from datetime import datetime, time
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            data_fim_completa = datetime.combine(data_fim_obj, time.max)
            abastecimentos = abastecimentos.filter(data_abastecimento__lte=data_fim_completa)
        except:
            pass
    
    abastecimentos = abastecimentos.order_by('-data_abastecimento', '-horas_uso_abastecimento')
    
    # Estatísticas
    total_litros = abastecimentos.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum'] or 0
    total_valor_combustivel = abastecimentos.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    total_valor_aditivo = abastecimentos.aggregate(Sum('valor_total_aditivo'))['valor_total_aditivo__sum'] or 0
    total_valor_nota = abastecimentos.aggregate(Sum('valor_total_nota'))['valor_total_nota__sum'] or 0
    total_valor = total_valor_nota or total_valor_combustivel
    media_valor_litro = abastecimentos.aggregate(Avg('valor_litro'))['valor_litro__avg'] or 0
    
    context = {
        'equipamento': equipamento,
        'abastecimentos': abastecimentos,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_litros': total_litros,
        'total_valor_combustivel': total_valor_combustivel,
        'total_valor_aditivo': total_valor_aditivo,
        'total_valor_nota': total_valor_nota,
        'total_valor': total_valor,
        'media_valor_litro': media_valor_litro,
    }
    
    return render(request, 'militares/equipamento_abastecimento_por_equipamento.html', context)


# ==================== VIEWS PARA MANUTENÇÕES DE EQUIPAMENTOS ====================

@login_required
def equipamento_manutencao_list(request):
    """Lista todas as manutenções de equipamentos operacionais"""
    manutencoes = ManutencaoEquipamento.objects.select_related(
        'equipamento', 'responsavel', 'criado_por'
    ).order_by('-data_manutencao', '-horas_uso_manutencao')
    
    # Filtros
    search = request.GET.get('search', '')
    equipamento_id = request.GET.get('equipamento', '')
    tipo_manutencao = request.GET.get('tipo_manutencao', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    ativo = request.GET.get('ativo', '')
    
    if search:
        manutencoes = manutencoes.filter(
            Q(equipamento__codigo__icontains=search) |
            Q(fornecedor_oficina__icontains=search) |
            Q(descricao_servico__icontains=search) |
            Q(observacoes__icontains=search)
        )
    
    if equipamento_id:
        manutencoes = manutencoes.filter(equipamento_id=equipamento_id)
    
    if tipo_manutencao:
        manutencoes = manutencoes.filter(tipo_manutencao=tipo_manutencao)
    
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            manutencoes = manutencoes.filter(data_manutencao__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            from datetime import datetime
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_obj = data_fim_obj.replace(hour=23, minute=59, second=59)
            manutencoes = manutencoes.filter(data_manutencao__lte=data_fim_obj)
        except:
            pass
    
    if ativo == '1':
        manutencoes = manutencoes.filter(ativo=True)
    elif ativo == '0':
        manutencoes = manutencoes.filter(ativo=False)
    
    # Estatísticas
    total_manutencoes = manutencoes.count()
    total_valor = manutencoes.aggregate(Sum('valor_manutencao'))['valor_manutencao__sum'] or 0
    
    # Calcular média do valor das manutenções
    media_valor = manutencoes.aggregate(Avg('valor_manutencao'))['valor_manutencao__avg'] or 0
    
    # Paginação
    paginator = Paginator(manutencoes, 30)
    page = request.GET.get('page')
    manutencoes = paginator.get_page(page)
    
    # Lista de equipamentos para filtro
    equipamentos = EquipamentoOperacional.objects.filter(ativo=True).order_by('codigo')
    
    context = {
        'manutencoes': manutencoes,
        'equipamentos': equipamentos,
        'search': search,
        'equipamento_id': equipamento_id,
        'tipo_manutencao': tipo_manutencao,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ativo': ativo,
        'total_manutencoes': total_manutencoes,
        'total_valor': total_valor,
        'media_valor': media_valor,
    }
    
    return render(request, 'militares/equipamento_manutencao_list.html', context)


@login_required
def equipamento_manutencao_create(request):
    """Cria nova manutenção de equipamento via modal"""
    if request.method == 'POST':
        form = ManutencaoEquipamentoForm(request.POST)
        if form.is_valid():
            manutencao = form.save(commit=False)
            manutencao.criado_por = request.user
            if not manutencao.responsavel and hasattr(request.user, 'militar'):
                manutencao.responsavel = request.user.militar
            manutencao.save()
            messages.success(request, f'Manutenção registrada com sucesso para {manutencao.equipamento.codigo}!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Manutenção registrada com sucesso!'})
            return redirect('militares:equipamento_manutencao_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    form = ManutencaoEquipamentoForm()
    equipamento_id = request.GET.get('equipamento', '')
    if equipamento_id:
        try:
            equipamento = EquipamentoOperacional.objects.get(pk=equipamento_id, ativo=True)
            form.fields['equipamento'].initial = equipamento
            form.fields['horas_uso_manutencao'].initial = equipamento.horas_uso
        except:
            pass
    
    if hasattr(request.user, 'militar'):
        form.fields['responsavel'].initial = request.user.militar
    
    return render(request, 'militares/equipamento_manutencao_form_modal.html', {'form': form})


@login_required
def equipamento_manutencao_update(request, pk):
    """Atualiza manutenção de equipamento via modal"""
    manutencao = get_object_or_404(ManutencaoEquipamento, pk=pk)
    
    if request.method == 'POST':
        form = ManutencaoEquipamentoForm(request.POST, instance=manutencao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manutenção atualizada com sucesso!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Manutenção atualizada com sucesso!'})
            return redirect('militares:equipamento_manutencao_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    form = ManutencaoEquipamentoForm(instance=manutencao)
    return render(request, 'militares/equipamento_manutencao_form_modal.html', {'form': form, 'manutencao': manutencao})


@login_required
def equipamento_manutencao_detail(request, pk):
    """Detalhes de uma manutenção de equipamento via modal"""
    manutencao = get_object_or_404(ManutencaoEquipamento, pk=pk)
    return render(request, 'militares/equipamento_manutencao_detail_modal.html', {'manutencao': manutencao})


@login_required
def equipamento_manutencao_delete(request, pk):
    """Exclui uma manutenção de equipamento - Apenas para superusuários"""
    if not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Apenas superusuários podem excluir manutenções.'})
        messages.error(request, 'Apenas superusuários podem excluir manutenções.')
        return redirect('militares:equipamento_manutencao_list')
    
    manutencao = get_object_or_404(ManutencaoEquipamento, pk=pk)
    codigo = manutencao.equipamento.codigo
    
    if request.method == 'POST':
        manutencao.delete()
        messages.success(request, f'Manutenção do equipamento {codigo} excluída com sucesso!')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Manutenção excluída com sucesso!'})
        return redirect('militares:equipamento_manutencao_list')
    
    return render(request, 'militares/equipamento_manutencao_confirm_delete_modal.html', {'manutencao': manutencao})


# ==================== VIEWS PARA TROCAS DE ÓLEO DE EQUIPAMENTOS ====================

@login_required
def equipamento_troca_oleo_list(request):
    """Lista todas as trocas de óleo de equipamentos operacionais"""
    trocas = TrocaOleoEquipamento.objects.select_related(
        'equipamento', 'responsavel', 'criado_por'
    ).order_by('-data_troca', '-horas_uso_troca')
    
    # Filtros
    search = request.GET.get('search', '')
    equipamento_id = request.GET.get('equipamento', '')
    tipo_oleo = request.GET.get('tipo_oleo', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    ativo = request.GET.get('ativo', '')
    
    if search:
        trocas = trocas.filter(
            Q(equipamento__codigo__icontains=search) |
            Q(fornecedor_oficina__icontains=search) |
            Q(observacoes__icontains=search)
        )
    
    if equipamento_id:
        trocas = trocas.filter(equipamento_id=equipamento_id)
    
    if tipo_oleo:
        trocas = trocas.filter(tipo_oleo=tipo_oleo)
    
    if data_inicio:
        try:
            from datetime import datetime
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            trocas = trocas.filter(data_troca__gte=data_inicio_obj)
        except:
            pass
    
    if data_fim:
        try:
            from datetime import datetime
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_obj = data_fim_obj.replace(hour=23, minute=59, second=59)
            trocas = trocas.filter(data_troca__lte=data_fim_obj)
        except:
            pass
    
    if ativo == '1':
        trocas = trocas.filter(ativo=True)
    elif ativo == '0':
        trocas = trocas.filter(ativo=False)
    
    # Estatísticas (antes da paginação)
    total_trocas = trocas.count()
    total_valor = trocas.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    total_litros = trocas.aggregate(Sum('quantidade_litros'))['quantidade_litros__sum'] or 0
    media_valor = trocas.aggregate(Avg('valor_total'))['valor_total__avg'] or 0
    
    # Paginação
    paginator = Paginator(trocas, 30)
    page = request.GET.get('page')
    trocas = paginator.get_page(page)
    
    # Lista de equipamentos para filtro
    equipamentos = EquipamentoOperacional.objects.filter(ativo=True).order_by('codigo')
    
    context = {
        'trocas': trocas,
        'equipamentos': equipamentos,
        'search': search,
        'equipamento_id': equipamento_id,
        'tipo_oleo': tipo_oleo,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'ativo': ativo,
        'total_trocas': total_trocas,
        'total_valor': total_valor,
        'total_litros': total_litros,
        'media_valor': media_valor,
    }
    
    return render(request, 'militares/equipamento_troca_oleo_list.html', context)


@login_required
def equipamento_troca_oleo_create(request):
    """Cria nova troca de óleo de equipamento via modal"""
    if request.method == 'POST':
        form = TrocaOleoEquipamentoForm(request.POST)
        if form.is_valid():
            troca = form.save(commit=False)
            troca.criado_por = request.user
            if not troca.responsavel and hasattr(request.user, 'militar'):
                troca.responsavel = request.user.militar
            troca.save()
            messages.success(request, f'Troca de óleo registrada com sucesso para {troca.equipamento.codigo}!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Troca de óleo registrada com sucesso!'})
            return redirect('militares:equipamento_troca_oleo_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    form = TrocaOleoEquipamentoForm()
    equipamento_id = request.GET.get('equipamento', '')
    if equipamento_id:
        try:
            equipamento = EquipamentoOperacional.objects.get(pk=equipamento_id, ativo=True)
            form.fields['equipamento'].initial = equipamento
            form.fields['horas_uso_troca'].initial = equipamento.horas_uso
        except:
            pass
    
    if hasattr(request.user, 'militar'):
        form.fields['responsavel'].initial = request.user.militar
    
    return render(request, 'militares/equipamento_troca_oleo_form_modal.html', {'form': form})


@login_required
def equipamento_troca_oleo_update(request, pk):
    """Atualiza troca de óleo de equipamento via modal"""
    troca = get_object_or_404(TrocaOleoEquipamento, pk=pk)
    
    if request.method == 'POST':
        form = TrocaOleoEquipamentoForm(request.POST, instance=troca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Troca de óleo atualizada com sucesso!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Troca de óleo atualizada com sucesso!'})
            return redirect('militares:equipamento_troca_oleo_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    form = TrocaOleoEquipamentoForm(instance=troca)
    return render(request, 'militares/equipamento_troca_oleo_form_modal.html', {'form': form, 'troca': troca})


@login_required
def equipamento_troca_oleo_detail(request, pk):
    """Detalhes de uma troca de óleo de equipamento via modal"""
    troca = get_object_or_404(TrocaOleoEquipamento, pk=pk)
    return render(request, 'militares/equipamento_troca_oleo_detail_modal.html', {'troca': troca})


@login_required
def equipamento_troca_oleo_delete(request, pk):
    """Exclui uma troca de óleo de equipamento - Apenas para superusuários"""
    if not request.user.is_superuser:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Apenas superusuários podem excluir trocas de óleo.'})
        messages.error(request, 'Apenas superusuários podem excluir trocas de óleo.')
        return redirect('militares:equipamento_troca_oleo_list')
    
    troca = get_object_or_404(TrocaOleoEquipamento, pk=pk)
    codigo = troca.equipamento.codigo
    
    if request.method == 'POST':
        troca.delete()
        messages.success(request, f'Troca de óleo do equipamento {codigo} excluída com sucesso!')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Troca de óleo excluída com sucesso!'})
        return redirect('militares:equipamento_troca_oleo_list')
    
    return render(request, 'militares/equipamento_troca_oleo_confirm_delete_modal.html', {'troca': troca})

