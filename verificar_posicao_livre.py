#!/usr/bin/env python
"""
Script para verificar se uma posição específica está livre
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def verificar_posicao():
    militares_1s = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='1S',
        quadro='PRACAS'
    ).order_by('numeracao_antiguidade')
    
    print("Militares 1º Sargento - Praças:")
    for militar in militares_1s:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Verificar se posição 20 está livre
    posicao_20 = militares_1s.filter(numeracao_antiguidade=20).first()
    if posicao_20:
        print(f"\n❌ Posição 20 está ocupada por: {posicao_20.nome_completo}")
    else:
        print(f"\n✅ Posição 20 está livre")

if __name__ == "__main__":
    verificar_posicao() 