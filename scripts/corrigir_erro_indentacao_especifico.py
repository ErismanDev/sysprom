import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

print(f"Total de linhas no arquivo: {len(linhas)}")

# Verificar se o arquivo tem pelo menos 10454 linhas
if len(linhas) >= 10454:
    # Verificar as linhas problemáticas
    linha_10453 = linhas[10453].strip()
    linha_10454 = linhas[10454].strip()
    
    print(f"Linha 10453: '{linha_10453}'")
    print(f"Linha 10454: '{linha_10454}'")
    
    # Se a linha 10454 contém o import problemático
    if 'from .forms import UsuarioForm' in linha_10454:
        print("Encontrado import problemático na linha 10454!")
        
        # Verificar se a linha 10453 é uma definição de função
        if linha_10453.startswith('def ') or linha_10453.startswith('class '):
            print("Linha 10453 é uma definição de função/classe!")
            
            # Remover a linha 10454 (import dentro da função)
            del linhas[10454]
            print("Import removido da função!")
            
            # Verificar se a função ficou vazia e adicionar pass
            if len(linhas) > 10453 and linhas[10453].strip().endswith(':'):
                linhas.insert(10454, '    pass\n')
                print("Adicionado 'pass' para função vazia!")
        else:
            print("Linha 10453 não é uma definição de função!")
            # Se não é uma função, apenas remover a indentação
            linhas[10454] = linha_10454 + '\n'
            print("Corrigida indentação do import!")
    else:
        print("Import não encontrado na linha 10454!")
        # Procurar por imports mal indentados em todo o arquivo
        for i, linha in enumerate(linhas):
            if 'from .forms import UsuarioForm' in linha and linha.startswith('    '):
                print(f"Encontrado import mal indentado na linha {i+1}")
                # Remover a linha mal indentada
                del linhas[i]
                print(f"Import removido da linha {i+1}!")
                break

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print("Correção aplicada!") 