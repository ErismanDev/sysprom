from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.db import transaction
from datetime import date
from django.contrib.auth.models import User
from .models import (
    NotificacaoSessao, SessaoComissao, DeliberacaoComissao, 
    MembroComissao, PresencaSessao, VotoDeliberacao, Militar, Vaga, PrevisaoVaga, Promocao, FichaConceitoOficiais, FichaConceitoPracas, MilitarFuncao, FuncaoMilitar, UsuarioFuncaoMilitar, Lotacao, Ferias, LicencaEspecial, Afastamento
)
from collections import defaultdict
import threading

# Flags para evitar recursão infinita nos signals
_sync_lock = threading.Lock()
_syncing_militar = set()
_syncing_usuario = set()
_atualizando_situacao = set()  # Flag para evitar loops ao atualizar situação



@receiver(user_logged_in)
def criar_notificacoes_login(sender, user, request, **kwargs):
    """Cria notificações quando o usuário faz login"""
    
    # Verificar se o usuário é membro de alguma comissão
    membros_comissao = MembroComissao.objects.filter(
        usuario=user,
        ativo=True
    ).select_related('comissao')
    
    if not membros_comissao.exists():
        return
    
    # Data atual
    hoje = date.today()
    
    for membro in membros_comissao:
        comissao = membro.comissao
        
        # Buscar sessões da comissão
        sessoes = SessaoComissao.objects.filter(
            comissao=comissao,
            status__in=['AGENDADA', 'EM_ANDAMENTO']
        ).order_by('data_sessao', 'hora_inicio')
        
        for sessao in sessoes:
            # Verificar se o membro está presente na sessão
            try:
                presenca = PresencaSessao.objects.get(
                    sessao=sessao,
                    membro=membro
                )
                if not presenca.presente:
                    continue  # Membro não está presente
            except PresencaSessao.DoesNotExist:
                continue  # Presença não registrada
            
            # Notificação para sessão hoje
            if sessao.data_sessao == hoje:
                NotificacaoSessao.criar_notificacao_sessao_hoje(user, sessao)
            
            # Verificar deliberações pendentes de votação
            deliberacoes = sessao.deliberacoes.all()
            for deliberacao in deliberacoes:
                # Verificar se o membro já votou nesta deliberação
                voto_existe = VotoDeliberacao.objects.filter(
                    deliberacao=deliberacao,
                    membro=membro
                ).exists()
                
                if not voto_existe:
                    NotificacaoSessao.criar_notificacao_votacao_pendente(user, deliberacao)
            
            # Notificação para sessão pendente (se há deliberações não votadas)
            if sessao.status == 'EM_ANDAMENTO':
                total_deliberacoes = sessao.deliberacoes.count()
                votos_realizados = VotoDeliberacao.objects.filter(
                    deliberacao__sessao=sessao,
                    membro=membro
                ).count()
                
                if votos_realizados < total_deliberacoes:
                    NotificacaoSessao.criar_notificacao_sessao_pendente(user, sessao)


@receiver(post_save, sender=SessaoComissao)
def notificar_mudanca_status_sessao(sender, instance, created, **kwargs):
    """Notifica mudanças de status da sessão"""
    if created:
        # Nova sessão criada
        membros = MembroComissao.objects.filter(
            comissao=instance.comissao,
            ativo=True
        ).select_related('usuario')
        
        for membro in membros:
            if membro.usuario:
                NotificacaoSessao.objects.create(
                    usuario=membro.usuario,
                    tipo='SESSAO_AGENDADA',
                    titulo=f"Nova Sessão {instance.numero} Agendada",
                    mensagem=f"A sessão {instance.numero} da {instance.comissao.nome} foi agendada para {instance.data_sessao.strftime('%d/%m/%Y')} às {instance.hora_inicio.strftime('%H:%M')}.",
                    prioridade='MEDIA',
                    sessao=instance,
                    comissao=instance.comissao
                )


@receiver(post_save, sender=DeliberacaoComissao)
def notificar_nova_deliberacao(sender, instance, created, **kwargs):
    """Notifica nova deliberação criada"""
    if created:
        # Buscar membros presentes na sessão
        membros_presentes = PresencaSessao.objects.filter(
            sessao=instance.sessao,
            presente=True
        ).select_related('membro__usuario')
        
        for presenca in membros_presentes:
            if presenca.membro.usuario:
                NotificacaoSessao.objects.create(
                    usuario=presenca.membro.usuario,
                    tipo='DELIBERACAO_PENDENTE',
                    titulo=f"Nova Deliberação {instance.numero}",
                    mensagem=f"A deliberação '{instance.assunto}' foi criada na sessão {instance.sessao.numero}.",
                    prioridade='ALTA',
                    deliberacao=instance,
                    sessao=instance.sessao,
                    comissao=instance.sessao.comissao
                ) 


