#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, ItemQuadroAcesso

def testar_busca_militares():
    """Testa a lógica de busca dos militares no quadro 367"""
    
    try:
        quadro = QuadroAcesso.objects.get(pk=367)
        print(f"=== Quadro 367 ===")
        print(f"Tipo: {quadro.tipo}")
        print(f"Categoria: {quadro.categoria}")
        
        # Testar a lógica de busca do PDF
        print("\n--- Testando lógica de busca do PDF ---")
        
        # Buscar todos os militares do quadro (lógica corrigida)
        todos_militares = quadro.itemquadroacesso_set.all()
        print(f"Total de militares no quadro: {todos_militares.count()}")
        
        # Testar transições para oficiais
        transicoes_teste = [
            ('TC', 'CB'),  # TENENTE-CORONEL para CORONEL
            ('MJ', 'TC'),  # MAJOR para TENENTE-CORONEL
            ('CP', 'MJ'),  # CAPITÃO para MAJOR
        ]
        
        for origem, destino in transicoes_teste:
            print(f"\n--- Transição {origem} → {destino} ---")
            
            # Usar a mesma lógica do PDF
            aptos = todos_militares.filter(
                militar__posto_graduacao=origem,
                militar__quadro=quadro.categoria
            ).order_by('posicao')
            
            print(f"Militares aptos encontrados: {aptos.count()}")
            
            for item in aptos:
                pontuacao_str = f"{item.pontuacao:.2f}" if item.pontuacao else "-"
                print(f"  - {item.militar.nome_completo} ({item.militar.posto_graduacao}): {pontuacao_str}")
                
                # Verificar se a pontuação está sendo formatada corretamente
                if item.pontuacao:
                    print(f"    Pontuação original: {item.pontuacao}")
                    print(f"    Pontuação formatada: {pontuacao_str}")
        
        # Verificar se há militares com pontuação
        militares_com_pontuacao = todos_militares.filter(pontuacao__isnull=False).exclude(pontuacao=0)
        print(f"\n--- Militares com pontuação ---")
        print(f"Total: {militares_com_pontuacao.count()}")
        
        for item in militares_com_pontuacao:
            print(f"  - {item.militar.nome_completo}: {item.pontuacao}")
            
    except QuadroAcesso.DoesNotExist:
        print("❌ Quadro 367 não encontrado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    testar_busca_militares() 