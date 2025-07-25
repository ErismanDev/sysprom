#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroFixacaoVagas, AssinaturaQuadroFixacaoVagas

def verificar_assinaturas():
    """Verifica as assinaturas do quadro de fixação de vagas"""
    
    # Buscar o quadro específico (ID 30)
    try:
        quadro = QuadroFixacaoVagas.objects.get(pk=30)
        print(f"Quadro encontrado: {quadro.titulo}")
        print(f"Tipo: {quadro.get_tipo_display()}")
        print(f"Status: {quadro.get_status_display()}")
        print()
        
        # Verificar todas as assinaturas
        assinaturas = quadro.assinaturas.all()
        print(f"Total de assinaturas: {assinaturas.count()}")
        
        for i, assinatura in enumerate(assinaturas, 1):
            print(f"\nAssinatura {i}:")
            print(f"  Assinado por: {assinatura.assinado_por.get_full_name()}")
            print(f"  Tipo: {assinatura.get_tipo_assinatura_display()}")
            print(f"  Função: {assinatura.funcao_assinatura or 'Não registrada'}")
            print(f"  Data: {assinatura.data_assinatura}")
            print(f"  Observações: {assinatura.observacoes or 'Nenhuma'}")
        
        # Verificar assinaturas eletrônicas especificamente
        assinaturas_eletronicas = quadro.assinaturas.filter(tipo_assinatura='ELETRONICA')
        print(f"\nAssinaturas eletrônicas: {assinaturas_eletronicas.count()}")
        
        for i, assinatura in enumerate(assinaturas_eletronicas, 1):
            print(f"\nAssinatura Eletrônica {i}:")
            print(f"  Assinado por: {assinatura.assinado_por.get_full_name()}")
            print(f"  Função: {assinatura.funcao_assinatura or 'Não registrada'}")
            print(f"  Data: {assinatura.data_assinatura}")
        
    except QuadroFixacaoVagas.DoesNotExist:
        print("Quadro com ID 30 não encontrado!")
        
        # Listar todos os quadros disponíveis
        quadros = QuadroFixacaoVagas.objects.all()
        print(f"\nQuadros disponíveis ({quadros.count()}):")
        for quadro in quadros:
            print(f"  ID: {quadro.pk} - {quadro.titulo} ({quadro.get_tipo_display()})")

if __name__ == '__main__':
    verificar_assinaturas() 