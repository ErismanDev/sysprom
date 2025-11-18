#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Permissões Baseado em Funções Militares
Substitui o sistema antigo de cargos/funções por funções militares
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import UsuarioSessao, FuncaoMilitar, UsuarioFuncaoMilitar
from .permissoes_niveis import (
    obter_nivel_hierarquico_usuario, tem_nivel_suficiente,
    pode_gerenciar_militares, pode_editar_militares, pode_excluir_militares,
    pode_gerenciar_usuarios, pode_gerenciar_funcoes, pode_gerenciar_permissoes,
    pode_acessar_relatorios, pode_acessar_dashboard, obter_descricao_nivel
)
from .permissoes_hierarquicas import (
    obter_nivel_acesso_usuario,
    pode_editar_militar,
    pode_visualizar_militar,
    filtrar_militares_por_acesso,
    pode_acessar_lotacao,
    obter_areas_acesso_usuario
)


# ============================================================================
# FUNÇÕES DE VERIFICAÇÃO DE PERMISSÕES BASEADAS EM FUNÇÕES MILITARES
# ============================================================================

def obter_sessao_ativa_usuario(user):
    """
    Retorna a sessão ativa do usuário com função militar e lotação
    """
    if not user or not user.is_authenticated:
        return None
    
    return UsuarioSessao.objects.filter(
        usuario=user,
        ativo=True
    ).select_related(
        'funcao_militar_usuario__funcao_militar',
        'funcao_militar_usuario__orgao',
        'funcao_militar_usuario__grande_comando',
        'funcao_militar_usuario__unidade',
        'funcao_militar_usuario__sub_unidade'
    ).first()


def obter_funcao_militar_usuario(user):
    """
    Retorna a função militar ativa do usuário
    """
    sessao = obter_sessao_ativa_usuario(user)
    if not sessao:
        return None
    
    return sessao.funcao_militar_usuario.funcao_militar


def obter_nivel_acesso_usuario_legacy(user):
    """
    Retorna o nível de acesso do usuário baseado na sua função militar (versão legada)
    """
    if not user or not user.is_authenticated:
        return {'grupo': 'USUARIO', 'nivel': 5, 'acesso': 'NENHUM', 'publicacao': 'NENHUM'}
    
    # Superusuários têm acesso total
    if user.is_superuser:
        return {'grupo': 'ADMINISTRATIVO', 'nivel': 1, 'acesso': 'TOTAL', 'publicacao': 'EDITOR_GERAL'}
    
    funcao = obter_funcao_militar_usuario(user)
    if not funcao:
        return {'grupo': 'USUARIO', 'nivel': 5, 'acesso': 'NENHUM', 'publicacao': 'NENHUM'}
    
    return {
        'grupo': funcao.grupo,
        'nivel': funcao.nivel,
        'acesso': funcao.acesso,
        'publicacao': funcao.publicacao
    }




def tem_nivel_minimo(user, nivel_minimo):
    """
    Verifica se o usuário tem nível mínimo necessário
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    nivel = obter_nivel_acesso_usuario(user)
    # Mapear níveis para números (menor número = maior acesso)
    nivel_map = {
        'TOTAL': 1,
        'ORGAO': 2,
        'GRANDE_COMANDO': 3,
        'UNIDADE': 4,
        'SUBUNIDADE': 5,
        'NENHUM': 6
    }
    nivel_usuario = nivel_map.get(nivel, 6)
    return nivel_usuario <= nivel_minimo


def tem_grupo_permitido(user, grupos_permitidos):
    """
    Verifica se o usuário pertence a um dos grupos permitidos
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Para compatibilidade, sempre retorna True se tem acesso
    # O sistema atual não usa grupos, apenas níveis de acesso
    return True


