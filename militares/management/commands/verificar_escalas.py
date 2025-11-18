from django.core.management.base import BaseCommand
from militares.models import EscalaServico, EscalaMilitar
from datetime import datetime

class Command(BaseCommand):
    help = 'Verifica escalas de serviço no banco de dados'

    def handle(self, *args, **kwargs):
        mes = 10
        ano = 2025
        
        self.stdout.write(f'Verificando escalas em {mes}/{ano}:')
        
        # Verificar escalas
        escalas = EscalaServico.objects.filter(data__year=ano, data__month=mes)
        self.stdout.write(f'Total de escalas: {escalas.count()}')
        
        for escala in escalas[:5]:
            self.stdout.write(f'  {escala.data} - {escala.organizacao} - {escala.militares.count()} militares')
            
            # Verificar militares escalados
            for militar_escala in escala.militares.all()[:3]:
                self.stdout.write(f'    - {militar_escala.militar.nome_completo} ({militar_escala.hora_inicio} - {militar_escala.hora_fim})')
        
        # Verificar todas as escalas
        todas_escalas = EscalaServico.objects.all()
        self.stdout.write(f'Total de escalas no sistema: {todas_escalas.count()}')
        
        if todas_escalas.exists():
            ultima_escala = todas_escalas.order_by('-data').first()
            self.stdout.write(f'Última escala: {ultima_escala.data} - {ultima_escala.organizacao}')
