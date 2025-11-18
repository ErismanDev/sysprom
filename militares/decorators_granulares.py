"""
Decoradores para sistema de permissões granulares
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .permissoes_simples import tem_permissao


def permissao_requerida(modulo, acao):
    """
    Decorator para verificar permissão granular específica
    
    Args:
        modulo: Nome do módulo (ex: 'fichas_oficiais', 'quadros_acesso', etc.)
        acao: Ação (ex: 'visualizar', 'criar', 'editar', 'excluir', 'gerenciar')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Verificar permissão granular
            if not tem_permissao(request.user, modulo, acao):
                messages.error(request, f'Acesso negado. Você não tem permissão para {acao} {modulo}.')
                return HttpResponseForbidden('Acesso negado')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def permissao_visualizar(modulo):
    """Decorator para permissão de visualização"""
    return permissao_requerida(modulo, 'visualizar')


def permissao_criar(modulo):
    """Decorator para permissão de criação"""
    return permissao_requerida(modulo, 'criar')


def permissao_editar(modulo):
    """Decorator para permissão de edição"""
    return permissao_requerida(modulo, 'editar')


def permissao_excluir(modulo):
    """Decorator para permissão de exclusão"""
    return permissao_requerida(modulo, 'excluir')


def permissao_gerenciar(modulo):
    """Decorator para permissão de gerenciamento"""
    return permissao_requerida(modulo, 'gerenciar')


# Decoradores específicos para módulos comuns
def pode_visualizar_fichas_oficiais(view_func):
    """Decorator para visualizar fichas de oficiais"""
    return permissao_visualizar('fichas_oficiais')(view_func)


def pode_criar_fichas_oficiais(view_func):
    """Decorator para criar fichas de oficiais"""
    return permissao_criar('fichas_oficiais')(view_func)


def pode_editar_fichas_oficiais(view_func):
    """Decorator para editar fichas de oficiais"""
    return permissao_editar('fichas_oficiais')(view_func)


def pode_excluir_fichas_oficiais(view_func):
    """Decorator para excluir fichas de oficiais"""
    return permissao_excluir('fichas_oficiais')(view_func)


def pode_visualizar_fichas_pracas(view_func):
    """Decorator para visualizar fichas de praças"""
    return permissao_visualizar('fichas_pracas')(view_func)


def pode_criar_fichas_pracas(view_func):
    """Decorator para criar fichas de praças"""
    return permissao_criar('fichas_pracas')(view_func)


def pode_editar_fichas_pracas(view_func):
    """Decorator para editar fichas de praças"""
    return permissao_editar('fichas_pracas')(view_func)


def pode_excluir_fichas_pracas(view_func):
    """Decorator para excluir fichas de praças"""
    return permissao_excluir('fichas_pracas')(view_func)


def pode_visualizar_quadros_acesso(view_func):
    """Decorator para visualizar quadros de acesso"""
    return permissao_visualizar('quadros_acesso')(view_func)


def pode_criar_quadros_acesso(view_func):
    """Decorator para criar quadros de acesso"""
    return permissao_criar('quadros_acesso')(view_func)


def pode_editar_quadros_acesso(view_func):
    """Decorator para editar quadros de acesso"""
    return permissao_editar('quadros_acesso')(view_func)


def pode_excluir_quadros_acesso(view_func):
    """Decorator para excluir quadros de acesso"""
    return permissao_excluir('quadros_acesso')(view_func)


def pode_visualizar_quadros_fixacao(view_func):
    """Decorator para visualizar quadros de fixação"""
    return permissao_visualizar('quadros_fixacao')(view_func)


def pode_criar_quadros_fixacao(view_func):
    """Decorator para criar quadros de fixação"""
    return permissao_criar('quadros_fixacao')(view_func)


def pode_editar_quadros_fixacao(view_func):
    """Decorator para editar quadros de fixação"""
    return permissao_editar('quadros_fixacao')(view_func)


def pode_excluir_quadros_fixacao(view_func):
    """Decorator para excluir quadros de fixação"""
    return permissao_excluir('quadros_fixacao')(view_func)


def pode_visualizar_almanaques(view_func):
    """Decorator para visualizar almanaques"""
    return permissao_visualizar('almanaques')(view_func)


def pode_criar_almanaques(view_func):
    """Decorator para criar almanaques"""
    return permissao_criar('almanaques')(view_func)


def pode_editar_almanaques(view_func):
    """Decorator para editar almanaques"""
    return permissao_editar('almanaques')(view_func)


def pode_excluir_almanaques(view_func):
    """Decorator para excluir almanaques"""
    return permissao_excluir('almanaques')(view_func)


def pode_visualizar_promocoes(view_func):
    """Decorator para visualizar promoções"""
    return permissao_visualizar('promocoes')(view_func)


def pode_criar_promocoes(view_func):
    """Decorator para criar promoções"""
    return permissao_criar('promocoes')(view_func)


def pode_editar_promocoes(view_func):
    """Decorator para editar promoções"""
    return permissao_editar('promocoes')(view_func)


def pode_excluir_promocoes(view_func):
    """Decorator para excluir promoções"""
    return permissao_excluir('promocoes')(view_func)


def pode_visualizar_calendarios(view_func):
    """Decorator para visualizar calendários"""
    return permissao_visualizar('calendarios')(view_func)


def pode_criar_calendarios(view_func):
    """Decorator para criar calendários"""
    return permissao_criar('calendarios')(view_func)


def pode_editar_calendarios(view_func):
    """Decorator para editar calendários"""
    return permissao_editar('calendarios')(view_func)


def pode_excluir_calendarios(view_func):
    """Decorator para excluir calendários"""
    return permissao_excluir('calendarios')(view_func)


def pode_visualizar_comissoes(view_func):
    """Decorator para visualizar comissões"""
    return permissao_visualizar('comissoes')(view_func)


def pode_criar_comissoes(view_func):
    """Decorator para criar comissões"""
    return permissao_criar('comissoes')(view_func)


def pode_editar_comissoes(view_func):
    """Decorator para editar comissões"""
    return permissao_editar('comissoes')(view_func)


def pode_excluir_comissoes(view_func):
    """Decorator para excluir comissões"""
    return permissao_excluir('comissoes')(view_func)


def pode_visualizar_usuarios(view_func):
    """Decorator para visualizar usuários"""
    return permissao_visualizar('usuarios')(view_func)


def pode_gerenciar_usuarios(view_func):
    """Decorator para gerenciar usuários"""
    return permissao_gerenciar('usuarios')(view_func)


def pode_gerenciar_permissoes(view_func):
    """Decorator para gerenciar permissões"""
    return permissao_gerenciar('permissoes')(view_func)


def pode_acessar_logs(view_func):
    """Decorator para acessar logs"""
    return permissao_requerida('logs', 'acessar')(view_func)


def pode_gerenciar_medalhas(view_func):
    """Decorator para gerenciar medalhas"""
    return permissao_gerenciar('medalhas')(view_func)
