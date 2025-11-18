from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from militares.models import Militar, Vaga, PrevisaoVaga
from collections import defaultdict


class Command(BaseCommand):
    help = 'Atualiza automaticamente o efetivo atual nas vagas baseado nos militares cadastrados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar as alterações (modo de teste)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('[INICIANDO] Atualização automática do efetivo nas vagas...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  MODO DE TESTE - Nenhuma alteração será salva')
            )
        
        # Contar militares por posto e quadro
        efetivo_por_posto_quadro = defaultdict(int)
        
        # Buscar todos os militares ativos
        militares_ativos = Militar.objects.filter(classificacao='ATIVO')
        
        self.stdout.write(f'📊 Total de militares ativos: {militares_ativos.count()}')
        
        # Contar efetivo por posto e quadro
        for militar in militares_ativos:
            key = (militar.posto_graduacao, militar.quadro)
            efetivo_por_posto_quadro[key] += 1
            
            if verbose:
                self.stdout.write(
                    f'  ✅ {militar.nome_completo} - {militar.get_posto_graduacao_display()} - {militar.get_quadro_display()}'
                )
        
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
                # Mapear posto para o formato das vagas
                posto_vaga = mapeamento_postos.get(posto_militar)
                
                if not posto_vaga:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Posto não mapeado: {posto_militar}')
                    )
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
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'🆕 Criada vaga: {vaga.get_posto_display()} - {vaga.get_quadro_display()} '
                            f'(Efetivo: {efetivo_atual})'
                        )
                    )
                else:
                    # Atualizar efetivo atual
                    if vaga.efetivo_atual != efetivo_atual:
                        efetivo_anterior = vaga.efetivo_atual
                        vaga.efetivo_atual = efetivo_atual
                        
                        if not dry_run:
                            vaga.save()
                        
                        vagas_atualizadas += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'[ATUALIZADA] Vaga: {vaga.get_posto_display()} - {vaga.get_quadro_display()} '
                                f'(Efetivo: {efetivo_anterior} → {efetivo_atual})'
                            )
                        )
                    elif verbose:
                        self.stdout.write(
                            f'  ℹ️  Vaga já atualizada: {vaga.get_posto_display()} - {vaga.get_quadro_display()} '
                            f'(Efetivo: {efetivo_atual})'
                        )
            
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
                        efetivo_anterior = previsao.efetivo_atual
                        previsao.efetivo_atual = efetivo_atual
                        
                        if not dry_run:
                            previsao.save()
                        
                        previsoes_atualizadas += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'📈 Atualizada previsão: {previsao.get_posto_display()} - {previsao.get_quadro_display()} '
                                f'(Efetivo: {efetivo_anterior} → {efetivo_atual})'
                            )
                        )
                    elif verbose:
                        self.stdout.write(
                            f'  ℹ️  Previsão já atualizada: {previsao.get_posto_display()} - {previsao.get_quadro_display()} '
                            f'(Efetivo: {efetivo_atual})'
                        )
                        
                except PrevisaoVaga.DoesNotExist:
                    if verbose:
                        self.stdout.write(
                            f'  ⚠️  Previsão não encontrada: {posto_vaga} - {quadro_militar}'
                        )
        
        # Resumo final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RESUMO DA ATUALIZAÇÃO'))
        self.stdout.write('='*60)
        self.stdout.write(f'👥 Militares ativos processados: {militares_ativos.count()}')
        self.stdout.write(f'🆕 Vagas criadas: {vagas_criadas}')
        self.stdout.write(f'[RESULTADO] Vagas atualizadas: {vagas_atualizadas}')
        self.stdout.write(f'📈 Previsões atualizadas: {previsoes_atualizadas}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  MODO DE TESTE - Nenhuma alteração foi salva')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Atualização concluída com sucesso!')
            )
        
        # Mostrar efetivo por posto/quadro
        if verbose:
            self.stdout.write('\n📋 EFETIVO POR POSTO/QUADRO:')
            self.stdout.write('-'*40)
            for (posto, quadro), efetivo in sorted(efetivo_por_posto_quadro.items()):
                self.stdout.write(f'  {posto} - {quadro}: {efetivo} militares') 