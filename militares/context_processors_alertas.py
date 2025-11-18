from django.utils import timezone
from datetime import timedelta
from .models import CalendarioPromocao, UsuarioFuncaoMilitar


def alertas_login_processor(request):
    """
    Context processor para alertas de datas vencendo nos calendários
    APENAS no primeiro login do dia
    """
    if not request.user.is_authenticated:
        return {}
    
    # VERIFICAÇÃO CRÍTICA: Só mostrar popup no primeiro login do dia
    # Verificar se já foi mostrado hoje usando session
    session_key = 'popup_alertas_mostrado_hoje'
    hoje = timezone.now().date().isoformat()
    
    # Se já foi mostrado hoje, não mostrar novamente
    if hasattr(request, 'session') and request.session.get(session_key) == hoje:
        return {
            'alertas_popup': [],
            'tem_alertas_popup': False
        }
    
    alertas_popup = []
    
    # Verificar se o usuário tem funções especiais que devem ver alertas de calendários
    cargos_especiais = [
        'Diretor de Gestão de Pessoas', 
        'Chefe da Seção de Promoções',
        'Operador do Sistema',
        'Administrador do Sistema'
    ]
    
    tem_permissao_calendario = False
    if request.user.is_superuser or request.user.is_staff:
        tem_permissao_calendario = True
    else:
        funcoes_especiais = UsuarioFuncaoMilitar.objects.filter(
            usuario=request.user,
            ativo=True,
            funcao_militar__nome__in=cargos_especiais
        )
        tem_permissao_calendario = funcoes_especiais.exists()
    
    # FOCO: Alertas de datas vencendo nos calendários (a partir de 5 dias)
    if tem_permissao_calendario:
        calendarios_ativos = CalendarioPromocao.objects.filter(
            ativo=True,
            status__in=['APROVADO', 'HOMOLOGADO']
        )
        
        alertas_urgentes = []
        alertas_criticos = []
        alertas_atencao = []
        alertas_vencidos = []
        
        for calendario in calendarios_ativos:
            alertas_calendario = calendario.get_alertas_datas()
            
            for alerta in alertas_calendario:
                item_alerta = {
                    'calendario': calendario,
                    'alerta': alerta
                }
                
                if alerta['tipo'] == 'URGENTE':
                    alertas_urgentes.append(item_alerta)
                elif alerta['tipo'] == 'CRITICO':
                    alertas_criticos.append(item_alerta)
                elif alerta['tipo'] == 'ATENCAO':
                    alertas_atencao.append(item_alerta)
                elif alerta['tipo'] == 'VENCIDO':
                    alertas_vencidos.append(item_alerta)
        
        # PRIORIDADE 1: Alertas URGENTES (vence hoje)
        if alertas_urgentes:
            alertas_popup.append({
                'tipo': 'VENCE_HOJE',
                'titulo': '🚨 ATENÇÃO: Atividades Vencem HOJE!',
                'mensagem': f"URGENTE: {len(alertas_urgentes)} atividade(s) de calendário(s) vencem hoje e precisam de atenção imediata!",
                'detalhes': alertas_urgentes,
                'cor': 'danger',
                'icone': 'fas fa-exclamation-triangle',
                'prioridade': 1
            })
        
        # PRIORIDADE 2: Alertas CRÍTICOS (1-3 dias)
        if alertas_criticos:
            alertas_popup.append({
                'tipo': 'VENCE_BREVE',
                'titulo': '⚠️ Atividades Vencem em Breve',
                'mensagem': f"CRÍTICO: {len(alertas_criticos)} atividade(s) de calendário(s) vencem nos próximos 1-3 dias!",
                'detalhes': alertas_criticos,
                'cor': 'warning',
                'icone': 'fas fa-clock',
                'prioridade': 2
            })
        
        # PRIORIDADE 3: Alertas de ATENÇÃO (4-7 dias) - A PARTIR DE 5 DIAS
        if alertas_atencao:
            alertas_popup.append({
                'tipo': 'VENCE_PROXIMO',
                'titulo': '📅 Atividades Vencem na Próxima Semana',
                'mensagem': f"ATENÇÃO: {len(alertas_atencao)} atividade(s) de calendário(s) vencem na próxima semana (4-7 dias)!",
                'detalhes': alertas_atencao,
                'cor': 'info',
                'icone': 'fas fa-calendar-week',
                'prioridade': 3
            })
        
        # PRIORIDADE 4: Alertas VENCIDOS (para conhecimento)
        if alertas_vencidos and len(alertas_vencidos) <= 3:  # Mostrar apenas se poucos vencidos
            alertas_popup.append({
                'tipo': 'JA_VENCIDO',
                'titulo': '❌ Atividades Vencidas',
                'mensagem': f"Informação: {len(alertas_vencidos)} atividade(s) já venceram e podem precisar de ação.",
                'detalhes': alertas_vencidos,
                'cor': 'secondary',
                'icone': 'fas fa-calendar-times',
                'prioridade': 4
            })
    
    # Ordenar alertas por prioridade (menor número = maior prioridade)
    alertas_popup.sort(key=lambda x: x.get('prioridade', 999))
    
    # Se há alertas, marcar na session que foi mostrado hoje
    if alertas_popup:
        request.session[session_key] = hoje
    
    return {
        'alertas_popup': alertas_popup,
        'tem_alertas_popup': len(alertas_popup) > 0
    }
