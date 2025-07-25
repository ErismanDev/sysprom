#!/usr/bin/env python
import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.views import quadro_acesso_pdf
from militares.models import QuadroAcesso

def testar_funcao_pdf():
    """Testa diretamente a função quadro_acesso_pdf"""
    
    try:
        # Criar um request fake
        factory = RequestFactory()
        request = factory.get('/militares/quadros-acesso/367/pdf/')
        
        # Criar um usuário fake para login
        user = User.objects.create_user(username='test', password='test')
        request.user = user
        
        # Chamar a função diretamente
        print("=== Testando função quadro_acesso_pdf ===")
        response = quadro_acesso_pdf(request, 367)
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Tipo da resposta: {type(response)}")
        
        if hasattr(response, 'content'):
            print(f"Tamanho do conteúdo: {len(response.content)} bytes")
            
            # Verificar se contém a string "DEBUG"
            if b'DEBUG' in response.content:
                print("✅ String 'DEBUG' encontrada no PDF!")
            else:
                print("❌ String 'DEBUG' NÃO encontrada no PDF")
                
            # Verificar se contém a string "PONTUAÇÃO"
            if b'PONTUA\xc3\x87\xc3\x83O' in response.content or b'PONTUACAO' in response.content:
                print("✅ String 'PONTUAÇÃO' encontrada no PDF!")
            else:
                print("❌ String 'PONTUAÇÃO' NÃO encontrada no PDF")
        
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_funcao_pdf() 