#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import *

def verificar_modelos_quadros_vagas():
    print("=== VERIFICANDO MODELOS DE QUADROS E VAGAS NO POSTGRESQL ===\n")
    
    try:
        # Verificar modelo QuadroAcesso
        print("=== MODELO QuadroAcesso ===")
        campos_quadro = QuadroAcesso._meta.get_fields()
        for campo in campos_quadro:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar modelo Vaga
        print(f"\n=== MODELO Vaga ===")
        campos_vaga = Vaga._meta.get_fields()
        for campo in campos_vaga:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar modelo QuadroFixacaoVagas
        print(f"\n=== MODELO QuadroFixacaoVagas ===")
        campos_quadro_fixacao = QuadroFixacaoVagas._meta.get_fields()
        for campo in campos_quadro_fixacao:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar se existem quadros de acesso
        print(f"\n=== QUADROS DE ACESSO EXISTENTES ===")
        quadros = QuadroAcesso.objects.all()
        print(f"Total de quadros de acesso: {quadros.count()}")
        for quadro in quadros:
            print(f"   • ID: {quadro.id}, Tipo: {quadro.tipo}, Categoria: {quadro.categoria}")
        
        # Verificar se existem vagas
        print(f"\n=== VAGAS EXISTENTES ===")
        vagas = Vaga.objects.all()
        print(f"Total de vagas: {vagas.count()}")
        for vaga in vagas:
            print(f"   • ID: {vaga.id}, Quadro: {vaga.quadro}, Posto: {vaga.posto}")
        
        # Verificar se existem quadros de fixação
        print(f"\n=== QUADROS DE FIXAÇÃO EXISTENTES ===")
        quadros_fixacao = QuadroFixacaoVagas.objects.all()
        print(f"Total de quadros de fixação: {quadros_fixacao.count()}")
        for quadro in quadros_fixacao:
            print(f"   • ID: {quadro.id}, Título: {quadro.titulo}, Tipo: {quadro.tipo}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_modelos_quadros_vagas() 