#!/usr/bin/env python
"""
Teste específico para reproduzir o problema: mover 6 para 1
"""

import os
import sys
import django
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.contrib.auth.models import User

def testar_problema_6_para_1():
    """Testa o problema específico: mover militar 6 para posição 1"""
    
    print("=== TESTE ESPECÍFICO: MOVER 6 PARA 1 ===")
    
    # Prefixo aleatório para garantir unicidade
    prefixo = random.randint(1000, 9999)
    
    # Criar militares de teste se não existirem
    user, created = User.objects.get_or_create(
        username='teste',
        defaults={'email': 'teste@teste.com'}
    )
    
    # Limpar militares de teste existentes
    Militar.objects.filter(nome_completo__startswith=f'TESTE_PROBLEMA_{prefixo}').delete()
    
    # Criar 6 militares de teste
    militares = []
    for i in range(1, 7):
        militar = Militar.objects.create(
            nome_completo=f'TESTE_PROBLEMA_{prefixo} Militar {i}',
            nome_guerra=f'Militar {i}',
            matricula=f'TESTE{prefixo}{i:03d}',
            cpf=f'{prefixo}{i:09d}',
            rg=f'1234567{prefixo}{i}',
            orgao_expedidor='SSP',
            data_nascimento='1990-01-01',
            sexo='M',
            quadro='COMB',
            posto_graduacao='2T',
            data_ingresso='2020-01-01',
            data_promocao_atual='2020-01-01',
            situacao='AT',
            email=f'militar{i}@teste.com',
            telefone='(11) 1111-1111',
            celular='(11) 99999-9999',
            numeracao_antiguidade=i
        )
        militares.append(militar)
    
    print("Estado inicial:")
    for militar in militares:
        print(f"  - {militar.nome_completo}: {militar.numeracao_antiguidade}º")
    
    # Pegar o militar 6
    militar_6 = Militar.objects.get(nome_completo=f'TESTE_PROBLEMA_{prefixo} Militar 6')
    numeracao_anterior = militar_6.numeracao_antiguidade
    
    print(f"\nMovendo {militar_6.nome_completo} da posição {numeracao_anterior} para 1...")
    
    # Alterar para posição 1
    militar_6.numeracao_antiguidade = 1
    militar_6.save()
    
    # Chamar reordenação
    militar_6.reordenar_numeracoes_apos_alteracao(numeracao_anterior)
    
    # Verificar resultado
    print("\nEstado após reordenação:")
    militares_atualizados = Militar.objects.filter(
        nome_completo__startswith=f'TESTE_PROBLEMA_{prefixo}'
    ).order_by('numeracao_antiguidade')
    
    for militar in militares_atualizados:
        print(f"  - {militar.nome_completo}: {militar.numeracao_antiguidade}º")
    
    # Verificar se não há duplicatas
    numeracoes = [m.numeracao_antiguidade for m in militares_atualizados if m.numeracao_antiguidade]
    duplicatas = len(numeracoes) != len(set(numeracoes))
    
    if duplicatas:
        print("❌ ERRO: Há numerações duplicadas!")
        print(f"Numerações: {numeracoes}")
    else:
        print("✅ SUCESSO: Não há duplicatas!")
        print(f"Numerações: {numeracoes}")
    
    # Verificar se o militar 1 foi empurrado para 2
    militar_1_original = Militar.objects.get(nome_completo=f'TESTE_PROBLEMA_{prefixo} Militar 1')
    if militar_1_original.numeracao_antiguidade == 2:
        print("✅ Militar 1 foi empurrado corretamente para posição 2")
    else:
        print(f"❌ ERRO: Militar 1 não foi empurrado corretamente. Está na posição {militar_1_original.numeracao_antiguidade}")
    
    # Verificar se o militar 2 foi empurrado para 3
    militar_2_original = Militar.objects.get(nome_completo=f'TESTE_PROBLEMA_{prefixo} Militar 2')
    if militar_2_original.numeracao_antiguidade == 3:
        print("✅ Militar 2 foi empurrado corretamente para posição 3")
    else:
        print(f"❌ ERRO: Militar 2 não foi empurrado corretamente. Está na posição {militar_2_original.numeracao_antiguidade}")
    
    # Verificar se o militar 6 está na posição 1
    militar_6.refresh_from_db()
    if militar_6.numeracao_antiguidade == 1:
        print("✅ Militar 6 está corretamente na posição 1")
    else:
        print(f"❌ ERRO: Militar 6 não está na posição 1. Está na posição {militar_6.numeracao_antiguidade}")

if __name__ == "__main__":
    testar_problema_6_para_1() 