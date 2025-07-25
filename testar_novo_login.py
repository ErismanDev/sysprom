#!/usr/bin/env python
"""
Script para testar o novo sistema de login com múltiplas funções
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao
from datetime import date

def testar_novo_login():
    """Testa o novo sistema de login com múltiplas funções"""
    
    print("=== TESTE DO NOVO SISTEMA DE LOGIN ===")
    print("=" * 50)
    
    # 1. Verificar usuário erisman
    try:
        user = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {user.get_full_name()} ({user.username})")
        print(f"   - Ativo: {user.is_active}")
        print(f"   - Superusuário: {user.is_superuser}")
        
        # 2. Verificar funções do usuário
        funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
        print(f"\n📋 Funções ativas do usuário: {funcoes.count()}")
        
        for funcao in funcoes:
            print(f"   - {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
        
        # 3. Testar login via cliente
        client = Client()
        
        print(f"\n🔐 Testando login...")
        response = client.post('/login/', {
            'username': 'erisman',
            'password': 'cbmepi123'
        })
        
        print(f"   Status code: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Login bem-sucedido!")
            print(f"   Redirect para: {response.url}")
            
            # Verificar sessão
            session = client.session
            print(f"\n📊 Dados da sessão:")
            print(f"   - funcao_atual_id: {session.get('funcao_atual_id')}")
            print(f"   - funcao_atual_nome: {session.get('funcao_atual_nome')}")
            print(f"   - funcoes_disponiveis: {session.get('funcoes_disponiveis')}")
            
            # Seguir redirecionamento
            if response.url == '/militares/selecionar-funcao/':
                print(f"\n🔄 Redirecionado para seleção de função")
                response = client.get('/militares/selecionar-funcao/')
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Página de seleção carregada!")
                    
                    # Selecionar primeira função
                    if funcoes.exists():
                        primeira_funcao = funcoes.first()
                        print(f"\n🎯 Selecionando função: {primeira_funcao.cargo_funcao.nome}")
                        
                        response = client.post('/militares/selecionar-funcao/', {
                            'funcao_id': primeira_funcao.id
                        })
                        
                        print(f"   Status: {response.status_code}")
                        print(f"   Redirect para: {response.url}")
                        
                        if response.status_code == 302 and response.url == '/militares/':
                            print("   ✅ Função selecionada com sucesso!")
                            
                            # Verificar dashboard
                            response = client.get('/militares/')
                            print(f"   Dashboard status: {response.status_code}")
                            
                            if response.status_code == 200:
                                print("   ✅ Dashboard acessível!")
                            else:
                                print("   ❌ Erro ao acessar dashboard")
                        else:
                            print("   ❌ Erro ao selecionar função")
                    else:
                        print("   ❌ Nenhuma função disponível")
                else:
                    print("   ❌ Erro ao carregar página de seleção")
            elif response.url == '/militares/':
                print(f"\n✅ Redirecionado diretamente para dashboard (função única)")
                
                # Verificar dashboard
                response = client.get('/militares/')
                print(f"   Dashboard status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Dashboard acessível!")
                else:
                    print("   ❌ Erro ao acessar dashboard")
            else:
                print(f"   ❌ Redirecionamento inesperado: {response.url}")
        else:
            print("   ❌ Falha no login!")
            
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado!")
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    testar_novo_login() 