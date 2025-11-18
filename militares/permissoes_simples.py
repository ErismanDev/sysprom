#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Permissões Baseado na Função Militar da Sessão

Este módulo implementa um sistema de permissões onde:
- Usuário: apenas para login no sistema
- Militar: vinculado ao usuário
- Função Militar: define todas as permissões de acesso e CRUD
- Sessão: usuário seleciona qual função usar na sessão
- Superusuário: acesso completo, bypassa todas as restrições
"""

from django.contrib.auth import get_user_model
from .models import UsuarioSessao, UsuarioFuncaoMilitar, PermissaoFuncao

User = get_user_model()


def obter_funcao_militar_ativa(user):
    """
    Obtém a função militar ativa da sessão do usuário
    
    Args:
        user: Usuário Django
        
    Returns:
        UsuarioFuncaoMilitar ou None se não houver sessão ativa
    """
    if not user or not user.is_authenticated:
        return None
    
    # Superusuários não precisam de sessão
    if user.is_superuser:
        return None
    
    try:
        sessao_ativa = UsuarioSessao.objects.filter(
            usuario=user,
            ativo=True
        ).first()
        
        if not sessao_ativa or not sessao_ativa.funcao_militar_usuario:
            return None
            
        return sessao_ativa.funcao_militar_usuario
        
    except Exception:
        return None


def tem_permissao(user, modulo, acao):
    """
    Verifica se o usuário tem permissão baseada na função militar da sessão
    
    Args:
        user: Usuário Django
        modulo: Módulo do sistema (ex: 'militares', 'fichas_oficiais', 'quadros_acesso')
        acao: Ação (ex: 'visualizar', 'criar', 'editar', 'excluir', 'gerenciar')
        
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Mapear módulos para os códigos do modelo PermissaoFuncao
    modulo_mapping = {
        # Menus Principais
        'menu_dashboard': 'MENU_DASHBOARD',
        'menu_efetivo': 'MENU_EFETIVO',
        'menu_secao_promocoes': 'MENU_SECAO_PROMOCOES',
        'menu_medalhas': 'MENU_MEDALHAS',
        'menu_publicacoes': 'MENU_PUBLICACOES',
        'menu_configuracoes': 'MENU_CONFIGURACOES',
        'menu_relatorios': 'MENU_RELATORIOS',
        
        # Submenus - Efetivo
        'submenu_ativos': 'SUBMENU_ATIVOS',
        'submenu_inativos': 'SUBMENU_INATIVOS',
        'submenu_lotacoes': 'SUBMENU_LOTACOES',
        
        # Submenus - Seção de Promoções
        'submenu_fichas_oficiais': 'SUBMENU_FICHAS_OFICIAIS',
        'submenu_fichas_pracas': 'SUBMENU_FICHAS_PRACAS',
        'submenu_calendarios': 'SUBMENU_CALENDARIOS',
        'submenu_quadros_fixacao': 'SUBMENU_QUADROS_FIXACAO',
        'submenu_quadros_acesso': 'SUBMENU_QUADROS_ACESSO',
        'submenu_comissoes': 'SUBMENU_COMISSOES',
        'submenu_meus_votos': 'SUBMENU_MEUS_VOTOS',
        'submenu_promocoes': 'SUBMENU_PROMOCOES',
        'submenu_almanaques': 'SUBMENU_ALMANAQUES',
        
        # Submenus - Publicações
        'submenu_publicacoes': 'SUBMENU_PUBLICACOES',
        'submenu_notas': 'SUBMENU_NOTAS',
        'submenu_boletins_ostensivos': 'SUBMENU_BOLETINS_OSTENSIVOS',
        'submenu_boletins_reservados': 'SUBMENU_BOLETINS_RESERVADOS',
        'submenu_boletins_especiais': 'SUBMENU_BOLETINS_ESPECIAIS',
        'submenu_avisos': 'SUBMENU_AVISOS',
        'submenu_ordens_servico': 'SUBMENU_ORDENS_SERVICO',
        
        # Módulos de Ação - Militares Ativos
        'militares': 'MILITARES',
        'inativos': 'INATIVOS',
        'fichas_oficiais': 'FICHAS_OFICIAIS',
        'fichas_pracas': 'FICHAS_PRACAS',
        'quadros_acesso': 'QUADROS_ACESSO',
        'quadros_fixacao': 'QUADROS_FIXACAO',
        'comissoes_oficiais': 'COMISSOES_OFICIAIS',
        'comissoes_pracas': 'COMISSOES_PRACAS',
        'promocoes': 'PROMOCOES',
        'calendarios': 'CALENDARIOS',
        'almanaques': 'ALMANAQUES',
        'medalhas': 'MEDALHAS',
        
        # Módulos de Ação - Publicações
        'publicacoes': 'PUBLICACOES',
        'notas': 'NOTAS',
        'boletins_ostensivos': 'BOLETINS_OSTENSIVOS',
        'boletins_reservados': 'BOLETINS_RESERVADOS',
        'boletins_especiais': 'BOLETINS_ESPECIAIS',
        'avisos': 'AVISOS',
        'ordens_servico': 'ORDENS_SERVICO',
        
        # Módulos de Ação - Operações Planejadas
        'planejadas': 'PLANEJADAS',
        'orcamentos_planejadas': 'ORCAMENTOS_PLANEJADAS',
        
        # Módulos de Ação - Almoxarifado
        'almoxarifado': 'ALMOXARIFADO',
        'menu_almoxarifado': 'MENU_ALMOXARIFADO',
        
        # Módulos de Ação - Afastamentos
        'afastamentos': 'AFASTAMENTOS',
        'menu_afastamentos': 'MENU_AFASTAMENTOS',
    }
    
    # Mapear ações para os códigos do modelo PermissaoFuncao
    acao_mapping = {
        'visualizar': 'VISUALIZAR',
        'criar': 'CRIAR',
        'editar': 'EDITAR',
        'excluir': 'EXCLUIR',
        'transferir': 'TRANSFERIR',
        'promover': 'PROMOVER',
        'inativar': 'INATIVAR',
        'ficha_conceito': 'FICHA_CONCEITO',
        'exportar': 'EXPORTAR',
        'dashboard': 'DASHBOARD',
        'reordenar': 'REORDENAR',
        'reativar': 'REATIVAR',
        'gerenciar': 'ADMINISTRAR',
        'votar': 'VOTAR',
        'aprovar': 'APROVAR',
        'rejeitar': 'REJEITAR',
    }
    
    # Obter códigos mapeados
    modulo_codigo = modulo_mapping.get(modulo)
    acao_codigo = acao_mapping.get(acao)
    
    if not modulo_codigo or not acao_codigo:
        return False
    
    # Verificar se existe permissão no modelo PermissaoFuncao
    # As permissões são salvas como (modulo, acesso) separados, não como {modulo}_{acesso}
    try:
        # Verificar se existe a permissão específica (modulo='ALMOXARIFADO', acesso='VISUALIZAR')
        permissao_especifica = PermissaoFuncao.objects.filter(
            funcao_militar=funcao_militar,
            modulo=modulo_codigo,
            acesso=acao_codigo,
            ativo=True
        ).exists()
        
        if permissao_especifica:
            return True
        
        # Verificar também se existe permissão no formato {modulo}_{acesso} (para compatibilidade)
        modulo_busca = f"{modulo_codigo}_{acao_codigo}"
        permissao_formato_antigo = PermissaoFuncao.objects.filter(
            funcao_militar=funcao_militar,
            modulo=modulo_busca,
            ativo=True
        ).exists()
        
        if permissao_formato_antigo:
            return True
        
        # Se não existe permissão específica, verificar se existe a permissão base do módulo
        # (ex: ALMOXARIFADO com qualquer acesso - que dá acesso a todas as ações do módulo)
        permissao_modulo = PermissaoFuncao.objects.filter(
            funcao_militar=funcao_militar,
            modulo=modulo_codigo,
            ativo=True
        ).exists()
        
        return permissao_modulo
        
    except Exception as e:
        print(f"Erro ao verificar permissão {modulo}.{acao}: {e}")
        return False


