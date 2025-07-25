#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    """Script para criar usuário administrador"""
    
    print("👑 CRIAR USUÁRIO ADMINISTRADOR")
    print("=" * 40)
    
    # Dados do admin
    username = input("👤 Username (ex: admin): ").strip()
    if not username:
        username = "admin"
    
    first_name = input("📝 Nome: ").strip()
    if not first_name:
        first_name = "Administrador"
    
    last_name = input("📝 Sobrenome: ").strip()
    if not last_name:
        last_name = "Sistema"
    
    email = input("📧 Email: ").strip()
    if not email:
        email = "admin@cbmepi.gov.br"
    
    # Senha
    while True:
        password = input("🔑 Senha: ")
        confirm_password = input("🔑 Confirme a senha: ")
        
        if password == confirm_password:
            if len(password) >= 8:
                break
            else:
                print("❌ A senha deve ter pelo menos 8 caracteres!")
        else:
            print("❌ As senhas não coincidem!")
    
    # Verificar se usuário já existe
    if User.objects.filter(username=username).exists():
        print(f"\n⚠️  Usuário '{username}' já existe!")
        choice = input("Deseja sobrescrever? (s/n): ").lower()
        if choice != 's':
            print("❌ Operação cancelada!")
            return
        
        # Atualizar usuário existente
        user = User.objects.get(username=username)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        
        print(f"\n✅ Usuário '{username}' atualizado com sucesso!")
    else:
        # Criar novo usuário
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
    
    print(f"\n📋 DETALHES DO USUÁRIO:")
    print(f"👤 Username: {user.username}")
    print(f"📝 Nome: {user.get_full_name()}")
    print(f"📧 Email: {user.email}")
    print(f"🔑 Senha: {password}")
    print(f"👑 Admin: {'✅ Sim' if user.is_superuser else '❌ Não'}")
    print(f"🔧 Staff: {'✅ Sim' if user.is_staff else '❌ Não'}")
    print(f"✅ Ativo: {'✅ Sim' if user.is_active else '❌ Não'}")
    
    print(f"\n🌐 Acesse:")
    print(f"   • Sistema: http://127.0.0.1:8000/login/")
    print(f"   • Admin: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    create_admin_user() 