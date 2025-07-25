from django.core.management.base import BaseCommand
from militares.models import Intersticio


class Command(BaseCommand):
    help = 'Remove registros incorretos de interstícios no quadro de praças'

    def handle(self, *args, **options):
        # Postos que NÃO pertencem ao quadro de praças
        postos_incorretos_pracas = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
        
        # Buscar interstícios incorretos no quadro de praças
        intersticios_incorretos = Intersticio.objects.filter(
            quadro='PRACAS',
            posto__in=postos_incorretos_pracas
        )
        
        if intersticios_incorretos.exists():
            self.stdout.write(f'Encontrados {intersticios_incorretos.count()} registros incorretos:')
            for inter in intersticios_incorretos:
                self.stdout.write(f'  - {inter.get_posto_display()} no quadro de praças')
            
            # Confirmar exclusão
            confirmacao = input('\nDeseja excluir estes registros? (s/N): ')
            if confirmacao.lower() in ['s', 'sim', 'y', 'yes']:
                intersticios_incorretos.delete()
                self.stdout.write(self.style.SUCCESS('Registros incorretos removidos com sucesso!'))
            else:
                self.stdout.write('Operação cancelada.')
        else:
            self.stdout.write(self.style.SUCCESS('Nenhum registro incorreto encontrado.'))
        
        # Mostrar estatísticas atuais
        self.stdout.write('\nEstatísticas atuais:')
        for quadro in ['COMB', 'SAUDE', 'ENG', 'COMP', 'PRACAS']:
            count = Intersticio.objects.filter(quadro=quadro).count()
            self.stdout.write(f'  {quadro}: {count} interstícios') 