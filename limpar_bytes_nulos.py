#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def limpar_bytes_nulos(arquivo):
    """Remove bytes nulos de um arquivo"""
    try:
        # Ler o arquivo em modo binário
        with open(arquivo, 'rb') as f:
            conteudo = f.read()
        
        # Contar bytes nulos
        bytes_nulos = conteudo.count(b'\x00')
        print(f"Encontrados {bytes_nulos} bytes nulos no arquivo {arquivo}")
        
        if bytes_nulos > 0:
            # Remover bytes nulos
            conteudo_limpo = conteudo.replace(b'\x00', b'')
            
            # Salvar o arquivo limpo
            with open(arquivo, 'wb') as f:
                f.write(conteudo_limpo)
            
            print(f"Bytes nulos removidos com sucesso!")
            return True
        else:
            print("Nenhum byte nulo encontrado.")
            return False
            
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return False

if __name__ == "__main__":
    arquivo = "militares/views.py"
    limpar_bytes_nulos(arquivo) 