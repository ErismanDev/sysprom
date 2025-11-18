#!/usr/bin/env python3
"""
Comando de management para atualizar automaticamente férias que já terminaram.
Executar: python manage.py atualizar_ferias_vencidas
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from militares.models import Ferias


class Command(BaseCommand):
    help = 'Atualiza automaticamente férias que já terminaram (data_fim < hoje) e retorna situação do militar para PRONTO'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria atualizado sem fazer alterações',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas',
        )

    def handle(self, *args, **options):
        hoje = date.today()
        self.stdout.write(self.style.SUCCESS('[INICIANDO] Verificando férias vencidas...'))
        
        # Buscar férias que ainda estão como GOZANDO mas já terminaram
        ferias_vencidas = Ferias.objects.filter(
            status='GOZANDO',
            data_fim__lt=hoje
        )
        
        total = ferias_vencidas.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✅ Nenhuma férias vencida encontrada.'))
            return
        
        self.stdout.write(f'📋 Encontradas {total} férias vencidas.')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('[DRY RUN] Nenhuma alteração será feita.'))
        
        atualizadas = 0
        for ferias in ferias_vencidas:
            militar_nome = ferias.militar.nome_guerra if ferias.militar else 'N/A'
            
            if options['verbose'] or options['dry_run']:
                self.stdout.write(
                    f"  - {militar_nome}: "
                    f"Data fim: {ferias.data_fim.strftime('%d/%m/%Y')} "
                    f"(Status: {ferias.get_status_display()})"
                )
            
            if not options['dry_run']:
                # Atualizar status para GOZADA
                ferias.status = 'GOZADA'
                ferias.save(update_fields=['status'])
                
                # O save() do modelo já atualiza a situação do militar para PRONTO
                # quando status muda para GOZADA
                
                atualizadas += 1
        
        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {atualizadas} férias atualizadas. Situação dos militares atualizada para PRONTO.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] {atualizadas} férias seriam atualizadas.')
            )

