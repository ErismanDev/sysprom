#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, AssinaturaQuadroAcesso
from django.contrib.auth.models import User

def testar_assinaturas_regeneracao():
    print("=== TESTE: ASSINATURAS DURANTE REGENERAÇÃO ===\n")
    
    # Buscar um quadro de acesso existente
    quadro = QuadroAcesso.objects.filter(status='ELABORADO').first()
    
    if not quadro:
        print("❌ Nenhum quadro elaborado encontrado!")
        return
    
    print(f"Quadro selecionado: {quadro.get_titulo_completo()}")
    print(f"ID: {quadro.id}")
    print(f"Status atual: {quadro.get_status_display()}")
    
    # Verificar assinaturas existentes
    assinaturas_antes = quadro.assinaturas.all()
    print(f"\nAssinaturas ANTES da regeneração: {assinaturas_antes.count()}")
    
    for assinatura in assinaturas_antes:
        print(f"  - {assinatura.assinado_por.get_full_name()} ({assinatura.get_tipo_assinatura_display()}) - {assinatura.data_assinatura}")
    
    # Se não há assinaturas, criar uma para teste
    if not assinaturas_antes.exists():
        print("\n--- CRIANDO ASSINATURA DE TESTE ---")
        user = User.objects.first()
        if user:
            assinatura_teste = AssinaturaQuadroAcesso.objects.create(
                quadro_acesso=quadro,
                assinado_por=user,
                tipo_assinatura='APROVACAO',
                observacoes='Assinatura de teste'
            )
            print(f"✅ Assinatura de teste criada: {assinatura_teste}")
            assinaturas_antes = quadro.assinaturas.all()
        else:
            print("❌ Nenhum usuário encontrado para criar assinatura de teste")
            return
    
    # Verificar itens do quadro
    itens_antes = quadro.itemquadroacesso_set.all()
    print(f"\nItens do quadro ANTES da regeneração: {itens_antes.count()}")
    
    # Regenerar o quadro
    print(f"\n--- REGENERANDO QUADRO ---")
    sucesso, mensagem = quadro.gerar_quadro_automatico()
    print(f"Resultado: {mensagem}")
    
    # Verificar assinaturas após regeneração
    quadro.refresh_from_db()
    assinaturas_depois = quadro.assinaturas.all()
    print(f"\nAssinaturas DEPOIS da regeneração: {assinaturas_depois.count()}")
    
    for assinatura in assinaturas_depois:
        print(f"  - {assinatura.assinado_por.get_full_name()} ({assinatura.get_tipo_assinatura_display()}) - {assinatura.data_assinatura}")
    
    # Verificar itens do quadro após regeneração
    itens_depois = quadro.itemquadroacesso_set.all()
    print(f"\nItens do quadro DEPOIS da regeneração: {itens_depois.count()}")
    
    # Comparar
    if assinaturas_antes.count() == assinaturas_depois.count():
        print(f"\n✅ SUCESSO: Assinaturas mantidas ({assinaturas_antes.count()} → {assinaturas_depois.count()})")
    else:
        print(f"\n❌ PROBLEMA: Assinaturas perdidas ({assinaturas_antes.count()} → {assinaturas_depois.count()})")
    
    if itens_antes.count() != itens_depois.count():
        print(f"ℹ️  Itens do quadro alterados ({itens_antes.count()} → {itens_depois.count()})")
    else:
        print(f"ℹ️  Itens do quadro mantidos ({itens_antes.count()} → {itens_depois.count()})")

if __name__ == "__main__":
    testar_assinaturas_regeneracao() 