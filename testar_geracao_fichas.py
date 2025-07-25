#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoOficiais, FichaConceitoPracas

def testar_geracao_fichas():
    """
    Testa a geração de fichas de conceito para identificar problemas
    """
    print("=== TESTE DE GERAÇÃO DE FICHAS DE CONCEITO ===\n")
    
    # 1. Verificar militares ativos
    militares_ativos = Militar.objects.filter(situacao='AT')
    print(f"1. MILITARES ATIVOS:")
    print("-" * 40)
    print(f"Total: {militares_ativos.count()}")
    
    # 2. Verificar militares sem fichas
    militares_sem_ficha = []
    for militar in militares_ativos:
        try:
            militar.fichaconceitooficiais
            tem_ficha = True
        except:
            try:
                militar.fichaconceitopracas
                tem_ficha = True
            except:
                tem_ficha = False
        
        if not tem_ficha:
            militares_sem_ficha.append(militar)
    
    print(f"\n2. MILITARES SEM FICHA:")
    print("-" * 40)
    print(f"Total: {len(militares_sem_ficha)}")
    
    if militares_sem_ficha:
        print("\nDetalhes dos militares sem ficha:")
        for militar in militares_sem_ficha:
            tempo_posto = militar.tempo_posto_atual()
            print(f"  - {militar.nome_completo} ({militar.posto_graduacao})")
            print(f"    Data de promoção: {militar.data_promocao_atual}")
            print(f"    Tempo no posto: {tempo_posto} anos")
            print()
        
        # 3. Tentar criar fichas
        print("3. TENTANDO CRIAR FICHAS...")
        print("-" * 40)
        
        fichas_criadas = 0
        for militar in militares_sem_ficha:
            try:
                if militar.posto_graduacao in ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']:
                    # Criar ficha de oficiais
                    ficha = FichaConceitoOficiais.objects.create(
                        militar=militar,
                    )
                    print(f"  ✅ Ficha de oficiais criada: {militar.nome_completo}")
                else:
                    # Criar ficha de praças
                    ficha = FichaConceitoPracas.objects.create(
                        militar=militar,
                    )
                    print(f"  ✅ Ficha de praças criada: {militar.nome_completo}")
                fichas_criadas += 1
            except Exception as e:
                print(f"  ❌ Erro ao criar ficha para {militar.nome_completo}: {e}")
        
        print(f"\n✅ {fichas_criadas} fichas criadas com sucesso!")
    else:
        print("✅ Todos os militares já possuem fichas de conceito!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    testar_geracao_fichas() 