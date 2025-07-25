#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from datetime import date

def diagnosticar_quadro_pracas():
    print("=== DIAGNÓSTICO QUADROS DE PRACAS ===\n")
    
    # 1. Verificar se existem militares com quadro PRACAS
    pracas = Militar.objects.filter(quadro='PRACAS')
    print(f"1. Total de militares com quadro 'PRACAS': {pracas.count()}")
    
    if pracas.count() == 0:
        print("   ❌ NENHUM militar com quadro 'PRACAS' encontrado!")
        print("   Isso explica por que o quadro não está sendo gerado.")
        print("\n   Verificando todos os quadros disponíveis:")
        quadros = Militar.objects.values_list('quadro', flat=True).distinct()
        for quadro in quadros:
            count = Militar.objects.filter(quadro=quadro).count()
            print(f"   - {quadro}: {count} militares")
        return
    
    print("   ✅ Militares praças encontrados!")
    
    # 2. Listar alguns militares praças para análise
    print(f"\n2. Primeiros 5 militares praças:")
    for i, militar in enumerate(pracas[:5]):
        print(f"   {i+1}. {militar.nome_completo} - Posto: {militar.get_posto_graduacao_display()} - Ingresso: {militar.data_ingresso}")
    
    # 3. Verificar se existem quadros de acesso para praças
    quadros_pracas = QuadroAcesso.objects.filter(tipo='PRACAS')
    print(f"\n3. Quadros de acesso para praças existentes: {quadros_pracas.count()}")
    
    if quadros_pracas.exists():
        print("   Quadros encontrados:")
        for quadro in quadros_pracas:
            print(f"   - {quadro} (ID: {quadro.id})")
    
    # 4. Tentar gerar um quadro de acesso para praças
    print(f"\n4. Tentando gerar quadro de acesso para praças...")
    
    # Definir próxima data de promoção (ajuste conforme sua regra)
    hoje = date.today()
    ano = hoje.year
    datas_promocao = [date(ano, 7, 18), date(ano, 12, 25)]
    datas_futuras = [d for d in datas_promocao if d >= hoje]
    if not datas_futuras:
        data_promocao = date(ano+1, 7, 18)
    else:
        data_promocao = datas_futuras[0]

    print(f"\n=== GERANDO QUADRO DE ACESSO PARA PRACAS EM {data_promocao} ===")
    quadro_existente = QuadroAcesso.objects.filter(tipo='ANTIGUIDADE', data_promocao=data_promocao).first()
    if quadro_existente:
        print(f"Já existe um quadro de acesso para praças na data {data_promocao}: ID {quadro_existente.id}")
    else:
        quadro = QuadroAcesso(tipo='ANTIGUIDADE', data_promocao=data_promocao)
        quadro.save()
        ok, msg = quadro.gerar_quadro_completo()
        print(f"Quadro gerado: {ok}. Mensagem: {msg}")
        
        if ok:
            print(f"\n5. VERIFICANDO ITENS DO QUADRO:")
            print("-" * 50)
            
            itens = quadro.itemquadroacesso_set.all().order_by('posicao')
            
            if itens.exists():
                print(f"Total de itens: {itens.count()}")
                
                # Verificar se há praças no quadro
                itens_pracas = itens.filter(
                    militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
                )
                print(f"Itens de praças: {itens_pracas.count()}")
                
                if itens_pracas.exists():
                    print(f"\n  Praças no quadro:")
                    for item in itens_pracas[:10]:
                        m = item.militar
                        print(f"    {item.posicao}. {m.nome_completo} ({m.posto_graduacao}) - Pontuação: {item.pontuacao}")
                else:
                    print("❌ NENHUMA PRAÇA FOI INCLUÍDA NO QUADRO!")
                    
                    # Verificar quais postos foram incluídos
                    postos_incluidos = itens.values_list('militar__posto_graduacao', flat=True).distinct()
                    print(f"Postos incluídos no quadro: {list(postos_incluidos)}")
            else:
                print("❌ NENHUM ITEM FOI CRIADO NO QUADRO!")
        else:
            print(f"❌ QUADRO NÃO FOI ELABORADO: {msg}")

if __name__ == "__main__":
    diagnosticar_quadro_pracas() 