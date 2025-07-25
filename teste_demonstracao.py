#!/usr/bin/env python
"""
Demonstração da funcionalidade de reordenação
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def demonstrar_funcionalidade():
    """Demonstra a funcionalidade movendo um militar da posição 3 para 1"""
    
    print("=== DEMONSTRAÇÃO DA FUNCIONALIDADE ===")
    
    # Buscar militares de teste
    militares = Militar.objects.filter(
        nome_completo__startswith='TESTE'
    ).order_by('numeracao_antiguidade')
    
    if militares.count() < 3:
        print("❌ Precisa de pelo menos 3 militares de teste.")
        return
    
    print("Estado inicial:")
    for militar in militares:
        print(f"  - {militar.nome_completo}: {militar.numeracao_antiguidade}º")
    
    # Pegar o militar da posição 3
    militar_3 = militares.filter(numeracao_antiguidade=3).first()
    if not militar_3:
        print("❌ Não encontrou militar na posição 3.")
        return
    
    print(f"\nMovendo {militar_3.nome_completo} da posição 3 para 1...")
    
    # Salvar numeração anterior
    numeracao_anterior = militar_3.numeracao_antiguidade
    
    # Alterar para posição 1
    militar_3.numeracao_antiguidade = 1
    militar_3.save()
    
    # Chamar reordenação
    militar_3.reordenar_numeracoes_apos_alteracao(numeracao_anterior)
    
    # Verificar resultado
    print("\nEstado após reordenação:")
    militares_atualizados = Militar.objects.filter(
        nome_completo__startswith='TESTE'
    ).order_by('numeracao_antiguidade')
    
    for militar in militares_atualizados:
        print(f"  - {militar.nome_completo}: {militar.numeracao_antiguidade}º")
    
    # Verificar se não há duplicatas
    numeracoes = [m.numeracao_antiguidade for m in militares_atualizados if m.numeracao_antiguidade]
    duplicatas = len(numeracoes) != len(set(numeracoes))
    
    if duplicatas:
        print("❌ ERRO: Há numerações duplicadas!")
    else:
        print("✅ SUCESSO: Reordenação funcionou corretamente!")
    
    # Restaurar estado original
    print(f"\nRestaurando {militar_3.nome_completo} para posição 3...")
    militar_3.numeracao_antiguidade = 3
    militar_3.save()
    militar_3.reordenar_numeracoes_apos_alteracao(1)
    
    print("Estado restaurado:")
    militares_final = Militar.objects.filter(
        nome_completo__startswith='TESTE'
    ).order_by('numeracao_antiguidade')
    
    for militar in militares_final:
        print(f"  - {militar.nome_completo}: {militar.numeracao_antiguidade}º")

if __name__ == "__main__":
    demonstrar_funcionalidade() 