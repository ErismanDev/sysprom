#!/usr/bin/env python
"""
Script para testar a funcionalidade de deslocamento automático quando a numeração de antiguidade é alterada manualmente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_deslocamento_manual():
    print("=== TESTANDO DESLOCAMENTO MANUAL ===")
    
    # Buscar militares ativos de qualquer posto
    militares = Militar.objects.filter(
        situacao='AT'
    ).order_by('posto_graduacao', 'quadro', 'numeracao_antiguidade')
    
    print(f"Militares ativos encontrados: {militares.count()}")
    
    # Agrupar por posto/quadro
    grupos = {}
    for militar in militares:
        chave = f"{militar.posto_graduacao}-{militar.quadro}"
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(militar)
    
    # Encontrar um grupo com pelo menos 4 militares
    grupo_teste = None
    for chave, grupo in grupos.items():
        if len(grupo) >= 4:
            grupo_teste = grupo
            print(f"\nTestando com grupo: {chave}")
            break
    
    if not grupo_teste:
        print("Não há grupos com 4 ou mais militares para teste")
        return
    
    print("\nSituação inicial:")
    for militar in grupo_teste:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # Pegar o 4º militar
    quarto_militar = grupo_teste[3]  # índice 3 = 4º
    numeracao_anterior = quarto_militar.numeracao_antiguidade
    
    print(f"\nMovendo {quarto_militar.nome_completo} do {numeracao_anterior}º para 1º")
    
    # Alterar para 1º
    quarto_militar.numeracao_antiguidade = 1
    quarto_militar.save()
    
    print("\nApós a alteração:")
    militares_atualizados = Militar.objects.filter(
        posto_graduacao=quarto_militar.posto_graduacao,
        quadro=quarto_militar.quadro,
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

if __name__ == '__main__':
    testar_deslocamento_manual() 