#!/usr/bin/env python
"""
Script para verificar e atualizar quadros manuais que não tenham critério de ordenação definido
"""

import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso

def atualizar_criterios_manuais():
    """Verifica e atualiza quadros manuais sem critério de ordenação definido"""
    
    print("=== ATUALIZAÇÃO DE CRITÉRIOS DE ORDENAÇÃO MANUAL ===\n")
    
    # Buscar quadros manuais
    quadros_manuais = QuadroAcesso.objects.filter(is_manual=True)
    
    if not quadros_manuais.exists():
        print("❌ Nenhum quadro manual encontrado no banco de dados.")
        return
    
    print(f"📊 Encontrados {quadros_manuais.count()} quadros manuais:\n")
    
    quadros_atualizados = 0
    
    for quadro in quadros_manuais:
        print(f"🔍 Quadro ID {quadro.id}:")
        print(f"   Tipo: {quadro.get_tipo_display()}")
        print(f"   Status: {quadro.get_status_display()}")
        print(f"   Critério Atual: {quadro.criterio_ordenacao_manual}")
        print(f"   Data Promoção: {quadro.data_promocao.strftime('%d/%m/%Y')}")
        print(f"   Militares no Quadro: {quadro.itemquadroacesso_set.count()}")
        
        # Verificar se precisa atualizar
        if not quadro.criterio_ordenacao_manual or quadro.criterio_ordenacao_manual == 'MANUAL':
            # Verificar se tem militares com pontuação
            itens_com_pontuacao = quadro.itemquadroacesso_set.filter(pontuacao__gt=0)
            
            if itens_com_pontuacao.exists():
                # Se tem pontuação, definir como merecimento
                novo_criterio = 'MERECIMENTO'
                print(f"   ⚠️  Atualizando para: {novo_criterio} (tem militares com pontuação)")
            else:
                # Se não tem pontuação, definir como antiguidade
                novo_criterio = 'ANTIGUIDADE'
                print(f"   ⚠️  Atualizando para: {novo_criterio} (sem pontuação)")
            
            # Atualizar o quadro
            quadro.criterio_ordenacao_manual = novo_criterio
            quadro.save()
            quadros_atualizados += 1
            print(f"   ✅ Atualizado!")
        else:
            print(f"   ✅ Já tem critério definido")
        
        print()
    
    print("=== RESUMO ===")
    print(f"📊 Total de quadros manuais: {quadros_manuais.count()}")
    print(f"✅ Quadros atualizados: {quadros_atualizados}")
    print(f"📋 Quadros já corretos: {quadros_manuais.count() - quadros_atualizados}")
    
    if quadros_atualizados > 0:
        print(f"\n🎉 {quadros_atualizados} quadros foram atualizados com sucesso!")
    else:
        print(f"\n✅ Todos os quadros já estão com critérios definidos!")

if __name__ == '__main__':
    atualizar_criterios_manuais() 