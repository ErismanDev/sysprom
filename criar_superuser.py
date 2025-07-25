#!/usr/bin/env python
"""
Script para criar um superusuário automaticamente
"""

import os
import sys
import django

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def criar_superuser():
    """Cria um superusuário automaticamente"""
    
    # Definir variável de ambiente para senha
    os.environ['PGPASSWORD'] = 'Erisman@193'
    
    print("🔧 Criando superusuário...")
    
    # Verificar se já existe um superusuário
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superusuário já existe!")
        return
    
    # Criar superusuário
    try:
        user = User.objects.create_superuser(
            username='admin',
            email='admin@sepromcbmepi.com',
            password='admin123'
        )
        print("✅ Superusuário criado com sucesso!")
        print(f"👤 Usuário: admin")
        print(f"🔑 Senha: admin123")
        print("⚠️ IMPORTANTE: Altere a senha após o primeiro login!")
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")

if __name__ == "__main__":
    criar_superuser() 