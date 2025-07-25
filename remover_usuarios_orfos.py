#!/usr/bin/env python
"""
Script para remover usuários que não estão vinculados aos militares
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def verificar_usuarios_orfos():
    """
    Verifica usuários que não estão vinculados aos militares
    """
    print("=== VERIFICANDO USUÁRIOS ÓRFÃOS ===")
    
    total_usuarios = User.objects.count()
    print(f"Total de usuários: {total_usuarios}")
    
    # Usuários que são CPFs
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    print(f"Usuários CPF: {usuarios_cpf.count()}")
    
    # Militares com usuário
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    print(f"Militares com usuário: {militares_com_usuario}")
    
    # Usuários CPF que não têm militar correspondente
    usuarios_cpf_sem_militar = []
    for user in usuarios_cpf:
        if not Militar.objects.filter(cpf=user.username).exists():
            usuarios_cpf_sem_militar.append(user)
    
    print(f"Usuários CPF sem militar: {len(usuarios_cpf_sem_militar)}")
    
    # Usuários administrativos (não CPF)
    usuarios_admin = User.objects.exclude(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    print(f"Usuários administrativos: {usuarios_admin.count()}")
    
    # Usuários administrativos que não são essenciais
    usuarios_admin_nao_essenciais = []
    usuarios_essenciais = [
        'admin', 'superusuario', 'erisman', 'diretor_gestao',
        'presidente_cpo', 'presidente_cpp', 'membro_nato_cpo', 'membro_nato_cpp',
        'membro_efetivo_cpo', 'membro_efetivo_cpp', 'suplente_cpo', 'suplente_cpp',
        'digitador', 'chefe_promocoes'
    ]
    
    for user in usuarios_admin:
        if user.username not in usuarios_essenciais and not user.is_staff and not user.is_superuser:
            usuarios_admin_nao_essenciais.append(user)
    
    print(f"Usuários administrativos não essenciais: {len(usuarios_admin_nao_essenciais)}")
    
    # Mostrar alguns exemplos
    if usuarios_cpf_sem_militar:
        print("\nExemplos de usuários CPF sem militar:")
        for i, user in enumerate(usuarios_cpf_sem_militar[:5]):
            print(f"  {i+1}. {user.username} - {user.email}")
    
    if usuarios_admin_nao_essenciais:
        print("\nExemplos de usuários administrativos não essenciais:")
        for i, user in enumerate(usuarios_admin_nao_essenciais[:10]):
            print(f"  {i+1}. {user.username} - {user.email}")
    
    return usuarios_cpf_sem_militar, usuarios_admin_nao_essenciais

def remover_usuarios_orfos():
    """
    Remove usuários que não estão vinculados aos militares
    """
    print("\n=== REMOVENDO USUÁRIOS ÓRFÃOS ===")
    
    # Usuários CPF que não têm militar correspondente
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    usuarios_cpf_sem_militar = []
    
    for user in usuarios_cpf:
        if not Militar.objects.filter(cpf=user.username).exists():
            usuarios_cpf_sem_militar.append(user)
    
    # Usuários administrativos não essenciais
    usuarios_admin = User.objects.exclude(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    usuarios_essenciais = [
        'admin', 'superusuario', 'erisman', 'diretor_gestao',
        'presidente_cpo', 'presidente_cpp', 'membro_nato_cpo', 'membro_nato_cpp',
        'membro_efetivo_cpo', 'membro_efetivo_cpp', 'suplente_cpo', 'suplente_cpp',
        'digitador', 'chefe_promocoes'
    ]
    
    usuarios_admin_nao_essenciais = []
    for user in usuarios_admin:
        if user.username not in usuarios_essenciais and not user.is_staff and not user.is_superuser:
            usuarios_admin_nao_essenciais.append(user)
    
    total_para_remover = len(usuarios_cpf_sem_militar) + len(usuarios_admin_nao_essenciais)
    
    if total_para_remover == 0:
        print("Nenhum usuário órfão encontrado.")
        return
    
    print(f"Removendo {total_para_remover} usuários órfãos...")
    print(f"  - Usuários CPF sem militar: {len(usuarios_cpf_sem_militar)}")
    print(f"  - Usuários administrativos não essenciais: {len(usuarios_admin_nao_essenciais)}")
    
    usuarios_removidos = 0
    
    # Remover usuários CPF sem militar
    for user in usuarios_cpf_sem_militar:
        print(f"  Removendo CPF sem militar: {user.username}")
        user.delete()
        usuarios_removidos += 1
    
    # Remover usuários administrativos não essenciais
    for user in usuarios_admin_nao_essenciais:
        print(f"  Removendo admin não essencial: {user.username}")
        user.delete()
        usuarios_removidos += 1
    
    print(f"\nTotal de usuários removidos: {usuarios_removidos}")
    
    # Verificar resultado
    total_final = User.objects.count()
    print(f"Total de usuários após remoção: {total_final}")

def verificar_usuarios_essenciais():
    """
    Verifica usuários essenciais que devem permanecer
    """
    print("\n=== USUÁRIOS ESSENCIAIS (NÃO REMOVIDOS) ===")
    
    usuarios_essenciais = [
        'admin', 'superusuario', 'erisman', 'diretor_gestao',
        'presidente_cpo', 'presidente_cpp', 'membro_nato_cpo', 'membro_nato_cpp',
        'membro_efetivo_cpo', 'membro_efetivo_cpp', 'suplente_cpo', 'suplente_cpp',
        'digitador', 'chefe_promocoes'
    ]
    
    for username in usuarios_essenciais:
        try:
            user = User.objects.get(username=username)
            print(f"  {username} - {user.email} - Staff: {user.is_staff} - Super: {user.is_superuser}")
        except User.DoesNotExist:
            print(f"  {username} - NÃO ENCONTRADO")

if __name__ == "__main__":
    # Verificar usuários órfãos
    usuarios_cpf_sem_militar, usuarios_admin_nao_essenciais = verificar_usuarios_orfos()
    
    # Verificar usuários essenciais
    verificar_usuarios_essenciais()
    
    total_para_remover = len(usuarios_cpf_sem_militar) + len(usuarios_admin_nao_essenciais)
    
    if total_para_remover > 0:
        resposta = input(f"\nDeseja remover {total_para_remover} usuários órfãos? (s/n): ").lower()
        if resposta == 's':
            remover_usuarios_orfos()
        else:
            print("Remoção cancelada.")
    else:
        print("Nenhum usuário órfão encontrado.") 