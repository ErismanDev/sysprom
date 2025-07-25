#!/usr/bin/env python
"""
Script para testar o cálculo de vagas disponíveis
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import PrevisaoVaga

def testar_calculo_vagas():
    """Testa o cálculo de vagas disponíveis"""
    
    print("=== TESTE DO CÁLCULO DE VAGAS DISPONÍVEIS ===\n")
    
    # Buscar uma previsão de vaga para testar
    previsao = PrevisaoVaga.objects.filter(posto='CB', quadro='COMB').first()
    
    if not previsao:
        print("❌ Nenhuma previsão de vaga encontrada para CB/COMB")
        return
    
    print(f"📊 PREVISÃO DE VAGA TESTE:")
    print(f"   Posto: {previsao.get_posto_display()}")
    print(f"   Quadro: {previsao.get_quadro_display()}")
    print(f"   Efetivo Atual: {previsao.efetivo_atual}")
    print(f"   Efetivo Previsto: {previsao.efetivo_previsto}")
    print(f"   Vagas Disponíveis (atual): {previsao.vagas_disponiveis}")
    
    # Testar o cálculo manual
    calculo_manual = max(0, previsao.efetivo_previsto - previsao.efetivo_atual)
    print(f"   Cálculo Manual: {previsao.efetivo_previsto} - {previsao.efetivo_atual} = {calculo_manual}")
    
    # Testar o método do modelo
    calculo_modelo = previsao.calcular_vagas_disponiveis()
    print(f"   Cálculo do Modelo: {calculo_modelo}")
    
    # Verificar se estão iguais
    if calculo_manual == calculo_modelo:
        print("✅ Cálculo manual e do modelo estão iguais")
    else:
        print("❌ Cálculo manual e do modelo estão diferentes!")
    
    # Testar o save
    print(f"\n🔄 TESTANDO O SAVE:")
    print(f"   Vagas Disponíveis antes do save: {previsao.vagas_disponiveis}")
    
    # Alterar valores e salvar
    previsao.efetivo_atual = 5
    previsao.efetivo_previsto = 6
    previsao.save()
    
    print(f"   Vagas Disponíveis após save: {previsao.vagas_disponiveis}")
    
    # Recarregar do banco
    previsao.refresh_from_db()
    print(f"   Vagas Disponíveis após refresh: {previsao.vagas_disponiveis}")
    
    # Verificar se o cálculo está correto
    esperado = max(0, 6 - 5)  # 1
    if previsao.vagas_disponiveis == esperado:
        print("✅ Cálculo correto após save!")
    else:
        print(f"❌ Cálculo incorreto! Esperado: {esperado}, Obtido: {previsao.vagas_disponiveis}")

if __name__ == "__main__":
    testar_calculo_vagas() 