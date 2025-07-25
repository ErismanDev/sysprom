#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoOficiais, FichaConceitoPracas, Documento
from django.urls import reverse
from django.test import Client

def testar_upload_documento():
    """Testa se o upload de documentos está funcionando"""
    
    print("=== TESTE DE UPLOAD DE DOCUMENTOS ===\n")
    
    # Buscar um militar com ficha de conceito
    militar_com_ficha = None
    
    # Tentar encontrar um militar com ficha de oficiais
    ficha_oficiais = FichaConceitoOficiais.objects.first()
    if ficha_oficiais:
        militar_com_ficha = ficha_oficiais.militar
        tipo_ficha = "oficiais"
        ficha_id = ficha_oficiais.id
    else:
        # Tentar encontrar um militar com ficha de praças
        ficha_pracas = FichaConceitoPracas.objects.first()
        if ficha_pracas:
            militar_com_ficha = ficha_pracas.militar
            tipo_ficha = "praças"
            ficha_id = ficha_pracas.id
        else:
            print("❌ Nenhuma ficha de conceito encontrada!")
            return
    
    print(f"Militar: {militar_com_ficha.nome_completo}")
    print(f"Posto: {militar_com_ficha.get_posto_graduacao_display()}")
    print(f"Ficha de conceito: {tipo_ficha} (ID: {ficha_id})")
    
    # Verificar documentos existentes
    if tipo_ficha == "oficiais":
        documentos = Documento.objects.filter(ficha_conceito_oficiais_id=ficha_id)
    else:
        documentos = Documento.objects.filter(ficha_conceito_pracas_id=ficha_id)
    
    print(f"Documentos existentes: {documentos.count()}")
    
    # Testar acesso à URL de upload
    client = Client()
    try:
        url = f'/militares/ficha-conceito/{ficha_id}/documento/'
        response = client.get(url)
        print(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de upload carregada com sucesso!")
        else:
            print(f"❌ Erro ao carregar página: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao acessar URL: {e}")
    
    # Verificar se há problemas com o modelo Documento
    print("\n=== VERIFICAÇÃO DO MODELO DOCUMENTO ===")
    
    # Verificar campos do modelo
    campos_documento = [field.name for field in Documento._meta.fields]
    print(f"Campos do modelo Documento: {campos_documento}")
    
    # Verificar se os campos de ficha estão presentes
    campos_ficha = [field for field in campos_documento if 'ficha_conceito' in field]
    print(f"Campos de ficha de conceito: {campos_ficha}")
    
    # Verificar relacionamentos
    print("\n=== VERIFICAÇÃO DE RELACIONAMENTOS ===")
    
    # Testar relacionamento inverso
    if tipo_ficha == "oficiais":
        ficha = FichaConceitoOficiais.objects.get(id=ficha_id)
        documentos_relacionados = Documento.objects.filter(ficha_conceito_oficiais=ficha)
    else:
        ficha = FichaConceitoPracas.objects.get(id=ficha_id)
        documentos_relacionados = Documento.objects.filter(ficha_conceito_pracas=ficha)
    
    print(f"Documentos relacionados via filtro: {documentos_relacionados.count()}")
    
    print("\n✅ Teste concluído!")

if __name__ == '__main__':
    testar_upload_documento() 