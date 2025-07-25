#!/usr/bin/env python
"""
Script para verificar permissões do usuário admin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, MembroComissao, ComissaoPromocao

def verificar_permissoes_usuario(username):
    """Verifica todas as permissões de um usuário"""
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado!")
        return
    
    print(f"\n🔍 VERIFICANDO PERMISSÕES DO USUÁRIO: {user.get_full_name()} ({username})")
    print("=" * 80)
    
    # 1. Verificar se é superusuário/staff
    print(f"\n1️⃣ STATUS DO USUÁRIO:")
    print(f"   • is_superuser: {user.is_superuser}")
    print(f"   • is_staff: {user.is_staff}")
    print(f"   • is_active: {user.is_active}")
    
    # 2. Verificar funções ativas
    print(f"\n2️⃣ FUNÇÕES ATIVAS:")
    funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
    if funcoes.exists():
        for funcao in funcoes:
            print(f"   • {funcao.cargo_funcao.nome} (desde {funcao.data_inicio})")
    else:
        print("   ❌ Nenhuma função ativa encontrada!")
    
    # 3. Verificar se tem funções especiais
    funcoes_especiais = funcoes.filter(
        cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema']
    )
    print(f"\n3️⃣ FUNÇÕES ESPECIAIS:")
    if funcoes_especiais.exists():
        for funcao in funcoes_especiais:
            print(f"   ✅ {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função especial encontrada")
    
    # 4. Verificar membros de comissão
    print(f"\n4️⃣ MEMBROS DE COMISSÃO:")
    membros = MembroComissao.objects.filter(usuario=user, ativo=True, comissao__status='ATIVA')
    if membros.exists():
        for membro in membros:
            print(f"   • {membro.comissao.tipo} - {membro.comissao.nome}")
            print(f"     Cargo: {membro.cargo}")
            print(f"     Presidente: {membro.eh_presidente()}")
    else:
        print("   ❌ Nenhum membro de comissão ativo encontrado")
    
    # 5. Verificar permissões de menu (simular context processor)
    print(f"\n5️⃣ PERMISSÕES DE MENU (simulando context processor):")
    
    # Verificar se é usuário comum
    is_consultor = funcoes.filter(cargo_funcao__nome='Usuário').exists()
    
    # Verificar se tem funções especiais
    tem_funcoes_especiais = funcoes_especiais.exists()
    
    # Verificar se é membro de comissão
    is_cpo = membros.filter(comissao__tipo='CPO').exists()
    is_cpp = membros.filter(comissao__tipo='CPP').exists()
    
    print(f"   • is_consultor: {is_consultor}")
    print(f"   • tem_funcoes_especiais: {tem_funcoes_especiais}")
    print(f"   • is_cpo: {is_cpo}")
    print(f"   • is_cpp: {is_cpp}")
    
    # Determinar permissões baseado na lógica do context processor
    if is_consultor:
        print(f"   ❌ Usuário comum - acesso muito limitado")
        show_quadros_acesso = False
        show_quadros_fixacao = False
        show_comissoes = False
    elif tem_funcoes_especiais or user.is_superuser:
        print(f"   ✅ Usuário especial - acesso total")
        show_quadros_acesso = True
        show_quadros_fixacao = True
        show_comissoes = True
    elif is_cpo or is_cpp:
        print(f"   ✅ Membro de comissão - acesso limitado")
        show_quadros_acesso = False
        show_quadros_fixacao = True
        show_comissoes = True
    else:
        print(f"   ❌ Usuário comum - acesso limitado")
        show_quadros_acesso = False
        show_quadros_fixacao = False
        show_comissoes = False
    
    print(f"\n6️⃣ RESULTADO DAS PERMISSÕES:")
    print(f"   • show_quadros_acesso: {show_quadros_acesso}")
    print(f"   • show_quadros_fixacao: {show_quadros_fixacao}")
    print(f"   • show_comissoes: {show_comissoes}")
    
    # 6. Recomendações
    print(f"\n7️⃣ RECOMENDAÇÕES:")
    
    if not show_quadros_acesso and not show_quadros_fixacao and not show_comissoes:
        print("   ❌ PROBLEMA: Usuário não tem acesso aos módulos principais!")
        
        if not tem_funcoes_especiais and not user.is_superuser:
            print("   💡 SOLUÇÃO 1: Tornar usuário superusuário")
            print("      python manage.py shell")
            print(f"      user = User.objects.get(username='{username}')")
            print(f"      user.is_superuser = True")
            print(f"      user.save()")
        
        if not funcoes_especiais.exists():
            print("   💡 SOLUÇÃO 2: Adicionar função especial")
            print("      - Diretor de Gestão de Pessoas")
            print("      - Chefe da Seção de Promoções") 
            print("      - Administrador do Sistema")
        
        if not membros.exists():
            print("   💡 SOLUÇÃO 3: Adicionar como membro de comissão")
            print("      - CPO (Comissão de Promoção de Oficiais)")
            print("      - CPP (Comissão de Promoção de Praças)")
    
    elif show_quadros_fixacao and show_comissoes:
        print("   ✅ Usuário tem acesso adequado aos módulos principais")
    
    print(f"\n" + "=" * 80)

def main():
    """Função principal"""
    print("🔧 VERIFICADOR DE PERMISSÕES DE USUÁRIO")
    print("=" * 80)
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Digite o username do usuário: ")
    
    verificar_permissoes_usuario(username)

if __name__ == "__main__":
    main() 