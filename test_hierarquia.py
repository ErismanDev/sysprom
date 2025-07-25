#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceito

print('=== TESTE DE ORDENAÇÃO POR HIERARQUIA ===\n')

# Teste para Oficiais
print('OFICIAIS:')
oficiais = Militar.objects.filter(
    situacao='AT',
    posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
)
fichas_oficiais = FichaConceito.objects.filter(militar__in=oficiais)

hierarquia_oficiais = {
    'CB': 1,   # Coronel
    'TC': 2,   # Tenente Coronel
    'MJ': 3,   # Major
    'CP': 4,   # Capitão
    '1T': 5,   # 1º Tenente
    '2T': 6,   # 2º Tenente
    'AS': 7,   # Aspirante a Oficial
    'AA': 8,   # Aluno de Adaptação
}

fichas_list_oficiais = list(fichas_oficiais)
fichas_list_oficiais.sort(key=lambda x: (
    hierarquia_oficiais.get(x.militar.posto_graduacao, 999),
    x.militar.numeracao_antiguidade or 999999,
    x.militar.nome_completo
))

print(f'Total de fichas de oficiais: {len(fichas_list_oficiais)}')
for i, ficha in enumerate(fichas_list_oficiais[:10], 1):  # Mostrar apenas os 10 primeiros
    print(f'{i:2d}. {ficha.militar.get_posto_graduacao_display():<15} - {ficha.militar.nome_completo}')

print('\n' + '='*50 + '\n')

# Teste para Praças
print('PRACAS:')
pracas = Militar.objects.filter(
    situacao='AT',
    posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
)
fichas_pracas = FichaConceito.objects.filter(militar__in=pracas)

hierarquia_pracas = {
    'ST': 1,   # Subtenente
    '1S': 2,   # 1º Sargento
    '2S': 3,   # 2º Sargento
    '3S': 4,   # 3º Sargento
    'CAB': 5,  # Cabo
    'SD': 6,   # Soldado
}

fichas_list_pracas = list(fichas_pracas)
fichas_list_pracas.sort(key=lambda x: (
    hierarquia_pracas.get(x.militar.posto_graduacao, 999),
    x.militar.numeracao_antiguidade or 999999,
    x.militar.nome_completo
))

print(f'Total de fichas de praças: {len(fichas_list_pracas)}')
for i, ficha in enumerate(fichas_list_pracas[:10], 1):  # Mostrar apenas os 10 primeiros
    print(f'{i:2d}. {ficha.militar.get_posto_graduacao_display():<15} - {ficha.militar.nome_completo}')

print('\n=== TESTE CONCLUÍDO ===') 