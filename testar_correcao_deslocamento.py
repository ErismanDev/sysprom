#!/usr/bin/env python
"""
Script para testar a correção do deslocamento automático de antiguidade
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_correcao_deslocamento():
    print("=== TESTANDO CORREÇÃO DO DESLOCAMENTO MANUAL ===")
    
    # Buscar militares ativos de qualquer posto
    militares = Militar.objects.filter(
        situacao='AT'
    ).order_by('posto_graduacao', 'quadro', 'numeracao_antiguidade')
    
    # Agrupar por posto/quadro
    grupos = {}
    for militar in militares:
        chave = f"{militar.posto_graduacao}-{militar.quadro}"
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(militar)
    
    # Encontrar um grupo com pelo menos 5 militares
    grupo_teste = None
    for chave, grupo in grupos.items():
        if len(grupo) >= 5:
            grupo_teste = grupo
            print(f"\nTestando com grupo: {chave}")
            break
    
    if not grupo_teste:
        print("Não há grupos com 5 ou mais militares para teste")
        return
    
    print("\nSituação inicial:")
    for militar in grupo_teste:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Pegar o 5º militar
    quinto_militar = grupo_teste[4]  # índice 4 = 5º
    numeracao_anterior = quinto_militar.numeracao_antiguidade
    
    print(f"\nMovendo {quinto_militar.nome_completo} do {numeracao_anterior}º para 1º")
    
    # Alterar para 1º
    quinto_militar.numeracao_antiguidade = 1
    quinto_militar.save()
    
    print("\nApós a alteração:")
    militares_atualizados = Militar.objects.filter(
        posto_graduacao=quinto_militar.posto_graduacao,
        quadro=quinto_militar.quadro,
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    for militar in militares_atualizados:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Verificar se há duplicatas
    numeracoes = [m.numeracao_antiguidade for m in militares_atualizados]
    duplicatas = [n for n in numeracoes if numeracoes.count(n) > 1]
    if duplicatas:
        print(f"\nERRO: Encontradas numerações duplicadas: {duplicatas}")
    else:
        print("\n✓ Reordenação realizada sem duplicatas")
        
    # Verificar sequência
    numeracoes_ordenadas = sorted(numeracoes)
    if numeracoes == numeracoes_ordenadas:
        print("✓ Sequência está correta")
    else:
        print(f"ERRO: Sequência incorreta. Esperado: {numeracoes_ordenadas}, Atual: {numeracoes}")
    
    # Verificar se não há "buracos" na sequência
    sequencia_esperada = list(range(1, len(numeracoes) + 1))
    if numeracoes == sequencia_esperada:
        print("✓ Sequência sem buracos (1, 2, 3, 4, 5...)")
    else:
        print(f"ERRO: Há buracos na sequência. Esperado: {sequencia_esperada}, Atual: {numeracoes}")

if __name__ == '__main__':
    testar_correcao_deslocamento() 