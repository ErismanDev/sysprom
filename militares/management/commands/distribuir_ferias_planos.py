from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from militares.models import PlanoFerias, Ferias, Militar
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from calendar import monthrange
import math


class Command(BaseCommand):
    help = 'Distribui todos os militares ativos em um plano de férias, dividindo-os igualmente entre os 12 meses do ano'

    def add_arguments(self, parser):
        parser.add_argument(
            'plano_id',
            type=int,
            help='ID do plano de férias onde os militares serão distribuídos'
        )
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Quantidade de dias de férias por militar (padrão: 30)'
        )
        parser.add_argument(
            '--mes-inicio',
            type=int,
            default=1,
            help='Mês inicial para distribuição (1-12, padrão: 1)'
        )
        parser.add_argument(
            '--sobrescrever',
            action='store_true',
            help='Sobrescrever férias já existentes no plano para os militares'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar'
        )

    def handle(self, *args, **options):
        plano_id = options['plano_id']
        dias_ferias = options['dias']
        mes_inicio = options['mes_inicio']
        sobrescrever = options['sobrescrever']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita\n'))

        # Validar mês inicial
        if mes_inicio < 1 or mes_inicio > 12:
            raise CommandError('--mes-inicio deve estar entre 1 e 12')

        # Buscar plano de férias
        try:
            plano = PlanoFerias.objects.get(pk=plano_id)
        except PlanoFerias.DoesNotExist:
            raise CommandError(f'Plano de férias com ID {plano_id} não encontrado')

        self.stdout.write(f"Plano: {plano.titulo}")
        self.stdout.write(f"Ano de Referência: {plano.ano_referencia}")
        self.stdout.write(f"Ano do Plano: {plano.ano_plano}\n")

        # Buscar todos os militares ativos
        militares = Militar.objects.exclude(situacao='INATIVO').order_by('posto_graduacao', 'data_promocao_atual', 'numeracao_antiguidade')
        total_militares = militares.count()

        if total_militares == 0:
            raise CommandError('Nenhum militar ativo encontrado')

        self.stdout.write(f"Total de militares ativos: {total_militares}")

        # Data de referência: amanhã (para só reprogramar meses futuros)
        amanha = date.today() + timedelta(days=1)
        
        hoje = date.today()
        
        # Verificar férias existentes
        ferias_existentes = plano.ferias.count()
        
        # Férias para preservar: já usufruídas ou de meses passados (completas)
        ferias_para_preservar = plano.ferias.filter(
            Q(status='GOZADA') |
            # Preservar férias de meses passados que já terminaram completamente
            Q(data_fim__lt=amanha)
        )
        
        # Férias em andamento que começaram antes de amanhã (precisam calcular dias gozados)
        ferias_em_andamento = plano.ferias.filter(
            status='GOZANDO',
            data_inicio__lt=amanha,
            data_fim__gte=amanha  # Ainda não terminou
        )
        
        # Férias futuras para reprogramar completamente
        ferias_para_reprogramar = plano.ferias.exclude(
            # Excluir as que devem ser preservadas ou estão em andamento
            Q(status='GOZADA') | Q(data_fim__lt=amanha) | 
            Q(status='GOZANDO', data_inicio__lt=amanha, data_fim__gte=amanha)
        )
        
        if ferias_existentes > 0:
            self.stdout.write(self.style.WARNING(f"Aviso: Já existem {ferias_existentes} férias cadastradas no plano"))
            self.stdout.write(f"  - {ferias_para_preservar.count()} serão preservadas (já usufruídas ou meses passados)")
            self.stdout.write(f"  - {ferias_em_andamento.count()} estão em andamento (salvar dias gozados e reprogramar restante)")
            self.stdout.write(f"  - {ferias_para_reprogramar.count()} serão reprogramadas (próximos meses)")
            
            if not sobrescrever:
                self.stdout.write(self.style.WARNING("\nUse --sobrescrever para reprogramar férias futuras\n"))
        
        # Dicionário para armazenar dias restantes de militares com férias em andamento
        # chave: militar_id, valor: dias_restantes
        militares_dias_restantes = {}
        
        if sobrescrever and not dry_run:
            # Processar férias em andamento primeiro
            ferias_reprogramadas_com_dias_gozados = 0
            for ferias_andamento in ferias_em_andamento:
                # Calcular dias já gozados (desde data_inicio até hoje, inclusive)
                dias_ja_gozados = (hoje - ferias_andamento.data_inicio).days + 1
                dias_restantes = ferias_andamento.quantidade_dias - dias_ja_gozados
                
                if dias_restantes <= 0:
                    # Todos os dias já foram gozados, apenas marcar como GOZADA
                    ferias_andamento.status = 'GOZADA'
                    if ferias_andamento.observacoes:
                        ferias_andamento.observacoes += f"\n\nAutomático: Férias concluída durante reprogramação do plano."
                    else:
                        ferias_andamento.observacoes = "Automático: Férias concluída durante reprogramação do plano."
                    ferias_andamento.save()
                    self.stdout.write(f"  ⚠️  {ferias_andamento.militar.nome_guerra} - Todos os {dias_ja_gozados} dias já foram gozados")
                else:
                    # Salvar informação dos dias gozados na observação
                    obs_original = ferias_andamento.observacoes or ""
                    obs_original += f"\n\nREPROGRAMAÇÃO: {dias_ja_gozados} dias já gozados (de {ferias_andamento.data_inicio.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}). {dias_restantes} dias restantes serão reprogramados."
                    
                    # Marcar como reprogramada
                    ferias_andamento.status = 'REPROGRAMADA'
                    ferias_andamento.observacoes = obs_original
                    ferias_andamento.save()
                    
                    # Armazenar dias restantes para usar na redistribuição
                    militares_dias_restantes[ferias_andamento.militar_id] = dias_restantes
                    ferias_reprogramadas_com_dias_gozados += 1
                    self.stdout.write(f"  📝 {ferias_andamento.militar.nome_guerra} - {dias_ja_gozados} dias gozados, {dias_restantes} dias restantes a reprogramar")
            
            # Remover férias futuras que devem ser reprogramadas completamente
            count_removidas = ferias_para_reprogramar.count()
            ferias_para_reprogramar.delete()
            
            if ferias_reprogramadas_com_dias_gozados > 0:
                self.stdout.write(f"\n{ferias_reprogramadas_com_dias_gozados} férias em andamento processadas (dias gozados salvos)")
            self.stdout.write(f"{count_removidas} férias futuras foram removidas para reprogramação\n")

        # Distribuir militares entre os 12 meses
        militares_lista = list(militares)
        total_militares = len(militares_lista)
        militares_por_mes = total_militares // 12
        resto = total_militares % 12
        
        self.stdout.write(f"Distribuição: {militares_por_mes} por mês, {resto} meses com +1\n")

        # Meses em português para exibição
        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        # Obter usuário para cadastro (primeiro superusuário ou primeiro usuário)
        try:
            usuario = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if not usuario:
                raise CommandError('Nenhum usuário encontrado no sistema para registrar o cadastro')
        except:
            usuario = None

        ano_referencia = plano.ano_referencia
        ano_gozo = plano.ano_plano  # Ano em que as férias serão gozadas
        
        # Data de referência: amanhã (para só reprogramar meses futuros)
        amanha = date.today() + timedelta(days=1)
        
        self.stdout.write(f"Ano de Referência: {ano_referencia}")
        self.stdout.write(f"Ano de Gozo: {ano_gozo}")
        self.stdout.write(f"Data de referência: {amanha.strftime('%d/%m/%Y')}")
        self.stdout.write(f"Meses anteriores a esta data serão preservados.\n")
        
        ferias_criadas = 0
        ferias_removidas = 0
        meses_preservados = []
        meses_reprogramados = []
        
        # Primeiro, identificar quais meses são futuros (baseado no ano de gozo)
        for i in range(12):
            mes = ((mes_inicio - 1 + i) % 12) + 1
            data_inicio_mes = date(ano_gozo, mes, 1)  # Usar ano_gozo, não ano_referencia
            if data_inicio_mes < amanha:
                meses_preservados.append(mes)
            else:
                meses_reprogramados.append(mes)
        
        total_meses_futuros = len(meses_reprogramados)
        # Sempre distribuir nos 12 meses do ano de gozo
        total_meses_para_distribuir = 12
        meses_reprogramados = list(range(1, 13))  # Todos os 12 meses
        
        self.stdout.write(f"\nDistribuindo nos 12 meses do ano de gozo ({ano_gozo})")
        
        # Recalcular distribuição para os meses que serão distribuídos
        militares_por_mes_futuro = total_militares // total_meses_para_distribuir if total_meses_para_distribuir > 0 else 0
        resto_futuros = total_militares % total_meses_para_distribuir if total_meses_para_distribuir > 0 else 0
        
        self.stdout.write(f"Distribuição: {militares_por_mes_futuro} por mês, {resto_futuros} meses com +1\n")

        indice_militar = 0

        try:
            with transaction.atomic():
                # Percorrer os 12 meses começando do mês inicial
                for i in range(12):
                    # Calcular o mês (ciclo de 12 meses)
                    mes = ((mes_inicio - 1 + i) % 12) + 1
                    
                    # Calcular data de início (primeiro dia do mês) - usar ano_gozo, não ano_referencia
                    data_inicio = date(ano_gozo, mes, 1)
                    
                    # Sempre distribuir nos 12 meses, mesmo que alguns já tenham passado
                    # Usar índice sequencial (0-11) para todos os meses
                    indice_mes_futuro = i
                    
                    # Calcular quantos militares para este mês futuro
                    militares_neste_mes = militares_por_mes_futuro
                    if indice_mes_futuro < resto_futuros:
                        militares_neste_mes += 1
                    
                    # Pegar os militares para este mês
                    militares_mes = militares_lista[indice_militar:indice_militar + militares_neste_mes]
                    indice_militar += militares_neste_mes
                    
                    if not militares_mes:
                        continue

                    # Calcular data de fim (baseado na quantidade de dias)
                    # Adicionar dias_ferias - 1 porque o primeiro dia conta
                    data_fim = data_inicio + timedelta(days=dias_ferias - 1)

                    self.stdout.write(f"\n{meses_nomes[mes]}/{ano_gozo}: {len(militares_mes)} militares")
                    self.stdout.write(f"  Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")

                    for militar in militares_mes:
                        # Verificar se este militar tem dias restantes de férias em andamento
                        dias_para_este_militar = militares_dias_restantes.get(militar.id, dias_ferias)
                        
                        # Se tem dias restantes menores que o padrão, usar os dias restantes
                        if dias_para_este_militar < dias_ferias:
                            data_fim_ajustada = data_inicio + timedelta(days=dias_para_este_militar - 1)
                            obs_ferias = f"Reprogramação parcial: {dias_para_este_militar} dias restantes de férias anteriormente em andamento."
                        else:
                            data_fim_ajustada = data_fim
                            obs_ferias = None
                        
                        if not dry_run:
                            Ferias.objects.create(
                                plano=plano,
                                militar=militar,
                                tipo='INTEGRAL',
                                ano_referencia=ano_referencia,
                                data_inicio=data_inicio,
                                data_fim=data_fim_ajustada,
                                quantidade_dias=dias_para_este_militar,
                                status='PLANEJADA',
                                observacoes=obs_ferias,
                                cadastrado_por=usuario
                            )
                        
                        if dias_para_este_militar < dias_ferias:
                            self.stdout.write(f"  ✅ {militar.nome_guerra} ({militar.get_posto_graduacao_display()}) - {dias_para_este_militar} dias restantes")
                        else:
                            self.stdout.write(f"  ✅ {militar.nome_guerra} ({militar.get_posto_graduacao_display()})")
                        ferias_criadas += 1
                        
                        # Remover do dicionário após criar a férias
                        if militar.id in militares_dias_restantes:
                            del militares_dias_restantes[militar.id]

                if dry_run:
                    raise Exception("DRY_RUN")

        except Exception as e:
            if str(e) == "DRY_RUN":
                pass  # Esperado no dry-run
            else:
                raise

        # Estatísticas finais
        self.stdout.write(f"\n{'='*60}")
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'DRY-RUN: {ferias_criadas} férias seriam criadas'))
        else:
            self.stdout.write(self.style.SUCCESS(f'SUCESSO: {ferias_criadas} férias foram criadas'))
        
        # Distribuição por mês
        if not dry_run:
            self.stdout.write(f"\nDistribuição final:")
            for i in range(12):
                mes = ((mes_inicio - 1 + i) % 12) + 1
                count = plano.ferias.filter(data_inicio__month=mes, data_inicio__year=ano_referencia).count()
                if count > 0:
                    self.stdout.write(f"  {meses_nomes[mes]}: {count} férias")

