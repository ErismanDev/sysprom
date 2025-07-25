#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso

def verificar_subtenentes():
    print("=== VERIFICAÇÃO DE SUBTENENTES NO SISTEMA ===\n")
    
    # 1. Verificar se há subtenentes cadastrados
    subtenentes = Militar.objects.filter(posto_graduacao='ST')
    print(f"Total de subtenentes cadastrados: {subtenentes.count()}")
    
    if subtenentes.exists():
        print("\nLista de subtenentes:")
        for st in subtenentes:
            print(f"- {st.nome_completo} (Quadro: {st.get_quadro_display()}, Situação: {st.get_situacao_display()})")
            
        # 2. Verificar subtenentes ativos
        subtenentes_ativos = subtenentes.filter(situacao='AT')
        print(f"\nSubtenentes ativos: {subtenentes_ativos.count()}")
        
        for st in subtenentes_ativos:
            print(f"- {st.nome_completo} (Quadro: {st.get_quadro_display()})")
            
        # 3. Verificar se há quadros de acesso para subtenentes
        quadros_acesso_st = QuadroAcesso.objects.filter(posto='ST')
        print(f"\nQuadros de acesso para subtenentes: {quadros_acesso_st.count()}")
        
        for qa in quadros_acesso_st:
            print(f"- {qa.get_tipo_display()} - {qa.get_quadro_display()} - {qa.data_promocao} - {qa.get_status_display()}")
            
        # 4. Verificar requisitos dos subtenentes ativos
        print("\n=== ANÁLISE DE REQUISITOS DOS SUBTENENTES ATIVOS ===")
        for st in subtenentes_ativos:
            print(f"\n{st.nome_completo} ({st.get_quadro_display()}):")
            print(f"  - Próxima promoção: {st.proxima_promocao()}")
            print(f"  - Apto para promoção por antiguidade: {'Sim' if st.apto_promocao_antiguidade() else 'Não'}")
            print(f"  - Tempo no posto atual: {st.tempo_posto_atual()} anos")
            print(f"  - Interstício mínimo: {st.intersticio_formatado()}")
            print(f"  - Tempo restante para interstício: {st.tempo_restante_intersticio()} meses")
            print(f"  - Inspeção de saúde válida: {'Sim' if st.apto_inspecao_saude else 'Não'}")
            
            # Verificar cursos específicos por quadro
            if st.quadro == 'COMP':
                print(f"  - Possui CHO: {'Sim' if st.curso_cho else 'Não'}")
            elif st.quadro == 'COMB':
                print(f"  - Próxima promoção seria para: Aspirante")
            else:
                print(f"  - Próxima promoção seria para: 2º Tenente")
                
    else:
        print("Nenhum subtenente encontrado no sistema!")
        
        # Verificar se há militares em outros postos
        total_militares = Militar.objects.count()
        print(f"\nTotal de militares no sistema: {total_militares}")
        
        if total_militares > 0:
            print("\nDistribuição por posto:")
            postos = Militar.objects.values('posto_graduacao').annotate(
                count=models.Count('id')
            ).order_by('posto_graduacao')
            
            for posto in postos:
                print(f"- {posto['posto_graduacao']}: {posto['count']}")

if __name__ == '__main__':
    verificar_subtenentes() 