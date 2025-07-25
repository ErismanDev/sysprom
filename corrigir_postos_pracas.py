#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def corrigir_postos_pracas():
    """Corrige os postos das praças que estão incorretos"""
    print("=== CORREÇÃO DE POSTOS DE PRACAS ===")
    
    # Buscar praças
    pracas = Militar.objects.filter(
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    
    print(f"Total de praças encontradas: {pracas.count()}")
    
    for militar in pracas:
        print(f"\n--- {militar.nome_completo} ---")
        print(f"Posto atual: {militar.posto_graduacao} ({militar.get_posto_graduacao_display()})")
        
        # Verificar se o nome sugere um posto diferente
        nome = militar.nome_completo.upper()
        posto_sugerido = None
        
        if 'SUBTENENTE' in nome or 'ST' in nome:
            posto_sugerido = 'ST'
        elif '1º SARGENTO' in nome or '1S' in nome:
            posto_sugerido = '1S'
        elif '2º SARGENTO' in nome or '2S' in nome:
            posto_sugerido = '2S'
        elif '3º SARGENTO' in nome or '3S' in nome:
            posto_sugerido = '3S'
        elif 'CABO' in nome or 'CAB' in nome:
            posto_sugerido = 'CAB'
        elif 'SOLDADO' in nome or 'SD' in nome:
            posto_sugerido = 'SD'
        
        if posto_sugerido and posto_sugerido != militar.posto_graduacao:
            print(f"  SUGESTÃO: Alterar de {militar.posto_graduacao} para {posto_sugerido}")
            
            # Perguntar se deve corrigir
            resposta = input(f"  Corrigir posto de {militar.posto_graduacao} para {posto_sugerido}? (s/n): ")
            if resposta.lower() == 's':
                militar.posto_graduacao = posto_sugerido
                militar.save()
                print(f"  ✓ Posto corrigido para {posto_sugerido}")
            else:
                print(f"  ✗ Posto mantido como {militar.posto_graduacao}")
        else:
            print(f"  ✓ Posto correto: {militar.posto_graduacao}")

if __name__ == "__main__":
    corrigir_postos_pracas() 