@receiver(post_save, sender=Militar)
def atualizar_efetivo_vagas_militar_salvo(sender, instance, created, **kwargs):
    """
    Atualiza automaticamente o efetivo nas vagas quando um militar é salvo
    """
    # Aguardar um pouco para garantir que a transação foi commitada
    from django.db import connection
    if connection.in_atomic_block:
        return
    
    # Executar em background para não bloquear a resposta
    transaction.on_commit(lambda: _atualizar_efetivo_por_posto_quadro(instance.posto_graduacao, instance.quadro))


@receiver(post_delete, sender=Militar)
def atualizar_efetivo_vagas_militar_excluido(sender, instance, **kwargs):
    """
    Atualiza automaticamente o efetivo nas vagas quando um militar é excluído
    """
    # Aguardar um pouco para garantir que a transação foi commitada
    from django.db import connection
    if connection.in_atomic_block:
        return
    
    # Executar em background para não bloquear a resposta
    transaction.on_commit(lambda: _atualizar_efetivo_por_posto_quadro(instance.posto_graduacao, instance.quadro))


def _atualizar_efetivo_por_posto_quadro(posto_graduacao, quadro):
    """
    Atualiza o efetivo atual para um posto/quadro específico
    """
    try:
        # Mapear postos para compatibilidade
        mapeamento_postos = {
            'CB': 'CB',    # Coronel
            'TC': 'TC',    # Tenente-Coronel
            'MJ': 'MJ',    # Major
            'CP': 'CP',    # Capitão
            '1T': '1T',    # 1º Tenente
            '2T': '2T',    # 2º Tenente
            'ST': 'ST',    # Subtenente
            '1S': '1S',    # 1º Sargento
            '2S': '2S',    # 2º Sargento
            '3S': '3S',    # 3º Sargento
            'CAB': 'CAB',  # Cabo
            'SD': 'SD',    # Soldado
        }
        
        posto_vaga = mapeamento_postos.get(posto_graduacao)
        if not posto_vaga:
            return
        
        # Contar militares ativos para este posto/quadro
        efetivo_atual = Militar.objects.filter(
            posto_graduacao=posto_graduacao,
            quadro=quadro,
            classificacao='ATIVO'
        ).count()
        
        # Atualizar vaga
        try:
            vaga = Vaga.objects.get(posto=posto_vaga, quadro=quadro)
            if vaga.efetivo_atual != efetivo_atual:
                vaga.efetivo_atual = efetivo_atual
                vaga.save(update_fields=['efetivo_atual'])
        except Vaga.DoesNotExist:
            # Criar vaga se não existir
            Vaga.objects.create(
                posto=posto_vaga,
                quadro=quadro,
                efetivo_atual=efetivo_atual,
                efetivo_maximo=efetivo_atual + 10  # Valor padrão
            )
        
        # Atualizar previsão de vaga
        try:
            previsao = PrevisaoVaga.objects.get(
                posto=posto_vaga,
                quadro=quadro,
                ativo=True
            )
            if previsao.efetivo_atual != efetivo_atual:
                previsao.efetivo_atual = efetivo_atual
                previsao.save(update_fields=['efetivo_atual'])
        except PrevisaoVaga.DoesNotExist:
            # Previsão não existe, não criar automaticamente
            pass
            
    except Exception as e:
        # Log do erro sem interromper o fluxo
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao atualizar efetivo para {posto_graduacao}/{quadro}: {e}")


