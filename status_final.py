#!/usr/bin/env python
"""
Script para verificar o status final do sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def verificar_status_final():
    """
    Verifica o status final do sistema
    """
    print("=== STATUS FINAL APÓS CORREÇÃO ===")
    
    # Usuários
    total_usuarios = User.objects.count()
    usuarios_com_email = User.objects.exclude(email='').count()
    emails_unicos = User.objects.exclude(email='').values('email').distinct().count()
    
    print(f"Usuários: {total_usuarios}")
    print(f"Usuários com email: {usuarios_com_email}")
    print(f"Emails únicos: {emails_unicos}")
    print(f"Emails duplicados: {usuarios_com_email - emails_unicos}")
    
    # Militares
    total_militares = Militar.objects.count()
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    
    print(f"\nMilitares: {total_militares}")
    print(f"Militares com usuário: {militares_com_usuario}")
    print(f"Militares sem usuário: {total_militares - militares_com_usuario}")
    
    # Verificar se ainda há duplicados
    if usuarios_com_email - emails_unicos == 0:
        print("\n✅ SISTEMA LIMPO - Nenhum email duplicado encontrado!")
    else:
        print(f"\n⚠️  Ainda há {usuarios_com_email - emails_unicos} emails duplicados")
    
    print("\n=== SISTEMA PRONTO PARA USO! ===")

if __name__ == "__main__":
    verificar_status_final() 