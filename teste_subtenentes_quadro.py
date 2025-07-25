#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso, Intersticio

def testar_subtenentes_quadro_acesso():
    print("=== TESTE DETALHADO DE SUBTENENTES NO QUADRO DE ACESSO ===\n")
    
    # 1. Verificar subtenentes existentes
    subtenentes = Militar.objects.filter(posto_graduacao='ST')
    print(f"Subtenentes encontrados: {subtenentes.count()}")
    
    for st in subtenentes:
        print(f"\n--- ANÁLISE DO SUBTENENTE: {st.nome_completo} ---")
        print(f"Quadro: {st.get_quadro_display()}")
        print(f"Situação: {st.get_situacao_display()}")
        print(f"Data de promoção atual: {st.data_promocao_atual}")
        print(f"Tempo no posto atual: {st.tempo_posto_atual()} anos")
        print(f"Inspeção de saúde válida: {'Sim' if st.apto_inspecao_saude else 'Não'}")
        
        # Verificar cursos específicos
        if st.quadro == 'COMP':
            print(f"Possui CHO: {'Sim' if st.curso_cho else 'Não'}")
        elif st.quadro == 'COMB':
            print(f"Próxima promoção seria para: Aspirante")
        else:
            print(f"Próxima promoção seria para: 2º Tenente")
    
    # 2. Verificar interstícios configurados para subtenentes
    print(f"\n--- INTERSTÍCIOS CONFIGURADOS PARA SUBTENENTES ---")
    intersticios_st = Intersticio.objects.filter(posto='ST')
    print(f"Interstícios configurados: {intersticios_st.count()}")
    
    for inter in intersticios_st:
        print(f"- {inter.get_quadro_display()}: {inter.tempo_formatado()}")
    
    # 3. Criar um quadro de acesso de teste para subtenentes
    print(f"\n--- CRIANDO QUADRO DE ACESSO DE TESTE ---")
    
    # Data de promoção futura
    data_promocao_teste = date.today() + timedelta(days=30)
    
    # Testar para cada quadro
    quadros_teste = ['COMB', 'COMP']
    
    for quadro_teste in quadros_teste:
        print(f"\nTestando quadro: {quadro_teste}")
        
        # Criar quadro de acesso de teste
        quadro_teste_obj = QuadroAcesso(
            tipo='ANTIGUIDADE',
            posto='ST',
            quadro=quadro_teste,
            data_promocao=data_promocao_teste,
            status='EM_ELABORACAO'
        )
        
        # Verificar militares aptos
        militares_aptos = quadro_teste_obj.militares_aptos()
        militares_inaptos = quadro_teste_obj.militares_inaptos_com_motivo()
        
        print(f"Militares aptos: {len(militares_aptos)}")
        print(f"Militares inaptos: {len(militares_inaptos)}")
        
        # Mostrar detalhes dos inaptos
        for item in militares_inaptos:
            print(f"  - {item['militar'].nome_completo}: {item['motivo']}")
        
        # Testar validação individual para cada subtenente
        subtenentes_quadro = Militar.objects.filter(
            posto_graduacao='ST',
            quadro=quadro_teste,
            situacao='AT'
        )
        
        print(f"\nValidação individual para {quadro_teste}:")
        for st in subtenentes_quadro:
            apto, motivo = quadro_teste_obj.validar_requisitos_quadro_acesso(st)
            print(f"  - {st.nome_completo}: {'Apto' if apto else 'Inapto'} - {motivo}")
            
            # Verificar cada validação separadamente
            print(f"    * Interstício: {'OK' if quadro_teste_obj._validar_intersticio_minimo(st, data_promocao_teste) else 'FALHA'}")
            print(f"    * Inspeção de saúde: {'OK' if quadro_teste_obj._validar_inspecao_saude(st) else 'FALHA'}")
            print(f"    * Cursos inerentes: {'OK' if quadro_teste_obj._validar_cursos_inerentes(st) else 'FALHA'}")
    
    # 4. Verificar se há problemas na lógica de validação
    print(f"\n--- ANÁLISE DA LÓGICA DE VALIDAÇÃO ---")
    
    # Verificar se subtenentes do quadro Combatente precisam de cursos específicos
    print("Verificando cursos obrigatórios para subtenentes:")
    
    cursos_obrigatorios = {
        'COMB': {
            'ST': []  # Subtenente do Combatente não tem cursos obrigatórios definidos
        },
        'COMP': {
            'ST': ['curso_cho']  # Subtenente do Complementar precisa CHO
        }
    }
    
    for quadro, postos in cursos_obrigatorios.items():
        for posto, cursos in postos.items():
            print(f"  - {quadro}/{posto}: {cursos if cursos else 'Nenhum curso obrigatório'}")
    
    # 5. Verificar se há subtenentes sem interstício configurado
    print(f"\n--- VERIFICAÇÃO DE INTERSTÍCIOS ---")
    
    for st in Militar.objects.filter(posto_graduacao='ST', situacao='AT'):
        try:
            intersticio = Intersticio.objects.get(
                posto='ST',
                quadro=st.quadro,
                ativo=True
            )
            print(f"  - {st.nome_completo} ({st.get_quadro_display()}): {intersticio.tempo_formatado()}")
        except Intersticio.DoesNotExist:
            print(f"  - {st.nome_completo} ({st.get_quadro_display()}): INTERSTÍCIO NÃO CONFIGURADO")

if __name__ == '__main__':
    testar_subtenentes_quadro_acesso() 