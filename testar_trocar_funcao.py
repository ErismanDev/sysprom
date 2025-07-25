#!/usr/bin/env python
"""
Script para testar a funcionalidade de trocar função
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao

def testar_trocar_funcao():
    """Testa a funcionalidade de trocar função"""
    
    print("🔍 TESTANDO FUNCIONALIDADE DE TROCAR FUNÇÃO")
    print("=" * 60)
    
    # 1. Verificar usuários com múltiplas funções
    print("📋 1. USUÁRIOS COM MÚLTIPLAS FUNÇÕES:")
    usuarios_com_multiplas_funcoes = []
    
    for usuario in User.objects.filter(is_active=True):
        funcoes_ativas = UsuarioFuncao.objects.filter(
            usuario=usuario,
            status='ATIVO'
        ).count()
        
        if funcoes_ativas > 1:
            usuarios_com_multiplas_funcoes.append(usuario)
            print(f"   ✅ {usuario.get_full_name()} ({usuario.username}): {funcoes_ativas} funções")
    
    if not usuarios_com_multiplas_funcoes:
        print("   ⚠️  Nenhum usuário com múltiplas funções encontrado")
    
    # 2. Verificar todas as funções ativas
    print(f"\n📊 2. TODAS AS FUNÇÕES ATIVAS:")
    funcoes_ativas = UsuarioFuncao.objects.filter(status='ATIVO').select_related('usuario', 'cargo_funcao')
    
    for funcao in funcoes_ativas:
        print(f"   - {funcao.usuario.username}: {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
    
    # 3. Como acessar a funcionalidade
    print(f"\n🌐 3. COMO ACESSAR TROCAR FUNÇÃO:")
    print("   - URL: http://127.0.0.1:8000/militares/trocar-funcao/")
    print("   - Menu: Clique no nome do usuário no canto superior direito")
    print("   - Opção: 'Trocar Função'")
    
    # 4. Verificar se há usuários para testar
    if usuarios_com_multiplas_funcoes:
        print(f"\n🧪 4. USUÁRIOS PARA TESTAR:")
        for usuario in usuarios_com_multiplas_funcoes[:3]:  # Mostrar apenas os primeiros 3
            print(f"   - {usuario.get_full_name()} ({usuario.username})")
            funcoes = UsuarioFuncao.objects.filter(usuario=usuario, status='ATIVO')
            for funcao in funcoes:
                print(f"     • {funcao.cargo_funcao.nome}")
    
    # 5. Verificar URLs disponíveis
    print(f"\n🔗 5. URLS DISPONÍVEIS:")
    print("   - Trocar função: /militares/trocar-funcao/")
    print("   - Selecionar função: /militares/selecionar-funcao/")
    
    # 6. Verificar se o middleware está funcionando
    print(f"\n⚙️  6. MIDDLEWARE DE FUNÇÃO:")
    print("   - Arquivo: militares/middleware.py")
    print("   - Classe: FuncaoSelecaoMiddleware")
    print("   - Função: Verifica se usuário tem função selecionada")
    
    return True

if __name__ == '__main__':
    testar_trocar_funcao() 