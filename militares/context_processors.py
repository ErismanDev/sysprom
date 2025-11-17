from django.utils import timezone
from datetime import timedelta
from .models import SessaoComissao, MembroComissao, Viatura, ManutencaoViatura
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from functools import wraps
from django.conf import settings
from .models import UsuarioFuncaoMilitar
from .decorators import can_edit_militar

# Funções de permissão de submenu (sistema antigo removido)
def pode_visualizar_submenu(request, submenu):
    """Verifica se pode visualizar um submenu específico"""
    from .permissoes_simples import tem_permissao
    return tem_permissao(request.user, submenu.lower(), 'visualizar')

def tem_acesso_secao_promocoes(request):
    """Verifica se tem acesso à seção de promoções"""
    from .permissoes_simples import tem_permissao
    return (tem_permissao(request.user, 'promocoes', 'visualizar') or 
            tem_permissao(request.user, 'calendarios', 'visualizar') or
            tem_permissao(request.user, 'comissoes', 'visualizar') or
            tem_permissao(request.user, 'quadros_acesso', 'visualizar') or
            tem_permissao(request.user, 'quadros_fixacao', 'visualizar'))

# Importações para o sistema de permissões
from .permissoes_simples import (
    pode_visualizar_fichas_oficiais, pode_criar_fichas_oficiais, pode_editar_fichas_oficiais, pode_excluir_fichas_oficiais,
    pode_visualizar_fichas_pracas, pode_criar_fichas_pracas, pode_editar_fichas_pracas, pode_excluir_fichas_pracas,
    pode_visualizar_quadros_acesso, pode_criar_quadros_acesso, pode_editar_quadros_acesso, pode_excluir_quadros_acesso,
    pode_visualizar_quadros_fixacao, pode_criar_quadros_fixacao, pode_editar_quadros_fixacao, pode_excluir_quadros_fixacao,
    pode_visualizar_almanaques, pode_criar_almanaques, pode_editar_almanaques, pode_excluir_almanaques,
    pode_visualizar_promocoes, pode_criar_promocoes, pode_editar_promocoes, pode_excluir_promocoes,
    pode_visualizar_calendarios, pode_criar_calendarios, pode_editar_calendarios, pode_excluir_calendarios,
    pode_visualizar_comissoes, pode_criar_comissoes, pode_editar_comissoes, pode_excluir_comissoes,
    pode_visualizar_lotacoes, pode_criar_lotacoes, pode_editar_lotacoes, pode_excluir_lotacoes,
    pode_gerenciar_usuarios, pode_gerenciar_permissoes, pode_acessar_logs, pode_gerenciar_medalhas,
    tem_acesso_total_secao_promocoes
)

from .permissoes_militares import (
    pode_editar_militares,
    pode_editar_fichas_conceito,
    pode_gerenciar_quadros_vagas,
    pode_gerenciar_comissoes,
    pode_assinar_documentos,
    pode_gerenciar_usuarios,
    pode_acessar_relatorios,
    pode_acessar_promocoes,
    pode_visualizar_punicoes_elogios,
    tem_funcao_comissao_promocoes,
    tem_apenas_funcoes_comissao_cpo_cpp,
    tem_funcao_ativa_comissao_cpo_cpp,
    obter_sessao_ativa_usuario
)

from .permissoes_niveis import (
    pode_gerenciar_militares, pode_editar_militares, pode_excluir_militares,
    pode_gerenciar_usuarios, pode_gerenciar_funcoes, pode_gerenciar_permissoes,
    pode_acessar_relatorios, pode_acessar_dashboard, obter_nivel_hierarquico_usuario
)

class MenuPermissions:
    """
    Classe para encapsular as permissões de menu, permitindo acesso tanto por atributo quanto por chave
    """
    def __init__(self, permissions_dict):
        self._permissions = permissions_dict
    
    def __getattr__(self, name):
        return self._permissions.get(name, False)
    
    def __getitem__(self, key):
        return self._permissions.get(key, False)
    
    def get(self, key, default=False):
        return self._permissions.get(key, default)
    
    def __contains__(self, key):
        return key in self._permissions
    
    def __iter__(self):
        return iter(self._permissions)
    
    def keys(self):
        return self._permissions.keys()
    
    def items(self):
        return self._permissions.items()

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

def chat_processor(request):
    """Context processor para disponibilizar contagem de mensagens de chat não lidas"""
    if request.user.is_authenticated:
        from .models import Chat
        from .permissoes_militares import tem_funcao_restrita
        
        # Verificar se usuário tem função restrita (não pode usar chat)
        tem_funcao_restrita_user = tem_funcao_restrita(request.user)
        
        if not tem_funcao_restrita_user:
            chats = Chat.obter_chats_usuario(request.user)
            total_nao_lidas = sum(chat.contar_mensagens_nao_lidas(request.user) for chat in chats)
        else:
            total_nao_lidas = 0
        
        return {
            'total_chat_nao_lidas': total_nao_lidas,
            'pode_usar_chat': not tem_funcao_restrita_user,
        }
    return {
        'total_chat_nao_lidas': 0,
        'pode_usar_chat': False,
    }

def funcao_atual_processor(request):
    """
    Context processor para disponibilizar a função atual em todos os templates
    """
    if request.user.is_authenticated and hasattr(request, 'session'):
        funcao_atual_id = request.session.get('funcao_atual_id')
        if funcao_atual_id:
            try:
                from .models import UsuarioFuncaoMilitar
                funcao_atual = UsuarioFuncaoMilitar.objects.select_related('funcao_militar').get(
                    id=funcao_atual_id,
                    usuario=request.user,
                    ativo=True
                )
                return {
                    'funcao_atual': funcao_atual,
                    'funcao_atual_nome': funcao_atual.funcao_militar.nome,
                }
            except UsuarioFuncaoMilitar.DoesNotExist:
                # Se a função não existe mais, limpa a sessão
                if hasattr(request, 'session'):
                    request.session.pop('funcao_atual_id', None)
                    request.session.pop('funcao_atual_nome', None)
    
    return {
        'funcao_atual': None,
        'funcao_atual_nome': None,
    }

def sessao_ativa_processor(request):
    """
    Context processor para disponibilizar a sessão ativa do usuário em todos os templates
    """
    if request.user.is_authenticated:
        # Superusuários e Administradores do Sistema não precisam de sessão militar
        if request.user.is_superuser:
            return {
                'sessao_ativa': None,
            }
        
        # Verificar se é usuário master
        from .models import UsuarioMaster
        if UsuarioMaster.objects.filter(
            username=request.user.username,
            ativo=True
        ).exists():
            return {
                'sessao_ativa': None,
            }
        
        # Verificar se é Administrador do Sistema
        from .models import UsuarioFuncaoMilitar
        tem_funcao_admin = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Administrador do Sistema', 'Administrador']
        ).exists()
        
        if tem_funcao_admin:
            return {
                'sessao_ativa': None,
            }
        
        from .permissoes_militares import obter_sessao_ativa_usuario
        sessao_ativa = obter_sessao_ativa_usuario(request.user)
        return {
            'sessao_ativa': sessao_ativa,
        }
    
    return {
        'sessao_ativa': None,
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
        funcao_admin = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome='Administrador do Sistema'
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
        funcoes_comissao = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['CPO', 'CPP']
        ).exists()
        
        # Verificar se usuário tem funções especiais que permitem CRUD completo
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema']
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

