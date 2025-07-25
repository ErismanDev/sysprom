#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso

def verificar_quadro_367():
    """Verifica o tipo real do quadro 367"""
    
    try:
        quadro = QuadroAcesso.objects.get(pk=367)
        print(f"=== Quadro 367 ===")
        print(f"ID: {quadro.pk}")
        print(f"Tipo: {quadro.tipo}")
        print(f"Tipo Display: {quadro.get_tipo_display()}")
        print(f"Categoria: {quadro.categoria}")
        print(f"Data: {quadro.data_promocao}")
        print(f"Total de militares: {quadro.itemquadroacesso_set.count()}")
        
        # Verificar se é realmente merecimento
        if quadro.tipo == 'MERECIMENTO':
            print("✅ O quadro É do tipo MERECIMENTO")
        else:
            print(f"❌ O quadro NÃO é do tipo MERECIMENTO, é: {quadro.tipo}")
            
    except QuadroAcesso.DoesNotExist:
        print("❌ Quadro 367 não encontrado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_quadro_367() 