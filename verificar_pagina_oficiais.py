#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceito

print('=== SIMULAÇÃO DA VIEW ficha_conceito_list ===\n')

# Simular exatamente o que a view faz
militar_id = None  # Simular sem parâmetro militar

if militar_id:
    militar = None
    fichas = list(militar.fichaconceitooficiais_set.all()) + list(militar.fichaconceitopracas_set.all())
else:
    militar = None
    # Filtrar apenas oficiais (CB, TC, MJ, CP, 1T, 2T, AS, AA)
    oficiais = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
    )
    fichas = FichaConceito.objects.filter(militar__in=oficiais).order_by('-data_registro')

# Estatísticas para mostrar no template (apenas oficiais)
total_oficiais_ativos = Militar.objects.filter(
    situacao='AT',
    posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
).count()
total_fichas_oficiais = fichas.count()
oficiais_sem_ficha = total_oficiais_ativos - total_fichas_oficiais

print(f'Total de oficiais ativos: {total_oficiais_ativos}')
print(f'Total de fichas de oficiais: {total_fichas_oficiais}')
print(f'Oficiais sem ficha: {oficiais_sem_ficha}')
print(f'Fichas que serão exibidas: {fichas.count()}')

print('\n--- FICHAS QUE SERÃO EXIBIDAS ---')
for ficha in fichas:
    print(f'- {ficha.militar.nome_completo} ({ficha.militar.posto_graduacao}) - Pontos: {ficha.calcular_pontos()}')

print('\n--- VERIFICAÇÃO DE FILTRO ---')
# Verificar se há fichas de praças sendo incluídas incorretamente
fichas_pracas = FichaConceito.objects.filter(
    militar__posto_graduacao__in=['ST', '1S', '2S', '3S', 'CAB', 'SD']
)
print(f'Fichas de praças que NÃO deveriam aparecer: {fichas_pracas.count()}')

if fichas_pracas.exists():
    print('Fichas de praças encontradas (erro no filtro):')
    for ficha in fichas_pracas:
        print(f'- {ficha.militar.nome_completo} ({ficha.militar.posto_graduacao})')

print('\n=== FIM DA SIMULAÇÃO ===') 