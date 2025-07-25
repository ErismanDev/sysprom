#!/usr/bin/env python
"""
Script para corrigir usernames dos usuários para usar o CPF dos militares
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def verificar_usuarios_atual():
    """Verifica como estão os usuários atualmente"""
    
    print("🔍 VERIFICANDO USUÁRIOS ATUALMENTE")
    print("=" * 50)
    
    usuarios = User.objects.all()
    print(f"Total de usuários: {usuarios.count()}")
    
    # Verificar primeiros 10 usuários
    print("\n👥 Primeiros 10 usuários:")
    for i, user in enumerate(usuarios[:10], 1):
        militar = Militar.objects.filter(user=user).first()
        if militar:
            print(f"{i}. Usuário: {user.username} | Militar: {militar.nome_completo} | CPF: {militar.cpf}")
        else:
            print(f"{i}. Usuário: {user.username} | Sem militar vinculado")
    
    # Verificar padrão dos usernames
    print("\n📊 Análise dos usernames:")
    usernames_com_militar = []
    usernames_sem_militar = []
    
    for user in usuarios:
        militar = Militar.objects.filter(user=user).first()
        if militar:
            usernames_com_militar.append(user.username)
        else:
            usernames_sem_militar.append(user.username)
    
    print(f"Usuários com militar: {len(usernames_com_militar)}")
    print(f"Usuários sem militar: {len(usernames_sem_militar)}")
    
    # Mostrar alguns exemplos de usernames com militar
    print("\n🔍 Exemplos de usernames com militar:")
    for username in usernames_com_militar[:5]:
        print(f"  - {username}")
    
    return usernames_com_militar, usernames_sem_militar

def corrigir_usernames_para_cpf():
    """Corrige os usernames para usar o CPF dos militares"""
    
    print("\n🔧 CORRIGINDO USERNAMES PARA CPF")
    print("=" * 50)
    
    militares_com_usuario = Militar.objects.filter(user__isnull=False)
    print(f"Militares com usuário: {militares_com_usuario.count()}")
    
    corrigidos = 0
    erros = 0
    
    for militar in militares_com_usuario:
        try:
            cpf = militar.cpf
            
            if not cpf:
                print(f"  ⚠️ Militar {militar.nome_completo} sem CPF")
                continue
            
            # Limpar CPF (remover pontos e traços)
            cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
            
            if len(cpf_limpo) != 11:
                print(f"  ⚠️ CPF inválido para {militar.nome_completo}: {cpf_limpo}")
                continue
            
            usuario = militar.user
            
            # Verificar se o username já é o CPF
            if usuario.username == cpf_limpo:
                print(f"  ✅ {militar.nome_completo} já tem username correto: {cpf_limpo}")
                continue
            
            # Verificar se já existe usuário com este CPF
            if User.objects.filter(username=cpf_limpo).exclude(id=usuario.id).exists():
                print(f"  ❌ CPF {cpf_limpo} já existe para outro usuário")
                erros += 1
                continue
            
            # Salvar username antigo para log
            username_antigo = usuario.username
            
            # Atualizar username
            usuario.username = cpf_limpo
            usuario.save()
            
            print(f"  ✅ {militar.nome_completo}: {username_antigo} → {cpf_limpo}")
            corrigidos += 1
            
        except Exception as e:
            print(f"  ❌ Erro ao corrigir {militar.nome_completo}: {e}")
            erros += 1
    
    print(f"\n📊 RESUMO:")
    print(f"  ✅ Corrigidos: {corrigidos}")
    print(f"  ❌ Erros: {erros}")
    
    return corrigidos, erros

def verificar_resultado_final():
    """Verifica o resultado final após a correção"""
    
    print("\n📊 VERIFICANDO RESULTADO FINAL")
    print("=" * 50)
    
    militares_com_usuario = Militar.objects.filter(user__isnull=False)
    
    print("👥 Exemplos de militares com CPF como username:")
    for i, militar in enumerate(militares_com_usuario[:10], 1):
        cpf_limpo = ''.join(filter(str.isdigit, str(militar.cpf)))
        print(f"{i}. {militar.nome_completo} | Username: {militar.user.username} | CPF: {cpf_limpo}")
    
    # Verificar se todos os usernames são CPFs válidos
    usernames_cpf = 0
    usernames_outros = 0
    
    for militar in militares_com_usuario:
        cpf_limpo = ''.join(filter(str.isdigit, str(militar.cpf)))
        if militar.user.username == cpf_limpo:
            usernames_cpf += 1
        else:
            usernames_outros += 1
            print(f"  ⚠️ {militar.nome_completo}: username {militar.user.username} ≠ CPF {cpf_limpo}")
    
    print(f"\n📊 Estatísticas finais:")
    print(f"  ✅ Usernames corretos (CPF): {usernames_cpf}")
    print(f"  ⚠️ Usernames incorretos: {usernames_outros}")
    
    return usernames_cpf, usernames_outros

def mostrar_instrucoes_login():
    """Mostra instruções de login"""
    
    print("\n🔑 INSTRUÇÕES DE LOGIN")
    print("=" * 50)
    print("Agora os militares podem fazer login usando:")
    print("  👤 Usuário: CPF (apenas números, sem pontos/traços)")
    print("  🔑 Senha: militar123")
    print()
    print("Exemplos:")
    print("  - CPF: 123.456.789-01 → Usuário: 12345678901")
    print("  - CPF: 987.654.321-00 → Usuário: 98765432100")
    print()
    print("Superusuário admin:")
    print("  👤 Usuário: admin")
    print("  🔑 Senha: admin123")

if __name__ == "__main__":
    print("🚀 Iniciando correção de usernames para CPF")
    print("=" * 60)
    
    # Verificar situação atual
    usernames_com_militar, usernames_sem_militar = verificar_usuarios_atual()
    
    # Corrigir usernames
    corrigidos, erros = corrigir_usernames_para_cpf()
    
    # Verificar resultado
    usernames_cpf, usernames_outros = verificar_resultado_final()
    
    # Mostrar instruções
    mostrar_instrucoes_login()
    
    print(f"\n🎉 Processo concluído!")
    print(f"📊 Resumo:")
    print(f"  - Usernames corrigidos: {corrigidos}")
    print(f"  - Erros: {erros}")
    print(f"  - Usernames corretos: {usernames_cpf}")
    print(f"  - Usernames incorretos: {usernames_outros}") 