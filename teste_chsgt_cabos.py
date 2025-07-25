#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a funcionalidade da nota do CHSGT para cabos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from decimal import Decimal

def testar_ordenacao_chsgt_cabos():
    """Testa a ordenação de cabos com CHSGT baseada na nota"""
    
    print("=== TESTE DE ORDENAÇÃO DE CABOS COM CHSGT ===\n")
    
    # Buscar todos os cabos com CHSGT
    cabos_com_chsgt = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='CAB',
        curso_chsgt=True
    ).order_by('nome_completo')
    
    print(f"Encontrados {cabos_com_chsgt.count()} cabos com CHSGT:")
    
    for cabo in cabos_com_chsgt:
        nota = cabo.nota_chsgt or "Não informada"
        antiguidade = cabo.numeracao_antiguidade or "Não informada"
        print(f"- {cabo.nome_completo}: Nota CHSGT = {nota}, Antiguidade = {antiguidade}")
    
    print("\n" + "="*50)
    
    # Simular ordenação como no quadro de acesso
    cabos_ordenados = []
    for cabo in cabos_com_chsgt:
        nota_chsgt = cabo.nota_chsgt or 0
        numeracao = cabo.numeracao_antiguidade or 999999
        
        cabos_ordenados.append({
            'militar': cabo,
            'nota_chsgt': nota_chsgt,
            'numeracao_antiguidade': numeracao
        })
    
    # Ordenar por nota do CHSGT (maior primeiro) e depois por antiguidade
    cabos_ordenados.sort(key=lambda x: (-x['nota_chsgt'], x['numeracao_antiguidade']))
    
    print("ORDENAÇÃO APLICADA (maior nota CHSGT primeiro, depois menor antiguidade):")
    for i, item in enumerate(cabos_ordenados, 1):
        cabo = item['militar']
        nota = item['nota_chsgt']
        antiguidade = item['numeracao_antiguidade']
        print(f"{i}º - {cabo.nome_completo}: Nota CHSGT = {nota}, Antiguidade = {antiguidade}")
    
    print("\n" + "="*50)
    
    # Verificar quadros de acesso existentes
    quadros_cabos = QuadroAcesso.objects.filter(
        categoria='PRACAS',
        tipo='ANTIGUIDADE'
    ).order_by('-data_promocao')
    
    print(f"Quadros de acesso para praças (antiguidade) encontrados: {quadros_cabos.count()}")
    
    for quadro in quadros_cabos[:3]:  # Mostrar apenas os 3 mais recentes
        print(f"\nQuadro: {quadro.numero} ({quadro.data_promocao})")
        print(f"Status: {quadro.get_status_display()}")
        
        # Buscar itens do quadro que são cabos
        itens_cabos = quadro.itemquadroacesso_set.filter(
            militar__posto_graduacao='CAB'
        ).order_by('posicao')
        
        print(f"Cabos no quadro: {itens_cabos.count()}")
        
        for item in itens_cabos:
            cabo = item.militar
            nota = cabo.nota_chsgt or "Não informada"
            antiguidade = cabo.numeracao_antiguidade or "Não informada"
            tem_chsgt = "Sim" if cabo.curso_chsgt else "Não"
            
            print(f"  {item.posicao}ª posição - {cabo.nome_completo}")
            print(f"    CHSGT: {tem_chsgt}, Nota: {nota}, Antiguidade: {antiguidade}")

if __name__ == "__main__":
    testar_ordenacao_chsgt_cabos() 