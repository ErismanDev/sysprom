#!/usr/bin/env python
"""
Script para testar o context processor diretamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from militares.context_processors import menu_permissions_processor

def testar_context_processor():
    """Testa o context processor diretamente"""
    
    print("🔧 TESTANDO CONTEXT PROCESSOR")
    print("=" * 60)
    
    # Criar request factory
    factory = RequestFactory()
    
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        return
    
    # Criar request mock
    request = factory.get('/')
    request.user = user
    
    print(f"\n1️⃣ USUÁRIO: {user.username}")
    print(f"   • is_superuser: {user.is_superuser}")
    print(f"   • is_staff: {user.is_staff}")
    
    # Verificar funções
    from militares.models import UsuarioFuncao
    funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
    print(f"\n2️⃣ FUNÇÕES ATIVAS:")
    for funcao in funcoes:
        print(f"   • {funcao.cargo_funcao.nome}")
    
    # Testar context processor
    print(f"\n3️⃣ RESULTADO DO CONTEXT PROCESSOR:")
    try:
        context = menu_permissions_processor(request)
        menu_permissions = context.get('menu_permissions', {})
        
        print(f"   • show_dashboard: {menu_permissions.get('show_dashboard', False)}")
        print(f"   • show_efetivo: {menu_permissions.get('show_efetivo', False)}")
        print(f"   • show_usuarios: {menu_permissions.get('show_usuarios', False)}")
        print(f"   • show_permissoes: {menu_permissions.get('show_permissoes', False)}")
        print(f"   • show_fichas_oficiais: {menu_permissions.get('show_fichas_oficiais', False)}")
        print(f"   • show_fichas_pracas: {menu_permissions.get('show_fichas_pracas', False)}")
        print(f"   • show_quadros_acesso: {menu_permissions.get('show_quadros_acesso', False)}")
        print(f"   • show_quadros_fixacao: {menu_permissions.get('show_quadros_fixacao', False)}")
        print(f"   • show_promocoes: {menu_permissions.get('show_promocoes', False)}")
        print(f"   • show_calendarios: {menu_permissions.get('show_calendarios', False)}")
        print(f"   • show_comissoes: {menu_permissions.get('show_comissoes', False)}")
        print(f"   • show_meus_votos: {menu_permissions.get('show_meus_votos', False)}")
        print(f"   • show_administracao: {menu_permissions.get('show_administracao', False)}")
        print(f"   • is_special: {menu_permissions.get('is_special', False)}")
        
        # Verificar se tem acesso aos módulos principais
        principais = [
            menu_permissions.get('show_quadros_acesso', False),
            menu_permissions.get('show_quadros_fixacao', False),
            menu_permissions.get('show_comissoes', False)
        ]
        
        print(f"\n4️⃣ ACESSO AOS MÓDULOS PRINCIPAIS:")
        print(f"   • Quadros de Acesso: {principais[0]}")
        print(f"   • Quadros de Fixação: {principais[1]}")
        print(f"   • Comissões: {principais[2]}")
        
        if all(principais):
            print(f"\n✅ SUCESSO! Usuário tem acesso total")
        else:
            print(f"\n❌ PROBLEMA! Usuário não tem acesso total")
            
    except Exception as e:
        print(f"❌ ERRO no context processor: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    testar_context_processor() 