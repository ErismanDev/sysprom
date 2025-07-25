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
    
    # Verificar se tem função de administrador
    from .models import UsuarioFuncao
    return UsuarioFuncao.objects.filter(
        usuario=user,
        cargo_funcao__nome__icontains='administrador',
        status='ATIVO'
    ).exists()

def admin_bypass(view_func):
    """
    Decorator que permite admin bypass - admin tem acesso total
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Se é admin, permitir acesso total
        if is_admin_user(request.user):
            return view_func(request, *args, **kwargs)
        
        # Se não é admin, aplicar verificações normais
        # (aqui você pode adicionar outras verificações se necessário)
        return view_func(request, *args, **kwargs)
    
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
            return redirect('militares:militar_dashboard')
        
        return _wrapped_view
    return decorator

