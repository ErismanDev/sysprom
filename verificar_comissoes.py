#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, UsuarioFuncao, ComissaoPromocao

def verificar_comissoes():
    """Verifica as comissões e membros"""
    
    # Verificar todas as comissões
    comissoes = ComissaoPromocao.objects.all()
    print(f"Total de comissões: {comissoes.count()}")
    
    for comissao in comissoes:
        print(f"\n=== Comissão: {comissao.tipo} ===")
        print(f"  Status: {comissao.status}")
        print(f"  Membros ativos: {comissao.membros.filter(ativo=True).count()}")
        
        membros = comissao.membros.filter(ativo=True)
        for membro in membros:
            print(f"    - {membro.usuario.username} ({membro.usuario.get_full_name()})")
    
    # Verificar usuário específico
    usuario = User.objects.get(username='49008382334')
    print(f"\n{'='*60}")
    print(f"=== Usuário: {usuario.username} ===")
    
    # Verificar funções
    funcoes = UsuarioFuncao.objects.filter(usuario=usuario, status='ATIVO')
    print(f"Funções ativas: {funcoes.count()}")
    for funcao in funcoes:
        print(f"  - {funcao.cargo_funcao.nome}")
    
    # Verificar membros de comissão
    membros_comissao = MembroComissao.objects.filter(usuario=usuario)
    print(f"Membros de comissão (todos): {membros_comissao.count()}")
    for membro in membros_comissao:
        print(f"  - {membro.comissao.tipo} - {membro.comissao.status} (Ativo: {membro.ativo})")
    
    # Verificar membros ativos
    membros_ativos = MembroComissao.objects.filter(usuario=usuario, ativo=True)
    print(f"Membros de comissão ativos: {membros_ativos.count()}")
    for membro in membros_ativos:
        print(f"  - {membro.comissao.tipo} - {membro.comissao.status}")

if __name__ == '__main__':
    verificar_comissoes() 