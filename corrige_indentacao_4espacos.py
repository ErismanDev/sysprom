import re

with open('militares/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

nova_lines = []
inside_func = False
for i, line in enumerate(lines):
    if 'def ficha_conceito_list' in line:
        inside_func = True
    if inside_func and (line.strip().startswith('context = {') or line.strip().startswith('# Montar lista final:')):
        line = '    ' + line.lstrip()
    if inside_func and line.strip().startswith('return render('):
        line = '    ' + line.lstrip()
        inside_func = False  # Considera que a função termina após o return
    # Corrige linhas do dicionário context
    if inside_func and (
        line.lstrip().startswith("'militar':") or
        line.lstrip().startswith("'fichas':") or
        line.lstrip().startswith("'total_oficiais_ativos':") or
        line.lstrip().startswith("'total_fichas_oficiais':") or
        line.lstrip().startswith("'oficiais_sem_ficha':") or
        line.lstrip().startswith("'oficiais_com_ficha':") or
        line.lstrip().startswith("'is_oficiais':")
    ):
        line = '        ' + line.lstrip()
    nova_lines.append(line)

with open('militares/views.py', 'w', encoding='utf-8') as f:
    f.writelines(nova_lines)

print('Indentação ajustada para 4 espaços!') 