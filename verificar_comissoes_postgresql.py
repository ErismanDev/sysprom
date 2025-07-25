#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import ComissaoPromocao

def verificar_comissoes_postgresql():
    print("=== VERIFICANDO COMISSÕES NO POSTGRESQL ===\n")
    
    comissoes = ComissaoPromocao.objects.all()
    print(f"Total de comissões: {comissoes.count()}")
    
    for comissao in comissoes:
        print(f"  • ID: {comissao.id} - {comissao.nome} ({comissao.tipo}) - {comissao.status}")

if __name__ == '__main__':
    verificar_comissoes_postgresql() 