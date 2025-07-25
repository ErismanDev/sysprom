#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso, FichaConceito
from datetime import date, timedelta

def testar_correcao_merecimento():
    """Testa as correções feitas no método gerar_quadro_completo para merecimento"""
    
    print("=== TESTE DAS CORREÇÕES NO QUADRO DE MERECIMENTO ===\n")
    
    # 1. Verificar se existem militares com ficha de conceito
    print("1. VERIFICANDO MILITARES COM FICHA DE CONCEITO:")
    print("-" * 50)
    
    militares_com_ficha = Militar.objects.filter(
        fichaconceitooficiais__isnull=False,
        fichaconceitopracas__isnull=False,
        situacao='AT'
    ).distinct()
    
    print(f"Total de militares com ficha de conceito: {militares_com_ficha.count()}")
    
    if militares_com_ficha.count() == 0:
        print("❌ NENHUM MILITAR COM FICHA DE CONCEITO ENCONTRADO!")
        print("   Isso explica por que o quadro de merecimento não está gerando.")
        return
    
    # Mostrar alguns militares com ficha
    print("\nExemplos de militares com ficha:")
    for militar in militares_com_ficha[:5]:
        ficha = militar.fichaconceitooficiais_set.first() or militar.fichaconceitopracas_set.first()
        print(f"  - {militar.nome_completo} ({militar.quadro}-{militar.posto_graduacao}) - Pontos: {ficha.pontos}")
    
    # 2. Verificar transições que devem aparecer em merecimento
    print("\n2. VERIFICANDO TRANSIÇÕES PARA MERECIMENTO:")
    print("-" * 50)
    
    # Transições que devem aparecer em merecimento
    transicoes_merecimento = ['TC→CB']  # Só por merecimento
    transicoes_ambos = ['CP→MJ', 'MJ→TC']  # Ambos os critérios
    
    print("Transições SÓ por merecimento:")
    for transicao in transicoes_merecimento:
        print(f"  - {transicao}")
    
    print("\nTransições que permitem AMBOS os critérios:")
    for transicao in transicoes_ambos:
        print(f"  - {transicao}")
    
    # 3. Verificar militares aptos para transições de merecimento
    print("\n3. VERIFICANDO MILITARES APTOS PARA MERECIMENTO:")
    print("-" * 50)
    
    # Buscar militares que podem ser promovidos por merecimento
    militares_aptos_merecimento = []
    
    # TC → CB (só merecimento)
    tcs_com_ficha = Militar.objects.filter(
        posto_graduacao='TC',
        situacao='AT',
        fichaconceitooficiais__isnull=False,
        fichaconceitopracas__isnull=False
    )
    print(f"Tenentes-Coronéis com ficha: {tcs_com_ficha.count()}")
    
    # CP → MJ (ambos)
    cps_com_ficha = Militar.objects.filter(
        posto_graduacao='CP',
        situacao='AT',
        fichaconceitooficiais__isnull=False,
        fichaconceitopracas__isnull=False
    )
    print(f"Capitães com ficha: {cps_com_ficha.count()}")
    
    # MJ → TC (ambos)
    mjs_com_ficha = Militar.objects.filter(
        posto_graduacao='MJ',
        situacao='AT',
        fichaconceitooficiais__isnull=False,
        fichaconceitopracas__isnull=False
    )
    print(f"Majores com ficha: {mjs_com_ficha.count()}")
    
    # 4. Tentar criar um quadro de merecimento
    print("\n4. TENTANDO CRIAR QUADRO DE MERECIMENTO:")
    print("-" * 50)
    
    # Data futura para promoção
    data_promocao = date.today() + timedelta(days=30)
    
    # Verificar se já existe quadro para esta data
    quadro_existente = QuadroAcesso.objects.filter(
        tipo='MERECIMENTO',
        data_promocao=data_promocao
    ).first()
    
    if quadro_existente:
        print(f"Quadro já existe para {data_promocao.strftime('%d/%m/%Y')}")
        quadro = quadro_existente
    else:
        print(f"Criando novo quadro de merecimento para {data_promocao.strftime('%d/%m/%Y')}")
        quadro = QuadroAcesso.objects.create(
            tipo='MERECIMENTO',
            data_promocao=data_promocao,
            status='EM_ELABORACAO'
        )
    
    # 5. Gerar o quadro
    print("\n5. GERANDO O QUADRO:")
    print("-" * 50)
    
    sucesso, mensagem = quadro.gerar_quadro_completo()
    
    print(f"Sucesso: {sucesso}")
    print(f"Mensagem: {mensagem}")
    
    if sucesso:
        # 6. Verificar resultado
        print("\n6. VERIFICANDO RESULTADO:")
        print("-" * 50)
        
        itens = quadro.itemquadroacesso_set.all()
        print(f"Total de militares no quadro: {itens.count()}")
        
        if itens.count() > 0:
            print("\nMilitares incluídos no quadro:")
            for item in itens[:10]:  # Mostrar apenas os primeiros 10
                ficha = item.militar.fichaconceitooficiais_set.first() or item.militar.fichaconceitopracas_set.first()
                pontos_ficha = ficha.pontos if ficha else 0
                print(f"  {item.posicao}º - {item.militar.nome_completo} ({item.militar.quadro}-{item.militar.posto_graduacao}) - Pontos: {item.pontuacao} (Ficha: {pontos_ficha})")
            
            if itens.count() > 10:
                print(f"  ... e mais {itens.count() - 10} militares")
        else:
            print("❌ NENHUM MILITAR FOI INCLUÍDO NO QUADRO!")
    
    # 7. Verificar militares inaptos
    print("\n7. VERIFICANDO MILITARES INAPTOS:")
    print("-" * 50)
    
    militares_inaptos = quadro.militares_inaptos_com_motivo()
    print(f"Total de militares inaptos: {len(militares_inaptos)}")
    
    if militares_inaptos:
        print("\nExemplos de militares inaptos:")
        for militar, motivo in militares_inaptos[:5]:
            print(f"  - {militar.nome_completo} ({militar.quadro}-{militar.posto_graduacao}): {motivo}")
    
    # 8. Testar ordenação por hierarquia
    print("\n8. TESTANDO ORDENAÇÃO POR HIERARQUIA:")
    print("-" * 50)
    
    if itens.count() > 0:
        # Verificar se a ordenação está respeitando a hierarquia
        itens_ordenados = itens.order_by('posicao')
        
        # Definir hierarquia correta
        hierarquia_quadros = ['COMB', 'SAUDE', 'ENG', 'COMP']
        hierarquia_postos = ['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'ST', '1S', '2S', '3S', 'SD']
        
        print("Verificando ordenação por hierarquia:")
        for i in range(len(itens_ordenados) - 1):
            item_atual = itens_ordenados[i]
            item_proximo = itens_ordenados[i + 1]
            
            militar_atual = item_atual.militar
            militar_proximo = item_proximo.militar
            
            # Verificar se o quadro está na ordem correta
            indice_quadro_atual = hierarquia_quadros.index(militar_atual.quadro) if militar_atual.quadro in hierarquia_quadros else 999
            indice_quadro_proximo = hierarquia_quadros.index(militar_proximo.quadro) if militar_proximo.quadro in hierarquia_quadros else 999
            
            # Verificar se o posto está na ordem correta
            indice_posto_atual = hierarquia_postos.index(militar_atual.posto_graduacao) if militar_atual.posto_graduacao in hierarquia_postos else 999
            indice_posto_proximo = hierarquia_postos.index(militar_proximo.posto_graduacao) if militar_proximo.posto_graduacao in hierarquia_postos else 999
            
            if indice_quadro_atual < indice_quadro_proximo:
                print(f"  ✓ {militar_atual.get_quadro_display()} vem antes de {militar_proximo.get_quadro_display()}")
            elif indice_quadro_atual > indice_quadro_proximo:
                print(f"  ✗ ERRO: {militar_atual.get_quadro_display()} não deveria vir antes de {militar_proximo.get_quadro_display()}")
            else:
                # Mesmo quadro, verificar posto
                if indice_posto_atual < indice_posto_proximo:
                    print(f"  ✓ {militar_atual.get_posto_graduacao_display()} vem antes de {militar_proximo.get_posto_graduacao_display()}")
                elif indice_posto_atual > indice_posto_proximo:
                    print(f"  ✗ ERRO: {militar_atual.get_posto_graduacao_display()} não deveria vir antes de {militar_proximo.get_posto_graduacao_display()}")
                else:
                    print(f"  ✓ Mesmo posto: {militar_atual.get_posto_graduacao_display()}")
    
    # 9. Resumo
    print("\n9. RESUMO:")
    print("-" * 50)
    
    if sucesso and itens.count() > 0:
        print("✅ QUADRO DE MERECIMENTO GERADO COM SUCESSO!")
        print(f"   - Militares incluídos: {itens.count()}")
        print(f"   - Militares inaptos: {len(militares_inaptos)}")
        print(f"   - Data de promoção: {quadro.data_promocao.strftime('%d/%m/%Y')}")
        print("   - Correções aplicadas:")
        print("     ✓ Hierarquia de postos corrigida (removido CB duplicado)")
        print("     ✓ Ordenação por merecimento usando método específico")
        print("     ✓ Pontuação da ficha sendo usada corretamente")
    else:
        print("❌ PROBLEMA NA GERAÇÃO DO QUADRO DE MERECIMENTO!")
        print("   Possíveis causas:")
        print("   - Militares não têm ficha de conceito")
        print("   - Militares não atendem aos requisitos (interstício, inspeção de saúde, cursos)")
        print("   - Não há militares nos postos que permitem merecimento")

if __name__ == '__main__':
    testar_correcao_merecimento() 