# Funções específicas para compatibilidade com o sistema atual
def pode_visualizar_militares(user):
    """Verifica se pode visualizar militares"""
    return tem_permissao(user, 'militares', 'visualizar')


def pode_criar_militares(user):
    """Verifica se pode criar militares"""
    return tem_permissao(user, 'militares', 'criar')


def pode_editar_militares(user):
    """Verifica se pode editar militares"""
    return tem_permissao(user, 'militares', 'editar')


def pode_excluir_militares(user):
    """Verifica se pode excluir militares"""
    return tem_permissao(user, 'militares', 'excluir')


def pode_visualizar_fichas_oficiais(user):
    """Verifica se pode visualizar fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'visualizar')


def pode_criar_fichas_oficiais(user):
    """Verifica se pode criar fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'criar')


def pode_editar_fichas_oficiais(user):
    """Verifica se pode editar fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'editar')


def pode_excluir_fichas_oficiais(user):
    """Verifica se pode excluir fichas de oficiais"""
    return tem_permissao(user, 'fichas_oficiais', 'excluir')


def pode_visualizar_fichas_pracas(user):
    """Verifica se pode visualizar fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'visualizar')


def pode_criar_fichas_pracas(user):
    """Verifica se pode criar fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'criar')


def pode_editar_fichas_pracas(user):
    """Verifica se pode editar fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'editar')


