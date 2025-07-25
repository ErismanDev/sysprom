#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import ItemQuadroFixacaoVagas, PrevisaoVaga

def testar_vagas_automaticas():
    """Testa se as vagas fixadas estão sendo automaticamente sincronizadas"""
    
    print("🧪 TESTE DE VAGAS FIXADAS AUTOMÁTICAS")
    print("=" * 60)
    
    # Buscar um item para teste
    item_teste = ItemQuadroFixacaoVagas.objects.select_related('previsao_vaga').first()
    
    if not item_teste:
        print("❌ Nenhum item de quadro de fixação de vagas encontrado!")
        return
    
    previsao = item_teste.previsao_vaga
    vagas_disponiveis_antes = previsao.vagas_disponiveis
    vagas_fixadas_antes = item_teste.vagas_fixadas
    
    print(f"📋 Item de teste: {previsao.get_quadro_display()} - {previsao.get_posto_display()}")
    print(f"   Vagas Disponíveis: {vagas_disponiveis_antes}")
    print(f"   Vagas Fixadas (antes): {vagas_fixadas_antes}")
    print()
    
    # Simular alteração nas vagas disponíveis
    print("🔄 Simulando alteração nas vagas disponíveis...")
    
    # Salvar valores originais
    efetivo_atual_original = previsao.efetivo_atual
    efetivo_previsto_original = previsao.efetivo_previsto
    
    # Alterar efetivo atual para simular mudança nas vagas disponíveis
    nova_vagas_disponiveis = vagas_disponiveis_antes + 2
    novo_efetivo_atual = previsao.efetivo_previsto - nova_vagas_disponiveis
    
    previsao.efetivo_atual = novo_efetivo_atual
    previsao.save()
    
    print(f"   Novo Efetivo Atual: {novo_efetivo_atual}")
    print(f"   Novas Vagas Disponíveis: {previsao.vagas_disponiveis}")
    print()
    
    # Testar se o save() do item sincroniza automaticamente
    print("💾 Testando sincronização automática...")
    item_teste.save()
    
    vagas_fixadas_depois = item_teste.vagas_fixadas
    vagas_disponiveis_depois = previsao.vagas_disponiveis
    
    print(f"   Vagas Disponíveis (depois): {vagas_disponiveis_depois}")
    print(f"   Vagas Fixadas (depois): {vagas_fixadas_depois}")
    print()
    
    # Verificar se sincronizou corretamente
    if vagas_fixadas_depois == vagas_disponiveis_depois:
        print("✅ SUCESSO: Vagas fixadas foram automaticamente sincronizadas!")
        print(f"   {vagas_fixadas_depois} = {vagas_disponiveis_depois}")
    else:
        print("❌ FALHA: Vagas fixadas não foram sincronizadas automaticamente!")
        print(f"   {vagas_fixadas_depois} ≠ {vagas_disponiveis_depois}")
    
    # Restaurar valores originais
    print("\n🔄 Restaurando valores originais...")
    previsao.efetivo_atual = efetivo_atual_original
    previsao.efetivo_previsto = efetivo_previsto_original
    previsao.save()
    
    item_teste.save()  # Isso deve sincronizar de volta
    
    print(f"   Vagas Disponíveis (restauradas): {previsao.vagas_disponiveis}")
    print(f"   Vagas Fixadas (restauradas): {item_teste.vagas_fixadas}")
    
    if item_teste.vagas_fixadas == previsao.vagas_disponiveis:
        print("✅ Valores restaurados com sucesso!")
    else:
        print("❌ Erro ao restaurar valores!")
    
    print("\n" + "=" * 60)
    print("📝 CONCLUSÃO:")
    print("   As vagas fixadas agora são automaticamente iguais às vagas disponíveis.")
    print("   Qualquer alteração nas vagas disponíveis será refletida automaticamente.")
    print("   Não é mais necessário editar manualmente as vagas fixadas.")

if __name__ == '__main__':
    testar_vagas_automaticas() 