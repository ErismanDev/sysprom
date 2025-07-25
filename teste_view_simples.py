#!/usr/bin/env python3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import ModeloAta

print("=== TESTE SIMPLES ===")
modelos = ModeloAta.objects.all()
print(f"Modelos existentes: {modelos.count()}")

for modelo in modelos:
    print(f"- {modelo.nome} ({modelo.tipo_comissao})")

print("Teste concluído!") 