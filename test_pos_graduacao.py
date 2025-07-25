#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def test_pos_graduacao():
    print("=== TESTE: Pós-Graduação para Major e Tenente-Coronel do Quadro Complementar ===\n")
    
    # Teste 1: Major do Complementar sem Pós-Graduação
    print("1. Testando Major do Complementar SEM Pós-Graduação:")
    major_sem_pos = Militar.objects.create(
        matricula='123456',
        nome_completo='Major Teste Sem Pós',
        nome_guerra='Teste',
        cpf='12345678901',
        data_nascimento=date(1980, 1, 1),
        quadro='COMP',
        posto_graduacao='MJ',
        data_ingresso=date(2010, 1, 1),
        data_promocao_atual=date(2020, 1, 1),
        curso_formacao_oficial=False,
        curso_aperfeicoamento_oficial=False,
        curso_superior=True,
        pos_graduacao=False,  # SEM PÓS-GRADUAÇÃO
        curso_csbm=False
    )
    
    apto_major_sem_pos = major_sem_pos.apto_promocao_antiguidade()
    print(f"   Major sem Pós-Graduação - Apto para promoção: {'Sim' if apto_major_sem_pos else 'Não'}")
    
    # Teste 2: Major do Complementar com Pós-Graduação
    print("\n2. Testando Major do Complementar COM Pós-Graduação:")
    major_com_pos = Militar.objects.create(
        matricula='123457',
        nome_completo='Major Teste Com Pós',
        nome_guerra='Teste2',
        cpf='12345678902',
        data_nascimento=date(1980, 1, 1),
        quadro='COMP',
        posto_graduacao='MJ',
        data_ingresso=date(2010, 1, 1),
        data_promocao_atual=date(2020, 1, 1),
        curso_formacao_oficial=False,
        curso_aperfeicoamento_oficial=False,
        curso_superior=True,
        pos_graduacao=True,  # COM PÓS-GRADUAÇÃO
        curso_csbm=False
    )
    
    apto_major_com_pos = major_com_pos.apto_promocao_antiguidade()
    print(f"   Major com Pós-Graduação - Apto para promoção: {'Sim' if apto_major_com_pos else 'Não'}")
    
    # Teste 3: Tenente-Coronel do Complementar sem Pós-Graduação
    print("\n3. Testando Tenente-Coronel do Complementar SEM Pós-Graduação:")
    tc_sem_pos = Militar.objects.create(
        matricula='123458',
        nome_completo='TC Teste Sem Pós',
        nome_guerra='Teste3',
        cpf='12345678903',
        data_nascimento=date(1980, 1, 1),
        quadro='COMP',
        posto_graduacao='TC',
        data_ingresso=date(2010, 1, 1),
        data_promocao_atual=date(2020, 1, 1),
        curso_formacao_oficial=False,
        curso_aperfeicoamento_oficial=False,
        curso_superior=True,
        pos_graduacao=False,  # SEM PÓS-GRADUAÇÃO
        curso_csbm=True
    )
    
    apto_tc_sem_pos = tc_sem_pos.apto_promocao_antiguidade()
    print(f"   TC sem Pós-Graduação - Apto para promoção: {'Sim' if apto_tc_sem_pos else 'Não'}")
    
    # Teste 4: Tenente-Coronel do Complementar com Pós-Graduação
    print("\n4. Testando Tenente-Coronel do Complementar COM Pós-Graduação:")
    tc_com_pos = Militar.objects.create(
        matricula='123459',
        nome_completo='TC Teste Com Pós',
        nome_guerra='Teste4',
        cpf='12345678904',
        data_nascimento=date(1980, 1, 1),
        quadro='COMP',
        posto_graduacao='TC',
        data_ingresso=date(2010, 1, 1),
        data_promocao_atual=date(2020, 1, 1),
        curso_formacao_oficial=False,
        curso_aperfeicoamento_oficial=False,
        curso_superior=True,
        pos_graduacao=True,  # COM PÓS-GRADUAÇÃO
        curso_csbm=True
    )
    
    apto_tc_com_pos = tc_com_pos.apto_promocao_antiguidade()
    print(f"   TC com Pós-Graduação - Apto para promoção: {'Sim' if apto_tc_com_pos else 'Não'}")
    
    # Teste 5: Verificar aptidão para quadro de acesso
    print("\n5. Testando aptidão para quadro de acesso:")
    apto_quadro_major_sem_pos, msg_major_sem_pos = major_sem_pos.apto_quadro_acesso()
    apto_quadro_major_com_pos, msg_major_com_pos = major_com_pos.apto_quadro_acesso()
    apto_quadro_tc_sem_pos, msg_tc_sem_pos = tc_sem_pos.apto_quadro_acesso()
    apto_quadro_tc_com_pos, msg_tc_com_pos = tc_com_pos.apto_quadro_acesso()
    
    print(f"   Major sem Pós-Graduação - Apto para quadro: {'Sim' if apto_quadro_major_sem_pos else 'Não'} ({msg_major_sem_pos})")
    print(f"   Major com Pós-Graduação - Apto para quadro: {'Sim' if apto_quadro_major_com_pos else 'Não'} ({msg_major_com_pos})")
    print(f"   TC sem Pós-Graduação - Apto para quadro: {'Sim' if apto_quadro_tc_sem_pos else 'Não'} ({msg_tc_sem_pos})")
    print(f"   TC com Pós-Graduação - Apto para quadro: {'Sim' if apto_quadro_tc_com_pos else 'Não'} ({msg_tc_com_pos})")
    
    # Limpeza
    Militar.objects.filter(matricula__in=['123456', '123457', '123458', '123459']).delete()
    
    print("\n=== RESULTADO ESPERADO ===")
    print("Major sem Pós-Graduação: Não apto")
    print("Major com Pós-Graduação: Apto")
    print("TC sem Pós-Graduação: Não apto")
    print("TC com Pós-Graduação: Apto")
    print("\nTeste concluído!")

if __name__ == '__main__':
    test_pos_graduacao() 