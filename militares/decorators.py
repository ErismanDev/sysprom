from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from functools import wraps
from django.http import HttpResponseForbidden
from militares.models import UsuarioFuncao, CargoFuncao, MembroComissao

def can_edit_ficha_conceito(user):
    """
    Verifica se o usuário pode editar fichas de conceito.
    Apenas admin, chefe da seção de promoções e diretor de gestão de pessoas podem editar.
    """
    from .permissoes_simples import pode_editar_fichas_conceito
    return pode_editar_fichas_conceito(user)

def can_edit_militar(user):
    """
    Verifica se o usuário pode editar cadastros de militares.
    Apenas admin, chefe da seção de promoções e diretor de gestão de pessoas podem editar.
    """
    from .permissoes_simples import pode_editar_militares
    return pode_editar_militares(user)

def require_ficha_conceito_permission(view_func):
    """
    Decorator que verifica se o usuário tem permissão para editar fichas de conceito.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar se o usuário tem permissão básica
        if not can_edit_ficha_conceito(request.user):
            messages.error(request, 'Você não tem permissão para editar fichas de conceito. Apenas administradores, chefes da seção de promoções e diretores de gestão de pessoas podem editar.')
            return redirect('militares:ficha_conceito_list')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def ficha_conceito_permission_required(view_func):
    """
    Decorator que combina login_required com verificação de permissão para fichas de conceito.
    """
    from django.contrib.auth.decorators import login_required
    
    @login_required
    @require_ficha_conceito_permission
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return wrapper 

def usuario_comissao_required(view_func):
    """
    Decorator para verificar se o usuário tem função de comissão (CPO ou CPP)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem função de comissão ativa
        funcoes_comissao = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['CPO', 'CPP']
        )
        
        # Verificar se usuário tem funções especiais
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        )
        
        if not funcoes_comissao.exists() and not funcoes_especiais.exists() and not request.user.is_superuser:
            messages.error(request, 'Acesso negado. Você não possui permissão para acessar esta área.')
            return HttpResponseForbidden('Acesso negado')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def usuario_cpo_required(view_func):
    """
    Decorator para verificar se o usuário tem função CPO ou funções especiais
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem função CPO ativa
        funcao_cpo = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome='CPO'
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem acesso completo
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Permitir acesso se for superusuário, tiver função CPO ou funções especiais
        if request.user.is_superuser or funcao_cpo or funcoes_especiais:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas usuários CPO ou funções especiais podem acessar esta área.')
        return HttpResponseForbidden('Acesso negado')
    return _wrapped_view

def usuario_cpp_required(view_func):
    """
    Decorator para verificar se o usuário tem função CPP ou funções especiais
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem função CPP ativa
        funcao_cpp = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome='CPP'
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem acesso completo
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Permitir acesso se for superusuário, tiver função CPP ou funções especiais
        if request.user.is_superuser or funcao_cpp or funcoes_especiais:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas usuários CPP ou funções especiais podem acessar esta área.')
        return HttpResponseForbidden('Acesso negado')
    return _wrapped_view

def apenas_visualizacao_comissao(view_func):
    """
    Decorator para permitir apenas visualização para usuários de comissão
    (exceto para funções especiais que podem fazer CRUD completo)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem função de comissão
        funcoes_comissao = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['CPO', 'CPP']
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem CRUD completo
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Se for membro de comissão (CPO/CPP) e tentar fazer operações de escrita, bloquear
        if funcoes_comissao and request.method in ['POST', 'PUT', 'DELETE'] and not funcoes_especiais and not request.user.is_superuser:
            messages.error(request, 'Usuários de comissão podem apenas visualizar. Não é permitido editar.')
            return HttpResponseForbidden('Apenas visualização permitida')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def comissao_acesso_total(view_func):
    """
    Decorator para permitir acesso total para membros de comissão
    quando estão dentro do contexto de comissões (sessões, votos, etc.)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem função de comissão
        funcoes_comissao = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['CPO', 'CPP']
        ).exists()
        
        # Verificar se usuário é membro de comissão ativa
        membros_comissao = MembroComissao.objects.filter(
            usuario=request.user,
            ativo=True,
            comissao__status='ATIVA'
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem CRUD completo
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Permitir acesso total se for membro de comissão, funções especiais ou superusuário
        if funcoes_comissao or membros_comissao or funcoes_especiais or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas membros de comissão podem acessar esta área.')
        return HttpResponseForbidden('Acesso negado')
    return _wrapped_view

def administracao_required(view_func):
    """
    Decorator para verificar se o usuário tem acesso à administração
    Apenas Administrador do Sistema pode acessar
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem função de administrador do sistema
        funcao_admin = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Permitir acesso se for superusuário ou tiver função de administrador
        if request.user.is_superuser or funcao_admin:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas Administradores do Sistema podem acessar esta área.')
        return HttpResponseForbidden('Acesso negado')
    return _wrapped_view

def militar_edit_permission(view_func):
    """
    Decorator para verificar permissão de edição de militares
    Combina can_edit_militar com apenas_visualizacao_comissao
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem função de comissão
        funcoes_comissao = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['CPO', 'CPP']
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem CRUD completo
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Se for membro de comissão (CPO/CPP) e tentar fazer operações de escrita, bloquear
        if funcoes_comissao and request.method in ['POST', 'PUT', 'DELETE'] and not funcoes_especiais and not request.user.is_superuser:
            messages.error(request, 'Usuários de comissão podem apenas visualizar. Não é permitido editar.')
            return HttpResponseForbidden('Apenas visualização permitida')
        
        # Verificar permissão básica de edição
        if not can_edit_militar(request.user):
            messages.error(request, 'Você não tem permissão para editar militares. Apenas administradores, chefes da seção de promoções e diretores de gestão de pessoas podem editar.')
            return redirect('militares:militar_list')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cargos_especiais_required(view_func):
    """
    Decorator para verificar se o usuário tem cargo especial
    (Diretor de Gestão de Pessoas ou Chefe da Seção de Promoções)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem cargos especiais
        cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=cargos_especiais
        )
        
        # Permitir acesso se for superusuário, staff ou tiver cargo especial
        if request.user.is_superuser or request.user.is_staff or funcoes_especiais.exists():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas Diretor de Gestão de Pessoas e Chefe da Seção de Promoções podem realizar esta ação.')
        return HttpResponseForbidden('Acesso negado')
    
    return _wrapped_view 