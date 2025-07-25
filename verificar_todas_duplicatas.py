#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.db.models import Count

def verificar_todas_duplicatas():
    print("=== VERIFICANDO TODAS AS DUPLICATAS NO SISTEMA ===")
    
    # Verificar duplicatas por posto/quadro
    duplicatas = Militar.objects.filter(
        situacao='AT'
    ).values('posto_graduacao', 'quadro', 'numeracao_antiguidade').annotate(
        count=Count('id')
    ).filter(count__gt=1).order_by('posto_graduacao', 'quadro', 'numeracao_antiguidade')
    
    if duplicatas:
        print(f"Encontradas {len(duplicatas)} combinações com duplicatas:")
        for dup in duplicatas:
            print(f"\n{dup['posto_graduacao']} - {dup['quadro']}: {dup['numeracao_antiguidade']} (aparece {dup['count']} vezes)")
            
            # Mostrar os militares com essa numeração
            militares = Militar.objects.filter(
                posto_graduacao=dup['posto_graduacao'],
                quadro=dup['quadro'],
                numeracao_antiguidade=dup['numeracao_antiguidade'],
                situacao='AT'
            ).order_by('id')
            
            for militar in militares:
                print(f"  - ID {militar.id}: {militar.nome_completo}")
    else:
        print("✓ Não foram encontradas duplicatas!")
    
    # Verificar especificamente ST-PRACAS com e sem CHO
    print("\n" + "="*60)
    print("VERIFICANDO SUBTENENTES PRACAS (COM E SEM CHO)")
    print("="*60)
    
    # ST-PRACAS COM CHO
    st_com_cho = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT',
        curso_cho=True
    ).order_by('numeracao_antiguidade')
    
    print(f"\nST-PRACAS COM CHO: {st_com_cho.count()} militares")
    for militar in st_com_cho:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # ST-PRACAS SEM CHO
    st_sem_cho = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT',
        curso_cho=False
    ).order_by('numeracao_antiguidade')
    
    print(f"\nST-PRACAS SEM CHO: {st_sem_cho.count()} militares")
    for militar in st_sem_cho:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Verificar duplicatas em cada grupo ST
    numeracoes_com_cho = [m.numeracao_antiguidade for m in st_com_cho]
    numeracoes_sem_cho = [m.numeracao_antiguidade for m in st_sem_cho]
    
    duplicatas_com_cho = [n for n in numeracoes_com_cho if numeracoes_com_cho.count(n) > 1]
    duplicatas_sem_cho = [n for n in numeracoes_sem_cho if numeracoes_sem_cho.count(n) > 1]
    
    if duplicatas_com_cho:
        print(f"\nERRO: Duplicatas em ST-PRACAS COM CHO: {duplicatas_com_cho}")
    else:
        print(f"\n✓ ST-PRACAS COM CHO: Sem duplicatas")
        
    if duplicatas_sem_cho:
        print(f"ERRO: Duplicatas em ST-PRACAS SEM CHO: {duplicatas_sem_cho}")
    else:
        print(f"✓ ST-PRACAS SEM CHO: Sem duplicatas")

if __name__ == '__main__':
    verificar_todas_duplicatas() 