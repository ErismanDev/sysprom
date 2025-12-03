from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Militar


def get_posto_display(posto_code):
    """Retorna o display de um posto baseado no código"""
    POSTO_CHOICES = {
        'AS': 'Aspirante a Oficial',
        'AA': 'Aluno de Adaptação',
        '2T': '2º Tenente',
        '1T': '1º Tenente',
        'CP': 'Capitão',
        'MJ': 'Major',
        'TC': 'Tenente-Coronel',
        'CB': 'Coronel',
        'ST': 'Subtenente',
        '1S': '1º Sargento',
        '2S': '2º Sargento',
        '3S': '3º Sargento',
        'CAB': 'Cabo',
        'SD': 'Soldado',
    }
    return POSTO_CHOICES.get(posto_code, '')


@require_GET
@login_required
def militar_info_ajax(request):
    """Retorna informações do militar para o formulário de promoção (posto atual e próxima promoção)"""
    militar_id = request.GET.get('militar_id')
    is_historica = request.GET.get('is_historica', 'false').lower() == 'true'
    
    if not militar_id:
        return JsonResponse({'error': 'ID não informado'}, status=400)
    try:
        militar = Militar.objects.get(pk=militar_id)
        
        # Para promoções históricas, permitir qualquer posto (inclusive coronel)
        if militar.posto_graduacao == 'CB' and not is_historica:
            return JsonResponse({
                'error': 'Coronéis não podem ser promovidos para posto superior (último posto na hierarquia). Use "Promoção Histórica" se necessário.',
                'posto_atual': militar.posto_graduacao,
                'posto_atual_display': militar.get_posto_graduacao_display(),
                'proxima_promocao': None,
                'proxima_promocao_display': '',
                'aviso_historica': True
            })
        
        proxima = militar.proxima_promocao()
        return JsonResponse({
            'posto_atual': militar.posto_graduacao,
            'posto_atual_display': militar.get_posto_graduacao_display(),
            'proxima_promocao': proxima,
            'proxima_promocao_display': get_posto_display(proxima) if proxima else '',
            'permite_historica': militar.posto_graduacao == 'CB'
        })
    except Militar.DoesNotExist:
        return JsonResponse({'error': 'Militar não encontrado'}, status=404)


@require_GET
@login_required
def militar_info_completa_ajax(request):
    """Retorna informações completas do militar para formulários de edição"""
    militar_id = request.GET.get('militar_id')
    
    if not militar_id:
        return JsonResponse({'error': 'ID não informado'}, status=400)
    
    try:
        militar = Militar.objects.get(pk=militar_id)
        
        # Buscar lotação atual
        lotacao_data = None
        try:
            lotacao_atual = militar.lotacao_atual
            if lotacao_atual and hasattr(lotacao_atual, 'orgao'):
                lotacao_data = {
                    'orgao_id': lotacao_atual.orgao.id if lotacao_atual.orgao else None,
                    'orgao_nome': str(lotacao_atual.orgao) if lotacao_atual.orgao else None,
                    'grande_comando_id': lotacao_atual.grande_comando.id if lotacao_atual.grande_comando else None,
                    'grande_comando_nome': str(lotacao_atual.grande_comando) if lotacao_atual.grande_comando else None,
                    'unidade_id': lotacao_atual.unidade.id if lotacao_atual.unidade else None,
                    'unidade_nome': str(lotacao_atual.unidade) if lotacao_atual.unidade else None,
                    'sub_unidade_id': lotacao_atual.sub_unidade.id if lotacao_atual.sub_unidade else None,
                    'sub_unidade_nome': str(lotacao_atual.sub_unidade) if lotacao_atual.sub_unidade else None,
                }
        except Exception:
            # Se houver erro ao buscar lotação, definir como None
            lotacao_data = None
        
        # Preparar dados do militar
        militar_data = {
            'id': militar.id,
            'nome_completo': militar.nome_completo,
            'nome_guerra': militar.nome_guerra or '',
            'matricula': militar.matricula,
            'cpf': militar.cpf or '',
            'posto_graduacao': militar.posto_graduacao,
            'posto': militar.posto_graduacao,
            'posto_graduacao_display': militar.get_posto_graduacao_display(),
            'posto_display': militar.get_posto_graduacao_display(),
            'email': militar.email or '',
            'telefone': militar.telefone or '',
            'celular': militar.celular or '',
            'quadro': militar.quadro,
            'quadro_display': militar.get_quadro_display(),
            'situacao': militar.situacao,
            'situacao_display': militar.get_situacao_display(),
            'lotacao_atual': lotacao_data,
            'foto_url': militar.foto.url if militar.foto else None
        }
        
        # Adicionar campos de endereço se existirem no modelo
        # Verificar se o modelo tem atributos de endereço
        campos_endereco = ['endereco', 'logradouro', 'rua', 'bairro', 'numero', 'complemento', 
                          'cidade', 'uf', 'estado', 'cep']
        for campo in campos_endereco:
            if hasattr(militar, campo):
                try:
                    valor = getattr(militar, campo, None)
                    # Sempre incluir o campo, mesmo se vazio
                    if valor is not None and valor != '':
                        # Converter para string, tratando casos especiais
                        if isinstance(valor, str):
                            militar_data[campo] = valor
                        else:
                            militar_data[campo] = str(valor)
                    else:
                        militar_data[campo] = ''
                except Exception as e:
                    # Se houver erro ao acessar o campo, definir como vazio
                    militar_data[campo] = ''
        
        return JsonResponse({
            'success': True,
            'militar': militar_data
        })
    except Militar.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Militar não encontrado'}, status=404)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return JsonResponse({
            'success': False, 
            'error': f'Erro ao buscar militar: {str(e)}',
            'traceback': error_trace
        }, status=500)


@require_GET
@login_required
def militar_data_ingresso_ajax(request, militar_id):
    """Retorna a data de ingresso do militar para cálculo de decênios"""
    try:
        militar = Militar.objects.get(pk=militar_id)
        
        if not militar.data_ingresso:
            return JsonResponse({'error': 'Data de ingresso não informada para este militar'}, status=404)
        
        return JsonResponse({
            'data_ingresso': militar.data_ingresso.strftime('%Y-%m-%d')
        })
    except Militar.DoesNotExist:
        return JsonResponse({'error': 'Militar não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erro ao buscar data de ingresso: {str(e)}'}, status=500)


@require_POST
@login_required
@csrf_exempt
def update_voluntario_status(request):
    """Atualiza o status de voluntário do militar logado"""
    try:
        # Verificar se o usuário tem um militar associado
        if not hasattr(request.user, 'militar') or not request.user.militar:
            return JsonResponse({
                'success': False, 
                'message': 'Usuário não possui militar associado'
            }, status=400)
        
        # Obter dados do JSON
        data = json.loads(request.body)
        voluntario_status = data.get('voluntario_status')
        
        if voluntario_status not in ['SIM', 'NAO']:
            return JsonResponse({
                'success': False,
                'message': 'Status de voluntário inválido'
            }, status=400)
        
        # Atualizar o status
        militar = request.user.militar
        militar.voluntario_operacoes = voluntario_status
        militar.save(update_fields=['voluntario_operacoes'])
        
        # Mensagem de sucesso
        if voluntario_status == 'SIM':
            message = 'Você foi registrado como voluntário para operações planejadas!'
        else:
            message = 'Você não é mais voluntário para operações planejadas.'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'voluntario_status': voluntario_status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dados inválidos recebidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        }, status=500) 