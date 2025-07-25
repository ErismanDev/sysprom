#!/usr/bin/env python
"""
Script para testar o problema de reordenação de antiguidade
Problema: quando um militar é movido da posição 3 para 1, o militar que estava na posição 1 não é empurrado
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.contrib.auth.models import User

def criar_militares_teste():
    """Cria militares de teste para reproduzir o problema"""
    
    # Criar usuário de teste se não existir
    user, created = User.objects.get_or_create(
        username='teste',
        defaults={'email': 'teste@teste.com'}
    )
    
    # Limpar militares de teste existentes
    Militar.objects.filter(nome_completo__startswith='TESTE').delete()
    
    # Criar 3 militares de teste
    militares = []
    for i in range(1, 4):
        militar = Militar.objects.create(
            numeracao_antiguidade=i,
            matricula=f'TESTE{i:03d}',
            nome_completo=f'TESTE Militar {i}',
            nome_guerra=f'TESTE{i}',
            cpf=f'111.111.111-{i:02d}',
            rg=f'1234567{i}',
            orgao_expedidor='SSP',
            data_nascimento='1990-01-01',
            sexo='M',
            quadro='COMB',
            posto_graduacao='CP',
            data_ingresso='2010-01-01',
            data_promocao_atual='2020-01-01',
            situacao='AT',
            email=f'teste{i}@teste.com',
            telefone='(11) 1111-1111',
            celular='(11) 99999-9999'
        )
        militares.append(militar)
        print(f"Criado militar {i}: {militar.nome_completo} - Antiguidade: {militar.numeracao_antiguidade}")
    
    return militares

def mostrar_estado_atual():
    """Mostra o estado atual dos militares"""
    print("\n=== ESTADO ATUAL ===")
    militares = Militar.objects.filter(
        nome_completo__startswith='TESTE'
    ).order_by('numeracao_antiguidade')
    
    for militar in militares:
        print(f"{militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    print("==================\n")

def testar_problema_reordenacao():
    """Testa o problema de reordenação"""
    
    print("=== TESTE DE REORDENAÇÃO ===")
    
    # Criar militares de teste
    militares = criar_militares_teste()
    
    # Mostrar estado inicial
    print("\nEstado inicial:")
    mostrar_estado_atual()
    
    # Simular o problema: mover militar 3 para posição 1
    militar_3 = militares[2]  # Militar na posição 3
    militar_1 = militares[0]  # Militar na posição 1
    
    print(f"Movendo {militar_3.nome_completo} da posição {militar_3.numeracao_antiguidade} para posição 1")
    
    # Alterar a numeração do militar 3 para 1
    militar_3.numeracao_antiguidade = 1
    militar_3.save()
    
    print(f"\nApós alteração direta:")
    mostrar_estado_atual()
    
    # Agora testar a reordenação automática
    print("Executando reordenação automática...")
    militar_3.reordenar_numeracoes_apos_alteracao()
    
    print(f"\nApós reordenação automática:")
    mostrar_estado_atual()
    
    # Verificar se há duplicatas
    numeracoes = list(Militar.objects.filter(
        nome_completo__startswith='TESTE'
    ).values_list('numeracao_antiguidade', flat=True))
    
    duplicatas = [n for n in numeracoes if numeracoes.count(n) > 1]
    if duplicatas:
        print(f"❌ PROBLEMA ENCONTRADO: Numerações duplicadas: {duplicatas}")
    else:
        print("✅ Nenhuma duplicata encontrada")
    
    # Verificar se a sequência está correta
    numeracoes_ordenadas = sorted(numeracoes)
    if numeracoes == numeracoes_ordenadas and len(numeracoes) == len(set(numeracoes)):
        print("✅ Sequência correta")
    else:
        print("❌ Sequência incorreta")
    
    return militares

def testar_admin_save():
    """Testa o método save_model do admin"""
    
    print("\n=== TESTE DO ADMIN SAVE ===")
    
    # Criar militares de teste
    militares = criar_militares_teste()
    
    print("\nEstado inicial:")
    mostrar_estado_atual()
    
    # Simular o que o admin faz
    from militares.admin import MilitarAdmin
    from django.contrib.admin import ModelForm
    
    # Criar um formulário simulado
    class TestForm:
        def __init__(self, changed_data):
            self.changed_data = changed_data
    
    # Simular a alteração via admin
    militar_3 = militares[2]
    militar_1 = militares[0]
    
    print(f"Simulando alteração via admin: {militar_3.nome_completo} -> posição 1")
    
    # Simular o save_model do admin
    numeracao_anterior = militar_3.numeracao_antiguidade
    militar_3.numeracao_antiguidade = 1
    militar_3.save()
    
    print(f"\nApós salvar no banco:")
    mostrar_estado_atual()
    
    # Chamar reordenação como o admin faz
    militar_3.reordenar_numeracoes_apos_alteracao(numeracao_anterior)
    
    print(f"\nApós reordenação do admin:")
    mostrar_estado_atual()

if __name__ == '__main__':
    print("Iniciando testes de reordenação...")
    
    # Teste 1: Reordenação direta
    testar_problema_reordenacao()
    
    # Teste 2: Simulação do admin
    testar_admin_save()
    
    print("\nTestes concluídos!") 