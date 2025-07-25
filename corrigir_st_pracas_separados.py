#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def corrigir_st_pracas_separados():
    print("=== CORRIGINDO SUBTENENTES PRACAS (SEPARANDO COM/SEM CHO) ===")
    
    # Reordenar ST-PRACAS COM CHO
    st_com_cho = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT',
        curso_cho=True
    ).order_by('numeracao_antiguidade', 'id')
    
    print(f"\nReordenando ST-PRACAS COM CHO: {st_com_cho.count()} militares")
    for i, militar in enumerate(st_com_cho, 1):
        if militar.numeracao_antiguidade != i:
            print(f"  Corrigindo {militar.nome_completo}: {militar.numeracao_antiguidade}º -> {i}º")
            militar.numeracao_antiguidade = i
            militar.save(update_fields=['numeracao_antiguidade'])
        else:
            print(f"  {militar.nome_completo}: {i}º (já correto)")
    
    # Reordenar ST-PRACAS SEM CHO
    st_sem_cho = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT',
        curso_cho=False
    ).order_by('numeracao_antiguidade', 'id')
    
    print(f"\nReordenando ST-PRACAS SEM CHO: {st_sem_cho.count()} militares")
    for i, militar in enumerate(st_sem_cho, 1):
        if militar.numeracao_antiguidade != i:
            print(f"  Corrigindo {militar.nome_completo}: {militar.numeracao_antiguidade}º -> {i}º")
            militar.numeracao_antiguidade = i
            militar.save(update_fields=['numeracao_antiguidade'])
        else:
            print(f"  {militar.nome_completo}: {i}º (já correto)")
    
    print("\n✓ Reordenação concluída!")
    
    # Verificar resultado
    print("\n" + "="*60)
    print("VERIFICANDO RESULTADO")
    print("="*60)
    
    # ST-PRACAS COM CHO
    st_com_cho_final = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT',
        curso_cho=True
    ).order_by('numeracao_antiguidade')
    
    print(f"\nST-PRACAS COM CHO: {st_com_cho_final.count()} militares")
    for militar in st_com_cho_final:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # ST-PRACAS SEM CHO
    st_sem_cho_final = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT',
        curso_cho=False
    ).order_by('numeracao_antiguidade')
    
    print(f"\nST-PRACAS SEM CHO: {st_sem_cho_final.count()} militares")
    for militar in st_sem_cho_final:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Verificar duplicatas
    numeracoes_com_cho = [m.numeracao_antiguidade for m in st_com_cho_final]
    numeracoes_sem_cho = [m.numeracao_antiguidade for m in st_sem_cho_final]
    
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
    corrigir_st_pracas_separados() 