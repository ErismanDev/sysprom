#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso

print('=== VERIFICAÇÃO DE QUADROS DE MERECIMENTO ===\n')

# Buscar todos os quadros de merecimento
quadros_merecimento = QuadroAcesso.objects.filter(tipo='MERECIMENTO').order_by('-data_promocao')

print(f'Total de quadros de merecimento: {quadros_merecimento.count()}\n')

if not quadros_merecimento.exists():
    print('❌ Nenhum quadro de merecimento encontrado!')
    
    # Verificar todos os quadros existentes
    todos_quadros = QuadroAcesso.objects.all().order_by('-data_promocao')
    print(f'\nTodos os quadros existentes ({todos_quadros.count()}):')
    for q in todos_quadros:
        print(f'  ID: {q.id} | Tipo: {q.get_tipo_display()} | Data: {q.data_promocao} | Status: {q.get_status_display()}')
else:
    for i, quadro in enumerate(quadros_merecimento, 1):
        print(f'--- QUADRO DE MERECIMENTO {i} ---')
        print(f'ID: {quadro.id}')
        print(f'Data de promoção: {quadro.data_promocao}')
        print(f'Status: {quadro.get_status_display()}')
        print(f'Ativo: {"Sim" if quadro.ativo else "Não"}')
        print(f'Data de criação: {quadro.data_criacao}')
        print(f'Data de atualização: {quadro.data_atualizacao}')
        
        # Verificar itens
        itens = quadro.itemquadroacesso_set.all()
        print(f'Total de itens: {itens.count()}')
        
        if itens.exists():
            print('Itens:')
            for item in itens.order_by('posicao'):
                print(f'  Posição {item.posicao}: {item.militar.nome_completo} ({item.militar.posto_graduacao} - {item.militar.quadro}) - Pontuação: {item.pontuacao}')
        
        print()

print('\n=== FIM DA VERIFICAÇÃO ===') 