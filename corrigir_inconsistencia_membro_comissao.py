#!/usr/bin/env python
"""
Script para corrigir inconsistência no membro de comissão
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import MembroComissao

def corrigir_inconsistencia():
    """Corrige a inconsistência encontrada no membro de comissão"""
    
    print("=== CORRIGINDO INCONSISTÊNCIA NO MEMBRO DE COMISSÃO ===\n")
    
    # Buscar membros inconsistentes (militares inativos com membros de comissão ativos)
    membros_inconsistentes = MembroComissao.objects.filter(
        militar__situacao__in=['IN', 'TR', 'AP', 'EX'],
        ativo=True
    )
    
    if membros_inconsistentes.exists():
        print(f"Encontrados {membros_inconsistentes.count()} membros inconsistentes:")
        
        for membro in membros_inconsistentes:
            print(f"  - {membro.militar.nome_completo} ({membro.militar.get_situacao_display()}) - {membro.comissao.nome}")
            print(f"    Militar: {membro.militar.situacao} | Membro Ativo: {membro.ativo}")
            
            # Corrigir a inconsistência
            membro.ativo = False
            membro.save()
            
            print(f"    ✅ Corrigido: Membro marcado como inativo")
            print()
    else:
        print("Nenhuma inconsistência encontrada!")
    
    print("=== CORREÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    corrigir_inconsistencia() 