import os

CAMINHO_ARQUIVO = "militares/views.py"

def substituir_funcao():
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        conteudo = f.read()

    novo_conteudo = conteudo.replace(
        "funcao_atual = obter_funcao_atual_usuario(assinatura.assinado_por)",
        "funcao_atual = obter_funcao_atual_usuario(assinatura.assinado_por, request)"
    )

    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)

    print("Substituição concluída com sucesso!")

if __name__ == "__main__":
    substituir_funcao() 