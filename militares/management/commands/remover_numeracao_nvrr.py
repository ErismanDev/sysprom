from django.core.management.base import BaseCommand
from militares.models import Militar


class Command(BaseCommand):
    help = 'Remove a numeração de antiguidade dos militares NVRR'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executar em modo de teste (não salva as alterações)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar informações detalhadas'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']

        self.stdout.write(
            self.style.SUCCESS('Iniciando remoção de numeração de antiguidade dos militares NVRR...')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DE TESTE - Nenhuma alteração será salva')
            )

        try:
            # Buscar militares NVRR ativos
            militares_nvrr = Militar.objects.filter(
                posto_graduacao='NVRR',
                situacao='AT'
            )

            total_militares = militares_nvrr.count()
            militares_com_numeracao = militares_nvrr.filter(numeracao_antiguidade__isnull=False).count()

            self.stdout.write(f'Total de militares NVRR encontrados: {total_militares}')
            self.stdout.write(f'Militares NVRR com numeração: {militares_com_numeracao}')

            if verbose:
                self.stdout.write('\nMilitares NVRR com numeração:')
                for militar in militares_nvrr.filter(numeracao_antiguidade__isnull=False):
                    self.stdout.write(
                        f'  - {militar.nome_completo} (Matrícula: {militar.matricula}) - '
                        f'Numeração atual: {militar.numeracao_antiguidade}'
                    )

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS('\nSimulação concluída! Nenhuma alteração foi feita.')
                )
            else:
                # Remover numeração dos militares NVRR
                militares_alterados = militares_nvrr.filter(numeracao_antiguidade__isnull=False)
                
                for militar in militares_alterados:
                    militar.numeracao_antiguidade = None
                    militar.save(update_fields=['numeracao_antiguidade'])
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nRemoção concluída com sucesso! {militares_alterados.count()} militares NVRR tiveram sua numeração removida.'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao remover numeração: {str(e)}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS('\nOperação concluída!')
        ) 