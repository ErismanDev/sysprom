from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import UsuarioFuncaoMilitar

@csrf_exempt
def mark_welcome_shown(request):
    """
    Marca na sessão que a popup de boas-vindas foi mostrada
    """
    if request.method == 'POST':
        try:
            request.session['usuario_welcome_shown'] = True
            request.session.save()  # Forçar salvamento da sessão
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def welcome_usuario(request):
    """
    Página de boas-vindas para usuários com função 'Serviço Operacional' ativa
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Verificar se o usuário tem sessão ativa com função "Serviço Operacional"
    from militares.models import UsuarioSessao
    sessao_ativa = UsuarioSessao.objects.filter(
        usuario=request.user,
        ativo=True
    ).first()

    if not sessao_ativa:
        messages.error(request, 'Sessão não encontrada. Selecione uma função primeiro.')
        return redirect('militares:selecionar_funcao_lotacao')
    
    if sessao_ativa.funcao_militar.nome != 'Serviço Operacional':
        messages.error(request, 'Acesso negado. Esta função é apenas para usuários com função "Serviço Operacional".')
        return redirect('militares:home')

    # Redirecionar diretamente para a ficha, sem mostrar popup
    return redirect('militares:redirect_usuario_ficha')


@login_required
def redirect_usuario_ficha(request):
    """
    Redireciona usuários com função 'Serviço Operacional' ativa para sua própria ficha de conceito
    """
    if not request.user.is_authenticated:
        return redirect('login')

    # Verificar se o usuário tem sessão ativa com função "Serviço Operacional"
    from militares.models import UsuarioSessao
    sessao_ativa = UsuarioSessao.objects.filter(
        usuario=request.user,
        ativo=True
    ).first()

    if not sessao_ativa:
        messages.error(request, 'Sessão não encontrada. Selecione uma função primeiro.')
        return redirect('militares:selecionar_funcao_lotacao')
    
    if sessao_ativa.funcao_militar.nome != 'Serviço Operacional':
        messages.error(request, 'Acesso negado. Esta função é apenas para usuários com função "Serviço Operacional".')
        return redirect('militares:home')
    
    # Buscar a ficha do usuário
    try:
        militar = request.user.militar
        if not militar:
            messages.error(request, 'Usuário não possui militar associado.')
            return redirect('militares:home')
        
        # Buscar ficha de conceito do usuário
        if militar.posto_graduacao in ['SD', 'CAB', '3S', '2S', '1S', 'ST']:
            # Praça
            ficha = militar.fichaconceitopracas_set.first()
            if ficha:
                # Renderizar diretamente a página da ficha em vez de redirecionar
                return redirect('militares:ficha_conceito_pracas_detail', pk=ficha.pk)
        else:
            # Oficial
            ficha = militar.fichaconceitooficiais_set.first()
            if ficha:
                # Renderizar diretamente a página da ficha em vez de redirecionar
                return redirect('militares:ficha_conceito_detail', pk=ficha.pk)
        
        # Se não encontrou ficha, criar uma
        messages.info(request, 'Ficha de conceito não encontrada. Será criada uma nova ficha.')
        return redirect('militares:ficha_conceito_form')
        
    except Exception as e:
        messages.error(request, f'Erro ao acessar ficha: {str(e)}')
        return redirect('militares:home') 