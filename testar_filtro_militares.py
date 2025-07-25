#!/usr/bin/env python
"""
Script para testar a filtragem de militares ativos e inativos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_filtros():
    """Testa a filtragem de militares ativos e inativos"""
    
    print("=== TESTE DE FILTRAGEM DE MILITARES ===\n")
    
    # 1. Contadores gerais
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    militares_inativos = Militar.objects.filter(situacao__in=['IN', 'TR', 'AP', 'EX']).count()
    
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   Total de militares: {total_militares}")
    print(f"   Militares ativos: {militares_ativos}")
    print(f"   Militares inativos: {militares_inativos}")
    print(f"   Soma ativos + inativos: {militares_ativos + militares_inativos}")
    print()
    
    # 2. Verificar se há militares com outras situações
    outras_situacoes = Militar.objects.exclude(situacao__in=['AT', 'IN', 'TR', 'AP', 'EX'])
    if outras_situacoes.exists():
        print("⚠️  ATENÇÃO: Encontrados militares com situações não padrão:")
        for militar in outras_situacoes:
            print(f"   - {militar.nome_completo}: {militar.situacao}")
        print()
    
    # 3. Mostrar alguns exemplos de militares ativos
    print("👥 EXEMPLOS DE MILITARES ATIVOS:")
    ativos = Militar.objects.filter(situacao='AT')[:5]
    for militar in ativos:
        print(f"   - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - {militar.situacao}")
    print()
    
    # 4. Mostrar alguns exemplos de militares inativos
    print("👤 EXEMPLOS DE MILITARES INATIVOS:")
    inativos = Militar.objects.filter(situacao__in=['IN', 'TR', 'AP', 'EX'])[:5]
    for militar in inativos:
        print(f"   - {militar.nome_completo} ({militar.get_posto_graduacao_display()}) - {militar.get_situacao_display()}")
    print()
    
    # 5. Verificar se a filtragem está funcionando corretamente
    print("✅ VERIFICAÇÃO DA FILTRAGEM:")
    
    # Testar se militares ativos não aparecem na lista de inativos
    ativos_ids = set(Militar.objects.filter(situacao='AT').values_list('id', flat=True))
    inativos_ids = set(Militar.objects.filter(situacao__in=['IN', 'TR', 'AP', 'EX']).values_list('id', flat=True))
    
    intersecao = ativos_ids.intersection(inativos_ids)
    if intersecao:
        print(f"   ❌ ERRO: {len(intersecao)} militares aparecem tanto na lista de ativos quanto de inativos!")
        for militar_id in intersecao:
            militar = Militar.objects.get(id=militar_id)
            print(f"      - {militar.nome_completo} (ID: {militar_id})")
    else:
        print("   ✅ OK: Nenhum militar aparece simultaneamente nas listas de ativos e inativos")
    
    # 6. Verificar se todos os militares estão sendo contabilizados
    total_contabilizado = len(ativos_ids) + len(inativos_ids)
    if total_contabilizado == total_militares:
        print("   ✅ OK: Todos os militares estão sendo contabilizados corretamente")
    else:
        print(f"   ⚠️  ATENÇÃO: {total_militares - total_contabilizado} militares não estão sendo contabilizados")
    
    print()
    print("=== FIM DO TESTE ===")

if __name__ == "__main__":
    testar_filtros() 