#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import PrevisaoVaga, QUADRO_CHOICES

def verificar_todos_quadros():
    print("=== VERIFICANDO PREVISÕES PARA TODOS OS QUADROS ===\n")
    
    for cod, nome in QUADRO_CHOICES:
        print(f"QUADRO: {cod} ({nome})")
        print("-" * 50)
        
        previsoes = PrevisaoVaga.objects.filter(
            quadro=cod,
            ativo=True
        ).order_by('posto')
        
        print(f"Total de previsões: {previsoes.count()}")
        
        if previsoes.count() > 0:
            for previsao in previsoes:
                print(f"  - {previsao.get_posto_display()}: {previsao.vagas_disponiveis} vagas")
        else:
            print("  ❌ Nenhuma previsão encontrada")
        
        print()
    
    # Verificar todas as previsões ativas
    print("TODAS AS PREVISÕES ATIVAS:")
    print("-" * 50)
    
    todas_previsoes = PrevisaoVaga.objects.filter(ativo=True).order_by('quadro', 'posto')
    
    for previsao in todas_previsoes:
        print(f"- {previsao.quadro} | {previsao.get_posto_display()}: {previsao.vagas_disponiveis} vagas")

if __name__ == '__main__':
    verificar_todos_quadros() 