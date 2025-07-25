#!/usr/bin/env python
import re

def aplicar_decorators_views():
    """Aplicar decorators de controle de acesso nas views"""
    
    # Ler o arquivo views.py
    with open('militares/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aplicar decorator @apenas_visualizacao_comissao nas views de ficha de conceito
    # Substituir todas as ocorrências de @login_required seguido de def ficha_conceito_*
    pattern = r'@login_required\s+def (ficha_conceito_\w+)'
    replacement = r'@login_required\n@apenas_visualizacao_comissao\ndef \1'
    
    content = re.sub(pattern, replacement, content)
    
    # Aplicar decorator @usuario_cpo_required nas views de comissão CPO
    # Substituir views relacionadas a CPO
    cpo_patterns = [
        (r'@login_required\s+def (comissao_promocao_\w+)', r'@login_required\n@usuario_cpo_required\ndef \1'),
        (r'@login_required\s+def (membro_comissao_\w+)', r'@login_required\n@usuario_cpo_required\ndef \1'),
        (r'@login_required\s+def (sessao_comissao_\w+)', r'@login_required\n@usuario_cpo_required\ndef \1'),
    ]
    
    for pattern, replacement in cpo_patterns:
        content = re.sub(pattern, replacement, content)
    
    # Aplicar decorator @usuario_cpp_required nas views de comissão CPP
    # Substituir views relacionadas a CPP
    cpp_patterns = [
        (r'@login_required\s+def (comissao_promocao_\w+)', r'@login_required\n@usuario_cpp_required\ndef \1'),
        (r'@login_required\s+def (membro_comissao_\w+)', r'@login_required\n@usuario_cpp_required\ndef \1'),
        (r'@login_required\s+def (sessao_comissao_\w+)', r'@login_required\n@usuario_cpp_required\ndef \1'),
    ]
    
    for pattern, replacement in cpp_patterns:
        content = re.sub(pattern, replacement, content)
    
    # Salvar o arquivo modificado
    with open('militares/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Decorators aplicados com sucesso!")
    print("📋 Resumo das alterações:")
    print("   - Views de ficha de conceito: @apenas_visualizacao_comissao")
    print("   - Views de comissão CPO: @usuario_cpo_required")
    print("   - Views de comissão CPP: @usuario_cpp_required")

if __name__ == "__main__":
    aplicar_decorators_views() 