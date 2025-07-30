#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Correção simples - comentar sorted() problemático
"""

def corrigir_simples():
    """Comenta a parte problemática do sorted()"""
    
    print("🔧 Aplicando correção simples...")
    
    try:
        # Ler o arquivo
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fazer backup
        with open('militares/views.py.backup_simples', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Backup criado")
        
        # Substituir sorted() por order_by() simples
        old_code = '''        militares = sorted(militares, key=lambda x: (
            hierarquia_postos.get(x.posto_graduacao, 999),
            # Para Subtenentes (ST), ordenar por CHO primeiro (True vem antes de False)
            (x.posto_graduacao == 'ST' and not x.curso_cho, x.posto_graduacao == 'ST' and x.curso_cho),
            x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
            x.nome_completo
        ))'''
        
        new_code = '''        # OTIMIZAÇÃO: Usar order_by simples em vez de sorted() em Python
        militares = militares.order_by('posto_graduacao', 'numeracao_antiguidade', 'nome_completo')'''
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            
            # Salvar arquivo
            with open('militares/views.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Correção aplicada!")
            return True
        else:
            print("⚠️ Código não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    corrigir_simples() 