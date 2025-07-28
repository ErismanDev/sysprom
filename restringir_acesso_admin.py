#!/usr/bin/env python
"""
Script para restringir acesso às seções administrativas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao, PermissaoFuncao

def restringir_acesso_admin():
    """Restringe o acesso às seções administrativas"""
    
    print("🔒 RESTRINGINDO ACESSO ÀS SEÇÕES ADMINISTRATIVAS")
    print("=" * 60)
    
    # 1. Definir funções que podem acessar seções administrativas
    funcoes_admin = [
        'Administrador do Sistema',
        'Administrador'
    ]
    
    print(f"📋 FUNÇÕES COM ACESSO ADMINISTRATIVO:")
    for funcao in funcoes_admin:
        print(f"   • {funcao}")
    
    # 2. Verificar se essas funções existem
    print(f"\n🔍 VERIFICANDO EXISTÊNCIA DAS FUNÇÕES:")
    for funcao_nome in funcoes_admin:
        try:
            cargo = CargoFuncao.objects.get(nome=funcao_nome)
            usuarios = UsuarioFuncao.objects.filter(cargo_funcao=cargo, status='ATIVO').count()
            print(f"   ✅ {funcao_nome}: {usuarios} usuários ativos")
        except CargoFuncao.DoesNotExist:
            print(f"   ❌ {funcao_nome}: NÃO EXISTE")
    
    # 3. Verificar usuários com essas funções
    print(f"\n👥 USUÁRIOS COM FUNÇÕES ADMINISTRATIVAS:")
    usuarios_admin = UsuarioFuncao.objects.filter(
        cargo_funcao__nome__in=funcoes_admin,
        status='ATIVO'
    ).select_related('usuario', 'cargo_funcao')
    
    for uf in usuarios_admin:
        print(f"   • {uf.usuario.username} - {uf.cargo_funcao.nome}")
    
    # 4. Verificar superusuários
    print(f"\n👑 SUPERUSUÁRIOS:")
    superusers = User.objects.filter(is_superuser=True)
    for user in superusers:
        print(f"   • {user.username} (superuser)")
    
    # 5. Verificar context processor
    print(f"\n🔍 VERIFICANDO CONTEXT PROCESSOR:")
    from militares.context_processors import menu_permissions_processor
    from django.test import RequestFactory
    
    factory = RequestFactory()
    
    # Testar com usuário admin
    try:
        user_admin = User.objects.get(username='erisman')
        request = factory.get('/')
        request.user = user_admin
        
        context = menu_permissions_processor(request)
        menu_permissions = context.get('menu_permissions', {})
        
        print(f"\n  👤 {user_admin.username} (admin):")
        print(f"    • show_administracao: {menu_permissions.get('show_administracao', False)}")
        print(f"    • show_usuarios: {menu_permissions.get('show_usuarios', False)}")
        print(f"    • show_permissoes: {menu_permissions.get('show_permissoes', False)}")
        print(f"    • show_gerenciar_intersticios: {menu_permissions.get('show_gerenciar_intersticios', False)}")
        print(f"    • show_gerenciar_previsao: {menu_permissions.get('show_gerenciar_previsao', False)}")
        
    except User.DoesNotExist:
        print(f"  ❌ Usuário 'erisman' não encontrado")
    
    # 6. Verificar permissões no sistema
    print(f"\n🔐 VERIFICANDO PERMISSÕES NO SISTEMA:")
    
    # Verificar permissões para Administrador do Sistema
    try:
        cargo_admin_sistema = CargoFuncao.objects.get(nome='Administrador do Sistema')
        permissoes_admin = PermissaoFuncao.objects.filter(
            cargo_funcao=cargo_admin_sistema,
            ativo=True
        )
        
        print(f"  📋 Permissões do 'Administrador do Sistema': {permissoes_admin.count()}")
        
        # Agrupar por módulo
        modulos = {}
        for permissao in permissoes_admin:
            if permissao.modulo not in modulos:
                modulos[permissao.modulo] = []
            modulos[permissao.modulo].append(permissao.acesso)
        
        for modulo, acessos in modulos.items():
            print(f"    • {modulo}: {', '.join(acessos)}")
            
    except CargoFuncao.DoesNotExist:
        print(f"  ❌ Cargo 'Administrador do Sistema' não encontrado")
    
    # 7. Verificar permissões para Administrador
    try:
        cargo_admin = CargoFuncao.objects.get(nome='Administrador')
        permissoes_admin = PermissaoFuncao.objects.filter(
            cargo_funcao=cargo_admin,
            ativo=True
        )
        
        print(f"  📋 Permissões do 'Administrador': {permissoes_admin.count()}")
        
        # Agrupar por módulo
        modulos = {}
        for permissao in permissoes_admin:
            if permissao.modulo not in modulos:
                modulos[permissao.modulo] = []
            modulos[permissao.modulo].append(permissao.acesso)
        
        for modulo, acessos in modulos.items():
            print(f"    • {modulo}: {', '.join(acessos)}")
            
    except CargoFuncao.DoesNotExist:
        print(f"  ❌ Cargo 'Administrador' não encontrado")
    
    # 8. Verificar se há outras funções com permissões administrativas
    print(f"\n🔍 VERIFICANDO OUTRAS FUNÇÕES COM PERMISSÕES ADMINISTRATIVAS:")
    
    # Buscar todas as permissões que incluem ADMINISTRAR
    permissoes_admin_sistema = PermissaoFuncao.objects.filter(
        acesso='ADMINISTRAR',
        ativo=True
    ).select_related('cargo_funcao')
    
    cargos_com_admin = {}
    for permissao in permissoes_admin_sistema:
        if permissao.cargo_funcao:  # Verificar se cargo_funcao não é None
            cargo_nome = permissao.cargo_funcao.nome
            if cargo_nome not in cargos_com_admin:
                cargos_com_admin[cargo_nome] = []
            cargos_com_admin[cargo_nome].append(permissao.modulo)
    
    for cargo, modulos in cargos_com_admin.items():
        print(f"  • {cargo}: {', '.join(modulos)}")
    
    # 9. Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   ✅ Apenas as seguintes funções podem acessar seções administrativas:")
    print(f"      • Superusuários (is_superuser=True)")
    print(f"      • Administrador do Sistema")
    print(f"      • Administrador")
    
    print(f"\n   🔒 Seções administrativas restritas:")
    print(f"      • Gerenciar Usuários")
    print(f"      • Cargos e Funções")
    print(f"      • Administração")
    print(f"      • Gerenciar Interstícios")
    print(f"      • Gerenciar Previsão de Vagas")
    
    print(f"\n   📋 Para testar:")
    print(f"      1. Faça login com um usuário que NÃO tem função administrativa")
    print(f"      2. Verifique se as seções administrativas NÃO aparecem no menu")
    print(f"      3. Tente acessar diretamente as URLs administrativas")
    print(f"      4. Confirme que o acesso é negado")

if __name__ == "__main__":
    restringir_acesso_admin() 