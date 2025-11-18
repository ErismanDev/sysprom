from django.core.management.base import BaseCommand
from militares.models import EscalaMilitar

class Command(BaseCommand):
    help = 'Verifica militares escalados'

    def handle(self, *args, **kwargs):
        self.stdout.write('Verificando militares escalados:')
        
        total = EscalaMilitar.objects.count()
        self.stdout.write(f'Total de militares escalados: {total}')
        
        if total > 0:
            for em in EscalaMilitar.objects.all()[:10]:
                self.stdout.write(f'  {em.militar.nome_completo} - {em.escala.data} - {em.escala.organizacao}')
        else:
            self.stdout.write('Nenhum militar escalado encontrado!')
