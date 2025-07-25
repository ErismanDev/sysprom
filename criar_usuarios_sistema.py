#!/usr/bin/env python
"""
Script para criar usuários do sistema SysProm - CBMEPI
Vincula usuários aos militares cadastrados no sistema
"""

import os
import sys
import django
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, CargoComissao, ComissaoPromocao, MembroComissao

def criar_grupos():
    """Criar grupos de usuários com permissões específicas"""
    grupos = {
        'Admin': {
            'description': 'Administrador do sistema - acesso total',
            'permissions': ['add', 'change', 'delete', 'view']
        },
        'Chefe_Seção_Promoções': {
            'description': 'Chefe da Seção de Promoções',
            'permissions': ['add', 'change', 'view']
        },
        'Diretor_Gestão_Pessoas': {
            'description': 'Diretor de Gestão de Pessoas',
            'permissions': ['add', 'change', 'view']
        },
        'Presidente_CPO': {
            'description': 'Presidente da Comissão de Promoções de Oficiais',
            'permissions': ['add', 'change', 'view']
        },
        'Presidente_CPP': {
            'description': 'Presidente da Comissão de Promoções de Praças',
            'permissions': ['add', 'change', 'view']
        },
        'Membro_Nato_CPO': {
            'description': 'Membro Nato da Comissão de Promoções de Oficiais',
            'permissions': ['add', 'change', 'view']
        },
        'Membro_Nato_CPP': {
            'description': 'Membro Nato da Comissão de Promoções de Praças',
            'permissions': ['add', 'change', 'view']
        },
        'Membro_Efetivo_CPO': {
            'description': 'Membro Efetivo da Comissão de Promoções de Oficiais',
            'permissions': ['add', 'change', 'view']
        },
        'Membro_Efetivo_CPP': {
            'description': 'Membro Efetivo da Comissão de Promoções de Praças',
            'permissions': ['add', 'change', 'view']
        },
        'Suplente_CPO': {
            'description': 'Suplente da Comissão de Promoções de Oficiais',
            'permissions': ['view']
        },
        'Suplente_CPP': {
            'description': 'Suplente da Comissão de Promoções de Praças',
            'permissions': ['view']
        },
        'Digitador': {
            'description': 'Digitador - acesso limitado para entrada de dados',
            'permissions': ['add', 'change', 'view']
        },
        'Usuarios': {
            'description': 'Usuários gerais - acesso básico',
            'permissions': ['view']
        }
    }
    
    grupos_criados = {}
    
    for nome_grupo, config in grupos.items():
        grupo, created = Group.objects.get_or_create(name=nome_grupo)
        if created:
            grupo.description = config['description']
            grupo.save()
            print(f"✓ Grupo '{nome_grupo}' criado")
        else:
            print(f"⚠ Grupo '{nome_grupo}' já existe")
        
        grupos_criados[nome_grupo] = grupo
    
    return grupos_criados

def atribuir_permissoes_grupos(grupos):
    """Atribuir permissões específicas aos grupos"""
    # Obter todos os content types do app militares
    content_types = ContentType.objects.filter(app_label='militares')
    
    for nome_grupo, grupo in grupos.items():
        if nome_grupo == 'Admin':
            # Admin tem todas as permissões
            for content_type in content_types:
                for action in ['add', 'change', 'delete', 'view']:
                    codename = f'{action}_{content_type.model}'
                    permission, created = Permission.objects.get_or_create(
                        codename=codename,
                        content_type=content_type,
                        defaults={'name': f'Can {action} {content_type.model}'}
                    )
                    grupo.permissions.add(permission)
        else:
            # Outros grupos têm permissões específicas
            permissoes_config = grupos[nome_grupo]['permissions']
            for content_type in content_types:
                for action in permissoes_config:
                    codename = f'{action}_{content_type.model}'
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=content_type
                        )
                        grupo.permissions.add(permission)
                    except Permission.DoesNotExist:
                        pass  # Permissão não existe, pular
    
    print("✓ Permissões atribuídas aos grupos")

