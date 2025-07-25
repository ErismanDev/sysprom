#!/usr/bin/env python
"""
Script para testar a verificação de ata de sessão
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

from militares.models import AtaSessao

def testar_verificacao_ata():
    """
    Testa a verificação de ata de sessão
    """
    print("🔍 TESTE DE VERIFICAÇÃO DE ATA DE SESSÃO\n")
    
    # Buscar uma ata de sessão
    ata = AtaSessao.objects.first()
    if not ata:
        print("❌ Nenhuma ata de sessão encontrada")
        return
    
    print(f"📄 Ata encontrada: ID {ata.pk}")
    
    # Simular a verificação
    try:
        # Gerar códigos
        codigo_verificador = f"{ata.pk:08d}"
        codigo_crc = f"{hash(str(ata.pk)) % 0xFFFFFFF:07X}"
        
        print(f"🔢 Código Verificador: {codigo_verificador}")
        print(f"🔢 Código CRC: {codigo_crc}")
        
        # Simular a lógica da view
        documento_id = int(codigo_verificador[:8])
        codigo_crc_esperado = f"{hash(str(documento_id)) % 0xFFFFFFF:07X}"
        
        if codigo_crc.upper() == codigo_crc_esperado:
            print("✅ Códigos válidos!")
            
            # Buscar o documento
            documento = AtaSessao.objects.get(pk=documento_id)
            print(f"📋 Documento encontrado: {documento}")
            
            # Verificar se tem sessão
            if hasattr(documento, 'sessao') and documento.sessao:
                print(f"📋 Sessão: {documento.sessao}")
                print(f"🔢 Número da sessão: {documento.sessao.numero}")
                print(f"📅 Data da sessão: {documento.sessao.data_sessao}")
                
                # Criar resultado
                resultado = {
                    'tipo': 'Ata de Sessão',
                    'titulo': f'Ata da Sessão {documento.sessao.numero}',
                    'data_criacao': documento.sessao.data_sessao,
                    'assinaturas': documento.assinaturas.count()
                }
                
                print("✅ Resultado criado com sucesso!")
                print(f"📄 Tipo: {resultado['tipo']}")
                print(f"📄 Título: {resultado['titulo']}")
                print(f"📄 Data: {resultado['data_criacao']}")
                print(f"📄 Assinaturas: {resultado['assinaturas']}")
                
            else:
                print("❌ Documento não tem sessão associada")
                
        else:
            print("❌ Códigos inválidos")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_verificacao_ata() 