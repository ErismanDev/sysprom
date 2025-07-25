#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.urls import reverse
from django.test import Client

def testar_simples():
    """Teste simples da funcionalidade de promoção"""
    
    print("=== TESTE SIMPLES DA PROMOÇÃO DE SUBTENENTE ===\n")
    
    # Buscar um subtenente para teste
    subtenente = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT'
    ).first()
    
    if not subtenente:
        print("❌ Nenhum subtenente encontrado!")
        return
    
    print(f"Subtenente: {subtenente.nome_completo}")
    print(f"ID: {subtenente.id}")
    print(f"Posto: {subtenente.posto_graduacao}")
    print(f"Quadro: {subtenente.quadro}")
    print(f"Situação: {subtenente.situacao}")
    print(f"Apto para promoção: {'Sim' if subtenente.apto_promocao_antiguidade() else 'Não'}")
    
    # Testar se a URL está configurada
    try:
        from militares.urls import urlpatterns
        urls_promocao = [url for url in urlpatterns if 'promocao_subtenente' in str(url)]
        if urls_promocao:
            print("✅ URL da promoção de subtenente está configurada")
        else:
            print("❌ URL da promoção de subtenente NÃO está configurada")
    except Exception as e:
        print(f"❌ Erro ao verificar URLs: {e}")
    
    # Testar se a view existe
    try:
        from militares.views import promocao_subtenente_view
        print("✅ View promocao_subtenente_view existe")
    except ImportError:
        print("❌ View promocao_subtenente_view NÃO existe")
    
    # Testar se o template existe
    template_path = "militares/templates/militares/promocao_subtenente.html"
    if os.path.exists(template_path):
        print("✅ Template promocao_subtenente.html existe")
    else:
        print("❌ Template promocao_subtenente.html NÃO existe")
    
    # Verificar se o botão está no template de detalhes
    detail_template_path = "militares/templates/militares/militar_detail.html"
    if os.path.exists(detail_template_path):
        with open(detail_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "Promover para 2º Tenente" in content:
                print("✅ Botão 'Promover para 2º Tenente' está no template")
            else:
                print("❌ Botão 'Promover para 2º Tenente' NÃO está no template")
    else:
        print("❌ Template militar_detail.html NÃO existe")
    
    print(f"\n--- INSTRUÇÕES PARA TESTE MANUAL ---")
    print(f"1. Acesse: http://127.0.0.1:8000/militares/{subtenente.id}/")
    print(f"2. Procure pelo botão amarelo 'Promover para 2º Tenente'")
    print(f"3. Se não aparecer, verifique se o militar é ST/PRACAS/AT")
    print(f"4. Clique no botão para testar a promoção")

if __name__ == "__main__":
    testar_simples() 