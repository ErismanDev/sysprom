#!/usr/bin/env python
import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso, FichaConceito

def investigar_pontuacao_merecimento():
    """Investiga o problema da pontuação no quadro de merecimento"""
    
    print("=== INVESTIGAÇÃO DA PONTUAÇÃO NO QUADRO DE MERECIMENTO ===\n")
    
    # Buscar o quadro de merecimento mais recente
    quadro = QuadroAcesso.objects.filter(
        tipo='MERECIMENTO',
        status='ELABORADO'
    ).order_by('-data_criacao').first()
    
    if not quadro:
        print("❌ Nenhum quadro de merecimento elaborado encontrado!")
        return
    
    print(f"Quadro: {quadro.get_titulo_completo()}")
    print(f"Data de promoção: {quadro.data_promocao}")
    print(f"Status: {quadro.get_status_display()}")
    
    # Verificar itens do quadro
    itens = quadro.itemquadroacesso_set.all()
    print(f"\nTotal de itens no quadro: {itens.count()}")
    
    if itens.count() == 0:
        print("❌ Nenhum item no quadro!")
        return
    
    print("\n=== DETALHAMENTO DOS ITENS ===")
    print("-" * 80)
    
    for item in itens:
        militar = item.militar
        ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
        
        print(f"\nMilitar: {militar.nome_completo}")
        print(f"  - Quadro: {militar.quadro}")
        print(f"  - Posto: {militar.posto_graduacao}")
        print(f"  - Posição no quadro: {item.posicao}")
        print(f"  - Pontuação no quadro: {item.pontuacao}")
        
        if ficha:
            print(f"  - Pontuação na ficha: {ficha.pontos}")
            print(f"  - Tem ficha: Sim")
        else:
            print(f"  - Tem ficha: Não")
        
        # Verificar se a pontuação está correta
        if ficha and ficha.pontos != item.pontuacao:
            print(f"  ❌ PROBLEMA: Pontuação diferente!")
            print(f"     Ficha: {ficha.pontos} | Quadro: {item.pontuacao}")
        else:
            print(f"  ✅ Pontuação correta")
    
    # Verificar o método de geração
    print("\n=== VERIFICANDO MÉTODO DE GERAÇÃO ===")
    print("-" * 80)
    
    # Simular o processo de geração para um militar específico
    for item in itens[:2]:  # Verificar apenas os primeiros 2
        militar = item.militar
        print(f"\nSimulando geração para: {militar.nome_completo}")
        
        # Determinar tipo de transição
        proximo_posto = quadro._obter_proximo_posto(militar.posto_graduacao)
        if proximo_posto:
            tipo_quadro_transicao = quadro.determinar_tipo_quadro_por_transicao(
                militar.posto_graduacao, proximo_posto
            )
            print(f"  - Transição: {militar.posto_graduacao} → {proximo_posto}")
            print(f"  - Tipo de transição: {tipo_quadro_transicao}")
            
            # Verificar pontuação esperada
            ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
            if ficha:
                if tipo_quadro_transicao == 'MERECIMENTO':
                    pontuacao_esperada = float(ficha.pontos) if ficha.pontos is not None else 0.0
                    print(f"  - Pontuação esperada (merecimento): {pontuacao_esperada}")
                elif tipo_quadro_transicao == 'AMBOS':
                    pontuacao_esperada = float(ficha.pontos) if ficha.pontos is not None else 0.0
                    print(f"  - Pontuação esperada (ambos): {pontuacao_esperada}")
                else:
                    print(f"  - Pontuação esperada (antiguidade): baseada em numeração/data")
                
                if abs(pontuacao_esperada - float(item.pontuacao)) > 0.01:
                    print(f"  ❌ PROBLEMA: Pontuação incorreta!")
                    print(f"     Esperada: {pontuacao_esperada} | Atual: {item.pontuacao}")
                else:
                    print(f"  ✅ Pontuação correta")
            else:
                print(f"  ❌ Militar sem ficha de conceito!")
        else:
            print(f"  - Sem próximo posto definido")

if __name__ == '__main__':
    investigar_pontuacao_merecimento() 