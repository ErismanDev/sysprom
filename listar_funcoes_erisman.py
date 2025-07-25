#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao

def listar_funcoes_erisman():
    print('=== LISTAGEM DETALHADA DAS FUNÇÕES DO USUÁRIO "erisman" ===\n')
    try:
        user = User.objects.get(username='erisman')
        print(f'Usuário: {user.get_full_name()} (ID: {user.pk}) | Ativo: {user.is_active}')
        funcoes = UsuarioFuncao.objects.filter(usuario=user)
        print(f'Total de funções encontradas: {funcoes.count()}')
        for funcao in funcoes:
            print(f'--- Função ID: {funcao.pk} ---')
            print(f'  Cargo: {funcao.cargo_funcao.nome}')
            print(f'  Tipo: {funcao.get_tipo_funcao_display()}')
            print(f'  Status: "{funcao.status}"')
            print(f'  Data Início: {funcao.data_inicio}')
            print(f'  Data Fim: {funcao.data_fim}')
            print(f'  Observações: {funcao.observacoes}')
            print(f'  Data Registro: {funcao.data_registro}')
            print(f'  Data Atualização: {funcao.data_atualizacao}')
            print(f'  Esta ativo (método): {funcao.esta_ativo()}')
            print(f'  Usuario ID: {funcao.usuario_id}')
            print(f'  CargoFuncao ID: {funcao.cargo_funcao_id}')
            print('')
    except User.DoesNotExist:
        print('Usuário "erisman" não encontrado!')

if __name__ == '__main__':
    listar_funcoes_erisman() 