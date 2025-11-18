"""
Views para o sistema de chat em tempo real
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from .models import Chat, MensagemChat, Militar, Chamada
from datetime import timedelta
import json


def obter_info_militar(usuario):
    """Obtém informações do militar (posto e nome de guerra)"""
    try:
        militar = usuario.militar
        if militar:
            posto = militar.get_posto_graduacao_display() if militar.posto_graduacao else ''
            nome_guerra = militar.nome_guerra if militar.nome_guerra else ''
            if posto and nome_guerra:
                return f"{posto} {nome_guerra}"
            elif posto:
                return posto
            elif nome_guerra:
                return nome_guerra
    except:
        pass
    return usuario.get_full_name() or usuario.username


def obter_foto_militar(usuario):
    """Obtém a foto do militar ou retorna None"""
    try:
        militar = usuario.militar
        if militar and militar.foto:
            return militar.foto.url
    except:
        pass
    return None


def verificar_usuario_online(usuario):
    """Verifica se o usuário está online (tem sessão ativa)"""
    try:
        # Buscar sessões ativas do usuário (não expiradas)
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        for session in sessions:
            try:
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(usuario.id):
                    return True
            except:
                # Se não conseguir decodificar a sessão, continua procurando
                continue
    except Exception as e:
        # Log do erro se necessário
        pass
    return False


@login_required
def chat_list(request):
    """Lista todas as conversas do usuário"""
    usuario = request.user
    
    # Obter todos os chats do usuário
    chats = Chat.obter_chats_usuario(usuario)
    
    # Adicionar informações extras para cada chat
    chats_com_info = []
    for chat in chats:
        outro_participante = chat.obter_outro_participante(usuario)
        ultima_mensagem = chat.obter_ultima_mensagem()
        nao_lidas = chat.contar_mensagens_nao_lidas(usuario)
        outro_online = verificar_usuario_online(outro_participante)
        outro_nome = obter_info_militar(outro_participante)
        
        outro_foto = obter_foto_militar(outro_participante)
        
        chats_com_info.append({
            'chat': chat,
            'outro_participante': outro_participante,
            'outro_nome': outro_nome,
            'outro_foto': outro_foto,
            'outro_online': outro_online,
            'ultima_mensagem': ultima_mensagem,
            'nao_lidas': nao_lidas,
        })
    
    # Lista de usuários para iniciar nova conversa com fotos
    usuarios_disponiveis = []
    usuarios = User.objects.filter(
        is_active=True
    ).exclude(
        id=usuario.id
    ).select_related('militar').order_by('username')
    
    for user_obj in usuarios:
        usuario_foto = obter_foto_militar(user_obj)
        usuario_nome = obter_info_militar(user_obj)
        usuarios_disponiveis.append({
            'usuario': user_obj,
            'foto': usuario_foto,
            'nome': usuario_nome,
        })
    
    context = {
        'chats_com_info': chats_com_info,
        'usuarios_disponiveis': usuarios_disponiveis,
    }
    
    return render(request, 'militares/chat_list.html', context)


@login_required
def chat_detail(request, chat_id):
    """Visualiza e gerencia um chat específico"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        messages.error(request, 'Você não tem acesso a este chat.')
        return redirect('militares:chat_list')
    
    outro_participante = chat.obter_outro_participante(usuario)
    outro_online = verificar_usuario_online(outro_participante)
    outro_nome = obter_info_militar(outro_participante)
    outro_foto = obter_foto_militar(outro_participante)
    usuario_foto = obter_foto_militar(usuario)
    
    # Obter mensagens do chat com informações dos remetentes
    mensagens = MensagemChat.objects.filter(
        chat=chat
    ).select_related('remetente', 'remetente__militar').order_by('data_envio')
    
    # Adicionar foto para cada mensagem
    mensagens_com_foto = []
    for msg in mensagens:
        msg_foto = obter_foto_militar(msg.remetente) if msg.remetente != usuario else usuario_foto
        mensagens_com_foto.append({
            'mensagem': msg,
            'foto': msg_foto,
        })
    
    # Marcar mensagens recebidas como lidas
    MensagemChat.objects.filter(
        chat=chat,
        remetente=outro_participante,
        lida=False
    ).update(
        lida=True,
        data_leitura=timezone.now()
    )
    
    context = {
        'chat': chat,
        'outro_participante': outro_participante,
        'outro_nome': outro_nome,
        'outro_foto': outro_foto,
        'outro_online': outro_online,
        'usuario_foto': usuario_foto,
        'mensagens_com_foto': mensagens_com_foto,
    }
    
    return render(request, 'militares/chat_detail.html', context)


