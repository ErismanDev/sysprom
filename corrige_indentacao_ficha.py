import re

with open('militares/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

nova_lines = []
inside_func = False
for i, line in enumerate(lines):
    if 'def ficha_conceito_list' in line:
        inside_func = True
    if inside_func and (line.strip().startswith('context = {') or line.strip().startswith('# Montar lista final:')):
        # Corrige indentação para 4 espaços
        if not line.startswith('    '):
            line = '    ' + line.lstrip()
    if inside_func and line.strip().startswith('return render('):
        if not line.startswith('    '):
            line = '    ' + line.lstrip()
        inside_func = False  # Considera que a função termina após o return
    nova_lines.append(line)

with open('militares/views.py', 'w', encoding='utf-8') as f:
    f.writelines(nova_lines)

print('Indentação corrigida!') 