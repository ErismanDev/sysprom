#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from militares.models import UsuarioFuncao, CargoFuncao
from militares.views import selecionar_funcao

def testar_selecionar_funcao():
    """Testa a view selecionar_funcao"""
    
    print("=== TESTE DA VIEW SELECIONAR_FUNCAO ===\n")
    
    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username='teste_selecionar_funcao',
        defaults={
            'first_name': 'Usuário',
            'last_name': 'Teste',
            'email': 'teste@teste.com'
        }
    )
    
    if created:
        user.set_password('teste123')
        user.save()
        print(f"Usuário de teste criado: {user.username}")
    else:
        print(f"Usuário de teste já existe: {user.username}")
    
    # Criar um cargo/função de teste
    cargo, created = CargoFuncao.objects.get_or_create(
        nome='Teste Cargo',
        defaults={
            'descricao': 'Cargo para teste',
            'ativo': True,
            'ordem': 1
        }
    )
    
    if created:
        print(f"Cargo de teste criado: {cargo.nome}")
    else:
        print(f"Cargo de teste já existe: {cargo.nome}")
    
    # Criar uma função para o usuário
    funcao, created = UsuarioFuncao.objects.get_or_create(
        usuario=user,
        cargo_funcao=cargo,
        defaults={
            'tipo_funcao': 'ADMINISTRATIVO',
            'status': 'ATIVO',
            'data_inicio': '2024-01-01'
        }
    )
    
    if created:
        print(f"Função de teste criada para {user.username}")
    else:
        print(f"Função de teste já existe para {user.username}")
    
    # Testar a view com sessão
    factory = RequestFactory()
    request = factory.get('/militares/selecionar-funcao/')
    request.user = user
    
    # Adicionar middleware de sessão
    middleware = SessionMiddleware(lambda request: None)
    middleware.process_request(request)
    request.session.save()
    
    try:
        response = selecionar_funcao(request)
        print(f"\nStatus da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ View funcionando corretamente!")
            print(f"Tipo de resposta: {type(response)}")
        else:
            print(f"❌ Erro na view: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao executar a view: {e}")
        import traceback
        traceback.print_exc()
    
    # Limpar dados de teste
    print(f"\n=== LIMPEZA DOS DADOS DE TESTE ===")
    UsuarioFuncao.objects.filter(usuario=user).delete()
    CargoFuncao.objects.filter(nome='Teste Cargo').delete()
    User.objects.filter(username='teste_selecionar_funcao').delete()
    print("Dados de teste removidos!")

if __name__ == '__main__':
    testar_selecionar_funcao() 