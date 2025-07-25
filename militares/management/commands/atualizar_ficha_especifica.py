from django.core.management.base import BaseCommand
from militares.models import FichaConceitoPracas


class Command(BaseCommand):
    help = 'Atualiza uma ficha específica de praças'

    def add_arguments(self, parser):
        parser.add_argument('ficha_id', type=int, help='ID da ficha de conceito de praças')

    def handle(self, *args, **options):
        ficha_id = options['ficha_id']
        
        try:
            ficha = FichaConceitoPracas.objects.get(pk=ficha_id)
        except FichaConceitoPracas.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Ficha com ID {ficha_id} não encontrada'))
            return
        
        self.stdout.write(f'Ficha: {ficha.militar.nome_completo}')
        self.stdout.write(f'Pontos antes: {ficha.pontos}')
        
        # Forçar recálculo
        ficha.save()
        
        self.stdout.write(f'Pontos depois: {ficha.pontos}')
        self.stdout.write(f'Pontos calculados: {ficha.calcular_pontos()}')
        
        # Mostrar todos os campos
        self.stdout.write('\nCampos da ficha:')
        for field in ficha._meta.fields:
            if field.name not in ['id', 'militar', 'data_registro', 'observacoes', 'pontos']:
                value = getattr(ficha, field.name)
                self.stdout.write(f'  {field.name}: {value}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Ficha atualizada com sucesso!')
        ) 