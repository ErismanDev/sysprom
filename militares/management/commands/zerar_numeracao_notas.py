from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from militares.models import Publicacao


class Command(BaseCommand):
    help = 'Zera a numeração das notas e atualiza o banco com sequência correta'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco de dados',
        )
        parser.add_argument(
            '--ano',
            type=int,
            help='Ano específico para zerar (padrão: ano atual)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        ano = options.get('ano') or timezone.now().year
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita no banco de dados'))
        
        # Buscar todas as notas ativas do ano especificado
        notas = Publicacao.objects.filter(
            tipo='NOTA',
            ativo=True,
            numero__endswith=f'/{ano}'
        ).order_by('data_criacao')
        
        total_notas = notas.count()
        
        self.stdout.write(f'Encontradas {total_notas} notas do ano {ano} para reordenar')
        
        if total_notas == 0:
            self.stdout.write(self.style.WARNING('Nenhuma nota encontrada'))
            return
        
        # Mostrar numeração atual
        self.stdout.write('\nNumeração atual:')
        for i, nota in enumerate(notas[:10], 1):
            self.stdout.write(f'{i:2d}. {nota.numero} - {nota.titulo[:50]}...')
        
        if total_notas > 10:
            self.stdout.write(f'... e mais {total_notas - 10} notas')
        
        if not dry_run:
            with transaction.atomic():
                # Zerar todos os números das notas do ano
                self.stdout.write(f'\nZerando numeração das notas do ano {ano}...')
                notas.update(numero='')
                
                # Reordenar por data de criação e renumerar
                self.stdout.write('Renumerando em ordem cronológica...')
                notas_ordenadas = Publicacao.objects.filter(
                    tipo='NOTA',
                    ativo=True,
                    numero=''
                ).order_by('data_criacao')
                
                for i, nota in enumerate(notas_ordenadas, 1):
                    novo_numero = f"{i:03d}/{ano}"
                    nota.numero = novo_numero
                    nota.save(update_fields=['numero'])
                    self.stdout.write(f'✓ {nota.titulo[:50]}... -> {novo_numero}')
        
        # Mostrar resultado final
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN: Nenhuma alteração foi feita'))
        else:
            self.stdout.write(self.style.SUCCESS('Renumeração concluída com sucesso!'))
            
            # Mostrar numeração final
            notas_finais = Publicacao.objects.filter(
                tipo='NOTA',
                ativo=True,
                numero__endswith=f'/{ano}'
            ).order_by('numero')
            
            self.stdout.write(f'\nNumeração final ({notas_finais.count()} notas):')
            for i, nota in enumerate(notas_finais[:10], 1):
                self.stdout.write(f'{i:2d}. {nota.numero} - {nota.titulo[:50]}...')
            
            if notas_finais.count() > 10:
                self.stdout.write(f'... e mais {notas_finais.count() - 10} notas')
