#!/usr/bin/env python
"""
Script para verificar usuários sem funções vinculadas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import CargoFuncao, UsuarioFuncao

def verificar_usuarios_sem_funcao():
    """
    Verifica usuários que não têm nenhuma função vinculada
    """
    print("🔍 Verificando usuários sem funções vinculadas...")
    print("=" * 70)
    
    # Buscar todos os usuários
    todos_usuarios = User.objects.all()
    
    # Buscar usuários com funções (usando o relacionamento correto)
    usuarios_com_funcao = User.objects.filter(funcoes__isnull=False).distinct()
    
    # Buscar usuários sem funções
    usuarios_sem_funcao = User.objects.filter(funcoes__isnull=True)
    
    print(f"📊 Estatísticas gerais:")
    print(f"   • Total de usuários: {todos_usuarios.count()}")
    print(f"   • Usuários com funções: {usuarios_com_funcao.count()}")
    print(f"   • Usuários sem funções: {usuarios_sem_funcao.count()}")
    print()
    
    if usuarios_sem_funcao.exists():
        print("❌ **USUÁRIOS SEM FUNÇÕES VINCULADAS:**")
        print()
        
        for i, usuario in enumerate(usuarios_sem_funcao, 1):
            print(f"**{i}. {usuario.username.upper()}**")
            print(f"   • **Username**: `{usuario.username}`")
            print(f"   • **Nome completo**: {usuario.get_full_name()}")
            print(f"   • **Email**: {usuario.email}")
            print(f"   • **Status**: {'✅ Ativo' if usuario.is_active else '❌ Inativo'}")
            print(f"   • **Superusuário**: {'✅ Sim' if usuario.is_superuser else '❌ Não'}")
            print(f"   • **Staff**: {'✅ Sim' if usuario.is_staff else '❌ Não'}")
            
            # Verificar se tem militar vinculado
            if hasattr(usuario, 'militar') and usuario.militar:
                print(f"   • **Militar vinculado**: {usuario.militar.nome_completo}")
                print(f"   • **Posto**: {usuario.militar.posto_graduacao}")
            else:
                print(f"   • **Militar vinculado**: Nenhum")
            
            print()
    
    else:
        print("✅ Todos os usuários já têm funções vinculadas!")
    
    # Verificar funções disponíveis
    print("🔧 **FUNÇÕES DISPONÍVEIS NO SISTEMA:**")
    print()
    
    funcoes_disponiveis = CargoFuncao.objects.all().order_by('nome')
    
    for i, funcao in enumerate(funcoes_disponiveis, 1):
        print(f"**{i}. {funcao.nome}**")
        print(f"   • **ID**: {funcao.id}")
        print(f"   • **Descrição**: {funcao.descricao}")
        print(f"   • **Ativo**: {'✅ Sim' if funcao.ativo else '❌ Não'}")
        print()
    
    return usuarios_sem_funcao, funcoes_disponiveis

def verificar_funcao_padrao():
    """
    Verifica se existe uma função padrão para usuários
    """
    print("🔍 Verificando função padrão para usuários...")
    print("=" * 50)
    
    # Buscar funções que podem ser padrão
    funcoes_padrao = CargoFuncao.objects.filter(
        nome__icontains='padrão'
    ).order_by('nome')
    
    if funcoes_padrao.exists():
        print("✅ **FUNÇÕES PADRÃO ENCONTRADAS:**")
        print()
        
        for funcao in funcoes_padrao:
            print(f"**{funcao.nome}**")
            print(f"   • **ID**: {funcao.id}")
            print(f"   • **Descrição**: {funcao.descricao}")
            print(f"   • **Ativo**: {'✅ Sim' if funcao.ativo else '❌ Não'}")
            print()
        
        return funcoes_padrao.first()
    
    else:
        print("❌ Nenhuma função padrão encontrada!")
        print("💡 Será necessário criar ou escolher uma função padrão")
        return None

def main():
    """
    Função principal
    """
    usuarios_sem_funcao, funcoes_disponiveis = verificar_usuarios_sem_funcao()
    print()
    funcao_padrao = verificar_funcao_padrao()
    
    print("=" * 70)
    print("📋 **RESUMO:**")
    print(f"• Usuários sem funções: {usuarios_sem_funcao.count()}")
    print(f"• Funções disponíveis: {funcoes_disponiveis.count()}")
    
    if funcao_padrao:
        print(f"• Função padrão sugerida: {funcao_padrao.nome}")
    else:
        print("• Função padrão: Não encontrada")

if __name__ == '__main__':
    main() 