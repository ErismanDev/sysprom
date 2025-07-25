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

def testar_datas_corrigidas():
    """Testa se as datas de promoção estão sendo aplicadas corretamente"""
    
    print("=== TESTE DE DATAS CORRIGIDAS NOS ALMANAQUES ===\n")
    
    # Testar os três tipos de almanaque
    tipos_teste = ['OFICIAIS', 'PRACAS', 'GERAL']
    
    for tipo in tipos_teste:
        print(f"🔍 Testando almanaque do tipo: {tipo}")
        
        # Verificar qual data deve aparecer
        if tipo == 'OFICIAIS':
            data_esperada = "18/07/2025 e 23/12/2025"
        elif tipo == 'PRACAS':
            data_esperada = "18/07/2025 e 25/12/2025"
        else:
            data_esperada = "18/07/2025"
        
        print(f"   📅 Data esperada: {data_esperada}")
        
        # Testar função de PDF alternativa
        try:
            print(f"   📄 Gerando PDF com função alternativa...")
            pdf_conteudo = gerar_pdf_almanaque_direct_old(tipo)
            
            # Verificar se a data está no PDF
            pdf_texto = pdf_conteudo.decode('utf-8', errors='ignore')
            if data_esperada in pdf_texto:
                print(f"   ✅ Data encontrada no PDF: {data_esperada}")
            else:
                print(f"   ❌ Data NÃO encontrada no PDF!")
                print(f"   🔍 Procurando por padrões de data no PDF...")
                
                # Procurar por padrões de data
                import re
                datas_encontradas = re.findall(r'\d{2}/\d{2}/\d{4}', pdf_texto)
                if datas_encontradas:
                    print(f"   📋 Datas encontradas no PDF: {datas_encontradas}")
                else:
                    print(f"   📋 Nenhuma data encontrada no PDF")
                    
        except Exception as e:
            print(f"   ❌ Erro ao gerar PDF: {e}")
        
        print()
    
    print("=== FIM DO TESTE ===")

if __name__ == "__main__":
    testar_datas_corrigidas() 