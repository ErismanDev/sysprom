#!/usr/bin/env python
"""
Script para testar a estrutura do modelo AtaSessao
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

from militares.models import AtaSessao, SessaoComissao

def testar_modelo_ata():
    """
    Testa a estrutura do modelo AtaSessao
    """
    print("🔍 TESTE DO MODELO ATASESSAO\n")
    
    # Buscar uma ata de sessão
    ata = AtaSessao.objects.first()
    if not ata:
        print("❌ Nenhuma ata de sessão encontrada")
        return
    
    print(f"📄 Ata encontrada: ID {ata.pk}")
    
    # Verificar se tem sessão
    if hasattr(ata, 'sessao'):
        print("✅ Ata tem relacionamento 'sessao'")
        
        sessao = ata.sessao
        print(f"📋 Sessão: {sessao}")
        
        # Verificar campos da sessão
        if hasattr(sessao, 'numero'):
            print(f"✅ Sessão tem campo 'numero': {sessao.numero}")
        else:
            print("❌ Sessão NÃO tem campo 'numero'")
            print(f"🔍 Campos disponíveis: {[f.name for f in sessao._meta.fields]}")
        
        if hasattr(sessao, 'data_sessao'):
            print(f"✅ Sessão tem campo 'data_sessao': {sessao.data_sessao}")
        else:
            print("❌ Sessão NÃO tem campo 'data_sessao'")
            print(f"🔍 Campos disponíveis: {[f.name for f in sessao._meta.fields]}")
        
        if hasattr(sessao, 'data'):
            print(f"✅ Sessão tem campo 'data': {sessao.data}")
        else:
            print("❌ Sessão NÃO tem campo 'data'")
            
    else:
        print("❌ Ata NÃO tem relacionamento 'sessao'")
        print(f"🔍 Campos disponíveis: {[f.name for f in ata._meta.fields]}")
    
    # Verificar se tem assinaturas
    if hasattr(ata, 'assinaturas'):
        print(f"✅ Ata tem relacionamento 'assinaturas': {ata.assinaturas.count()} assinaturas")
    else:
        print("❌ Ata NÃO tem relacionamento 'assinaturas'")

if __name__ == "__main__":
    testar_modelo_ata() 