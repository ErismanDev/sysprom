#!/usr/bin/env python
"""
Script para verificar diferentes tipos de duplicados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Count
from militares.models import Militar

def verificar_duplicados_detalhado():
    """
    Verifica diferentes tipos de duplicados
    """
    print("=== ANÁLISE DETALHADA DE DUPLICADOS ===")
    
    # 1. Verificar usuários por username
    print("\n1. USUÁRIOS POR USERNAME:")
    total_usuarios = User.objects.count()
    usuarios_unicos = User.objects.values('username').distinct().count()
    print(f"  Total: {total_usuarios}")
    print(f"  Únicos: {usuarios_unicos}")
    print(f"  Duplicados: {total_usuarios - usuarios_unicos}")
    
    # 2. Verificar usuários por email
    print("\n2. USUÁRIOS POR EMAIL:")
    emails_unicos = User.objects.exclude(email='').values('email').distinct().count()
    emails_total = User.objects.exclude(email='').count()
    print(f"  Total com email: {emails_total}")
    print(f"  Emails únicos: {emails_unicos}")
    print(f"  Emails duplicados: {emails_total - emails_unicos}")
    
    # 3. Verificar militares por CPF
    print("\n3. MILITARES POR CPF:")
    total_militares = Militar.objects.count()
    cpfs_unicos = Militar.objects.values('cpf').distinct().count()
    print(f"  Total: {total_militares}")
    print(f"  CPFs únicos: {cpfs_unicos}")
    print(f"  CPFs duplicados: {total_militares - cpfs_unicos}")
    
    # 4. Verificar militares por nome
    print("\n4. MILITARES POR NOME:")
    nomes_unicos = Militar.objects.values('nome_completo').distinct().count()
    print(f"  Nomes únicos: {nomes_unicos}")
    print(f"  Nomes duplicados: {total_militares - nomes_unicos}")
    
    # 5. Verificar usuários que são CPFs
    print("\n5. USUÁRIOS QUE SÃO CPFS:")
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    print(f"  Total de usuários CPF: {usuarios_cpf.count()}")
    
    # 6. Verificar se há CPFs de usuários que não existem como militares
    print("\n6. CPFS DE USUÁRIOS SEM MILITAR CORRESPONDENTE:")
    cpfs_sem_militar = 0
    for user in usuarios_cpf:
        if not Militar.objects.filter(cpf=user.username).exists():
            cpfs_sem_militar += 1
            print(f"  {user.username} - {user.email}")
    print(f"  Total de CPFs sem militar: {cpfs_sem_militar}")
    
    # 7. Verificar militares sem usuário
    print("\n7. MILITARES SEM USUÁRIO:")
    militares_sem_usuario = Militar.objects.filter(user__isnull=True).count()
    print(f"  Militares sem usuário: {militares_sem_usuario}")
    
    # 8. Verificar usuários administrativos duplicados
    print("\n8. USUÁRIOS ADMINISTRATIVOS:")
    admins = User.objects.filter(username__in=['admin', 'superusuario', 'erisman'])
    for admin in admins:
        print(f"  {admin.username}: {admin.email} - Staff: {admin.is_staff} - Super: {admin.is_superuser}")

if __name__ == "__main__":
    verificar_duplicados_detalhado() 