#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoPracas, FichaConceitoOficiais

def test_fichas_pracas():
    """Testa as fichas de praças e verifica os dados"""
    print("=== TESTE DE FICHAS DE PRACAS ===")
    
    # Buscar todas as fichas de praças
    fichas_pracas = FichaConceitoPracas.objects.all()
    print(f"Total de fichas de praças: {fichas_pracas.count()}")
    
    for ficha in fichas_pracas:
        militar = ficha.militar
        print(f"\n--- Ficha ID: {ficha.pk} ---")
        print(f"Militar: {militar.nome_completo}")
        print(f"Posto/Graduação: {militar.posto_graduacao}")
        print(f"Display do Posto: {militar.get_posto_graduacao_display()}")
        print(f"É oficial? {militar.is_oficial()}")
        print(f"Tempo no posto: {ficha.tempo_posto}")
        print(f"Data de registro: {ficha.data_registro}")
        
        # Verificar se há fichas de oficiais para este militar
        fichas_oficiais = militar.fichaconceitooficiais_set.all()
        if fichas_oficiais.exists():
            print(f"ATENÇÃO: Este militar também possui {fichas_oficiais.count()} ficha(s) de oficiais!")
            for ficha_oficial in fichas_oficiais:
                print(f"  - Ficha oficial ID: {ficha_oficial.pk}")

def test_militares_pracas():
    """Testa os militares praças e verifica se estão corretos"""
    print("\n=== TESTE DE MILITARES PRACAS ===")
    
    # Buscar praças
    pracas = Militar.objects.filter(
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    
    print(f"Total de praças encontradas: {pracas.count()}")
    
    for militar in pracas:
        print(f"\n--- {militar.nome_completo} ---")
        print(f"Posto: {militar.posto_graduacao}")
        print(f"Display: {militar.get_posto_graduacao_display()}")
        print(f"É oficial? {militar.is_oficial()}")
        
        # Verificar fichas
        fichas_pracas = militar.fichaconceitopracas_set.all()
        fichas_oficiais = militar.fichaconceitooficiais_set.all()
        
        print(f"Fichas de praças: {fichas_pracas.count()}")
        print(f"Fichas de oficiais: {fichas_oficiais.count()}")

if __name__ == "__main__":
    test_fichas_pracas()
    test_militares_pracas() 