def tem_acesso_suficiente(user, acesso_necessario):
    """
    Verifica se o usuário tem acesso suficiente baseado na hierarquia
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    acesso_usuario = obter_nivel_acesso_usuario(user)
    
    # Hierarquia de acesso (do maior para o menor)
    hierarquia_acesso = {
        'TOTAL': 1,
        'ORGAO': 2,
        'GRANDE_COMANDO': 3,
        'UNIDADE': 4,
        'SUBUNIDADE': 5,
        'NENHUM': 6
    }
    
    nivel_usuario = hierarquia_acesso.get(acesso_usuario, 6)
    nivel_necessario = hierarquia_acesso.get(acesso_necessario, 6)
    
    return nivel_usuario <= nivel_necessario


# ============================================================================
# PERMISSÕES ESPECÍFICAS DO SISTEMA
# ============================================================================

def pode_editar_militares(user):
    """
    Verifica se o usuário pode editar militares baseado no nível hierárquico
    """
    if not user or not user.is_authenticated:
        return False
    
    # Usar o novo sistema de níveis hierárquicos
    from .permissoes_niveis import pode_editar_militares as pode_editar_militares_nivel
    return pode_editar_militares_nivel(user)


def pode_gerenciar_militares(user):
    """
    Verifica se o usuário pode gerenciar militares baseado no nível hierárquico
    """
    if not user or not user.is_authenticated:
        return False
    
    # Usar o novo sistema de níveis hierárquicos
    from .permissoes_niveis import pode_gerenciar_militares as pode_gerenciar_militares_nivel
    return pode_gerenciar_militares_nivel(user)


def pode_editar_militar_especifico(user, militar):
    """
    Verifica se o usuário pode editar um militar específico
    Considera as regras de gestão, promoções e níveis hierárquicos
    """
    if not user or not user.is_authenticated or not militar:
        return False
    
    # Superusuários e usuários master sempre podem
    if user.is_superuser:
        return True
    
    from .models import UsuarioMaster
    if UsuarioMaster.objects.filter(username=user.username, ativo=True).exists():
        return True
    
    # Verificar se tem função específica da estrutura
    if tem_funcao_especifica_estrutura(user):
        return pode_editar_militar_gestao(user, militar)
    
    # Para outras funções, usar o sistema de níveis
    return pode_atualizar_militar_por_nivel(user, militar)


def pode_editar_fichas_conceito(user):
    """
    Verifica se o usuário pode editar fichas de conceito
    Apenas chefe e auxiliar da seção de promoções podem editar fichas de conceito
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Apenas chefe e auxiliar da seção de promoções podem editar fichas de conceito
    if tem_funcao_chefe_auxiliar_promocoes(user):
        return True
    
    # Outras funções específicas da estrutura NÃO podem editar fichas de conceito
    if tem_funcao_especifica_estrutura(user):
        return False
    
    # Verificar por grupo e nível (para outras funções)
    return (tem_grupo_permitido(user, ['ADMINISTRATIVO', 'GESTAO', 'OPERACIONAL']) and 
            tem_nivel_minimo(user, 3))


def pode_visualizar_ficha_conceito(user, ficha_militar):
    """
    Verifica se o usuário pode visualizar uma ficha de conceito específica
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Se pode editar fichas, pode visualizar qualquer uma
    if pode_editar_fichas_conceito(user):
        return True
    
    # Verificar se é a própria ficha
    if ficha_militar and ficha_militar.militar.user == user:
        return True
    
    return False


def pode_visualizar_propria_ficha(user):
    """
    Verifica se o usuário pode visualizar sua própria ficha
    """
    if not user or not user.is_authenticated:
        return False
    
    return True  # Qualquer usuário autenticado pode ver sua própria ficha


def pode_deletar_militar_especifico(user, militar):
    """
    Verifica se o usuário pode deletar um militar específico
    Funções específicas da estrutura NÃO podem deletar militares
    """
    if not user or not user.is_authenticated or not militar:
        return False
    
    # Superusuários e usuários master sempre podem
    if user.is_superuser:
        return True
    
    from .models import UsuarioMaster
    if UsuarioMaster.objects.filter(username=user.username, ativo=True).exists():
        return True
    
    # Funções específicas da estrutura NÃO podem deletar militares
    if tem_funcao_especifica_estrutura(user):
        return False
    
    # Para outras funções, usar as regras normais
    from .permissoes_niveis import pode_excluir_militares
    return pode_excluir_militares(user)


def pode_gerenciar_quadros_vagas(user):
    """
    Verifica se o usuário pode gerenciar quadros de vagas
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return (tem_grupo_permitido(user, ['ADMINISTRATIVO', 'GESTAO']) and 
            tem_nivel_minimo(user, 2))


def pode_gerenciar_comissoes(user):
    """
    Verifica se o usuário pode gerenciar comissões
    Baseado na função militar específica de comissão
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários sempre podem gerenciar comissões
    if user.is_superuser:
        return True
    
    # Verificar se tem função de comissão de promoções
    return tem_funcao_comissao_promocoes(user)


def pode_assinar_documentos(user):
    """
    Verifica se o usuário pode assinar documentos
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return (tem_grupo_permitido(user, ['ADMINISTRATIVO', 'GESTAO', 'COMISSAO']) and 
            tem_nivel_minimo(user, 2))


def pode_gerenciar_usuarios(user):
    """
    Verifica se o usuário pode gerenciar usuários
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return (tem_grupo_permitido(user, ['ADMINISTRATIVO']) and 
            tem_nivel_minimo(user, 1))


def pode_acessar_relatorios(user):
    """
    Verifica se o usuário pode acessar relatórios
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return tem_grupo_permitido(user, ['ADMINISTRATIVO', 'GESTAO', 'OPERACIONAL'])


