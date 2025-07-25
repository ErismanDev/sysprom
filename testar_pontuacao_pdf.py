#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, ItemQuadroAcesso

def testar_pontuacao_pdf():
    """Testa se a pontuação está sendo encontrada corretamente no PDF"""
    
    # Buscar todos os quadros de merecimento
    quadros_merecimento = QuadroAcesso.objects.filter(tipo='MERECIMENTO')
    
    print(f"Encontrados {quadros_merecimento.count()} quadros de merecimento")
    
    for quadro in quadros_merecimento:
        print(f"\n=== Quadro {quadro.pk} - {quadro.get_tipo_display()} ===")
        print(f"Data: {quadro.data_promocao}")
        print(f"Categoria: {quadro.categoria}")
        
        # Buscar todos os militares do quadro
        todos_militares = quadro.itemquadroacesso_set.all()
        print(f"Total de militares no quadro: {todos_militares.count()}")
        
        # Verificar militares com pontuação
        militares_com_pontuacao = todos_militares.filter(pontuacao__isnull=False).exclude(pontuacao=0)
        print(f"Militares com pontuação: {militares_com_pontuacao.count()}")
        
        for item in militares_com_pontuacao[:5]:  # Mostrar apenas os primeiros 5
            print(f"  - {item.militar.nome_completo} ({item.militar.posto_graduacao}): {item.pontuacao}")
        
        # Testar a lógica de busca do PDF
        print("\n--- Testando lógica de busca do PDF ---")
        
        # Buscar militares por transição
        if quadro.categoria == 'PRACAS':
            transicoes_teste = [
                ('1S', 'ST'),  # 1º SARGENTO para SUBTENENTE
                ('2S', '1S'),  # 2º SARGENTO para 1º SARGENTO
            ]
        else:
            transicoes_teste = [
                ('TC', 'CB'),  # TENENTE-CORONEL para CORONEL
                ('MJ', 'TC'),  # MAJOR para TENENTE-CORONEL
                ('CP', 'MJ'),  # CAPITÃO para MAJOR
            ]
        
        for origem, destino in transicoes_teste:
            aptos = todos_militares.filter(
                militar__posto_graduacao=origem,
                militar__quadro=quadro.categoria
            ).order_by('posicao')
            
            print(f"\nTransição {origem} → {destino}:")
            print(f"  Militares aptos: {aptos.count()}")
            
            for item in aptos:
                pontuacao_str = f"{item.pontuacao:.2f}" if item.pontuacao else "-"
                print(f"    - {item.militar.nome_completo}: {pontuacao_str}")

if __name__ == '__main__':
    testar_pontuacao_pdf() 