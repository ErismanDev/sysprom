#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de permissões simplificado baseado em funções
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import UsuarioFuncao


# ============================================================================
# FUNÇÕES DE VERIFICAÇÃO DE PERMISSÕES
# ============================================================================

def tem_funcao_especial(user, funcoes_lista):
    """
    Verifica se o usuário tem alguma das funções especiais listadas
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm acesso total
    if user.is_superuser:
        return True
    
    # Dividir a lista de funções por vírgula
    funcoes = [f.strip() for f in funcoes_lista.split(',')]
    
    # Verificar se o usuário tem alguma das funções especificadas
    return UsuarioFuncao.objects.filter(
        usuario=user,
        cargo_funcao__nome__in=funcoes,
        status='ATIVO'
    ).exists()


def pode_editar_militares(user):
    """
    Verifica se o usuário pode editar cadastros de militares
    """
    funcoes_permitidas = 'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções,Administrador do Sistema,Administrador'
    return tem_funcao_especial(user, funcoes_permitidas)


def pode_editar_fichas_conceito(user):
    """
    Verifica se o usuário pode editar fichas de conceito
    """
    funcoes_permitidas = 'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções,Administrador do Sistema,Administrador'
    return tem_funcao_especial(user, funcoes_permitidas)


def pode_gerenciar_quadros_vagas(user):
    """
    Verifica se o usuário pode gerenciar quadros de fixação de vagas
    """
    funcoes_permitidas = 'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções,Administrador do Sistema,Administrador'
    return tem_funcao_especial(user, funcoes_permitidas)


def pode_gerenciar_comissoes(user):
    """
    Verifica se o usuário pode gerenciar comissões
    """
    funcoes_permitidas = 'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções,Administrador do Sistema,Administrador'
    return tem_funcao_especial(user, funcoes_permitidas)


def pode_gerenciar_usuarios(user):
    """
    Verifica se o usuário pode gerenciar usuários
    """
    funcoes_permitidas = 'Administrador do Sistema,Administrador'
    return tem_funcao_especial(user, funcoes_permitidas)


def pode_assinar_documentos(user):
    """
    Verifica se o usuário pode assinar documentos
    """
    funcoes_permitidas = 'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções,Administrador do Sistema,Administrador,Presidente da CPO,Presidente da CPP'
    return tem_funcao_especial(user, funcoes_permitidas)


def pode_visualizar_tudo(user):
    """
    Verifica se o usuário pode visualizar todos os módulos
    """
    funcoes_permitidas = 'Diretor de Gestão de Pessoas,Chefe da Seção de Promoções,Administrador do Sistema,Administrador'
    return tem_funcao_especial(user, funcoes_permitidas)


def eh_membro_comissao(user):
    """
    Verifica se o usuário é membro de alguma comissão
    """
    funcoes_comissao = 'CPO,CPP,Membro da CPO,Membro da CPP,Presidente da CPO,Presidente da CPP,Vice-Presidente da CPO,Vice-Presidente da CPP,Secretário da CPO,Secretário da CPP'
    return tem_funcao_especial(user, funcoes_comissao)


# ============================================================================
# DECORATORS DE PERMISSÃO
# ============================================================================

def requer_funcao_especial(funcoes_lista):
    """
    Decorator para verificar se o usuário tem função especial
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if tem_funcao_especial(request.user, funcoes_lista):
                return view_func(request, *args, **kwargs)
            else:
                funcoes = [f.strip() for f in funcoes_lista.split(',')]
                messages.error(request, f'Acesso negado. Apenas usuários com as seguintes funções podem acessar: {", ".join(funcoes)}')
                return HttpResponseForbidden('Acesso negado')
        
        return _wrapped_view
    return decorator


