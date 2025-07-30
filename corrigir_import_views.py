#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Corrigir import no arquivo views.py
"""

def corrigir_import():
    """Corrige o import do Django no arquivo views.py"""
    
    print("🔧 Corrigindo import no arquivo views.py...")
    
    try:
        # Ler o arquivo
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir o import
        old_import = "from django.db.models import Q, Sum, Count"
        new_import = "from django.db.models import Q, Sum, Count, Case, When, IntegerField"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            # Salvar o arquivo
            with open('militares/views.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Import corrigido com sucesso!")
            return True
        else:
            print("⚠️ Import não encontrado ou já corrigido")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao corrigir import: {e}")
        return False

if __name__ == '__main__':
    corrigir_import() 