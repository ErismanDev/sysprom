#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar e corrigir problemas com cursos inerentes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from datetime import date

def analisar_cursos_inerentes():
    """Analisa todos os militares e identifica problemas com cursos inerentes"""
    
    print("=== ANÁLISE DE CURSOS INERENTES ===\n")
    
    # Definir cursos obrigatórios por quadro e posto (copiado do modelo)
    cursos_obrigatorios = {
        'COMB': {
            '2T': ['curso_formacao_oficial'],  # 2º Tenente precisa ter CFO
            '1T': ['curso_formacao_oficial'],  # 1º Tenente precisa ter CFO
            'CP': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],  # Capitão precisa CFO e CAO
            'MJ': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],  # Major precisa CFO e CAO
            'TC': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_csbm'],  # TC precisa CFO, CAO e CSBM
        },
        'SAUDE': {
            '2T': ['curso_formacao_oficial'],
            '1T': ['curso_formacao_oficial'],
            'CP': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
            'MJ': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
            'TC': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_csbm'],
        },
        'ENG': {
            'AS': ['curso_adaptacao_oficial'],  # Aspirante precisa CADOF
            '2T': ['curso_formacao_oficial'],
            '1T': ['curso_formacao_oficial'],
            'CP': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
            'MJ': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial'],
            'TC': ['curso_formacao_oficial', 'curso_aperfeicoamento_oficial', 'curso_csbm'],
        },
        'COMP': {
            'ST': ['curso_cho'],  # Subtenente precisa CHO para 2º Tenente
            '2T': ['curso_cho'],  # 2º Tenente precisa CHO para 1º Tenente
            '1T': ['curso_cho'],  # 1º Tenente precisa CHO para Capitão
            'CP': ['curso_cho', 'curso_superior'],  # Capitão precisa CHO e curso superior
            'MJ': ['curso_cho', 'curso_superior', 'pos_graduacao'],  # Major precisa CHO, curso superior e pós-graduação
            'TC': ['curso_cho', 'curso_superior', 'pos_graduacao', 'curso_csbm'],  # TC precisa todos
        },
    }
    
    # Obter próximo posto
    def obter_proximo_posto(posto_atual):
        proximas_promocoes = {
            'AS': '2T', '2T': '1T', '1T': 'CP', 'CP': 'MJ', 'MJ': 'TC', 'TC': 'CB',
            'ST': '2T', 'SD': 'CB', 'CB': '3S', '3S': '2S', '2S': '1S', '1S': 'ST'
        }
        return proximas_promocoes.get(posto_atual)
    
    # Função para validar cursos inerentes
    def validar_cursos_inerentes(militar):
        proximo_posto = obter_proximo_posto(militar.posto_graduacao)
        
        # Verificar se o posto atual tem cursos obrigatórios definidos
        cursos_necessarios = cursos_obrigatorios.get(militar.quadro, {}).get(militar.posto_graduacao, [])
        
        if not cursos_necessarios:
            return True, "Não há cursos obrigatórios definidos para este posto/quadro"
        
        # Verificar se possui todos os cursos necessários
        cursos_faltando = []
        for curso in cursos_necessarios:
            if not getattr(militar, curso, False):
                cursos_faltando.append(curso)
        
        if cursos_faltando:
            return False, f"Faltam cursos: {', '.join(cursos_faltando)}"
        
        return True, "Todos os cursos necessários possuídos"
    
    # Analisar todos os militares ativos
    militares = Militar.objects.filter(situacao='AT')
    
    problemas_encontrados = []
    militares_ok = []
    
    for militar in militares:
        apto, motivo = validar_cursos_inerentes(militar)
        
        if apto:
            militares_ok.append(militar)
        else:
            problemas_encontrados.append({
                'militar': militar,
                'motivo': motivo,
                'cursos_necessarios': cursos_obrigatorios.get(militar.quadro, {}).get(militar.posto_graduacao, [])
            })
    
    # Exibir resultados
    print(f"Total de militares ativos: {militares.count()}")
    print(f"Militares com cursos inerentes OK: {len(militares_ok)}")
    print(f"Militares com problemas: {len(problemas_encontrados)}")
    print()
    
    if problemas_encontrados:
        print("=== PROBLEMAS ENCONTRADOS ===")
        for problema in problemas_encontrados:
            militar = problema['militar']
            print(f"\nMilitar: {militar.nome_completo} ({militar.matricula})")
            print(f"Quadro: {militar.get_quadro_display()}")
            print(f"Posto: {militar.get_posto_graduacao_display()}")
            print(f"Problema: {problema['motivo']}")
            print(f"Cursos necessários: {problema['cursos_necessarios']}")
            
            # Mostrar cursos atuais
            cursos_atuais = []
            for curso in problema['cursos_necessarios']:
                valor = getattr(militar, curso, False)
                cursos_atuais.append(f"{curso}: {'✓' if valor else '✗'}")
            print(f"Cursos atuais: {', '.join(cursos_atuais)}")
    
    return problemas_encontrados, militares_ok

def corrigir_cursos_inerentes():
    """Corrige problemas identificados com cursos inerentes"""
    
    print("\n=== CORREÇÃO DE CURSOS INERENTES ===\n")
    
    problemas, militares_ok = analisar_cursos_inerentes()
    
    if not problemas:
        print("Nenhum problema encontrado para corrigir!")
        return
    
    print(f"\nEncontrados {len(problemas)} problemas para corrigir.")
    
    # Aqui você pode implementar a lógica de correção
    # Por exemplo, marcar automaticamente cursos baseado em outros critérios
    
    for problema in problemas:
        militar = problema['militar']
        print(f"\nAnalisando correção para: {militar.nome_completo}")
        
        # Lógica de correção baseada no quadro e posto
        if militar.quadro == 'COMB':
            if militar.posto_graduacao in ['2T', '1T', 'CP', 'MJ', 'TC']:
                # Para quadros de oficiais, se tem CFO, provavelmente tem os outros cursos básicos
                if militar.curso_formacao_oficial:
                    if not militar.curso_aperfeicoamento_oficial and militar.posto_graduacao in ['CP', 'MJ', 'TC']:
                        print(f"  → Marcando curso_aperfeicoamento_oficial como True")
                        militar.curso_aperfeicoamento_oficial = True
                    
                    if not militar.curso_csbm and militar.posto_graduacao == 'TC':
                        print(f"  → Marcando curso_csbm como True")
                        militar.curso_csbm = True
        
        elif militar.quadro == 'COMP':
            if militar.posto_graduacao in ['ST', '2T', '1T', 'CP', 'MJ', 'TC']:
                # Para quadro complementar, se tem curso superior, provavelmente tem CHO
                if militar.curso_superior and not militar.curso_cho:
                    print(f"  → Marcando curso_cho como True")
                    militar.curso_cho = True
                
                # Se tem pós-graduação, provavelmente tem curso superior
                if militar.pos_graduacao and not militar.curso_superior:
                    print(f"  → Marcando curso_superior como True")
                    militar.curso_superior = True
        
        # Salvar as correções
        militar.save()
    
    print("\n=== VERIFICAÇÃO PÓS-CORREÇÃO ===")
    analisar_cursos_inerentes()

if __name__ == "__main__":
    print("Iniciando análise de cursos inerentes...")
    
    # Primeiro, apenas analisar
    problemas, militares_ok = analisar_cursos_inerentes()
    
    # Perguntar se quer corrigir
    if problemas:
        resposta = input("\nDeseja aplicar correções automáticas? (s/n): ")
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            corrigir_cursos_inerentes()
        else:
            print("Correções não aplicadas.")
    else:
        print("Nenhum problema encontrado!") 