def atualizar_todas_vagas_efetivo():
    """
    Função para atualizar todas as vagas com o efetivo atual
    Pode ser chamada manualmente ou via comando
    """
    # Contar militares por posto e quadro
    efetivo_por_posto_quadro = defaultdict(int)
    
    # Buscar todos os militares ativos
    militares_ativos = Militar.objects.filter(classificacao='ATIVO')
    
    # Contar efetivo por posto e quadro
    for militar in militares_ativos:
        key = (militar.posto_graduacao, militar.quadro)
        efetivo_por_posto_quadro[key] += 1
    
    # Mapear postos para compatibilidade
    mapeamento_postos = {
        'CB': 'CB',    # Coronel
        'TC': 'TC',    # Tenente-Coronel
        'MJ': 'MJ',    # Major
        'CP': 'CP',    # Capitão
        '1T': '1T',    # 1º Tenente
        '2T': '2T',    # 2º Tenente
        'ST': 'ST',    # Subtenente
        '1S': '1S',    # 1º Sargento
        '2S': '2S',    # 2º Sargento
        '3S': '3S',    # 3º Sargento
        'CAB': 'CAB',  # Cabo
        'SD': 'SD',    # Soldado
    }
    
    # Atualizar vagas
    vagas_atualizadas = 0
    vagas_criadas = 0
    
    with transaction.atomic():
        for (posto_militar, quadro_militar), efetivo_atual in efetivo_por_posto_quadro.items():
            posto_vaga = mapeamento_postos.get(posto_militar)
            
            if not posto_vaga:
                continue
            
            # Buscar ou criar vaga
            vaga, created = Vaga.objects.get_or_create(
                posto=posto_vaga,
                quadro=quadro_militar,
                defaults={
                    'efetivo_atual': efetivo_atual,
                    'efetivo_maximo': efetivo_atual + 10,  # Valor padrão
                }
            )
            
            if created:
                vagas_criadas += 1
            else:
                # Atualizar efetivo atual
                if vaga.efetivo_atual != efetivo_atual:
                    vaga.efetivo_atual = efetivo_atual
                    vaga.save(update_fields=['efetivo_atual'])
                    vagas_atualizadas += 1
        
        # Atualizar previsões de vagas também
        previsoes_atualizadas = 0
        
        for (posto_militar, quadro_militar), efetivo_atual in efetivo_por_posto_quadro.items():
            posto_vaga = mapeamento_postos.get(posto_militar)
            
            if not posto_vaga:
                continue
            
            # Buscar previsão de vaga
            try:
                previsao = PrevisaoVaga.objects.get(
                    posto=posto_vaga,
                    quadro=quadro_militar,
                    ativo=True
                )
                
                if previsao.efetivo_atual != efetivo_atual:
                    previsao.efetivo_atual = efetivo_atual
                    previsao.save(update_fields=['efetivo_atual'])
                    previsoes_atualizadas += 1
                    
            except PrevisaoVaga.DoesNotExist:
                # Previsão não existe, não criar automaticamente
                pass
    
    return {
        'militares_processados': militares_ativos.count(),
        'vagas_criadas': vagas_criadas,
        'vagas_atualizadas': vagas_atualizadas,
        'previsoes_atualizadas': previsoes_atualizadas,
    } 


@receiver(post_save, sender=Militar)
def atualizar_membro_comissao_apos_inativacao(sender, instance, created, **kwargs):
    """
    Atualiza automaticamente o campo 'ativo' do MembroComissao quando um militar é inativado
    """
    if not created:  # Só executa quando o militar é atualizado, não criado
        # Verificar se a situação mudou para inativa
        situacoes_inativas = ['IN', 'TR', 'AP', 'EX']
        
        if instance.situacao in situacoes_inativas:
            # Buscar todos os membros de comissão deste militar
            membros_comissao = MembroComissao.objects.filter(
                militar=instance,
                ativo=True  # Só atualizar se ainda estiver ativo
            )
            
            if membros_comissao.exists():
                # Atualizar todos os membros de comissão para inativo
                membros_comissao.update(ativo=False)
                print(f"[SINAL] Militar {instance.nome_completo} inativado. {membros_comissao.count()} membros de comissão marcados como inativos.")
        
        elif instance.classificacao == 'ATIVO':
            # Se o militar foi reativado, verificar se deve reativar os membros de comissão
            # (opcional - depende da regra de negócio)
            membros_comissao = MembroComissao.objects.filter(
                militar=instance,
                ativo=False  # Só atualizar se estiver inativo
            )
            
            if membros_comissao.exists():
                # Reativar membros de comissão (opcional)
                membros_comissao.update(ativo=True)
                print(f"[SINAL] Militar {instance.nome_completo} reativado. {membros_comissao.count()} membros de comissão reativados.") 


@receiver(post_save, sender=Militar)
def atualizar_vagas_apos_salvar(sender, instance, **kwargs):
    # Recalcular efetivo e vagas para o posto/quadro atual
    posto = instance.posto_graduacao
    quadro = instance.quadro
    efetivo_atual = Militar.objects.filter(posto_graduacao=posto, quadro=quadro, classificacao='ATIVO').count()
    # Atualizar PrevisaoVaga
    previsao = PrevisaoVaga.objects.filter(posto=posto, quadro=quadro, ativo=True).first()
    if previsao:
        previsao.efetivo_atual = efetivo_atual
        previsao.save()
    # Atualizar Vaga
    vaga = Vaga.objects.filter(posto=posto, quadro=quadro).first()
    if vaga:
        vaga.efetivo_atual = efetivo_atual
        vaga.save()

@receiver(post_delete, sender=Militar)
def atualizar_vagas_apos_excluir(sender, instance, **kwargs):
    # Recalcular efetivo e vagas para o posto/quadro anterior
    posto = instance.posto_graduacao
    quadro = instance.quadro
    efetivo_atual = Militar.objects.filter(posto_graduacao=posto, quadro=quadro, classificacao='ATIVO').count()
    # Atualizar PrevisaoVaga
    previsao = PrevisaoVaga.objects.filter(posto=posto, quadro=quadro, ativo=True).first()
    if previsao:
        previsao.efetivo_atual = efetivo_atual
        previsao.save()
    # Atualizar Vaga
    vaga = Vaga.objects.filter(posto=posto, quadro=quadro).first()
    if vaga:
        vaga.efetivo_atual = efetivo_atual
        vaga.save() 





