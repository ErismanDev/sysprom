#!/usr/bin/env python
"""
Script para testar a verificação de votos de deliberação
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import VotoDeliberacao

def testar_verificacao_voto():
    print("🗳️ TESTE DA VERIFICAÇÃO DE VOTOS DE DELIBERAÇÃO\n")
    
    # Buscar votos existentes
    votos = VotoDeliberacao.objects.all()[:3]
    
    if not votos:
        print("❌ Nenhum voto de deliberação encontrado")
        return
    
    for voto in votos:
        print(f"📄 Voto encontrado: ID {voto.pk}")
        
        # Testar acesso ao membro
        if hasattr(voto, 'membro'):
            print("✅ Voto tem campo 'membro'")
            membro = voto.membro
            if hasattr(membro, 'militar'):
                print(f"✅ Membro tem militar: {membro.militar.nome_completo}")
            else:
                print("❌ Membro NÃO tem militar")
        else:
            print("❌ Voto NÃO tem campo 'membro'")
            print(f"🔍 Campos disponíveis: {[f.name for f in voto._meta.fields]}")
        
        # Testar campo data_registro
        if hasattr(voto, 'data_registro'):
            print(f"✅ Voto tem campo 'data_registro': {voto.data_registro}")
        else:
            print("❌ Voto NÃO tem campo 'data_registro'")
        
        # Testar campo assinado
        if hasattr(voto, 'assinado'):
            print(f"✅ Voto tem campo 'assinado': {voto.assinado}")
        else:
            print("❌ Voto NÃO tem campo 'assinado'")
        
        # Gerar códigos de verificação
        codigo_verificador = f"{voto.pk:08d}"
        codigo_crc = f"{hash(str(voto.pk)) % 0xFFFFFFF:07X}"
        
        print(f"🔢 Código Verificador: {codigo_verificador}")
        print(f"🔢 Código CRC: {codigo_crc}")
        print()

    print("✅ Teste concluído!")
    print("\n🔗 URL de Verificação: http://127.0.0.1:8000/militares/verificar-autenticidade/")
    print("📝 Use os códigos acima para testar a verificação")

if __name__ == "__main__":
    testar_verificacao_voto() 