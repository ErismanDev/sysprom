#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Group

def corrigir_grupos():
    print("=== Corrigindo Grupos de Usuários ===\n")
    
    # Obter os grupos corretos
    try:
        grupo_chefe = Group.objects.get(name='Chefe da Seção de Promoções')
        grupo_diretor = Group.objects.get(name='Diretor de Gestão de Pessoas')
        print(f"✓ Grupo Chefe encontrado: {grupo_chefe.name}")
        print(f"✓ Grupo Diretor encontrado: {grupo_diretor.name}")
    except Group.DoesNotExist as e:
        print(f"✗ Erro ao encontrar grupo: {e}")
        return
    
    # Corrigir usuário chefe_promocoes
    try:
        chefe = User.objects.get(username='chefe_promocoes')
        print(f"\nUsuário chefe_promocoes encontrado: {chefe.get_full_name()}")
        print(f"Grupos atuais: {[g.name for g in chefe.groups.all()]}")
        
        # Limpar grupos e adicionar o correto
        chefe.groups.clear()
        chefe.groups.add(grupo_chefe)
        chefe.save()
        
        print(f"✓ Grupos atualizados: {[g.name for g in chefe.groups.all()]}")
    except User.DoesNotExist:
        print("✗ Usuário chefe_promocoes não encontrado")
    
    # Verificar usuário diretor_gestao
    try:
        diretor = User.objects.get(username='diretor_gestao')
        print(f"\nUsuário diretor_gestao encontrado: {diretor.get_full_name()}")
        print(f"Grupos atuais: {[g.name for g in diretor.groups.all()]}")
        
        # Verificar se já está no grupo correto
        if grupo_diretor in diretor.groups.all():
            print("✓ Usuário diretor_gestao já está no grupo correto")
        else:
            # Limpar grupos e adicionar o correto
            diretor.groups.clear()
            diretor.groups.add(grupo_diretor)
            diretor.save()
            print(f"✓ Grupos atualizados: {[g.name for g in diretor.groups.all()]}")
    except User.DoesNotExist:
        print("✗ Usuário diretor_gestao não encontrado")
    
    print("\n=== Teste de Permissões ===")
    from militares.decorators import can_edit_ficha_conceito, can_edit_militar
    
    # Testar permissões dos usuários corrigidos
    for username in ['chefe_promocoes', 'diretor_gestao']:
        try:
            user = User.objects.get(username=username)
            print(f"\nUsuário: {username}")
            print(f"  Nome: {user.get_full_name()}")
            print(f"  Grupos: {[g.name for g in user.groups.all()]}")
            print(f"  Pode editar fichas de conceito: {'SIM' if can_edit_ficha_conceito(user) else 'NÃO'}")
            print(f"  Pode editar cadastros de militares: {'SIM' if can_edit_militar(user) else 'NÃO'}")
        except User.DoesNotExist:
            print(f"✗ Usuário {username} não encontrado")

if __name__ == '__main__':
    corrigir_grupos() 