def pode_excluir_fichas_pracas(user):
    """Verifica se pode excluir fichas de praças"""
    return tem_permissao(user, 'fichas_pracas', 'excluir')


def pode_visualizar_fichas_conceito(user):
    """Verifica se pode visualizar fichas de conceito (oficiais ou praças)"""
    return (pode_visualizar_fichas_oficiais(user) or pode_visualizar_fichas_pracas(user))


def pode_editar_fichas_conceito(user):
    """Verifica se pode editar fichas de conceito (oficiais ou praças)"""
    return (pode_editar_fichas_oficiais(user) or pode_editar_fichas_pracas(user))


def pode_gerenciar_quadros_acesso(user):
    """Verifica se pode gerenciar quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'gerenciar')


def pode_gerenciar_quadros_fixacao(user):
    """Verifica se pode gerenciar quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'gerenciar')


def pode_gerenciar_comissoes(user):
    """Verifica se pode gerenciar comissões"""
    return (tem_permissao(user, 'comissoes_oficiais', 'gerenciar') or 
            tem_permissao(user, 'comissoes_pracas', 'gerenciar'))


def pode_votar_comissoes(user):
    """Verifica se pode votar em comissões"""
    return (tem_permissao(user, 'comissoes_oficiais', 'votar') or 
            tem_permissao(user, 'comissoes_pracas', 'votar'))


def pode_gerenciar_promocoes(user):
    """Verifica se pode gerenciar promoções"""
    return tem_permissao(user, 'promocoes', 'gerenciar')


def pode_gerenciar_calendarios(user):
    """Verifica se pode gerenciar calendários"""
    return tem_permissao(user, 'calendarios', 'gerenciar')


def pode_gerenciar_medalhas(user):
    """Verifica se pode gerenciar medalhas"""
    return tem_permissao(user, 'medalhas', 'gerenciar')


def pode_acessar_dashboard(user):
    """Verifica se pode acessar o dashboard"""
    return tem_permissao(user, 'menu_dashboard', 'visualizar')


def pode_acessar_efetivo(user):
    """Verifica se pode acessar o módulo efetivo"""
    return tem_permissao(user, 'menu_efetivo', 'visualizar')


def pode_acessar_secao_promocoes(user):
    """Verifica se pode acessar a seção de promoções"""
    return tem_permissao(user, 'menu_secao_promocoes', 'visualizar')


def pode_acessar_medalhas(user):
    """Verifica se pode acessar o módulo medalhas"""
    return tem_permissao(user, 'menu_medalhas', 'visualizar')


def pode_acessar_configuracoes(user):
    """Verifica se pode acessar configurações"""
    return tem_permissao(user, 'menu_configuracoes', 'visualizar')


def pode_acessar_relatorios(user):
    """Verifica se pode acessar relatórios"""
    return tem_permissao(user, 'menu_relatorios', 'visualizar')


# ==================== FUNÇÕES PARA PUBLICAÇÕES ====================

# Função removida - duplicada na linha 846


def pode_visualizar_publicacoes(user):
    """Verifica se pode visualizar publicações"""
    return tem_permissao(user, 'publicacoes', 'visualizar')


def pode_criar_publicacoes(user):
    """Verifica se pode criar publicações"""
    return tem_permissao(user, 'publicacoes', 'criar')


def pode_editar_publicacoes(user):
    """Verifica se pode editar publicações"""
    return tem_permissao(user, 'publicacoes', 'editar')


