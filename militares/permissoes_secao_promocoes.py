"""
Permissões específicas para Seção de Promoções
"""

def tem_funcao_secao_promocoes(user):
    """
    Verifica se o usuário tem função de seção de promoções
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Verificar funções específicas
    funcoes_especiais = [
        'Chefe da Seção de Promoções',
        'Diretor de Gestão de Pessoas',
        'Auxiliar da Seção de Promoções'
    ]
    
    return user.funcoes_militares.filter(
        funcao_militar__nome__in=funcoes_especiais,
        ativo=True
    ).exists()


def pode_gerenciar_secao_promocoes(user):
    """
    Verifica se o usuário pode gerenciar seções de promoções
    Apenas chefe da seção de promoções, diretor de gestão de pessoas e auxiliar da seção de promoções
    """
    return tem_funcao_secao_promocoes(user)


def pode_criar_secao_promocoes(user):
    """
    Verifica se o usuário pode criar seções de promoções
    """
    return tem_funcao_secao_promocoes(user)


def pode_editar_secao_promocoes(user):
    """
    Verifica se o usuário pode editar seções de promoções
    """
    return tem_funcao_secao_promocoes(user)


def pode_excluir_secao_promocoes(user):
    """
    Verifica se o usuário pode excluir seções de promoções
    """
    return tem_funcao_secao_promocoes(user)


def pode_ativar_desativar_secao_promocoes(user):
    """
    Verifica se o usuário pode ativar/desativar seções de promoções
    """
    return tem_funcao_secao_promocoes(user)


def pode_acessar_dashboard_secao_promocoes(user):
    """
    Verifica se o usuário pode acessar o dashboard da seção de promoções
    """
    return tem_funcao_secao_promocoes(user)


def obter_funcoes_secao_promocoes(user):
    """
    Retorna as funções de seção de promoções do usuário
    """
    if not user or not user.is_authenticated:
        return []
    
    funcoes_especiais = [
        'Chefe da Seção de Promoções',
        'Diretor de Gestão de Pessoas',
        'Auxiliar da Seção de Promoções'
    ]
    
    return user.funcoes_militares.filter(
        funcao_militar__nome__in=funcoes_especiais,
        ativo=True
    ).values_list('funcao_militar__nome', flat=True)
