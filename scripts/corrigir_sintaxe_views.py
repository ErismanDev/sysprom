import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Corrigir a linha problemática (linha 19)
for i, linha in enumerate(linhas):
    if 'from .models import (' in linha and 'from .forms import UsuarioForm' in linhas[i+1]:
        # Remover a linha problemática e reorganizar os imports
        linhas[i] = 'from .models import (\n'
        linhas[i+1] = '    Militar, FichaConceitoOficiais, FichaConceitoPracas, QuadroAcesso, ItemQuadroAcesso, \n'
        break

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print('Erro de sintaxe corrigido no arquivo views.py!') 