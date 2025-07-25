#!/usr/bin/env python
"""
Script para configurar o usuário admin com acesso total sem restrições
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

def configurar_admin_total():
    """Configura o usuário admin com acesso total"""
    
    print("👑 CONFIGURANDO ADMIN COM ACESSO TOTAL")
    print("=" * 60)
    
    # 1. Verificar/criar usuário admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Administrador',
            'last_name': 'do Sistema',
            'email': 'admin@cbmepi.com',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    if created:
        admin_user.set_password('admin')
        admin_user.save()
        print("✅ Usuário admin criado")
    else:
        # Garantir que é superusuário
        if not admin_user.is_superuser:
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            print("✅ Admin configurado como superusuário")
        else:
            print("ℹ️ Admin já é superusuário")
    
    # 2. Adicionar todas as permissões Django
    print("\n🔑 ADICIONANDO TODAS AS PERMISSÕES DJANGO:")
    
    # Obter todas as permissões do sistema
    todas_permissoes = Permission.objects.all()
    print(f"   Total de permissões Django: {todas_permissoes.count()}")
    
    # Adicionar todas as permissões ao admin
    admin_user.user_permissions.set(todas_permissoes)
    print("✅ Todas as permissões Django adicionadas ao admin")
    
    # 3. Adicionar a todos os grupos
    print("\n👥 ADICIONANDO A TODOS OS GRUPOS:")
    todos_grupos = Group.objects.all()
    
    for grupo in todos_grupos:
        admin_user.groups.add(grupo)
        print(f"   ✅ Adicionado ao grupo: {grupo.name}")
    
    # 4. Configurar cargo de administrador
    print("\n🎯 CONFIGURANDO CARGO DE ADMINISTRADOR:")
    
    # Criar/atualizar cargo de administrador
    cargo_admin, created = CargoFuncao.objects.get_or_create(
        nome='Administrador',
        defaults={
            'descricao': 'Administrador do sistema com acesso total sem restrições',
            'ativo': True
        }
    )
    
    if created:
        print("✅ Cargo 'Administrador' criado")
    else:
        print("ℹ️ Cargo 'Administrador' já existe")
    
    # 5. Adicionar todas as permissões ao cargo
    print("\n📋 ADICIONANDO TODAS AS PERMISSÕES AO CARGO:")
    
    # Limpar permissões existentes
    PermissaoFuncao.objects.filter(cargo_funcao=cargo_admin).delete()
    
    # Adicionar todas as permissões possíveis
    modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
    acessos = [choice[0] for choice in PermissaoFuncao.ACESSOS_CHOICES]
    
    total_permissoes = 0
    for modulo in modulos:
        for acesso in acessos:
            PermissaoFuncao.objects.create(
                cargo_funcao=cargo_admin,
                modulo=modulo,
                acesso=acesso,
                ativo=True,
                observacoes='Acesso total do administrador'
            )
            total_permissoes += 1
    
    print(f"✅ {total_permissoes} permissões adicionadas ao cargo")
    
    # 6. Atribuir cargo ao admin
    print("\n👤 ATRIBUINDO CARGO AO ADMIN:")
    
    funcao_admin, created = UsuarioFuncao.objects.get_or_create(
        usuario=admin_user,
        cargo_funcao=cargo_admin,
        defaults={
            'tipo_funcao': 'EFETIVA',
            'status': 'ATIVO',
            'data_inicio': '2024-01-01'
        }
    )
    
    if created:
        print("✅ Função de administrador atribuída ao admin")
    else:
        print("ℹ️ Função de administrador já existe para o admin")
    
    # 7. Verificar resultado final
    print("\n✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    
    # Verificar permissões
    permissoes_django = admin_user.user_permissions.count()
    grupos = admin_user.groups.count()
    permissoes_cargo = PermissaoFuncao.objects.filter(cargo_funcao=cargo_admin).count()
    
    print(f"📊 RESUMO:")
    print(f"   Permissões Django: {permissoes_django}")
    print(f"   Grupos: {grupos}")
    print(f"   Permissões do cargo: {permissoes_cargo}")
    print(f"   Superusuário: {admin_user.is_superuser}")
    print(f"   Staff: {admin_user.is_staff}")
    
    print(f"\n🎉 O usuário admin agora tem acesso total sem restrições!")

def remover_travas_admin():
    """Remove todas as travas de permissão para o admin"""
    
    print("\n🔓 REMOVENDO TRAVAS DE PERMISSÃO")
    print("=" * 60)
    
    try:
        admin_user = User.objects.get(username='admin')
        
        # 1. Garantir que é superusuário
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        
        # 2. Adicionar todas as permissões Django
        todas_permissoes = Permission.objects.all()
        admin_user.user_permissions.set(todas_permissoes)
        
        # 3. Adicionar a todos os grupos
        todos_grupos = Group.objects.all()
        for grupo in todos_grupos:
            admin_user.groups.add(grupo)
        
        # 4. Verificar se tem função de administrador
        funcao_admin = UsuarioFuncao.objects.filter(
            usuario=admin_user,
            cargo_funcao__nome__icontains='administrador',
            status='ATIVO'
        ).first()
        
        if not funcao_admin:
            # Criar função de administrador
            cargo_admin = CargoFuncao.objects.filter(
                nome__icontains='administrador'
            ).first()
            
            if cargo_admin:
                UsuarioFuncao.objects.create(
                    usuario=admin_user,
                    cargo_funcao=cargo_admin,
                    tipo_funcao='EFETIVA',
                    status='ATIVO',
                    data_inicio='2024-01-01'
                )
        
        print("✅ Todas as travas removidas do admin!")
        
    except User.DoesNotExist:
        print("❌ Usuário admin não encontrado!")

def verificar_acesso_admin():
    """Verifica se o admin tem acesso total"""
    
    print("\n🔍 VERIFICANDO ACESSO DO ADMIN")
    print("=" * 60)
    
    try:
        admin_user = User.objects.get(username='admin')
        
        print(f"👤 Usuário: {admin_user.username}")
        print(f"   Superusuário: {admin_user.is_superuser}")
        print(f"   Staff: {admin_user.is_staff}")
        print(f"   Ativo: {admin_user.is_active}")
        
        # Verificar permissões Django
        permissoes_django = admin_user.user_permissions.count()
        print(f"\n🔑 Permissões Django: {permissoes_django}")
        
        # Verificar grupos
        grupos = admin_user.groups.all()
        print(f"👥 Grupos ({grupos.count()}):")
        for grupo in grupos:
            print(f"   - {grupo.name}")
        
        # Verificar função
        funcao_admin = UsuarioFuncao.objects.filter(
            usuario=admin_user,
            status='ATIVO'
        ).first()
        
        if funcao_admin:
            print(f"\n🎯 Função: {funcao_admin.cargo_funcao.nome}")
            
            # Verificar permissões da função
            permissoes_funcao = PermissaoFuncao.objects.filter(
                cargo_funcao=funcao_admin.cargo_funcao,
                ativo=True
            ).count()
            
            print(f"   Permissões da função: {permissoes_funcao}")
            
            # Verificar se tem todas as permissões CRUD
            modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
            acessos_crud = ['CRIAR', 'EDITAR', 'EXCLUIR']
            
            total_esperado = len(modulos) * len(acessos_crud)
            if permissoes_funcao >= total_esperado:
                print("   ✅ Tem todas as permissões CRUD")
            else:
                print(f"   ⚠️ Faltam permissões (tem {permissoes_funcao}, esperado {total_esperado})")
        else:
            print("   ❌ Nenhuma função ativa encontrada")
        
        # Verificar se pode fazer tudo
        if admin_user.is_superuser and permissoes_django > 0:
            print("\n🎉 ADMIN TEM ACESSO TOTAL!")
        else:
            print("\n⚠️ ADMIN PODE TER RESTRIÇÕES!")
            
    except User.DoesNotExist:
        print("❌ Usuário admin não encontrado!")

if __name__ == "__main__":
    print("👑 CONFIGURADOR DE ADMIN TOTAL")
    print("=" * 60)
    print("1. Configurar admin com acesso total")
    print("2. Remover travas do admin")
    print("3. Verificar acesso do admin")
    
    opcao = input("\nEscolha uma opção (1-3): ").strip()
    
    if opcao == "1":
        configurar_admin_total()
    elif opcao == "2":
        remover_travas_admin()
    elif opcao == "3":
        verificar_acesso_admin()
    else:
        print("❌ Opção inválida!") 