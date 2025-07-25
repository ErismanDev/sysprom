#!/usr/bin/env python
"""
Script para criar funções de teste para verificar o sistema de assinatura
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import CargoFuncao, UsuarioFuncao
from datetime import date

def criar_funcoes_teste():
    """Criar funções de teste para verificar o sistema"""
    
    # Criar cargos/funções se não existirem
    cargos_funcoes = [
        'Presidente',
        'Diretor',
        'Chefe',
        'Comandante',
        'Secretário',
        'Coordenador',
        'Supervisor',
        'Gerente',
        'Assessor',
        'Consultor',
        'Membro de Comissão',
        'Membro Efetivo',
        'Membro Nato'
    ]
    
    for nome_cargo in cargos_funcoes:
        cargo, created = CargoFuncao.objects.get_or_create(
            nome=nome_cargo,
            defaults={
                'descricao': f'Cargo/Função de {nome_cargo}',
                'ativo': True,
                'ordem': len(cargos_funcoes)
            }
        )
        if created:
            print(f"Criado cargo: {nome_cargo}")
        else:
            print(f"Cargo já existe: {nome_cargo}")
    
    # Buscar usuários para atribuir funções
    usuarios = User.objects.filter(is_active=True).exclude(username='usuario')[:5]
    
    for i, usuario in enumerate(usuarios):
        # Criar algumas funções para cada usuário
        funcoes_para_usuario = cargos_funcoes[i % len(cargos_funcoes):(i + 2) % len(cargos_funcoes)]
        if not funcoes_para_usuario:
            funcoes_para_usuario = [cargos_funcoes[0]]
        
        for nome_funcao in funcoes_para_usuario:
            cargo = CargoFuncao.objects.get(nome=nome_funcao)
            
            # Verificar se já existe
            if not UsuarioFuncao.objects.filter(usuario=usuario, cargo_funcao=cargo).exists():
                funcao = UsuarioFuncao.objects.create(
                    usuario=usuario,
                    cargo_funcao=cargo,
                    tipo_funcao='ADMINISTRATIVO',
                    status='ATIVO',
                    data_inicio=date.today()
                )
                print(f"Atribuída função {nome_funcao} ao usuário {usuario.username}")
            else:
                print(f"Usuário {usuario.username} já tem a função {nome_funcao}")

if __name__ == '__main__':
    criar_funcoes_teste()
    print("Script concluído!") 