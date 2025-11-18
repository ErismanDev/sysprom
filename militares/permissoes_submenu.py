#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de permissões de submenu (sistema antigo removido)
Este arquivo foi criado para resolver erro de importação
"""

def pode_visualizar_submenu(user, submenu):
    """
    Função de compatibilidade para verificar se pode visualizar um submenu específico
    """
    from .permissoes_simples import tem_permissao
    return tem_permissao(user, submenu.lower(), 'visualizar')

def tem_acesso_secao_promocoes(user):
    """
    Função de compatibilidade para verificar se tem acesso à seção de promoções
    """
    from .permissoes_simples import tem_permissao
    return (tem_permissao(user, 'promocoes', 'visualizar') or 
            tem_permissao(user, 'calendarios', 'visualizar') or
            tem_permissao(user, 'comissoes', 'visualizar') or
            tem_permissao(user, 'quadros_acesso', 'visualizar') or
            tem_permissao(user, 'quadros_fixacao', 'visualizar'))
