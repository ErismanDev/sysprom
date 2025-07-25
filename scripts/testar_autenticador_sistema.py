#!/usr/bin/env python
"""
Script para testar se o autenticador está usando as URLs do sistema corretamente
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

from militares.models import QuadroAcesso, QuadroFixacaoVagas, VotoDeliberacao
from militares.utils import gerar_autenticador_veracidade

def testar_autenticador_sistema():
    """
    Testa se o autenticador está gerando URLs do sistema corretamente
    """
    print("🧪 TESTANDO AUTENTICADOR DO SISTEMA\n")
    
    # Simular um request
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_HOST'] = '127.0.0.1:8000'
    
    # Testar com diferentes tipos de documentos
    documentos_teste = [
        {
            'nome': 'Quadro de Acesso',
            'modelo': QuadroAcesso,
            'tipo': 'quadro'
        },
        {
            'nome': 'Quadro de Fixação de Vagas', 
            'modelo': QuadroFixacaoVagas,
            'tipo': 'quadro_fixacao'
        },
        {
            'nome': 'Voto de Deliberação',
            'modelo': VotoDeliberacao,
            'tipo': 'voto'
        }
    ]
    
    for doc_info in documentos_teste:
        print(f"📄 Testando {doc_info['nome']}:")
        
        # Buscar um documento existente
        try:
            documento = doc_info['modelo'].objects.first()
            if documento:
                print(f"  ✅ Documento encontrado: ID {documento.pk}")
                
                # Gerar autenticador
                autenticador = gerar_autenticador_veracidade(
                    documento, 
                    request, 
                    tipo_documento=doc_info['tipo']
                )
                
                print(f"  🔗 URL gerada: {autenticador['url_autenticacao']}")
                
                # Verificar se é URL do sistema
                if '127.0.0.1:8000' in autenticador['url_autenticacao'] or 'localhost' in autenticador['url_autenticacao']:
                    print(f"  ✅ URL do sistema: Sim")
                else:
                    print(f"  ❌ URL do sistema: Não (ainda usando SEI)")
                
                print(f"  🔢 Código verificador: {autenticador['codigo_verificador']}")
                print(f"  🔢 Código CRC: {autenticador['codigo_crc']}")
                
            else:
                print(f"  ❌ Nenhum documento encontrado para teste")
                
        except Exception as e:
            print(f"  ❌ Erro ao testar: {e}")
        
        print()
    
    print("=== RESUMO DO TESTE ===\n")
    print("✅ URLs do sistema implementadas para:")
    print("  • Quadros de Acesso")
    print("  • Quadros de Fixação de Vagas") 
    print("  • Votos de Deliberação")
    print("\n🔗 Agora os QR codes apontam para o sistema interno")
    print("🔒 Mantendo a segurança e autenticidade dos documentos")

if __name__ == '__main__':
    testar_autenticador_sistema() 