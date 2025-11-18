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
from .models import UsuarioFuncaoMilitar


def obter_funcao_atual(request):
    """
    Obtém a função atual do usuário da sessão
    """
    if not request.user.is_authenticated:
        return None
    
    funcao_id = request.session.get('funcao_atual_id')
    if funcao_id:
        try:
            return UsuarioFuncaoMilitar.objects.select_related('funcao_militar').get(
                id=funcao_id,
                usuario=request.user,
                ativo=True
            )
        except UsuarioFuncaoMilitar.DoesNotExist:
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
    
    # Usar sistema de permissões granulares
    from .permissoes_simples import tem_permissao as tem_permissao_granular
    return tem_permissao_granular(request.user, modulo.lower(), acesso.lower())


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
    
    # Usar sistema de permissões granulares
    from .permissoes_simples import tem_permissao as tem_permissao_granular
    return tem_permissao_granular(request.user, modulo.lower(), 'visualizar')


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
                return redirect('militares:home')
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
                return redirect('militares:home')
        return _wrapped_view
    return decorator


def requer_funcao_ativa(view_func):
    """
    Decorator para verificar se o usuário tem função ativa
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Superusuários não precisam de função ativa
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar se o usuário tem uma função ativa
        from militares.models import UsuarioFuncaoMilitar
        funcao_ativa = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True
        ).first()
        
        if not funcao_ativa:
            # Se não tem função ativa, ativar a primeira função disponível
            primeira_funcao = UsuarioFuncaoMilitar.objects.filter(
                usuario=request.user
            ).first()
            
            if primeira_funcao:
                # Desativar todas as funções do usuário
                UsuarioFuncaoMilitar.objects.filter(usuario=request.user).update(ativo=False)
                
                # Ativar a primeira função
                primeira_funcao.ativo = True
                primeira_funcao.save()
                
                # Criar sessão ativa
                from militares.models import UsuarioSessao
                UsuarioSessao.objects.filter(usuario=request.user, ativo=True).update(ativo=False)
                UsuarioSessao.objects.create(
                    usuario=request.user,
                    funcao_militar_usuario=primeira_funcao
                )
            else:
                messages.error(request, 'Você não possui funções cadastradas no sistema.')
                return redirect('logout')
        
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
    
    # Sistema antigo removido - usar permissões granulares
    # Retornar lista vazia por compatibilidade
    return []


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


def pode_reordenar_antiguidade(request):
    """Verifica se pode reordenar antiguidade"""
    return tem_permissao(request, 'MILITARES', 'REORDENAR_ANTIGUIDADE')


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
        'pode_reordenar_antiguidade': lambda: pode_reordenar_antiguidade(request),
        'modulos_acessiveis': obter_modulos_acessiveis(request),
        'tem_permissao': lambda modulo, acesso: tem_permissao(request, modulo, acesso),
        'tem_permissao_modulo': lambda modulo: tem_permissao_modulo(request, modulo),
    } 