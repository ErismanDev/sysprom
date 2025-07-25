#!/usr/bin/env python
"""
Script para verificar problemas específicos na exibição dos usuários no template
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

from django.contrib.auth.models import User
from django.template import Template, Context
from django.template.loader import get_template

def testar_template_usuarios():
    """
    Testa a renderização do template de usuários
    """
    print("🧪 Testando renderização do template de usuários...")
    
    try:
        # Buscar template de usuários (se existir)
        try:
            template = get_template('militares/usuarios/usuarios_list.html')
        except:
            # Se não existir, criar um template simples para teste
            template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Lista de Usuários</title>
            </head>
            <body>
                <h1>Usuários do Sistema</h1>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Nome Completo</th>
                            <th>Email</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                    {% for usuario in usuarios %}
                        <tr>
                            <td>{{ usuario.id }}</td>
                            <td>{{ usuario.username }}</td>
                            <td>{{ usuario.get_full_name }}</td>
                            <td>{{ usuario.email }}</td>
                            <td>{% if usuario.is_active %}Ativo{% else %}Inativo{% endif %}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </body>
            </html>
            """)
        
        # Buscar alguns usuários para teste
        usuarios_teste = User.objects.all()[:5]
        
        # Criar contexto
        context = {
            'usuarios': usuarios_teste,
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

def verificar_caracteres_especificos_usuarios():
    """
    Verifica caracteres específicos que podem causar problemas nos usuários
    """
    print("🔍 Verificando caracteres específicos problemáticos nos usuários...")
    
    usuarios = User.objects.all()
    caracteres_problematicos = []
    
    for usuario in usuarios:
        # Verificar first_name
        if usuario.first_name:
            for i, char in enumerate(usuario.first_name):
                if ord(char) > 127:  # Caracteres não-ASCII
                    caracteres_problematicos.append({
                        'usuario_id': usuario.id,
                        'username': usuario.username,
                        'campo': 'first_name',
                        'posicao': i,
                        'caractere': char,
                        'codigo_unicode': f"U+{ord(char):04X}"
                    })
        
        # Verificar last_name
        if usuario.last_name:
            for i, char in enumerate(usuario.last_name):
                if ord(char) > 127:  # Caracteres não-ASCII
                    caracteres_problematicos.append({
                        'usuario_id': usuario.id,
                        'username': usuario.username,
                        'campo': 'last_name',
                        'posicao': i,
                        'caractere': char,
                        'codigo_unicode': f"U+{ord(char):04X}"
                    })
        
        # Verificar username
        if usuario.username:
            for i, char in enumerate(usuario.username):
                if ord(char) > 127:  # Caracteres não-ASCII
                    caracteres_problematicos.append({
                        'usuario_id': usuario.id,
                        'username': usuario.username,
                        'campo': 'username',
                        'posicao': i,
                        'caractere': char,
                        'codigo_unicode': f"U+{ord(char):04X}"
                    })
    
    print(f"📊 Total de caracteres especiais encontrados: {len(caracteres_problematicos)}")
    
    if caracteres_problematicos:
        print("\n📋 Primeiros 10 caracteres especiais:")
        for i, char_info in enumerate(caracteres_problematicos[:10]):
            print(f"  {i+1}. Usuário {char_info['username']} - {char_info['campo']}: '{char_info['caractere']}' ({char_info['codigo_unicode']})")
    
    return caracteres_problematicos

def testar_encoding_django_usuarios():
    """
    Testa configurações de encoding do Django para usuários
    """
    print("🔍 Testando configurações de encoding do Django...")
    
    from django.conf import settings
    
    print(f"  DEFAULT_CHARSET: {getattr(settings, 'DEFAULT_CHARSET', 'Não definido')}")
    print(f"  FILE_CHARSET: {getattr(settings, 'FILE_CHARSET', 'Não definido')}")
    
    # Testar encoding de strings com nomes de usuários
    test_strings = [
        "João Silva",
        "Maria José",
        "Antônio Carlos",
        "José da Silva",
        "François"
    ]
    
    print("\n  Testando encoding de strings de usuários:")
    for test_str in test_strings:
        try:
            # Testar codificação UTF-8
            encoded = test_str.encode('utf-8')
            decoded = encoded.decode('utf-8')
            print(f"    '{test_str}' -> UTF-8: OK")
        except Exception as e:
            print(f"    '{test_str}' -> UTF-8: ERRO - {e}")

def verificar_problemas_template_simples_usuarios():
    """
    Verifica problemas específicos no template usando um teste simples
    """
    print("🔍 Verificando problemas específicos no template de usuários...")
    
    # Template simples para teste
    template_simples = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Teste de Usuários</title>
    </head>
    <body>
        <h1>Teste de Caracteres Especiais em Usuários</h1>
        <ul>
        {% for usuario in usuarios %}
            <li>{{ usuario.username }} - {{ usuario.get_full_name }} - {{ usuario.email }}</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """
    
    try:
        # Criar template
        template = Template(template_simples)
        
        # Buscar usuários com caracteres especiais
        usuarios_teste = User.objects.filter(
            first_name__regex=r'[àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ]'
        )[:3]
        
        if not usuarios_teste.exists():
            # Se não encontrar com regex, pegar alguns aleatórios
            usuarios_teste = User.objects.all()[:3]
        
        # Criar contexto
        context = Context({'usuarios': usuarios_teste})
        
        # Renderizar
        html_resultado = template.render(context)
        
        print(f"✅ Template simples renderizado com sucesso!")
        print(f"📊 Tamanho do resultado: {len(html_resultado)} caracteres")
        
        # Verificar se os nomes aparecem corretamente
        for usuario in usuarios_teste:
            nome_completo = usuario.get_full_name()
            if nome_completo in html_resultado:
                print(f"  ✅ Nome '{nome_completo}' encontrado no HTML")
            else:
                print(f"  ❌ Nome '{nome_completo}' NÃO encontrado no HTML")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do template: {e}")
        return False

def verificar_usuarios_vinculados_militares():
    """
    Verifica usuários que estão vinculados a militares
    """
    print("🔍 Verificando usuários vinculados a militares...")
    
    from militares.models import Militar
    
    usuarios_com_militar = User.objects.filter(militar__isnull=False)
    usuarios_sem_militar = User.objects.filter(militar__isnull=True)
    
    print(f"📊 Usuários com militar vinculado: {usuarios_com_militar.count()}")
    print(f"📊 Usuários sem militar vinculado: {usuarios_sem_militar.count()}")
    
    # Verificar caracteres especiais em usuários com militar
    caracteres_problematicos = []
    
    for usuario in usuarios_com_militar:
        nome_completo = usuario.get_full_name()
        militar_nome = usuario.militar.nome_completo if usuario.militar else "N/A"
        
        # Verificar se há diferença entre o nome do usuário e do militar
        if nome_completo != militar_nome:
            caracteres_problematicos.append({
                'usuario_id': usuario.id,
                'username': usuario.username,
                'usuario_nome': nome_completo,
                'militar_nome': militar_nome,
                'diferenca': True
            })
    
    print(f"📊 Usuários com diferença de nomes: {len(caracteres_problematicos)}")
    
    if caracteres_problematicos:
        print("\n📋 Primeiros 5 usuários com diferença de nomes:")
        for i, info in enumerate(caracteres_problematicos[:5]):
            print(f"  {i+1}. {info['username']}")
            print(f"     Usuário: '{info['usuario_nome']}'")
            print(f"     Militar: '{info['militar_nome']}'")
    
    return caracteres_problematicos

def main():
    """
    Função principal
    """
    print("🚀 Iniciando verificação de problemas no template de usuários...")
    print("=" * 60)
    
    # Testar configurações de encoding do Django
    testar_encoding_django_usuarios()
    print()
    
    # Verificar caracteres específicos
    caracteres_problematicos = verificar_caracteres_especificos_usuarios()
    print()
    
    # Verificar usuários vinculados a militares
    verificar_usuarios_vinculados_militares()
    print()
    
    # Testar template simples
    verificar_problemas_template_simples_usuarios()
    print()
    
    # Testar template completo
    testar_template_usuarios()
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