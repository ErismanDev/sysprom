#!/usr/bin/env python
"""
Script para testar o sistema de permissões
"""

import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao
from militares.permissoes_simples import *

def testar_sistema_permissoes():
    """Testa o sistema de permissões"""
    
    print("🔍 TESTANDO SISTEMA DE PERMISSÕES")
    print("=" * 60)
    
    # Verificar se existem usuários
    usuarios = User.objects.all()
    print(f"Total de usuários: {usuarios.count()}")
    
    # Verificar se existem cargos/funções
    cargos = CargoFuncao.objects.all()
    print(f"Total de cargos/funções: {cargos.count()}")
    
    # Listar cargos disponíveis
    print("\n📋 CARGOS DISPONÍVEIS:")
    for cargo in cargos:
        print(f"  - {cargo.nome}")
    
    # Verificar usuários com funções
    usuarios_com_funcoes = UsuarioFuncao.objects.filter(status='ATIVO').select_related('usuario', 'cargo_funcao')
    print(f"\n👥 USUÁRIOS COM FUNÇÕES ATIVAS: {usuarios_com_funcoes.count()}")
    
    for uf in usuarios_com_funcoes:
        print(f"  - {uf.usuario.username} -> {uf.cargo_funcao.nome}")
    
    # Testar com o usuário erisman
    try:
        erisman = User.objects.get(username='erisman')
        print(f"\n🧪 TESTANDO COM USUÁRIO: {erisman.username}")
        
        # Verificar funções do erisman
        funcoes_erisman = UsuarioFuncao.objects.filter(
            usuario=erisman,
            status='ATIVO'
        ).select_related('cargo_funcao')
        
        print(f"Funções ativas: {funcoes_erisman.count()}")
        for funcao in funcoes_erisman:
            print(f"  - {funcao.cargo_funcao.nome}")
        
        # Testar funções de permissão
        print(f"\n🔐 TESTANDO PERMISSÕES:")
        print(f"  pode_editar_militares: {pode_editar_militares(erisman)}")
        print(f"  pode_editar_fichas_conceito: {pode_editar_fichas_conceito(erisman)}")
        print(f"  pode_gerenciar_quadros_vagas: {pode_gerenciar_quadros_vagas(erisman)}")
        print(f"  pode_gerenciar_comissoes: {pode_gerenciar_comissoes(erisman)}")
        print(f"  pode_gerenciar_usuarios: {pode_gerenciar_usuarios(erisman)}")
        print(f"  pode_assinar_documentos: {pode_assinar_documentos(erisman)}")
        print(f"  pode_visualizar_tudo: {pode_visualizar_tudo(erisman)}")
        print(f"  eh_membro_comissao: {eh_membro_comissao(erisman)}")
        
        # Testar função especial
        print(f"  tem_funcao_especial('Diretor de Gestão de Pessoas'): {tem_funcao_especial(erisman, 'Diretor de Gestão de Pessoas')}")
        print(f"  tem_funcao_especial('Administrador do Sistema'): {tem_funcao_especial(erisman, 'Administrador do Sistema')}")
        
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
    
    # Verificar context processor
    print(f"\n🔧 TESTANDO CONTEXT PROCESSOR:")
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = erisman if 'erisman' in locals() else AnonymousUser()
    
    try:
        context = permissoes_simples_processor(request)
        print(f"Context processor funcionando: {len(context)} variáveis disponíveis")
        for key in context.keys():
            print(f"  - {key}")
    except Exception as e:
        print(f"❌ Erro no context processor: {e}")
    
    print("\n✅ Teste concluído!")

if __name__ == '__main__':
    testar_sistema_permissoes() 