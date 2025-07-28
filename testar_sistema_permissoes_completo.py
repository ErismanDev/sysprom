#!/usr/bin/env python
"""
Script para testar o sistema de permissões completo
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import CargoFuncao, UsuarioFuncao, PermissaoFuncao
from militares.permissoes_sistema import (
    tem_permissao, tem_permissao_modulo, obter_permissoes_usuario,
    pode_executar_acao
)

def testar_sistema_permissoes_completo():
    """Testa o sistema completo de permissões"""
    
    print("🧪 TESTANDO SISTEMA DE PERMISSÕES COMPLETO")
    print("=" * 60)
    
    # Criar usuário de teste
    print("👤 Criando usuário de teste...")
    user, created = User.objects.get_or_create(
        username='teste_permissoes',
        defaults={
            'email': 'teste@teste.com',
            'first_name': 'Usuário',
            'last_name': 'Teste'
        }
    )
    
    if created:
        user.set_password('123456')
        user.save()
        print("✅ Usuário de teste criado")
    else:
        print("✅ Usuário de teste já existe")
    
    # Criar cargo de teste
    print("\n🎯 Criando cargo de teste...")
    cargo, created = CargoFuncao.objects.get_or_create(
        nome='Teste Permissões',
        defaults={
            'descricao': 'Cargo para testar sistema de permissões',
            'ativo': True
        }
    )
    
    if created:
        print("✅ Cargo de teste criado")
    else:
        print("✅ Cargo de teste já existe")
    
    # Associar usuário ao cargo
    print("\n🔗 Associando usuário ao cargo...")
    usuario_funcao, created = UsuarioFuncao.objects.get_or_create(
        usuario=user,
        cargo_funcao=cargo,
        defaults={
            'status': 'ATIVO',
            'data_inicio': '2024-01-01'
        }
    )
    
    if created:
        print("✅ Usuário associado ao cargo")
    else:
        print("✅ Usuário já estava associado ao cargo")
    
    # Testar permissões antes de adicionar
    print("\n🔍 Testando permissões ANTES de adicionar...")
    print(f"Tem permissão MILITARES/VISUALIZAR: {tem_permissao(user, 'MILITARES', 'VISUALIZAR')}")
    print(f"Tem permissão FICHAS_CONCEITO/EDITAR: {tem_permissao(user, 'FICHAS_CONCEITO', 'EDITAR')}")
    print(f"Tem permissão módulo PROMOCOES: {tem_permissao_modulo(user, 'PROMOCOES')}")
    
    # Adicionar permissões específicas
    print("\n➕ Adicionando permissões específicas...")
    
    permissoes_para_adicionar = [
        ('MILITARES', 'VISUALIZAR'),
        ('MILITARES', 'CRIAR'),
        ('FICHAS_CONCEITO', 'VISUALIZAR'),
        ('FICHAS_CONCEITO', 'EDITAR'),
        ('PROMOCOES', 'VISUALIZAR'),
        ('PROMOCOES', 'APROVAR'),
        ('COMISSAO', 'VISUALIZAR'),
        ('COMISSAO', 'ASSINAR'),
        ('DOCUMENTOS', 'VISUALIZAR'),
        ('DOCUMENTOS', 'GERAR_PDF'),
    ]
    
    for modulo, acesso in permissoes_para_adicionar:
        permissao, created = PermissaoFuncao.objects.get_or_create(
            cargo_funcao=cargo,
            modulo=modulo,
            acesso=acesso,
            defaults={'ativo': True}
        )
        
        if created:
            print(f"✅ Permissão {modulo}/{acesso} adicionada")
        else:
            print(f"✅ Permissão {modulo}/{acesso} já existia")
    
    # Testar permissões após adicionar
    print("\n🔍 Testando permissões APÓS adicionar...")
    print(f"Tem permissão MILITARES/VISUALIZAR: {tem_permissao(user, 'MILITARES', 'VISUALIZAR')}")
    print(f"Tem permissão MILITARES/CRIAR: {tem_permissao(user, 'MILITARES', 'CRIAR')}")
    print(f"Tem permissão MILITARES/EDITAR: {tem_permissao(user, 'MILITARES', 'EDITAR')}")
    print(f"Tem permissão FICHAS_CONCEITO/VISUALIZAR: {tem_permissao(user, 'FICHAS_CONCEITO', 'VISUALIZAR')}")
    print(f"Tem permissão FICHAS_CONCEITO/EDITAR: {tem_permissao(user, 'FICHAS_CONCEITO', 'EDITAR')}")
    print(f"Tem permissão módulo PROMOCOES: {tem_permissao_modulo(user, 'PROMOCOES')}")
    print(f"Tem permissão módulo USUARIOS: {tem_permissao_modulo(user, 'USUARIOS')}")
    
    # Testar ações HTTP
    print("\n🌐 Testando ações HTTP...")
    print(f"Pode executar GET em MILITARES: {pode_executar_acao(user, 'MILITARES', 'GET')}")
    print(f"Pode executar POST em MILITARES: {pode_executar_acao(user, 'MILITARES', 'POST')}")
    print(f"Pode executar PUT em FICHAS_CONCEITO: {pode_executar_acao(user, 'FICHAS_CONCEITO', 'PUT')}")
    print(f"Pode executar DELETE em PROMOCOES: {pode_executar_acao(user, 'PROMOCOES', 'DELETE')}")
    
    # Obter todas as permissões do usuário
    print("\n📋 Todas as permissões do usuário:")
    todas_permissoes = obter_permissoes_usuario(user)
    for modulo, acesso in todas_permissoes:
        print(f"   - {modulo}/{acesso}")
    
    # Obter permissões por módulo
    print("\n📊 Permissões por módulo:")
    modulos = ['MILITARES', 'FICHAS_CONCEITO', 'PROMOCOES', 'COMISSAO', 'DOCUMENTOS']
    for modulo in modulos:
        permissoes_modulo = obter_permissoes_usuario(user, modulo)
        if permissoes_modulo:
            print(f"   {modulo}: {len(permissoes_modulo)} permissões")
            for _, acesso in permissoes_modulo:
                print(f"     - {acesso}")
        else:
            print(f"   {modulo}: Nenhuma permissão")
    
    # Testar com superusuário
    print("\n👑 Testando com superusuário...")
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        print(f"Superusuário: {superuser.username}")
        print(f"Tem permissão MILITARES/VISUALIZAR: {tem_permissao(superuser, 'MILITARES', 'VISUALIZAR')}")
        print(f"Tem permissão módulo USUARIOS: {tem_permissao_modulo(superuser, 'USUARIOS')}")
        print(f"Pode executar DELETE em qualquer módulo: {pode_executar_acao(superuser, 'QUALQUER_MODULO', 'DELETE')}")
    else:
        print("❌ Nenhum superusuário encontrado")
    
    # Estatísticas gerais
    print("\n📈 Estatísticas do sistema:")
    total_cargos = CargoFuncao.objects.count()
    total_permissoes = PermissaoFuncao.objects.count()
    total_usuarios_funcao = UsuarioFuncao.objects.count()
    
    print(f"   Total de cargos: {total_cargos}")
    print(f"   Total de permissões: {total_permissoes}")
    print(f"   Total de associações usuário-cargo: {total_usuarios_funcao}")
    
    # Módulos mais utilizados
    print("\n🏆 Módulos mais utilizados:")
    from django.db.models import Count
    modulos_populares = PermissaoFuncao.objects.values('modulo').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    for item in modulos_populares:
        print(f"   {item['modulo']}: {item['count']} permissões")
    
    # Tipos de acesso mais utilizados
    print("\n🎯 Tipos de acesso mais utilizados:")
    acessos_populares = PermissaoFuncao.objects.values('acesso').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    for item in acessos_populares:
        print(f"   {item['acesso']}: {item['count']} permissões")
    
    print("\n✅ Teste do sistema de permissões completo finalizado!")
    print("=" * 60)
    print("🎯 Agora você pode:")
    print("   1. Acessar /militares/cargos/ para gerenciar permissões")
    print("   2. Marcar/desmarcar permissões e ver o efeito em tempo real")
    print("   3. Testar diferentes usuários com diferentes cargos")
    print("   4. Verificar que as permissões são aplicadas em todas as views")

if __name__ == "__main__":
    testar_sistema_permissoes_completo() 