#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corrigir automaticamente os redirects de 'militares:home' para 'militares:militar_dashboard'
no arquivo militares/views.py.
"""

def corrigir_redirects():
    caminho = 'militares/views.py'
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    novo_conteudo = conteudo.replace(
        "'militares:home'", "'militares:militar_dashboard'"
    )
    # Também corrige nos GET/POST de next
    novo_conteudo = novo_conteudo.replace(
        "request.GET.get('next', 'militares:home')", "request.GET.get('next', 'militares:militar_dashboard')"
    )
    novo_conteudo = novo_conteudo.replace(
        "request.POST.get('next', 'militares:home')", "request.POST.get('next', 'militares:militar_dashboard')"
    )
    
    if conteudo != novo_conteudo:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        print('Redirects corrigidos com sucesso!')
    else:
        print('Nenhuma alteração necessária.')

if __name__ == '__main__':
    corrigir_redirects() 