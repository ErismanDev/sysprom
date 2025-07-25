#!/usr/bin/env python
import os
import sys
import django
import requests
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_acesso_promocao():
    """Testa se a URL da promoção de subtenente está acessível"""
    
    print("=== TESTE DE ACESSO À PROMOÇÃO DE SUBTENENTE ===\n")
    
    # Buscar um subtenente apto para teste
    subtenente_teste = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT'
    ).first()
    
    if not subtenente_teste:
        print("❌ Nenhum subtenente encontrado para teste!")
        return
    
    print(f"Subtenente selecionado para teste: {subtenente_teste.nome_completo}")
    print(f"ID: {subtenente_teste.id}")
    print(f"Apto para promoção: {'Sim' if subtenente_teste.apto_promocao_antiguidade() else 'Não'}")
    
    # URLs para testar
    urls_teste = [
        f"http://127.0.0.1:8000/militares/promocao-subtenente/?militar_id={subtenente_teste.id}",
        f"http://127.0.0.1:8000/militares/{subtenente_teste.id}/",
    ]
    
    print(f"\n--- TESTANDO URLs ---")
    
    for url in urls_teste:
        print(f"\nTestando: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ URL acessível!")
                if "promocao-subtenente" in url:
                    print("✅ Página de promoção carregada com sucesso!")
            else:
                print(f"❌ Erro: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Erro de conexão - servidor não está rodando")
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    print(f"\n--- INSTRUÇÕES PARA TESTE MANUAL ---")
    print(f"1. Acesse: http://127.0.0.1:8000/militares/{subtenente_teste.id}/")
    print(f"2. Procure pelo botão 'Promover para 2º Tenente' (amarelo)")
    print(f"3. Clique no botão para acessar a página de promoção")
    print(f"4. Verifique se a página carrega corretamente")
    
    # Verificar se o botão aparece no template
    print(f"\n--- VERIFICAÇÃO DO TEMPLATE ---")
    print(f"Subtenente: {subtenente_teste.posto_graduacao} ({subtenente_teste.quadro})")
    print(f"Situação: {subtenente_teste.situacao}")
    
    if (subtenente_teste.posto_graduacao == 'ST' and 
        subtenente_teste.quadro == 'PRACAS' and 
        subtenente_teste.situacao == 'AT'):
        print("✅ Condições para exibir o botão estão atendidas")
    else:
        print("❌ Condições para exibir o botão NÃO estão atendidas")
        print(f"  - Posto deve ser 'ST': {subtenente_teste.posto_graduacao == 'ST'}")
        print(f"  - Quadro deve ser 'PRACAS': {subtenente_teste.quadro == 'PRACAS'}")
        print(f"  - Situação deve ser 'AT': {subtenente_teste.situacao == 'AT'}")

if __name__ == "__main__":
    testar_acesso_promocao() 