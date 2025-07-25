#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def reordenar_forcado_tc_comb():
    print("=== REORDENAÇÃO FORÇADA TC - COMB ===")
    militares = Militar.objects.filter(
        posto_graduacao='TC',
        quadro='COMB',
        situacao='AT'
    ).order_by('numeracao_antiguidade', 'id')
    print(f"Encontrados {militares.count()} TC - COMB ativos")
    for i, militar in enumerate(militares, 1):
        print(f"  {militar.nome_completo}: {militar.numeracao_antiguidade}º -> {i}º")
        militar.numeracao_antiguidade = i
        militar.save(update_fields=['numeracao_antiguidade'])
    print("\n✓ Reordenação forçada concluída!")
    # Exibir resultado final
    militares_atualizados = Militar.objects.filter(
        posto_graduacao='TC',
        quadro='COMB',
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    print("\nResultado final:")
    for militar in militares_atualizados:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")

if __name__ == '__main__':
    reordenar_forcado_tc_comb() 