from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate
from .models import SessaoComissao, AtaSessao, AssinaturaAta, MembroComissao


@login_required
def membros_comissao_ajax(request, pk):
    """Retorna membros da comissão via AJAX"""
    try:
        sessao = SessaoComissao.objects.get(pk=pk)
        membros = MembroComissao.objects.filter(
            comissao=sessao.comissao,
            ativo=True
        )
        
        membros_data = []
        for membro in membros:
            membros_data.append({
                'id': membro.id,
                'nome_completo': membro.militar.nome_completo,
                'posto_graduacao': membro.militar.get_posto_graduacao_display(),
                'tipo': membro.get_tipo_display(),
                'cargo': membro.cargo.nome if membro.cargo else ''
            })
        
        return JsonResponse({
            'success': True,
            'membros': membros_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def assinaturas_existentes_ajax(request, pk):
    """Retorna assinaturas existentes via AJAX"""
    try:
        sessao = SessaoComissao.objects.get(pk=pk)
        ata = AtaSessao.objects.get(sessao=sessao)
        
        assinaturas_data = []
        for assinatura in ata.assinaturas.all():
            assinaturas_data.append({
                'membro_id': assinatura.membro.id,
                'nome_completo': assinatura.membro.militar.nome_completo,
                'posto_graduacao': assinatura.membro.militar.get_posto_graduacao_display(),
                'tipo': assinatura.membro.get_tipo_display(),
                'assinado_por': assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username,
                'data_assinatura': assinatura.data_assinatura.strftime('%d/%m/%Y %H:%M'),
                'observacoes': assinatura.observacoes or ''
            })
        
        return JsonResponse({
            'success': True,
            'assinaturas': assinaturas_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def assinar_ata_ajax(request):
    """Processa assinatura de ata via AJAX"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido'
        })
    
    try:
        sessao_id = request.POST.get('sessao_id')
        membro_id = request.POST.get('membro_id')
        observacoes = request.POST.get('observacoes', '')
        senha = request.POST.get('senha')
        
        if not sessao_id:
            return JsonResponse({
                'success': False,
                'error': 'ID da sessão não fornecido'
            })
        
        if not membro_id:
            return JsonResponse({
                'success': False,
                'error': 'Selecione um membro da comissão'
            })
        
        if not senha:
            return JsonResponse({
                'success': False,
                'error': 'Digite sua senha para confirmar a assinatura'
            })
        
        # Verificar senha
        user = authenticate(username=request.user.username, password=senha)
        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Senha incorreta'
            })
        
        # Buscar sessão e ata
        sessao = SessaoComissao.objects.get(pk=sessao_id)
        ata = AtaSessao.objects.get(sessao=sessao)
        
        # Verificar se o usuário é membro da comissão
        try:
            membro_usuario = MembroComissao.objects.get(
                comissao=sessao.comissao,
                usuario=request.user,
                ativo=True
            )
        except MembroComissao.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Você não é membro desta comissão'
            })
        
        # Buscar membro que será assinado
        try:
            membro_assinatura = MembroComissao.objects.get(
                id=membro_id,
                comissao=sessao.comissao,
                ativo=True
            )
        except MembroComissao.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Membro da comissão não encontrado'
            })
        
        # Verificar se já assinou
        if AssinaturaAta.objects.filter(ata=ata, membro=membro_assinatura).exists():
            return JsonResponse({
                'success': False,
                'error': 'Este membro já assinou esta ata'
            })
        
        # Capturar a função atual do usuário na sessão
        funcao_atual = request.session.get('funcao_atual_nome', 'Usuário do Sistema')
        
        # Criar assinatura
        assinatura = AssinaturaAta.objects.create(
            ata=ata,
            membro=membro_assinatura,
            assinado_por=request.user,
            observacoes=observacoes,
            funcao_assinatura=funcao_atual
        )
        
        # Verificar se todas as assinaturas foram feitas
        total_membros = MembroComissao.objects.filter(
            comissao=sessao.comissao,
            ativo=True
        ).count()
        
        if ata.assinaturas.count() >= total_membros:
            ata.status = 'ASSINADA'
            ata.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Ata assinada com sucesso por {membro_assinatura.militar.nome_completo}',
            'assinatura_id': assinatura.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }) 


@login_required
def deletar_ata_ajax(request, pk):
    """Deletar ata via AJAX"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido'
        })
    
    try:
        sessao = SessaoComissao.objects.get(pk=pk)
        ata = AtaSessao.objects.get(sessao=sessao)
        
        # Verificar se o usuário tem permissão
        try:
            membro = MembroComissao.objects.get(
                comissao=sessao.comissao,
                usuario=request.user,
                ativo=True
            )
        except MembroComissao.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Você não é membro desta comissão'
            })
        
        # Verificar se a ata pode ser deletada (apenas rascunho)
        if ata.status != 'RASCUNHO':
            return JsonResponse({
                'success': False,
                'error': 'Apenas atas em rascunho podem ser deletadas'
            })
        
        # Deletar a ata
        ata.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Ata deletada com sucesso'
        })
        
    except SessaoComissao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sessão não encontrada'
        })
    except AtaSessao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Ata não encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }) 