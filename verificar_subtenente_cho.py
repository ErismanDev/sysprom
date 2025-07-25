#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso
from datetime import date

def verificar_subtenente_cho():
    print("=== VERIFICAÇÃO DE SUBTENENTES COM CHO ===\n")
    
    # Buscar todos os subtenentes
    subtenentes = Militar.objects.filter(
        posto_graduacao='ST',
        situacao='AT'
    )
    
    print(f"Total de subtenentes ativos: {subtenentes.count()}")
    
    # Verificar subtenentes com CHO
    subtenentes_com_cho = subtenentes.filter(curso_cho=True)
    print(f"Subtenentes com CHO: {subtenentes_com_cho.count()}")
    
    if subtenentes_com_cho.exists():
        print("\n--- SUBTENENTES COM CHO ---")
        for st in subtenentes_com_cho:
            print(f"\nMilitar: {st.nome_completo}")
            print(f"  - Matrícula: {st.matricula}")
            print(f"  - Quadro: {st.get_quadro_display()}")
            print(f"  - Data promoção atual: {st.data_promocao_atual}")
            print(f"  - Tempo no posto: {st.tempo_posto_atual()} anos")
            print(f"  - CHO: {'SIM' if st.curso_cho else 'NÃO'}")
            print(f"  - Curso superior: {'SIM' if st.curso_superior else 'NÃO'}")
            print(f"  - Pós-graduação: {'SIM' if st.pos_graduacao else 'NÃO'}")
            print(f"  - Inspeção de saúde: {'SIM' if st.apto_inspecao_saude else 'NÃO'}")
            print(f"  - Data inspeção: {st.data_inspecao_saude}")
            print(f"  - Validade inspeção: {st.data_validade_inspecao_saude}")
            print(f"  - Ficha de conceito: {'SIM' if st.fichaconceitooficiais_set.exists() or st.fichaconceitopracas_set.exists() else 'NÃO'}")
            
            # Verificar se está em algum quadro de acesso
            quadros = QuadroAcesso.objects.filter(status='ELABORADO')
            print(f"  - Quadros de acesso elaborados: {quadros.count()}")
            
            for quadro in quadros:
                item = quadro.itemquadroacesso_set.filter(militar=st).first()
                if item:
                    print(f"    * Quadro {quadro.get_tipo_display()} ({quadro.data_promocao}): Posição {item.posicao}")
                else:
                    print(f"    * Quadro {quadro.get_tipo_display()} ({quadro.data_promocao}): NÃO está no quadro")
                    
                    # Testar validação
                    apto, motivo = quadro.validar_requisitos_quadro_acesso(st)
                    print(f"      - Apto: {'SIM' if apto else 'NÃO'} - Motivo: {motivo}")
                    
                    # Testar cada validação separadamente
                    data_promocao = quadro.data_promocao
                    print(f"      - Interstício: {'OK' if quadro._validar_intersticio_minimo(st, data_promocao) else 'FALHA'}")
                    print(f"      - Inspeção de saúde: {'OK' if quadro._validar_inspecao_saude(st) else 'FALHA'}")
                    print(f"      - Cursos inerentes: {'OK' if quadro._validar_cursos_inerentes(st) else 'FALHA'}")
    
    # Verificar subtenentes sem CHO
    subtenentes_sem_cho = subtenentes.filter(curso_cho=False)
    print(f"\nSubtenentes sem CHO: {subtenentes_sem_cho.count()}")
    
    if subtenentes_sem_cho.exists():
        print("\n--- SUBTENENTES SEM CHO ---")
        for st in subtenentes_sem_cho:
            print(f"  - {st.nome_completo} (Matrícula: {st.matricula})")
    
    # Verificar quadro de acesso mais recente
    print(f"\n--- ANÁLISE DO QUADRO MAIS RECENTE ---")
    quadro_recente = QuadroAcesso.objects.filter(status='ELABORADO').order_by('-data_promocao').first()
    
    if quadro_recente:
        print(f"Quadro mais recente: {quadro_recente.get_titulo_completo()}")
        print(f"Data de promoção: {quadro_recente.data_promocao}")
        
        # Verificar militares no quadro
        itens_quadro = quadro_recente.itemquadroacesso_set.all()
        print(f"Total de militares no quadro: {itens_quadro.count()}")
        
        # Verificar subtenentes no quadro
        subtenentes_no_quadro = itens_quadro.filter(militar__posto_graduacao='ST')
        print(f"Subtenentes no quadro: {subtenentes_no_quadro.count()}")
        
        if subtenentes_no_quadro.exists():
            print("\nSubtenentes no quadro:")
            for item in subtenentes_no_quadro:
                st = item.militar
                print(f"  - {st.nome_completo} (Posição {item.posicao})")
                print(f"    * CHO: {'SIM' if st.curso_cho else 'NÃO'}")
                print(f"    * Quadro: {st.get_quadro_display()}")
        
        # Verificar militares aptos vs inaptos
        militares_aptos = quadro_recente.militares_aptos()
        militares_inaptos = quadro_recente.militares_inaptos_com_motivo()
        
        print(f"\nMilitares aptos: {len(militares_aptos)}")
        print(f"Militares inaptos: {len(militares_inaptos)}")
        
        # Verificar subtenentes aptos vs inaptos
        subtenentes_aptos = [m for m in militares_aptos if m.posto_graduacao == 'ST']
        subtenentes_inaptos = [item for item in militares_inaptos if item['militar'].posto_graduacao == 'ST']
        
        print(f"Subtenentes aptos: {len(subtenentes_aptos)}")
        print(f"Subtenentes inaptos: {len(subtenentes_inaptos)}")
        
        if subtenentes_inaptos:
            print("\nSubtenentes inaptos:")
            for item in subtenentes_inaptos:
                st = item['militar']
                print(f"  - {st.nome_completo}: {item['motivo']}")
                print(f"    * CHO: {'SIM' if st.curso_cho else 'NÃO'}")
                print(f"    * Quadro: {st.get_quadro_display()}")
    else:
        print("Nenhum quadro elaborado encontrado!")

if __name__ == "__main__":
    verificar_subtenente_cho() 