#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema simples de permissões baseado nos campos diretos do modelo FuncaoMilitar
"""

from django.contrib.auth.models import User
from .models import UsuarioFuncaoMilitar, FuncaoMilitar


def obter_funcao_militar_ativa(user):
    """Retorna a função militar ativa do usuário baseada na sessão"""
    if not user or not user.is_authenticated:
        return None
    
    try:
        # Primeiro, tentar obter da sessão ativa
        from .models import UsuarioSessao
        sessao_ativa = UsuarioSessao.objects.filter(
            usuario=user,
            ativo=True
        ).order_by('-data_ultima_atividade').first()
        
        if sessao_ativa and sessao_ativa.funcao_militar_usuario:
            return sessao_ativa.funcao_militar_usuario.funcao_militar
        
        # Se não houver sessão ativa, buscar a primeira função ativa disponível
        funcao_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=user, 
            ativo=True
        ).order_by('-data_criacao').first()
        
        if funcao_usuario:
            return funcao_usuario.funcao_militar
        
        return None
    except Exception:
        return None


def tem_permissao_funcao_militar(user, campo_permissao):
    """
    Verifica se o usuário tem uma permissão específica baseada na função militar ativa
    
    Args:
        user: Usuário Django
        campo_permissao: Nome do campo de permissão (ex: 'quadros_acesso_visualizar')
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    funcao = obter_funcao_militar_ativa(user)
    if not funcao:
        return False
    
    # Verificar se a função está ativa
    if not funcao.ativo:
        return False
    
    # Verificar se o campo de permissão existe e está True
    return getattr(funcao, campo_permissao, False)


def obter_funcao_militar_ativa_completa(user):
    """Versão completa da função obter_funcao_militar_ativa"""
    if not user or not user.is_authenticated:
        return None
    
    try:
        # Primeiro, tentar obter da sessão ativa
        from .models import UsuarioSessao
        sessao_ativa = UsuarioSessao.objects.filter(
            usuario=user,
            ativo=True
        ).order_by('-data_ultima_atividade').first()
        
        if sessao_ativa and sessao_ativa.funcao_militar_usuario:
            return sessao_ativa.funcao_militar_usuario.funcao_militar
        
        # Se não houver sessão ativa, buscar a primeira função ativa disponível
        funcao_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=user, 
            ativo=True
        ).order_by('-data_criacao').first()
        
        if funcao_usuario:
            return funcao_usuario.funcao_militar
        return None
    except Exception as e:
        print(f"Erro ao obter função militar ativa para usuário {user.id}: {e}")
        return None


def tem_permissao(user, modulo, acao):
    """
    Verifica se o usuário tem permissão para uma ação específica em um módulo
    
    Args:
        user: Usuário Django
        modulo: Nome do módulo (ex: 'fichas_oficiais', 'quadros_acesso', etc.)
        acao: Ação (ex: 'visualizar', 'criar', 'editar', 'excluir', 'gerenciar')
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários têm todas as permissões
    if user.is_superuser:
        return True
    
    funcao = obter_funcao_militar_ativa(user)
    if not funcao:
        return False
    
    # Verificar se a função está ativa
    if not funcao.ativo:
        return False
    
    # Mapear permissões administrativas especiais
    if modulo == 'usuarios' and acao == 'gerenciar':
        return pode_gerenciar_usuarios(user)
    elif modulo == 'permissoes' and acao == 'gerenciar':
        return pode_gerenciar_permissoes(user)
    elif modulo == 'logs' and acao == 'acessar':
        return pode_acessar_logs(user)
    elif modulo == 'medalhas' and acao == 'gerenciar':
        return pode_gerenciar_medalhas(user)
    
    # Verificar permissões granulares no modelo PermissaoFuncao
    try:
        from .models import PermissaoFuncao
        
        # Mapear módulos para os códigos do modelo PermissaoFuncao
        modulo_mapping = {
            'militares': 'ATIVOS',
            'inativos': 'INATIVOS',
            'lotacoes': 'LOTACOES',
            'fichas_oficiais': 'FICHAS_OFICIAIS',
            'fichas_pracas': 'FICHAS_PRACAS',
            'quadros_acesso': 'QUADROS_ACESSO',
            'quadros_fixacao': 'QUADROS_FIXACAO',
            'almanaques': 'ALMANAQUES',
            'promocoes': 'PROMOCOES',
            'calendarios': 'CALENDARIOS',
            'comissoes': 'COMISSOES',
            'medalhas': 'MEDALHAS',
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
        }
        
        # Obter códigos mapeados
        modulo_codigo = modulo_mapping.get(modulo)
        acao_codigo = acao_mapping.get(acao)
        
        if not modulo_codigo or not acao_codigo:
            return False
        
        # Construir nome do módulo para busca
        modulo_busca = f"{modulo_codigo}_{acao_codigo}"
        
        # Verificar se existe permissão no modelo PermissaoFuncao
        permissao_existe = PermissaoFuncao.objects.filter(
            funcao_militar=funcao,
            modulo=modulo_busca,
            ativo=True
        ).exists()
        
        return permissao_existe
        
    except Exception as e:
        print(f"Erro ao verificar permissão {modulo}.{acao}: {e}")
        return False


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


def pode_visualizar_comissoes(user):
    """Verifica se pode visualizar comissões"""
    return tem_permissao(user, 'comissoes', 'visualizar')


def pode_criar_comissoes(user):
    """Verifica se pode criar comissões"""
    return tem_permissao(user, 'comissoes', 'criar')


def pode_editar_comissoes(user):
    """Verifica se pode editar comissões"""
    return tem_permissao(user, 'comissoes', 'editar')


def pode_excluir_comissoes(user):
    """Verifica se pode excluir comissões"""
    return tem_permissao(user, 'comissoes', 'excluir')


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


def pode_gerenciar_usuarios(user):
    """Verifica se pode gerenciar usuários"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Usar o novo sistema de permissões
    from .permissoes_sistema import tem_permissao
    return tem_permissao(user, 'USUARIOS', 'ADMINISTRAR') or tem_permissao(user, 'USUARIOS', 'CRIAR')


