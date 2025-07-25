#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_reordenacao_coroneis():
    print("=== TESTANDO REORDENAÇÃO DE CORONÉIS ===")
    
    # Buscar coronéis ativos
    coroneis = Militar.objects.filter(
        posto_graduacao='CEL',
        quadro='OFICIAIS',
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    print(f"Coronéis encontrados: {coroneis.count()}")
    print("\nSituação atual:")
    for militar in coroneis:
        print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    if coroneis.count() >= 4:
        # Pegar o 4º coronel
        quarto_coronel = coroneis[3]  # índice 3 = 4º
        print(f"\nMovendo {quarto_coronel.nome_completo} do {quarto_coronel.numeracao_antiguidade}º para 1º")
        
        # Salvar a numeração anterior
        numeracao_anterior = quarto_coronel.numeracao_antiguidade
        
        # Alterar para 1º
        quarto_coronel.numeracao_antiguidade = 1
        quarto_coronel.save()
        
        print("\nApós a alteração:")
        coroneis_atualizados = Militar.objects.filter(
            posto_graduacao='CEL',
            quadro='OFICIAIS',
            situacao='AT'
        ).order_by('numeracao_antiguidade')
        
        for militar in coroneis_atualizados:
            print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
        
        # Verificar se há duplicatas
        numeracoes = [m.numeracao_antiguidade for m in coroneis_atualizados]
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
        print("Não há coronéis suficientes para o teste (mínimo 4)")

if __name__ == '__main__':
    testar_reordenacao_coroneis() 