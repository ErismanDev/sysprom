#!/usr/bin/env python
import os
import sys
import django
from django.db.models import Q

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoOficiais, FichaConceitoPracas

def corrigir_inconsistencias_fichas():
    """
    Corrige inconsistências de fichas de praças que têm fichas de oficiais
    """
    print("=== CORREÇÃO DE INCONSISTÊNCIAS DE FICHAS ===\n")
    
    # 1. Identificar praças com ficha de oficiais
    pracas_com_ficha_oficiais = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST'],
        fichaconceitooficiais__isnull=False
    )
    
    print(f"1. PRACAS COM FICHA DE OFICIAIS ENCONTRADAS: {pracas_com_ficha_oficiais.count()}")
    
    if pracas_com_ficha_oficiais.exists():
        print("\n   PRACAS COM FICHA DE OFICIAIS:")
        for militar in pracas_com_ficha_oficiais:
            print(f"     - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - Matrícula: {militar.matricula}")
        
        # Perguntar se deve corrigir
        print(f"\n2. OPÇÕES DE CORREÇÃO:")
        print("   a) Remover fichas de oficiais das praças")
        print("   b) Converter praças para oficiais (se foram promovidas)")
        print("   c) Não fazer nada")
        
        opcao = input("\nEscolha uma opção (a/b/c): ").lower()
        
        if opcao == 'a':
            # Remover fichas de oficiais das praças
            print("\n3. REMOVENDO FICHAS DE OFICIAIS DAS PRACAS...")
            fichas_removidas = 0
            
            for militar in pracas_com_ficha_oficiais:
                fichas_oficiais = militar.fichaconceitooficiais_set.all()
                for ficha in fichas_oficiais:
                    print(f"   - Removendo ficha de oficiais de {militar.nome_completo}")
                    ficha.delete()
                    fichas_removidas += 1
            
            print(f"\n✅ {fichas_removidas} fichas de oficiais removidas das praças!")
            
        elif opcao == 'b':
            # Converter praças para oficiais
            print("\n3. CONVERTENDO PRACAS PARA OFICIAIS...")
            print("   ATENÇÃO: Esta opção mudará o posto das praças para 2T (2º Tenente)")
            
            confirmacao = input("   Confirma a conversão? (s/n): ").lower()
            
            if confirmacao == 's':
                for militar in pracas_com_ficha_oficiais:
                    print(f"   - Convertendo {militar.nome_completo} de {militar.get_posto_graduacao_display()} para 2º Tenente")
                    militar.posto_graduacao = '2T'
                    militar.quadro = 'COMP'  # Complementar
                    militar.save()
                
                print(f"\n✅ {pracas_com_ficha_oficiais.count()} praças convertidas para oficiais!")
            else:
                print("\n❌ Conversão cancelada!")
        
        else:
            print("\n❌ Nenhuma correção realizada!")
    
    else:
        print("\n✅ Não há inconsistências encontradas!")
    
    # 4. Verificar resultado final
    print(f"\n4. VERIFICAÇÃO FINAL:")
    pracas_final = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    
    pracas_sem_ficha_final = pracas_final.exclude(
        Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
    )
    
    print(f"   - Total de praças: {pracas_final.count()}")
    print(f"   - Praças sem ficha: {pracas_sem_ficha_final.count()}")
    
    if pracas_sem_ficha_final.exists():
        print("\n   Pracas sem ficha:")
        for militar in pracas_sem_ficha_final:
            print(f"     - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - Matrícula: {militar.matricula}")

if __name__ == '__main__':
    corrigir_inconsistencias_fichas() 