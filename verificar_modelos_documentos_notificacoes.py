#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import *

def verificar_modelos_documentos_notificacoes():
    print("=== VERIFICANDO MODELOS DE DOCUMENTOS E NOTIFICAÇÕES NO POSTGRESQL ===\n")
    
    try:
        # Verificar modelo Documento
        print("=== MODELO Documento ===")
        campos_documento = Documento._meta.get_fields()
        for campo in campos_documento:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar modelo NotificacaoSessao
        print(f"\n=== MODELO NotificacaoSessao ===")
        campos_notificacao = NotificacaoSessao._meta.get_fields()
        for campo in campos_notificacao:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar modelo DocumentoSessao
        print(f"\n=== MODELO DocumentoSessao ===")
        campos_documento_sessao = DocumentoSessao._meta.get_fields()
        for campo in campos_documento_sessao:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar se existem documentos
        print(f"\n=== DOCUMENTOS EXISTENTES ===")
        documentos = Documento.objects.all()
        print(f"Total de documentos: {documentos.count()}")
        for documento in documentos:
            print(f"   • ID: {documento.id}, Tipo: {documento.tipo}, Título: {documento.titulo[:50]}...")
        
        # Verificar se existem notificações
        print(f"\n=== NOTIFICAÇÕES EXISTENTES ===")
        notificacoes = NotificacaoSessao.objects.all()
        print(f"Total de notificações: {notificacoes.count()}")
        for notificacao in notificacoes:
            print(f"   • ID: {notificacao.id}, Tipo: {notificacao.tipo}, Título: {notificacao.titulo[:50]}...")
        
        # Verificar se existem documentos de sessão
        print(f"\n=== DOCUMENTOS DE SESSÃO EXISTENTES ===")
        documentos_sessao = DocumentoSessao.objects.all()
        print(f"Total de documentos de sessão: {documentos_sessao.count()}")
        for documento in documentos_sessao:
            print(f"   • ID: {documento.id}, Tipo: {documento.tipo}, Título: {documento.titulo[:50]}...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_modelos_documentos_notificacoes() 