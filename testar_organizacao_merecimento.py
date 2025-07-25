#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def testar_organizacao_merecimento():
    print("=== TESTANDO ORGANIZAÇÃO DOS MILITARES NO QUADRO DE MERECIMENTO ===\n")
    
    # 1. Buscar o quadro de merecimento
    quadro = QuadroAcesso.objects.filter(tipo='MERECIMENTO').first()
    if not quadro:
        print("❌ Nenhum quadro de merecimento encontrado!")
        return
    
    print(f"1. QUADRO DE MERECIMENTO (ID: {quadro.pk}):")
    print("-" * 50)
    print(f"Data de promoção: {quadro.data_promocao}")
    print(f"Status: {quadro.status}")
    print(f"Observações: {quadro.observacoes}")
    
    # 2. Buscar todos os militares aptos do quadro
    militares_aptos = quadro.itemquadroacesso_set.all().select_related('militar').order_by('posicao')
    print(f"\n2. MILITARES APTOS NO QUADRO:")
    print("-" * 50)
    print(f"Total de militares aptos: {militares_aptos.count()}")
    
    for item in militares_aptos:
        print(f"  {item.posicao}. {item.militar.nome_completo} ({item.militar.quadro}-{item.militar.posto_graduacao}) - Pontuação: {item.pontuacao}")
    
    # 3. Definir transições para quadros de merecimento
    print(f"\n3. TRANSIÇÕES DEFINIDAS PARA MERECIMENTO:")
    print("-" * 50)
    
    transicoes_por_quadro = {
        'COMB': [  # Combatente - inclui TC→CB
            {
                'numero': 'I',
                'titulo': 'TENENTE-CORONEL para o posto de CORONEL',
                'origem': 'TC',
                'destino': 'CB',
            },
            {
                'numero': 'II',
                'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                'origem': 'MJ',
                'destino': 'TC',
            },
            {
                'numero': 'III',
                'titulo': 'CAPITÃO para o posto de MAJOR',
                'origem': 'CP',
                'destino': 'MJ',
            }
        ],
        'SAUDE': [  # Saúde - apenas MJ→TC e CP→MJ
            {
                'numero': 'I',
                'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                'origem': 'MJ',
                'destino': 'TC',
            },
            {
                'numero': 'II',
                'titulo': 'CAPITÃO para o posto de MAJOR',
                'origem': 'CP',
                'destino': 'MJ',
            }
        ],
        'ENG': [  # Engenheiro - apenas MJ→TC e CP→MJ
            {
                'numero': 'I',
                'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                'origem': 'MJ',
                'destino': 'TC',
            },
            {
                'numero': 'II',
                'titulo': 'CAPITÃO para o posto de MAJOR',
                'origem': 'CP',
                'destino': 'MJ',
            }
        ],
        'COMP': [  # Complementar - apenas MJ→TC e CP→MJ
            {
                'numero': 'I',
                'titulo': 'MAJOR para o posto de TENENTE-CORONEL',
                'origem': 'MJ',
                'destino': 'TC',
            },
            {
                'numero': 'II',
                'titulo': 'CAPITÃO para o posto de MAJOR',
                'origem': 'CP',
                'destino': 'MJ',
            }
        ]
    }
    
    # 4. Organizar militares por quadro e transição (simulando a view)
    print(f"\n4. ORGANIZANDO MILITARES POR QUADRO E TRANSIÇÃO:")
    print("-" * 50)
    
    quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    estrutura_quadros = {}
    
    for q in quadros:
        estrutura_quadros[q] = {
            'nome': q,
            'transicoes': []
        }
        
        transicoes_do_quadro = transicoes_por_quadro.get(q, [])
        print(f"\n  Quadro: {q}")
        
        for transicao in transicoes_do_quadro:
            origem = transicao['origem']
            destino = transicao['destino']
            
            # Filtrar militares desta transição
            militares_desta_transicao = [
                item for item in militares_aptos 
                if item.militar.quadro == q and item.militar.posto_graduacao == origem
            ]
            
            print(f"    Transição {origem} → {destino}: {len(militares_desta_transicao)} militares")
            
            for item in militares_desta_transicao:
                print(f"      - {item.militar.nome_completo} (Posição: {item.posicao}, Pontuação: {item.pontuacao})")
            
            estrutura_quadros[q]['transicoes'].append({
                'origem': origem,
                'destino': destino,
                'origem_nome': origem,
                'destino_nome': destino,
                'militares': militares_desta_transicao,
            })
    
    # 5. Verificar se há militares que não foram organizados
    print(f"\n5. VERIFICANDO MILITARES NÃO ORGANIZADOS:")
    print("-" * 50)
    
    militares_organizados = []
    for q, dados in estrutura_quadros.items():
        for transicao in dados['transicoes']:
            militares_organizados.extend(transicao['militares'])
    
    militares_nao_organizados = [item for item in militares_aptos if item not in militares_organizados]
    
    if militares_nao_organizados:
        print(f"❌ {len(militares_nao_organizados)} militares não foram organizados:")
        for item in militares_nao_organizados:
            print(f"  - {item.militar.nome_completo} ({item.militar.quadro}-{item.militar.posto_graduacao})")
    else:
        print("✅ Todos os militares foram organizados corretamente!")
    
    # 6. Verificar se há transições vazias
    print(f"\n6. VERIFICANDO TRANSIÇÕES VAZIAS:")
    print("-" * 50)
    
    transicoes_vazias = []
    for q, dados in estrutura_quadros.items():
        for transicao in dados['transicoes']:
            if not transicao['militares']:
                transicoes_vazias.append(f"{q}: {transicao['origem']} → {transicao['destino']}")
    
    if transicoes_vazias:
        print(f"⚠️  {len(transicoes_vazias)} transições vazias:")
        for transicao in transicoes_vazias:
            print(f"  - {transicao}")
    else:
        print("✅ Todas as transições têm militares!")
    
    # 7. Resumo final
    print(f"\n7. RESUMO FINAL:")
    print("-" * 50)
    
    total_transicoes = sum(len(dados['transicoes']) for dados in estrutura_quadros.values())
    total_transicoes_com_militares = sum(
        len([t for t in dados['transicoes'] if t['militares']]) 
        for dados in estrutura_quadros.values()
    )
    
    print(f"Total de transições definidas: {total_transicoes}")
    print(f"Transições com militares: {total_transicoes_com_militares}")
    print(f"Transições vazias: {total_transicoes - total_transicoes_com_militares}")
    print(f"Total de militares no quadro: {militares_aptos.count()}")
    print(f"Militares organizados: {len(militares_organizados)}")
    print(f"Militares não organizados: {len(militares_nao_organizados)}")

if __name__ == "__main__":
    testar_organizacao_merecimento() 