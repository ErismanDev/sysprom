#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.urls import reverse
from militares.models import QuadroAcesso
from datetime import datetime

def teste_url_redirecionamento():
    """Testa se as URLs de redirecionamento estão funcionando"""
    print("=== TESTE DE URL DE REDIRECIONAMENTO ===")
    
    # Criar quadros de teste
    try:
        # Quadro de praças
        quadro_pracas = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='PRACAS',
            data_promocao=datetime.now().date(),
            status='EM_ELABORACAO',
            observacoes="Teste de URL - praças"
        )
        print(f"✓ Quadro de praças criado com ID: {quadro_pracas.pk}")
        
        # Quadro de oficiais
        quadro_oficiais = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            categoria='OFICIAIS',
            data_promocao=datetime.now().date(),
            status='EM_ELABORACAO',
            observacoes="Teste de URL - oficiais"
        )
        print(f"✓ Quadro de oficiais criado com ID: {quadro_oficiais.pk}")
        
        # Testar URLs
        print("\n--- Testando URLs ---")
        
        # URL para praças
        try:
            url_pracas = reverse('militares:quadro_acesso_pracas_detail', kwargs={'pk': quadro_pracas.pk})
            print(f"✓ URL para praças: {url_pracas}")
        except Exception as e:
            print(f"✗ ERRO na URL de praças: {str(e)}")
        
        # URL para oficiais
        try:
            url_oficiais = reverse('militares:quadro_acesso_detail', kwargs={'pk': quadro_oficiais.pk})
            print(f"✓ URL para oficiais: {url_oficiais}")
        except Exception as e:
            print(f"✗ ERRO na URL de oficiais: {str(e)}")
        
        # Testar lógica de redirecionamento
        print("\n--- Testando lógica de redirecionamento ---")
        
        # Para praças
        if quadro_pracas.categoria == 'PRACAS':
            print("✓ Categoria 'PRACAS' detectada corretamente")
            print(f"  - Redirecionamento esperado: quadro_acesso_pracas_detail")
            print(f"  - URL esperada: {url_pracas}")
        else:
            print(f"✗ ERRO: Categoria esperada 'PRACAS', mas é '{quadro_pracas.categoria}'")
        
        # Para oficiais
        if quadro_oficiais.categoria == 'OFICIAIS':
            print("✓ Categoria 'OFICIAIS' detectada corretamente")
            print(f"  - Redirecionamento esperado: quadro_acesso_detail")
            print(f"  - URL esperada: {url_oficiais}")
        else:
            print(f"✗ ERRO: Categoria esperada 'OFICIAIS', mas é '{quadro_oficiais.categoria}'")
        
        # Limpar quadros de teste
        quadro_pracas.delete()
        quadro_oficiais.delete()
        print("✓ Quadros de teste removidos")
        
    except Exception as e:
        print(f"✗ ERRO: {str(e)}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    teste_url_redirecionamento() 