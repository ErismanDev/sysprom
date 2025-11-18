# -*- coding: utf-8 -*-
"""
Sistema de Permissões por Níveis Hierárquicos
Baseado no acesso (TOTAL, ORGAO, GRANDE_COMANDO, UNIDADE, SUBUNIDADE) e nível (1-5)
"""

from .models import UsuarioMaster, UsuarioSessao, FuncaoMilitar
from django.contrib.auth.models import User


def obter_nivel_hierarquico_usuario(user):
    """
    Obtém o nível hierárquico do usuário baseado na função militar ativa
    Retorna: {'acesso': 'UNIDADE', 'nivel': 3} ou None se não encontrado
    """
    try:
        # Verificar se é usuário master
        if hasattr(user, 'usuariomaster') and user.usuariomaster:
            return {'acesso': 'TOTAL', 'nivel': 5}
        
        # Verificar se é superusuário
        if user.is_superuser:
            return {'acesso': 'TOTAL', 'nivel': 5}
        
        # Buscar sessão ativa
        sessao = UsuarioSessao.objects.filter(
            usuario=user,
            ativo=True
        ).first()
        
        if not sessao or not sessao.funcao_militar_usuario:
            return None
        
        funcao = sessao.funcao_militar_usuario.funcao_militar
        return {
            'acesso': funcao.acesso,
            'nivel': funcao.nivel
        }
    
    except Exception:
        return None


def tem_nivel_suficiente(user, acesso_requerido, nivel_requerido):
    """
    Verifica se o usuário tem nível suficiente para acessar uma funcionalidade
    
    Args:
        user: Usuário Django
        acesso_requerido: 'TOTAL', 'ORGAO', 'GRANDE_COMANDO', 'UNIDADE', 'SUBUNIDADE'
        nivel_requerido: 1-5 (nível mínimo necessário)
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    nivel_usuario = obter_nivel_hierarquico_usuario(user)
    
    if not nivel_usuario:
        return False
    
    # Mapear hierarquia de acesso (maior = mais permissões)
    hierarquia_acesso = {
        'TOTAL': 5,
        'ORGAO': 4,
        'GRANDE_COMANDO': 3,
        'UNIDADE': 2,
        'SUBUNIDADE': 1,
        'NENHUM': 0
    }
    
    acesso_usuario = hierarquia_acesso.get(nivel_usuario['acesso'], 0)
    acesso_necessario = hierarquia_acesso.get(acesso_requerido, 0)
    
    # Verificar se o acesso é suficiente
    if acesso_usuario < acesso_necessario:
        return False
    
    # Se o acesso é igual, verificar o nível
    if acesso_usuario == acesso_necessario:
        return nivel_usuario['nivel'] >= nivel_requerido
    
    # Se o acesso é maior, tem permissão independente do nível
    return True


def pode_gerenciar_militares(user):
    """
    Verifica se o usuário pode gerenciar militares baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'UNIDADE', 3)


def pode_editar_militares(user):
    """
    Verifica se o usuário pode editar militares baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'UNIDADE', 4)


def pode_excluir_militares(user):
    """
    Verifica se o usuário pode excluir militares baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'UNIDADE', 5)


def pode_gerenciar_usuarios(user):
    """
    Verifica se o usuário pode gerenciar usuários baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'ORGAO', 4)


def pode_gerenciar_funcoes(user):
    """
    Verifica se o usuário pode gerenciar funções militares baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'ORGAO', 5)


def pode_gerenciar_permissoes(user):
    """
    Verifica se o usuário pode gerenciar permissões baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'TOTAL', 5)


def pode_acessar_relatorios(user):
    """
    Verifica se o usuário pode acessar relatórios baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'UNIDADE', 2)


def pode_acessar_dashboard(user):
    """
    Verifica se o usuário pode acessar dashboard baseado no nível hierárquico
    """
    return tem_nivel_suficiente(user, 'UNIDADE', 1)


