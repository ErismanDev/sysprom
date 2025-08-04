#!/usr/bin/env python3
"""
Comando de management para conversão automática de fichas de conceito.
Executar: python manage.py converter_fichas_automatico
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from militares.models import Militar, FichaConceitoOficiais, FichaConceitoPracas, Promocao

class Command(BaseCommand):
    help = 'Converte automaticamente fichas de praças para oficiais quando necessário'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recentes', action='store_true', help='Converte apenas militares promovidos recentemente',
        )
        parser.add_argument(
            '--todos', action='store_true', help='Converte todos os militares que precisam',
        )

    def handle(self, *args, **options):
        if options['recentes']:
            self.converter_militares_recentes()
        elif options['todos']:
            self.converter_todos_militares()
        else:
            self.converter_militares_recentes()

    def converter_militares_recentes(self):
        """Converte fichas de militares promovidos recentemente"""
        self.stdout.write('🔄 Convertendo fichas de militares recentemente promovidos...')
        
        # Buscar promoções dos últimos 30 dias
        data_limite = timezone.now().date() - timedelta(days=30)
        promocoes_recentes = Promocao.objects.filter(
            data_promocao__gte=data_limite
        ).order_by('-data_promocao')
        
        militares_convertidos = 0
        
        for promocao in promocoes_recentes:
            militar = promocao.militar
            
            # Verificar se precisa de conversão
            if (militar.quadro in ['COMB', 'SAUDE', 'ENG', 'COMP'] and 
                militar.posto_graduacao in ['2T', '1T', 'CP', 'MJ', 'TC', 'CB']):
                
                # Verificar se já tem ficha de oficiais
                ficha_oficiais = FichaConceitoOficiais.objects.filter(militar=militar).first()
                ficha_pracas = FichaConceitoPracas.objects.filter(militar=militar).first()
                
                if not ficha_oficiais or ficha_pracas:
                    # Converter ficha
                    try:
                        ficha_oficiais, mensagem = militar.converter_ficha_pracas_para_oficiais(
                            motivo_conversao=f"Conversão automática via comando management"
                        )
                        militares_convertidos += 1
                        self.stdout.write(f'   ✅ {militar.nome_completo}: {mensagem}')
                    except Exception as e:
                        self.stdout.write(f'   ❌ {militar.nome_completo}: Erro - {e}')
        
        self.stdout.write(f'✅ Conversão concluída: {militares_convertidos} militares convertidos')

    def converter_todos_militares(self):
        """Converte fichas de todos os militares que precisam"""
        self.stdout.write('🔄 Convertendo fichas de todos os militares...')
        
        # Buscar todos os militares oficiais
        militares_oficiais = Militar.objects.filter(
            quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
            posto_graduacao__in=['2T', '1T', 'CP', 'MJ', 'TC', 'CB']
        )
        
        militares_convertidos = 0
        
        for militar in militares_oficiais:
            # Verificar se precisa de conversão
            ficha_oficiais = FichaConceitoOficiais.objects.filter(militar=militar).first()
            ficha_pracas = FichaConceitoPracas.objects.filter(militar=militar).first()
            
            if not ficha_oficiais or ficha_pracas:
                # Converter ficha
                try:
                    ficha_oficiais, mensagem = militar.converter_ficha_pracas_para_oficiais(
                        motivo_conversao=f"Conversão automática via comando management"
                    )
                    militares_convertidos += 1
                    self.stdout.write(f'   ✅ {militar.nome_completo}: {mensagem}')
                except Exception as e:
                    self.stdout.write(f'   ❌ {militar.nome_completo}: Erro - {e}')
        
        self.stdout.write(f'✅ Conversão concluída: {militares_convertidos} militares convertidos')