def pode_excluir_publicacoes(user):
    """Verifica se pode excluir publicações"""
    return tem_permissao(user, 'publicacoes', 'excluir')


def pode_publicar_publicacoes(user):
    """Verifica se pode publicar publicações"""
    return tem_permissao(user, 'publicacoes', 'publicar')


# Funções específicas para Notas
def pode_visualizar_notas(user):
    """Verifica se pode visualizar notas"""
    return tem_permissao(user, 'notas', 'visualizar')


def pode_criar_notas(user):
    """Verifica se pode criar notas"""
    return tem_permissao(user, 'notas', 'criar')


def pode_editar_notas(user):
    """Verifica se pode editar notas"""
    return tem_permissao(user, 'notas', 'editar')


def pode_excluir_notas(user):
    """Verifica se pode excluir notas"""
    return tem_permissao(user, 'notas', 'excluir')


def pode_publicar_notas(user):
    """Verifica se pode publicar notas"""
    return tem_permissao(user, 'notas', 'publicar')


# Funções específicas para Boletins Ostensivos
def pode_visualizar_boletins_ostensivos(user):
    """Verifica se pode visualizar boletins ostensivos"""
    return tem_permissao(user, 'boletins_ostensivos', 'visualizar')


def pode_criar_boletins_ostensivos(user):
    """Verifica se pode criar boletins ostensivos"""
    return tem_permissao(user, 'boletins_ostensivos', 'criar')


def pode_editar_boletins_ostensivos(user):
    """Verifica se pode editar boletins ostensivos"""
    return tem_permissao(user, 'boletins_ostensivos', 'editar')


def pode_excluir_boletins_ostensivos(user):
    """Verifica se pode excluir boletins ostensivos"""
    return tem_permissao(user, 'boletins_ostensivos', 'excluir')


def pode_publicar_boletins_ostensivos(user):
    """Verifica se pode publicar boletins ostensivos"""
    return tem_permissao(user, 'boletins_ostensivos', 'publicar')


# Funções específicas para Boletins Reservados
def pode_visualizar_boletins_reservados(user):
    """Verifica se pode visualizar boletins reservados"""
    return tem_permissao(user, 'boletins_reservados', 'visualizar')


def pode_criar_boletins_reservados(user):
    """Verifica se pode criar boletins reservados"""
    return tem_permissao(user, 'boletins_reservados', 'criar')


def pode_editar_boletins_reservados(user):
    """Verifica se pode editar boletins reservados"""
    return tem_permissao(user, 'boletins_reservados', 'editar')


def pode_excluir_boletins_reservados(user):
    """Verifica se pode excluir boletins reservados"""
    return tem_permissao(user, 'boletins_reservados', 'excluir')


def pode_publicar_boletins_reservados(user):
    """Verifica se pode publicar boletins reservados"""
    return tem_permissao(user, 'boletins_reservados', 'publicar')


# Funções específicas para Boletins Especiais
def pode_visualizar_boletins_especiais(user):
    """Verifica se pode visualizar boletins especiais"""
    return tem_permissao(user, 'boletins_especiais', 'visualizar')


def pode_criar_boletins_especiais(user):
    """Verifica se pode criar boletins especiais"""
    return tem_permissao(user, 'boletins_especiais', 'criar')


def pode_editar_boletins_especiais(user):
    """Verifica se pode editar boletins especiais"""
    return tem_permissao(user, 'boletins_especiais', 'editar')


def pode_excluir_boletins_especiais(user):
    """Verifica se pode excluir boletins especiais"""
    return tem_permissao(user, 'boletins_especiais', 'excluir')


def pode_publicar_boletins_especiais(user):
    """Verifica se pode publicar boletins especiais"""
    return tem_permissao(user, 'boletins_especiais', 'publicar')


# Funções específicas para Avisos
def pode_visualizar_avisos(user):
    """Verifica se pode visualizar avisos"""
    return tem_permissao(user, 'avisos', 'visualizar')


def pode_criar_avisos(user):
    """Verifica se pode criar avisos"""
    return tem_permissao(user, 'avisos', 'criar')


def pode_editar_avisos(user):
    """Verifica se pode editar avisos"""
    return tem_permissao(user, 'avisos', 'editar')


def pode_excluir_avisos(user):
    """Verifica se pode excluir avisos"""
    return tem_permissao(user, 'avisos', 'excluir')