def funcoes_usuario_processor(request):
    """
    Context processor para disponibilizar as funções do usuário em todos os templates
    Busca as funções diretamente do MilitarFuncao (funções exercidas da ficha)
    """
    if request.user.is_authenticated:
        from .models import UsuarioSessao, MilitarFuncao
        from .permissoes_hierarquicas import obter_nivel_acesso_usuario, obter_areas_acesso_usuario
        
        # Verificar se o usuário tem militar associado
        if hasattr(request.user, 'militar') and request.user.militar:
            # Buscar funções diretamente do MilitarFuncao
            todas_funcoes = MilitarFuncao.objects.filter(
                militar=request.user.militar,
                status='ATUAL',
                ativo=True
            ).select_related('funcao_militar').order_by('funcao_militar__nome')
            
            # Separar funções por tipo
            funcao_principal = todas_funcoes.filter(tipo_funcao='PRINCIPAL').first()
            funcoes_adicionais = todas_funcoes.filter(tipo_funcao='ADICIONAL')
            funcoes_temporarias = todas_funcoes.filter(tipo_funcao='TEMPORARIA')
            funcoes_comissao = todas_funcoes.filter(tipo_funcao='COMISSAO')
        else:
            # Se não tem militar associado, retornar vazio
            todas_funcoes = MilitarFuncao.objects.none()
            funcao_principal = None
            funcoes_adicionais = MilitarFuncao.objects.none()
            funcoes_temporarias = MilitarFuncao.objects.none()
            funcoes_comissao = MilitarFuncao.objects.none()
        
        # Buscar função atual (sessão ativa)
        funcao_atual = None
        try:
            sessao_ativa = UsuarioSessao.objects.filter(
                usuario=request.user,
                ativo=True
            ).select_related('funcao_militar_usuario__funcao_militar').first()
            
            if sessao_ativa:
                funcao_atual = sessao_ativa.funcao_militar_usuario
        except:
            pass
        
        # Obter informações de acesso hierárquico
        nivel_acesso = obter_nivel_acesso_usuario(request.user)
        areas_acesso = obter_areas_acesso_usuario(request.user)
        
        return {
            'funcoes_usuario': todas_funcoes,  # Agora retorna MilitarFuncao diretamente
            'funcao_principal': funcao_principal,
            'funcoes_adicionais': funcoes_adicionais,
            'funcoes_temporarias': funcoes_temporarias,
            'funcoes_comissao': funcoes_comissao,
            'funcao_atual': funcao_atual,
            'nivel_acesso': nivel_acesso,
            'areas_acesso': areas_acesso,
        }
    
    return {
        'funcoes_usuario': [],
        'funcao_principal': None,
        'funcoes_adicionais': [],
        'funcoes_temporarias': [],
        'funcoes_comissao': [],
        'funcao_atual': None,
        'nivel_acesso': None,
        'areas_acesso': [],
    }

