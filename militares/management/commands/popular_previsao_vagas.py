from django.core.management.base import BaseCommand
from militares.models import PrevisaoVaga


class Command(BaseCommand):
    help = 'Popula as previsões de vagas com os dados do anexo'

    def handle(self, *args, **options):
        # Dados do anexo fornecido
        dados_anexo = {
            # I - QUADRO DE OFICIAIS BOMBEIROS MILITAR COMBATENTES
            ('CB', 'COMB'): {'efetivo_atual': 0, 'efetivo_previsto': 6},
            ('TC', 'COMB'): {'efetivo_atual': 0, 'efetivo_previsto': 16},
            ('MJ', 'COMB'): {'efetivo_atual': 0, 'efetivo_previsto': 35},
            ('CP', 'COMB'): {'efetivo_atual': 0, 'efetivo_previsto': 38},
            ('1T', 'COMB'): {'efetivo_atual': 0, 'efetivo_previsto': 50},
            ('2T', 'COMB'): {'efetivo_atual': 0, 'efetivo_previsto': 56},
            
            # II - QUADRO DE OFICIAIS BOMBEIROS MILITAR DE SAÚDE
            ('TC', 'SAUDE'): {'efetivo_atual': 0, 'efetivo_previsto': 1},
            ('MJ', 'SAUDE'): {'efetivo_atual': 0, 'efetivo_previsto': 1},
            ('CP', 'SAUDE'): {'efetivo_atual': 0, 'efetivo_previsto': 2},
            ('1T', 'SAUDE'): {'efetivo_atual': 0, 'efetivo_previsto': 2},
            ('2T', 'SAUDE'): {'efetivo_atual': 0, 'efetivo_previsto': 6},
            
            # III - QUADRO DE OFICIAIS BOMBEIROS MILITAR ENGENHEIROS
            ('TC', 'ENG'): {'efetivo_atual': 0, 'efetivo_previsto': 2},
            ('MJ', 'ENG'): {'efetivo_atual': 0, 'efetivo_previsto': 2},
            ('CP', 'ENG'): {'efetivo_atual': 0, 'efetivo_previsto': 2},
            ('1T', 'ENG'): {'efetivo_atual': 0, 'efetivo_previsto': 2},
            ('2T', 'ENG'): {'efetivo_atual': 0, 'efetivo_previsto': 2},
            
            # IV - QUADRO DE OFICIAIS BOMBEIROS MILITAR COMPLEMENTARES
            ('MJ', 'COMP'): {'efetivo_atual': 0, 'efetivo_previsto': 6},
            ('CP', 'COMP'): {'efetivo_atual': 0, 'efetivo_previsto': 24},
            ('1T', 'COMP'): {'efetivo_atual': 0, 'efetivo_previsto': 36},
            ('2T', 'COMP'): {'efetivo_atual': 0, 'efetivo_previsto': 41},
            
            # V - QUADRO DE PRAÇAS BOMBEIROS MILITAR
            ('ST', 'PRACAS'): {'efetivo_atual': 0, 'efetivo_previsto': 63},
            ('1S', 'PRACAS'): {'efetivo_atual': 0, 'efetivo_previsto': 102},
            ('2S', 'PRACAS'): {'efetivo_atual': 0, 'efetivo_previsto': 130},
            ('3S', 'PRACAS'): {'efetivo_atual': 0, 'efetivo_previsto': 150},
            ('CAB', 'PRACAS'): {'efetivo_atual': 0, 'efetivo_previsto': 240},
            ('SD', 'PRACAS'): {'efetivo_atual': 0, 'efetivo_previsto': 428},
        }
        
        # Limpar previsões existentes
        PrevisaoVaga.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Previsões de vagas existentes removidas.'))
        
        # Criar novas previsões
        criadas = 0
        for (posto, quadro), dados in dados_anexo.items():
            try:
                PrevisaoVaga.objects.create(
                    posto=posto,
                    quadro=quadro,
                    efetivo_atual=dados['efetivo_atual'],
                    efetivo_previsto=dados['efetivo_previsto'],
                    ativo=True
                )
                criadas += 1
                self.stdout.write(f'Criada previsão: {posto} - {quadro} ({dados["efetivo_previsto"]} vagas)')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao criar previsão {posto} - {quadro}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total de {criadas} previsões de vagas criadas com sucesso!'))
        
        # Calcular totais
        total_previsto = sum(dados['efetivo_previsto'] for dados in dados_anexo.values())
        self.stdout.write(f'Total de efetivo previsto: {total_previsto}')
        
        # Resumo por quadro
        quadros = {}
        for (posto, quadro), dados in dados_anexo.items():
            if quadro not in quadros:
                quadros[quadro] = 0
            quadros[quadro] += dados['efetivo_previsto']
        
        self.stdout.write('\nResumo por quadro:')
        for quadro, total in quadros.items():
            self.stdout.write(f'  {quadro}: {total} vagas') 