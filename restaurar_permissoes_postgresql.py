#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao
from datetime import date

def restaurar_permissoes_postgresql():
    print("=== RESTAURANDO PERMISSÕES PARA POSTGRESQL ===\n")
    
    # 1. Verificar e criar cargos especiais se não existirem
    cargos_especiais = [
        'Diretor de Gestão de Pessoas',
        'Chefe da Seção de Promoções', 
        'Administrador do Sistema',
        'Administrador'
    ]
    
    print("1. VERIFICANDO CARGOS ESPECIAIS:")
    for cargo_nome in cargos_especiais:
        cargo, created = CargoFuncao.objects.get_or_create(nome=cargo_nome)
        if created:
            print(f"   ✅ Criado: {cargo_nome}")
        else:
            print(f"   ✅ Já existe: {cargo_nome}")
    print()
    
    # 2. Verificar usuário admin
    print("2. VERIFICANDO USUÁRIO ADMIN:")
    try:
        admin = User.objects.get(username='admin')
        print(f"   ✅ Usuário admin encontrado")
        
        # Garantir que admin tem todas as permissões
        admin.is_superuser = True
        admin.is_staff = True
        admin.is_active = True
        admin.save()
        print(f"   ✅ Permissões de superusuário garantidas")
        
        # Verificar funções especiais do admin
        for cargo_nome in cargos_especiais:
            cargo = CargoFuncao.objects.get(nome=cargo_nome)
            funcao, created = UsuarioFuncao.objects.get_or_create(
                usuario=admin,
                cargo_funcao=cargo,
                defaults={'status': 'ATIVO', 'data_inicio': date.today()}
            )
            if created:
                print(f"   ✅ Função {cargo_nome} criada para admin")
            else:
                funcao.status = 'ATIVO'
                funcao.save()
                print(f"   ✅ Função {cargo_nome} ativada para admin")
                
    except User.DoesNotExist:
        print("   ❌ Usuário admin não encontrado")
    print()
    
    # 3. Verificar usuário ERISMAN
    print("3. VERIFICANDO USUÁRIO ERISMAN:")
    try:
        erisman = User.objects.get(username='49008382334')
        print(f"   ✅ Usuário ERISMAN encontrado")
        
        # Verificar funções especiais do ERISMAN
        for cargo_nome in cargos_especiais:
            cargo = CargoFuncao.objects.get(nome=cargo_nome)
            funcao, created = UsuarioFuncao.objects.get_or_create(
                usuario=erisman,
                cargo_funcao=cargo,
                defaults={'status': 'ATIVO', 'data_inicio': date.today()}
            )
            if created:
                print(f"   ✅ Função {cargo_nome} criada para ERISMAN")
            else:
                funcao.status = 'ATIVO'
                funcao.save()
                print(f"   ✅ Função {cargo_nome} ativada para ERISMAN")
                
    except User.DoesNotExist:
        print("   ❌ Usuário ERISMAN não encontrado")
    print()
    
    # 4. Verificar usuário Erisman (com username diferente)
    print("4. VERIFICANDO USUÁRIO ERISMAN (username 'Erisman'):")
    try:
        erisman2 = User.objects.get(username='Erisman')
        print(f"   ✅ Usuário Erisman encontrado")
        
        # Verificar funções especiais do Erisman
        for cargo_nome in cargos_especiais:
            cargo = CargoFuncao.objects.get(nome=cargo_nome)
            funcao, created = UsuarioFuncao.objects.get_or_create(
                usuario=erisman2,
                cargo_funcao=cargo,
                defaults={'status': 'ATIVO', 'data_inicio': date.today()}
            )
            if created:
                print(f"   ✅ Função {cargo_nome} criada para Erisman")
            else:
                funcao.status = 'ATIVO'
                funcao.save()
                print(f"   ✅ Função {cargo_nome} ativada para Erisman")
                
    except User.DoesNotExist:
        print("   ❌ Usuário Erisman não encontrado")
    print()
    
    # 5. Verificar usuário Diretor de Gestão de Pessoas
    print("5. VERIFICANDO DIRETOR DE GESTÃO DE PESSOAS:")
    try:
        diretor = User.objects.get(username='36136794349')
        print(f"   ✅ Usuário Diretor encontrado")
        
        # Garantir que tem função de Diretor de Gestão de Pessoas
        cargo_diretor = CargoFuncao.objects.get(nome='Diretor de Gestão de Pessoas')
        funcao, created = UsuarioFuncao.objects.get_or_create(
            usuario=diretor,
            cargo_funcao=cargo_diretor,
            defaults={'status': 'ATIVO', 'data_inicio': date.today()}
        )
        if created:
            print(f"   ✅ Função Diretor de Gestão de Pessoas criada")
        else:
            funcao.status = 'ATIVO'
            funcao.save()
            print(f"   ✅ Função Diretor de Gestão de Pessoas ativada")
                
    except User.DoesNotExist:
        print("   ❌ Usuário Diretor não encontrado")
    except CargoFuncao.DoesNotExist:
        print("   ❌ Cargo Diretor de Gestão de Pessoas não encontrado")
    print()
    
    # 6. Resumo final
    print("6. RESUMO FINAL:")
    for cargo_nome in cargos_especiais:
        try:
            cargo = CargoFuncao.objects.get(nome=cargo_nome)
            usuarios_com_funcao = UsuarioFuncao.objects.filter(
                cargo_funcao=cargo, 
                status='ATIVO'
            )
            print(f"   • {cargo_nome}: {usuarios_com_funcao.count()} usuários")
            for uf in usuarios_com_funcao:
                print(f"     - {uf.usuario.username}")
        except CargoFuncao.DoesNotExist:
            print(f"   • {cargo_nome}: ❌ NÃO EXISTE")
    
    print("\n=== RESTAURAÇÃO CONCLUÍDA ===")

if __name__ == '__main__':
    restaurar_permissoes_postgresql() 