def criar_cargos_comissao():
    """Criar cargos padrão para as comissões"""
    cargos = [
        {'nome': 'Comandante Geral', 'codigo': 'COMANDANTE_GERAL', 'descricao': 'Comandante Geral do CBMEPI', 'ordem': 1},
        {'nome': 'Subcomandante', 'codigo': 'SUBCOMANDANTE', 'descricao': 'Subcomandante do CBMEPI', 'ordem': 2},
        {'nome': 'Chefe do Estado-Maior', 'codigo': 'CHEFE_EM', 'descricao': 'Chefe do Estado-Maior', 'ordem': 3},
        {'nome': 'Diretor de Gestão de Pessoas', 'codigo': 'DIRETOR_GESTAO_PESSOAS', 'descricao': 'Diretor de Gestão de Pessoas', 'ordem': 4},
        {'nome': 'Chefe da Seção de Promoções', 'codigo': 'CHEFE_SECAO_PROMOCOES', 'descricao': 'Chefe da Seção de Promoções', 'ordem': 5},
        {'nome': 'Coronel', 'codigo': 'CORONEL', 'descricao': 'Coronel', 'ordem': 6},
        {'nome': 'Tenente Coronel', 'codigo': 'TENENTE_CORONEL', 'descricao': 'Tenente Coronel', 'ordem': 7},
        {'nome': 'Major', 'codigo': 'MAJOR', 'descricao': 'Major', 'ordem': 8},
        {'nome': 'Capitão', 'codigo': 'CAPITAO', 'descricao': 'Capitão', 'ordem': 9},
        {'nome': '1º Tenente', 'codigo': 'PRIMEIRO_TENENTE', 'descricao': '1º Tenente', 'ordem': 10},
        {'nome': '2º Tenente', 'codigo': 'SEGUNDO_TENENTE', 'descricao': '2º Tenente', 'ordem': 11},
        {'nome': 'Subtenente', 'codigo': 'SUBTENENTE', 'descricao': 'Subtenente', 'ordem': 12},
        {'nome': '1º Sargento', 'codigo': 'PRIMEIRO_SARGENTO', 'descricao': '1º Sargento', 'ordem': 13},
        {'nome': '2º Sargento', 'codigo': 'SEGUNDO_SARGENTO', 'descricao': '2º Sargento', 'ordem': 14},
        {'nome': '3º Sargento', 'codigo': 'TERCEIRO_SARGENTO', 'descricao': '3º Sargento', 'ordem': 15},
        {'nome': 'Cabo', 'codigo': 'CABO', 'descricao': 'Cabo', 'ordem': 16},
        {'nome': 'Soldado', 'codigo': 'SOLDADO', 'descricao': 'Soldado', 'ordem': 17},
    ]
    
    cargos_criados = {}
    
    for cargo_data in cargos:
        cargo, created = CargoComissao.objects.get_or_create(
            codigo=cargo_data['codigo'],
            defaults={
                'nome': cargo_data['nome'],
                'descricao': cargo_data['descricao'],
                'ordem': cargo_data['ordem'],
                'ativo': True
            }
        )
        if created:
            print(f"✓ Cargo '{cargo.nome}' criado")
        else:
            print(f"⚠ Cargo '{cargo.nome}' já existe")
        
        cargos_criados[cargo.codigo] = cargo
    
    return cargos_criados

