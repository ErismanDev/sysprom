#!/usr/bin/env python
"""
Script para verificar usuários com militar associado
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao

def verificar_usuarios_militares():
    """Verifica usuários com militar associado"""
    
    print("🔍 VERIFICANDO USUÁRIOS COM MILITAR ASSOCIADO")
    print("=" * 60)
    
    # 1. Verificar todos os usuários
    usuarios = User.objects.all()
    print(f"📋 Total de usuários: {usuarios.count()}")
    
    # 2. Verificar usuários com militar associado
    usuarios_com_militar = []
    usuarios_sem_militar = []
    
    for usuario in usuarios:
        try:
            militar = usuario.militar
            usuarios_com_militar.append((usuario, militar))
        except Militar.DoesNotExist:
            usuarios_sem_militar.append(usuario)
    
    print(f"\n✅ USUÁRIOS COM MILITAR ASSOCIADO: {len(usuarios_com_militar)}")
    for usuario, militar in usuarios_com_militar:
        print(f"   • {usuario.username} - {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
    
    print(f"\n❌ USUÁRIOS SEM MILITAR ASSOCIADO: {len(usuarios_sem_militar)}")
    for usuario in usuarios_sem_militar:
        print(f"   • {usuario.username}")
    
    # 3. Verificar militares sem usuário associado
    militares_sem_usuario = Militar.objects.filter(user__isnull=True)
    print(f"\n🔍 MILITARES SEM USUÁRIO ASSOCIADO: {militares_sem_usuario.count()}")
    for militar in militares_sem_usuario[:10]:  # Mostrar apenas os primeiros 10
        print(f"   • {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - {militar.matricula}")
    
    if militares_sem_usuario.count() > 10:
        print(f"   ... e mais {militares_sem_usuario.count() - 10} militares")
    
    # 4. Sugerir associação
    if usuarios_com_militar and militares_sem_usuario.exists():
        print(f"\n💡 SUGESTÃO:")
        print(f"   Para testar a ficha pessoal, você pode:")
        print(f"   1. Associar um militar a um usuário existente")
        print(f"   2. Ou criar um novo usuário e associar a um militar")
        
        # Mostrar alguns militares disponíveis
        print(f"\n   Militares disponíveis para associação:")
        for militar in militares_sem_usuario[:5]:
            print(f"     • {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - {militar.matricula}")
    
    # 5. Verificar se há usuários com função "Usuário"
    usuarios_com_funcao_padrao = UsuarioFuncao.objects.filter(
        cargo_funcao__nome='Usuário',
        status='ATIVO'
    ).select_related('usuario')
    
    print(f"\n👤 USUÁRIOS COM FUNÇÃO 'USUÁRIO': {usuarios_com_funcao_padrao.count()}")
    for uf in usuarios_com_funcao_padrao:
        try:
            militar = uf.usuario.militar
            print(f"   • {uf.usuario.username} - {militar.nome_completo} ✅")
        except Militar.DoesNotExist:
            print(f"   • {uf.usuario.username} - SEM MILITAR ❌")

if __name__ == "__main__":
    verificar_usuarios_militares() 