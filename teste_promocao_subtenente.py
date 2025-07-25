#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, Promocao

def testar_promocao_subtenente():
    """Testa a promoção de subtenente exatamente como a view faz"""
    
    # Buscar militar de teste
    militar = Militar.objects.filter(nome_completo='TESTE PROMOÇÃO 2').first()
    if not militar:
        print("Militar de teste não encontrado!")
        return
    
    print("=== TESTE DE PROMOÇÃO DE SUBTENENTE ===")
    print(f"Militar: {militar.nome_completo}")
    print(f"ID: {militar.pk}")
    print(f"Posto atual: {militar.posto_graduacao}")
    print(f"Quadro atual: {militar.quadro}")
    print(f"Data promoção atual: {militar.data_promocao_atual}")
    
    # Verificar se é subtenente do quadro praças
    if militar.posto_graduacao != 'ST' or militar.quadro != 'PRACAS':
        print("ERRO: Militar não é subtenente do quadro praças!")
        return
    
    # Capturar dados anteriores
    posto_anterior = militar.posto_graduacao
    quadro_anterior = militar.quadro
    
    # Data de promoção
    data_promocao = date(2025, 7, 15)
    
    print(f"\n=== APLICANDO PROMOÇÃO ===")
    print(f"Posto anterior: {posto_anterior}")
    print(f"Quadro anterior: {quadro_anterior}")
    print(f"Nova data: {data_promocao}")
    
    # Atualizar posto e quadro (exatamente como na view)
    militar.posto_graduacao = '2T'  # 2º Tenente
    militar.quadro = 'COMP'  # Complementar
    militar.data_promocao_atual = data_promocao
    
    print(f"Posto novo definido: {militar.posto_graduacao}")
    print(f"Quadro novo definido: {militar.quadro}")
    print(f"Data nova definida: {militar.data_promocao_atual}")
    
    # Aplicar nova numeração por promoção
    nova_numeracao = militar.atribuir_numeracao_por_promocao(posto_anterior, quadro_anterior)
    print(f"Nova numeração: {nova_numeracao}")
    
    # Reordenar os militares do posto anterior
    militares_reordenados = militar.reordenar_posto_anterior_apos_promocao(posto_anterior, quadro_anterior)
    print(f"Militares reordenados: {militares_reordenados}")
    
    # Converter ficha de conceito
    ficha_oficiais, mensagem_conversao = militar.converter_ficha_pracas_para_oficiais(
        motivo_conversao="Promoção de Subtenente para 2º Tenente"
    )
    print(f"Conversão ficha: {mensagem_conversao}")
    
    # SALVAR AS ALTERAÇÕES
    print("\n=== SALVANDO ALTERAÇÕES ===")
    militar.save()
    print("Militar salvo!")
    
    # Verificar se foi salvo corretamente
    militar.refresh_from_db()
    print(f"Posto após save: {militar.posto_graduacao}")
    print(f"Quadro após save: {militar.quadro}")
    print(f"Data após save: {militar.data_promocao_atual}")
    
    # Registrar promoção no histórico
    Promocao.objects.create(
        militar=militar,
        posto_anterior=posto_anterior,
        posto_novo='2T',
        criterio='ANTIGUIDADE',
        data_promocao=data_promocao,
        data_publicacao=data_promocao,
        numero_ato='Promoção automática via sistema',
        observacoes=f'Promoção de Subtenente (Praças) para 2º Tenente (Complementar). Nova numeração: {nova_numeracao}º.'
    )
    print("Promoção registrada no histórico!")
    
    print("\n=== RESULTADO FINAL ===")
    print(f"Militar: {militar.nome_completo}")
    print(f"Posto: {militar.posto_graduacao}")
    print(f"Quadro: {militar.quadro}")
    print(f"Data Promoção: {militar.data_promocao_atual}")
    print(f"Numeração: {militar.numeracao_antiguidade}")
    
    return militar

if __name__ == "__main__":
    militar = testar_promocao_subtenente()
    if militar:
        print(f"\n✅ Teste concluído! Militar {militar.nome_completo} promovido com sucesso!")
    else:
        print("\n❌ Teste falhou!") 