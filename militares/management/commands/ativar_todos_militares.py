from django.core.management.base import BaseCommand
from militares.models import Militar


class Command(BaseCommand):
    help = 'Ativa todos os militares que estão inativos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Buscar todos os militares inativos
        militares_inativos = Militar.objects.filter(classificacao='INATIVO')
        total_inativos = militares_inativos.count()

        if total_inativos == 0:
            self.stdout.write(
                self.style.SUCCESS('Não há militares inativos no sistema.')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Encontrados {total_inativos} militares inativos.')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita.')
            )
            
            # Mostrar alguns exemplos dos militares que seriam ativados
            for militar in militares_inativos[:10]:  # Mostrar apenas os primeiros 10
                self.stdout.write(f'  - {militar.matricula} - {militar.nome_completo}')
            
            if total_inativos > 10:
                self.stdout.write(f'  ... e mais {total_inativos - 10} militares')
        else:
            # Ativar todos os militares inativos
            militares_inativos.update(classificacao='ATIVO')
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {total_inativos} militares foram ativados com sucesso!')
            )

        # Mostrar estatísticas finais
        total_ativos = Militar.objects.filter(classificacao='ATIVO').count()
        total_geral = Militar.objects.count()
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('ESTATÍSTICAS FINAIS')
        self.stdout.write('='*50)
        self.stdout.write(f'Total de militares ativos: {total_ativos}')
        self.stdout.write(f'Total de militares inativos: {Militar.objects.filter(situacao="IN").count()}')
        self.stdout.write(f'Total geral: {total_geral}')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Todos os militares foram ativados!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\nMODO DRY-RUN: Execute sem --dry-run para aplicar as mudanças.')
            ) 