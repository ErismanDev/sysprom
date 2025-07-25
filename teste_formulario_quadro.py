#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from militares.views import gerar_quadro_acesso
from militares.models import QuadroAcesso
from datetime import datetime

def testar_formulario_quadro():
    """Testa o formulário de geração de quadro"""
    print("=== TESTE DE FORMULÁRIO DE QUADRO ===")
    
    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username='teste_quadro',
        defaults={'email': 'teste@teste.com'}
    )
    if created:
        user.set_password('teste123')
        user.save()
        print(f"✓ Usuário de teste criado: {user.username}")
    else:
        print(f"✓ Usuário de teste já existe: {user.username}")
    
    # Criar uma requisição de teste
    factory = RequestFactory()
    
    # Teste 1: Gerar quadro de praças
    print("\n--- Teste 1: Gerar quadro de praças ---")
    request = factory.post('/gerar-quadro-acesso/', {
        'tipo': 'ANTIGUIDADE',
        'categoria': 'PRACAS',
        'data_promocao': '2025-07-18',
        'csrfmiddlewaretoken': 'teste'
    })
    request.user = user
    
    try:
        response = gerar_quadro_acesso(request)
        print(f"✓ Resposta: {response.status_code}")
        print(f"✓ URL de redirecionamento: {response.url}")
        
        # Verificar se o quadro foi criado
        quadros_pracas = QuadroAcesso.objects.filter(categoria='PRACAS').order_by('-data_criacao')
        if quadros_pracas.exists():
            ultimo_quadro = quadros_pracas.first()
            print(f"✓ Quadro de praças criado com ID: {ultimo_quadro.pk}")
            print(f"  - Categoria: {ultimo_quadro.categoria}")
            print(f"  - Tipo: {ultimo_quadro.tipo}")
            print(f"  - Data: {ultimo_quadro.data_promocao}")
        else:
            print("✗ Nenhum quadro de praças foi criado")
            
    except Exception as e:
        print(f"✗ ERRO no teste de praças: {str(e)}")
    
    # Teste 2: Gerar quadro de oficiais
    print("\n--- Teste 2: Gerar quadro de oficiais ---")
    request = factory.post('/gerar-quadro-acesso/', {
        'tipo': 'ANTIGUIDADE',
        'categoria': 'OFICIAIS',
        'data_promocao': '2025-07-18',
        'csrfmiddlewaretoken': 'teste'
    })
    request.user = user
    
    try:
        response = gerar_quadro_acesso(request)
        print(f"✓ Resposta: {response.status_code}")
        print(f"✓ URL de redirecionamento: {response.url}")
        
        # Verificar se o quadro foi criado
        quadros_oficiais = QuadroAcesso.objects.filter(categoria='OFICIAIS').order_by('-data_criacao')
        if quadros_oficiais.exists():
            ultimo_quadro = quadros_oficiais.first()
            print(f"✓ Quadro de oficiais criado com ID: {ultimo_quadro.pk}")
            print(f"  - Categoria: {ultimo_quadro.categoria}")
            print(f"  - Tipo: {ultimo_quadro.tipo}")
            print(f"  - Data: {ultimo_quadro.data_promocao}")
        else:
            print("✗ Nenhum quadro de oficiais foi criado")
            
    except Exception as e:
        print(f"✗ ERRO no teste de oficiais: {str(e)}")
    
    # Limpar quadros de teste
    print("\n--- Limpeza ---")
    quadros_teste = QuadroAcesso.objects.filter(
        data_promocao=datetime.strptime('2025-07-18', '%Y-%m-%d').date()
    )
    if quadros_teste.exists():
        quadros_teste.delete()
        print(f"✓ {quadros_teste.count()} quadros de teste removidos")
    else:
        print("✓ Nenhum quadro de teste encontrado para remoção")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    testar_formulario_quadro() 