@receiver(post_save, sender=User)
def associar_usuario_a_militar(sender, instance, created, **kwargs):
    """
    Associa automaticamente um usuário a um militar quando o usuário é criado
    """
    if created:
        # Ignorar usuários sintéticos do módulo de ensino
        if instance.username.startswith(('aluno_', 'instrutor_', 'monitor_')):
            return

        # Tentar encontrar um militar que corresponda ao usuário de forma resiliente
        militar = None

        # Primeiro, tentar por CPF (username)
        if instance.username:
            militar = Militar.objects.filter(cpf=instance.username).first()

        # Se não encontrou por CPF, tentar por nome completo
        if not militar:
            nome_completo = f"{instance.first_name} {instance.last_name}".strip()
            if nome_completo:
                militar = Militar.objects.filter(nome_completo__iexact=nome_completo).first()

        # Se não encontrou por nome, tentar por email
        if not militar and instance.email:
            militar = Militar.objects.filter(email__iexact=instance.email).first()

        if militar and not militar.user:
            militar.user = instance
            militar.save(update_fields=['user'])
            print(f"[SINAL] Usuário {instance.username} associado automaticamente ao militar {militar.nome_completo}")
        
        # Atribuir função padrão "Serviço Operacional" para o usuário
        atribuir_funcao_padrao_usuario(instance) 

@receiver(post_save, sender=User)
def criar_militar_para_usuario(sender, instance, created, **kwargs):
    """Cria um militar automaticamente quando um usuário é criado"""
    # Verificar se signals estão desabilitados (para restore de backup)
    import os
    if os.environ.get('DISABLE_SIGNALS', '0') == '1':
        return
    if created and not hasattr(instance, 'militar'):
        # Ignorar usuários sintéticos do módulo de ensino
        if instance.username.startswith(('aluno_', 'instrutor_', 'monitor_')):
            return
        # Verificar se o usuário tem dados suficientes para criar um militar
        if instance.first_name and instance.last_name:
            try:
                # Criar militar básico
                militar = Militar.objects.create(
                    user=instance,
                    matricula=f"USER_{instance.id}",
                    nome_completo=f"{instance.first_name} {instance.last_name}",
                    nome_guerra=instance.first_name,
                    cpf="000.000.000-00",  # CPF temporário
                    rg="0000000",
                    orgao_expedidor="SSP",
                    data_nascimento=timezone.now().date(),
                    sexo='M',
                    quadro='COMB',
                    posto_graduacao='SD',
                    data_ingresso=timezone.now().date(),
                    data_promocao_atual=timezone.now().date(),
                    classificacao='ATIVO',
                    email=instance.email or f"user{instance.id}@example.com",
                    telefone="(00) 00000-0000",
                    celular="(00) 00000-0000"
                )
                print(f"Militar criado automaticamente para usuário {instance.username}")
            except Exception as e:
                print(f"Erro ao criar militar para usuário {instance.username}: {e}")

@receiver(post_save, sender=Militar)
def atualizar_fichas_conceito_militar(sender, instance, **kwargs):
    """Atualiza fichas de conceito quando militar é salvo"""
    try:
        ficha_oficiais = instance.fichaconceitooficiais_set.first()
        if ficha_oficiais:
            ficha_oficiais.save()
        
        ficha_pracas = instance.fichaconceitopracas_set.first()
        if ficha_pracas:
            ficha_pracas.save()
            
    except Exception as e:
        print(f"Erro ao atualizar fichas de conceito para militar {instance.matricula}: {e}")

@receiver(post_save, sender=Promocao)
def atualizar_data_promocao_atual_militar(sender, instance, created, **kwargs):
    """Atualiza automaticamente a data_promocao_atual do militar quando uma promoção é criada"""
    if created:
        try:
            militar = instance.militar
            
            # Atualizar a data_promocao_atual para a data da promoção mais recente
            promocao_recente = Promocao.objects.filter(
                militar=militar
            ).order_by('-data_promocao').first()
            
            if promocao_recente and militar.data_promocao_atual != promocao_recente.data_promocao:
                militar.data_promocao_atual = promocao_recente.data_promocao
                militar.save(update_fields=['data_promocao_atual'])
                print(f"Data de promoção atualizada automaticamente para {militar.nome_completo}: {promocao_recente.data_promocao}")
            
            # Atualizar o posto/graduação se não for promoção histórica
            # Para promoções históricas, NÃO alterar o posto atual do militar
            if not instance.is_historica:
                if militar.posto_graduacao != instance.posto_novo:
                    militar.posto_graduacao = instance.posto_novo
                    militar.save(update_fields=['posto_graduacao'])
                    print(f"Posto atualizado automaticamente para {militar.nome_completo}: {instance.posto_novo}")
            else:
                print(f"Promoção histórica registrada para {militar.nome_completo}: {instance.posto_anterior} -> {instance.posto_novo} (posto atual mantido: {militar.posto_graduacao})")
                    
        except Exception as e:
            print(f"Erro ao atualizar militar após promoção: {e}")

