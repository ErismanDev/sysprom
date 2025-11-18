from django.core.management.base import BaseCommand
from django.db import transaction
from militares.models import Militar


class Command(BaseCommand):
    help = 'Reordena automaticamente as numerações de antiguidade após inativações de militares'

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
        dry_run = options['dry_run']
        verbose = options['verbose']
        posto = options['posto']
        quadro = options['quadro']
        
        self.stdout.write(
            self.style.SUCCESS('[INICIANDO] Reordenação de antiguidade após inativações...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('[AVISO] MODO DE TESTE - Nenhuma alteração será salva')
            )
        
        try:
            with transaction.atomic():
                # Executar reordenação
                total_reordenados = Militar.reordenar_todos_apos_inativacao(
                    posto_graduacao=posto,
                    quadro=quadro
                )
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Reordenação concluída (modo teste)! {total_reordenados} militares seriam reordenados.')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Reordenação concluída com sucesso! {total_reordenados} militares foram reordenados.')
                    )
                
                if verbose:
                    self._mostrar_detalhes_reordenacao(posto, quadro)
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante a reordenação: {str(e)}')
            )
            raise

    def _mostrar_detalhes_reordenacao(self, posto=None, quadro=None):
        """Mostra detalhes da reordenação realizada"""
        self.stdout.write('\n📊 DETALHES DA REORDENAÇÃO:')
        
        # Filtrar militares
        filtros = {'situacao': 'AT'}
        if posto:
            filtros['posto_graduacao'] = posto
        if quadro:
            filtros['quadro'] = quadro
        
        militares = Militar.objects.filter(**filtros).order_by('posto_graduacao', 'quadro', 'numeracao_antiguidade')
        
        # Agrupar por posto e quadro
        grupos = {}
        for militar in militares:
            chave = f"{militar.get_posto_graduacao_display()} - {militar.get_quadro_display()}"
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(militar)
        
        for grupo, militares_grupo in grupos.items():
            self.stdout.write(f'\n  📋 {grupo}:')
            for militar in militares_grupo:
                self.stdout.write(f'    {militar.numeracao_antiguidade}º - {militar.nome_completo}')
        
        self.stdout.write(f'\n📈 Total de militares processados: {militares.count()}') 