def menu_permissions_processor(request):
    """
    Context processor para determinar as permissões de menu do usuário
    baseado no sistema de permissões granulares por função militar
    """
    if not request.user.is_authenticated:
        return {
            'menu_permissions': MenuPermissions({
                'show_dashboard': False,
                'show_efetivo': False,
                'show_ativos': False,
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
                'show_logs': False,
                'show_medalhas': False,
                'show_lotacoes': False,
                'show_elegiveis': False,
                'show_propostas': False,
                'show_medalhas_concessoes': False,
                'show_medalhas_propostas': False,
                'show_publicacoes': False,
                'show_notas': False,
                'show_boletins_ostensivos': False,
                'show_boletins_reservados': False,
                'show_boletins_especiais': False,
                'show_avisos': False,
                'show_ordens_servico': False,
                'show_viaturas': False,
                'show_viaturas_submenu': False,
                'show_equipamentos_operacionais': False,
                'show_equipamentos_operacionais_combustivel': False,
                'show_equipamentos_operacionais_manutencoes': False,
                'show_equipamentos_operacionais_trocas_oleo': False,
                'show_equipamentos_operacionais_tempos_uso': False,
                'show_controle_combustivel': False,
                'show_manutencoes': False,
                'show_trocas_oleo': False,
                'show_licenciamentos': False,
                'show_rodagens': False,
                'show_painel_guarda': False,
                'show_averbacoes': False,
                'show_material_belico': False,
                'show_bens_moveis': False,
                'show_almoxarifado': False,
                'show_almoxarifado_requisicoes': False,
                'show_processos': False,
                'show_armas_instituicao': False,
                'show_armas_particulares': False,
                'show_cautelas_armas': False,
                'show_controle_movimentacoes': False,
                'show_controle_municao': False,
                'show_cautelas_municoes': False,
                'show_afastamentos': False,
                'show_ferias': False,
            })
        }
    
    # Superusuários têm acesso total
    if request.user.is_superuser:
        return {
            'menu_permissions': MenuPermissions({
                'show_dashboard': True,
                'show_efetivo': True,
                'show_ativos': True,
                'show_inativos': True,
                'show_elogios': True,
                'show_elogios_oficiais': True,
                'show_elogios_pracas': True,
                'show_punicoes': True,
                'show_punicoes_oficiais': True,
                'show_punicoes_pracas': True,
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
                'show_gerenciar_intersticios': True,
                'show_gerenciar_previsao': True,
                'show_administracao': True,
                'show_logs': True,
                'show_medalhas': True,
                'show_lotacoes': True,
                'show_averbacoes': True,
                'show_elegiveis': True,
                'show_propostas': True,
                'show_medalhas_concessoes': True,
                'show_medalhas_propostas': True,
                'show_publicacoes': True,
                'show_notas': True,
                'show_boletins_ostensivos': True,
                'show_boletins_reservados': True,
                'show_boletins_especiais': True,
                'show_avisos': True,
                'show_ordens_servico': True,
                'show_viaturas': True,
                'show_viaturas_submenu': True,
                'show_controle_combustivel': True,
                'show_manutencoes': True,
                'show_trocas_oleo': True,
                'show_licenciamentos': True,
                'show_rodagens': True,
                'show_painel_guarda': True,
                'show_material_belico': True,
                'show_bens_moveis': True,
                'show_almoxarifado': True,
                'show_almoxarifado_requisicoes': True,
                'show_processos': True,
                'show_armas_instituicao': True,
                'show_armas_particulares': True,
                'show_cautelas_armas': True,
                'show_controle_movimentacoes': True,
                'show_controle_municao': True,
                'show_cautelas_municoes': True,
                'show_planejadas': True,
                'show_operador_planejadas': True,
                'show_fiscal_planejadas': True,
                'show_liquidacao': True,
                'show_notas': True,
                'show_afastamentos': True,
                'show_ferias': True,
                # Permissões específicas de ações
                'MILITARES_VISUALIZAR': True,
                'MILITARES_CRIAR': True,
                'MILITARES_EDITAR': True,
                'MILITARES_EXCLUIR': True,
                'MILITARES_TRANSFERIR': True,
                'MILITARES_PROMOVER': True,
                'MILITARES_INATIVAR': True,
                'MILITARES_FICHA_CONCEITO': True,
                'MILITARES_EXPORTAR': True,
                'MILITARES_DASHBOARD': True,
                'MILITARES_REORDENAR': True,
                'INATIVOS_VISUALIZAR': True,
                'INATIVOS_EDITAR': True,
                'INATIVOS_EXCLUIR': True,
                'INATIVOS_REATIVAR': True,
                'LOTACOES_VISUALIZAR': True,
                'LOTACOES_CRIAR': True,
                'LOTACOES_EDITAR': True,
                'LOTACOES_EXCLUIR': True,
                'QUADROS_ACESSO_VISUALIZAR': True,
                'QUADROS_ACESSO_CRIAR': True,
                'QUADROS_ACESSO_EDITAR': True,
                'QUADROS_ACESSO_EXCLUIR': True,
                'QUADROS_ACESSO_ASSINAR': True,
                'QUADROS_ACESSO_HOMOLOGAR': True,
                'QUADROS_ACESSO_DESHOMOLOGAR': True,
                'QUADROS_ACESSO_ELABORAR': True,
                'QUADROS_ACESSO_REGENERAR': True,
                'QUADROS_ACESSO_GERAR_PDF': True,
                'QUADROS_FIXACAO_VISUALIZAR': True,
                'QUADROS_FIXACAO_CRIAR': True,
                'QUADROS_FIXACAO_EDITAR': True,
                'QUADROS_FIXACAO_EXCLUIR': True,
                'COMISSOES_VISUALIZAR': True,
                'COMISSOES_CRIAR': True,
                'COMISSOES_EDITAR': True,
                'COMISSOES_EXCLUIR': True,
                'COMISSOES_OFICIAIS_VISUALIZAR': True,
                'COMISSOES_OFICIAIS_CRIAR': True,
                'COMISSOES_OFICIAIS_EDITAR': True,
                'COMISSOES_OFICIAIS_EXCLUIR': True,
                'COMISSOES_PRACAS_VISUALIZAR': True,
                'COMISSOES_PRACAS_CRIAR': True,
                'COMISSOES_PRACAS_EDITAR': True,
                'COMISSOES_PRACAS_EXCLUIR': True,
                'PUBLICACOES_VISUALIZAR': True,
                'PUBLICACOES_CRIAR': True,
                'PUBLICACOES_EDITAR': True,
                'PUBLICACOES_EXCLUIR': True,
                'PUBLICACOES_PUBLICAR': True,
            })
        }
    
    # Obter permissões baseadas no sistema granular
    from .permissoes_sistema import tem_permissao
    from .models import UsuarioFuncaoMilitar, FuncaoMenuConfig
    from .permissoes_militares import obter_nivel_acesso_usuario, obter_sessao_ativa_usuario
    from .permissoes_niveis import obter_nivel_hierarquico_usuario
    from .permissoes_simples import tem_acesso_total_secao_promocoes
    
    # Obter nível de acesso do usuário
    nivel_acesso = obter_nivel_acesso_usuario(request.user)
    
    # Se não tem sessão ativa, usar permissões granulares das funções ativas
    if not nivel_acesso or nivel_acesso == 'NENHUM':
        # Continuar para a lógica de permissões granulares abaixo
        pass
    
    nivel_usuario = obter_nivel_hierarquico_usuario(request.user)
    
    # Obter a função ativa na sessão do usuário
    sessao_ativa = obter_sessao_ativa_usuario(request.user)
    
    if sessao_ativa and sessao_ativa.funcao_militar_usuario:
        # Usar as configurações de menu da função ativa
        funcao_ativa = sessao_ativa.funcao_militar_usuario.funcao_militar
        funcao_usuario = sessao_ativa.funcao_militar_usuario
        
        # Obter permissões da função - get_menu_permissions() já mapeia as permissões granulares
        menu_permissions_dict = funcao_ativa.get_menu_permissions()
        
        # Garantir que temos um dicionário mutável
        # O método get_menu_permissions() retorna um dicionário diretamente
        if isinstance(menu_permissions_dict, dict):
            menu_permissions = menu_permissions_dict.copy()
        elif hasattr(menu_permissions_dict, '_permissions'):
            # Se for um objeto MenuPermissions, extrair o dicionário interno
            menu_permissions = menu_permissions_dict._permissions.copy()
        elif hasattr(menu_permissions_dict, '__dict__'):
            menu_permissions = dict(menu_permissions_dict.__dict__)
        else:
            # Tentar converter para dicionário
            try:
                menu_permissions = dict(menu_permissions_dict) if menu_permissions_dict else {}
            except:
                menu_permissions = {}
        
        # Garantir que todas as chaves de menu existam (inicializar com False se não existirem)
        chaves_menu = [
            'show_dashboard', 'show_efetivo', 'show_ativos', 'show_inativos', 'show_lotacoes', 'show_averbacoes',
            'show_afastamentos', 'show_ferias', 'show_viaturas', 'show_viaturas_submenu', 'show_controle_combustivel',
            'show_manutencoes', 'show_trocas_oleo', 'show_licenciamentos', 'show_rodagens', 'show_painel_guarda',
            'show_equipamentos_operacionais', 'show_equipamentos_operacionais_combustivel',
            'show_equipamentos_operacionais_manutencoes', 'show_equipamentos_operacionais_trocas_oleo',
            'show_equipamentos_operacionais_tempos_uso', 'show_material_belico', 'show_bens_moveis',
            'show_almoxarifado', 'show_almoxarifado_requisicoes', 'show_processos', 'show_armas_instituicao',
            'show_armas_particulares', 'show_cautelas_armas', 'show_controle_movimentacoes', 'show_controle_municao',
            'show_cautelas_municoes', 'show_elogios', 'show_elogios_oficiais', 'show_elogios_pracas',
            'show_punicoes', 'show_punicoes_oficiais', 'show_punicoes_pracas', 'show_publicacoes', 'show_notas',
            'show_boletins_ostensivos', 'show_boletins_reservados', 'show_boletins_especiais', 'show_avisos',
            'show_ordens_servico', 'show_escalas', 'show_escalas_lista', 'show_escalas_configuracao',
            'show_escalas_banco_horas', 'show_escalas_operacoes', 'show_planejadas', 'show_operador_planejadas',
            'show_fiscal_planejadas', 'show_liquidacao', 'show_medalhas', 'show_secao_promocoes',
            'show_fichas_oficiais', 'show_fichas_pracas', 'show_quadros_acesso', 'show_quadros_fixacao',
            'show_almanaques', 'show_promocoes', 'show_calendarios', 'show_comissoes', 'show_meus_votos',
            'show_intersticios', 'show_gerenciar_intersticios', 'show_gerenciar_previsao',
            'show_medalhas_concessoes', 'show_medalhas_propostas', 'show_elegiveis', 'show_propostas',
            'show_configuracoes', 'show_usuarios', 'show_permissoes', 'show_logs', 'show_titulos_publicacao', 'show_administracao'
        ]
        
        for chave in chaves_menu:
            if chave not in menu_permissions:
                menu_permissions[chave] = False
        
        # Aplicar permissões granulares adicionais que podem não estar no get_menu_permissions()
        # (para garantir compatibilidade com permissões antigas)
        from .models import PermissaoFuncao
        permissoes_granulares = PermissaoFuncao.objects.filter(
            funcao_militar=funcao_ativa,
            ativo=True
        )
        
        # Mapear permissões granulares para permissões de menu (complementar ao get_menu_permissions)
        # IMPORTANTE: Este mapeamento complementa o get_menu_permissions() para garantir que todas as permissões sejam aplicadas
        for permissao in permissoes_granulares:
            # Verificar se a permissão tem acesso VISUALIZAR (para menus)
            if permissao.acesso == 'VISUALIZAR':
                if permissao.modulo == 'MENU_DASHBOARD':
                    menu_permissions['show_dashboard'] = True
                elif permissao.modulo == 'MENU_EFETIVO':
                    menu_permissions['show_efetivo'] = True
                elif permissao.modulo == 'MENU_AFASTAMENTOS':
                    menu_permissions['show_afastamentos'] = True
                elif permissao.modulo == 'MENU_FERIAS':
                    menu_permissions['show_ferias'] = True
                elif permissao.modulo == 'MENU_VIATURAS':
                    menu_permissions['show_viaturas'] = True
                elif permissao.modulo == 'MENU_PUBLICACOES':
                    menu_permissions['show_publicacoes'] = True
                elif permissao.modulo == 'MENU_ESCALAS':
                    menu_permissions['show_escalas'] = True
                elif permissao.modulo == 'MENU_PLANEJADAS':
                    menu_permissions['show_planejadas'] = True
                elif permissao.modulo == 'MENU_MEDALHAS':
                    menu_permissions['show_medalhas'] = True
                elif permissao.modulo == 'MENU_SECAO_PROMOCOES':
                    menu_permissions['show_secao_promocoes'] = True
                elif permissao.modulo == 'MENU_CONFIGURACOES':
                    menu_permissions['show_administracao'] = True
                    menu_permissions['show_configuracoes'] = True
                elif permissao.modulo == 'SUBMENU_ATIVOS':
                    menu_permissions['show_ativos'] = True
                elif permissao.modulo == 'SUBMENU_INATIVOS':
                    menu_permissions['show_inativos'] = True
                elif permissao.modulo == 'SUBMENU_LOTACOES':
                    menu_permissions['show_lotacoes'] = True
                elif permissao.modulo == 'SUBMENU_AVERBACOES':
                    menu_permissions['show_averbacoes'] = True
                elif permissao.modulo == 'MENU_FROTA':
                    menu_permissions['show_viaturas'] = True
                elif permissao.modulo == 'MENU_EQUIPAMENTOS_OPERACIONAIS':
                    menu_permissions['show_equipamentos_operacionais'] = True
                elif permissao.modulo == 'SUBMENU_VIATURAS':
                    menu_permissions['show_viaturas_submenu'] = True
                elif permissao.modulo == 'SUBMENU_EQUIPAMENTOS_OPERACIONAIS':
                    menu_permissions['show_equipamentos_operacionais'] = True
                elif permissao.modulo == 'SUBMENU_EQUIPAMENTOS_OPERACIONAIS_COMBUSTIVEL':
                    menu_permissions['show_equipamentos_operacionais_combustivel'] = True
                elif permissao.modulo == 'SUBMENU_EQUIPAMENTOS_OPERACIONAIS_MANUTENCOES':
                    menu_permissions['show_equipamentos_operacionais_manutencoes'] = True
                elif permissao.modulo == 'SUBMENU_EQUIPAMENTOS_OPERACIONAIS_TROCAS_OLEO':
                    menu_permissions['show_equipamentos_operacionais_trocas_oleo'] = True
                elif permissao.modulo == 'SUBMENU_EQUIPAMENTOS_OPERACIONAIS_TEMPOS_USO':
                    menu_permissions['show_equipamentos_operacionais_tempos_uso'] = True
                elif permissao.modulo == 'SUBMENU_CONTROLE_COMBUSTIVEL':
                    menu_permissions['show_controle_combustivel'] = True
                elif permissao.modulo == 'SUBMENU_MANUTENCOES':
                    menu_permissions['show_manutencoes'] = True
                elif permissao.modulo == 'SUBMENU_TROCAS_OLEO':
                    menu_permissions['show_trocas_oleo'] = True
                elif permissao.modulo == 'SUBMENU_LICENCIAMENTOS':
                    menu_permissions['show_licenciamentos'] = True
                elif permissao.modulo == 'SUBMENU_RODAGENS':
                    menu_permissions['show_rodagens'] = True
                elif permissao.modulo == 'SUBMENU_PAINEL_GUARDA':
                    menu_permissions['show_painel_guarda'] = True
                elif permissao.modulo == 'MENU_MATERIAL_BELICO':
                    menu_permissions['show_material_belico'] = True
                elif permissao.modulo == 'MENU_BENS_MOVEIS':
                    menu_permissions['show_bens_moveis'] = True
                elif permissao.modulo == 'MENU_ALMOXARIFADO':
                    menu_permissions['show_almoxarifado'] = True
                elif permissao.modulo == 'ALMOXARIFADO':
                    menu_permissions['show_almoxarifado'] = True
                elif permissao.modulo == 'SUBMENU_ALMOXARIFADO_ITENS':
                    menu_permissions['show_almoxarifado'] = True
                elif permissao.modulo == 'SUBMENU_ALMOXARIFADO_ENTRADAS':
                    menu_permissions['show_almoxarifado'] = True
                elif permissao.modulo == 'SUBMENU_ALMOXARIFADO_SAIDAS':
                    menu_permissions['show_almoxarifado'] = True
                elif permissao.modulo == 'SUBMENU_ALMOXARIFADO_REQUISICOES':
                    menu_permissions['show_almoxarifado'] = True
                    menu_permissions['show_almoxarifado_requisicoes'] = True
                elif permissao.modulo == 'MENU_PROCESSOS':
                    menu_permissions['show_processos'] = True
                elif permissao.modulo == 'SUBMENU_ARMAS_INSTITUICAO':
                    menu_permissions['show_armas_instituicao'] = True
                elif permissao.modulo == 'SUBMENU_ARMAS_PARTICULARES':
                    menu_permissions['show_armas_particulares'] = True
                elif permissao.modulo == 'SUBMENU_CAUTELAS_ARMAS':
                    menu_permissions['show_cautelas_armas'] = True
                elif permissao.modulo == 'SUBMENU_CONTROLE_MOVIMENTACOES':
                    menu_permissions['show_controle_movimentacoes'] = True
                elif permissao.modulo == 'SUBMENU_CONTROLE_MUNICAO':
                    menu_permissions['show_controle_municao'] = True
                elif permissao.modulo == 'SUBMENU_CAUTELAS_MUNICOES':
                    menu_permissions['show_cautelas_municoes'] = True
                # Submenus Efetivo adicionais
                elif permissao.modulo == 'MENU_EFETIVO_ELOGIOS':
                    menu_permissions['show_efetivo_elogios'] = True
                elif permissao.modulo == 'MENU_EFETIVO_PUNICOES':
                    menu_permissions['show_efetivo_punicoes'] = True
                # Menu Elogios/Punições separados
                elif permissao.modulo == 'MENU_ELOGIOS':
                    menu_permissions['show_elogios'] = True
                elif permissao.modulo == 'SUBMENU_ELOGIOS_OFICIAIS':
                    menu_permissions['show_elogios_oficiais'] = True
                elif permissao.modulo == 'SUBMENU_ELOGIOS_PRACAS':
                    menu_permissions['show_elogios_pracas'] = True
                elif permissao.modulo == 'MENU_PUNICOES':
                    menu_permissions['show_punicoes'] = True
                elif permissao.modulo == 'SUBMENU_PUNICOES_OFICIAIS':
                    menu_permissions['show_punicoes_oficiais'] = True
                elif permissao.modulo == 'SUBMENU_PUNICOES_PRACAS':
                    menu_permissions['show_punicoes_pracas'] = True
                elif permissao.modulo == 'SUBMENU_NOTAS':
                    menu_permissions['show_notas'] = True
                elif permissao.modulo == 'SUBMENU_NOTAS_RESERVADAS':
                    menu_permissions['show_notas_reservadas'] = True
                elif permissao.modulo == 'SUBMENU_BOLETINS_OSTENSIVOS':
                    menu_permissions['show_boletins_ostensivos'] = True
                elif permissao.modulo == 'SUBMENU_BOLETINS_RESERVADOS':
                    menu_permissions['show_boletins_reservados'] = True
                elif permissao.modulo == 'SUBMENU_BOLETINS_ESPECIAIS':
                    menu_permissions['show_boletins_especiais'] = True
                elif permissao.modulo == 'SUBMENU_AVISOS':
                    menu_permissions['show_avisos'] = True
                elif permissao.modulo == 'SUBMENU_ORDENS_SERVICO':
                    menu_permissions['show_ordens_servico'] = True
                elif permissao.modulo == 'SUBMENU_ESCALAS_LISTA':
                    menu_permissions['show_escalas_lista'] = True
                elif permissao.modulo == 'SUBMENU_ESCALAS_CONFIGURACAO':
                    menu_permissions['show_escalas_configuracao'] = True
                elif permissao.modulo == 'SUBMENU_ESCALAS_BANCO_HORAS':
                    menu_permissions['show_escalas_banco_horas'] = True
                elif permissao.modulo == 'SUBMENU_ESCALAS_OPERACOES':
                    menu_permissions['show_escalas_operacoes'] = True
                elif permissao.modulo == 'SUBMENU_PLANEJADAS':
                    menu_permissions['show_planejadas'] = True
                elif permissao.modulo == 'SUBMENU_OPERADOR_PLANEJADAS':
                    menu_permissions['show_operador_planejadas'] = True
                    # Operadores de planejadas também podem ver notas para copiar links
                    menu_permissions['show_notas'] = True
                elif permissao.modulo == 'SUBMENU_FISCAL_PLANEJADAS':
                    menu_permissions['show_fiscal_planejadas'] = True
                elif permissao.modulo == 'SUBMENU_LIQUIDACAO':
                    menu_permissions['show_liquidacao'] = True
                # Submenus de Seção de Promoções
                elif permissao.modulo == 'SUBMENU_FICHAS_OFICIAIS':
                    menu_permissions['show_fichas_oficiais'] = True
                elif permissao.modulo == 'SUBMENU_FICHAS_PRACAS':
                    menu_permissions['show_fichas_pracas'] = True
                elif permissao.modulo == 'SUBMENU_QUADROS_ACESSO':
                    menu_permissions['show_quadros_acesso'] = True
                elif permissao.modulo == 'SUBMENU_QUADROS_FIXACAO':
                    menu_permissions['show_quadros_fixacao'] = True
                elif permissao.modulo == 'SUBMENU_ALMANAQUES':
                    menu_permissions['show_almanaques'] = True
                elif permissao.modulo == 'SUBMENU_PROMOCOES':
                    menu_permissions['show_promocoes'] = True
                elif permissao.modulo == 'SUBMENU_CALENDARIOS':
                    menu_permissions['show_calendarios'] = True
                elif permissao.modulo == 'SUBMENU_COMISSOES':
                    menu_permissions['show_comissoes'] = True
                elif permissao.modulo == 'SUBMENU_MEUS_VOTOS':
                    menu_permissions['show_meus_votos'] = True
                elif permissao.modulo == 'SUBMENU_INTERSTICIOS':
                    menu_permissions['show_intersticios'] = True
                elif permissao.modulo == 'SUBMENU_GERENCIAR_INTERSTICIOS':
                    menu_permissions['show_gerenciar_intersticios'] = True
                elif permissao.modulo == 'SUBMENU_GERENCIAR_PREVISAO':
                    menu_permissions['show_gerenciar_previsao'] = True
                elif permissao.modulo == 'SUBMENU_MEDALHAS_CONCESSOES':
                    menu_permissions['show_medalhas_concessoes'] = True
                elif permissao.modulo == 'SUBMENU_MEDALHAS_PROPOSTAS':
                    menu_permissions['show_medalhas_propostas'] = True
                elif permissao.modulo == 'SUBMENU_ELEGIVEIS':
                    menu_permissions['show_elegiveis'] = True
                elif permissao.modulo == 'SUBMENU_PROPOSTAS':
                    menu_permissions['show_propostas'] = True
                # Submenus de Configurações
                elif permissao.modulo == 'SUBMENU_USUARIOS':
                    menu_permissions['show_usuarios'] = True
                elif permissao.modulo == 'SUBMENU_PERMISSOES':
                    menu_permissions['show_permissoes'] = True
                elif permissao.modulo == 'SUBMENU_LOGS':
                    menu_permissions['show_logs'] = True
                elif permissao.modulo == 'SUBMENU_ADMINISTRACAO':
                    menu_permissions['show_administracao'] = True
                elif permissao.modulo == 'SUBMENU_TITULOS_PUBLICACAO':
                    menu_permissions['show_titulos_publicacao'] = True
            # Mapear permissões granulares para ações específicas (não apenas VISUALIZAR)
            elif permissao.modulo == 'INATIVOS' and permissao.acesso == 'REATIVAR':
                menu_permissions['INATIVOS_REATIVAR'] = True
            elif permissao.modulo == 'INATIVOS' and permissao.acesso == 'VISUALIZAR':
                menu_permissions['INATIVOS_VISUALIZAR'] = True
            elif permissao.modulo == 'INATIVOS' and permissao.acesso == 'EDITAR':
                menu_permissions['INATIVOS_EDITAR'] = True
            elif permissao.modulo == 'INATIVOS' and permissao.acesso == 'EXCLUIR':
                menu_permissions['INATIVOS_EXCLUIR'] = True
        
        # GARANTIR QUE O MENU PESSOAL SEMPRE APAREÇA
        # Quando uma função não tem permissões granulares selecionadas, 
        # o usuário deve ver apenas a página inicial e as fichas pessoais sem CRUD
        if hasattr(request.user, 'militar') and request.user.militar:
            menu_permissions['show_pessoal'] = True
            menu_permissions['show_minhas_informacoes'] = True
            menu_permissions['show_minha_ficha_cadastro'] = True
            menu_permissions['show_minha_ficha_conceito_oficial'] = True
            menu_permissions['show_minha_ficha_conceito_praca'] = True
            menu_permissions['show_criar_ficha_conceito_oficial'] = True
            menu_permissions['show_criar_ficha_conceito_praca'] = True
        
        # REMOVIDO: Bypass de permissões granulares para acesso TOTAL
        # O sistema agora deve respeitar as permissões granulares mesmo com acesso TOTAL
        # As permissões granulares controlam a interface (menus, submenus, botões)
        # O acesso TOTAL controla apenas o acesso aos dados (hierarquia)
        # As permissões granulares devem ser configuradas explicitamente
        
        elif funcao_usuario.nivel_acesso == 'ORGAO':
            # Nível ÓRGÃO: acesso ao órgão + toda sua descendência
            # Aplicar permissões básicas de visualização e gestão limitada
            menu_permissions.update({
                'show_dashboard': True,
                'show_efetivo': True,
                'show_ativos': True,
                'show_inativos': True,
                'show_lotacoes': True,
                'show_averbacoes': True,
                'show_publicacoes': True,
                'show_notas': True,
                'show_boletins_ostensivos': True,
                'show_avisos': True,
                'show_secao_promocoes': True,
                'show_fichas_oficiais': True,
                'show_fichas_pracas': True,
                'show_quadros_acesso': True,
                'show_medalhas': True,
                'show_medalhas_concessoes': True,
                'show_medalhas_propostas': True,
                
                # Permissões específicas de ações (limitadas)
                'MILITARES_VISUALIZAR': True,
                'MILITARES_EDITAR': True,
                'MILITARES_EXPORTAR': True,
                'MILITARES_DASHBOARD': True,
                'INATIVOS_VISUALIZAR': True,
                'LOTACOES_VISUALIZAR': True,
                'LOTACOES_EDITAR': True,
                'QUADROS_ACESSO_VISUALIZAR': True,
                'QUADROS_ACESSO_EDITAR': True,
                'PUBLICACOES_VISUALIZAR': True,
                'PUBLICACOES_EDITAR': True,
                'NOTAS_VISUALIZAR': True,
                'NOTAS_EDITAR': True,
                'BOLETINS_OSTENSIVOS_VISUALIZAR': True,
                'BOLETINS_OSTENSIVOS_EDITAR': True,
                'AVISOS_VISUALIZAR': True,
                'AVISOS_EDITAR': True,
                'MEDALHAS_VISUALIZAR': True,
                'MEDALHAS_EDITAR': True,
            })
            
        elif funcao_usuario.nivel_acesso == 'GRANDE_COMANDO':
            # Nível GRANDE_COMANDO: acesso ao grande comando + toda sua descendência
            # Aplicar permissões de gestão de grande comando
            menu_permissions.update({
                'show_dashboard': True,
                'show_efetivo': True,
                'show_ativos': True,
                'show_inativos': True,
                'show_lotacoes': True,
                'show_averbacoes': True,
                'show_publicacoes': True,
                'show_notas': True,
                'show_boletins_ostensivos': True,
                'show_avisos': True,
                'show_secao_promocoes': True,
                'show_fichas_oficiais': True,
                'show_fichas_pracas': True,
                'show_quadros_acesso': True,
                'show_medalhas': True,
                'show_medalhas_concessoes': True,
                'show_medalhas_propostas': True,
                
                # Permissões específicas de ações
                'MILITARES_VISUALIZAR': True,
                'MILITARES_CRIAR': True,
                'MILITARES_EDITAR': True,
                'MILITARES_EXPORTAR': True,
                'MILITARES_DASHBOARD': True,
                'INATIVOS_VISUALIZAR': True,
                'INATIVOS_EDITAR': True,
                'LOTACOES_VISUALIZAR': True,
                'LOTACOES_CRIAR': True,
                'LOTACOES_EDITAR': True,
                'QUADROS_ACESSO_VISUALIZAR': True,
                'QUADROS_ACESSO_CRIAR': True,
                'QUADROS_ACESSO_EDITAR': True,
                'PUBLICACOES_VISUALIZAR': True,
                'PUBLICACOES_CRIAR': True,
                'PUBLICACOES_EDITAR': True,
                'NOTAS_VISUALIZAR': True,
                'NOTAS_CRIAR': True,
                'NOTAS_EDITAR': True,
                'BOLETINS_OSTENSIVOS_VISUALIZAR': True,
                'BOLETINS_OSTENSIVOS_CRIAR': True,
                'BOLETINS_OSTENSIVOS_EDITAR': True,
                'AVISOS_VISUALIZAR': True,
                'AVISOS_CRIAR': True,
                'AVISOS_EDITAR': True,
                'MEDALHAS_VISUALIZAR': True,
                'MEDALHAS_CRIAR': True,
                'MEDALHAS_EDITAR': True,
            })
            
        elif funcao_usuario.nivel_acesso == 'UNIDADE':
            # Nível UNIDADE: acesso à unidade + toda sua descendência
            # Aplicar permissões de gestão de unidade
            menu_permissions.update({
                'show_dashboard': True,
                'show_efetivo': True,
                'show_ativos': True,
                'show_lotacoes': True,
                'show_averbacoes': True,
                'show_publicacoes': True,
                'show_notas': True,
                'show_boletins_ostensivos': True,
                'show_avisos': True,
                'show_medalhas': True,
                'show_medalhas_concessoes': True,
                'show_medalhas_propostas': True,
                
                # Permissões específicas de ações (limitadas à unidade)
                'MILITARES_VISUALIZAR': True,
                'MILITARES_EDITAR': True,
                'MILITARES_EXPORTAR': True,
                'MILITARES_DASHBOARD': True,
                'LOTACOES_VISUALIZAR': True,
                'LOTACOES_EDITAR': True,
                'PUBLICACOES_VISUALIZAR': True,
                'PUBLICACOES_EDITAR': True,
                'NOTAS_VISUALIZAR': True,
                'NOTAS_EDITAR': True,
                'BOLETINS_OSTENSIVOS_VISUALIZAR': True,
                'BOLETINS_OSTENSIVOS_EDITAR': True,
                'AVISOS_VISUALIZAR': True,
                'AVISOS_EDITAR': True,
                'MEDALHAS_VISUALIZAR': True,
                'MEDALHAS_EDITAR': True,
            })
            
        elif funcao_usuario.nivel_acesso == 'SUBUNIDADE':
            # Nível SUBUNIDADE: acesso à subunidade
            # Aplicar permissões básicas de visualização
            menu_permissions.update({
                'show_dashboard': True,
                'show_efetivo': True,
                'show_ativos': True,
                'show_publicacoes': True,
                'show_notas': True,
                'show_avisos': True,
                'show_medalhas': True,
                'show_medalhas_concessoes': True,
                'show_medalhas_propostas': True,
                
                # Permissões específicas de ações (apenas visualização)
                'MILITARES_VISUALIZAR': True,
                'MILITARES_EXPORTAR': True,
                'MILITARES_DASHBOARD': True,
                'PUBLICACOES_VISUALIZAR': True,
                'NOTAS_VISUALIZAR': True,
                'AVISOS_VISUALIZAR': True,
                'MEDALHAS_VISUALIZAR': True,
            })
            
        elif funcao_usuario.nivel_acesso == 'NENHUM':
            # Nível NENHUM: apenas página home e dados pessoais (sem edição)
            menu_permissions.update({
                # Acesso apenas à página home e dados pessoais
                'show_dashboard': False,      # Não tem acesso ao dashboard
                'show_efetivo': False,        # Não tem acesso ao efetivo
                'show_ativos': False,         # Não tem acesso aos ativos
                'show_inativos': False,       # Não tem acesso aos inativos
                'show_usuarios': False,       # Não tem acesso aos usuários
                'show_permissoes': False,     # Não tem acesso às permissões
                'show_fichas_oficiais': False, # Não tem acesso às fichas de oficiais
                'show_fichas_pracas': False,  # Não tem acesso às fichas de praças
                'show_quadros_acesso': False, # Não tem acesso aos quadros de acesso
                'show_quadros_fixacao': False, # Não tem acesso aos quadros de fixação
                'show_almanaques': False,     # Não tem acesso aos almanaques
                'show_promocoes': False,      # Não tem acesso às promoções
                'show_calendarios': False,    # Não tem acesso aos calendários
                'show_comissoes': False,      # Não tem acesso às comissões
                'show_meus_votos': False,     # Não tem acesso aos votos
                'show_intersticios': False,   # Não tem acesso aos interstícios
                'show_gerenciar_intersticios': False, # Não tem acesso ao gerenciar interstícios
                'show_gerenciar_previsao': False,     # Não tem acesso ao gerenciar previsão
                'show_administracao': False,  # Não tem acesso à administração
                'show_logs': False,           # Não tem acesso aos logs
                'show_medalhas': False,       # Não tem acesso às medalhas
                'show_lotacoes': False,       # Não tem acesso às lotações
                'show_averbacoes': False,      # Não tem acesso às averbações
                'show_elegiveis': False,      # Não tem acesso aos elegíveis
                'show_propostas': False,      # Não tem acesso às propostas
                'show_medalhas_concessoes': False, # Não tem acesso às concessões de medalhas
                'show_medalhas_propostas': False,  # Não tem acesso às propostas de medalhas
                'show_publicacoes': False,    # Não tem acesso às publicações
                'show_notas': False,          # Não tem acesso às notas
                'show_boletins_ostensivos': False,  # Não tem acesso aos boletins ostensivos
                'show_boletins_reservados': False,  # Não tem acesso aos boletins reservados
                'show_boletins_especiais': False,   # Não tem acesso aos boletins especiais
                'show_avisos': False,         # Não tem acesso aos avisos
                'show_ordens_servico': False, # Não tem acesso às ordens de serviço
                'show_escalas': False,        # Não tem acesso às escalas
                'show_configuracoes': False,  # Não tem acesso às configurações
                'show_relatorios': False,     # Não tem acesso aos relatórios
                'show_pessoal': True,         # Tem acesso aos dados pessoais
                
                # Apenas visualização dos dados pessoais
                'MILITARES_VISUALIZAR_PROPRIO': True,
                'MILITARES_EDITAR_PROPRIO': False,  # Não pode editar
                'MILITARES_EXPORTAR_PROPRIO': True,  # Pode exportar seus próprios dados
            })
        
        # Adicionar permissões específicas do usuário
        menu_permissions.update({
            'is_consultor': not pode_editar_militares(request.user),
            'funcao_ativa_nome': funcao_ativa.nome,
            'funcao_ativa_id': funcao_ativa.id,
        })
        
        # Debug: Log das permissões da função ativa (apenas em desenvolvimento)
        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            print(f"Menu permissions para {request.user.username} - Funcao: {funcao_ativa.nome}")
            print(f"   - Dashboard: {menu_permissions.get('show_dashboard', False)}")
            print(f"   - Efetivo: {menu_permissions.get('show_efetivo', False)}")
            print(f"   - Seção Promoções: {menu_permissions.get('show_secao_promocoes', False)}")
            print(f"   - Administração: {menu_permissions.get('show_administracao', False)}")
        
        return {
            'menu_permissions': MenuPermissions(menu_permissions)
        }
    
    # Usuários sem sessão ativa - usar permissões básicas (apenas menu pessoal)
    # O sistema deve funcionar baseado na função selecionada, não em todas as funções do usuário
    permissoes_basicas = {
        # Menus principais - todos False por padrão
        'show_dashboard': False,
        'show_efetivo': False,
        'show_publicacoes': False,
        'show_secao_promocoes': False,
        'show_medalhas': False,
        'show_configuracoes': False,
        'show_afastamentos': False,
        'show_ferias': False,
        'show_viaturas': False,
        'show_viaturas_submenu': False,
        'show_material_belico': False,
        'show_bens_moveis': False,
        'show_almoxarifado': False,
        'show_almoxarifado_requisicoes': False,
        'show_processos': False,
        
        # Submenus - Efetivo
        'show_ativos': False,
        'show_inativos': False,
        'show_lotacoes': False,
        'show_averbacoes': False,
        
        # Submenus - Frota
        'show_equipamentos_operacionais': False,
        'show_equipamentos_operacionais_combustivel': False,
        'show_equipamentos_operacionais_manutencoes': False,
        'show_equipamentos_operacionais_trocas_oleo': False,
        'show_equipamentos_operacionais_tempos_uso': False,
        'show_controle_combustivel': False,
        'show_manutencoes': False,
        'show_trocas_oleo': False,
        'show_licenciamentos': False,
        'show_rodagens': False,
        'show_painel_guarda': False,
        
        # Submenus - Material Bélico
        'show_armas_instituicao': False,
        'show_armas_particulares': False,
        'show_cautelas_armas': False,
        'show_controle_movimentacoes': False,
        'show_controle_municao': False,
        'show_cautelas_municoes': False,
        
        # Submenus - Publicações
        'show_notas': False,
        'show_boletins_ostensivos': False,
        'show_boletins_reservados': False,
        'show_boletins_especiais': False,
        'show_avisos': False,
        'show_ordens_servico': False,
        
        # Submenus - Seção de Promoções
        'show_fichas_oficiais': False,
        'show_fichas_pracas': False,
        'show_calendarios': False,
        'show_quadros_acesso': False,
        'show_quadros_fixacao': False,
        'show_comissoes': False,
        'show_meus_votos': False,
        'show_promocoes': False,
        'show_almanaques': False,
        
        # Submenus - Medalhas
        'show_medalhas_concessoes': False,
        'show_medalhas_propostas': False,
        'show_elegiveis': False,
        'show_propostas': False,
        
        # Submenus - Configurações
        'show_intersticios': False,
        'show_gerenciar_intersticios': False,
        'show_gerenciar_previsao': False,
        'show_usuarios': False,
        'show_permissoes': False,
        'show_logs': False,
        'show_titulos_publicacao': False,
        'show_administracao': False,
        
        'is_consultor': True,
        # Permissões específicas de ações - todas False por padrão
        'MILITARES_VISUALIZAR': False,
        'MILITARES_CRIAR': False,
        'MILITARES_EDITAR': False,
        'MILITARES_EXCLUIR': False,
        'MILITARES_TRANSFERIR': False,
        'MILITARES_PROMOVER': False,
        'MILITARES_INATIVAR': False,
        'MILITARES_FICHA_CONCEITO': False,
        'MILITARES_EXPORTAR': False,
        'MILITARES_DASHBOARD': False,
        'MILITARES_REORDENAR': False,
        'INATIVOS_VISUALIZAR': False,
        'INATIVOS_EDITAR': False,
        'INATIVOS_EXCLUIR': False,
        'INATIVOS_REATIVAR': False,
        'LOTACOES_VISUALIZAR': False,
        'LOTACOES_CRIAR': False,
        'LOTACOES_EDITAR': False,
        'LOTACOES_EXCLUIR': False,
        'QUADROS_ACESSO_VISUALIZAR': False,
        'QUADROS_ACESSO_CRIAR': False,
        'QUADROS_ACESSO_EDITAR': False,
        'QUADROS_ACESSO_EXCLUIR': False,
        'QUADROS_ACESSO_ASSINAR': False,
        'QUADROS_ACESSO_HOMOLOGAR': False,
        'QUADROS_ACESSO_DESHOMOLOGAR': False,
        'QUADROS_ACESSO_ELABORAR': False,
        'QUADROS_ACESSO_REGENERAR': False,
        'QUADROS_ACESSO_GERAR_PDF': False,
        'QUADROS_FIXACAO_VISUALIZAR': False,
        'QUADROS_FIXACAO_CRIAR': False,
        'QUADROS_FIXACAO_EDITAR': False,
        'QUADROS_FIXACAO_EXCLUIR': False,
        'COMISSOES_VISUALIZAR': False,
        'COMISSOES_CRIAR': False,
        'COMISSOES_EDITAR': False,
        'COMISSOES_EXCLUIR': False,
        'COMISSOES_OFICIAIS_VISUALIZAR': False,
        'COMISSOES_OFICIAIS_CRIAR': False,
        'COMISSOES_OFICIAIS_EDITAR': False,
        'COMISSOES_OFICIAIS_EXCLUIR': False,
        'COMISSOES_PRACAS_VISUALIZAR': False,
        'COMISSOES_PRACAS_CRIAR': False,
        'COMISSOES_PRACAS_EDITAR': False,
        'COMISSOES_PRACAS_EXCLUIR': False,
        'PUBLICACOES_VISUALIZAR': False,
        'PUBLICACOES_CRIAR': False,
        'PUBLICACOES_EDITAR': False,
        'PUBLICACOES_EXCLUIR': False,
        'PUBLICACOES_PUBLICAR': False,
    }
    
    # GARANTIR QUE O MENU PESSOAL SEMPRE APAREÇA
    # Quando uma função não tem permissões granulares selecionadas, 
    # o usuário deve ver apenas a página inicial e as fichas pessoais sem CRUD
    if hasattr(request.user, 'militar') and request.user.militar:
        permissoes_basicas['show_pessoal'] = True
        permissoes_basicas['show_minhas_informacoes'] = True
        permissoes_basicas['show_minha_ficha_cadastro'] = True
        permissoes_basicas['show_minha_ficha_conceito_oficial'] = True
        permissoes_basicas['show_minha_ficha_conceito_praca'] = True
        permissoes_basicas['show_criar_ficha_conceito_oficial'] = True
        permissoes_basicas['show_criar_ficha_conceito_praca'] = True
    
    return {
        'menu_permissions': MenuPermissions(permissoes_basicas)
    }


