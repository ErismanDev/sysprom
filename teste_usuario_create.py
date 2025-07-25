#!/usr/bin/env python
"""
Script para testar a criação de usuários via web
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.test import Client
from django.urls import reverse

def test_usuario_create():
    """Testa a criação de usuários via web"""
    print("=== TESTE DE CRIAÇÃO DE USUÁRIOS VIA WEB ===\n")
    
    # Criar cliente de teste
    client = Client()
    
    # 1. Testar acesso à página de criação (sem login)
    print("1. Testando acesso sem login...")
    response = client.get(reverse('militares:usuario_create'))
    print(f"   Status: {response.status_code}")
    print(f"   Redirecionamento para login: {'Sim' if response.status_code == 302 else 'Não'}")
    print()
    
    # 2. Criar um usuário admin para teste
    print("2. Criando usuário admin para teste...")
    try:
        admin_user = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='Teste',
            is_staff=True,
            is_superuser=True
        )
        print(f"   ✅ Usuário admin criado: {admin_user.username}")
    except Exception as e:
        print(f"   ❌ Erro ao criar admin: {e}")
        return
    
    # 3. Fazer login
    print("3. Fazendo login...")
    login_success = client.login(username='test_admin', password='admin123')
    print(f"   Login bem-sucedido: {'Sim' if login_success else 'Não'}")
    print()
    
    # 4. Testar acesso à página de criação (com login)
    print("4. Testando acesso com login...")
    response = client.get(reverse('militares:usuario_create'))
    print(f"   Status: {response.status_code}")
    print(f"   Página carregada: {'Sim' if response.status_code == 200 else 'Não'}")
    print()
    
    # 5. Testar criação de usuário via POST
    print("5. Testando criação de usuário...")
    post_data = {
        'username': 'novo_usuario',
        'first_name': 'Novo',
        'last_name': 'Usuário',
        'email': 'novo@test.com',
        'password': 'senha123',
        'confirm_password': 'senha123',
        'is_active': 'on',
        'groups': []
    }
    
    response = client.post(reverse('militares:usuario_create'), post_data)
    print(f"   Status: {response.status_code}")
    print(f"   Redirecionamento após criação: {'Sim' if response.status_code == 302 else 'Não'}")
    
    # Verificar se o usuário foi criado
    try:
        novo_usuario = User.objects.get(username='novo_usuario')
        print(f"   ✅ Usuário criado com sucesso: {novo_usuario.get_full_name()}")
    except User.DoesNotExist:
        print(f"   ❌ Usuário não foi criado")
    print()
    
    # 6. Testar lista de usuários
    print("6. Testando acesso à lista de usuários...")
    response = client.get(reverse('militares:usuarios_custom_list'))
    print(f"   Status: {response.status_code}")
    print(f"   Lista carregada: {'Sim' if response.status_code == 200 else 'Não'}")
    print()
    
    # 7. Limpeza
    print("7. Limpando dados de teste...")
    try:
        User.objects.filter(username__in=['test_admin', 'novo_usuario']).delete()
        print("   ✅ Dados de teste removidos")
    except Exception as e:
        print(f"   ❌ Erro na limpeza: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == '__main__':
    test_usuario_create() 