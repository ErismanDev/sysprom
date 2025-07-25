#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def testar_qr_code():
    print("=== TESTE: QR CODE ===\n")
    
    try:
        import qrcode
        print("✅ Módulo qrcode importado com sucesso")
        
        # Testar criação de QR code
        url = "https://sei.pi.gov.br/sei/controlador_externo.php?acao=documento_conferir&id_orgao_acesso_externo=0"
        qr = qrcode.make(url)
        print("✅ QR code criado com sucesso")
        
        # Testar salvamento em buffer
        from io import BytesIO
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        print("✅ QR code salvo em buffer com sucesso")
        
        # Testar criação de imagem para ReportLab
        from reportlab.platypus import Image
        from reportlab.lib.units import cm
        
        qr_img = Image(qr_buffer, width=2*cm, height=2*cm)
        print("✅ Imagem do QR code criada para ReportLab")
        
        print("\n✅ Todos os testes do QR code passaram!")
        
    except ImportError as e:
        print(f"❌ Erro ao importar qrcode: {e}")
    except Exception as e:
        print(f"❌ Erro ao criar QR code: {e}")

if __name__ == '__main__':
    testar_qr_code() 