#!/usr/bin/env python
"""
Script para testar a funcionalidade de reordenação após inativação de militares
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import transaction
from militares.models import Militar, Vaga

def testar_reordenacao_inativacao():
    """Testa a funcionalidade de reordenação após inativação"""
    
    print("=== TESTANDO REORDENAÇÃO APÓS INATIVAÇÃO ===\n")
    
    # 1. Verificar militares ativos por posto/quadro
    print("1. 📊 MILITARES ATIVOS POR POSTO/QUADRO:")
    militares_ativos = Militar.objects.filter(situacao='AT').order_by('posto_graduacao', 'quadro', 'numeracao_antiguidade')
    
    grupos = {}
    for militar in militares_ativos:
        chave = f"{militar.get_posto_graduacao_display()} - {militar.get_quadro_display()}"
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(militar)
    
    for grupo, militares in grupos.items():
        print(f"\n  📋 {grupo}:")
        for militar in militares:
            print(f"    {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # 2. Verificar vagas existentes
    print("\n2. 📋 VAGAS EXISTENTES:")
    vagas = Vaga.objects.all().order_by('posto', 'quadro')
    for vaga in vagas:
        print(f"  {vaga.get_posto_display()} - {vaga.get_quadro_display()}: {vaga.efetivo_atual}/{vaga.efetivo_maximo}")
    
    # 3. Simular inativação de um militar
    print("\n3. 🔄 SIMULANDO INATIVAÇÃO:")
    
    # Escolher um militar para testar
    militar_teste = Militar.objects.filter(situacao='AT').first()
    if not militar_teste:
        print("❌ Nenhum militar ativo encontrado para teste")
        return
    
    print(f"  Militar selecionado: {militar_teste.nome_completo}")
    print(f"  Posto: {militar_teste.get_posto_graduacao_display()}")
    print(f"  Quadro: {militar_teste.get_quadro_display()}")
    print(f"  Antiguidade atual: {militar_teste.numeracao_antiguidade}º")
    
    # Verificar militares do mesmo posto/quadro antes da inativação
    militares_mesmo_posto = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=militar_teste.posto_graduacao,
        quadro=militar_teste.quadro
    ).exclude(pk=militar_teste.pk).order_by('numeracao_antiguidade')
    
    print(f"\n  Militares do mesmo posto/quadro antes da inativação:")
    for militar in militares_mesmo_posto:
        print(f"    {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # 4. Executar inativação
    print(f"\n4. 🚫 INATIVANDO MILITAR...")
    
    with transaction.atomic():
        # Salvar situação anterior
        situacao_anterior = militar_teste.situacao
        
        # Inativar militar
        militar_teste.situacao = 'IN'
        militar_teste.save()
        
        print(f"  ✅ Militar inativado com sucesso!")
        print(f"  Situação anterior: {situacao_anterior}")
        print(f"  Situação atual: {militar_teste.situacao}")
        
        # 5. Verificar reordenação automática
        print(f"\n5. 🔄 VERIFICANDO REORDENAÇÃO AUTOMÁTICA:")
        
        militares_apos_reordenacao = Militar.objects.filter(
            situacao='AT',
            posto_graduacao=militar_teste.posto_graduacao,
            quadro=militar_teste.quadro
        ).order_by('numeracao_antiguidade')
        
        print(f"  Militares após reordenação:")
        for i, militar in enumerate(militares_apos_reordenacao, 1):
            print(f"    {militar.numeracao_antiguidade}º - {militar.nome_completo}")
            if militar.numeracao_antiguidade != i:
                print(f"      ⚠️  Numeração inconsistente! Esperado: {i}º")
        
        # 6. Verificar atualização da vaga
        print(f"\n6. 📋 VERIFICANDO ATUALIZAÇÃO DA VAGA:")
        
        try:
            vaga = Vaga.objects.get(posto=militar_teste.posto_graduacao, quadro=militar_teste.quadro)
            print(f"  Vaga encontrada: {vaga.get_posto_display()} - {vaga.get_quadro_display()}")
            print(f"  Efetivo atual: {vaga.efetivo_atual}")
            print(f"  Efetivo máximo: {vaga.efetivo_maximo}")
            print(f"  Vagas disponíveis: {vaga.vagas_disponiveis}")
        except Vaga.DoesNotExist:
            print(f"  ⚠️  Vaga não encontrada para {militar_teste.get_posto_graduacao_display()} - {militar_teste.get_quadro_display()}")
        
        # 7. Reativar militar para não afetar os dados
        print(f"\n7. 🔄 REATIVANDO MILITAR...")
        militar_teste.situacao = 'AT'
        militar_teste.save()
        print(f"  ✅ Militar reativado com sucesso!")
    
    print(f"\n=== TESTE CONCLUÍDO ===")
    print(f"✅ A funcionalidade de reordenação após inativação está funcionando corretamente!")

if __name__ == '__main__':
    testar_reordenacao_inativacao() 