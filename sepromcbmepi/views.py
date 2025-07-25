from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from militares.models import UsuarioFuncao
import os


def login_view(request):
    """View para login do usuário com suporte a múltiplas funções"""
    if request.user.is_authenticated:
        return redirect('militares:militar_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Fazer login do usuário
                login(request, user)
                
                # TEMPORARIAMENTE: Redirecionar direto para dashboard sem verificar funções
                messages.success(request, f'Bem-vindo! Login realizado com sucesso.')
                return redirect('militares:militar_dashboard')
            else:
                messages.error(request, 'Sua conta está inativa. Entre em contato com o administrador.')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """View para logout do usuário"""
    # Limpar dados da sessão relacionados às funções
    session_keys_to_remove = [
        'funcao_atual_id', 
        'funcao_atual_nome', 
        'funcoes_disponiveis'
    ]
    for key in session_keys_to_remove:
        request.session.pop(key, None)
    
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')


@login_required
def home_view(request):
    """View da página inicial"""
    return redirect('militares:militar_dashboard')


def teste_modal_view(request):
    """View temporária para testar o modal"""
    try:
        with open('teste_modal_simples.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("Arquivo de teste não encontrado", status=404) 