#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.db.models import Count

def verificar_duplicatas():
    print("=== VERIFICANDO DUPLICATAS DE NUMERAÇÃO ===")
    
    # Verificar duplicatas por posto e quadro
    duplicatas = Militar.objects.filter(
        situacao='AT'
    ).values('posto_graduacao', 'quadro', 'numeracao_antiguidade').annotate(
        count=Count('id')
    ).filter(count__gt=1).order_by('posto_graduacao', 'quadro', 'numeracao_antiguidade')
    
    if duplicatas:
        print(f"Encontradas {len(duplicatas)} combinações com duplicatas:")
        for dup in duplicatas:
            print(f"  {dup['posto_graduacao']} - {dup['quadro']}: {dup['numeracao_antiguidade']} (aparece {dup['count']} vezes)")
            
            # Mostrar os militares com essa numeração
            militares = Militar.objects.filter(
                posto_graduacao=dup['posto_graduacao'],
                quadro=dup['quadro'],
                numeracao_antiguidade=dup['numeracao_antiguidade'],
                situacao='AT'
            ).order_by('id')
            
            for militar in militares:
                print(f"    - ID {militar.id}: {militar.nome_completo} (ID: {militar.id})")
    else:
        print("Nenhuma duplicata encontrada!")
    
    print("\n=== VERIFICANDO SEQUÊNCIA POR POSTO/QUADRO ===")
    
    # Verificar se há lacunas na sequência
    postos_quadros = Militar.objects.filter(
        situacao='AT'
    ).values('posto_graduacao', 'quadro').distinct()
    
    for pq in postos_quadros:
        posto = pq['posto_graduacao']
        quadro = pq['quadro']
        
        militares = Militar.objects.filter(
            posto_graduacao=posto,
            quadro=quadro,
            situacao='AT'
        ).order_by('numeracao_antiguidade')
        
        print(f"\n{posto} - {quadro}:")
        print(f"  Total de militares: {militares.count()}")
        
        if militares.exists():
            numeracoes = list(militares.values_list('numeracao_antiguidade', flat=True))
            print(f"  Numerações: {numeracoes}")
            
            # Verificar se começa em 1
            if numeracoes and numeracoes[0] != 1:
                print(f"  ⚠️  Não começa em 1! Primeira numeração: {numeracoes[0]}")
            
            # Verificar se é sequencial
            esperado = list(range(1, len(numeracoes) + 1))
            if numeracoes != esperado:
                print(f"  ⚠️  Sequência incorreta!")
                print(f"     Esperado: {esperado}")
                print(f"     Atual:    {numeracoes}")

if __name__ == '__main__':
    verificar_duplicatas() 