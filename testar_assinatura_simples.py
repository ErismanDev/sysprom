#!/usr/bin/env python3
"""
Script para testar a funcionalidade de assinatura eletrônica simples
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import SessaoComissao, AtaSessao, AssinaturaAta, MembroComissao, User
from django.utils import timezone

def testar_assinatura_simples():
    """Testar a funcionalidade de assinatura eletrônica simples"""
    print("=== TESTE: ASSINATURA ELETRÔNICA SIMPLES ===\n")
    
    # Buscar uma sessão com ata
    try:
        sessao = SessaoComissao.objects.filter(
            ata_editada__isnull=False
        ).first()
        
        if not sessao:
            print("❌ Nenhuma sessão com ata encontrada")
            return
        
        ata = sessao.ata_editada
        print(f"✅ Sessão encontrada: {sessao.numero}")
        print(f"✅ Ata encontrada: Versão {ata.versao}, Status: {ata.get_status_display()}")
        
        # Buscar um membro da comissão
        membro = MembroComissao.objects.filter(
            comissao=sessao.comissao,
            ativo=True
        ).first()
        
        if not membro:
            print("❌ Nenhum membro da comissão encontrado")
            return
        
        print(f"✅ Membro encontrado: {membro.militar.nome_completo}")
        
        # Simular dados de assinatura simples
        hash_documento = "teste_hash_123456"
        timestamp = timezone.now().isoformat()
        assinatura_digital = "assinatura_teste_base64"
        certificado = "ASSINATURA_SIMPLES_SEI"
        
        # Criar assinatura
        assinatura, created = AssinaturaAta.objects.get_or_create(
            ata=ata,
            membro=membro,
            defaults={
                'assinado_por': membro.usuario,
                'hash_documento': hash_documento,
                'timestamp': timestamp,
                'assinatura_digital': assinatura_digital,
                'certificado': certificado,
                'ip_assinatura': '127.0.0.1',
                'user_agent': 'Teste Script'
            }
        )
        
        if created:
            print(f"✅ Assinatura criada com sucesso!")
        else:
            print(f"✅ Assinatura atualizada!")
        
        print(f"   - Hash: {assinatura.hash_documento}")
        print(f"   - Timestamp: {assinatura.timestamp}")
        print(f"   - Certificado: {assinatura.certificado}")
        print(f"   - Data: {assinatura.data_assinatura}")
        
        # Verificar se a ata pode ser finalizada
        if ata.pode_ser_finalizada():
            print("✅ Ata pode ser finalizada!")
            ata.status = 'ASSINADA'
            ata.save()
            print("✅ Ata marcada como ASSINADA!")
        else:
            print("⚠️ Ata ainda não pode ser finalizada")
        
        # Mostrar todas as assinaturas da ata
        assinaturas = ata.assinaturas.all()
        print(f"\n📋 Total de assinaturas: {assinaturas.count()}")
        
        for i, assinatura in enumerate(assinaturas, 1):
            print(f"   {i}. {assinatura.membro.militar.nome_completo} - {assinatura.data_assinatura}")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_assinatura_simples() 