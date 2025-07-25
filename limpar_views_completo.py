#!/usr/bin/env python
import re

def limpar_views_completo():
    """Remove todas as funções duplicadas do arquivo views.py mantendo apenas a primeira ocorrência"""
    
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
    
    # Para cada função duplicada, manter apenas a primeira ocorrência
    for funcao in funcoes_duplicadas:
        print(f"Processando função: {funcao}")
        
        # Padrão para encontrar a função
        pattern = rf'@login_required\s*\ndef {funcao}\(.*?\):(.*?)(?=@login_required\s*\ndef|\Z)'
        
        # Encontrar todas as ocorrências
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if len(matches) > 1:
            print(f"  - Encontradas {len(matches)} ocorrências de {funcao}")
            
            # Manter apenas a primeira ocorrência
            primeira_ocorrencia = matches[0]
            outras_ocorrencias = matches[1:]
            
            # Remover as outras ocorrências
            for match in reversed(outras_ocorrencias):
                start = match.start()
                end = match.end()
                content = content[:start] + content[end:]
                print(f"  - Removida ocorrência em posição {start}-{end}")
    
    # Salvar o arquivo limpo
    with open('militares/views_limpo_final.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nArquivo limpo salvo como: militares/views_limpo_final.py")
    print(f"Tamanho original: {len(open('militares/views.py', 'r', encoding='utf-8').read())} caracteres")
    print(f"Tamanho limpo: {len(content)} caracteres")

if __name__ == "__main__":
    limpar_views_completo() 