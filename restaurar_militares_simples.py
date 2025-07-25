#!/usr/bin/env python
"""
Script simples para restaurar militares do backup
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

def restaurar_militares():
    """
    Restaura os militares do backup
    """
    print("Restaurando militares do backup...")
    
    try:
        with open('backups/backup_completo_20250724_130613.json', 'r', encoding='utf-16') as f:
            data = json.load(f)
        
        # Filtrar militares
        militares_backup = [obj for obj in data if obj.get('model') == 'militares.militar']
        
        print(f"Total de militares no backup: {len(militares_backup)}")
        print(f"Militares atuais no sistema: {Militar.objects.count()}")
        
        militares_criados = 0
        militares_erro = 0
        
        for militar_data in militares_backup:
            try:
                fields = militar_data['fields']
                cpf = fields.get('cpf', 'N/A')
                
                # Verificar se o militar já existe
                if Militar.objects.filter(cpf=cpf).exists():
                    continue
                
                # Remover campos que não devem ser definidos manualmente
                campos_remover = ['id', 'created_at', 'updated_at']
                for campo in campos_remover:
                    if campo in fields:
                        del fields[campo]
                
                # Remover campo user por enquanto (vamos associar depois)
                if 'user' in fields:
                    del fields['user']
                
                # Criar militar
                militar = Militar(**fields)
                militar.save()
                
                militares_criados += 1
                
                if militares_criados % 50 == 0:
                    print(f"  Progresso: {militares_criados} militares criados...")
                
            except Exception as e:
                print(f"  Erro ao criar militar {cpf}: {e}")
                militares_erro += 1
        
        print(f"\nResumo da restauração:")
        print(f"  Militares criados: {militares_criados}")
        print(f"  Erros: {militares_erro}")
        
        # Associar usuários aos militares
        print("\nAssociando usuários aos militares...")
        associacoes = 0
        
        usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
        
        for user in usuarios_cpf:
            try:
                militar = Militar.objects.get(cpf=user.username)
                militar.user = user
                militar.save()
                associacoes += 1
            except Militar.DoesNotExist:
                pass
        
        print(f"  Usuários associados: {associacoes}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    restaurar_militares() 