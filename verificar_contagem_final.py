#!/usr/bin/env python
"""
Script para verificar e corrigir a contagem final de usuários
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def verificar_contagem_atual():
    """
    Verifica a contagem atual
    """
    print("=== CONTAGEM ATUAL ===")
    
    total_usuarios = User.objects.count()
    total_militares = Militar.objects.count()
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    militares_sem_usuario = Militar.objects.filter(user__isnull=True).count()
    
    print(f"Total de usuários: {total_usuarios}")
    print(f"Total de militares: {total_militares}")
    print(f"Militares com usuário: {militares_com_usuario}")
    print(f"Militares sem usuário: {militares_sem_usuario}")
    
    return total_usuarios, total_militares

def verificar_tipos_usuarios():
    """
    Verifica os tipos de usuários
    """
    print("\n=== TIPOS DE USUÁRIOS ===")
    
    # Usuários CPF (formato padrão)
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$').count()
    
    # Usuários militar_XXXXXX
    usuarios_militar = User.objects.filter(username__startswith='militar_').count()
    
    # Usuários administrativos
    usuarios_admin = User.objects.exclude(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$').exclude(username__startswith='militar_').count()
    
    print(f"Usuários CPF (formato padrão): {usuarios_cpf}")
    print(f"Usuários militar_XXXXXX: {usuarios_militar}")
    print(f"Usuários administrativos: {usuarios_admin}")
    
    # Listar usuários administrativos
    usuarios_admin_list = User.objects.exclude(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$').exclude(username__startswith='militar_')
    print(f"\nUsuários administrativos:")
    for user in usuarios_admin_list:
        print(f"  - {user.username} - {user.email} - Staff: {user.is_staff} - Super: {user.is_superuser}")
    
    return usuarios_cpf, usuarios_militar, usuarios_admin

def calcular_contagem_esperada():
    """
    Calcula a contagem esperada
    """
    print("\n=== CONTAGEM ESPERADA ===")
    
    total_militares = Militar.objects.count()
    usuarios_esperados = total_militares + 1  # +1 para o admin
    
    print(f"Militares: {total_militares}")
    print(f"Admin: 1")
    print(f"Total esperado: {usuarios_esperados}")
    
    return usuarios_esperados

def remover_usuarios_excedentes():
    """
    Remove usuários excedentes, mantendo apenas militares + admin
    """
    print("\n=== REMOVENDO USUÁRIOS EXCEDENTES ===")
    
    total_usuarios = User.objects.count()
    total_militares = Militar.objects.count()
    usuarios_esperados = total_militares + 1
    
    if total_usuarios <= usuarios_esperados:
        print("Nenhum usuário excedente para remover.")
        return
    
    usuarios_para_remover = total_usuarios - usuarios_esperados
    print(f"Removendo {usuarios_para_remover} usuários excedentes...")
    
    # Manter apenas usuários de militares e admin
    usuarios_para_manter = []
    
    # Adicionar usuários de militares
    for militar in Militar.objects.all():
        if militar.user:
            usuarios_para_manter.append(militar.user.id)
    
    # Adicionar admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        usuarios_para_manter.append(admin_user.id)
    
    # Remover usuários não essenciais
    usuarios_removidos = 0
    for user in User.objects.all():
        if user.id not in usuarios_para_manter:
            print(f"  Removendo: {user.username} - {user.email}")
            user.delete()
            usuarios_removidos += 1
    
    print(f"Total de usuários removidos: {usuarios_removidos}")

def verificar_resultado_final():
    """
    Verifica o resultado final
    """
    print("\n=== RESULTADO FINAL ===")
    
    total_usuarios = User.objects.count()
    total_militares = Militar.objects.count()
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    
    print(f"Total de usuários: {total_usuarios}")
    print(f"Total de militares: {total_militares}")
    print(f"Militares com usuário: {militares_com_usuario}")
    
    if total_usuarios == total_militares + 1:
        print("✅ Contagem correta! (militares + admin)")
    else:
        print(f"⚠️  Contagem incorreta. Esperado: {total_militares + 1}, Atual: {total_usuarios}")

if __name__ == "__main__":
    # Verificar contagem atual
    total_usuarios, total_militares = verificar_contagem_atual()
    
    # Verificar tipos de usuários
    usuarios_cpf, usuarios_militar, usuarios_admin = verificar_tipos_usuarios()
    
    # Calcular contagem esperada
    usuarios_esperados = calcular_contagem_esperada()
    
    # Mostrar diferença
    diferenca = total_usuarios - usuarios_esperados
    print(f"\nDiferença: {diferenca} usuários excedentes")
    
    if diferenca > 0:
        resposta = input(f"\nDeseja remover {diferenca} usuários excedentes? (s/n): ").lower()
        if resposta == 's':
            remover_usuarios_excedentes()
            verificar_resultado_final()
        else:
            print("Remoção cancelada.")
    else:
        print("Contagem já está correta.") 