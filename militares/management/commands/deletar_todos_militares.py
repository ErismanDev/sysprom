from django.core.management.base import BaseCommand
from militares.models import Militar

class Command(BaseCommand):
    help = 'Deleta todos os registros da tabela Militar.'

    def handle(self, *args, **options):
        total = Militar.objects.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum militar encontrado para deletar.'))
            return
        Militar.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Todos os {total} militares foram deletados com sucesso.')) 