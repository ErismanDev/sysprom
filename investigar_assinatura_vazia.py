#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, AssinaturaQuadroAcesso
from django.contrib.auth.models import User

def investigar_assinatura_vazia():
    print("=== INVESTIGAÇÃO: ASSINATURA VAZIA ===\n")
    
    # Buscar o quadro de acesso 142
    try:
        quadro = QuadroAcesso.objects.get(pk=142)
        print(f"📋 Quadro encontrado: {quadro}")
        print(f"   Tipo: {quadro.get_tipo_display()}")
        print(f"   Status: {quadro.get_status_display()}")
        print(f"   Data: {quadro.data_promocao}")
    except QuadroAcesso.DoesNotExist:
        print("❌ Quadro 142 não encontrado!")
        return
    
    # Verificar assinaturas
    assinaturas = quadro.assinaturas.all()
    print(f"\n📝 Assinaturas encontradas: {assinaturas.count()}")
    
    if assinaturas.exists():
        print("\nDetalhes das assinaturas:")
        for i, assinatura in enumerate(assinaturas, 1):
            print(f"   {i}. {assinatura.assinado_por.get_full_name()} - {assinatura.get_tipo_assinatura_display()}")
            print(f"      Data: {assinatura.data_assinatura}")
            print(f"      Observações: {assinatura.observacoes or 'Nenhuma'}")
    else:
        print("   Nenhuma assinatura encontrada")
    
    # Verificar se há usuários no sistema
    usuarios = User.objects.all()
    print(f"\n👥 Usuários no sistema: {usuarios.count()}")
    
    if usuarios.exists():
        print("Primeiros 5 usuários:")
        for i, user in enumerate(usuarios[:5], 1):
            print(f"   {i}. {user.get_full_name()} ({user.username})")
    
    # Verificar se há assinaturas órfãs (sem usuário)
    assinaturas_orfas = AssinaturaQuadroAcesso.objects.filter(assinado_por__isnull=True)
    print(f"\n🔍 Assinaturas órfãs (sem usuário): {assinaturas_orfas.count()}")
    
    if assinaturas_orfas.exists():
        print("Assinaturas órfãs encontradas:")
        for assinatura in assinaturas_orfas:
            print(f"   - ID: {assinatura.pk}, Quadro: {assinatura.quadro_acesso.pk}")
    
    # Verificar se há assinaturas com usuário mas sem nome
    assinaturas_sem_nome = AssinaturaQuadroAcesso.objects.filter(
        assinado_por__first_name='',
        assinado_por__last_name=''
    )
    print(f"\n🔍 Assinaturas com usuário sem nome: {assinaturas_sem_nome.count()}")
    
    if assinaturas_sem_nome.exists():
        print("Assinaturas com usuário sem nome:")
        for assinatura in assinaturas_sem_nome:
            print(f"   - ID: {assinatura.pk}, Usuário: {assinatura.assinado_por.username}")

if __name__ == '__main__':
    investigar_assinatura_vazia() 