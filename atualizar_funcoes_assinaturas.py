#!/usr/bin/env python
"""
Script para atualizar as funções das assinaturas existentes que estão vazias
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import AssinaturaQuadroAcesso, UsuarioFuncao, MembroComissao
from django.contrib.auth.models import User

def atualizar_funcoes_assinaturas():
    """Atualiza as funções das assinaturas que estão vazias"""
    print("🔄 ATUALIZANDO FUNÇÕES DAS ASSINATURAS")
    print("=" * 60)
    
    # Buscar assinaturas sem função
    assinaturas_sem_funcao = AssinaturaQuadroAcesso.objects.filter(
        funcao_assinatura__isnull=True
    ).select_related('assinado_por', 'quadro_acesso')
    
    print(f"📋 Assinaturas sem função encontradas: {assinaturas_sem_funcao.count()}")
    
    if not assinaturas_sem_funcao.exists():
        print("✅ Todas as assinaturas já possuem função registrada!")
        return
    
    atualizadas = 0
    
    for assinatura in assinaturas_sem_funcao:
        usuario = assinatura.assinado_por
        funcao_atual = "Usuário do Sistema"
        
        print(f"\n📝 Processando assinatura: {usuario.get_full_name()} - {assinatura.get_tipo_assinatura_display()}")
        
        # Tentar obter função do usuário
        if hasattr(usuario, 'militar') and usuario.militar:
            # Se é militar, buscar função na comissão
            membro_comissao = MembroComissao.objects.filter(
                usuario=usuario,
                ativo=True
            ).first()
            
            if membro_comissao:
                funcao_atual = f"{membro_comissao.get_tipo_display()} - {membro_comissao.cargo.nome}"
                print(f"   ✅ Função encontrada: {funcao_atual}")
            else:
                # Buscar função ativa do usuário
                funcao_usuario = UsuarioFuncao.objects.filter(
                    usuario=usuario,
                    status='ATIVO'
                ).first()
                
                if funcao_usuario:
                    funcao_atual = funcao_usuario.cargo_funcao.nome
                    print(f"   ✅ Função encontrada: {funcao_atual}")
                else:
                    funcao_atual = f"{usuario.militar.get_posto_graduacao_display()} - Militar"
                    print(f"   ⚠️  Função padrão: {funcao_atual}")
        else:
            # Se não é militar, buscar função ativa
            funcao_usuario = UsuarioFuncao.objects.filter(
                usuario=usuario,
                status='ATIVO'
            ).first()
            
            if funcao_usuario:
                funcao_atual = funcao_usuario.cargo_funcao.nome
                print(f"   ✅ Função encontrada: {funcao_atual}")
            else:
                print(f"   ⚠️  Função padrão: {funcao_atual}")
        
        # Atualizar a assinatura
        assinatura.funcao_assinatura = funcao_atual
        assinatura.save()
        atualizadas += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMO:")
    print(f"   - Assinaturas processadas: {assinaturas_sem_funcao.count()}")
    print(f"   - Assinaturas atualizadas: {atualizadas}")
    print(f"   - Função padrão usada: 'Usuário do Sistema'")
    
    # Verificar se ainda há assinaturas sem função
    restantes = AssinaturaQuadroAcesso.objects.filter(funcao_assinatura__isnull=True).count()
    if restantes > 0:
        print(f"   ⚠️  Ainda restam {restantes} assinaturas sem função")
    else:
        print(f"   ✅ Todas as assinaturas foram atualizadas!")

if __name__ == "__main__":
    atualizar_funcoes_assinaturas() 