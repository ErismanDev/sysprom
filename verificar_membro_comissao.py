#!/usr/bin/env python
"""
Script para verificar se o usuário é membro de comissão
e se isso está causando o bloqueio na edição de quadros
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, QuadroFixacaoVagas

def verificar_membro_comissao():
    """Verifica se o usuário é membro de comissão"""
    
    print("🔍 VERIFICANDO MEMBRO DE COMISSÃO")
    print("=" * 50)
    
    # Buscar usuário superusuário
    usuario = User.objects.filter(is_superuser=True).first()
    if not usuario:
        print("❌ Nenhum superusuário encontrado!")
        return
    
    print(f"👤 Usuário: {usuario.get_full_name() or usuario.username}")
    print()
    
    # Verificar membros de comissão
    membros_comissao = MembroComissao.objects.filter(
        usuario=usuario,
        ativo=True,
        comissao__status='ATIVA'
    )
    
    if membros_comissao.exists():
        print("👥 MEMBROS DE COMISSÃO ATIVOS:")
        for membro in membros_comissao:
            print(f"   ✅ {membro.comissao.tipo} - {membro.comissao.nome}")
            print(f"      - Ativo: {membro.ativo}")
            print(f"      - Comissão ativa: {membro.comissao.status}")
            if membro.comissao.eh_presidente(usuario):
                print(f"      👑 PRESIDENTE da comissão")
        print()
        
        # Verificar se isso está causando bloqueio
        print("🚨 PROBLEMA IDENTIFICADO:")
        print("   - Você é membro de comissão")
        print("   - A view quadro_fixacao_vagas_update tem verificação adicional")
        print("   - Ela bloqueia membros de comissão que tentam editar quadros")
        print("   - Mesmo sendo superusuário, a verificação de comissão tem prioridade")
        print()
        
        # Verificar quadros existentes
        print("📋 QUADROS DE FIXAÇÃO EXISTENTES:")
        quadros = QuadroFixacaoVagas.objects.all()
        if quadros.exists():
            for quadro in quadros:
                print(f"   • ID: {quadro.pk} - {quadro.titulo} - Tipo: {quadro.tipo}")
                
                # Verificar se seria bloqueado
                for membro in membros_comissao:
                    if membro.comissao.tipo == 'CPO' and quadro.tipo != 'OFICIAIS':
                        print(f"      ❌ BLOQUEADO: CPO tentando editar quadro de praças")
                    elif membro.comissao.tipo == 'CPP' and quadro.tipo != 'PRACAS':
                        print(f"      ❌ BLOQUEADO: CPP tentando editar quadro de oficiais")
                    else:
                        print(f"      ✅ PERMITIDO: {membro.comissao.tipo} editando {quadro.tipo}")
        else:
            print("   Nenhum quadro encontrado")
        
        print()
        print("💡 SOLUÇÕES:")
        print("   1. Remover usuário das comissões (se não precisar ser membro)")
        print("   2. Modificar a view para dar prioridade ao superusuário")
        print("   3. Adicionar verificação de superusuário antes da verificação de comissão")
        
    else:
        print("✅ NÃO é membro de comissão")
        print("   - Isso não deveria causar problemas de edição")
        print("   - O decorator @cargos_especiais_required deveria permitir acesso")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    verificar_membro_comissao() 