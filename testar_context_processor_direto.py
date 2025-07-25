#!/usr/bin/env python
"""
Script para testar o context processor diretamente
e verificar se está retornando as permissões corretas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from militares.context_processors import menu_permissions_processor

def testar_context_processor():
    """Testa o context processor diretamente"""
    
    print("🧪 TESTANDO CONTEXT PROCESSOR DIRETAMENTE")
    print("=" * 60)
    
    # Criar uma request factory
    factory = RequestFactory()
    
    # Buscar usuário superusuário
    usuario = User.objects.filter(is_superuser=True).first()
    if not usuario:
        print("❌ Nenhum superusuário encontrado!")
        return
    
    print(f"👤 Testando com usuário: {usuario.get_full_name() or usuario.username}")
    print(f"🔑 Superusuário: {usuario.is_superuser}")
    print(f"👨‍💼 Staff: {usuario.is_staff}")
    print()
    
    # Criar uma request
    request = factory.get('/')
    request.user = usuario
    
    # Chamar o context processor
    try:
        context = menu_permissions_processor(request)
        menu_permissions = context.get('menu_permissions', {})
        
        print("📋 PERMISSÕES RETORNADAS PELO CONTEXT PROCESSOR:")
        print(f"   • show_dashboard: {menu_permissions.get('show_dashboard', False)}")
        print(f"   • show_efetivo: {menu_permissions.get('show_efetivo', False)}")
        print(f"   • show_inativos: {menu_permissions.get('show_inativos', False)}")
        print(f"   • show_usuarios: {menu_permissions.get('show_usuarios', False)}")
        print(f"   • show_permissoes: {menu_permissions.get('show_permissoes', False)}")
        print(f"   • show_fichas_oficiais: {menu_permissions.get('show_fichas_oficiais', False)}")
        print(f"   • show_fichas_pracas: {menu_permissions.get('show_fichas_pracas', False)}")
        print(f"   • show_quadros_acesso: {menu_permissions.get('show_quadros_acesso', False)}")
        print(f"   • show_quadros_fixacao: {menu_permissions.get('show_quadros_fixacao', False)}")
        print(f"   • show_almanaques: {menu_permissions.get('show_almanaques', False)}")
        print(f"   • show_promocoes: {menu_permissions.get('show_promocoes', False)}")
        print(f"   • show_calendarios: {menu_permissions.get('show_calendarios', False)}")
        print(f"   • show_comissoes: {menu_permissions.get('show_comissoes', False)}")
        print(f"   • show_meus_votos: {menu_permissions.get('show_meus_votos', False)}")
        print(f"   • show_intersticios: {menu_permissions.get('show_intersticios', False)}")
        print(f"   • show_gerenciar_intersticios: {menu_permissions.get('show_gerenciar_intersticios', False)}")
        print(f"   • show_gerenciar_previsao: {menu_permissions.get('show_gerenciar_previsao', False)}")
        print(f"   • show_administracao: {menu_permissions.get('show_administracao', False)}")
        print(f"   • is_cpo: {menu_permissions.get('is_cpo', False)}")
        print(f"   • is_cpp: {menu_permissions.get('is_cpp', False)}")
        print(f"   • is_special: {menu_permissions.get('is_special', False)}")
        print(f"   • is_consultor: {menu_permissions.get('is_consultor', False)}")
        
        print()
        
        # Verificar especificamente o menu de quadros de fixação
        show_quadros_fixacao = menu_permissions.get('show_quadros_fixacao', False)
        
        if show_quadros_fixacao:
            print("✅ show_quadros_fixacao = True - Menu deveria aparecer")
        else:
            print("❌ show_quadros_fixacao = False - Menu NÃO deveria aparecer")
        
        print()
        
        # Verificar se há problemas
        if not show_quadros_fixacao and (usuario.is_superuser or usuario.is_staff):
            print("🚨 PROBLEMA IDENTIFICADO:")
            print("   - Usuário é superusuário/staff mas show_quadros_fixacao = False")
            print("   - Isso indica um problema no context processor")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro ao testar context processor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_context_processor() 