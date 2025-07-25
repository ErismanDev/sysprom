#!/usr/bin/env python
# -*- coding: utf-8-

"cript para debugar o processo de login
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE, romcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def verificar_usuarios():
    print("=== VERIFICAÇÃO DE USUÁRIOS ===")
    usuarios = User.objects.all()
    print(fTotal de usuários: {usuarios.count()}")
    
    for user in usuarios:
        print(fID: {user.id}, Username: {user.username}, Is Active: {user.is_active}, Is Superuser: {user.is_superuser}")
        
        # Verificar funções do usuário
        funcoes = UsuarioFuncao.objects.filter(usuario=user)
        print(f Funções: {funcoes.count()})
        for funcao in funcoes:
            print(f"    -[object Object]funcao.cargo_funcao.nome} (Status: {funcao.status})")

def verificar_cargos():
    print(n=== VERIFICAÇÃO DE CARGOS ===")
    cargos = CargoFuncao.objects.all()
    print(f"Total de cargos: {cargos.count()}")
    
    for cargo in cargos:
        print(fID:[object Object]cargo.id}, Nome: {cargo.nome}, Ativo: {cargo.ativo}")

def criar_funcao_teste():
    print(n=== CRIANDO FUNÇÃO DE TESTE ===")
    
    # Verificar se o cargo Administrador do Sistema existe
    cargo_admin, created = CargoFuncao.objects.get_or_create(
        nome='Administrador do Sistema',
        defaults={ativo': True}
    )
    
    if created:
        print(f"CargoAdministrador do Sistema' criado (ID: {cargo_admin.id})")
    else:
        print(f"CargoAdministrador do Sistema já existe (ID: {cargo_admin.id})")
    
    # Verificar se o usuário admin existe
    try:
        user_admin = User.objects.get(username='admin)
        print(f"Usuário admin encontrado (ID: {user_admin.id})")
        
        # Criar função para o admin
        funcao_admin, created = UsuarioFuncao.objects.get_or_create(
            usuario=user_admin,
            cargo_funcao=cargo_admin,
            defaults={'status': 'ATIVO'}
        )
        
        if created:
            print(f"FunçãoAdministrador do Sistema' criada para admin (ID: {funcao_admin.id})")
        else:
            print(f"FunçãoAdministrador do Sistema' já existe para admin (ID: {funcao_admin.id})")
            
    except User.DoesNotExist:
        print(Usuário admin não encontrado!)if __name__ == '__main__':
    verificar_usuarios()
    verificar_cargos()
    criar_funcao_teste()
    
    print("\n=== RESULTADO FINAL ===")
    verificar_usuarios() 