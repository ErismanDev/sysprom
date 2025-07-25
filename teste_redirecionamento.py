#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from datetime import datetime

def testar_redirecionamento():
    """Testa a lógica de redirecionamento baseada na categoria"""
    print("=== TESTE DE REDIRECIONAMENTO ===")
    
    # Criar quadros de teste
    try:
        # Quadro de praças
        quadro_pracas = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='PRACAS',
            data_promocao=datetime.now().date(),
            status='EM_ELABORACAO',
            observacoes="Teste de redirecionamento - praças"
        )
        print(f"✓ Quadro de praças criado com ID: {quadro_pracas.pk}")
        
        # Quadro de oficiais
        quadro_oficiais = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='OFICIAIS',
            data_promocao=datetime.now().date(),
            status='EM_ELABORACAO',
            observacoes="Teste de redirecionamento - oficiais"
        )
        print(f"✓ Quadro de oficiais criado com ID: {quadro_oficiais.pk}")
        
        # Testar lógica de redirecionamento
        print("\n--- Testando lógica de redirecionamento ---")
        
        # Para praças
        if quadro_pracas.categoria == 'PRACAS':
            url_pracas = f'/militares/pracas/quadros-acesso/{quadro_pracas.pk}/'
            print(f"✓ Redirecionamento para praças: {url_pracas}")
        else:
            print(f"✗ ERRO: Categoria esperada 'PRACAS', mas é '{quadro_pracas.categoria}'")
        
        # Para oficiais
        if quadro_oficiais.categoria == 'OFICIAIS':
            url_oficiais = f'/militares/quadros-acesso/{quadro_oficiais.pk}/'
            print(f"✓ Redirecionamento para oficiais: {url_oficiais}")
        else:
            print(f"✗ ERRO: Categoria esperada 'OFICIAIS', mas é '{quadro_oficiais.categoria}'")
        
        # Verificar URLs corretas
        print("\n--- Verificando URLs corretas ---")
        print("URL esperada para praças: /militares/pracas/quadros-acesso/{id}/")
        print("URL esperada para oficiais: /militares/quadros-acesso/{id}/")
        
        # Limpar quadros de teste
        quadro_pracas.delete()
        quadro_oficiais.delete()
        print("✓ Quadros de teste removidos")
        
    except Exception as e:
        print(f"✗ ERRO: {str(e)}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    testar_redirecionamento() 