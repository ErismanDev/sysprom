#!/usr/bin/env python3
"""
Comando de management para automatizar atualização de fichas de conceito.
Executar: python manage.py atualizar_fichas_conceito
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from militares.models import Militar, FichaConceitoOficiais, FichaConceitoPracas


class Command(BaseCommand):
    help = 'Atualiza automaticamente todas as fichas de conceito'

    def add_arguments(self, parser):
        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força atualização de todas as fichas',
        )
        parser.add_argument(
            '--recentes',
            action='store_true',
            help='Atualiza apenas militares promovidos recentemente',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Iniciando atualização automática de fichas de conceito...'))
        
        if options['forcar']:
            self.atualizar_todas_fichas()
        elif options['recentes']:
            self.atualizar_militares_recentes()
        else:
            self.atualizar_todas_fichas()
        
        self.stdout.write(self.style.SUCCESS('✅ Atualização concluída!'))

    def atualizar_todas_fichas(self):
        """Atualiza todas as fichas de conceito"""
        self.stdout.write('📋 Atualizando todas as fichas de conceito...')
        
        # Atualizar fichas de oficiais
        fichas_oficiais = FichaConceitoOficiais.objects.all()
        self.stdout.write(f'   Atualizando {fichas_oficiais.count()} fichas de oficiais...')
        
        for ficha in fichas_oficiais:
            try:
                ficha.save()
                self.stdout.write(f'      ✅ Ficha de oficiais {ficha.id} atualizada')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'      ❌ Erro na ficha {ficha.id}: {e}'))
        
        # Atualizar fichas de praças
        fichas_pracas = FichaConceitoPracas.objects.all()
        self.stdout.write(f'   Atualizando {fichas_pracas.count()} fichas de praças...')
        
        for ficha in fichas_pracas:
            try:
                ficha.save()
                self.stdout.write(f'      ✅ Ficha de praças {ficha.id} atualizada')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'      ❌ Erro na ficha {ficha.id}: {e}'))

    def atualizar_militares_recentes(self):
        """Atualiza apenas militares promovidos recentemente"""
        self.stdout.write('📋 Atualizando militares promovidos recentemente...')
        
        data_limite = timezone.now().date() - timedelta(days=30)
        militares_recentes = Militar.objects.filter(
            data_promocao_atual__gte=data_limite,
            situacao='AT'
        )
        
        self.stdout.write(f'   Encontrados {militares_recentes.count()} militares promovidos recentemente')
        
        for militar in militares_recentes:
            self.stdout.write(f'   📋 Militar: {militar.nome_completo}')
            
            # Atualizar fichas do militar
            ficha_oficiais = militar.fichaconceitooficiais_set.first()
            ficha_pracas = militar.fichaconceitopracas_set.first()
            
            if ficha_oficiais:
                ficha_oficiais.save()
                self.stdout.write(f'      ✅ Ficha de oficiais atualizada')
            
            if ficha_pracas:
                ficha_pracas.save()
                self.stdout.write(f'      ✅ Ficha de praças atualizada')
