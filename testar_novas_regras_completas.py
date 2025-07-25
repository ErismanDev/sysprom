#!/usr/bin/env python
"""
Script para testar as novas regras completas de quadros de acesso
"""

import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from datetime import date

def testar_novas_regras_completas():
    """Testa as novas regras completas de quadros de acesso"""
    
    print("=== TESTE DAS NOVAS REGRAS COMPLETAS DE QUADROS DE ACESSO ===\n")
    
    # Criar um quadro de teste
    data_promocao = date(2025, 12, 18)
    quadro_teste = QuadroAcesso(tipo='MANUAL', data_promocao=data_promocao)
    
    print("📋 Regras implementadas:")
    print("   🏆 Até 1º Tenente em todos os quadros: SÓ por antiguidade")
    print("      - Aspirante → 2º Tenente")
    print("      - CADOF → 2º Tenente")
    print("      - Subtenente → 2º Tenente")
    print("      - 2º Tenente → 1º Tenente")
    print("      - 1º Tenente → Capitão")
    print()
    print("   🔄 De Capitão para frente: ambas as situações (antiguidade E merecimento)")
    print("      - Capitão → Major")
    print("      - Major → Tenente-Coronel")
    print()
    print("   ⭐ Só por Merecimento:")
    print("      - Tenente-Coronel → Coronel")
    print()
    
    print("🔍 Testando determinação de tipo por transição:")
    
    transicoes_teste = [
        ('AS', '2T'),
        ('CADOF', '2T'),
        ('ST', '2T'),
        ('2T', '1T'),
        ('1T', 'CP'),
        ('CP', 'MJ'),
        ('MJ', 'TC'),
        ('TC', 'CB'),
    ]
    
    for origem, destino in transicoes_teste:
        tipo = quadro_teste.determinar_tipo_quadro_por_transicao(origem, destino)
        if tipo == 'ANTIGUIDADE':
            print(f"   {origem} → {destino}: 🏆 Só por Antiguidade")
        elif tipo == 'MERECIMENTO':
            print(f"   {origem} → {destino}: ⭐ Só por Merecimento")
        elif tipo == 'AMBOS':
            print(f"   {origem} → {destino}: 🔄 Ambos (Antiguidade E Merecimento)")
        else:
            print(f"   {origem} → {destino}: ❓ Tipo não definido")
    
    print()
    print("✅ Teste concluído!")
    print("\n💡 Resumo das regras:")
    print("   - Até 1º Tenente: SÓ por antiguidade")
    print("   - Capitão → Major: Ambos os critérios")
    print("   - Major → Tenente-Coronel: Ambos os critérios")
    print("   - Tenente-Coronel → Coronel: SÓ por merecimento")

if __name__ == '__main__':
    testar_novas_regras_completas() 