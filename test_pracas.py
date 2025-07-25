#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoPracas, FichaConceitoOficiais
from django.db.models import Q

def test_pracas():
    """Testa as praças e suas fichas de conceito"""
    print("=== TESTE DE PRACAS ===")
    
    # Buscar todas as praças
    pracas = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    )
    
    print(f"Total de praças encontradas: {pracas.count()}")
    
    for militar in pracas:
        print(f"\n--- {militar.nome_completo} ---")
        print(f"Posto: {militar.posto_graduacao}")
        print(f"É oficial? {militar.is_oficial()}")
        print(f"Tempo no posto: {militar.tempo_posto_atual()}")
        
        # Verificar fichas existentes
        ficha_oficiais = militar.fichaconceitooficiais_set.first()
        ficha_pracas = militar.fichaconceitopracas_set.first()
        
        if ficha_oficiais:
            print(f"FICHA DE OFICIAIS ENCONTRADA! - Tempo: {ficha_oficiais.tempo_posto}")
        if ficha_pracas:
            print(f"FICHA DE PRACAS ENCONTRADA! - Tempo: {ficha_pracas.tempo_posto}")
        
        if not ficha_oficiais and not ficha_pracas:
            print("NENHUMA FICHA ENCONTRADA")
    
    print("\n=== TESTE DE GERAÇÃO DE FICHAS ===")
    
    # Buscar praças sem ficha
    pracas_sem_ficha = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
    ).exclude(
        Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
    )
    
    print(f"Praças sem ficha: {pracas_sem_ficha.count()}")
    
    for militar in pracas_sem_ficha:
        print(f"\nCriando ficha para: {militar.nome_completo} ({militar.posto_graduacao})")
        
        # Verificar se é realmente uma praça
        if militar.is_oficial():
            print(f"ERRO: {militar.nome_completo} é oficial mas está sendo processado como praça!")
            continue
        
        try:
            ficha = FichaConceitoPracas.objects.create(militar=militar)
            print(f"Ficha criada com sucesso! Tempo no posto: {ficha.tempo_posto}")
        except Exception as e:
            print(f"Erro ao criar ficha: {e}")

if __name__ == '__main__':
    test_pracas() 