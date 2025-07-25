#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, Militar, UsuarioFuncao, ComissaoPromocao

def verificar_todas_comissoes():
    print("=== VERIFICANDO TODAS AS COMISSÕES E MEMBROS ===\n")
    
    # Buscar todas as comissões
    comissoes = ComissaoPromocao.objects.all()
    print(f"Total de comissões: {comissoes.count()}")
    
    if comissoes.count() == 0:
        print("❌ Nenhuma comissão encontrada!")
        return
    
    print("\n=== DETALHES DAS COMISSÕES ===")
    
    for comissao in comissoes:
        print(f"\n--- Comissão: {comissao.nome} ---")
        print(f"   Tipo: {comissao.tipo}")
        print(f"   Status: {comissao.status}")
        
        # Buscar todos os membros desta comissão (ativos e inativos)
        membros = MembroComissao.objects.filter(comissao=comissao).select_related(
            'usuario', 'militar'
        )
        
        print(f"   Total de membros: {membros.count()}")
        
        membros_ativos = membros.filter(ativo=True)
        membros_inativos = membros.filter(ativo=False)
        
        print(f"   Membros ativos: {membros_ativos.count()}")
        print(f"   Membros inativos: {membros_inativos.count()}")
        
        if membros.exists():
            print("   Detalhes dos membros:")
            for membro in membros:
                status_membro = "✅ ATIVO" if membro.ativo else "❌ INATIVO"
                print(f"     • {membro.usuario.username} - {membro.militar.nome_guerra} ({status_membro})")
                
                # Verificar funções do usuário
                funcoes = UsuarioFuncao.objects.filter(
                    usuario=membro.usuario,
                    status='ATIVO'
                ).select_related('cargo_funcao')
                
                if funcoes.exists():
                    funcoes_nomes = [f.cargo_funcao.nome for f in funcoes]
                    print(f"       Funções: {', '.join(funcoes_nomes)}")
                else:
                    print(f"       ❌ SEM FUNÇÕES ATIVAS!")
        else:
            print("   ❌ NENHUM MEMBRO CADASTRADO!")
    
    print("\n=== RESUMO GERAL ===")
    
    # Estatísticas gerais
    total_membros = MembroComissao.objects.count()
    total_membros_ativos = MembroComissao.objects.filter(ativo=True).count()
    total_membros_inativos = MembroComissao.objects.filter(ativo=False).count()
    
    print(f"Total de membros de comissões: {total_membros}")
    print(f"Membros ativos: {total_membros_ativos}")
    print(f"Membros inativos: {total_membros_inativos}")
    
    # Verificar usuários únicos que são membros
    usuarios_membros = set(MembroComissao.objects.values_list('usuario_id', flat=True))
    print(f"Usuários únicos que são membros: {len(usuarios_membros)}")
    
    # Verificar quantos desses usuários têm funções
    usuarios_com_funcoes = 0
    usuarios_sem_funcoes = 0
    
    for usuario_id in usuarios_membros:
        if UsuarioFuncao.objects.filter(usuario_id=usuario_id, status='ATIVO').exists():
            usuarios_com_funcoes += 1
        else:
            usuarios_sem_funcoes += 1
    
    print(f"Usuários membros COM funções: {usuarios_com_funcoes}")
    print(f"Usuários membros SEM funções: {usuarios_sem_funcoes}")

if __name__ == '__main__':
    verificar_todas_comissoes() 