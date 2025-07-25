#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, ItemQuadroAcesso
from django.contrib.auth.models import User
from django.test import RequestFactory
from militares.views_pracas import delete_quadro_acesso_pracas

def testar_delete_quadro_pracas():
    print("=== TESTANDO FUNCIONALIDADE DE DELETE DE QUADROS DE PRACAS ===\n")
    
    # 1. Verificar quadros existentes
    print("1. QUADROS EXISTENTES:")
    print("-" * 50)
    
    quadros = QuadroAcesso.objects.all().order_by('-data_promocao')
    print(f"Total de quadros: {quadros.count()}")
    
    for quadro in quadros[:5]:  # Mostrar apenas os 5 mais recentes
        itens_count = quadro.itemquadroacesso_set.count()
        itens_pracas = quadro.itemquadroacesso_set.filter(
            militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
        )
        print(f"  Quadro {quadro.pk}: {quadro.get_tipo_display()} - {quadro.data_promocao} - Status: {quadro.status}")
        print(f"    Total de itens: {itens_count}")
        print(f"    Itens de praças: {itens_pracas.count()}")
    
    # 2. Criar um quadro de teste para deletar
    print(f"\n2. CRIANDO QUADRO DE TESTE:")
    print("-" * 50)
    
    # Criar um usuário de teste
    user, created = User.objects.get_or_create(
        username='teste_delete',
        defaults={'email': 'teste@teste.com'}
    )
    
    # Criar um quadro de teste
    from datetime import date, timedelta
    data_teste = date.today() + timedelta(days=60)
    
    quadro_teste = QuadroAcesso.objects.create(
        tipo='MERECIMENTO',
        data_promocao=data_teste,
        status='EM_ELABORACAO'
    )
    
    print(f"Quadro de teste criado: {quadro_teste.pk}")
    print(f"Tipo: {quadro_teste.tipo}")
    print(f"Data: {quadro_teste.data_promocao}")
    print(f"Status: {quadro_teste.status}")
    
    # 3. Testar a view de delete
    print(f"\n3. TESTANDO VIEW DE DELETE:")
    print("-" * 50)
    
    factory = RequestFactory()
    
    # Testar GET (página de confirmação)
    request = factory.get(f'/militares/pracas/quadros-acesso/{quadro_teste.pk}/excluir/')
    request.user = user
    
    try:
        response = delete_quadro_acesso_pracas(request, pk=quadro_teste.pk)
        print(f"GET Response Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Página de confirmação carregada com sucesso")
        else:
            print(f"❌ Erro ao carregar página de confirmação: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no GET: {str(e)}")
    
    # Testar POST (exclusão)
    request = factory.post(f'/militares/pracas/quadros-acesso/{quadro_teste.pk}/excluir/')
    request.user = user
    
    try:
        response = delete_quadro_acesso_pracas(request, pk=quadro_teste.pk)
        print(f"POST Response Status: {response.status_code}")
        if response.status_code == 302:  # Redirect
            print("✅ Quadro excluído com sucesso (redirect)")
        else:
            print(f"❌ Erro ao excluir quadro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no POST: {str(e)}")
    
    # 4. Verificar se o quadro foi realmente excluído
    print(f"\n4. VERIFICANDO EXCLUSÃO:")
    print("-" * 50)
    
    try:
        quadro_verificacao = QuadroAcesso.objects.get(pk=quadro_teste.pk)
        print(f"❌ Quadro ainda existe: {quadro_verificacao.pk}")
    except QuadroAcesso.DoesNotExist:
        print("✅ Quadro foi excluído com sucesso")
    
    # 5. Testar com quadro sem praças
    print(f"\n5. TESTANDO COM QUADRO SEM PRACAS:")
    print("-" * 50)
    
    # Criar outro quadro de teste (sem praças)
    quadro_sem_pracas = QuadroAcesso.objects.create(
        tipo='ANTIGUIDADE',
        data_promocao=data_teste + timedelta(days=1),
        status='EM_ELABORACAO'
    )
    
    print(f"Quadro sem praças criado: {quadro_sem_pracas.pk}")
    
    # Testar delete do quadro sem praças
    request = factory.post(f'/militares/pracas/quadros-acesso/{quadro_sem_pracas.pk}/excluir/')
    request.user = user
    
    try:
        response = delete_quadro_acesso_pracas(request, pk=quadro_sem_pracas.pk)
        print(f"POST Response Status: {response.status_code}")
        if response.status_code == 302:  # Redirect
            print("✅ Quadro sem praças excluído com sucesso")
        else:
            print(f"❌ Erro ao excluir quadro sem praças: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no POST (quadro sem praças): {str(e)}")
    
    # Verificar se foi excluído
    try:
        quadro_verificacao = QuadroAcesso.objects.get(pk=quadro_sem_pracas.pk)
        print(f"❌ Quadro sem praças ainda existe: {quadro_verificacao.pk}")
    except QuadroAcesso.DoesNotExist:
        print("✅ Quadro sem praças foi excluído com sucesso")
    
    print(f"\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    testar_delete_quadro_pracas() 