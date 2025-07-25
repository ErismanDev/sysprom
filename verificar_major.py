#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar

def verificar_major():
    try:
        quadro = QuadroAcesso.objects.get(id=366)
        print(f"Quadro encontrado: {quadro}")
        print(f"Tipo: {quadro.get_tipo_display()}")
        print(f"Status: {quadro.get_status_display()}")
        
        # Buscar Majores combatentes ativos
        majores = Militar.objects.filter(
            posto_graduacao='MJ',
            quadro='COMB',
            situacao='AT'
        )
        
        print(f"\nMajores combatentes encontrados: {majores.count()}")
        for major in majores:
            print(f"  - {major.nome_completo} ({major.matricula})")
        
        # Verificar quais Majores já estão no quadro
        majores_no_quadro = quadro.itemquadroacesso_set.filter(
            militar__posto_graduacao='MJ',
            militar__quadro='COMB'
        )
        
        print(f"\nMajores no quadro366: {majores_no_quadro.count()}")
        for item in majores_no_quadro:
            print(f" - {item.militar.nome_completo} (posição {item.posicao})")
        
        if majores_no_quadro.exists():
            print("\n✅ Majores estão no quadro!")
        else:
            print("\n❌ Majores NÃO estão no quadro!")
            
    except QuadroAcesso.DoesNotExist:
        print("❌ Quadro 366 não encontrado!")

if __name__ == '__main__':
    verificar_major() 