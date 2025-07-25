import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

print("=== VERIFICAÇÃO DE DUPLICAÇÃO ===")

# Buscar militares ativos e inativos
ativos = Militar.objects.filter(situacao='AT')
inativos = Militar.objects.filter(situacao__in=['IN', 'TR', 'AP', 'EX'])

print(f"Militares ativos: {ativos.count()}")
print(f"Militares inativos: {inativos.count()}")

# Verificar sobreposição
ativos_ids = set(ativos.values_list('id', flat=True))
inativos_ids = set(inativos.values_list('id', flat=True))

intersecao = ativos_ids.intersection(inativos_ids)
print(f"Militares em ambas as listas: {len(intersecao)}")

if intersecao:
    print("\nMILITARES DUPLICADOS:")
    for militar_id in intersecao:
        militar = Militar.objects.get(id=militar_id)
        print(f"- {militar.nome_completo} (ID: {militar_id}, Situação: {militar.situacao})")

# Verificar todas as situações
print("\nTODAS AS SITUAÇÕES:")
situacoes = Militar.objects.values_list('situacao', flat=True).distinct()
for situacao in situacoes:
    count = Militar.objects.filter(situacao=situacao).count()
    print(f"{situacao}: {count}") 