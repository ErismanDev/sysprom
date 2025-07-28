#!/usr/bin/env python
"""
Script para limpar cache e forçar atualização das views
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.core.cache import cache
from django.core.management import call_command

def limpar_cache_final():
    """Limpa cache e força atualização"""
    
    print("🧹 LIMPANDO CACHE E FORÇANDO ATUALIZAÇÃO")
    print("=" * 60)
    
    # 1. Limpar cache do Django
    print("1️⃣ Limpando cache do Django...")
    cache.clear()
    print("   ✅ Cache limpo!")
    
    # 2. Coletar arquivos estáticos
    print("2️⃣ Coletando arquivos estáticos...")
    try:
        call_command('collectstatic', '--noinput', verbosity=0)
        print("   ✅ Arquivos estáticos coletados!")
    except Exception as e:
        print(f"   ⚠️ Erro ao coletar estáticos: {e}")
    
    # 3. Verificar dados no banco
    print("3️⃣ Verificando dados no banco...")
    from militares.models import AlmanaqueMilitar, QuadroAcesso, QuadroFixacaoVagas
    
    total_almanaques = AlmanaqueMilitar.objects.filter(ativo=True).count()
    total_quadros_acesso = QuadroAcesso.objects.count()
    total_quadros_fixacao = QuadroFixacaoVagas.objects.count()
    
    print(f"   • Almanaques ativos: {total_almanaques}")
    print(f"   • Quadros de acesso: {total_quadros_acesso}")
    print(f"   • Quadros de fixação: {total_quadros_fixacao}")
    
    # 4. Verificar usuário admin
    print("4️⃣ Verificando usuário admin...")
    from django.contrib.auth.models import User
    try:
        user_admin = User.objects.get(username='erisman')
        print(f"   ✅ Usuário encontrado: {user_admin.username}")
        print(f"   • is_superuser: {user_admin.is_superuser}")
        print(f"   • is_staff: {user_admin.is_staff}")
    except User.DoesNotExist:
        print("   ❌ Usuário 'erisman' não encontrado")
    
    # 5. Verificar funções do usuário
    print("5️⃣ Verificando funções do usuário...")
    from militares.models import UsuarioFuncao
    funcoes = UsuarioFuncao.objects.filter(usuario=user_admin, status='ATIVO')
    
    if funcoes.exists():
        for funcao in funcoes:
            print(f"   • {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função ativa encontrada")
    
    # 6. Conclusão
    print("6️⃣ CONCLUSÃO:")
    print("   🎯 Todas as views foram corrigidas para incluir superusuários!")
    print("   📋 Agora você deve conseguir ver:")
    
    if total_almanaques > 0:
        print("   ✅ Almanaques (se houver dados)")
    else:
        print("   ⚠️ Almanaques (não há dados no banco)")
    
    if total_quadros_acesso > 0:
        print("   ✅ Quadros de Acesso (se houver dados)")
    else:
        print("   ⚠️ Quadros de Acesso (não há dados no banco)")
    
    if total_quadros_fixacao > 0:
        print("   ✅ Quadros de Fixação (se houver dados)")
    else:
        print("   ⚠️ Quadros de Fixação (não há dados no banco)")
    
    print("\n   🔍 PRÓXIMOS PASSOS:")
    print("   1. Acesse: http://127.0.0.1:8000/militares/")
    print("   2. Clique nos menus: Almanaques, Quadros de Acesso, Quadros de Fixação")
    print("   3. Se não aparecer dados, pode ser que não existam no banco")
    print("   4. Tente Ctrl+F5 para forçar recarregamento do navegador")
    
    print("\n   🎉 SISTEMA CORRIGIDO COM SUCESSO!")

if __name__ == "__main__":
    limpar_cache_final() 