def pode_gerenciar_permissoes(user):
    """Verifica se pode gerenciar permissões"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Usar o novo sistema de permissões
    from .permissoes_sistema import tem_permissao
    return tem_permissao(user, 'PERMISSOES', 'ADMINISTRAR') or tem_permissao(user, 'FUNCAO', 'ADMINISTRAR')


def pode_acessar_logs(user):
    """Verifica se pode acessar logs"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Usar o novo sistema de permissões
    from .permissoes_sistema import tem_permissao
    return tem_permissao(user, 'SISTEMA', 'ADMINISTRAR') or tem_permissao(user, 'AUDITORIA', 'VISUALIZAR')


def pode_gerenciar_medalhas(user):
    """Verifica se pode gerenciar medalhas"""
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Usar o novo sistema de permissões
    from .permissoes_sistema import tem_permissao
    return tem_permissao(user, 'MEDALHAS', 'ADMINISTRAR') or tem_permissao(user, 'MEDALHAS', 'CRIAR')


def tem_acesso_total_secao_promocoes(user):
    """
    Verifica se o usuário tem acesso total à seção de promoções
    (todas as permissões de todos os módulos)
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    funcao = obter_funcao_militar_ativa(user)
    if not funcao or not funcao.ativo:
        return False
    
    # Verificar se tem todas as permissões de todos os módulos da seção de promoções
    modulos = [
        'fichas_oficiais', 'fichas_pracas', 'quadros_acesso', 'quadros_fixacao',
        'almanaques', 'promocoes', 'calendarios', 'comissoes'
    ]
    
    acoes = ['visualizar', 'criar', 'editar', 'excluir']
    
    for modulo in modulos:
        for acao in acoes:
            if not tem_permissao(user, modulo, acao):
                return False
    
    return True


def pode_editar_militares(user):
    """
    Verifica se o usuário pode editar cadastros de militares.
    Usa o sistema de permissões granulares.
    """
    return tem_permissao(user, 'militares', 'editar')

def pode_editar_fichas_conceito(user):
    """
    Verifica se o usuário pode editar fichas de conceito
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    funcao = obter_funcao_militar_ativa(user)
    if not funcao or not funcao.ativo:
        return False
    
    # Verificar se tem permissão para editar fichas de oficiais ou praças
    return (pode_editar_fichas_oficiais(user) or pode_editar_fichas_pracas(user))


