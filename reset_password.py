#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def reset_user_password():
    """Script para redefinir senha de usuário"""
    
    print("🔐 REDEFINIR SENHA DE USUÁRIO")
    print("=" * 40)
    
    # Listar usuários existentes
    users = User.objects.all()
    print(f"\n📋 Usuários existentes ({users.count()}):")
    for i, user in enumerate(users, 1):
        status = "✅ Ativo" if user.is_active else "❌ Inativo"
        print(f"{i}. {user.username} - {user.get_full_name()} ({status})")
    
    # Escolher usuário
    while True:
        try:
            choice = input(f"\nEscolha o número do usuário (1-{len(users)}): ")
            user_index = int(choice) - 1
            if 0 <= user_index < len(users):
                selected_user = users[user_index]
                break
            else:
                print("❌ Número inválido!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    print(f"\n👤 Usuário selecionado: {selected_user.username}")
    print(f"📝 Nome: {selected_user.get_full_name()}")
    print(f"📧 Email: {selected_user.email}")
    
    # Nova senha
    while True:
        new_password = input("\n🔑 Digite a nova senha: ")
        confirm_password = input("🔑 Confirme a nova senha: ")
        
        if new_password == confirm_password:
            if len(new_password) >= 8:
                break
            else:
                print("❌ A senha deve ter pelo menos 8 caracteres!")
        else:
            print("❌ As senhas não coincidem!")
    
    # Aplicar nova senha
    selected_user.set_password(new_password)
    selected_user.save()
    
    print(f"\n✅ Senha alterada com sucesso!")
    print(f"👤 Usuário: {selected_user.username}")
    print(f"🔑 Nova senha: {new_password}")
    print(f"\n🌐 Acesse: http://127.0.0.1:8000/login/")

if __name__ == "__main__":
    reset_user_password() 