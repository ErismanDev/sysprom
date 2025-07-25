#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from datetime import datetime

def teste_comparacao_categoria():
    """Testa se há algum problema com a comparação da categoria"""
    print("=== TESTE DE COMPARAÇÃO DE CATEGORIA ===")
    
    # Criar quadro de praças
    quadro = QuadroAcesso.objects.create(
        tipo='ANTIGUIDADE',
        categoria='PRACAS',
        data_promocao=datetime.now().date(),
        status='EM_ELABORACAO',
        observacoes="Teste de comparação"
    )
    
    print(f"Quadro criado com ID: {quadro.pk}")
    print(f"Categoria do quadro: '{quadro.categoria}'")
    print(f"Tipo da categoria: {type(quadro.categoria)}")
    print(f"Comprimento da categoria: {len(quadro.categoria)}")
    
    # Testar diferentes formas de comparação
    print(f"\n--- Testando comparações ---")
    
    # Comparação direta
    resultado1 = quadro.categoria == 'PRACAS'
    print(f"quadro.categoria == 'PRACAS': {resultado1}")
    
    # Comparação com strip
    resultado2 = quadro.categoria.strip() == 'PRACAS'
    print(f"quadro.categoria.strip() == 'PRACAS': {resultado2}")
    
    # Comparação case-insensitive
    resultado3 = quadro.categoria.upper() == 'PRACAS'
    print(f"quadro.categoria.upper() == 'PRACAS': {resultado3}")
    
    # Verificar se há espaços ou caracteres especiais
    print(f"Representação em bytes: {repr(quadro.categoria)}")
    print(f"Caracteres ASCII: {[ord(c) for c in quadro.categoria]}")
    
    # Testar a lógica de redirecionamento
    print(f"\n--- Testando lógica de redirecionamento ---")
    
    if quadro.categoria == 'PRACAS':
        print("✓ Redirecionando para praças")
        url_esperada = f'/militares/pracas/quadros-acesso/{quadro.pk}/'
        print(f"✓ URL esperada: {url_esperada}")
    else:
        print("✗ Redirecionando para oficiais (ERRO!)")
        url_esperada = f'/militares/quadros-acesso/{quadro.pk}/'
        print(f"✗ URL incorreta: {url_esperada}")
    
    # Limpar quadro de teste
    quadro.delete()
    print("✓ Quadro de teste removido")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    teste_comparacao_categoria() 