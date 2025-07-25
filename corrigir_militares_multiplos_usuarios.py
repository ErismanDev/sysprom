#!/usr/bin/env python
"""
Script para corrigir militares que têm múltiplos usuários
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def verificar_militares_multiplos_usuarios():
    """
    Verifica militares com múltiplos usuários
    """
    print("=== VERIFICANDO MILITARES COM MÚLTIPLOS USUÁRIOS ===")
    
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
    
    print(f"Militares com múltiplos usuários encontrados: {len(militares_multiplos_usuarios)}")
    
    return militares_multiplos_usuarios

def mostrar_detalhes_duplicacao(militares_multiplos_usuarios):
    """
    Mostra detalhes da duplicação
    """
    print("\n=== DETALHES DA DUPLICAÇÃO ===")
    
    for i, caso in enumerate(militares_multiplos_usuarios, 1):
        militar = caso['militar']
        usuario_vinculado = caso['usuario_vinculado']
        outros_usuarios = caso['outros_usuarios']
        
        print(f"\n{i}. Militar: {militar.nome_completo}")
        print(f"   CPF: {militar.cpf}")
        print(f"   Matrícula: {militar.matricula}")
        print(f"   Usuário vinculado: {usuario_vinculado.username} (ID: {usuario_vinculado.id})")
        print(f"   Outros usuários ({outros_usuarios.count()}):")
        
        for user in outros_usuarios:
            print(f"     - {user.username} (ID: {user.id}) - Email: {user.email}")

def corrigir_militares_multiplos_usuarios(militares_multiplos_usuarios):
    """
    Corrige militares com múltiplos usuários
    """
    print(f"\n=== CORRIGINDO {len(militares_multiplos_usuarios)} MILITARES ===")
    
    usuarios_removidos = 0
    
    for caso in militares_multiplos_usuarios:
        militar = caso['militar']
        usuario_vinculado = caso['usuario_vinculado']
        outros_usuarios = caso['outros_usuarios']
        
        print(f"\nMilitar: {militar.nome_completo} (CPF: {militar.cpf})")
        print(f"  Mantendo usuário vinculado: {usuario_vinculado.username}")
        
        # Remover os outros usuários
        for user in outros_usuarios:
            print(f"  Removendo usuário duplicado: {user.username}")
            user.delete()
            usuarios_removidos += 1
    
    print(f"\nTotal de usuários removidos: {usuarios_removidos}")

def verificar_resultado():
    """
    Verifica o resultado após a correção
    """
    print("\n=== VERIFICAÇÃO FINAL ===")
    
    total_usuarios = User.objects.count()
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$').count()
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    
    print(f"Total de usuários: {total_usuarios}")
    print(f"Usuários CPF: {usuarios_cpf}")
    print(f"Militares com usuário: {militares_com_usuario}")
    
    # Verificar se ainda há militares com múltiplos usuários
    militares_multiplos_usuarios = verificar_militares_multiplos_usuarios()
    if militares_multiplos_usuarios:
        print(f"⚠️  Ainda há {len(militares_multiplos_usuarios)} militares com múltiplos usuários")
    else:
        print("✅ Nenhum militar com múltiplos usuários encontrado!")

if __name__ == "__main__":
    # Verificar militares com múltiplos usuários
    militares_multiplos_usuarios = verificar_militares_multiplos_usuarios()
    
    if not militares_multiplos_usuarios:
        print("Nenhum militar com múltiplos usuários encontrado.")
        exit()
    
    # Mostrar detalhes
    mostrar_detalhes_duplicacao(militares_multiplos_usuarios)
    
    # Perguntar se deseja corrigir
    resposta = input(f"\nDeseja corrigir {len(militares_multiplos_usuarios)} militares com múltiplos usuários? (s/n): ").lower()
    if resposta == 's':
        corrigir_militares_multiplos_usuarios(militares_multiplos_usuarios)
        verificar_resultado()
    else:
        print("Correção cancelada.") 