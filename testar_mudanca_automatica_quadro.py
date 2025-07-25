#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_mudanca_automatica_quadro():
    """
    Testa a mudança automática de quadro quando militar é promovido de ST para 2T
    """
    print("=== TESTE DE MUDANÇA AUTOMÁTICA DE QUADRO ===\n")
    
    # 1. Identificar militares com inconsistência (PRACAS + 2T)
    militares_inconsistentes = Militar.objects.filter(
        quadro='PRACAS',
        posto_graduacao='2T'
    )
    
    print(f"1. MILITARES COM INCONSISTÊNCIA ENCONTRADOS:")
    print("-" * 50)
    print(f"Total: {militares_inconsistentes.count()}")
    
    if militares_inconsistentes.exists():
        for militar in militares_inconsistentes:
            print(f"  - {militar.nome_completo} (ID: {militar.id})")
            print(f"    * Posto: {militar.get_posto_graduacao_display()}")
            print(f"    * Quadro: {militar.get_quadro_display()}")
            print(f"    * Matrícula: {militar.matricula}")
            print()
    
    # 2. Simular promoção de ST para 2T
    print(f"2. SIMULANDO PROMOÇÃO DE ST PARA 2T:")
    print("-" * 50)
    
    # Buscar um militar ST no quadro PRACAS para testar
    militar_st = Militar.objects.filter(
        quadro='PRACAS',
        posto_graduacao='ST',
        situacao='AT'
    ).first()
    
    if militar_st:
        print(f"Testando com militar: {militar_st.nome_completo}")
        print(f"  * Posto atual: {militar_st.get_posto_graduacao_display()}")
        print(f"  * Quadro atual: {militar_st.get_quadro_display()}")
        
        # Simular promoção
        posto_anterior = militar_st.posto_graduacao
        militar_st.posto_graduacao = '2T'
        militar_st.save()
        
        print(f"  * Posto após promoção: {militar_st.get_posto_graduacao_display()}")
        print(f"  * Quadro após promoção: {militar_st.get_quadro_display()}")
        
        # Verificar se a mudança foi aplicada
        if militar_st.quadro == 'COMP':
            print("  ✅ Mudança automática de quadro aplicada com sucesso!")
        else:
            print("  ❌ Mudança automática de quadro NÃO foi aplicada!")
        
        # Reverter para teste
        militar_st.posto_graduacao = posto_anterior
        militar_st.quadro = 'PRACAS'
        militar_st.save()
        print(f"  * Revertido para teste")
        
    else:
        print("Nenhum militar ST encontrado no quadro PRACAS para teste")
    
    # 3. Corrigir militares já inconsistentes
    print(f"\n3. CORRIGINDO MILITARES JÁ INCONSISTENTES:")
    print("-" * 50)
    
    if militares_inconsistentes.exists():
        corrigidos = 0
        for militar in militares_inconsistentes:
            print(f"Corrigindo {militar.nome_completo}:")
            print(f"  * Posto: {militar.get_posto_graduacao_display()}")
            print(f"  * Quadro anterior: {militar.get_quadro_display()}")
            
            # Aplicar correção
            militar.quadro = 'COMP'
            militar.save()
            
            print(f"  * Quadro novo: {militar.get_quadro_display()}")
            print(f"  ✅ Corrigido!")
            print()
            corrigidos += 1
        
        print(f"Total de militares corrigidos: {corrigidos}")
    else:
        print("Nenhum militar inconsistente para corrigir")
    
    # 4. Verificação final
    print(f"\n4. VERIFICAÇÃO FINAL:")
    print("-" * 50)
    
    militares_inconsistentes_apos = Militar.objects.filter(
        quadro='PRACAS',
        posto_graduacao='2T'
    )
    
    if militares_inconsistentes_apos.exists():
        print(f"❌ Ainda existem {militares_inconsistentes_apos.count()} militares inconsistentes")
        for militar in militares_inconsistentes_apos:
            print(f"  - {militar.nome_completo}")
    else:
        print("✅ Todos os militares estão com quadro correto!")
    
    # 5. Estatísticas
    print(f"\n5. ESTATÍSTICAS:")
    print("-" * 50)
    
    print("Militares por quadro:")
    for quadro in ['PRACAS', 'COMB', 'SAUDE', 'ENG', 'COMP']:
        count = Militar.objects.filter(quadro=quadro).count()
        print(f"  {quadro}: {count}")
    
    print(f"\nMilitares por posto:")
    for posto in ['ST', '2T']:
        count = Militar.objects.filter(posto_graduacao=posto).count()
        print(f"  {posto}: {count}")

if __name__ == "__main__":
    testar_mudanca_automatica_quadro() 