@login_required
def chat_iniciar(request, usuario_id):
    """Inicia uma nova conversa com um usuário"""
    outro_usuario = get_object_or_404(User, id=usuario_id, is_active=True)
    usuario = request.user
    
    if outro_usuario == usuario:
        messages.error(request, 'Você não pode iniciar uma conversa consigo mesmo.')
        return redirect('militares:chat_list')
    
    # Obter ou criar chat
    chat, created = Chat.obter_ou_criar_chat(usuario, outro_usuario)
    
    return redirect('militares:chat_detail', chat_id=chat.id)


@login_required
@require_http_methods(["POST"])
def chat_enviar_mensagem(request, chat_id):
    """Envia uma mensagem no chat (AJAX)"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    mensagem_texto = request.POST.get('mensagem', '').strip()
    
    if not mensagem_texto:
        return JsonResponse({'success': False, 'error': 'A mensagem não pode estar vazia.'}, status=400)
    
    # Criar mensagem
    mensagem = MensagemChat.objects.create(
        chat=chat,
        remetente=usuario,
        mensagem=mensagem_texto
    )
    
    # Atualizar última atualização do chat
    chat.ultima_atualizacao = timezone.now()
    chat.save(update_fields=['ultima_atualizacao'])
    
    remetente_nome = obter_info_militar(usuario)
    remetente_foto = obter_foto_militar(usuario)
    
    return JsonResponse({
        'success': True,
        'mensagem': {
            'id': mensagem.id,
            'texto': mensagem.mensagem,
            'remetente': remetente_nome,
            'remetente_id': usuario.id,
            'remetente_foto': remetente_foto,
            'data_envio': mensagem.data_envio.strftime('%d/%m/%Y %H:%M:%S'),
            'lida': mensagem.lida,
        }
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_enviar_audio(request, chat_id):
    """Envia uma mensagem de áudio no chat (AJAX)"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    audio_file = request.FILES.get('audio')
    duracao = request.POST.get('duracao', 0)
    
    if not audio_file:
        return JsonResponse({'success': False, 'error': 'Nenhum arquivo de áudio foi enviado.'}, status=400)
    
    try:
        duracao_int = int(duracao)
    except:
        duracao_int = None
    
    # Criar mensagem de áudio
    mensagem = MensagemChat.objects.create(
        chat=chat,
        remetente=usuario,
        mensagem='',  # Mensagem vazia para áudio
        audio=audio_file,
        duracao_audio=duracao_int
    )
    
    # Atualizar última atualização do chat
    chat.ultima_atualizacao = timezone.now()
    chat.save(update_fields=['ultima_atualizacao'])
    
    remetente_nome = obter_info_militar(usuario)
    remetente_foto = obter_foto_militar(usuario)
    
    return JsonResponse({
        'success': True,
        'mensagem': {
            'id': mensagem.id,
            'texto': '',
            'audio': mensagem.audio.url if mensagem.audio else None,
            'duracao_audio': mensagem.duracao_audio,
            'remetente': remetente_nome,
            'remetente_id': usuario.id,
            'remetente_foto': remetente_foto,
            'data_envio': mensagem.data_envio.strftime('%d/%m/%Y %H:%M:%S'),
            'lida': mensagem.lida,
        }
    })


