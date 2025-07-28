#!/usr/bin/env python
"""
Script para vincular o usuário correto ao militar José ERISMAN de Sousa
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def corrigir_vinculo_militar():
    """Corrige o vínculo do militar José ERISMAN de Sousa"""
    
    print("🔧 CORRIGINDO VÍNCULO DO MILITAR JOSÉ ERISMAN DE SOUSA")
    print("=" * 60)
    
    # 1. Buscar militar José ERISMAN de Sousa
    try:
        militar_erisman = Militar.objects.get(nome_completo__icontains='ERISMAN')
        print(f"✅ Militar encontrado: {militar_erisman.nome_completo} (ID: {militar_erisman.pk})")
        print(f"   CPF: {militar_erisman.cpf}")
        print(f"   Matrícula: {militar_erisman.matricula}")
    except Militar.DoesNotExist:
        print("❌ Militar com nome 'ERISMAN' não encontrado")
        return
    
    # 2. Buscar usuário 49008382334
    try:
        user_correto = User.objects.get(username='49008382334')
        print(f"✅ Usuário encontrado: {user_correto.username}")
    except User.DoesNotExist:
        print("❌ Usuário '49008382334' não encontrado")
        return
    
    # 3. Verificar se o militar já tem usuário associado
    if hasattr(militar_erisman, 'user') and militar_erisman.user:
        print(f"⚠️ Militar já tem usuário associado: {militar_erisman.user.username}")
        if militar_erisman.user != user_correto:
            print(f"   Removendo associação anterior...")
            militar_erisman.user = None
            militar_erisman.save()
    
    # 4. Associar o militar ao usuário correto
    print(f"🔗 Associando militar {militar_erisman.nome_completo} ao usuário {user_correto.username}...")
    militar_erisman.user = user_correto
    militar_erisman.save()
    
    # 5. Verificar se a associação foi feita
    try:
        militar_associado = user_correto.militar
        print(f"✅ Associação realizada com sucesso!")
        print(f"   Usuário: {user_correto.username}")
        print(f"   Militar: {militar_associado.nome_completo}")
        print(f"   Posto: {militar_associado.get_posto_graduacao_display()}")
        print(f"   Matrícula: {militar_associado.matricula}")
    except Militar.DoesNotExist:
        print("❌ Erro na associação")
        return
    
    # 6. Verificar se o usuário erisman ainda tem militar associado
    try:
        user_erisman = User.objects.get(username='erisman')
        try:
            militar_erisman_old = user_erisman.militar
            print(f"⚠️ Usuário 'erisman' ainda tem militar associado: {militar_erisman_old.nome_completo}")
            print(f"   Removendo associação...")
            militar_erisman_old.user = None
            militar_erisman_old.save()
            print(f"   ✅ Associação removida")
        except Militar.DoesNotExist:
            print(f"✅ Usuário 'erisman' não tem mais militar associado")
    except User.DoesNotExist:
        print(f"✅ Usuário 'erisman' não existe")
    
    # 7. Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    print(f"   ✅ Militar José ERISMAN de Sousa associado ao usuário 49008382334")
    print(f"   ✅ Usuário erisman não tem mais militar associado")
    print(f"\n   📋 Para testar:")
    print(f"      1. Faça login com o usuário 49008382334")
    print(f"      2. Acesse: http://127.0.0.1:8000/militares/")
    print(f"      3. Clique em 'Minha Ficha de Cadastro'")
    print(f"      4. Deve mostrar a ficha do Major José ERISMAN de Sousa")

if __name__ == "__main__":
    corrigir_vinculo_militar() 