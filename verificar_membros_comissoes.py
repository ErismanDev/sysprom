#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, Militar, UsuarioFuncao, ComissaoPromocao

def verificar_membros_comissoes():
    print("=== VERIFICANDO MEMBROS DE COMISSÕES E SUAS FUNÇÕES ===\n")
    
    # Buscar todos os membros de comissões
    membros = MembroComissao.objects.filter(ativo=True).select_related(
        'usuario', 'militar', 'comissao'
    )
    
    print(f"Total de membros de comissões ativos: {membros.count()}")
    
    if membros.count() == 0:
        print("❌ Nenhum membro de comissão encontrado!")
        return
    
    print("\n=== DETALHES DOS MEMBROS ===")
    
    for membro in membros:
        print(f"\n--- Membro: {membro.usuario.username} ---")
        print(f"   Militar: {membro.militar.nome_guerra} ({membro.militar.cpf})")
        print(f"   Comissão: {membro.comissao.nome} ({membro.comissao.tipo})")
        print(f"   Status da comissão: {membro.comissao.status}")
        
        # Verificar funções do usuário
        funcoes_usuario = UsuarioFuncao.objects.filter(
            usuario=membro.usuario,
            status='ATIVO'
        ).select_related('cargo_funcao')
        
        print(f"   Funções do usuário: {funcoes_usuario.count()}")
        
        if funcoes_usuario.exists():
            for funcao in funcoes_usuario:
                print(f"     • {funcao.cargo_funcao.nome}")
        else:
            print("     ❌ NENHUMA FUNÇÃO ATIVA!")
        
        # Simular a lógica da view comissao_list
        cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
        funcoes_ativas = funcoes_usuario.filter(cargo_funcao__nome__in=cargos_especiais)
        
        if funcoes_ativas.exists() or membro.usuario.is_superuser or membro.usuario.is_staff:
            print("     ✅ ACESSO TOTAL (função especial ou superuser)")
        else:
            # Verificar se é membro de comissão
            membros_comissao = MembroComissao.objects.filter(
                usuario=membro.usuario,
                ativo=True
            )
            
            if membros_comissao.exists():
                tem_cpo = membros_comissao.filter(comissao__tipo='CPO').exists()
                tem_cpp = membros_comissao.filter(comissao__tipo='CPP').exists()
                
                if tem_cpo and tem_cpp:
                    print("     ✅ ACESSO TOTAL (membro CPO e CPP)")
                elif tem_cpo:
                    print("     ✅ ACESSO CPO (membro CPO)")
                elif tem_cpp:
                    print("     ✅ ACESSO CPP (membro CPP)")
                else:
                    print("     ❌ SEM ACESSO (não é membro de comissão)")
            else:
                print("     ❌ SEM ACESSO (não é membro de comissão)")
    
    print("\n=== RESUMO ===")
    
    # Contar usuários sem funções
    usuarios_sem_funcoes = []
    for membro in membros:
        if not UsuarioFuncao.objects.filter(usuario=membro.usuario, status='ATIVO').exists():
            usuarios_sem_funcoes.append(membro.usuario.username)
    
    print(f"Usuários membros de comissões SEM funções: {len(usuarios_sem_funcoes)}")
    if usuarios_sem_funcoes:
        print("Usuários sem funções:")
        for username in usuarios_sem_funcoes[:10]:  # Mostrar apenas os primeiros 10
            print(f"  • {username}")
        if len(usuarios_sem_funcoes) > 10:
            print(f"  ... e mais {len(usuarios_sem_funcoes) - 10} usuários")

if __name__ == '__main__':
    verificar_membros_comissoes() 