#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def corrigir_quadros_incompatíveis():
    print("=== CORREÇÃO DE MILITARES INCOMPATÍVEIS NOS QUADROS ===\n")
    
    # Verificar todos os quadros de acesso
    quadros = QuadroAcesso.objects.all()
    print(f"Quadros de acesso encontrados: {quadros.count()}")
    
    total_corrigidos = 0
    
    for quadro in quadros:
        print(f"\n--- ANALISANDO QUADRO: {quadro.get_titulo_completo()} ---")
        
        # Buscar itens incompatíveis
        itens = quadro.itemquadroacesso_set.all()
        incompatíveis = []
        
        for item in itens:
            militar = item.militar
            if militar.posto_graduacao != quadro.posto or militar.quadro != quadro.quadro:
                incompatíveis.append({
                    'item': item,
                    'militar': militar,
                    'motivo': []
                })
                
                if militar.posto_graduacao != quadro.posto:
                    incompatíveis[-1]['motivo'].append(f"Posto: {militar.get_posto_graduacao_display()} vs {quadro.get_posto_display()}")
                if militar.quadro != quadro.quadro:
                    incompatíveis[-1]['motivo'].append(f"Quadro: {militar.get_quadro_display()} vs {quadro.get_quadro_display()}")
        
        if incompatíveis:
            print(f"Encontrados {len(incompatíveis)} militares incompatíveis:")
            
            for inc in incompatíveis:
                militar = inc['militar']
                item = inc['item']
                motivos = inc['motivo']
                
                print(f"  - {militar.nome_completo} (Posição {item.posicao})")
                print(f"    Motivos: {', '.join(motivos)}")
                
                # Remover o item incompatível
                item.delete()
                print(f"    ✓ Removido do quadro")
                total_corrigidos += 1
        else:
            print("Nenhum militar incompatível encontrado")
    
    print(f"\n=== RESUMO ====")
    print(f"Total de militares incompatíveis removidos: {total_corrigidos}")
    
    if total_corrigidos > 0:
        print(f"\n⚠️  ATENÇÃO: {total_corrigidos} militares foram removidos por incompatibilidade!")
        print("Verifique se houve algum erro na geração dos quadros ou inclusão manual.")

if __name__ == '__main__':
    corrigir_quadros_incompatíveis() 