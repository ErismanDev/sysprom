#!/usr/bin/env python
"""
Script para testar o sistema de permissões de cargos/funções existentes
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao, UsuarioFuncao
from django.contrib.auth.models import User

def testar_permissoes_existentes():
    """Testa o sistema de permissões com dados existentes"""
    print("🧪 TESTANDO SISTEMA DE PERMISSÕES - DADOS EXISTENTES")
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
    
    # 2. Verificar permissões existentes
    print("\n2. 🔐 PERMISSÕES EXISTENTES:")
    permissoes = PermissaoFuncao.objects.filter(ativo=True).select_related('cargo_funcao')
    if permissoes.exists():
        for permissao in permissoes[:10]:  # Mostrar apenas as primeiras 10
            print(f"   ✅ {permissao.cargo_funcao.nome} - {permissao.modulo} - {permissao.acesso}")
        if permissoes.count() > 10:
            print(f"   ... e mais {permissoes.count() - 10} permissões")
    else:
        print("   ❌ Nenhuma permissão encontrada")
    
    # 3. Testar agrupamento por módulo
    print("\n3. 📁 AGRUPAMENTO POR MÓDULO:")
    permissoes_por_modulo = {}
    for permissao in permissoes:
        if permissao.modulo not in permissoes_por_modulo:
            permissoes_por_modulo[permissao.modulo] = []
        permissoes_por_modulo[permissao.modulo].append(permissao)
    
    for modulo, permissoes_list in permissoes_por_modulo.items():
        acessos = [p.acesso for p in permissoes_list]
        print(f"   📂 {modulo}: {', '.join(acessos)}")
    
    # 4. Verificar usuários com funções
    print("\n4. 👥 USUÁRIOS COM FUNÇÕES:")
    usuarios_com_funcoes = UsuarioFuncao.objects.select_related('usuario', 'cargo_funcao').all()
    if usuarios_com_funcoes.exists():
        for usuario_funcao in usuarios_com_funcoes[:5]:  # Mostrar apenas os primeiros 5
            print(f"   👤 {usuario_funcao.usuario.get_full_name()} - {usuario_funcao.cargo_funcao.nome}")
        if usuarios_com_funcoes.count() > 5:
            print(f"   ... e mais {usuarios_com_funcoes.count() - 5} usuários")
    else:
        print("   ❌ Nenhum usuário com função encontrado")
    
    # 5. Estatísticas gerais
    print("\n5. 📈 ESTATÍSTICAS GERAIS:")
    total_cargos = CargoFuncao.objects.count()
    cargos_ativos = CargoFuncao.objects.filter(ativo=True).count()
    total_permissoes = PermissaoFuncao.objects.filter(ativo=True).count()
    total_usuarios = UsuarioFuncao.objects.count()
    
    print(f"   📊 Total de cargos: {total_cargos}")
    print(f"   ✅ Cargos ativos: {cargos_ativos}")
    print(f"   🔐 Total de permissões: {total_permissoes}")
    print(f"   👥 Usuários com funções: {total_usuarios}")
    
    # 6. Testar carregamento de permissões por cargo
    print("\n6. 🔍 TESTE DE CARREGAMENTO DE PERMISSÕES:")
    cargo_teste = cargos.first()
    if cargo_teste:
        print(f"   Testando cargo: {cargo_teste.nome}")
        permissoes_cargo = PermissaoFuncao.objects.filter(cargo_funcao=cargo_teste, ativo=True)
        print(f"   Permissões encontradas: {permissoes_cargo.count()}")
        
        # Agrupar por módulo
        permissoes_por_modulo_cargo = {}
        for permissao in permissoes_cargo:
            if permissao.modulo not in permissoes_por_modulo_cargo:
                permissoes_por_modulo_cargo[permissao.modulo] = []
            permissoes_por_modulo_cargo[permissao.modulo].append(permissao)
        
        for modulo, permissoes_list in permissoes_por_modulo_cargo.items():
            acessos = [p.acesso for p in permissoes_list]
            print(f"   📂 {modulo}: {', '.join(acessos)}")
    else:
        print("   ❌ Nenhum cargo disponível para teste")
    
    print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    testar_permissoes_existentes() 