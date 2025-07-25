#!/usr/bin/env python
"""
Script para corrigir emails duplicados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Count

def corrigir_emails_duplicados():
    """
    Corrige emails duplicados
    """
    print("=== CORRIGINDO EMAILS DUPLICADOS ===")
    
    # Encontrar emails duplicados
    emails_duplicados = User.objects.exclude(email='').values('email').annotate(count=Count('id')).filter(count__gt=1)
    
    print(f"Emails duplicados encontrados: {emails_duplicados.count()}")
    
    emails_corrigidos = 0
    
    for dup in emails_duplicados:
        email = dup['email']
        count = dup['count']
        
        print(f"\nCorrigindo email: {email} ({count} registros)")
        
        # Pegar todos os usuários com este email
        users = User.objects.filter(email=email).order_by('id')
        
        # Manter o primeiro e limpar os outros
        primeiro = users.first()
        outros = users.exclude(id=primeiro.id)
        
        print(f"  Mantendo: {primeiro.username} - {primeiro.email}")
        
        for user in outros:
            print(f"  Limpando email de: {user.username}")
            user.email = ''  # Limpar o email
            user.save()
            emails_corrigidos += 1
    
    print(f"\nTotal de emails corrigidos: {emails_corrigidos}")
    
    # Verificar resultado
    emails_finais = User.objects.exclude(email='').values('email').distinct().count()
    print(f"Emails únicos após correção: {emails_finais}")

def verificar_emails_duplicados():
    """
    Verifica emails duplicados
    """
    print("=== VERIFICANDO EMAILS DUPLICADOS ===")
    
    emails_total = User.objects.exclude(email='').count()
    emails_unicos = User.objects.exclude(email='').values('email').distinct().count()
    emails_duplicados = User.objects.exclude(email='').values('email').annotate(count=Count('id')).filter(count__gt=1)
    
    print(f"Total de usuários com email: {emails_total}")
    print(f"Emails únicos: {emails_unicos}")
    print(f"Emails duplicados: {emails_total - emails_unicos}")
    
    if emails_duplicados:
        print("\nExemplos de emails duplicados:")
        for dup in emails_duplicados[:5]:
            email = dup['email']
            count = dup['count']
            print(f"  {email}: {count} registros")
            
            users = User.objects.filter(email=email)
            for user in users:
                print(f"    - {user.username} (ID: {user.id})")
    
    return emails_duplicados

if __name__ == "__main__":
    # Verificar emails duplicados
    duplicados = verificar_emails_duplicados()
    
    if duplicados:
        resposta = input("\nDeseja corrigir os emails duplicados? (s/n): ").lower()
        if resposta == 's':
            corrigir_emails_duplicados()
        else:
            print("Correção cancelada.")
    else:
        print("Nenhum email duplicado encontrado.") 