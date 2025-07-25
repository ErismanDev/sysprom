#!/usr/bin/env python
"""
Script para verificar usuários duplicados e não vinculados aos militares
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def verificar_usuarios_duplicados():
    """Verifica usuários duplicados e não vinculados"""
    print("🔍 Verificando usuários duplicados e não vinculados...")
    print("=" * 70)
    
    # Buscar todos os usuários
    todos_usuarios = User.objects.all()
    usuarios_com_militar = User.objects.filter(militar__isnull=False)
    usuarios_sem_militar = User.objects.filter(militar__isnull=True)
    
    print(f"📊 Estatísticas gerais:")
    print(f"   • Total de usuários: {todos_usuarios.count()}")
    print(f"   • Usuários com militar vinculado: {usuarios_com_militar.count()}")
    print(f"   • Usuários sem militar vinculado: {usuarios_sem_militar.count()}")
    
    # Verificar se há CPFs duplicados
    print(f"\n🔍 Verificando CPFs duplicados...")
    
    # Buscar usuários por CPF (username)
    cpfs_unicos = set()
    cpfs_duplicados = {}
    
    for usuario in todos_usuarios:
        cpf = usuario.username
        if cpf in cpfs_unicos:
            if cpf not in cpfs_duplicados:
                cpfs_duplicados[cpf] = []
            cpfs_duplicados[cpf].append(usuario)
        else:
            cpfs_unicos.add(cpf)
    
    print(f"   • CPFs únicos: {len(cpfs_unicos)}")
    print(f"   • CPFs duplicados: {len(cpfs_duplicados)}")
    
    if cpfs_duplicados:
        print(f"\n📋 CPFs com usuários duplicados:")
        for cpf, usuarios in cpfs_duplicados.items():
            print(f"   • CPF: {cpf}")
            for i, usuario in enumerate(usuarios):
                tem_militar = "✅ Com militar" if hasattr(usuario, 'militar') and usuario.militar else "❌ Sem militar"
                print(f"     {i+1}. ID: {usuario.id} | Nome: {usuario.get_full_name()} | {tem_militar}")
    
    # Verificar usuários sem militar
    print(f"\n📋 Usuários sem militar vinculado:")
    for usuario in usuarios_sem_militar:
        print(f"   • ID: {usuario.id} | Username: {usuario.username} | Nome: {usuario.get_full_name()}")
    
    return {
        'total_usuarios': todos_usuarios.count(),
        'usuarios_com_militar': usuarios_com_militar.count(),
        'usuarios_sem_militar': usuarios_sem_militar.count(),
        'cpfs_duplicados': cpfs_duplicados
    }

def main():
    """Função principal"""
    resultado = verificar_usuarios_duplicados()
    
    print(f"\n" + "=" * 70)
    print(f"📊 RESUMO:")
    print(f"   • Total de usuários: {resultado['total_usuarios']}")
    print(f"   • Usuários com militar: {resultado['usuarios_com_militar']}")
    print(f"   • Usuários sem militar: {resultado['usuarios_sem_militar']}")
    print(f"   • CPFs duplicados: {len(resultado['cpfs_duplicados'])}")
    
    if resultado['usuarios_sem_militar'] > 0:
        print(f"\n⚠️  Existem {resultado['usuarios_sem_militar']} usuários sem militar vinculado!")
        print(f"💡 Recomendação: Remover usuários não vinculados")
    else:
        print(f"\n✅ Todos os usuários estão vinculados a militares!")

if __name__ == '__main__':
    main() 