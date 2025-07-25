#!/usr/bin/env python
"""
Script para verificar e corrigir usuários duplicados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Count

def verificar_duplicados():
    """
    Verifica usuários duplicados
    """
    print("=== ANÁLISE DE USUÁRIOS DUPLICADOS ===")
    
    total_usuarios = User.objects.count()
    usuarios_unicos = User.objects.values('username').distinct().count()
    
    print(f"Total de usuários: {total_usuarios}")
    print(f"Usuários únicos por username: {usuarios_unicos}")
    print(f"Usuários duplicados: {total_usuarios - usuarios_unicos}")
    
    # Encontrar duplicados
    duplicados = User.objects.values('username').annotate(count=Count('id')).filter(count__gt=1)
    
    if duplicados:
        print("\nUsuários duplicados encontrados:")
        for dup in duplicados:
            username = dup['username']
            count = dup['count']
            print(f"  {username}: {count} registros")
            
            # Mostrar detalhes dos duplicados
            users = User.objects.filter(username=username).order_by('id')
            for i, user in enumerate(users):
                print(f"    {i+1}. ID: {user.id}, Email: {user.email}, Ativo: {user.is_active}, Staff: {user.is_staff}")
    
    return duplicados

def corrigir_duplicados():
    """
    Corrige usuários duplicados mantendo apenas o primeiro
    """
    print("\n=== CORRIGINDO USUÁRIOS DUPLICADOS ===")
    
    duplicados = User.objects.values('username').annotate(count=Count('id')).filter(count__gt=1)
    
    if not duplicados:
        print("Nenhum usuário duplicado encontrado.")
        return
    
    removidos = 0
    
    for dup in duplicados:
        username = dup['username']
        count = dup['count']
        
        print(f"\nCorrigindo duplicados para: {username} ({count} registros)")
        
        # Pegar todos os usuários com este username
        users = User.objects.filter(username=username).order_by('id')
        
        # Manter o primeiro (mais antigo) e remover os outros
        primeiro = users.first()
        outros = users.exclude(id=primeiro.id)
        
        print(f"  Mantendo: ID {primeiro.id} (Email: {primeiro.email})")
        
        for user in outros:
            print(f"  Removendo: ID {user.id} (Email: {user.email})")
            user.delete()
            removidos += 1
    
    print(f"\nTotal de usuários duplicados removidos: {removidos}")
    
    # Verificar resultado
    total_final = User.objects.count()
    print(f"Total de usuários após correção: {total_final}")

if __name__ == "__main__":
    # Verificar duplicados
    duplicados = verificar_duplicados()
    
    if duplicados:
        resposta = input("\nDeseja corrigir os usuários duplicados? (s/n): ").lower()
        if resposta == 's':
            corrigir_duplicados()
        else:
            print("Correção cancelada.")
    else:
        print("Nenhum usuário duplicado encontrado.") 