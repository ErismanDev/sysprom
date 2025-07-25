#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, Militar

def verificar_usuarios_comissoes():
    print("=== VERIFICAÇÃO DE USUÁRIOS EM COMISSÕES ===\n")
    
    # Verificar todos os membros de comissão
    membros = MembroComissao.objects.all().select_related('usuario', 'militar', 'comissao')
    
    print("1. MEMBROS DE COMISSÃO:")
    for membro in membros:
        print(f"   • Militar: {membro.militar.nome_completo}")
        print(f"     - Comissão: {membro.comissao.nome} ({membro.comissao.tipo})")
        print(f"     - Usuário Django: {membro.usuario}")
        print(f"     - Ativo: {membro.ativo}")
        
        # Verificar se o militar tem usuário Django
        if membro.usuario:
            try:
                user = User.objects.get(username=membro.usuario.username)
                print(f"     - ✅ Usuário Django encontrado: {user.username}")
            except User.DoesNotExist:
                print(f"     - ❌ Usuário Django NÃO encontrado para: {membro.usuario.username}")
        else:
            print(f"     - ❌ Nenhum usuário Django associado")
        
        print()
    
    # Verificar militares que têm usuário Django mas não estão em comissões
    print("2. MILITARES COM USUÁRIO DJANGO:")
    militares_com_usuario = Militar.objects.filter(user__isnull=False).select_related('user')
    for militar in militares_com_usuario:
        membros_militar = MembroComissao.objects.filter(militar=militar)
        print(f"   • {militar.nome_completo} - Usuário: {militar.user.username}")
        print(f"     - Membro de comissões: {membros_militar.count()}")
        for membro in membros_militar:
            print(f"       * {membro.comissao.nome} ({membro.comissao.tipo}) - Ativo: {membro.ativo}")
        print()
    
    print("=== FIM DA VERIFICAÇÃO ===")

if __name__ == '__main__':
    verificar_usuarios_comissoes() 