def pode_visualizar_militares(user):
    """
    Verifica se o usuário pode visualizar militares
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Qualquer usuário autenticado pode visualizar militares
    # Mas com restrições baseadas na função militar
    return True


def pode_visualizar_punicoes_elogios(user, militar):
    """
    Verifica se o usuário pode visualizar punições e elogios de um militar
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Se é o próprio militar, sempre pode ver (verificar de duas formas)
    if militar:
        # Verificação 1: militar.user == user (relação direta)
        if militar.user == user:
            return True
        # Verificação 2: user.militar == militar (relação inversa)
        try:
            if hasattr(user, 'militar') and user.militar == militar:
                return True
        except:
            pass
    
    # Se o militar é oficial, aplicar regra restrita de visualização
    sessao = obter_sessao_ativa_usuario(user)
    if militar and hasattr(militar, 'is_oficial') and militar.is_oficial():
        if not (sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.funcao_militar):
            return False
        funcao = sessao.funcao_militar_usuario.funcao_militar
        funcoes_permitidas = [
            'Comandante Geral',
            'Subcomandante Geral',
            'Diretor de Gestão de Pessoas',
            'Chefe da Seção de Inteligencia e Contra Inteligencia',
        ]
        return funcao.nome in funcoes_permitidas
    
    # Para qualquer outro caso: negar
    
    return False


def pode_editar_punicoes_elogios(user, militar):
    """
    Verifica se o usuário pode editar punições e elogios de um militar
    """
    if not user or not user.is_authenticated:
        return False
    
    # Edição exclusivamente para superusuários
    return bool(user and user.is_superuser)


# ============================================================================
# DECORATORS DE PERMISSÃO
# ============================================================================

def requer_sessao_ativa(view_func):
    """
    Decorator que verifica se o usuário tem uma sessão ativa
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Superusuários podem acessar sem função militar
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar se é usuário master
        from .models import UsuarioMaster
        if UsuarioMaster.objects.filter(
            username=request.user.username,
            ativo=True
        ).exists():
            return view_func(request, *args, **kwargs)
        
        # Administradores do Sistema podem acessar sem lotação
        from .models import UsuarioFuncaoMilitar
        tem_funcao_admin = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Administrador do Sistema', 'Administrador']
        ).exists()
        
        if tem_funcao_admin:
            return view_func(request, *args, **kwargs)
        
        sessao = obter_sessao_ativa_usuario(request.user)
        if not sessao:
            messages.warning(request, 'Você precisa selecionar uma função e lotação para acessar o sistema.')
            return redirect('militares:selecionar_funcao_lotacao')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def requer_funcao_especial(funcoes_permitidas):
    """
    Decorator que verifica se o usuário tem uma das funções especiais permitidas
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Superusuários sempre podem
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar se é usuário master
            from .models import UsuarioMaster
            if UsuarioMaster.objects.filter(
                username=request.user.username,
                ativo=True
            ).exists():
                return view_func(request, *args, **kwargs)
            
            # Administradores do Sistema podem acessar sem lotação
            from .models import UsuarioFuncaoMilitar
            tem_funcao_admin = UsuarioFuncaoMilitar.objects.filter(
                usuario=request.user,
                ativo=True,
                funcao_militar__nome__in=['Administrador do Sistema', 'Administrador']
            ).exists()
            
            if tem_funcao_admin:
                return view_func(request, *args, **kwargs)
            
            sessao = obter_sessao_ativa_usuario(request.user)
            if not sessao:
                messages.error(request, 'Você precisa selecionar uma função e lotação para acessar esta funcionalidade.')
                return redirect('militares:selecionar_funcao_lotacao')
            
            funcao_atual = sessao.funcao_militar_usuario.funcao_militar.nome
            funcoes_lista = [f.strip() for f in funcoes_permitidas.split(',')]
            
            if funcao_atual not in funcoes_lista:
                messages.error(request, f'Você não tem permissão para acessar esta funcionalidade. Funções permitidas: {funcoes_permitidas}')
                return redirect('militares:militar_list')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def requer_permissao_modulo(modulo, acesso='VISUALIZAR'):
    """
    Decorator que verifica se o usuário tem permissão para um módulo específico
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Superusuários sempre podem
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar permissões baseadas em função militar
            if modulo == 'MILITARES' and acesso == 'EDITAR':
                if not pode_editar_militares(request.user):
                    messages.error(request, 'Você não tem permissão para editar militares.')
                    return redirect('militares:militar_list')
            
            elif modulo == 'FICHAS_CONCEITO' and acesso == 'EDITAR':
                if not pode_editar_fichas_conceito(request.user):
                    messages.error(request, 'Você não tem permissão para editar fichas de conceito.')
                    return redirect('militares:militar_list')
            
            elif modulo == 'QUADROS_VAGAS' and acesso in ['EDITAR', 'CRIAR', 'EXCLUIR']:
                if not pode_gerenciar_quadros_vagas(request.user):
                    messages.error(request, 'Você não tem permissão para gerenciar quadros de vagas.')
                    return redirect('militares:militar_list')
            
            elif modulo == 'COMISSAO' and acesso in ['EDITAR', 'CRIAR', 'EXCLUIR']:
                if not pode_gerenciar_comissoes(request.user):
                    messages.error(request, 'Você não tem permissão para gerenciar comissões.')
                    return redirect('militares:militar_list')
            
            elif modulo == 'DOCUMENTOS' and acesso == 'ASSINAR':
                if not pode_assinar_documentos(request.user):
                    messages.error(request, 'Você não tem permissão para assinar documentos.')
                    return redirect('militares:militar_list')
            
            elif modulo == 'USUARIOS' and acesso in ['EDITAR', 'CRIAR', 'EXCLUIR']:
                if not pode_gerenciar_usuarios(request.user):
                    messages.error(request, 'Você não tem permissão para gerenciar usuários.')
                    return redirect('militares:militar_list')
            
            elif modulo == 'RELATORIOS' and acesso == 'VISUALIZAR':
                if not pode_acessar_relatorios(request.user):
                    messages.error(request, 'Você não tem permissão para acessar relatórios.')
                    return redirect('militares:militar_list')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def requer_gerenciamento_comissoes(view_func):
    """
    Decorator que verifica se o usuário pode gerenciar comissões
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not pode_gerenciar_comissoes(request.user):
            messages.error(request, 'Você não tem permissão para gerenciar comissões.')
            return redirect('militares:comissao_list')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def requer_acesso_promocoes(view_func):
    """
    Decorator que verifica se o usuário pode acessar promoções
    Baseado na função militar de comissão
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Superusuários sempre podem
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Verificar se tem função de comissão
        if not pode_acessar_promocoes(request.user):
            messages.error(request, 'Você precisa ter uma função de comissão para acessar promoções.')
            return redirect('militares:selecionar_funcao_lotacao')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ============================================================================
# FUNÇÕES DE UTILIDADE
# ============================================================================

def obter_permissoes_usuario(user):
    """
    Retorna todas as permissões do usuário baseadas na sua função militar
    """
    if not user or not user.is_authenticated:
        return {}
    
    if user.is_superuser:
        return {
            'editar_militares': True,
            'editar_fichas_conceito': True,
            'gerenciar_quadros_vagas': True,
            'gerenciar_comissoes': True,
            'assinar_documentos': True,
            'gerenciar_usuarios': True,
            'acessar_relatorios': True,
            'visualizar_punicoes_elogios': True,
        }
    
    return {
        'visualizar_militares': pode_visualizar_militares(user),
        'editar_militares': pode_editar_militares(user),
        'editar_fichas_conceito': pode_editar_fichas_conceito(user),
        'gerenciar_quadros_vagas': pode_gerenciar_quadros_vagas(user),
        'gerenciar_comissoes': pode_gerenciar_comissoes(user),
        'assinar_documentos': pode_assinar_documentos(user),
        'gerenciar_usuarios': pode_gerenciar_usuarios(user),
        'acessar_relatorios': pode_acessar_relatorios(user),
        'visualizar_punicoes_elogios': True,  # Sempre pode ver suas próprias
    }


def obter_funcoes_militares_usuario(user):
    """
    Retorna todas as funções militares disponíveis para o usuário
    """
    if not user or not user.is_authenticated:
        return UsuarioFuncaoMilitar.objects.none()
    
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        ativo=True
    ).select_related('funcao_militar').order_by('funcao_militar__ordem', 'funcao_militar__nome')


def tem_funcao_militar(user, nome_funcao):
    """
    Verifica se o usuário tem uma função militar específica
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários sempre têm todas as funções
    if user.is_superuser:
        return True
    
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        funcao_militar__nome=nome_funcao,
        ativo=True
    ).exists()


