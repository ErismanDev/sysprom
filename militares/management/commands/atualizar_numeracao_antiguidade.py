from django.core.management.base import BaseCommand
from militares.models import Militar


class Command(BaseCommand):
    help = 'Valida e mostra a numeração de antiguidade dos militares ativos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Verifica se há duplicações na numeração',
        )

    def handle(self, *args, **options):
        self.stdout.write('Verificando numeração de antiguidade dos militares...')
        
        # Buscar todos os militares ativos
        militares_ativos = Militar.objects.filter(situacao='AT')
        total_militares = militares_ativos.count()
        
        if total_militares == 0:
            self.stdout.write(self.style.WARNING('Nenhum militar ativo encontrado.'))
            return
        
        self.stdout.write(f'Encontrados {total_militares} militares ativos.')
        
        # Agrupar por posto e quadro
        grupos = {}
        for militar in militares_ativos:
            chave = (militar.posto_graduacao, militar.quadro)
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(militar)
        
        self.stdout.write(f'Agrupados em {len(grupos)} grupos (posto/quadro).')
        
        # Verificar numeração para cada grupo
        total_com_numeracao = 0
        total_sem_numeracao = 0
        duplicacoes = []
        
        for (posto, quadro), militares in grupos.items():
            self.stdout.write(f'\n{posto}/{quadro}: {len(militares)} militares')
            
            # Verificar duplicações
            numeracoes = {}
            for militar in militares:
                if militar.numeracao_antiguidade:
                    total_com_numeracao += 1
                    if militar.numeracao_antiguidade in numeracoes:
                        duplicacoes.append({
                            'posto': posto,
                            'quadro': quadro,
                            'numeracao': militar.numeracao_antiguidade,
                            'militares': [numeracoes[militar.numeracao_antiguidade], militar]
                        })
                    else:
                        numeracoes[militar.numeracao_antiguidade] = militar
                    
                    self.stdout.write(f'  {militar.numeracao_antiguidade}º - {militar.nome_completo}')
                else:
                    total_sem_numeracao += 1
                    self.stdout.write(f'  — - {militar.nome_completo} (sem numeração)')
        
        # Resumo
        self.stdout.write(
            self.style.SUCCESS(
                f'\nResumo: {total_com_numeracao} com numeração, {total_sem_numeracao} sem numeração'
            )
        )
        
        if duplicacoes:
            self.stdout.write(
                self.style.ERROR(
                    f'\nATENÇÃO: Encontradas {len(duplicacoes)} duplicações na numeração!'
                )
            )
            for dup in duplicacoes:
                self.stdout.write(
                    self.style.ERROR(
                        f'  {dup["posto"]}/{dup["quadro"]} - Numeração {dup["numeracao"]}º: '
                        f'{dup["militares"][0].nome_completo} e {dup["militares"][1].nome_completo}'
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ Nenhuma duplicação encontrada na numeração.'
                )
            ) 