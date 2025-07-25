from django.core.management.base import BaseCommand
from militares.models import Intersticio


class Command(BaseCommand):
    help = 'Remove interstícios das praças do quadro Combatente, mantendo apenas oficiais'

    def handle(self, *args, **options):
        # Postos de praças que devem ser removidos do quadro Combatente
        postos_pracas = ['ST', '1S', '2S', '3S', 'CB', 'SD']
        
        # Postos de oficiais que devem permanecer no quadro Combatente
        postos_oficiais = ['AS', 'AA', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']  # CB = Coronel
        
        removidos = 0
        
        # Remover interstícios das praças do quadro Combatente
        for posto in postos_pracas:
            try:
                intersticios = Intersticio.objects.filter(
                    quadro='COMB',
                    posto=posto
                )
                count = intersticios.count()
                if count > 0:
                    intersticios.delete()
                    removidos += count
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Removido: {posto} do quadro Combatente'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Não encontrado: {posto} no quadro Combatente'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Erro ao remover {posto}: {e}'
                    )
                )
        
        # Verificar quais oficiais permanecem
        oficiais_restantes = Intersticio.objects.filter(
            quadro='COMB'
        ).values_list('posto', flat=True)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {removidos} interstícios de praças removidos do quadro Combatente.'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Oficiais restantes no quadro Combatente: {list(oficiais_restantes)}'
            )
        ) 