#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao

# Verificar cargos com "Secretário"
secretarios = CargoFuncao.objects.filter(nome__icontains='Secretário')
print('=== CARGOS COM "SECRETÁRIO" ===')
for cargo in secretarios:
    print(f'ID: {cargo.id} | Nome: "{cargo.nome}" | Descrição: "{cargo.descricao}"')
print(f'\nTotal encontrado: {secretarios.count()}')

# Verificar todos os cargos para ver se há algum problema
print('\n=== TODOS OS CARGOS ===')
todos_cargos = CargoFuncao.objects.all().order_by('nome')
for cargo in todos_cargos:
    print(f'ID: {cargo.id} | Nome: "{cargo.nome}"') 