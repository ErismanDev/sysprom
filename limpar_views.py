#!/usr/bin/env python
import re

def limpar_views():
    """Remove funções duplicadas do arquivo views.py"""
    
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lista de funções que estão duplicadas
    funcoes_duplicadas = [
        'ficha_conceito_list',
        'ficha_conceito_create', 
        'militar_list',
        'militar_detail',
        'militar_create',
        'militar_update',
        'militar_delete',
        'militar_search_ajax',
        'militar_dashboard',
        'quadro_acesso_list',
        'quadro_acesso_detail'
    ]
    
    # Manter apenas a primeira ocorrência de cada função
    for funcao in funcoes_duplicadas:
        # Encontrar todas as ocorrências da função
        pattern = rf'@login_required\s*\ndef {funcao}\(.*?\):(.*?)(?=@login_required\s*\ndef|\Z)'
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if len(matches) > 1:
            print(f'Encontradas {len(matches)} ocorrências de {funcao}')
            
            # Manter apenas a primeira ocorrência
            for i, match in enumerate(matches[1:], 1):
                start = match.start()
                end = match.end()
                content = content[:start] + content[end:]
                print(f'  Removida ocorrência {i+1} de {funcao}')
    
    # Salvar o arquivo limpo
    with open('militares/views_limpo.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('\nArquivo limpo salvo como militares/views_limpo.py')
    print('Verifique o arquivo e depois renomeie para views.py')

if __name__ == '__main__':
    limpar_views() 