#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import *

def verificar_modelos_postgresql():
    print("=== VERIFICANDO MODELOS NO POSTGRESQL ===\n")
    
    try:
        # Verificar modelo SessaoComissao
        print("=== MODELO SessaoComissao ===")
        campos_sessao = SessaoComissao._meta.get_fields()
        for campo in campos_sessao:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar modelo VotoDeliberacao
        print(f"\n=== MODELO VotoDeliberacao ===")
        campos_voto = VotoDeliberacao._meta.get_fields()
        for campo in campos_voto:
            print(f"   • {campo.name}: {campo.__class__.__name__}")
        
        # Verificar se existem sessões
        print(f"\n=== SESSÕES EXISTENTES ===")
        sessoes = SessaoComissao.objects.all()
        print(f"Total de sessões: {sessoes.count()}")
        for sessao in sessoes:
            print(f"   • ID: {sessao.id}, Número: {sessao.numero}, Tipo: {sessao.tipo}")
        
        # Verificar se existem votos
        print(f"\n=== VOTOS EXISTENTES ===")
        votos = VotoDeliberacao.objects.all()
        print(f"Total de votos: {votos.count()}")
        for voto in votos:
            print(f"   • ID: {voto.id}, Voto: {voto.voto}, Membro: {voto.membro_id}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_modelos_postgresql() 