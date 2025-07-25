import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Lista de imports que devem estar no topo
imports_para_mover = []
linhas_para_remover = []

# Encontrar imports mal indentados
for i, linha in enumerate(linhas):
    linha_stripped = linha.strip()
    if (linha_stripped.startswith('from django import') or 
        linha_stripped.startswith('from .forms import') or
        linha_stripped.startswith('from .models import') or
        linha_stripped.startswith('import django') or
        linha_stripped.startswith('from django')) and linha.startswith('    '):
        # Se o import está indentado, adicionar à lista para mover
        imports_para_mover.append(linha_stripped)
        linhas_para_remover.append(i)

# Remover linhas indentadas
for i in reversed(linhas_para_remover):
    del linhas[i]

# Adicionar imports no topo (após os imports existentes)
if imports_para_mover:
    # Encontrar onde termina a seção de imports
    idx_inserir = 0
    for i, linha in enumerate(linhas):
        if not linha.strip().startswith(('from ', 'import ')) and linha.strip():
            idx_inserir = i
            break
    
    # Inserir imports no local correto
    for import_line in imports_para_mover:
        linhas.insert(idx_inserir, import_line + '\n')
        idx_inserir += 1

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print(f'Corrigidos {len(imports_para_mover)} imports mal indentados!') 