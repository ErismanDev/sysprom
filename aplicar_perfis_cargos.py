#!/usr/bin/env python
"""
Script para aplicar perfis de acesso aos cargos que não têm permissões
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao, PerfilAcesso

def aplicar_perfis_cargos():
    """Aplica perfis de acesso aos cargos que não têm permissões"""
    
    print("🔧 APLICANDO PERFIS AOS CARGOS")
    print("=" * 50)
    
    # Obter cargos sem permissões
    cargos_sem_permissoes = []
    for cargo in CargoFuncao.objects.filter(ativo=True):
        if not PermissaoFuncao.objects.filter(cargo_funcao=cargo, ativo=True).exists():
            cargos_sem_permissoes.append(cargo)
    
    print(f"\n📋 CARGOS SEM PERMISSÕES: {len(cargos_sem_permissoes)}")
    for cargo in cargos_sem_permissoes:
        print(f"   - {cargo.nome}")
    
    # Obter perfis disponíveis
    perfis = PerfilAcesso.objects.filter(ativo=True)
    print(f"\n👥 PERFIS DISPONÍVEIS:")
    for perfil in perfis:
        print(f"   - {perfil.nome}: {perfil.permissoes.count()} permissões")
    
    # Mapeamento de cargos para perfis baseado no nome
    mapeamento = {
        'Administrador do Sistema': 'Administrador',
        'Gestor de Promoções': 'Gestor',
        'Presidente da CPP': 'Membro de Comissão',
        'Vice-Presidente da CPP': 'Membro de Comissão',
        'Secretário da CPP': 'Membro de Comissão',
        'Membro Efetivo da CPP': 'Membro de Comissão',
        'Membro Nato da CPP': 'Membro de Comissão',
        'Suplente da CPP': 'Membro de Comissão',
        'Presidente da CPO': 'Membro de Comissão',
        'Vice-Presidente da CPO': 'Membro de Comissão',
        'Secretário da CPO': 'Membro de Comissão',
        'Membro Efetivo da CPO': 'Membro de Comissão',
        'Membro Nato da CPO': 'Membro de Comissão',
        'Suplente da CPO': 'Membro de Comissão',
        'Digitador': 'Operador',
        'Operador': 'Operador',
        'Consulta': 'Consulta',
        'Função Padrão': 'Consulta',  # Perfil básico para função padrão
    }
    
    print(f"\n🔗 APLICANDO PERFIS:")
    aplicacoes = 0
    
    for cargo in cargos_sem_permissoes:
        perfil_nome = mapeamento.get(cargo.nome, 'Consulta')  # Padrão é Consulta
        
        try:
            perfil = PerfilAcesso.objects.get(nome=perfil_nome)
            
            # Aplicar permissões do perfil ao cargo
            for permissao in perfil.permissoes.all():
                PermissaoFuncao.objects.create(
                    cargo_funcao=cargo,
                    modulo=permissao.modulo,
                    acesso=permissao.acesso,
                    ativo=True,
                    observacoes=f"Aplicado do perfil: {perfil.nome}"
                )
            
            print(f"   ✅ {cargo.nome} → {perfil.nome} ({perfil.permissoes.count()} permissões)")
            aplicacoes += 1
            
        except PerfilAcesso.DoesNotExist:
            print(f"   ❌ {cargo.nome} → Perfil '{perfil_nome}' não encontrado")
    
    print(f"\n📊 RESUMO:")
    print(f"   - Cargos processados: {len(cargos_sem_permissoes)}")
    print(f"   - Perfis aplicados: {aplicacoes}")
    print(f"   - Erros: {len(cargos_sem_permissoes) - aplicacoes}")
    
    # Verificar resultado final
    cargos_sem_permissoes_final = []
    for cargo in CargoFuncao.objects.filter(ativo=True):
        if not PermissaoFuncao.objects.filter(cargo_funcao=cargo, ativo=True).exists():
            cargos_sem_permissoes_final.append(cargo)
    
    if cargos_sem_permissoes_final:
        print(f"\n⚠️  CARGOS AINDA SEM PERMISSÕES: {len(cargos_sem_permissoes_final)}")
        for cargo in cargos_sem_permissoes_final:
            print(f"   - {cargo.nome}")
    else:
        print(f"\n✅ TODOS OS CARGOS AGORA TÊM PERMISSÕES!")
    
    print(f"\n🎉 PROCESSO CONCLUÍDO!")
    print(f"   Acesse: http://127.0.0.1:8000/militares/permissoes/")
    
    return True

if __name__ == '__main__':
    aplicar_perfis_cargos() 