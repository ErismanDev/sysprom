import time
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from militares.models import UsuarioFuncaoMilitar, LogSistema


class FuncaoSelecaoMiddleware:
    """
    Middleware para verificar se o usuário precisa selecionar uma função após login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # URLs que não precisam de verificação de função
        urls_excluidas = [
            '/login/',
            '/logout/',
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/selecionar-funcao/',
            '/selecionar-funcao-lotacao/',
            '/militares/selecionar-funcao-lotacao/',
            '/militares/selecionar-funcao/',
            '/militares/abastecimento-qr',  # URL pública para abastecimento via QR Code (com e sem ID)
            '/militares/frota-mobile',  # URL pública para formulário mobile de controle de frota (abastecimento/manutenção)
            '/militares/abastecimento-qr/sucesso',  # URL pública para página de sucesso após abastecimento
            '/militares/painel-guarda-login/',  # URL pública para login do painel de guarda
            '/militares/painel-guarda/',  # URL pública do painel de guarda (tem login integrado)
            '/militares/painel-guarda-ajax/',  # Endpoint AJAX do painel de guarda
            '/militares/ensino/login/',  # Login do módulo de ensino
        ]
        
        # Verificar se a URL atual está excluída
        if any(request.path.startswith(url) for url in urls_excluidas):
            return self.get_response(request)
        
        # Verificar se é usuário do módulo de ensino (através da sessão)
        ensino_tipo = request.session.get('ensino_tipo')
        ensino_id = request.session.get('ensino_id')
        if ensino_tipo and ensino_id:
            # Usuários do módulo de ensino não precisam de UsuarioSessao
            return self.get_response(request)
        
        # Superusuários podem acessar sem função e sem sessão
        if request.user.is_superuser:
            return self.get_response(request)
        
        # Verificar se é usuário master
        from militares.models import UsuarioMaster
        if UsuarioMaster.objects.filter(
            username=request.user.username,
            ativo=True
        ).exists():
            return self.get_response(request)
        
        # Verificar se é Administrador do Sistema
        from militares.models import UsuarioFuncaoMilitar
        tem_funcao_admin = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Administrador do Sistema', 'Administrador']
        ).exists()
        
        if tem_funcao_admin:
            return self.get_response(request)
        
        # Verificar se o usuário tem sessão ativa
        from militares.models import UsuarioSessao
        sessao_ativa = UsuarioSessao.objects.filter(
            usuario=request.user,
            ativo=True
        ).first()
        
        # Se não tem sessão ativa, redirecionar para login
        if not sessao_ativa:
            from django.shortcuts import redirect
            return redirect('login')
        
        return self.get_response(request)


class ControleAcessoComissaoMiddleware:
    """
    Middleware para controle de acesso baseado em funções de comissão
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar se o usuário está autenticado
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Superusuários têm acesso total - pular todas as verificações
        if request.user.is_superuser:
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
            '/militares/comissao-fichas-oficiais/',
            '/militares/comissao-fichas-pracas/',
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
            '/militares/comissao-fichas-oficiais/',
            '/militares/comissao-fichas-pracas/',
        ]
        
        # URLs que permitem apenas visualização para membros de comissão
        urls_apenas_visualizacao = [
            '/militares/ficha-conceito/',
            '/militares/militares/',
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
        funcoes_comissao = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=[
                'CPO', 'CPP',
                'Membro Efetivo da Comissão de Promoções de Oficiais',
                'Membro Efetivo da Comissão de Promoções de Praças'
            ]
        )
        
        # Verificar se o usuário tem funções especiais
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        )
        
        # Verificar se é administrador do sistema
        funcao_admin = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome='Administrador do Sistema'
        ).exists()
        
        if funcoes_comissao.exists():
            # Usuário tem função de comissão
            funcao_cpo = funcoes_comissao.filter(
                funcao_militar__nome__in=['CPO', 'Membro Efetivo da Comissão de Promoções de Oficiais']
            ).exists()
            funcao_cpp = funcoes_comissao.filter(
                funcao_militar__nome__in=['CPP', 'Membro Efetivo da Comissão de Promoções de Praças']
            ).exists()
            
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


