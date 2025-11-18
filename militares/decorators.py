from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from functools import wraps
from django.http import HttpResponseForbidden
from militares.models import UsuarioFuncaoMilitar, FuncaoMilitar, MembroComissao

def can_edit_ficha_conceito(user):
    """
    Verifica se o usuário pode editar fichas de conceito.
    Baseado na função militar da sessão.
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
            messages.error(request, 'Você não tem permissão para editar fichas de conceito. Apenas Chefe da Seção de Promoções e Auxiliar da Seção de Promoções podem editar.')
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
        funcoes_comissao = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['CPO', 'CPP']
        )
        
        # Verificar se usuário tem funções especiais
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
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
        funcao_cpo = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome='CPO'
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem acesso completo
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
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
        funcao_cpp = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome='CPP'
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem acesso completo
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
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
        funcoes_comissao = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['CPO', 'CPP']
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem CRUD completo
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
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
        funcoes_comissao = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['CPO', 'CPP']
        ).exists()
        
        # Verificar se usuário é membro de comissão ativa
        membros_comissao = MembroComissao.objects.filter(
            usuario=request.user,
            ativo=True,
            comissao__status='ATIVA'
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem CRUD completo
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
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
    Apenas Administrador do Sistema ou Usuário Master pode acessar
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se é usuário master
        from .models import UsuarioMaster
        if UsuarioMaster.objects.filter(
            username=request.user.username,
            ativo=True
        ).exists():
            return view_func(request, *args, **kwargs)
        
        # Verificar se usuário tem função de administrador do sistema
        funcao_admin = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Permitir acesso se for superusuário ou tiver função de administrador
        if request.user.is_superuser or funcao_admin:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas Administradores do Sistema ou Usuários Master podem acessar esta área.')
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
        funcoes_comissao = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['CPO', 'CPP']
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem CRUD completo
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        ).exists()
        
        # Se for membro de comissão (CPO/CPP) e tentar fazer operações de escrita, bloquear
        if funcoes_comissao and request.method in ['POST', 'PUT', 'DELETE'] and not funcoes_especiais and not request.user.is_superuser:
            messages.error(request, 'Usuários de comissão podem apenas visualizar. Não é permitido editar.')
            return HttpResponseForbidden('Apenas visualização permitida')
        
        # Verificar permissão básica de edição
        if not can_edit_militar(request.user):
            messages.error(request, 'Você não tem permissão para editar militares. Apenas administradores, chefes da seção de promoções, diretores de gestão de pessoas e operadores do sistema podem editar.')
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
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=cargos_especiais
        )
        
        # Permitir acesso se for superusuário, staff ou tiver cargo especial
        if request.user.is_superuser or request.user.is_staff or funcoes_especiais.exists():
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas Diretor de Gestão de Pessoas e Chefe da Seção de Promoções podem realizar esta ação.')
        return HttpResponseForbidden('Acesso negado')
    
    return _wrapped_view

def diretor_gestao_chefe_promocoes_required(view_func):
    """
    Decorator para verificar se o usuário é Diretor de Gestão de Pessoas ou Chefe da Seção de Promoções
    Também verifica se o usuário tem a permissão granular MILITARES_TRANSFERIR
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar se usuário tem as funções específicas permitidas
        funcoes_permitidas = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções']
        funcoes_usuario = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=funcoes_permitidas
        )
        
        # Verificar também se o usuário tem a permissão granular MILITARES_TRANSFERIR
        from .permissoes_simples import tem_permissao
        tem_permissao_transferir = tem_permissao(request.user, 'militares', 'transferir')
        
        # Permitir acesso se for superusuário, tiver uma das funções específicas ou tiver a permissão granular
        if request.user.is_superuser or funcoes_usuario.exists() or tem_permissao_transferir:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Acesso negado. Apenas Diretor de Gestão de Pessoas, Chefe da Seção de Promoções ou usuários com permissão para transferir podem realizar esta ação.')
        return HttpResponseForbidden('Acesso negado')
    
    return _wrapped_view

def ficha_conceito_visualizacao_required(view_func):
    """
    Decorator para verificar se o usuário pode visualizar fichas de conceito
    Permite visualização para usuários com permissão de edição ou para visualizar própria ficha
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        from .permissoes_simples import pode_editar_fichas_conceito, pode_visualizar_fichas_conceito
        
        # Se pode editar fichas, pode visualizar qualquer uma
        if pode_editar_fichas_conceito(request.user):
            return view_func(request, *args, **kwargs)
        
        # Verificar se é para visualizar ficha específica (se pk estiver nos kwargs)
        if 'pk' in kwargs:
            from .models import FichaConceitoPracas, FichaConceitoOficiais
            from django.shortcuts import get_object_or_404
            
            try:
                # Tentar buscar ficha de praças
                ficha = get_object_or_404(FichaConceitoPracas, pk=kwargs['pk'])
                
                # Verificar se é a própria ficha do usuário
                if hasattr(request.user, 'militar') and ficha.militar == request.user.militar:
                    return view_func(request, *args, **kwargs)
                
                # Se não é a própria ficha, verificar permissão geral
                if pode_visualizar_fichas_conceito(request.user):
                    return view_func(request, *args, **kwargs)
            except:
                try:
                    # Tentar buscar ficha de oficiais
                    ficha = get_object_or_404(FichaConceitoOficiais, pk=kwargs['pk'])
                    
                    # Verificar se é a própria ficha do usuário
                    if hasattr(request.user, 'militar') and ficha.militar == request.user.militar:
                        return view_func(request, *args, **kwargs)
                    
                    # Se não é a própria ficha, verificar permissão geral
                    if pode_visualizar_fichas_conceito(request.user):
                        return view_func(request, *args, **kwargs)
                except:
                    pass
        
        messages.error(request, 'Você não tem permissão para visualizar esta ficha de conceito.')
        return redirect('militares:ficha_conceito_pracas_list')
    
    return _wrapped_view 