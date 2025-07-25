#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao
from datetime import date

def atribuir_funcoes_usuarios():
    print("=== ATRIBUINDO FUNÇÕES AOS USUÁRIOS ===\n")
    
    # 1. Verificar quantos usuários não têm funções
    usuarios_com_funcao = set(UsuarioFuncao.objects.filter(status='ATIVO').values_list('usuario_id', flat=True))
    usuarios_sem_funcao = User.objects.exclude(id__in=usuarios_com_funcao).exclude(username='admin')
    
    print(f"Usuários sem funções: {usuarios_sem_funcao.count()}")
    
    if usuarios_sem_funcao.count() == 0:
        print("✅ Todos os usuários já têm funções!")
        return
    
    # 2. Buscar ou criar função básica "Usuário"
    try:
        cargo_usuario = CargoFuncao.objects.get(nome='Usuário')
        print(f"✅ Função 'Usuário' encontrada")
    except CargoFuncao.DoesNotExist:
        print("❌ Função 'Usuário' não encontrada")
        return
    
    # 3. Atribuir função "Usuário" aos usuários sem funções
    print(f"\nAtribuindo função 'Usuário' aos usuários...")
    
    funcoes_criadas = 0
    for user in usuarios_sem_funcao:
        # Verificar se já existe uma função inativa
        funcao_existente = UsuarioFuncao.objects.filter(
            usuario=user,
            cargo_funcao=cargo_usuario
        ).first()
        
        if funcao_existente:
            # Ativar função existente
            funcao_existente.status = 'ATIVO'
            funcao_existente.data_inicio = date.today()
            funcao_existente.save()
            print(f"   ✅ Ativada função para: {user.username}")
        else:
            # Criar nova função
            UsuarioFuncao.objects.create(
                usuario=user,
                cargo_funcao=cargo_usuario,
                status='ATIVO',
                data_inicio=date.today()
            )
            print(f"   ✅ Criada função para: {user.username}")
        
        funcoes_criadas += 1
        
        # Mostrar progresso a cada 50 usuários
        if funcoes_criadas % 50 == 0:
            print(f"   Progresso: {funcoes_criadas}/{usuarios_sem_funcao.count()}")
    
    print(f"\n✅ Concluído! {funcoes_criadas} funções atribuídas.")
    
    # 4. Verificar resultado final
    print(f"\n=== VERIFICAÇÃO FINAL ===")
    usuarios_com_funcao_final = set(UsuarioFuncao.objects.filter(status='ATIVO').values_list('usuario_id', flat=True))
    usuarios_sem_funcao_final = User.objects.exclude(id__in=usuarios_com_funcao_final).exclude(username='admin')
    
    print(f"Usuários sem funções após atribuição: {usuarios_sem_funcao_final.count()}")
    
    # 5. Mostrar resumo das funções
    print(f"\nResumo das funções:")
    funcoes_ativas = UsuarioFuncao.objects.filter(status='ATIVO').select_related('cargo_funcao')
    from collections import Counter
    contador_funcoes = Counter(uf.cargo_funcao.nome for uf in funcoes_ativas)
    
    for funcao, quantidade in contador_funcoes.most_common():
        print(f"   • {funcao}: {quantidade} usuários")
    
    print("\n=== ATRIBUIÇÃO CONCLUÍDA ===")

if __name__ == '__main__':
    atribuir_funcoes_usuarios() 