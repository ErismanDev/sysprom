with open('militares/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(419, 440):  # linhas 420 a 440 (índice começa em 0)
    if i < len(lines):
        l = lines[i].lstrip()
        # Linhas principais do bloco
        if l.startswith('context = {') or l.startswith('# Montar lista final:') or l.startswith('return render('):
            lines[i] = '    ' + l
        # Linhas do dicionário context
        elif (
            l.startswith("'militar':") or
            l.startswith("'fichas':") or
            l.startswith("'total_oficiais_ativos':") or
            l.startswith("'total_fichas_oficiais':") or
            l.startswith("'oficiais_sem_ficha':") or
            l.startswith("'oficiais_com_ficha':") or
            l.startswith("'is_oficiais':")
        ):
            lines[i] = '        ' + l
        # Fecha dicionário
        elif l.startswith('}'): 
            lines[i] = '    ' + l

with open('militares/views.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Indentação das linhas 420-440 zerada e corrigida para 4/8 espaços!') 