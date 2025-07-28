#!/usr/bin/env python
"""
Script para corrigir as chaves duplas no template
"""

def corrigir_chaves_duplas():
    """Corrige as chaves duplas no template Django"""
    
    print("🔧 CORRIGINDO CHAVES DUPLAS NO TEMPLATE")
    print("=" * 60)
    
    # Ler o arquivo template
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir chaves duplas
    content = content.replace('{{{{ choice.tag }}}}', '{{ choice.tag }}')
    content = content.replace('{{{{ choice.id_for_label }}}}', '{{ choice.id_for_label }}')
    content = content.replace('{{{{ choice.choice_label }}}}', '{{ choice.choice_label }}')
    content = content.replace('{{{ form.', '{{ form.')
    content = content.replace('.label }}}', '.label }}')
    content = content.replace('{{{ choice.tag }}}', '{{ choice.tag }}')
    content = content.replace('{{{ choice.id_for_label }}}', '{{ choice.id_for_label }}')
    content = content.replace('{{{ choice.choice_label }}}', '{{ choice.choice_label }}')
    
    # Salvar o arquivo corrigido
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Chaves duplas corrigidas!")
    print("🎮 Agora acesse /militares/cargos/ para ver todos os módulos!")

if __name__ == "__main__":
    corrigir_chaves_duplas() 