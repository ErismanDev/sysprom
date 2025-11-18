"""
Template tags para verificar permissões granulares
"""
from django import template
from militares.permissoes_simples import tem_permissao

register = template.Library()

@register.filter
def tem_permissao_granular(user, permissao):
    """
    Verifica se o usuário tem uma permissão granular específica
    
    Uso no template:
    {% if user|tem_permissao_granular:"fichas_oficiais_visualizar" %}
    """
    if not user or not user.is_authenticated:
        return False
    
    # Separar módulo e ação
    if '_' in permissao:
        modulo, acao = permissao.rsplit('_', 1)
        return tem_permissao(user, modulo, acao)
    
    return False

@register.filter
def pode_visualizar(user, modulo):
    """Verifica se pode visualizar um módulo"""
    return tem_permissao(user, modulo, 'visualizar')

@register.filter
def pode_criar(user, modulo):
    """Verifica se pode criar em um módulo"""
    return tem_permissao(user, modulo, 'criar')

@register.filter
def pode_editar(user, modulo):
    """Verifica se pode editar em um módulo"""
    return tem_permissao(user, modulo, 'editar')

@register.filter
def pode_excluir(user, modulo):
    """Verifica se pode excluir em um módulo"""
    return tem_permissao(user, modulo, 'excluir')

@register.filter
def pode_gerenciar(user, modulo):
    """Verifica se pode gerenciar um módulo"""
    return tem_permissao(user, modulo, 'gerenciar')

# Filtros específicos para módulos comuns
@register.filter
def pode_visualizar_fichas_oficiais(user):
    """Verifica se pode visualizar fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'visualizar')

@register.filter
def pode_criar_fichas_oficiais(user):
    """Verifica se pode criar fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'criar')

@register.filter
def pode_editar_fichas_oficiais(user):
    """Verifica se pode editar fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'editar')

@register.filter
def pode_excluir_fichas_oficiais(user):
    """Verifica se pode excluir fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'excluir')

@register.filter
def pode_visualizar_fichas_pracas(user):
    """Verifica se pode visualizar fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'visualizar')

@register.filter
def pode_criar_fichas_pracas(user):
    """Verifica se pode criar fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'criar')

@register.filter
def pode_editar_fichas_pracas(user):
    """Verifica se pode editar fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'editar')

@register.filter
def pode_excluir_fichas_pracas(user):
    """Verifica se pode excluir fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'excluir')

@register.filter
def pode_visualizar_quadros_acesso(user):
    """Verifica se pode visualizar quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'visualizar')

@register.filter
def pode_criar_quadros_acesso(user):
    """Verifica se pode criar quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'criar')

@register.filter
def pode_editar_quadros_acesso(user):
    """Verifica se pode editar quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'editar')

@register.filter
def pode_excluir_quadros_acesso(user):
    """Verifica se pode excluir quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'excluir')

@register.filter
def pode_visualizar_quadros_fixacao(user):
    """Verifica se pode visualizar quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'visualizar')

@register.filter
def pode_criar_quadros_fixacao(user):
    """Verifica se pode criar quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'criar')

@register.filter
def pode_editar_quadros_fixacao(user):
    """Verifica se pode editar quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'editar')

@register.filter
def pode_excluir_quadros_fixacao(user):
    """Verifica se pode excluir quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'excluir')

@register.filter
def pode_visualizar_almanaques(user):
    """Verifica se pode visualizar almanaques"""
    return tem_permissao(user, 'almanaques', 'visualizar')

@register.filter
def pode_criar_almanaques(user):
    """Verifica se pode criar almanaques"""
    return tem_permissao(user, 'almanaques', 'criar')

@register.filter
def pode_criar_militares(user):
    """Verifica se pode criar militares"""
    return tem_permissao(user, 'militares', 'criar')

@register.filter
def pode_editar_almanaques(user):
    """Verifica se pode editar almanaques"""
    return tem_permissao(user, 'almanaques', 'editar')

@register.filter
def pode_excluir_almanaques(user):
    """Verifica se pode excluir almanaques"""
    return tem_permissao(user, 'almanaques', 'excluir')

@register.filter
def pode_visualizar_promocoes(user):
    """Verifica se pode visualizar promoções"""
    return tem_permissao(user, 'promocoes', 'visualizar')

@register.filter
def pode_criar_promocoes(user):
    """Verifica se pode criar promoções"""
    return tem_permissao(user, 'promocoes', 'criar')

@register.filter
def pode_editar_promocoes(user):
    """Verifica se pode editar promoções"""
    return tem_permissao(user, 'promocoes', 'editar')

@register.filter
def pode_excluir_promocoes(user):
    """Verifica se pode excluir promoções"""
    return tem_permissao(user, 'promocoes', 'excluir')

@register.filter
def pode_visualizar_calendarios(user):
    """Verifica se pode visualizar calendários"""
    return tem_permissao(user, 'calendarios', 'visualizar')

@register.filter
def pode_criar_calendarios(user):
    """Verifica se pode criar calendários"""
    return tem_permissao(user, 'calendarios', 'criar')

@register.filter
def pode_editar_calendarios(user):
    """Verifica se pode editar calendários"""
    return tem_permissao(user, 'calendarios', 'editar')

@register.filter
def pode_excluir_calendarios(user):
    """Verifica se pode excluir calendários"""
    return tem_permissao(user, 'calendarios', 'excluir')

@register.filter
def pode_visualizar_comissoes(user):
    """Verifica se pode visualizar comissões"""
    return tem_permissao(user, 'comissoes', 'visualizar')

@register.filter
def pode_criar_comissoes(user):
    """Verifica se pode criar comissões"""
    return tem_permissao(user, 'comissoes', 'criar')

@register.filter
def pode_editar_comissoes(user):
    """Verifica se pode editar comissões"""
    return tem_permissao(user, 'comissoes', 'editar')

@register.filter
def pode_excluir_comissoes(user):
    """Verifica se pode excluir comissões"""
    return tem_permissao(user, 'comissoes', 'excluir')

@register.filter
def pode_visualizar_usuarios(user):
    """Verifica se pode visualizar usuários"""
    return tem_permissao(user, 'usuarios', 'visualizar')

@register.filter
def pode_gerenciar_usuarios(user):
    """Verifica se pode gerenciar usuários"""
    return tem_permissao(user, 'usuarios', 'gerenciar')

@register.filter
def pode_gerenciar_permissoes(user):
    """Verifica se pode gerenciar permissões"""
    return tem_permissao(user, 'permissoes', 'gerenciar')

@register.filter
def pode_acessar_logs(user):
    """Verifica se pode acessar logs"""
    return tem_permissao(user, 'logs', 'acessar')

@register.filter
def pode_gerenciar_medalhas(user):
    """Verifica se pode gerenciar medalhas"""
    return tem_permissao(user, 'medalhas', 'gerenciar')
