#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_correcao_reordenacao():
    print("=== TESTANDO CORREÇÃO DA REORDENAÇÃO ===")
    
    # Buscar qualquer posto que tenha militares ativos
    militares_ativos = Militar.objects.filter(situacao='AT').values('posto_graduacao', 'quadro').distinct()
    
    if not militares_ativos:
        print("❌ Nenhum militar ativo encontrado no sistema")
        return
    
    print(f"Postos encontrados: {len(militares_ativos)}")
    
    for i, (posto, quadro) in enumerate(militares_ativos[:3]):  # Testar apenas os 3 primeiros
        print(f"\n{i+1}. TESTE COM {posto} - {quadro}:")
        
        militares = Militar.objects.filter(
            posto_graduacao=posto,
            quadro=quadro,
            situacao='AT'
        ).order_by('numeracao_antiguidade')
        
        print(f"Militares encontrados: {militares.count()}")
        
        if militares.count() < 2:
            print("  ⚠️  Poucos militares para testar")
            continue
            
        print("\nSituação atual:")
        for militar in militares:
            print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo} (Promoção: {militar.data_promocao_atual})")
        
        # Pegar o 2º militar
        segundo_militar = militares[1]  # índice 1 = 2º
        numeracao_anterior = segundo_militar.numeracao_antiguidade
        print(f"\nMovendo {segundo_militar.nome_completo} do {numeracao_anterior}º para 1º")
        
        # Alterar para 1º
        segundo_militar.numeracao_antiguidade = 1
        segundo_militar.save()
        
        print("\nApós a alteração:")
        militares_atualizados = Militar.objects.filter(
            posto_graduacao=posto,
            quadro=quadro,
            situacao='AT'
        ).order_by('numeracao_antiguidade')
        
        for militar in militares_atualizados:
            print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo} (Promoção: {militar.data_promocao_atual})")
        
        # Verificar se há duplicatas
        numeracoes = [m.numeracao_antiguidade for m in militares_atualizados]
        duplicatas = [n for n in numeracoes if numeracoes.count(n) > 1]
        if duplicatas:
            print(f"\n❌ ERRO: Encontradas numerações duplicadas: {duplicatas}")
        else:
            print("\n✅ Reordenação realizada sem duplicatas")
            
        # Verificar sequência
        numeracoes_ordenadas = sorted(numeracoes)
        if numeracoes == numeracoes_ordenadas and numeracoes[0] == 1:
            print("✅ Sequência correta (1, 2, 3, ...)")
        else:
            print(f"❌ Sequência incorreta: {numeracoes}")

if __name__ == "__main__":
    testar_correcao_reordenacao() 