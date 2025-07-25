import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Verificar se já existe o import correto
import_usuarioform = 'from .forms import UsuarioForm\n'
if any(import_usuarioform.strip() in linha.strip() for linha in linhas):
    print('Import do UsuarioForm já existe.')
else:
    # Encontrar o último import de forms
    idx = None
    for i, linha in enumerate(linhas):
        if linha.strip().startswith('from .forms import'):
            idx = i
    if idx is not None:
        linhas.insert(idx + 1, import_usuarioform)
    else:
        # Se não encontrar, adicionar após os imports de models
        for i, linha in enumerate(linhas):
            if linha.strip().startswith('from .models import'):
                linhas.insert(i + 1, import_usuarioform)
                break
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print('Import do UsuarioForm adicionado com sucesso!') 