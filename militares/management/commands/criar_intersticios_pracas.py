from django.core.management.base import BaseCommand
from militares.models import Intersticio


class Command(BaseCommand):
    help = 'Cria interstícios para o quadro de praças bombeiros militares'

    def handle(self, *args, **options):
        # Interstícios para praças (em anos e meses)
        intersticios_pracas = {
            'SD': {'anos': 0, 'meses': 6},      # Soldado: 6 meses para Cabo
            'CAB': {'anos': 2, 'meses': 0},      # Cabo: 2 anos para 3º Sargento
            '3S': {'anos': 2, 'meses': 0},      # 3º Sargento: 2 anos para 2º Sargento
            '2S': {'anos': 3, 'meses': 0},      # 2º Sargento: 3 anos para 1º Sargento
            '1S': {'anos': 0, 'meses': 0},      # 1º Sargento: posto máximo (sem interstício)
        }

        quadro_pracas = 'PRACAS'  # Quadro específico para praças
        criados = 0
        atualizados = 0

        for posto_codigo, tempo in intersticios_pracas.items():
            anos = tempo['anos']
            meses = tempo['meses']
            
            # Criar ou atualizar interstício
            intersticio, created = Intersticio.objects.get_or_create(
                posto=posto_codigo,
                quadro=quadro_pracas,
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
                        f'Criado: {posto_codigo} - {quadro_pracas} ({anos}a {meses}m)'
                    )
                )
            else:
                # Atualizar se já existe
                intersticio.tempo_minimo_anos = anos
                intersticio.tempo_minimo_meses = meses
                intersticio.ativo = True
                intersticio.save()
                atualizados += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Atualizado: {posto_codigo} - {quadro_pracas} ({anos}a {meses}m)'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {criados} interstícios criados, {atualizados} atualizados.'
            )
        ) 