@receiver(post_delete, sender=Promocao)
def reverter_data_promocao_atual_militar(sender, instance, **kwargs):
    """Reverte a data_promocao_atual do militar quando uma promoção é excluída"""
    try:
        militar = instance.militar
        
        # Buscar a promoção mais recente restante
        promocao_recente = Promocao.objects.filter(
            militar=militar
        ).order_by('-data_promocao').first()
        
        if promocao_recente:
            # Atualizar para a promoção mais recente restante
            if militar.data_promocao_atual != promocao_recente.data_promocao:
                militar.data_promocao_atual = promocao_recente.data_promocao
                militar.save(update_fields=['data_promocao_atual'])
                print(f"Data de promoção revertida para {militar.nome_completo}: {promocao_recente.data_promocao}")
        else:
            # Se não há mais promoções, usar uma data padrão (5 anos após ingresso)
            from datetime import timedelta
            data_padrao = militar.data_ingresso + timedelta(days=5*365)
            if data_padrao > timezone.now().date():
                data_padrao = timezone.now().date() - timedelta(days=5*365)
            
            militar.data_promocao_atual = data_padrao
            militar.save(update_fields=['data_promocao_atual'])
            print(f"Data de promoção definida como padrão para {militar.nome_completo}: {data_padrao}")
            
    except Exception as e:
        print(f"Erro ao reverter militar após exclusão de promoção: {e}")

@receiver(post_save, sender=FichaConceitoOficiais)
def atualizar_pontos_ficha_oficiais(sender, instance, **kwargs):
    """Atualiza automaticamente os pontos da ficha de oficiais"""
    try:
        # Recalcular pontos
        pontos_calculados = instance.calcular_pontos()
        if instance.pontos != pontos_calculados:
            instance.pontos = pontos_calculados
            instance.save(update_fields=['pontos'])
            print(f"Pontos atualizados para ficha de oficiais de {instance.militar.nome_completo}: {pontos_calculados}")
    except Exception as e:
        print(f"Erro ao atualizar pontos da ficha de oficiais: {e}")

@receiver(post_save, sender=FichaConceitoPracas)
def atualizar_pontos_ficha_pracas(sender, instance, **kwargs):
    """Atualiza automaticamente os pontos da ficha de praças"""
    try:
        # Recalcular pontos
        pontos_calculados = instance.calcular_pontos()
        if instance.pontos != pontos_calculados:
            instance.pontos = pontos_calculados
            instance.save(update_fields=['pontos'])
            print(f"Pontos atualizados para ficha de praças de {instance.militar.nome_completo}: {pontos_calculados}")
    except Exception as e:
        print(f"Erro ao atualizar pontos da ficha de praças: {e}")


@receiver(post_save, sender=MilitarFuncao)
def replicar_funcao_militar_para_usuario(sender, instance, created, **kwargs):
    """Replica automaticamente a função do militar para o usuário associado"""
    # Verificar se já estamos sincronizando este militar para evitar recursão
    with _sync_lock:
        if instance.id in _syncing_militar:
            return
        _syncing_militar.add(instance.id)
    
    try:
        # Verificar se o militar tem usuário associado
        if not instance.militar.user:
            return
        
        usuario = instance.militar.user
        
        # Usar Função Militar diretamente
        funcao_militar = instance.funcao_militar
        
        # Verificar se já existe uma função do usuário com esta função militar
        funcao_existente = UsuarioFuncaoMilitar.objects.filter(
            usuario=usuario,
            funcao_militar=funcao_militar
        ).first()
        
        if funcao_existente:
            # Só desativar se a função não estiver em andamento (status ATUAL)
            if not instance.ativo and instance.status == 'ATUAL':
                # Verificar se há outras funções ativas do militar
                outras_funcoes_ativas = MilitarFuncao.objects.filter(
                    militar=instance.militar,
                    ativo=True,
                    status='ATUAL'
                ).exclude(id=instance.id)
                
                if outras_funcoes_ativas.exists():
                    # Se há outras funções ativas, desativar esta função do usuário
                    funcao_existente.ativo = False
                    funcao_existente.save()
                    print(f"Função militar desativada para usuário {usuario.username}: {funcao_militar.nome}")
                else:
                    # Se não há outras funções ativas, manter ativa mas marcar como inativa
                    funcao_existente.ativo = False
                    funcao_existente.save()
                    print(f"Função militar mantida ativa (única função) para usuário {usuario.username}: {funcao_militar.nome}")
            else:
                # Atualizar função existente normalmente
                funcao_existente.ativo = instance.ativo and instance.status == 'ATUAL'
                funcao_existente.save()
                print(f"Função militar atualizada para usuário {usuario.username}: {funcao_militar.nome}")
        else:
            # Criar nova função militar do usuário apenas se estiver ativa
            if instance.ativo and instance.status == 'ATUAL':
                # Verificar se a função foi adicionada via interface de usuário ou via militar
                # Se foi adicionada via usuário, não remover a função padrão
                funcao_via_usuario = hasattr(instance, '_adicionada_via_usuario') and instance._adicionada_via_usuario
                
                # Remover função padrão "Serviço Operacional" apenas se foi adicionada via militar
                # (não via interface de usuário) e exceto para superusuários
                if not funcao_via_usuario:
                    funcao_padrao = FuncaoMilitar.objects.filter(nome='Serviço Operacional', ativo=True).first()
                    if funcao_padrao and not usuario.is_superuser:
                        UsuarioFuncaoMilitar.objects.filter(
                            usuario=usuario,
                            funcao_militar=funcao_padrao
                        ).delete()
                        print(f"Função padrão 'Serviço Operacional' removida do usuário {usuario.username}")
                
                # Criar nova função militar do usuário
                UsuarioFuncaoMilitar.objects.create(
                    usuario=usuario,
                    funcao_militar=funcao_militar,
                    ativo=instance.ativo and instance.status == 'ATUAL'
                )
                print(f"Função militar criada para usuário {usuario.username}: {funcao_militar.nome}")
            
    except Exception as e:
        print(f"Erro ao replicar função do militar para usuário: {e}")
    finally:
        # Remover da lista de sincronização
        with _sync_lock:
            _syncing_militar.discard(instance.id)




