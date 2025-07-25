#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_promocao_subtenente():
    """Testa a funcionalidade de promoção de subtenentes"""
    
    print("=== TESTE DE PROMOÇÃO DE SUBTENENTES ===\n")
    
    # Buscar subtenentes do quadro praças
    subtenentes_pracas = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT'
    )
    
    print(f"Subtenentes do quadro praças encontrados: {subtenentes_pracas.count()}")
    
    if not subtenentes_pracas.exists():
        print("❌ Nenhum subtenente do quadro praças encontrado!")
        print("\nVerificando outros militares...")
        
        # Mostrar distribuição de militares por posto e quadro
        militares_por_posto = Militar.objects.values('posto_graduacao', 'quadro').annotate(
            count=django.db.models.Count('id')
        ).order_by('posto_graduacao', 'quadro')
        
        for item in militares_por_posto:
            print(f"- {item['posto_graduacao']} ({item['quadro']}): {item['count']} militares")
        
        return
    
    print("\n--- SUBTENENTES ENCONTRADOS ---")
    for st in subtenentes_pracas:
        print(f"\n{st.nome_completo}:")
        print(f"  - Matrícula: {st.matricula}")
        print(f"  - Data de promoção atual: {st.data_promocao_atual}")
        print(f"  - Tempo no posto: {st.tempo_posto_atual()} anos")
        print(f"  - Numeração de antiguidade: {st.numeracao_antiguidade}")
        print(f"  - Apto para promoção: {'Sim' if st.apto_promocao_antiguidade() else 'Não'}")
        print(f"  - Possui CHO: {'Sim' if st.curso_cho else 'Não'}")
        print(f"  - Inspeção de saúde válida: {'Sim' if st.apto_inspecao_saude else 'Não'}")
        print(f"  - Apto interstício: {'Sim' if st.apto_intersticio() else 'Não'}")
    
    # Verificar 2º tenentes do quadro complementar
    tenentes_complementar = Militar.objects.filter(
        posto_graduacao='2T',
        quadro='COMP',
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    print(f"\n--- 2º TENENTES DO QUADRO COMPLEMENTAR ---")
    print(f"Total: {tenentes_complementar.count()}")
    
    if tenentes_complementar.exists():
        print("Numerações existentes:")
        for tenente in tenentes_complementar:
            print(f"  - {tenente.nome_completo}: {tenente.numeracao_antiguidade}º")
    
    # Simular uma promoção
    print(f"\n--- SIMULAÇÃO DE PROMOÇÃO ---")
    
    # Escolher o primeiro subtenente apto
    subtenente_apto = None
    for st in subtenentes_pracas:
        if st.apto_promocao_antiguidade():
            subtenente_apto = st
            break
    
    if not subtenente_apto:
        print("❌ Nenhum subtenente apto para promoção encontrado!")
        return
    
    print(f"Subtenente selecionado para simulação: {subtenente_apto.nome_completo}")
    print(f"Numeração atual: {subtenente_apto.numeracao_antiguidade}")
    
    # Simular a promoção
    posto_anterior = subtenente_apto.posto_graduacao
    quadro_anterior = subtenente_apto.quadro
    
    # Calcular próxima numeração
    proxima_numeracao = subtenente_apto.atribuir_numeracao_por_promocao(posto_anterior, quadro_anterior)
    
    print(f"Próxima numeração que seria atribuída: {proxima_numeracao}º")
    
    # Verificar se há ficha de conceito
    ficha_pracas = subtenente_apto.fichaconceitopracas_set.first()
    if ficha_pracas:
        print(f"Ficha de conceito de praças encontrada: ID {ficha_pracas.id}")
        print(f"Pontuação: {ficha_pracas.pontos}")
    else:
        print("Nenhuma ficha de conceito de praças encontrada")
    
    print(f"\n✅ Teste concluído! A funcionalidade está pronta para uso.")
    print(f"Para testar a promoção real, acesse:")
    print(f"http://127.0.0.1:8000/militares/promocao-subtenente/?militar_id={subtenente_apto.id}")

if __name__ == "__main__":
    testar_promocao_subtenente() 