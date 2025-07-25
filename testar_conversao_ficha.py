#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, FichaConceitoPracas, FichaConceitoOficiais

def testar_conversao_ficha():
    """Testa a funcionalidade de conversão automática de ficha de praças para oficiais"""
    
    print("=== TESTE DE CONVERSÃO AUTOMÁTICA DE FICHA ===\n")
    
    # Buscar um militar com ficha de praças
    militar_com_ficha_pracas = None
    
    # Tentar encontrar um militar com ficha de praças
    ficha_pracas = FichaConceitoPracas.objects.first()
    if ficha_pracas:
        militar_com_ficha_pracas = ficha_pracas.militar
        print(f"✅ Militar encontrado com ficha de praças: {militar_com_ficha_pracas.nome_completo}")
        print(f"   Posto atual: {militar_com_ficha_pracas.get_posto_graduacao_display()}")
        print(f"   Quadro atual: {militar_com_ficha_pracas.get_quadro_display()}")
        print(f"   ID da ficha de praças: {ficha_pracas.id}")
    else:
        print("❌ Nenhuma ficha de praças encontrada no sistema!")
        return
    
    # Verificar se o militar já tem ficha de oficiais
    if militar_com_ficha_pracas.fichaconceitooficiais_set.exists():
        print("⚠️  Militar já possui ficha de oficiais!")
        return
    
    # Simular mudança de quadro de praças para oficiais
    print(f"\n🔄 Simulando mudança de quadro: PRACAS -> COMP")
    print(f"   Posto anterior: {militar_com_ficha_pracas.posto_graduacao}")
    print(f"   Quadro anterior: {militar_com_ficha_pracas.quadro}")
    
    # Salvar dados anteriores
    posto_anterior = militar_com_ficha_pracas.posto_graduacao
    quadro_anterior = militar_com_ficha_pracas.quadro
    
    # Alterar para quadro de oficiais
    militar_com_ficha_pracas.quadro = 'COMP'
    militar_com_ficha_pracas.posto_graduacao = '2T'
    
    print(f"   Novo posto: {militar_com_ficha_pracas.posto_graduacao}")
    print(f"   Novo quadro: {militar_com_ficha_pracas.quadro}")
    
    # Salvar para acionar a conversão automática
    militar_com_ficha_pracas.save()
    
    # Verificar se a conversão foi realizada
    print(f"\n📋 Verificando conversão...")
    
    # Verificar se ainda existe ficha de praças
    ficha_pracas_atual = militar_com_ficha_pracas.fichaconceitopracas_set.first()
    if ficha_pracas_atual:
        print(f"❌ Ficha de praças ainda existe: {ficha_pracas_atual.id}")
    else:
        print(f"✅ Ficha de praças foi removida")
    
    # Verificar se foi criada ficha de oficiais
    ficha_oficiais = militar_com_ficha_pracas.fichaconceitooficiais_set.first()
    if ficha_oficiais:
        print(f"✅ Ficha de oficiais criada: {ficha_oficiais.id}")
        print(f"   Observações: {ficha_oficiais.observacoes}")
        print(f"   Pontos: {ficha_oficiais.pontos}")
    else:
        print(f"❌ Ficha de oficiais não foi criada")
    
    # Restaurar dados originais para não afetar o sistema
    print(f"\n🔄 Restaurando dados originais...")
    militar_com_ficha_pracas.quadro = quadro_anterior
    militar_com_ficha_pracas.posto_graduacao = posto_anterior
    militar_com_ficha_pracas.save()
    
    print(f"✅ Teste concluído!")

if __name__ == "__main__":
    testar_conversao_ficha() 