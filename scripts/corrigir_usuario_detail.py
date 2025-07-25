import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

# Encontrar e corrigir a função usuario_detail
for i, linha in enumerate(linhas):
    if 'def usuario_detail(request, pk):' in linha:
        # Procurar pela linha que define funcoes_usuario
        for j in range(i, min(i + 20, len(linhas))):
            if 'funcoes_usuario = usuario.funcoes.filter' in linhas[j]:
                # Adicionar inicialização antes
                linhas.insert(j-1, '    funcoes_usuario = []  # Inicializar com lista vazia\n')
                break
        break

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    f.writelines(linhas)

print('Função usuario_detail corrigida com sucesso!') 