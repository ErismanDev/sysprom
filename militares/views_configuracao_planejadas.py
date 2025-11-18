"""
Views para configuração de planejadas
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import ConfiguracaoPlanejadas
from datetime import datetime


@login_required
def configuracao_planejadas_list(request):
    """Lista todas as configurações de planejadas"""
    configuracao_ativa = ConfiguracaoPlanejadas.get_configuracao_ativa()
    configuracoes = ConfiguracaoPlanejadas.objects.all().order_by('-data_criacao')
    
    context = {
        'title': 'Configurações de Planejadas',
        'page_title': 'Configurações de Planejadas',
        'configuracao_ativa': configuracao_ativa,
        'configuracoes': configuracoes,
    }
    
    return render(request, 'militares/configuracao_planejadas_list.html', context)


@login_required
def configuracao_planejadas_create(request):
    """Cria nova configuração de planejadas"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Desativar configuração atual se existir
                ConfiguracaoPlanejadas.objects.filter(ativo=True).update(ativo=False)
                
                # Criar nova configuração
                configuracao = ConfiguracaoPlanejadas.objects.create(
                    quantidade_planejadas_por_militar_mes=int(request.POST.get('quantidade_planejadas_por_militar_mes', 4)),
                    valor_planejada_normal=float(request.POST.get('valor_por_hora_normal', 0.00)),
                    valor_planejada_fim_semana=float(request.POST.get('valor_por_hora_fds', 0.00)),
                    valor_por_hora_normal=float(request.POST.get('valor_por_hora_normal', 0.00)),
                    valor_por_hora_fds=float(request.POST.get('valor_por_hora_fds', 0.00)),
                    horas_planejada_p1=int(request.POST.get('horas_planejada_p1', 6)),
                    horas_planejada_p2=int(request.POST.get('horas_planejada_p2', 12)),
                    horas_planejada_p3=int(request.POST.get('horas_planejada_p3', 18)),
                    horas_planejada_p4=int(request.POST.get('horas_planejada_p4', 24)),
                    intervalo_turno_6h=int(request.POST.get('intervalo_turno_6h', 6)),
                    intervalo_turno_12h=int(request.POST.get('intervalo_turno_12h', 12)),
                    intervalo_turno_18h=int(request.POST.get('intervalo_turno_18h', 18)),
                    intervalo_turno_24h=int(request.POST.get('intervalo_turno_24h', 24)),
                    permitir_flexibilizacao_p1=request.POST.get('permitir_flexibilizacao_p1') == 'on',
                    permitir_flexibilizacao_p2=request.POST.get('permitir_flexibilizacao_p2') == 'on',
                    permitir_flexibilizacao_p3=request.POST.get('permitir_flexibilizacao_p3') == 'on',
                    permitir_flexibilizacao_p4=request.POST.get('permitir_flexibilizacao_p4') == 'on',
                    permitir_flexibilizacao_validacoes=request.POST.get('permitir_flexibilizacao_validacoes') == 'on',
                    observacoes=request.POST.get('observacoes', ''),
                    ativo=True
                )
                
                messages.success(request, 'Configuração de planejadas criada com sucesso!')
                return redirect('militares:configuracao_planejadas_list')
                
        except ValidationError as e:
            messages.error(request, f'Erro de validação: {str(e)}')
            print(f"Erro de validação: {str(e)}")  # Debug
        except Exception as e:
            messages.error(request, f'Erro ao criar configuração: {str(e)}')
            print(f"Erro ao criar configuração: {str(e)}")  # Debug
            import traceback
            traceback.print_exc()  # Debug completo
    
    # Criar configuração padrão se não existir
    configuracao_padrao = ConfiguracaoPlanejadas.get_ou_create_configuracao_padrao()
    
    context = {
        'title': 'Nova Configuração de Planejadas',
        'page_title': 'Nova Configuração de Planejadas',
        'configuracao_padrao': configuracao_padrao,
    }
    
    return render(request, 'militares/configuracao_planejadas_form.html', context)


