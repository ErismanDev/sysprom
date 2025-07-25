import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

print("=== INVESTIGAÇÃO DE DUPLICAÇÃO ===\n")

# Buscar todos os militares
todos_militares = Militar.objects.all()
print(f"Total de militares: {todos_militares.count()}")

# Buscar militares ativos
militares_ativos = Militar.objects.filter(situacao='AT')
print(f"Militares ativos: {militares_ativos.count()}")

# Buscar militares inativos
militares_inativos = Militar.objects.filter(situacao__in=['IN', 'TR', 'AP', 'EX'])
print(f"Militares inativos: {militares_inativos.count()}")

# Verificar se há sobreposição
ativos_ids = set(militares_ativos.values_list('id', flat=True))
inativos_ids = set(militares_inativos.values_list('id', flat=True))

intersecao = ativos_ids.intersection(inativos_ids)
print(f"\nMilitares que aparecem em ambas as listas: {len(intersecao)}")

if intersecao:
    print("\n=== MILITARES DUPLICADOS ===")
    for militar_id in intersecao:
        militar = Militar.objects.get(id=militar_id)
        print(f"ID: {militar_id}")
        print(f"Nome: {militar.nome_completo}")
        print(f"Posto: {militar.get_posto_graduacao_display()}")
        print(f"Situação: {militar.situacao} ({militar.get_situacao_display()})")
        print(f"Matrícula: {militar.matricula}")
        print("---")

# Verificar todas as situações possíveis
print("\n=== TODAS AS SITUAÇÕES ===")
situacoes = Militar.objects.values_list('situacao', flat=True).distinct()
for situacao in situacoes:
    count = Militar.objects.filter(situacao=situacao).count()
    print(f"{situacao}: {count} militares")

# Verificar se há militares com situação nula ou vazia
nulos = Militar.objects.filter(situacao__isnull=True)
vazios = Militar.objects.filter(situacao='')
print(f"\nMilitares com situação nula: {nulos.count()}")
print(f"Militares com situação vazia: {vazios.count()}")

# Mostrar alguns exemplos de cada situação
print("\n=== EXEMPLOS POR SITUAÇÃO ===")
for situacao in situacoes:
    militares = Militar.objects.filter(situacao=situacao)[:3]
    print(f"\n{situacao} ({len(militares)} primeiros):")
    for militar in militares:
        print(f"  - {militar.nome_completo} (ID: {militar.id})") 