def pode_publicar_avisos(user):
    """Verifica se pode publicar avisos"""
    return tem_permissao(user, 'avisos', 'publicar')


# Funções específicas para Ordens de Serviço
def pode_visualizar_ordens_servico(user):
    """Verifica se pode visualizar ordens de serviço"""
    return tem_permissao(user, 'ordens_servico', 'visualizar')


def pode_criar_ordens_servico(user):
    """Verifica se pode criar ordens de serviço"""
    return tem_permissao(user, 'ordens_servico', 'criar')


def pode_editar_ordens_servico(user):
    """Verifica se pode editar ordens de serviço"""
    return tem_permissao(user, 'ordens_servico', 'editar')


def pode_excluir_ordens_servico(user):
    """Verifica se pode excluir ordens de serviço"""
    return tem_permissao(user, 'ordens_servico', 'excluir')


def pode_publicar_ordens_servico(user):
    """Verifica se pode publicar ordens de serviço"""
    return tem_permissao(user, 'ordens_servico', 'publicar')


# Funções específicas para Escalas de Serviço
def pode_gerenciar_escalas(user):
    """Verifica se pode gerenciar escalas de serviço"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Verificar se tem permissão para gerenciar militares (que inclui escalas)
    return pode_editar_militares(user)


# Funções para filtros hierárquicos baseados na função militar
def filtrar_fichas_conceito_por_usuario(user, fichas):
    """
    Filtra as fichas de conceito baseado nas permissões do usuário
    Permite que usuários vejam suas próprias fichas mesmo sem permissão geral
    """
    if not user or not user.is_authenticated:
        return []
    
    if user.is_superuser:
        return fichas
    
    # Se pode visualizar fichas de conceito, retorna todas
    if pode_visualizar_fichas_conceito(user):
        return fichas
    
    # Verificar se o usuário tem função militar ativa
    funcao = obter_funcao_militar_ativa(user)
    if not funcao or not funcao.ativo:
        # Mesmo sem função ativa, permitir ver própria ficha
        fichas_permitidas = []
        for ficha in fichas:
            # Verificar se é ficha de praças
            if hasattr(ficha, 'militar') and hasattr(ficha.militar, 'user'):
                if ficha.militar.user == user:
                    fichas_permitidas.append(ficha)
        return fichas_permitidas
    
    # Se não pode visualizar geralmente, permitir apenas própria ficha
    fichas_permitidas = []
    for ficha in fichas:
        # Verificar se é a própria ficha do usuário
        if hasattr(ficha, 'militar') and hasattr(ficha.militar, 'user'):
            if ficha.militar.user == user:
                fichas_permitidas.append(ficha)
    
    return fichas_permitidas


# Funções para compatibilidade com sistema antigo
def pode_gerenciar_usuarios(user):
    """Verifica se pode gerenciar usuários"""
    return tem_permissao(user, 'usuarios', 'gerenciar')


def pode_gerenciar_permissoes(user):
    """Verifica se pode gerenciar permissões"""
    return tem_permissao(user, 'permissoes', 'gerenciar')


def pode_acessar_logs(user):
    """Verifica se pode acessar logs"""
    return tem_permissao(user, 'logs', 'acessar')


def pode_editar_punicoes_elogios(user):
    """Verifica se pode editar punições e elogios"""
    return tem_permissao(user, 'militares', 'editar')


def pode_editar_medalhas(user):
    """Verifica se pode editar medalhas"""
    return tem_permissao(user, 'medalhas', 'editar')


def pode_editar_contato(user):
    """Verifica se pode editar contato"""
    return tem_permissao(user, 'militares', 'editar')


def pode_editar_cadastros_militares(user):
    """Verifica se pode editar cadastros de militares"""
    return tem_permissao(user, 'militares', 'editar')


# Funções para militares inativos
def pode_visualizar_inativos(user):
    """Verifica se pode visualizar militares inativos"""
    return tem_permissao(user, 'inativos', 'visualizar')


def pode_editar_inativos(user):
    """Verifica se pode editar militares inativos"""
    return tem_permissao(user, 'inativos', 'editar')


def pode_reativar_inativos(user):
    """Verifica se pode reativar militares inativos"""
    # Verificar permissão granular
    if tem_permissao(user, 'inativos', 'reativar'):
        return True
    
    # Verificar se tem a permissão no menu_permissions (botão marcado nas permissões da função militar)
    # Isso permite que usuários com a permissão marcada na função possam reativar
    from .permissoes_hierarquicas import obter_funcao_militar_ativa
    from .models import PermissaoFuncao
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if funcao_usuario and funcao_usuario.ativo:
        funcao_militar = funcao_usuario.funcao_militar
        if funcao_militar and funcao_militar.ativo:
            # Verificar se existe permissão INATIVOS_REATIVAR
            tem_permissao_reativar = PermissaoFuncao.objects.filter(
                funcao_militar=funcao_militar,
                modulo='INATIVOS',
                acesso='REATIVAR',
                ativo=True
            ).exists()
            if tem_permissao_reativar:
                return True
    
    return False


def pode_excluir_inativos(user):
    """Verifica se pode excluir militares inativos"""
    return tem_permissao(user, 'inativos', 'excluir')


# Funções para quadros de acesso
def pode_visualizar_quadros_acesso(user):
    """Verifica se pode visualizar quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'visualizar')


