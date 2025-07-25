#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def debug_reordenacao_coronel():
    print("=== DEBUG REORDENAÇÃO CORONÉIS ===")
    
    posto = 'CB'
    quadro = 'OFICIAIS'
    militares = Militar.objects.filter(
        posto_graduacao=posto,
        quadro=quadro,
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    if militares.count() < 2:
        print("  Poucos coronéis para testar")
        return
    
    print(f"Coronéis encontrados: {militares.count()}")
    print("\nANTES da alteração:")
    for militar in militares:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Pegar o último coronel
    ultimo_coronel = militares.last()
    numeracao_anterior = ultimo_coronel.numeracao_antiguidade
    print(f"\nMovendo {ultimo_coronel.nome_completo} do {numeracao_anterior}º para 1º")
    
    # Simular a alteração
    ultimo_coronel.numeracao_antiguidade = 1
    ultimo_coronel.save()
    
    print("\nAPÓS a alteração:")
    coroneis_atualizados = Militar.objects.filter(
        posto_graduacao=posto,
        quadro=quadro,
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    for militar in coroneis_atualizados:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Verificar duplicatas
    numeracoes = [m.numeracao_antiguidade for m in coroneis_atualizados]
    duplicatas = [n for n in numeracoes if numeracoes.count(n) > 1]
    if duplicatas:
        print(f"\n❌ DUPLICATAS ENCONTRADAS: {duplicatas}")
        print(f"   Todas as numerações: {numeracoes}")
    else:
        print("\n✅ Sem duplicatas")
    
    # Verificar sequência
    numeracoes_ordenadas = sorted(numeracoes)
    if numeracoes == numeracoes_ordenadas and numeracoes[0] == 1:
        print("✅ Sequência correta")
    else:
        print(f"❌ Sequência incorreta: {numeracoes}")

if __name__ == "__main__":
    debug_reordenacao_coronel() 