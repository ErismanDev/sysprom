#!/usr/bin/env python
"""
Script para testar a geração de PDF de atas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import AtaSessao, SessaoComissao
from django.contrib.auth.models import User

def testar_pdf_ata():
    """Testar se a função de gerar PDF funciona para atas em rascunho"""
    
    # Buscar uma sessão com ata
    try:
        sessao = SessaoComissao.objects.filter(ata_editada__isnull=False).first()
        if not sessao:
            print("❌ Nenhuma sessão com ata encontrada")
            return
        
        ata = sessao.ata_editada
        print(f"✅ Sessão encontrada: {sessao.numero}")
        print(f"✅ Ata encontrada: ID {ata.pk}")
        print(f"✅ Status da ata: {ata.status}")
        print(f"✅ Conteúdo da ata: {len(ata.conteudo)} caracteres")
        
        # Usar um usuário existente
        user = User.objects.first()
        if not user:
            print("❌ Nenhum usuário encontrado no sistema")
            return
        
        print(f"✅ Usando usuário: {user.username}")
        
        # Simular uma requisição para gerar PDF
        from django.test import RequestFactory
        from militares.views import ata_gerar_pdf
        
        # Criar requisição
        factory = RequestFactory()
        request = factory.get(f'/militares/comissao/sessoes/{sessao.pk}/ata-gerar-pdf/')
        request.user = user
        
        # Chamar a função
        print(f"🔄 Tentando gerar PDF para ata {ata.pk}...")
        response = ata_gerar_pdf(request, sessao.pk)
        
        print(f"✅ Status da resposta: {response.status_code}")
        print(f"✅ Tipo de conteúdo: {response.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print("✅ PDF gerado com sucesso!")
            print(f"✅ Tamanho do PDF: {len(response.content)} bytes")
        else:
            print(f"❌ Erro ao gerar PDF: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_pdf_ata() 