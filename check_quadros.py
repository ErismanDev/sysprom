#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroFixacaoVagas

# Verificar todos os quadros de fixação de vagas
quadros = QuadroFixacaoVagas.objects.all().order_by('-data_criacao')

print(f"Total de quadros de fixação de vagas: {quadros.count()}")
print("\nQuadros existentes:")
for quadro in quadros:
    print(f"  ID: {quadro.pk}")
    print(f"  Número: {quadro.numero}")
    print(f"  Tipo: {quadro.tipo}")
    print(f"  Data de Criação: {quadro.data_criacao}")
    print(f"  Data de Promoção: {quadro.data_promocao}")
    print(f"  Status: {quadro.status}")
    print(f"  Título: {quadro.titulo}")
    print("  ---")

# Verificar quadros por tipo
quadros_oficiais = QuadroFixacaoVagas.objects.filter(tipo='OFICIAIS')
quadros_pracas = QuadroFixacaoVagas.objects.filter(tipo='PRACAS')

print(f"\nQuadros de Oficiais: {quadros_oficiais.count()}")
print(f"Quadros de Praças: {quadros_pracas.count()}") 