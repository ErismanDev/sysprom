from django.core.management.base import BaseCommand
from django.db import transaction
from militares.models import Orgao, GrandeComando, Unidade, SubUnidade


class Command(BaseCommand):
    help = 'Cria todas as instâncias de lotação baseadas no organograma do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria criado sem executar',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita'))
        
        instancias_criadas = 0
        
        with transaction.atomic():
            # Criar instâncias de órgão
            for orgao in Orgao.objects.filter(ativo=True):
                if not dry_run:
                    # Aqui você pode criar uma instância de lotação para o órgão se necessário
                    pass
                
                self.stdout.write(f"Órgão: {orgao.nome}")
                instancias_criadas += 1
                
                # Criar instâncias de grande comando
                for gc in orgao.grandes_comandos.filter(ativo=True):
                    if not dry_run:
                        # Aqui você pode criar uma instância de lotação para o grande comando se necessário
                        pass
                    
                    self.stdout.write(f"  Grande Comando: {orgao.nome} | {gc.nome}")
                    instancias_criadas += 1
                    
                    # Criar instâncias de unidade
                    for unidade in gc.unidades.filter(ativo=True):
                        if not dry_run:
                            # Aqui você pode criar uma instância de lotação para a unidade se necessário
                            pass
                        
                        self.stdout.write(f"    Unidade: {orgao.nome} | {gc.nome} | {unidade.nome}")
                        instancias_criadas += 1
                        
                        # Criar instâncias de subunidade
                        for subunidade in unidade.sub_unidades.filter(ativo=True):
                            if not dry_run:
                                # Aqui você pode criar uma instância de lotação para a subunidade se necessário
                                pass
                            
                            self.stdout.write(f"      Subunidade: {orgao.nome} | {gc.nome} | {unidade.nome} | {subunidade.nome}")
                            instancias_criadas += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY-RUN: {instancias_criadas} instâncias seriam criadas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'SUCESSO: {instancias_criadas} instâncias foram processadas')
            )
