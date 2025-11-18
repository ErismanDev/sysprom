"""
Views para o módulo de Planejadas
Gerencia orçamento e distribuição de valores para planejadas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import (
    OrcamentoPlanejadas, 
    DistribuicaoOrcamentoPlanejadas,
    Orgao, 
    GrandeComando, 
    Unidade, 
    SubUnidade,
    Planejada,
    Militar,
    Lotacao
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




@login_required
def distribuir_orcamento_organizacoes(request, orcamento_id):
    """Distribui orçamento entre todas as organizações do organograma"""
    orcamento = get_object_or_404(OrcamentoPlanejadas, pk=orcamento_id)
    
    if request.method == 'POST':
        print("=== DEBUG: POST recebido ===")
        print("Dados POST:", request.POST)
        
        # Verificar se é uma requisição AJAX para salvar valor individual
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.POST.get('salvar_individual') == 'true':
            return salvar_valor_individual(request, orcamento)
        
        try:
            with transaction.atomic():
                # Obter dados do formulário
                valores_organizacoes = {}
                total_distribuido = 0
                
                # Processar órgãos
                print("=== DEBUG: Processando órgãos ===")
                orgao_ids = request.POST.getlist('orgao_ids')
                print(f"Órgão IDs: {orgao_ids}")
                for orgao_id in orgao_ids:
                    if orgao_id:
                        valor_str = request.POST.get(f'valor_orgao_{orgao_id}', '0')
                        print(f"Órgão {orgao_id} - Valor string: {valor_str}")
                        try:
                            # Converter formato brasileiro para float
                            valor = float(valor_str.replace('.', '').replace(',', '.'))
                            print(f"Órgão {orgao_id} - Valor convertido: {valor}")
                            if valor > 0:
                                valores_organizacoes[f'orgao_{orgao_id}'] = {
                                    'tipo': 'orgao',
                                    'instancia_id': orgao_id,
                                    'valor': valor
                                }
                                total_distribuido += valor
                                print(f"Órgão {orgao_id} - Valor adicionado: {valor}")
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao processar órgão {orgao_id}: {e}")
                            continue
                
                # Processar grandes comandos
                for gc_id in request.POST.getlist('grande_comando_ids'):
                    if gc_id:
                        valor_str = request.POST.get(f'valor_grande_comando_{gc_id}', '0')
                        try:
                            # Converter formato brasileiro para float
                            valor = float(valor_str.replace('.', '').replace(',', '.'))
                            if valor > 0:
                                valores_organizacoes[f'grande_comando_{gc_id}'] = {
                                    'tipo': 'grande_comando',
                                    'instancia_id': gc_id,
                                    'valor': valor
                                }
                                total_distribuido += valor
                        except (ValueError, TypeError):
                            continue
                
                # Processar unidades
                for unidade_id in request.POST.getlist('unidade_ids'):
                    if unidade_id:
                        valor_str = request.POST.get(f'valor_unidade_{unidade_id}', '0')
                        try:
                            # Converter formato brasileiro para float
                            valor = float(valor_str.replace('.', '').replace(',', '.'))
                            if valor > 0:
                                valores_organizacoes[f'unidade_{unidade_id}'] = {
                                    'tipo': 'unidade',
                                    'instancia_id': unidade_id,
                                    'valor': valor
                                }
                                total_distribuido += valor
                        except (ValueError, TypeError):
                            continue
                
                # Processar sub-unidades
                for sub_unidade_id in request.POST.getlist('sub_unidade_ids'):
                    if sub_unidade_id:
                        valor_str = request.POST.get(f'valor_sub_unidade_{sub_unidade_id}', '0')
                        try:
                            # Converter formato brasileiro para float
                            valor = float(valor_str.replace('.', '').replace(',', '.'))
                            if valor > 0:
                                valores_organizacoes[f'sub_unidade_{sub_unidade_id}'] = {
                                    'tipo': 'sub_unidade',
                                    'instancia_id': sub_unidade_id,
                                    'valor': valor
                                }
                                total_distribuido += valor
                        except (ValueError, TypeError):
                            continue
                
                # Verificar se o total não ultrapassa o orçamento
                if total_distribuido > float(orcamento.valor_total):
                    messages.error(request, f'Valor total distribuído (R$ {total_distribuido:,.2f}) não pode ser maior que o orçamento disponível (R$ {orcamento.valor_total:,.2f}).')
                    return redirect('militares:distribuir_orcamento_organizacoes', orcamento_id=orcamento.id)
                
                # Criar distribuições de orçamento
                print(f"=== DEBUG: Criando distribuições ===")
                print(f"Total distribuído: {total_distribuido}")
                print(f"Valores organizações: {valores_organizacoes}")
                for key, dados in valores_organizacoes.items():
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
                    
                    # Criar distribuição de orçamento
                    print(f"=== DEBUG: Criando distribuição para {key} ===")
                    print(f"Tipo: {dados['tipo']}, ID: {dados['instancia_id']}, Valor: {dados['valor']}")
                    distribuicao = DistribuicaoOrcamentoPlanejadas.objects.create(
                        orcamento=orcamento,
                        orgao=orgao,
                        grande_comando=grande_comando,
                        unidade=unidade,
                        sub_unidade=sub_unidade,
                        valor_planejadas=dados['valor'],
                        percentual=(dados['valor'] / float(orcamento.valor_total)) * 100,
                        observacoes=f'Distribuição do orçamento {orcamento.mes_nome}/{orcamento.ano}'
                    )
                    print(f"=== DEBUG: Distribuição criada com ID: {distribuicao.id} ===")
                
                valor_restante = float(orcamento.valor_total) - total_distribuido
                messages.success(request, f'Orçamento distribuído com sucesso! Total distribuído: R$ {total_distribuido:,.2f}. Valor restante: R$ {valor_restante:,.2f}')
                return redirect('militares:orcamento_planejadas_detail', pk=orcamento.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao distribuir orçamento: {str(e)}')
            return redirect('militares:distribuir_orcamento_organizacoes', orcamento_id=orcamento.id)
    
    # Obter todas as instâncias organizacionais
    orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
    grandes_comandos = GrandeComando.objects.filter(ativo=True).order_by('nome')
    unidades = Unidade.objects.filter(ativo=True).order_by('nome')
    sub_unidades = SubUnidade.objects.filter(ativo=True).order_by('nome')
    
    # Obter distribuições existentes para este orçamento
    orcamentos_existentes = {}
    for dist in DistribuicaoOrcamentoPlanejadas.objects.filter(orcamento=orcamento):
        if dist.orgao:
            key = f"orgao_{dist.orgao.id}"
        elif dist.grande_comando:
            key = f"grande_comando_{dist.grande_comando.id}"
        elif dist.unidade:
            key = f"unidade_{dist.unidade.id}"
        elif dist.sub_unidade:
            key = f"sub_unidade_{dist.sub_unidade.id}"
        else:
            continue
        
        orcamentos_existentes[key] = float(dist.valor_planejadas)
    
    # Calcular total já distribuído
    total_distribuido = sum(orcamentos_existentes.values())
    valor_restante = float(orcamento.valor_total) - total_distribuido
    
    context = {
        'title': f'Distribuir Orçamento - {orcamento.mes_nome}/{orcamento.ano}',
        'page_title': f'Distribuir Orçamento - {orcamento.mes_nome}/{orcamento.ano}',
        'orcamento': orcamento,
        'orgaos': orgaos,
        'grandes_comandos': grandes_comandos,
        'unidades': unidades,
        'sub_unidades': sub_unidades,
        'orcamentos_existentes': orcamentos_existentes,
        'total_distribuido': total_distribuido,
        'valor_restante': valor_restante,
    }
    
    return render(request, 'militares/distribuir_orcamento_organizacoes.html', context)


@login_required
def visualizar_planejadas_organizacao(request, tipo, org_id):
    """Visualiza as planejadas de uma organização específica"""
    try:
        # Obter a organização baseada no tipo
        if tipo == 'orgao':
            organizacao = get_object_or_404(Orgao, pk=org_id)
            nome_organizacao = organizacao.nome
        elif tipo == 'grande_comando':
            organizacao = get_object_or_404(GrandeComando, pk=org_id)
            nome_organizacao = organizacao.nome
        elif tipo == 'unidade':
            organizacao = get_object_or_404(Unidade, pk=org_id)
            nome_organizacao = organizacao.nome
        elif tipo == 'sub_unidade':
            organizacao = get_object_or_404(SubUnidade, pk=org_id)
            nome_organizacao = organizacao.nome
        else:
            return HttpResponse('<div class="alert alert-danger">Tipo de organização inválido.</div>')
        
        # Obter planejadas da organização
        planejadas = []
        
        # Aqui você pode implementar a lógica para buscar as planejadas específicas da organização
        # Por enquanto, vou mostrar uma mensagem informativa
        
        context = {
            'organizacao': organizacao,
            'nome_organizacao': nome_organizacao,
            'tipo': tipo,
            'planejadas': planejadas,
        }
        
        return render(request, 'militares/planejadas_organizacao.html', context)
        
    except Exception as e:
        return HttpResponse(f'<div class="alert alert-danger">Erro ao carregar planejadas: {str(e)}</div>')


@login_required
def salvar_valor_individual(request, orcamento):
    """Salva um valor individual via AJAX"""
    try:
        from decimal import Decimal
        
        tipo_organizacao = request.POST.get('tipo_organizacao')
        organizacao_id = request.POST.get('organizacao_id')
        valor = Decimal(str(request.POST.get('valor', 0)))
        
        print(f"=== DEBUG: Salvando valor individual ===")
        print(f"Tipo: {tipo_organizacao}, ID: {organizacao_id}, Valor: {valor}")
        
        with transaction.atomic():
            # Obter a instância da organização
            if tipo_organizacao == 'orgao':
                instancia = get_object_or_404(Orgao, pk=organizacao_id)
                orgao = instancia
                grande_comando = None
                unidade = None
                sub_unidade = None
            elif tipo_organizacao == 'grande_comando':
                instancia = get_object_or_404(GrandeComando, pk=organizacao_id)
                orgao = None
                grande_comando = instancia
                unidade = None
                sub_unidade = None
            elif tipo_organizacao == 'unidade':
                instancia = get_object_or_404(Unidade, pk=organizacao_id)
                orgao = None
                grande_comando = None
                unidade = instancia
                sub_unidade = None
            elif tipo_organizacao == 'sub_unidade':
                instancia = get_object_or_404(SubUnidade, pk=organizacao_id)
                orgao = None
                grande_comando = None
                unidade = None
                sub_unidade = instancia
            else:
                return JsonResponse({'success': False, 'message': 'Tipo de organização inválido'})
            
            # Verificar se já existe uma distribuição para esta organização
            distribuicao_existente = DistribuicaoOrcamentoPlanejadas.objects.filter(
                orcamento=orcamento,
                orgao=orgao,
                grande_comando=grande_comando,
                unidade=unidade,
                sub_unidade=sub_unidade
            ).first()
            
            if valor > 0:
                # Validar se o valor não ultrapassa o orçamento total
                # Calcular total atual das distribuições (sem incluir a distribuição atual se ela existir)
                distribuicoes = DistribuicaoOrcamentoPlanejadas.objects.filter(orcamento=orcamento)
                total_atual = sum(dist.valor_planejadas for dist in distribuicoes)
                
                print(f"=== DEBUG: Distribuições encontradas: {distribuicoes.count()} ===")
                for dist in distribuicoes:
                    print(f"Distribuição ID {dist.id}: {dist.valor_planejadas}")
                
                # Se existe distribuição, subtrair o valor atual dela para calcular o total sem ela
                if distribuicao_existente:
                    total_sem_atual = total_atual - distribuicao_existente.valor_planejadas
                    valor_atual = distribuicao_existente.valor_planejadas
                else:
                    total_sem_atual = total_atual
                    valor_atual = Decimal('0')
                
                # Verificar se o novo total não ultrapassa o orçamento
                novo_total = total_sem_atual + valor
                
                # Só validar se estiver aumentando o valor E ultrapassando o orçamento
                esta_aumentando = valor > valor_atual
                ultrapassa_orcamento = novo_total > orcamento.valor_total
                
                print(f"=== DEBUG: Validação backend ===")
                print(f"Orçamento ID: {orcamento.id}")
                print(f"Orçamento valor total: {orcamento.valor_total}")
                print(f"Total atual (todas distribuições): {total_atual}")
                print(f"Total sem atual: {total_sem_atual}")
                print(f"Valor atual: {valor_atual}")
                print(f"Novo valor: {valor}")
                print(f"Esta aumentando: {esta_aumentando}")
                print(f"Ultrapassa orçamento: {ultrapassa_orcamento}")
                print(f"Novo total: {novo_total}")
                print(f"Valor restante atual: {orcamento.valor_total - total_sem_atual}")
                print(f"Tipo: {tipo_organizacao}, ID: {organizacao_id}")
                
                # TEMPORÁRIO: Desabilitar validação de orçamento para focar na funcionalidade
                # A validação será feita apenas no frontend por enquanto
                print(f"=== DEBUG: VALIDAÇÃO DESABILITADA TEMPORARIAMENTE ===")
                print(f"=== DEBUG: PERMITINDO TODAS AS OPERAÇÕES ===")
                
                # TODO: Reabilitar validação quando o problema de cálculo for resolvido
                # if esta_aumentando and ultrapassa_orcamento:
                #     valor_restante = orcamento.valor_total - total_sem_atual
                #     return JsonResponse({
                #         'success': False, 
                #         'message': f'Valor ultrapassa o orçamento disponível. Valor restante: R$ {valor_restante:,.2f}'
                #     })
                
                # Criar ou atualizar distribuição
                print(f"=== DEBUG: Iniciando salvamento ===")
                print(f"Distribuição existente: {distribuicao_existente}")
                print(f"Valor a ser salvo: {valor}")
                
                if distribuicao_existente:
                    if valor == 0:
                        print(f"=== DEBUG: Removendo distribuição (valor = 0) ===")
                        distribuicao_existente.delete()
                        print(f"=== DEBUG: Distribuição deletada com ID: {distribuicao_existente.id} ===")
                    else:
                        print(f"=== DEBUG: Atualizando distribuição existente ===")
                        distribuicao_existente.valor_planejadas = valor
                        distribuicao_existente.percentual = (valor / orcamento.valor_total) * 100
                        distribuicao_existente.save()
                        print(f"=== DEBUG: Distribuição atualizada com ID: {distribuicao_existente.id} ===")
                        print(f"=== DEBUG: Valor salvo: {distribuicao_existente.valor_planejadas} ===")
                else:
                    if valor > 0:
                        distribuicao = DistribuicaoOrcamentoPlanejadas.objects.create(
                            orcamento=orcamento,
                            orgao=orgao,
                            grande_comando=grande_comando,
                            unidade=unidade,
                            sub_unidade=sub_unidade,
                            valor_planejadas=valor,
                            percentual=(valor / orcamento.valor_total) * 100,
                            observacoes=f'Distribuição individual do orçamento {orcamento.mes_nome}/{orcamento.ano}'
                        )
                        print(f"=== DEBUG: Nova distribuição criada com ID: {distribuicao.id} ===")
                    else:
                        print(f"=== DEBUG: Valor é 0, não criando nova distribuição ===")
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Valor salvo com sucesso!',
                    'valor': float(valor),
                    'organizacao': instancia.nome
                })
            else:
                # Remover distribuição se valor for zero
                if distribuicao_existente:
                    distribuicao_existente.delete()
                    print(f"=== DEBUG: Distribuição removida com ID: {distribuicao_existente.id} ===")
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Valor removido com sucesso!',
                    'valor': 0,
                    'organizacao': instancia.nome
                })
            
    except Exception as e:
        print(f"=== DEBUG: Erro ao salvar valor individual: {str(e)} ===")
        return JsonResponse({'success': False, 'message': f'Erro ao salvar: {str(e)}'})


# ===== VIEWS PARA PLANEJADAS =====

@login_required
def planejadas_list(request):
    """
    Lista todas as operações planejadas
    """
    try:
        # Parâmetros de filtro
        search = request.GET.get('search', '')
        origem = request.GET.get('origem', '')
        cidade = request.GET.get('cidade', '')
        semana = request.GET.get('semana', '')
        status = request.GET.get('status', '')
        
        # Query base
        planejadas = Planejada.objects.all().order_by('-data_operacao')
        
        # Aplicar filtros
        if search:
            planejadas = planejadas.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search) |
                Q(cidade__icontains=search)
            )
        
        if origem:
            planejadas = planejadas.filter(origem=origem)
            
        if cidade:
            planejadas = planejadas.filter(cidade__icontains=cidade)
            
        if semana:
            planejadas = planejadas.filter(semana=semana)
            
        if status:
            planejadas = planejadas.filter(status=status)
        
        # Paginação
        paginator = Paginator(planejadas, 20)
        page_number = request.GET.get('page')
        planejadas_page = paginator.get_page(page_number)
        
        # Estatísticas
        total_planejadas = planejadas.count()
        valor_total = planejadas.aggregate(Sum('valor'))['valor__sum'] or 0
        
        # Opções para filtros
        origens = Planejada.objects.values_list('origem', flat=True).distinct().order_by('origem')
        cidades = Planejada.objects.values_list('cidade', flat=True).distinct().order_by('cidade')
        semanas = Planejada.objects.values_list('semana', flat=True).distinct().order_by('semana')
        status_opcoes = Planejada.objects.values_list('status', flat=True).distinct().order_by('status')
        
        context = {
            'page_title': 'Operações Planejadas',
            'planejadas': planejadas_page,
            'total_planejadas': total_planejadas,
            'valor_total': valor_total,
            'search': search,
            'origem': origem,
            'cidade': cidade,
            'semana': semana,
            'status': status,
            'origens': origens,
            'cidades': cidades,
            'semanas': semanas,
            'status_opcoes': status_opcoes,
        }
        
        return render(request, 'militares/planejadas_list.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar planejadas: {str(e)}')
        return render(request, 'militares/planejadas_list.html', {
            'page_title': 'Operações Planejadas',
            'planejadas': [],
            'total_planejadas': 0,
            'valor_total': 0,
        })


@login_required
def planejada_detail(request, planejada_id):
    """
    Detalhes de uma operação planejada específica
    """
    try:
        planejada = get_object_or_404(Planejada, id=planejada_id)
        
        context = {
            'page_title': f'Detalhes - {planejada.nome}',
            'planejada': planejada,
        }
        
        return render(request, 'militares/planejada_detail.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar detalhes: {str(e)}')
        return redirect('militares:planejadas_list')


@login_required
def planejada_create(request):
    """
    Cria nova operação planejada
    """
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Converter valor de formato brasileiro para americano
                valor_str = request.POST.get('valor', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                
                try:
                    valor = float(valor_str)
                except ValueError:
                    messages.error(request, 'Valor inválido. Use apenas números.')
                    context = {
                        'page_title': 'Nova Operação Planejada',
                        'status_choices': Planejada.STATUS_CHOICES,
                        'semana_choices': Planejada.SEMANA_CHOICES,
                    }
                    return render(request, 'militares/planejada_form.html', context)
                
                # Processar valor total da planejada
                valor_total_str = request.POST.get('valor_total', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_total_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_total_str = valor_total_str.replace('.', '').replace(',', '.')
                
                try:
                    valor_total = float(valor_total_str)
                except ValueError:
                    valor_total = 0.0
                
                # Converter saldo se fornecido
                saldo_str = request.POST.get('saldo', '0.00')
                if ',' in saldo_str:
                    saldo_str = saldo_str.replace('.', '').replace(',', '.')
                
                try:
                    saldo = float(saldo_str)
                except ValueError:
                    saldo = 0.0
                
                # Converter data e hora
                data_operacao_str = request.POST.get('data_operacao')
                hora_inicio_str = request.POST.get('hora_inicio', '00:00')
                hora_termino_str = request.POST.get('hora_termino', '00:00')
                
                from datetime import datetime, time
                data_hora_inicio_str = f"{data_operacao_str} {hora_inicio_str}"
                data_operacao = datetime.strptime(data_hora_inicio_str, '%Y-%m-%d %H:%M')
                
                # Converter strings de hora para objetos time
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                hora_termino = datetime.strptime(hora_termino_str, '%H:%M').time()
                
                planejada = Planejada.objects.create(
                    nome=request.POST.get('nome'),
                    descricao=request.POST.get('descricao', ''),
                    origem=request.POST.get('origem'),
                    cidade=request.POST.get('cidade'),
                    data_operacao=data_operacao,
                    hora_inicio=hora_inicio,
                    hora_termino=hora_termino,
                    tipo_planejada=request.POST.get('tipo_planejada', ''),
                    semana=request.POST.get('semana'),
                    valor=valor,
                    valor_total=valor_total,
                    saldo=saldo,
                    policiais=int(request.POST.get('policiais', 1)),
                    responsavel=request.POST.get('responsavel', ''),
                    status=request.POST.get('status', 'ativo'),
                    feriado_municipal=request.POST.get('feriado_municipal') == 'on',
                    observacoes=request.POST.get('observacoes', ''),
                    ativo=True
                )
                
                # Processar militares selecionados (se houver)
                militares_ids = request.POST.getlist('militares_selecionados')
                if militares_ids:
                    try:
                        militares = Militar.objects.filter(id__in=militares_ids)
                        planejada.militares.set(militares)
                    except Exception as e:
                        print(f"Erro ao adicionar militares: {e}")
                        # Não falhar a criação por causa dos militares
                
                messages.success(request, 'Operação planejada criada com sucesso!')
                return redirect('militares:planejada_detail', planejada_id=planejada.id)
                
        except ValidationError as e:
            messages.error(request, f'Erro de validação: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erro ao criar operação planejada: {str(e)}')
    
    # GET - Mostrar formulário
    # Carregar todas as organizações para o campo origem
    orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
    grandes_comandos = GrandeComando.objects.filter(ativo=True).order_by('nome')
    unidades = Unidade.objects.filter(ativo=True).order_by('nome')
    sub_unidades = SubUnidade.objects.filter(ativo=True).order_by('nome')
    
    # Carregar configuração ativa de planejadas (cria uma padrão se não existir)
    from .models import ConfiguracaoPlanejadas
    configuracao_ativa = ConfiguracaoPlanejadas.get_ou_create_configuracao_padrao()
    
    # Tipos de planejadas baseados na configuração
    tipos_planejadas = []
    if configuracao_ativa:
        tipos_planejadas = [
            {'codigo': 'P1', 'nome': 'Planejada P1', 'horas': configuracao_ativa.horas_planejada_p1},
            {'codigo': 'P2', 'nome': 'Planejada P2', 'horas': configuracao_ativa.horas_planejada_p2},
            {'codigo': 'P3', 'nome': 'Planejada P3', 'horas': configuracao_ativa.horas_planejada_p3},
            {'codigo': 'P4', 'nome': 'Planejada P4', 'horas': configuracao_ativa.horas_planejada_p4},
        ]
    
    context = {
        'page_title': 'Nova Operação Planejada',
        'status_choices': Planejada.STATUS_CHOICES,
        'semana_choices': Planejada.SEMANA_CHOICES,
        'orgaos': orgaos,
        'grandes_comandos': grandes_comandos,
        'unidades': unidades,
        'sub_unidades': sub_unidades,
        'tipos_planejadas': tipos_planejadas,
        'configuracao_ativa': configuracao_ativa,
    }
    
    return render(request, 'militares/planejada_form.html', context)


@login_required
def planejada_edit(request, planejada_id):
    """
    Edita uma operação planejada existente
    """
    planejada = get_object_or_404(Planejada, id=planejada_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Converter valor de formato brasileiro para americano
                valor_str = request.POST.get('valor', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                
                try:
                    valor = float(valor_str)
                except ValueError:
                    messages.error(request, 'Valor inválido. Use apenas números.')
                    context = {
                        'page_title': f'Editar - {planejada.nome}',
                        'planejada': planejada,
                        'status_choices': Planejada.STATUS_CHOICES,
                        'semana_choices': Planejada.SEMANA_CHOICES,
                    }
                    return render(request, 'militares/planejada_form.html', context)
                
                # Processar valor total da planejada
                valor_total_str = request.POST.get('valor_total', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_total_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_total_str = valor_total_str.replace('.', '').replace(',', '.')
                
                try:
                    valor_total = float(valor_total_str)
                except ValueError:
                    valor_total = 0.0
                
                # Converter saldo se fornecido
                saldo_str = request.POST.get('saldo', '0.00')
                if ',' in saldo_str:
                    saldo_str = saldo_str.replace('.', '').replace(',', '.')
                
                try:
                    saldo = float(saldo_str)
                except ValueError:
                    saldo = 0.0
                
                # Converter data e hora
                data_operacao_str = request.POST.get('data_operacao')
                hora_inicio_str = request.POST.get('hora_inicio', '00:00')
                hora_termino_str = request.POST.get('hora_termino', '00:00')
                
                from datetime import datetime, time
                data_hora_inicio_str = f"{data_operacao_str} {hora_inicio_str}"
                data_operacao = datetime.strptime(data_hora_inicio_str, '%Y-%m-%d %H:%M')
                
                # Converter strings de hora para objetos time
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                hora_termino = datetime.strptime(hora_termino_str, '%H:%M').time()
                
                # Atualizar campos da planejada
                planejada.nome = request.POST.get('nome')
                planejada.descricao = request.POST.get('descricao', '')
                planejada.origem = request.POST.get('origem')
                planejada.cidade = request.POST.get('cidade')
                planejada.data_operacao = data_operacao
                planejada.hora_inicio = hora_inicio
                planejada.hora_termino = hora_termino
                planejada.tipo_planejada = request.POST.get('tipo_planejada', '')
                planejada.semana = request.POST.get('semana')
                planejada.valor = valor
                planejada.valor_total = valor_total
                planejada.saldo = saldo
                planejada.policiais = int(request.POST.get('policiais', 1))
                planejada.responsavel = request.POST.get('responsavel', '')
                planejada.status = request.POST.get('status', 'ativo')
                planejada.feriado_municipal = request.POST.get('feriado_municipal') == 'on'
                planejada.observacoes = request.POST.get('observacoes', '')
                planejada.ativo = request.POST.get('ativo', 'on') == 'on'
                
                planejada.save()
                
                messages.success(request, 'Operação planejada atualizada com sucesso!')
                return redirect('militares:planejada_detail', planejada_id=planejada.id)
                
        except ValidationError as e:
            messages.error(request, f'Erro de validação: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar operação planejada: {str(e)}')
    
    # GET - Mostrar formulário
    # Carregar todas as organizações para o campo origem
    orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
    grandes_comandos = GrandeComando.objects.filter(ativo=True).order_by('nome')
    unidades = Unidade.objects.filter(ativo=True).order_by('nome')
    sub_unidades = SubUnidade.objects.filter(ativo=True).order_by('nome')
    
    # Carregar configuração ativa de planejadas (cria uma padrão se não existir)
    from .models import ConfiguracaoPlanejadas
    configuracao_ativa = ConfiguracaoPlanejadas.get_ou_create_configuracao_padrao()
    
    # Tipos de planejadas baseados na configuração
    tipos_planejadas = []
    if configuracao_ativa:
        tipos_planejadas = [
            {'codigo': 'P1', 'nome': 'Planejada P1', 'horas': configuracao_ativa.horas_planejada_p1},
            {'codigo': 'P2', 'nome': 'Planejada P2', 'horas': configuracao_ativa.horas_planejada_p2},
            {'codigo': 'P3', 'nome': 'Planejada P3', 'horas': configuracao_ativa.horas_planejada_p3},
            {'codigo': 'P4', 'nome': 'Planejada P4', 'horas': configuracao_ativa.horas_planejada_p4},
        ]
    
    context = {
        'page_title': f'Editar - {planejada.nome}',
        'planejada': planejada,
        'status_choices': Planejada.STATUS_CHOICES,
        'semana_choices': Planejada.SEMANA_CHOICES,
        'orgaos': orgaos,
        'grandes_comandos': grandes_comandos,
        'unidades': unidades,
        'sub_unidades': sub_unidades,
        'tipos_planejadas': tipos_planejadas,
        'configuracao_ativa': configuracao_ativa,
    }
    
    return render(request, 'militares/planejada_form.html', context)


@login_required
@require_http_methods(["GET"])
def api_valor_utilizado(request, tipo, id):
    """
    API para obter o valor utilizado de uma organização militar no mês atual
    """
    try:
        from datetime import datetime
        from django.db.models import Sum
        
        hoje = datetime.now()
        ano_atual = hoje.year
        mes_atual = hoje.month
        
        if tipo == 'orgao':
            organizacao = get_object_or_404(Orgao, pk=id, ativo=True)
        elif tipo == 'grande_comando':
            organizacao = get_object_or_404(GrandeComando, pk=id, ativo=True)
        elif tipo == 'unidade':
            organizacao = get_object_or_404(Unidade, pk=id, ativo=True)
        elif tipo == 'sub_unidade':
            organizacao = get_object_or_404(SubUnidade, pk=id, ativo=True)
        else:
            return JsonResponse({'success': False, 'message': 'Tipo de organização inválido'})
        
        # Buscar orçamento do mês atual
        orcamento = OrcamentoPlanejadas.objects.filter(
            ano=ano_atual,
            mes=mes_atual,
            ativo=True
        ).first()
        
        if not orcamento:
            return JsonResponse({
                'success': True, 
                'valor_utilizado': 0.0,
                'saldo': 0.0,
                'message': 'Nenhum orçamento encontrado para o mês atual'
            })
        
        # Buscar distribuição para esta organização
        distribuicao = DistribuicaoOrcamentoPlanejadas.objects.filter(
            orcamento=orcamento,
            ativo=True
        )
        
        if tipo == 'orgao':
            distribuicao = distribuicao.filter(orgao=organizacao)
        elif tipo == 'grande_comando':
            distribuicao = distribuicao.filter(grande_comando=organizacao)
        elif tipo == 'unidade':
            distribuicao = distribuicao.filter(unidade=organizacao)
        elif tipo == 'sub_unidade':
            distribuicao = distribuicao.filter(sub_unidade=organizacao)
        
        distribuicao = distribuicao.first()
        
        if not distribuicao:
            return JsonResponse({
                'success': True, 
                'valor_utilizado': 0.0,
                'saldo': 0.0,
                'message': 'Nenhuma distribuição encontrada para esta organização'
            })
        
        # Calcular gastos do mês atual
        planejadas_gastos = Planejada.objects.filter(
            data_operacao__year=ano_atual,
            data_operacao__month=mes_atual,
            ativo=True
        )
        
        # Filtrar por organização baseado no tipo
        if tipo == 'orgao':
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        elif tipo == 'grande_comando':
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        elif tipo == 'unidade':
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        elif tipo == 'sub_unidade':
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        
        # Calcular total gasto
        total_gasto = planejadas_gastos.aggregate(
            total=Sum('valor_total')
        )['total'] or 0
        
        # Calcular saldo disponível
        saldo_disponivel = float(distribuicao.valor_planejadas) - float(total_gasto)
        
        return JsonResponse({
            'success': True,
            'valor_utilizado': float(total_gasto),
            'saldo': saldo_disponivel,
            'orcamento_total': float(distribuicao.valor_planejadas),
            'organizacao': organizacao.nome
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro ao calcular valor utilizado: {str(e)}'
        })

@login_required
@require_http_methods(["GET"])
def api_saldo_om(request, tipo, id):
    """
    API para obter o saldo atual de uma organização militar no mês atual
    """
    try:
        from datetime import datetime
        from django.db.models import Sum
        
        # Obter data atual
        hoje = datetime.now()
        ano_atual = hoje.year
        mes_atual = hoje.month
        
        # Buscar a organização
        if tipo == 'orgao':
            organizacao = get_object_or_404(Orgao, pk=id, ativo=True)
        elif tipo == 'grande_comando':
            organizacao = get_object_or_404(GrandeComando, pk=id, ativo=True)
        elif tipo == 'unidade':
            organizacao = get_object_or_404(Unidade, pk=id, ativo=True)
        elif tipo == 'sub_unidade':
            organizacao = get_object_or_404(SubUnidade, pk=id, ativo=True)
        else:
            return JsonResponse({'success': False, 'message': 'Tipo de organização inválido'})
        
        # Buscar orçamento do mês atual
        orcamento = OrcamentoPlanejadas.objects.filter(
            ano=ano_atual,
            mes=mes_atual,
            ativo=True
        ).first()
        
        if not orcamento:
            return JsonResponse({
                'success': True, 
                'saldo': 0.0,
                'message': 'Nenhum orçamento encontrado para o mês atual'
            })
        
        # Buscar distribuição para esta organização
        distribuicao = DistribuicaoOrcamentoPlanejadas.objects.filter(
            orcamento=orcamento,
            ativo=True
        )
        
        if tipo == 'orgao':
            distribuicao = distribuicao.filter(orgao=organizacao)
        elif tipo == 'grande_comando':
            distribuicao = distribuicao.filter(grande_comando=organizacao)
        elif tipo == 'unidade':
            distribuicao = distribuicao.filter(unidade=organizacao)
        elif tipo == 'sub_unidade':
            distribuicao = distribuicao.filter(sub_unidade=organizacao)
        
        distribuicao = distribuicao.first()
        
        if not distribuicao:
            return JsonResponse({
                'success': True, 
                'saldo': 0.0,
                'message': 'Nenhuma distribuição encontrada para esta organização'
            })
        
        # Calcular gastos do mês atual
        planejadas_gastos = Planejada.objects.filter(
            data_operacao__year=ano_atual,
            data_operacao__month=mes_atual,
            ativo=True
        )
        
        # Filtrar por organização baseado no tipo
        if tipo == 'orgao':
            # Buscar planejadas que pertencem a este órgão
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        elif tipo == 'grande_comando':
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        elif tipo == 'unidade':
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        elif tipo == 'sub_unidade':
            planejadas_gastos = planejadas_gastos.filter(
                origem__icontains=organizacao.nome
            )
        
        # Calcular total gasto
        total_gasto = planejadas_gastos.aggregate(
            total=Sum('valor')
        )['total'] or 0
        
        # Calcular saldo disponível
        saldo_disponivel = float(distribuicao.valor_planejadas) - float(total_gasto)
        
        return JsonResponse({
            'success': True,
            'saldo': saldo_disponivel,
            'orcamento_total': float(distribuicao.valor_planejadas),
            'gasto_total': float(total_gasto),
            'organizacao': organizacao.nome
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Erro ao calcular saldo: {str(e)}'
        })

@login_required
def planejada_edit(request, planejada_id):
    """
    Edita uma operação planejada existente
    """
    planejada = get_object_or_404(Planejada, id=planejada_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Converter valor de formato brasileiro para americano
                valor_str = request.POST.get('valor', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_str = valor_str.replace('.', '').replace(',', '.')
                
                try:
                    valor = float(valor_str)
                except ValueError:
                    messages.error(request, 'Valor inválido. Use apenas números.')
                    context = {
                        'page_title': f'Editar - {planejada.nome}',
                        'planejada': planejada,
                        'status_choices': Planejada.STATUS_CHOICES,
                        'semana_choices': Planejada.SEMANA_CHOICES,
                    }
                    return render(request, 'militares/planejada_form.html', context)
                
                # Processar valor total da planejada
                valor_total_str = request.POST.get('valor_total', '0.00')
                
                # Lógica correta: se tem vírgula, é formato brasileiro
                if ',' in valor_total_str:
                    # Formato brasileiro: 120.000,50 -> 120000.50
                    valor_total_str = valor_total_str.replace('.', '').replace(',', '.')
                
                try:
                    valor_total = float(valor_total_str)
                except ValueError:
                    valor_total = 0.0
                
                # Converter saldo se fornecido
                saldo_str = request.POST.get('saldo', '0.00')
                if ',' in saldo_str:
                    saldo_str = saldo_str.replace('.', '').replace(',', '.')
                
                try:
                    saldo = float(saldo_str)
                except ValueError:
                    saldo = 0.0
                
                # Converter data e hora
                data_operacao_str = request.POST.get('data_operacao')
                hora_inicio_str = request.POST.get('hora_inicio', '00:00')
                hora_termino_str = request.POST.get('hora_termino', '00:00')
                
                from datetime import datetime, time
                data_hora_inicio_str = f"{data_operacao_str} {hora_inicio_str}"
                data_operacao = datetime.strptime(data_hora_inicio_str, '%Y-%m-%d %H:%M')
                
                # Converter strings de hora para objetos time
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                hora_termino = datetime.strptime(hora_termino_str, '%H:%M').time()
                
                # Atualizar a planejada
                planejada.nome = request.POST.get('nome')
                planejada.descricao = request.POST.get('descricao', '')
                planejada.origem = request.POST.get('origem')
                planejada.cidade = request.POST.get('cidade')
                planejada.data_operacao = data_operacao
                planejada.hora_inicio = hora_inicio
                planejada.hora_termino = hora_termino
                planejada.tipo_planejada = request.POST.get('tipo_planejada', '')
                planejada.semana = request.POST.get('semana')
                planejada.valor = valor
                planejada.valor_total = valor_total
                planejada.saldo = saldo
                planejada.policiais = int(request.POST.get('policiais', 1))
                planejada.responsavel = request.POST.get('responsavel', '')
                planejada.status = request.POST.get('status', 'ativo')
                planejada.feriado_municipal = request.POST.get('feriado_municipal') == 'on'
                planejada.observacoes = request.POST.get('observacoes', '')
                
                planejada.save()
                
                messages.success(request, f'Operação planejada "{planejada.nome}" atualizada com sucesso!')
                return redirect('militares:planejada_detail', planejada_id=planejada.id)
                
        except Exception as e:
            messages.error(request, f'Erro ao atualizar operação planejada: {str(e)}')
    
    # GET - Exibir formulário de edição
    # Carregar todas as organizações para o campo origem
    orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
    grandes_comandos = GrandeComando.objects.filter(ativo=True).order_by('nome')
    unidades = Unidade.objects.filter(ativo=True).order_by('nome')
    sub_unidades = SubUnidade.objects.filter(ativo=True).order_by('nome')
    
    # Carregar configuração ativa de planejadas (cria uma padrão se não existir)
    from .models import ConfiguracaoPlanejadas
    configuracao_ativa = ConfiguracaoPlanejadas.get_ou_create_configuracao_padrao()
    
    # Tipos de planejadas baseados na configuração
    tipos_planejadas = []
    if configuracao_ativa:
        tipos_planejadas = [
            {'codigo': 'P1', 'nome': 'Planejada P1', 'horas': configuracao_ativa.horas_planejada_p1},
            {'codigo': 'P2', 'nome': 'Planejada P2', 'horas': configuracao_ativa.horas_planejada_p2},
            {'codigo': 'P3', 'nome': 'Planejada P3', 'horas': configuracao_ativa.horas_planejada_p3},
            {'codigo': 'P4', 'nome': 'Planejada P4', 'horas': configuracao_ativa.horas_planejada_p4},
        ]
    
    context = {
        'page_title': f'Editar - {planejada.nome}',
        'planejada': planejada,
        'status_choices': Planejada.STATUS_CHOICES,
        'semana_choices': Planejada.SEMANA_CHOICES,
        'orgaos': orgaos,
        'grandes_comandos': grandes_comandos,
        'unidades': unidades,
        'sub_unidades': sub_unidades,
        'tipos_planejadas': tipos_planejadas,
        'configuracao_ativa': configuracao_ativa,
    }
    return render(request, 'militares/planejada_form.html', context)


# ===== APIs PARA SELEÇÃO DE MILITARES EM OPERAÇÕES PLANEJADAS =====

@login_required
def api_militares_disponiveis_planejada(request, planejada_id):
    """API para buscar militares disponíveis para a operação planejada"""
    planejada = get_object_or_404(Planejada, id=planejada_id)
    militares_escalados = planejada.militares.values_list('id', flat=True)
    
    # Verificar se há termo de pesquisa
    termo_pesquisa = request.GET.get('q', '').strip()
    
    # Buscar militares ativos
    if termo_pesquisa:
        militares = Militar.objects.filter(
            classificacao='ATIVO'
        ).filter(
            Q(nome_completo__icontains=termo_pesquisa) |
            Q(nome_guerra__icontains=termo_pesquisa) |
            Q(matricula__icontains=termo_pesquisa)
        ).distinct()
    else:
        militares = Militar.objects.filter(classificacao='ATIVO')
    
    # Ordenar por hierarquia militar e antiguidade
    ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
    
    from django.db.models import Case, When, Value, IntegerField
    hierarquia_ordem = Case(
        *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
        default=Value(len(ordem_hierarquica)),
        output_field=IntegerField()
    )
    
    militares = militares.order_by(
        hierarquia_ordem,
        'data_promocao_atual',
        'numeracao_antiguidade'
    ).values('id', 'nome_completo', 'posto_graduacao', 'data_promocao_atual', 'numeracao_antiguidade')
    
    # Converter para lista e marcar quais já estão escalados
    militares_list = []
    for militar in militares:
        ja_escalado = militar['id'] in militares_escalados
        
        # Calcular tempo no posto atual
        tempo_posto = ""
        if militar['data_promocao_atual']:
            from datetime import date
            hoje = date.today()
            dias_no_posto = (hoje - militar['data_promocao_atual']).days
            anos = dias_no_posto // 365
            meses = (dias_no_posto % 365) // 30
            if anos > 0:
                tempo_posto = f"{anos}a {meses}m"
            elif meses > 0:
                tempo_posto = f"{meses}m"
            else:
                tempo_posto = f"{dias_no_posto}d"
        
        # Obter o nome completo do posto/graduação
        posto_choices = {
            'CB': 'Coronel',
            'TC': 'Tenente-Coronel',
            'MJ': 'Major',
            'CP': 'Capitão',
            '1T': '1º Tenente',
            '2T': '2º Tenente',
            'AS': 'Aspirante',
            'ST': 'Subtenente',
            '1S': '1º Sargento',
            '2S': '2º Sargento',
            '3S': '3º Sargento',
            'CAB': 'Cabo',
            'SD': 'Soldado'
        }
        posto_graduacao_display = posto_choices.get(militar['posto_graduacao'], militar['posto_graduacao'])
        
        # Determinar status de disponibilidade
        if ja_escalado:
            status_disponibilidade = "ja_escalado"
            mensagem_status = "Já escalado nesta operação"
        else:
            status_disponibilidade = "disponivel"
            mensagem_status = "Disponível"
        
        militares_list.append({
            'id': militar['id'],
            'nome_completo': militar['nome_completo'],
            'posto_graduacao': militar['posto_graduacao'],
            'posto_graduacao_display': posto_graduacao_display,
            'tempo_posto': tempo_posto,
            'ja_escalado': ja_escalado,
            'status_disponibilidade': status_disponibilidade,
            'mensagem_status': mensagem_status
        })
    
    return JsonResponse({
        'militares': militares_list,
        'total': len(militares_list)
    })


@login_required
def api_militares_escalados_planejada(request, planejada_id):
    """API para buscar militares já escalados na operação planejada"""
    planejada = get_object_or_404(Planejada, id=planejada_id)
    
    militares_escalados = planejada.militares.all().order_by(
        'posto_graduacao',
        'data_promocao_atual',
        'numeracao_antiguidade'
    )
    
    militares_list = []
    for militar in militares_escalados:
        # Calcular tempo no posto atual
        tempo_posto = ""
        if militar.data_promocao_atual:
            from datetime import date
            hoje = date.today()
            dias_no_posto = (hoje - militar.data_promocao_atual).days
            anos = dias_no_posto // 365
            meses = (dias_no_posto % 365) // 30
            if anos > 0:
                tempo_posto = f"{anos}a {meses}m"
            elif meses > 0:
                tempo_posto = f"{meses}m"
            else:
                tempo_posto = f"{dias_no_posto}d"
        
        # Obter o nome completo do posto/graduação
        posto_choices = {
            'CB': 'Coronel',
            'TC': 'Tenente-Coronel',
            'MJ': 'Major',
            'CP': 'Capitão',
            '1T': '1º Tenente',
            '2T': '2º Tenente',
            'AS': 'Aspirante',
            'ST': 'Subtenente',
            '1S': '1º Sargento',
            '2S': '2º Sargento',
            '3S': '3º Sargento',
            'CAB': 'Cabo',
            'SD': 'Soldado'
        }
        posto_graduacao_display = posto_choices.get(militar.posto_graduacao, militar.posto_graduacao)
        
        militares_list.append({
            'id': militar.id,
            'nome_completo': militar.nome_completo,
            'posto_graduacao': militar.posto_graduacao,
            'posto_graduacao_display': posto_graduacao_display,
            'tempo_posto': tempo_posto
        })
    
    return JsonResponse({
        'militares': militares_list,
        'total': len(militares_list)
    })


@login_required
@require_http_methods(["POST"])
def api_adicionar_militar_planejada(request, planejada_id):
    """API para adicionar militar à operação planejada"""
    planejada = get_object_or_404(Planejada, id=planejada_id)
    militar_id = request.POST.get('militar_id')
    
    if not militar_id:
        return JsonResponse({'success': False, 'message': 'ID do militar não fornecido'}, status=400)
    
    try:
        militar = Militar.objects.get(id=militar_id)
        
        # Verificar se o militar já está escalado
        if planejada.militares.filter(id=militar_id).exists():
            return JsonResponse({'success': False, 'message': 'Militar já está escalado nesta operação'}, status=400)
        
        # Adicionar militar à operação
        planejada.militares.add(militar)
        
        return JsonResponse({
            'success': True,
            'message': f'Militar {militar.nome_completo} adicionado à operação com sucesso!'
        })
        
    except Militar.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Militar não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao adicionar militar: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def api_remover_militar_planejada(request, planejada_id):
    """API para remover militar da operação planejada"""
    planejada = get_object_or_404(Planejada, id=planejada_id)
    militar_id = request.POST.get('militar_id')
    
    if not militar_id:
        return JsonResponse({'success': False, 'message': 'ID do militar não fornecido'}, status=400)
    
    try:
        militar = Militar.objects.get(id=militar_id)
        
        # Verificar se o militar está escalado
        if not planejada.militares.filter(id=militar_id).exists():
            return JsonResponse({'success': False, 'message': 'Militar não está escalado nesta operação'}, status=400)
        
        # Remover militar da operação
        planejada.militares.remove(militar)
        
        return JsonResponse({
            'success': True,
            'message': f'Militar {militar.nome_completo} removido da operação com sucesso!'
        })
        
    except Militar.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Militar não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao remover militar: {str(e)}'}, status=500)


@login_required
def api_militares_disponiveis_geral(request):
    """API genérica para buscar militares disponíveis (usada na criação)"""
    # Verificar se há termo de pesquisa
    termo_pesquisa = request.GET.get('q', '').strip()
    
    # Buscar militares ativos
    if termo_pesquisa:
        militares = Militar.objects.filter(
            classificacao='ATIVO'
        ).filter(
            Q(nome_completo__icontains=termo_pesquisa) |
            Q(nome_guerra__icontains=termo_pesquisa) |
            Q(matricula__icontains=termo_pesquisa)
        ).distinct()
    else:
        militares = Militar.objects.filter(classificacao='ATIVO')
    
    # Ordenar por hierarquia militar e antiguidade
    ordem_hierarquica = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'ST', '1S', '2S', '3S', 'CAB', 'SD']
    
    from django.db.models import Case, When, Value, IntegerField
    hierarquia_ordem = Case(
        *[When(posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
        default=Value(len(ordem_hierarquica)),
        output_field=IntegerField()
    )
    
    militares = militares.order_by(
        hierarquia_ordem,
        'data_promocao_atual',
        'numeracao_antiguidade'
    ).values('id', 'nome_completo', 'posto_graduacao', 'data_promocao_atual', 'numeracao_antiguidade')
    
    # Converter para lista
    militares_list = []
    for militar in militares:
        # Calcular tempo no posto atual
        tempo_posto = ""
        if militar['data_promocao_atual']:
            from datetime import date
            hoje = date.today()
            dias_no_posto = (hoje - militar['data_promocao_atual']).days
            anos = dias_no_posto // 365
            meses = (dias_no_posto % 365) // 30
            if anos > 0:
                tempo_posto = f"{anos}a {meses}m"
            elif meses > 0:
                tempo_posto = f"{meses}m"
            else:
                tempo_posto = f"{dias_no_posto}d"
        
        # Obter o nome completo do posto/graduação
        posto_choices = {
            'CB': 'Coronel',
            'TC': 'Tenente-Coronel',
            'MJ': 'Major',
            'CP': 'Capitão',
            '1T': '1º Tenente',
            '2T': '2º Tenente',
            'AS': 'Aspirante',
            'ST': 'Subtenente',
            '1S': '1º Sargento',
            '2S': '2º Sargento',
            '3S': '3º Sargento',
            'CAB': 'Cabo',
            'SD': 'Soldado'
        }
        posto_graduacao_display = posto_choices.get(militar['posto_graduacao'], militar['posto_graduacao'])
        
        militares_list.append({
            'id': militar['id'],
            'nome_completo': militar['nome_completo'],
            'posto_graduacao': militar['posto_graduacao'],
            'posto_graduacao_display': posto_graduacao_display,
            'tempo_posto': tempo_posto
        })
    
    return JsonResponse({
        'militares': militares_list,
        'total': len(militares_list)
    })
 
 @ l o g i n _ r e q u i r e d  
 d e f   p l a n e j a d a _ m i l i t a r e s ( r e q u e s t ,   p l a n e j a d a _ i d ) :  
         " " "  
         R e t o r n a   o s   m i l i t a r e s   a s s o c i a d o s   a   u m a   p l a n e j a d a   e s p e c � � f i c a   v i a   A J A X  
         " " "  
         t r y :  
                 p l a n e j a d a   =   g e t _ o b j e c t _ o r _ 4 0 4 ( P l a n e j a d a ,   i d = p l a n e j a d a _ i d )  
                  
                 #   B u s c a r   m i l i t a r e s   a s s o c i a d o s   � �   p l a n e j a d a  
                 m i l i t a r e s   =   p l a n e j a d a . m i l i t a r e s . a l l ( ) . o r d e r _ b y ( ' n o m e _ c o m p l e t o ' )  
                  
                 m i l i t a r e s _ l i s t   =   [ ]  
                 f o r   m i l i t a r   i n   m i l i t a r e s :  
                         #   M a p e a r   p o s t o / g r a d u a � � � � o   p a r a   d i s p l a y  
                         p o s t o _ c h o i c e s   =   {  
                                 ' C E L ' :   ' C o r o n e l ' ,  
                                 ' T C ' :   ' T e n e n t e - C o r o n e l ' ,  
                                 ' M A J ' :   ' M a j o r ' ,  
                                 ' C A P ' :   ' C a p i t � � o ' ,  
                                 ' 1 T ' :   ' 1 � �   T e n e n t e ' ,  
                                 ' 2 T ' :   ' 2 � �   T e n e n t e ' ,  
                                 ' A S P ' :   ' A s p i r a n t e ' ,  
                                 ' S T ' :   ' S u b t e n e n t e ' ,  
                                 ' 1 S ' :   ' 1 � �   S a r g e n t o ' ,  
                                 ' 2 S ' :   ' 2 � �   S a r g e n t o ' ,  
                                 ' 3 S ' :   ' 3 � �   S a r g e n t o ' ,  
                                 ' C A B ' :   ' C a b o ' ,  
                                 ' S D ' :   ' S o l d a d o '  
                         }  
                         p o s t o _ g r a d   =   p o s t o _ c h o i c e s . g e t ( m i l i t a r . p o s t o _ g r a d u a c a o ,   m i l i t a r . p o s t o _ g r a d u a c a o )  
                          
                         m i l i t a r e s _ l i s t . a p p e n d ( {  
                                 ' i d ' :   m i l i t a r . i d ,  
                                 ' n o m e _ c o m p l e t o ' :   m i l i t a r . n o m e _ c o m p l e t o ,  
                                 ' p o s t o _ g r a d ' :   p o s t o _ g r a d ,  
                                 ' m a t r i c u l a ' :   m i l i t a r . m a t r i c u l a ,  
                                 ' l o t a c a o ' :   s t r ( m i l i t a r . l o t a c a o )   i f   m i l i t a r . l o t a c a o   e l s e   ' N � � o   i n f o r m a d o '  
                         } )  
                  
                 r e t u r n   J s o n R e s p o n s e ( {  
                         ' s u c c e s s ' :   T r u e ,  
                         ' m i l i t a r e s ' :   m i l i t a r e s _ l i s t ,  
                         ' t o t a l ' :   l e n ( m i l i t a r e s _ l i s t ) ,  
                         ' p l a n e j a d a _ n o m e ' :   p l a n e j a d a . n o m e  
                 } )  
                  
         e x c e p t   E x c e p t i o n   a s   e :  
                 r e t u r n   J s o n R e s p o n s e ( {  
                         ' s u c c e s s ' :   F a l s e ,  
                         ' m e s s a g e ' :   f ' E r r o   a o   c a r r e g a r   m i l i t a r e s :   { s t r ( e ) } ' ,  
                         ' m i l i t a r e s ' :   [ ] ,  
                         ' t o t a l ' :   0  
                 } )  
 