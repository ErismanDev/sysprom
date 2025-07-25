import os

def corrigir_views_pracas():
    """Corrigir views_pracas.py"""
    with open("militares/views_pracas.py", "r", encoding="utf-8") as f:
        conteudo = f.read()

    novo_conteudo = conteudo.replace(
        "funcao_atual = obter_funcao_atual_usuario(assinatura.assinado_por)",
        "funcao_atual = request.session.get('funcao_atual_nome', 'Usuário do Sistema') if request and hasattr(request, 'session') else 'Usuário do Sistema'"
    )

    with open("militares/views_pracas.py", "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    print("✅ views_pracas.py corrigido!")

def corrigir_views_ata():
    """Corrigir views.py - ocorrência da ata"""
    with open("militares/views.py", "r", encoding="utf-8") as f:
        conteudo = f.read()

    novo_conteudo = conteudo.replace(
        "funcao_atual = obter_funcao_atual_usuario(assinatura_eletronica.assinado_por)",
        "funcao_atual = request.session.get('funcao_atual_nome', 'Usuário do Sistema') if request and hasattr(request, 'session') else 'Usuário do Sistema'"
    )

    with open("militares/views.py", "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    print("✅ views.py (ata) corrigido!")

def corrigir_utils():
    """Corrigir utils.py"""
    with open("militares/utils.py", "r", encoding="utf-8") as f:
        conteudo = f.read()

    novo_conteudo = conteudo.replace(
        "funcao_atual = obter_funcao_atual_usuario(usuario)",
        "funcao_atual = 'Usuário do Sistema'  # Função será obtida da sessão"
    )
    
    novo_conteudo = novo_conteudo.replace(
        "funcao_atual = obter_funcao_atual_usuario(membro_comissao.usuario)",
        "funcao_atual = 'Usuário do Sistema'  # Função será obtida da sessão"
    )

    with open("militares/utils.py", "w", encoding="utf-8") as f:
        f.write(novo_conteudo)
    
    print("✅ utils.py corrigido!")

if __name__ == "__main__":
    print("🔧 Corrigindo todas as ocorrências da função...")
    corrigir_views_pracas()
    corrigir_views_ata()
    corrigir_utils()
    print("✅ Todas as correções concluídas!") 