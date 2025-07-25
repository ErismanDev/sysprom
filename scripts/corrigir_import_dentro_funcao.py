import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Verificar a linha 10454 (índice 10453)
if len(linhas) > 10453:
    linha_10453 = linhas[10453].strip()
    linha_10454 = linhas[10454].strip()
    
    print(f"Linha 10453: {linha_10453}")
    print(f"Linha 10454: {linha_10454}")
    
    # Se a linha 10453 é uma definição de função e a 10454 é um import
    if (linha_10453.startswith('def ') or linha_10453.startswith('class ')) and 'from .forms import UsuarioForm' in linha_10454:
        # Remover o import da função
        del linhas[10454]
        print("Import removido da função!")
        
        # Verificar se já existe o import no topo do arquivo
        import_existe = False
        for i, linha in enumerate(linhas):
            if 'from .forms import UsuarioForm' in linha and not linha.startswith('    '):
                import_existe = True
                break
        
        if not import_existe:
            # Adicionar o import no topo
            for i, linha in enumerate(linhas):
                if linha.strip().startswith('from .forms import') and not linha.startswith('    '):
                    linhas.insert(i + 1, 'from .forms import UsuarioForm\n')
                    break
            print("Import adicionado no topo do arquivo!")

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print("Correção aplicada!") 