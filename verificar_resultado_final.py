#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def verificar_resultado_final():
    print("=== VERIFICANDO RESULTADO FINAL ===")
    
    # Verificar os 1º Sargentos PRACAS
    militares = Militar.objects.filter(
        posto_graduacao='1S',
        quadro='PRACAS',
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    print(f"\n1º Sargentos PRACAS após a correção:")
    for militar in militares:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Verificar se há duplicatas
    numeracoes = [m.numeracao_antiguidade for m in militares]
    duplicatas = [n for n in numeracoes if numeracoes.count(n) > 1]
    if duplicatas:
        print(f"\nERRO: Encontradas numerações duplicadas: {duplicatas}")
    else:
        print(f"\n✓ Sem duplicatas")
    
    # Verificar se há buracos na sequência
    sequencia_esperada = list(range(1, len(numeracoes) + 1))
    if numeracoes == sequencia_esperada:
        print("✓ Sequência sem buracos (1, 2, 3, 4, 5...)")
    else:
        print(f"ERRO: Há buracos na sequência. Esperado: {sequencia_esperada}, Atual: {numeracoes}")

if __name__ == '__main__':
    verificar_resultado_final() 