def revisoes_proximas_processor(request):
    """
    Context processor para alertar sobre viaturas próximas da revisão (faltando 100km ou menos).
    Apenas para usuários com acesso ao menu de frota.
    """
    alertas_revisao = []
    
    if not request.user.is_authenticated:
        return {
            'alertas_revisao': [],
            'total_alertas_revisao': 0
        }
    
    # Verificar se o usuário tem acesso ao menu de frota
    from .permissoes_simples import tem_permissao
    tem_acesso_frota = (
        request.user.is_superuser or
        tem_permissao(request.user, 'viaturas', 'visualizar')
    )
    
    if not tem_acesso_frota:
        return {
            'alertas_revisao': [],
            'total_alertas_revisao': 0
        }
    
    # Buscar todas as viaturas ativas
    viaturas = Viatura.objects.filter(ativo=True)
    
    for viatura in viaturas:
        # Buscar a última revisão da viatura que tenha próximo_km_revisao definido
        ultima_revisao = ManutencaoViatura.objects.filter(
            viatura=viatura,
            tipo_manutencao='REVISAO',
            proximo_km_revisao__isnull=False,
            ativo=True
        ).order_by('-data_manutencao', '-km_manutencao').first()
        
        if ultima_revisao and ultima_revisao.proximo_km_revisao:
            km_atual = viatura.km_atual
            km_proximo_revisao = ultima_revisao.proximo_km_revisao
            km_restantes = km_proximo_revisao - km_atual
            
            # Alerta se faltam 100km ou menos (incluindo valores negativos = já passou)
            if km_restantes <= 100:
                alertas_revisao.append({
                    'viatura': viatura,
                    'km_atual': km_atual,
                    'km_proximo_revisao': km_proximo_revisao,
                    'km_restantes': km_restantes,
                    'ultima_revisao': ultima_revisao,
                    'urgente': km_restantes <= 0,  # Já passou do KM
                    'critico': 0 < km_restantes <= 50,  # Faltando 0-50km
                    'atencao': 50 < km_restantes <= 100,  # Faltando 51-100km
                })
    
    # Ordenar por urgência (mais urgente primeiro)
    alertas_revisao.sort(key=lambda x: (not x['urgente'], not x['critico'], x['km_restantes']))
    
    return {
        'alertas_revisao': alertas_revisao,
        'total_alertas_revisao': len(alertas_revisao)
    }