def requer_edicao_militares(view_func):
    """
    Decorator para verificar permissão de edição de militares
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if pode_editar_militares(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Você não tem permissão para editar militares. Apenas Diretor de Gestão de Pessoas, Chefe da Seção de Promoções e Administrador do Sistema podem editar.')
            return redirect('militares:militar_list')
    
    return _wrapped_view


def requer_edicao_fichas_conceito(view_func):
    """
    Decorator para verificar permissão de edição de fichas de conceito
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if pode_editar_fichas_conceito(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Você não tem permissão para editar fichas de conceito. Apenas Diretor de Gestão de Pessoas, Chefe da Seção de Promoções e Administrador do Sistema podem editar.')
            return redirect('militares:ficha_conceito_list')
    
    return _wrapped_view


def requer_gerenciamento_quadros_vagas(view_func):
    """
    Decorator para verificar permissão de gerenciamento de quadros de vagas
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if pode_gerenciar_quadros_vagas(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Você não tem permissão para gerenciar quadros de fixação de vagas. Apenas Diretor de Gestão de Pessoas, Chefe da Seção de Promoções e Administrador do Sistema podem gerenciar.')
            return redirect('militares:quadro_fixacao_vagas_list')
    
    return _wrapped_view


def requer_gerenciamento_comissoes(view_func):
    """
    Decorator para verificar permissão de gerenciamento de comissões
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if pode_gerenciar_comissoes(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Você não tem permissão para gerenciar comissões. Apenas Diretor de Gestão de Pessoas, Chefe da Seção de Promoções e Administrador do Sistema podem gerenciar.')
            return redirect('militares:comissao_list')
    
    return _wrapped_view


def requer_gerenciamento_usuarios(view_func):
    """
    Decorator para verificar permissão de gerenciamento de usuários
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if pode_gerenciar_usuarios(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Você não tem permissão para gerenciar usuários. Apenas Administrador do Sistema pode gerenciar.')
            return redirect('militares:militar_dashboard')
    
    return _wrapped_view


def requer_assinatura_documentos(view_func):
    """
    Decorator para verificar permissão de assinatura de documentos
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if pode_assinar_documentos(request.user):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Você não tem permissão para assinar documentos.')
            return redirect('militares:militar_dashboard')
    
    return _wrapped_view


def apenas_visualizacao_comissao(view_func):
    """
    Decorator para permitir apenas visualização para membros de comissão
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Se for membro de comissão e tentar fazer operações de escrita, bloquear
        if eh_membro_comissao(request.user) and request.method in ['POST', 'PUT', 'DELETE']:
            # Verificar se tem funções especiais que permitem CRUD completo
            if not pode_editar_militares(request.user):
                messages.error(request, 'Usuários de comissão podem apenas visualizar. Não é permitido editar.')
                return HttpResponseForbidden('Apenas visualização permitida')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def obter_funcoes_usuario(user):
    """
    Retorna todas as funções ativas do usuário
    """
    if not user or not user.is_authenticated:
        return []
    
    return UsuarioFuncao.objects.filter(
        usuario=user,
        status='ATIVO'
    ).select_related('cargo_funcao')


def obter_funcoes_especiais_usuario(user):
    """
    Retorna as funções especiais do usuário
    """
    funcoes_especiais = [
        'Diretor de Gestão de Pessoas',
        'Chefe da Seção de Promoções', 
        'Administrador do Sistema'
    ]
    
    return obter_funcoes_usuario(user).filter(
        cargo_funcao__nome__in=funcoes_especiais
    )


def obter_funcoes_comissao_usuario(user):
    """
    Retorna as funções de comissão do usuário
    """
    funcoes_comissao = [
        'CPO', 'CPP',
        'Membro da CPO', 'Membro da CPP',
        'Presidente da CPO', 'Presidente da CPP',
        'Vice-Presidente da CPO', 'Vice-Presidente da CPP',
        'Secretário da CPO', 'Secretário da CPP'
    ]
    
    return obter_funcoes_usuario(user).filter(
        cargo_funcao__nome__in=funcoes_comissao
    )


# ============================================================================
# CONTEXT PROCESSOR
# ============================================================================

def permissoes_simples_processor(request):
    """
    Context processor para disponibilizar funções de permissão nos templates
    """
    if not request.user.is_authenticated:
        return {}
    
    return {
        # Funções de verificação
        'pode_editar_militares': lambda: pode_editar_militares(request.user),
        'pode_editar_fichas_conceito': lambda: pode_editar_fichas_conceito(request.user),
        'pode_gerenciar_quadros_vagas': lambda: pode_gerenciar_quadros_vagas(request.user),
        'pode_gerenciar_comissoes': lambda: pode_gerenciar_comissoes(request.user),
        'pode_gerenciar_usuarios': lambda: pode_gerenciar_usuarios(request.user),
        'pode_assinar_documentos': lambda: pode_assinar_documentos(request.user),
        'pode_visualizar_tudo': lambda: pode_visualizar_tudo(request.user),
        'eh_membro_comissao': lambda: eh_membro_comissao(request.user),
        
        # Funções auxiliares
        'tem_funcao_especial': lambda funcoes: tem_funcao_especial(request.user, funcoes),
        'funcoes_usuario': obter_funcoes_usuario(request.user),
        'funcoes_especiais_usuario': obter_funcoes_especiais_usuario(request.user),
        'funcoes_comissao_usuario': obter_funcoes_comissao_usuario(request.user),
    } 