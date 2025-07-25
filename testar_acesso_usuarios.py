#!/usr/bin/env python
"""
Script para testar o acesso às funções de usuários
"""
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao

def testar_acesso_usuarios():
    """Testa o acesso às funções de usuários"""
    
    print("🔍 TESTANDO ACESSO ÀS FUNÇÕES DE USUÁRIOS")
    print("=" * 60)
    
    # 1. Verificar usuário erisman
    try:
        usuario = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {usuario.get_full_name()}")
        print(f"   - is_staff: {usuario.is_staff}")
        print(f"   - is_superuser: {usuario.is_superuser}")
        print(f"   - is_active: {usuario.is_active}")
        
        # Verificar permissões
        permissoes = usuario.user_permissions.all()
        print(f"   - Permissões diretas: {permissoes.count()}")
        
        grupos = usuario.groups.all()
        print(f"   - Grupos: {grupos.count()}")
        for grupo in grupos:
            print(f"     - {grupo.name}")
        
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado!")
        return False
    
    # 2. Verificar funções do usuário
    funcoes = usuario.funcoes.all()
    print(f"\n📋 Funções do usuário 'erisman':")
    print(f"   - Total de funções: {funcoes.count()}")
    
    for funcao in funcoes:
        print(f"     ✅ {funcao.nome_funcao} ({funcao.get_tipo_funcao_display()}) - {funcao.get_status_display()}")
    
    # 3. Verificar URLs disponíveis
    print(f"\n🌐 URLs DISPONÍVEIS:")
    print(f"   - Lista de usuários: /militares/usuarios/custom/")
    print(f"   - Detalhes do usuário: /militares/usuarios/{usuario.pk}/")
    print(f"   - Funções do usuário: /militares/usuarios/{usuario.pk}/funcoes/")
    print(f"   - Adicionar função: /militares/usuarios/{usuario.pk}/funcoes/adicionar/")
    
    # 4. Verificar se o usuário tem permissões necessárias
    print(f"\n🔐 PERMISSÕES NECESSÁRIAS:")
    permissoes_necessarias = [
        'auth.view_user',
        'auth.change_user',
        'auth.add_user',
        'auth.delete_user'
    ]
    
    for permissao in permissoes_necessarias:
        tem_permissao = usuario.has_perm(permissao)
        print(f"   - {permissao}: {'✅' if tem_permissao else '❌'}")
    
    # 5. Sugestões para resolver problemas
    print(f"\n💡 SUGESTÕES:")
    print(f"   1. Certifique-se de estar logado como 'erisman'")
    print(f"   2. Verifique se o usuário tem as permissões necessárias")
    print(f"   3. Use a URL correta: /militares/usuarios/custom/")
    print(f"   4. Se não tiver permissões, adicione ao grupo 'Staff'")
    
    return True

if __name__ == '__main__':
    sucesso = testar_acesso_usuarios()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ Teste concluído!")
        print("\n📝 Para acessar as funções:")
        print("   1. Faça login com o usuário 'erisman'")
        print("   2. Acesse: http://127.0.0.1:8000/militares/usuarios/custom/")
        print("   3. Selecione um usuário para gerenciar suas funções")
    else:
        print("❌ Teste falhou!") 