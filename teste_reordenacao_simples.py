#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def teste_reordenacao_simples():
    print("=== TESTE REORDENAÇÃO SIMPLES ===")
    
    # Buscar qualquer militar ativo
    militar = Militar.objects.filter(situacao='AT').first()
    
    if not militar:
        print("❌ Nenhum militar ativo encontrado")
        return
    
    print(f"Testando com: {militar.nome_completo} ({militar.posto_graduacao} - {militar.quadro})")
    print(f"Antiguidade atual: {militar.numeracao_antiguidade}")
    
    # Buscar outros militares do mesmo posto/quadro
    outros = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=militar.posto_graduacao,
        quadro=militar.quadro
    ).exclude(pk=militar.pk).order_by('numeracao_antiguidade')
    
    print(f"\nOutros militares do mesmo grupo:")
    for m in outros:
        print(f"  {m.numeracao_antiguidade}º - {m.nome_completo}")
    
    if outros.count() == 0:
        print("❌ Não há outros militares no mesmo grupo para testar")
        return
    
    # Simular alteração da antiguidade
    numeracao_anterior = militar.numeracao_antiguidade
    nova_numeracao = 1  # Mover para 1º
    
    print(f"\nSimulando alteração de {numeracao_anterior} para {nova_numeracao}")
    
    # Alterar a numeração
    militar.numeracao_antiguidade = nova_numeracao
    militar.save(update_fields=['numeracao_antiguidade'])
    
    # Chamar reordenação manualmente
    militar.reordenar_numeracoes_apos_alteracao(numeracao_anterior)
    
    # Verificar resultado
    print(f"\nAPÓS reordenação:")
    print(f"  Militar testado: {militar.numeracao_antiguidade}º - {militar.nome_completo}")
    
    outros_atualizados = Militar.objects.filter(
        situacao='AT',
        posto_graduacao=militar.posto_graduacao,
        quadro=militar.quadro
    ).exclude(pk=militar.pk).order_by('numeracao_antiguidade')
    
    for m in outros_atualizados:
        print(f"  {m.numeracao_antiguidade}º - {m.nome_completo}")
    
    # Verificar duplicidade
    numeracoes = [m.numeracao_antiguidade for m in Militar.objects.filter(
        situacao='AT',
        posto_graduacao=militar.posto_graduacao,
        quadro=militar.quadro
    )]
    
    duplicatas = [n for n in numeracoes if numeracoes.count(n) > 1]
    
    if duplicatas:
        print(f"\n❌ PROBLEMA: Números duplicados encontrados: {duplicatas}")
    else:
        print(f"\n✅ SUCESSO: Nenhum número duplicado encontrado")

if __name__ == "__main__":
    teste_reordenacao_simples() 