@login_required
def chat_api_mensagens(request, chat_id):
    """API para buscar mensagens do chat (AJAX)"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    # Obter última mensagem ID (para buscar apenas novas)
    ultima_mensagem_id = request.GET.get('ultima_id', None)
    
    if ultima_mensagem_id:
        # Buscar apenas novas mensagens (após a última conhecida)
        try:
            ultima_mensagem_id = int(ultima_mensagem_id)
            mensagens = MensagemChat.objects.filter(
                chat=chat,
                id__gt=ultima_mensagem_id
            ).select_related('remetente', 'remetente__militar').order_by('data_envio')
        except ValueError:
            mensagens = MensagemChat.objects.none()
    else:
        # Carregar todas as mensagens do chat (ordenadas do mais antigo ao mais recente)
        mensagens = MensagemChat.objects.filter(
            chat=chat
        ).select_related('remetente', 'remetente__militar').order_by('data_envio')
    
    mensagens_data = []
    for msg in mensagens:
        remetente_nome = obter_info_militar(msg.remetente)
        remetente_foto = obter_foto_militar(msg.remetente)
        mensagens_data.append({
            'id': msg.id,
            'texto': msg.mensagem,
            'audio': msg.audio.url if msg.audio else None,
            'duracao_audio': msg.duracao_audio,
            'remetente': remetente_nome,
            'remetente_id': msg.remetente.id,
            'remetente_foto': remetente_foto,
            'data_envio': msg.data_envio.strftime('%d/%m/%Y %H:%M:%S'),
            'lida': msg.lida,
        })
    
    # Marcar mensagens recebidas como lidas
    outro_participante = chat.obter_outro_participante(usuario)
    MensagemChat.objects.filter(
        chat=chat,
        remetente=outro_participante,
        lida=False
    ).update(
        lida=True,
        data_leitura=timezone.now()
    )
    
    # Obter última mensagem ID se houver mensagens
    ultima_id = None
    if mensagens.exists():
        ultima_id = mensagens.last().id
    
    return JsonResponse({
        'success': True,
        'mensagens': mensagens_data,
        'ultima_id': ultima_id,
    })


@login_required
def chat_api_status_leitura(request, chat_id):
    """API para verificar status de leitura das mensagens enviadas"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    # Obter IDs das mensagens enviadas pelo usuário que foram lidas
    mensagens_lidas = MensagemChat.objects.filter(
        chat=chat,
        remetente=usuario,
        lida=True
    ).values_list('id', flat=True)
    
    return JsonResponse({
        'success': True,
        'mensagens_lidas': list(mensagens_lidas),
    })


@login_required
def chat_api_chats(request):
    """API para buscar lista de chats atualizada (AJAX)"""
    usuario = request.user
    
    chats = Chat.obter_chats_usuario(usuario)
    
    chats_data = []
    for chat in chats:
        outro_participante = chat.obter_outro_participante(usuario)
        ultima_mensagem = chat.obter_ultima_mensagem()
        nao_lidas = chat.contar_mensagens_nao_lidas(usuario)
        outro_online = verificar_usuario_online(outro_participante)
        outro_nome = obter_info_militar(outro_participante)
        
        outro_foto = obter_foto_militar(outro_participante)
        
        chats_data.append({
            'id': chat.id,
            'outro_participante': outro_nome,
            'outro_participante_id': outro_participante.id,
            'outro_foto': outro_foto,
            'outro_online': outro_online,
            'ultima_mensagem': ultima_mensagem.mensagem[:50] + '...' if ultima_mensagem and len(ultima_mensagem.mensagem) > 50 else (ultima_mensagem.mensagem if ultima_mensagem else ''),
            'ultima_mensagem_id': ultima_mensagem.id if ultima_mensagem else None,
            'ultima_mensagem_remetente_id': ultima_mensagem.remetente.id if ultima_mensagem else None,
            'ultima_atualizacao': chat.ultima_atualizacao.strftime('%d/%m/%Y %H:%M'),
            'nao_lidas': nao_lidas,
        })
    
    # Contar total de mensagens não lidas
    total_nao_lidas = sum(chat.contar_mensagens_nao_lidas(usuario) for chat in chats)
    
    return JsonResponse({
        'success': True,
        'chats': chats_data,
        'total_nao_lidas': total_nao_lidas,
    })


@login_required
def chat_api_status_online(request, usuario_id):
    """API para verificar status online de um usuário (AJAX)"""
    try:
        outro_usuario = User.objects.get(id=usuario_id)
        online = verificar_usuario_online(outro_usuario)
        return JsonResponse({
            'success': True,
            'online': online,
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Usuário não encontrado',
        }, status=404)


