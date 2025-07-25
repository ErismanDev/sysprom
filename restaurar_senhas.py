#!/usr/bin/env python
"""
Script para restaurar as senhas originais dos usuários do backup
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def restaurar_senhas_originais(arquivo_backup):
    """
    Restaura as senhas originais dos usuários do backup
    """
    print(f"Restaurando senhas originais do backup: {arquivo_backup}")
    
    try:
        with open(arquivo_backup, 'r', encoding='utf-16') as f:
            dados_backup = json.load(f)
        
        # Filtrar usuários
        usuarios_backup = [obj for obj in dados_backup if obj.get('model') == 'auth.user']
        
        print(f"Total de usuários no backup: {len(usuarios_backup)}")
        
        senhas_restauradas = 0
        senhas_erro = 0
        
        for user_data in usuarios_backup:
            try:
                fields = user_data['fields']
                username = fields['username']
                
                # Buscar usuário no sistema
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    print(f"  ✗ Usuário {username} não encontrado no sistema")
                    continue
                
                # Verificar se tem senha no backup
                if 'password' in fields and fields['password']:
                    # A senha está hasheada, então precisamos usar set_password
                    # Mas como não temos a senha original, vamos usar a hasheada diretamente
                    user.password = fields['password']
                    user.save()
                    print(f"  ✓ Senha restaurada para {username}")
                    senhas_restauradas += 1
                else:
                    print(f"  - Usuário {username} não tem senha no backup")
                
            except Exception as e:
                print(f"  ✗ Erro ao restaurar senha para {fields.get('username', 'N/A')}: {e}")
                senhas_erro += 1
        
        print(f"\nResumo da restauração de senhas:")
        print(f"  Senhas restauradas: {senhas_restauradas}")
        print(f"  Erros: {senhas_erro}")
        
    except Exception as e:
        print(f"Erro ao ler backup: {e}")

def verificar_senhas_backup(arquivo_backup):
    """
    Verifica quais usuários têm senhas no backup
    """
    print(f"Verificando senhas no backup: {arquivo_backup}")
    
    try:
        with open(arquivo_backup, 'r', encoding='utf-16') as f:
            dados_backup = json.load(f)
        
        # Filtrar usuários
        usuarios_backup = [obj for obj in dados_backup if obj.get('model') == 'auth.user']
        
        usuarios_com_senha = 0
        usuarios_sem_senha = 0
        
        for user_data in usuarios_backup:
            fields = user_data['fields']
            if 'password' in fields and fields['password']:
                usuarios_com_senha += 1
            else:
                usuarios_sem_senha += 1
        
        print(f"Usuários com senha no backup: {usuarios_com_senha}")
        print(f"Usuários sem senha no backup: {usuarios_sem_senha}")
        
        # Mostrar alguns exemplos de usuários com senha
        print("\nExemplos de usuários com senha:")
        for i, user_data in enumerate(usuarios_backup[:5]):
            fields = user_data['fields']
            if 'password' in fields and fields['password']:
                print(f"  {fields['username']} - Senha: {'*' * len(fields['password'][:20])}...")
        
        return usuarios_com_senha > 0
        
    except Exception as e:
        print(f"Erro ao verificar backup: {e}")
        return False

if __name__ == "__main__":
    arquivo_backup = "backups/backup_completo_20250724_130613.json"
    
    # Verificar se há senhas no backup
    tem_senhas = verificar_senhas_backup(arquivo_backup)
    
    if tem_senhas:
        # Perguntar se deve restaurar
        resposta = input("\nDeseja restaurar as senhas originais? (s/n): ").lower()
        
        if resposta == 's':
            restaurar_senhas_originais(arquivo_backup)
        else:
            print("Restauração de senhas cancelada.")
    else:
        print("Nenhuma senha encontrada no backup.") 