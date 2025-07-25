import re

CAMINHO = "militares/views.py"

with open(CAMINHO, encoding="utf-8") as f:
    conteudo = f.read()

# Regex para encontrar o bloco duplicado e mal formatado
padrao = re.compile(
    r"""messages\.success\(request, mensagem\)\n\s*# Redirecionar para a view correta baseada na categoria\nif novo_quadro\.categoria == 'PRACAS':\n\s*return redirect\('militares:quadro_acesso_pracas_detail', pk=novo_quadro\.pk\)\nelse:\n\s*# Redirecionar para a view correta baseada na categoria\n\s*if novo_quadro\.categoria == 'PRACAS':\n\s*return redirect\('militares:quadro_acesso_pracas_detail', pk=novo_quadro\.pk\)\n\s*else:\n\s*return redirect\('militares:quadro_acesso_detail', pk=novo_quadro\.pk\)""",
    re.MULTILINE,
)

# Substituição pelo bloco correto
substituto = (
    "messages.success(request, mensagem)\n"
    "                # Redirecionar para a view correta baseada na categoria\n"
    "                if novo_quadro.categoria == 'PRACAS':\n"
    "                    return redirect('militares:quadro_acesso_pracas_detail', pk=novo_quadro.pk)\n"
    "                else:\n"
    "                    return redirect('militares:quadro_acesso_detail', pk=novo_quadro.pk)"
)

novo_conteudo, n = padrao.subn(substituto, conteudo)

if n > 0:
    with open(CAMINHO, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    print(f"Corrigido {n} bloco(s) duplicado(s) em {CAMINHO}.")
else:
    print("Nenhum bloco duplicado encontrado para corrigir.") 