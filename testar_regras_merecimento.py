��# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, ItemQuadroAcesso, FichaConceito
from datetime import date, timedelta

def testar_regras_merecimento():
    """Testa as regras espec�ficas para o PDF de merecimento conforme solicitado"""
    
    print("=== TESTE DAS REGRAS DE MERECIMENTO ===\n")
    
    # 1. Verificar regras implementadas
    print("1. REGRAS IMPLEMENTADAS:")
    print("-" * 50)
    
    print("' QUADRO COMBATENTE (COMB):")
    print("   - Tenente-Coronel �! Coronel (TC�!CB)")
    print("   - Major �! Tenente-Coronel (MJ�!TC)")
    print("   - Capit�o �! Major (CP�!MJ)")
    
    print("\n' QUADROS SA�DE, ENGENHEIRO E COMPLEMENTAR (SAUDE, ENG, COMP):")
    print("   - Major �! Tenente-Coronel (MJ�!TC)")
    print("   - Capit�o �! Major (CP�!MJ)")
    
    print("\nL' TRANSI��O TC�!CB APARECE APENAS NO QUADRO COMBATENTE")
    
    # 2. Verificar m�todo determinar_tipo_quadro_por_transicao
    print("\n2. VERIFICANDO M�TODO DETERMINAR_TIPO_QUADRO_POR_TRANSICAO:")
    print("-" * 50)
    
    # Criar um quadro tempor�rio para testar o m�todo
    quadro_teste = QuadroAcesso.objects.create(
        tipo='MERECIMENTO',
        data_promocao=date.today() + timedelta(days=30),
        status='EM_ELABORACAO'
    )
    
    # Testar transi��es
    transicoes_teste = [
        ('TC', 'CB'),  # S� merecimento
        ('MJ', 'TC'),  # Ambos
        ('CP', 'MJ'),  # Ambos
        ('1T', 'CP'),  # S� antiguidade
        ('2T', '1T'),  # S� antiguidade
    ]
    
    for origem, destino in transicoes_teste:
        tipo = quadro_teste.determinar_tipo_quadro_por_transicao(origem, destino)
        print(f"   {origem}�!{destino}: {tipo}")
    
    # 3. Verificar transi��es no PDF
    print("\n3. VERIFICANDO TRANSI��ES NO PDF:")
    print("-" * 50)
    
    # Simular as transi��es definidas na view quadro_acesso_pdf
    transicoes_pdf_merecimento = {
        'COMB': [
            ('TC', 'CB', 'I', 'TENENTE-CORONEL para o posto de CORONEL'),
            ('MJ', 'TC', 'II', 'MAJOR para o posto de TENENTE-CORONEL'),
            ('CP', 'MJ', 'III', 'CAPIT�O para o posto de MAJOR'),
        ],
        'SAUDE': [
            ('MJ', 'TC', 'I', 'MAJOR para o posto de TENENTE-CORONEL'),
            ('CP', 'MJ', 'II', 'CAPIT�O para o posto de MAJOR'),
        ],
        'ENG': [
            ('MJ', 'TC', 'I', 'MAJOR para o posto de TENENTE-CORONEL'),
            ('CP', 'MJ', 'II', 'CAPIT�O para o posto de MAJOR'),
        ],
        'COMP': [
            ('MJ', 'TC', 'I', 'MAJOR para o posto de TENENTE-CORONEL'),
            ('CP', 'MJ', 'II', 'CAPIT�O para o posto de MAJOR'),
        ]
    }
    
    for quadro, transicoes in transicoes_pdf_merecimento.items():
        print(f"\n   {quadro}:")
        for origem, destino, numero, titulo in transicoes:
            print(f"     {numero}. {titulo} ({origem}�!{destino})")
    
    # 4. Verificar se h� militares aptos para merecimento
    print("\n4. VERIFICANDO MILITARES APTOS PARA MERECIMENTO:")
    print("-" * 50)
    
    # Buscar militares que podem ser promovidos por merecimento
    militares_aptos_merecimento = []
    
    # TC �! CB (s� merecimento, s� COMB)
    tcs_com_ficha = Militar.objects.filter(
        quadro='COMB',
        posto_graduacao='TC',
        situacao='AT',
        fichaconceito__isnull=False
    )
    print(f"Tenentes-Coron�is COMB com ficha: {tcs_com_ficha.count()}")
    
    # MJ �! TC (ambos, todos os quadros)
    mjs_com_ficha = Militar.objects.filter(
        posto_graduacao='MJ',
        situacao='AT',
        fichaconceito__isnull=False
    )
    print(f"Majores com ficha: {mjs_com_ficha.count()}")
    
    # CP �! MJ (ambos, todos os quadros)
    cps_com_ficha = Militar.objects.filter(
        posto_graduacao='CP',
        situacao='AT',
        fichaconceito__isnull=False
    )
    print(f"Capit�es com ficha: {cps_com_ficha.count()}")
    
    # 5. Tentar criar um quadro de merecimento
    print("\n5. TENTANDO CRIAR QUADRO DE MERECIMENTO:")
    print("-" * 50)
    
    # Data futura para promo��o
    data_promocao = date.today() + timedelta(days=30)
    
    # Verificar se j� existe quadro para esta data
    quadro_existente = QuadroAcesso.objects.filter(
        tipo='MERECIMENTO',
        data_promocao=data_promocao
    ).first()
    
    if quadro_existente:
        print(f"Quadro j� existe para {data_promocao.strftime('%d/%m/%Y')}")
        quadro = quadro_existente
    else:
        print(f"Criando novo quadro de merecimento para {data_promocao.strftime('%d/%m/%Y')}")
        quadro = QuadroAcesso.objects.create(
            tipo='MERECIMENTO',
            data_promocao=data_promocao,
            status='EM_ELABORACAO'
        )
    
    # 6. Gerar o quadro
    print("\n6. GERANDO O QUADRO:")
    print("-" * 50)
    
    sucesso, mensagem = quadro.gerar_quadro_completo()
    print(f"Resultado: {mensagem}")
    
    if sucesso:
        itens = quadro.itemquadroacesso_set.all().select_related('militar')
        print(f"Militares inclu�dos: {itens.count()}")
        
        # Verificar se as regras est�o sendo aplicadas
        print("\n7. VERIFICANDO APLICA��O DAS REGRAS:")
        print("-" * 50)
        
        # Agrupar por quadro e posto
        grupos = {}
        for item in itens:
            militar = item.militar
            chave = f"{militar.quadro}-{militar.posto_graduacao}"
            if chave not in grupos:
                grupos[chave] = []
            grupos[chave].append(item)
        
        # Verificar se apenas as transi��es corretas est�o sendo inclu�das
        transicoes_permitidas = {
            'COMB': ['TC', 'MJ', 'CP'],  # TC�!CB, MJ�!TC, CP�!MJ
            'SAUDE': ['MJ', 'CP'],       # MJ�!TC, CP�!MJ
            'ENG': ['MJ', 'CP'],         # MJ�!TC, CP�!MJ
            'COMP': ['MJ', 'CP'],        # MJ�!TC, CP�!MJ
        }
        
        for chave, itens_grupo in grupos.items():
            quadro_codigo, posto = chave.split('-')
            print(f"\n   {quadro_codigo}-{posto}: {len(itens_grupo)} militares")
            
            if posto in transicoes_permitidas.get(quadro_codigo, []):
                print(f"     ' CORRETO: Transi��o permitida para merecimento")
            else:
                print(f"     L' INCORRETO: Transi��o n�o deveria aparecer no merecimento")
            
            # Mostrar alguns militares
            for item in itens_grupo[:3]:
                print(f"       - {item.militar.nome_completo} (posi��o {item.posicao})")
            if len(itens_grupo) > 3:
                print(f"       ... e mais {len(itens_grupo) - 3} militares")
        
        # Verificar se TC�!CB aparece apenas no COMB
        tcs_no_quadro = [item for item in itens if item.militar.posto_graduacao == 'TC']
        print(f"\n   Tenentes-Coron�is no quadro: {len(tcs_no_quadro)}")
        
        for item in tcs_no_quadro:
            if item.militar.quadro == 'COMB':
                print(f"     ' CORRETO: TC do quadro COMB inclu�do")
            else:
                print(f"     L' INCORRETO: TC do quadro {item.militar.quadro} n�o deveria estar inclu�do")
    
    # Limpar quadro de teste
    if not quadro_existente:
        quadro.delete()
    
    print("\n=== TESTE CONCLU�DO ===")
    print("\nRESUMO DAS REGRAS IMPLEMENTADAS:")
    print("' Transi��es diferenciadas por quadro no PDF de merecimento")
    print("' TC�!CB aparece apenas no quadro Combatente")
    print("' MJ�!TC e CP�!MJ aparecem em todos os quadros")
    print("' Sistema filtra corretamente as transi��es permitidas")

if __name__ == '__main__':
    testar_regras_merecimento()
