#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def reordenar_tc_comb_id():
    print("=== REORDENAÇÃO ABSOLUTA TC - COMB (POR ID) ===")
    militares = Militar.objects.filter(
        posto_graduacao='TC',
        quadro='COMB',
        situacao='AT'
    ).order_by('id')
    print(f"Encontrados {militares.count()} TC - COMB ativos")
    for i, militar in enumerate(militares, 1):
        print(f"  {militar.nome_completo}: {militar.numeracao_antiguidade}º -> {i}º (ID {militar.id})")
        militar.numeracao_antiguidade = i
        militar.save(update_fields=['numeracao_antiguidade'])
    print("\n✓ Reordenação absoluta concluída!")
    # Exibir resultado final
    militares_atualizados = Militar.objects.filter(
        posto_graduacao='TC',
        quadro='COMB',
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    print("\nResultado final:")
    for militar in militares_atualizados:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo} (ID {militar.id})")

if __name__ == '__main__':
    reordenar_tc_comb_id() 