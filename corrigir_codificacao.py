#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def corrigir_codificacao(arquivo):
    """Corrige a codificação de um arquivo"""
    try:
        # Ler o arquivo em modo binário
        with open(arquivo, 'rb') as f:
            conteudo = f.read()
        
        # Tentar decodificar com diferentes codificações
        codificacoes = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for codificacao in codificacoes:
            try:
                texto = conteudo.decode(codificacao)
                print(f"Arquivo decodificado com sucesso usando {codificacao}")
                
                # Salvar com codificação UTF-8
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(texto)
                
                print(f"Arquivo salvo com codificação UTF-8")
                return True
                
            except UnicodeDecodeError:
                continue
        
        print("Não foi possível decodificar o arquivo com nenhuma codificação conhecida")
        return False
        
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return False

if __name__ == "__main__":
    arquivo = "militares/views.py"
    corrigir_codificacao(arquivo) 