def pode_criar_quadros_acesso(user):
    """Verifica se pode criar quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'criar')


def pode_editar_quadros_acesso(user):
    """Verifica se pode editar quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'editar')


def pode_excluir_quadros_acesso(user):
    """Verifica se pode excluir quadros de acesso"""
    return tem_permissao(user, 'quadros_acesso', 'excluir')


# Funções para quadros de fixação
def pode_visualizar_quadros_fixacao(user):
    """Verifica se pode visualizar quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'visualizar')


def pode_criar_quadros_fixacao(user):
    """Verifica se pode criar quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'criar')


def pode_editar_quadros_fixacao(user):
    """Verifica se pode editar quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'editar')


def pode_excluir_quadros_fixacao(user):
    """Verifica se pode excluir quadros de fixação"""
    return tem_permissao(user, 'quadros_fixacao', 'excluir')


# Funções para almanaques
def pode_visualizar_almanaques(user):
    """Verifica se pode visualizar almanaques"""
    return tem_permissao(user, 'almanaques', 'visualizar')


def pode_criar_almanaques(user):
    """Verifica se pode criar almanaques"""
    return tem_permissao(user, 'almanaques', 'criar')


def pode_editar_almanaques(user):
    """Verifica se pode editar almanaques"""
    return tem_permissao(user, 'almanaques', 'editar')


def pode_excluir_almanaques(user):
    """Verifica se pode excluir almanaques"""
    return tem_permissao(user, 'almanaques', 'excluir')


# Funções para promoções
def pode_visualizar_promocoes(user):
    """Verifica se pode visualizar promoções"""
    return tem_permissao(user, 'promocoes', 'visualizar')


def pode_criar_promocoes(user):
    """Verifica se pode criar promoções"""
    return tem_permissao(user, 'promocoes', 'criar')


def pode_editar_promocoes(user):
    """Verifica se pode editar promoções"""
    return tem_permissao(user, 'promocoes', 'editar')


def pode_excluir_promocoes(user):
    """Verifica se pode excluir promoções"""
    return tem_permissao(user, 'promocoes', 'excluir')


# Funções para calendários
def pode_visualizar_calendarios(user):
    """Verifica se pode visualizar calendários"""
    return tem_permissao(user, 'calendarios', 'visualizar')


def pode_criar_calendarios(user):
    """Verifica se pode criar calendários"""
    return tem_permissao(user, 'calendarios', 'criar')


def pode_editar_calendarios(user):
    """Verifica se pode editar calendários"""
    return tem_permissao(user, 'calendarios', 'editar')


def pode_excluir_calendarios(user):
    """Verifica se pode excluir calendários"""
    return tem_permissao(user, 'calendarios', 'excluir')


# Funções para comissões
def pode_visualizar_comissoes(user):
    """Verifica se pode visualizar comissões"""
    return (tem_permissao(user, 'comissoes_oficiais', 'visualizar') or 
            tem_permissao(user, 'comissoes_pracas', 'visualizar'))


def pode_criar_comissoes(user):
    """Verifica se pode criar comissões"""
    return (tem_permissao(user, 'comissoes_oficiais', 'criar') or 
            tem_permissao(user, 'comissoes_pracas', 'criar'))


def pode_editar_comissoes(user):
    """Verifica se pode editar comissões"""
    return (tem_permissao(user, 'comissoes_oficiais', 'editar') or 
            tem_permissao(user, 'comissoes_pracas', 'editar'))


def pode_excluir_comissoes(user):
    """Verifica se pode excluir comissões"""
    return (tem_permissao(user, 'comissoes_oficiais', 'excluir') or 
            tem_permissao(user, 'comissoes_pracas', 'excluir'))


# Funções para lotações
def pode_visualizar_lotacoes(user):
    """Verifica se pode visualizar lotações"""
    return tem_permissao(user, 'lotacoes', 'visualizar')


def pode_criar_lotacoes(user):
    """Verifica se pode criar lotações"""
    return tem_permissao(user, 'lotacoes', 'criar')


def pode_editar_lotacoes(user):
    """Verifica se pode editar lotações"""
    return tem_permissao(user, 'lotacoes', 'editar')


def pode_excluir_lotacoes(user):
    """Verifica se pode excluir lotações"""
    return tem_permissao(user, 'lotacoes', 'excluir')


# Funções para usuários
def pode_gerenciar_usuarios(user):
    """Verifica se pode gerenciar usuários"""
    return tem_permissao(user, 'usuarios', 'gerenciar')


def pode_gerenciar_permissoes(user):
    """Verifica se pode gerenciar permissões"""
    return tem_permissao(user, 'permissoes', 'gerenciar')


def pode_acessar_logs(user):
    """Verifica se pode acessar logs"""
    return tem_permissao(user, 'logs', 'acessar')


def pode_gerenciar_medalhas(user):
    """Verifica se pode gerenciar medalhas"""
    return tem_permissao(user, 'medalhas', 'gerenciar')


# Função para acesso total à seção de promoções
def tem_acesso_total_secao_promocoes(user):
    """Verifica se tem acesso total à seção de promoções"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    return funcao_militar and funcao_militar.acesso == 'TOTAL'


