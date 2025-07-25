from django.utils import timezone
from datetime import timedelta
from .models import SessaoComissao, MembroComissao
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from functools import wraps
from .models import UsuarioFuncao
from .decorators import can_edit_militar

def sessao_alertas(request):
    """
    Context processor para adicionar alertas de sessões agendadas
    """
    if not request.user.is_authenticated:
        return {}
    
    # Verificar se o usuário é membro de alguma comissão
    membros = MembroComissao.objects.filter(usuario=request.user, ativo=True)
    if not membros.exists():
        return {}
    
    # Buscar sessões agendadas para as comissões do usuário
    hoje = timezone.now().date()
    proximos_7_dias = hoje + timedelta(days=7)
    
    # Sessões agendadas para hoje
    sessoes_hoje = SessaoComissao.objects.filter(
        comissao__membros__in=membros,
        data_sessao=hoje,
        status='AGENDADA'
    ).select_related('comissao').distinct()
    
    # Sessões agendadas para os próximos 7 dias
    sessoes_proximas = SessaoComissao.objects.filter(
        comissao__membros__in=membros,
        data_sessao__range=[hoje + timedelta(days=1), proximos_7_dias],
        status='AGENDADA'
    ).select_related('comissao').distinct()
    
    # Sessões em andamento hoje
    sessoes_em_andamento = SessaoComissao.objects.filter(
        comissao__membros__in=membros,
        data_sessao=hoje,
        status='EM_ANDAMENTO'
    ).select_related('comissao').distinct()
    
    return {
        'sessoes_alertas': {
            'hoje': sessoes_hoje,
            'proximas': sessoes_proximas,
            'em_andamento': sessoes_em_andamento,
            'tem_alertas': sessoes_hoje.exists() or sessoes_proximas.exists() or sessoes_em_andamento.exists()
        }
    } 

def notificacoes_processor(request):
    """Context processor para disponibilizar notificações em todos os templates"""
    if request.user.is_authenticated:
        from .models import NotificacaoSessao
        total_notificacoes = NotificacaoSessao.objects.filter(
            usuario=request.user,
            lida=False
        ).count()
        
        return {
            'total_notificacoes': total_notificacoes,
        }
    return {
        'total_notificacoes': 0,
    } 

def funcao_atual_processor(request):
    """
    Context processor para disponibilizar a função atual em todos os templates
    """
    if request.user.is_authenticated:
        funcao_atual_id = request.session.get('funcao_atual_id')
        if funcao_atual_id:
            try:
                from .models import UsuarioFuncao
                funcao_atual = UsuarioFuncao.objects.select_related('cargo_funcao').get(
                    id=funcao_atual_id,
                    usuario=request.user,
                    status='ATIVO'
                )
                return {
                    'funcao_atual': funcao_atual,
                    'funcao_atual_nome': funcao_atual.cargo_funcao.nome,
                }
            except UsuarioFuncao.DoesNotExist:
                # Se a função não existe mais, limpa a sessão
                request.session.pop('funcao_atual_id', None)
                request.session.pop('funcao_atual_nome', None)
    
    return {
        'funcao_atual': None,
        'funcao_atual_nome': None,
    } 

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
            cargo_funcao__nome='Administrador do Sistema'
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
            cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema']
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

