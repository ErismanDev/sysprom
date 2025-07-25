#!/usr/bin/env python
import os
import sys
import django
from django.db.models import Q

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoOficiais, FichaConceitoPracas

def investigar_pracas_sem_ficha():
    """
    Investiga detalhadamente as praças sem ficha
    """
    print("=== INVESTIGAÇÃO DETALHADA DE PRACAS SEM FICHA ===\n")
    
    # 1. Buscar todas as praças ativas
    pracas = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    
    print(f"1. TOTAL DE PRACAS ATIVAS: {pracas.count()}")
    
    # 2. Verificar praças com ficha de praças
    pracas_com_ficha_pracas = pracas.filter(
        fichaconceitopracas__isnull=False
    )
    print(f"2. PRACAS COM FICHA DE PRACAS: {pracas_com_ficha_pracas.count()}")
    
    # 3. Verificar praças com ficha de oficiais (inconsistência)
    pracas_com_ficha_oficiais = pracas.filter(
        fichaconceitooficiais__isnull=False
    )
    print(f"3. PRACAS COM FICHA DE OFICIAIS: {pracas_com_ficha_oficiais.count()}")
    
    if pracas_com_ficha_oficiais.exists():
        print("\n   PRACAS COM FICHA DE OFICIAIS (INCONSISTÊNCIA):")
        for militar in pracas_com_ficha_oficiais:
            print(f"     - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - Matrícula: {militar.matricula}")
    
    # 4. Verificar praças sem nenhuma ficha
    pracas_sem_ficha = pracas.exclude(
        Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
    )
    print(f"\n4. PRACAS SEM NENHUMA FICHA: {pracas_sem_ficha.count()}")
    
    if pracas_sem_ficha.exists():
        print("\n   PRACAS SEM FICHA:")
        for militar in pracas_sem_ficha:
            print(f"     - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - Matrícula: {militar.matricula}")
    
    # 5. Verificar praças com ambas as fichas (inconsistência)
    pracas_com_ambas_fichas = pracas.filter(
        fichaconceitooficiais__isnull=False,
        fichaconceitopracas__isnull=False
    )
    print(f"\n5. PRACAS COM AMBAS AS FICHAS (INCONSISTÊNCIA): {pracas_com_ambas_fichas.count()}")
    
    if pracas_com_ambas_fichas.exists():
        print("\n   PRACAS COM AMBAS AS FICHAS:")
        for militar in pracas_com_ambas_fichas:
            print(f"     - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - Matrícula: {militar.matricula}")
    
    # 6. Resumo
    print(f"\n6. RESUMO:")
    print(f"   - Total de praças: {pracas.count()}")
    print(f"   - Com ficha de praças: {pracas_com_ficha_pracas.count()}")
    print(f"   - Com ficha de oficiais: {pracas_com_ficha_oficiais.count()}")
    print(f"   - Com ambas as fichas: {pracas_com_ambas_fichas.count()}")
    print(f"   - Sem ficha: {pracas_sem_ficha.count()}")
    
    # Verificar se os números batem
    total_verificado = (pracas_com_ficha_pracas.count() + 
                       pracas_com_ficha_oficiais.count() - 
                       pracas_com_ambas_fichas.count() + 
                       pracas_sem_ficha.count())
    
    print(f"   - Total verificado: {total_verificado}")
    print(f"   - Diferença: {pracas.count() - total_verificado}")

if __name__ == '__main__':
    investigar_pracas_sem_ficha() 