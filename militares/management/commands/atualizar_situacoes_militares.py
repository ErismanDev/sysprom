#!/usr/bin/env python3
"""
Comando de management para atualizar automaticamente a situação dos militares
baseado em afastamentos, férias e licenças ativas até a data atual.
Executar: python manage.py atualizar_situacoes_militares
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from datetime import date
from militares.models import Militar, Afastamento, Ferias, LicencaEspecial


class Command(BaseCommand):
    help = 'Atualiza automaticamente a situação dos militares baseado em afastamentos, férias e licenças ativas até a data atual'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria atualizado sem fazer alterações',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas',
        )
        parser.add_argument(
            '--atualizar-ferias',
            action='store_true',
            help='Também atualiza férias vencidas antes de sincronizar situações',
        )

    def handle(self, *args, **options):
        hoje = date.today()
        
        # 1. Encerrar afastamentos vencidos (status ATIVO com data_fim_prevista < hoje)
        self.stdout.write(self.style.SUCCESS('[1/3] Verificando afastamentos vencidos...'))
        afastamentos_vencidos = Afastamento.objects.filter(
            status='ATIVO',
            data_fim_prevista__lt=hoje,
            data_fim_real__isnull=True
        )
        
        total_afastamentos = afastamentos_vencidos.count()
        if total_afastamentos > 0:
            self.stdout.write(f'📋 Encontrados {total_afastamentos} afastamentos vencidos.')
            for afastamento in afastamentos_vencidos:
                if not options['dry_run']:
                    afastamento.status = 'ENCERRADO'
                    afastamento.data_fim_real = afastamento.data_fim_prevista
                    afastamento.save(update_fields=['status', 'data_fim_real'])
                if options['verbose']:
                    self.stdout.write(f"  - {afastamento.militar.nome_guerra}: Afastamento #{afastamento.pk} encerrado")
            if not options['dry_run']:
                self.stdout.write(self.style.SUCCESS(f'✅ {total_afastamentos} afastamentos encerrados.'))
        else:
            self.stdout.write('✅ Nenhum afastamento vencido encontrado.')
        
        self.stdout.write('')
        
        # 2. Se solicitado, atualizar férias vencidas
        if options['atualizar_ferias']:
            self.stdout.write(self.style.SUCCESS('[2/3] Atualizando férias vencidas...'))
            
            ferias_vencidas = Ferias.objects.filter(
                status='GOZANDO',
                data_fim__lt=hoje
            )
            
            total_ferias = ferias_vencidas.count()
            if total_ferias > 0:
                self.stdout.write(f'📋 Encontradas {total_ferias} férias vencidas.')
                for ferias in ferias_vencidas:
                    if not options['dry_run']:
                        ferias.status = 'GOZADA'
                        ferias.save(update_fields=['status'])
                    if options['verbose']:
                        self.stdout.write(f"  - {ferias.militar.nome_guerra}: Férias atualizada para GOZADA")
                if not options['dry_run']:
                    self.stdout.write(self.style.SUCCESS(f'✅ {total_ferias} férias atualizadas.'))
            else:
                self.stdout.write('✅ Nenhuma férias vencida encontrada.')
            
            self.stdout.write('')
        
        # 3. Sincronizar situações dos militares
        if options['atualizar_ferias']:
            self.stdout.write(self.style.SUCCESS('[3/3] Verificando situações dos militares...'))
        else:
            self.stdout.write(self.style.SUCCESS('[2/2] Verificando situações dos militares...'))
        
        # Buscar todos os militares ativos
        militares_ativos = Militar.objects.filter(classificacao='ATIVO')
        
        total = militares_ativos.count()
        self.stdout.write(f'📋 Total de militares ativos: {total}')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('[DRY RUN] Nenhuma alteração será feita.'))
        
        atualizados = 0
        
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
            
            # Verificar se a situação atual está correta
            if militar.situacao != situacao_esperada:
                if options['verbose'] or options['dry_run']:
                    # Criar um objeto temporário para obter o display da situação esperada
                    temp_militar = Militar(situacao=situacao_esperada)
                    self.stdout.write(
                        f"  - {militar.nome_guerra}: "
                        f"Situação atual: {militar.get_situacao_display()} → "
                        f"Situação esperada: {temp_militar.get_situacao_display()}"
                    )
                
                if not options['dry_run']:
                    militar.situacao = situacao_esperada
                    militar.save(update_fields=['situacao'])
                    atualizados += 1
        
        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {atualizados} militares atualizados.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] {atualizados} militares seriam atualizados.')
            )

