#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, MembroComissao, ComissaoPromocao

def diagnosticar_comissoes():
    print("=== DIAGNÓSTICO DE COMISSÕES ===\n")
    
    # Verificar todas as comissões
    print("1. COMISSÕES EXISTENTES:")
    comissoes = ComissaoPromocao.objects.all()
    for comissao in comissoes:
        print(f"   • {comissao.nome} (ID: {comissao.pk}, Tipo: {comissao.tipo}, Status: {comissao.status})")
        membros = comissao.membros.all()
        print(f"     - Membros: {membros.count()}")
        for membro in membros:
            print(f"       * {membro.militar.nome_completo} (Usuário: {membro.usuario}, Ativo: {membro.ativo})")
    print()
    
    # Verificar usuários com funções de comissão
    print("2. USUÁRIOS COM FUNÇÕES DE COMISSÃO:")
    funcoes_comissao = ['CPO', 'CPP', 'Membro da CPO', 'Membro da CPP', 'Presidente da CPO', 'Presidente da CPP']
    usuarios_com_funcao = UsuarioFuncao.objects.filter(
        cargo_funcao__nome__in=funcoes_comissao,
        status='ATIVO'
    ).select_related('usuario', 'cargo_funcao')
    
    for uf in usuarios_com_funcao:
        print(f"   • {uf.usuario.username} - {uf.cargo_funcao.nome}")
    print()
    
    # Verificar membros de comissão
    print("3. MEMBROS DE COMISSÃO:")
    membros = MembroComissao.objects.all().select_related('usuario', 'militar', 'comissao')
    for membro in membros:
        print(f"   • {membro.militar.nome_completo} - Comissão: {membro.comissao.nome} - Usuário: {membro.usuario} - Ativo: {membro.ativo}")
    print()
    
    # Testar com um usuário específico
    print("4. TESTE COM USUÁRIO ADMIN:")
    try:
        user_admin = User.objects.get(username='admin')
        print(f"   • Usuário: {user_admin.username}")
        print(f"   • is_superuser: {user_admin.is_superuser}")
        print(f"   • is_staff: {user_admin.is_staff}")
        
        # Verificar funções
        funcoes = UsuarioFuncao.objects.filter(usuario=user_admin, status='ATIVO')
        print(f"   • Funções ativas: {funcoes.count()}")
        for f in funcoes:
            print(f"     - {f.cargo_funcao.nome}")
        
        # Verificar membros de comissão
        membros_admin = MembroComissao.objects.filter(usuario=user_admin, ativo=True)
        print(f"   • Membros de comissão: {membros_admin.count()}")
        for m in membros_admin:
            print(f"     - {m.comissao.nome} ({m.comissao.tipo})")
        
        # Simular a lógica da view
        cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        funcoes_ativas = user_admin.funcoes.filter(
            cargo_funcao__nome__in=cargos_especiais,
            status='ATIVO',
        )
        print(f"   • Tem funções especiais: {funcoes_ativas.exists()}")
        print(f"   • Deveria ver todas as comissões: {funcoes_ativas.exists() or user_admin.is_superuser or user_admin.is_staff}")
        
    except User.DoesNotExist:
        print("   • Usuário admin não encontrado")
    
    print("\n=== FIM DO DIAGNÓSTICO ===")

if __name__ == '__main__':
    diagnosticar_comissoes() 