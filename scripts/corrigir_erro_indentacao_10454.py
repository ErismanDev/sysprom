import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Verificar se o arquivo tem pelo menos 10454 linhas
if len(linhas) >= 10454:
    # Verificar as linhas problemáticas
    linha_10453 = linhas[10453].strip()
    linha_10454 = linhas[10454].strip()
    
    print(f"Linha 10453: '{linha_10453}'")
    print(f"Linha 10454: '{linha_10454}'")
    
    # Se a linha 10454 contém o import problemático
    if 'from .forms import UsuarioForm' in linha_10454:
        # Verificar se a linha 10453 é uma definição de função
        if linha_10453.startswith('def ') or linha_10453.startswith('class '):
            # Remover a linha 10454 (import dentro da função)
            del linhas[10454]
            print("Import removido da função!")
            
            # Adicionar pass se a função ficou vazia
            if len(linhas) > 10453 and linhas[10453].strip().endswith(':'):
                linhas.insert(10454, '    pass\n')
                print("Adicionado 'pass' para função vazia!")
        else:
            # Se não é uma função, apenas remover a indentação
            linhas[10454] = linha_10454 + '\n'
            print("Corrigida indentação do import!")

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print("Correção aplicada!") 