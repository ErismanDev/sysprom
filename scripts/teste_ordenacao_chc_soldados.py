#!/usr/bin/env python
"""
Script para testar a ordenação de soldados com CHC no quadro de acesso por antiguidade.
Testa se soldados com CHC são ordenados pela nota do curso (maior nota primeiro) 
e desempate pela numeração de antiguidade (menor número = mais antigo).
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from django.utils import timezone
from datetime import date

def testar_ordenacao_chc_soldados():
    """Testa a ordenação de soldados com CHC no quadro de acesso"""
    print("=== TESTE DE ORDENAÇÃO DE SOLDADOS COM CHC ===")
    
    # Buscar soldados com CHC
    soldados_chc = Militar.objects.filter(
        posto_graduacao='SD',
        curso_chc=True,
        situacao='AT'
    ).order_by('nome_completo')
    
    if not soldados_chc.exists():
        print("❌ Nenhum soldado com CHC encontrado no sistema.")
        print("Crie alguns soldados com CHC e notas diferentes para testar.")
        return
    
    print(f"✅ Encontrados {soldados_chc.count()} soldados com CHC:")
    
    # Mostrar informações dos soldados
    for i, soldado in enumerate(soldados_chc, 1):
        nota_chc = soldado.nota_chc or 0
        numeracao = soldado.numeracao_antiguidade or 999999
        print(f"  {i}. {soldado.nome_completo}")
        print(f"     - Nota CHC: {nota_chc}")
        print(f"     - Numeração: {numeracao}")
        print(f"     - Data promoção: {soldado.data_promocao_atual}")
        print()
    
    # Criar quadro de acesso para testar
    data_promocao = date(2025, 8, 1)
    
    # Verificar se já existe um quadro de acesso para praças nesta data
    quadro_existente = QuadroAcesso.objects.filter(
        tipo='ANTIGUIDADE',
        categoria='PRACAS',
        data_promocao=data_promocao
    ).first()
    
    if quadro_existente:
        print(f"⚠️  Usando quadro existente: {quadro_existente}")
        quadro = quadro_existente
    else:
        print(f"📋 Criando novo quadro de acesso para praças em {data_promocao}")
        quadro = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='PRACAS',
            data_promocao=data_promocao,
            status='EM_ELABORACAO'
        )
    
    # Gerar quadro
    print("\n🔄 Gerando quadro de acesso...")
    sucesso, mensagem = quadro.gerar_quadro_completo()
    
    if sucesso:
        print(f"✅ {mensagem}")
        
        # Buscar itens do quadro ordenados
        itens_quadro = quadro.itemquadroacesso_set.all().order_by('posicao')
        
        print(f"\n📊 Resultado da ordenação ({itens_quadro.count()} militares):")
        print("-" * 80)
        
        # Filtrar apenas soldados com CHC para mostrar a ordenação
        soldados_ordenados = []
        for item in itens_quadro:
            if item.militar.posto_graduacao == 'SD' and item.militar.curso_chc:
                soldados_ordenados.append(item)
        
        if soldados_ordenados:
            print(f"🎯 Soldados com CHC no quadro ({len(soldados_ordenados)}):")
            for i, item in enumerate(soldados_ordenados, 1):
                militar = item.militar
                nota_chc = militar.nota_chc or 0
                numeracao = militar.numeracao_antiguidade or 999999
                
                print(f"  {item.posicao}ª posição: {militar.nome_completo}")
                print(f"     - Nota CHC: {nota_chc}")
                print(f"     - Numeração: {numeracao}")
                print(f"     - Pontuação: {item.pontuacao}")
                print()
            
            # Verificar se a ordenação está correta
            print("🔍 Verificando ordenação...")
            ordenacao_correta = True
            
            for i in range(len(soldados_ordenados) - 1):
                atual = soldados_ordenados[i]
                proximo = soldados_ordenados[i + 1]
                
                nota_atual = atual.militar.nota_chc or 0
                nota_proximo = proximo.militar.nota_chc or 0
                num_atual = atual.militar.numeracao_antiguidade or 999999
                num_proximo = proximo.militar.numeracao_antiguidade or 999999
                
                # Verificar se a ordenação está correta:
                # 1. Maior nota CHC primeiro
                # 2. Em caso de empate, menor numeração primeiro
                if nota_atual < nota_proximo:
                    print(f"❌ ERRO: {atual.militar.nome_completo} (nota {nota_atual}) vem antes de {proximo.militar.nome_completo} (nota {nota_proximo})")
                    ordenacao_correta = False
                elif nota_atual == nota_proximo and num_atual > num_proximo:
                    print(f"❌ ERRO: Empate de nota {nota_atual}, mas {atual.militar.nome_completo} (num {num_atual}) vem antes de {proximo.militar.nome_completo} (num {num_proximo})")
                    ordenacao_correta = False
            
            if ordenacao_correta:
                print("✅ Ordenação está correta!")
                print("   - Soldados com CHC ordenados pela nota (maior primeiro)")
                print("   - Desempate pela numeração de antiguidade (menor primeiro)")
            else:
                print("❌ Ordenação incorreta detectada!")
        else:
            print("⚠️  Nenhum soldado com CHC foi incluído no quadro.")
            print("Verifique se os soldados atendem aos requisitos do quadro.")
    else:
        print(f"❌ Erro ao gerar quadro: {mensagem}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    testar_ordenacao_chc_soldados() 