def tem_funcao_restrita(user):
    """
    Verifica se o usuário tem função restrita (Serviço Operacional ou Serviço Administrativo)
    Usuários com essas funções só podem visualizar sua própria ficha, sem CRUD ou PDFs
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários não têm restrições
    if user.is_superuser:
        return False
    
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        funcao_militar__nome__in=['Serviço Operacional', 'Serviço Administrativo'],
        ativo=True
    ).exists()


def pode_fazer_crud_pdf(user, militar):
    """
    Verifica se o usuário pode fazer CRUD e gerar PDFs para um militar
    Retorna False se o usuário tem função restrita e está vendo sua própria ficha
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários sempre podem
    if user.is_superuser:
        return True
    
    # Se não tem função restrita, pode fazer CRUD/PDF normalmente
    if not tem_funcao_restrita(user):
        return True
    
    # Se tem função restrita, verificar se é a própria ficha
    is_proprio_militar = False
    
    # Verificar se request.user.militar existe e é o mesmo militar
    if hasattr(user, 'militar') and user.militar:
        is_proprio_militar = (user.militar.pk == militar.pk)
    
    # Verificar também se militar.user existe e é o mesmo usuário
    if not is_proprio_militar and militar.user:
        is_proprio_militar = (militar.user.pk == user.pk)
    
    # Se é a própria ficha e tem função restrita, não pode fazer CRUD/PDF
    if is_proprio_militar:
        return False
    
    # Se não é a própria ficha, usuário restrito não deveria nem ver
    return False


# ============================================================================
# CONTEXT PROCESSOR
# ============================================================================