def alertas_frota_processor(request):
    """
    Context processor para alertar sobre licenciamentos e outros itens de frota próximos ao vencimento.
    Verifica licenciamentos próximos ao vencimento (30, 60, 90 dias) e vencidos.
    Apenas para usuários com acesso ao menu de frota.
    """
    alertas_licenciamento = []
    
    if not request.user.is_authenticated:
        return {
            'alertas_licenciamento': [],
            'total_alertas_licenciamento': 0,
            'total_alertas_frota': 0
        }
    
    # Verificar se o usuário tem acesso ao menu de frota
    from .permissoes_simples import tem_permissao
    tem_acesso_frota = (
        request.user.is_superuser or
        tem_permissao(request.user, 'viaturas', 'visualizar')
    )
    
    if not tem_acesso_frota:
        return {
            'alertas_licenciamento': [],
            'total_alertas_licenciamento': 0,
            'total_alertas_frota': 0
        }
    
    # Importar modelo de LicenciamentoViatura
    from .models import LicenciamentoViatura
    from datetime import date, timedelta
    
    hoje = date.today()
    
    # Buscar licenciamentos ativos
    licenciamentos = LicenciamentoViatura.objects.filter(ativo=True)
    
    for licenciamento in licenciamentos:
        # Verificar apenas licenciamentos pendentes (não pagos)
        if licenciamento.status != 'PAGO':
            data_vencimento = licenciamento.data_vencimento
            dias_restantes = (data_vencimento - hoje).days
            
            # Alerta se estiver próximo ao vencimento ou já vencido
            if dias_restantes <= 90:
                # Determinar nível de urgência
                urgente = dias_restantes <= 0  # Vencido
                critico = 0 < dias_restantes <= 30  # Faltando 0-30 dias
                atencao_media = 30 < dias_restantes <= 60  # Faltando 31-60 dias
                atencao_baixa = 60 < dias_restantes <= 90  # Faltando 61-90 dias
                
                alertas_licenciamento.append({
                    'licenciamento': licenciamento,
                    'viatura': licenciamento.viatura,
                    'data_vencimento': data_vencimento,
                    'dias_restantes': dias_restantes,
                    'valor': licenciamento.valor_licenciamento,
                    'ano': licenciamento.ano_licenciamento,
                    'urgente': urgente,
                    'critico': critico,
                    'atencao_media': atencao_media,
                    'atencao_baixa': atencao_baixa,
                })
    
    # Ordenar por urgência (mais urgente primeiro)
    alertas_licenciamento.sort(key=lambda x: (
        not x['urgente'],  # Vencidos primeiro
        not x['critico'],  # Depois críticos (0-30 dias)
        not x['atencao_media'],  # Depois atenção média (31-60)
        not x['atencao_baixa'],  # Depois atenção baixa (61-90)
        x['dias_restantes']  # Por fim, ordenar por dias restantes
    ))
    
    total_alertas_frota = len(alertas_licenciamento)
    
    return {
        'alertas_licenciamento': alertas_licenciamento,
        'total_alertas_licenciamento': len(alertas_licenciamento),
        'total_alertas_frota': total_alertas_frota
    } 