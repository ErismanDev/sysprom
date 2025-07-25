#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, ItemQuadroAcesso

def verificar_quadro_militares():
    """Verifica o quadro real dos militares no quadro 367"""
    
    try:
        quadro = QuadroAcesso.objects.get(pk=367)
        print(f"=== Quadro 367 ===")
        print(f"Tipo: {quadro.tipo}")
        print(f"Categoria: {quadro.categoria}")
        
        # Buscar todos os militares do quadro
        todos_militares = quadro.itemquadroacesso_set.all()
        print(f"\n--- Militares no quadro ---")
        print(f"Total: {todos_militares.count()}")
        
        for item in todos_militares:
            print(f"\nMilitar: {item.militar.nome_completo}")
            print(f"  Posto: {item.militar.posto_graduacao}")
            print(f"  Quadro do militar: {item.militar.quadro}")
            print(f"  Pontuação: {item.pontuacao}")
            
        # Testar busca sem filtro de quadro
        print(f"\n--- Testando busca sem filtro de quadro ---")
        for origem in ['TC', 'MJ', 'CP']:
            aptos = todos_militares.filter(
                militar__posto_graduacao=origem
            ).order_by('posicao')
            
            print(f"\nTransição {origem}:")
            print(f"  Militares encontrados: {aptos.count()}")
            
            for item in aptos:
                pontuacao_str = f"{item.pontuacao:.2f}" if item.pontuacao else "-"
                print(f"    - {item.militar.nome_completo} ({item.militar.posto_graduacao}): {pontuacao_str}")
                
    except QuadroAcesso.DoesNotExist:
        print("❌ Quadro 367 não encontrado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_quadro_militares() 