#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.contrib.auth.models import User

print("=== CRIANDO DADOS DE TESTE PARA ORDENAÇÃO ===")
print()

# Criar usuário admin se não existir
user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@teste.com',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    user.set_password('admin123')
    user.save()
    print("✅ Usuário admin criado")

# Criar usuários únicos para cada militar
def criar_usuario_para_militar(nome, username):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@teste.com',
            'first_name': nome.split()[0],
            'last_name': ' '.join(nome.split()[1:]) if len(nome.split()) > 1 else '',
        }
    )
    if created:
        user.set_password('123456')
        user.save()
    return user

# Dados de teste para soldados com CHC
dados_soldados = [
    {'nome_completo': 'Soldado João Silva', 'nota_chc': 9.5, 'numeracao_antiguidade': 1},
    {'nome_completo': 'Soldado Maria Santos', 'nota_chc': 10.0, 'numeracao_antiguidade': 2},
    {'nome_completo': 'Soldado Pedro Costa', 'nota_chc': 8.8, 'numeracao_antiguidade': 3},
    {'nome_completo': 'Soldado Ana Oliveira', 'nota_chc': 9.2, 'numeracao_antiguidade': 4},
    {'nome_completo': 'Soldado Carlos Lima', 'nota_chc': 9.8, 'numeracao_antiguidade': 5},
]

# Dados de teste para cabos com CHSGT
dados_cabos = [
    {'nome_completo': 'Cabo Roberto Alves', 'nota_chsgt': 9.0, 'numeracao_antiguidade': 1},
    {'nome_completo': 'Cabo Fernanda Rocha', 'nota_chsgt': 9.7, 'numeracao_antiguidade': 2},
    {'nome_completo': 'Cabo Marcos Ferreira', 'nota_chsgt': 8.5, 'numeracao_antiguidade': 3},
    {'nome_completo': 'Cabo Juliana Martins', 'nota_chsgt': 9.9, 'numeracao_antiguidade': 4},
    {'nome_completo': 'Cabo Ricardo Souza', 'nota_chsgt': 9.3, 'numeracao_antiguidade': 5},
]

print("Criando soldados com CHC...")
for i, dados in enumerate(dados_soldados, 1):
    militar, created = Militar.objects.get_or_create(
        nome_completo=dados['nome_completo'],
        defaults={
            'nome_guerra': f'Soldado {i}',
            'matricula': f'2024{i:03d}',
            'cpf': f'1234567890{i:02d}',
            'posto_graduacao': 'Soldado',
            'data_ingresso': date(2020, 1, 1),
            'data_promocao_atual': date(2020, 1, 1),
            'data_nascimento': date(1990, 1, 1),
            'situacao': 'Ativo',
            'user': user,
            'nota_chc': dados['nota_chc'],
            'numeracao_antiguidade': dados['numeracao_antiguidade'],
            'curso_chc': True,
        }
    )
    if created:
        print(f"✅ Criado: {militar.nome_completo} - Nota CHC: {militar.nota_chc}")
    else:
        # Atualizar dados existentes
        militar.nota_chc = dados['nota_chc']
        militar.numeracao_antiguidade = dados['numeracao_antiguidade']
        militar.curso_chc = True
        militar.save()
        print(f"✅ Atualizado: {militar.nome_completo} - Nota CHC: {militar.nota_chc}")

print()
print("Criando cabos com CHSGT...")
for i, dados in enumerate(dados_cabos, 1):
    militar, created = Militar.objects.get_or_create(
        nome_completo=dados['nome_completo'],
        defaults={
            'nome_guerra': f'Cabo {i}',
            'matricula': f'2023{i:03d}',
            'cpf': f'9876543210{i:02d}',
            'posto_graduacao': 'Cabo',
            'data_ingresso': date(2019, 1, 1),
            'data_promocao_atual': date(2021, 1, 1),
            'data_nascimento': date(1985, 1, 1),
            'situacao': 'Ativo',
            'user': user,
            'nota_chsgt': dados['nota_chsgt'],
            'numeracao_antiguidade': dados['numeracao_antiguidade'],
            'curso_chsgt': True,
        }
    )
    if created:
        print(f"✅ Criado: {militar.nome_completo} - Nota CHSGT: {militar.nota_chsgt}")
    else:
        # Atualizar dados existentes
        militar.nota_chsgt = dados['nota_chsgt']
        militar.numeracao_antiguidade = dados['numeracao_antiguidade']
        militar.curso_chsgt = True
        militar.save()
        print(f"✅ Atualizado: {militar.nome_completo} - Nota CHSGT: {militar.nota_chsgt}")

print()
print("=== DADOS DE TESTE CRIADOS COM SUCESSO ===")
print("Execute 'python teste_ordenacao_chc.py' para verificar a ordenação") 