def criar_usuarios_exemplo():
    """Criar usuários de exemplo vinculados aos militares"""
    
    # Buscar alguns militares para vincular aos usuários
    militares = Militar.objects.filter(situacao='AT').order_by('posto_graduacao', 'nome_completo')
    
    if not militares.exists():
        print("❌ Nenhum militar cadastrado encontrado. Cadastre militares primeiro.")
        return
    
    # Definir usuários a serem criados
    usuarios_config = [
        {
            'username': 'admin',
            'email': 'admin@cbmepi.gov.br',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True,
            'grupo': 'Admin',
            'militar_matricula': None  # Admin não precisa estar vinculado a militar
        },
        {
            'username': 'chefe_promocoes',
            'email': 'chefe.promocoes@cbmepi.gov.br',
            'first_name': 'Chefe',
            'last_name': 'Seção Promoções',
            'password': 'chefe123',
            'grupo': 'Chefe_Seção_Promoções',
            'militar_matricula': militares.filter(posto_graduacao__in=['CB', 'TC', 'MJ']).first().matricula if militares.filter(posto_graduacao__in=['CB', 'TC', 'MJ']).exists() else None
        },
        {
            'username': 'diretor_gestao',
            'email': 'diretor.gestao@cbmepi.gov.br',
            'first_name': 'Diretor',
            'last_name': 'Gestão Pessoas',
            'password': 'diretor123',
            'grupo': 'Diretor_Gestão_Pessoas',
            'militar_matricula': militares.filter(posto_graduacao__in=['CB', 'TC']).first().matricula if militares.filter(posto_graduacao__in=['CB', 'TC']).exists() else None
        },
        {
            'username': 'presidente_cpo',
            'email': 'presidente.cpo@cbmepi.gov.br',
            'first_name': 'Presidente',
            'last_name': 'CPO',
            'password': 'presidente123',
            'grupo': 'Presidente_CPO',
            'militar_matricula': militares.filter(posto_graduacao__in=['CB', 'TC']).first().matricula if militares.filter(posto_graduacao__in=['CB', 'TC']).exists() else None
        },
        {
            'username': 'presidente_cpp',
            'email': 'presidente.cpp@cbmepi.gov.br',
            'first_name': 'Presidente',
            'last_name': 'CPP',
            'password': 'presidente123',
            'grupo': 'Presidente_CPP',
            'militar_matricula': militares.filter(posto_graduacao__in=['CB', 'TC', 'MJ']).first().matricula if militares.filter(posto_graduacao__in=['CB', 'TC', 'MJ']).exists() else None
        },
        {
            'username': 'membro_nato_cpo',
            'email': 'membro.nato.cpo@cbmepi.gov.br',
            'first_name': 'Membro',
            'last_name': 'Nato CPO',
            'password': 'membro123',
            'grupo': 'Membro_Nato_CPO',
            'militar_matricula': militares.filter(posto_graduacao__in=['CB', 'TC']).first().matricula if militares.filter(posto_graduacao__in=['CB', 'TC']).exists() else None
        },
        {
            'username': 'membro_nato_cpp',
            'email': 'membro.nato.cpp@cbmepi.gov.br',
            'first_name': 'Membro',
            'last_name': 'Nato CPP',
            'password': 'membro123',
            'grupo': 'Membro_Nato_CPP',
            'militar_matricula': militares.filter(posto_graduacao__in=['ST', '1S']).first().matricula if militares.filter(posto_graduacao__in=['ST', '1S']).exists() else None
        },
        {
            'username': 'membro_efetivo_cpo',
            'email': 'membro.efetivo.cpo@cbmepi.gov.br',
            'first_name': 'Membro',
            'last_name': 'Efetivo CPO',
            'password': 'membro123',
            'grupo': 'Membro_Efetivo_CPO',
            'militar_matricula': militares.filter(posto_graduacao__in=['CP', 'MJ']).first().matricula if militares.filter(posto_graduacao__in=['CP', 'MJ']).exists() else None
        },
        {
            'username': 'membro_efetivo_cpp',
            'email': 'membro.efetivo.cpp@cbmepi.gov.br',
            'first_name': 'Membro',
            'last_name': 'Efetivo CPP',
            'password': 'membro123',
            'grupo': 'Membro_Efetivo_CPP',
            'militar_matricula': militares.filter(posto_graduacao__in=['2S', '3S']).first().matricula if militares.filter(posto_graduacao__in=['2S', '3S']).exists() else None
        },
        {
            'username': 'suplente_cpo',
            'email': 'suplente.cpo@cbmepi.gov.br',
            'first_name': 'Suplente',
            'last_name': 'CPO',
            'password': 'suplente123',
            'grupo': 'Suplente_CPO',
            'militar_matricula': militares.filter(posto_graduacao__in=['1T', '2T']).first().matricula if militares.filter(posto_graduacao__in=['1T', '2T']).exists() else None
        },
        {
            'username': 'suplente_cpp',
            'email': 'suplente.cpp@cbmepi.gov.br',
            'first_name': 'Suplente',
            'last_name': 'CPP',
            'password': 'suplente123',
            'grupo': 'Suplente_CPP',
            'militar_matricula': militares.filter(posto_graduacao__in=['CAB', 'SD']).first().matricula if militares.filter(posto_graduacao__in=['CAB', 'SD']).exists() else None
        },
        {
            'username': 'digitador',
            'email': 'digitador@cbmepi.gov.br',
            'first_name': 'Digitador',
            'last_name': 'Sistema',
            'password': 'digitador123',
            'grupo': 'Digitador',
            'militar_matricula': militares.first().matricula if militares.exists() else None
        },
        {
            'username': 'usuario',
            'email': 'usuario@cbmepi.gov.br',
            'first_name': 'Usuário',
            'last_name': 'Geral',
            'password': 'usuario123',
            'grupo': 'Usuarios',
            'militar_matricula': militares.first().matricula if militares.exists() else None
        }
    ]
    
    grupos = {grupo.name: grupo for grupo in Group.objects.all()}
    
    for config in usuarios_config:
        try:
            # Verificar se usuário já existe
            if User.objects.filter(username=config['username']).exists():
                print(f"⚠ Usuário '{config['username']}' já existe")
                continue
            
            # Criar usuário
            user = User.objects.create_user(
                username=config['username'],
                email=config['email'],
                first_name=config['first_name'],
                last_name=config['last_name'],
                password=config['password'],
                is_staff=config.get('is_staff', False),
                is_superuser=config.get('is_superuser', False)
            )
            
            # Adicionar ao grupo
            if config['grupo'] in grupos:
                user.groups.add(grupos[config['grupo']])
            
            # Vincular ao militar se especificado
            if config['militar_matricula']:
                try:
                    militar = Militar.objects.get(matricula=config['militar_matricula'])
                    print(f"✓ Usuário '{config['username']}' criado e vinculado ao militar {militar.nome_completo}")
                except Militar.DoesNotExist:
                    print(f"⚠ Usuário '{config['username']}' criado mas militar não encontrado")
            else:
                print(f"✓ Usuário '{config['username']}' criado (sem vínculo militar)")
                
        except Exception as e:
            print(f"❌ Erro ao criar usuário '{config['username']}': {e}")

