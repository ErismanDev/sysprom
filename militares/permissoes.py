#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de controle de acesso baseado em funções
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import UsuarioFuncao, PermissaoFuncao


def obter_funcao_atual(request):
    """
    Obtém a função atual do usuário da sessão
    """
    if not request.user.is_authenticated:
        return None
    
    funcao_id = request.session.get('funcao_atual_id')
    if funcao_id:
        try:
            return UsuarioFuncao.objects.select_related('cargo_funcao').get(
                id=funcao_id,
                usuario=request.user,
                status='ATIVO'
            )
        except UsuarioFuncao.DoesNotExist:
            # Se a função não existe mais, limpa a sessão
            request.session.pop('funcao_atual_id', None)
            request.session.pop('funcao_atual_nome', None)
    
    return None


def tem_permissao(request, modulo, acesso):
    """
    Verifica se o usuário tem permissão para um módulo e tipo de acesso específicos
    """
    if not request.user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if request.user.is_superuser:
        return True
    
    funcao_atual = obter_funcao_atual(request)
    if not funcao_atual:
        return False
    
    # Verificar se existe a permissão específica
    return PermissaoFuncao.objects.filter(
        cargo_funcao=funcao_atual.cargo_funcao,
        modulo=modulo,
        acesso=acesso,
        ativo=True
    ).exists()


def tem_permissao_modulo(request, modulo):
    """
    Verifica se o usuário tem qualquer permissão para um módulo
    """
    if not request.user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if request.user.is_superuser:
        return True
    
    funcao_atual = obter_funcao_atual(request)
    if not funcao_atual:
        return False
    
    # Verificar se existe qualquer permissão para o módulo
    return PermissaoFuncao.objects.filter(
        cargo_funcao=funcao_atual.cargo_funcao,
        modulo=modulo,
        ativo=True
    ).exists()


def requer_permissao(modulo, acesso):
    """
    Decorator para verificar permissão específica
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if tem_permissao(request, modulo, acesso):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'Você não tem permissão para {acesso.lower()} {modulo.lower()}.')
                return redirect('militares:militar_dashboard')
        return _wrapped_view
    return decorator


def requer_permissao_modulo(modulo):
    """
    Decorator para verificar se tem qualquer permissão no módulo
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if tem_permissao_modulo(request, modulo):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'Você não tem acesso ao módulo {modulo.lower()}.')
                return redirect('militares:militar_dashboard')
        return _wrapped_view
    return decorator


def requer_funcao_ativa(view_func):
    """
    Decorator para verificar se o usuário tem função ativa
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        funcao_atual = obter_funcao_atual(request)
        if not funcao_atual:
            messages.error(request, 'Você precisa selecionar uma função para acessar esta área.')
            return redirect('militares:selecionar_funcao')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def obter_permissoes_usuario(request):
    """
    Retorna todas as permissões do usuário atual
    """
    if not request.user.is_authenticated:
        return []
    
    funcao_atual = obter_funcao_atual(request)
    if not funcao_atual:
        return []
    
    return PermissaoFuncao.objects.filter(
        cargo_funcao=funcao_atual.cargo_funcao,
        ativo=True
    ).values_list('modulo', 'acesso')


def obter_modulos_acessiveis(request):
    """
    Retorna os módulos que o usuário pode acessar
    """
    permissoes = obter_permissoes_usuario(request)
    return list(set([p[0] for p in permissoes]))


def pode_visualizar_militares(request):
    """Verifica se pode visualizar militares"""
    return tem_permissao(request, 'MILITARES', 'VISUALIZAR')


def pode_criar_militares(request):
    """Verifica se pode criar militares"""
    return tem_permissao(request, 'MILITARES', 'CRIAR')


def pode_editar_militares(request):
    """Verifica se pode editar militares"""
    return tem_permissao(request, 'MILITARES', 'EDITAR')


def pode_excluir_militares(request):
    """Verifica se pode excluir militares"""
    return tem_permissao(request, 'MILITARES', 'EXCLUIR')


def pode_homologar_quadros(request):
    """Verifica se pode homologar quadros de acesso"""
    return tem_permissao(request, 'QUADROS_ACESSO', 'HOMOLOGAR')


def pode_gerar_pdf(request):
    """Verifica se pode gerar PDFs"""
    return tem_permissao(request, 'DOCUMENTOS', 'GERAR_PDF')


def pode_assinar_documentos(request):
    """Verifica se pode assinar documentos"""
    return tem_permissao(request, 'DOCUMENTOS', 'ASSINAR')


def pode_administrar_usuarios(request):
    """Verifica se pode administrar usuários"""
    return tem_permissao(request, 'USUARIOS', 'ADMINISTRAR')


# Context processor para disponibilizar permissões nos templates
def permissoes_processor(request):
    """
    Context processor para disponibilizar funções de permissão nos templates
    """
    return {
        'pode_visualizar_militares': lambda: pode_visualizar_militares(request),
        'pode_criar_militares': lambda: pode_criar_militares(request),
        'pode_editar_militares': lambda: pode_editar_militares(request),
        'pode_excluir_militares': lambda: pode_excluir_militares(request),
        'pode_homologar_quadros': lambda: pode_homologar_quadros(request),
        'pode_gerar_pdf': lambda: pode_gerar_pdf(request),
        'pode_assinar_documentos': lambda: pode_assinar_documentos(request),
        'pode_administrar_usuarios': lambda: pode_administrar_usuarios(request),
        'modulos_acessiveis': obter_modulos_acessiveis(request),
        'tem_permissao': lambda modulo, acesso: tem_permissao(request, modulo, acesso),
        'tem_permissao_modulo': lambda modulo: tem_permissao_modulo(request, modulo),
    } 