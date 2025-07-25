#!/usr/bin/env python
"""
Script para testar o sistema de permissões de cargos/funções
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao, UsuarioFuncao
from django.contrib.auth.models import User

def testar_sistema_permissoes_cargos():
    """Testa o sistema de permissões de cargos"""
    print("🧪 TESTANDO SISTEMA DE PERMISSÕES DE CARGOS")
    print("=" * 60)
    
    # 1. Verificar cargos existentes
    print("\n1. 📋 CARGOS EXISTENTES:")
    cargos = CargoFuncao.objects.all().order_by('nome')
    if cargos.exists():
        for cargo in cargos:
            permissoes_count = PermissaoFuncao.objects.filter(cargo_funcao=cargo, ativo=True).count()
            usuarios_count = UsuarioFuncao.objects.filter(cargo_funcao=cargo).count()
            print(f"   ✅ {cargo.nome} - {permissoes_count} permissões, {usuarios_count} usuários")
    else:
        print("   ❌ Nenhum cargo encontrado")
    
    # 2. Criar um cargo de teste com nome único
    print("\n2. 🔧 CRIANDO CARGO DE TESTE:")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_cargo_teste = f"Cargo de Teste - Permissões {timestamp}"
    
    cargo_teste, created = CargoFuncao.objects.get_or_create(
        nome=nome_cargo_teste,
        defaults={
            'descricao': 'Cargo criado para testar o sistema de permissões',
            'ativo': True,
            'ordem': 999
        }
    )
    
    if created:
        print(f"   ✅ Cargo criado: {cargo_teste.nome}")
    else:
        print(f"   ℹ️  Cargo já existe: {cargo_teste.nome}")
    
    # 3. Testar criação de permissões
    print("\n3. 🔐 TESTANDO CRIAÇÃO DE PERMISSÕES:")
    
    # Limpar permissões existentes do cargo de teste
    PermissaoFuncao.objects.filter(cargo_funcao=cargo_teste).delete()
    
    # Criar algumas permissões de teste
    permissoes_teste = [
        ('MILITARES', 'VISUALIZAR'),
        ('MILITARES', 'CRIAR'),
        ('FICHAS_CONCEITO', 'VISUALIZAR'),
        ('FICHAS_CONCEITO', 'EDITAR'),
        ('DOCUMENTOS', 'VISUALIZAR'),
        ('DOCUMENTOS', 'GERAR_PDF'),
    ]
    
    for modulo, acesso in permissoes_teste:
        permissao, created = PermissaoFuncao.objects.get_or_create(
            cargo_funcao=cargo_teste,
            modulo=modulo,
            acesso=acesso,
            defaults={
                'ativo': True,
                'observacoes': 'Permissão de teste'
            }
        )
        if created:
            print(f"   ✅ Permissão criada: {modulo} - {acesso}")
        else:
            print(f"   ℹ️  Permissão já existe: {modulo} - {acesso}")
    
    # 4. Verificar permissões criadas
    print("\n4. 📊 PERMISSÕES DO CARGO DE TESTE:")
    permissoes_cargo = PermissaoFuncao.objects.filter(cargo_funcao=cargo_teste, ativo=True)
    if permissoes_cargo.exists():
        for permissao in permissoes_cargo:
            print(f"   ✅ {permissao.modulo} - {permissao.acesso}")
    else:
        print("   ❌ Nenhuma permissão encontrada")
    
    # 5. Testar agrupamento por módulo
    print("\n5. 📁 AGRUPAMENTO POR MÓDULO:")
    permissoes_por_modulo = {}
    for permissao in permissoes_cargo:
        if permissao.modulo not in permissoes_por_modulo:
            permissoes_por_modulo[permissao.modulo] = []
        permissoes_por_modulo[permissao.modulo].append(permissao)
    
    for modulo, permissoes in permissoes_por_modulo.items():
        acessos = [p.acesso for p in permissoes]
        print(f"   📂 {modulo}: {', '.join(acessos)}")
    
    # 6. Verificar usuários com funções
    print("\n6. 👥 USUÁRIOS COM FUNÇÕES:")
    usuarios_com_funcoes = UsuarioFuncao.objects.select_related('usuario', 'cargo_funcao').all()
    if usuarios_com_funcoes.exists():
        for usuario_funcao in usuarios_com_funcoes[:5]:  # Mostrar apenas os primeiros 5
            print(f"   👤 {usuario_funcao.usuario.get_full_name()} - {usuario_funcao.cargo_funcao.nome}")
        if usuarios_com_funcoes.count() > 5:
            print(f"   ... e mais {usuarios_com_funcoes.count() - 5} usuários")
    else:
        print("   ❌ Nenhum usuário com função encontrado")
    
    # 7. Estatísticas gerais
    print("\n7. 📈 ESTATÍSTICAS GERAIS:")
    total_cargos = CargoFuncao.objects.count()
    cargos_ativos = CargoFuncao.objects.filter(ativo=True).count()
    total_permissoes = PermissaoFuncao.objects.filter(ativo=True).count()
    total_usuarios = UsuarioFuncao.objects.count()
    
    print(f"   📊 Total de cargos: {total_cargos}")
    print(f"   ✅ Cargos ativos: {cargos_ativos}")
    print(f"   🔐 Total de permissões: {total_permissoes}")
    print(f"   👥 Usuários com funções: {total_usuarios}")
    
    # 8. Limpeza - remover cargo de teste
    print("\n8. 🧹 LIMPEZA:")
    try:
        cargo_teste.delete()
        print(f"   ✅ Cargo de teste removido: {nome_cargo_teste}")
    except Exception as e:
        print(f"   ⚠️  Erro ao remover cargo de teste: {e}")
    
    print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    testar_sistema_permissoes_cargos() 