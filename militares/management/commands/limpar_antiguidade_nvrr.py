from django.core.management.base import BaseCommand
from militares.models import Militar


class Command(BaseCommand):
    help = 'Remove a numeração de antiguidade de militares do NVRR'

    def handle(self, *args, **options):
        # Buscar militares do NVRR
        militares_nvrr = Militar.objects.filter(
            numeracao_antiguidade__isnull=False
        ).filter(
            quadro='NVRR'
        ) | Militar.objects.filter(
            numeracao_antiguidade__isnull=False
        ).filter(
            posto_graduacao='NVRR'
        )
        
        count = 0
        for militar in militares_nvrr:
            self.stdout.write(
                f'Removendo antiguidade do militar: {militar.nome_completo} '
                f'(Antiguidade anterior: {militar.numeracao_antiguidade})'
            )
            militar.numeracao_antiguidade = None
            militar.save()
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processo concluído! {count} militares do NVRR tiveram sua '
                f'numeração de antiguidade removida.'
            )
        ) 