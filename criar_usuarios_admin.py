#!/usr/bin/env python
"""
Script para criar outros usuários admin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from militares.models import UsuarioFuncao, CargoFuncao, PermissaoFuncao

def criar_usuario_admin():
    """Cria um novo usuário admin"""
    
    print("👑 CRIADOR DE USUÁRIOS ADMIN")
    print("=" * 50)
    
    # Solicitar dados do usuário
    print("\n📝 DADOS DO USUÁRIO:")
    username = input("Username: ").strip()
    
    if not username:
        print("❌ Username é obrigatório!")
        return
    
    # Verificar se usuário já existe
    if User.objects.filter(username=username).exists():
        print(f"❌ Usuário '{username}' já existe!")
        return
    
    # Dados opcionais
    first_name = input("Nome: ").strip()
    last_name = input("Sobrenome: ").strip()
    email = input("Email: ").strip()
    
    # Senha
    password = input("Senha: ").strip()
    if not password:
        print("❌ Senha é obrigatória!")
        return
    
    confirm_password = input("Confirmar senha: ").strip()
    if password != confirm_password:
        print("❌ Senhas não coincidem!")
        return
    
    # Criar usuário
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        print(f"\n✅ Usuário '{username}' criado com sucesso!")
        
        # Configurar permissões
        configurar_permissoes_admin(user)
        
        # Configurar função de administrador
        configurar_funcao_admin(user)
        
        print(f"\n🎉 Usuário '{username}' configurado como ADMIN TOTAL!")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")

def configurar_permissoes_admin(user):
    """Configura todas as permissões para um usuário admin"""
    
    print(f"\n🔑 CONFIGURANDO PERMISSÕES PARA {user.username}:")
    
    # 1. Adicionar todas as permissões Django
    todas_permissoes = Permission.objects.all()
    user.user_permissions.set(todas_permissoes)
    print(f"   ✅ {todas_permissoes.count()} permissões Django adicionadas")
    
    # 2. Adicionar a todos os grupos
    todos_grupos = Group.objects.all()
    for grupo in todos_grupos:
        user.groups.add(grupo)
    print(f"   ✅ Adicionado a {todos_grupos.count()} grupos")

def configurar_funcao_admin(user):
    """Configura função de administrador para um usuário"""
    
    print(f"\n🎯 CONFIGURANDO FUNÇÃO DE ADMINISTRADOR:")
    
    # Verificar/criar cargo de administrador
    cargo_admin, created = CargoFuncao.objects.get_or_create(
        nome='Administrador',
        defaults={
            'descricao': 'Administrador do sistema com acesso total',
            'ativo': True
        }
    )
    
    if created:
        print("   ✅ Cargo 'Administrador' criado")
        
        # Adicionar todas as permissões ao cargo
        modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
        acessos = [choice[0] for choice in PermissaoFuncao.ACESSOS_CHOICES]
        
        for modulo in modulos:
            for acesso in acessos:
                PermissaoFuncao.objects.create(
                    cargo_funcao=cargo_admin,
                    modulo=modulo,
                    acesso=acesso,
                    ativo=True
                )
        print(f"   ✅ {len(modulos) * len(acessos)} permissões adicionadas ao cargo")
    else:
        print("   ℹ️ Cargo 'Administrador' já existe")
    
    # Atribuir função ao usuário
    funcao_admin, created = UsuarioFuncao.objects.get_or_create(
        usuario=user,
        cargo_funcao=cargo_admin,
        defaults={
            'tipo_funcao': 'EFETIVA',
            'status': 'ATIVO',
            'data_inicio': '2024-01-01'
        }
    )
    
    if created:
        print("   ✅ Função de administrador atribuída")
    else:
        print("   ℹ️ Função de administrador já existe")

def listar_usuarios_admin():
    """Lista todos os usuários admin"""
    
    print("\n📋 USUÁRIOS ADMIN EXISTENTES:")
    print("=" * 50)
    
    # Buscar usuários superusuários
    admins = User.objects.filter(is_superuser=True).order_by('username')
    
    if admins.exists():
        for admin in admins:
            print(f"👤 {admin.username}")
            print(f"   Nome: {admin.get_full_name() or 'N/A'}")
            print(f"   Email: {admin.email or 'N/A'}")
            print(f"   Ativo: {admin.is_active}")
            print(f"   Staff: {admin.is_staff}")
            print(f"   Superusuário: {admin.is_superuser}")
            
            # Verificar função
            funcao = UsuarioFuncao.objects.filter(
                usuario=admin,
                status='ATIVO'
            ).first()
            
            if funcao:
                print(f"   Função: {funcao.cargo_funcao.nome}")
            else:
                print(f"   Função: Nenhuma função ativa")
            
            print()
    else:
        print("❌ Nenhum usuário admin encontrado!")

def remover_usuario_admin():
    """Remove um usuário admin"""
    
    print("\n🗑️ REMOVER USUÁRIO ADMIN:")
    print("=" * 50)
    
    username = input("Username do usuário a remover: ").strip()
    
    if not username:
        print("❌ Username é obrigatório!")
        return
    
    try:
        user = User.objects.get(username=username)
        
        if not user.is_superuser:
            print(f"❌ Usuário '{username}' não é admin!")
            return
        
        confirmacao = input(f"⚠️ Tem certeza que deseja remover '{username}'? (s/n): ").strip().lower()
        
        if confirmacao == 's':
            user.delete()
            print(f"✅ Usuário '{username}' removido com sucesso!")
        else:
            print("❌ Operação cancelada!")
            
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado!")

def menu_principal():
    """Menu principal"""
    
    while True:
        print("\n" + "=" * 60)
        print("👑 GERENCIADOR DE USUÁRIOS ADMIN")
        print("=" * 60)
        print("1. Criar novo usuário admin")
        print("2. Listar usuários admin")
        print("3. Remover usuário admin")
        print("4. Sair")
        print("=" * 60)
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            criar_usuario_admin()
        elif opcao == "2":
            listar_usuarios_admin()
        elif opcao == "3":
            remover_usuario_admin()
        elif opcao == "4":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    menu_principal() 