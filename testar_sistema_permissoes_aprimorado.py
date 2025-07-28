#!/usr/bin/env python
"""
Script para testar o sistema de permissões aprimorado de cargos/funções
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

def testar_sistema_permissoes_aprimorado():
    """Testa o sistema de permissões aprimorado"""
    print("🚀 TESTANDO SISTEMA DE PERMISSÕES APRIMORADO")
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
    
    # 2. Criar cargos de teste com permissões específicas
    print("\n2. 🔧 CRIANDO CARGOS DE TESTE COM PERMISSÕES:")
    
    # Cargo de Administrador Completo
    cargo_admin, created = CargoFuncao.objects.get_or_create(
        nome="Administrador Completo - Teste",
        defaults={
            'descricao': 'Cargo com todas as permissões do sistema para testes',
            'ativo': True,
            'ordem': 999
        }
    )
    
    if created:
        print(f"   ✅ Cargo criado: {cargo_admin.nome}")
    else:
        print(f"   ℹ️  Cargo já existe: {cargo_admin.nome}")
    
    # Cargo de Visualizador
    cargo_visualizador, created = CargoFuncao.objects.get_or_create(
        nome="Visualizador - Teste",
        defaults={
            'descricao': 'Cargo com permissões apenas de visualização',
            'ativo': True,
            'ordem': 998
        }
    )
    
    if created:
        print(f"   ✅ Cargo criado: {cargo_visualizador.nome}")
    else:
        print(f"   ℹ️  Cargo já existe: {cargo_visualizador.nome}")
    
    # Cargo de Operador
    cargo_operador, created = CargoFuncao.objects.get_or_create(
        nome="Operador - Teste",
        defaults={
            'descricao': 'Cargo com permissões de operação básica',
            'ativo': True,
            'ordem': 997
        }
    )
    
    if created:
        print(f"   ✅ Cargo criado: {cargo_operador.nome}")
    else:
        print(f"   ℹ️  Cargo já existe: {cargo_operador.nome}")
    
    # 3. Aplicar permissões específicas
    print("\n3. 🔐 APLICANDO PERMISSÕES ESPECÍFICAS:")
    
    # Limpar permissões existentes dos cargos de teste
    PermissaoFuncao.objects.filter(cargo_funcao__in=[cargo_admin, cargo_visualizador, cargo_operador]).delete()
    
    # Permissões para Administrador Completo
    modulos_admin = [
        'MILITARES', 'FICHAS_CONCEITO', 'QUADROS_ACESSO', 'PROMOCOES', 
        'VAGAS', 'COMISSAO', 'DOCUMENTOS', 'USUARIOS', 'RELATORIOS', 'CONFIGURACOES'
    ]
    acessos_admin = [
        'VISUALIZAR', 'CRIAR', 'EDITAR', 'EXCLUIR', 'APROVAR', 'HOMOLOGAR', 
        'GERAR_PDF', 'IMPRIMIR', 'ASSINAR', 'ADMINISTRAR'
    ]
    
    for modulo in modulos_admin:
        for acesso in acessos_admin:
            PermissaoFuncao.objects.create(
                cargo_funcao=cargo_admin,
                modulo=modulo,
                acesso=acesso,
                ativo=True,
                observacoes=f'Permissão de administrador completo - {modulo} - {acesso}'
            )
    
    print(f"   ✅ {cargo_admin.nome}: {len(modulos_admin) * len(acessos_admin)} permissões aplicadas")
    
    # Permissões para Visualizador
    modulos_visualizador = [
        'MILITARES', 'FICHAS_CONCEITO', 'QUADROS_ACESSO', 'PROMOCOES', 
        'VAGAS', 'COMISSAO', 'DOCUMENTOS', 'RELATORIOS'
    ]
    
    for modulo in modulos_visualizador:
        PermissaoFuncao.objects.create(
            cargo_funcao=cargo_visualizador,
            modulo=modulo,
            acesso='VISUALIZAR',
            ativo=True,
            observacoes=f'Permissão de visualização - {modulo}'
        )
    
    print(f"   ✅ {cargo_visualizador.nome}: {len(modulos_visualizador)} permissões de visualização aplicadas")
    
    # Permissões para Operador
    modulos_operador = [
        'MILITARES', 'FICHAS_CONCEITO', 'QUADROS_ACESSO', 'PROMOCOES', 'VAGAS'
    ]
    acessos_operador = ['VISUALIZAR', 'CRIAR', 'EDITAR']
    
    for modulo in modulos_operador:
        for acesso in acessos_operador:
            PermissaoFuncao.objects.create(
                cargo_funcao=cargo_operador,
                modulo=modulo,
                acesso=acesso,
                ativo=True,
                observacoes=f'Permissão de operador - {modulo} - {acesso}'
            )
    
    print(f"   ✅ {cargo_operador.nome}: {len(modulos_operador) * len(acessos_operador)} permissões aplicadas")
    
    # 4. Verificar permissões aplicadas
    print("\n4. 📊 VERIFICANDO PERMISSÕES APLICADAS:")
    
    for cargo in [cargo_admin, cargo_visualizador, cargo_operador]:
        permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo, ativo=True)
        print(f"\n   📋 {cargo.nome}:")
        print(f"      Total de permissões: {permissoes.count()}")
        
        # Agrupar por módulo
        permissoes_por_modulo = {}
        for permissao in permissoes:
            if permissao.modulo not in permissoes_por_modulo:
                permissoes_por_modulo[permissao.modulo] = []
            permissoes_por_modulo[permissao.modulo].append(permissao.acesso)
        
        for modulo, acessos in permissoes_por_modulo.items():
            print(f"      - {modulo}: {', '.join(acessos)}")
    
    # 5. Estatísticas gerais
    print("\n5. 📈 ESTATÍSTICAS GERAIS:")
    total_cargos = CargoFuncao.objects.count()
    cargos_ativos = CargoFuncao.objects.filter(ativo=True).count()
    total_permissoes = PermissaoFuncao.objects.filter(ativo=True).count()
    total_usuarios = UsuarioFuncao.objects.count()
    
    print(f"   📊 Total de cargos: {total_cargos}")
    print(f"   📊 Cargos ativos: {cargos_ativos}")
    print(f"   📊 Total de permissões: {total_permissoes}")
    print(f"   📊 Total de usuários com funções: {total_usuarios}")
    
    # 6. Verificar módulos mais utilizados
    print("\n6. 🎯 MÓDULOS MAIS UTILIZADOS:")
    from django.db.models import Count
    
    modulos_populares = PermissaoFuncao.objects.filter(ativo=True).values('modulo').annotate(
        total=Count('id')
    ).order_by('-total')
    
    for modulo in modulos_populares[:5]:
        print(f"   📊 {modulo['modulo']}: {modulo['total']} permissões")
    
    # 7. Verificar tipos de acesso mais comuns
    print("\n7. 🔑 TIPOS DE ACESSO MAIS COMUNS:")
    acessos_populares = PermissaoFuncao.objects.filter(ativo=True).values('acesso').annotate(
        total=Count('id')
    ).order_by('-total')
    
    for acesso in acessos_populares:
        print(f"   📊 {acesso['acesso']}: {acesso['total']} ocorrências")
    
    # 8. Instruções para teste
    print("\n8. 🧪 INSTRUÇÕES PARA TESTE:")
    print("   🌐 Acesse o sistema e vá para:")
    print("      - /militares/cargos/ (Lista de cargos)")
    print("      - /militares/cargos/novo/ (Criar novo cargo)")
    print("      - /militares/cargos/{id}/ (Ver detalhes do cargo)")
    print("      - /militares/cargos/{id}/editar/ (Editar cargo)")
    print("\n   ✨ Funcionalidades para testar:")
    print("      - Marcar/desmarcar todas as permissões de um módulo")
    print("      - Usar botões de ação global (Marcar Todos, Desmarcar Todos, etc.)")
    print("      - Ver contadores de permissões em tempo real")
    print("      - Ver cores dos cards baseadas na quantidade de permissões")
    print("      - Testar responsividade em diferentes tamanhos de tela")
    
    print("\n✅ TESTE CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    testar_sistema_permissoes_aprimorado() 