@login_required
def chat_api_usuarios(request):
    """API para buscar lista de usuários disponíveis para iniciar conversa"""
    usuario = request.user
    
    # Obter usuários ativos
    usuarios = User.objects.filter(
        is_active=True
    ).exclude(
        id=usuario.id
    ).select_related('militar').order_by('username')
    
    # Obter IDs dos usuários já em conversas
    chats = Chat.obter_chats_usuario(usuario)
    ids_em_conversas = set()
    for chat in chats:
        outro = chat.obter_outro_participante(usuario)
        ids_em_conversas.add(outro.id)
    
    usuarios_data = []
    for user_obj in usuarios:
        usuario_foto = obter_foto_militar(user_obj)
        usuario_nome = obter_info_militar(user_obj)
        usuario_online = verificar_usuario_online(user_obj)
        ja_tem_chat = user_obj.id in ids_em_conversas
        
        usuarios_data.append({
            'id': user_obj.id,
            'nome': usuario_nome,
            'foto': usuario_foto,
            'online': usuario_online,
            'email': user_obj.email,
            'ja_tem_chat': ja_tem_chat,
        })
    
    return JsonResponse({
        'success': True,
        'usuarios': usuarios_data,
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_chamada_iniciar(request, chat_id):
    """Inicia uma chamada de voz ou vídeo"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    try:
        # Log para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'Recebendo chamada para chat {chat_id}, body: {request.body.decode("utf-8")[:500]}')
        
        data = json.loads(request.body)
        tipo = data.get('tipo', 'voz')  # 'voz' ou 'video'
        oferta = data.get('oferta', {})
        
        logger.info(f'Tipo: {tipo}, Oferta tipo: {type(oferta)}')
        
        # Se oferta for string, tentar fazer parse
        if isinstance(oferta, str):
            try:
                oferta = json.loads(oferta)
            except:
                oferta = {}
        
        # Garantir que oferta é um dicionário
        if not isinstance(oferta, dict):
            oferta = {}
        
        # Cancelar chamadas antigas (mais de 5 minutos) antes de verificar
        from django.utils import timezone
        from datetime import timedelta
        Chamada.objects.filter(
            chat=chat,
            status__in=['INICIANDO', 'CHAMANDO', 'EM_ANDAMENTO'],
            data_inicio__lt=timezone.now() - timedelta(minutes=5)
        ).update(status='CANCELADA', data_fim=timezone.now())
        
        # Verificar se já existe chamada pendente recente
        chamada_existente = Chamada.objects.filter(
            chat=chat,
            status__in=['INICIANDO', 'CHAMANDO', 'EM_ANDAMENTO']
        ).first()
        
        if chamada_existente:
            # Se a chamada existente foi iniciada pelo mesmo usuário, cancelar e criar nova
            if chamada_existente.iniciador == usuario:
                chamada_existente.status = 'CANCELADA'
                chamada_existente.data_fim = timezone.now()
                chamada_existente.save(update_fields=['status', 'data_fim'])
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Já existe uma chamada em andamento iniciada por outro usuário'
                }, status=400)
        
        # Criar nova chamada
        tipo_chamada = 'VIDEO' if tipo == 'video' else 'VOZ'
        chamada = Chamada.objects.create(
            chat=chat,
            iniciador=usuario,
            tipo=tipo_chamada,
            status='CHAMANDO',
            oferta_sdp=json.dumps(oferta) if oferta else None
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Chamada iniciada',
            'chamada_id': chamada.id,
        })
    except json.JSONDecodeError as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Erro ao processar JSON: {str(e)}',
            'details': traceback.format_exc()
        }, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Erro ao iniciar chamada: {str(e)}',
            'details': traceback.format_exc()
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_chamada_aceitar(request, chat_id):
    """Aceita uma chamada"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    try:
        data = json.loads(request.body)
        resposta_str = data.get('resposta', '{}')
        chamada_id = data.get('chamada_id')
        
        # Parse da resposta se for string
        try:
            resposta = json.loads(resposta_str) if isinstance(resposta_str, str) else resposta_str
        except:
            resposta = {}
        
        # Buscar chamada
        if chamada_id:
            chamada = get_object_or_404(Chamada, id=chamada_id, chat=chat)
        else:
            chamada = Chamada.objects.filter(
                chat=chat,
                status__in=['INICIANDO', 'CHAMANDO']
            ).exclude(iniciador=usuario).first()
        
        if not chamada:
            return JsonResponse({
                'success': False,
                'error': 'Chamada não encontrada'
            }, status=404)
        
        # Atualizar chamada
        chamada.status = 'EM_ANDAMENTO'
        chamada.resposta_sdp = json.dumps(resposta) if resposta else None
        chamada.save(update_fields=['status', 'resposta_sdp'])
        
        return JsonResponse({
            'success': True,
            'message': 'Chamada aceita',
            'chamada_id': chamada.id,
            'oferta': json.loads(chamada.oferta_sdp) if chamada.oferta_sdp else None
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def chat_chamada_pendente(request, chat_id):
    """Verifica se há chamada pendente"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    # Log para debug
    import logging
    logger = logging.getLogger(__name__)
    
    # Primeiro, verificar todas as chamadas do chat para debug
    todas_chamadas = Chamada.objects.filter(chat=chat).order_by('-data_inicio')[:5]
    logger.info(f'Verificando chamadas pendentes - Chat: {chat_id}, Usuário: {usuario.username}')
    logger.info(f'Total de chamadas no chat (últimas 5): {todas_chamadas.count()}')
    for c in todas_chamadas:
        logger.info(f'  - Chamada ID: {c.id}, Status: {c.status}, Iniciador: {c.iniciador.username}, Tipo: {c.tipo}')
    
    # Buscar chamada pendente (não iniciada pelo usuário atual)
    chamadas = Chamada.objects.filter(
        chat=chat,
        status__in=['INICIANDO', 'CHAMANDO']
    ).exclude(iniciador=usuario).order_by('-data_inicio')
    
    logger.info(f'Chamadas pendentes encontradas (excluindo iniciador): {chamadas.count()}')
    for c in chamadas:
        logger.info(f'  - Chamada pendente ID: {c.id}, Status: {c.status}, Iniciador: {c.iniciador.username}, Tipo: {c.tipo}')
    
    chamada = chamadas.first()
    
    if chamada:
        logger.info(f'Chamada pendente encontrada - ID: {chamada.id}, Tipo: {chamada.tipo}, Status: {chamada.status}, Iniciador: {chamada.iniciador.username}')
        outro_participante = chat.obter_outro_participante(usuario)
        outro_nome = obter_info_militar(outro_participante)
        outro_foto = obter_foto_militar(outro_participante)
        
        return JsonResponse({
            'success': True,
            'chamada_pendente': {
                'id': chamada.id,
                'tipo': chamada.tipo.lower(),
                'iniciador_nome': obter_info_militar(chamada.iniciador),
                'iniciador_foto': obter_foto_militar(chamada.iniciador),
                'oferta': json.loads(chamada.oferta_sdp) if chamada.oferta_sdp else None,
            }
        })
    
    logger.info(f'Nenhuma chamada pendente encontrada para chat {chat_id}')
    return JsonResponse({
        'success': True,
        'chamada_pendente': None,
    })


@login_required
def chat_chamada_pendente_todas(request):
    """Verifica se há chamadas pendentes em todos os chats do usuário"""
    usuario = request.user
    
    # Buscar todos os chats do usuário
    chats = Chat.objects.filter(
        Q(participante1=usuario) | Q(participante2=usuario),
        ativo=True
    )
    
    # Buscar chamadas pendentes em todos os chats (não iniciadas pelo usuário atual)
    chamadas_pendentes = Chamada.objects.filter(
        chat__in=chats,
        status__in=['INICIANDO', 'CHAMANDO']
    ).exclude(iniciador=usuario).order_by('-data_inicio')
    
    # Log para debug
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f'Verificando todas as chamadas pendentes - Usuário: {usuario.username}, Total encontradas: {chamadas_pendentes.count()}')
    
    chamada = chamadas_pendentes.first()
    
    if chamada:
        logger.info(f'Chamada pendente encontrada - ID: {chamada.id}, Chat: {chamada.chat.id}, Tipo: {chamada.tipo}, Status: {chamada.status}, Iniciador: {chamada.iniciador.username}')
        outro_participante = chamada.chat.obter_outro_participante(usuario)
        outro_nome = obter_info_militar(outro_participante)
        outro_foto = obter_foto_militar(outro_participante)
        
        return JsonResponse({
            'success': True,
            'chamada_pendente': {
                'id': chamada.id,
                'chat_id': chamada.chat.id,
                'tipo': chamada.tipo.lower(),
                'iniciador_nome': obter_info_militar(chamada.iniciador),
                'iniciador_foto': obter_foto_militar(chamada.iniciador),
                'oferta': json.loads(chamada.oferta_sdp) if chamada.oferta_sdp else None,
            }
        })
    
    logger.info(f'Nenhuma chamada pendente encontrada para usuário {usuario.username}')
    return JsonResponse({
        'success': True,
        'chamada_pendente': None,
    })


@login_required
def chat_chamada_status(request, chat_id, chamada_id):
    """Verifica o status de uma chamada"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    chamada = get_object_or_404(Chamada, id=chamada_id, chat=chat)
    
    resposta_data = None
    if chamada.resposta_sdp:
        try:
            resposta_data = json.loads(chamada.resposta_sdp)
        except:
            pass
    
    return JsonResponse({
        'success': True,
        'chamada': {
            'id': chamada.id,
            'status': chamada.status,
            'tipo': chamada.tipo.lower(),
            'oferta': json.loads(chamada.oferta_sdp) if chamada.oferta_sdp else None,
            'resposta': resposta_data,
        }
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_chamada_finalizar(request, chat_id, chamada_id):
    """Finaliza uma chamada"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    chamada = get_object_or_404(Chamada, id=chamada_id, chat=chat)
    
    try:
        data = json.loads(request.body)
        duracao = data.get('duracao', None)
        chamada.finalizar(duracao=duracao)
        
        return JsonResponse({
            'success': True,
            'message': 'Chamada finalizada',
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_chamada_rejeitar(request, chat_id, chamada_id):
    """Rejeita uma chamada"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    chamada = get_object_or_404(Chamada, id=chamada_id, chat=chat)
    chamada.rejeitar()
    
    return JsonResponse({
        'success': True,
        'message': 'Chamada rejeitada',
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_chamada_cancelar(request, chat_id, chamada_id):
    """Cancela uma chamada"""
    chat = get_object_or_404(Chat, id=chat_id, ativo=True)
    usuario = request.user
    
    # Verificar se o usuário é participante do chat
    if chat.participante1 != usuario and chat.participante2 != usuario:
        return JsonResponse({'success': False, 'error': 'Você não tem acesso a este chat.'}, status=403)
    
    chamada = get_object_or_404(Chamada, id=chamada_id, chat=chat, iniciador=usuario)
    chamada.cancelar()
    
    return JsonResponse({
        'success': True,
        'message': 'Chamada cancelada',
    })


@login_required
@require_http_methods(["POST"])
def chat_delete(request, chat_id):
    """Exclui (desativa) uma conversa"""
    try:
        chat = get_object_or_404(Chat, id=chat_id)
        
        # Verificar se o usuário é participante do chat
        if chat.participante1 != request.user and chat.participante2 != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para excluir esta conversa.'
            }, status=403)
        
        # Desativar o chat (ao invés de deletar, para manter histórico)
        chat.ativo = False
        chat.save(update_fields=['ativo'])
        
        return JsonResponse({
            'success': True,
            'message': 'Conversa excluída com sucesso.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def chat_deletar_mensagem(request, chat_id, mensagem_id):
    """Deleta uma mensagem do chat (apenas o remetente pode deletar)"""
    try:
        chat = get_object_or_404(Chat, id=chat_id, ativo=True)
        mensagem = get_object_or_404(MensagemChat, id=mensagem_id, chat=chat)
        usuario = request.user
        
        # Verificar se o usuário é participante do chat
        if chat.participante1 != usuario and chat.participante2 != usuario:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem acesso a este chat.'
            }, status=403)
        
        # Verificar se o usuário é o remetente da mensagem
        if mensagem.remetente != usuario:
            return JsonResponse({
                'success': False,
                'error': 'Você só pode apagar suas próprias mensagens.'
            }, status=403)
        
        # Deletar o arquivo de áudio se existir
        if mensagem.audio:
            try:
                mensagem.audio.delete(save=False)
            except Exception as e:
                print(f'Erro ao deletar arquivo de áudio: {e}')
        
        # Deletar a mensagem
        mensagem.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Mensagem apagada com sucesso.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
