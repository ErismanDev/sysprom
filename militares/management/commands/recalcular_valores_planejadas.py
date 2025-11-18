from django.core.management.base import BaseCommand
from militares.models import Planejada


class Command(BaseCommand):
    help = 'Recalcula os valores totais de todas as planejadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar as alterações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        planejadas = Planejada.objects.all()
        total_planejadas = planejadas.count()
        atualizadas = 0
        
        self.stdout.write(f'Encontradas {total_planejadas} planejadas para verificar...')
        
        for planejada in planejadas:
            valor_anterior = planejada.valor_total
            valor_calculado = planejada.valor * planejada.policiais
            
            if valor_anterior != valor_calculado:
                self.stdout.write(
                    f'Planejada ID {planejada.id} - {planejada.nome}: '
                    f'R$ {valor_anterior:.2f} -> R$ {valor_calculado:.2f}'
                )
                
                if not dry_run:
                    planejada.valor_total = valor_calculado
                    planejada.save(update_fields=['valor_total'])
                    atualizadas += 1
                else:
                    atualizadas += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: {atualizadas} planejadas seriam atualizadas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'{atualizadas} planejadas foram atualizadas com sucesso!')
            )
