#!/usr/bin/env python
"""
Script para testar o conteúdo exato do QR code
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
import qrcode
from io import BytesIO

def testar_qr_code():
    """
    Testa o conteúdo exato do QR code
    """
    print("🔍 TESTANDO CONTEÚDO DO QR CODE\n")
    
    # Buscar um quadro de acesso
    quadro = QuadroAcesso.objects.first()
    if not quadro:
        print("❌ Nenhum quadro de acesso encontrado")
        return
    
    print(f"📄 Quadro encontrado: ID {quadro.pk}")
    
    # Simular request
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    
    # Gerar autenticador
    autenticador = gerar_autenticador_veracidade(quadro, request, tipo_documento='quadro')
    
    print(f"🔗 URL do autenticador: {autenticador['url_autenticacao']}")
    
    # Verificar se a URL termina com vírgula
    if autenticador['url_autenticacao'].endswith(','):
        print("⚠️  PROBLEMA: URL termina com vírgula!")
    else:
        print("✅ URL sem vírgula")
    
    # Gerar QR code manualmente para comparar
    url_manual = autenticador['url_autenticacao']
    qr_manual = qrcode.make(url_manual)
    
    print(f"🔗 URL para QR code manual: {url_manual}")
    
    # Verificar se há caracteres especiais
    print(f"🔢 Comprimento da URL: {len(url_manual)}")
    print(f"🔢 Últimos 10 caracteres: '{url_manual[-10:]}'")
    
    # Verificar se há espaços ou caracteres invisíveis
    for i, char in enumerate(url_manual):
        if char.isspace() or ord(char) < 32:
            print(f"⚠️  Caractere especial na posição {i}: '{char}' (ord: {ord(char)})")
    
    # Testar se a URL é válida
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url_manual)
        print(f"✅ URL válida: {parsed.scheme}://{parsed.netloc}{parsed.path}")
    except Exception as e:
        print(f"❌ URL inválida: {e}")

if __name__ == '__main__':
    testar_qr_code() 