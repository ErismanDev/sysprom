#!/usr/bin/env python3
"""
Script para corrigir erros de sintaxe nas múltiplas definições da função gerar_quadro_acesso
"""

import re

def corrigir_views_py():
    """Corrige os erros de sintaxe no arquivo views.py"""
    
    # Ler o arquivo
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrões para encontrar e corrigir os problemas
    patterns_to_fix = [
        # Padrão 1: Código mal indentado após if sucesso
        (
            r'(if sucesso:\s*.*?messages\.success\(request, mensagem\)\s*# Redirecionar para a view correta baseada na categoria\s*)if novo_quadro\.categoria == \'PRACAS\':\s*return redirect\(\'militares:quadro_acesso_pracas_detail\', pk=novo_quadro\.pk\)\s*else:\s*# Redirecionar para a view correta baseada na categoria\s*if novo_quadro\.categoria == \'PRACAS\':\s*return redirect\(\'militares:quadro_acesso_pracas_detail\', pk=novo_quadro\.pk\)\s*else:\s*return redirect\(\'militares:quadro_acesso_detail\', pk=novo_quadro\.pk\)',
            r'\1                # Redirecionar para a view correta baseada na categoria\n                if novo_quadro.categoria == \'PRACAS\':\n                    return redirect(\'militares:quadro_acesso_pracas_detail\', pk=novo_quadro.pk)\n                else:\n                    return redirect(\'militares:quadro_acesso_detail\', pk=novo_quadro.pk)'
        ),
    ]
    
    # Aplicar as correções
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Remover definições duplicadas da função gerar_quadro_acesso
    # Manter apenas a primeira definição (linha 2091)
    
    # Encontrar todas as definições da função
    function_pattern = r'@login_required\s*def gerar_quadro_acesso\(request\):(.*?)(?=@login_required\s*def|$)'
    matches = list(re.finditer(function_pattern, content, re.DOTALL))
    
    if len(matches) > 1:
        print(f"Encontradas {len(matches)} definições da função gerar_quadro_acesso")
        
        # Manter apenas a primeira definição (que está correta)
        first_match = matches[0]
        first_function = first_match.group(0)
        
        # Remover todas as outras definições
        for i, match in enumerate(matches[1:], 1):
            print(f"Removendo definição duplicada #{i+1}")
            content = content.replace(match.group(0), '')
    
    # Escrever o arquivo corrigido
    with open('militares/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Arquivo views.py corrigido com sucesso!")

if __name__ == '__main__':
    corrigir_views_py() 