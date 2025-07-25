#!/usr/bin/env python
"""
Script para testar a funcionalidade de reativação com restauração da numeração de antiguidade
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_reativacao_antiguidade():
    """Testa a funcionalidade de reativação com restauração da numeração de antiguidade"""
    
    print("=== TESTE DE REATIVAÇÃO COM RESTAURAÇÃO DE ANTIGUIDADE ===\n")
    
    # 1. Buscar um militar ativo para testar
    militar_teste = Militar.objects.filter(situacao='AT').first()
    
    if not militar_teste:
        print("❌ Nenhum militar ativo encontrado para teste")
        return
    
    print(f"📊 MILITAR SELECIONADO PARA TESTE:")
    print(f"   Nome: {militar_teste.nome_completo}")
    print(f"   Posto: {militar_teste.get_posto_graduacao_display()}")
    print(f"   Quadro: {militar_teste.get_quadro_display()}")
    print(f"   Antiguidade atual: {militar_teste.numeracao_antiguidade}")
    print(f"   Situação atual: {militar_teste.get_situacao_display()}")
    
    # 2. Verificar militares do mesmo posto/quadro
    militares_mesmo_posto = Militar.objects.filter(
        posto_graduacao=militar_teste.posto_graduacao,
        quadro=militar_teste.quadro,
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    print(f"\n📋 MILITARES DO MESMO POSTO/QUADRO (ANTES):")
    for militar in militares_mesmo_posto:
        print(f"   {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # 3. Simular inativação
    print(f"\n🔄 SIMULANDO INATIVAÇÃO:")
    antiguidade_original = militar_teste.numeracao_antiguidade
    militar_teste.situacao = 'IN'
    militar_teste.save()
    
    print(f"   Antiguidade salva: {militar_teste.numeracao_antiguidade_anterior}")
    print(f"   Antiguidade atual: {militar_teste.numeracao_antiguidade}")
    
    # 4. Verificar reordenação após inativação
    militares_apos_inativacao = Militar.objects.filter(
        posto_graduacao=militar_teste.posto_graduacao,
        quadro=militar_teste.quadro,
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    print(f"\n📋 MILITARES DO MESMO POSTO/QUADRO (APÓS INATIVAÇÃO):")
    for militar in militares_apos_inativacao:
        print(f"   {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # 5. Simular reativação
    print(f"\n🔄 SIMULANDO REATIVAÇÃO:")
    militar_teste.situacao = 'AT'
    militar_teste.save()
    
    print(f"   Antiguidade restaurada: {militar_teste.numeracao_antiguidade}")
    print(f"   Antiguidade anterior (deve ser None): {militar_teste.numeracao_antiguidade_anterior}")
    
    # 6. Verificar resultado final
    militares_final = Militar.objects.filter(
        posto_graduacao=militar_teste.posto_graduacao,
        quadro=militar_teste.quadro,
        situacao='AT'
    ).order_by('numeracao_antiguidade')
    
    print(f"\n📋 MILITARES DO MESMO POSTO/QUADRO (APÓS REATIVAÇÃO):")
    for militar in militares_final:
        print(f"   {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    # 7. Verificar se a antiguidade foi restaurada
    if militar_teste.numeracao_antiguidade == antiguidade_original:
        print(f"\n✅ SUCESSO: Antiguidade restaurada corretamente!")
        print(f"   Original: {antiguidade_original}")
        print(f"   Restaurada: {militar_teste.numeracao_antiguidade}")
    else:
        print(f"\n❌ FALHA: Antiguidade não foi restaurada corretamente!")
        print(f"   Original: {antiguidade_original}")
        print(f"   Atual: {militar_teste.numeracao_antiguidade}")

if __name__ == "__main__":
    testar_reativacao_antiguidade() 