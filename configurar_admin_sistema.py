#!/usr/bin/env python
"""
Script para configurar a função Administrador do Sistema com todas as permissões
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def configurar_admin_sistema():
    """Configura a função Administrador do Sistema com todas as permissões"""
    
    print("🔧 CONFIGURANDO ADMINISTRADOR DO SISTEMA")
    print("=" * 60)
    
    # 1. Verificar se o cargo existe
    cargo_admin = CargoFuncao.objects.filter(nome='Administrador do Sistema').first()
    
    if not cargo_admin:
        print("❌ Cargo 'Administrador do Sistema' não encontrado!")
        print("🔧 Criando cargo...")
        
        cargo_admin = CargoFuncao.objects.create(
            nome='Administrador do Sistema',
            descricao='Administrador do sistema com acesso total a todas as funcionalidades'
        )
        print(f"✅ Cargo criado com ID: {cargo_admin.id}")
    else:
        print(f"✅ Cargo 'Administrador do Sistema' já existe (ID: {cargo_admin.id})")
    
    # 2. Verificar usuários com essa função
    usuarios_admin = UsuarioFuncao.objects.filter(
        cargo_funcao=cargo_admin,
        status='ATIVO'
    )
    
    print(f"\n2️⃣ USUÁRIOS COM FUNÇÃO ADMINISTRADOR DO SISTEMA:")
    if usuarios_admin.exists():
        for uf in usuarios_admin:
            print(f"   • {uf.usuario.username} ({uf.usuario.get_full_name()})")
            print(f"     - Desde: {uf.data_inicio}")
            print(f"     - Status: {uf.status}")
    else:
        print("   ❌ Nenhum usuário com essa função encontrado")
    
    # 3. Perguntar se quer adicionar função ao usuário admin
    print(f"\n3️⃣ ADICIONAR FUNÇÃO AO USUÁRIO ADMIN?")
    
    try:
        user_admin = User.objects.get(username='admin')
        funcao_existente = UsuarioFuncao.objects.filter(
            usuario=user_admin,
            cargo_funcao=cargo_admin,
            status='ATIVO'
        ).exists()
        
        if funcao_existente:
            print("   ✅ Usuário 'admin' já tem a função 'Administrador do Sistema'")
        else:
            print("   ❌ Usuário 'admin' não tem a função 'Administrador do Sistema'")
            print("   🔧 Adicionando função...")
            
            from datetime import date
            nova_funcao = UsuarioFuncao.objects.create(
                usuario=user_admin,
                cargo_funcao=cargo_admin,
                data_inicio=date.today(),
                status='ATIVO'
            )
            print(f"   ✅ Função adicionada com ID: {nova_funcao.id}")
            
    except User.DoesNotExist:
        print("   ❌ Usuário 'admin' não encontrado")
    
    # 4. Verificar permissões do context processor
    print(f"\n4️⃣ TESTANDO PERMISSÕES:")
    
    from django.test import RequestFactory
    from militares.context_processors import menu_permissions_processor
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user_admin
    
    context = menu_permissions_processor(request)
    menu_permissions = context.get('menu_permissions', {})
    
    print(f"   • show_quadros_acesso: {menu_permissions.get('show_quadros_acesso', False)}")
    print(f"   • show_quadros_fixacao: {menu_permissions.get('show_quadros_fixacao', False)}")
    print(f"   • show_comissoes: {menu_permissions.get('show_comissoes', False)}")
    print(f"   • show_administracao: {menu_permissions.get('show_administracao', False)}")
    print(f"   • is_special: {menu_permissions.get('is_special', False)}")
    
    # 5. Verificar se tem acesso total
    principais = [
        menu_permissions.get('show_quadros_acesso', False),
        menu_permissions.get('show_quadros_fixacao', False),
        menu_permissions.get('show_comissoes', False)
    ]
    
    print(f"\n5️⃣ RESULTADO FINAL:")
    if all(principais):
        print("   ✅ SUCESSO! Usuário tem acesso total a todos os módulos")
        print("   🎯 Agora você deve conseguir ver:")
        print("      • Quadros de Acesso")
        print("      • Quadros de Fixação de Vagas")
        print("      • Comissões")
        print("      • Todos os outros módulos administrativos")
    else:
        print("   ❌ PROBLEMA! Usuário ainda não tem acesso total")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    configurar_admin_sistema() 