#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso
from datetime import date

def debug_geracao_quadro():
    print("=== DEBUG DA GERAÇÃO DO QUADRO ===\n")
    
    # Buscar o quadro mais recente
    quadro = QuadroAcesso.objects.filter(status='ELABORADO').order_by('-data_promocao').first()
    
    if not quadro:
        print("Nenhum quadro elaborado encontrado!")
        return
    
    print(f"Quadro: {quadro.get_titulo_completo()}")
    print(f"Data de promoção: {quadro.data_promocao}")
    print(f"Tipo: {quadro.get_tipo_display()}")
    
    # Simular o processo de geração
    print(f"\n--- SIMULAÇÃO DO PROCESSO DE GERAÇÃO ---")
    
    # Definir todos os quadros e postos (como no método gerar_quadro_completo)
    quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    postos = ['ST', '2T', '1T', 'CP', 'MJ', 'TC', 'CB']
    
    todos_militares_aptos = []
    todos_militares_inaptos = []
    
    print(f"Quadros considerados: {quadros}")
    print(f"Postos considerados: {postos}")
    
    # Coletar militares aptos de todos os quadros e postos
    for quadro_codigo in quadros:
        for posto in postos:
            print(f"\n--- ANALISANDO: {quadro_codigo} - {posto} ---")
            
            # Buscar militares do posto atual que podem ser promovidos para o próximo posto
            militares_candidatos = Militar.objects.filter(
                quadro=quadro_codigo,
                posto_graduacao=posto,
                situacao='AT'
            )
            
            print(f"Militares candidatos encontrados: {militares_candidatos.count()}")
            
            # Para quadros por antiguidade, não exigir ficha de conceito
            if quadro.tipo == 'ANTIGUIDADE':
                print("Quadro por antiguidade - não exigindo ficha de conceito")
                pass  # Não filtrar por ficha de conceito
            else:
                # Para quadros por merecimento, exigir ficha de conceito
                print("Quadro por merecimento - exigindo ficha de conceito")
                militares_candidatos = militares_candidatos.filter(
                    Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
                )
                print(f"Militares com ficha de conceito: {militares_candidatos.count()}")
            
            # Validar cada militar
            for militar in militares_candidatos:
                print(f"\n  Militar: {militar.nome_completo}")
                print(f"    - Posto: {militar.get_posto_graduacao_display()}")
                print(f"    - Quadro: {militar.get_quadro_display()}")
                
                apto, motivo = quadro.validar_requisitos_quadro_acesso(militar)
                print(f"    - Apto: {'SIM' if apto else 'NÃO'} - Motivo: {motivo}")
                
                if apto:
                    todos_militares_aptos.append({
                        'militar': militar,
                        'quadro': quadro_codigo,
                        'posto': posto,
                        'motivo': 'Apto'
                    })
                    print(f"    - ADICIONADO à lista de aptos")
                else:
                    todos_militares_inaptos.append({
                        'militar': militar,
                        'quadro': quadro_codigo,
                        'posto': posto,
                        'motivo': motivo
                    })
                    print(f"    - ADICIONADO à lista de inaptos")
    
    print(f"\n--- RESULTADO DA COLETA ---")
    print(f"Total de militares aptos coletados: {len(todos_militares_aptos)}")
    print(f"Total de militares inaptos coletados: {len(todos_militares_inaptos)}")
    
    # Verificar se o subtenente com CHO foi coletado
    subtenente_cho = Militar.objects.filter(
        nome_completo='Subtenente Com CHO'
    ).first()
    
    if subtenente_cho:
        print(f"\n--- VERIFICAÇÃO DO SUBTENENTE COM CHO ---")
        print(f"Nome: {subtenente_cho.nome_completo}")
        print(f"Posto: {subtenente_cho.get_posto_graduacao_display()}")
        print(f"Quadro: {subtenente_cho.get_quadro_display()}")
        
        # Verificar se foi coletado
        encontrado_apto = any(item['militar'].id == subtenente_cho.id for item in todos_militares_aptos)
        encontrado_inapto = any(item['militar'].id == subtenente_cho.id for item in todos_militares_inaptos)
        
        print(f"Encontrado na lista de aptos: {'SIM' if encontrado_apto else 'NÃO'}")
        print(f"Encontrado na lista de inaptos: {'SIM' if encontrado_inapto else 'NÃO'}")
        
        if not encontrado_apto and not encontrado_inapto:
            print("PROBLEMA: Subtenente não foi coletado em nenhuma lista!")
            print("Isso significa que ele não foi considerado no loop de quadros/postos")
            
            # Verificar se o posto ST está sendo considerado
            if 'ST' not in postos:
                print("PROBLEMA IDENTIFICADO: Posto 'ST' não está na lista de postos!")
                print(f"Postos considerados: {postos}")
            else:
                print("Posto 'ST' está na lista, mas não foi encontrado")
    
    # Verificar o que está realmente no quadro
    print(f"\n--- VERIFICAÇÃO DO QUADRO REAL ---")
    itens_quadro = quadro.itemquadroacesso_set.all()
    print(f"Total de itens no quadro: {itens_quadro.count()}")
    
    for item in itens_quadro:
        militar = item.militar
        print(f"  - {militar.nome_completo} (Posição {item.posicao})")
        print(f"    * Posto: {militar.get_posto_graduacao_display()}")
        print(f"    * Quadro: {militar.get_quadro_display()}")

if __name__ == "__main__":
    debug_geracao_quadro() 