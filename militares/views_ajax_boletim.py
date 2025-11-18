from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from militares.models import Publicacao
import json

@login_required
def devolver_nota_origem_ajax(request, pk):
    """AJAX: Devolver nota para origem removendo do boletim"""
    try:
        nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
        
        # Verificar se a nota está em um boletim
        if not nota.numero_boletim:
            return JsonResponse({
                'success': False,
                'error': 'Esta nota não está incluída em nenhum boletim'
            })
        
        # Verificar se a nota está em um boletim disponibilizado
        boletim = Publicacao.objects.filter(
            numero=nota.numero_boletim,
            tipo='BOLETIM_OSTENSIVO'
        ).first()
        
        if boletim and boletim.data_disponibilizacao:
            return JsonResponse({
                'success': False,
                'error': 'Esta nota não pode ser devolvida pois o boletim já foi disponibilizado.'
            })
        
        # Remover a nota do boletim
        boletim_numero = nota.numero_boletim
        nota.numero_boletim = None
        nota.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Nota {nota.numero} devolvida para origem com sucesso!'
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Nota não encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao devolver nota: {str(e)}'
        })

@login_required
def transferir_nota_boletim_ajax(request, pk):
    """AJAX: Transferir nota para outro boletim"""
    from datetime import datetime, date
    
    try:
        nota = get_object_or_404(Publicacao, pk=pk, tipo='NOTA')
        
        # Verificar se a nota está em um boletim disponibilizado
        if nota.numero_boletim:
            boletim_atual = Publicacao.objects.filter(
                numero=nota.numero_boletim,
                tipo='BOLETIM_OSTENSIVO'
            ).first()
            
            if boletim_atual and boletim_atual.data_disponibilizacao:
                return JsonResponse({
                    'success': False,
                    'error': 'Esta nota não pode ser transferida pois o boletim já foi disponibilizado.'
                })
        
        if request.method != 'POST':
            return JsonResponse({
                'success': False,
                'error': 'Método não permitido'
            })
        
        data = json.loads(request.body)
        boletim_destino = data.get('boletim_destino')
        
        if not boletim_destino:
            return JsonResponse({
                'success': False,
                'error': 'Número do boletim de destino é obrigatório'
            })
        
        # Verificar se o boletim de destino existe
        try:
            boletim_destino_obj = Publicacao.objects.get(
                numero=boletim_destino,
                tipo='BOLETIM_OSTENSIVO'
            )
        except Publicacao.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Boletim {boletim_destino} não encontrado'
            })
        
        # VALIDAÇÃO CRÍTICA: Só permitir transferir para boletim do dia atual
        data_hoje = date.today()
        data_boletim_destino = boletim_destino_obj.data_boletim if boletim_destino_obj.data_boletim else boletim_destino_obj.data_criacao.date()
        
        if data_boletim_destino != data_hoje:
            return JsonResponse({
                'success': False,
                'error': f'Não é possível transferir notas para boletins de datas diferentes de hoje. Boletim de destino é de {data_boletim_destino.strftime("%d/%m/%Y")} e hoje é {data_hoje.strftime("%d/%m/%Y")}. As notas só podem ser transferidas para o boletim do dia atual.'
            })
        
        # Transferir a nota
        nota.numero_boletim = boletim_destino
        nota.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Nota {nota.numero} transferida para o boletim {boletim_destino} com sucesso!'
        })
        
    except Publicacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Nota não encontrada'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Dados inválidos'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao transferir nota: {str(e)}'
        })
