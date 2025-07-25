#!/usr/bin/env python
"""
Script para corrigir erro de sintaxe nas importações
"""
import re

def corrigir_imports():
    """Corrige as importações malformadas"""
    
    print("🔧 CORRIGINDO ERRO DE SINTAXE")
    print("=" * 50)
    
    # Ler o arquivo
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir as linhas problemáticas
    # Linha 1: from .decorators import (incompleta)
    content = re.sub(
        r'from \.decorators import\s*\n',
        'from .decorators import usuario_comissao_required, usuario_cpo_required, usuario_cpp_required, apenas_visualizacao_comissao, administracao_required, militar_edit_permission, comissao_acesso_total, cargos_especiais_required\n',
        content
    )
    
    # Linha 2: from .admin_decorators import ... (malformada)
    content = re.sub(
        r'from \.admin_decorators import admin_bypass, admin_or_permission_required usuario_comissao_required, usuario_cpo_required, usuario_cpp_required, apenas_visualizacao_comissao, administracao_required, militar_edit_permission, comissao_acesso_total, cargos_especiais_required',
        'from .admin_decorators import admin_bypass, admin_or_permission_required',
        content
    )
    
    # Remover linhas duplicadas de import
    lines = content.split('\n')
    cleaned_lines = []
    seen_imports = set()
    
    for line in lines:
        if line.strip().startswith('from .admin_decorators import'):
            if 'admin_decorators' not in seen_imports:
                cleaned_lines.append(line)
                seen_imports.add('admin_decorators')
        else:
            cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Salvar arquivo
    with open('militares/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Erro de sintaxe corrigido!")

if __name__ == "__main__":
    corrigir_imports() 