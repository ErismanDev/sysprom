#!/usr/bin/env python
"""
Script para ativar todos os militares (situacao = 'AT')
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import transaction
from militares.models import Militar

def ativar_todos_militares():
    print("=== ATIVANDO TODOS OS MILITARES ===\n")
    with transaction.atomic():
        inativos = Militar.objects.exclude(situacao='AT').count()
        if inativos > 0:
            Militar.objects.exclude(situacao='AT').update(situacao='AT')
            print(f"✓ {inativos} militares atualizados para ATIVO (AT)")
        else:
            print("✓ Todos os militares já estão ATIVOS (AT)")
    print("\nProcesso concluído!")

if __name__ == '__main__':
    ativar_todos_militares() 