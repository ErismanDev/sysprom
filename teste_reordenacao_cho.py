#!/usr/bin/env python
"""
Script para testar especificamente a reordenação quando Subtenente ganha CHO
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_reordenacao_cho():
    print("=== TESTE ESPECÍFICO DE REORDENAÇÃO CHO ===\n")
    
    # 1. Verificar estado atual
    subtenentes = Militar.objects.filter(posto_graduacao='ST', situacao='AT')
    print(f"Total de Subtenentes: {subtenentes.count()}")
    
    # 2. Verificar Subtenentes por quadro
    for quadro in ['COMP', 'PRACAS']:
        print(f"\n--- QUADRO {quadro} ---")
        st_quadro = subtenentes.filter(quadro=quadro)
        st_com_cho = st_quadro.filter(curso_cho=True).order_by('numeracao_antiguidade', 'nome_completo')
        st_sem_cho = st_quadro.filter(curso_cho=False).order_by('numeracao_antiguidade', 'nome_completo')
        
        print(f"Total no quadro {quadro}: {st_quadro.count()}")
        print(f"Com CHO: {st_com_cho.count()}")
        print(f"Sem CHO: {st_sem_cho.count()}")
        
        if st_com_cho.exists():
            print("\nCom CHO:")
            for st in st_com_cho:
                print(f"  {st.numeracao_antiguidade}. {st.nome_completo} (Promoção: {st.data_promocao_atual})")
        
        if st_sem_cho.exists():
            print("\nSem CHO:")
            for st in st_sem_cho:
                print(f"  {st.numeracao_antiguidade}. {st.nome_completo} (Promoção: {st.data_promocao_atual})")
    
    # 3. Testar reordenação manual
    print(f"\n--- TESTE DE REORDENAÇÃO MANUAL ---")
    
    # Encontrar um Subtenente sem CHO para testar
    st_sem_cho = subtenentes.filter(curso_cho=False).first()
    if st_sem_cho:
        print(f"Subtenente para teste: {st_sem_cho.nome_completo}")
        print(f"Quadro: {st_sem_cho.quadro}")
        print(f"CHO atual: {st_sem_cho.curso_cho}")
        print(f"Antiguidade atual: {st_sem_cho.numeracao_antiguidade}")
        
        # Salvar estado anterior
        cho_anterior = st_sem_cho.curso_cho
        antiguidade_anterior = st_sem_cho.numeracao_antiguidade
        
        # Simular ganho de CHO
        print(f"\nSimulando ganho de CHO...")
        st_sem_cho.curso_cho = True
        st_sem_cho.save()
        
        print(f"CHO após alteração: {st_sem_cho.curso_cho}")
        print(f"Antiguidade após alteração: {st_sem_cho.numeracao_antiguidade}")
        
        # Verificar reordenação no quadro
        st_quadro = Militar.objects.filter(posto_graduacao='ST', quadro=st_sem_cho.quadro, situacao='AT')
        st_com_cho = st_quadro.filter(curso_cho=True).order_by('numeracao_antiguidade', 'nome_completo')
        st_sem_cho_novos = st_quadro.filter(curso_cho=False).order_by('numeracao_antiguidade', 'nome_completo')
        
        print(f"\nReordenação no quadro {st_sem_cho.quadro}:")
        print("Com CHO:")
        for st in st_com_cho:
            print(f"  {st.numeracao_antiguidade}. {st.nome_completo}")
        
        print("Sem CHO:")
        for st in st_sem_cho_novos:
            print(f"  {st.numeracao_antiguidade}. {st.nome_completo}")
        
        # Reverter para não afetar os dados
        st_sem_cho.curso_cho = cho_anterior
        st_sem_cho.save()
        print(f"\nRevertido CHO para {st_sem_cho.curso_cho}")
    else:
        print("Não há Subtenentes sem CHO para testar.")
    
    # 4. Verificar se o método save está sendo chamado
    print(f"\n--- VERIFICANDO MÉTODO SAVE ---")
    print("Verificando se o método save do modelo Militar está sendo executado...")
    
    # Testar com um Subtenente existente
    st_teste = subtenentes.first()
    if st_teste:
        print(f"Testando com: {st_teste.nome_completo}")
        print(f"CHO atual: {st_teste.curso_cho}")
        
        # Alterar CHO para forçar execução do método save
        cho_original = st_teste.curso_cho
        st_teste.curso_cho = not cho_original
        st_teste.save()
        
        print(f"CHO após save: {st_teste.curso_cho}")
        
        # Reverter
        st_teste.curso_cho = cho_original
        st_teste.save()
        print(f"CHO revertido: {st_teste.curso_cho}")
    
    print(f"\n=== TESTE CONCLUÍDO ===")

if __name__ == '__main__':
    testar_reordenacao_cho() 