#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, Militar, UsuarioFuncao, ComissaoPromocao

def verificar_militares_comissoes():
    print("=== VERIFICANDO MILITARES E COMISSÕES ===\n")
    
    # Buscar todas as comissões
    comissoes = ComissaoPromocao.objects.all()
    print(f"Comissões disponíveis: {comissoes.count()}")
    
    for comissao in comissoes:
        print(f"  • {comissao.nome} ({comissao.tipo}) - {comissao.status}")
    
    print(f"\n=== MILITARES CADASTRADOS NO SISTEMA ===")
    
    # Buscar militares que têm usuários associados
    militares_com_usuarios = Militar.objects.filter(user__isnull=False).select_related('user')
    print(f"Militares com usuários: {militares_com_usuarios.count()}")
    
    # Verificar quais militares são membros de comissões
    militares_membros = set(MembroComissao.objects.values_list('militar_id', flat=True))
    print(f"Militares que são membros de comissões: {len(militares_membros)}")
    
    print(f"\n=== MILITARES QUE NÃO SÃO MEMBROS DE COMISSÕES ===")
    
    militares_nao_membros = militares_com_usuarios.exclude(id__in=militares_membros)
    print(f"Militares que NÃO são membros: {militares_nao_membros.count()}")
    
    if militares_nao_membros.count() > 0:
        print("\nPrimeiros 10 militares que não são membros:")
        for militar in militares_nao_membros[:10]:
            print(f"  • {militar.nome_guerra} ({militar.cpf}) - Usuário: {militar.user.username}")
            
            # Verificar funções do usuário
            funcoes = UsuarioFuncao.objects.filter(
                usuario=militar.user,
                status='ATIVO'
            ).select_related('cargo_funcao')
            
            if funcoes.exists():
                funcoes_nomes = [f.cargo_funcao.nome for f in funcoes]
                print(f"    Funções: {', '.join(funcoes_nomes)}")
            else:
                print(f"    ❌ SEM FUNÇÕES ATIVAS!")
    
    print(f"\n=== MILITARES QUE SÃO MEMBROS DE COMISSÕES ===")
    
    militares_membros_objs = militares_com_usuarios.filter(id__in=militares_membros)
    print(f"Militares que SÃO membros: {militares_membros_objs.count()}")
    
    for militar in militares_membros_objs:
        print(f"  • {militar.nome_guerra} ({militar.cpf}) - Usuário: {militar.user.username}")
        
        # Verificar em quais comissões é membro
        membros_comissoes = MembroComissao.objects.filter(
            militar=militar
        ).select_related('comissao')
        
        for membro in membros_comissoes:
            status = "✅ ATIVO" if membro.ativo else "❌ INATIVO"
            print(f"    Membro de: {membro.comissao.nome} ({membro.comissao.tipo}) - {status}")
        
        # Verificar funções do usuário
        funcoes = UsuarioFuncao.objects.filter(
            usuario=militar.user,
            status='ATIVO'
        ).select_related('cargo_funcao')
        
        if funcoes.exists():
            funcoes_nomes = [f.cargo_funcao.nome for f in funcoes]
            print(f"    Funções: {', '.join(funcoes_nomes)}")
        else:
            print(f"    ❌ SEM FUNÇÕES ATIVAS!")

if __name__ == '__main__':
    verificar_militares_comissoes() 