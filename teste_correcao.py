#!/usr/bin/env python
"""
Script para testar a correção da reordenação de antiguidade
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
    """Mostra o estado atual dos militares buscados do banco"""
    print("\n=== ESTADO ATUAL (direto do banco) ===")
    militares = Militar.objects.filter(
        nome_completo__startswith='TESTE'
    ).order_by('numeracao_antiguidade', 'id')
    if not militares:
        print("(Nenhum militar encontrado)")
    for militar in militares:
        print(f"ID: {militar.id} | {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    print(f"Total de militares: {militares.count()}")
    print("==================\n")

def testar_correcao():
    print("=== TESTE DA CORREÇÃO ===")
    militares = criar_militares_teste()
    print("Estado inicial:")
    mostrar_estado_atual()
    militar_3 = militares[2]
    print(f"Movendo {militar_3.nome_completo} da posição {militar_3.numeracao_antiguidade} para posição 1")
    militar_3.numeracao_antiguidade = 1
    militar_3.save()
    print("Após salvar no banco:")
    mostrar_estado_atual()
    print("Executando reordenação corrigida...")
    militar_3.reordenar_numeracoes_apos_alteracao(3)
    # Forçar refresh do objeto militar_3
    militar_3.refresh_from_db()
    print("Após reordenação corrigida:")
    mostrar_estado_atual()
    print(f"Militar movido após refresh: {militar_3.nome_completo} | Antiguidade: {militar_3.numeracao_antiguidade}")
    print("Resultado esperado:")
    print("- TESTE Militar 3 deve estar na posição 1")
    print("- TESTE Militar 1 deve estar na posição 2")
    print("- TESTE Militar 2 deve estar na posição 3")
    print("\nResultado atual:")
    militares_finais = Militar.objects.filter(nome_completo__startswith='TESTE').order_by('numeracao_antiguidade', 'id')
    for militar in militares_finais:
        print(f"- {militar.nome_completo}: posição {militar.numeracao_antiguidade}")
    numeracoes = [m.numeracao_antiguidade for m in militares_finais]
    if len(numeracoes) != len(set(numeracoes)):
        print("❌ CORREÇÃO NÃO FUNCIONOU! (duplicatas)")
    elif numeracoes == [1, 2, 3]:
        print("✅ CORREÇÃO FUNCIONOU!")
    else:
        print(f"❌ CORREÇÃO NÃO FUNCIONOU! (sequência incorreta: {numeracoes})")
    print("\nTeste concluído!")

if __name__ == "__main__":
    testar_correcao() 