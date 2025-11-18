"""
Sistema de tarefas automáticas para atualização de situações dos militares.
Executa automaticamente em background quando o servidor inicia.
"""

import threading
import time
from datetime import date, datetime
from django.db.models import Q
from django.utils import timezone
from militares.models import Militar, Afastamento, Ferias, LicencaEspecial
import logging

logger = logging.getLogger(__name__)

# Flag para controlar se a tarefa está rodando
_tarefa_rodando = False
_thread_tarefa = None


def atualizar_situacoes_automaticamente():
    """
    Atualiza automaticamente as situações dos militares.
    Esta função é executada periodicamente em background.
    """
    try:
        hoje = date.today()
        
        # 1. Encerrar afastamentos vencidos (status ATIVO com data_fim_prevista < hoje)
        afastamentos_vencidos = Afastamento.objects.filter(
            status='ATIVO',
            data_fim_prevista__lt=hoje,
            data_fim_real__isnull=True
        )
        
        for afastamento in afastamentos_vencidos:
            afastamento.status = 'ENCERRADO'
            afastamento.data_fim_real = afastamento.data_fim_prevista
            afastamento.save(update_fields=['status', 'data_fim_real'])
        
        # 2. Atualizar férias vencidas
        ferias_vencidas = Ferias.objects.filter(
            status='GOZANDO',
            data_fim__lt=hoje
        )
        
        for ferias in ferias_vencidas:
            ferias.status = 'GOZADA'
            ferias.save(update_fields=['status'])
        
        # 3. Sincronizar situações de todos os militares ativos
        militares_ativos = Militar.objects.filter(classificacao='ATIVO')
        total_atualizados = 0
        
        for militar in militares_ativos:
            # Verificar se há afastamentos ativos até hoje
            # Considerar ativo apenas se:
            # - data_inicio <= hoje
            # - status != CANCELADO
            # - (data_fim_real >= hoje) OU (data_fim_prevista >= hoje E data_fim_real is null)
            # Se data_fim_prevista < hoje e data_fim_real is null, não considerar como ativo
            afastamentos_ativos = Afastamento.objects.filter(
                militar=militar
            ).exclude(status='CANCELADO').filter(
                data_inicio__lte=hoje
            ).filter(
                Q(data_fim_real__gte=hoje) | 
                Q(data_fim_prevista__gte=hoje, data_fim_real__isnull=True) |
                Q(data_fim_prevista__isnull=True, data_fim_real__isnull=True)
            )
            
            # Verificar se há férias ativas até hoje
            # Considerar ativo apenas se data_fim >= hoje
            # Se data_fim < hoje, não considerar como ativo (mesmo que status seja GOZANDO)
            ferias_ativas = Ferias.objects.filter(
                militar=militar
            ).exclude(status__in=['CANCELADA', 'REPROGRAMADA', 'GOZADA']).filter(
                data_inicio__lte=hoje,
                data_fim__gte=hoje
            ).filter(
                status__in=['GOZANDO', 'PLANEJADA']
            )
            
            # Verificar se há licenças especiais ativas até hoje
            # Considerar ativo apenas se (data_fim >= hoje OU data_fim is null)
            # Se data_fim < hoje, não considerar como ativo
            licencas_ativas = LicencaEspecial.objects.filter(
                militar=militar
            ).exclude(status='CANCELADA').filter(
                data_inicio__lte=hoje
            ).filter(
                Q(data_fim__gte=hoje) | 
                Q(data_fim__isnull=True)
            )
            
            # Determinar qual situação o militar deveria ter
            situacao_esperada = None
            
            if afastamentos_ativos.exists():
                primeiro_afastamento = afastamentos_ativos.order_by('data_inicio').first()
                situacao_esperada = primeiro_afastamento.tipo_afastamento
            elif ferias_ativas.exists():
                situacao_esperada = 'AFASTAMENTO_FERIAS'
            elif licencas_ativas.exists():
                situacao_esperada = 'AFASTAMENTO_LICENCA_ESPECIAL'
            else:
                situacao_esperada = 'PRONTO'
            
            # Atualizar situação se necessário
            if militar.situacao != situacao_esperada:
                militar.situacao = situacao_esperada
                militar.save(update_fields=['situacao'])
                total_atualizados += 1
        
        if total_atualizados > 0:
            logger.info(f'[AUTOMÁTICO] {total_atualizados} militares tiveram suas situações atualizadas automaticamente.')
        
    except Exception as e:
        logger.error(f'Erro ao atualizar situações automaticamente: {e}')


def tarefa_periodica():
    """
    Tarefa que executa periodicamente em background.
    Verifica e atualiza situações uma vez por dia (às 06:00).
    """
    global _tarefa_rodando
    
    primeira_execucao = True
    
    while _tarefa_rodando:
        try:
            agora = datetime.now()
            proxima_execucao = agora.replace(hour=6, minute=0, second=0, microsecond=0)
            
            # Se já passou das 06:00 hoje
            if agora >= proxima_execucao:
                # Na primeira execução, executar imediatamente se já passou das 06:00
                if primeira_execucao:
                    logger.info('[AUTOMÁTICO] Executando primeira atualização automática...')
                    atualizar_situacoes_automaticamente()
                    primeira_execucao = False
                    # Agendar para amanhã às 06:00
                    from datetime import timedelta
                    proxima_execucao += timedelta(days=1)
                else:
                    # Agendar para amanhã às 06:00
                    from datetime import timedelta
                    proxima_execucao += timedelta(days=1)
            
            # Calcular segundos até a próxima execução
            segundos_ate_execucao = (proxima_execucao - agora).total_seconds()
            
            logger.info(f'[AUTOMÁTICO] Próxima atualização agendada para: {proxima_execucao.strftime("%d/%m/%Y %H:%M")}')
            
            # Aguardar até o horário agendado
            time.sleep(segundos_ate_execucao)
            
            # Executar atualização
            if _tarefa_rodando:
                logger.info('[AUTOMÁTICO] Iniciando atualização automática de situações...')
                atualizar_situacoes_automaticamente()
                logger.info('[AUTOMÁTICO] Atualização automática concluída.')
                primeira_execucao = False
            
        except Exception as e:
            logger.error(f'Erro na tarefa periódica de atualização: {e}')
            # Em caso de erro, aguardar 1 hora antes de tentar novamente
            time.sleep(3600)  # 1 hora


def iniciar_tarefa_automatica():
    """
    Inicia a tarefa automática em background.
    Deve ser chamada quando o servidor inicia.
    """
    global _tarefa_rodando, _thread_tarefa
    
    # Verificar se já está rodando
    if _tarefa_rodando:
        return
    
    # Verificar se estamos em modo de desenvolvimento (runserver)
    # ou em produção (WSGI)
    import sys
    if 'runserver' in sys.argv or 'gunicorn' in sys.argv or 'uwsgi' in sys.argv:
        _tarefa_rodando = True
        _thread_tarefa = threading.Thread(target=tarefa_periodica, daemon=True)
        _thread_tarefa.start()
        logger.info('[AUTOMÁTICO] Tarefa de atualização automática de situações iniciada.')


def parar_tarefa_automatica():
    """
    Para a tarefa automática.
    """
    global _tarefa_rodando
    _tarefa_rodando = False
    logger.info('[AUTOMÁTICO] Tarefa de atualização automática de situações parada.')

