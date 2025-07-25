#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from militares.models import QuadroAcesso
from datetime import datetime

def testar_navegador():
    """Testa o formulário usando o cliente de teste do Django"""
    print("=== TESTE DE NAVEGADOR ===")
    
    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username='teste_navegador',
        defaults={'email': 'teste@teste.com'}
    )
    if created:
        user.set_password('teste123')
        user.save()
        print(f"✓ Usuário de teste criado: {user.username}")
    else:
        print(f"✓ Usuário de teste já existe: {user.username}")
    
    # Criar cliente de teste
    client = Client()
    
    # Fazer login
    login_success = client.login(username='teste_navegador', password='teste123')
    if login_success:
        print("✓ Login realizado com sucesso")
    else:
        print("✗ Falha no login")
        return
    
    # Teste 1: Acessar página de geração de quadro
    print("\n--- Teste 1: Acessar página de geração ---")
    response = client.get('/militares/gerar-quadro-acesso/')
    print(f"✓ Status da página: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Página carregada com sucesso")
        # Verificar se o campo categoria está presente
        if 'categoria' in response.content.decode():
            print("✓ Campo categoria encontrado na página")
        else:
            print("✗ Campo categoria NÃO encontrado na página")
    else:
        print(f"✗ Erro ao carregar página: {response.status_code}")
    
    # Teste 2: Enviar formulário com praças
    print("\n--- Teste 2: Enviar formulário para praças ---")
    response = client.post('/militares/gerar-quadro-acesso/', {
        'tipo': 'ANTIGUIDADE',
        'categoria': 'PRACAS',
        'data_promocao': '2025-07-18',
    })
    
    print(f"✓ Status da resposta: {response.status_code}")
    print(f"✓ URL de redirecionamento: {response.url}")
    
    # Verificar se o quadro foi criado
    quadros_pracas = QuadroAcesso.objects.filter(categoria='PRACAS').order_by('-data_criacao')
    if quadros_pracas.exists():
        ultimo_quadro = quadros_pracas.first()
        print(f"✓ Quadro de praças criado com ID: {ultimo_quadro.pk}")
        print(f"  - Categoria: {ultimo_quadro.categoria}")
        print(f"  - Tipo: {ultimo_quadro.tipo}")
        
        # Verificar se o redirecionamento está correto
        if 'pracas/quadros-acesso' in response.url:
            print("✓ Redirecionamento correto para praças")
        else:
            print(f"✗ Redirecionamento incorreto: {response.url}")
    else:
        print("✗ Nenhum quadro de praças foi criado")
    
    # Teste 3: Enviar formulário com oficiais
    print("\n--- Teste 3: Enviar formulário para oficiais ---")
    response = client.post('/militares/gerar-quadro-acesso/', {
        'tipo': 'ANTIGUIDADE',
        'categoria': 'OFICIAIS',
        'data_promocao': '2025-07-18',
    })
    
    print(f"✓ Status da resposta: {response.status_code}")
    print(f"✓ URL de redirecionamento: {response.url}")
    
    # Verificar se o quadro foi criado
    quadros_oficiais = QuadroAcesso.objects.filter(categoria='OFICIAIS').order_by('-data_criacao')
    if quadros_oficiais.exists():
        ultimo_quadro = quadros_oficiais.first()
        print(f"✓ Quadro de oficiais criado com ID: {ultimo_quadro.pk}")
        print(f"  - Categoria: {ultimo_quadro.categoria}")
        print(f"  - Tipo: {ultimo_quadro.tipo}")
        
        # Verificar se o redirecionamento está correto
        if 'quadros-acesso' in response.url and 'pracas' not in response.url:
            print("✓ Redirecionamento correto para oficiais")
        else:
            print(f"✗ Redirecionamento incorreto: {response.url}")
    else:
        print("✗ Nenhum quadro de oficiais foi criado")
    
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
    testar_navegador() 