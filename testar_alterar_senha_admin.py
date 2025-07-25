#!/usr/bin/env python
"""
Script para testar a funcionalidade de administradores alterarem senhas de outros usuários
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from militares.models import UsuarioFuncao

def testar_alterar_senha_admin():
    """Testa a funcionalidade de administradores alterarem senhas"""
    
    print("=== TESTE DE ALTERAR SENHA POR ADMINISTRADOR ===")
    print("=" * 50)
    
    # 1. Verificar usuário administrador
    try:
        admin_user = User.objects.get(username='erisman')
        print(f"✅ Administrador encontrado: {admin_user.get_full_name()} ({admin_user.username})")
        print(f"   - Superusuário: {admin_user.is_superuser}")
        print(f"   - Ativo: {admin_user.is_active}")
        
        # 2. Verificar usuário alvo
        target_user = User.objects.filter(is_active=True).exclude(username='erisman').first()
        if target_user:
            print(f"\n✅ Usuário alvo encontrado: {target_user.get_full_name()} ({target_user.username})")
        else:
            print("❌ Nenhum usuário alvo encontrado!")
            return
        
        # 3. Testar login como administrador
        client = Client()
        print(f"\n🔐 Fazendo login como administrador...")
        response = client.post('/login/', {
            'username': 'erisman',
            'password': 'cbmepi123'
        })
        
        if response.status_code == 302:
            print("   ✅ Login bem-sucedido!")
            
            # Seguir redirecionamento se necessário
            if response.url == '/militares/selecionar-funcao/':
                print("   🔄 Redirecionado para seleção de função...")
                response = client.get('/militares/selecionar-funcao/')
                
                # Selecionar primeira função disponível
                funcoes = UsuarioFuncao.objects.filter(usuario=admin_user, status='ATIVO')
                if funcoes.exists():
                    primeira_funcao = funcoes.first()
                    response = client.post('/militares/selecionar-funcao/', {
                        'funcao_id': primeira_funcao.id
                    })
                    print(f"   ✅ Função selecionada: {primeira_funcao.cargo_funcao.nome}")
            
            # 4. Acessar página de detalhes do usuário alvo
            print(f"\n📋 Acessando página de detalhes do usuário alvo...")
            response = client.get(f'/militares/usuarios/{target_user.pk}/')
            
            if response.status_code == 200:
                print("   ✅ Página de detalhes carregada!")
                
                # Verificar se o botão de alterar senha está presente
                content = response.content.decode('utf-8')
                if 'Alterar Senha do Usuário' in content:
                    print("   ✅ Botão 'Alterar Senha do Usuário' encontrado!")
                else:
                    print("   ❌ Botão 'Alterar Senha do Usuário' não encontrado!")
                
                # 5. Acessar página de alterar senha
                print(f"\n🔑 Acessando página de alterar senha...")
                response = client.get(f'/militares/usuarios/{target_user.pk}/alterar-senha/')
                
                if response.status_code == 200:
                    print("   ✅ Página de alterar senha carregada!")
                    
                    # Verificar se o formulário está presente
                    content = response.content.decode('utf-8')
                    if 'Nova Senha' in content and 'Confirmar Nova Senha' in content:
                        print("   ✅ Formulário de alterar senha encontrado!")
                        
                        # 6. Testar alteração de senha
                        print(f"\n💾 Testando alteração de senha...")
                        nova_senha = 'nova_senha_teste_123'
                        response = client.post(f'/militares/usuarios/{target_user.pk}/alterar-senha/', {
                            'nova_senha1': nova_senha,
                            'nova_senha2': nova_senha
                        })
                        
                        if response.status_code == 302:
                            print("   ✅ Senha alterada com sucesso!")
                            
                            # 7. Verificar se a senha foi realmente alterada
                            target_user.refresh_from_db()
                            if target_user.check_password(nova_senha):
                                print("   ✅ Senha confirmada no banco de dados!")
                                
                                # 8. Testar login com nova senha
                                print(f"\n🔐 Testando login com nova senha...")
                                client2 = Client()
                                response = client2.post('/login/', {
                                    'username': target_user.username,
                                    'password': nova_senha
                                })
                                
                                if response.status_code == 302:
                                    print("   ✅ Login com nova senha bem-sucedido!")
                                else:
                                    print("   ❌ Falha no login com nova senha!")
                            else:
                                print("   ❌ Senha não foi alterada no banco de dados!")
                        else:
                            print(f"   ❌ Erro ao alterar senha: {response.status_code}")
                    else:
                        print("   ❌ Formulário de alterar senha não encontrado!")
                else:
                    print(f"   ❌ Erro ao carregar página de alterar senha: {response.status_code}")
            else:
                print(f"   ❌ Erro ao carregar página de detalhes: {response.status_code}")
                print(f"   URL de redirecionamento: {response.url}")
        else:
            print("   ❌ Falha no login!")
            
    except User.DoesNotExist:
        print("❌ Usuário administrador 'erisman' não encontrado!")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_alterar_senha_admin() 