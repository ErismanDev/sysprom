#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import ModeloAta, SessaoComissao, AtaSessao
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def testar_view_salvar_modelo():
    """Testa a view modelo_ata_salvar_atual"""
    print("=== TESTE DA VIEW SALVAR MODELO ===")
    
    # Configurar request factory
    factory = RequestFactory()
    
    # Obter sessão e usuário
    sessao = SessaoComissao.objects.get(pk=4)
    user = User.objects.first()
    
    print(f"Sessão: {sessao.numero}")
    print(f"Usuário: {user.username}")
    
    # Criar request POST simulado
    post_data = {
        'nome': 'Modelo de Teste',
        'descricao': 'Descrição do modelo de teste',
        'tipo_comissao': 'GERAL',
        'tipo_sessao': 'GERAL',
        'conteudo': '<p>Conteúdo de teste</p>',
        'csrfmiddlewaretoken': 'test_token'
    }
    
    request = factory.post(f'/militares/comissao/sessoes/{sessao.pk}/salvar-como-modelo/', post_data)
    request.user = user
    request.headers = {'X-Requested-With': 'XMLHttpRequest'}
    
    print("Request criado:")
    print(f"Method: {request.method}")
    print(f"User: {request.user}")
    print(f"Headers: {request.headers}")
    print(f"POST data: {request.POST}")
    
    # Importar e chamar a view
    from militares.views import modelo_ata_salvar_atual
    
    try:
        response = modelo_ata_salvar_atual(request, sessao.pk)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        if hasattr(response, 'content'):
            import json
            try:
                data = json.loads(response.content.decode())
                print(f"JSON response: {data}")
            except:
                print("Response não é JSON válido")
                
    except Exception as e:
        print(f"❌ Erro na view: {str(e)}")
        import traceback
        traceback.print_exc()

def testar_criacao_direta():
    """Testa criação direta de modelo"""
    print("\n=== TESTE DE CRIAÇÃO DIRETA ===")
    
    try:
        user = User.objects.first()
        
        modelo = ModeloAta.objects.create(
            nome="Teste Direto",
            descricao="Teste de criação direta",
            tipo_comissao="GERAL",
            tipo_sessao="GERAL",
            conteudo="<p>Conteúdo de teste direto</p>",
            criado_por=user,
            ativo=True,
            padrao=False
        )
        
        print(f"✅ Modelo criado: {modelo.nome} (ID: {modelo.pk})")
        
        # Limpar
        modelo.delete()
        print("✅ Modelo removido")
        
    except Exception as e:
        print(f"❌ Erro na criação direta: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_criacao_direta()
    testar_view_salvar_modelo() 