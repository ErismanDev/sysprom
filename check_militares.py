#!/usr/bin/env python
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from django.utils import timezone

def check_militares():
    print("=== VERIFICAÇÃO DE MILITARES ===")
    
    # Total de militares
    total_militares = Militar.objects.count()
    print(f"Total de militares: {total_militares}")
    
    # Oficiais ativos
    oficiais_ativos = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    )
    print(f"Oficiais ativos: {oficiais_ativos.count()}")
    
    # Oficiais aptos em saúde
    oficiais_aptos = Militar.objects.filter(
        situacao='AT',
        apto_inspecao_saude=True,
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    )
    print(f"Oficiais aptos em saúde: {oficiais_aptos.count()}")
    
    # Verificar quadro específico
    try:
        quadro = QuadroAcesso.objects.get(pk=278)
        print(f"\n=== QUADRO 278 ===")
        print(f"Tipo: {quadro.tipo}")
        print(f"Status: {quadro.status}")
        print(f"Data promoção: {quadro.data_promocao}")
        
        # Militares no quadro
        militares_no_quadro = quadro.itemquadroacesso_set.values_list('militar_id', flat=True)
        print(f"Militares no quadro: {len(militares_no_quadro)}")
        
        # Oficiais elegíveis para o quadro
        if quadro.tipo == 'MERECIMENTO':
            oficiais_elegiveis = Militar.objects.filter(
                situacao='AT',
                posto_graduacao__in=['CP', 'MJ', 'TC']
            ).exclude(id__in=militares_no_quadro)
        else:
            oficiais_elegiveis = Militar.objects.filter(
                situacao='AT',
                posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
            ).exclude(id__in=militares_no_quadro)
        
        print(f"Oficiais elegíveis (não no quadro): {oficiais_elegiveis.count()}")
        
        # Filtrar aptos
        oficiais_disponiveis = []
        for oficial in oficiais_elegiveis:
            apto = True
            
            if oficial.situacao != 'AT':
                apto = False
            elif not oficial.apto_inspecao_saude:
                apto = False
            elif oficial.data_validade_inspecao_saude and oficial.data_validade_inspecao_saude < timezone.now().date():
                apto = False
            
            if apto:
                oficiais_disponiveis.append(oficial)
        
        print(f"Oficiais disponíveis (aptos): {len(oficiais_disponiveis)}")
        
        # Mostrar alguns oficiais disponíveis
        if oficiais_disponiveis:
            print("\nPrimeiros 5 oficiais disponíveis:")
            for i, oficial in enumerate(oficiais_disponiveis[:5]):
                print(f"  {i+1}. {oficial.nome_completo} - {oficial.get_posto_graduacao_display()}")
        else:
            print("\nNenhum oficial disponível encontrado!")
            
    except QuadroAcesso.DoesNotExist:
        print("Quadro 266 não encontrado!")
    
    print("\n=== FIM DA VERIFICAÇÃO ===")

if __name__ == '__main__':
    try:
        with open('backups/backup_completo_20250724_130613.json', 'r', encoding='utf-16') as f:
            data = json.load(f)
        
        # Filtrar militares
        militares = [obj for obj in data if obj.get('model') == 'militares.militar']
        
        print(f"Militares no backup: {len(militares)}")
        
        if militares:
            print("\nPrimeiros 5 militares:")
            for i, m in enumerate(militares[:5]):
                fields = m['fields']
                print(f"  {i+1}. {fields.get('nome_completo', 'N/A')} - {fields.get('cpf', 'N/A')} - {fields.get('posto_graduacao', 'N/A')}")
        else:
            print("Nenhum militar encontrado no backup")
            
    except Exception as e:
        print(f"Erro: {e}") 