def permissoes_militares_processor(request):
    """
    Context processor para disponibilizar permissões baseadas em funções militares
    """
    if not request.user.is_authenticated:
        return {
            'permissoes_militares': {},
            'funcao_militar_atual': None,
            'tem_funcao_comissao': False,
        }
    
    # Superusuários têm todas as permissões
    if request.user.is_superuser:
        return {
            'permissoes_militares': {
                'visualizar_militares': True,
                'editar_militares': True,
                'editar_fichas_conceito': True,
                'gerenciar_quadros_vagas': True,
                'gerenciar_comissoes': True,
                'assinar_documentos': True,
                'gerenciar_usuarios': True,
                'acessar_relatorios': True,
                'acessar_promocoes': True,
                'visualizar_punicoes_elogios': True,
            },
            'funcao_militar_atual': None,
            'tem_funcao_comissao': True,
        }
    
    # Obter permissões do usuário
    permissoes = obter_permissoes_usuario(request.user)
    funcao_atual = obter_funcao_militar_usuario(request.user)
    tem_comissao = tem_funcao_comissao(request.user)
    
    return {
        'permissoes_militares': permissoes,
        'funcao_militar_atual': funcao_atual,
        'tem_funcao_comissao': tem_comissao,
    }


def tem_funcao_comissao(user):
    """
    Verifica se o usuário tem alguma função de comissão ativa
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários sempre podem atuar como comissão
    if user.is_superuser:
        return True
    
    # Verificar funções de comissão (grupo COMISSAO) ou seção de promoções (grupo GESTAO)
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        funcao_militar__grupo__in=['COMISSAO', 'GESTAO'],
        ativo=True
    ).exists()


def pode_acessar_promocoes(user):
    """
    Verifica se o usuário pode acessar a área de promoções
    Baseado na função militar de comissão
    """
    if not user or not user.is_authenticated:
        return False
    
    # Superusuários sempre podem
    if user.is_superuser:
        return True
    
    # Verificar se tem função de comissão
    return tem_funcao_comissao(user)


def obter_funcoes_comissao_usuario(user):
    """
    Retorna todas as funções de comissão disponíveis para o usuário
    """
    if not user or not user.is_authenticated:
        return UsuarioFuncaoMilitar.objects.none()
    
    # Superusuários podem escolher qualquer função de comissão
    if user.is_superuser:
        return UsuarioFuncaoMilitar.objects.filter(
            funcao_militar__grupo='COMISSAO',
            ativo=True
        ).select_related('funcao_militar').order_by('funcao_militar__ordem', 'funcao_militar__nome')
    
    return UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        funcao_militar__grupo='COMISSAO',
        ativo=True
    ).select_related('funcao_militar').order_by('funcao_militar__ordem', 'funcao_militar__nome')


def obter_nivel_acesso_usuario(usuario):
    """
    Determina o nível de acesso do usuário baseado na sua função militar ativa
    Retorna: 'TOTAL', 'ORGAO', 'GRANDE_COMANDO', 'UNIDADE', 'SUBUNIDADE', 'NENHUM'
    """
    if not usuario or not usuario.is_authenticated:
        return 'NENHUM'
    
    # Usuários master têm acesso total
    from .models import UsuarioMaster
    if UsuarioMaster.objects.filter(
        username=usuario.username,
        ativo=True
    ).exists():
        return 'TOTAL'
    
    # Superusuários têm acesso total
    if usuario.is_superuser:
        return 'TOTAL'
    
    # Obter sessão ativa do usuário
    sessao = obter_sessao_ativa_usuario(usuario)
    
    if not sessao or not sessao.funcao_militar_usuario:
        return 'NENHUM'
    
    # Retornar o nível de acesso da função militar ativa
    return sessao.funcao_militar_usuario.nivel_acesso


def obter_filtros_hierarquia_usuario(usuario):
    """
    Retorna os filtros Django ORM para aplicar baseado no nível de acesso do usuário
    """
    nivel = obter_nivel_acesso_usuario(usuario)
    
    if nivel == 'TOTAL':
        # Acesso total - sem filtros
        return {}
    elif nivel == 'ORGAO':
        # Acesso ao órgão
        sessao = obter_sessao_ativa_usuario(usuario)
        if sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.orgao:
            return {
                'lotacoes__orgao': sessao.funcao_militar_usuario.orgao,
                'lotacoes__ativo': True,
                'lotacoes__status': 'ATUAL'
            }
    elif nivel == 'GRANDE_COMANDO':
        # Acesso ao grande comando e suas unidades/sub-unidades
        sessao = obter_sessao_ativa_usuario(usuario)
        if sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.grande_comando:
            return {
                'lotacoes__grande_comando': sessao.funcao_militar_usuario.grande_comando,
                'lotacoes__ativo': True,
                'lotacoes__status': 'ATUAL'
            }
    elif nivel == 'UNIDADE':
        # Acesso à unidade e suas sub-unidades
        sessao = obter_sessao_ativa_usuario(usuario)
        if sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.unidade:
            return {
                'lotacoes__unidade': sessao.funcao_militar_usuario.unidade,
                'lotacoes__ativo': True,
                'lotacoes__status': 'ATUAL'
            }
    elif nivel == 'SUBUNIDADE':
        # Acesso apenas à sub-unidade
        sessao = obter_sessao_ativa_usuario(usuario)
        if sessao and sessao.funcao_militar_usuario and sessao.funcao_militar_usuario.sub_unidade:
            return {
                'lotacoes__sub_unidade': sessao.funcao_militar_usuario.sub_unidade,
                'lotacoes__ativo': True,
                'lotacoes__status': 'ATUAL'
            }
    
    # Se não tem acesso ou não conseguiu determinar, retorna filtro vazio (sem resultados)
    return {'id': -1}  # Filtro que não retorna nada


# ============================================================================
# PERMISSÕES ESPECÍFICAS PARA FUNÇÕES DE GESTÃO E PROMOÇÕES
# ============================================================================

def tem_funcao_especifica_estrutura(user):
    """
    Verifica se o usuário tem função específica dentro da estrutura
    (todas as funções exceto Serviço Operacional)
    """
    if not user or not user.is_authenticated:
        return False
    
    sessao = obter_sessao_ativa_usuario(user)
    if not sessao or not sessao.funcao_militar_usuario:
        return False
    
    funcao_nome = sessao.funcao_militar_usuario.funcao_militar.nome
    
    # Todas as funções específicas da estrutura (exceto Serviço Operacional)
    funcoes_especificas = [
        'Administrador do Sistema',
        'Diretor de Gestão de Pessoas',
        'Chefe da Seção de Promoções',
        'Auxiliar da Seção de Promoções',
        'Ajudante Geral',
        'Comandante Geral',
        'Subcomandante Geral',
        'Presidente da Comissão de Promoções',
        'Membro Nato da Comissão de Promoções',
        'Membro da Comissão de Promoções',
        'Secretário da Comissão de Promoções',
        'Relator da Comissão de Promoções'
    ]
    
    return funcao_nome in funcoes_especificas


def tem_funcao_chefe_auxiliar_promocoes(user):
    """
    Verifica se o usuário tem função de chefe ou auxiliar da seção de promoções
    (apenas essas podem editar ficha de conceito e antiguidade)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar todas as funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        ativo=True
    ).select_related('funcao_militar')
    
    if not funcoes_usuario.exists():
        return False
    
    # Funções que podem editar ficha de conceito e antiguidade
    funcoes_promocoes = [
        'Chefe da Seção de Promoções',
        'Auxiliar da Seção de Promoções',
        'Presidente da Comissão de Promoções',  # Mantido para compatibilidade
        'Secretário da Comissão de Promoções'   # Mantido para compatibilidade
    ]
    
    # Verificar se alguma das funções ativas é de promoções
    for funcao_usr in funcoes_usuario:
        if funcao_usr.funcao_militar.nome in funcoes_promocoes:
            return True
    
    return False


