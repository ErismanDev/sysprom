#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Permissões Completo baseado no modelo PermissaoFuncao
Permite verificar permissões específicas por módulo e tipo de acesso
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import UsuarioFuncao, PermissaoFuncao


# ============================================================================
# FUNÇÕES DE VERIFICAÇÃO DE PERMISSÕES
# ============================================================================

def tem_permissao(user, modulo, acesso):
    """
    Verifica se o usuário tem uma permissão específica
    
    Args:
        user: Usuário autenticado
        modulo: Módulo do sistema (ex: 'MILITARES', 'FICHAS_CONCEITO')
        acesso: Tipo de acesso (ex: 'VISUALIZAR', 'CRIAR', 'EDITAR')
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários sempre têm todas as permissões
    if user.is_superuser:
        return True
    
    # Verificar se o usuário tem alguma função ativa
    funcoes_usuario = UsuarioFuncao.objects.filter(
        usuario=user,
        status='ATIVO'
    ).select_related('cargo_funcao')
    
    if not funcoes_usuario.exists():
        return False
    
    # Verificar se alguma das funções do usuário tem a permissão específica
    for funcao in funcoes_usuario:
        permissao = PermissaoFuncao.objects.filter(
            cargo_funcao=funcao.cargo_funcao,
            modulo=modulo,
            acesso=acesso,
            ativo=True
        ).exists()
        
        if permissao:
            return True
    
    return False


def tem_permissao_modulo(user, modulo):
    """
    Verifica se o usuário tem qualquer permissão no módulo
    
    Args:
        user: Usuário autenticado
        modulo: Módulo do sistema
    
    Returns:
        bool: True se tem alguma permissão no módulo
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários sempre têm acesso
    if user.is_superuser:
        return True
    
    # Verificar funções ativas do usuário
    funcoes_usuario = UsuarioFuncao.objects.filter(
        usuario=user,
        status='ATIVO'
    ).select_related('cargo_funcao')
    
    if not funcoes_usuario.exists():
        return False
    
    # Verificar se alguma função tem permissão no módulo
    for funcao in funcoes_usuario:
        permissao = PermissaoFuncao.objects.filter(
            cargo_funcao=funcao.cargo_funcao,
            modulo=modulo,
            ativo=True
        ).exists()
        
        if permissao:
            return True
    
    return False


def obter_permissoes_usuario(user, modulo=None):
    """
    Obtém todas as permissões do usuário, opcionalmente filtradas por módulo
    
    Args:
        user: Usuário autenticado
        modulo: Módulo específico (opcional)
    
    Returns:
        list: Lista de permissões (modulo, acesso)
    """
    if not user or not user.is_authenticated:
        return []
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        if modulo:
            return [(modulo, acesso) for acesso in [
                'VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 
                'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'
            ]]
        else:
            # Retornar todas as combinações possíveis
            modulos = [
                'MILITARES',
                'FICHAS_CONCEITO',
                'QUADROS_ACESSO',
                'PROMOCOES',
                'VAGAS',
                'COMISSAO',
                'DOCUMENTOS',
                'USUARIOS',
                'RELATORIOS',
                'CONFIGURACOES',
                'ALMANAQUES',
                'CALENDARIOS',
                'NOTIFICACOES',
                'MODELOS_ATA',
                'CARGOS_COMISSAO',
                'QUADROS_FIXACAO',
                'ASSINATURAS',
                'ESTATISTICAS',
                'EXPORTACAO',
                'IMPORTACAO',
                'BACKUP',
                'AUDITORIA',
                'DASHBOARD',
                'BUSCA',
                'AJAX',
                'API',
                'SESSAO',
                'FUNCAO',
                'PERFIL',
                'SISTEMA',
            ]
            acessos = [
                'VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 
                'HOMOLOGAR', 'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'
            ]
            return [(mod, acc) for mod in modulos for acc in acessos]
    
    # Buscar permissões das funções do usuário
    funcoes_usuario = UsuarioFuncao.objects.filter(
        usuario=user,
        status='ATIVO'
    ).select_related('cargo_funcao')
    
    permissoes = []
    for funcao in funcoes_usuario:
        queryset = PermissaoFuncao.objects.filter(
            cargo_funcao=funcao.cargo_funcao,
            ativo=True
        )
        
        if modulo:
            queryset = queryset.filter(modulo=modulo)
        
        for permissao in queryset:
            permissoes.append((permissao.modulo, permissao.acesso))
    
    return list(set(permissoes))  # Remover duplicatas


