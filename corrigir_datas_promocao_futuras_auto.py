#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def corrigir_datas_promocao_futuras_auto():
    """
    Identifica e corrige automaticamente militares com datas de promoção no futuro
    """
    print("=== CORREÇÃO AUTOMÁTICA DE DATAS DE PROMOÇÃO NO FUTURO ===\n")
    
    hoje = date.today()
    
    # 1. Identificar militares com data de promoção no futuro
    militares_futuro = Militar.objects.filter(
        data_promocao_atual__gt=hoje
    ).order_by('data_promocao_atual')
    
    print(f"1. MILITARES COM DATA DE PROMOÇÃO NO FUTURO:")
    print("-" * 60)
    print(f"Total encontrado: {militares_futuro.count()}")
    
    if militares_futuro.exists():
        print("\nDetalhes dos militares:")
        for militar in militares_futuro:
            tempo_atual = militar.tempo_posto_atual()
            print(f"  - {militar.nome_completo} ({militar.posto_graduacao})")
            print(f"    Data de promoção: {militar.data_promocao_atual}")
            print(f"    Tempo no posto (calculado): {tempo_atual} anos")
            print()
        
        # 2. Corrigir automaticamente
        print("2. CORRIGINDO DATAS DE PROMOÇÃO...")
        print("-" * 40)
        
        militares_corrigidos = 0
        for militar in militares_futuro:
            data_anterior = militar.data_promocao_atual
            militar.data_promocao_atual = hoje
            militar.save(update_fields=['data_promocao_atual'])
            
            print(f"  ✅ {militar.nome_completo}: {data_anterior} -> {hoje}")
            militares_corrigidos += 1
        
        print(f"\n✅ {militares_corrigidos} militares corrigidos com sucesso!")
        
        # 3. Verificar se há fichas de conceito que precisam ser atualizadas
        print("\n3. VERIFICANDO FICHAS DE CONCEITO...")
        print("-" * 40)
        
        fichas_atualizadas = 0
        for militar in militares_futuro:
            # Verificar fichas de oficiais
            try:
                ficha_oficiais = militar.fichaconceitooficiais
                tempo_anterior = ficha_oficiais.tempo_posto
                ficha_oficiais.save()  # Isso recalcula o tempo_posto
                tempo_novo = ficha_oficiais.tempo_posto
                if tempo_anterior != tempo_novo:
                    print(f"  ✅ Ficha de oficiais atualizada: {militar.nome_completo}")
                    fichas_atualizadas += 1
            except:
                pass
            
            # Verificar fichas de praças
            try:
                ficha_pracas = militar.fichaconceitopracas
                tempo_anterior = ficha_pracas.tempo_posto
                ficha_pracas.save()  # Isso recalcula o tempo_posto
                tempo_novo = ficha_pracas.tempo_posto
                if tempo_anterior != tempo_novo:
                    print(f"  ✅ Ficha de praças atualizada: {militar.nome_completo}")
                    fichas_atualizadas += 1
            except:
                pass
        
        if fichas_atualizadas > 0:
            print(f"\n✅ {fichas_atualizadas} fichas de conceito atualizadas!")
        else:
            print("\nℹ️ Nenhuma ficha de conceito precisou ser atualizada.")
    else:
        print("✅ Nenhum militar com data de promoção no futuro encontrado!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    corrigir_datas_promocao_futuras_auto() 