#!/usr/bin/env python
"""
Script para testar a verificação de autenticidade
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, AtaSessao, VotoDeliberacao, QuadroFixacaoVagas

def testar_verificacao():
    """
    Testa a verificação de autenticidade com documentos existentes
    """
    print("🧪 TESTANDO VERIFICAÇÃO DE AUTENTICIDADE\n")
    
    # Testar Quadro de Acesso
    print("📋 Testando Quadro de Acesso:")
    quadros = QuadroAcesso.objects.all()[:3]
    for quadro in quadros:
        codigo_verificador = f"{quadro.pk:08d}"
        codigo_crc = f"{hash(str(quadro.pk)) % 0xFFFFFFF:07X}"
        print(f"  ID: {quadro.pk}")
        print(f"  Código Verificador: {codigo_verificador}")
        print(f"  Código CRC: {codigo_crc}")
        print(f"  Tipo: {quadro.get_tipo_display()}")
        print()
    
    # Testar Ata de Sessão
    print("📄 Testando Ata de Sessão:")
    atas = AtaSessao.objects.all()[:3]
    for ata in atas:
        codigo_verificador = f"{ata.pk:08d}"
        codigo_crc = f"{hash(str(ata.pk)) % 0xFFFFFFF:07X}"
        print(f"  ID: {ata.pk}")
        print(f"  Código Verificador: {codigo_verificador}")
        print(f"  Código CRC: {codigo_crc}")
        print(f"  Sessão: {ata.sessao.numero}")
        print()
    
    # Testar Voto de Deliberação
    print("🗳️ Testando Voto de Deliberação:")
    votos = VotoDeliberacao.objects.all()[:3]
    for voto in votos:
        codigo_verificador = f"{voto.pk:08d}"
        codigo_crc = f"{hash(str(voto.pk)) % 0xFFFFFFF:07X}"
        print(f"  ID: {voto.pk}")
        print(f"  Código Verificador: {codigo_verificador}")
        print(f"  Código CRC: {codigo_crc}")
        try:
            print(f"  Militar: {voto.membro.militar.nome_completo}")
        except:
            print(f"  Militar: N/A")
        print()
    
    # Testar Quadro de Fixação de Vagas
    print("📋 Testando Quadro de Fixação de Vagas:")
    quadros_fixacao = QuadroFixacaoVagas.objects.all()[:3]
    for quadro in quadros_fixacao:
        codigo_verificador = f"{quadro.pk:08d}"
        codigo_crc = f"{hash(str(quadro.pk)) % 0xFFFFFFF:07X}"
        print(f"  ID: {quadro.pk}")
        print(f"  Código Verificador: {codigo_verificador}")
        print(f"  Código CRC: {codigo_crc}")
        print(f"  Tipo: {quadro.get_tipo_display()}")
        print()
    
    print("✅ Teste concluído!")
    print("\n🔗 URL de Verificação: http://127.0.0.1:8000/militares/verificar-autenticidade/")
    print("📝 Use os códigos acima para testar a verificação")

if __name__ == "__main__":
    testar_verificacao() 