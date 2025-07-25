from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UsuarioFuncao


@login_required
def mark_welcome_shown(request):
    """
    Marca na sessão que a popup de boas-vindas foi mostrada
    """
    if request.method == 'POST':
        request.session['usuario_welcome_shown'] = True
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def welcome_usuario(request):
    """
    Página de boas-vindas para usuários do tipo 'Usuário'
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Verificar se usuário é do tipo "Usuário"
    is_usuario = UsuarioFuncao.objects.filter(
        usuario=request.user,
        status='ATIVO',
        cargo_funcao__nome='Usuário'
    ).exists()
    
    if not is_usuario:
        return redirect('militares:militar_dashboard')
    
    # Redirecionar diretamente para a ficha, sem mostrar popup
    return redirect('militares:redirect_usuario_ficha')


@login_required
def redirect_usuario_ficha(request):
    """
    Redireciona usuários do tipo 'Usuário' para sua própria ficha de conceito
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Verificar se usuário é do tipo "Usuário"
    is_usuario = UsuarioFuncao.objects.filter(
        usuario=request.user,
        status='ATIVO',
        cargo_funcao__nome='Usuário'
    ).exists()
    
    if not is_usuario:
        return redirect('militares:militar_dashboard')
    
    # Buscar a ficha do usuário
    try:
        militar = request.user.militar
        if not militar:
            messages.error(request, 'Usuário não possui militar associado.')
            return redirect('militares:militar_dashboard')
        
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
        return redirect('militares:militar_dashboard') 