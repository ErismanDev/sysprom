#!/usr/bin/env python
import os
import sys
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def adicionar_funcao_admin_sistema():
    print('=== ADICIONANDO FUNÇÃO "Administrador do Sistema" PARA O USUÁRIO "erisman" ===\n')
    try:
        user = User.objects.get(username='erisman')
        cargo, created = CargoFuncao.objects.get_or_create(nome='Administrador do Sistema', defaults={
            'descricao': 'Acesso total ao sistema',
            'ativo': True
        })
        if created:
            print('Cargo "Administrador do Sistema" criado.')
        else:
            print('Cargo "Administrador do Sistema" já existia.')
        # Verificar se já existe função ativa igual
        funcao_existente = UsuarioFuncao.objects.filter(usuario=user, cargo_funcao=cargo, status='ATIVO').first()
        if funcao_existente:
            print('Usuário já possui esta função ativa!')
        else:
            funcao = UsuarioFuncao.objects.create(
                usuario=user,
                cargo_funcao=cargo,
                tipo_funcao='SUPORTE',
                status='ATIVO',
                data_inicio=date.today(),
                observacoes='Função adicionada via script.'
            )
            print(f'Função criada com sucesso! ID: {funcao.pk}')
    except User.DoesNotExist:
        print('Usuário "erisman" não encontrado!')

if __name__ == '__main__':
    adicionar_funcao_admin_sistema() 