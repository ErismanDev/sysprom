#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Permissões Hierárquicas Integrado

Este módulo implementa um sistema de permissões onde:
- Permissões de DADOS: baseadas na hierarquia (órgão, grande comando, unidade, sub-unidade)
- Permissões GRANULARES: baseadas em menus, submenus e botões de ações

O sistema verifica:
1. Se o usuário tem acesso aos DADOS (baseado na hierarquia)
2. Se o usuário tem permissão GRANULAR para a ação (baseado na função militar)
"""

from django.contrib.auth import get_user_model
from .models import UsuarioSessao, UsuarioFuncaoMilitar, PermissaoFuncao, Militar
from .permissoes_simples import tem_permissao

User = get_user_model()


def obter_funcao_militar_ativa(user):
    """
    Obtém a função militar ativa da sessão do usuário
    """
    if not user or not user.is_authenticated:
        return None
    
    # Superusuários não precisam de sessão
    if user.is_superuser:
        return None
    
    try:
        from .models import UsuarioSessao
        sessao_ativa = UsuarioSessao.objects.filter(
            usuario=user,
            ativo=True
        ).first()
        
        if not sessao_ativa or not sessao_ativa.funcao_militar_usuario:
            return None
            
        return sessao_ativa.funcao_militar_usuario
        
    except Exception:
        return None


def pode_acessar_dados(user, militar=None, orgao=None, grande_comando=None, unidade=None, sub_unidade=None):
    """
    Verifica se o usuário tem acesso aos DADOS baseado na hierarquia
    
    Args:
        user: Usuário Django
        militar: Objeto Militar (opcional)
        orgao: Objeto Orgao (opcional)
        grande_comando: Objeto GrandeComando (opcional)
        unidade: Objeto Unidade (opcional)
        sub_unidade: Objeto SubUnidade (opcional)
        
    Returns:
        bool: True se tem acesso aos dados, False caso contrário
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm acesso total
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    # Verificar acesso hierárquico usando o campo 'acesso' da FuncaoMilitar
    funcao_militar = funcao_usuario.funcao_militar
    
    # Se o acesso é TOTAL, permitir independente da lotação
    if funcao_militar.acesso == 'TOTAL':
        return True
    
    # Se foi passado um militar, extrair sua lotação
    if militar:
        if hasattr(militar, 'lotacao_atual') and militar.lotacao_atual:
            lotacao = militar.lotacao_atual
            orgao = lotacao.orgao
            grande_comando = lotacao.grande_comando
            unidade = lotacao.unidade
            sub_unidade = lotacao.sub_unidade
        else:
            # Se não tem lotação, não pode acessar (exceto para TOTAL)
            return False
    
    return funcao_militar.pode_acessar_lotacao(orgao, grande_comando, unidade, sub_unidade)


def tem_permissao_completa(user, modulo, acao, militar=None, orgao=None, grande_comando=None, unidade=None, sub_unidade=None):
    """
    Verifica se o usuário tem permissão COMPLETA (dados + granulares)
    
    Args:
        user: Usuário Django
        modulo: Módulo (ex: 'militares', 'dashboard')
        acao: Ação (ex: 'visualizar', 'criar', 'editar')
        militar: Objeto Militar (opcional)
        orgao: Objeto Orgao (opcional)
        grande_comando: Objeto GrandeComando (opcional)
        unidade: Objeto Unidade (opcional)
        sub_unidade: Objeto SubUnidade (opcional)
        
    Returns:
        bool: True se tem permissão completa, False caso contrário
    """
    # 1. Verificar permissão granular de interface (menus, submenus, botões de ação)
    if not tem_permissao(user, modulo, acao):
        return False
    
    # 2. Verificar permissão hierárquica de acesso aos dados
    # Se a permissão granular é para um menu/submenu que não lida diretamente com dados hierárquicos
    # (ex: Dashboard, Minhas Informações), então a permissão granular já é suficiente.
    # Caso contrário, precisamos verificar o acesso aos dados.
    
    # Módulos que precisam de verificação de dados hierárquicos
    modulos_com_restricao_de_dados = [
        'militares', 'inativos', 'lotacoes', # Exemplo de módulos que lidam com dados hierárquicos
        # Adicionar outros módulos conforme necessário
    ]

    if modulo in modulos_com_restricao_de_dados:
        return pode_acessar_dados(
            user,
            militar=militar,
            orgao=orgao,
            grande_comando=grande_comando,
            unidade=unidade,
            sub_unidade=sub_unidade
        )
    
    return True # Se não é um módulo com restrição de dados, a permissão granular é suficiente


def pode_visualizar_militar(user, militar):
    """
    Verifica se o usuário pode visualizar um militar específico
    
    Args:
        user: Usuário Django
        militar: Objeto Militar
        
    Returns:
        bool: True se pode visualizar, False caso contrário
    """
    # Verificar permissão granular
    if not tem_permissao(user, 'militares', 'visualizar'):
        return False
    
    # Verificar acesso aos dados
    return pode_acessar_dados(user, militar=militar)


def pode_editar_militar(user, militar):
    """
    Verifica se o usuário pode editar um militar específico
    
    Args:
        user: Usuário Django
        militar: Objeto Militar
        
    Returns:
        bool: True se pode editar, False caso contrário
    """
    # Verificar permissão granular
    if not tem_permissao(user, 'militares', 'editar'):
        return False
    
    # Verificar acesso aos dados
    return pode_acessar_dados(user, militar=militar)


def pode_executar_acao(user, modulo, acao):
    """
    Verifica se pode executar uma ação específica (apenas permissões granulares)
    """
    return tem_permissao(user, modulo, acao)


