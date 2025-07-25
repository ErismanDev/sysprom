#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import QuadroAcesso, MembroComissao, UsuarioFuncao, CargoFuncao

def testar_permissoes_quadro_acesso():
    """Testa as permissões para quadros de acesso"""
    
    # Verificar se existem quadros de acesso
    total_quadros = QuadroAcesso.objects.count()
    print(f"Total de quadros de acesso no banco: {total_quadros}")
    
    if total_quadros > 0:
        print("Quadros encontrados:")
        for quadro in QuadroAcesso.objects.all()[:5]:  # Mostrar apenas os 5 primeiros
            print(f"  - {quadro}")
    
    # Verificar usuários
    usuarios = User.objects.all()
    print(f"\nTotal de usuários: {usuarios.count()}")
    
    for usuario in usuarios:
        print(f"\n=== Usuário: {usuario.username} ===")
        print(f"  is_superuser: {usuario.is_superuser}")
        print(f"  is_staff: {usuario.is_staff}")
        print(f"  is_active: {usuario.is_active}")
        
        # Verificar funções
        funcoes = UsuarioFuncao.objects.filter(usuario=usuario, status='ATIVO')
        print(f"  Funções ativas: {funcoes.count()}")
        for funcao in funcoes:
            print(f"    - {funcao.cargo_funcao.nome}")
        
        # Verificar membros de comissão
        membros_comissao = MembroComissao.objects.filter(
            usuario=usuario,
            ativo=True
        )
        print(f"  Membro de comissões ativas: {membros_comissao.count()}")
        for membro in membros_comissao:
            print(f"    - {membro.comissao.tipo} - {membro.comissao.status}")
        
        # Testar lógica de permissão
        cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções']
        funcoes_ativas = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
        
        if usuario.is_superuser or usuario.is_staff:
            print("  ✅ Acesso total (superusuário/staff)")
        elif funcoes_ativas.exists():
            print("  ✅ Acesso total (função especial)")
        elif membros_comissao.exists():
            tem_cpo = membros_comissao.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros_comissao.filter(comissao__tipo='CPP').exists()
            if tem_cpo and tem_cpp:
                print("  ✅ Acesso total (membro CPO e CPP)")
            elif tem_cpo:
                print("  ✅ Acesso parcial (membro CPO - apenas oficiais)")
            elif tem_cpp:
                print("  ✅ Acesso parcial (membro CPP - apenas praças)")
            else:
                print("  ❌ Sem acesso (membro de comissão sem CPO/CPP)")
        else:
            print("  ❌ Sem acesso (sem funções especiais ou comissões)")

if __name__ == '__main__':
    testar_permissoes_quadro_acesso() 