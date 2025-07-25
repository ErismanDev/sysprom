#!/usr/bin/env python
"""
Script para debugar a URL do quadro de acesso
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso
from militares.utils import gerar_autenticador_veracidade
from django.test import RequestFactory
from django.urls import reverse

def debug_url_quadro():
    """
    Debug da URL do quadro de acesso
    """
    print("🔍 DEBUG DA URL DO QUADRO DE ACESSO\n")
    
    # Buscar um quadro de acesso
    quadro = QuadroAcesso.objects.first()
    if not quadro:
        print("❌ Nenhum quadro de acesso encontrado")
        return
    
    print(f"📄 Quadro encontrado: ID {quadro.pk}")
    
    # Testar reverse da URL
    try:
        url_reverse = reverse('militares:visualizar_quadro_html', kwargs={'pk': quadro.pk})
        print(f"🔗 URL reverse: {url_reverse}")
    except Exception as e:
        print(f"❌ Erro no reverse: {e}")
        return
    
    # Simular request
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    
    # Gerar autenticador
    try:
        autenticador = gerar_autenticador_veracidade(quadro, request, tipo_documento='quadro')
        print(f"🔗 URL do autenticador: {autenticador['url_autenticacao']}")
        
        # Verificar se tem vírgula
        if autenticador['url_autenticacao'].endswith(','):
            print("⚠️  PROBLEMA: URL termina com vírgula!")
        else:
            print("✅ URL sem vírgula")
            
    except Exception as e:
        print(f"❌ Erro ao gerar autenticador: {e}")
    
    # Testar URL completa
    url_completa = f"http://127.0.0.1:8000{url_reverse}"
    print(f"🔗 URL completa: {url_completa}")
    
    # Verificar se a URL existe nas URLs do sistema
    from django.urls import get_resolver
    resolver = get_resolver()
    
    try:
        resolver.resolve(url_reverse)
        print("✅ URL resolve corretamente")
    except Exception as e:
        print(f"❌ URL não resolve: {e}")

if __name__ == '__main__':
    debug_url_quadro() 