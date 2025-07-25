#!/usr/bin/env python
"""
Script para verificar duplicação de forma detalhada
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

def verificar_duplicacao_por_cpf():
    """
    Verifica duplicação por CPF (formato padrão)
    """
    print("=== VERIFICAÇÃO POR CPF (FORMATO PADRÃO) ===")
    
    # Usuários que são CPFs no formato padrão
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    
    # Agrupar por CPF
    cpfs_duplicados = {}
    for user in usuarios_cpf:
        cpf = user.username
        if cpf not in cpfs_duplicados:
            cpfs_duplicados[cpf] = []
        cpfs_duplicados[cpf].append(user)
    
    # Filtrar apenas CPFs com mais de um usuário
    cpfs_com_duplicados = {cpf: users for cpf, users in cpfs_duplicados.items() if len(users) > 1}
    
    print(f"CPFs com usuários duplicados: {len(cpfs_com_duplicados)}")
    
    if cpfs_com_duplicados:
        for cpf, users in list(cpfs_com_duplicados.items())[:5]:
            print(f"  {cpf}: {len(users)} usuários")
    
    return cpfs_com_duplicados

def verificar_duplicacao_por_padrao_militar():
    """
    Verifica duplicação por padrão militar_XXXXXX
    """
    print("\n=== VERIFICAÇÃO POR PADRÃO MILITAR_XXXXXX ===")
    
    # Usuários com padrão militar_
    usuarios_militar = User.objects.filter(username__startswith='militar_')
    
    # Extrair o número/identificação do militar
    militares_duplicados = {}
    for user in usuarios_militar:
        # Extrair a parte após "militar_"
        identificacao = user.username.replace('militar_', '')
        if identificacao not in militares_duplicados:
            militares_duplicados[identificacao] = []
        militares_duplicados[identificacao].append(user)
    
    # Filtrar apenas identificações com mais de um usuário
    militares_com_duplicados = {id: users for id, users in militares_duplicados.items() if len(users) > 1}
    
    print(f"Militares com usuários duplicados: {len(militares_com_duplicados)}")
    
    if militares_com_duplicados:
        for id_militar, users in list(militares_com_duplicados.items())[:5]:
            print(f"  militar_{id_militar}: {len(users)} usuários")
    
    return militares_com_duplicados

def verificar_duplicacao_por_email():
    """
    Verifica duplicação por email
    """
    print("\n=== VERIFICAÇÃO POR EMAIL ===")
    
    # Usuários com email
    usuarios_com_email = User.objects.exclude(email='')
    
    # Agrupar por email
    emails_duplicados = {}
    for user in usuarios_com_email:
        email = user.email.lower().strip()
        if email not in emails_duplicados:
            emails_duplicados[email] = []
        emails_duplicados[email].append(user)
    
    # Filtrar apenas emails com mais de um usuário
    emails_com_duplicados = {email: users for email, users in emails_duplicados.items() if len(users) > 1}
    
    print(f"Emails com usuários duplicados: {len(emails_com_duplicados)}")
    
    if emails_com_duplicados:
        for email, users in list(emails_com_duplicados.items())[:5]:
            print(f"  {email}: {len(users)} usuários")
    
    return emails_com_duplicados

def verificar_vinculacao_militares():
    """
    Verifica a vinculação dos militares com usuários
    """
    print("\n=== VERIFICAÇÃO DE VINCULAÇÃO MILITARES ===")
    
    total_militares = Militar.objects.count()
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    militares_sem_usuario = Militar.objects.filter(user__isnull=True).count()
    
    print(f"Total de militares: {total_militares}")
    print(f"Militares com usuário: {militares_com_usuario}")
    print(f"Militares sem usuário: {militares_sem_usuario}")
    
    # Verificar militares com múltiplos usuários
    militares_multiplos_usuarios = []
    for militar in Militar.objects.all():
        if militar.user:
            # Verificar se há outros usuários com o mesmo CPF
            outros_usuarios = User.objects.filter(username=militar.cpf).exclude(id=militar.user.id)
            if outros_usuarios.exists():
                militares_multiplos_usuarios.append({
                    'militar': militar,
                    'usuario_vinculado': militar.user,
                    'outros_usuarios': outros_usuarios
                })
    
    print(f"Militares com múltiplos usuários: {len(militares_multiplos_usuarios)}")
    
    if militares_multiplos_usuarios:
        for caso in militares_multiplos_usuarios[:3]:
            militar = caso['militar']
            print(f"  Militar: {militar.nome_completo} (CPF: {militar.cpf})")
            print(f"    Usuário vinculado: {caso['usuario_vinculado'].username}")
            print(f"    Outros usuários: {[u.username for u in caso['outros_usuarios']]}")
    
    return militares_multiplos_usuarios

def verificar_usuarios_por_tipo():
    """
    Verifica usuários por tipo
    """
    print("\n=== VERIFICAÇÃO POR TIPO DE USUÁRIO ===")
    
    total_usuarios = User.objects.count()
    
    # Usuários CPF (formato padrão)
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$').count()
    
    # Usuários militar_XXXXXX
    usuarios_militar = User.objects.filter(username__startswith='militar_').count()
    
    # Usuários administrativos
    usuarios_admin = User.objects.exclude(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$').exclude(username__startswith='militar_').count()
    
    print(f"Total de usuários: {total_usuarios}")
    print(f"Usuários CPF (formato padrão): {usuarios_cpf}")
    print(f"Usuários militar_XXXXXX: {usuarios_militar}")
    print(f"Usuários administrativos: {usuarios_admin}")
    
    # Verificar se há CPFs em formato diferente
    usuarios_cpf_outros_formatos = User.objects.filter(username__regex=r'^\d+$').exclude(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$').count()
    print(f"Usuários CPF (outros formatos): {usuarios_cpf_outros_formatos}")

if __name__ == "__main__":
    # Verificar duplicação por CPF
    cpfs_duplicados = verificar_duplicacao_por_cpf()
    
    # Verificar duplicação por padrão militar
    militares_duplicados = verificar_duplicacao_por_padrao_militar()
    
    # Verificar duplicação por email
    emails_duplicados = verificar_duplicacao_por_email()
    
    # Verificar vinculação de militares
    militares_multiplos_usuarios = verificar_vinculacao_militares()
    
    # Verificar usuários por tipo
    verificar_usuarios_por_tipo()
    
    # Resumo
    print("\n=== RESUMO ===")
    total_duplicados = len(cpfs_duplicados) + len(militares_duplicados) + len(emails_duplicados) + len(militares_multiplos_usuarios)
    print(f"Total de tipos de duplicação encontrados: {total_duplicados}")
    
    if total_duplicados == 0:
        print("✅ Nenhuma duplicação encontrada!")
    else:
        print("⚠️  Duplicações encontradas - verificar detalhes acima") 