def obter_permissoes_por_nivel(acesso, nivel):
    """
    Retorna as permissões disponíveis para um determinado acesso e nível
    
    Args:
        acesso: 'TOTAL', 'ORGAO', 'GRANDE_COMANDO', 'UNIDADE', 'SUBUNIDADE'
        nivel: 1-5
    
    Returns:
        dict: Dicionário com as permissões disponíveis
    """
    permissoes = {
        'gerenciar_militares': False,
        'editar_militares': False,
        'excluir_militares': False,
        'gerenciar_usuarios': False,
        'gerenciar_funcoes': False,
        'gerenciar_permissoes': False,
        'acessar_relatorios': False,
        'acessar_dashboard': False,
    }
    
    # Mapear hierarquia de acesso
    hierarquia_acesso = {
        'TOTAL': 5,
        'ORGAO': 4,
        'GRANDE_COMANDO': 3,
        'UNIDADE': 2,
        'SUBUNIDADE': 1,
        'NENHUM': 0
    }
    
    acesso_num = hierarquia_acesso.get(acesso, 0)
    
    # Permissões por nível e acesso
    if acesso_num >= 2:  # UNIDADE ou superior
        permissoes['acessar_dashboard'] = nivel >= 1
        permissoes['acessar_relatorios'] = nivel >= 2
        permissoes['gerenciar_militares'] = nivel >= 3
        permissoes['editar_militares'] = nivel >= 4
        permissoes['excluir_militares'] = nivel >= 5
    
    if acesso_num >= 4:  # ORGAO ou superior
        permissoes['gerenciar_usuarios'] = nivel >= 4
        permissoes['gerenciar_funcoes'] = nivel >= 5
    
    if acesso_num >= 5:  # TOTAL
        permissoes['gerenciar_permissoes'] = nivel >= 5
    
    return permissoes


def obter_descricao_nivel(acesso, nivel):
    """
    Retorna uma descrição do nível hierárquico do usuário
    """
    descricoes = {
        'TOTAL': {
            1: 'Acesso Total - Nível 1 (Básico)',
            2: 'Acesso Total - Nível 2 (Intermediário)',
            3: 'Acesso Total - Nível 3 (Avançado)',
            4: 'Acesso Total - Nível 4 (Especialista)',
            5: 'Acesso Total - Nível 5 (Master)'
        },
        'ORGAO': {
            1: 'Acesso Órgão - Nível 1 (Básico)',
            2: 'Acesso Órgão - Nível 2 (Intermediário)',
            3: 'Acesso Órgão - Nível 3 (Avançado)',
            4: 'Acesso Órgão - Nível 4 (Especialista)',
            5: 'Acesso Órgão - Nível 5 (Master)'
        },
        'GRANDE_COMANDO': {
            1: 'Acesso Grande Comando - Nível 1 (Básico)',
            2: 'Acesso Grande Comando - Nível 2 (Intermediário)',
            3: 'Acesso Grande Comando - Nível 3 (Avançado)',
            4: 'Acesso Grande Comando - Nível 4 (Especialista)',
            5: 'Acesso Grande Comando - Nível 5 (Master)'
        },
        'UNIDADE': {
            1: 'Acesso Unidade - Nível 1 (Básico)',
            2: 'Acesso Unidade - Nível 2 (Intermediário)',
            3: 'Acesso Unidade - Nível 3 (Avançado)',
            4: 'Acesso Unidade - Nível 4 (Especialista)',
            5: 'Acesso Unidade - Nível 5 (Master)'
        },
        'SUBUNIDADE': {
            1: 'Acesso Subunidade - Nível 1 (Básico)',
            2: 'Acesso Subunidade - Nível 2 (Intermediário)',
            3: 'Acesso Subunidade - Nível 3 (Avançado)',
            4: 'Acesso Subunidade - Nível 4 (Especialista)',
            5: 'Acesso Subunidade - Nível 5 (Master)'
        }
    }
    
    return descricoes.get(acesso, {}).get(nivel, 'Nível não definido')
