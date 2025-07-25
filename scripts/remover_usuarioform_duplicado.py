import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Encontrar e remover a definição duplicada do UsuarioForm
inicio_remocao = None
fim_remocao = None

for i, linha in enumerate(linhas):
    if 'class UsuarioForm(forms.ModelForm):' in linha and '"""Formulário para criação/edição de usuários"""' in linhas[i+1]:
        inicio_remocao = i
        # Procurar o fim da classe (próxima classe ou função)
        for j in range(i+1, len(linhas)):
            if linhas[j].strip().startswith('class ') or linhas[j].strip().startswith('@login_required'):
                fim_remocao = j
                break
        break

if inicio_remocao is not None and fim_remocao is not None:
    # Remover a definição duplicada
    linhas = linhas[:inicio_remocao] + linhas[fim_remocao:]
    
    # Adicionar import do UsuarioForm no início do arquivo
    import_added = False
    for i, linha in enumerate(linhas):
        if 'from .forms import' in linha:
            if 'UsuarioForm' not in linha:
                linhas[i] = linha.rstrip() + ', UsuarioForm\n'
            import_added = True
            break
        elif 'from .models import' in linha:
            # Adicionar após os imports de models
            linhas.insert(i+1, 'from .forms import UsuarioForm\n')
            import_added = True
            break
    
    if not import_added:
        # Adicionar no início do arquivo se não encontrar outros imports
        for i, linha in enumerate(linhas):
            if linha.strip().startswith('from django'):
                linhas.insert(i, 'from .forms import UsuarioForm\n')
                break

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print('Definição duplicada do UsuarioForm removida e import adicionado!') 