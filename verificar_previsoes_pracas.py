#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import PrevisaoVaga, Militar, POSTO_GRADUACAO_CHOICES

def verificar_previsoes_pracas():
    print("=== VERIFICANDO PREVISÕES DE VAGAS PARA PRAÇAS ===\n")
    
    # 1. Verificar previsões existentes para praças
    print("1. PREVISÕES DE VAGAS PARA PRAÇAS:")
    print("-" * 50)
    
    previsoes_pracas = PrevisaoVaga.objects.filter(
        quadro='PRACAS',
        posto__in=['ST', '1S', '2S', '3S', 'CAB', 'SD'],
        ativo=True
    ).order_by('posto')
    
    print(f"Total de previsões para praças: {previsoes_pracas.count()}")
    
    for previsao in previsoes_pracas:
        print(f"- {previsao.get_posto_display()}: {previsao.vagas_disponiveis} vagas disponíveis")
    
    # 2. Verificar militares praças no sistema
    print("\n2. MILITARES PRAÇAS NO SISTEMA:")
    print("-" * 50)
    
    militares_pracas = Militar.objects.filter(
        posto_graduacao__in=['ST', '1S', '2S', '3S', 'CAB', 'SD'],
        situacao='AT'
    ).order_by('posto_graduacao', 'nome_completo')
    
    print(f"Total de militares praças ativos: {militares_pracas.count()}")
    
    # Agrupar por posto
    por_posto = {}
    for militar in militares_pracas:
        posto = militar.posto_graduacao
        if posto not in por_posto:
            por_posto[posto] = []
        por_posto[posto].append(militar)
    
    for posto in ['ST', '1S', '2S', '3S', 'CAB', 'SD']:
        count = len(por_posto.get(posto, []))
        posto_display = dict(POSTO_GRADUACAO_CHOICES).get(posto, posto)
        print(f"- {posto_display}: {count} militares")
    
    # 3. Verificar se há previsões para todos os postos
    print("\n3. VERIFICAÇÃO DE COBERTURA:")
    print("-" * 50)
    
    postos_com_previsao = set(previsoes_pracas.values_list('posto', flat=True))
    postos_com_militares = set(por_posto.keys())
    
    print(f"Postos com previsão: {sorted(postos_com_previsao)}")
    print(f"Postos com militares: {sorted(postos_com_militares)}")
    
    postos_sem_previsao = postos_com_militares - postos_com_previsao
    if postos_sem_previsao:
        print(f"⚠️  POSTOS SEM PREVISÃO: {sorted(postos_sem_previsao)}")
    else:
        print("✅ Todos os postos com militares têm previsão")
    
    # 4. Sugestões
    print("\n4. SUGESTÕES:")
    print("-" * 50)
    
    if previsoes_pracas.count() == 0:
        print("❌ Nenhuma previsão de vaga para praças encontrada!")
        print("   Crie previsões de vagas para os postos de praças no admin.")
    elif previsoes_pracas.count() < len(postos_com_militares):
        print("⚠️  Alguns postos não têm previsão de vagas.")
        print("   Crie previsões para os postos faltantes.")
    else:
        print("✅ Sistema configurado corretamente para praças.")

if __name__ == '__main__':
    verificar_previsoes_pracas() 