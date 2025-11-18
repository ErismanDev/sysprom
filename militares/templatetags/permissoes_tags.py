from django import template
from militares.permissoes_simples import obter_funcao_militar_ativa as obter_funcao_militar_ativa_from_module

register = template.Library()

@register.filter
def tem_permissao(permissoes_dict, key):
    """Verifica se uma permissão específica existe no dicionário"""
    if not isinstance(permissoes_dict, dict):
        return False
    return permissoes_dict.get(key, False)

@register.filter
def modulo_tem_permissao(permissoes_dict, modulo):
    """Verifica se um módulo tem alguma permissão"""
    if not isinstance(permissoes_dict, dict):
        return False
    for key in permissoes_dict.keys():
        if key.startswith(modulo + '_'):
            return True
    return False

@register.filter
def obter_funcao_militar_ativa(user):
    """Obtém a função militar ativa do usuário"""
    return obter_funcao_militar_ativa_from_module(user)