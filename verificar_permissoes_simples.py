#!/usr/bin/env python
"""
Script simplificado para verificar as permissões do usuário
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User

def verificar_permissoes_simples():
    print("🔍 VERIFICAÇÃO SIMPLIFICADA DE PERMISSÕES\n")
    
    # Buscar usuário José ERISMAN
    try:
        usuario = User.objects.get(username='490.083.823-34')
        print(f"👤 Usuário: {usuario.get_full_name()} ({usuario.username})")
    except User.DoesNotExist:
        print("❌ Usuário não encontrado")
        return
    
    # Verificar grupos
    grupos = usuario.groups.all()
    print(f"\n📋 Grupos:")
    for grupo in grupos:
        print(f"  - {grupo.name}")
    
    # Verificar se tem permissões especiais
    print(f"\n🔐 Permissões:")
    print(f"  - is_superuser: {usuario.is_superuser}")
    print(f"  - is_staff: {usuario.is_staff}")
    
    # Verificar permissões específicas
    permissoes = usuario.user_permissions.all()
    print(f"\n📝 Permissões Específicas:")
    for permissao in permissoes:
        print(f"  - {permissao.codename}")
    
    # Verificar se tem permissões de grupo
    print(f"\n👥 Permissões de Grupo:")
    for grupo in grupos:
        print(f"  Grupo: {grupo.name}")
        for permissao in grupo.permissions.all():
            print(f"    - {permissao.codename}")

if __name__ == "__main__":
    verificar_permissoes_simples() 