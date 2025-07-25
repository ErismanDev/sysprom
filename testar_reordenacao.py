#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_reordenacao():
    """Testa a reordenação após promoção"""
    
    print("=== TESTE DE REORDENAÇÃO APÓS PROMOÇÃO ===\n")
    
    # Buscar um Major para promover (independente do quadro)
    major = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='MJ'
    ).order_by('data_promocao_atual', 'pk').first()
    
    if not major:
        print("❌ Nenhum Major encontrado para teste")
        return
    
    print(f"🔍 Militar selecionado: {major.nome_completo}")
    print(f"📊 Posto atual: {major.posto_graduacao} (numeração: {major.numeracao_antiguidade})")
    
    # Listar Majores antes da promoção
    print(f"\n📋 Majores antes da promoção:")
    majores_antes = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='MJ',
        quadro='COMB'
    ).order_by('numeracao_antiguidade')
    
    for m in majores_antes:
        print(f"  - {m.nome_completo}: {m.numeracao_antiguidade}º")
    
    # Simular promoção
    posto_anterior = major.posto_graduacao
    quadro_anterior = major.quadro
    
    print(f"\n🚀 Promovendo {major.nome_completo} de {posto_anterior} para TC...")
    
    # Atualizar posto
    major.posto_graduacao = 'TC'
    
    # Atribuir numeração no novo posto
    major.atribuir_numeracao_por_promocao(posto_anterior, quadro_anterior)
    
    # Reordenar os Majores
    major.reordenar_posto_anterior_apos_promocao(posto_anterior, quadro_anterior)
    
    # Salvar
    major.save()
    
    print(f"✅ Promoção realizada!")
    print(f"📊 Novo posto: {major.posto_graduacao} (numeração: {major.numeracao_antiguidade})")
    
    # Listar Majores após a promoção
    print(f"\n📋 Majores após a promoção:")
    majores_depois = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='MJ',
        quadro='COMB'
    ).order_by('numeracao_antiguidade')
    
    for m in majores_depois:
        print(f"  - {m.nome_completo}: {m.numeracao_antiguidade}º")
    
    # Listar Tenentes-Coronéis
    print(f"\n📋 Tenentes-Coronéis:")
    tcs = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='TC',
        quadro='COMB'
    ).order_by('numeracao_antiguidade')
    
    for tc in tcs:
        print(f"  - {tc.nome_completo}: {tc.numeracao_antiguidade}º")
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    testar_reordenacao() 