from django.core.management.base import BaseCommand
from django.db import transaction
from militares.models import FichaConceitoOficiais, FichaConceitoPracas, Militar


class Command(BaseCommand):
    help = 'Atualiza todas as fichas de conceito existentes, recalculando tempo no posto e pontos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            choices=['oficiais', 'pracas', 'todos'],
            default='todos',
            help='Tipo de ficha a ser atualizada (oficiais, pracas, todos)'
        )
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força a atualização mesmo se não houver mudanças'
        )

    def handle(self, *args, **options):
        tipo = options['tipo']
        forcar = options['forcar']
        
        self.stdout.write('Iniciando atualização das fichas de conceito...')
        
        with transaction.atomic():
            if tipo in ['oficiais', 'todos']:
                self.atualizar_fichas_oficiais(forcar)
            
            if tipo in ['pracas', 'todos']:
                self.atualizar_fichas_pracas(forcar)
        
        self.stdout.write(
            self.style.SUCCESS('Atualização das fichas de conceito concluída com sucesso!')
        )

    def atualizar_fichas_oficiais(self, forcar=False):
        """Atualiza fichas de conceito de oficiais"""
        fichas = FichaConceitoOficiais.objects.all()
        total = fichas.count()
        
        self.stdout.write(f'Atualizando {total} fichas de conceito de oficiais...')
        
        atualizadas = 0
        for ficha in fichas:
            try:
                # Força o recálculo do tempo no posto e pontos
                tempo_anterior = ficha.tempo_posto
                pontos_anterior = ficha.pontos
                
                ficha.save()  # Isso vai recalcular tempo_posto e pontos
                
                if forcar or tempo_anterior != ficha.tempo_posto or pontos_anterior != ficha.pontos:
                    atualizadas += 1
                    self.stdout.write(
                        f'  ✓ Militar: {ficha.militar.nome_completo} - '
                        f'Tempo: {tempo_anterior} → {ficha.tempo_posto}, '
                        f'Pontos: {pontos_anterior} → {ficha.pontos}'
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Erro ao atualizar ficha do militar {ficha.militar.nome_completo}: {e}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Fichas de oficiais atualizadas: {atualizadas}/{total}')
        )

    def atualizar_fichas_pracas(self, forcar=False):
        """Atualiza fichas de conceito de praças"""
        fichas = FichaConceitoPracas.objects.all()
        total = fichas.count()
        
        self.stdout.write(f'Atualizando {total} fichas de conceito de praças...')
        
        atualizadas = 0
        for ficha in fichas:
            try:
                # Força o recálculo do tempo no posto e pontos
                tempo_anterior = ficha.tempo_posto
                pontos_anterior = ficha.pontos
                
                ficha.save()  # Isso vai recalcular tempo_posto e pontos
                
                if forcar or tempo_anterior != ficha.tempo_posto or pontos_anterior != ficha.pontos:
                    atualizadas += 1
                    self.stdout.write(
                        f'  ✓ Militar: {ficha.militar.nome_completo} - '
                        f'Tempo: {tempo_anterior} → {ficha.tempo_posto}, '
                        f'Pontos: {pontos_anterior} → {ficha.pontos}'
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Erro ao atualizar ficha do militar {ficha.militar.nome_completo}: {e}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Fichas de praças atualizadas: {atualizadas}/{total}')
        ) 