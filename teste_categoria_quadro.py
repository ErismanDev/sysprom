#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from datetime import datetime

def testar_categoria_quadro():
    """Testa se o campo categoria está sendo salvo corretamente"""
    print("=== TESTE DE CATEGORIA DE QUADRO ===")
    
    # Criar um quadro de teste para praças
    try:
        quadro_pracas = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='PRACAS',
            data_promocao=datetime.now().date(),
            status='EM_ELABORACAO',
            observacoes="Teste de quadro de praças"
        )
        print(f"✓ Quadro de praças criado com ID: {quadro_pracas.pk}")
        print(f"  - Categoria: {quadro_pracas.categoria}")
        print(f"  - Tipo: {quadro_pracas.tipo}")
        
        # Verificar se a categoria foi salva corretamente
        if quadro_pracas.categoria == 'PRACAS':
            print("✓ Categoria 'PRACAS' foi salva corretamente")
        else:
            print(f"✗ ERRO: Categoria esperada 'PRACAS', mas foi salva como '{quadro_pracas.categoria}'")
        
        # Criar um quadro de teste para oficiais
        quadro_oficiais = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='OFICIAIS',
            data_promocao=datetime.now().date(),
            status='EM_ELABORACAO',
            observacoes="Teste de quadro de oficiais"
        )
        print(f"✓ Quadro de oficiais criado com ID: {quadro_oficiais.pk}")
        print(f"  - Categoria: {quadro_oficiais.categoria}")
        print(f"  - Tipo: {quadro_oficiais.tipo}")
        
        # Verificar se a categoria foi salva corretamente
        if quadro_oficiais.categoria == 'OFICIAIS':
            print("✓ Categoria 'OFICIAIS' foi salva corretamente")
        else:
            print(f"✗ ERRO: Categoria esperada 'OFICIAIS', mas foi salva como '{quadro_oficiais.categoria}'")
        
        # Limpar os quadros de teste
        quadro_pracas.delete()
        quadro_oficiais.delete()
        print("✓ Quadros de teste removidos")
        
    except Exception as e:
        print(f"✗ ERRO ao criar quadros de teste: {str(e)}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    testar_categoria_quadro() 