def tem_funcao_comissao_promocoes(user):
    """
    Verifica se o usuário tem função de comissão de promoções
    (CPO, CPP ou funções da seção de promoções)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar todas as funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        ativo=True
    ).select_related('funcao_militar')
    
    if not funcoes_usuario.exists():
        return False
    
    # Funções de comissão de promoções
    funcoes_comissao = [
        'Chefe da Seção de Promoções',
        'Auxiliar da Seção de Promoções',
        'Presidente da CPO (CPO)',
        'Membro Nato da CPO (CPO)',
        'Membro Efetivo da CPO (CPO)',
        'Secretário da CPO (CPO)',
        'Relator da CPO (CPO)',
        'Presidente da CPP (CPP)',
        'Membro Nato da CPP (CPP)',
        'Membro Efetivo da CPP (CPP)',
        'Secretário da CPP (CPP)',
        'Relator da CPP (CPP)',
        # Mantido para compatibilidade
        'Presidente da Comissão de Promoções',
        'Membro Nato da Comissão de Promoções',
        'Membro da Comissão de Promoções',
        'Secretário da Comissão de Promoções',
        'Relator da Comissão de Promoções'
    ]
    
    # Verificar se alguma das funções ativas é de comissão
    for funcao_usr in funcoes_usuario:
        if funcao_usr.funcao_militar.nome in funcoes_comissao:
            return True
    
    return False


def tem_apenas_funcoes_comissao_cpo_cpp(user):
    """
    Verifica se o usuário tem APENAS funções de comissão CPO/CPP
    (sem funções administrativas como Chefe/Auxiliar da Seção)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar todas as funções ativas do usuário
    funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
        usuario=user,
        ativo=True
    ).select_related('funcao_militar')
    
    if not funcoes_usuario.exists():
        return False
    
    # Funções de comissão CPO/CPP (sem funções administrativas)
    funcoes_comissao_cpo_cpp = [
        'Presidente da CPO (CPO)',
        'Membro Nato da CPO (CPO)',
        'Membro Efetivo da CPO (CPO)',
        'Secretário da CPO (CPO)',
        'Relator da CPO (CPO)',
        'Presidente da CPP (CPP)',
        'Membro Nato da CPP (CPP)',
        'Membro Efetivo da CPP (CPP)',
        'Secretário da CPP (CPP)',
        'Relator da CPP (CPP)',
        # Mantido para compatibilidade
        'Presidente da Comissão de Promoções',
        'Membro Nato da Comissão de Promoções',
        'Membro da Comissão de Promoções',
        'Secretário da Comissão de Promoções',
        'Relator da Comissão de Promoções'
    ]
    
    # Funções administrativas (que dão acesso completo)
    funcoes_admin = [
        'Chefe da Seção de Promoções',
        'Auxiliar da Seção de Promoções',
        'Administrador do Sistema',
        'Diretor de Gestão de Pessoas',
        'Ajudante Geral',
        'Comandante Geral',
        'Subcomandante Geral'
    ]
    
    tem_comissao_cpo_cpp = False
    tem_funcao_admin = False
    
    for funcao_usr in funcoes_usuario:
        if funcao_usr.funcao_militar.nome in funcoes_comissao_cpo_cpp:
            tem_comissao_cpo_cpp = True
        elif funcao_usr.funcao_militar.nome in funcoes_admin:
            tem_funcao_admin = True
    
    # Retorna True apenas se tem comissão CPO/CPP E não tem função administrativa
    return tem_comissao_cpo_cpp and not tem_funcao_admin


