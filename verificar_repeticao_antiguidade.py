#!/usr/bin/env python
"""
Script para verificar duplicidade de numeracao_antiguidade entre militares ativos do mesmo posto/quadro
"""
import os
import django
from collections import Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def verificar_repeticao():
    qs = Militar.objects.filter(situacao='AT')
    grupos = {}
    for militar in qs:
        chave = (militar.posto_graduacao, militar.quadro)
        grupos.setdefault(chave, []).append(militar)
    encontrou = False
    for (posto, quadro), grupo in grupos.items():
        c = Counter(m.numeracao_antiguidade for m in grupo)
        repetidos = [n for n, count in c.items() if n and count > 1]
        if repetidos:
            encontrou = True
            print(f'Posto: {posto}, Quadro: {quadro}, Repetidos: {repetidos}')
            for n in repetidos:
                print('  -', [f"{m.nome_completo} (id={m.id})" for m in grupo if m.numeracao_antiguidade == n])
    if not encontrou:
        print('✅ Não há repetição de antiguidade entre militares ativos do mesmo posto/quadro.')

if __name__ == "__main__":
    verificar_repeticao() 