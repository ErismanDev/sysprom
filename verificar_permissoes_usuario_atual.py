#!/usr/bin/env python
"""
Script para verificar as permissões do usuário atual
e identificar problemas de acesso aos quadros de fixação de vagas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, MembroComissao, CargoFuncao

def verificar_permissoes_usuario():
    """Verifica as permissões do usuário atual"""
    
    print("🔍 VERIFICANDO PERMISSÕES DO USUÁRIO ATUAL")
    print("=" * 60)
    
    # Buscar usuário atual (assumindo que é o primeiro superusuário)
    try:
        usuario = User.objects.filter(is_superuser=True).first()
        if not usuario:
            print("❌ Nenhum superusuário encontrado!")
            return
        
        print(f"👤 Usuário: {usuario.get_full_name() or usuario.username}")
        print(f"📧 Email: {usuario.email}")
        print(f"🔑 Superusuário: {usuario.is_superuser}")
        print(f"👨‍💼 Staff: {usuario.is_staff}")
        print(f"✅ Ativo: {usuario.is_active}")
        print()
        
        # Verificar funções do usuário
        print("📋 FUNÇÕES DO USUÁRIO:")
        funcoes = UsuarioFuncao.objects.filter(usuario=usuario, status='ATIVO')
        
        if funcoes.exists():
            for funcao in funcoes:
                print(f"   ✅ {funcao.cargo_funcao.nome} (Status: {funcao.status})")
        else:
            print("   ❌ Nenhuma função ativa encontrada")
        
        print()
        
        # Verificar membros de comissão
        print("👥 MEMBROS DE COMISSÃO:")
        membros = MembroComissao.objects.filter(usuario=usuario, ativo=True)
        
        if membros.exists():
            for membro in membros:
                print(f"   ✅ {membro.comissao.tipo} - {membro.comissao.nome} (Ativo: {membro.ativo})")
                if membro.comissao.eh_presidente(usuario):
                    print(f"      👑 PRESIDENTE da comissão")
        else:
            print("   ❌ Nenhum membro de comissão ativo encontrado")
        
        print()
        
        # Verificar permissões específicas para quadros de fixação
        print("🎯 PERMISSÕES PARA QUADROS DE FIXAÇÃO:")
        
        # Funções especiais que podem acessar quadros de fixação
        cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        
        funcoes_especiais = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
        
        if funcoes_especiais.exists():
            print("   ✅ Tem funções especiais:")
            for funcao in funcoes_especiais:
                print(f"      - {funcao.cargo_funcao.nome}")
        else:
            print("   ❌ NÃO tem funções especiais")
        
        # Verificar se é membro de comissão
        if membros.exists():
            print("   ✅ É membro de comissão")
            
            # Verificar tipos de comissão
            tem_cpo = membros.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros.filter(comissao__tipo='CPP').exists()
            
            if tem_cpo:
                print("      - Membro da CPO (pode ver quadros de oficiais)")
            if tem_cpp:
                print("      - Membro da CPP (pode ver quadros de praças)")
            if tem_cpo and tem_cpp:
                print("      - Membro de ambas (pode ver todos os quadros)")
        else:
            print("   ❌ NÃO é membro de comissão")
        
        print()
        
        # Verificar se deveria ter acesso
        print("🔍 DIAGNÓSTICO:")
        
        tem_acesso = False
        razoes = []
        
        if usuario.is_superuser or usuario.is_staff:
            tem_acesso = True
            razoes.append("Superusuário/Staff")
        
        if funcoes_especiais.exists():
            tem_acesso = True
            razoes.append("Tem funções especiais")
        
        if membros.exists():
            tem_acesso = True
            razoes.append("É membro de comissão")
        
        if tem_acesso:
            print(f"   ✅ DEVERIA ter acesso aos quadros de fixação")
            print(f"   📝 Razões: {', '.join(razoes)}")
        else:
            print("   ❌ NÃO deveria ter acesso aos quadros de fixação")
            print("   📝 Motivo: Não tem permissões necessárias")
        
        print()
        
        # Verificar context processor
        print("🔧 VERIFICAÇÃO DO CONTEXT PROCESSOR:")
        
        # Simular a lógica do context processor
        if funcoes_especiais.exists() or usuario.is_superuser:
            print("   ✅ Context processor deveria mostrar menu (funções especiais)")
        elif membros.exists():
            print("   ✅ Context processor deveria mostrar menu (membro de comissão)")
        else:
            print("   ❌ Context processor NÃO deveria mostrar menu")
        
        print()
        
        # Sugestões
        print("💡 SUGESTÕES:")
        
        if not funcoes_especiais.exists() and not membros.exists():
            print("   1. Adicionar função 'Administrador do Sistema' ao usuário")
            print("   2. Ou adicionar usuário como membro de comissão")
        
        if funcoes_especiais.exists() or membros.exists():
            print("   1. Verificar se o context processor está funcionando corretamente")
            print("   2. Verificar se há cache do navegador")
            print("   3. Verificar se o servidor foi reiniciado após mudanças")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro ao verificar permissões: {e}")

if __name__ == "__main__":
    verificar_permissoes_usuario() 