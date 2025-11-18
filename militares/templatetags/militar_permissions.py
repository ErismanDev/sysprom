from django import template
from militares.permissoes_hierarquicas import pode_editar_militar, pode_visualizar_militar

register = template.Library()

@register.filter
def pode_editar_militar_template(militar, user):
    """
    Template filter para verificar se o usuário pode editar um militar específico
    """
    return pode_editar_militar(user, militar)

@register.filter
def pode_visualizar_militar_template(militar, user):
    """
    Template filter para verificar se o usuário pode visualizar um militar específico
    """
    return pode_visualizar_militar(user, militar)

@register.filter
def pode_editar_publicacao(publicacao, user):
    """
    Template filter para verificar se o usuário pode editar uma publicação
    """
    return publicacao.can_edit(user)

@register.filter
def pode_publicar_publicacao(publicacao, user):
    """
    Template filter para verificar se o usuário pode publicar uma publicação
    """
    return publicacao.can_publish(user)
