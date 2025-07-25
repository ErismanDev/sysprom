#!/usr/bin/env python
"""
Script para diagnosticar problemas de permissões do administrador
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from militares.models import UsuarioFuncao, CargoFuncao, PermissaoFuncao

def diagnosticar_permissoes_admin():
    """Diagnostica problemas de permissões do administrador"""
    
    print("🔍 DIAGNÓSTICO DE PERMISSÕES DO ADMINISTRADOR")
    print("=" * 60)
    
    # 1. Verificar usuário admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuário admin encontrado: {admin_user.get_full_name()}")
        print(f"   Superusuário: {admin_user.is_superuser}")
        print(f"   Staff: {admin_user.is_staff}")
        print(f"   Ativo: {admin_user.is_active}")
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        return
    
    # 2. Verificar funções do admin
    print(f"\n📋 FUNÇÕES DO ADMIN:")
    funcoes_admin = UsuarioFuncao.objects.filter(
        usuario=admin_user,
        status='ATIVO'
    ).select_related('cargo_funcao')
    
    if funcoes_admin.exists():
        for funcao in funcoes_admin:
            print(f"   ✅ {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
            
            # Verificar permissões desta função
            permissoes_funcao = PermissaoFuncao.objects.filter(
                cargo_funcao=funcao.cargo_funcao,
                ativo=True
            )
            print(f"      Permissões: {permissoes_funcao.count()}")
            
            # Mostrar algumas permissões
            for perm in permissoes_funcao[:5]:
                print(f"        - {perm.modulo}: {perm.acesso}")
            if permissoes_funcao.count() > 5:
                print(f"        ... e mais {permissoes_funcao.count() - 5} permissões")
    else:
        print("   ❌ Nenhuma função ativa encontrada!")
    
    # 3. Verificar permissões Django diretas
    print(f"\n🔑 PERMISSÕES DJANGO DIRETAS:")
    permissoes_django = admin_user.user_permissions.all()
    grupos = admin_user.groups.all()
    
    print(f"   Permissões diretas: {permissoes_django.count()}")
    print(f"   Grupos: {grupos.count()}")
    
    for grupo in grupos:
        print(f"     - {grupo.name}")
        permissoes_grupo = grupo.permissions.all()
        print(f"       Permissões do grupo: {permissoes_grupo.count()}")
    
    # 4. Verificar cargos disponíveis
    print(f"\n👥 CARGOS DISPONÍVEIS:")
    cargos = CargoFuncao.objects.all().order_by('id')
    
    for cargo in cargos:
        perms_count = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
        print(f"   {cargo.id:2d}: {cargo.nome:<30} ({perms_count:3d} permissões)")
    
    # 5. Verificar se o admin tem função de administrador
    print(f"\n🎯 VERIFICAÇÃO ESPECÍFICA:")
    
    # Verificar se tem função de administrador
    funcao_admin = funcoes_admin.filter(
        cargo_funcao__nome__icontains='administrador'
    ).first()
    
    if funcao_admin:
        print(f"   ✅ Tem função de administrador: {funcao_admin.cargo_funcao.nome}")
        
        # Verificar permissões CRUD
        permissoes_crud = PermissaoFuncao.objects.filter(
            cargo_funcao=funcao_admin.cargo_funcao,
            acesso__in=['CRIAR', 'EDITAR', 'EXCLUIR'],
            ativo=True
        )
        
        print(f"   Permissões CRUD: {permissoes_crud.count()}")
        
        # Verificar por módulo
        modulos_crud = {}
        for perm in permissoes_crud:
            if perm.modulo not in modulos_crud:
                modulos_crud[perm.modulo] = []
            modulos_crud[perm.modulo].append(perm.acesso)
        
        for modulo, acessos in modulos_crud.items():
            print(f"     {modulo}: {', '.join(acessos)}")
            
    else:
        print("   ❌ NÃO tem função de administrador!")
        print("   💡 SOLUÇÃO: Adicionar função de administrador ao usuário")
    
    # 6. Verificar se o sistema está usando o decorator correto
    print(f"\n🔧 VERIFICAÇÃO DO SISTEMA:")
    
    # Verificar se existe função de administrador
    cargo_admin = CargoFuncao.objects.filter(
        nome__icontains='administrador'
    ).first()
    
    if cargo_admin:
        print(f"   ✅ Cargo de administrador existe: {cargo_admin.nome}")
        
        # Verificar se tem todas as permissões
        todas_permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo_admin)
        print(f"   Total de permissões: {todas_permissoes.count()}")
        
        # Verificar se tem permissões CRUD em todos os módulos
        modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
        acessos_crud = ['CRIAR', 'EDITAR', 'EXCLUIR']
        
        modulos_faltando = []
        for modulo in modulos:
            for acesso in acessos_crud:
                if not PermissaoFuncao.objects.filter(
                    cargo_funcao=cargo_admin,
                    modulo=modulo,
                    acesso=acesso,
                    ativo=True
                ).exists():
                    modulos_faltando.append(f"{modulo}:{acesso}")
        
        if modulos_faltando:
            print(f"   ⚠️ Permissões faltando: {len(modulos_faltando)}")
            for perm in modulos_faltando[:10]:
                print(f"     - {perm}")
            if len(modulos_faltando) > 10:
                print(f"     ... e mais {len(modulos_faltando) - 10}")
        else:
            print("   ✅ Todas as permissões CRUD estão configuradas")
            
    else:
        print("   ❌ Cargo de administrador não existe!")
        print("   💡 SOLUÇÃO: Criar cargo de administrador")
    
    # 7. Recomendações
    print(f"\n💡 RECOMENDAÇÕES:")
    
    if not funcao_admin:
        print("   1. Adicionar função de administrador ao usuário admin")
        print("   2. Executar: python gerenciar_rapido.py")
        print("   3. Usar comando: 'cargo 1' (assumindo que ID 1 é administrador)")
    
    if cargo_admin and modulos_faltando:
        print("   1. Adicionar permissões faltantes ao cargo de administrador")
        print("   2. Executar: python gerenciar_rapido.py")
        print(f"   3. Usar comando: 'cargo {cargo_admin.id}'")
    
    if not cargo_admin:
        print("   1. Criar cargo de administrador")
        print("   2. Configurar todas as permissões")
        print("   3. Atribuir ao usuário admin")

def corrigir_permissoes_admin():
    """Corrige automaticamente as permissões do administrador"""
    
    print("\n🔧 CORRIGINDO PERMISSÕES DO ADMINISTRADOR")
    print("=" * 60)
    
    # 1. Verificar/criar cargo de administrador
    cargo_admin, created = CargoFuncao.objects.get_or_create(
        nome='Administrador',
        defaults={
            'descricao': 'Administrador do sistema com acesso total',
            'ativo': True
        }
    )
    
    if created:
        print(f"✅ Cargo 'Administrador' criado (ID: {cargo_admin.id})")
    else:
        print(f"ℹ️ Cargo 'Administrador' já existe (ID: {cargo_admin.id})")
    
    # 2. Adicionar todas as permissões ao cargo
    modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
    acessos = [choice[0] for choice in PermissaoFuncao.ACESSOS_CHOICES]
    
    total_permissoes = 0
    for modulo in modulos:
        for acesso in acessos:
            permissao, created = PermissaoFuncao.objects.get_or_create(
                cargo_funcao=cargo_admin,
                modulo=modulo,
                acesso=acesso,
                defaults={'ativo': True}
            )
            if created:
                total_permissoes += 1
    
    print(f"✅ {total_permissoes} permissões adicionadas ao cargo")
    
    # 3. Verificar/criar função do usuário admin
    try:
        admin_user = User.objects.get(username='admin')
        
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
            print(f"✅ Função de administrador atribuída ao usuário admin")
        else:
            print(f"ℹ️ Função de administrador já existe para o usuário admin")
            
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        return
    
    # 4. Verificar resultado
    permissoes_finais = PermissaoFuncao.objects.filter(cargo_funcao=cargo_admin).count()
    print(f"\n✅ CORREÇÃO CONCLUÍDA!")
    print(f"   Total de permissões do administrador: {permissoes_finais}")

if __name__ == "__main__":
    print("Escolha uma opção:")
    print("1. Diagnosticar permissões")
    print("2. Corrigir permissões automaticamente")
    
    opcao = input("Opção (1-2): ").strip()
    
    if opcao == "1":
        diagnosticar_permissoes_admin()
    elif opcao == "2":
        corrigir_permissoes_admin()
    else:
        print("❌ Opção inválida!") 