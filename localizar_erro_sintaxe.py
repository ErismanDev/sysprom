#!/usr/bin/env python
import ast
import sys

def localizar_erro_sintaxe(arquivo):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        # Verificar linha por linha
        for i, linha in enumerate(linhas, 1):
            try:
                # Tentar compilar até esta linha
                codigo_ate_linha = ''.join(linhas[:i])
                ast.parse(codigo_ate_linha)
            except SyntaxError as e:
                print(f"❌ Erro de sintaxe encontrado na linha {i}:")
                print(f"   Erro: {e.msg}")
                print(f"   Linha {i}: {linha.strip()}")
                if i > 1:
                    print(f"   Linha {i-1}: {linhas[i-2].strip()}")
                if i < len(linhas):
                    print(f"   Linha {i+1}: {linhas[i].strip()}")
                return False
            except Exception as e:
                print(f"❌ Erro inesperado na linha {i}: {e}")
                return False
        
        print(f"✅ Arquivo {arquivo} tem sintaxe válida!")
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar {arquivo}: {e}")
        return False

if __name__ == "__main__":
    arquivo = "militares/views.py"
    localizar_erro_sintaxe(arquivo) 