#!/usr/bin/env python
"""
Script simples para restaurar apenas usuários e militares
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

def restaurar_usuarios_militares_simples(arquivo_backup):
    """
    Restaura apenas usuários e militares de forma simples
    """
    print(f"Restaurando usuários e militares do backup: {arquivo_backup}")
    
    # Ler o arquivo de backup
    try:
        with open(arquivo_backup, 'r', encoding='utf-16') as f:
            dados_backup = json.load(f)
        print(f"Backup carregado com sucesso. Contém {len(dados_backup)} objetos.")
    except Exception as e:
        print(f"Erro ao ler backup: {e}")
        return
    
    # Limpar usuários e militares existentes
    print("Limpando dados existentes...")
    Militar.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    
    # Contadores
    usuarios_criados = 0
    militares_criados = 0
    
    # Restaurar dados
    print("Restaurando dados...")
    
    for item in dados_backup:
        try:
            model_name = item['model']
            pk = item['pk']
            fields = item['fields']
            
            if model_name == 'auth.user':
                # Restaurar usuário
                if not User.objects.filter(pk=pk).exists():
                    user = User(pk=pk, **fields)
                    user.save()
                    usuarios_criados += 1
                    if usuarios_criados % 10 == 0:
                        print(f"  {usuarios_criados} usuários criados...")
            
            elif model_name == 'militares.militar':
                # Restaurar militar
                if not Militar.objects.filter(pk=pk).exists():
                    militar = Militar(pk=pk, **fields)
                    militar.save()
                    militares_criados += 1
                    if militares_criados % 10 == 0:
                        print(f"  {militares_criados} militares criados...")
                        
        except Exception as e:
            print(f"  Erro ao restaurar {item.get('model', 'desconhecido')}: {e}")
            continue
    
    print("Restauração concluída!")
    print(f"Usuários criados: {usuarios_criados}")
    print(f"Militares criados: {militares_criados}")
    print(f"Total de usuários no sistema: {User.objects.count()}")
    print(f"Total de militares no sistema: {Militar.objects.count()}")

if __name__ == '__main__':
    arquivo_backup = 'backups/backup_completo_20250724_130613.json'
    restaurar_usuarios_militares_simples(arquivo_backup) 