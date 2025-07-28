#!/usr/bin/env python
"""
Script para corrigir a sintaxe do template Django
"""

def corrigir_sintaxe_template():
    """Corrige a sintaxe do template Django"""
    
    print("🔧 CORRIGINDO SINTAXE DO TEMPLATE")
    print("=" * 60)
    
    # Ler o arquivo template
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir sintaxe Django
    content = content.replace('{ choice.tag }', '{{ choice.tag }}')
    content = content.replace('{ choice.id_for_label }', '{{ choice.id_for_label }}')
    content = content.replace('{ choice.choice_label }', '{{ choice.choice_label }}')
    content = content.replace('{ form.', '{{ form.')
    content = content.replace('.label }', '.label }}')
    
    # Salvar o arquivo corrigido
    with open('militares/templates/militares/cargos/cargo_funcao_form.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Sintaxe do template corrigida!")
    print("🎮 Agora acesse /militares/cargos/ para ver todos os módulos!")

if __name__ == "__main__":
    corrigir_sintaxe_template() 