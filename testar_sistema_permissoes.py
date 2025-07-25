#!/usr/bin/env python
"""
Script para testar o sistema de permissões
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from militares.models import UsuarioFuncao, CargoFuncao, PermissaoFuncao
from militares.permissoes import tem_permissao, obter_funcao_atual

def testar_sistema_permissoes():
    """Testa o sistema de permissões"""
    
    print("🧪 TESTANDO SISTEMA DE PERMISSÕES")
    print("=" * 50)
    
    # 1. Obter usuário admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuário admin: {admin_user.username}")
    except User.DoesNotExist:
        print("❌ Usuário admin não encontrado!")
        return
    
    # 2. Criar request factory
    factory = RequestFactory()
    
    # 3. Testar diferentes cenários
    cenarios = [
        {
            'nome': 'Usuário sem função selecionada',
            'setup': lambda req: None,
            'testes': [
                ('MILITARES', 'CRIAR'),
                ('MILITARES', 'EDITAR'),
                ('MILITARES', 'EXCLUIR'),
            ]
        },
        {
            'nome': 'Usuário com função de administrador',
            'setup': lambda req: setup_funcao_admin(req, admin_user),
            'testes': [
                ('MILITARES', 'CRIAR'),
                ('MILITARES', 'EDITAR'),
                ('MILITARES', 'EXCLUIR'),
                ('USUARIOS', 'ADMINISTRAR'),
                ('CONFIGURACOES', 'EDITAR'),
            ]
        },
        {
            'nome': 'Usuário com função de gestor',
            'setup': lambda req: setup_funcao_gestor(req, admin_user),
            'testes': [
                ('MILITARES', 'CRIAR'),
                ('MILITARES', 'EDITAR'),
                ('MILITARES', 'EXCLUIR'),
            ]
        }
    ]
    
    for cenario in cenarios:
        print(f"\n📋 CENÁRIO: {cenario['nome']}")
        print("-" * 40)
        
        # Criar request
        request = factory.get('/')
        request.user = admin_user
        request.session = {}
        
        # Setup do cenário
        cenario['setup'](request)
        
        # Executar testes
        for modulo, acesso in cenario['testes']:
            resultado = tem_permissao(request, modulo, acesso)
            status = "✅" if resultado else "❌"
            print(f"   {status} {modulo}:{acesso} = {resultado}")
    
    # 4. Testar função específica
    print(f"\n🔍 TESTE ESPECÍFICO - Função Atual:")
    request = factory.get('/')
    request.user = admin_user
    request.session = {}
    
    setup_funcao_admin(request, admin_user)
    
    funcao_atual = obter_funcao_atual(request)
    if funcao_atual:
        print(f"   Função: {funcao_atual.cargo_funcao.nome}")
        print(f"   ID da função: {funcao_atual.id}")
        
        # Verificar permissões desta função
        permissoes = PermissaoFuncao.objects.filter(
            cargo_funcao=funcao_atual.cargo_funcao,
            ativo=True
        )
        print(f"   Total de permissões: {permissoes.count()}")
        
        # Mostrar algumas permissões CRUD
        permissoes_crud = permissoes.filter(acesso__in=['CRIAR', 'EDITAR', 'EXCLUIR'])
        print(f"   Permissões CRUD: {permissoes_crud.count()}")
        
        for perm in permissoes_crud[:10]:
            print(f"     - {perm.modulo}: {perm.acesso}")
    else:
        print("   ❌ Nenhuma função atual encontrada!")

def setup_funcao_admin(request, user):
    """Configura função de administrador na sessão"""
    funcao_admin = UsuarioFuncao.objects.filter(
        usuario=user,
        cargo_funcao__nome__icontains='administrador',
        status='ATIVO'
    ).first()
    
    if funcao_admin:
        request.session['funcao_atual_id'] = funcao_admin.id
        request.session['funcao_atual_nome'] = funcao_admin.cargo_funcao.nome
        print(f"   Configurado: {funcao_admin.cargo_funcao.nome}")
    else:
        print("   ❌ Função de administrador não encontrada!")

def setup_funcao_gestor(request, user):
    """Configura função de gestor na sessão"""
    funcao_gestor = UsuarioFuncao.objects.filter(
        usuario=user,
        cargo_funcao__nome__icontains='gestor',
        status='ATIVO'
    ).first()
    
    if funcao_gestor:
        request.session['funcao_atual_id'] = funcao_gestor.id
        request.session['funcao_atual_nome'] = funcao_gestor.cargo_funcao.nome
        print(f"   Configurado: {funcao_gestor.cargo_funcao.nome}")
    else:
        print("   ❌ Função de gestor não encontrada!")

def verificar_decorators_views():
    """Verifica se as views estão usando os decorators corretos"""
    
    print(f"\n🔧 VERIFICANDO DECORATORS NAS VIEWS")
    print("=" * 50)
    
    # Ler o arquivo views.py
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar decorators específicos
        decorators = [
            '@permission_required',
            '@requer_permissao',
            '@requer_funcao_ativa',
            '@administracao_required',
            '@militar_edit_permission'
        ]
        
        for decorator in decorators:
            count = content.count(decorator)
            print(f"   {decorator}: {count} ocorrências")
        
        # Verificar views específicas que podem estar causando problemas
        views_problematicas = [
            'militar_create',
            'militar_update', 
            'militar_delete',
            'ficha_conceito_create',
            'ficha_conceito_update',
            'ficha_conceito_delete'
        ]
        
        print(f"\n📋 VIEWS PROBLEMÁTICAS:")
        for view in views_problematicas:
            if view in content:
                # Encontrar a linha da view
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if f'def {view}(' in line:
                        # Verificar decorators na linha anterior
                        if i > 0 and any(d in lines[i-1] for d in decorators):
                            print(f"   ✅ {view}: Tem decorator")
                        else:
                            print(f"   ❌ {view}: SEM decorator")
                        break
            else:
                print(f"   ⚠️ {view}: Não encontrada")
                
    except FileNotFoundError:
        print("❌ Arquivo views.py não encontrado!")

def corrigir_decorators_views():
    """Corrige decorators nas views problemáticas"""
    
    print(f"\n🔧 CORRIGINDO DECORATORS NAS VIEWS")
    print("=" * 50)
    
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Views que precisam do decorator @requer_funcao_ativa
        views_para_corrigir = [
            'militar_create',
            'militar_update',
            'militar_delete',
            'ficha_conceito_create',
            'ficha_conceito_update',
            'ficha_conceito_delete'
        ]
        
        import re
        
        for view in views_para_corrigir:
            # Padrão para encontrar a definição da view
            pattern = r'@login_required\s+def ' + view + r'\('
            
            if re.search(pattern, content):
                # Adicionar decorator @requer_funcao_ativa
                replacement = r'@login_required\n@requer_funcao_ativa\ndef ' + view + r'('
                content = re.sub(pattern, replacement, content)
                print(f"   ✅ {view}: Decorator adicionado")
            else:
                print(f"   ⚠️ {view}: Não encontrada ou já tem decorator")
        
        # Salvar arquivo
        with open('militares/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Arquivo views.py atualizado!")
        
    except FileNotFoundError:
        print("❌ Arquivo views.py não encontrado!")

if __name__ == "__main__":
    print("Escolha uma opção:")
    print("1. Testar sistema de permissões")
    print("2. Verificar decorators nas views")
    print("3. Corrigir decorators nas views")
    
    opcao = input("Opção (1-3): ").strip()
    
    if opcao == "1":
        testar_sistema_permissoes()
    elif opcao == "2":
        verificar_decorators_views()
    elif opcao == "3":
        corrigir_decorators_views()
    else:
        print("❌ Opção inválida!") 