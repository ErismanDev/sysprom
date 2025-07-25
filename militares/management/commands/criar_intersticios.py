from django.core.management.base import BaseCommand
from militares.models import Intersticio, POSTO_GRADUACAO_CHOICES, QUADRO_CHOICES


class Command(BaseCommand):
    help = 'Cria dados iniciais de interstícios para todos os postos e quadros'

    def handle(self, *args, **options):
        # Valores padrão de interstício (em anos)
        intersticios_padrao = {
            'AS': 0.5,  # 6 meses como Aspirante para 2º Tenente
            'AA': 0.5,  # 6 meses como Aluno de Adaptação para 2º Tenente
            '2T': 3,    # 3 anos como 2º Tenente para 1º Tenente
            '1T': 4,    # 4 anos como 1º Tenente para Capitão
            'CP': 4,    # 4 anos como Capitão para Major
            'MJ': 4,    # 4 anos como Major para Tenente-Coronel
            'TC': 3,    # 3 anos como Tenente-Coronel para Coronel
        }

        # Postos que não têm interstício (último posto)
        postos_sem_intersticio = ['CB', 'ST', '1S', '2S', '3S', 'CB', 'SD']

        criados = 0
        atualizados = 0

        for quadro in QUADRO_CHOICES:
            quadro_codigo = quadro[0]
            for posto in POSTO_GRADUACAO_CHOICES:
                posto_codigo = posto[0]
                
                # Pular postos que não têm interstício
                if posto_codigo in postos_sem_intersticio:
                    continue
                
                # Obter tempo padrão para o posto
                tempo_padrao = intersticios_padrao.get(posto_codigo, 0)
                anos = int(tempo_padrao)
                meses = int((tempo_padrao - anos) * 12)
                
                # Criar ou atualizar interstício
                intersticio, created = Intersticio.objects.get_or_create(
                    posto=posto_codigo,
                    quadro=quadro_codigo,
                    defaults={
                        'tempo_minimo_anos': anos,
                        'tempo_minimo_meses': meses,
                        'ativo': True
                    }
                )
                
                if created:
                    criados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Criado: {posto[1]} - {quadro[1]} ({anos}a {meses}m)'
                        )
                    )
                else:
                    atualizados += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Já existe: {posto[1]} - {quadro[1]}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {criados} interstícios criados, {atualizados} já existiam.'
            )
        ) 