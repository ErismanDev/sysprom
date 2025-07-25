#!/usr/bin/env python
"""
Script para verificar problemas específicos na exibição dos militares no template
"""

import os
import sys
import django
import unicodedata
import re
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.template import Template, Context
from django.template.loader import get_template

def testar_template_militares():
    """
    Testa a renderização do template de militares
    """
    print("🧪 Testando renderização do template de militares...")
    
    try:
        # Carregar o template
        template = get_template('militares/militar_list.html')
        
        # Buscar alguns militares para teste
        militares_teste = Militar.objects.filter(situacao='AT')[:5]
        
        # Criar contexto
        context = {
            'militares': militares_teste,
            'request': None,  # Mock request
        }
        
        # Renderizar template
        html_rendered = template.render(context)
        
        print(f"✅ Template renderizado com sucesso!")
        print(f"📊 Tamanho do HTML gerado: {len(html_rendered)} caracteres")
        
        # Verificar se há caracteres problemáticos no HTML gerado
        caracteres_problematicos = []
        for i, char in enumerate(html_rendered):
            if ord(char) > 127:  # Caracteres não-ASCII
                if i < 1000:  # Mostrar apenas os primeiros 1000 caracteres
                    caracteres_problematicos.append(f"Posição {i}: '{char}' (U+{ord(char):04X})")
        
        if caracteres_problematicos:
            print(f"⚠️  Caracteres especiais encontrados no HTML:")
            for char_info in caracteres_problematicos[:10]:
                print(f"  - {char_info}")
        else:
            print("✅ Nenhum caractere problemático encontrado no HTML")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao renderizar template: {e}")
        return False

def verificar_caracteres_especificos():
    """
    Verifica caracteres específicos que podem causar problemas
    """
    print("🔍 Verificando caracteres específicos problemáticos...")
    
    militares = Militar.objects.all()
    caracteres_problematicos = []
    
    for militar in militares:
        # Verificar nome_completo
        if militar.nome_completo:
            for i, char in enumerate(militar.nome_completo):
                if ord(char) > 127:  # Caracteres não-ASCII
                    caracteres_problematicos.append({
                        'militar_id': militar.id,
                        'matricula': militar.matricula,
                        'campo': 'nome_completo',
                        'posicao': i,
                        'caractere': char,
                        'codigo_unicode': f"U+{ord(char):04X}"
                    })
        
        # Verificar nome_guerra
        if militar.nome_guerra:
            for i, char in enumerate(militar.nome_guerra):
                if ord(char) > 127:  # Caracteres não-ASCII
                    caracteres_problematicos.append({
                        'militar_id': militar.id,
                        'matricula': militar.matricula,
                        'campo': 'nome_guerra',
                        'posicao': i,
                        'caractere': char,
                        'codigo_unicode': f"U+{ord(char):04X}"
                    })
    
    print(f"📊 Total de caracteres especiais encontrados: {len(caracteres_problematicos)}")
    
    if caracteres_problematicos:
        print("\n📋 Primeiros 10 caracteres especiais:")
        for i, char_info in enumerate(caracteres_problematicos[:10]):
            print(f"  {i+1}. Militar {char_info['matricula']} - {char_info['campo']}: '{char_info['caractere']}' ({char_info['codigo_unicode']})")
    
    return caracteres_problematicos

def testar_encoding_django():
    """
    Testa configurações de encoding do Django
    """
    print("🔍 Testando configurações de encoding do Django...")
    
    from django.conf import settings
    
    print(f"  DEFAULT_CHARSET: {getattr(settings, 'DEFAULT_CHARSET', 'Não definido')}")
    print(f"  FILE_CHARSET: {getattr(settings, 'FILE_CHARSET', 'Não definido')}")
    
    # Testar encoding de strings
    test_strings = [
        "João da Silva",
        "Maria José",
        "Antônio Carlos",
        "São Paulo",
        "Ceará"
    ]
    
    print("\n  Testando encoding de strings:")
    for test_str in test_strings:
        try:
            # Testar codificação UTF-8
            encoded = test_str.encode('utf-8')
            decoded = encoded.decode('utf-8')
            print(f"    '{test_str}' -> UTF-8: OK")
        except Exception as e:
            print(f"    '{test_str}' -> UTF-8: ERRO - {e}")

def verificar_problemas_template_simples():
    """
    Verifica problemas específicos no template usando um teste simples
    """
    print("🔍 Verificando problemas específicos no template...")
    
    # Template simples para teste
    template_simples = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Teste de Caracteres</title>
    </head>
    <body>
        <h1>Teste de Caracteres Especiais</h1>
        <ul>
        {% for militar in militares %}
            <li>{{ militar.nome_completo }} - {{ militar.nome_guerra }}</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """
    
    try:
        # Criar template
        template = Template(template_simples)
        
        # Buscar militares com caracteres especiais
        militares_teste = Militar.objects.filter(
            nome_completo__regex=r'[àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ]'
        )[:3]
        
        if not militares_teste.exists():
            # Se não encontrar com regex, pegar alguns aleatórios
            militares_teste = Militar.objects.all()[:3]
        
        # Criar contexto
        context = Context({'militares': militares_teste})
        
        # Renderizar
        html_resultado = template.render(context)
        
        print(f"✅ Template simples renderizado com sucesso!")
        print(f"📊 Tamanho do resultado: {len(html_resultado)} caracteres")
        
        # Verificar se os nomes aparecem corretamente
        for militar in militares_teste:
            if militar.nome_completo in html_resultado:
                print(f"  ✅ Nome '{militar.nome_completo}' encontrado no HTML")
            else:
                print(f"  ❌ Nome '{militar.nome_completo}' NÃO encontrado no HTML")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do template: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 Iniciando verificação de problemas no template de militares...")
    print("=" * 60)
    
    # Testar configurações de encoding do Django
    testar_encoding_django()
    print()
    
    # Verificar caracteres específicos
    caracteres_problematicos = verificar_caracteres_especificos()
    print()
    
    # Testar template simples
    verificar_problemas_template_simples()
    print()
    
    # Testar template completo
    testar_template_militares()
    print()
    
    print("=" * 60)
    print("🏁 Verificação concluída!")
    
    if caracteres_problematicos:
        print(f"⚠️  Encontrados {len(caracteres_problematicos)} caracteres especiais")
        print("💡 Recomendação: Verificar se o template está configurado corretamente para UTF-8")
    else:
        print("✅ Nenhum problema detectado!")

if __name__ == '__main__':
    main() 