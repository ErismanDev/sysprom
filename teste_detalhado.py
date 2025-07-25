#!/usr/bin/env python
"""
Script para testar detalhadamente a reordenação de antiguidade
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
            matricula=f'TESTE{i:03d}',
            nome_completo=f'TESTE Militar {i}',
            nome_guerra=f'TESTE{i}',
            cpf=f'111.111.111-{i:02d}',
            rg=f'1234567-{i}',
            orgao_expedidor='SSP',
            data_nascimento='1990-01-01',
            sexo='M',
            quadro='COMB',
            posto_graduacao='2T',
            data_ingresso='2010-01-01',
            data_promocao_atual='2020-01-01',
            situacao='AT',
            email=f'teste{i}@teste.com',
            telefone='(11) 1111-1111',
            celular='(11) 99999-9999',
            numeracao_antiguidade=i
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

def testar_reordenacao_detalhada():
    """Testa a reordenação com mais detalhes"""
    print("=== TESTE DETALHADO DA REORDENAÇÃO ===")
    
    # Criar militares
    militares = criar_militares_teste()
    
    print("Estado inicial:")
    mostrar_estado_atual()
    
    # Pegar o militar 3 (posição 3)
    militar_3 = militares[2]  # índice 2 = militar 3
    
    print(f"Movendo {militar_3.nome_completo} da posição {militar_3.numeracao_antiguidade} para posição 1")
    
    # Salvar no banco primeiro
    militar_3.numeracao_antiguidade = 1
    militar_3.save()
    
    print("Após salvar no banco:")
    mostrar_estado_atual()
    
    # Executar reordenação
    print("Executando reordenação...")
    militar_3.reordenar_numeracoes_apos_alteracao(3)  # numeracao_anterior=3
    
    print("Após reordenação:")
    mostrar_estado_atual()
    
    # Verificar resultado
    militares_finais = Militar.objects.filter(
        nome_completo__startswith='TESTE'
    ).order_by('numeracao_antiguidade')
    
    print("=== VERIFICAÇÃO FINAL ===")
    numeracoes = []
    for militar in militares_finais:
        numeracoes.append(militar.numeracao_antiguidade)
        print(f"{militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Verificar se há duplicatas
    if len(numeracoes) != len(set(numeracoes)):
        print("❌ DUPLICATAS ENCONTRADAS!")
    else:
        print("✅ Nenhuma duplicata encontrada")
    
    # Verificar se a sequência está correta
    esperado = [1, 2, 3]
    if numeracoes == esperado:
        print("✅ Sequência correta")
    else:
        print(f"❌ Sequência incorreta. Esperado: {esperado}, Atual: {numeracoes}")
    
    print("Teste detalhado concluído!")

if __name__ == "__main__":
    testar_reordenacao_detalhada() 