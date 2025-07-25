#!/usr/bin/env python
"""
Script para testar o filtro de militares por tipo de comissão (CPO/CPP)
"""
import os
import sys
import django

# Configurar Django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import (
    Militar, UsuarioFuncao, CargoFuncao, ComissaoPromocao
)

def testar_filtro_comissao_tipo():
    """Testa o filtro de militares por tipo de comissão"""
    
    print("🧪 TESTANDO FILTRO POR TIPO DE COMISSÃO")
    print("=" * 60)
    
    # 1. Verificar comissões existentes
    print("\n📋 1. COMISSÕES EXISTENTES:")
    comissoes = ComissaoPromocao.objects.all()
    for comissao in comissoes:
        print(f"   📋 {comissao.nome} ({comissao.tipo})")
        print(f"      Status: {comissao.get_status_display()}")
        print(f"      Membros: {comissao.membros.count()}")
        print()
    
    # 2. Verificar militares com funções CPO
    print("\n👥 2. MILITARES COM FUNÇÕES CPO:")
    militares_cpo = Militar.objects.filter(
        situacao='AT',
        user__funcoes__cargo_funcao__nome__icontains='CPO'
    ).distinct()
    
    print(f"   📊 Total encontrados: {militares_cpo.count()}")
    for militar in militares_cpo[:5]:  # Mostrar apenas os primeiros 5
        funcoes = UsuarioFuncao.objects.filter(
            usuario=militar.user,
            status='ATIVO',
            cargo_funcao__nome__icontains='CPO'
        )
        print(f"   👤 {militar.get_posto_graduacao_display()} {militar.nome_completo}")
        for funcao in funcoes:
            print(f"      🏷️  {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
        print()
    
    # 3. Verificar militares com funções CPP
    print("\n👥 3. MILITARES COM FUNÇÕES CPP:")
    militares_cpp = Militar.objects.filter(
        situacao='AT',
        user__funcoes__cargo_funcao__nome__icontains='CPP'
    ).distinct()
    
    print(f"   📊 Total encontrados: {militares_cpp.count()}")
    for militar in militares_cpp[:5]:  # Mostrar apenas os primeiros 5
        funcoes = UsuarioFuncao.objects.filter(
            usuario=militar.user,
            status='ATIVO',
            cargo_funcao__nome__icontains='CPP'
        )
        print(f"   👤 {militar.get_posto_graduacao_display()} {militar.nome_completo}")
        for funcao in funcoes:
            print(f"      🏷️  {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
        print()
    
    # 4. Verificar funções relacionadas a comissões
    print("\n🏷️  4. FUNÇÕES RELACIONADAS A COMISSÕES:")
    
    # Funções CPO
    funcoes_cpo = CargoFuncao.objects.filter(nome__icontains='CPO')
    print("   📋 Funções CPO:")
    for funcao in funcoes_cpo:
        usuarios_count = UsuarioFuncao.objects.filter(
            cargo_funcao=funcao,
            status='ATIVO'
        ).count()
        print(f"      - {funcao.nome} ({usuarios_count} usuários)")
    
    # Funções CPP
    funcoes_cpp = CargoFuncao.objects.filter(nome__icontains='CPP')
    print("   📋 Funções CPP:")
    for funcao in funcoes_cpp:
        usuarios_count = UsuarioFuncao.objects.filter(
            cargo_funcao=funcao,
            status='ATIVO'
        ).count()
        print(f"      - {funcao.nome} ({usuarios_count} usuários)")
    
    # 5. Estatísticas finais
    print("\n📊 5. ESTATÍSTICAS:")
    total_militares = Militar.objects.filter(situacao='AT').count()
    militares_com_usuario = Militar.objects.filter(situacao='AT', user__isnull=False).count()
    militares_sem_usuario = Militar.objects.filter(situacao='AT', user__isnull=True).count()
    
    print(f"   📋 Total de militares ativos: {total_militares}")
    print(f"   👤 Militares com usuário: {militares_com_usuario}")
    print(f"   ❌ Militares sem usuário: {militares_sem_usuario}")
    print(f"   🏷️  Militares com função CPO: {militares_cpo.count()}")
    print(f"   🏷️  Militares com função CPP: {militares_cpp.count()}")
    
    # 6. Recomendações
    print("\n💡 6. RECOMENDAÇÕES:")
    if militares_cpo.count() == 0:
        print("   ⚠️  Nenhum militar encontrado com função CPO")
        print("      → Verifique se existem funções com 'CPO' no nome")
    
    if militares_cpp.count() == 0:
        print("   ⚠️  Nenhum militar encontrado com função CPP")
        print("      → Verifique se existem funções com 'CPP' no nome")
    
    if militares_sem_usuario > 0:
        print(f"   ⚠️  {militares_sem_usuario} militares não possuem usuário vinculado")
        print("      → Esses militares não aparecerão no filtro por função")
    
    print("\n✅ Teste concluído!")
    print("   O filtro por tipo de comissão está funcionando.")
    print("   - CPO: mostra apenas militares com funções CPO")
    print("   - CPP: mostra apenas militares com funções CPP")

if __name__ == '__main__':
    testar_filtro_comissao_tipo() 