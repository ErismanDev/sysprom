#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a interface do CHSGT
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_interface_chsgt():
    """Testa se a interface do CHSGT está funcionando"""
    
    print("=== TESTE DA INTERFACE CHSGT ===\n")
    
    # Buscar um cabo para teste
    cabos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='CAB'
    )[:5]
    
    if not cabos.exists():
        print("❌ Nenhum cabo encontrado para teste")
        return
    
    print(f"✅ Encontrados {cabos.count()} cabos para teste")
    
    for cabo in cabos:
        print(f"\n--- Testando Cabo: {cabo.nome_completo} ---")
        print(f"ID: {cabo.pk}")
        print(f"CHSGT atual: {cabo.curso_chsgt}")
        print(f"Nota CHSGT atual: {cabo.nota_chsgt}")
        
        # Simular edição
        print(f"URL de edição: /militares/militares/{cabo.pk}/editar/")
        print(f"Para testar: acesse a URL acima e marque o checkbox CHSGT")
        
    print("\n=== INSTRUÇÕES PARA TESTE ===")
    print("1. Acesse um cabo no sistema")
    print("2. Vá para edição")
    print("3. Marque o checkbox 'Possui Curso de Habilitação de Sargentos (CHSGT)'")
    print("4. Verifique se o campo 'Nota do CHSGT' aparece")
    print("5. Desmarque o checkbox e verifique se o campo some")
    print("6. Abra o console do navegador (F12) para ver os logs de debug")

if __name__ == "__main__":
    testar_interface_chsgt() 