def pode_visualizar_fichas_conceito(user):
    """
    Verifica se o usuário pode visualizar fichas de conceito
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    funcao = obter_funcao_militar_ativa(user)
    if not funcao or not funcao.ativo:
        return False
    
    # Verificar se tem permissão para visualizar fichas de oficiais ou praças
    return (pode_visualizar_fichas_oficiais(user) or pode_visualizar_fichas_pracas(user))


def filtrar_fichas_conceito_por_usuario(user, fichas):
    """
    Filtra as fichas de conceito baseado nas permissões do usuário
    """
    if not user or not user.is_authenticated:
        return []
    
    if user.is_superuser:
        return fichas
    
    funcao = obter_funcao_militar_ativa(user)
    if not funcao or not funcao.ativo:
        return []
    
    # Se pode editar fichas de conceito, retorna todas
    if pode_editar_fichas_conceito(user):
        return fichas
    
    # Caso contrário, retorna lista vazia (sem permissão)
    return []


def pode_visualizar_ficha_conceito(user, militar):
    """
    Verifica se o usuário pode visualizar uma ficha de conceito específica.
    Usa o sistema de permissões granulares e hierárquicas.
    """
    # Se pode editar fichas, pode visualizar qualquer uma
    if pode_editar_fichas_conceito(user):
        return True
    
    # Verificar permissões granulares de visualização
    pode_visualizar_oficiais = tem_permissao(user, 'fichas_oficiais', 'visualizar')
    pode_visualizar_pracas = tem_permissao(user, 'fichas_pracas', 'visualizar')
    
    # Verificar se tem permissão para visualizar o tipo de ficha
    if militar.quadro in ['OFICIAIS', 'OFICIAIS_TEMPORARIOS']:
        return pode_visualizar_oficiais
    elif militar.quadro in ['PRACAS', 'PRACAS_TEMPORARIOS']:
        return pode_visualizar_pracas
    
    return False


def permissoes_simples_processor(request):
    """
    Context processor para disponibilizar as permissões simples nos templates
    """
    context = {}
    
    if request.user.is_authenticated:
        user = request.user
        
        # Permissões de fichas de oficiais
        context['pode_visualizar_fichas_oficiais'] = pode_visualizar_fichas_oficiais(user)
        context['pode_criar_fichas_oficiais'] = pode_criar_fichas_oficiais(user)
        context['pode_editar_fichas_oficiais'] = pode_editar_fichas_oficiais(user)
        context['pode_excluir_fichas_oficiais'] = pode_excluir_fichas_oficiais(user)
        
        # Permissões de fichas de praças
        context['pode_visualizar_fichas_pracas'] = pode_visualizar_fichas_pracas(user)
        context['pode_criar_fichas_pracas'] = pode_criar_fichas_pracas(user)
        context['pode_editar_fichas_pracas'] = pode_editar_fichas_pracas(user)
        context['pode_excluir_fichas_pracas'] = pode_excluir_fichas_pracas(user)
        
        # Permissões de quadros de acesso
        context['pode_visualizar_quadros_acesso'] = pode_visualizar_quadros_acesso(user)
        context['pode_criar_quadros_acesso'] = pode_criar_quadros_acesso(user)
        context['pode_editar_quadros_acesso'] = pode_editar_quadros_acesso(user)
        context['pode_excluir_quadros_acesso'] = pode_excluir_quadros_acesso(user)
        
        # Permissões de quadros de fixação
        context['pode_visualizar_quadros_fixacao'] = pode_visualizar_quadros_fixacao(user)
        context['pode_criar_quadros_fixacao'] = pode_criar_quadros_fixacao(user)
        context['pode_editar_quadros_fixacao'] = pode_editar_quadros_fixacao(user)
        context['pode_excluir_quadros_fixacao'] = pode_excluir_quadros_fixacao(user)
        
        # Permissões de almanaques
        context['pode_visualizar_almanaques'] = pode_visualizar_almanaques(user)
        context['pode_criar_almanaques'] = pode_criar_almanaques(user)
        context['pode_editar_almanaques'] = pode_editar_almanaques(user)
        context['pode_excluir_almanaques'] = pode_excluir_almanaques(user)
        
        # Permissões de promoções
        context['pode_visualizar_promocoes'] = pode_visualizar_promocoes(user)
        context['pode_criar_promocoes'] = pode_criar_promocoes(user)
        context['pode_editar_promocoes'] = pode_editar_promocoes(user)
        context['pode_excluir_promocoes'] = pode_excluir_promocoes(user)
        
        # Permissões de calendários
        context['pode_visualizar_calendarios'] = pode_visualizar_calendarios(user)
        context['pode_criar_calendarios'] = pode_criar_calendarios(user)
        context['pode_editar_calendarios'] = pode_editar_calendarios(user)
        context['pode_excluir_calendarios'] = pode_excluir_calendarios(user)
        
        # Permissões de comissões
        context['pode_visualizar_comissoes'] = pode_visualizar_comissoes(user)
        context['pode_criar_comissoes'] = pode_criar_comissoes(user)
        context['pode_editar_comissoes'] = pode_editar_comissoes(user)
        context['pode_excluir_comissoes'] = pode_excluir_comissoes(user)
        
        # Permissões de lotações
        context['pode_visualizar_lotacoes'] = pode_visualizar_lotacoes(user)
        context['pode_criar_lotacoes'] = pode_criar_lotacoes(user)
        context['pode_editar_lotacoes'] = pode_editar_lotacoes(user)
        context['pode_excluir_lotacoes'] = pode_excluir_lotacoes(user)
        
        # Permissões administrativas
        context['pode_gerenciar_usuarios'] = pode_gerenciar_usuarios(user)
        context['pode_gerenciar_permissoes'] = pode_gerenciar_permissoes(user)
        context['pode_acessar_logs'] = pode_acessar_logs(user)
        context['pode_gerenciar_medalhas'] = pode_gerenciar_medalhas(user)
        
        # Acesso total à seção de promoções
        context['tem_acesso_total_secao_promocoes'] = tem_acesso_total_secao_promocoes(user)
        
        # Função para verificar permissões genéricas
        context['tem_permissao'] = tem_permissao
    
    return context