#!/usr/bin/env python
"""
Script para identificar e corrigir usuários duplicados
onde um está vinculado ao militar e o outro não
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

def verificar_usuarios_duplicados():
    """
    Verifica usuários duplicados por CPF
    """
    print("=== VERIFICANDO USUÁRIOS DUPLICADOS ===")
    
    # Usuários que são CPFs
    usuarios_cpf = User.objects.filter(username__regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    
    # Agrupar por CPF e contar
    cpfs_duplicados = {}
    for user in usuarios_cpf:
        cpf = user.username
        if cpf not in cpfs_duplicados:
            cpfs_duplicados[cpf] = []
        cpfs_duplicados[cpf].append(user)
    
    # Filtrar apenas CPFs com mais de um usuário
    cpfs_com_duplicados = {cpf: users for cpf, users in cpfs_duplicados.items() if len(users) > 1}
    
    print(f"CPFs com usuários duplicados: {len(cpfs_com_duplicados)}")
    
    return cpfs_com_duplicados

def analisar_vinculacao_militar(cpfs_com_duplicados):
    """
    Analisa a vinculação dos usuários duplicados com militares
    """
    print("\n=== ANÁLISE DE VINCULAÇÃO COM MILITARES ===")
    
    casos_para_corrigir = []
    
    for cpf, usuarios in cpfs_com_duplicados.items():
        print(f"\nCPF: {cpf}")
        print(f"  Usuários encontrados: {len(usuarios)}")
        
        # Verificar se existe militar para este CPF
        militar = Militar.objects.filter(cpf=cpf).first()
        
        if militar:
            print(f"  Militar encontrado: {militar.nome} (ID: {militar.id})")
            
            # Verificar qual usuário está vinculado
            usuarios_vinculados = []
            usuarios_nao_vinculados = []
            
            for user in usuarios:
                if hasattr(militar, 'user') and militar.user == user:
                    usuarios_vinculados.append(user)
                else:
                    usuarios_nao_vinculados.append(user)
            
            print(f"  Usuários vinculados: {len(usuarios_vinculados)}")
            print(f"  Usuários não vinculados: {len(usuarios_nao_vinculados)}")
            
            if usuarios_vinculados and usuarios_nao_vinculados:
                casos_para_corrigir.append({
                    'cpf': cpf,
                    'militar': militar,
                    'usuarios_vinculados': usuarios_vinculados,
                    'usuarios_nao_vinculados': usuarios_nao_vinculados
                })
                
                print("  ⚠️  CASO PARA CORRIGIR: Um vinculado, outros não")
            elif not usuarios_vinculados and usuarios_nao_vinculados:
                print("  ⚠️  CASO PARA CORRIGIR: Nenhum vinculado")
                casos_para_corrigir.append({
                    'cpf': cpf,
                    'militar': militar,
                    'usuarios_vinculados': [],
                    'usuarios_nao_vinculados': usuarios_nao_vinculados
                })
        else:
            print(f"  ❌ Nenhum militar encontrado para este CPF")
    
    return casos_para_corrigir

def corrigir_usuarios_duplicados(casos_para_corrigir):
    """
    Corrige os usuários duplicados
    """
    print(f"\n=== CORRIGINDO {len(casos_para_corrigir)} CASOS ===")
    
    usuarios_removidos = 0
    
    for caso in casos_para_corrigir:
        cpf = caso['cpf']
        militar = caso['militar']
        usuarios_vinculados = caso['usuarios_vinculados']
        usuarios_nao_vinculados = caso['usuarios_nao_vinculados']
        
        print(f"\nCPF: {cpf}")
        
        if usuarios_vinculados:
            # Manter o usuário vinculado, remover os outros
            usuario_manter = usuarios_vinculados[0]
            print(f"  Mantendo usuário vinculado: {usuario_manter.username}")
            
            for user in usuarios_nao_vinculados:
                print(f"  Removendo usuário não vinculado: {user.username}")
                user.delete()
                usuarios_removidos += 1
        else:
            # Nenhum vinculado, manter o mais antigo e vincular
            usuarios_ordenados = sorted(usuarios_nao_vinculados, key=lambda u: u.date_joined)
            usuario_manter = usuarios_ordenados[0]
            usuarios_remover = usuarios_ordenados[1:]
            
            print(f"  Mantendo usuário mais antigo: {usuario_manter.username}")
            
            # Vincular o militar ao usuário mantido
            militar.user = usuario_manter
            militar.save()
            print(f"  Vinculando militar {militar.nome} ao usuário {usuario_manter.username}")
            
            # Remover os outros usuários
            for user in usuarios_remover:
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
    
    # Verificar se ainda há duplicados
    cpfs_duplicados = verificar_usuarios_duplicados()
    if cpfs_duplicados:
        print(f"⚠️  Ainda há {len(cpfs_duplicados)} CPFs com duplicados")
    else:
        print("✅ Nenhum CPF duplicado encontrado!")

if __name__ == "__main__":
    # Verificar usuários duplicados
    cpfs_com_duplicados = verificar_usuarios_duplicados()
    
    if not cpfs_com_duplicados:
        print("Nenhum usuário duplicado encontrado.")
        exit()
    
    # Analisar vinculação com militares
    casos_para_corrigir = analisar_vinculacao_militar(cpfs_com_duplicados)
    
    if not casos_para_corrigir:
        print("Nenhum caso para corrigir encontrado.")
        exit()
    
    # Perguntar se deseja corrigir
    resposta = input(f"\nDeseja corrigir {len(casos_para_corrigir)} casos de usuários duplicados? (s/n): ").lower()
    if resposta == 's':
        corrigir_usuarios_duplicados(casos_para_corrigir)
        verificar_resultado()
    else:
        print("Correção cancelada.") 