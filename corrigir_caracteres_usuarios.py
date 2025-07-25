#!/usr/bin/env python
"""
Script para corrigir problemas de caracteres na tabela de usuários
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
from django.db import connection

def normalizar_caracteres(texto):
    """
    Normaliza caracteres especiais e corrige problemas de encoding
    """
    if not texto:
        return texto
    
    # Converter para string se não for
    texto = str(texto)
    
    # Normalizar caracteres Unicode (NFD = decomposição)
    texto = unicodedata.normalize('NFD', texto)
    
    # Mapeamento de caracteres problemáticos comuns
    substituicoes = {
        # Caracteres especiais que podem estar corrompidos
        'à': 'à', 'á': 'á', 'â': 'â', 'ã': 'ã', 'ä': 'ä', 'å': 'å',
        'ç': 'ç',
        'è': 'è', 'é': 'é', 'ê': 'ê', 'ë': 'ë',
        'ì': 'ì', 'í': 'í', 'î': 'î', 'ï': 'ï',
        'ñ': 'ñ',
        'ò': 'ò', 'ó': 'ó', 'ô': 'ô', 'õ': 'õ', 'ö': 'ö',
        'ù': 'ù', 'ú': 'ú', 'û': 'û', 'ü': 'ü',
        'ý': 'ý', 'ÿ': 'ÿ',
        
        # Maiúsculas
        'À': 'À', 'Á': 'Á', 'Â': 'Â', 'Ã': 'Ã', 'Ä': 'Ä', 'Å': 'Å',
        'Ç': 'Ç',
        'È': 'È', 'É': 'É', 'Ê': 'Ê', 'Ë': 'Ë',
        'Ì': 'Ì', 'Í': 'Í', 'Î': 'Î', 'Ï': 'Ï',
        'Ñ': 'Ñ',
        'Ò': 'Ò', 'Ó': 'Ó', 'Ô': 'Ô', 'Õ': 'Õ', 'Ö': 'Ö',
        'Ù': 'Ù', 'Ú': 'Ú', 'Û': 'Û', 'Ü': 'Ü',
        'Ý': 'Ý',
        
        # Caracteres especiais do português
        'ª': 'ª', 'º': 'º',
        '°': '°',
        '§': '§',
        '©': '©', '®': '®', '™': '™',
        
        # Aspas e parênteses
        '"': '"', '"': '"',
        "'": "'", "'": "'",
        '(': '(', ')': ')',
        '[': '[', ']': ']',
        '{': '{', '}': '}',
        
        # Pontuação
        '…': '...',
        '–': '-', '—': '-',
        '•': '•',
    }
    
    # Aplicar substituições
    for char_antigo, char_novo in substituicoes.items():
        texto = texto.replace(char_antigo, char_novo)
    
    # Remover caracteres de controle (exceto quebras de linha e tabulações)
    texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texto)
    
    # Normalizar espaços
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    
    return texto

def verificar_problemas_caracteres_usuarios():
    """
    Verifica problemas de caracteres nos dados dos usuários
    """
    print("🔍 Verificando problemas de caracteres nos dados dos usuários...")
    
    problemas_encontrados = []
    usuarios = User.objects.all()
    
    for usuario in usuarios:
        campos_problematicos = []
        
        # Verificar first_name
        if usuario.first_name:
            nome_original = usuario.first_name
            nome_normalizado = normalizar_caracteres(nome_original)
            if nome_original != nome_normalizado:
                campos_problematicos.append(f"first_name: '{nome_original}' -> '{nome_normalizado}'")
        
        # Verificar last_name
        if usuario.last_name:
            nome_original = usuario.last_name
            nome_normalizado = normalizar_caracteres(nome_original)
            if nome_original != nome_normalizado:
                campos_problematicos.append(f"last_name: '{nome_original}' -> '{nome_normalizado}'")
        
        # Verificar username
        if usuario.username:
            username_original = usuario.username
            username_normalizado = normalizar_caracteres(username_original)
            if username_original != username_normalizado:
                campos_problematicos.append(f"username: '{username_original}' -> '{username_normalizado}'")
        
        # Verificar email
        if usuario.email:
            email_original = usuario.email
            email_normalizado = normalizar_caracteres(email_original)
            if email_original != email_normalizado:
                campos_problematicos.append(f"email: '{email_original}' -> '{email_normalizado}'")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'usuario_id': usuario.id,
                'username': usuario.username,
                'nome_atual': f"{usuario.first_name} {usuario.last_name}".strip(),
                'campos': campos_problematicos
            })
    
    print(f"📊 Total de usuários verificados: {len(usuarios)}")
    print(f"⚠️  Usuários com problemas de caracteres: {len(problemas_encontrados)}")
    
    if problemas_encontrados:
        print("\n📋 Primeiros 10 problemas encontrados:")
        for i, problema in enumerate(problemas_encontrados[:10]):
            print(f"  {i+1}. Usuário ID {problema['usuario_id']} ({problema['username']}):")
            for campo in problema['campos']:
                print(f"     - {campo}")
    
    return problemas_encontrados

def corrigir_caracteres_usuarios():
    """
    Corrige problemas de caracteres nos dados dos usuários
    """
    print("🔧 Corrigindo problemas de caracteres nos dados dos usuários...")
    
    usuarios = User.objects.all()
    total_corrigidos = 0
    erros = []
    
    for usuario in usuarios:
        try:
            alterado = False
            
            # Corrigir first_name
            if usuario.first_name:
                nome_original = usuario.first_name
                nome_corrigido = normalizar_caracteres(nome_original)
                if nome_original != nome_corrigido:
                    usuario.first_name = nome_corrigido
                    alterado = True
            
            # Corrigir last_name
            if usuario.last_name:
                nome_original = usuario.last_name
                nome_corrigido = normalizar_caracteres(nome_original)
                if nome_original != nome_corrigido:
                    usuario.last_name = nome_corrigido
                    alterado = True
            
            # Corrigir username (com cuidado para não duplicar)
            if usuario.username:
                username_original = usuario.username
                username_corrigido = normalizar_caracteres(username_original)
                if username_original != username_corrigido:
                    # Verificar se o username corrigido já existe
                    if User.objects.filter(username=username_corrigido).exclude(id=usuario.id).exists():
                        print(f"  ⚠️  Usuário ID {usuario.id}: username '{username_corrigido}' já existe, mantendo original")
                    else:
                        usuario.username = username_corrigido
                        alterado = True
            
            # Corrigir email
            if usuario.email:
                email_original = usuario.email
                email_corrigido = normalizar_caracteres(email_original)
                if email_original != email_corrigido:
                    # Verificar se o email corrigido já existe
                    if User.objects.filter(email=email_corrigido).exclude(id=usuario.id).exists():
                        print(f"  ⚠️  Usuário ID {usuario.id}: email '{email_corrigido}' já existe, mantendo original")
                    else:
                        usuario.email = email_corrigido
                        alterado = True
            
            if alterado:
                usuario.save()
                total_corrigidos += 1
                print(f"  ✅ Usuário ID {usuario.id} ({usuario.username}) corrigido")
                
        except Exception as e:
            erro_msg = f"Erro ao corrigir usuário ID {usuario.id}: {e}"
            erros.append(erro_msg)
            print(f"  ❌ {erro_msg}")
            continue
    
    print(f"\n✅ Correção concluída!")
    print(f"📊 Usuários corrigidos: {total_corrigidos}")
    print(f"❌ Erros: {len(erros)}")
    
    if erros:
        print("\n📋 Primeiros 5 erros:")
        for erro in erros[:5]:
            print(f"  - {erro}")
    
    return total_corrigidos

def verificar_encoding_banco_usuarios():
    """
    Verifica a configuração de encoding do banco de dados para usuários
    """
    print("🔍 Verificando configuração de encoding do banco de dados...")
    
    try:
        with connection.cursor() as cursor:
            # Verificar encoding do banco
            cursor.execute("SHOW server_encoding;")
            server_encoding = cursor.fetchone()[0]
            print(f"  Server encoding: {server_encoding}")
            
            # Verificar encoding do cliente
            cursor.execute("SHOW client_encoding;")
            client_encoding = cursor.fetchone()[0]
            print(f"  Client encoding: {client_encoding}")
            
            # Verificar tabela auth_user
            cursor.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'auth_user' 
                AND data_type IN ('character varying', 'text', 'character')
                ORDER BY ordinal_position
            """)
            
            colunas = cursor.fetchall()
            print(f"\n📋 Colunas de texto na tabela auth_user:")
            for coluna in colunas:
                print(f"  - {coluna[0]}: {coluna[1]} (max: {coluna[2]})")
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar encoding: {e}")

