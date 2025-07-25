#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def testar_lógica_datas():
    """Testa a nova lógica de datas baseada na data de geração"""
    
    print("=== TESTE DA LÓGICA DE DATAS ===\n")
    
    # Função para determinar a data de promoção
    def determinar_data_promocao(data_geracao, tipo):
        if tipo == 'OFICIAIS':
            # Se gerado entre 18/07 e 23/12: usar 18/07/2025
            # Se gerado entre 23/12 e 18/07: usar 23/12/2025
            if (data_geracao.month == 7 and data_geracao.day >= 18) or (data_geracao.month > 7 and data_geracao.month < 12) or (data_geracao.month == 12 and data_geracao.day < 23):
                return "18/07/2025"
            else:
                return "23/12/2025"
        elif tipo == 'PRACAS':
            # Se gerado entre 18/07 e 25/12: usar 18/07/2025
            # Se gerado entre 25/12 e 18/07: usar 25/12/2025
            if (data_geracao.month == 7 and data_geracao.day >= 18) or (data_geracao.month > 7 and data_geracao.month < 12) or (data_geracao.month == 12 and data_geracao.day < 25):
                return "18/07/2025"
            else:
                return "25/12/2025"
        else:  # GERAL
            return "18/07/2025"
    
    # Datas de teste
    datas_teste = [
        date(2025, 7, 15),   # 15/07/2025 - antes da primeira promoção
        date(2025, 7, 18),   # 18/07/2025 - dia da primeira promoção
        date(2025, 7, 20),   # 20/07/2025 - após primeira promoção
        date(2025, 8, 15),   # 15/08/2025 - agosto
        date(2025, 10, 15),  # 15/10/2025 - outubro
        date(2025, 12, 20),  # 20/12/2025 - antes da segunda promoção
        date(2025, 12, 23),  # 23/12/2025 - dia da segunda promoção (oficiais)
        date(2025, 12, 25),  # 25/12/2025 - dia da segunda promoção (praças)
        date(2025, 12, 30),  # 30/12/2025 - após segunda promoção
        date(2026, 1, 15),   # 15/01/2026 - janeiro do ano seguinte
        date(2026, 6, 15),   # 15/06/2026 - junho do ano seguinte
    ]
    
    tipos_teste = ['OFICIAIS', 'PRACAS', 'GERAL']
    
    for tipo in tipos_teste:
        print(f"🔍 Testando tipo: {tipo}")
        print(f"   {'Data de Geração':<15} | {'Data de Promoção':<15}")
        print(f"   {'-'*15} | {'-'*15}")
        
        for data_teste in datas_teste:
            data_promocao = determinar_data_promocao(data_teste, tipo)
            print(f"   {data_teste.strftime('%d/%m/%Y'):<15} | {data_promocao:<15}")
        
        print()
    
    print("=== RESUMO DA LÓGICA ===")
    print("📅 OFICIAIS:")
    print("   - 18/07 a 22/12: 18/07/2025")
    print("   - 23/12 a 17/07: 23/12/2025")
    print()
    print("📅 PRAÇAS:")
    print("   - 18/07 a 24/12: 18/07/2025")
    print("   - 25/12 a 17/07: 25/12/2025")
    print()
    print("📅 GERAL:")
    print("   - Sempre: 18/07/2025")

if __name__ == "__main__":
    testar_lógica_datas() 