def pode_executar_acao(user, modulo, acao):
    """
    Verifica se o usuário pode executar uma ação específica baseada no método HTTP
    
    Args:
        user: Usuário autenticado
        modulo: Módulo do sistema
        acao: Ação a ser executada (GET, POST, PUT, DELETE)
    
    Returns:
        bool: True se pode executar a ação
    """
    # Mapeamento de ações HTTP para tipos de permissão
    mapeamento_acoes = {
        'GET': 'VISUALIZAR',
        'POST': 'CRIAR',
        'PUT': 'EDITAR',
        'PATCH': 'EDITAR',
        'DELETE': 'EXCLUIR',
    }
    
    tipo_permissao = mapeamento_acoes.get(acao, 'VISUALIZAR')
    return tem_permissao(user, modulo, tipo_permissao)


# ============================================================================
# DECORATORS DE PERMISSÃO
# ============================================================================

def requer_permissao(modulo, acesso):
    """
    Decorator para verificar permissão específica
    
    Args:
        modulo: Módulo do sistema
        acesso: Tipo de acesso necessário
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if tem_permissao(request.user, modulo, acesso):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'Você não tem permissão para {acesso.lower()} {modulo.lower()}.')
                return redirect('militares:militar_dashboard')
        return _wrapped_view
    return decorator


def requer_permissao_modulo(modulo):
    """
    Decorator para verificar se tem qualquer permissão no módulo
    
    Args:
        modulo: Módulo do sistema
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if tem_permissao_modulo(request.user, modulo):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'Você não tem acesso ao módulo {modulo.lower()}.')
                return redirect('militares:militar_dashboard')
        return _wrapped_view
    return decorator


