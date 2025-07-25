#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from militares.models import FichaConceitoOficiais, FichaConceitoPracas, Militar

class Command(BaseCommand):
    help = 'Verifica a integridade das fichas de conceito no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write("=== VERIFICAÇÃO DE INTEGRIDADE DAS FICHAS DE CONCEITO ===\n")
        
        # 1. Verificar militares sem ficha de conceito
        self.stdout.write("🔍 1. Verificando militares sem ficha de conceito...")
        
        militares_ativos = Militar.objects.filter(situacao='AT')
        militares_sem_ficha = militares_ativos.exclude(
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        )
        
        if militares_sem_ficha.exists():
            self.stdout.write(
                self.style.WARNING(f"⚠️ Encontrados {militares_sem_ficha.count()} militares ativos sem ficha de conceito!")
            )
            
            # Agrupar por posto
            por_posto = militares_sem_ficha.values('posto_graduacao').annotate(
                count=Count('id')
            ).order_by('posto_graduacao')
            
            for item in por_posto:
                self.stdout.write(f"   {item['posto_graduacao']}: {item['count']} militares")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Todos os militares ativos possuem ficha de conceito"))
        
        # 2. Verificar fichas órfãs (sem militar)
        self.stdout.write("\n🔍 2. Verificando fichas órfãs...")
        
        fichas_oficiais_orfas = FichaConceitoOficiais.objects.filter(militar__isnull=True)
        fichas_pracas_orfas = FichaConceitoPracas.objects.filter(militar__isnull=True)
        
        if fichas_oficiais_orfas.exists() or fichas_pracas_orfas.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Encontradas fichas órfãs!")
            )
            self.stdout.write(f"   Fichas de oficiais órfãs: {fichas_oficiais_orfas.count()}")
            self.stdout.write(f"   Fichas de praças órfãs: {fichas_pracas_orfas.count()}")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Nenhuma ficha órfã encontrada"))
        
        # 3. Verificar fichas de militares inativos
        self.stdout.write("\n🔍 3. Verificando fichas de militares inativos...")
        
        fichas_militares_inativos = FichaConceitoOficiais.objects.filter(
            militar__situacao='IN'
        ).count() + FichaConceitoPracas.objects.filter(
            militar__situacao='IN'
        ).count()
        
        if fichas_militares_inativos > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Encontradas {fichas_militares_inativos} fichas de militares inativos")
            )
        else:
            self.stdout.write(self.style.SUCCESS("✅ Nenhuma ficha de militar inativo encontrada"))
        
        # 4. Verificar consistência de tipos de ficha
        self.stdout.write("\n🔍 4. Verificando consistência de tipos de ficha...")
        
        # Oficiais com ficha de praças
        oficiais_com_ficha_pracas = Militar.objects.filter(
            posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA'],
            fichaconceitopracas__isnull=False
        )
        
        # Praças com ficha de oficiais
        pracas_com_ficha_oficiais = Militar.objects.filter(
            posto_graduacao__in=['ST', '1S', '2S', '3S', 'CAB', 'SD'],
            fichaconceitooficiais__isnull=False
        )
        
        if oficiais_com_ficha_pracas.exists() or pracas_com_ficha_oficiais.exists():
            self.stdout.write(
                self.style.WARNING(f"⚠️ Encontradas inconsistências de tipo de ficha!")
            )
            
            if oficiais_com_ficha_pracas.exists():
                self.stdout.write(f"   Oficiais com ficha de praças: {oficiais_com_ficha_pracas.count()}")
                for militar in oficiais_com_ficha_pracas[:5]:  # Mostrar apenas os primeiros 5
                    self.stdout.write(f"      - {militar.nome_completo} ({militar.posto_graduacao})")
            
            if pracas_com_ficha_oficiais.exists():
                self.stdout.write(f"   Praças com ficha de oficiais: {pracas_com_ficha_oficiais.count()}")
                for militar in pracas_com_ficha_oficiais[:5]:  # Mostrar apenas os primeiros 5
                    self.stdout.write(f"      - {militar.nome_completo} ({militar.posto_graduacao})")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Todas as fichas estão com o tipo correto"))
        
        # 5. Estatísticas gerais
        self.stdout.write("\n=== ESTATÍSTICAS GERAIS ===")
        
        total_militares_ativos = militares_ativos.count()
        total_fichas_oficiais = FichaConceitoOficiais.objects.count()
        total_fichas_pracas = FichaConceitoPracas.objects.count()
        total_militares_com_ficha = Militar.objects.filter(
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        ).distinct().count()
        
        # Estatísticas por posto
        self.stdout.write(f"📊 Total de militares ativos: {total_militares_ativos}")
        self.stdout.write(f"📊 Total de fichas de oficiais: {total_fichas_oficiais}")
        self.stdout.write(f"📊 Total de fichas de praças: {total_fichas_pracas}")
        self.stdout.write(f"📊 Total de militares com ficha: {total_militares_com_ficha}")
        
        # Cobertura
        cobertura = (total_militares_com_ficha / total_militares_ativos * 100) if total_militares_ativos > 0 else 0
        self.stdout.write(f"📊 Cobertura de fichas: {cobertura:.1f}%")
        
        # Estatísticas por quadro
        self.stdout.write("\n📊 Distribuição por quadro:")
        estatisticas_quadro = militares_ativos.values('quadro').annotate(
            total=Count('id'),
            com_ficha=Count('id', filter=Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False))
        ).order_by('quadro')
        
        for stat in estatisticas_quadro:
            quadro = stat['quadro']
            total = stat['total']
            com_ficha = stat['com_ficha']
            percentual = (com_ficha / total * 100) if total > 0 else 0
            self.stdout.write(f"   {quadro}: {com_ficha}/{total} ({percentual:.1f}%)")
        
        # Estatísticas por posto
        self.stdout.write("\n📊 Distribuição por posto:")
        estatisticas_posto = militares_ativos.values('posto_graduacao').annotate(
            total=Count('id'),
            com_ficha=Count('id', filter=Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False))
        ).order_by('posto_graduacao')
        
        for stat in estatisticas_posto:
            posto = stat['posto_graduacao']
            total = stat['total']
            com_ficha = stat['com_ficha']
            percentual = (com_ficha / total * 100) if total > 0 else 0
            self.stdout.write(f"   {posto}: {com_ficha}/{total} ({percentual:.1f}%)")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Verificação de integridade concluída!")) 