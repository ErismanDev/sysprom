#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso

def verificar_jose_erisman():
    print("=== VERIFICAÇÃO ESPECÍFICA: JOSE ERISMAN DE SOUSA ===\n")
    
    # Encontrar o militar
    militar = Militar.objects.filter(nome_completo__icontains='JOSE ERISMAN').first()
    if not militar:
        print("Militar JOSE ERISMAN DE SOUSA não encontrado!")
        return
    
    print(f"Militar encontrado: {militar.nome_completo}")
    print(f"ID: {militar.id}")
    print(f"Matrícula: {militar.matricula}")
    print(f"Posto: {militar.get_posto_graduacao_display()}")
    print(f"Quadro: {militar.get_quadro_display()}")
    print(f"Situação: {militar.get_situacao_display()}")
    print(f"Data de promoção atual: {militar.data_promocao_atual}")
    print(f"Tempo no posto: {militar.tempo_posto_atual()} anos")
    
    # Verificar se está no quadro de acesso
    quadro = QuadroAcesso.objects.first()
    if quadro:
        print(f"\n--- VERIFICAÇÃO NO QUADRO DE ACESSO ---")
        print(f"Quadro: {quadro.get_titulo_completo()}")
        print(f"Posto do quadro: {quadro.posto}")
        print(f"Quadro do quadro: {quadro.quadro}")
        
        # Verificar se está nos itens do quadro
        item_quadro = quadro.itemquadroacesso_set.filter(militar=militar).first()
        if item_quadro:
            print(f"Está no quadro na posição: {item_quadro.posicao}")
        else:
            print("NÃO está nos itens do quadro!")
        
        # Verificar se está na lista de militares aptos
        militares_aptos = quadro.militares_aptos()
        militares_aptos_ids = [m.id for m in militares_aptos]
        
        if militar.id in militares_aptos_ids:
            print("Está na lista de militares aptos")
        else:
            print("NÃO está na lista de militares aptos!")
            
            # Verificar por que não está apto
            print(f"\n--- ANÁLISE DE POR QUE NÃO ESTÁ APTO ---")
            
            # Verificar se atende aos filtros básicos
            if militar.quadro != quadro.quadro:
                print(f"  - Quadro diferente: {militar.quadro} vs {quadro.quadro}")
            if militar.posto_graduacao != quadro.posto:
                print(f"  - Posto diferente: {militar.posto_graduacao} vs {quadro.posto}")
            if militar.situacao != 'AT':
                print(f"  - Situação não ativa: {militar.situacao}")
            
            # Validar requisitos
            apto, motivo = quadro.validar_requisitos_quadro_acesso(militar)
            print(f"  - Validação de requisitos: {'Apto' if apto else 'Inapto'} - {motivo}")
            
            # Verificar cada validação separadamente
            print(f"  - Interstício: {'OK' if quadro._validar_intersticio_minimo(militar, quadro.data_promocao) else 'FALHA'}")
            print(f"  - Inspeção de saúde: {'OK' if quadro._validar_inspecao_saude(militar) else 'FALHA'}")
            print(f"  - Cursos inerentes: {'OK' if quadro._validar_cursos_inerentes(militar) else 'FALHA'}")

if __name__ == '__main__':
    verificar_jose_erisman() 