def obter_permissoes_da_funcao(user):
    """
    Obtém todas as permissões da função militar ativa da sessão
    
    Args:
        user: Usuário Django
        
    Returns:
        dict: Dicionário com todas as permissões da função
    """
    if not user or not user.is_authenticated:
        return {}
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return {'superuser': True}
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario:
        return {}
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Buscar todas as permissões da função
    permissoes = PermissaoFuncao.objects.filter(
        funcao_militar=funcao_militar,
        ativo=True
    ).values_list('modulo', flat=True)
    
    return {
        'funcao': funcao_militar.nome,
        'acesso': funcao_militar.get_acesso_display(),
        'permissoes': list(permissoes),
        'superuser': False
    }


# ==================== FUNÇÕES PARA PUBLICAÇÕES ====================

def pode_acessar_publicacoes(user):
    """Verifica se o usuário pode acessar o módulo de publicações"""
    if user.is_superuser:
        return True
    
    # Primeiro tentar usar a função ativa da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    
    # Se não houver sessão ativa, usar a primeira função ativa do usuário
    if not funcao_usuario:
        funcao_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=user,
            ativo=True
        ).first()
    
    if not funcao_usuario:
        return False
    
    # Funções permitidas para acessar publicações
    funcoes_permitidas = [
        'EDITOR_GERAL', 'EDITOR_ADJUNTO', 'EDITOR', 
        'APROVADOR', 'REVISOR', 'DIGITADOR', 'OPERADOR_PLANEJADAS'
    ]
    
    return funcao_usuario.funcao_militar.publicacao in funcoes_permitidas


def pode_criar_publicacoes(user):
    """Verifica se o usuário pode criar publicações"""
    return pode_acessar_publicacoes(user)


def pode_editar_publicacoes(user):
    """Verifica se o usuário pode editar publicações"""
    if user.is_superuser:
        return True
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario:
        return False
    
    # Funções que podem editar (editores e aprovadores)
    funcoes_edicao = [
        'EDITOR_GERAL', 'EDITOR_ADJUNTO', 'EDITOR', 
        'APROVADOR'
    ]
    
    return funcao_usuario.funcao_militar.publicacao in funcoes_edicao


def pode_aprovar_publicacoes(user):
    """Verifica se o usuário pode aprovar publicações"""
    if user.is_superuser:
        return True
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario:
        return False
    
    # Funções que podem aprovar
    funcoes_aprovacao = [
        'EDITOR_GERAL', 'EDITOR_ADJUNTO', 'APROVADOR'
    ]
    
    return funcao_usuario.funcao_militar.publicacao in funcoes_aprovacao