def atribuir_funcao_padrao_usuario(usuario):
    """Atribui a função padrão para usuários sem função específica"""
    try:
        # Verificar se o usuário já possui funções militares
        if UsuarioFuncaoMilitar.objects.filter(usuario=usuario).exists():
            return
        
        # Para superusuários, atribuir "Administrador do Sistema"
        if usuario.is_superuser:
            funcao_padrao = FuncaoMilitar.objects.filter(
                nome='Administrador do Sistema',
                ativo=True
            ).first()
            
            if not funcao_padrao:
                print(f"Função 'Administrador do Sistema' não encontrada para superusuário {usuario.username}")
                return
        else:
            # Para usuários normais, atribuir "Serviço Operacional"
            funcao_padrao = FuncaoMilitar.objects.filter(
                nome='Serviço Operacional',
                ativo=True
            ).first()
            
            if not funcao_padrao:
                print(f"Função padrão 'Serviço Operacional' não encontrada para usuário {usuario.username}")
                return
        
        # Criar função padrão para o usuário
        UsuarioFuncaoMilitar.objects.create(
            usuario=usuario,
            funcao_militar=funcao_padrao,
            ativo=True
        )
        
        print(f"Função padrão '{funcao_padrao.nome}' atribuída ao usuário {usuario.username}")
        
    except Exception as e:
        print(f"Erro ao atribuir função padrão para usuário {usuario.username}: {e}")


def sincronizar_funcao_com_lotacao(usuario_funcao):
    """Sincroniza uma função do usuário com sua lotação atual"""
    try:
        from .models import Lotacao
        
        # Buscar lotação atual do militar
        lotacao_atual = Lotacao.objects.filter(
            militar=usuario_funcao.usuario.militar,
            ativo=True,
            data_fim__isnull=True
        ).first()
        
        if not lotacao_atual:
            return
        
        # Atualizar campos de lotação se não estiverem definidos
        atualizado = False
        
        if not usuario_funcao.orgao and lotacao_atual.orgao:
            usuario_funcao.orgao = lotacao_atual.orgao
            atualizado = True
            
        if not usuario_funcao.grande_comando and lotacao_atual.grande_comando:
            usuario_funcao.grande_comando = lotacao_atual.grande_comando
            atualizado = True
            
        if not usuario_funcao.unidade and lotacao_atual.unidade:
            usuario_funcao.unidade = lotacao_atual.unidade
            atualizado = True
            
        if not usuario_funcao.sub_unidade and lotacao_atual.sub_unidade:
            usuario_funcao.sub_unidade = lotacao_atual.sub_unidade
            atualizado = True
        
        if atualizado:
            usuario_funcao.save()
            print(f"Função '{usuario_funcao.funcao_militar.nome}' sincronizada com lotação para {usuario_funcao.usuario.username}")
            
    except Exception as e:
        print(f"Erro ao sincronizar função com lotação: {e}")


# Signal já registrado diretamente na função replicar_funcao_militar_para_usuario


