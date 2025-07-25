#!/usr/bin/env python
"""
Script para testar se o problema das permissões foi resolvido
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from militares.models import CargoFuncao, UsuarioFuncao, PermissaoFuncao

def testar_permissoes_funcao():
    """Testa se o sistema de permissões está funcionando corretamente"""
    
    print("=== Teste do Sistema de Permissões ===")
    
    try:
        # 1. Verificar se existe pelo menos um cargo/função
        cargos = CargoFuncao.objects.all()
        print(f"1. Cargos/Funções encontrados: {cargos.count()}")
        
        if not cargos.exists():
            print("   Criando cargo de teste...")
            cargo_teste = CargoFuncao.objects.create(
                nome="Cargo de Teste",
                descricao="Cargo para teste do sistema",
                ativo=True,
                ordem=1
            )
        else:
            cargo_teste = cargos.first()
            print(f"   Usando cargo: {cargo_teste.nome}")
        
        # 2. Verificar se existe pelo menos um usuário
        usuarios = User.objects.all()
        print(f"2. Usuários encontrados: {usuarios.count()}")
        
        if not usuarios.exists():
            print("   Criando usuário de teste...")
            usuario_teste = User.objects.create_user(
                username='teste',
                first_name='Usuário',
                last_name='Teste',
                email='teste@teste.com',
                password='teste123'
            )
        else:
            usuario_teste = usuarios.first()
            print(f"   Usando usuário: {usuario_teste.get_full_name()}")
        
        # 3. Criar uma função de usuário
        print("3. Criando função de usuário...")
        funcao_usuario, created = UsuarioFuncao.objects.get_or_create(
            usuario=usuario_teste,
            cargo_funcao=cargo_teste,
            defaults={
                'tipo_funcao': 'ADMINISTRATIVO',
                'status': 'ATIVO',
                'data_inicio': '2025-01-01'
            }
        )
        
        if created:
            print(f"   Função criada: {funcao_usuario}")
        else:
            print(f"   Função já existia: {funcao_usuario}")
        
        # 4. Criar uma permissão de função
        print("4. Criando permissão de função...")
        permissao_funcao, created = PermissaoFuncao.objects.get_or_create(
            cargo_funcao=cargo_teste,
            modulo='MILITARES',
            acesso='VISUALIZAR',
            defaults={
                'ativo': True,
                'observacoes': 'Permissão de teste'
            }
        )
        
        if created:
            print(f"   Permissão criada: {permissao_funcao}")
        else:
            print(f"   Permissão já existia: {permissao_funcao}")
        
        # 5. Testar se a função aplicar_permissoes_funcao_a_usuarios funciona
        print("5. Testando aplicação de permissões...")
        
        # Importar a função
        from militares.views import aplicar_permissoes_funcao_a_usuarios
        
        try:
            aplicar_permissoes_funcao_a_usuarios(cargo_teste)
            print("   ✅ Função aplicar_permissoes_funcao_a_usuarios executada com sucesso!")
        except Exception as e:
            print(f"   ❌ Erro ao executar aplicar_permissoes_funcao_a_usuarios: {e}")
            return False
        
        # 6. Verificar se as permissões foram aplicadas
        print("6. Verificando permissões aplicadas...")
        permissoes_usuario = usuario_teste.user_permissions.all()
        print(f"   Permissões do usuário: {permissoes_usuario.count()}")
        
        for perm in permissoes_usuario:
            print(f"   - {perm.codename}")
        
        print("\n=== Teste Concluído com Sucesso! ===")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = testar_permissoes_funcao()
    sys.exit(0 if sucesso else 1) 