def testar_exibicao_caracteres_usuarios():
    """
    Testa a exibição de caracteres especiais em nomes de usuários
    """
    print("🧪 Testando exibição de caracteres especiais em usuários...")
    
    # Lista de nomes com caracteres especiais para testar
    nomes_teste = [
        "João Silva",
        "Maria José",
        "Antônio Carlos",
        "François",
        "José María",
        "São Paulo",
        "Ceará",
        "Pará",
        "Amapá",
        "Maranhão",
        "Piauí",
        "Paraíba",
        "Pernambuco",
        "Alagoas",
        "Sergipe",
        "Bahia",
        "Minas Gerais",
        "Espírito Santo",
        "Rio de Janeiro",
        "São Paulo",
        "Paraná",
        "Santa Catarina",
        "Rio Grande do Sul",
        "Mato Grosso do Sul",
        "Mato Grosso",
        "Goiás",
        "Distrito Federal",
        "Rondônia",
        "Acre",
        "Amazonas",
        "Roraima",
        "Tocantins"
    ]
    
    print("  Caracteres de teste:")
    for i, texto in enumerate(nomes_teste, 1):
        normalizado = normalizar_caracteres(texto)
        print(f"    {i:2d}. Original: '{texto}'")
        print(f"        Normalizado: '{normalizado}'")
        if texto != normalizado:
            print(f"        ⚠️  Diferença detectada!")

