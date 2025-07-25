#!/usr/bin/env python
"""
Script para associar automaticamente o usuário erisman ao militar correto usando o campo 'user' do modelo Militar
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.contrib.auth.models import User

def associar_erisman_militar():
    print("🔗 ASSOCIANDO USUÁRIO ERISMAN AO MILITAR (campo 'user')")
    print("=" * 60)
    try:
        usuario = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {usuario.get_full_name()} ({usuario.username})")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado!")
        return
    try:
        militar = Militar.objects.get(nome_completo__icontains='ERISMAN')
        print(f"✅ Militar encontrado: {militar.nome_completo} - {militar.get_posto_graduacao_display()}")
    except Militar.DoesNotExist:
        print("❌ Militar ERISMAN não encontrado!")
        return
    # Associar o usuário ao militar
    militar.user = usuario
    militar.save()
    print(f"✅ Usuário {usuario.username} associado ao militar {militar.nome_completo} (campo 'user')")
    militar.refresh_from_db()
    if militar.user == usuario:
        print(f"✅ Associação confirmada!")
    else:
        print(f"❌ Erro na associação!")
if __name__ == "__main__":
    associar_erisman_militar() 