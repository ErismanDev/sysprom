#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import AlmanaqueMilitar

def testar_datas_promocao():
    """Testa as datas de promoção nos almanaques"""
    
    print("=== TESTE DE DATAS DE PROMOÇÃO NOS ALMANAQUES ===\n")
    
    # Datas de promoção definidas
    data_promocao_1 = date(2025, 7, 18)   # 18/07/2025
    data_promocao_2_oficiais = date(2025, 12, 23)  # 23/12/2025
    data_promocao_2_pracas = date(2025, 12, 25)    # 25/12/2025
    
    print("📅 Datas de promoção configuradas:")
    print(f"   - Primeira promoção: {data_promocao_1.strftime('%d/%m/%Y')}")
    print(f"   - Segunda promoção OFICIAIS: {data_promocao_2_oficiais.strftime('%d/%m/%Y')}")
    print(f"   - Segunda promoção PRAÇAS: {data_promocao_2_pracas.strftime('%d/%m/%Y')}")
    print()
    
    # Simular diferentes datas atuais para testar a lógica
    datas_teste = [
        date(2025, 7, 15),   # Antes da primeira promoção
        date(2025, 7, 20),   # Após a primeira promoção
        date(2025, 12, 20),  # Antes da segunda promoção de oficiais
        date(2025, 12, 24),  # Após a segunda promoção de oficiais
        date(2025, 12, 26),  # Após a segunda promoção de praças
    ]
    
    print("🔍 Testando lógica de datas:")
    for data_atual in datas_teste:
        print(f"\n📅 Data atual: {data_atual.strftime('%d/%m/%Y')}")
        
        # Testar para OFICIAIS
        if data_atual <= data_promocao_2_oficiais:
            data_ultima_promocao_oficiais = data_promocao_1
        else:
            data_ultima_promocao_oficiais = data_promocao_2_oficiais
        print(f"   🎖️  OFICIAIS: última promoção = {data_ultima_promocao_oficiais.strftime('%d/%m/%Y')}")
        
        # Testar para PRAÇAS
        if data_atual <= data_promocao_2_pracas:
            data_ultima_promocao_pracas = data_promocao_1
        else:
            data_ultima_promocao_pracas = data_promocao_2_pracas
        print(f"   👥 PRAÇAS: última promoção = {data_ultima_promocao_pracas.strftime('%d/%m/%Y')}")
        
        # Testar para GERAL
        if data_atual <= data_promocao_2_pracas:
            data_ultima_promocao_geral = data_promocao_1
        else:
            data_ultima_promocao_geral = data_promocao_2_pracas
        print(f"   🌐 GERAL: última promoção = {data_ultima_promocao_geral.strftime('%d/%m/%Y')}")
    
    # Verificar almanaques existentes
    print("\n=== ALMANAQUES EXISTENTES ===")
    almanaques = AlmanaqueMilitar.objects.filter(ativo=True).order_by('-data_geracao')[:10]
    
    if almanaques.exists():
        for almanaque in almanaques:
            print(f"📋 {almanaque.numero} - {almanaque.titulo}")
            print(f"   Tipo: {almanaque.get_tipo_display()}")
            print(f"   Data de geração: {almanaque.data_geracao.strftime('%d/%m/%Y %H:%M')}")
            if almanaque.data_ultima_promocao:
                print(f"   Data última promoção: {almanaque.data_ultima_promocao.strftime('%d/%m/%Y')}")
            else:
                print(f"   Data última promoção: Não definida")
            print()
    else:
        print("❌ Nenhum almanaque encontrado no banco de dados")
    
    print("=== RESUMO ===")
    print("✅ Datas de promoção configuradas:")
    print("   - OFICIAIS: 18/07/2025 e 23/12/2025")
    print("   - PRAÇAS: 18/07/2025 e 25/12/2025")
    print("   - GERAL: usa a data mais recente entre todas")
    print()
    print("📝 Como funciona:")
    print("   - Se a data atual <= segunda promoção: usa primeira promoção (18/07)")
    print("   - Se a data atual > segunda promoção: usa segunda promoção")
    print("   - Para GERAL: sempre usa a data mais recente disponível")

if __name__ == "__main__":
    testar_datas_promocao() 