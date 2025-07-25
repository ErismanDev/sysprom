#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def investigar_view_quadro():
    print("=== INVESTIGAÇÃO: VIEW DO QUADRO DE ACESSO ===\n")
    
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
    
    # 2. Simular a lógica da view
    print(f"\n--- SIMULANDO LÓGICA DA VIEW ---")
    
    # Buscar todos os militares aptos do quadro (como na view)
    militares_aptos = quadro.itemquadroacesso_set.all().select_related('militar').order_by('posicao')
    print(f"Militares aptos do quadro: {militares_aptos.count()}")
    
    for item in militares_aptos:
        print(f"  - {item.militar.nome_completo} ({item.militar.posto_graduacao} - {item.militar.quadro}) - Posição {item.posicao}")
    
    # 3. Verificar as transições definidas para o quadro
    print(f"\n--- TRANSIÇÕES DEFINIDAS ---")
    
    if quadro.tipo == 'ANTIGUIDADE':
        transicoes_por_quadro = {
            'COMB': [  # Combatente
                {
                    'numero': 'I',
                    'titulo': 'CAPITÃO para o posto de MAJOR',
                    'origem': 'CP',
                    'destino': 'MJ',
                },
                {
                    'numero': 'II',
                    'titulo': '1º TENENTE para o posto de CAPITÃO',
                    'origem': '1T',
                    'destino': 'CP',
                },
                {
                    'numero': 'III',
                    'titulo': '2º TENENTE para o posto de 1º TENENTE',
                    'origem': '2T',
                    'destino': '1T',
                },
                {
                    'numero': 'IV',
                    'titulo': 'ASPIRANTE A OFICIAL para o posto de 2º TENENTE',
                    'origem': 'AS',
                    'destino': '2T',
                }
            ]
        }
    else:
        print("Tipo de quadro não suportado para esta análise")
        return
    
    # 4. Simular a filtragem por transição
    print(f"\n--- FILTRAGEM POR TRANSIÇÃO ---")
    
    quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    nomes_quadros = dict(QuadroAcesso.QUADRO_CHOICES)
    nomes_postos = dict(QuadroAcesso.POSTO_CHOICES)
    
    estrutura_quadros = {}
    for q in quadros:
        estrutura_quadros[q] = {
            'nome': nomes_quadros.get(q, q),
            'transicoes': []
        }
        transicoes_do_quadro = transicoes_por_quadro.get(q, [])
        print(f"\nQuadro: {q} ({nomes_quadros.get(q, q)})")
        
        for transicao in transicoes_do_quadro:
            origem = transicao['origem']
            destino = transicao['destino']
            print(f"  Transição: {origem} → {destino} ({nomes_postos.get(origem, origem)} → {nomes_postos.get(destino, destino)})")
            
            # Filtrar militares desta transição
            militares_desta_transicao = [
                item for item in militares_aptos 
                if item.militar.quadro == q and item.militar.posto_graduacao == origem
            ]
            
            print(f"    Militares encontrados: {len(militares_desta_transicao)}")
            for item in militares_desta_transicao:
                print(f"      - {item.militar.nome_completo} (ID: {item.militar.id}) - Posição {item.posicao}")
            
            estrutura_quadros[q]['transicoes'].append({
                'origem': origem,
                'destino': destino,
                'origem_nome': nomes_postos.get(origem, origem),
                'destino_nome': nomes_postos.get(destino, destino),
                'militares': militares_desta_transicao,
            })
    
    # 5. Verificar especificamente o Major do Combatente
    print(f"\n--- VERIFICAÇÃO ESPECÍFICA: MAJOR DO COMBATENTE ---")
    
    major_combatente = Militar.objects.filter(
        situacao='AT',
        quadro='COMB',
        posto_graduacao='MJ'
    ).first()
    
    if major_combatente:
        print(f"Major do combatente encontrado: {major_combatente.nome_completo} (ID: {major_combatente.id})")
        
        # Verificar se está no quadro
        item_quadro = ItemQuadroAcesso.objects.filter(
            quadro_acesso=quadro,
            militar=major_combatente
        ).first()
        
        if item_quadro:
            print(f"  - Está no quadro na posição {item_quadro.posicao}")
            
            # Verificar se aparece na transição CP→MJ
            militares_cp_mj = [
                item for item in militares_aptos 
                if item.militar.quadro == 'COMB' and item.militar.posto_graduacao == 'CP'
            ]
            
            print(f"  - Militares na transição CP→MJ: {len(militares_cp_mj)}")
            for item in militares_cp_mj:
                print(f"    - {item.militar.nome_completo} (ID: {item.militar.id}) - Posição {item.posicao}")
            
            # Verificar se o major aparece na transição MJ→TC
            militares_mj_tc = [
                item for item in militares_aptos 
                if item.militar.quadro == 'COMB' and item.militar.posto_graduacao == 'MJ'
            ]
            
            print(f"  - Militares na transição MJ→TC: {len(militares_mj_tc)}")
            for item in militares_mj_tc:
                print(f"    - {item.militar.nome_completo} (ID: {item.militar.id}) - Posição {item.posicao}")
        else:
            print(f"  - NÃO está no quadro!")
    else:
        print("Nenhum major do combatente encontrado!")

if __name__ == "__main__":
    investigar_view_quadro() 