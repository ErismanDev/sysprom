#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def verificar_inclusao_errada():
    print("=== VERIFICAÇÃO: INCLUSÃO ERRADA NO QUADRO ===\n")
    
    # Encontrar o militar
    militar = Militar.objects.filter(nome_completo__icontains='JOSE ERISMAN').first()
    quadro = QuadroAcesso.objects.first()
    
    if not militar or not quadro:
        print("Militar ou quadro não encontrado!")
        return
    
    print(f"Militar: {militar.nome_completo}")
    print(f"  - Posto: {militar.get_posto_graduacao_display()}")
    print(f"  - Quadro: {militar.get_quadro_display()}")
    
    print(f"\nQuadro de Acesso: {quadro.get_titulo_completo()}")
    print(f"  - Posto: {quadro.posto} ({quadro.get_posto_display()})")
    print(f"  - Quadro: {quadro.quadro} ({quadro.get_quadro_display()})")
    
    # Verificar se deveria estar no quadro
    print(f"\n--- VERIFICAÇÃO DE ELEGIBILIDADE ---")
    
    # 1. Verificar posto
    if militar.posto_graduacao != quadro.posto:
        print(f"❌ POSTO INCOMPATÍVEL:")
        print(f"   Militar: {militar.posto_graduacao} ({militar.get_posto_graduacao_display()})")
        print(f"   Quadro: {quadro.posto} ({quadro.get_posto_display()})")
    else:
        print(f"✅ Posto compatível")
    
    # 2. Verificar quadro
    if militar.quadro != quadro.quadro:
        print(f"❌ QUADRO INCOMPATÍVEL:")
        print(f"   Militar: {militar.quadro} ({militar.get_quadro_display()})")
        print(f"   Quadro: {quadro.quadro} ({quadro.get_quadro_display()})")
    else:
        print(f"✅ Quadro compatível")
    
    # 3. Verificar se está nos itens do quadro
    item_quadro = quadro.itemquadroacesso_set.filter(militar=militar).first()
    if item_quadro:
        print(f"\n❌ MILITAR ESTÁ NO QUADRO ERRADO!")
        print(f"   Posição: {item_quadro.posicao}")
        print(f"   Pontuação: {item_quadro.pontuacao}")
        print(f"   Data de inclusão: {item_quadro.data_inclusao}")
        
        # Verificar se foi incluído manualmente ou por erro na geração
        print(f"\n--- ANÁLISE DA INCLUSÃO ---")
        
        # Verificar se o quadro foi gerado automaticamente
        if quadro.status == 'ELABORADO':
            print(f"   Quadro foi elaborado automaticamente")
            
            # Verificar se há outros militares incompatíveis
            todos_itens = quadro.itemquadroacesso_set.all()
            incompatíveis = []
            
            for item in todos_itens:
                m = item.militar
                if m.posto_graduacao != quadro.posto or m.quadro != quadro.quadro:
                    incompatíveis.append({
                        'militar': m.nome_completo,
                        'posto': m.get_posto_graduacao_display(),
                        'quadro': m.get_quadro_display(),
                        'posicao': item.posicao
                    })
            
            if incompatíveis:
                print(f"   Outros militares incompatíveis no quadro:")
                for inc in incompatíveis:
                    print(f"     - {inc['militar']} ({inc['posto']} - {inc['quadro']}) - Posição {inc['posicao']}")
            else:
                print(f"   Este é o único militar incompatível no quadro")
        else:
            print(f"   Quadro não foi elaborado automaticamente (Status: {quadro.get_status_display()})")
    else:
        print(f"\n✅ Militar não está no quadro (correto)")

if __name__ == '__main__':
    verificar_inclusao_errada() 