@login_required
def configuracao_planejadas_edit(request, pk):
    """Edita configuração de planejadas existente"""
    try:
        configuracao = get_object_or_404(ConfiguracaoPlanejadas, pk=pk)
    except:
        # Se o ID não existir, redireciona para a configuração ativa
        configuracao_ativa = ConfiguracaoPlanejadas.get_configuracao_ativa()
        if configuracao_ativa:
            messages.warning(request, f'Configuração com ID {pk} não encontrada. Redirecionando para a configuração ativa.')
            return redirect('militares:configuracao_planejadas_edit', pk=configuracao_ativa.id)
        else:
            messages.error(request, f'Configuração com ID {pk} não encontrada e nenhuma configuração ativa disponível.')
            return redirect('militares:configuracao_planejadas_list')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Se for ativar esta configuração, desativar as outras
                if request.POST.get('ativo') == 'on':
                    ConfiguracaoPlanejadas.objects.filter(ativo=True).exclude(id=configuracao.id).update(ativo=False)
                
                # Converter valores de string para os tipos corretos
                valor_normal_str = request.POST.get('valor_por_hora_normal', '0.00').replace(',', '.')
                valor_fds_str = request.POST.get('valor_por_hora_fds', '0.00').replace(',', '.')
                
                configuracao.quantidade_planejadas_por_militar_mes = int(request.POST.get('quantidade_planejadas_por_militar_mes', 4))
                configuracao.valor_planejada_normal = float(valor_normal_str)
                configuracao.valor_planejada_fim_semana = float(valor_fds_str)
                configuracao.valor_por_hora_normal = float(valor_normal_str)
                configuracao.valor_por_hora_fds = float(valor_fds_str)
                configuracao.horas_planejada_p1 = int(request.POST.get('horas_planejada_p1', 6))
                configuracao.horas_planejada_p2 = int(request.POST.get('horas_planejada_p2', 12))
                configuracao.horas_planejada_p3 = int(request.POST.get('horas_planejada_p3', 18))
                configuracao.horas_planejada_p4 = int(request.POST.get('horas_planejada_p4', 24))
                configuracao.intervalo_turno_6h = int(request.POST.get('intervalo_turno_6h', 6))
                configuracao.intervalo_turno_12h = int(request.POST.get('intervalo_turno_12h', 12))
                configuracao.intervalo_turno_18h = int(request.POST.get('intervalo_turno_18h', 18))
                configuracao.intervalo_turno_24h = int(request.POST.get('intervalo_turno_24h', 24))
                configuracao.permitir_flexibilizacao_p1 = request.POST.get('permitir_flexibilizacao_p1') == 'on'
                configuracao.permitir_flexibilizacao_p2 = request.POST.get('permitir_flexibilizacao_p2') == 'on'
                configuracao.permitir_flexibilizacao_p3 = request.POST.get('permitir_flexibilizacao_p3') == 'on'
                configuracao.permitir_flexibilizacao_p4 = request.POST.get('permitir_flexibilizacao_p4') == 'on'
                configuracao.permitir_flexibilizacao_validacoes = request.POST.get('permitir_flexibilizacao_validacoes') == 'on'
                configuracao.observacoes = request.POST.get('observacoes', '')
                configuracao.ativo = request.POST.get('ativo') == 'on'
                
                # Validar antes de salvar
                configuracao.full_clean()
                configuracao.save()
                
                messages.success(request, 'Configuração de planejadas atualizada com sucesso!')
                return redirect('militares:configuracao_planejadas_list')
                
        except ValidationError as e:
            messages.error(request, f'Erro de validação: {str(e)}')
            import traceback
            print(f"Erro de validação: {traceback.format_exc()}")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar configuração: {str(e)}')
            import traceback
            print(f"Erro ao salvar: {traceback.format_exc()}")
    
    context = {
        'title': 'Editar Configuração de Planejadas',
        'page_title': 'Editar Configuração de Planejadas',
        'configuracao': configuracao,
    }
    
    return render(request, 'militares/configuracao_planejadas_form.html', context)


