from django.core.management.base import BaseCommand
from militares.models import Militar

class Command(BaseCommand):
    help = 'Reordena a antiguidade de todos os militares de um grupo (ex: Coronéis Combatentes Ativos)'

    def add_arguments(self, parser):
        parser.add_argument('--posto', type=str, required=True, help='Posto/Graduação (ex: CB)')
        parser.add_argument('--quadro', type=str, required=True, help='Quadro (ex: COMB)')

    def handle(self, *args, **options):
        posto = options['posto']
        quadro = options['quadro']
        
        militares = Militar.objects.filter(
            classificacao='ATIVO',
            posto_graduacao=posto,
            quadro=quadro
        ).order_by('numeracao_antiguidade', 'pk')
        
        self.stdout.write(f'Encontrados {militares.count()} militares para reordenar ({posto} - {quadro})')
        
        for i, militar in enumerate(militares, 1):
            if militar.numeracao_antiguidade != i:
                self.stdout.write(f'Corrigindo {militar.nome_completo}: {militar.numeracao_antiguidade} -> {i}')
                militar.numeracao_antiguidade = i
                militar.save(update_fields=['numeracao_antiguidade'])
        
        self.stdout.write(self.style.SUCCESS('Reordenação concluída!')) 