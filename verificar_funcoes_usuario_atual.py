#!/usr/bin/env python
"""
Script para verificar as funções do usuário atual e identificar problemas de permissão
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao, QuadroFixacaoVagas

def verificar_funcoes_usuario(username):
    """Verifica as funções de um usuário específico"""
    print(f"🔍 VERIFICANDO FUNÇÕES DO USUÁRIO: {username}")
    print("=" * 60)
    
    try:
        usuario = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ Usuário '{username}' não encontrado!")
        return None
    
    print(f"👤 Usuário: {usuario.get_full_name()} ({usuario.username})")
    print(f"📧 Email: {usuario.email}")
    print(f"🔐 Superusuário: {usuario.is_superuser}")
    print(f"👨‍💼 Staff: {usuario.is_staff}")
    print(f"✅ Ativo: {usuario.is_active}")
    
    # Verificar funções
    funcoes = UsuarioFuncao.objects.filter(
        usuario=usuario,
        status='ATIVO'
    ).select_related('cargo_funcao')
    
    print(f"\n🏷️ Funções ativas ({funcoes.count()}):")
    if funcoes.exists():
        for funcao in funcoes:
            print(f"   • {funcao.cargo_funcao.nome} (desde {funcao.data_inicio})")
    else:
        print("   Nenhuma função ativa encontrada")
    
    # Verificar cargos especiais
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    funcoes_especiais = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
    
    print(f"\n⭐ Cargos especiais ({funcoes_especiais.count()}):")
    if funcoes_especiais.exists():
        for funcao in funcoes_especiais:
            print(f"   ✅ {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhum cargo especial encontrado")
    
    # Testar permissão do decorator
    print(f"\n🔐 TESTE DO DECORATOR @cargos_especiais_required:")
    
    # Simular a verificação do decorator
    funcoes_especiais_decorator = UsuarioFuncao.objects.filter(
        usuario=usuario,
        status='ATIVO',
        cargo_funcao__nome__in=cargos_especiais
    )
    
    tem_cargo_especial = funcoes_especiais_decorator.exists()
    eh_superuser = usuario.is_superuser
    eh_staff = usuario.is_staff
    
    print(f"   Tem cargo especial: {tem_cargo_especial}")
    print(f"   É superusuário: {eh_superuser}")
    print(f"   É staff: {eh_staff}")
    
    # Verificar se deveria ter acesso
    deveria_ter_acesso = eh_superuser or eh_staff or tem_cargo_especial
    print(f"   Deveria ter acesso: {deveria_ter_acesso}")
    
    if not deveria_ter_acesso:
        print("   ❌ PROBLEMA: Usuário não tem permissão para excluir quadros!")
        print("   💡 Solução: Adicionar uma das seguintes funções:")
        for cargo in cargos_especiais:
            print(f"      - {cargo}")
    else:
        print("   ✅ Usuário tem permissão para excluir quadros")
    
    return usuario

def verificar_quadros_disponiveis():
    """Verifica quadros disponíveis para exclusão"""
    print(f"\n📋 QUADROS DE FIXAÇÃO DISPONÍVEIS:")
    print("=" * 60)
    
    quadros = QuadroFixacaoVagas.objects.all().order_by('-data_criacao')
    
    if quadros.exists():
        for quadro in quadros:
            print(f"   • ID {quadro.pk}: {quadro.titulo} ({quadro.tipo}) - {quadro.status}")
    else:
        print("   Nenhum quadro encontrado")
    
    return quadros

def verificar_cargos_cadastrados():
    """Verifica todos os cargos cadastrados no sistema"""
    print(f"\n🏷️ TODOS OS CARGOS CADASTRADOS:")
    print("=" * 60)
    
    cargos = CargoFuncao.objects.all().order_by('nome')
    
    if cargos.exists():
        for cargo in cargos:
            usuarios_cargo = UsuarioFuncao.objects.filter(
                cargo_funcao=cargo,
                status='ATIVO'
            ).count()
            print(f"   • {cargo.nome}: {usuarios_cargo} usuários ativos")
    else:
        print("   Nenhum cargo cadastrado")

def main():
    print("🔧 VERIFICADOR DE PERMISSÕES - QUADROS DE FIXAÇÃO")
    print("=" * 70)
    
    # Verificar usuário atual (você pode alterar o username aqui)
    username = input("Digite o username do usuário para verificar: ").strip()
    
    if not username:
        print("❌ Username não informado!")
        return
    
    # Verificar funções do usuário
    usuario = verificar_funcoes_usuario(username)
    
    if usuario:
        # Verificar quadros disponíveis
        verificar_quadros_disponiveis()
        
        # Verificar cargos cadastrados
        verificar_cargos_cadastrados()
        
        print(f"\n" + "=" * 70)
        print("💡 RESUMO:")
        print("   Para excluir quadros de fixação, o usuário precisa ter:")
        print("   - Função 'Diretor de Gestão de Pessoas' OU")
        print("   - Função 'Chefe da Seção de Promoções' OU")
        print("   - Função 'Administrador do Sistema' OU")
        print("   - Ser superusuário OU")
        print("   - Ser staff")
        
        if not usuario.is_superuser and not usuario.is_staff:
            funcoes_especiais = UsuarioFuncao.objects.filter(
                usuario=usuario,
                status='ATIVO',
                cargo_funcao__nome__in=['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
            )
            
            if not funcoes_especiais.exists():
                print(f"\n❌ PROBLEMA IDENTIFICADO:")
                print(f"   O usuário '{username}' não tem nenhuma das funções necessárias!")
                print(f"   Adicione uma das funções especiais para permitir exclusão de quadros.")

if __name__ == "__main__":
    main() 