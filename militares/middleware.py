from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from militares.models import UsuarioFuncao


class FuncaoSelecaoMiddleware:
    """
    Middleware para verificar se o usuário precisa selecionar uma função após login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Middleware agora não faz mais nenhuma verificação de função
        return self.get_response(request)


class ControleAcessoComissaoMiddleware:
    """
    Middleware para controle de acesso baseado em funções de comissão
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # TEMPORARIAMENTE DESABILITADO PARA DEBUG
        return self.get_response(request)
        
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # URLs que requerem função CPO específica
        urls_cpo = [
            '/militares/comissao/',
            '/militares/comissao-promocao/',
            '/militares/membro-comissao/',
            '/militares/sessao-comissao/',
            '/militares/deliberacao-comissao/',
            '/militares/ata-sessao/',
            '/militares/modelo-ata/',
        ]
        
        # URLs que requerem função CPP específica
        urls_cpp = [
            '/militares/comissao/',
            '/militares/comissao-promocao/',
            '/militares/membro-comissao/',
            '/militares/sessao-comissao/',
            '/militares/deliberacao-comissao/',
            '/militares/ata-sessao/',
            '/militares/modelo-ata/',
        ]
        
        # URLs que permitem apenas visualização para membros de comissão
        urls_apenas_visualizacao = [
            '/militares/ficha-conceito/',
            '/militares/militar/',
            '/militares/documento/',
        ]
        
        # URLs de administração (apenas Administrador do Sistema)
        urls_administracao = [
            '/militares/usuarios/',
            '/militares/grupos/',
            '/militares/permissoes/',
            '/admin/',
        ]
        
        current_path = request.path
        
        # Verificar se o usuário tem função de comissão
        funcoes_comissao = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['CPO', 'CPP']
        )
        
        # Verificar se o usuário tem funções especiais
        funcoes_especiais = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        )
        
        # Verificar se é administrador do sistema
        funcao_admin = UsuarioFuncao.objects.filter(
            usuario=request.user,
            status='ATIVO',
            cargo_funcao__nome='Administrador do Sistema'
        ).exists()
        
        if funcoes_comissao.exists():
            # Usuário tem função de comissão
            funcao_cpo = funcoes_comissao.filter(cargo_funcao__nome='CPO').exists()
            funcao_cpp = funcoes_comissao.filter(cargo_funcao__nome='CPP').exists()
            
            # Verificar acesso a URLs CPO (apenas CPO pode acessar)
            if any(current_path.startswith(url) for url in urls_cpo) and not funcao_cpo and not funcoes_especiais.exists() and not request.user.is_superuser:
                messages.error(request, 'Acesso negado. Apenas usuários CPO podem acessar esta área.')
                return HttpResponseForbidden('Acesso negado')
            
            # Verificar acesso a URLs CPP (apenas CPP pode acessar)
            if any(current_path.startswith(url) for url in urls_cpp) and not funcao_cpp and not funcoes_especiais.exists() and not request.user.is_superuser:
                messages.error(request, 'Acesso negado. Apenas usuários CPP podem acessar esta área.')
                return HttpResponseForbidden('Acesso negado')
            
            # Verificar apenas visualização para membros de comissão (exceto funções especiais)
            if any(current_path.startswith(url) for url in urls_apenas_visualizacao):
                if request.method in ['POST', 'PUT', 'DELETE'] and not funcoes_especiais.exists() and not request.user.is_superuser:
                    messages.error(request, 'Usuários de comissão podem apenas visualizar. Não é permitido editar.')
                    return HttpResponseForbidden('Apenas visualização permitida')
        
        # Verificar acesso à administração (apenas Administrador do Sistema)
        if any(current_path.startswith(url) for url in urls_administracao):
            if not funcao_admin and not request.user.is_superuser:
                messages.error(request, 'Acesso negado. Apenas Administradores do Sistema podem acessar esta área.')
                return HttpResponseForbidden('Acesso negado')
        
        return self.get_response(request) 