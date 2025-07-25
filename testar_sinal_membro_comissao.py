#!/usr/bin/env python
"""
Script para testar o sinal de atualização automática do campo ativo do MembroComissao
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, MembroComissao, ComissaoPromocao

def testar_sinal_membro_comissao():
    """Testa o sinal de atualização automática do campo ativo do MembroComissao"""
    
    print("=== TESTE DO SINAL DE ATUALIZAÇÃO DE MEMBRO DE COMISSÃO ===\n")
    
    # 1. Verificar militares que são membros de comissão
    print("1. 📊 MILITARES MEMBROS DE COMISSÃO:")
    membros_comissao = MembroComissao.objects.select_related('militar', 'comissao').all()
    
    if membros_comissao.exists():
        for membro in membros_comissao:
            print(f"   - {membro.militar.nome_completo} ({membro.militar.get_situacao_display()}) - {membro.comissao.nome} - Ativo: {membro.ativo}")
    else:
        print("   Nenhum membro de comissão encontrado.")
    
    print()
    
    # 2. Verificar militares ativos que são membros de comissão
    print("2. 📊 MILITARES ATIVOS MEMBROS DE COMISSÃO:")
    membros_ativos = MembroComissao.objects.filter(
        militar__situacao='AT',
        ativo=True
    ).select_related('militar', 'comissao')
    
    if membros_ativos.exists():
        for membro in membros_ativos:
            print(f"   - {membro.militar.nome_completo} - {membro.comissao.nome}")
    else:
        print("   Nenhum militar ativo membro de comissão encontrado.")
    
    print()
    
    # 3. Verificar militares inativos que são membros de comissão
    print("3. 📊 MILITARES INATIVOS MEMBROS DE COMISSÃO:")
    membros_inativos = MembroComissao.objects.filter(
        militar__situacao__in=['IN', 'TR', 'AP', 'EX']
    ).select_related('militar', 'comissao')
    
    if membros_inativos.exists():
        for membro in membros_inativos:
            print(f"   - {membro.militar.nome_completo} ({membro.militar.get_situacao_display()}) - {membro.comissao.nome} - Ativo: {membro.ativo}")
    else:
        print("   Nenhum militar inativo membro de comissão encontrado.")
    
    print()
    
    # 4. Verificar inconsistências
    print("4. 🔍 VERIFICANDO INCONSISTÊNCIAS:")
    
    # Militares inativos com membros de comissão ativos
    membros_inconsistentes = MembroComissao.objects.filter(
        militar__situacao__in=['IN', 'TR', 'AP', 'EX'],
        ativo=True
    )
    
    if membros_inconsistentes.exists():
        print(f"   ❌ ENCONTRADOS {membros_inconsistentes.count()} MEMBROS INCONSISTENTES:")
        for membro in membros_inconsistentes:
            print(f"      - {membro.militar.nome_completo} ({membro.militar.get_situacao_display()}) - {membro.comissao.nome}")
    else:
        print("   ✅ Nenhuma inconsistência encontrada!")
    
    print()
    
    # 5. Estatísticas finais
    print("5. 📈 ESTATÍSTICAS FINAIS:")
    total_membros = MembroComissao.objects.count()
    membros_ativos_count = MembroComissao.objects.filter(ativo=True).count()
    membros_inativos_count = MembroComissao.objects.filter(ativo=False).count()
    
    print(f"   Total de membros de comissão: {total_membros}")
    print(f"   Membros ativos: {membros_ativos_count}")
    print(f"   Membros inativos: {membros_inativos_count}")
    
    if total_membros > 0:
        percentual_ativos = (membros_ativos_count / total_membros) * 100
        print(f"   Percentual de ativos: {percentual_ativos:.1f}%")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    testar_sinal_membro_comissao() 