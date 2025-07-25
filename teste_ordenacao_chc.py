#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.db.models import Q

print("=== TESTE DE ORDENAÇÃO CHC ===")
print()

# Buscar soldados com nota CHC
militares = Militar.objects.filter(
    Q(posto_graduacao='Soldado') & 
    Q(nota_chc__isnull=False)
).order_by('-nota_chc', 'numeracao_antiguidade')

print(f"Total de soldados com CHC: {militares.count()}")
print()

if militares.exists():
    print("Ordenação Soldado → Cabo (CHC):")
    print("Pos | Nome | Nota CHC | Antiguidade")
    print("-" * 50)
    
    for i, militar in enumerate(militares[:10], 1):
        print(f"{i:2d}º | {militar.nome_completo[:20]:20s} | {militar.nota_chc:8.2f} | {militar.numeracao_antiguidade}")
    
    print()
    print("Verificação:")
    print(f"1ª posição - Maior nota: {militares.first().nota_chc}")
    print(f"Última posição - Menor nota: {militares.last().nota_chc}")
    
    if militares.first().nota_chc >= militares.last().nota_chc:
        print("✅ Ordenação CORRETA: Maior nota na 1ª posição")
    else:
        print("❌ Ordenação INCORRETA")
else:
    print("Nenhum soldado com nota CHC encontrado.")

print()
print("=== TESTE DE ORDENAÇÃO CHSGT ===")
print()

# Buscar cabos com nota CHSGT
militares_chsgt = Militar.objects.filter(
    Q(posto_graduacao='Cabo') & 
    Q(nota_chsgt__isnull=False)
).order_by('-nota_chsgt', 'numeracao_antiguidade')

print(f"Total de cabos com CHSGT: {militares_chsgt.count()}")
print()

if militares_chsgt.exists():
    print("Ordenação Cabo → 3º Sargento (CHSGT):")
    print("Pos | Nome | Nota CHSGT | Antiguidade")
    print("-" * 50)
    
    for i, militar in enumerate(militares_chsgt[:10], 1):
        print(f"{i:2d}º | {militar.nome_completo[:20]:20s} | {militar.nota_chsgt:9.2f} | {militar.numeracao_antiguidade}")
    
    print()
    print("Verificação:")
    print(f"1ª posição - Maior nota: {militares_chsgt.first().nota_chsgt}")
    print(f"Última posição - Menor nota: {militares_chsgt.last().nota_chsgt}")
    
    if militares_chsgt.first().nota_chsgt >= militares_chsgt.last().nota_chsgt:
        print("✅ Ordenação CORRETA: Maior nota na 1ª posição")
    else:
        print("❌ Ordenação INCORRETA")
else:
    print("Nenhum cabo com nota CHSGT encontrado.") 