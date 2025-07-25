#!/usr/bin/env python
"""
Script para testar a associação automática de usuários a militares
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar
from django.db import transaction

def testar_associacao_automatica():
    """Testa a associação automática de usuários a militares"""
    
    print("=== TESTE DE ASSOCIAÇÃO AUTOMÁTICA ===")
    
    # 1. Verificar militares sem usuário associado
    militares_sem_usuario = Militar.objects.filter(user__isnull=True)
    print(f"\n1. Militares sem usuário associado: {militares_sem_usuario.count()}")
    
    if militares_sem_usuario.exists():
        print("   Militares encontrados:")
        for militar in militares_sem_usuario[:5]:  # Mostrar apenas os primeiros 5
            print(f"   - {militar.nome_completo} (CPF: {militar.cpf})")
    
    # 2. Verificar usuários sem militar associado
    usuarios_sem_militar = User.objects.filter(militar__isnull=True)
    print(f"\n2. Usuários sem militar associado: {usuarios_sem_militar.count()}")
    
    if usuarios_sem_militar.exists():
        print("   Usuários encontrados:")
        for user in usuarios_sem_militar[:5]:  # Mostrar apenas os primeiros 5
            print(f"   - {user.username} ({user.get_full_name()})")
    
    # 3. Testar criação de usuário para militar existente
    print(f"\n3. Testando criação de usuário para militar existente...")
    
    # Buscar um militar sem usuário
    militar_teste = Militar.objects.filter(user__isnull=True).first()
    
    if militar_teste:
        print(f"   Militar selecionado para teste: {militar_teste.nome_completo}")
        
        # Criar usuário (isso deve disparar o signal)
        with transaction.atomic():
            username = militar_teste.cpf
            first_name = militar_teste.nome_completo.split()[0]
            last_name = ' '.join(militar_teste.nome_completo.split()[1:]) if len(militar_teste.nome_completo.split()) > 1 else ''
            
            # Verificar se já existe usuário com este username
            if User.objects.filter(username=username).exists():
                print(f"   Usuário com username {username} já existe")
            else:
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=militar_teste.email,
                    password='cbmepi123'
                )
                print(f"   Usuário criado: {user.username}")
                
                # Verificar se a associação foi feita
                militar_teste.refresh_from_db()
                if militar_teste.user:
                    print(f"   ✓ Associação automática funcionou! Militar associado ao usuário {militar_teste.user.username}")
                else:
                    print(f"   ✗ Associação automática falhou")
    else:
        print("   Nenhum militar sem usuário encontrado para teste")
    
    # 4. Testar criação de militar para usuário existente
    print(f"\n4. Testando criação de militar para usuário existente...")
    
    # Buscar um usuário sem militar
    user_teste = User.objects.filter(militar__isnull=True).first()
    
    if user_teste:
        print(f"   Usuário selecionado para teste: {user_teste.username}")
        
        # Criar militar (isso deve disparar o signal)
        with transaction.atomic():
            # Verificar se já existe militar com este CPF
            if Militar.objects.filter(cpf=user_teste.username).exists():
                print(f"   Militar com CPF {user_teste.username} já existe")
            else:
                # Criar militar de teste
                militar = Militar.objects.create(
                    matricula=f"TESTE_{user_teste.username}",
                    nome_completo=user_teste.get_full_name(),
                    nome_guerra=user_teste.first_name,
                    cpf=user_teste.username,
                    rg="123456789",
                    orgao_expedidor="SSP",
                    data_nascimento="1990-01-01",
                    sexo="M",
                    quadro="COMB",
                    posto_graduacao="SD",
                    data_ingresso="2020-01-01",
                    data_promocao_atual="2020-01-01",
                    situacao="AT",
                    email=user_teste.email or f"{user_teste.username}@teste.com",
                    telefone="(86) 99999-9999",
                    celular="(86) 99999-9999"
                )
                print(f"   Militar criado: {militar.nome_completo}")
                
                # Verificar se a associação foi feita
                user_teste.refresh_from_db()
                if hasattr(user_teste, 'militar') and user_teste.militar:
                    print(f"   ✓ Associação automática funcionou! Usuário associado ao militar {user_teste.militar.nome_completo}")
                else:
                    print(f"   ✗ Associação automática falhou")
    else:
        print("   Nenhum usuário sem militar encontrado para teste")
    
    # 5. Estatísticas finais
    print(f"\n5. Estatísticas finais:")
    total_militares = Militar.objects.count()
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    total_usuarios = User.objects.count()
    usuarios_com_militar = User.objects.filter(militar__isnull=False).count()
    
    print(f"   Total de militares: {total_militares}")
    print(f"   Militares com usuário: {militares_com_usuario} ({militares_com_usuario/total_militares*100:.1f}%)")
    print(f"   Total de usuários: {total_usuarios}")
    print(f"   Usuários com militar: {usuarios_com_militar} ({usuarios_com_militar/total_usuarios*100:.1f}%)")
    
    print(f"\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    testar_associacao_automatica() 