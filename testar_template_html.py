#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.template.loader import render_to_string
from django.template import Context, Template

def testar_template_html():
    """Testa o template HTML com as datas corretas"""
    
    print("=== TESTE DO TEMPLATE HTML ===\n")
    
    # Template do Art. 1º
    template_texto = """
    <p><strong>Art. 1º</strong> Fica fixada a antiguidade dos 
    {% if almanaque.tipo == 'OFICIAIS' %}
        <span style="background-color: #ffff00; font-weight: bold; padding: 2px 4px; border-radius: 3px;">OFICIAIS</span>
    {% elif almanaque.tipo == 'PRACAS' %}
        <span style="background-color: #ffff00; font-weight: bold; padding: 2px 4px; border-radius: 3px;">PRAÇAS</span>
    {% else %}
        Militares
    {% endif %}
    do Corpo de Bombeiros Militar do Estado do Piauí, após as promoções ocorridas em 
    {% if almanaque.tipo == 'OFICIAIS' %}
        18/07/2025 e 23/12/2025
    {% elif almanaque.tipo == 'PRACAS' %}
        18/07/2025 e 25/12/2025
    {% else %}
        18/07/2025
    {% endif %}, conforme segue:</p>
    """
    
    # Testar os três tipos
    tipos_teste = ['OFICIAIS', 'PRACAS', 'GERAL']
    
    for tipo in tipos_teste:
        print(f"🔍 Testando template para tipo: {tipo}")
        
        # Criar contexto simulado
        context = {
            'almanaque': type('Almanaque', (), {'tipo': tipo})()
        }
        
        # Renderizar template
        template = Template(template_texto)
        resultado = template.render(Context(context))
        
        print(f"   📄 Resultado HTML:")
        print(f"   {resultado.strip()}")
        
        # Verificar se a data correta está presente
        if tipo == 'OFICIAIS':
            data_esperada = "18/07/2025 e 23/12/2025"
        elif tipo == 'PRACAS':
            data_esperada = "18/07/2025 e 25/12/2025"
        else:
            data_esperada = "18/07/2025"
        
        if data_esperada in resultado:
            print(f"   ✅ Data correta encontrada: {data_esperada}")
        else:
            print(f"   ❌ Data NÃO encontrada!")
        
        print()
    
    print("=== FIM DO TESTE ===")

if __name__ == "__main__":
    testar_template_html() 