def verificar_usuarios_com_caracteres_especiais():
    """
    Verifica usuários que têm caracteres especiais nos nomes
    """
    print("🔍 Verificando usuários com caracteres especiais...")
    
    usuarios = User.objects.all()
    usuarios_com_caracteres_especiais = []
    
    for usuario in usuarios:
        nome_completo = f"{usuario.first_name} {usuario.last_name}".strip()
        
        # Verificar se tem caracteres especiais
        caracteres_especiais = []
        for i, char in enumerate(nome_completo):
            if ord(char) > 127:  # Caracteres não-ASCII
                caracteres_especiais.append({
                    'posicao': i,
                    'caractere': char,
                    'codigo_unicode': f"U+{ord(char):04X}"
                })
        
        if caracteres_especiais:
            usuarios_com_caracteres_especiais.append({
                'usuario_id': usuario.id,
                'username': usuario.username,
                'nome_completo': nome_completo,
                'caracteres_especiais': caracteres_especiais
            })
    
    print(f"📊 Total de usuários com caracteres especiais: {len(usuarios_com_caracteres_especiais)}")
    
    if usuarios_com_caracteres_especiais:
        print("\n📋 Usuários com caracteres especiais:")
        for i, usuario_info in enumerate(usuarios_com_caracteres_especiais[:10]):
            print(f"  {i+1}. ID {usuario_info['usuario_id']} - {usuario_info['username']}")
            print(f"     Nome: '{usuario_info['nome_completo']}'")
            for char_info in usuario_info['caracteres_especiais']:
                print(f"     Caractere: '{char_info['caractere']}' ({char_info['codigo_unicode']}) na posição {char_info['posicao']}")
    
    return usuarios_com_caracteres_especiais

def main():
    """
    Função principal
    """
    print("🚀 Iniciando correção de caracteres na tabela de usuários...")
    print("=" * 60)
    
    # Verificar encoding do banco
    verificar_encoding_banco_usuarios()
    print()
    
    # Testar normalização de caracteres
    testar_exibicao_caracteres_usuarios()
    print()
    
    # Verificar usuários com caracteres especiais
    usuarios_com_caracteres = verificar_usuarios_com_caracteres_especiais()
    print()
    
    # Verificar problemas existentes
    problemas = verificar_problemas_caracteres_usuarios()
    print()
    
    if problemas:
        print("🔧 Iniciando correção automática...")
        corrigir_caracteres_usuarios()
        print()
        
        # Verificar novamente após correção
        print("🔍 Verificando após correção...")
        problemas_apos = verificar_problemas_caracteres_usuarios()
        
        if not problemas_apos:
            print("✅ Todos os problemas de caracteres foram corrigidos!")
        else:
            print(f"⚠️  Ainda restam {len(problemas_apos)} problemas de caracteres")
    else:
        print("✅ Nenhum problema de caracteres encontrado!")
    
    print("\n" + "=" * 60)
    print("🏁 Processo concluído!")

if __name__ == '__main__':
    main() 