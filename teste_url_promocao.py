#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from militares.models import Militar

def testar_url_promocao():
    """Testa se a URL da promoção de subtenente está acessível"""
    
    print("=== TESTE DA URL DE PROMOÇÃO DE SUBTENENTE ===\n")
    
    # Testar se a URL existe
    try:
        url = reverse('militares:promocao_subtenente')
        print(f"✅ URL encontrada: {url}")
    except Exception as e:
        print(f"❌ Erro ao encontrar URL: {e}")
        return
    
    # Buscar um subtenente para teste
    subtenente = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT'
    ).first()
    
    if not subtenente:
        print("❌ Nenhum subtenente encontrado para teste!")
        return
    
    print(f"Subtenente para teste: {subtenente.nome_completo}")
    print(f"ID: {subtenente.id}")
    
    # Testar acesso à URL com parâmetro
    client = Client()
    try:
        response = client.get(f'{url}?militar_id={subtenente.id}')
        print(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página carregada com sucesso!")
        else:
            print(f"❌ Erro ao carregar página: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao acessar URL: {e}")

if __name__ == '__main__':
    testar_url_promocao() 