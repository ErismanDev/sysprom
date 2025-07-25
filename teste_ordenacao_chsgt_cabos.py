#!/usr/bin/env python
"""
Script para testar detalhadamente a ordenação de cabos com CHSGT.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from datetime import date

def testar_ordenacao_detalhada_chsgt():
    """Testa a ordenação detalhadamente para cabos com CHSGT"""
    print("=== TESTE DETALHADO DE ORDENAÇÃO DE CABOS COM CHSGT ===")
    
    # Buscar cabos com CHSGT
    cabos = Militar.objects.filter(
        posto_graduacao='CAB',
        curso_chsgt=True,
        situacao='AT'
    ).order_by('nome_completo')
    
    print(f"Encontrados {cabos.count()} cabos com CHSGT:")
    for i, cabo in enumerate(cabos, 1):
        print(f"  {i}. {cabo.nome_completo}")
        print(f"     - Nota CHSGT: {cabo.nota_chsgt}")
        print(f"     - Numeração: {cabo.numeracao_antiguidade}")
        print()
    
    # Criar quadro de acesso
    data_promocao = date(2025, 8, 1)
    quadro = QuadroAcesso.objects.filter(
        tipo='ANTIGUIDADE',
        categoria='PRACAS',
        data_promocao=data_promocao
    ).first()
    
    if not quadro:
        print("Criando novo quadro...")
        quadro = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='PRACAS',
            data_promocao=data_promocao,
            status='EM_ELABORACAO'
        )
    
    # Gerar quadro
    print("Gerando quadro...")
    sucesso, mensagem = quadro.gerar_quadro_completo()
    
    if sucesso:
        print(f"✅ {mensagem}")
        
        # Buscar itens do quadro
        itens = quadro.itemquadroacesso_set.all().order_by('posicao')
        
        print(f"\nResultado da ordenação ({itens.count()} militares):")
        print("-" * 80)
        
        # Filtrar apenas cabos com CHSGT
        cabos_ordenados = []
        for item in itens:
            if item.militar.posto_graduacao == 'CAB' and item.militar.curso_chsgt:
                cabos_ordenados.append(item)
        
        if cabos_ordenados:
            print(f"Cabos com CHSGT no quadro ({len(cabos_ordenados)}):")
            for i, item in enumerate(cabos_ordenados, 1):
                militar = item.militar
                nota_chsgt = militar.nota_chsgt or 0
                numeracao = militar.numeracao_antiguidade or 999999
                
                print(f"  {item.posicao}ª posição: {militar.nome_completo}")
                print(f"     - Nota CHSGT: {nota_chsgt}")
                print(f"     - Numeração: {numeracao}")
                print(f"     - Pontuação: {item.pontuacao}")
                print()
            
            # Verificar se a ordenação está correta
            print("Verificando ordenação...")
            ordenacao_correta = True
            
            for i in range(len(cabos_ordenados) - 1):
                atual = cabos_ordenados[i]
                proximo = cabos_ordenados[i + 1]
                
                nota_atual = atual.militar.nota_chsgt or 0
                nota_proximo = proximo.militar.nota_chsgt or 0
                num_atual = atual.militar.numeracao_antiguidade or 999999
                num_proximo = proximo.militar.numeracao_antiguidade or 999999
                
                print(f"Comparando:")
                print(f"  {atual.militar.nome_completo} (nota {nota_atual}, num {num_atual})")
                print(f"  {proximo.militar.nome_completo} (nota {nota_proximo}, num {num_proximo})")
                
                # Verificar se a ordenação está correta:
                # 1. Maior nota CHSGT primeiro
                # 2. Em caso de empate, menor numeração primeiro
                if nota_atual < nota_proximo:
                    print(f"❌ ERRO: {atual.militar.nome_completo} (nota {nota_atual}) vem antes de {proximo.militar.nome_completo} (nota {nota_proximo})")
                    ordenacao_correta = False
                elif nota_atual == nota_proximo and num_atual > num_proximo:
                    print(f"❌ ERRO: Empate de nota {nota_atual}, mas {atual.militar.nome_completo} (num {num_atual}) vem antes de {proximo.militar.nome_completo} (num {num_proximo})")
                    ordenacao_correta = False
                else:
                    print(f"✅ OK: Ordenação correta")
                print()
            
            if ordenacao_correta:
                print("✅ Ordenação está correta!")
                print("   - Cabos com CHSGT ordenados pela nota (maior primeiro)")
                print("   - Desempate pela numeração de antiguidade (menor primeiro)")
            else:
                print("❌ Ordenação incorreta detectada!")
        else:
            print("⚠️  Nenhum cabo com CHSGT foi incluído no quadro.")
            print("Verifique se os cabos atendem aos requisitos do quadro.")
    else:
        print(f"❌ Erro ao gerar quadro: {mensagem}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    testar_ordenacao_detalhada_chsgt() 