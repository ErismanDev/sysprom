#!/usr/bin/env python
"""
Script para corrigir a contagem de usuários no dashboard
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
    Verifica a contagem atual de usuários
    """
    print("=== CONTAGEM ATUAL ===")
    
    total_usuarios = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    
    print(f"Total de usuários (User.objects.count()): {total_usuarios}")
    print(f"Usuários ativos: {usuarios_ativos}")
    
    return total_usuarios, usuarios_ativos

def calcular_contagem_correta():
    """
    Calcula a contagem correta de usuários (sem duplicados)
    """
    print("\n=== CONTAGEM CORRETA ===")
    
    # Usuários únicos por CPF (formato padrão)
    usuarios_cpf_unicos = User.objects.filter(
        username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
    ).values('username').distinct().count()
    
    # Usuários administrativos únicos
    usuarios_admin = User.objects.exclude(
        username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
    ).exclude(username__startswith='militar_')
    
    # Filtrar usuários administrativos essenciais
    usuarios_essenciais = [
        'admin', 'superusuario', 'erisman', 'diretor_gestao',
        'presidente_cpo', 'presidente_cpp', 'membro_nato_cpo', 'membro_nato_cpp',
        'membro_efetivo_cpo', 'membro_efetivo_cpp', 'suplente_cpo', 'suplente_cpp',
        'digitador', 'chefe_promocoes'
    ]
    
    usuarios_admin_unicos = 0
    for username in usuarios_essenciais:
        if User.objects.filter(username=username).exists():
            usuarios_admin_unicos += 1
    
    # Usuários militar_XXXXXX únicos (sem duplicados)
    usuarios_militar_unicos = User.objects.filter(
        username__startswith='militar_'
    ).values('username').distinct().count()
    
    total_correto = usuarios_cpf_unicos + usuarios_admin_unicos + usuarios_militar_unicos
    
    print(f"Usuários CPF únicos: {usuarios_cpf_unicos}")
    print(f"Usuários administrativos essenciais: {usuarios_admin_unicos}")
    print(f"Usuários militar_XXXXXX únicos: {usuarios_militar_unicos}")
    print(f"Total correto: {total_correto}")
    
    return total_correto

def corrigir_contagem_dashboard():
    """
    Corrige a contagem removendo usuários duplicados
    """
    print("\n=== CORRIGINDO CONTAGEM ===")
    
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
        print("Removendo usuários duplicados...")
        usuarios_removidos = 0
        
        for caso in militares_multiplos_usuarios:
            militar = caso['militar']
            outros_usuarios = caso['outros_usuarios']
            
            print(f"  Militar: {militar.nome_completo} (CPF: {militar.cpf})")
            
            for user in outros_usuarios:
                print(f"    Removendo: {user.username}")
                user.delete()
                usuarios_removidos += 1
        
        print(f"Total de usuários removidos: {usuarios_removidos}")
    else:
        print("Nenhum usuário duplicado encontrado.")

def verificar_resultado():
    """
    Verifica o resultado após a correção
    """
    print("\n=== RESULTADO FINAL ===")
    
    total_usuarios = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    
    print(f"Total de usuários após correção: {total_usuarios}")
    print(f"Usuários ativos: {usuarios_ativos}")
    
    # Verificar se ainda há duplicados
    militares_multiplos_usuarios = []
    for militar in Militar.objects.all():
        if militar.user:
            outros_usuarios = User.objects.filter(username=militar.cpf).exclude(id=militar.user.id)
            if outros_usuarios.exists():
                militares_multiplos_usuarios.append(militar)
    
    if militares_multiplos_usuarios:
        print(f"⚠️  Ainda há {len(militares_multiplos_usuarios)} militares com múltiplos usuários")
    else:
        print("✅ Nenhum militar com múltiplos usuários encontrado!")

if __name__ == "__main__":
    # Verificar contagem atual
    total_atual, ativos_atual = verificar_contagem_atual()
    
    # Calcular contagem correta
    total_correto = calcular_contagem_correta()
    
    # Mostrar diferença
    diferenca = total_atual - total_correto
    print(f"\nDiferença: {diferenca} usuários duplicados")
    
    if diferenca > 0:
        resposta = input(f"\nDeseja corrigir removendo {diferenca} usuários duplicados? (s/n): ").lower()
        if resposta == 's':
            corrigir_contagem_dashboard()
            verificar_resultado()
        else:
            print("Correção cancelada.")
    else:
        print("Nenhuma correção necessária.") 