class LoggingMiddleware(MiddlewareMixin):
    """Middleware para registrar automaticamente as atividades do sistema"""
    
    def process_request(self, request):
        # Marcar o início do tempo de processamento
        request.start_time = time.time()
    
    def process_response(self, request, response):
        # Calcular o tempo de execução
        if hasattr(request, 'start_time'):
            tempo_execucao = time.time() - request.start_time
        else:
            tempo_execucao = None
        
        # Não registrar logs para arquivos estáticos ou admin
        if self._should_skip_logging(request):
            return response
        
        try:
            # Determinar o nível do log baseado no status da resposta
            nivel = self._determinar_nivel(response.status_code)
            
            # Determinar o módulo baseado na URL
            modulo = self._determinar_modulo(request.path)
            
            # Determinar a ação baseada no método HTTP
            acao = self._determinar_acao(request.method)
            
            # Criar descrição
            descricao = self._criar_descricao(request, response)
            
            # Obter detalhes da requisição
            detalhes = self._obter_detalhes_requisicao(request)
            
            # Registrar o log
            LogSistema.registrar(
                nivel=nivel,
                modulo=modulo,
                acao=acao,
                usuario=request.user if not isinstance(request.user, AnonymousUser) else None,
                descricao=descricao,
                detalhes=detalhes,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                url=request.build_absolute_uri(),
                metodo_http=request.method,
                tempo_execucao=tempo_execucao,
                erro=None if response.status_code < 400 else f'Status {response.status_code}',
            )
            
        except Exception as e:
            # Em caso de erro no logging, não afetar a resposta
            print(f"Erro ao registrar log: {e}")
        
        return response
    
    def process_exception(self, request, exception):
        """Registrar exceções não tratadas"""
        try:
            # Obter o tempo de execução
            if hasattr(request, 'start_time'):
                tempo_execucao = time.time() - request.start_time
            else:
                tempo_execucao = None
            
            # Registrar o erro
            LogSistema.registrar(
                nivel='ERROR',
                modulo=self._determinar_modulo(request.path),
                acao='EXCEPTION',
                usuario=request.user if not isinstance(request.user, AnonymousUser) else None,
                descricao=f'Exceção não tratada: {str(exception)}',
                detalhes={
                    'exception_type': type(exception).__name__,
                    'exception_args': str(exception.args),
                },
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                url=request.build_absolute_uri(),
                metodo_http=request.method,
                tempo_execucao=tempo_execucao,
                erro=str(exception),
                traceback=self._get_traceback(exception),
            )
            
        except Exception as e:
            print(f"Erro ao registrar exceção: {e}")
        
        return None
    
    def _should_skip_logging(self, request):
        """Determina se deve pular o logging para esta requisição"""
        skip_paths = [
            '/static/',
            '/media/',
            '/admin/jsi18n/',
            '/favicon.ico',
            '/robots.txt',
        ]
        
        # Pular arquivos estáticos
        for path in skip_paths:
            if request.path.startswith(path):
                return True
        
        # Pular requisições de API que não são importantes
        if request.path.startswith('/api/') and request.method == 'GET':
            return True
        
        return False
    
    def _determinar_nivel(self, status_code):
        """Determina o nível do log baseado no status da resposta"""
        if status_code >= 500:
            return 'CRITICAL'
        elif status_code >= 400:
            return 'ERROR'
        elif status_code >= 300:
            return 'WARNING'
        else:
            return 'INFO'
    
    def _determinar_modulo(self, path):
        """Determina o módulo baseado na URL"""
        if path.startswith('/militares/'):
            return 'MILITARES'
        elif path.startswith('/usuarios/'):
            return 'USUARIOS'
        elif path.startswith('/comissao/'):
            return 'COMISSAO'
        elif path.startswith('/admin/'):
            return 'SISTEMA'
        elif path.startswith('/login/') or path.startswith('/logout/'):
            return 'SEGURANCA'
        else:
            return 'SISTEMA'
    
    def _determinar_acao(self, method):
        """Determina a ação baseada no método HTTP"""
        acoes = {
            'GET': 'VIEW',
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }
        return acoes.get(method, 'OTHER')
    
    def _criar_descricao(self, request, response):
        """Cria uma descrição para o log"""
        if request.path.startswith('/militares/'):
            if 'list' in request.path:
                return 'Listagem de militares acessada'
            elif 'detail' in request.path:
                return 'Detalhes de militar visualizados'
            elif 'create' in request.path:
                return 'Formulário de criação de militar acessado'
            elif 'update' in request.path:
                return 'Formulário de edição de militar acessado'
            else:
                return f'Acesso à página: {request.path}'
        elif request.path.startswith('/admin/'):
            return f'Acesso ao admin: {request.path}'
        elif request.path.startswith('/login/'):
            return 'Tentativa de login'
        elif request.path.startswith('/logout/'):
            return 'Logout realizado'
        else:
            return f'Acesso à página: {request.path}'
    
    def _obter_detalhes_requisicao(self, request):
        """Obtém detalhes da requisição para o log"""
        detalhes = {
            'path': request.path,
            'method': request.method,
            'content_type': request.content_type,
            'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        }
        
        # Adicionar parâmetros GET (limitado para não sobrecarregar)
        if request.GET:
            detalhes['get_params'] = dict(request.GET.items())
        
        # Adicionar parâmetros POST (limitado e sensível)
        if request.POST and request.method in ['POST', 'PUT', 'PATCH']:
            post_data = {}
            for key, value in request.POST.items():
                # Não registrar senhas ou dados sensíveis
                if 'password' not in key.lower() and 'senha' not in key.lower():
                    post_data[key] = value[:100] if len(str(value)) > 100 else value
            detalhes['post_params'] = post_data
        
        return detalhes
    
    def _get_client_ip(self, request):
        """Obtém o IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_traceback(self, exception):
        """Obtém o traceback da exceção"""
        import traceback
        return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__)) 