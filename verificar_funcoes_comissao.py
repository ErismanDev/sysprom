#!/usr/bin/env python
"""
Script para verificar as funções de comissão do usuário
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao

def verificar_funcoes_comissao():
    """Verifica as funções de comissão do usuário"""
    
    print("🔍 VERIFICANDO FUNÇÕES DE COMISSÃO")
    print("=" * 50)
    
    # Buscar usuário superusuário
    usuario = User.objects.filter(is_superuser=True).first()
    if not usuario:
        print("❌ Nenhum superusuário encontrado!")
        return
    
    print(f"👤 Usuário: {usuario.get_full_name() or usuario.username}")
    print()
    
    # Verificar todas as funções do usuário
    funcoes = UsuarioFuncao.objects.filter(usuario=usuario, status='ATIVO')
    
    if funcoes.exists():
        print("📋 TODAS AS FUNÇÕES ATIVAS:")
        for funcao in funcoes:
            print(f"   ✅ {funcao.cargo_funcao.nome} (Status: {funcao.status})")
        print()
        
        # Verificar funções de comissão
        funcoes_comissao = funcoes.filter(cargo_funcao__nome__in=['CPO', 'CPP'])
        
        if funcoes_comissao.exists():
            print("👥 FUNÇÕES DE COMISSÃO:")
            for funcao in funcoes_comissao:
                print(f"   ✅ {funcao.cargo_funcao.nome} (Status: {funcao.status})")
            print()
            
            print("🚨 PROBLEMA IDENTIFICADO:")
            print("   - Você tem função de comissão (CPO/CPP)")
            print("   - A view quadro_fixacao_vagas_update tem verificação de membro de comissão")
            print("   - Mas também pode estar sendo afetado por decorators que verificam funções")
            print()
            
            # Verificar se há decorators que bloqueiam funções de comissão
            print("🔍 VERIFICANDO DECORATORS:")
            print("   - @cargos_especiais_required: ✅ Deveria permitir (superusuário)")
            print("   - Verificação adicional na view: ❌ Pode estar bloqueando")
            print()
            
            print("💡 SOLUÇÕES:")
            print("   1. Modificar a view para dar prioridade ao superusuário")
            print("   2. Remover a verificação de comissão para superusuários")
            print("   3. Adicionar verificação de superusuário antes da verificação de comissão")
            
        else:
            print("✅ NÃO tem funções de comissão")
            print("   - O problema pode estar em outro lugar")
            
    else:
        print("❌ Nenhuma função ativa encontrada")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    verificar_funcoes_comissao() 