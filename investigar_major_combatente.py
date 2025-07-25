#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso
from django.utils import timezone

def investigar_major_combatente():
    print("=== INVESTIGAÇÃO: MAJOR DO COMBATENTE APTO ===\n")
    
    # 1. Verificar o quadro específico
    try:
        quadro = QuadroAcesso.objects.get(pk=311)
        print(f"Quadro encontrado: {quadro.get_titulo_completo()}")
        print(f"Tipo: {quadro.tipo}")
        print(f"Status: {quadro.status}")
        print(f"Data promoção: {quadro.data_promocao}")
        print(f"Categoria: {quadro.categoria}")
    except QuadroAcesso.DoesNotExist:
        print("Quadro 311 não encontrado!")
        return
    
    # 2. Buscar majors do combatente ativos
    majors_combatente = Militar.objects.filter(
        situacao='AT',
        quadro='COMB',
        posto_graduacao='MJ'
    )
    
    print(f"\n--- MAJORS DO COMBATENTE ATIVOS ---")
    print(f"Total encontrados: {majors_combatente.count()}")
    
    for militar in majors_combatente:
        print(f"\nMilitar: {militar.nome_completo} (ID: {militar.id})")
        print(f"  - Situação: {militar.situacao}")
        print(f"  - Quadro: {militar.quadro}")
        print(f"  - Posto: {militar.posto_graduacao}")
        print(f"  - Data promoção atual: {militar.data_promocao_atual}")
        print(f"  - Apto inspeção saúde: {militar.apto_inspecao_saude}")
        print(f"  - Data inspeção saúde: {militar.data_inspecao_saude}")
        print(f"  - Validade inspeção saúde: {militar.data_validade_inspecao_saude}")
        print(f"  - Curso formação oficial: {militar.curso_formacao_oficial}")
        print(f"  - Curso aperfeiçoamento oficial: {militar.curso_aperfeicoamento_oficial}")
        print(f"  - Curso CSBM: {militar.curso_csbm}")
        
        # Verificar se está no quadro
        item_quadro = ItemQuadroAcesso.objects.filter(
            quadro_acesso=quadro,
            militar=militar
        ).first()
        
        if item_quadro:
            print(f"  - ESTÁ NO QUADRO: Posição {item_quadro.posicao}")
        else:
            print(f"  - NÃO ESTÁ NO QUADRO")
            
            # Testar validação individual
            apto, motivo = quadro.validar_requisitos_quadro_acesso(militar)
            print(f"  - Validação: {'APTO' if apto else 'INAPTO'}")
            if not apto:
                print(f"  - Motivo: {motivo}")
    
    # 3. Verificar militares aptos do quadro
    print(f"\n--- MILITARES APTOS DO QUADRO ---")
    militares_aptos = quadro.militares_aptos()
    print(f"Total aptos: {len(militares_aptos)}")
    
    majors_aptos = [m for m in militares_aptos if m.posto_graduacao == 'MJ' and m.quadro == 'COMB']
    print(f"Majors do combatente aptos: {len(majors_aptos)}")
    
    for militar in majors_aptos:
        print(f"  - {militar.nome_completo} (ID: {militar.id})")
    
    # 4. Verificar militares inaptos
    print(f"\n--- MILITARES INAPTOS DO QUADRO ---")
    militares_inaptos = quadro.militares_inaptos_com_motivo()
    
    majors_inaptos = [item for item in militares_inaptos 
                      if item['militar'].posto_graduacao == 'MJ' and item['militar'].quadro == 'COMB']
    
    print(f"Majors do combatente inaptos: {len(majors_inaptos)}")
    
    for item in majors_inaptos:
        militar = item['militar']
        motivo = item['motivo']
        print(f"  - {militar.nome_completo} (ID: {militar.id}): {motivo}")
    
    # 5. Verificar itens salvos no quadro
    print(f"\n--- ITENS SALVOS NO QUADRO ---")
    itens_quadro = quadro.itemquadroacesso_set.all().select_related('militar')
    print(f"Total itens salvos: {itens_quadro.count()}")
    
    majors_salvos = [item for item in itens_quadro 
                     if item.militar.posto_graduacao == 'MJ' and item.militar.quadro == 'COMB']
    
    print(f"Majors do combatente salvos: {len(majors_salvos)}")
    
    for item in majors_salvos:
        print(f"  - {item.militar.nome_completo} (ID: {item.militar.id}) - Posição {item.posicao}")
    
    # 6. Testar regeneração do quadro
    print(f"\n--- TESTANDO REGENERAÇÃO ---")
    
    # Simular regeneração sem salvar
    militares_aptos_regeneracao = quadro.militares_aptos()
    militares_inaptos_regeneracao = quadro.militares_inaptos_com_motivo()
    
    majors_aptos_regeneracao = [m for m in militares_aptos_regeneracao 
                               if m.posto_graduacao == 'MJ' and m.quadro == 'COMB']
    
    print(f"Majors aptos na regeneração: {len(majors_aptos_regeneracao)}")
    
    for militar in majors_aptos_regeneracao:
        print(f"  - {militar.nome_completo} (ID: {militar.id})")
    
    # 7. Verificar se há diferença entre salvos e regeneração
    ids_majors_salvos = {item.militar.id for item in majors_salvos}
    ids_majors_regeneracao = {m.id for m in majors_aptos_regeneracao}
    
    print(f"\n--- COMPARAÇÃO ---")
    print(f"IDs salvos: {ids_majors_salvos}")
    print(f"IDs regeneração: {ids_majors_regeneracao}")
    
    if ids_majors_salvos != ids_majors_regeneracao:
        print("DIFERENÇA ENCONTRADA!")
        print(f"Salvos mas não na regeneração: {ids_majors_salvos - ids_majors_regeneracao}")
        print(f"Na regeneração mas não salvos: {ids_majors_regeneracao - ids_majors_salvos}")
    else:
        print("Nenhuma diferença encontrada entre salvos e regeneração")

if __name__ == "__main__":
    investigar_major_combatente() 