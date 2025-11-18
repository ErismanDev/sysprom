from django.core.management.base import BaseCommand
from militares.models import FuncaoMilitar


class Command(BaseCommand):
    help = 'Habilita a permissão pode_transferir para a função Ajudante Geral'

    def handle(self, *args, **options):
        try:
            # Buscar a função Ajudante Geral
            ajudante_geral = FuncaoMilitar.objects.filter(nome='Ajudante Geral').first()
            
            if not ajudante_geral:
                self.stdout.write(
                    self.style.ERROR('Função "Ajudante Geral" não encontrada!')
                )
                return
            
            # Verificar configuração atual
            self.stdout.write(f'Função: {ajudante_geral.nome}')
            self.stdout.write(f'Acesso: {ajudante_geral.acesso}')
            self.stdout.write(f'Nível de acesso: {ajudante_geral.nivel_acesso}')
            self.stdout.write(f'Pode transferir (antes): {ajudante_geral.pode_transferir}')
            
            # Habilitar a permissão pode_transferir
            ajudante_geral.pode_transferir = True
            ajudante_geral.save()
            
            self.stdout.write(
                self.style.SUCCESS('Permissão pode_transferir habilitada com sucesso!')
            )
            self.stdout.write(f'Pode transferir (depois): {ajudante_geral.pode_transferir}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao habilitar permissão: {str(e)}')
            )
