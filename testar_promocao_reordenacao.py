#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def testar_promocao_reordenacao():
    """Testa a reordenação após promoção"""
    
    print("=== TESTE DE REORDENAÇÃO APÓS PROMOÇÃO ===\n")
    
    # Escolher um posto para testar (ex: 1T - 1º Tenente)
    posto_teste = '1T'
    
    print(f"📊 Testando promoção para posto: {posto_teste}")
    
    # Listar militares ANTES da promoção
    print(f"\n📋 Militares ANTES da promoção:")
    militares_antes = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto_teste
    ).order_by('numeracao_antiguidade')
    
    for m in militares_antes:
        print(f"  - {m.nome_completo}: {m.numeracao_antiguidade}º")
    
    if militares_antes.count() < 2:
        print("❌ Precisa de pelo menos 2 militares no posto para testar")
        return
    
    # Escolher o militar que será promovido (o 1º)
    militar_promover = militares_antes.first()
    posto_anterior = militar_promover.posto_graduacao
    
    print(f"\n🚀 Promovendo {militar_promover.nome_completo} (atual {militar_promover.numeracao_antiguidade}º)")
    
    # Simular promoção
    posto_novo = 'CP'  # 1º Tenente promovendo para Capitão
    
    print(f"📈 De {posto_anterior} para {posto_novo}")
    
    # Atualizar posto
    militar_promover.posto_graduacao = posto_novo
    
    # Atribuir numeração no novo posto
    nova_numeracao = militar_promover.atribuir_numeracao_por_promocao(posto_anterior, militar_promover.quadro)
    
    # Reordenar os militares do posto anterior
    militares_reordenados = militar_promover.reordenar_posto_anterior_apos_promocao(posto_anterior, militar_promover.quadro)
    
    # Salvar
    militar_promover.save()
    
    print(f"✅ Promoção realizada!")
    print(f"📊 Novo posto: {militar_promover.posto_graduacao} (numeração: {militar_promover.numeracao_antiguidade})")
    print(f"🔄 {militares_reordenados} militares reordenados no posto anterior")
    
    # Listar militares DEPOIS da promoção (posto anterior)
    print(f"\n📋 Militares DEPOIS da promoção (posto anterior):")
    militares_depois = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=posto_anterior
    ).order_by('numeracao_antiguidade')
    
    for m in militares_depois:
        print(f"  - {m.nome_completo}: {m.numeracao_antiguidade}º")
    
    # Verificar se a reordenação funcionou
    print(f"\n🔍 Verificação:")
    print(f"  - Militar promovido: {militar_promover.nome_completo} agora é {militar_promover.get_posto_graduacao_display()} {militar_promover.numeracao_antiguidade}º")
    
    # Mostrar como os outros "subiram"
    for m in militares_depois:
        print(f"  - {m.nome_completo} agora é {m.numeracao_antiguidade}º")
    
    print(f"\n✅ Teste concluído!")

if __name__ == "__main__":
    testar_promocao_reordenacao() 