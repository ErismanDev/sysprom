#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, ItemQuadroAcesso

print('=== ITENS DO QUADRO DE MERECIMENTO ===\n')

quadros_merecimento = QuadroAcesso.objects.filter(tipo='MERECIMENTO').order_by('-data_promocao')

if not quadros_merecimento.exists():
    print('❌ Nenhum quadro de merecimento encontrado!')
    exit()

for quadro in quadros_merecimento:
    print(f'Quadro ID: {quadro.id} | Data promoção: {quadro.data_promocao} | Status: {quadro.get_status_display()}')
    itens = ItemQuadroAcesso.objects.filter(quadro_acesso=quadro).order_by('posicao')
    if not itens.exists():
        print('  (Nenhum item encontrado neste quadro)')
    else:
        for item in itens:
            print(f'  Posição {item.posicao}: {item.militar.nome_completo} | Posto: {item.militar.posto_graduacao} | Quadro: {item.militar.quadro} | Pontuação: {item.pontuacao}')
    print()
print('=== FIM ===') 