#!/usr/bin/env python
import ast
import sys

def verificar_sintaxe(arquivo):
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Tentar compilar o código
        ast.parse(conteudo)
        print(f"✅ Arquivo {arquivo} tem sintaxe válida!")
        return True
    except SyntaxError as e:
        print(f"❌ Erro de sintaxe em {arquivo}:")
        print(f"   Linha {e.lineno}: {e.msg}")
        print(f"   Posição: {e.offset}")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar {arquivo}: {e}")
        return False

if __name__ == "__main__":
    arquivo = "militares/views.py"
    verificar_sintaxe(arquivo) 