#!/usr/bin/env python
"""
Script para corrigir problemas de caracteres na lista de militares
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

def verificar_problemas_caracteres():
    """
    Verifica problemas de caracteres nos dados dos militares
    """
    print("🔍 Verificando problemas de caracteres nos dados dos militares...")
    
    problemas_encontrados = []
    militares = Militar.objects.all()
    
    for militar in militares:
        campos_problematicos = []
        
        # Verificar nome_completo
        if militar.nome_completo:
            nome_original = militar.nome_completo
            nome_normalizado = normalizar_caracteres(nome_original)
            if nome_original != nome_normalizado:
                campos_problematicos.append(f"nome_completo: '{nome_original}' -> '{nome_normalizado}'")
        
        # Verificar nome_guerra
        if militar.nome_guerra:
            nome_original = militar.nome_guerra
            nome_normalizado = normalizar_caracteres(nome_original)
            if nome_original != nome_normalizado:
                campos_problematicos.append(f"nome_guerra: '{nome_original}' -> '{nome_normalizado}'")
        
        # Verificar observacoes
        if militar.observacoes:
            obs_original = militar.observacoes
            obs_normalizada = normalizar_caracteres(obs_original)
            if obs_original != obs_normalizada:
                campos_problematicos.append(f"observacoes: '{obs_original[:50]}...' -> '{obs_normalizada[:50]}...'")
        
        if campos_problematicos:
            problemas_encontrados.append({
                'militar_id': militar.id,
                'matricula': militar.matricula,
                'nome_atual': militar.nome_completo,
                'campos': campos_problematicos
            })
    
    print(f"📊 Total de militares verificados: {len(militares)}")
    print(f"⚠️  Militares com problemas de caracteres: {len(problemas_encontrados)}")
    
    if problemas_encontrados:
        print("\n📋 Primeiros 10 problemas encontrados:")
        for i, problema in enumerate(problemas_encontrados[:10]):
            print(f"  {i+1}. Militar ID {problema['militar_id']} ({problema['matricula']}):")
            for campo in problema['campos']:
                print(f"     - {campo}")
    
    return problemas_encontrados

def corrigir_caracteres_militares():
    """
    Corrige problemas de caracteres nos dados dos militares
    """
    print("🔧 Corrigindo problemas de caracteres nos dados dos militares...")
    
    militares = Militar.objects.all()
    total_corrigidos = 0
    erros = []
    
    for militar in militares:
        try:
            alterado = False
            
            # Corrigir nome_completo
            if militar.nome_completo:
                nome_original = militar.nome_completo
                nome_corrigido = normalizar_caracteres(nome_original)
                if nome_original != nome_corrigido:
                    militar.nome_completo = nome_corrigido
                    alterado = True
            
            # Corrigir nome_guerra
            if militar.nome_guerra:
                nome_original = militar.nome_guerra
                nome_corrigido = normalizar_caracteres(nome_original)
                if nome_original != nome_corrigido:
                    militar.nome_guerra = nome_corrigido
                    alterado = True
            
            # Corrigir observacoes
            if militar.observacoes:
                obs_original = militar.observacoes
                obs_corrigida = normalizar_caracteres(obs_original)
                if obs_original != obs_corrigida:
                    militar.observacoes = obs_corrigida
                    alterado = True
            
            if alterado:
                militar.save()
                total_corrigidos += 1
                print(f"  ✅ Militar ID {militar.id} ({militar.matricula}) corrigido")
                
        except Exception as e:
            erro_msg = f"Erro ao corrigir militar ID {militar.id}: {e}"
            erros.append(erro_msg)
            print(f"  ❌ {erro_msg}")
            continue
    
    print(f"\n✅ Correção concluída!")
    print(f"📊 Militares corrigidos: {total_corrigidos}")
    print(f"❌ Erros: {len(erros)}")
    
    if erros:
        print("\n📋 Primeiros 5 erros:")
        for erro in erros[:5]:
            print(f"  - {erro}")
    
    return total_corrigidos

def verificar_encoding_banco():
    """
    Verifica a configuração de encoding do banco de dados
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
            
            # Verificar encoding da conexão
            cursor.execute("SHOW client_connection;")
            connection_encoding = cursor.fetchone()[0]
            print(f"  Connection encoding: {connection_encoding}")
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar encoding: {e}")

def testar_exibicao_caracteres():
    """
    Testa a exibição de caracteres especiais
    """
    print("🧪 Testando exibição de caracteres especiais...")
    
    # Lista de caracteres especiais para testar
    caracteres_teste = [
        "João da Silva",
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
    for i, texto in enumerate(caracteres_teste, 1):
        normalizado = normalizar_caracteres(texto)
        print(f"    {i:2d}. Original: '{texto}'")
        print(f"        Normalizado: '{normalizado}'")
        if texto != normalizado:
            print(f"        ⚠️  Diferença detectada!")

def main():
    """
    Função principal
    """
    print("🚀 Iniciando correção de caracteres na lista de militares...")
    print("=" * 60)
    
    # Verificar encoding do banco
    verificar_encoding_banco()
    print()
    
    # Testar normalização de caracteres
    testar_exibicao_caracteres()
    print()
    
    # Verificar problemas existentes
    problemas = verificar_problemas_caracteres()
    print()
    
    if problemas:
        print("🔧 Iniciando correção automática...")
        corrigir_caracteres_militares()
        print()
        
        # Verificar novamente após correção
        print("🔍 Verificando após correção...")
        problemas_apos = verificar_problemas_caracteres()
        
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