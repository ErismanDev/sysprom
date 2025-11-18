"""
Views para o módulo de Planejadas
Gerencia orçamento e distribuição de valores para planejadas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from .models import (
    OrcamentoPlanejadas, 
    DistribuicaoOrcamentoPlanejadas,
    Orgao, 
    GrandeComando, 
    Unidade, 
    SubUnidade
)
from datetime import datetime


# ===== VIEWS PARA ORÇAMENTO =====

@login_required
def orcamento_planejadas_list(request):
    """Lista todos os orçamentos de planejadas"""
    orcamentos = OrcamentoPlanejadas.objects.all().order_by('-ano', '-mes')
    
    # Estatísticas gerais
    total_orcamentos = orcamentos.count()
    valor_total_geral = orcamentos.aggregate(total=Sum('valor_total'))['total'] or 0
    
    context = {
        'title': 'Orçamentos de Planejadas',
        'page_title': 'Orçamentos de Planejadas',
        'orcamentos': orcamentos,
        'total_orcamentos': total_orcamentos,
        'valor_total_geral': valor_total_geral,
    }
    
    return render(request, 'militares/orcamento_planejadas_list.html', context)


@login_required
def orcamento_planejadas_create(request):
    """Cria novo orçamento de planejadas"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Desativar outros orçamentos do mesmo mês/ano
                ano = int(request.POST.get('ano'))
                mes = int(request.POST.get('mes'))
                
                OrcamentoPlanejadas.objects.filter(ano=ano, mes=mes).update(ativo=False)
                
                # Converter valor de formato brasileiro para americano
                valor_str = request.POST.get('valor_total', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                # Se não tem vírgula, já está no formato americano
                
                try:
                    valor_total = float(valor_str)
                except ValueError:
                    messages.error(request, 'Valor inválido. Use apenas números.')
                    context = {
                        'title': 'Novo Orçamento de Planejadas',
                        'page_title': 'Novo Orçamento de Planejadas',
                        'anos_disponiveis': list(range(2020, 2031)),
                        'meses_choices': OrcamentoPlanejadas.MES_CHOICES,
                    }
                    return render(request, 'militares/orcamento_planejadas_form.html', context)
                
                orcamento = OrcamentoPlanejadas.objects.create(
                    ano=ano,
                    mes=mes,
                    valor_total=valor_total,
                    observacoes=request.POST.get('observacoes', ''),
                    ativo=True
                )
                
                messages.success(request, 'Orçamento de planejadas criado com sucesso!')
                return redirect('militares:orcamento_planejadas_list')
                
        except ValidationError as e:
            messages.error(request, f'Erro de validação: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erro ao criar orçamento: {str(e)}')
    
    # Obter anos disponíveis
    anos_disponiveis = list(range(2020, 2031))
    
    context = {
        'title': 'Novo Orçamento de Planejadas',
        'page_title': 'Novo Orçamento de Planejadas',
        'anos_disponiveis': anos_disponiveis,
        'meses_choices': OrcamentoPlanejadas.MES_CHOICES,
    }
    
    return render(request, 'militares/orcamento_planejadas_form.html', context)


@login_required
def orcamento_planejadas_detail(request, pk):
    """Detalhes do orçamento de planejadas"""
    orcamento = get_object_or_404(OrcamentoPlanejadas, pk=pk)
    
    context = {
        'title': f'Orçamento {orcamento.mes_nome}/{orcamento.ano}',
        'page_title': f'Orçamento {orcamento.mes_nome}/{orcamento.ano}',
        'orcamento': orcamento,
    }
    
    return render(request, 'militares/orcamento_planejadas_detail.html', context)


@login_required
def orcamento_planejadas_edit(request, pk):
    """Edita orçamento de planejadas"""
    orcamento = get_object_or_404(OrcamentoPlanejadas, pk=pk)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                orcamento.ano = int(request.POST.get('ano'))
                orcamento.mes = int(request.POST.get('mes'))
                # Converter valor de formato brasileiro para americano
                valor_str = request.POST.get('valor_total', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                # Se não tem vírgula, já está no formato americano
                
                try:
                    orcamento.valor_total = float(valor_str)
                except ValueError:
                    messages.error(request, 'Valor inválido. Use apenas números.')
                    return render(request, 'militares/orcamento_planejadas_form.html', context)
                orcamento.observacoes = request.POST.get('observacoes', '')
                orcamento.ativo = request.POST.get('ativo') == 'on'
                
                orcamento.save()
                
                messages.success(request, 'Orçamento atualizado com sucesso!')
                return redirect('militares:orcamento_planejadas_list')
                
        except ValidationError as e:
            messages.error(request, f'Erro de validação: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar orçamento: {str(e)}')
    
    context = {
        'title': 'Editar Orçamento de Planejadas',
        'page_title': 'Editar Orçamento de Planejadas',
        'orcamento': orcamento,
        'anos_disponiveis': list(range(2020, 2031)),
        'meses_choices': OrcamentoPlanejadas.MES_CHOICES,
    }
    
    return render(request, 'militares/orcamento_planejadas_form.html', context)


@login_required
def orcamento_planejadas_delete(request, pk):
    """Exclui orçamento de planejadas"""
    try:
        orcamento = get_object_or_404(OrcamentoPlanejadas, pk=pk)
        orcamento.delete()
        messages.success(request, 'Orçamento excluído com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao excluir orçamento: {str(e)}')
    
    return redirect('militares:orcamento_planejadas_list')


# ===== VIEWS PARA ORÇAMENTO MENSAL POR ORGANIZAÇÃO =====

@login_required
def orcamento_mensal_organizacoes_list(request):
    """Lista todas as organizações com orçamento mensal configurado"""
    
    # Filtros
    tipo_instancia = request.GET.get('tipo_instancia', 'todas')
    busca = request.GET.get('busca', '')
    
    # Obter orçamentos mensais ativos
    orcamentos_query = OrcamentoMensalOrganizacao.objects.filter(ativo=True).select_related(
        'orgao', 'grande_comando', 'unidade', 'sub_unidade'
    )
    
    # Filtrar por tipo de instância
    if tipo_instancia == 'orgao':
        orcamentos_query = orcamentos_query.filter(
            orgao__isnull=False,
            grande_comando__isnull=True,
            unidade__isnull=True,
            sub_unidade__isnull=True
        )
    elif tipo_instancia == 'grande_comando':
        orcamentos_query = orcamentos_query.filter(
            grande_comando__isnull=False,
            unidade__isnull=True,
            sub_unidade__isnull=True
        )
    elif tipo_instancia == 'unidade':
        orcamentos_query = orcamentos_query.filter(
            unidade__isnull=False,
            sub_unidade__isnull=True
        )
    elif tipo_instancia == 'sub_unidade':
        orcamentos_query = orcamentos_query.filter(
            sub_unidade__isnull=False
        )
    
    # Filtro de busca
    if busca:
        orcamentos_query = orcamentos_query.filter(
            Q(orgao__nome__icontains=busca) |
            Q(grande_comando__nome__icontains=busca) |
            Q(unidade__nome__icontains=busca) |
            Q(sub_unidade__nome__icontains=busca) |
            Q(orgao__sigla__icontains=busca) |
            Q(grande_comando__sigla__icontains=busca) |
            Q(unidade__sigla__icontains=busca) |
            Q(sub_unidade__sigla__icontains=busca)
        )
    
    # Ordenar por tipo e nome
    orcamentos_query = orcamentos_query.order_by(
        'orgao__nome', 'grande_comando__nome', 'unidade__nome', 'sub_unidade__nome'
    )
    
    # Paginação
    paginator = Paginator(orcamentos_query, 20)
    page_number = request.GET.get('page')
    orcamentos = paginator.get_page(page_number)
    
    # Estatísticas
    total_organizacoes = orcamentos_query.count()
    valor_total_mensal = orcamentos_query.aggregate(total=Sum('valor_mensal'))['total'] or 0
    
    context = {
        'title': 'Orçamento Mensal por Organização',
        'page_title': 'Orçamento Mensal por Organização',
        'orcamentos': orcamentos,
        'total_organizacoes': total_organizacoes,
        'valor_total_mensal': valor_total_mensal,
        'tipo_instancia': tipo_instancia,
        'busca': busca,
    }
    
    return render(request, 'militares/orcamento_mensal_organizacoes_list.html', context)


@login_required
def orcamento_mensal_organizacoes_configurar(request):
    """Configura orçamento mensal para todas as organizações"""
    
    # Obter todas as instâncias organizacionais
    orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
    grandes_comandos = GrandeComando.objects.filter(ativo=True).order_by('nome')
    unidades = Unidade.objects.filter(ativo=True).order_by('nome')
    sub_unidades = SubUnidade.objects.filter(ativo=True).order_by('nome')
    
    # Obter orçamentos existentes
    orcamentos_existentes = {}
    for orc in OrcamentoMensalOrganizacao.objects.filter(ativo=True):
        if orc.orgao:
            key = f"orgao_{orc.orgao.id}"
        elif orc.grande_comando:
            key = f"grande_comando_{orc.grande_comando.id}"
        elif orc.unidade:
            key = f"unidade_{orc.unidade.id}"
        elif orc.sub_unidade:
            key = f"sub_unidade_{orc.sub_unidade.id}"
        else:
            continue
        
        orcamentos_existentes[key] = {
            'valor': float(orc.valor_mensal),
            'observacoes': orc.observacoes or '',
            'id': orc.id
        }
    
    # Calcular total atual
    total_atual = OrcamentoMensalOrganizacao.objects.filter(ativo=True).aggregate(
        total=Sum('valor_mensal')
    )['total'] or 0
    
    context = {
        'title': 'Configurar Orçamento Mensal por Organização',
        'page_title': 'Configurar Orçamento Mensal por Organização',
        'orgaos': orgaos,
        'grandes_comandos': grandes_comandos,
        'unidades': unidades,
        'sub_unidades': sub_unidades,
        'orcamentos_existentes': orcamentos_existentes,
        'total_atual': total_atual,
    }
    
    return render(request, 'militares/orcamento_mensal_organizacoes_configurar.html', context)


@login_required
def orcamento_mensal_organizacoes_salvar(request):
    """Salva os orçamentos mensais configurados"""
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Processar dados do formulário
                dados_orcamento = {}
                
                # Processar órgãos
                for orgao_id in request.POST.getlist('orgao_ids'):
                    if orgao_id:
                        valor_str = request.POST.get(f'valor_orgao_{orgao_id}', '0')
                        observacoes = request.POST.get(f'observacoes_orgao_{orgao_id}', '')
                        
                        try:
                            valor = float(valor_str.replace(',', '.'))
                            if valor > 0:
                                dados_orcamento[f'orgao_{orgao_id}'] = {
                                    'tipo': 'orgao',
                                    'instancia_id': orgao_id,
                                    'valor': valor,
                                    'observacoes': observacoes
                                }
                        except (ValueError, TypeError):
                            continue
                
                # Processar grandes comandos
                for gc_id in request.POST.getlist('grande_comando_ids'):
                    if gc_id:
                        valor_str = request.POST.get(f'valor_grande_comando_{gc_id}', '0')
                        observacoes = request.POST.get(f'observacoes_grande_comando_{gc_id}', '')
                        
                        try:
                            valor = float(valor_str.replace(',', '.'))
                            if valor > 0:
                                dados_orcamento[f'grande_comando_{gc_id}'] = {
                                    'tipo': 'grande_comando',
                                    'instancia_id': gc_id,
                                    'valor': valor,
                                    'observacoes': observacoes
                                }
                        except (ValueError, TypeError):
                            continue
                
                # Processar unidades
                for unidade_id in request.POST.getlist('unidade_ids'):
                    if unidade_id:
                        valor_str = request.POST.get(f'valor_unidade_{unidade_id}', '0')
                        observacoes = request.POST.get(f'observacoes_unidade_{unidade_id}', '')
                        
                        try:
                            valor = float(valor_str.replace(',', '.'))
                            if valor > 0:
                                dados_orcamento[f'unidade_{unidade_id}'] = {
                                    'tipo': 'unidade',
                                    'instancia_id': unidade_id,
                                    'valor': valor,
                                    'observacoes': observacoes
                                }
                        except (ValueError, TypeError):
                            continue
                
                # Processar sub-unidades
                for sub_unidade_id in request.POST.getlist('sub_unidade_ids'):
                    if sub_unidade_id:
                        valor_str = request.POST.get(f'valor_sub_unidade_{sub_unidade_id}', '0')
                        observacoes = request.POST.get(f'observacoes_sub_unidade_{sub_unidade_id}', '')
                        
                        try:
                            valor = float(valor_str.replace(',', '.'))
                            if valor > 0:
                                dados_orcamento[f'sub_unidade_{sub_unidade_id}'] = {
                                    'tipo': 'sub_unidade',
                                    'instancia_id': sub_unidade_id,
                                    'valor': valor,
                                    'observacoes': observacoes
                                }
                        except (ValueError, TypeError):
                            continue
                
                # Desativar orçamentos existentes
                OrcamentoMensalOrganizacao.objects.filter(ativo=True).update(ativo=False)
                
                # Criar novos orçamentos
                for key, dados in dados_orcamento.items():
                    # Obter a instância
                    if dados['tipo'] == 'orgao':
                        instancia = get_object_or_404(Orgao, pk=dados['instancia_id'])
                        orgao = instancia
                        grande_comando = None
                        unidade = None
                        sub_unidade = None
                    elif dados['tipo'] == 'grande_comando':
                        instancia = get_object_or_404(GrandeComando, pk=dados['instancia_id'])
                        orgao = None
                        grande_comando = instancia
                        unidade = None
                        sub_unidade = None
                    elif dados['tipo'] == 'unidade':
                        instancia = get_object_or_404(Unidade, pk=dados['instancia_id'])
                        orgao = None
                        grande_comando = None
                        unidade = instancia
                        sub_unidade = None
                    elif dados['tipo'] == 'sub_unidade':
                        instancia = get_object_or_404(SubUnidade, pk=dados['instancia_id'])
                        orgao = None
                        grande_comando = None
                        unidade = None
                        sub_unidade = instancia
                    
                    # Criar orçamento mensal
                    OrcamentoMensalOrganizacao.objects.create(
                        orgao=orgao,
                        grande_comando=grande_comando,
                        unidade=unidade,
                        sub_unidade=sub_unidade,
                        valor_mensal=dados['valor'],
                        observacoes=dados['observacoes'],
                        ativo=True
                    )
                
                messages.success(request, f'Orçamento mensal configurado com sucesso para {len(dados_orcamento)} organizações.')
                return redirect('militares:orcamento_mensal_organizacoes_list')
                
        except Exception as e:
            messages.error(request, f'Erro ao salvar configuração: {str(e)}')
            return redirect('militares:orcamento_mensal_organizacoes_configurar')
    
    return redirect('militares:orcamento_mensal_organizacoes_configurar')


@login_required
def orcamento_mensal_organizacao_edit(request, pk):
    """Edita orçamento mensal de uma organização específica"""
    orcamento = get_object_or_404(OrcamentoMensalOrganizacao, pk=pk)
    
    if request.method == 'POST':
        try:
            valor_str = request.POST.get('valor_mensal', '0')
            observacoes = request.POST.get('observacoes', '')
            
            valor = float(valor_str.replace(',', '.'))
            
            if valor <= 0:
                messages.error(request, 'O valor mensal deve ser maior que zero.')
                return redirect('militares:orcamento_mensal_organizacao_edit', pk=pk)
            
            orcamento.valor_mensal = valor
            orcamento.observacoes = observacoes
            orcamento.save()
            
            messages.success(request, 'Orçamento mensal atualizado com sucesso.')
            return redirect('militares:orcamento_mensal_organizacoes_list')
            
        except (ValueError, TypeError):
            messages.error(request, 'Valor inválido.')
            return redirect('militares:orcamento_mensal_organizacao_edit', pk=pk)
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')
            return redirect('militares:orcamento_mensal_organizacao_edit', pk=pk)
    
    context = {
        'title': f'Editar Orçamento - {orcamento.get_instancia_nome()}',
        'page_title': f'Editar Orçamento - {orcamento.get_instancia_nome()}',
        'orcamento': orcamento,
    }
    
    return render(request, 'militares/orcamento_mensal_organizacao_edit.html', context)


@login_required
def orcamento_mensal_organizacao_delete(request, pk):
    """Desativa orçamento mensal de uma organização"""
    orcamento = get_object_or_404(OrcamentoMensalOrganizacao, pk=pk)
    
    if request.method == 'POST':
        orcamento.ativo = False
        orcamento.save()
        
        messages.success(request, f'Orçamento mensal de {orcamento.get_instancia_nome()} desativado com sucesso.')
        return redirect('militares:orcamento_mensal_organizacoes_list')
    
    context = {
        'title': f'Desativar Orçamento - {orcamento.get_instancia_nome()}',
        'page_title': f'Desativar Orçamento - {orcamento.get_instancia_nome()}',
        'orcamento': orcamento,
    }
    
    return render(request, 'militares/orcamento_mensal_organizacao_delete.html', context)