def requer_acao_http(modulo, acao):
    """
    Decorator para verificar permissão baseada no método HTTP
    
    Args:
        modulo: Módulo do sistema
        acao: Método HTTP (GET, POST, PUT, DELETE)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if pode_executar_acao(request.user, modulo, request.method):
                return view_func(request, *args, **kwargs)
            else:
                mapeamento_acoes = {
                    'GET': 'visualizar',
                    'POST': 'criar',
                    'PUT': 'editar',
                    'PATCH': 'editar',
                    'DELETE': 'excluir',
                }
                acao_desc = mapeamento_acoes.get(request.method, 'acessar')
                messages.error(request, f'Você não tem permissão para {acao_desc} {modulo.lower()}.')
                return redirect('militares:militar_dashboard')
        return _wrapped_view
    return decorator


# ============================================================================
# DECORATORS ESPECÍFICOS POR MÓDULO
# ============================================================================

# Militares
def requer_perm_militares(acesso='VISUALIZAR'):
    """Decorator para permissões de militares"""
    return requer_permissao('MILITARES', acesso)

def requer_perm_militares_visualizar(view_func):
    """Decorator para visualizar militares"""
    return requer_permissao('MILITARES', 'VISUALIZAR')(view_func)

def requer_perm_militares_criar(view_func):
    """Decorator para criar militares"""
    return requer_permissao('MILITARES', 'CRIAR')(view_func)

def requer_perm_militares_editar(view_func):
    """Decorator para editar militares"""
    return requer_permissao('MILITARES', 'EDITAR')(view_func)

def requer_perm_militares_excluir(view_func):
    """Decorator para excluir militares"""
    return requer_permissao('MILITARES', 'EXCLUIR')(view_func)

def requer_perm_militares_admin(view_func):
    """Decorator para administrar militares"""
    return requer_permissao('MILITARES', 'ADMINISTRAR')(view_func)

# Fichas de Conceito
def requer_perm_fichas_conceito(acesso='VISUALIZAR'):
    """Decorator para permissões de fichas de conceito"""
    return requer_permissao('FICHAS_CONCEITO', acesso)

def requer_perm_fichas_visualizar(view_func):
    """Decorator para visualizar fichas"""
    return requer_permissao('FICHAS_CONCEITO', 'VISUALIZAR')(view_func)

def requer_perm_fichas_criar(view_func):
    """Decorator para criar fichas"""
    return requer_permissao('FICHAS_CONCEITO', 'CRIAR')(view_func)

def requer_perm_fichas_editar(view_func):
    """Decorator para editar fichas"""
    return requer_permissao('FICHAS_CONCEITO', 'EDITAR')(view_func)

def requer_perm_fichas_aprovar(view_func):
    """Decorator para aprovar fichas"""
    return requer_permissao('FICHAS_CONCEITO', 'APROVAR')(view_func)

def requer_perm_fichas_admin(view_func):
    """Decorator para administrar fichas"""
    return requer_permissao('FICHAS_CONCEITO', 'ADMINISTRAR')(view_func)

# Quadros de Acesso
def requer_perm_quadros_acesso(acesso='VISUALIZAR'):
    """Decorator para permissões de quadros de acesso"""
    return requer_permissao('QUADROS_ACESSO', acesso)

def requer_perm_quadros_visualizar(view_func):
    """Decorator para visualizar quadros"""
    return requer_permissao('QUADROS_ACESSO', 'VISUALIZAR')(view_func)

def requer_perm_quadros_criar(view_func):
    """Decorator para criar quadros"""
    return requer_permissao('QUADROS_ACESSO', 'CRIAR')(view_func)

def requer_perm_quadros_editar(view_func):
    """Decorator para editar quadros"""
    return requer_permissao('QUADROS_ACESSO', 'EDITAR')(view_func)

def requer_perm_quadros_excluir(view_func):
    """Decorator para excluir quadros"""
    return requer_permissao('QUADROS_ACESSO', 'EXCLUIR')(view_func)

def requer_perm_quadros_admin(view_func):
    """Decorator para administrar quadros"""
    return requer_permissao('QUADROS_ACESSO', 'ADMINISTRAR')(view_func)

# Promoções
def requer_perm_promocoes(acesso='VISUALIZAR'):
    """Decorator para permissões de promoções"""
    return requer_permissao('PROMOCOES', acesso)

def requer_perm_promocoes_visualizar(view_func):
    """Decorator para visualizar promoções"""
    return requer_permissao('PROMOCOES', 'VISUALIZAR')(view_func)

def requer_perm_promocoes_criar(view_func):
    """Decorator para criar promoções"""
    return requer_permissao('PROMOCOES', 'CRIAR')(view_func)

def requer_perm_promocoes_editar(view_func):
    """Decorator para editar promoções"""
    return requer_permissao('PROMOCOES', 'EDITAR')(view_func)

def requer_perm_promocoes_aprovar(view_func):
    """Decorator para aprovar promoções"""
    return requer_permissao('PROMOCOES', 'APROVAR')(view_func)

def requer_perm_promocoes_homologar(view_func):
    """Decorator para homologar promoções"""
    return requer_permissao('PROMOCOES', 'HOMOLOGAR')(view_func)

def requer_perm_promocoes_admin(view_func):
    """Decorator para administrar promoções"""
    return requer_permissao('PROMOCOES', 'ADMINISTRAR')(view_func)

# Vagas
def requer_perm_vagas(acesso='VISUALIZAR'):
    """Decorator para permissões de vagas"""
    return requer_permissao('VAGAS', acesso)

def requer_perm_vagas_visualizar(view_func):
    """Decorator para visualizar vagas"""
    return requer_permissao('VAGAS', 'VISUALIZAR')(view_func)

def requer_perm_vagas_criar(view_func):
    """Decorator para criar vagas"""
    return requer_permissao('VAGAS', 'CRIAR')(view_func)

def requer_perm_vagas_editar(view_func):
    """Decorator para editar vagas"""
    return requer_permissao('VAGAS', 'EDITAR')(view_func)

def requer_perm_vagas_excluir(view_func):
    """Decorator para excluir vagas"""
    return requer_permissao('VAGAS', 'EXCLUIR')(view_func)

def requer_perm_vagas_admin(view_func):
    """Decorator para administrar vagas"""
    return requer_permissao('VAGAS', 'ADMINISTRAR')(view_func)

# Comissão
def requer_perm_comissao(acesso='VISUALIZAR'):
    """Decorator para permissões de comissão"""
    return requer_permissao('COMISSAO', acesso)

def requer_perm_comissao_visualizar(view_func):
    """Decorator para visualizar comissões"""
    return requer_permissao('COMISSAO', 'VISUALIZAR')(view_func)

def requer_perm_comissao_criar(view_func):
    """Decorator para criar comissões"""
    return requer_permissao('COMISSAO', 'CRIAR')(view_func)

def requer_perm_comissao_editar(view_func):
    """Decorator para editar comissões"""
    return requer_permissao('COMISSAO', 'EDITAR')(view_func)

def requer_perm_comissao_excluir(view_func):
    """Decorator para excluir comissões"""
    return requer_permissao('COMISSAO', 'EXCLUIR')(view_func)

def requer_perm_comissao_assinar(view_func):
    """Decorator para assinar comissões"""
    return requer_permissao('COMISSAO', 'ASSINAR')(view_func)

def requer_perm_comissao_admin(view_func):
    """Decorator para administrar comissões"""
    return requer_permissao('COMISSAO', 'ADMINISTRAR')(view_func)

# Documentos
def requer_perm_documentos(acesso='VISUALIZAR'):
    """Decorator para permissões de documentos"""
    return requer_permissao('DOCUMENTOS', acesso)

def requer_perm_documentos_visualizar(view_func):
    """Decorator para visualizar documentos"""
    return requer_permissao('DOCUMENTOS', 'VISUALIZAR')(view_func)

def requer_perm_documentos_criar(view_func):
    """Decorator para criar documentos"""
    return requer_permissao('DOCUMENTOS', 'CRIAR')(view_func)

def requer_perm_documentos_editar(view_func):
    """Decorator para editar documentos"""
    return requer_permissao('DOCUMENTOS', 'EDITAR')(view_func)

def requer_perm_documentos_excluir(view_func):
    """Decorator para excluir documentos"""
    return requer_permissao('DOCUMENTOS', 'EXCLUIR')(view_func)

def requer_perm_documentos_gerar_pdf(view_func):
    """Decorator para gerar PDF de documentos"""
    return requer_permissao('DOCUMENTOS', 'GERAR_PDF')(view_func)

def requer_perm_documentos_imprimir(view_func):
    """Decorator para imprimir documentos"""
    return requer_permissao('DOCUMENTOS', 'IMPRIMIR')(view_func)

def requer_perm_documentos_assinar(view_func):
    """Decorator para assinar documentos"""
    return requer_permissao('DOCUMENTOS', 'ASSINAR')(view_func)

def requer_perm_documentos_admin(view_func):
    """Decorator para administrar documentos"""
    return requer_permissao('DOCUMENTOS', 'ADMINISTRAR')(view_func)

# Usuários
def requer_perm_usuarios(acesso='VISUALIZAR'):
    """Decorator para permissões de usuários"""
    return requer_permissao('USUARIOS', acesso)

def requer_perm_usuarios_visualizar(view_func):
    """Decorator para visualizar usuários"""
    return requer_permissao('USUARIOS', 'VISUALIZAR')(view_func)

def requer_perm_usuarios_criar(view_func):
    """Decorator para criar usuários"""
    return requer_permissao('USUARIOS', 'CRIAR')(view_func)

def requer_perm_usuarios_editar(view_func):
    """Decorator para editar usuários"""
    return requer_permissao('USUARIOS', 'EDITAR')(view_func)

def requer_perm_usuarios_excluir(view_func):
    """Decorator para excluir usuários"""
    return requer_permissao('USUARIOS', 'EXCLUIR')(view_func)

def requer_perm_usuarios_admin(view_func):
    """Decorator para administrar usuários"""
    return requer_permissao('USUARIOS', 'ADMINISTRAR')(view_func)

# Relatórios
def requer_perm_relatorios(acesso='VISUALIZAR'):
    """Decorator para permissões de relatórios"""
    return requer_permissao('RELATORIOS', acesso)

def requer_perm_relatorios_visualizar(view_func):
    """Decorator para visualizar relatórios"""
    return requer_permissao('RELATORIOS', 'VISUALIZAR')(view_func)

def requer_perm_relatorios_gerar_pdf(view_func):
    """Decorator para gerar PDF de relatórios"""
    return requer_permissao('RELATORIOS', 'GERAR_PDF')(view_func)

def requer_perm_relatorios_imprimir(view_func):
    """Decorator para imprimir relatórios"""
    return requer_permissao('RELATORIOS', 'IMPRIMIR')(view_func)

def requer_perm_relatorios_admin(view_func):
    """Decorator para administrar relatórios"""
    return requer_permissao('RELATORIOS', 'ADMINISTRAR')(view_func)

# Configurações
def requer_perm_configuracoes(acesso='VISUALIZAR'):
    """Decorator para permissões de configurações"""
    return requer_permissao('CONFIGURACOES', acesso)

def requer_perm_configuracoes_visualizar(view_func):
    """Decorator para visualizar configurações"""
    return requer_permissao('CONFIGURACOES', 'VISUALIZAR')(view_func)

def requer_perm_configuracoes_editar(view_func):
    """Decorator para editar configurações"""
    return requer_permissao('CONFIGURACOES', 'EDITAR')(view_func)

def requer_perm_configuracoes_admin(view_func):
    """Decorator para administrar configurações"""
    return requer_permissao('CONFIGURACOES', 'ADMINISTRAR')(view_func)


# ============================================================================
# FUNÇÕES AUXILIARES PARA TEMPLATES
# ============================================================================

def tem_permissao_template(user, modulo, acesso):
    """
    Função para usar em templates
    """
    return tem_permissao(user, modulo, acesso)


def tem_permissao_modulo_template(user, modulo):
    """
    Função para usar em templates
    """
    return tem_permissao_modulo(user, modulo)


def obter_permissoes_template(user, modulo=None):
    """
    Função para usar em templates
    """
    return obter_permissoes_usuario(user, modulo)


# ============================================================================
# CONTEXT PROCESSOR PARA TEMPLATES
# ============================================================================

def permissoes_context(request):
    """
    Context processor para disponibilizar funções de permissão nos templates
    """
    return {
        'tem_permissao': lambda modulo, acesso: tem_permissao(request.user, modulo, acesso),
        'tem_permissao_modulo': lambda modulo: tem_permissao_modulo(request.user, modulo),
        'obter_permissoes': lambda modulo=None: obter_permissoes_usuario(request.user, modulo),
        'permissoes_usuario': obter_permissoes_usuario(request.user),
    } 