#!/usr/bin/env python
"""
Script para corrigir todas as vagas disponíveis no banco de dados
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import PrevisaoVaga

def corrigir_vagas_disponiveis():
    """Corrige todas as vagas disponíveis no banco de dados"""
    
    print("=== CORRIGINDO VAGAS DISPONÍVEIS ===\n")
    
    # Buscar todas as previsões de vagas
    previsoes = PrevisaoVaga.objects.all()
    
    print(f"📊 Encontradas {previsoes.count()} previsões de vagas")
    
    corrigidas = 0
    for previsao in previsoes:
        # Calcular o valor correto
        valor_correto = max(0, previsao.efetivo_previsto - previsao.efetivo_atual)
        
        # Verificar se precisa corrigir
        if previsao.vagas_disponiveis != valor_correto:
            print(f"🔧 Corrigindo {previsao.get_posto_display()} - {previsao.get_quadro_display()}:")
            print(f"   Efetivo Atual: {previsao.efetivo_atual}")
            print(f"   Efetivo Previsto: {previsao.efetivo_previsto}")
            print(f"   Vagas Disponíveis (atual): {previsao.vagas_disponiveis}")
            print(f"   Vagas Disponíveis (correto): {valor_correto}")
            
            # Corrigir
            previsao.vagas_disponiveis = valor_correto
            previsao.save(update_fields=['vagas_disponiveis'])
            
            print(f"   ✅ Corrigido!")
            corrigidas += 1
        else:
            print(f"✅ {previsao.get_posto_display()} - {previsao.get_quadro_display()}: {previsao.vagas_disponiveis} (já correto)")
    
    print(f"\n📈 RESUMO:")
    print(f"   Total de previsões: {previsoes.count()}")
    print(f"   Previsões corrigidas: {corrigidas}")
    print(f"   Previsões já corretas: {previsoes.count() - corrigidas}")

if __name__ == "__main__":
    corrigir_vagas_disponiveis() 