#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para criar perfis de acesso padrão no sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao, PerfilAcesso

def criar_perfis_padrao():
    """Cria perfis de acesso padrão"""
    
    print("=== CRIANDO PERFIS DE ACESSO PADRAO ===\n")
    
    # 1. Perfil Administrador (acesso total)
    perfil_admin, created = PerfilAcesso.objects.get_or_create(
        nome='Administrador',
        defaults={
            'descricao': 'Acesso total ao sistema - todas as permissões',
            'ativo': True
        }
    )
    
    if created:
        print("✅ Perfil 'Administrador' criado")
    else:
        print("ℹ️ Perfil 'Administrador' já existe")
    
    # 2. Perfil Gestor (acesso de gestão)
    perfil_gestor, created = PerfilAcesso.objects.get_or_create(
        nome='Gestor',
        defaults={
            'descricao': 'Acesso de gestão - pode visualizar, criar, editar e aprovar',
            'ativo': True
        }
    )
    
    if created:
        print("✅ Perfil 'Gestor' criado")
    else:
        print("ℹ️ Perfil 'Gestor' já existe")
    
    # 3. Perfil Operador (acesso operacional)
    perfil_operador, created = PerfilAcesso.objects.get_or_create(
        nome='Operador',
        defaults={
            'descricao': 'Acesso operacional - pode visualizar e criar',
            'ativo': True
        }
    )
    
    if created:
        print("✅ Perfil 'Operador' criado")
    else:
        print("ℹ️ Perfil 'Operador' já existe")
    
    # 4. Perfil Consulta (apenas visualização)
    perfil_consulta, created = PerfilAcesso.objects.get_or_create(
        nome='Consulta',
        defaults={
            'descricao': 'Acesso apenas para consulta - apenas visualização',
            'ativo': True
        }
    )
    
    if created:
        print("✅ Perfil 'Consulta' criado")
    else:
        print("ℹ️ Perfil 'Consulta' já existe")
    
    # 5. Perfil Comissão (acesso específico para comissões)
    perfil_comissao, created = PerfilAcesso.objects.get_or_create(
        nome='Membro de Comissão',
        defaults={
            'descricao': 'Acesso específico para membros de comissão',
            'ativo': True
        }
    )
    
    if created:
        print("✅ Perfil 'Membro de Comissão' criado")
    else:
        print("ℹ️ Perfil 'Membro de Comissão' já existe")
    
    print(f"\n=== PERFIS CRIADOS ===")
    print(f"Total de perfis: {PerfilAcesso.objects.count()}")
    
    # Listar perfis criados
    for perfil in PerfilAcesso.objects.all():
        print(f"- {perfil.nome}: {perfil.descricao}")


def criar_cargos_padrao():
    """Cria cargos padrão para aplicar os perfis"""
    
    print("\n=== CRIANDO CARGOS PADRAO ===\n")
    
    # Criar cargos padrão
    cargos_padrao = [
        {
            'nome': 'Administrador do Sistema',
            'descricao': 'Acesso total ao sistema',
            'ordem': 1
        },
        {
            'nome': 'Gestor de Promoções',
            'descricao': 'Responsável pela gestão de promoções',
            'ordem': 2
        },
        {
            'nome': 'Operador do Sistema',
            'descricao': 'Operador com acesso limitado',
            'ordem': 3
        },
        {
            'nome': 'Usuário',
            'descricao': 'Acesso apenas para consulta',
            'ordem': 4
        },
        {
            'nome': 'Membro de Comissão',
            'descricao': 'Membro de comissão de promoções',
            'ordem': 5
        },
    ]
    
    cargos_criados = {}
    
    for cargo_info in cargos_padrao:
        cargo, created = CargoFuncao.objects.get_or_create(
            nome=cargo_info['nome'],
            defaults={
                'descricao': cargo_info['descricao'],
                'ativo': True,
                'ordem': cargo_info['ordem']
            }
        )
        
        if created:
            print(f"✅ Cargo '{cargo.nome}' criado")
        else:
            print(f"ℹ️ Cargo '{cargo.nome}' já existe")
        
        cargos_criados[cargo.nome] = cargo
    
    return cargos_criados


