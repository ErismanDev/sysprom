#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, ComissaoPromocao, UsuarioFuncao

def testar_comissoes_erisman():
    print("=== TESTE DE COMISSÕES DO ERISMAN ===\n")
    
    # Buscar usuário ERISMAN
    try:
        user = User.objects.get(username='49008382334')
        print(f"✅ Usuário: {user.username} - {user.get_full_name()}")
    except User.DoesNotExist:
        print("❌ Usuário ERISMAN não encontrado")
        return
    
    # Verificar funções especiais
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    funcoes_ativas = user.funcoes.filter(
        cargo_funcao__nome__in=cargos_especiais,
        status='ATIVO',
    )
    print(f"Funções especiais: {funcoes_ativas.count()}")
    for f in funcoes_ativas:
        print(f"   • {f.cargo_funcao.nome}")
    
    # Verificar se tem acesso total
    tem_acesso_total = funcoes_ativas.exists() or user.is_superuser or user.is_staff
    print(f"Tem acesso total: {tem_acesso_total}")
    
    # Verificar membros de comissão
    membros_comissao = MembroComissao.objects.filter(
        usuario=user,
        ativo=True
    )
    print(f"Membros de comissão: {membros_comissao.count()}")
    for m in membros_comissao:
        print(f"   • {m.comissao.nome} ({m.comissao.tipo}) - Status: {m.comissao.status}")
    
    # Simular a lógica da view
    if tem_acesso_total:
        comissoes = ComissaoPromocao.objects.all()
        print(f"✅ Verá TODAS as comissões: {comissoes.count()}")
    else:
        if membros_comissao.exists():
            tem_cpo = membros_comissao.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros_comissao.filter(comissao__tipo='CPP').exists()
            
            if tem_cpo and tem_cpp:
                comissoes = ComissaoPromocao.objects.all()
                print(f"✅ Verá TODAS as comissões (membro de CPO e CPP): {comissoes.count()}")
            elif tem_cpo:
                comissoes = ComissaoPromocao.objects.filter(tipo='CPO')
                print(f"✅ Verá apenas comissões CPO: {comissoes.count()}")
            elif tem_cpp:
                comissoes = ComissaoPromocao.objects.filter(tipo='CPP')
                print(f"✅ Verá apenas comissões CPP: {comissoes.count()}")
            else:
                comissoes = ComissaoPromocao.objects.none()
                print("❌ Não verá nenhuma comissão")
        else:
            comissoes = ComissaoPromocao.objects.none()
            print("❌ Não verá nenhuma comissão (não é membro)")
    
    # Mostrar comissões que verá
    if comissoes.exists():
        print("\nComissões que verá:")
        for c in comissoes:
            print(f"   • {c.nome} ({c.tipo}) - Status: {c.status}")
    else:
        print("\n❌ Não verá nenhuma comissão")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == '__main__':
    testar_comissoes_erisman() 