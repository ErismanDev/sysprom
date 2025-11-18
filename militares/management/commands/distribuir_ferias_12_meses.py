from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from militares.models import PlanoFerias, Ferias, Militar
from django.contrib.auth.models import User
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Distribui militares ativos em um plano de férias, dividindo-os igualmente entre os 12 meses do ano'

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
            help='Mês inicial para distribuição (1-12, padrão: 1 - Janeiro)'
        )
        parser.add_argument(
            '--sobrescrever',
            action='store_true',
            help='Sobrescrever férias já existentes no plano'
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

        # Avisar se o plano está aprovado ou publicado (mas permitir distribuição)
        if plano.status in ['APROVADO', 'PUBLICADO']:
            self.stdout.write(self.style.WARNING(
                f'AVISO: O plano esta com status "{plano.get_status_display()}". '
                f'A distribuicao sera realizada mesmo assim.\n'
            ))

        self.stdout.write(f"Plano: {plano.titulo}")
        self.stdout.write(f"Ano de Referência: {plano.ano_referencia}")
        self.stdout.write(f"Ano do Plano (Gozo): {plano.ano_plano}")
        self.stdout.write(f"Dias de férias: {dias_ferias}")
        self.stdout.write(f"Mês inicial: {mes_inicio}\n")

        # Identificar militares com férias preservadas (já usufruídas ou em andamento)
        ferias_preservadas = plano.ferias.filter(
            Q(status='GOZADA') |  # Já usufruídas
            Q(status='GOZANDO')   # Em andamento
        )
        militares_com_ferias_preservadas = set(ferias_preservadas.values_list('militar_id', flat=True))
        
        # Identificar todos os militares com férias no plano (exceto reprogramadas)
        militares_com_ferias = set(plano.ferias.exclude(status='REPROGRAMADA').values_list('militar_id', flat=True))

        if sobrescrever:
            # Remover apenas férias planejadas e futuras (preservar GOZADA e GOZANDO)
            ferias_para_remover = plano.ferias.filter(
                Q(status='PLANEJADA') |  # Apenas planejadas
                Q(status='CANCELADA')    # Canceladas também podem ser removidas
            ).exclude(
                status__in=['GOZADA', 'GOZANDO']  # Nunca remover essas
            )
            count_removidas = ferias_para_remover.count()
            
            if not dry_run:
                ferias_para_remover.delete()
            
            self.stdout.write(self.style.WARNING(f'{count_removidas} férias planejadas/futuras serão removidas para redistribuição.'))
            self.stdout.write(self.style.SUCCESS(f'{ferias_preservadas.count()} férias usufruídas/em andamento serão preservadas.'))
            
            # Buscar todos os militares ativos, mas excluir os que têm férias preservadas
            # (eles não serão redistribuídos)
            militares = Militar.objects.filter(
                classificacao='ATIVO'
            ).exclude(
                id__in=militares_com_ferias_preservadas
            ).order_by('posto_graduacao', 'data_promocao_atual', 'numeracao_antiguidade')
        else:
            # Buscar apenas militares que ainda não têm férias no plano
            militares = Militar.objects.filter(
                classificacao='ATIVO'
            ).exclude(
                id__in=militares_com_ferias
            ).order_by('posto_graduacao', 'data_promocao_atual', 'numeracao_antiguidade')

        total_militares = militares.count()

        if total_militares == 0:
            raise CommandError('Nenhum militar encontrado para distribuir.')

        self.stdout.write(f"Total de militares a distribuir: {total_militares}\n")

        # Calcular distribuição
        militares_lista = list(militares)
        militares_por_mes = total_militares // 12
        resto = total_militares % 12

        self.stdout.write(f"Distribuição: {militares_por_mes} militares por mês, {resto} meses com +1\n")

        ano_gozo = plano.ano_plano
        ano_referencia = plano.ano_referencia

        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        # Obter usuário para cadastro
        try:
            usuario = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if not usuario:
                raise CommandError('Nenhum usuário encontrado no sistema para registrar o cadastro')
        except:
            usuario = None

        ferias_criadas = 0
        indice_militar = 0

        try:
            with transaction.atomic():
                # Distribuir entre os 12 meses
                for i in range(12):
                    # Calcular o mês (ciclo de 12 meses começando do mês inicial)
                    mes = ((mes_inicio - 1 + i) % 12) + 1
                    
                    # Calcular data de início (primeiro dia do mês)
                    data_inicio = date(ano_gozo, mes, 1)
                    
                    # Calcular quantos militares para este mês
                    militares_neste_mes = militares_por_mes
                    if i < resto:
                        militares_neste_mes += 1
                    
                    # Pegar os militares para este mês
                    militares_mes = militares_lista[indice_militar:indice_militar + militares_neste_mes]
                    indice_militar += militares_neste_mes
                    
                    if not militares_mes:
                        continue
                    
                    # Calcular data de fim
                    data_fim = data_inicio + timedelta(days=dias_ferias - 1)

                    self.stdout.write(f"{meses_nomes[mes]}/{ano_gozo}: {len(militares_mes)} militares")
                    self.stdout.write(f"  Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")

                    if not dry_run:
                        # Criar férias para cada militar
                        # (militares com férias preservadas já foram excluídos da lista)
                        for militar in militares_mes:
                            Ferias.objects.create(
                                plano=plano,
                                militar=militar,
                                tipo='INTEGRAL',
                                ano_referencia=ano_referencia,
                                data_inicio=data_inicio,
                                data_fim=data_fim,
                                quantidade_dias=dias_ferias,
                                status='PLANEJADA',
                                cadastrado_por=usuario
                            )
                            ferias_criadas += 1
                            self.stdout.write(f"    [OK] {militar.get_posto_graduacao_display()} {militar.nome_completo}")
                    else:
                        # Modo dry-run, apenas listar
                        for militar in militares_mes:
                            self.stdout.write(f"    [DRY-RUN] {militar.get_posto_graduacao_display()} {militar.nome_completo}")
                            ferias_criadas += 1

                    self.stdout.write("")

            if not dry_run:
                self.stdout.write(self.style.SUCCESS(
                    f'\nDistribuicao concluida com sucesso!\n'
                    f'{ferias_criadas} ferias criadas distribuidas entre os 12 meses do ano {ano_gozo}.'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'\n[DRY-RUN] Seriam criadas {ferias_criadas} férias distribuídas entre os 12 meses.'
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nERRO ao distribuir militares: {str(e)}'))
            raise CommandError(f'Erro ao distribuir militares: {str(e)}')

