#!/usr/bin/env python
"""
Script para verificar especificamente a assinatura do Tenente Coronel José ERISMAN de Sousa
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import AssinaturaQuadroAcesso, UsuarioFuncao, MembroComissao
from django.contrib.auth.models import User

def verificar_assinatura_erisman():
    """Verifica especificamente a assinatura do Tenente Coronel José ERISMAN de Sousa"""
    print("🔍 VERIFICANDO ASSINATURA DO TENENTE CORONEL ERISMAN")
    print("=" * 60)
    
    # Buscar o usuário erisman
    try:
        usuario = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {usuario.get_full_name()} ({usuario.username})")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado!")
        return
    
    # Verificar se é militar
    if hasattr(usuario, 'militar') and usuario.militar:
        militar = usuario.militar
        print(f"✅ Militar associado: {militar.nome_completo} - {militar.get_posto_graduacao_display()}")
    else:
        print("❌ Usuário não tem militar associado!")
        return
    
    # Verificar assinaturas do usuário
    assinaturas = AssinaturaQuadroAcesso.objects.filter(
        assinado_por=usuario
    ).select_related('quadro_acesso')
    
    print(f"\n📝 Assinaturas encontradas: {assinaturas.count()}")
    
    for i, assinatura in enumerate(assinaturas, 1):
        print(f"\n--- Assinatura {i} ---")
        print(f"   Quadro: {assinatura.quadro_acesso}")
        print(f"   Tipo: {assinatura.get_tipo_assinatura_display()}")
        print(f"   Data: {assinatura.data_assinatura}")
        print(f"   Função salva: '{assinatura.funcao_assinatura}'")
        
        # Verificar função na comissão
        membro_comissao = MembroComissao.objects.filter(
            usuario=usuario,
            ativo=True
        ).first()
        
        if membro_comissao:
            print(f"   ✅ Membro de comissão: {membro_comissao.get_tipo_display()} - {membro_comissao.cargo.nome}")
        else:
            print(f"   ❌ Não é membro de comissão ativo")
        
        # Verificar funções do usuário
        funcoes_usuario = UsuarioFuncao.objects.filter(
            usuario=usuario,
            status='ATIVO'
        )
        
        print(f"   📋 Funções ativas do usuário: {funcoes_usuario.count()}")
        for funcao in funcoes_usuario:
            print(f"      - {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
    
    # Verificar se há assinaturas sem função
    assinaturas_sem_funcao = assinaturas.filter(funcao_assinatura__isnull=True)
    print(f"\n⚠️  Assinaturas sem função: {assinaturas_sem_funcao.count()}")
    
    if assinaturas_sem_funcao.exists():
        print("   Assinaturas que precisam ser atualizadas:")
        for assinatura in assinaturas_sem_funcao:
            print(f"      - {assinatura.quadro_acesso} ({assinatura.data_assinatura})")

if __name__ == "__main__":
    verificar_assinatura_erisman() 