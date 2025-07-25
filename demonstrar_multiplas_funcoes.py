#!/usr/bin/env python
"""
Script para demonstrar o sistema de múltiplas funções
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao
from datetime import date

def demonstrar_multiplas_funcoes():
    """Demonstra como o sistema funciona com múltiplas funções"""
    
    print("=== SISTEMA DE MÚLTIPLAS FUNÇÕES ===")
    print("=" * 50)
    
    # 1. Verificar todos os usuários com múltiplas funções
    print("👥 USUÁRIOS COM MÚLTIPLAS FUNÇÕES:")
    usuarios_multiplas_funcoes = []
    
    for user in User.objects.filter(is_active=True):
        funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
        if funcoes.count() > 1:
            usuarios_multiplas_funcoes.append({
                'usuario': user,
                'funcoes': funcoes
            })
    
    if usuarios_multiplas_funcoes:
        for item in usuarios_multiplas_funcoes:
            user = item['usuario']
            funcoes = item['funcoes']
            print(f"\n📋 {user.get_full_name()} ({user.username}):")
            for funcao in funcoes:
                print(f"   - {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
    else:
        print("   Nenhum usuário com múltiplas funções encontrado")
    
    # 2. Verificar usuários com função única
    print(f"\n👤 USUÁRIOS COM FUNÇÃO ÚNICA:")
    usuarios_funcao_unica = []
    
    for user in User.objects.filter(is_active=True):
        funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
        if funcoes.count() == 1:
            usuarios_funcao_unica.append({
                'usuario': user,
                'funcao': funcoes.first()
            })
    
    for item in usuarios_funcao_unica:
        user = item['usuario']
        funcao = item['funcao']
        print(f"   - {user.get_full_name()} ({user.username}): {funcao.cargo_funcao.nome}")
    
    # 3. Verificar usuários sem funções
    print(f"\n❌ USUÁRIOS SEM FUNÇÕES:")
    usuarios_sem_funcoes = []
    
    for user in User.objects.filter(is_active=True):
        funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
        if funcoes.count() == 0:
            usuarios_sem_funcoes.append(user)
    
    for user in usuarios_sem_funcoes:
        print(f"   - {user.get_full_name()} ({user.username})")
    
    # 4. Estatísticas gerais
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    total_usuarios = User.objects.filter(is_active=True).count()
    total_funcoes = UsuarioFuncao.objects.filter(status='ATIVO').count()
    
    print(f"   - Total de usuários ativos: {total_usuarios}")
    print(f"   - Total de funções ativas: {total_funcoes}")
    print(f"   - Usuários com múltiplas funções: {len(usuarios_multiplas_funcoes)}")
    print(f"   - Usuários com função única: {len(usuarios_funcao_unica)}")
    print(f"   - Usuários sem funções: {len(usuarios_sem_funcoes)}")
    
    # 5. Demonstrar fluxo de login
    print(f"\n🔄 FLUXO DE LOGIN:")
    print("   1. Usuário faz login com credenciais")
    print("   2. Sistema verifica funções ativas do usuário")
    print("   3. Se apenas uma função: seleção automática")
    print("   4. Se múltiplas funções: redireciona para seleção")
    print("   5. Se nenhuma função: erro e logout")
    print("   6. Após seleção: acesso ao sistema com função ativa")
    
    # 6. Demonstrar troca de função
    print(f"\n🔄 TROCA DE FUNÇÃO:")
    print("   - Usuário pode trocar de função durante a sessão")
    print("   - Funções ficam disponíveis na sessão")
    print("   - Middleware verifica função ativa em cada requisição")
    print("   - Se função não existe mais: troca automática ou logout")
    
    # 7. Demonstrar controle de acesso
    print(f"\n🔒 CONTROLE DE ACESSO:")
    print("   - Baseado na função ativa do usuário")
    print("   - Funções especiais têm acesso total")
    print("   - Funções de comissão têm acesso limitado")
    print("   - Middleware aplica restrições automaticamente")

if __name__ == '__main__':
    demonstrar_multiplas_funcoes() 