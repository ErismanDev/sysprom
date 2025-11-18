from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from militares.models import Afastamento


class Command(BaseCommand):
    help = 'Encerra automaticamente afastamentos cuja data_fim_prevista já passou'

    def handle(self, *args, **options):
        hoje = date.today()
        
        # Buscar afastamentos ativos com data_fim_prevista já passada
        afastamentos_vencidos = Afastamento.objects.filter(
            status='ATIVO',
            data_fim_prevista__lt=hoje
        ).exclude(data_fim_real__isnull=False)
        
        total_encerrados = 0
        
        for afastamento in afastamentos_vencidos:
            # Encerrar o afastamento
            afastamento.status = 'ENCERRADO'
            # Se não tem data_fim_real, usar a data_fim_prevista
            if not afastamento.data_fim_real:
                afastamento.data_fim_real = afastamento.data_fim_prevista
            afastamento.save(update_fields=['status', 'data_fim_real'])
            
            # O método save() do modelo já vai restaurar a situação do militar para PRONTO
            # se não houver outros afastamentos/férias/licenças ativas
            
            total_encerrados += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Afastamento #{afastamento.pk} ({afastamento.militar.nome_guerra}) '
                    f'encerrado automaticamente. Data prevista: {afastamento.data_fim_prevista}'
                )
            )
        
        if total_encerrados == 0:
            self.stdout.write(
                self.style.SUCCESS('Nenhum afastamento vencido encontrado.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nTotal de afastamentos encerrados: {total_encerrados}'
                )
            )