def obter_nivel_acesso_usuario(user):
    """
    Retorna o nível de acesso hierárquico do usuário
    
    Returns:
        str: Nível de acesso ('TOTAL', 'ORGAO', 'GRANDE_COMANDO', 'UNIDADE', 'SUBUNIDADE', 'NENHUM')
    """
    if not user or not user.is_authenticated:
        return 'NENHUM'
    
    if user.is_superuser:
        return 'TOTAL'
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return 'NENHUM'
    
    # Usar o campo 'acesso' da FuncaoMilitar em vez do 'nivel_acesso' da UsuarioFuncaoMilitar
    return funcao_usuario.funcao_militar.acesso


def obter_lotacao_usuario(user):
    """
    Retorna a lotação do usuário baseada na função ativa
    
    Returns:
        dict: Dicionário com informações da lotação
    """
    if not user or not user.is_authenticated:
        return None
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return None
    
    return {
        'orgao': funcao_usuario.orgao,
        'grande_comando': funcao_usuario.grande_comando,
        'unidade': funcao_usuario.unidade,
        'sub_unidade': funcao_usuario.sub_unidade,
    }


def filtrar_militares_por_acesso(user, queryset):
    """
    Filtra um queryset de militares baseado no acesso hierárquico do usuário
    
    Args:
        user: Usuário Django
        queryset: QuerySet de militares
        
    Returns:
        QuerySet filtrado
    """
    if not user or not user.is_authenticated:
        return queryset.none()
    
    # Superusuários veem tudo
    if user.is_superuser:
        return queryset
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return queryset.none()
    
    # Aplicar filtros baseados no nível de acesso da FuncaoMilitar
    funcao_militar = funcao_usuario.funcao_militar
    nivel_acesso = funcao_militar.acesso
    
    if nivel_acesso == 'TOTAL':
        return queryset
    
    elif nivel_acesso == 'ORGAO':
        if not funcao_usuario.orgao:
            return queryset.none()
        return queryset.filter(
            lotacao_atual__orgao=funcao_usuario.orgao
        )
    
    elif nivel_acesso == 'GRANDE_COMANDO':
        if not funcao_usuario.grande_comando:
            return queryset.none()
        return queryset.filter(
            lotacao_atual__grande_comando=funcao_usuario.grande_comando
        )
    
    elif nivel_acesso == 'UNIDADE':
        if not funcao_usuario.unidade:
            return queryset.none()
        return queryset.filter(
            lotacao_atual__unidade=funcao_usuario.unidade
        )
    
    elif nivel_acesso == 'SUBUNIDADE':
        if not funcao_usuario.sub_unidade:
            return queryset.none()
        return queryset.filter(
            lotacao_atual__sub_unidade=funcao_usuario.sub_unidade
        )
    
    else:  # NENHUM
        return queryset.none()


# Funções de compatibilidade para o sistema atual
def pode_visualizar_militares(user):
    """Verifica se pode visualizar militares (apenas permissões granulares)"""
    return tem_permissao(user, 'militares', 'visualizar')


def pode_criar_militares(user):
    """Verifica se pode criar militares (apenas permissões granulares)"""
    return tem_permissao(user, 'militares', 'criar')


def pode_editar_militares(user):
    """Verifica se pode editar militares (apenas permissões granulares)"""
    return tem_permissao(user, 'militares', 'editar')


def pode_excluir_militares(user):
    """Verifica se pode excluir militares (apenas permissões granulares)"""
    return tem_permissao(user, 'militares', 'excluir')


def pode_acessar_lotacao(user, orgao=None, grande_comando=None, unidade=None, sub_unidade=None):
    """
    Verifica se o usuário pode acessar uma lotação específica baseado na hierarquia
    
    Args:
        user: Usuário Django
        orgao: Objeto Orgao (opcional)
        grande_comando: Objeto GrandeComando (opcional)
        unidade: Objeto Unidade (opcional)
        sub_unidade: Objeto SubUnidade (opcional)
        
    Returns:
        bool: True se tem acesso à lotação, False caso contrário
    """
    return pode_acessar_dados(user, orgao=orgao, grande_comando=grande_comando, unidade=unidade, sub_unidade=sub_unidade)


def obter_areas_acesso_usuario(user):
    """
    Retorna as áreas de acesso do usuário baseadas na hierarquia
    
    Returns:
        dict: Dicionário com informações sobre as áreas de acesso
    """
    if not user or not user.is_authenticated:
        return {'nivel': 'NENHUM', 'areas': []}
    
    if user.is_superuser:
        return {'nivel': 'TOTAL', 'areas': ['Sistema completo']}
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return {'nivel': 'NENHUM', 'areas': []}
    
    areas = []
    funcao_militar = funcao_usuario.funcao_militar
    nivel = funcao_militar.acesso
    
    if funcao_usuario.orgao:
        areas.append(f"Órgão: {funcao_usuario.orgao.sigla}")
    
    if funcao_usuario.grande_comando:
        areas.append(f"Grande Comando: {funcao_usuario.grande_comando.sigla}")
    
    if funcao_usuario.unidade:
        areas.append(f"Unidade: {funcao_usuario.unidade.sigla}")
    
    if funcao_usuario.sub_unidade:
        areas.append(f"Sub-Unidade: {funcao_usuario.sub_unidade.sigla}")
    
    return {
        'nivel': nivel,
        'areas': areas,
        'orgao': funcao_usuario.orgao,
        'grande_comando': funcao_usuario.grande_comando,
        'unidade': funcao_usuario.unidade,
        'sub_unidade': funcao_usuario.sub_unidade,
    }