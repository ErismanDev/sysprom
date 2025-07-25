#!/usr/bin/env python
"""
Script para verificar e corrigir a associação do usuário ERISMAN
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, MembroComissao

def verificar_usuario_erisman():
    print("=== VERIFICAÇÃO DO USUÁRIO ERISMAN ===\n")
    
    # Verificar se existe usuário Django com username 49008382334
    try:
        user = User.objects.get(username='49008382334')
        print(f"✅ Usuário Django encontrado: {user.username}")
        print(f"   - Nome: {user.first_name} {user.last_name}")
        print(f"   - Email: {user.email}")
        print(f"   - Ativo: {user.is_active}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Superuser: {user.is_superuser}")
    except User.DoesNotExist:
        print("❌ Usuário Django NÃO encontrado para: 49008382334")
    
    print()
    
    # Verificar militar José ERISMAN
    try:
        militar = Militar.objects.get(nome_completo__icontains='ERISMAN')
        print(f"✅ Militar encontrado: {militar.nome_completo}")
        print(f"   - Matrícula: {militar.matricula}")
        print(f"   - CPF: {militar.cpf}")
        print(f"   - Usuário Django associado: {militar.user}")
        
        if militar.user:
            print(f"   - Username do usuário: {militar.user.username}")
        else:
            print("   - ❌ Nenhum usuário Django associado ao militar")
            
    except Militar.DoesNotExist:
        print("❌ Militar ERISMAN não encontrado")
    
    print()
    
    # Verificar membros de comissão do ERISMAN
    membros_erisman = MembroComissao.objects.filter(militar__nome_completo__icontains='ERISMAN')
    print(f"Membros de comissão do ERISMAN: {membros_erisman.count()}")
    for membro in membros_erisman:
        print(f"   • Comissão: {membro.comissao.nome} ({membro.comissao.tipo})")
        print(f"     - Ativo: {membro.ativo}")
        print(f"     - Usuário: {membro.usuario}")
    
    print("\n=== FIM DA VERIFICAÇÃO ===")

if __name__ == '__main__':
    verificar_usuario_erisman() 