def tem_funcao_ativa_comissao_cpo_cpp(user):
    """
    Verifica se a função ativa na sessão do usuário é de comissão CPO/CPP
    (baseado na seleção de função na sessão)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar a função ativa na sessão
    sessao = obter_sessao_ativa_usuario(user)
    if not sessao or not sessao.funcao_militar_usuario:
        return False
    
    funcao_nome = sessao.funcao_militar_usuario.funcao_militar.nome
    
    # Funções de comissão CPO/CPP
    funcoes_comissao_cpo_cpp = [
        'Presidente da CPO (CPO)',
        'Membro Nato da CPO (CPO)',
        'Membro Efetivo da CPO (CPO)',
        'Secretário da CPO (CPO)',
        'Relator da CPO (CPO)',
        'Presidente da CPP (CPP)',
        'Membro Nato da CPP (CPP)',
        'Membro Efetivo da CPP (CPP)',
        'Secretário da CPP (CPP)',
        'Relator da CPP (CPP)',
        # Mantido para compatibilidade
        'Presidente da Comissão de Promoções',
        'Membro Nato da Comissão de Promoções',
        'Membro da Comissão de Promoções',
        'Secretário da Comissão de Promoções',
        'Relator da Comissão de Promoções'
    ]
    
    return funcao_nome in funcoes_comissao_cpo_cpp


def pode_editar_militar_gestao(user, militar):
    """
    Verifica se usuário com função específica da estrutura pode editar um militar específico
    Baseado na lotação e descendências
    """
    if not tem_funcao_especifica_estrutura(user):
        return False
    
    # Superusuários e usuários master sempre podem
    if user.is_superuser:
        return True
    
    from .models import UsuarioMaster
    if UsuarioMaster.objects.filter(username=user.username, ativo=True).exists():
        return True
    
    sessao = obter_sessao_ativa_usuario(user)
    if not sessao or not sessao.funcao_militar_usuario:
        return False
    
    # Verificar se o militar está na lotação do usuário ou suas descendências
    return militar_na_lotacao_descendencia(militar, sessao.funcao_militar_usuario)


def militar_na_lotacao_descendencia(militar, funcao_usuario):
    """
    Verifica se um militar está na lotação do usuário ou suas descendências
    """
    from .models import Lotacao
    
    # Buscar lotação atual do militar
    lotacao_atual = Lotacao.objects.filter(
        militar=militar,
        ativo=True,
        status='ATUAL'
    ).first()
    
    if not lotacao_atual:
        return False
    
    # Verificar se está na mesma lotação ou descendência
    if funcao_usuario.orgao and lotacao_atual.orgao == funcao_usuario.orgao:
        return True
    
    if funcao_usuario.grande_comando and lotacao_atual.grande_comando == funcao_usuario.grande_comando:
        return True
    
    if funcao_usuario.unidade and lotacao_atual.unidade == funcao_usuario.unidade:
        return True
    
    if funcao_usuario.sub_unidade and lotacao_atual.sub_unidade == funcao_usuario.sub_unidade:
        return True
    
    return False


def pode_editar_campo_militar_gestao(user, militar, campo):
    """
    Verifica se usuário com função específica da estrutura pode editar um campo específico
    Aplica as restrições: não pode editar ficha de conceito nem antiguidade
    (exceto chefe e auxiliar da seção de promoções)
    """
    if not pode_editar_militar_gestao(user, militar):
        return False
    
    # Campos restritos que não podem ser editados por funções específicas da estrutura
    campos_restritos = [
        'ficha_conceito',
        'ficha_conceito_oficiais',
        'ficha_conceito_pracas',
        'numero_antiguidade',
        'antiguidade',
        'data_antiguidade'
    ]
    
    # Verificar se o campo está na lista de restritos
    if campo.lower() in [c.lower() for c in campos_restritos]:
        # Apenas chefe e auxiliar da seção de promoções podem editar esses campos
        return tem_funcao_chefe_auxiliar_promocoes(user)
    
    return True


def pode_editar_antiguidade_militar(user, militar):
    """
    Verifica se o usuário pode editar a antiguidade de um militar
    Apenas chefe e auxiliar da seção de promoções podem editar antiguidade
    """
    if not user or not user.is_authenticated or not militar:
        return False
    
    # Superusuários e usuários master sempre podem
    if user.is_superuser:
        return True
    
    from .models import UsuarioMaster
    if UsuarioMaster.objects.filter(username=user.username, ativo=True).exists():
        return True
    
    # Apenas chefe e auxiliar da seção de promoções podem editar antiguidade
    return tem_funcao_chefe_auxiliar_promocoes(user)


# ============================================================================
# SISTEMA DE PERMISSÕES BASEADO EM NÍVEIS HIERÁRQUICOS
# ============================================================================

def obter_nivel_usuario(user):
    """
    Obtém o nível hierárquico do usuário baseado na sua função ativa
    """
    if not user or not user.is_authenticated:
        return 0
    
    # Superusuários e usuários master têm nível máximo
    if user.is_superuser:
        return 5
    
    from .models import UsuarioMaster
    if UsuarioMaster.objects.filter(username=user.username, ativo=True).exists():
        return 5
    
    sessao = obter_sessao_ativa_usuario(user)
    if not sessao or not sessao.funcao_militar_usuario:
        return 0
    
    return sessao.funcao_militar_usuario.funcao_militar.nivel


def pode_apenas_visualizar(user):
    """
    Verifica se o usuário tem permissão apenas para visualização (Nível 1)
    """
    nivel = obter_nivel_usuario(user)
    return nivel == 1


def pode_atualizar_dados_cadastrais(user):
    """
    Verifica se o usuário pode atualizar dados cadastrais (Nível 2)
    """
    nivel = obter_nivel_usuario(user)
    return nivel >= 2


def pode_editar_inserir_dados_ficha(user):
    """
    Verifica se o usuário pode editar e inserir novos dados na ficha (Níveis 3-5)
    """
    nivel = obter_nivel_usuario(user)
    return nivel >= 3


def pode_editar_campo_por_nivel(user, campo):
    """
    Verifica se o usuário pode editar um campo específico baseado no seu nível
    """
    if not user or not user.is_authenticated:
        return False
    
    nivel = obter_nivel_usuario(user)
    
    # Nível 1: Apenas visualização
    if nivel == 1:
        return False
    
    # Nível 2: Pode atualizar dados cadastrais básicos
    if nivel == 2:
        campos_permitidos_nivel_2 = [
            'nome_completo',
            'nome_guerra',
            'cpf',
            'rg',
            'data_nascimento',
            'sexo',
            'estado_civil',
            'endereco',
            'telefone',
            'email',
            'altura',
            'peso',
            'cor_olhos',
            'cor_cabelos',
            'tipo_sanguineo',
            'nome_pai',
            'nome_mae',
            'naturalidade',
            'nacionalidade'
        ]
        return campo.lower() in [c.lower() for c in campos_permitidos_nivel_2]
    
    # Níveis 3-5: Pode editar todos os campos (exceto restrições especiais)
    if nivel >= 3:
        # Campos restritos que só funções específicas podem editar
        campos_restritos = [
            'ficha_conceito',
            'ficha_conceito_oficiais',
            'ficha_conceito_pracas',
            'numero_antiguidade',
            'antiguidade',
            'data_antiguidade'
        ]
        
        # Se é campo restrito, verificar se tem função específica
        if campo.lower() in [c.lower() for c in campos_restritos]:
            return tem_funcao_chefe_auxiliar_promocoes(user)
        
        return True
    
    return False


def pode_inserir_novo_militar(user):
    """
    Verifica se o usuário pode inserir novos militares (Níveis 3-5)
    """
    nivel = obter_nivel_usuario(user)
    return nivel >= 3


def pode_atualizar_militar_por_nivel(user, militar, campo=None):
    """
    Verifica se o usuário pode atualizar um militar baseado no seu nível
    """
    if not user or not user.is_authenticated or not militar:
        return False
    
    # Superusuários e usuários master sempre podem
    if user.is_superuser:
        return True
    
    from .models import UsuarioMaster
    if UsuarioMaster.objects.filter(username=user.username, ativo=True).exists():
        return True
    
    nivel = obter_nivel_usuario(user)
    
    # Nível 1: Apenas visualização
    if nivel == 1:
        return False
    
    # Nível 2: Pode atualizar dados cadastrais
    if nivel == 2:
        if campo:
            return pode_editar_campo_por_nivel(user, campo)
        return True
    
    # Níveis 3-5: Pode editar todos os campos (com restrições)
    if nivel >= 3:
        if campo:
            return pode_editar_campo_por_nivel(user, campo)
        return True
    
    return False
