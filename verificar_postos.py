#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def verificar_postos():
    """Verifica quais postos têm militares"""
    
    print("=== VERIFICANDO POSTOS COM MILITARES ===\n")
    
    # Buscar todos os militares ativos agrupados por posto
    militares_por_posto = {}
    
    for militar in Militar.objects.filter(situacao='AT').order_by('posto_graduacao', 'numeracao_antiguidade'):
        posto = militar.posto_graduacao
        if posto not in militares_por_posto:
            militares_por_posto[posto] = []
        militares_por_posto[posto].append(militar)
    
    for posto, militares in militares_por_posto.items():
        print(f"📊 {posto}: {len(militares)} militares")
        for m in militares[:3]:  # Mostrar apenas os 3 primeiros
            print(f"  - {m.nome_completo}: {m.numeracao_antiguidade}º")
        if len(militares) > 3:
            print(f"  ... e mais {len(militares) - 3} militares")
        print()

if __name__ == "__main__":
    verificar_postos() 