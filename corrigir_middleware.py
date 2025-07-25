#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corrigir automaticamente os caminhos de exclusão no middleware.
"""

def corrigir_middleware():
    caminho = 'militares/middleware.py'
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Corrigir os caminhos de exclusão para incluir o prefixo /militares/
    novo_conteudo = conteudo.replace(
        "'/selecionar-funcao/',",
        "'/militares/selecionar-funcao/',"
    )
    novo_conteudo = novo_conteudo.replace(
        "'/trocar-funcao/',",
        "'/militares/trocar-funcao/',"
    )
    
    if conteudo != novo_conteudo:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        print('Middleware corrigido com sucesso!')
        print('Caminhos de exclusão atualizados para incluir o prefixo /militares/')
    else:
        print('Nenhuma alteração necessária no middleware.')

if __name__ == '__main__':
    corrigir_middleware() 