#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se a correção de cursos inerentes funcionou
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from datetime import date

def testar_cursos_inerentes():
    """Testa se a validação de cursos inerentes está funcionando corretamente"""
    
    print("=== TESTE DE CURSOS INERENTES ===\n")
    
    # Criar um quadro de teste com data única
    quadro_teste = QuadroAcesso.objects.create(
        tipo='ANTIGUIDADE',
        data_promocao=date(2026, 1, 1),  # Data única para teste
        status='EM_ELABORACAO'
    )
    
    # Obter todos os militares ativos
    militares = Militar.objects.filter(situacao='AT')
    
    militares_aptos = 0
    militares_inaptos = 0
    
    print(f"Testando {militares.count()} militares ativos...\n")
    
    for militar in militares:
        apto, motivo = quadro_teste.validar_requisitos_quadro_acesso(militar)
        
        if apto:
            militares_aptos += 1
            print(f"✓ {militar.nome_completo} ({militar.matricula}) - {militar.get_quadro_display()} {militar.get_posto_graduacao_display()}")
        else:
            militares_inaptos += 1
            print(f"❌ {militar.nome_completo} ({militar.matricula}) - {militar.get_quadro_display()} {militar.get_posto_graduacao_display()}")
            print(f"   Motivo: {motivo}")
    
    # Limpar quadro de teste
    quadro_teste.delete()
    
    print(f"\n=== RESULTADO ===")
    print(f"Militares aptos: {militares_aptos}")
    print(f"Militares inaptos: {militares_inaptos}")
    print(f"Total: {militares.count()}")
    
    if militares_inaptos == 0:
        print("🎉 TODOS OS MILITARES ESTÃO APTOS!")
    else:
        print(f"⚠️  Ainda há {militares_inaptos} militares inaptos")
    
    return militares_aptos, militares_inaptos

if __name__ == "__main__":
    testar_cursos_inerentes() 