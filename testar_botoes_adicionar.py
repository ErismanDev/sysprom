#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import QuadroAcesso

def testar_botoes_adicionar():
    print("=== TESTE DOS BOTÕES ADICIONAR ===\n")
    
    # Verificar quadros manuais com diferentes status
    quadros_manuais = QuadroAcesso.objects.filter(is_manual=True)
    
    if not quadros_manuais.exists():
        print("❌ Nenhum quadro manual encontrado!")
        return
    
    print(f"✅ {quadros_manuais.count()} quadro(s) manual(is) encontrado(s)")
    
    for quadro in quadros_manuais:
        print(f"\n--- Quadro Manual ID {quadro.id} ---")
        print(f"   Tipo: {quadro.get_tipo_display()}")
        print(f"   Status: {quadro.get_status_display()}")
        print(f"   Critério: {quadro.criterio_ordenacao_manual}")
        print(f"   Militares: {quadro.itemquadroacesso_set.count()}")
        
        # Verificar onde o botão deve aparecer
        if quadro.status == 'ELABORADO':
            print("   ✅ Botão 'Adicionar Militar' aparece no cabeçalho do quadro")
        elif quadro.status == 'EM_ELABORACAO':
            print("   ✅ Botão 'Adicionar Militar' aparece em card separado (em elaboração)")
        elif quadro.status == 'NAO_ELABORADO':
            print("   ✅ Botão 'Adicionar Militar' aparece em card separado (não elaborado)")
        else:
            print("   ❓ Status não reconhecido")
    
    print(f"\n=== INSTRUÇÕES PARA TESTAR ===")
    print("1. Acesse um quadro manual na interface web")
    print("2. Verifique se o botão 'Adicionar Militar' aparece:")
    print("   - No cabeçalho do quadro (se elaborado)")
    print("   - Em um card separado (se em elaboração ou não elaborado)")
    print("3. Clique no botão e teste a funcionalidade")
    print("4. O botão deve abrir o modal de adição de militar")

if __name__ == '__main__':
    testar_botoes_adicionar() 