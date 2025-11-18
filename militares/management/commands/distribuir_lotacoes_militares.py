from django.core.management.base import BaseCommand
from django.db import transaction
from militares.models import Orgao, GrandeComando, Unidade, SubUnidade, Militar, Lotacao
from datetime import date
import random


class Command(BaseCommand):
    help = 'Apaga todas as lotações existentes e distribui os militares entre os diferentes níveis do organograma (1 lotação por militar)'

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
            militares = list(Militar.objects.exclude(situacao='INATIVO'))
            self.stdout.write(f"Encontrados {len(militares)} militares ativos")
            
            # 3. Buscar todas as organizações do organograma
            orgaos = list(Orgao.objects.filter(ativo=True))
            grandes_comandos = list(GrandeComando.objects.filter(ativo=True))
            unidades = list(Unidade.objects.filter(ativo=True))
            subunidades = list(SubUnidade.objects.filter(ativo=True))
            
            self.stdout.write(f"Organograma:")
            self.stdout.write(f"  - {len(orgaos)} órgãos")
            self.stdout.write(f"  - {len(grandes_comandos)} grandes comandos")
            self.stdout.write(f"  - {len(unidades)} unidades")
            self.stdout.write(f"  - {len(subunidades)} subunidades")
            
            # 4. Criar lista de todas as opções de lotação
            opcoes_lotacao = []
            
            # Adicionar órgãos
            for orgao in orgaos:
                opcoes_lotacao.append({
                    'tipo': 'orgao',
                    'orgao': orgao,
                    'grande_comando': None,
                    'unidade': None,
                    'sub_unidade': None,
                    'lotacao': orgao.nome
                })
            
            # Adicionar grandes comandos
            for gc in grandes_comandos:
                opcoes_lotacao.append({
                    'tipo': 'grande_comando',
                    'orgao': gc.orgao,
                    'grande_comando': gc,
                    'unidade': None,
                    'sub_unidade': None,
                    'lotacao': f"{gc.orgao.nome} | {gc.nome}"
                })
            
            # Adicionar unidades
            for unidade in unidades:
                opcoes_lotacao.append({
                    'tipo': 'unidade',
                    'orgao': unidade.grande_comando.orgao,
                    'grande_comando': unidade.grande_comando,
                    'unidade': unidade,
                    'sub_unidade': None,
                    'lotacao': f"{unidade.grande_comando.orgao.nome} | {unidade.grande_comando.nome} | {unidade.nome}"
                })
            
            # Adicionar subunidades
            for subunidade in subunidades:
                opcoes_lotacao.append({
                    'tipo': 'subunidade',
                    'orgao': subunidade.unidade.grande_comando.orgao,
                    'grande_comando': subunidade.unidade.grande_comando,
                    'unidade': subunidade.unidade,
                    'sub_unidade': subunidade,
                    'lotacao': f"{subunidade.unidade.grande_comando.orgao.nome} | {subunidade.unidade.grande_comando.nome} | {subunidade.unidade.nome} | {subunidade.nome}"
                })
            
            self.stdout.write(f"Total de opções de lotação: {len(opcoes_lotacao)}")
            
            # 5. Distribuir militares aleatoriamente entre as opções
            lotacoes_criadas = 0
            
            for i, militar in enumerate(militares):
                # Selecionar uma opção aleatória
                opcao = random.choice(opcoes_lotacao)
                
                if not dry_run:
                    Lotacao.objects.create(
                        militar=militar,
                        lotacao=opcao['lotacao'],
                        orgao=opcao['orgao'],
                        grande_comando=opcao['grande_comando'],
                        unidade=opcao['unidade'],
                        sub_unidade=opcao['sub_unidade'],
                        status='ATUAL',
                        data_inicio=date.today(),
                        ativo=True
                    )
                
                self.stdout.write(f"{i+1:2d}. {militar.nome_guerra:20s} -> {opcao['lotacao']}")
                lotacoes_criadas += 1
            
            # 6. Mostrar estatísticas de distribuição
            if not dry_run:
                self.stdout.write(f"\nEstatísticas de distribuição:")
                
                # Contar por tipo
                lotacoes_orgao = Lotacao.objects.filter(grande_comando__isnull=True, unidade__isnull=True, sub_unidade__isnull=True).count()
                lotacoes_gc = Lotacao.objects.filter(grande_comando__isnull=False, unidade__isnull=True, sub_unidade__isnull=True).count()
                lotacoes_unidade = Lotacao.objects.filter(unidade__isnull=False, sub_unidade__isnull=True).count()
                lotacoes_subunidade = Lotacao.objects.filter(sub_unidade__isnull=False).count()
                
                self.stdout.write(f"  - Órgãos: {lotacoes_orgao}")
                self.stdout.write(f"  - Grandes Comandos: {lotacoes_gc}")
                self.stdout.write(f"  - Unidades: {lotacoes_unidade}")
                self.stdout.write(f"  - Subunidades: {lotacoes_subunidade}")
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY-RUN: {lotacoes_criadas} lotações seriam criadas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'SUCESSO: {lotacoes_criadas} lotações foram criadas')
            )