@receiver(post_save, sender=UsuarioFuncaoMilitar)
def sincronizar_funcao_usuario_para_militar(sender, instance, created, **kwargs):
    """Sincroniza função do usuário para o militar associado"""
    # Verificar se já estamos sincronizando este usuário para evitar recursão
    with _sync_lock:
        if instance.id in _syncing_usuario:
            return
        _syncing_usuario.add(instance.id)
    
    try:
        # Verificar se o usuário tem militar associado
        if not hasattr(instance.usuario, 'militar') or not instance.usuario.militar:
            return
        
        militar = instance.usuario.militar
        funcao_militar = instance.funcao_militar
        
        # Verificar se já existe uma função do militar com esta função militar
        funcao_existente = MilitarFuncao.objects.filter(
            militar=militar,
            funcao_militar=funcao_militar,
            status='ATUAL'
        ).first()
        
        if funcao_existente:
            # Só desativar se a função não estiver em andamento (status ATUAL)
            if not instance.ativo and funcao_existente.status == 'ATUAL':
                # Verificar se há outras funções ativas do usuário
                outras_funcoes_ativas = UsuarioFuncaoMilitar.objects.filter(
                    usuario=instance.usuario,
                    ativo=True
                ).exclude(id=instance.id)
                
                if outras_funcoes_ativas.exists():
                    # Se há outras funções ativas, desativar esta função do militar
                    funcao_existente.ativo = False
                    funcao_existente.status = 'ANTERIOR'
                    funcao_existente.data_fim = date.today()
                    funcao_existente.save()
                    print(f"Função militar desativada para militar {militar.matricula}: {funcao_militar.nome}")
                else:
                    # Se não há outras funções ativas, manter ativa mas marcar como inativa
                    funcao_existente.ativo = False
                    funcao_existente.save()
                    print(f"Função militar mantida ativa (única função) para militar {militar.matricula}: {funcao_militar.nome}")
            else:
                # Atualizar função existente normalmente
                funcao_existente.ativo = instance.ativo
                funcao_existente.save()
                print(f"Função militar atualizada para militar {militar.matricula}: {funcao_militar.nome}")
        else:
            # Criar nova função militar apenas se estiver ativa
            if instance.ativo:
                MilitarFuncao.objects.create(
                    militar=militar,
                    funcao_militar=funcao_militar,
                    tipo_funcao='PRINCIPAL',
                    status='ATUAL',
                    data_inicio=date.today(),
                    ativo=instance.ativo
                )
                print(f"Função militar criada para militar {militar.matricula}: {funcao_militar.nome}")
            
    except Exception as e:
        print(f"Erro ao sincronizar função do usuário para militar: {e}")
    finally:
        # Remover da lista de sincronização
        with _sync_lock:
            _syncing_usuario.discard(instance.id)


@receiver(post_delete, sender=UsuarioFuncaoMilitar)
def remover_funcao_militar_quando_usuario_perde(sender, instance, **kwargs):
    """Remove função do militar quando usuário perde a função"""
    try:
        # Verificar se o usuário tem militar associado
        if not hasattr(instance.usuario, 'militar') or not instance.usuario.militar:
            return
        
        militar = instance.usuario.militar
        funcao_militar = instance.funcao_militar
        
        # Verificar se há outras funções ativas do usuário
        outras_funcoes_ativas = UsuarioFuncaoMilitar.objects.filter(
            usuario=instance.usuario,
            ativo=True
        ).exists()
        
        if outras_funcoes_ativas:
            # Se há outras funções ativas, remover função atual do militar
            MilitarFuncao.objects.filter(
                militar=militar,
                funcao_militar=funcao_militar,
                status='ATUAL'
            ).update(status='ANTERIOR', data_fim=date.today())
            print(f"Função militar removida do militar {militar.matricula}: {funcao_militar.nome}")
        else:
            # Se não há outras funções ativas, manter a função mas marcar como inativa
            MilitarFuncao.objects.filter(
                militar=militar,
                funcao_militar=funcao_militar,
                status='ATUAL'
            ).update(ativo=False)
            print(f"Função militar mantida (única função) para militar {militar.matricula}: {funcao_militar.nome}")
        
    except Exception as e:
        print(f"Erro ao remover função do militar: {e}")


@receiver(post_delete, sender=MilitarFuncao)
def remover_funcao_usuario_quando_militar_perde(sender, instance, **kwargs):
    """Remove função do usuário quando militar perde a função"""
    try:
        # Verificar se o militar tem usuário associado
        if not instance.militar.user:
            return
        
        usuario = instance.militar.user
        funcao_militar = instance.funcao_militar
        
        # Verificar se há outras funções ativas do militar
        outras_funcoes_ativas = MilitarFuncao.objects.filter(
            militar=instance.militar,
            ativo=True,
            status='ATUAL'
        ).exists()
        
        if outras_funcoes_ativas:
            # Se há outras funções ativas, remover função do usuário
            UsuarioFuncaoMilitar.objects.filter(
                usuario=usuario,
                funcao_militar=funcao_militar
            ).delete()
            print(f"Função militar removida do usuário {usuario.username}: {funcao_militar.nome}")
        else:
            # Se não há outras funções ativas, manter a função mas marcar como inativa
            UsuarioFuncaoMilitar.objects.filter(
                usuario=usuario,
                funcao_militar=funcao_militar
            ).update(ativo=False)
            print(f"Função militar mantida (única função) para usuário {usuario.username}: {funcao_militar.nome}")
        
        # Se o usuário não tem mais funções ativas, atribuir função padrão
        if not UsuarioFuncaoMilitar.objects.filter(usuario=usuario, ativo=True).exists():
            atribuir_funcao_padrao_usuario(usuario)
        
    except Exception as e:
        print(f"Erro ao remover função do usuário: {e}") 


