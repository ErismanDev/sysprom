#!/usr/bin/env python
"""
Script para testar detalhadamente a geração do QR code
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

def testar_qr_code_detalhado():
    """
    Testa detalhadamente a geração do QR code
    """
    print("🔍 TESTE DETALHADO DO QR CODE\n")
    
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
    
    print(f"🔗 URL do autenticador: '{autenticador['url_autenticacao']}'")
    
    # Teste 1: Gerar QR code diretamente
    url_direta = autenticador['url_autenticacao']
    qr_direto = qrcode.make(url_direta)
    
    # Salvar QR code direto
    buffer_direto = BytesIO()
    qr_direto.save(buffer_direto, format='PNG')
    buffer_direto.seek(0)
    
    print(f"✅ QR code direto gerado: {len(buffer_direto.getvalue())} bytes")
    
    # Teste 2: Verificar se há diferença na URL
    print(f"🔢 Caracteres da URL:")
    for i, char in enumerate(url_direta):
        print(f"  {i:2d}: '{char}' (ord: {ord(char):3d})")
    
    # Teste 3: Verificar se há caracteres especiais no final
    print(f"\n🔢 Últimos 5 caracteres:")
    for i in range(max(0, len(url_direta) - 5), len(url_direta)):
        char = url_direta[i]
        print(f"  {i:2d}: '{char}' (ord: {ord(char):3d})")
    
    # Teste 4: Verificar se a URL é igual à esperada
    url_esperada = f"http://127.0.0.1:8000/militares/quadros-acesso/{quadro.pk}/visualizar-html/"
    print(f"\n🔗 URL esperada: '{url_esperada}'")
    print(f"🔗 URL gerada:   '{url_direta}'")
    print(f"🔗 URLs iguais: {url_direta == url_esperada}")
    
    # Teste 5: Verificar se há espaços extras
    print(f"🔢 Comprimento esperado: {len(url_esperada)}")
    print(f"🔢 Comprimento gerado:   {len(url_direta)}")
    
    if len(url_direta) > len(url_esperada):
        print(f"⚠️  URL gerada tem {len(url_direta) - len(url_esperada)} caracteres extras")
        print(f"🔢 Caracteres extras: '{url_direta[len(url_esperada):]}'")

if __name__ == '__main__':
    testar_qr_code_detalhado() 