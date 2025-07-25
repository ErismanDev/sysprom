#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso

def investigar_regeneracao_quadro():
    print("=== INVESTIGAÇÃO: MILITARES SAINDO DO QUADRO DE ACESSO ===\n")
    
    # 1. Verificar quadros de acesso existentes
    quadros = QuadroAcesso.objects.all()
    print(f"Quadros de acesso encontrados: {quadros.count()}")
    
    for quadro in quadros:
        print(f"\n--- ANÁLISE DO QUADRO: {quadro.get_titulo_completo()} ---")
        print(f"Status atual: {quadro.get_status_display()}")
        print(f"Data de promoção: {quadro.data_promocao}")
        
        # Verificar itens atuais
        itens_atuais = quadro.itemquadroacesso_set.all().order_by('posicao')
        print(f"Militares atualmente no quadro: {itens_atuais.count()}")
        
        for item in itens_atuais:
            print(f"  - Posição {item.posicao}: {item.militar.nome_completo}")
        
        # 2. Simular regeneração sem salvar
        print(f"\n--- SIMULANDO REGENERAÇÃO ---")
        
        # Buscar militares aptos
        militares_aptos = quadro.militares_aptos()
        militares_inaptos = quadro.militares_inaptos_com_motivo()
        
        print(f"Militares aptos na regeneração: {len(militares_aptos)}")
        print(f"Militares inaptos na regeneração: {len(militares_inaptos)}")
        
        # Verificar quais militares sairiam
        militares_atuais_ids = set(item.militar.id for item in itens_atuais)
        militares_aptos_ids = set(militar.id for militar in militares_aptos)
        
        militares_saindo = militares_atuais_ids - militares_aptos_ids
        militares_entrando = militares_aptos_ids - militares_atuais_ids
        
        print(f"\nMilitares que SAIRIAM do quadro: {len(militares_saindo)}")
        for militar_id in militares_saindo:
            militar = Militar.objects.get(id=militar_id)
            print(f"  - {militar.nome_completo}")
            
            # Verificar por que ficou inapto
            apto, motivo = quadro.validar_requisitos_quadro_acesso(militar)
            print(f"    Motivo: {motivo}")
            
            # Verificar cada validação separadamente
            print(f"    * Interstício: {'OK' if quadro._validar_intersticio_minimo(militar, quadro.data_promocao) else 'FALHA'}")
            print(f"    * Inspeção de saúde: {'OK' if quadro._validar_inspecao_saude(militar) else 'FALHA'}")
            print(f"    * Cursos inerentes: {'OK' if quadro._validar_cursos_inerentes(militar) else 'FALHA'}")
        
        print(f"\nMilitares que ENTRARIAM no quadro: {len(militares_entrando)}")
        for militar_id in militares_entrando:
            militar = Militar.objects.get(id=militar_id)
            print(f"  - {militar.nome_completo}")
        
        # 3. Verificar se há mudanças nos dados dos militares
        print(f"\n--- VERIFICANDO MUDANÇAS NOS DADOS ---")
        
        for item in itens_atuais:
            militar = item.militar
            print(f"\nMilitar: {militar.nome_completo}")
            print(f"  - Data de promoção atual: {militar.data_promocao_atual}")
            print(f"  - Tempo no posto: {militar.tempo_posto_atual()} anos")
            print(f"  - Inspeção de saúde válida: {'Sim' if militar.apto_inspecao_saude else 'Não'}")
            print(f"  - Data validade inspeção: {militar.data_validade_inspecao_saude}")
            
            # Verificar se há mudanças recentes
            if militar.data_atualizacao:
                print(f"  - Última atualização: {militar.data_atualizacao}")
            
            # Verificar cursos específicos
            if militar.quadro == 'COMP':
                print(f"  - Possui CHO: {'Sim' if militar.curso_cho else 'Não'}")
            elif militar.quadro == 'COMB':
                print(f"  - Possui CFO: {'Sim' if militar.curso_formacao_oficial else 'Não'}")
        
        # 4. Verificar se a data de promoção do quadro mudou
        print(f"\n--- VERIFICANDO DATA DE PROMOÇÃO ---")
        print(f"Data de promoção do quadro: {quadro.data_promocao}")
        
        # Verificar se algum militar não completou interstício até essa data
        for item in itens_atuais:
            militar = item.militar
            apto_intersticio = quadro._validar_intersticio_minimo(militar, quadro.data_promocao)
            if not apto_intersticio:
                print(f"  - {militar.nome_completo}: Interstício não completado até {quadro.data_promocao}")

if __name__ == '__main__':
    investigar_regeneracao_quadro() 