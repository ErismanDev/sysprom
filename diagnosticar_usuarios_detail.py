#!/usr/bin/env python
"""
Script para diagnosticar problemas na página de detalhes do usuário
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from militares.models import Militar

def diagnosticar_usuarios_detail():
    """Diagnostica problemas na página de detalhes do usuário"""
    
    print("🔍 DIAGNÓSTICO - PÁGINA DE DETALHES DO USUÁRIO")
    print("=" * 60)
    
    # 1. Verificar usuário ID 1581
    try:
        user = User.objects.get(id=1581)
        print(f"✅ Usuário encontrado: {user.username} (ID: {user.id})")
        print(f"   Nome: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
    except User.DoesNotExist:
        print("❌ Usuário ID 1581 não encontrado")
        return
    
    # 2. Verificar grupos do usuário
    grupos = user.groups.all()
    print(f"\n📋 GRUPOS DO USUÁRIO ({grupos.count()}):")
    if grupos.exists():
        for grupo in grupos:
            print(f"   ✅ {grupo.name} (ID: {grupo.id})")
            # Verificar permissões do grupo
            perms_grupo = grupo.permissions.all()
            print(f"      Permissões do grupo ({perms_grupo.count()}):")
            for perm in perms_grupo:
                print(f"        - {perm.name} ({perm.codename})")
    else:
        print("   ⚠️ Usuário não pertence a nenhum grupo")
    
    # 3. Verificar permissões diretas do usuário
    perms_diretas = user.user_permissions.all()
    print(f"\n🔐 PERMISSÕES DIRETAS DO USUÁRIO ({perms_diretas.count()}):")
    if perms_diretas.exists():
        for perm in perms_diretas:
            print(f"   ✅ {perm.name} ({perm.codename})")
    else:
        print("   ⚠️ Usuário não tem permissões diretas")
    
    # 4. Verificar todas as permissões (grupos + diretas)
    todas_perms = user.get_all_permissions()
    print(f"\n🎯 TODAS AS PERMISSÕES ({len(todas_perms)}):")
    if todas_perms:
        for perm in sorted(todas_perms):
            print(f"   ✅ {perm}")
    else:
        print("   ⚠️ Usuário não tem nenhuma permissão")
    
    # 5. Verificar se o usuário tem militar associado
    try:
        militar = user.militar
        print(f"\n👤 MILITAR ASSOCIADO:")
        print(f"   ✅ {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
        print(f"   CPF: {militar.cpf}")
        print(f"   Matrícula: {militar.matricula}")
    except Militar.DoesNotExist:
        print(f"\n👤 MILITAR ASSOCIADO:")
        print(f"   ⚠️ Usuário não tem militar associado")
    
    # 6. Verificar grupos disponíveis no sistema
    todos_grupos = Group.objects.all()
    print(f"\n📚 GRUPOS DISPONÍVEIS NO SISTEMA ({todos_grupos.count()}):")
    for grupo in todos_grupos:
        print(f"   📋 {grupo.name} (ID: {grupo.id})")
        perms_count = grupo.permissions.count()
        print(f"      Permissões: {perms_count}")
    
    # 7. Verificar permissões disponíveis
    content_types = ContentType.objects.filter(app_label='militares')
    perms_militares = Permission.objects.filter(content_type__in=content_types)
    print(f"\n🔑 PERMISSÕES DISPONÍVEIS (militares) ({perms_militares.count()}):")
    for perm in perms_militares[:10]:  # Mostrar apenas as primeiras 10
        print(f"   🔐 {perm.name} ({perm.codename}) - {perm.content_type.model}")
    
    if perms_militares.count() > 10:
        print(f"   ... e mais {perms_militares.count() - 10} permissões")
    
    # 8. Verificar template
    print(f"\n📄 VERIFICANDO TEMPLATE:")
    try:
        with open('militares/templates/usuarios/detail.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        if 'grupos' in template_content.lower():
            print(f"   ✅ Template contém referência a grupos")
        else:
            print(f"   ❌ Template não contém referência a grupos")
        
        if 'permissoes' in template_content.lower() or 'permissions' in template_content.lower():
            print(f"   ✅ Template contém referência a permissões")
        else:
            print(f"   ❌ Template não contém referência a permissões")
        
        # Verificar se há cards específicos
        if 'card' in template_content.lower():
            print(f"   ✅ Template contém cards")
        else:
            print(f"   ❌ Template não contém cards")
            
    except FileNotFoundError:
        print(f"   ❌ Template detail.html não encontrado")
    
    # 9. Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   📊 Usuário tem {grupos.count()} grupos")
    print(f"   🔐 Usuário tem {perms_diretas.count()} permissões diretas")
    print(f"   🎯 Usuário tem {len(todas_perms)} permissões totais")
    
    if grupos.count() == 0 and perms_diretas.count() == 0:
        print(f"\n⚠️ PROBLEMA IDENTIFICADO:")
        print(f"   O usuário não tem grupos nem permissões, por isso os cards estão vazios")
        print(f"   Solução: Adicionar o usuário a grupos ou dar permissões diretas")
    
    print(f"\n🔧 PRÓXIMOS PASSOS:")
    print(f"   1. Verificar se a view está passando os dados corretamente")
    print(f"   2. Verificar se o template está renderizando os cards")
    print(f"   3. Adicionar grupos/permissões ao usuário se necessário")

if __name__ == "__main__":
    diagnosticar_usuarios_detail() 