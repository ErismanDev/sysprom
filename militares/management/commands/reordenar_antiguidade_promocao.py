from django.core.management.base import BaseCommand
from militares.models import Militar


class Command(BaseCommand):
    help = 'Reordena automaticamente as numerações de antiguidade baseada na data da promoção atual (dentro de cada posto)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posto',
            type=str,
            help='Posto/Graduação específico para reordenar (ex: CP, MJ, TC)'
        )
        parser.add_argument(
            '--quadro',
            type=str,
            help='Quadro específico para reordenar (ex: COMB, SAUDE, ENG)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executar em modo de teste (não salva as alterações)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar informações detalhadas'
        )

    def handle(self, *args, **options):
        posto = options['posto']
        quadro = options['quadro']
        dry_run = options['dry_run']
        verbose = options['verbose']

        self.stdout.write(
            self.style.SUCCESS('Iniciando reordenação de antiguidade por promoção...')
        )

        if posto:
            self.stdout.write(f'Filtro por posto: {posto}')
        if quadro:
            self.stdout.write(f'Filtro por quadro: {quadro}')
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DE TESTE - Nenhuma alteração será salva')
            )

        try:
            # Executar reordenação
            if dry_run:
                # Em modo de teste, apenas mostrar o que seria feito
                militares = Militar.objects.filter(situacao='AT')
                if posto:
                    militares = militares.filter(posto_graduacao=posto)
                if quadro:
                    militares = militares.filter(quadro=quadro)
                
                militares_ordenados = Militar.reordenar_por_antiguidade_promocao(militares)
                
                self.stdout.write(f'\nTotal de militares encontrados: {len(militares_ordenados)}')
                
                if verbose:
                    self.stdout.write('\nOrdem que seria aplicada:')
                    for i, militar in enumerate(militares_ordenados, 1):
                        info = militar.get_info_antiguidade_promocao()
                        self.stdout.write(
                            f'{i:2d}º - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - '
                            f'Promoção atual: {info["data_promocao_atual"]} - '
                            f'Promoção anterior: {info["data_promocao_anterior"] or "N/A"}'
                        )
                
                self.stdout.write(
                    self.style.SUCCESS('\nReordenação simulada com sucesso!')
                )
            else:
                # Executar reordenação real
                total_reordenados = Militar.reordenar_numeracoes_por_antiguidade_promocao(
                    posto_graduacao=posto,
                    quadro=quadro
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nReordenação concluída com sucesso! {total_reordenados} militares foram reordenados.'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao reordenar: {str(e)}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS('\nOperação concluída!')
        ) 