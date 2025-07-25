#!/usr/bin/env python
import os
import sys
import django
from django.db import models

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_numeracao_promocao():
    """Testa a numeração de promoção para entender o problema"""
    
    print("=== TESTE DE NUMERAÇÃO DE PROMOÇÃO ===\n")
    
    # Buscar militares ativos de um posto específico (ex: 1T - 1º Tenente)
    posto_teste = '1T'
    quadro_teste = 'COMB'
    
    print(f"Testando para posto: {posto_teste}, quadro: {quadro_teste}")
    
    # Listar militares existentes no posto
    militares_existentes = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto_teste,
        quadro=quadro_teste
    ).order_by('numeracao_antiguidade')
    
    print(f"\nMilitares existentes no posto {posto_teste}/{quadro_teste}:")
    for militar in militares_existentes:
        print(f"  - {militar.nome_completo}: {militar.numeracao_antiguidade}º")
    
    # Buscar a maior numeração existente
    max_numeracao = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto_teste,
        quadro=quadro_teste
    ).aggregate(
        models.Max('numeracao_antiguidade')
    )['numeracao_antiguidade__max']
    
    print(f"\nMaior numeração existente: {max_numeracao}")
    
    # Simular uma promoção
    print("\n=== SIMULANDO PROMOÇÃO ===")
    
    # Buscar um militar de posto inferior para simular promoção
    militar_para_promover = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='2T',  # 2º Tenente promovendo para 1º Tenente
        quadro=quadro_teste
    ).first()
    
    if not militar_para_promover:
        # Se não encontrar 2T, tentar com outro posto
        militar_para_promover = Militar.objects.filter(
            situacao='AT',
            posto_graduacao='CP',  # Capitão promovendo para Major
            quadro=quadro_teste
        ).first()
        posto_destino = 'MJ'
    else:
        posto_destino = posto_teste
    
    if militar_para_promover:
        print(f"Militar para promover: {militar_para_promover.nome_completo}")
        print(f"Posto atual: {militar_para_promover.posto_graduacao}")
        print(f"Numeração atual: {militar_para_promover.numeracao_antiguidade}")
        print(f"Posto destino: {posto_destino}")
        
        # Simular a promoção
        posto_anterior = militar_para_promover.posto_graduacao
        militar_para_promover.posto_graduacao = posto_destino
        
        # Chamar o método de atribuição de numeração
        nova_numeracao = militar_para_promover.atribuir_numeracao_por_promocao(posto_anterior, quadro_teste)
        
        print(f"\nNova numeração atribuída: {nova_numeracao}")
        
        # Verificar se a numeração está correta
        if nova_numeracao == (max_numeracao or 0) + 1:
            print("✅ Numeração correta!")
        else:
            print(f"❌ Numeração incorreta! Esperado: {(max_numeracao or 0) + 1}, Obtido: {nova_numeracao}")
        
        # Reverter a mudança para não afetar os dados
        militar_para_promover.posto_graduacao = posto_anterior
        militar_para_promover.numeracao_antiguidade = None
        militar_para_promover.save()
        
    else:
        print("Nenhum militar encontrado para simular promoção")
    
    # Testar com diferentes cenários
    print("\n=== TESTANDO DIFERENTES CENÁRIOS ===")
    
    # Cenário 1: Nenhum militar no posto
    print("\nCenário 1: Nenhum militar no posto")
    posto_vazio = 'CB'  # Coronel (assumindo que não há coronéis)
    militares_cb = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto_vazio,
        quadro=quadro_teste
    ).count()
    
    print(f"Militares no posto {posto_vazio}: {militares_cb}")
    
    if militares_cb == 0:
        # Simular promoção para posto vazio
        militar_teste = Militar.objects.filter(
            situacao='AT',
            posto_graduacao='TC',
            quadro=quadro_teste
        ).first()
        
        if militar_teste:
            posto_anterior = militar_teste.posto_graduacao
            militar_teste.posto_graduacao = posto_vazio
            
            nova_numeracao = militar_teste.atribuir_numeracao_por_promocao(posto_anterior, quadro_teste)
            print(f"Numeração atribuída para posto vazio: {nova_numeracao}")
            
            # Reverter
            militar_teste.posto_graduacao = posto_anterior
            militar_teste.numeracao_antiguidade = None
            militar_teste.save()
    
    # Cenário 2: Verificar se há gaps na numeração
    print("\nCenário 2: Verificando gaps na numeração")
    numeracoes = list(militares_existentes.values_list('numeracao_antiguidade', flat=True))
    print(f"Numerações existentes: {numeracoes}")
    
    if numeracoes:
        # Verificar se há gaps
        numeracoes_ordenadas = sorted(numeracoes)
        gaps = []
        for i in range(1, max(numeracoes_ordenadas) + 1):
            if i not in numeracoes_ordenadas:
                gaps.append(i)
        
        if gaps:
            print(f"Gaps encontrados: {gaps}")
        else:
            print("Não há gaps na numeração")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    testar_numeracao_promocao() 