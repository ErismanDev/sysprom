#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def corrigir_inconsistencias_quadro_posto():
    """
    Identifica e corrige militares com inconsistências entre quadro e posto.
    
    Regras:
    - Quadro PRACAS: apenas postos SD, CAB, 3S, 2S, 1S, ST
    - Quadros OFICIAIS (COMB, SAUDE, ENG, COMP): apenas postos AS, AA, 2T, 1T, CP, MJ, TC, CB
    """
    print("=== CORREÇÃO DE INCONSISTÊNCIAS QUADRO/POSTO ===\n")
    
    # Definir mapeamento correto
    quadros_pracas = ['PRACAS']
    quadros_oficiais = ['COMB', 'SAUDE', 'ENG', 'COMP']
    
    postos_pracas = ['SD', 'CAB', '3S', '2S', '1S', 'ST']
    postos_oficiais = ['AS', 'AA', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']
    
    # 1. Identificar militares com inconsistências
    print("1. IDENTIFICANDO INCONSISTÊNCIAS:")
    print("-" * 50)
    
    # Militares no quadro PRACAS com postos de oficiais
    pracas_com_posto_oficial = Militar.objects.filter(
        quadro='PRACAS',
        posto_graduacao__in=postos_oficiais
    )
    
    # Militares em quadros de oficiais com postos de praças
    oficiais_com_posto_praca = Militar.objects.filter(
        quadro__in=quadros_oficiais,
        posto_graduacao__in=postos_pracas
    )
    
    print(f"Militares no quadro PRACAS com postos de oficiais: {pracas_com_posto_oficial.count()}")
    print(f"Militares em quadros de oficiais com postos de praças: {oficiais_com_posto_praca.count()}")
    
    total_inconsistencias = pracas_com_posto_oficial.count() + oficiais_com_posto_praca.count()
    
    if total_inconsistencias == 0:
        print("✅ Nenhuma inconsistência encontrada!")
        return
    
    # 2. Mostrar detalhes das inconsistências
    print(f"\n2. DETALHES DAS INCONSISTÊNCIAS:")
    print("-" * 50)
    
    if pracas_com_posto_oficial.exists():
        print("\nMilitares no quadro PRACAS com postos de oficiais:")
        for militar in pracas_com_posto_oficial:
            print(f"  - {militar.nome_completo} (ID: {militar.id})")
            print(f"    * Posto atual: {militar.get_posto_graduacao_display()}")
            print(f"    * Quadro atual: {militar.get_quadro_display()}")
            print(f"    * Matrícula: {militar.matricula}")
            print()
    
    if oficiais_com_posto_praca.exists():
        print("\nMilitares em quadros de oficiais com postos de praças:")
        for militar in oficiais_com_posto_praca:
            print(f"  - {militar.nome_completo} (ID: {militar.id})")
            print(f"    * Posto atual: {militar.get_posto_graduacao_display()}")
            print(f"    * Quadro atual: {militar.get_quadro_display()}")
            print(f"    * Matrícula: {militar.matricula}")
            print()
    
    # 3. Perguntar se deseja corrigir
    print(f"\n3. CORREÇÃO AUTOMÁTICA:")
    print("-" * 50)
    
    resposta = input("Deseja corrigir automaticamente essas inconsistências? (s/n): ").lower().strip()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("Correção cancelada pelo usuário.")
        return
    
    # 4. Aplicar correções
    print(f"\n4. APLICANDO CORREÇÕES:")
    print("-" * 50)
    
    corrigidos = 0
    
    # Corrigir militares no quadro PRACAS com postos de oficiais
    for militar in pracas_com_posto_oficial:
        print(f"Corrigindo {militar.nome_completo}:")
        print(f"  * Posto: {militar.get_posto_graduacao_display()}")
        print(f"  * Quadro anterior: {militar.get_quadro_display()}")
        
        # Determinar quadro correto baseado no posto
        if militar.posto_graduacao in ['AS', 'AA', '2T', '1T']:
            novo_quadro = 'COMP'  # Complementar para postos iniciais
        elif militar.posto_graduacao in ['CP', 'MJ']:
            novo_quadro = 'COMB'  # Combatente para capitão e major
        elif militar.posto_graduacao in ['TC', 'CB']:
            novo_quadro = 'COMB'  # Combatente para tenente-coronel e coronel
        else:
            novo_quadro = 'COMP'  # Fallback para complementar
        
        militar.quadro = novo_quadro
        militar.save()
        
        print(f"  * Quadro novo: {militar.get_quadro_display()}")
        print(f"  ✅ Corrigido!")
        print()
        corrigidos += 1
    
    # Corrigir militares em quadros de oficiais com postos de praças
    for militar in oficiais_com_posto_praca:
        print(f"Corrigindo {militar.nome_completo}:")
        print(f"  * Posto: {militar.get_posto_graduacao_display()}")
        print(f"  * Quadro anterior: {militar.get_quadro_display()}")
        
        # Mover para quadro PRACAS
        militar.quadro = 'PRACAS'
        militar.save()
        
        print(f"  * Quadro novo: {militar.get_quadro_display()}")
        print(f"  ✅ Corrigido!")
        print()
        corrigidos += 1
    
    # 5. Verificar se ainda há inconsistências
    print(f"\n5. VERIFICAÇÃO FINAL:")
    print("-" * 50)
    
    pracas_com_posto_oficial_apos = Militar.objects.filter(
        quadro='PRACAS',
        posto_graduacao__in=postos_oficiais
    )
    
    oficiais_com_posto_praca_apos = Militar.objects.filter(
        quadro__in=quadros_oficiais,
        posto_graduacao__in=postos_pracas
    )
    
    total_inconsistencias_apos = pracas_com_posto_oficial_apos.count() + oficiais_com_posto_praca_apos.count()
    
    print(f"Total de militares corrigidos: {corrigidos}")
    print(f"Inconsistências restantes: {total_inconsistencias_apos}")
    
    if total_inconsistencias_apos == 0:
        print("✅ Todas as inconsistências foram corrigidas!")
    else:
        print("⚠️  Ainda existem inconsistências. Execute o script novamente.")
    
    # 6. Estatísticas finais
    print(f"\n6. ESTATÍSTICAS FINAIS:")
    print("-" * 50)
    
    for quadro in ['PRACAS', 'COMB', 'SAUDE', 'ENG', 'COMP']:
        count = Militar.objects.filter(quadro=quadro).count()
        print(f"Quadro {quadro}: {count} militares")
    
    print(f"\nPor posto:")
    for posto in ['SD', 'CAB', '3S', '2S', '1S', 'ST', 'AS', 'AA', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']:
        count = Militar.objects.filter(posto_graduacao=posto).count()
        print(f"  {posto}: {count} militares")

if __name__ == "__main__":
    corrigir_inconsistencias_quadro_posto() 