@receiver(post_save, sender=Lotacao)
def vincular_lotacao_organograma_automaticamente(sender, instance, created, **kwargs):
    """
    Vincula automaticamente a lotação ao organograma quando criada ou atualizada
    """
    try:
        # Só tentar vincular se não estiver já vinculada
        if not any([instance.orgao, instance.grande_comando, instance.unidade, instance.sub_unidade]):
            if instance.vincular_organograma_automaticamente():
                # Salvar novamente para persistir as vinculações
                instance.save(update_fields=['orgao', 'grande_comando', 'unidade', 'sub_unidade'])
                print(f"Lotacao '{instance.lotacao}' vinculada automaticamente ao organograma")
    except Exception as e:
        print(f"Erro ao vincular lotação automaticamente: {e}")


def atualizar_situacao_militar_automaticamente(militar):
    """
    Atualiza automaticamente a situação do militar baseado em afastamentos, férias e licenças ativas.
    Evita loops usando flag de controle.
    """
    if not militar or not militar.pk:
        return
    
    # Evitar loops infinitos
    if militar.pk in _atualizando_situacao:
        return
    
    try:
        _atualizando_situacao.add(militar.pk)
        
        from django.db.models import Q
        hoje = date.today()
        
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
            # Se há afastamentos ativos, usar a situação do primeiro afastamento
            primeiro_afastamento = afastamentos_ativos.order_by('data_inicio').first()
            situacao_esperada = primeiro_afastamento.tipo_afastamento
        elif ferias_ativas.exists():
            # Se há férias ativas, situação deve ser AFASTAMENTO_FERIAS
            situacao_esperada = 'AFASTAMENTO_FERIAS'
        elif licencas_ativas.exists():
            # Se há licenças ativas, situação deve ser AFASTAMENTO_LICENCA_ESPECIAL
            situacao_esperada = 'AFASTAMENTO_LICENCA_ESPECIAL'
        else:
            # Se não há nenhum afastamento, férias ou licenças ativas, situação deve ser PRONTO
            situacao_esperada = 'PRONTO'
        
        # Atualizar situação se necessário
        if militar.situacao != situacao_esperada:
            militar.situacao = situacao_esperada
            militar.save(update_fields=['situacao'])
            
    except Exception as e:
        print(f"Erro ao atualizar situação do militar {militar.nome_guerra}: {e}")
    finally:
        _atualizando_situacao.discard(militar.pk)


@receiver(post_save, sender=Ferias)
def atualizar_situacao_apos_salvar_ferias(sender, instance, **kwargs):
    """Atualiza situação do militar automaticamente após salvar férias"""
    if instance.militar:
        atualizar_situacao_militar_automaticamente(instance.militar)


@receiver(post_delete, sender=Ferias)
def atualizar_situacao_apos_deletar_ferias(sender, instance, **kwargs):
    """Atualiza situação do militar automaticamente após deletar férias"""
    if instance.militar:
        atualizar_situacao_militar_automaticamente(instance.militar)


@receiver(post_save, sender=LicencaEspecial)
def atualizar_situacao_apos_salvar_licenca(sender, instance, **kwargs):
    """Atualiza situação do militar automaticamente após salvar licença especial"""
    if instance.militar:
        atualizar_situacao_militar_automaticamente(instance.militar)


@receiver(post_delete, sender=LicencaEspecial)
def atualizar_situacao_apos_deletar_licenca(sender, instance, **kwargs):
    """Atualiza situação do militar automaticamente após deletar licença especial"""
    if instance.militar:
        atualizar_situacao_militar_automaticamente(instance.militar)


@receiver(post_save, sender=Afastamento)
def atualizar_situacao_apos_salvar_afastamento(sender, instance, **kwargs):
    """Atualiza situação do militar automaticamente após salvar afastamento"""
    if instance.militar:
        atualizar_situacao_militar_automaticamente(instance.militar)


@receiver(post_delete, sender=Afastamento)
def atualizar_situacao_apos_deletar_afastamento(sender, instance, **kwargs):
    """Atualiza situação do militar automaticamente após deletar afastamento"""
    if instance.militar:
        atualizar_situacao_militar_automaticamente(instance.militar)
