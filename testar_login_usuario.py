#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password

def testar_login_usuario():
    print("=== TESTANDO LOGIN DE USUÁRIOS ===\n")
    
    # Lista de usuários para testar
    usuarios_teste = [
        'admin',
        '490.083.823-34',  # ERISMAN
        '361.367.943-49',  # CLEMILTON
        '342.306.373-49',  # TAVARES
        '351.104.653-04',  # VELOSO
    ]
    
    # Senhas comuns para testar
    senhas_teste = [
        'admin',
        '123456',
        'password',
        'senha',
        '123',
        'admin123',
        'seprom',
        'cbmepi',
        'militar',
        'usuario',
        'teste',
        '123456789',
        '000000',
        '111111',
        '222222',
        '333333',
        '444444',
        '555555',
        '666666',
        '777777',
        '888888',
        '999999',
    ]
    
    for username in usuarios_teste:
        print(f"\n--- Testando usuário: {username} ---")
        
        try:
            # Buscar usuário
            try:
                usuario = User.objects.get(username=username)
                print(f"   ✅ Usuário encontrado")
                print(f"   - Ativo: {'Sim' if usuario.is_active else 'Não'}")
                print(f"   - Staff: {'Sim' if usuario.is_staff else 'Não'}")
                print(f"   - Superuser: {'Sim' if usuario.is_superuser else 'Não'}")
                print(f"   - Senha definida: {'Sim' if usuario.password else 'Não'}")
                
                if usuario.password:
                    print(f"   - Hash da senha: {usuario.password[:50]}...")
                
                # Testar senhas
                print(f"   - Testando senhas...")
                senha_encontrada = False
                
                for senha in senhas_teste:
                    if check_password(senha, usuario.password):
                        print(f"   ✅ SENHA ENCONTRADA: '{senha}'")
                        senha_encontrada = True
                        break
                
                if not senha_encontrada:
                    print(f"   ❌ Nenhuma das senhas testadas funcionou")
                    
                    # Tentar autenticação direta
                    print(f"   - Tentando autenticação...")
                    for senha in senhas_teste:
                        user_auth = authenticate(username=username, password=senha)
                        if user_auth:
                            print(f"   ✅ AUTENTICAÇÃO FUNCIONOU com senha: '{senha}'")
                            break
                    else:
                        print(f"   ❌ Autenticação falhou para todas as senhas")
                
            except User.DoesNotExist:
                print(f"   ❌ Usuário não encontrado")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print(f"\n=== DICAS PARA LOGIN ===")
    print(f"1. Tente usar seu CPF como usuário")
    print(f"2. Senhas comuns: admin, 123456, password, senha")
    print(f"3. Se não funcionar, pode ser necessário redefinir a senha")
    print(f"4. Verifique se o usuário está ativo no sistema")

if __name__ == '__main__':
    testar_login_usuario() 