def aplicar_perfis_aos_cargos(cargos):
    """Aplica os perfis aos cargos criados"""
    
    print("\n=== APLICANDO PERFIS AOS CARGOS ===\n")
    
    # Mapeamento de cargos para perfis
    mapeamento = {
        'Administrador do Sistema': 'Administrador',
        'Gestor de Promoções': 'Gestor',
        'Operador do Sistema': 'Operador',
        'Usuário': 'Consulta',
        'Membro de Comissão': 'Membro de Comissão',
    }
    
    for nome_cargo, nome_perfil in mapeamento.items():
        if nome_cargo in cargos:
            cargo = cargos[nome_cargo]
            perfil = PerfilAcesso.objects.get(nome=nome_perfil)
            
            # Aplicar perfil ao cargo
            perfil.aplicar_perfil(cargo)
            print(f"✅ Perfil '{nome_perfil}' aplicado ao cargo '{nome_cargo}'")


def criar_permissoes_padrao():
    """Cria permissões padrão para os perfis"""
    
    print("\n=== CRIANDO PERMISSOES PADRAO ===\n")
    
    # Obter perfis
    perfil_admin = PerfilAcesso.objects.get(nome='Administrador')
    perfil_gestor = PerfilAcesso.objects.get(nome='Gestor')
    perfil_operador = PerfilAcesso.objects.get(nome='Operador')
    perfil_consulta = PerfilAcesso.objects.get(nome='Consulta')
    perfil_comissao = PerfilAcesso.objects.get(nome='Membro de Comissão')
    
    # Definir permissões para cada perfil
    permissoes_perfil = {
        'Administrador': [
            # Todas as permissões para todos os módulos
            ('MILITARES', 'VISUALIZAR'), ('MILITARES', 'CRIAR'), ('MILITARES', 'EDITAR'), ('MILITARES', 'EXCLUIR'),
            ('FICHAS_CONCEITO', 'VISUALIZAR'), ('FICHAS_CONCEITO', 'CRIAR'), ('FICHAS_CONCEITO', 'EDITAR'), ('FICHAS_CONCEITO', 'EXCLUIR'),
            ('QUADROS_ACESSO', 'VISUALIZAR'), ('QUADROS_ACESSO', 'CRIAR'), ('QUADROS_ACESSO', 'EDITAR'), ('QUADROS_ACESSO', 'EXCLUIR'), ('QUADROS_ACESSO', 'HOMOLOGAR'),
            ('PROMOCOES', 'VISUALIZAR'), ('PROMOCOES', 'CRIAR'), ('PROMOCOES', 'EDITAR'), ('PROMOCOES', 'EXCLUIR'),
            ('VAGAS', 'VISUALIZAR'), ('VAGAS', 'CRIAR'), ('VAGAS', 'EDITAR'), ('VAGAS', 'EXCLUIR'),
            ('COMISSAO', 'VISUALIZAR'), ('COMISSAO', 'CRIAR'), ('COMISSAO', 'EDITAR'), ('COMISSAO', 'EXCLUIR'),
            ('DOCUMENTOS', 'VISUALIZAR'), ('DOCUMENTOS', 'CRIAR'), ('DOCUMENTOS', 'EDITAR'), ('DOCUMENTOS', 'EXCLUIR'), ('DOCUMENTOS', 'GERAR_PDF'), ('DOCUMENTOS', 'ASSINAR'),
            ('USUARIOS', 'VISUALIZAR'), ('USUARIOS', 'CRIAR'), ('USUARIOS', 'EDITAR'), ('USUARIOS', 'EXCLUIR'), ('USUARIOS', 'ADMINISTRAR'),
            ('RELATORIOS', 'VISUALIZAR'), ('RELATORIOS', 'CRIAR'), ('RELATORIOS', 'EDITAR'), ('RELATORIOS', 'EXCLUIR'),
            ('CONFIGURACOES', 'VISUALIZAR'), ('CONFIGURACOES', 'CRIAR'), ('CONFIGURACOES', 'EDITAR'), ('CONFIGURACOES', 'EXCLUIR'),
        ],
        'Gestor': [
            # Acesso de gestão - pode visualizar, criar, editar e aprovar
            ('MILITARES', 'VISUALIZAR'), ('MILITARES', 'CRIAR'), ('MILITARES', 'EDITAR'),
            ('FICHAS_CONCEITO', 'VISUALIZAR'), ('FICHAS_CONCEITO', 'CRIAR'), ('FICHAS_CONCEITO', 'EDITAR'),
            ('QUADROS_ACESSO', 'VISUALIZAR'), ('QUADROS_ACESSO', 'CRIAR'), ('QUADROS_ACESSO', 'EDITAR'), ('QUADROS_ACESSO', 'HOMOLOGAR'),
            ('PROMOCOES', 'VISUALIZAR'), ('PROMOCOES', 'CRIAR'), ('PROMOCOES', 'EDITAR'),
            ('VAGAS', 'VISUALIZAR'), ('VAGAS', 'CRIAR'), ('VAGAS', 'EDITAR'),
            ('COMISSAO', 'VISUALIZAR'), ('COMISSAO', 'CRIAR'), ('COMISSAO', 'EDITAR'),
            ('DOCUMENTOS', 'VISUALIZAR'), ('DOCUMENTOS', 'CRIAR'), ('DOCUMENTOS', 'EDITAR'), ('DOCUMENTOS', 'GERAR_PDF'), ('DOCUMENTOS', 'ASSINAR'),
            ('USUARIOS', 'VISUALIZAR'), ('USUARIOS', 'CRIAR'), ('USUARIOS', 'EDITAR'),
            ('RELATORIOS', 'VISUALIZAR'), ('RELATORIOS', 'CRIAR'), ('RELATORIOS', 'EDITAR'),
        ],
        'Operador': [
            # Acesso operacional - pode visualizar e criar
            ('MILITARES', 'VISUALIZAR'), ('MILITARES', 'CRIAR'),
            ('FICHAS_CONCEITO', 'VISUALIZAR'), ('FICHAS_CONCEITO', 'CRIAR'),
            ('QUADROS_ACESSO', 'VISUALIZAR'), ('QUADROS_ACESSO', 'CRIAR'),
            ('PROMOCOES', 'VISUALIZAR'), ('PROMOCOES', 'CRIAR'),
            ('VAGAS', 'VISUALIZAR'), ('VAGAS', 'CRIAR'),
            ('COMISSAO', 'VISUALIZAR'), ('COMISSAO', 'CRIAR'),
            ('DOCUMENTOS', 'VISUALIZAR'), ('DOCUMENTOS', 'CRIAR'),
            ('RELATORIOS', 'VISUALIZAR'), ('RELATORIOS', 'CRIAR'),
        ],
        'Consulta': [
            # Apenas visualização
            ('MILITARES', 'VISUALIZAR'),
            ('FICHAS_CONCEITO', 'VISUALIZAR'),
            ('QUADROS_ACESSO', 'VISUALIZAR'),
            ('PROMOCOES', 'VISUALIZAR'),
            ('VAGAS', 'VISUALIZAR'),
            ('COMISSAO', 'VISUALIZAR'),
            ('DOCUMENTOS', 'VISUALIZAR'),
            ('RELATORIOS', 'VISUALIZAR'),
        ],
        'Membro de Comissão': [
            # Acesso específico para comissão
            ('COMISSAO', 'VISUALIZAR'), ('COMISSAO', 'CRIAR'), ('COMISSAO', 'EDITAR'),
            ('DOCUMENTOS', 'VISUALIZAR'), ('DOCUMENTOS', 'CRIAR'), ('DOCUMENTOS', 'EDITAR'), ('DOCUMENTOS', 'ASSINAR'),
            ('RELATORIOS', 'VISUALIZAR'),
        ],
    }
    
    # Criar permissões para cada perfil
    for nome_perfil, permissoes in permissoes_perfil.items():
        perfil = PerfilAcesso.objects.get(nome=nome_perfil)
        print(f"\nCriando permissões para perfil: {nome_perfil}")
        
        for modulo, acesso in permissoes:
            # Criar permissão genérica (sem cargo específico)
            permissao, created = PermissaoFuncao.objects.get_or_create(
                modulo=modulo,
                acesso=acesso,
                defaults={
                    'ativo': True,
                    'observacoes': f'Permissão padrão do perfil {nome_perfil}'
                }
            )
            
            if created:
                print(f"  ✅ Criada permissão: {modulo} - {acesso}")
            else:
                print(f"  ℹ️ Permissão já existe: {modulo} - {acesso}")
            
            # Adicionar ao perfil se não estiver
            if permissao not in perfil.permissoes.all():
                perfil.permissoes.add(permissao)
                print(f"  ✅ Adicionada ao perfil: {modulo} - {acesso}")
    
    print(f"\n=== PERMISSOES CRIADAS ===")
    print(f"Total de permissões: {PermissaoFuncao.objects.count()}")


def main():
    """Função principal"""
    criar_perfis_padrao()
    criar_permissoes_padrao()
    cargos = criar_cargos_padrao()
    aplicar_perfis_aos_cargos(cargos)
    
    print(f"\n=== SISTEMA DE CONTROLE DE ACESSO CONFIGURADO ===")
    print("Agora você pode:")
    print("1. Acessar o admin do Django")
    print("2. Configurar cargos/funções")
    print("3. Aplicar perfis aos cargos")
    print("4. Usar os decorators nas views")
    print("\nCargos criados:")
    for nome, cargo in cargos.items():
        print(f"- {nome}")

if __name__ == '__main__':
    main() 