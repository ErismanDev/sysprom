#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso, FichaConceito
from datetime import date, timedelta

def investigar_merecimento():
    print("=== INVESTIGANDO QUADRO DE MERECIMENTO ===\n")
    
    # 1. Verificar quadros de merecimento existentes
    print("1. QUADROS DE MERECIMENTO EXISTENTES:")
    print("-" * 50)
    
    quadros_merecimento = QuadroAcesso.objects.filter(tipo='MERECIMENTO').order_by('-data_promocao')
    print(f"Total de quadros de merecimento: {quadros_merecimento.count()}")
    
    for quadro in quadros_merecimento:
        itens = quadro.itemquadroacesso_set.all()
        print(f"  Quadro {quadro.pk}: {quadro.data_promocao} - Status: {quadro.status}")
        print(f"    Itens: {itens.count()}")
        print(f"    Observações: {quadro.observacoes}")
    
    # 2. Verificar militares que deveriam estar no quadro de merecimento
    print(f"\n2. MILITARES CANDIDATOS PARA MERECIMENTO:")
    print("-" * 50)
    
    # Postos que podem ser promovidos por merecimento
    postos_merecimento = ['2T', '1T', 'CP', 'MJ', 'TC']
    
    for posto in postos_merecimento:
        militares_posto = Militar.objects.filter(
            posto_graduacao=posto,
            situacao='AT'
        )
        
        militares_com_ficha = militares_posto.filter(Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False))
        militares_com_pontuacao = militares_com_ficha.filter(fichaconceito__pontos__isnull=False)
        
        print(f"  {posto}: {militares_posto.count()} total, {militares_com_ficha.count()} com ficha, {militares_com_pontuacao.count()} com pontuação")
        
        if militares_com_pontuacao.exists():
            print(f"    Militares com pontuação:")
            for militar in militares_com_pontuacao[:3]:  # Mostrar apenas os 3 primeiros
                ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
                print(f"      - {militar.nome_completo} ({militar.quadro}): {ficha.pontos} pontos")
    
    # 3. Verificar transições permitidas para merecimento
    print(f"\n3. TRANSIÇÕES PERMITIDAS PARA MERECIMENTO:")
    print("-" * 50)
    
    transicoes_merecimento = [
        ('TC', 'CB'),  # Tenente Coronel → Coronel (só merecimento)
        ('MJ', 'TC'),  # Major → Tenente Coronel (ambos)
        ('CP', 'MJ'),  # Capitão → Major (ambos)
    ]
    
    for origem, destino in transicoes_merecimento:
        militares_origem = Militar.objects.filter(
            posto_graduacao=origem,
            situacao='AT',
            Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
        )
        print(f"  {origem} → {destino}: {militares_origem.count()} candidatos")
    
    # 4. Verificar um quadro específico de merecimento
    if quadros_merecimento.exists():
        quadro = quadros_merecimento.first()
        print(f"\n4. ANALISANDO QUADRO ESPECÍFICO (ID: {quadro.pk}):")
        print("-" * 50)
        
        print(f"Data de promoção: {quadro.data_promocao}")
        print(f"Status: {quadro.status}")
        print(f"Observações: {quadro.observacoes}")
        
        # Verificar se o quadro pode ser elaborado
        militares_aptos = quadro.militares_aptos()
        print(f"Militares aptos retornados pelo método: {len(militares_aptos)}")
        
        # Verificar militares inaptos
        militares_inaptos = quadro.militares_inaptos_com_motivo()
        print(f"Militares inaptos: {len(militares_inaptos)}")
        
        if militares_inaptos:
            print("Primeiros 5 inaptos:")
            for item in militares_inaptos[:5]:
                print(f"  - {item['militar'].nome_completo}: {item['motivo']}")
        
        # 5. Tentar regenerar o quadro
        print(f"\n5. TENTANDO REGENERAR O QUADRO:")
        print("-" * 50)
        
        try:
            sucesso, mensagem = quadro.gerar_quadro_completo()
            print(f"Resultado: {sucesso}")
            print(f"Mensagem: {mensagem}")
            
            if sucesso:
                itens = quadro.itemquadroacesso_set.all().order_by('posicao')
                print(f"Itens após regeneração: {itens.count()}")
                
                if itens.exists():
                    print("Primeiros 5 itens:")
                    for item in itens[:5]:
                        ficha = item.militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
                        pontos = ficha.pontos if ficha else "N/A"
                        print(f"  {item.posicao}. {item.militar.nome_completo} ({item.militar.quadro}-{item.militar.posto_graduacao}): {item.pontuacao} (Ficha: {pontos})")
                else:
                    print("Nenhum item foi criado!")
            else:
                print("Quadro não foi elaborado!")
                
        except Exception as e:
            print(f"Erro ao regenerar quadro: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 6. Verificar fichas de conceito
    print(f"\n6. VERIFICANDO FICHAS DE CONCEITO:")
    print("-" * 50)
    
    fichas = FichaConceito.objects.all()
    print(f"Total de fichas: {fichas.count()}")
    
    fichas_com_pontos = fichas.filter(pontos__isnull=False)
    print(f"Fichas com pontos: {fichas_com_pontos.count()}")
    
    if fichas_com_pontos.exists():
        print("Fichas com maior pontuação:")
        for ficha in fichas_com_pontos.order_by('-pontos')[:5]:
            print(f"  - {ficha.militar.nome_completo} ({ficha.militar.posto_graduacao}): {ficha.pontos} pontos")

if __name__ == "__main__":
    investigar_merecimento() 