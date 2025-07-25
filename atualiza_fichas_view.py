import re

# Lê o arquivo
with open('militares/views.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Regex para encontrar o bloco do contexto
padrao = re.compile(r"context = \{[^\}]+\}\s+return render\(request, 'militares/ficha_conceito_list.html', context\)", re.DOTALL)

novo_bloco = '''# Montar lista final: primeiro os sem ficha, depois os com ficha
fichas_final = oficiais_sem_ficha_list + fichas

context = {
    'militar': militar,
    'fichas': fichas_final,
    'total_oficiais_ativos': total_oficiais_ativos,
    'total_fichas_oficiais': total_fichas_oficiais,
    'oficiais_sem_ficha': oficiais_sem_ficha_list,
    'oficiais_com_ficha': fichas,
    'is_oficiais': True,
}
return render(request, 'militares/ficha_conceito_list.html', context)'''

# Substitui o bloco
novo_conteudo = padrao.sub(novo_bloco, conteudo)

# Salva o arquivo
with open('militares/views.py', 'w', encoding='utf-8') as f:
    f.write(novo_conteudo)

print('View atualizada com sucesso!') 