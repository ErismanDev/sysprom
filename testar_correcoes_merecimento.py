#!/usr/bin/env python
"""
Script para testar as correções implementadas no quadro de merecimento
"""

import os
import sys
import django
from datetime import date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso, Militar, FichaConceito

def testar_quadro_merecimento():
    """Testa a geração do quadro de merecimento com as correções"""
    print("=== TESTE DO QUADRO DE MERECIMENTO ===\n")
    
    # Buscar quadro de merecimento existente ou criar um novo
    try:
        quadro = QuadroAcesso.objects.filter(tipo='MERECIMENTO').first()
        if not quadro:
            print("Criando novo quadro de merecimento para teste...")
            quadro = QuadroAcesso.objects.create(
                tipo='MERECIMENTO',
                data_promocao=date(2025, 1, 1),
                status='EM_ELABORACAO'
            )
        else:
            print(f"Usando quadro existente: {quadro}")
    except Exception as e:
        print(f"Erro ao criar/buscar quadro: {e}")
        return
    
    # Limpar itens existentes
    quadro.itemquadroacesso_set.all().delete()
    
    print(f"\n1. Verificando militares candidatos...")
    
    # Verificar militares candidatos por posto
    postos = ['2T', '1T', 'CP', 'MJ', 'TC', 'CB']
    total_candidatos = 0
    total_com_ficha = 0
    
    for posto in postos:
        militares_posto = Militar.objects.filter(
            posto_graduacao=posto,
            situacao='AT'
        )
        militares_com_ficha = militares_posto.filter(fichaconceitooficiais__isnull=False) or militares_posto.filter(fichaconceitopracas__isnull=False)
        militares_com_pontuacao = militares_com_ficha.filter(fichaconceito__pontos__isnull=False)
        
        print(f"  {posto}: {militares_posto.count()} total, {militares_com_ficha.count()} com ficha, {militares_com_pontuacao.count()} com pontuação")
        total_candidatos += militares_posto.count()
        total_com_ficha += militares_com_pontuacao.count()
    
    print(f"\n  Total: {total_candidatos} candidatos, {total_com_ficha} com ficha válida")
    
    print(f"\n2. Gerando quadro de merecimento...")
    
    try:
        sucesso, mensagem = quadro.gerar_quadro_completo()
        print(f"  Resultado: {sucesso}")
        print(f"  Mensagem: {mensagem}")
        
        if sucesso:
            print(f"\n3. Verificando itens do quadro...")
            itens = quadro.itemquadroacesso_set.all().order_by('posicao')
            
            if itens.exists():
                print(f"  Total de itens: {itens.count()}")
                print(f"\n  Primeiros 10 itens:")
                for i, item in enumerate(itens[:10]):
                    ficha = item.militar.fichaconceitooficiais_set.first() or item.militar.fichaconceitopracas_set.first()
                    pontos_ficha = ficha.pontos if ficha else "N/A"
                    print(f"    {i+1}. {item.militar.nome_completo} ({item.militar.quadro}-{item.militar.posto_graduacao}) - Posição: {item.posicao}, Pontuação: {item.pontuacao} (Ficha: {pontos_ficha})")
                
                if itens.count() > 10:
                    print(f"    ... e mais {itens.count() - 10} itens")
            else:
                print("  Nenhum item encontrado no quadro")
        else:
            print(f"\n  Quadro não foi elaborado: {mensagem}")
            
    except Exception as e:
        print(f"  Erro na geração: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n4. Verificando militares sem ficha de conceito...")
    
    # Listar militares que deveriam estar no quadro mas não têm ficha
    militares_sem_ficha = []
    for posto in postos:
        militares_posto = Militar.objects.filter(
            posto_graduacao=posto,
            situacao='AT'
        )
        for militar in militares_posto:
            if not (militar.fichaconceitooficiais_set.exists() or militar.fichaconceitopracas_set.exists()):
                militares_sem_ficha.append(militar)
    
    if militares_sem_ficha:
        print(f"  Militares sem ficha de conceito ({len(militares_sem_ficha)}):")
        for militar in militares_sem_ficha[:5]:  # Mostrar apenas os primeiros 5
            print(f"    - {militar.nome_completo} ({militar.quadro}-{militar.posto_graduacao})")
        if len(militares_sem_ficha) > 5:
            print(f"    ... e mais {len(militares_sem_ficha) - 5} militares")
    else:
        print("  Todos os militares têm ficha de conceito")
    
    print(f"\n=== FIM DO TESTE ===")

def verificar_fichas_conceito():
    """Verifica o status das fichas de conceito"""
    print("\n=== VERIFICAÇÃO DAS FICHAS DE CONCEITO ===\n")
    
    total_militares = Militar.objects.filter(situacao='AT').count()
    militares_com_ficha = Militar.objects.filter(situacao='AT', fichaconceitooficiais__isnull=False) or Militar.objects.filter(situacao='AT', fichaconceitopracas__isnull=False).count()
    militares_com_pontuacao = Militar.objects.filter(situacao='AT', fichaconceito__pontos__isnull=False).count()
    
    print(f"Total de militares ativos: {total_militares}")
    print(f"Militares com ficha de conceito: {militares_com_ficha}")
    print(f"Militares com pontuação válida: {militares_com_pontuacao}")
    print(f"Militares sem ficha: {total_militares - militares_com_ficha}")
    print(f"Militares com ficha mas sem pontuação: {militares_com_ficha - militares_com_pontuacao}")
    
    # Verificar por posto
    print(f"\nPor posto:")
    postos = ['2T', '1T', 'CP', 'MJ', 'TC', 'CB']
    for posto in postos:
        total = Militar.objects.filter(posto_graduacao=posto, situacao='AT').count()
        com_ficha = Militar.objects.filter(posto_graduacao=posto, situacao='AT', fichaconceitooficiais__isnull=False) or Militar.objects.filter(posto_graduacao=posto, situacao='AT', fichaconceitopracas__isnull=False).count()
        com_pontuacao = Militar.objects.filter(posto_graduacao=posto, situacao='AT', fichaconceito__pontos__isnull=False).count()
        print(f"  {posto}: {total} total, {com_ficha} com ficha, {com_pontuacao} com pontuação")

if __name__ == '__main__':
    verificar_fichas_conceito()
    testar_quadro_merecimento() 