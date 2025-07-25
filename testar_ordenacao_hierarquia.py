#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def testar_ordenacao_hierarquia():
    print("=== TESTE DE ORDENAÇÃO POR HIERARQUIA ===\n")
    
    # Buscar o quadro mais recente
    quadro = QuadroAcesso.objects.filter(status='ELABORADO').order_by('-data_promocao').first()
    
    if not quadro:
        print("Nenhum quadro elaborado encontrado!")
        return
    
    print(f"Quadro: {quadro.get_titulo_completo()}")
    print(f"Data de promoção: {quadro.data_promocao}")
    print(f"Tipo: {quadro.get_tipo_display()}")
    
    # Verificar itens do quadro
    itens_quadro = quadro.itemquadroacesso_set.all().order_by('posicao')
    print(f"\nTotal de itens no quadro: {itens_quadro.count()}")
    
    print(f"\n--- ORDENAÇÃO ATUAL DO QUADRO ---")
    for item in itens_quadro:
        militar = item.militar
        print(f"Posição {item.posicao}: {militar.get_posto_graduacao_display()} {militar.nome_completo} ({militar.get_quadro_display()})")
    
    # Verificar se a ordenação está correta
    print(f"\n--- ANÁLISE DA ORDENAÇÃO ---")
    
    # Definir hierarquia correta dos postos (mais alto para mais baixo)
    hierarquia_postos = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'ST', '1S', '2S', '3S', 'CB', 'SD']
    
    # Definir hierarquia dos quadros
    hierarquia_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    
    itens_lista = list(itens_quadro)
    ordenacao_correta = True
    
    for i in range(len(itens_lista) - 1):
        item_atual = itens_lista[i]
        item_proximo = itens_lista[i + 1]
        
        militar_atual = item_atual.militar
        militar_proximo = item_proximo.militar
        
        # Verificar se o quadro está na ordem correta
        indice_quadro_atual = hierarquia_quadros.index(militar_atual.quadro) if militar_atual.quadro in hierarquia_quadros else 999
        indice_quadro_proximo = hierarquia_quadros.index(militar_proximo.quadro) if militar_proximo.quadro in hierarquia_quadros else 999
        
        # Verificar se o posto está na ordem correta
        indice_posto_atual = hierarquia_postos.index(militar_atual.posto_graduacao) if militar_atual.posto_graduacao in hierarquia_postos else 999
        indice_posto_proximo = hierarquia_postos.index(militar_proximo.posto_graduacao) if militar_proximo.posto_graduacao in hierarquia_postos else 999
        
        print(f"\nComparando posições {item_atual.posicao} e {item_proximo.posicao}:")
        print(f"  Atual: {militar_atual.get_posto_graduacao_display()} {militar_atual.nome_completo} ({militar_atual.get_quadro_display()})")
        print(f"  Próximo: {militar_proximo.get_posto_graduacao_display()} {militar_proximo.nome_completo} ({militar_proximo.get_quadro_display()})")
        
        # Verificar se a ordenação está correta
        if indice_quadro_atual < indice_quadro_proximo:
            print(f"  ✓ Quadro correto: {militar_atual.get_quadro_display()} vem antes de {militar_proximo.get_quadro_display()}")
        elif indice_quadro_atual > indice_quadro_proximo:
            print(f"  ✗ ERRO: Quadro incorreto: {militar_atual.get_quadro_display()} não deveria vir antes de {militar_proximo.get_quadro_display()}")
            ordenacao_correta = False
        else:
            # Mesmo quadro, verificar posto
            if indice_posto_atual < indice_posto_proximo:
                print(f"  ✓ Posto correto: {militar_atual.get_posto_graduacao_display()} vem antes de {militar_proximo.get_posto_graduacao_display()}")
            elif indice_posto_atual > indice_posto_proximo:
                print(f"  ✗ ERRO: Posto incorreto: {militar_atual.get_posto_graduacao_display()} não deveria vir antes de {militar_proximo.get_posto_graduacao_display()}")
                ordenacao_correta = False
            else:
                print(f"  ✓ Mesmo posto: {militar_atual.get_posto_graduacao_display()}")
    
    print(f"\n--- RESULTADO ---")
    if ordenacao_correta:
        print("✓ A ordenação está respeitando a hierarquia correta!")
    else:
        print("✗ A ordenação NÃO está respeitando a hierarquia correta!")
    
    # Mostrar como deveria ser a ordenação correta
    print(f"\n--- ORDENAÇÃO CORRETA ESPERADA ---")
    
    # Simular a ordenação correta
    militares_ordenados = []
    for item in itens_quadro:
        militar = item.militar
        indice_quadro = hierarquia_quadros.index(militar.quadro) if militar.quadro in hierarquia_quadros else 999
        indice_posto = hierarquia_postos.index(militar.posto_graduacao) if militar.posto_graduacao in hierarquia_postos else 999
        
        militares_ordenados.append({
            'militar': militar,
            'indice_quadro': indice_quadro,
            'indice_posto': indice_posto,
            'posicao_atual': item.posicao
        })
    
    # Ordenar corretamente
    militares_ordenados.sort(key=lambda x: (x['indice_quadro'], x['indice_posto']))
    
    for i, item in enumerate(militares_ordenados, 1):
        militar = item['militar']
        print(f"Posição {i} (atual: {item['posicao_atual']}): {militar.get_posto_graduacao_display()} {militar.nome_completo} ({militar.get_quadro_display()})")

if __name__ == '__main__':
    testar_ordenacao_hierarquia() 