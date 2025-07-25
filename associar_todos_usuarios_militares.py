#!/usr/bin/env python
"""
Script para associar automaticamente todos os usuários do sistema aos seus respectivos militares
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.contrib.auth.models import User

def associar_todos_usuarios_militares():
    """Associa automaticamente todos os usuários aos seus respectivos militares"""
    print("🔗 ASSOCIANDO TODOS OS USUÁRIOS AOS MILITARES")
    print("=" * 60)
    
    # Buscar todos os usuários
    usuarios = User.objects.all()
    print(f"📋 Total de usuários no sistema: {usuarios.count()}")
    
    # Buscar todos os militares
    militares = Militar.objects.all()
    print(f"🎖️  Total de militares no sistema: {militares.count()}")
    
    associacoes_feitas = 0
    associacoes_existentes = 0
    usuarios_sem_militar = 0
    militares_sem_usuario = 0
    
    print(f"\n🔍 PROCESSANDO ASSOCIAÇÕES:")
    print("-" * 60)
    
    # Processar cada usuário
    for usuario in usuarios:
        print(f"\n👤 Processando usuário: {usuario.get_full_name()} ({usuario.username})")
        
        # Tentar encontrar militar pelo nome do usuário
        militar_encontrado = None
        
        # Buscar por diferentes variações do nome
        nome_usuario = usuario.get_full_name() or usuario.username
        
        # Buscar militar pelo nome completo (usando filter para evitar múltiplos resultados)
        militares_candidatos = Militar.objects.filter(nome_completo__icontains=nome_usuario)
        
        if militares_candidatos.count() == 1:
            militar_encontrado = militares_candidatos.first()
            print(f"   ✅ Militar encontrado por nome completo: {militar_encontrado.nome_completo}")
        elif militares_candidatos.count() > 1:
            print(f"   ⚠️  Múltiplos militares encontrados por nome completo ({militares_candidatos.count()}):")
            for m in militares_candidatos:
                print(f"      - {m.nome_completo} ({m.get_posto_graduacao_display()})")
            # Tentar encontrar o mais específico
            for militar in militares_candidatos:
                if militar.nome_completo.lower() == nome_usuario.lower():
                    militar_encontrado = militar
                    print(f"   ✅ Militar específico encontrado: {militar_encontrado.nome_completo}")
                    break
        else:
            # Buscar por partes do nome
            partes_nome = nome_usuario.split()
            for parte in partes_nome:
                if len(parte) > 2:  # Ignorar palavras muito curtas
                    militares_parte = Militar.objects.filter(nome_completo__icontains=parte)
                    if militares_parte.count() == 1:
                        militar_encontrado = militares_parte.first()
                        print(f"   ✅ Militar encontrado por parte do nome '{parte}': {militar_encontrado.nome_completo}")
                        break
                    elif militares_parte.count() > 1:
                        print(f"   ⚠️  Múltiplos militares encontrados para '{parte}' ({militares_parte.count()})")
                        continue
        
        # Se não encontrou, tentar buscar por username
        if not militar_encontrado:
            militares_username = Militar.objects.filter(nome_completo__icontains=usuario.username)
            if militares_username.count() == 1:
                militar_encontrado = militares_username.first()
                print(f"   ✅ Militar encontrado por username: {militar_encontrado.nome_completo}")
            elif militares_username.count() > 1:
                print(f"   ⚠️  Múltiplos militares encontrados por username ({militares_username.count()})")
        
        # Se encontrou militar
        if militar_encontrado:
            # Verificar se já tem usuário associado
            if militar_encontrado.user:
                if militar_encontrado.user == usuario:
                    print(f"   ✅ Já associado corretamente")
                    associacoes_existentes += 1
                else:
                    print(f"   ⚠️  Militar já tem usuário diferente: {militar_encontrado.user.username}")
                    # Decidir se quer trocar (neste caso, vamos manter o atual)
                    print(f"   ℹ️  Mantendo associação atual")
                    associacoes_existentes += 1
            else:
                # Associar o usuário ao militar
                militar_encontrado.user = usuario
                militar_encontrado.save()
                print(f"   ✅ Usuário associado ao militar: {militar_encontrado.nome_completo}")
                associacoes_feitas += 1
        else:
            print(f"   ❌ Nenhum militar encontrado para este usuário")
            usuarios_sem_militar += 1
    
    # Verificar militares sem usuário
    militares_sem_usuario = Militar.objects.filter(user__isnull=True).count()
    
    print(f"\n" + "=" * 60)
    print(f"📊 RESUMO DAS ASSOCIAÇÕES:")
    print(f"   - Associações feitas: {associacoes_feitas}")
    print(f"   - Associações já existentes: {associacoes_existentes}")
    print(f"   - Usuários sem militar encontrado: {usuarios_sem_militar}")
    print(f"   - Militares sem usuário: {militares_sem_usuario}")
    
    # Mostrar usuários sem militar
    if usuarios_sem_militar > 0:
        print(f"\n⚠️  USUÁRIOS SEM MILITAR ENCONTRADO:")
        for usuario in usuarios:
            nome_usuario = usuario.get_full_name() or usuario.username
            militares_candidatos = Militar.objects.filter(nome_completo__icontains=nome_usuario)
            if militares_candidatos.count() == 0:
                print(f"   - {usuario.get_full_name()} ({usuario.username})")
    
    # Mostrar militares sem usuário
    if militares_sem_usuario > 0:
        print(f"\n⚠️  MILITARES SEM USUÁRIO:")
        for militar in Militar.objects.filter(user__isnull=True)[:10]:  # Mostrar apenas os primeiros 10
            print(f"   - {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
        if militares_sem_usuario > 10:
            print(f"   ... e mais {militares_sem_usuario - 10} militares")

if __name__ == "__main__":
    associar_todos_usuarios_militares() 