@login_required
def configuracao_planejadas_detail(request, pk):
    """Detalhes da configuração de planejadas"""
    try:
        configuracao = get_object_or_404(ConfiguracaoPlanejadas, pk=pk)
    except:
        # Se o ID não existir, redireciona para a configuração ativa
        configuracao_ativa = ConfiguracaoPlanejadas.get_configuracao_ativa()
        if configuracao_ativa:
            messages.warning(request, f'Configuração com ID {pk} não encontrada. Redirecionando para a configuração ativa.')
            return redirect('militares:configuracao_planejadas_detail', pk=configuracao_ativa.id)
        else:
            messages.error(request, f'Configuração com ID {pk} não encontrada e nenhuma configuração ativa disponível.')
            return redirect('militares:configuracao_planejadas_list')
    
    context = {
        'title': 'Detalhes da Configuração de Planejadas',
        'page_title': 'Detalhes da Configuração de Planejadas',
        'configuracao': configuracao,
    }
    
    return render(request, 'militares/configuracao_planejadas_detail.html', context)


@login_required
@require_http_methods(["POST"])
def configuracao_planejadas_activate(request, pk):
    """Ativa uma configuração de planejadas"""
    try:
        with transaction.atomic():
            # Desativar todas as configurações
            ConfiguracaoPlanejadas.objects.filter(ativo=True).update(ativo=False)
            
            # Ativar a configuração selecionada
            configuracao = get_object_or_404(ConfiguracaoPlanejadas, pk=pk)
            configuracao.ativo = True
            configuracao.save()
            
            messages.success(request, f'Configuração ativada com sucesso!')
            
    except Exception as e:
        messages.error(request, f'Erro ao ativar configuração: {str(e)}')
    
    return redirect('militares:configuracao_planejadas_list')


@login_required
@require_http_methods(["POST"])
def configuracao_planejadas_delete(request, pk):
    """Exclui uma configuração de planejadas"""
    try:
        configuracao = get_object_or_404(ConfiguracaoPlanejadas, pk=pk)
        
        # Não permitir excluir configuração ativa
        if configuracao.ativo:
            messages.error(request, 'Não é possível excluir a configuração ativa!')
            return redirect('militares:configuracao_planejadas_list')
        
        configuracao.delete()
        messages.success(request, 'Configuração excluída com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao excluir configuração: {str(e)}')
    
    return redirect('militares:configuracao_planejadas_list')


@login_required
def configuracao_planejadas_ajax(request):
    """Retorna configuração ativa via AJAX"""
    try:
        configuracao = ConfiguracaoPlanejadas.get_configuracao_ativa()
        
        if configuracao:
            data = {
                'success': True,
                'configuracao': {
                    'id': configuracao.id,
                    'quantidade_planejadas_por_militar_mes': configuracao.quantidade_planejadas_por_militar_mes,
                    'valor_planejada_normal': float(configuracao.valor_planejada_normal),
                    'valor_planejada_fim_semana': float(configuracao.valor_planejada_fim_semana),
                    'horas_planejada_p1': configuracao.horas_planejada_p1,
                    'horas_planejada_p2': configuracao.horas_planejada_p2,
                    'horas_planejada_p3': configuracao.horas_planejada_p3,
                    'horas_planejada_p4': configuracao.horas_planejada_p4,
                    'intervalo_turno_6h': configuracao.intervalo_turno_6h,
                    'intervalo_turno_12h': configuracao.intervalo_turno_12h,
                    'intervalo_turno_18h': configuracao.intervalo_turno_18h,
                    'intervalo_turno_24h': configuracao.intervalo_turno_24h,
                    'data_criacao': configuracao.data_criacao.strftime('%d/%m/%Y %H:%M'),
                }
            }
        else:
            data = {
                'success': False,
                'message': 'Nenhuma configuração ativa encontrada'
            }
            
    except Exception as e:
        data = {
            'success': False,
            'message': f'Erro ao buscar configuração: {str(e)}'
        }
    
    return JsonResponse(data)


