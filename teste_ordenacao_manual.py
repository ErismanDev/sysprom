#!/usr/bin/env python
"""
Script para testar os diferentes critérios de ordenação manual
"""

import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar, ItemQuadroAcesso

def testar_ordenacao_manual():
    """Testa os diferentes critérios de ordenação manual"""
    
    print("=== TESTE DE ORDENAÇÃO MANUAL ===\n")
    
    # Buscar militares para teste
    militares = Militar.objects.filter(situacao='AT')[:3]
    
    if not militares.exists():
        print("❌ Nenhum militar ativo encontrado para teste!")
        return
    
    # Testar cada critério de ordenação
    criterios = ['MANUAL', 'ANTIGUIDADE', 'MERECIMENTO']
    
    for i, criterio in enumerate(criterios):
        print(f"=== TESTANDO CRITÉRIO: {criterio} ===")
        
        # Criar quadro manual com data diferente para cada teste
        data_promocao = date(2025, 8, 15 + i)  # 15, 16, 17 de agosto
        quadro = QuadroAcesso.objects.create(
            tipo='MANUAL',
            data_promocao=data_promocao,
            status='EM_ELABORACAO',
            is_manual=True,
            criterio_ordenacao_manual=criterio,
            observacoes=f"Teste de ordenação por {criterio.lower()}"
        )
        
        print(f"✅ Quadro criado: {quadro.get_titulo_completo()}")
        print(f"   Critério: {quadro.get_criterio_ordenacao()}")
        print()
        
        # Adicionar militares
        print("Adicionando militares...")
        for i, militar in enumerate(militares):
            try:
                if criterio == 'MANUAL':
                    # Para ordem manual, definir posições específicas
                    posicao = 3 - i  # Posições invertidas: 3, 2, 1
                    pontuacao = 100 + i
                else:
                    # Para ordenação automática, não definir posição
                    posicao = None
                    pontuacao = 0
                
                quadro.adicionar_militar_manual(militar, posicao, pontuacao)
                print(f"✅ Militar {i+1}: {militar.nome_completo}")
                
                if criterio == 'ANTIGUIDADE':
                    print(f"   Antiguidade: {militar.numeracao_antiguidade or 'N/A'}")
                elif criterio == 'MERECIMENTO':
                    ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
                    if ficha:
                        print(f"   Pontuação Ficha: {ficha.pontos}")
                    else:
                        print(f"   Pontuação Ficha: N/A")
                
            except Exception as e:
                print(f"❌ Erro ao adicionar militar {i+1}: {e}")
        
        print()
        
        # Verificar ordenação final
        itens = ItemQuadroAcesso.objects.filter(quadro_acesso=quadro).order_by('posicao')
        
        print("=== ORDENAÇÃO FINAL ===")
        for item in itens:
            print(f"  {item.posicao}º - {item.militar.nome_completo}")
            if criterio == 'ANTIGUIDADE':
                print(f"      Antiguidade: {item.militar.numeracao_antiguidade or 'N/A'}")
            elif criterio == 'MERECIMENTO':
                ficha = item.militar.fichaconceitooficiais_set.first() or item.militar.fichaconceitopracas_set.first()
                if ficha:
                    print(f"      Pontuação: {ficha.pontos}")
                else:
                    print(f"      Pontuação: N/A")
            else:
                print(f"      Pontuação Manual: {item.pontuacao}")
        
        print()
        print(f"Critério de ordenação: {quadro.get_criterio_ordenacao()}")
        print(f"Quadro ID: {quadro.pk}")
        print("-" * 50)
        print()

if __name__ == '__main__':
    testar_ordenacao_manual() 