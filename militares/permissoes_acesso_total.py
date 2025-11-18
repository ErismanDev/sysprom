"""
Permissões de acesso total para funções específicas da Seção de Promoções
"""

def tem_funcao_acesso_total_secao_promocoes(user):
    """
    Verifica se o usuário tem função que dá acesso total à Seção de Promoções
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Verificar funções específicas que dão acesso total
    funcoes_acesso_total = [
        'Chefe da Seção de Promoções',
        'Diretor de Gestão de Pessoas',
        'Auxiliar da Seção de Promoções'
    ]
    
    return user.funcoes_militares.filter(
        funcao_militar__nome__in=funcoes_acesso_total,
        ativo=True
    ).exists()


def pode_acessar_fichas_conceito_oficiais(user):
    """
    Verifica se o usuário pode acessar fichas de conceito de oficiais
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_fichas_conceito_pracas(user):
    """
    Verifica se o usuário pode acessar fichas de conceito de praças
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_calendarios_promocoes(user):
    """
    Verifica se o usuário pode acessar calendários de promoções
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_quadros_fixacao_vagas(user):
    """
    Verifica se o usuário pode acessar quadros de fixação de vagas
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_quadros_acesso(user):
    """
    Verifica se o usuário pode acessar quadros de acesso
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_comissoes_promocoes(user):
    """
    Verifica se o usuário pode acessar comissões de promoções
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_meus_votos(user):
    """
    Verifica se o usuário pode acessar meus votos
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_promocoes(user):
    """
    Verifica se o usuário pode acessar promoções
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_acessar_almanaques(user):
    """
    Verifica se o usuário pode acessar almanaques
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_fichas_conceito(user):
    """
    Verifica se o usuário pode editar fichas de conceito
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_militares(user):
    """
    Verifica se o usuário pode editar militares
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_quadros_acesso(user):
    """
    Verifica se o usuário pode editar quadros de acesso
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_quadros_fixacao_vagas(user):
    """
    Verifica se o usuário pode editar quadros de fixação de vagas
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_comissoes(user):
    """
    Verifica se o usuário pode editar comissões
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_promocoes(user):
    """
    Verifica se o usuário pode editar promoções
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_almanaques(user):
    """
    Verifica se o usuário pode editar almanaques
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def pode_editar_calendarios_promocoes(user):
    """
    Verifica se o usuário pode editar calendários de promoções
    """
    return tem_funcao_acesso_total_secao_promocoes(user)


def obter_permissoes_secao_promocoes(user):
    """
    Retorna um dicionário com todas as permissões da seção de promoções
    """
    if not tem_funcao_acesso_total_secao_promocoes(user):
        return {
            'show_fichas_oficiais': False,
            'show_fichas_pracas': False,
            'show_calendarios': False,
            'show_quadros_fixacao': False,
            'show_quadros_acesso': False,
            'show_comissoes': False,
            'show_meus_votos': False,
            'show_promocoes': False,
            'show_almanaques': False,
            'can_edit_fichas_conceito': False,
            'can_edit_militares': False,
            'can_edit_quadros_acesso': False,
            'can_edit_quadros_fixacao': False,
            'can_edit_comissoes': False,
            'can_edit_promocoes': False,
            'can_edit_almanaques': False,
            'can_edit_calendarios': False,
        }
    
    # Se tem função de acesso total, retorna todas as permissões como True
    return {
        'show_fichas_oficiais': True,
        'show_fichas_pracas': True,
        'show_calendarios': True,
        'show_quadros_fixacao': True,
        'show_quadros_acesso': True,
        'show_comissoes': True,
        'show_meus_votos': True,
        'show_promocoes': True,
        'show_almanaques': True,
        'can_edit_fichas_conceito': True,
        'can_edit_militares': True,
        'can_edit_quadros_acesso': True,
        'can_edit_quadros_fixacao': True,
        'can_edit_comissoes': True,
        'can_edit_promocoes': True,
        'can_edit_almanaques': True,
        'can_edit_calendarios': True,
    }
