#!/usr/bin/env python
"""
Script para forçar atualização do menu e limpar cache
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.core.cache import cache
from django.test import RequestFactory
from militares.context_processors import menu_permissions_processor

def forcar_atualizacao_menu():
    """Força a atualização do menu e limpa cache"""
    
    print("🔄 FORÇANDO ATUALIZAÇÃO DO MENU")
    print("=" * 60)
    
    # Limpar cache do Django
    print("🧹 Limpando cache do Django...")
    cache.clear()
    print("✅ Cache limpo!")
    
    # Testar context processor
    print("🔍 Testando context processor...")
    factory = RequestFactory()
    request = factory.get('/')
    
    # Simular usuário admin
    from django.contrib.auth.models import User
    try:
        user_admin = User.objects.get(username='erisman')
        request.user = user_admin
        print(f"✅ Usuário simulado: {user_admin.username}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
        return
    
    # Chamar context processor
    context = menu_permissions_processor(request)
    menu_permissions = context.get('menu_permissions', {})
    
    print("📋 Permissões do menu:")
    print(f"   • show_dashboard: {menu_permissions.get('show_dashboard', False)}")
    print(f"   • show_efetivo: {menu_permissions.get('show_efetivo', False)}")
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
    
    # Verificar especificamente almanaques
    show_almanaques = menu_permissions.get('show_almanaques', False)
    
    if show_almanaques:
        print("\n✅ show_almanaques = True - Menu deveria aparecer")
        print("🔍 Verificando se há almanaques no banco...")
        
        from militares.models import AlmanaqueMilitar
        almanaques = AlmanaqueMilitar.objects.filter(ativo=True)
        
        if almanaques.exists():
            print(f"✅ Existem {almanaques.count()} almanaques ativos")
            for almanaque in almanaques:
                print(f"   - {almanaque.titulo} ({almanaque.tipo})")
        else:
            print("❌ Nenhum almanaque ativo encontrado")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Acesse: http://127.0.0.1:8000/militares/")
        print("2. Verifique se o menu 'Almanaques' aparece na sidebar")
        print("3. Se não aparecer, pode ser problema de cache do navegador")
        print("4. Tente Ctrl+F5 para forçar recarregamento")
        
    else:
        print("\n❌ show_almanaques = False - Menu NÃO deveria aparecer")
        print("🔧 Isso indica um problema no context processor")

if __name__ == "__main__":
    forcar_atualizacao_menu() 