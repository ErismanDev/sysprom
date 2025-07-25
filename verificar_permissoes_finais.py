#!/usr/bin/env python
"""
Script final para verificar todas as permissões do sistema
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from militares.models import UsuarioFuncao, CargoFuncao
from militares.context_processors import menu_permissions_processor
from militares.permissoes_simples import *

def verificar_permissoes_finais():
    """Verifica todas as permissões do sistema"""
    
    print("🔧 VERIFICAÇÃO FINAL DE PERMISSÕES")
    print("=" * 60)
    
    # 1. Verificar usuário admin
    try:
        user_admin = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        return
    
    print(f"\n1️⃣ USUÁRIO ADMIN:")
    print(f"   • Username: {user_admin.username}")
    print(f"   • Nome: {user_admin.get_full_name()}")
    print(f"   • is_superuser: {user_admin.is_superuser}")
    print(f"   • is_staff: {user_admin.is_staff}")
    print(f"   • is_active: {user_admin.is_active}")
    
    # 2. Verificar funções ativas
    funcoes = UsuarioFuncao.objects.filter(usuario=user_admin, status='ATIVO')
    print(f"\n2️⃣ FUNÇÕES ATIVAS:")
    for funcao in funcoes:
        print(f"   • {funcao.cargo_funcao.nome} (ID: {funcao.id})")
    
    # 3. Verificar funções especiais
    funcoes_especiais = funcoes.filter(
        cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    )
    print(f"\n3️⃣ FUNÇÕES ESPECIAIS:")
    if funcoes_especiais.exists():
        for funcao in funcoes_especiais:
            print(f"   ✅ {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função especial encontrada")
    
    # 4. Testar permissões específicas
    print(f"\n4️⃣ PERMISSÕES ESPECÍFICAS:")
    print(f"   • pode_editar_militares: {pode_editar_militares(user_admin)}")
    print(f"   • pode_editar_fichas_conceito: {pode_editar_fichas_conceito(user_admin)}")
    print(f"   • pode_gerenciar_quadros_vagas: {pode_gerenciar_quadros_vagas(user_admin)}")
    print(f"   • pode_gerenciar_comissoes: {pode_gerenciar_comissoes(user_admin)}")
    print(f"   • pode_gerenciar_usuarios: {pode_gerenciar_usuarios(user_admin)}")
    print(f"   • pode_assinar_documentos: {pode_assinar_documentos(user_admin)}")
    print(f"   • pode_visualizar_tudo: {pode_visualizar_tudo(user_admin)}")
    
    # 5. Testar context processor
    print(f"\n5️⃣ CONTEXT PROCESSOR:")
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user_admin
    
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
    
    # 6. Verificar acesso aos módulos principais
    principais = [
        menu_permissions.get('show_quadros_acesso', False),
        menu_permissions.get('show_quadros_fixacao', False),
        menu_permissions.get('show_comissoes', False)
    ]
    
    print(f"\n6️⃣ ACESSO AOS MÓDULOS PRINCIPAIS:")
    print(f"   • Quadros de Acesso: {principais[0]}")
    print(f"   • Quadros de Fixação: {principais[1]}")
    print(f"   • Comissões: {principais[2]}")
    
    # 7. Resultado final
    print(f"\n7️⃣ RESULTADO FINAL:")
    
    if all(principais):
        print("   ✅ SUCESSO TOTAL! Usuário admin tem acesso completo")
        print("   🎯 Agora você deve conseguir ver no navegador:")
        print("      • Quadros de Acesso")
        print("      • Quadros de Fixação de Vagas")
        print("      • Comissões")
        print("      • Todos os outros módulos administrativos")
        print("   💡 Se ainda não aparecer no navegador:")
        print("      • Limpe o cache do navegador (Ctrl+F5)")
        print("      • Faça logout e login novamente")
        print("      • Verifique se o servidor está rodando")
    else:
        print("   ❌ PROBLEMA! Usuário admin ainda não tem acesso total")
        print("   🔧 Verificar configurações novamente")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    verificar_permissoes_finais() 