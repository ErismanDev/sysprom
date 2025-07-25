#!/usr/bin/env python
"""
Script para testar se há problema na geração do QR code no PDF
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
from reportlab.platypus import Image
from io import BytesIO

def testar_pdf_qr_code():
    """
    Testa se há problema na geração do QR code no PDF
    """
    print("🔍 TESTE DO QR CODE NO PDF\n")
    
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
    
    # Verificar se o QR code foi gerado corretamente
    qr_img = autenticador['qr_img']
    print(f"✅ QR code gerado: {type(qr_img)}")
    
    # Verificar se é uma imagem do ReportLab
    if isinstance(qr_img, Image):
        print(f"✅ É uma imagem do ReportLab")
        print(f"🔢 Largura: {qr_img.drawWidth}")
        print(f"🔢 Altura: {qr_img.drawHeight}")
    else:
        print(f"❌ Não é uma imagem do ReportLab: {type(qr_img)}")
    
    # Verificar se há algum problema no buffer
    try:
        # Tentar acessar o buffer do QR code
        if hasattr(qr_img, 'image'):
            print(f"✅ Imagem tem atributo 'image'")
        else:
            print(f"⚠️  Imagem não tem atributo 'image'")
    except Exception as e:
        print(f"❌ Erro ao acessar imagem: {e}")
    
    # Verificar se a URL está correta no texto de autenticação
    texto = autenticador['texto_autenticacao']
    print(f"\n📝 Texto de autenticação:")
    print(f"'{texto}'")
    
    # Verificar se há vírgula no texto
    if ',' in texto:
        print(f"⚠️  Vírgula encontrada no texto na posição: {texto.find(',')}")
    else:
        print(f"✅ Nenhuma vírgula no texto")

if __name__ == '__main__':
    testar_pdf_qr_code() 