with open('militares/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == 'fichas_final = oficiais_sem_ficha_list + fichas':
        lines[i] = '    ' + line.lstrip()

with open('militares/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Indentação da linha fichas_final corrigida!') 