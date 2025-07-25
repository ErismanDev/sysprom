#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso

def criar_quadro_teste():
    """Cria um quadro manual de praças para teste"""
    print("=== CRIANDO QUADRO MANUAL DE PRAÇAS PARA TESTE ===")
    
    # Data de promoção para teste
    data_promocao = date(2025, 7, 18)
    
    # Verificar se já existe um quadro para esta data
    quadro_existente = QuadroAcesso.objects.filter(
        data_promocao=data_promocao,
        is_manual=True
    ).first()
    
    if quadro_existente:
        print(f"📋 Quadro já existe: {quadro_existente.pk}")
        return quadro_existente
    
    # Criar novo quadro manual
    novo_quadro = QuadroAcesso.objects.create(
        tipo='MANUAL',
        data_promocao=data_promocao,
        status='EM_ELABORACAO',
        is_manual=True,
        criterio_ordenacao_manual='ANTIGUIDADE',
        observacoes='Quadro manual de teste para praças'
    )
    
    print(f"✅ Quadro criado com sucesso!")
    print(f"   ID: {novo_quadro.pk}")
    print(f"   Data: {novo_quadro.data_promocao}")
    print(f"   Critério: {novo_quadro.criterio_ordenacao_manual}")
    
    return novo_quadro

if __name__ == '__main__':
    criar_quadro_teste() 