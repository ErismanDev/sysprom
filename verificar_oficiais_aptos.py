#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from django.utils import timezone

def verificar_oficiais_aptos():
    print("=== VERIFICAÇÃO DE OFICIAIS APTOS vs QUADRO ===\n")
    
    # Buscar o quadro mais recente de oficiais (qualquer status)
    quadro = QuadroAcesso.objects.filter(
        categoria='OFICIAIS'
    ).order_by('-data_criacao').first()
    
    if not quadro:
        print("Nenhum quadro de oficiais encontrado!")
        return
    
    print(f"Analisando quadro: {quadro.get_titulo_completo()}")
    print(f"Tipo: {quadro.tipo}")
    print(f"Categoria: {quadro.categoria}")
    print(f"Data promoção: {quadro.data_promocao}")
    print(f"Status: {quadro.status}")
    
    # Verificar se há Tenente-Coronel em quadro de antiguidade
    if quadro.tipo == 'ANTIGUIDADE':
        tenentes_coronel = Militar.objects.filter(
            situacao='AT',
            posto_graduacao='TC'
        )
        if tenentes_coronel.exists():
            print(f"\n⚠️  PROBLEMA ENCONTRADO!")
            print(f"Este é um quadro de ANTIGUIDADE, mas há Tenente-Coronel(s) que só podem ser promovidos por MERECIMENTO:")
            for tc in tenentes_coronel:
                print(f"  - {tc.nome_completo} (TC - {tc.quadro})")
    
    # 1. Buscar militares candidatos (primeira etapa)
    if quadro.tipo == 'MERECIMENTO':
        militares_candidatos = Militar.objects.filter(
            situacao='AT',
            quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP'],
            posto_graduacao__in=['CP', 'MJ', 'TC']
        )
    else:
        militares_candidatos = Militar.objects.filter(
            situacao='AT',
            quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP']
        )
        
        # Incluir subtenentes do quadro PRACAS
        subtenentes_pracas = Militar.objects.filter(
            situacao='AT',
            quadro='PRACAS',
            posto_graduacao='ST'
        )
        militares_candidatos = list(militares_candidatos) + list(subtenentes_pracas)
    
    print(f"\n--- ETAPA 1: MILITARES CANDIDATOS ---")
    print(f"Total de candidatos encontrados: {len(militares_candidatos)}")
    
    for militar in militares_candidatos:
        print(f"  - {militar.nome_completo} ({militar.posto_graduacao} - {militar.quadro})")
    
    # 2. Aplicar validações rigorosas
    print(f"\n--- ETAPA 2: VALIDAÇÕES INDIVIDUAIS ---")
    militares_aptos = []
    militares_inaptos = []
    
    for militar in militares_candidatos:
        # Excluir coronéis
        if militar.posto_graduacao == 'CB':
            militares_inaptos.append({
                'militar': militar,
                'motivo': 'Coronel não tem próximo posto para promoção'
            })
            continue
        
        # Verificar se Tenente-Coronel está em quadro de antiguidade
        if militar.posto_graduacao == 'TC' and quadro.tipo == 'ANTIGUIDADE':
            militares_inaptos.append({
                'militar': militar,
                'motivo': 'Tenente-Coronel só pode ser promovido por merecimento'
            })
            print(f"❌ {militar.nome_completo} ({militar.posto_graduacao} - {militar.quadro}) - INAPTO: Tenente-Coronel só pode ser promovido por merecimento")
            continue
        
        # Validar requisitos
        apto, motivo = quadro.validar_requisitos_quadro_acesso(militar)
        
        if apto:
            militares_aptos.append(militar)
            print(f"✅ {militar.nome_completo} ({militar.posto_graduacao} - {militar.quadro}) - APTO")
        else:
            militares_inaptos.append({
                'militar': militar,
                'motivo': motivo
            })
            print(f"❌ {militar.nome_completo} ({militar.posto_graduacao} - {militar.quadro}) - INAPTO: {motivo}")
    
    print(f"\n--- RESUMO ---")
    print(f"Total de candidatos: {len(militares_candidatos)}")
    print(f"Militares APTOS: {len(militares_aptos)}")
    print(f"Militares INAPTOS: {len(militares_inaptos)}")
    
    # 3. Verificar militares no quadro
    militares_no_quadro = quadro.itemquadroacesso_set.all()
    print(f"\n--- MILITARES NO QUADRO ---")
    print(f"Total no quadro: {militares_no_quadro.count()}")
    
    for item in militares_no_quadro:
        print(f"  - {item.militar.nome_completo} ({item.militar.posto_graduacao} - {item.militar.quadro}) - Posição: {item.posicao}")
    
    # 4. Comparar
    print(f"\n--- COMPARAÇÃO ---")
    print(f"Militares aptos: {len(militares_aptos)}")
    print(f"Militares no quadro: {militares_no_quadro.count()}")
    
    if len(militares_aptos) != militares_no_quadro.count():
        print(f"⚠️  DIFERENÇA ENCONTRADA!")
        print(f"   Aptos: {len(militares_aptos)}")
        print(f"   No quadro: {militares_no_quadro.count()}")
        
        # Verificar quais estão faltando
        ids_no_quadro = set(militares_no_quadro.values_list('militar_id', flat=True))
        ids_aptos = set(m.id for m in militares_aptos)
        
        faltando_no_quadro = ids_aptos - ids_no_quadro
        if faltando_no_quadro:
            print(f"\n--- MILITARES APTOS QUE NÃO ESTÃO NO QUADRO ---")
            for militar in militares_aptos:
                if militar.id in faltando_no_quadro:
                    print(f"  - {militar.nome_completo} ({militar.posto_graduacao} - {militar.quadro})")
    
    # 5. Detalhar validações para militares inaptos
    if militares_inaptos:
        print(f"\n--- DETALHAMENTO DOS INAPTOS ---")
        for item in militares_inaptos:
            militar = item['militar']
            motivo = item['motivo']
            print(f"\n{militar.nome_completo} ({militar.posto_graduacao} - {militar.quadro}):")
            print(f"  Motivo: {motivo}")
            
            # Verificar interstício
            if not quadro._validar_intersticio_minimo(militar, quadro.data_promocao):
                print(f"  ❌ Interstício: Não completou o tempo mínimo")
            else:
                print(f"  ✅ Interstício: OK")
            
            # Verificar inspeção de saúde
            if not quadro._validar_inspecao_saude(militar):
                print(f"  ❌ Inspeção de saúde: Não está em dia")
            else:
                print(f"  ✅ Inspeção de saúde: OK")
            
            # Verificar cursos
            if not quadro._validar_cursos_inerentes(militar):
                print(f"  ❌ Cursos: Não possui os cursos necessários")
            else:
                print(f"  ✅ Cursos: OK")

if __name__ == "__main__":
    verificar_oficiais_aptos() 