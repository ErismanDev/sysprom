#!/usr/bin/env python
"""
Script para testar permissões do usuário admin após correções
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, MembroComissao
from militares.permissoes_simples import *

def testar_permissoes_admin():
    """Testa todas as permissões do usuário admin"""
    
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Usuário 'admin' não encontrado!")
        return
    
    print(f"\n🔧 TESTANDO PERMISSÕES DO USUÁRIO ADMIN")
    print("=" * 60)
    
    # 1. Verificar status do usuário
    print(f"\n1️⃣ STATUS DO USUÁRIO:")
    print(f"   • is_superuser: {user.is_superuser}")
    print(f"   • is_staff: {user.is_staff}")
    print(f"   • is_active: {user.is_active}")
    
    # 2. Verificar funções ativas
    print(f"\n2️⃣ FUNÇÕES ATIVAS:")
    funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
    if funcoes.exists():
        for funcao in funcoes:
            print(f"   • {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função ativa encontrada!")
    
    # 3. Testar permissões específicas
    print(f"\n3️⃣ TESTE DE PERMISSÕES:")
    
    # Testar permissões de edição
    print(f"   • pode_editar_militares: {pode_editar_militares(user)}")
    print(f"   • pode_editar_fichas_conceito: {pode_editar_fichas_conceito(user)}")
    print(f"   • pode_gerenciar_quadros_vagas: {pode_gerenciar_quadros_vagas(user)}")
    print(f"   • pode_gerenciar_comissoes: {pode_gerenciar_comissoes(user)}")
    print(f"   • pode_gerenciar_usuarios: {pode_gerenciar_usuarios(user)}")
    print(f"   • pode_assinar_documentos: {pode_assinar_documentos(user)}")
    print(f"   • pode_visualizar_tudo: {pode_visualizar_tudo(user)}")
    
    # 4. Testar funções especiais
    print(f"\n4️⃣ FUNÇÕES ESPECIAIS:")
    funcoes_especiais = funcoes.filter(
        cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    )
    if funcoes_especiais.exists():
        for funcao in funcoes_especiais:
            print(f"   ✅ {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função especial encontrada")
    
    # 5. Verificar se tem acesso aos módulos principais
    print(f"\n5️⃣ ACESSO AOS MÓDULOS PRINCIPAIS:")
    
    # Simular context processor
    if user.is_superuser or funcoes_especiais.exists():
        print("   ✅ Acesso total (superusuário ou função especial)")
        show_quadros_acesso = True
        show_quadros_fixacao = True
        show_comissoes = True
    else:
        print("   ❌ Acesso limitado")
        show_quadros_acesso = False
        show_quadros_fixacao = False
        show_comissoes = False
    
    print(f"   • show_quadros_acesso: {show_quadros_acesso}")
    print(f"   • show_quadros_fixacao: {show_quadros_fixacao}")
    print(f"   • show_comissoes: {show_comissoes}")
    
    # 6. Resultado final
    print(f"\n6️⃣ RESULTADO FINAL:")
    
    if show_quadros_acesso and show_quadros_fixacao and show_comissoes:
        print("   ✅ SUCESSO! Usuário admin tem acesso total aos módulos principais")
        print("   🎯 Agora você deve conseguir ver:")
        print("      • Quadros de Acesso")
        print("      • Quadros de Fixação de Vagas")
        print("      • Comissões")
        print("      • Todos os outros módulos administrativos")
    else:
        print("   ❌ PROBLEMA! Usuário admin ainda não tem acesso total")
        print("   🔧 Verificar se as correções foram aplicadas corretamente")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    testar_permissoes_admin() 