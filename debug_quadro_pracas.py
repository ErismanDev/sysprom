#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso
from datetime import date, timedelta

def debug_quadro_pracas():
    print("=== DEBUG DA GERAÇÃO DE QUADROS PARA PRACAS ===\n")
    
    # 1. Verificar se existem militares praças no sistema
    print("1. VERIFICANDO MILITARES PRACAS NO SISTEMA:")
    print("-" * 50)
    
    postos_pracas = ['SD', 'CAB', '3S', '2S', '1S', 'ST']
    militares_pracas = Militar.objects.filter(
        posto_graduacao__in=postos_pracas,
        situacao='AT'
    )
    
    print(f"Total de militares praças ativos: {militares_pracas.count()}")
    
    for posto in postos_pracas:
        count = militares_pracas.filter(posto_graduacao=posto).count()
        print(f"  {posto}: {count} militares")
    
    if militares_pracas.count() == 0:
        print("❌ NÃO HÁ MILITARES PRACAS NO SISTEMA!")
        return
    
    # 2. Verificar se há militares aptos para promoção
    print(f"\n2. VERIFICANDO MILITARES APTOS PARA PROMOÇÃO:")
    print("-" * 50)
    
    # Data futura para promoção
    data_promocao = date.today() + timedelta(days=30)
    
    militares_aptos = []
    militares_inaptos = []
    
    for militar in militares_pracas:
        # Verificar se tem próximo posto
        proximo_posto = None
        if militar.posto_graduacao == 'SD':
            proximo_posto = 'CAB'
        elif militar.posto_graduacao == 'CAB':
            proximo_posto = '3S'
        elif militar.posto_graduacao == '3S':
            proximo_posto = '2S'
        elif militar.posto_graduacao == '2S':
            proximo_posto = '1S'
        elif militar.posto_graduacao == '1S':
            proximo_posto = 'ST'
        elif militar.posto_graduacao == 'ST':
            proximo_posto = '2T'  # Subtenente promove para 2º Tenente
        
        if proximo_posto:
            # Verificar requisitos básicos
            apto = True
            motivo = []
            
            # Verificar interstício
            if militar.data_promocao_atual:
                anos = data_promocao.year - militar.data_promocao_atual.year
                meses = data_promocao.month - militar.data_promocao_atual.month
                if meses < 0:
                    anos -= 1
                    meses += 12
                tempo_total_meses = anos * 12 + meses
                
                # Interstício mínimo para praças (exemplo)
                intersticio_minimo = 36  # 3 anos
                if tempo_total_meses < intersticio_minimo:
                    apto = False
                    motivo.append(f"Interstício insuficiente ({tempo_total_meses} meses < {intersticio_minimo})")
            else:
                apto = False
                motivo.append("Sem data de promoção atual")
            
            # Verificar inspeção de saúde
            if not militar.apto_inspecao_saude:
                apto = False
                motivo.append("Não apto em inspeção de saúde")
            
            if apto:
                militares_aptos.append({
                    'militar': militar,
                    'proximo_posto': proximo_posto,
                    'tempo_posto': tempo_total_meses if militar.data_promocao_atual else 0
                })
            else:
                militares_inaptos.append({
                    'militar': militar,
                    'motivo': ', '.join(motivo)
                })
    
    print(f"Militares aptos: {len(militares_aptos)}")
    print(f"Militares inaptos: {len(militares_inaptos)}")
    
    if militares_aptos:
        print(f"\n  Militares aptos:")
        for item in militares_aptos[:5]:  # Mostrar apenas os primeiros 5
            m = item['militar']
            print(f"    - {m.nome_completo} ({m.posto_graduacao} → {item['proximo_posto']}) - {item['tempo_posto']} meses no posto")
    
    if militares_inaptos:
        print(f"\n  Militares inaptos (primeiros 5):")
        for item in militares_inaptos[:5]:
            m = item['militar']
            print(f"    - {m.nome_completo} ({m.posto_graduacao}): {item['motivo']}")
    
    # 3. Tentar criar um quadro de acesso para praças
    print(f"\n3. TENTANDO CRIAR QUADRO DE ACESSO PARA PRACAS:")
    print("-" * 50)
    
    # Verificar se já existe quadro para esta data
    quadro_existente = QuadroAcesso.objects.filter(
        tipo='ANTIGUIDADE',
        data_promocao=data_promocao
    ).first()
    
    if quadro_existente:
        print(f"Quadro já existe para {data_promocao.strftime('%d/%m/%Y')}")
        quadro = quadro_existente
    else:
        print(f"Criando novo quadro de antiguidade para {data_promocao.strftime('%d/%m/%Y')}")
        quadro = QuadroAcesso.objects.create(
            tipo='ANTIGUIDADE',
            data_promocao=data_promocao,
            status='EM_ELABORACAO'
        )
    
    # 4. Gerar o quadro
    print(f"\n4. GERANDO O QUADRO:")
    print("-" * 50)
    
    try:
        sucesso, mensagem = quadro.gerar_quadro_completo()
        print(f"Resultado: {sucesso}")
        print(f"Mensagem: {mensagem}")
        
        if sucesso:
            print(f"\n5. VERIFICANDO ITENS DO QUADRO:")
            print("-" * 50)
            
            itens = quadro.itemquadroacesso_set.all().order_by('posicao')
            
            if itens.exists():
                print(f"Total de itens: {itens.count()}")
                
                # Verificar se há praças no quadro
                itens_pracas = itens.filter(
                    militar__posto_graduacao__in=postos_pracas
                )
                print(f"Itens de praças: {itens_pracas.count()}")
                
                if itens_pracas.exists():
                    print(f"\n  Praças no quadro:")
                    for item in itens_pracas[:10]:
                        m = item.militar
                        print(f"    {item.posicao}. {m.nome_completo} ({m.posto_graduacao}) - Pontuação: {item.pontuacao}")
                else:
                    print("❌ NENHUMA PRAÇA FOI INCLUÍDA NO QUADRO!")
                    
                    # Verificar quais postos foram incluídos
                    postos_incluidos = itens.values_list('militar__posto_graduacao', flat=True).distinct()
                    print(f"Postos incluídos no quadro: {list(postos_incluidos)}")
            else:
                print("❌ NENHUM ITEM FOI CRIADO NO QUADRO!")
        else:
            print(f"❌ QUADRO NÃO FOI ELABORADO: {mensagem}")
            
    except Exception as e:
        print(f"❌ ERRO AO GERAR QUADRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_quadro_pracas() 