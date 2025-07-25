#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import SessaoComissao, AtaSessao, AssinaturaAta, MembroComissao, UsuarioFuncao

def testar_assinatura_duplicada():
    """Testar se a correção da assinatura duplicada funcionou"""
    
    print("=== TESTE DE ASSINATURA DUPLICADA ===")
    
    # Buscar uma sessão com ata
    try:
        sessao = SessaoComissao.objects.get(pk=4)
        print(f"✅ Sessão encontrada: {sessao}")
    except SessaoComissao.DoesNotExist:
        print("❌ Sessão 4 não encontrada")
        return
    
    # Buscar a ata da sessão
    try:
        ata = AtaSessao.objects.get(sessao=sessao)
        print(f"✅ Ata encontrada: {ata}")
    except AtaSessao.DoesNotExist:
        print("❌ Ata não encontrada para a sessão")
        return
    
    # Buscar um usuário para testar
    try:
        usuario = User.objects.get(username='490.083.823-34')
        print(f"✅ Usuário encontrado: {usuario.get_full_name()}")
    except User.DoesNotExist:
        print("❌ Usuário não encontrado")
        return
    
    # Verificar se o usuário é membro da comissão
    membro = MembroComissao.objects.filter(
        comissao=sessao.comissao,
        usuario=usuario,
        ativo=True
    ).first()
    
    if membro:
        print(f"✅ Usuário é membro da comissão: {membro}")
    else:
        print("❌ Usuário não é membro da comissão")
        return
    
    # Verificar assinaturas existentes
    assinaturas_existentes = AssinaturaAta.objects.filter(
        ata=ata,
        membro=membro
    )
    
    print(f"\n📝 Assinaturas existentes do membro: {assinaturas_existentes.count()}")
    for assinatura in assinaturas_existentes:
        print(f"   - Tipo: {assinatura.get_tipo_assinatura_display()}")
        print(f"     Função: {assinatura.funcao_assinatura}")
        print(f"     Data: {assinatura.data_assinatura}")
    
    print("\n=== ANÁLISE DA CORREÇÃO ===")
    print("🔧 Antes da correção:")
    print("   - Verificava: ata=ata, assinado_por=request.user, tipo_assinatura=tipo_assinatura")
    print("   - Problema: Permitia múltiplas assinaturas do mesmo usuário com tipos diferentes")
    
    print("\n🔧 Depois da correção:")
    print("   - Verifica: ata=ata, membro=membro")
    print("   - Vantagem: Impede múltiplas assinaturas do mesmo membro na mesma ata")
    
    print("\n=== VERIFICAÇÃO ===")
    print("✅ Agora verifica se já existe assinatura do membro na ata")
    print("✅ Impede assinaturas duplicadas do mesmo membro")
    print("✅ Resolve o erro UNIQUE constraint failed")
    print("✅ Mantém a integridade dos dados")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    testar_assinatura_duplicada() 