def main():
    """Função principal"""
    print("=== CRIANDO USUÁRIOS DO SISTEMA SYSPROM - CBMEPI ===\n")
    
    try:
        with transaction.atomic():
            # 1. Criar grupos
            print("1. Criando grupos de usuários...")
            grupos = criar_grupos()
            print()
            
            # 2. Atribuir permissões
            print("2. Atribuindo permissões aos grupos...")
            atribuir_permissoes_grupos(grupos)
            print()
            
            # 3. Criar cargos das comissões
            print("3. Criando cargos das comissões...")
            cargos = criar_cargos_comissao()
            print()
            
            # 4. Criar usuários
            print("4. Criando usuários...")
            criar_usuarios_exemplo()
            print()
            
            print("=== CONCLUÍDO ===")
            print("\nUsuários criados:")
            print("- admin/admin123 (Administrador)")
            print("- chefe_promocoes/chefe123 (Chefe da Seção de Promoções)")
            print("- diretor_gestao/diretor123 (Diretor de Gestão de Pessoas)")
            print("- presidente_cpo/presidente123 (Presidente CPO)")
            print("- presidente_cpp/presidente123 (Presidente CPP)")
            print("- membro_nato_cpo/membro123 (Membro Nato CPO)")
            print("- membro_nato_cpp/membro123 (Membro Nato CPP)")
            print("- membro_efetivo_cpo/membro123 (Membro Efetivo CPO)")
            print("- membro_efetivo_cpp/membro123 (Membro Efetivo CPP)")
            print("- suplente_cpo/suplente123 (Suplente CPO)")
            print("- suplente_cpp/suplente123 (Suplente CPP)")
            print("- digitador/digitador123 (Digitador)")
            print("- usuario/usuario123 (Usuário Geral)")
            
    except Exception as e:
        print(f"❌ Erro durante a criação: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 