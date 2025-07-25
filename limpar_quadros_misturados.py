#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def limpar_quadros_misturados():
    """Remove militares do grupo errado dos quadros manuais (oficiais em quadros de praças e vice-versa)"""
    print("=== LIMPEZA DE QUADROS MANUAIS MISTURADOS ===")
    
    # Definir grupos
    pracas = ['SD', 'CAB', '3S', '2S', '1S', 'ST']
    oficiais = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    
    # Buscar apenas quadros manuais
    quadros = QuadroAcesso.objects.filter(is_manual=True)
    
    total_removidos = 0
    
    for quadro in quadros:
        print(f"\n📋 Verificando quadro: {quadro.data_promocao} (ID: {quadro.pk})")
        
        # Buscar itens do quadro
        itens = quadro.itemquadroacesso_set.all()
        
        # Verificar se é quadro de praças ou oficiais
        if quadro.criterio_ordenacao_manual in ['ANTIGUIDADE', 'MERECIMENTO']:
            # Quadro de praças - remover oficiais
            itens_errados = itens.filter(militar__posto_graduacao__in=oficiais)
            if itens_errados.exists():
                print(f"   ❌ Encontrados {itens_errados.count()} oficiais em quadro de praças")
                for item in itens_errados:
                    print(f"      - Removendo: {item.militar.nome_completo} ({item.militar.get_posto_graduacao_display()})")
                    item.delete()
                    total_removidos += 1
            else:
                print(f"   ✅ Nenhum oficial encontrado")
        else:
            # Quadro de oficiais - remover praças
            itens_errados = itens.filter(militar__posto_graduacao__in=pracas)
            if itens_errados.exists():
                print(f"   ❌ Encontrados {itens_errados.count()} praças em quadro de oficiais")
                for item in itens_errados:
                    print(f"      - Removendo: {item.militar.nome_completo} ({item.militar.get_posto_graduacao_display()})")
                    item.delete()
                    total_removidos += 1
            else:
                print(f"   ✅ Nenhuma praça encontrada")
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   Total de itens removidos: {total_removidos}")
    
    if total_removidos > 0:
        print(f"\n✅ Limpeza concluída! {total_removidos} militares removidos de quadros manuais incorretos.")
    else:
        print(f"\n✅ Nenhum militar encontrado em quadros manuais incorretos.")

if __name__ == '__main__':
    limpar_quadros_misturados() 