#!/usr/bin/env python
"""
Script para testar o deslocamento sequencial quando um militar é movido
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_deslocamento_sequencial():
    print("=== TESTE DE DESLOCAMENTO SEQUENCIAL ===\n")
    
    # Buscar militares ativos do mesmo posto/quadro
    militares_teste = Militar.objects.filter(
        situacao='AT',
        posto_graduacao='1S',
        quadro='PRACAS'
    ).order_by('numeracao_antiguidade')[:6]  # Pegar os 6 primeiros
    
    if len(militares_teste) < 6:
        print("❌ Não há militares suficientes para teste")
        return
    
    print("📋 SITUAÇÃO INICIAL (primeiros 6):")
    for i, militar in enumerate(militares_teste, 1):
        print(f"   {i}º - {militar.nome_completo} (antiguidade: {militar.numeracao_antiguidade})")
    
    # Escolher o 3º militar para mover para 2º
    militar_para_mover = militares_teste[2]  # 3º da lista
    posicao_original = militar_para_mover.numeracao_antiguidade
    nova_posicao = 2
    
    print(f"\n🔄 MOVENDO MILITAR:")
    print(f"   Militar: {militar_para_mover.nome_completo}")
    print(f"   De: {posicao_original}º")
    print(f"   Para: {nova_posicao}º")
    
    # Fazer a alteração
    militar_para_mover.numeracao_antiguidade = nova_posicao
    militar_para_mover.save()
    
    # Verificar resultado
    militares_depois = Militar.objects.filter(
        posto_graduacao=militar_para_mover.posto_graduacao,
        quadro=militar_para_mover.quadro,
        situacao='AT'
    ).order_by('numeracao_antiguidade')[:6]
    
    print(f"\n📋 SITUAÇÃO FINAL (primeiros 6):")
    for i, militar in enumerate(militares_depois, 1):
        print(f"   {i}º - {militar.nome_completo} (antiguidade: {militar.numeracao_antiguidade})")
    
    # Verificar se o militar foi movido corretamente
    militar_atualizado = Militar.objects.get(pk=militar_para_mover.pk)
    print(f"\n📊 RESULTADO:")
    print(f"   Antiguidade atual: {militar_atualizado.numeracao_antiguidade}")
    print(f"   Antiguidade esperada: {nova_posicao}")
    
    if militar_atualizado.numeracao_antiguidade == nova_posicao:
        print(f"✅ SUCESSO: Militar movido para a posição correta!")
    else:
        print(f"❌ FALHA: Militar não foi movido corretamente!")
    
    # Verificar se não há duplicação
    numeracoes = list(militares_depois.values_list('numeracao_antiguidade', flat=True))
    numeracoes_unicas = set(numeracoes)
    
    if len(numeracoes) == len(numeracoes_unicas):
        print(f"✅ SUCESSO: Não há duplicação de números de antiguidade!")
    else:
        print(f"❌ FALHA: Há duplicação de números de antiguidade!")
        print(f"   Total: {len(numeracoes)}, Únicos: {len(numeracoes_unicas)}")

if __name__ == "__main__":
    testar_deslocamento_sequencial() 