def pode_publicar_publicacoes(user):
    """Verifica se o usuário pode publicar publicações"""
    if user.is_superuser:
        return True
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario:
        return False
    
    # Apenas editores gerais podem publicar
    return funcao_usuario.funcao_militar.publicacao == 'EDITOR_GERAL'


def pode_acessar_boletins(user):
    """Verifica se o usuário pode acessar boletins (apenas editores)"""
    if user.is_superuser:
        return True
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario:
        return False
    
    # Apenas editores podem acessar boletins
    funcoes_editor = ['EDITOR_GERAL', 'EDITOR_ADJUNTO', 'EDITOR']
    return funcao_usuario.funcao_militar.publicacao in funcoes_editor


def pode_acessar_notas(user):
    """Verifica se o usuário pode acessar notas (editores, revisores e aprovadores)"""
    if user.is_superuser:
        return True
    
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario:
        return False
    
    # Editores, revisores e aprovadores podem acessar notas
    funcoes_permitidas = ['EDITOR_GERAL', 'EDITOR_ADJUNTO', 'EDITOR', 'REVISOR', 'APROVADOR']
    return funcao_usuario.funcao_militar.publicacao in funcoes_permitidas


# ==================== FUNÇÕES ESPECÍFICAS PARA OPERAÇÕES PLANEJADAS ====================

def pode_visualizar_operacoes_planejadas(user):
    """Verifica se pode visualizar operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Verificar se é operador, fiscal ou aprovador de planejadas
    return funcao_militar.publicacao in ['OPERADOR_PLANEJADAS', 'FISCAL_PLANEJADAS', 'APROVADOR']


def pode_criar_operacoes_planejadas(user):
    """Verifica se pode criar operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Apenas operadores de planejadas podem criar
    return funcao_militar.publicacao == 'OPERADOR_PLANEJADAS'


def pode_editar_operacoes_planejadas(user):
    """Verifica se pode editar operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Apenas operadores de planejadas podem editar
    return funcao_militar.publicacao == 'OPERADOR_PLANEJADAS'


def pode_excluir_operacoes_planejadas(user):
    """Verifica se pode excluir operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Apenas operadores de planejadas podem excluir
    return funcao_militar.publicacao == 'OPERADOR_PLANEJADAS'


def pode_gerenciar_operacoes_planejadas(user):
    """Verifica se pode gerenciar operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Operadores, fiscais e aprovadores de planejadas podem gerenciar
    return funcao_militar.publicacao in ['OPERADOR_PLANEJADAS', 'FISCAL_PLANEJADAS', 'APROVADOR']


def pode_visualizar_orcamentos_planejadas(user):
    """Verifica se pode visualizar orçamentos de operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Fiscais de planejadas podem visualizar orçamentos
    return funcao_militar.publicacao == 'FISCAL_PLANEJADAS'


def pode_criar_orcamentos_planejadas(user):
    """Verifica se pode criar orçamentos de operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Apenas fiscais de planejadas podem criar orçamentos
    return funcao_militar.publicacao == 'FISCAL_PLANEJADAS'


def pode_editar_orcamentos_planejadas(user):
    """Verifica se pode editar orçamentos de operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Apenas fiscais de planejadas podem editar orçamentos
    return funcao_militar.publicacao == 'FISCAL_PLANEJADAS'


def pode_excluir_orcamentos_planejadas(user):
    """Verifica se pode excluir orçamentos de operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Apenas fiscais de planejadas podem excluir orçamentos
    return funcao_militar.publicacao == 'FISCAL_PLANEJADAS'


def pode_gerenciar_orcamentos_planejadas(user):
    """Verifica se pode gerenciar orçamentos de operações planejadas"""
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    # Obter função militar da sessão
    funcao_usuario = obter_funcao_militar_ativa(user)
    if not funcao_usuario or not funcao_usuario.ativo:
        return False
    
    funcao_militar = funcao_usuario.funcao_militar
    if not funcao_militar or not funcao_militar.ativo:
        return False
    
    # Apenas fiscais de planejadas podem gerenciar orçamentos
    return funcao_militar.publicacao == 'FISCAL_PLANEJADAS'


# ==================== FUNÇÕES ESPECÍFICAS PARA NOTAS RESERVADAS ====================















