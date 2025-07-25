#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_reordenacao_cb():
    print("=== TESTANDO REORDENAÇÃO DE CABOS ===")
    
    # Buscar cabos ativos
    cabos = Militar.objects.filter(
        posto_graduacao='CB',
        quadro='PRACAS',
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    print(f"Cabos encontrados: {cabos.count()}")
    print("\nSituação atual:")
    for militar in cabos:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    if cabos.count() >= 4:
        # Pegar o 4º cabo
        quarto_cabo = cabos[3]  # índice 3 = 4º
        print(f"\nMovendo {quarto_cabo.nome_completo} do {quarto_cabo.numeracao_antiguidade}º para 1º")
        
        # Salvar a numeração anterior
        numeracao_anterior = quarto_cabo.numeracao_antiguidade
        
        # Alterar para 1º
        quarto_cabo.numeracao_antiguidade = 1
        quarto_cabo.save()
        
        print("\nApós a alteração:")
        cabos_atualizados = Militar.objects.filter(
            posto_graduacao='CB',
            quadro='PRACAS',
            situacao='AT'
        ).order_by('numeracao_antiguidade')
        
        for militar in cabos_atualizados:
            print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
        
        # Verificar se há duplicatas
        numeracoes = [m.numeracao_antiguidade for m in cabos_atualizados]
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
    else:
        print("Não há cabos suficientes para o teste (mínimo 4)")

if __name__ == '__main__':
    testar_reordenacao_cb() 