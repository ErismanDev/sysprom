#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoPracas, FichaConceitoOficiais
from datetime import date

def testar_atualizacao_ficha():
    """Testa se a ficha de conceito está sendo atualizada corretamente após promoção"""
    
    print("=== TESTE DE ATUALIZAÇÃO DA FICHA DE CONCEITO ===\n")
    
    # Buscar um subtenente com ficha de praças
    subtenente = Militar.objects.filter(
        posto_graduacao='ST',
        quadro='PRACAS',
        situacao='AT'
    ).first()
    
    if not subtenente:
        print("❌ Nenhum subtenente encontrado para teste!")
        return
    
    print(f"Subtenente selecionado: {subtenente.nome_completo}")
    print(f"ID: {subtenente.id}")
    print(f"Posto atual: {subtenente.get_posto_graduacao_display()}")
    print(f"Quadro atual: {subtenente.get_quadro_display()}")
    print(f"Tempo no posto: {subtenente.tempo_posto_atual()} anos")
    
    # Verificar ficha de praças atual
    ficha_pracas = subtenente.fichaconceitopracas_set.first()
    if ficha_pracas:
        print(f"\n📋 FICHA DE PRACAS ATUAL:")
        print(f"   Tempo no posto: {ficha_pracas.tempo_posto} anos")
        print(f"   Cursos CHO: {ficha_pracas.cursos_cho}")
        print(f"   Cursos CFSD: {ficha_pracas.cursos_cfsd}")
        print(f"   Cursos CHC: {ficha_pracas.cursos_chc}")
        print(f"   Cursos CHSGT: {ficha_pracas.cursos_chsgt}")
        print(f"   Cursos CAS: {ficha_pracas.cursos_cas}")
        print(f"   Cursos Superior: {ficha_pracas.cursos_civis_superior}")
        print(f"   Pontos: {ficha_pracas.pontos}")
    else:
        print("❌ Nenhuma ficha de praças encontrada!")
        return
    
    # Simular promoção para 2º tenente
    print(f"\n🔄 SIMULANDO PROMOÇÃO PARA 2º TENENTE...")
    
    # Salvar dados anteriores
    posto_anterior = subtenente.posto_graduacao
    quadro_anterior = subtenente.quadro
    
    # Atualizar posto e quadro
    subtenente.posto_graduacao = '2T'
    subtenente.quadro = 'COMP'
    subtenente.data_promocao_atual = date.today()
    subtenente.save()
    
    print(f"✅ Posto atualizado para: {subtenente.get_posto_graduacao_display()}")
    print(f"✅ Quadro atualizado para: {subtenente.get_quadro_display()}")
    
    # Converter ficha
    ficha_oficiais, mensagem = subtenente.converter_ficha_pracas_para_oficiais(
        motivo_conversao="Teste de promoção"
    )
    
    if ficha_oficiais:
        print(f"\n📋 FICHA DE OFICIAIS CONVERTIDA:")
        print(f"   Tempo no posto: {ficha_oficiais.tempo_posto} anos")
        print(f"   Cursos CHO: {ficha_oficiais.cursos_cho}")
        print(f"   Cursos CFSD: {ficha_oficiais.cursos_cfsd}")
        print(f"   Cursos CHC: {ficha_oficiais.cursos_chc}")
        print(f"   Cursos CHSGT: {ficha_oficiais.cursos_chsgt}")
        print(f"   Cursos CAS: {ficha_oficiais.cursos_cas}")
        print(f"   Cursos Superior: {ficha_oficiais.cursos_civis_superior}")
        print(f"   Pontos: {ficha_oficiais.pontos}")
        print(f"   Observações: {ficha_oficiais.observacoes}")
        
        # Verificar se os dados foram atualizados
        tempo_atual = subtenente.tempo_posto_atual()
        if ficha_oficiais.tempo_posto == tempo_atual:
            print(f"✅ Tempo no posto atualizado corretamente: {tempo_atual} anos")
        else:
            print(f"❌ Tempo no posto não atualizado! Esperado: {tempo_atual}, Atual: {ficha_oficiais.tempo_posto}")
        
        # Verificar se os cursos foram marcados corretamente
        if subtenente.curso_cho and ficha_oficiais.cursos_cho == 1:
            print("✅ Curso CHO marcado corretamente")
        elif not subtenente.curso_cho and ficha_oficiais.cursos_cho == 0:
            print("✅ Curso CHO não marcado (correto)")
        else:
            print(f"❌ Curso CHO inconsistente! Militar: {subtenente.curso_cho}, Ficha: {ficha_oficiais.cursos_cho}")
        
    else:
        print(f"❌ Erro na conversão: {mensagem}")
    
    # Restaurar dados originais
    subtenente.posto_graduacao = posto_anterior
    subtenente.quadro = quadro_anterior
    subtenente.save()
    
    print(f"\n🔄 Dados restaurados para teste")
    print(f"✅ Teste concluído!")

if __name__ == "__main__":
    testar_atualizacao_ficha() 