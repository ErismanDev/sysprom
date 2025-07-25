import os

ARQUIVO = os.path.join(os.path.dirname(__file__), '../militares/views.py')

with open(ARQUIVO, 'r', encoding='utf-8') as f:
    linhas = f.readlines()

nova_linha = "    permissoes_atuais = set(\n        (p.modulo, p.acesso)\n        for p in PermissaoFuncao.objects.filter(cargo_funcao=cargo)\n    )\n"

with open(ARQUIVO, 'w', encoding='utf-8') as f:
    for linha in linhas:
        if "permissoes_atuais = PermissaoFuncao.objects.filter(cargo_funcao=cargo).values_list('permissao_id', flat=True)" in linha:
            f.write(nova_linha)
        else:
            f.write(linha)

print('Linha de permissoes_atuais corrigida com sucesso!') 