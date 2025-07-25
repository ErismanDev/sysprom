#!/usr/bin/env python
"""
Script para verificar e restaurar usuários do backup
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def verificar_usuarios_backup(arquivo_backup):
    """
    Verifica os usuários no backup
    """
    print(f"Verificando usuários no backup: {arquivo_backup}")
    
    try:
        with open(arquivo_backup, 'r', encoding='utf-16') as f:
            dados_backup = json.load(f)
        
        # Filtrar usuários
        usuarios_backup = [obj for obj in dados_backup if obj.get('model') == 'auth.user']
        
        print(f"Total de usuários no backup: {len(usuarios_backup)}")
        
        for i, user_data in enumerate(usuarios_backup[:10]):  # Mostrar apenas os primeiros 10
            fields = user_data['fields']
            print(f"  {i+1}. {fields.get('username', 'N/A')} - {fields.get('email', 'N/A')} - {fields.get('first_name', '')} {fields.get('last_name', '')}")
        
        if len(usuarios_backup) > 10:
            print(f"  ... e mais {len(usuarios_backup) - 10} usuários")
        
        return usuarios_backup
        
    except Exception as e:
        print(f"Erro ao ler backup: {e}")
        return []

def restaurar_usuarios(usuarios_backup):
    """
    Restaura os usuários do backup
    """
    print(f"\nRestaurando {len(usuarios_backup)} usuários...")
    
    usuarios_criados = 0
    usuarios_erro = 0
    
    for user_data in usuarios_backup:
        try:
            fields = user_data['fields']
            
            # Verificar se o usuário já existe
            if User.objects.filter(username=fields['username']).exists():
                print(f"  Usuário {fields['username']} já existe, pulando...")
                continue
            
            # Criar usuário
            user = User.objects.create_user(
                username=fields['username'],
                email=fields.get('email', ''),
                password=fields.get('password', 'changeme123'),  # Senha padrão
                first_name=fields.get('first_name', ''),
                last_name=fields.get('last_name', ''),
                is_staff=fields.get('is_staff', False),
                is_superuser=fields.get('is_superuser', False),
                is_active=fields.get('is_active', True)
            )
            
            print(f"  ✓ Usuário {fields['username']} criado com sucesso")
            usuarios_criados += 1
            
        except Exception as e:
            print(f"  ✗ Erro ao criar usuário {fields.get('username', 'N/A')}: {e}")
            usuarios_erro += 1
    
    print(f"\nResumo da restauração de usuários:")
    print(f"  Usuários criados: {usuarios_criados}")
    print(f"  Erros: {usuarios_erro}")

if __name__ == "__main__":
    arquivo_backup = "backups/backup_completo_20250724_130613.json"
    
    # Verificar usuários no backup
    usuarios_backup = verificar_usuarios_backup(arquivo_backup)
    
    if usuarios_backup:
        # Perguntar se deve restaurar
        print(f"\nUsuários atuais no sistema: {User.objects.count()}")
        resposta = input("Deseja restaurar os usuários? (s/n): ").lower()
        
        if resposta == 's':
            restaurar_usuarios(usuarios_backup)
        else:
            print("Restauração de usuários cancelada.")
    else:
        print("Nenhum usuário encontrado no backup.") 