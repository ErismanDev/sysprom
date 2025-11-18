from django.core.management.base import BaseCommand
from django.db import transaction
from militares.models import Orgao, GrandeComando, Unidade, SubUnidade, Militar, Lotacao
from datetime import date


class Command(BaseCommand):
    help = 'Apaga todas as lotações existentes e cria novas lotações para todos os militares usando todos os níveis do organograma'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita'))
        
        with transaction.atomic():
            # 1. Apagar todas as lotações existentes
            if not dry_run:
                lotacoes_apagadas = Lotacao.objects.all().count()
                Lotacao.objects.all().delete()
                self.stdout.write(f"Apagadas {lotacoes_apagadas} lotações existentes")
            else:
                lotacoes_apagadas = Lotacao.objects.all().count()
                self.stdout.write(f"DRY-RUN: Seriam apagadas {lotacoes_apagadas} lotações existentes")
            
            # 2. Buscar todos os militares ativos
            militares = Militar.objects.exclude(situacao='INATIVO')
            self.stdout.write(f"Encontrados {militares.count()} militares ativos")
            
            # 3. Buscar todas as organizações do organograma
            orgaos = Orgao.objects.filter(ativo=True)
            grandes_comandos = GrandeComando.objects.filter(ativo=True)
            unidades = Unidade.objects.filter(ativo=True)
            subunidades = SubUnidade.objects.filter(ativo=True)
            
            self.stdout.write(f"Organograma:")
            self.stdout.write(f"  - {orgaos.count()} órgãos")
            self.stdout.write(f"  - {grandes_comandos.count()} grandes comandos")
            self.stdout.write(f"  - {unidades.count()} unidades")
            self.stdout.write(f"  - {subunidades.count()} subunidades")
            
            # 4. Criar lotações para cada militar em cada nível
            lotacoes_criadas = 0
            
            for militar in militares:
                self.stdout.write(f"\nCriando lotações para {militar.nome_guerra}:")
                
                # Criar lotação no órgão
                for orgao in orgaos:
                    if not dry_run:
                        Lotacao.objects.create(
                            militar=militar,
                            lotacao=orgao.nome,
                            orgao=orgao,
                            grande_comando=None,
                            unidade=None,
                            sub_unidade=None,
                            status='ATUAL' if lotacoes_criadas == 0 else 'ANTERIOR',
                            data_inicio=date.today(),
                            ativo=True
                        )
                    
                    self.stdout.write(f"  - Órgão: {orgao.nome}")
                    lotacoes_criadas += 1
                
                # Criar lotação nos grandes comandos
                for gc in grandes_comandos:
                    if not dry_run:
                        Lotacao.objects.create(
                            militar=militar,
                            lotacao=f"{gc.orgao.nome} | {gc.nome}",
                            orgao=gc.orgao,
                            grande_comando=gc,
                            unidade=None,
                            sub_unidade=None,
                            status='ANTERIOR',
                            data_inicio=date.today(),
                            ativo=True
                        )
                    
                    self.stdout.write(f"  - Grande Comando: {gc.orgao.nome} | {gc.nome}")
                    lotacoes_criadas += 1
                
                # Criar lotação nas unidades
                for unidade in unidades:
                    if not dry_run:
                        Lotacao.objects.create(
                            militar=militar,
                            lotacao=f"{unidade.grande_comando.orgao.nome} | {unidade.grande_comando.nome} | {unidade.nome}",
                            orgao=unidade.grande_comando.orgao,
                            grande_comando=unidade.grande_comando,
                            unidade=unidade,
                            sub_unidade=None,
                            status='ANTERIOR',
                            data_inicio=date.today(),
                            ativo=True
                        )
                    
                    self.stdout.write(f"  - Unidade: {unidade.grande_comando.orgao.nome} | {unidade.grande_comando.nome} | {unidade.nome}")
                    lotacoes_criadas += 1
                
                # Criar lotação nas subunidades
                for subunidade in subunidades:
                    if not dry_run:
                        Lotacao.objects.create(
                            militar=militar,
                            lotacao=f"{subunidade.unidade.grande_comando.orgao.nome} | {subunidade.unidade.grande_comando.nome} | {subunidade.unidade.nome} | {subunidade.nome}",
                            orgao=subunidade.unidade.grande_comando.orgao,
                            grande_comando=subunidade.unidade.grande_comando,
                            unidade=subunidade.unidade,
                            sub_unidade=subunidade,
                            status='ANTERIOR',
                            data_inicio=date.today(),
                            ativo=True
                        )
                    
                    self.stdout.write(f"  - Subunidade: {subunidade.unidade.grande_comando.orgao.nome} | {subunidade.unidade.grande_comando.nome} | {subunidade.unidade.nome} | {subunidade.nome}")
                    lotacoes_criadas += 1
                
                # Marcar apenas a primeira lotação como ATUAL
                if not dry_run:
                    primeira_lotacao = Lotacao.objects.filter(militar=militar).first()
                    if primeira_lotacao:
                        primeira_lotacao.status = 'ATUAL'
                        primeira_lotacao.save()
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY-RUN: {lotacoes_criadas} lotações seriam criadas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'SUCESSO: {lotacoes_criadas} lotações foram criadas')
            )
