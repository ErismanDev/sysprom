import os

CAMINHO_ARQUIVO = "militares/views.py"

def substituir_funcao_sessao():
    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Substituir a chamada da função para usar a sessão diretamente
    novo_conteudo = conteudo.replace(
        "funcao_atual = obter_funcao_atual_usuario(assinatura.assinado_por, request)",
        "funcao_atual = request.session.get('funcao_atual_nome', 'Usuário do Sistema') if request and hasattr(request, 'session') else 'Usuário do Sistema'"
    )

    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
        f.write(novo_conteudo)

    print("Substituição da função da sessão concluída com sucesso!")

if __name__ == "__main__":
    substituir_funcao_sessao() 