#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, UsuarioFuncao

def listar_funcoes_cargos():
    print('=== LISTAGEM DE CARGOS/FUNÇÕES E USUÁRIOS ===\n')
    cargos = CargoFuncao.objects.all().order_by('nome')
    for cargo in cargos:
        total = UsuarioFuncao.objects.filter(cargo_funcao=cargo).count()
        ativos = UsuarioFuncao.objects.filter(cargo_funcao=cargo, status='ATIVO').count()
        print(f'- {cargo.nome:40} | Usuários com esta função: {total} | Ativos: {ativos}')
    print('\n=== FIM ===')

if __name__ == '__main__':
    listar_funcoes_cargos() 