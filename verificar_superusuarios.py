#!/usr/bin/env python
"""
Script para verificar superusuários e suas credenciais
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def verificar_superusuarios():
    """
    Verifica todos os superusuários do sistema
    """
    print("🔍 Verificando superusuários do sistema...")
    print("=" * 60)
    
    # Buscar todos os superusuários
    superusuarios = User.objects.filter(is_superuser=True)
    
    print(f"📊 Total de superusuários encontrados: {superusuarios.count()}")
    print()
    
    if superusuarios.exists():
        print("👑 **SUPERUSUÁRIOS DO SISTEMA:**")
        print()
        
        for i, usuario in enumerate(superusuarios, 1):
            print(f"**{i}. {usuario.username.upper()}**")
            print(f"   • **Username**: `{usuario.username}`")
            print(f"   • **Nome completo**: {usuario.get_full_name()}")
            print(f"   • **Email**: {usuario.email}")
            print(f"   • **Status**: {'✅ Ativo' if usuario.is_active else '❌ Inativo'}")
            print(f"   • **Staff**: {'✅ Sim' if usuario.is_staff else '❌ Não'}")
            print(f"   • **Data de criação**: {usuario.date_joined.strftime('%d/%m/%Y %H:%M')}")
            print(f"   • **Último login**: {usuario.last_login.strftime('%d/%m/%Y %H:%M') if usuario.last_login else 'Nunca'}")
            
            # Verificar se tem militar vinculado
            if hasattr(usuario, 'militar') and usuario.militar:
                print(f"   • **Militar vinculado**: {usuario.militar.nome_completo}")
            else:
                print(f"   • **Militar vinculado**: Nenhum")
            
            print()
    
    else:
        print("❌ Nenhum superusuário encontrado no sistema!")
    
    # Verificar também usuários staff (que podem ter privilégios administrativos)
    usuarios_staff = User.objects.filter(is_staff=True, is_superuser=False)
    
    if usuarios_staff.exists():
        print("👥 **USUÁRIOS STAFF (ADMINISTRADORES):**")
        print()
        
        for i, usuario in enumerate(usuarios_staff, 1):
            print(f"**{i}. {usuario.username.upper()}**")
            print(f"   • **Username**: `{usuario.username}`")
            print(f"   • **Nome completo**: {usuario.get_full_name()}")
            print(f"   • **Email**: {usuario.email}")
            print(f"   • **Status**: {'✅ Ativo' if usuario.is_active else '❌ Inativo'}")
            print()
    
    print("=" * 60)
    print("💡 **INFORMAÇÕES IMPORTANTES:**")
    print("• Superusuários têm acesso total ao sistema")
    print("• Usuários staff têm acesso ao admin do Django")
    print("• Para alterar senhas, use o comando: python manage.py changepassword <username>")

def testar_login_superusuarios():
    """
    Testa o login dos superusuários
    """
    print("\n🧪 **TESTE DE LOGIN DOS SUPERUSUÁRIOS:**")
    print("=" * 60)
    
    from django.contrib.auth import authenticate
    
    superusuarios = User.objects.filter(is_superuser=True)
    
    for usuario in superusuarios:
        print(f"🔐 Testando login para: {usuario.username}")
        
        # Tentar autenticar (sem senha para verificar se o usuário existe)
        user = authenticate(username=usuario.username, password="")
        
        if user is None:
            print(f"   ✅ Usuário existe e está ativo")
        else:
            print(f"   ❌ Problema na autenticação")
        
        print()

def main():
    """
    Função principal
    """
    verificar_superusuarios()
    testar_login_superusuarios()

if __name__ == '__main__':
    main() 