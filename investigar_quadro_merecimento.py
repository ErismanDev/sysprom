#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def investigar_quadro_merecimento():
    """Investiga por que os militares não aparecem listados no quadro de merecimento"""
    
    print("=== INVESTIGAÇÃO DO QUADRO DE MERECIMENTO ===\n")
    
    # 1. Buscar o quadro de merecimento mais recente
    quadro = QuadroAcesso.objects.filter(
        tipo='MERECIMENTO',
        status='ELABORADO'
    ).order_by('-data_criacao').first()
    
    if not quadro:
        print("❌ Nenhum quadro de merecimento elaborado encontrado!")
        return
    
    print(f"Quadro: {quadro.get_titulo_completo()}")
    print(f"Data de promoção: {quadro.data_promocao}")
    print(f"Status: {quadro.get_status_display()}")
    print(f"Observações: {quadro.observacoes}")
    
    # 2. Verificar itens do quadro
    itens = quadro.itemquadroacesso_set.all()
    print(f"\nTotal de itens no quadro: {itens.count()}")
    
    if itens.count() == 0:
        print("❌ Nenhum item no quadro!")
        return
    
    print("\n=== DETALHAMENTO DOS ITENS ===")
    for item in itens:
        militar = item.militar
        print(f"\nMilitar: {militar.nome_completo}")
        print(f"  - Quadro: {militar.quadro}")
        print(f"  - Posto: {militar.posto_graduacao}")
        print(f"  - Posição: {item.posicao}")
        print(f"  - Pontuação: {item.pontuacao}")
    
    # 3. Simular a lógica da view
    print("\n=== SIMULANDO A LÓGICA DA VIEW ===")
    
    nomes_postos = dict(QuadroAcesso.POSTO_CHOICES)
    nomes_quadros = dict(QuadroAcesso.QUADRO_CHOICES)
    
    # Definir ordem dos quadros e transições
    quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
    
    # Transições por quadro
    transicoes_por_quadro = {
        'COMB': [
            ('MJ', 'TC'),  # Major para Tenente Coronel
            ('CP', 'MJ'),  # Capitão para Major
            ('1T', 'CP'),  # 1º Tenente para Capitão
            ('2T', '1T'),  # 2º Tenente para 1º Tenente
            ('AS', '2T'),  # Aspirante a Oficial para 2º Tenente
        ],
        'SAUDE': [
            ('MJ', 'TC'),  # Major para Tenente Coronel
            ('CP', 'MJ'),  # Capitão para Major
            ('1T', 'CP'),  # 1º Tenente para Capitão
            ('2T', '1T'),  # 2º Tenente para 1º Tenente
            ('AA', '2T'),  # Aluno de Adaptação para 2º Tenente
        ],
        'ENG': [
            ('MJ', 'TC'),  # Major para Tenente Coronel
            ('CP', 'MJ'),  # Capitão para Major
            ('1T', 'CP'),  # 1º Tenente para Capitão
            ('2T', '1T'),  # 2º Tenente para 1º Tenente
            ('AA', '2T'),  # Aluno de Adaptação para 2º Tenente
        ],
        'COMP': [
            ('MJ', 'TC'),  # Major para Tenente Coronel
            ('CP', 'MJ'),  # Capitão para Major
            ('1T', 'CP'),  # 1º Tenente para Capitão
            ('2T', '1T'),  # 2º Tenente para 1º Tenente
            ('ST', '2T'),  # Subtenente para 2º Tenente
        ],
    }
    
    # Buscar todos os militares aptos do quadro
    militares_aptos = quadro.itemquadroacesso_set.all().select_related('militar').order_by('posicao')
    
    print(f"Militares aptos encontrados: {militares_aptos.count()}")
    
    # Organizar militares por quadro e transição
    estrutura_quadros = {}
    
    for q in quadros:
        estrutura_quadros[q] = {
            'nome': nomes_quadros.get(q, q),
            'transicoes': []
        }
        
        transicoes_do_quadro = transicoes_por_quadro.get(q, [])
        
        for origem, destino in transicoes_do_quadro:
            # Para quadros de merecimento, só mostrar as transições permitidas
            if quadro.tipo == 'MERECIMENTO':
                if not ((origem == 'TC' and destino == 'CB') or (origem == 'MJ' and destino == 'TC') or (origem == 'CP' and destino == 'MJ')):
                    print(f"  Pulando transição {origem}→{destino} (não permitida para merecimento)")
                    continue
            
            militares_desta_transicao = [
                item for item in militares_aptos 
                if item.militar.quadro == q and item.militar.posto_graduacao == origem
            ]
            
            print(f"  Transição {origem}→{destino} no quadro {q}: {len(militares_desta_transicao)} militares")
            
            estrutura_quadros[q]['transicoes'].append({
                'origem': origem,
                'destino': destino,
                'origem_nome': nomes_postos.get(origem, origem),
                'destino_nome': nomes_postos.get(destino, destino),
                'militares': militares_desta_transicao,
            })
    
    # 4. Verificar estrutura final
    print("\n=== ESTRUTURA FINAL ===")
    for q, dados in estrutura_quadros.items():
        print(f"\nQuadro: {dados['nome']}")
        print(f"Transições: {len(dados['transicoes'])}")
        
        for transicao in dados['transicoes']:
            print(f"  {transicao['origem']}→{transicao['destino']}: {len(transicao['militares'])} militares")
            for militar in transicao['militares']:
                print(f"    - {militar.militar.nome_completo} ({militar.militar.posto_graduacao})")
    
    # 5. Verificar se há militares que não estão sendo capturados
    print("\n=== MILITARES NÃO CAPTURADOS ===")
    militares_capturados = set()
    for q, dados in estrutura_quadros.items():
        for transicao in dados['transicoes']:
            for militar in transicao['militares']:
                militares_capturados.add(militar.militar.id)
    
    militares_nao_capturados = []
    for item in militares_aptos:
        if item.militar.id not in militares_capturados:
            militares_nao_capturados.append(item)
    
    if militares_nao_capturados:
        print(f"❌ {len(militares_nao_capturados)} militares não foram capturados:")
        for item in militares_nao_capturados:
            print(f"  - {item.militar.nome_completo} ({item.militar.quadro}-{item.militar.posto_graduacao})")
    else:
        print("✅ Todos os militares foram capturados corretamente")

if __name__ == '__main__':
    investigar_quadro_merecimento() 