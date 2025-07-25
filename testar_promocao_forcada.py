#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_promocao_forcada():
    print("=== TESTE DE PROMOÇÃO FORÇADA ===\n")
    
    # Buscar um subtenente ativo do quadro praças
    militar = Militar.objects.filter(posto_graduacao='ST', quadro='PRACAS', situacao='AT').first()
    if not militar:
        print("❌ Nenhum subtenente do quadro praças encontrado!")
        return
    print(f"Antes da promoção: {militar.nome_completo} | Posto: {militar.get_posto_graduacao_display()} | Quadro: {militar.get_quadro_display()} | Data Promoção: {militar.data_promocao_atual}")
    
    # Promover
    militar.posto_graduacao = '2T'
    militar.quadro = 'COMP'
    militar.data_promocao_atual = date.today()
    militar.save()
    militar.refresh_from_db()
    print(f"Após promoção (refresh do banco): {militar.nome_completo} | Posto: {militar.get_posto_graduacao_display()} | Quadro: {militar.get_quadro_display()} | Data Promoção: {militar.data_promocao_atual}")
    
    # Restaurar para teste
    militar.posto_graduacao = 'ST'
    militar.quadro = 'PRACAS'
    militar.save()
    print("\n🔄 Dados restaurados para teste.")
    print("✅ Teste concluído!")

if __name__ == "__main__":
    testar_promocao_forcada() 