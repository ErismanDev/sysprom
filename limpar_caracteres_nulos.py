#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob

def limpar_caracteres_nulos(arquivo):
    """Remove caracteres nulos de um arquivo"""
    try:
        # Ler o arquivo em modo binário
        with open(arquivo, 'rb') as f:
            conteudo = f.read()
        
        # Contar caracteres nulos
        null_count = conteudo.count(b'\x00')
        if null_count > 0:
            print(f"Encontrados {null_count} caracteres nulos em {arquivo}")
            
            # Remover caracteres nulos
            conteudo_limpo = conteudo.replace(b'\x00', b'')
            
            # Salvar o arquivo limpo
            with open(arquivo, 'wb') as f:
                f.write(conteudo_limpo)
            
            print(f"Arquivo {arquivo} limpo com sucesso!")
            return True
        else:
            print(f"Nenhum caractere nulo encontrado em {arquivo}")
            return False
    except Exception as e:
        print(f"Erro ao processar {arquivo}: {e}")
        return False

def main():
    """Função principal"""
    print("=== LIMPANDO CARACTERES NULOS DOS ARQUIVOS PYTHON ===\n")
    
    # Lista de arquivos para verificar
    arquivos_para_limpar = [
        'militares/urls.py',
        'testar_regras_merecimento.py'
    ]
    
    arquivos_limpos = 0
    
    for arquivo in arquivos_para_limpar:
        if os.path.exists(arquivo):
            if limpar_caracteres_nulos(arquivo):
                arquivos_limpos += 1
        else:
            print(f"Arquivo {arquivo} não encontrado")
    
    print(f"\n=== RESUMO ===")
    print(f"Arquivos limpos: {arquivos_limpos}")
    
    # Verificar se ainda há caracteres nulos
    print(f"\n=== VERIFICAÇÃO FINAL ===")
    for arquivo in arquivos_para_limpar:
        if os.path.exists(arquivo):
            with open(arquivo, 'rb') as f:
                conteudo = f.read()
                null_count = conteudo.count(b'\x00')
                print(f"{arquivo}: {null_count} caracteres nulos restantes")

if __name__ == '__main__':
    main() 