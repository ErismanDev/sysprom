#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Group
from militares.decorators import can_edit_ficha_conceito, can_edit_militar

def test_permissions():
    print("=== Teste de Permissões para Edição de Fichas de Conceito e Cadastros de Militares ===\n")
    
    # Listar todos os usuários e seus grupos
    users = User.objects.all()
    
    for user in users:
        print(f"Usuário: {user.username}")
        print(f"  Nome: {user.get_full_name()}")
        print(f"  É superuser: {user.is_superuser}")
        print(f"  Grupos: {[group.name for group in user.groups.all()]}")
        
        # Testar permissões
        tem_permissao_ficha = can_edit_ficha_conceito(user)
        tem_permissao_militar = can_edit_militar(user)
        print(f"  Pode editar fichas de conceito: {'SIM' if tem_permissao_ficha else 'NÃO'}")
        print(f"  Pode editar cadastros de militares: {'SIM' if tem_permissao_militar else 'NÃO'}")
        print()
    
    # Listar grupos existentes
    print("=== Grupos Existentes ===")
    groups = Group.objects.all()
    for group in groups:
        print(f"  - {group.name}")
    
    print("\n=== Grupos Permitidos ===")
    grupos_permitidos = ['Chefe_Seção_Promoções', 'Diretor_Gestão_Pessoas']
    for grupo in grupos_permitidos:
        try:
            group = Group.objects.get(name=grupo)
            print(f"  ✓ {grupo} - Existe")
        except Group.DoesNotExist:
            print(f"  ✗ {grupo} - NÃO EXISTE")

if __name__ == '__main__':
    test_permissions() 