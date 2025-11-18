#!/usr/bin/env python
"""
Decorators para verificação de hierarquia de lotação
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .permissoes_hierarquicas import pode_editar_militar, pode_visualizar_militar

def requer_hierarquia_lotacao(view_func):
    """
    Decorator que verifica se o usuário pode editar/visualizar o militar específico
    baseado na hierarquia de lotação
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Superusuários sempre podem
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar se tem pk do militar nos argumentos
        pk = kwargs.get('pk')
        if not pk:
            # Se não tem pk, permitir acesso (pode ser uma view de listagem)
            return view_func(request, *args, **kwargs)
        
        # Buscar o militar
        from .models import Militar
        try:
            militar = Militar.objects.get(pk=pk)
        except Militar.DoesNotExist:
            messages.error(request, 'Militar não encontrado.')
            return redirect('militares:militar_list')
        
        # Verificar permissão baseada no método HTTP
        if request.method in ['POST', 'PUT', 'DELETE']:
            # Para operações de escrita, verificar se pode editar
            if not pode_editar_militar(request.user, militar):
                messages.error(request, 'Você não tem permissão para editar este militar. Apenas militares da sua área de lotação podem ser editados.')
                return redirect('militares:militar_list')
        else:
            # Para operações de leitura, verificar se pode visualizar
            if not pode_visualizar_militar(request.user, militar):
                messages.error(request, 'Você não tem permissão para visualizar este militar. Apenas militares da sua área de lotação podem ser visualizados.')
                return redirect('militares:militar_list')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
