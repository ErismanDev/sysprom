#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def teste_sistema_web():
    """Testa o sistema web diretamente"""
    
    print("=== TESTE DO SISTEMA WEB ===\n")
    
    # Criar cliente de teste
    client = Client()
    
    # Testar login
    print("1. Testando login...")
    response = client.post('/login/', {
        'username': 'erisman',
        'password': 'cbmepi123'
    })
    
    print(f"Status code: {response.status_code}")
    print(f"Redirect: {response.url if hasattr(response, 'url') else 'None'}")
    
    if response.status_code == 302:
        print("✅ Login bem-sucedido!")
        
        # Seguir o redirecionamento
        print("\n2. Seguindo redirecionamento...")
        response = client.get(response.url)
        print(f"Status code: {response.status_code}")
        
        # Verificar se há mensagens de erro
        from django.contrib.messages import get_messages
        messages = list(get_messages(response.wsgi_request))
        if messages:
            print("Mensagens:")
            for message in messages:
                print(f"  - {message}")
        
        # Verificar conteúdo da página
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'Você não possui funções ativas no sistema' in content:
                print("❌ ERRO: Mensagem de 'não possui funções ativas' encontrada!")
            else:
                print("✅ Página carregada sem erro de funções!")
        else:
            print(f"❌ Erro ao carregar página: {response.status_code}")
    else:
        print("❌ Falha no login!")

if __name__ == '__main__':
    teste_sistema_web() 