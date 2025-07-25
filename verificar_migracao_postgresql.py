#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao, MembroComissao, ComissaoPromocao

def verificar_migracao_postgresql():
    print("=== VERIFICAÇÃO DA MIGRAÇÃO PARA POSTGRESQL ===\n")
    
    # 1. Verificar usuários
    print("1. USUÁRIOS:")
    usuarios = User.objects.all()
    print(f"   Total de usuários: {usuarios.count()}")
    for user in usuarios:
        print(f"   • {user.username} - {user.get_full_name()} - Ativo: {user.is_active}")
    print()
    
    # 2. Verificar cargos/funções
    print("2. CARGOS/FUNÇÕES:")
    cargos = CargoFuncao.objects.all()
    print(f"   Total de cargos: {cargos.count()}")
    for cargo in cargos:
        print(f"   • {cargo.nome}")
    print()
    
    # 3. Verificar funções de usuários
    print("3. FUNÇÕES DE USUÁRIOS:")
    funcoes = UsuarioFuncao.objects.all()
    print(f"   Total de funções: {funcoes.count()}")
    for funcao in funcoes:
        print(f"   • {funcao.usuario.username} - {funcao.cargo_funcao.nome} - Status: {funcao.status}")
    print()
    
    # 4. Verificar comissões
    print("4. COMISSÕES:")
    comissoes = ComissaoPromocao.objects.all()
    print(f"   Total de comissões: {comissoes.count()}")
    for comissao in comissoes:
        print(f"   • {comissao.nome} ({comissao.tipo}) - Status: {comissao.status}")
    print()
    
    # 5. Verificar membros de comissão
    print("5. MEMBROS DE COMISSÃO:")
    membros = MembroComissao.objects.all()
    print(f"   Total de membros: {membros.count()}")
    for membro in membros:
        print(f"   • {membro.militar.nome_completo} - {membro.comissao.nome} - Usuário: {membro.usuario} - Ativo: {membro.ativo}")
    print()
    
    # 6. Verificar funções especiais
    print("6. FUNÇÕES ESPECIAIS:")
    funcoes_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    for funcao_nome in funcoes_especiais:
        try:
            cargo = CargoFuncao.objects.get(nome=funcao_nome)
            usuarios_com_funcao = UsuarioFuncao.objects.filter(cargo_funcao=cargo, status='ATIVO')
            print(f"   • {funcao_nome}: {usuarios_com_funcao.count()} usuários")
            for uf in usuarios_com_funcao:
                print(f"     - {uf.usuario.username}")
        except CargoFuncao.DoesNotExist:
            print(f"   • {funcao_nome}: ❌ NÃO EXISTE")
    print()
    
    # 7. Verificar usuário admin
    print("7. USUÁRIO ADMIN:")
    try:
        admin = User.objects.get(username='admin')
        print(f"   • Username: {admin.username}")
        print(f"   • is_superuser: {admin.is_superuser}")
        print(f"   • is_staff: {admin.is_staff}")
        print(f"   • is_active: {admin.is_active}")
        
        funcoes_admin = UsuarioFuncao.objects.filter(usuario=admin, status='ATIVO')
        print(f"   • Funções ativas: {funcoes_admin.count()}")
        for f in funcoes_admin:
            print(f"     - {f.cargo_funcao.nome}")
            
    except User.DoesNotExist:
        print("   • ❌ Usuário admin não encontrado")
    
    print("\n=== FIM DA VERIFICAÇÃO ===")

if __name__ == '__main__':
    verificar_migracao_postgresql() 