def menu_permissions_processor(request):
    """
    Context processor para determinar as permissões de menu do usuário
    baseado no tipo de comissão (CPO/CPP)
    """
    if not request.user.is_authenticated:
        return {
            'menu_permissions': {
                'show_dashboard': False,
                'show_efetivo': False,
                'show_inativos': False,
                'show_usuarios': False,
                'show_permissoes': False,
                'show_fichas_oficiais': False,
                'show_fichas_pracas': False,
                'show_quadros_acesso': False,
                'show_quadros_fixacao': False,
                'show_almanaques': False,
                'show_promocoes': False,
                'show_calendarios': False,
                'show_comissoes': False,
                'show_meus_votos': False,
                'show_intersticios': False,
                'show_gerenciar_intersticios': False,
                'show_gerenciar_previsao': False,
                'show_administracao': False,
                'is_cpo': False,
                'is_cpp': False,
                'is_special': False,
                'is_consultor': False,
            }
        }
    
    # Verificar se usuário é usuário comum
    is_consultor = UsuarioFuncao.objects.filter(
        usuario=request.user,
        status='ATIVO',
        cargo_funcao__nome='Usuário'
    ).exists()
    
    # Se for usuário comum, acesso muito limitado - apenas suas próprias informações
    if is_consultor:
        return {
            'menu_permissions': {
                'show_dashboard': False,  # Não mostra dashboard para usuários
                'show_efetivo': False,
                'show_inativos': False,
                'show_usuarios': False,
                'show_permissoes': False,
                'show_fichas_oficiais': False,
                'show_fichas_pracas': False,
                'show_quadros_acesso': False,
                'show_quadros_fixacao': False,
                'show_almanaques': False,
                'show_promocoes': False,
                'show_calendarios': False,
                'show_comissoes': False,
                'show_meus_votos': False,
                'show_intersticios': False,
                'show_gerenciar_intersticios': False,
                'show_gerenciar_previsao': False,
                'show_administracao': False,
                'is_cpo': False,
                'is_cpp': False,
                'is_special': False,
                'is_consultor': True,
            }
        }
    
    # Verificar se usuário tem funções especiais
    funcoes_especiais = UsuarioFuncao.objects.filter(
        usuario=request.user,
        status='ATIVO',
        cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    ).exists()
    
    # Verificar se usuário é membro de comissão
    membros_comissao = MembroComissao.objects.filter(
        usuario=request.user,
        ativo=True,
        comissao__status='ATIVA'
    )
    
    is_cpo = membros_comissao.filter(comissao__tipo='CPO').exists()
    is_cpp = membros_comissao.filter(comissao__tipo='CPP').exists()
    
    # Se tem funções especiais, pode ver tudo
    if funcoes_especiais or request.user.is_superuser:
        return {
            'menu_permissions': {
                'show_dashboard': True,
                'show_efetivo': True,
                'show_inativos': True,
                'show_usuarios': True,
                'show_permissoes': True,
                'show_fichas_oficiais': True,
                'show_fichas_pracas': True,
                'show_quadros_acesso': True,
                'show_quadros_fixacao': True,
                'show_almanaques': True,
                'show_promocoes': True,
                'show_calendarios': True,
                'show_comissoes': True,
                'show_meus_votos': True,
                'show_intersticios': True,
                'show_gerenciar_intersticios': request.user.is_staff,
                'show_gerenciar_previsao': request.user.is_staff,
                'show_administracao': True,
                'is_cpo': False,
                'is_cpp': False,
                'is_special': True,
                'is_consultor': False,
            }
        }
    
    # Se é membro de comissão, aplicar restrições
    if is_cpo or is_cpp:
        return {
            'menu_permissions': {
                'show_dashboard': True,
                'show_efetivo': True,  # Pode ver efetivo, mas filtrado por tipo
                'show_inativos': False,
                'show_usuarios': False,
                'show_permissoes': False,
                'show_fichas_oficiais': is_cpo,  # CPO vê fichas de oficiais
                'show_fichas_pracas': is_cpp,    # CPP vê fichas de praças
                'show_quadros_acesso': False,
                'show_quadros_fixacao': True,    # TODOS os membros de comissão podem ver quadros de fixação
                'show_almanaques': True,         # TODOS os membros de comissão podem ver almanaques
                'show_promocoes': False,
                'show_calendarios': True,        # Membros de comissão podem ver calendários
                'show_comissoes': True,           # Pode ver comissões, mas filtradas
                'show_meus_votos': True,
                'show_intersticios': False,
                'show_gerenciar_intersticios': False,
                'show_gerenciar_previsao': False,
                'show_administracao': False,
                'is_cpo': is_cpo,
                'is_cpp': is_cpp,
                'is_special': False,
                'is_consultor': False,
            }
        }
    
    # Usuário comum - acesso limitado
    return {
        'menu_permissions': {
            'show_dashboard': True,
            'show_efetivo': True,
            'show_inativos': False,
            'show_usuarios': False,
            'show_permissoes': False,
            'show_fichas_oficiais': False,
            'show_fichas_pracas': False,
            'show_quadros_acesso': False,
            'show_quadros_fixacao': False,
            'show_almanaques': False,
            'show_promocoes': False,
            'show_calendarios': True,        # Usuários comuns podem visualizar calendários
            'show_comissoes': False,
            'show_meus_votos': False,
            'show_intersticios': False,
            'show_gerenciar_intersticios': False,
            'show_gerenciar_previsao': False,
            'show_administracao': False,
            'is_cpo': False,
            'is_cpp': False,
            'is_special': False,
            'is_consultor': False,
        }
    } 