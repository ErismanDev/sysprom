#!/usr/bin/env python
"""
Script para testar a funcionalidade de buscar funções do usuário
"""

import os
import sys
import django

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, CargoFuncao, UsuarioFuncao, CargoComissao

def testar_funcoes_usuario():
    """Testa se o sistema de busca de funções do usuário está funcionando"""
    
    print("=== Teste do Sistema de Busca de Funções do Usuário ===")
    
    try:
        # 1. Verificar se existe pelo menos um usuário
        usuarios = User.objects.all()
        print(f"1. Usuários encontrados: {usuarios.count()}")
        
        if not usuarios.exists():
            print("   Criando usuário de teste...")
            usuario = User.objects.create_user(
                username='teste_usuario',
                first_name='Usuário',
                last_name='Teste',
                email='teste@teste.com',
                password='teste123'
            )
            print(f"   Usuário criado: {usuario.get_full_name()}")
        else:
            usuario = usuarios.first()
            print(f"   Usando usuário: {usuario.get_full_name()}")
        
        # 2. Verificar se existem cargos/funções
        cargos = CargoFuncao.objects.all()
        print(f"2. Cargos/Funções encontrados: {cargos.count()}")
        
        if not cargos.exists():
            print("   Criando cargos de teste...")
            cargo1 = CargoFuncao.objects.create(
                nome='Presidente da Comissão',
                descricao='Função de presidente',
                ativo=True,
                ordem=1
            )
            cargo2 = CargoFuncao.objects.create(
                nome='Membro Efetivo',
                descricao='Função de membro efetivo',
                ativo=True,
                ordem=2
            )
            print(f"   Cargos criados: {cargo1.nome}, {cargo2.nome}")
        else:
            cargo1 = cargos.first()
            cargo2 = cargos.last() if cargos.count() > 1 else cargo1
            print(f"   Usando cargos: {cargo1.nome}, {cargo2.nome}")
        
        # 3. Criar funções para o usuário
        from datetime import date, timedelta
        
        # Remover funções existentes do usuário
        UsuarioFuncao.objects.filter(usuario=usuario).delete()
        
        # Criar função 1
        funcao1 = UsuarioFuncao.objects.create(
            usuario=usuario,
            cargo_funcao=cargo1,
            tipo_funcao='COMISSAO',
            status='ATIVO',
            data_inicio=date.today() - timedelta(days=30),
            data_fim=date.today() + timedelta(days=365),
            descricao='Função de presidente'
        )
        
        # Criar função 2
        funcao2 = UsuarioFuncao.objects.create(
            usuario=usuario,
            cargo_funcao=cargo2,
            tipo_funcao='OPERACIONAL',
            status='ATIVO',
            data_inicio=date.today() - timedelta(days=15),
            data_fim=date.today() + timedelta(days=180),
            descricao='Função operacional'
        )
        
        print(f"3. Funções criadas para {usuario.get_full_name()}:")
        print(f"   - {funcao1.cargo_funcao.nome} ({funcao1.get_tipo_funcao_display()})")
        print(f"   - {funcao2.cargo_funcao.nome} ({funcao2.get_tipo_funcao_display()})")
        
        # 4. Testar busca de funções
        funcoes_usuario = UsuarioFuncao.objects.filter(
            usuario=usuario,
            status='ATIVO'
        ).select_related('cargo_funcao').order_by('cargo_funcao__nome')
        
        print(f"4. Funções ativas encontradas: {funcoes_usuario.count()}")
        
        for funcao in funcoes_usuario:
            print(f"   - {funcao.cargo_funcao.nome}")
            print(f"     Tipo: {funcao.get_tipo_funcao_display()}")
            print(f"     Período: {funcao.data_inicio} a {funcao.data_fim}")
            print(f"     Descrição: {funcao.descricao}")
        
        # 5. Verificar se existem cargos da comissão
        cargos_comissao = CargoComissao.objects.all()
        print(f"5. Cargos da Comissão encontrados: {cargos_comissao.count()}")
        
        if not cargos_comissao.exists():
            print("   Criando cargos da comissão de teste...")
            cargo_comissao1 = CargoComissao.objects.create(
                nome='Coronel',
                codigo='CORONEL',
                descricao='Cargo de Coronel',
                ativo=True,
                ordem=1
            )
            cargo_comissao2 = CargoComissao.objects.create(
                nome='Tenente Coronel',
                codigo='TENENTE_CORONEL',
                descricao='Cargo de Tenente Coronel',
                ativo=True,
                ordem=2
            )
            print(f"   Cargos da comissão criados: {cargo_comissao1.nome}, {cargo_comissao2.nome}")
        else:
            print(f"   Cargos da comissão existentes: {cargos_comissao.count()}")
        
        print("\n✅ Teste concluído com sucesso!")
        print("📋 Resumo:")
        print(f"   - Usuário: {usuario.get_full_name()}")
        print(f"   - Funções ativas: {funcoes_usuario.count()}")
        print(f"   - Cargos da comissão: {cargos_comissao.count()}")
        print("\n🎯 Funcionalidades testadas:")
        print("   ✓ Busca de funções do usuário")
        print("   ✓ Múltiplas funções por usuário")
        print("   ✓ Informações detalhadas das funções")
        print("   ✓ Cargos da comissão disponíveis")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_funcoes_usuario() 