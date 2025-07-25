#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.core.management.base import BaseCommand
from django.db.models import Count
from militares.models import FichaConceitoOficiais, FichaConceitoPracas, Militar

class Command(BaseCommand):
    help = 'Verifica e corrige fichas de conceito duplicadas no banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra as duplicatas sem corrigir',
        )
        parser.add_argument(
            '--corrigir',
            action='store_true',
            help='Corrige as duplicatas encontradas',
        )

    def handle(self, *args, **options):
        self.stdout.write("=== VERIFICANDO FICHAS DE CONCEITO DUPLICADAS ===\n")
        
        dry_run = options['dry_run']
        corrigir = options['corrigir']
        
        if not dry_run and not corrigir:
            self.stdout.write(
                self.style.WARNING(
                    "Use --dry-run para apenas verificar ou --corrigir para corrigir as duplicatas"
                )
            )
            return
        
        # Verificar fichas de oficiais duplicadas
        self.stdout.write("🔍 Verificando fichas de conceito de OFICIAIS...")
        duplicatas_oficiais = FichaConceitoOficiais.objects.values('militar').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicatas_oficiais.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Encontradas {duplicatas_oficiais.count()} fichas de oficiais duplicadas!")
            )
            
            for duplicata in duplicatas_oficiais:
                militar = Militar.objects.get(id=duplicata['militar'])
                fichas = FichaConceitoOficiais.objects.filter(militar=militar).order_by('data_registro')
                
                self.stdout.write(f"\n📋 Militar: {militar.nome_completo} ({militar.matricula})")
                self.stdout.write(f"   Posto: {militar.posto_graduacao}")
                self.stdout.write(f"   Fichas encontradas: {duplicata['count']}")
                
                for i, ficha in enumerate(fichas):
                    self.stdout.write(f"   {i+1}. ID: {ficha.id} - Data: {ficha.data_registro}")
                
                if corrigir:
                    # Manter apenas a ficha mais antiga (primeira)
                    ficha_manter = fichas.first()
                    fichas_excluir = fichas.exclude(id=ficha_manter.id)
                    
                    self.stdout.write(f"   ✅ Mantendo ficha ID: {ficha_manter.id}")
                    self.stdout.write(f"   🗑️ Excluindo {fichas_excluir.count()} fichas duplicadas")
                    
                    for ficha_excluir in fichas_excluir:
                        self.stdout.write(f"      - Excluindo ficha ID: {ficha_excluir.id}")
                        ficha_excluir.delete()
        else:
            self.stdout.write(self.style.SUCCESS("✅ Nenhuma ficha de oficiais duplicada encontrada"))
        
        # Verificar fichas de praças duplicadas
        self.stdout.write("\n🔍 Verificando fichas de conceito de PRACAS...")
        duplicatas_pracas = FichaConceitoPracas.objects.values('militar').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicatas_pracas.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Encontradas {duplicatas_pracas.count()} fichas de praças duplicadas!")
            )
            
            for duplicata in duplicatas_pracas:
                militar = Militar.objects.get(id=duplicata['militar'])
                fichas = FichaConceitoPracas.objects.filter(militar=militar).order_by('data_registro')
                
                self.stdout.write(f"\n📋 Militar: {militar.nome_completo} ({militar.matricula})")
                self.stdout.write(f"   Posto: {militar.posto_graduacao}")
                self.stdout.write(f"   Fichas encontradas: {duplicata['count']}")
                
                for i, ficha in enumerate(fichas):
                    self.stdout.write(f"   {i+1}. ID: {ficha.id} - Data: {ficha.data_registro}")
                
                if corrigir:
                    # Manter apenas a ficha mais antiga (primeira)
                    ficha_manter = fichas.first()
                    fichas_excluir = fichas.exclude(id=ficha_manter.id)
                    
                    self.stdout.write(f"   ✅ Mantendo ficha ID: {ficha_manter.id}")
                    self.stdout.write(f"   🗑️ Excluindo {fichas_excluir.count()} fichas duplicadas")
                    
                    for ficha_excluir in fichas_excluir:
                        self.stdout.write(f"      - Excluindo ficha ID: {ficha_excluir.id}")
                        ficha_excluir.delete()
        else:
            self.stdout.write(self.style.SUCCESS("✅ Nenhuma ficha de praças duplicada encontrada"))
        
        # Verificar militares com ambos os tipos de ficha
        self.stdout.write("\n🔍 Verificando militares com ambos os tipos de ficha...")
        militares_ambos_tipos = Militar.objects.filter(
            fichaconceitooficiais__isnull=False,
            fichaconceitopracas__isnull=False
        ).distinct()
        
        if militares_ambos_tipos.exists():
            self.stdout.write(
                self.style.WARNING(f"⚠️ Encontrados {militares_ambos_tipos.count()} militares com ambos os tipos de ficha!")
            )
            
            for militar in militares_ambos_tipos:
                ficha_oficiais = militar.fichaconceitooficiais_set.first()
                ficha_pracas = militar.fichaconceitopracas_set.first()
                
                self.stdout.write(f"\n📋 Militar: {militar.nome_completo} ({militar.matricula})")
                self.stdout.write(f"   Posto atual: {militar.posto_graduacao}")
                self.stdout.write(f"   Ficha Oficiais ID: {ficha_oficiais.id} - Data: {ficha_oficiais.data_registro}")
                self.stdout.write(f"   Ficha Praças ID: {ficha_pracas.id} - Data: {ficha_pracas.data_registro}")
                
                # Determinar qual ficha manter baseado no posto atual
                postos_oficiais = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
                is_oficial_atual = militar.posto_graduacao in postos_oficiais
                
                if corrigir:
                    if is_oficial_atual:
                        self.stdout.write(f"   ✅ Militar é oficial - mantendo ficha de oficiais")
                        self.stdout.write(f"   🗑️ Excluindo ficha de praças ID: {ficha_pracas.id}")
                        ficha_pracas.delete()
                    else:
                        self.stdout.write(f"   ✅ Militar é praça - mantendo ficha de praças")
                        self.stdout.write(f"   🗑️ Excluindo ficha de oficiais ID: {ficha_oficiais.id}")
                        ficha_oficiais.delete()
        else:
            self.stdout.write(self.style.SUCCESS("✅ Nenhum militar com ambos os tipos de ficha encontrado"))
        
        # Estatísticas finais
        self.stdout.write("\n=== ESTATÍSTICAS FINAIS ===")
        total_fichas_oficiais = FichaConceitoOficiais.objects.count()
        total_fichas_pracas = FichaConceitoPracas.objects.count()
        total_militares_com_ficha = Militar.objects.filter(
            fichaconceitooficiais__isnull=False
        ).count() + Militar.objects.filter(
            fichaconceitopracas__isnull=False
        ).count()
        
        self.stdout.write(f"📊 Total de fichas de oficiais: {total_fichas_oficiais}")
        self.stdout.write(f"📊 Total de fichas de praças: {total_fichas_pracas}")
        self.stdout.write(f"📊 Total de militares com ficha: {total_militares_com_ficha}")
        
        if corrigir:
            self.stdout.write(self.style.SUCCESS("\n✅ Correção concluída!"))
        else:
            self.stdout.write(self.style.WARNING("\n⚠️ Modo de verificação - nenhuma alteração foi feita")) 