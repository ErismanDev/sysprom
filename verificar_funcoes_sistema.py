#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def verificar_funcoes_sistema():
    print("=== VERIFICAÇÃO DAS FUNÇÕES DO SISTEMA ===\n")
    
    # 1. Verificar todas as funções existentes
    print("1. FUNÇÕES/CARGOS EXISTENTES:")
    cargos = CargoFuncao.objects.all().order_by('nome')
    print(f"   Total de funções: {cargos.count()}")
    for cargo in cargos:
        usuarios_com_funcao = UsuarioFuncao.objects.filter(
            cargo_funcao=cargo, 
            status='ATIVO'
        ).count()
        print(f"   • {cargo.nome} - {usuarios_com_funcao} usuários ativos")
    print()
    
    # 2. Verificar funções especiais que devem existir
    print("2. FUNÇÕES ESPECIAIS NECESSÁRIAS:")
    funcoes_especiais = [
        'Diretor de Gestão de Pessoas',
        'Chefe da Seção de Promoções',
        'Administrador do Sistema',
        'Administrador'
    ]
    
    for funcao_nome in funcoes_especiais:
        try:
            cargo = CargoFuncao.objects.get(nome=funcao_nome)
            usuarios_ativos = UsuarioFuncao.objects.filter(
                cargo_funcao=cargo, 
                status='ATIVO'
            )
            print(f"   ✅ {funcao_nome}: {usuarios_ativos.count()} usuários")
            for uf in usuarios_ativos:
                print(f"     - {uf.usuario.username}")
        except CargoFuncao.DoesNotExist:
            print(f"   ❌ {funcao_nome}: NÃO EXISTE")
    print()
    
    # 3. Verificar funções de comissão
    print("3. FUNÇÕES DE COMISSÃO:")
    funcoes_comissao = [
        'Presidente da CPO',
        'Membro Nato da CPO', 
        'Membro Efetivo da CPO',
        'Secretário da CPO',
        'Suplente da CPO',
        'Presidente da CPP',
        'Membro Nato da CPP',
        'Membro Efetivo da CPP', 
        'Secretário da CPP',
        'Suplente da CPP'
    ]
    
    for funcao_nome in funcoes_comissao:
        try:
            cargo = CargoFuncao.objects.get(nome=funcao_nome)
            usuarios_ativos = UsuarioFuncao.objects.filter(
                cargo_funcao=cargo, 
                status='ATIVO'
            )
            print(f"   ✅ {funcao_nome}: {usuarios_ativos.count()} usuários")
        except CargoFuncao.DoesNotExist:
            print(f"   ❌ {funcao_nome}: NÃO EXISTE")
    print()
    
    # 4. Verificar usuários sem funções
    print("4. USUÁRIOS SEM FUNÇÕES ATIVAS:")
    usuarios_com_funcao = User.objects.filter(funcoes__isnull=False).distinct()
    usuarios_sem_funcao = User.objects.exclude(id__in=usuarios_com_funcao).exclude(username='admin')
    
    print(f"   Total de usuários sem funções: {usuarios_sem_funcao.count()}")
    for user in usuarios_sem_funcao[:10]:  # Mostrar apenas os primeiros 10
        print(f"   • {user.username} - {user.get_full_name()}")
    if usuarios_sem_funcao.count() > 10:
        print(f"   ... e mais {usuarios_sem_funcao.count() - 10} usuários")
    print()
    
    # 5. Verificar usuários com múltiplas funções
    print("5. USUÁRIOS COM MÚLTIPLAS FUNÇÕES:")
    from django.db.models import Count
    usuarios_multiplas_funcoes = User.objects.annotate(
        num_funcoes=Count('funcoes')
    ).filter(num_funcoes__gt=1).order_by('-num_funcoes')
    
    for user in usuarios_multiplas_funcoes:
        funcoes = UsuarioFuncao.objects.filter(usuario=user, status='ATIVO')
        print(f"   • {user.username}: {funcoes.count()} funções")
        for uf in funcoes:
            print(f"     - {uf.cargo_funcao.nome}")
    print()
    
    print("=== FIM DA VERIFICAÇÃO ===")

if __name__ == '__main__':
    verificar_funcoes_sistema() 