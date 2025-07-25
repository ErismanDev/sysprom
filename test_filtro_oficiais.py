#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceito

print('=== TESTE DO FILTRO DE OFICIAIS ===\n')

# 1. Verificar todos os militares ativos
todos_militares = Militar.objects.filter(situacao='AT')
print(f'Total de militares ativos: {todos_militares.count()}')

# 2. Verificar oficiais ativos
oficiais = Militar.objects.filter(
    situacao='AT',
    posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
)
print(f'Total de oficiais ativos: {oficiais.count()}')

# 3. Verificar praças ativas
pracas = Militar.objects.filter(
    situacao='AT',
    posto_graduacao__in=['ST', '1S', '2S', '3S', 'CAB', 'SD']
)
print(f'Total de praças ativas: {pracas.count()}')

# 4. Verificar todas as fichas de conceito
todas_fichas = FichaConceito.objects.all()
print(f'Total de fichas de conceito: {todas_fichas.count()}')

# 5. Verificar fichas de oficiais
fichas_oficiais = FichaConceito.objects.filter(
    militar__in=oficiais
)
print(f'Total de fichas de oficiais: {fichas_oficiais.count()}')

# 6. Verificar fichas de praças
fichas_pracas = FichaConceito.objects.filter(
    militar__in=pracas
)
print(f'Total de fichas de praças: {fichas_pracas.count()}')

# 7. Mostrar alguns exemplos de oficiais
print('\n--- EXEMPLOS DE OFICIAIS ---')
for militar in oficiais[:5]:
    print(f'- {militar.nome_completo} ({militar.posto_graduacao})')

# 8. Mostrar alguns exemplos de praças
print('\n--- EXEMPLOS DE PRAÇAS ---')
for militar in pracas[:5]:
    print(f'- {militar.nome_completo} ({militar.posto_graduacao})')

# 9. Verificar se há fichas de praças sendo exibidas na página de oficiais
print('\n--- VERIFICAÇÃO DE FILTRO ---')
fichas_nao_oficiais = FichaConceito.objects.exclude(
    militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
)
print(f'Fichas que NÃO são de oficiais: {fichas_nao_oficiais.count()}')

if fichas_nao_oficiais.exists():
    print('Fichas que não deveriam aparecer na página de oficiais:')
    for ficha in fichas_nao_oficiais[:3]:
        print(f'- {ficha.militar.nome_completo} ({ficha.militar.posto_graduacao})')

print('\n=== FIM DO TESTE ===') 