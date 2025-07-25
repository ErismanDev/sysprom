#!/usr/bin/env python
"""
Script para testar se a assinatura está funcionando corretamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import AssinaturaQuadroAcesso, UsuarioFuncao, MembroComissao
from django.contrib.auth.models import User

def testar_assinatura_nova():
    """Testa se a assinatura está funcionando corretamente"""
    print("🧪 TESTANDO ASSINATURA NOVA")
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
    
    # Verificar função na comissão
    membro_comissao = MembroComissao.objects.filter(
        usuario=usuario,
        ativo=True
    ).first()
    
    if membro_comissao:
        print(f"✅ Membro de comissão: {membro_comissao.get_tipo_display()} - {membro_comissao.cargo.nome}")
        funcao_esperada = f"{membro_comissao.get_tipo_display()} - {membro_comissao.cargo.nome}"
    else:
        print(f"❌ Não é membro de comissão ativo")
        funcao_esperada = "Usuário do Sistema"
    
    # Verificar funções do usuário
    funcoes_usuario = UsuarioFuncao.objects.filter(
        usuario=usuario,
        status='ATIVO'
    )
    
    print(f"📋 Funções ativas do usuário: {funcoes_usuario.count()}")
    for funcao in funcoes_usuario:
        print(f"   - {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
    
    # Verificar assinaturas mais recentes
    assinaturas_recentes = AssinaturaQuadroAcesso.objects.filter(
        assinado_por=usuario
    ).order_by('-data_assinatura')[:3]
    
    print(f"\n📝 Últimas 3 assinaturas:")
    for i, assinatura in enumerate(assinaturas_recentes, 1):
        print(f"   {i}. {assinatura.quadro_acesso} - {assinatura.get_tipo_assinatura_display()}")
        print(f"      Data: {assinatura.data_assinatura}")
        print(f"      Função salva: '{assinatura.funcao_assinatura}'")
        
        if assinatura.funcao_assinatura == "Função não registrada":
            print(f"      ❌ PROBLEMA: Função não registrada!")
        elif assinatura.funcao_assinatura:
            print(f"      ✅ OK: Função registrada corretamente")
        else:
            print(f"      ⚠️  ATENÇÃO: Função vazia")
    
    print(f"\n🎯 Função esperada: '{funcao_esperada}'")
    
    # Simular criação de assinatura
    print(f"\n🔧 SIMULANDO CRIAÇÃO DE ASSINATURA:")
    
    if membro_comissao and membro_comissao.cargo:
        funcao_simulada = f"{membro_comissao.get_tipo_display()} - {membro_comissao.cargo.nome}"
    elif membro_comissao:
        funcao_simulada = membro_comissao.get_tipo_display()
    else:
        funcao_usuario = UsuarioFuncao.objects.filter(
            usuario=usuario,
            status='ATIVO'
        ).first()
        
        if funcao_usuario:
            funcao_simulada = funcao_usuario.cargo_funcao.nome
        else:
            funcao_simulada = "Usuário do Sistema"
    
    print(f"   Função que seria salva: '{funcao_simulada}'")
    
    if funcao_simulada == "Usuário do Sistema":
        print(f"   ⚠️  ATENÇÃO: Seria salva função padrão")
    else:
        print(f"   ✅ OK: Função específica seria salva")

if __name__ == "__main__":
    testar_assinatura_nova() 