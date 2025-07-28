#!/usr/bin/env python
"""
Script para corrigir todas as chaves duplas no template
"""

def corrigir_todas_chaves_duplas():
    """Corrige todas as chaves duplas no template Django"""
    
    print("🔧 CORRIGINDO TODAS AS CHAVES DUPLAS NO TEMPLATE")
    print("=" * 60)
    
    # Ler o arquivo template
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Contar ocorrências antes da correção
    ocorrencias_antes = content.count('{{{')
    print(f"📊 Ocorrências de chaves duplas encontradas: {ocorrencias_antes}")
    
    # Corrigir todas as chaves duplas
    content = content.replace('{{{', '{{')
    content = content.replace('}}}', '}}')
    
    # Contar ocorrências depois da correção
    ocorrencias_depois = content.count('{{{')
    print(f"📊 Ocorrências restantes: {ocorrencias_depois}")
    
    # Salvar o arquivo corrigido
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Todas as chaves duplas foram corrigidas!")
    print("🎮 Agora acesse /militares/cargos/ para ver todos os módulos!")

if __name__ == "__main__":
    corrigir_todas_chaves_duplas() 