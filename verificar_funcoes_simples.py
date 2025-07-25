#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def verificar_funcoes_simples():
    print("=== VERIFICAÇÃO SIMPLES DAS FUNÇÕES ===\n")
    
    # 1. Verificar todas as funções
    print("1. TODAS AS FUNÇÕES EXISTENTES:")
    cargos = CargoFuncao.objects.all().order_by('nome')
    print(f"Total de funções: {cargos.count()}")
    for cargo in cargos:
        print(f"• {cargo.nome}")
    print()
    
    # 2. Verificar funções especiais
    print("2. FUNÇÕES ESPECIAIS:")
    funcoes_especiais = [
        'Diretor de Gestão de Pessoas',
        'Chefe da Seção de Promoções',
        'Administrador do Sistema',
        'Administrador'
    ]
    
    for funcao_nome in funcoes_especiais:
        try:
            cargo = CargoFuncao.objects.get(nome=funcao_nome)
            usuarios = UsuarioFuncao.objects.filter(cargo_funcao=cargo, status='ATIVO')
            print(f"✅ {funcao_nome}: {usuarios.count()} usuários")
            for uf in usuarios:
                print(f"   - {uf.usuario.username}")
        except CargoFuncao.DoesNotExist:
            print(f"❌ {funcao_nome}: NÃO EXISTE")
    print()
    
    # 3. Verificar usuários com funções
    print("3. USUÁRIOS COM FUNÇÕES:")
    funcoes = UsuarioFuncao.objects.filter(status='ATIVO').select_related('usuario', 'cargo_funcao')
    print(f"Total de funções ativas: {funcoes.count()}")
    for uf in funcoes:
        print(f"• {uf.usuario.username} - {uf.cargo_funcao.nome}")
    print()
    
    # 4. Verificar se há usuários sem funções
    print("4. USUÁRIOS SEM FUNÇÕES:")
    usuarios_com_funcao = set(UsuarioFuncao.objects.filter(status='ATIVO').values_list('usuario_id', flat=True))
    usuarios_sem_funcao = User.objects.exclude(id__in=usuarios_com_funcao).exclude(username='admin')
    print(f"Total de usuários sem funções: {usuarios_sem_funcao.count()}")
    for user in usuarios_sem_funcao[:5]:  # Mostrar apenas 5
        print(f"• {user.username}")
    if usuarios_sem_funcao.count() > 5:
        print(f"... e mais {usuarios_sem_funcao.count() - 5} usuários")
    
    print("\n=== FIM DA VERIFICAÇÃO ===")

if __name__ == '__main__':
    verificar_funcoes_simples() 