#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_reordenacao_manual():
    """Testa a reordenação manual por data de promoção"""
    
    print("=== TESTE DE REORDENAÇÃO MANUAL POR DATA DE PROMOÇÃO ===\n")
    
    # Escolher um posto para testar (ex: 1T - 1º Tenente)
    posto_teste = '1T'
    
    print(f"📊 Testando reordenação para posto: {posto_teste}")
    
    # Listar militares antes da reordenação
    print(f"\n📋 Militares ANTES da reordenação:")
    militares_antes = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto_teste
    ).order_by('numeracao_antiguidade')
    
    for m in militares_antes:
        print(f"  - {m.nome_completo}: {m.numeracao_antiguidade}º (promovido em: {m.data_promocao_atual})")
    
    # Executar reordenação
    print(f"\n🔄 Executando reordenação...")
    total_reordenados = Militar.reordenar_numeracoes_por_antiguidade_promocao(posto_graduacao=posto_teste)
    
    print(f"✅ Total de militares reordenados: {total_reordenados}")
    
    # Listar militares após a reordenação
    print(f"\n📋 Militares DEPOIS da reordenação:")
    militares_depois = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto_teste
    ).order_by('numeracao_antiguidade')
    
    for m in militares_depois:
        print(f"  - {m.nome_completo}: {m.numeracao_antiguidade}º (promovido em: {m.data_promocao_atual})")
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    testar_reordenacao_manual() 