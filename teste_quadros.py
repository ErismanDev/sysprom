#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso

def testar_quadros():
    """Testa se existem quadros de acesso no banco"""
    
    total = QuadroAcesso.objects.count()
    print(f"Total de quadros de acesso: {total}")
    
    if total > 0:
        print("\nQuadros encontrados:")
        for quadro in QuadroAcesso.objects.all():
            print(f"  - ID: {quadro.id}")
            print(f"    Tipo: {quadro.tipo}")
            print(f"    Categoria: {quadro.categoria}")
            print(f"    Data Promoção: {quadro.data_promocao}")
            print(f"    Status: {quadro.status}")
            print(f"    Ativo: {quadro.ativo}")
            print(f"    Número: {quadro.numero}")
            print("    ---")
    else:
        print("Nenhum quadro de acesso encontrado no banco de dados.")

if __name__ == '__main__':
    testar_quadros() 