#!/usr/bin/env python
"""
Decorators para permitir acesso total ao admin
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

def is_admin_user(user):
    """Verifica se o usuário é admin (superusuário ou tem função de administrador)"""
    if not user.is_authenticated:
        return False
    
    # Superusuários sempre têm acesso
    if user.is_superuser:
        return True
    
    # Verificar se tem função de administrador ou operador do sistema
    from .models import UsuarioFuncaoMilitar
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        funcao_militar__nome__in=['Administrador', 'Administrador do Sistema', 'Admnistrador do Sistema', 'Operador do Sistema'],
        ativo=True
    ).exists()

def admin_bypass(view_func):
    """
    Decorator que permite admin bypass - admin OU usuários com permissões granulares
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Se é admin, permitir acesso total
        if is_admin_user(request.user):
            return view_func(request, *args, **kwargs)
        
        # Verificar se tem permissões granulares para editar militares
        from .permissoes_simples import pode_editar_militares
        if pode_editar_militares(request.user):
            return view_func(request, *args, **kwargs)
        
        # Se não tem nem permissão de admin nem granular, negar acesso
        messages.error(request, 'Acesso negado. Você não tem permissão para editar militares.')
        return redirect('militares:militar_list')
    
    return _wrapped_view

def admin_or_permission_required(permission):
    """
    Decorator que requer permissão OU ser admin
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Se é admin, permitir acesso
            if is_admin_user(request.user):
                return view_func(request, *args, **kwargs)
            
            # Se não é admin, verificar permissão
            if request.user.has_perm(permission):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'Acesso negado. Permissão necessária ou ser administrador.')
            return redirect('militares:home')
        
        return _wrapped_view
    return decorator

