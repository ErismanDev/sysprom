#!/usr/bin/env python
"""
Script para restaurar os militares do backup
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def verificar_militares_backup(arquivo_backup):
    """
    Verifica se há militares no backup
    """
    print(f"Verificando militares no backup: {arquivo_backup}")
    
    try:
        with open(arquivo_backup, 'r', encoding='utf-16') as f:
            dados_backup = json.load(f)
        
        # Filtrar militares
        militares_backup = [obj for obj in dados_backup if obj.get('model') == 'militares.militar']
        
        print(f"Total de militares no backup: {len(militares_backup)}")
        
        if militares_backup:
            # Mostrar alguns exemplos
            print("\nExemplos de militares no backup:")
            for i, militar_data in enumerate(militares_backup[:5]):
                fields = militar_data['fields']
                print(f"  {i+1}. {fields.get('nome_completo', 'N/A')} - {fields.get('cpf', 'N/A')} - {fields.get('posto_graduacao', 'N/A')}")
            
            if len(militares_backup) > 5:
                print(f"  ... e mais {len(militares_backup) - 5} militares")
        
        return militares_backup
        
    except Exception as e:
        print(f"Erro ao verificar backup: {e}")
        return []

def restaurar_militares(militares_backup):
    """
    Restaura os militares do backup
    """
    print(f"\nRestaurando {len(militares_backup)} militares...")
    
    militares_criados = 0
    militares_erro = 0
    
    for militar_data in militares_backup:
        try:
            fields = militar_data['fields']
            
            # Verificar se o militar já existe
            if Militar.objects.filter(cpf=fields['cpf']).exists():
                print(f"  Militar {fields['cpf']} já existe, pulando...")
                continue
            
            # Remover campos que não devem ser definidos manualmente
            campos_remover = ['id', 'created_at', 'updated_at']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            # Associar usuário se existir
            if 'user' in fields and fields['user']:
                try:
                    user = User.objects.get(id=fields['user'])
                    fields['user'] = user
                except User.DoesNotExist:
                    print(f"    Aviso: Usuário {fields['user']} não encontrado para militar {fields['cpf']}")
                    del fields['user']
            
            # Criar militar
            militar = Militar(**fields)
            militar.save()
            
            print(f"  ✓ Militar {fields['cpf']} - {fields.get('nome_completo', 'N/A')} criado com sucesso")
            militares_criados += 1
            
        except Exception as e:
            print(f"  ✗ Erro ao criar militar {fields.get('cpf', 'N/A')}: {e}")
            militares_erro += 1
    
    print(f"\nResumo da restauração de militares:")
    print(f"  Militares criados: {militares_criados}")
    print(f"  Erros: {militares_erro}")

def associar_usuarios_militares():
    """
    Associa usuários aos militares baseado no CPF
    """
    print("\nAssociando usuários aos militares...")
    
    associacoes = 0
    
    # Buscar usuários que são CPFs
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    
    for user in usuarios_cpf:
        try:
            # Buscar militar pelo CPF
            militar = Militar.objects.get(cpf=user.username)
            
            # Associar usuário ao militar
            militar.user = user
            militar.save()
            
            print(f"  ✓ Usuário {user.username} associado ao militar {militar.nome_completo}")
            associacoes += 1
            
        except Militar.DoesNotExist:
            print(f"  - Militar com CPF {user.username} não encontrado")
        except Exception as e:
            print(f"  ✗ Erro ao associar usuário {user.username}: {e}")
    
    print(f"\nTotal de associações realizadas: {associacoes}")

if __name__ == "__main__":
    arquivo_backup = "backups/backup_completo_20250724_130613.json"
    
    # Verificar militares no backup
    militares_backup = verificar_militares_backup(arquivo_backup)
    
    if militares_backup:
        # Perguntar se deve restaurar
        print(f"\nMilitares atuais no sistema: {Militar.objects.count()}")
        resposta = input("Deseja restaurar os militares? (s/n): ").lower()
        
        if resposta == 's':
            restaurar_militares(militares_backup)
            
            # Perguntar se deve associar usuários
            resposta2 = input("\nDeseja associar usuários aos militares? (s/n): ").lower()
            if resposta2 == 's':
                associar_usuarios_militares()
        else:
            print("Restauração de militares cancelada.")
    else:
        print("Nenhum militar encontrado no backup.") 