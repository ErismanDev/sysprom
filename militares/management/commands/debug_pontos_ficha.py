from django.core.management.base import BaseCommand
from militares.models import FichaConceitoOficiais, FichaConceitoPracas


class Command(BaseCommand):
    help = 'Debug dos pontos de uma ficha específica'

    def add_arguments(self, parser):
        parser.add_argument('ficha_id', type=int, help='ID da ficha de conceito')

    def handle(self, *args, **options):
        ficha_id = options['ficha_id']
        
        # Tentar buscar em ambos os modelos
        ficha = None
        try:
            ficha = FichaConceitoOficiais.objects.get(pk=ficha_id)
            tipo = 'oficiais'
        except FichaConceitoOficiais.DoesNotExist:
            try:
                ficha = FichaConceitoPracas.objects.get(pk=ficha_id)
                tipo = 'pracas'
            except FichaConceitoPracas.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Ficha com ID {ficha_id} não encontrada'))
                return
        
        self.stdout.write(f'Ficha de {tipo}: {ficha.militar.nome_completo}')
        self.stdout.write(f'Pontos salvos no banco: {ficha.pontos}')
        self.stdout.write(f'Pontos calculados: {ficha.calcular_pontos()}')
        
        # Mostrar todos os campos
        self.stdout.write('\nCampos da ficha:')
        for field in ficha._meta.fields:
            if field.name not in ['id', 'militar', 'data_registro', 'observacoes', 'pontos']:
                value = getattr(ficha, field.name)
                self.stdout.write(f'  {field.name}: {value}')
        
        # Recalcular e salvar
        pontos_antigos = ficha.pontos
        ficha.save()
        pontos_novos = ficha.pontos
        
        self.stdout.write(f'\nAntes do save: {pontos_antigos}')
        self.stdout.write(f'Depois do save: {pontos_novos}')
        self.stdout.write(f'Mudou? {pontos_antigos != pontos_novos}') 