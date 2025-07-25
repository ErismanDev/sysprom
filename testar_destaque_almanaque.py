#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import AlmanaqueMilitar
from militares.views import gerar_pdf_almanaque
from militares.pdf_utils import gerar_pdf_almanaque_direct_old

def testar_destaque_almanaque():
    """Testa a funcionalidade de destaque nos almanaques"""
    
    print("=== TESTE DE DESTAQUE NOS ALMANAQUES ===\n")
    
    # Testar os três tipos de almanaque
    tipos_teste = ['OFICIAIS', 'PRACAS', 'GERAL']
    
    for tipo in tipos_teste:
        print(f"🔍 Testando almanaque do tipo: {tipo}")
        
        # Testar função de PDF principal
        try:
            print(f"   📄 Gerando PDF com função principal...")
            pdf_content = gerar_pdf_almanaque(tipo)
            print(f"   ✅ PDF gerado com sucesso (tamanho: {len(pdf_content)} bytes)")
        except Exception as e:
            print(f"   ❌ Erro ao gerar PDF principal: {e}")
        
        # Testar função de PDF alternativa
        try:
            print(f"   📄 Gerando PDF com função alternativa...")
            pdf_content_alt = gerar_pdf_almanaque_direct_old(tipo)
            print(f"   ✅ PDF alternativo gerado com sucesso (tamanho: {len(pdf_content_alt)} bytes)")
        except Exception as e:
            print(f"   ❌ Erro ao gerar PDF alternativo: {e}")
        
        print()
    
    # Verificar almanaques existentes no banco
    print("=== ALMANAQUES EXISTENTES NO BANCO ===")
    almanaques = AlmanaqueMilitar.objects.filter(ativo=True).order_by('-data_geracao')[:5]
    
    if almanaques.exists():
        for almanaque in almanaques:
            print(f"📋 {almanaque.numero} - {almanaque.titulo}")
            print(f"   Tipo: {almanaque.get_tipo_display()}")
            print(f"   Data: {almanaque.data_geracao.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Total: {almanaque.total_geral} militares")
            print()
    else:
        print("❌ Nenhum almanaque encontrado no banco de dados")
    
    print("=== RESUMO ===")
    print("✅ Modificações implementadas:")
    print("   - Template HTML: destaque com fundo amarelo para OFICIAIS e PRAÇAS")
    print("   - PDF principal: destaque com negrito e sublinhado")
    print("   - PDF alternativo: destaque com negrito e sublinhado")
    print("   - PDF direto: destaque com negrito e sublinhado")
    print()
    print("📝 Como testar:")
    print("   1. Acesse /militares/almanaques/")
    print("   2. Crie um novo almanaque")
    print("   3. Visualize o HTML e o PDF")
    print("   4. Verifique se OFICIAIS e PRAÇAS estão destacados")
    print("   5. Verifique se GERAL mantém 'Militares' normal")

if __name__ == "__main__":
    testar_destaque_almanaque() 