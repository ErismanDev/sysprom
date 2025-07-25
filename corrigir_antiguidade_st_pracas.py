#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def reordenar_st_pracas():
    print('--- Reordenando Subtenentes PRACAS (com e sem CHO separados) ---')
    for tem_cho in [True, False]:
        grupo = 'COM CHO' if tem_cho else 'SEM CHO'
        militares = Militar.objects.filter(
            posto_graduacao='ST',
            quadro='PRACAS',
            situacao='AT',
            curso_cho=tem_cho
        ).order_by('numeracao_antiguidade', 'id')
        print(f"{grupo}: {militares.count()} encontrados")
        for i, militar in enumerate(militares, 1):
            if militar.numeracao_antiguidade != i:
                print(f"  Corrigindo {militar.nome_completo} (ID {militar.id}): {militar.numeracao_antiguidade} -> {i}")
                militar.numeracao_antiguidade = i
                militar.save(update_fields=['numeracao_antiguidade'])
    print('--- FIM ---')

if __name__ == '__main__':
    reordenar_st_pracas() 