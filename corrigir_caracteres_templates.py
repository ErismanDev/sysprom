#!/usr/bin/env python
"""
Script para corrigir problemas de codificação nos templates HTML
"""

import os
import re
import codecs
from pathlib import Path

def corrigir_caracteres_arquivo(arquivo_path):
    """
    Corrige caracteres especiais em um arquivo HTML
    """
    try:
        # Tentar ler com diferentes codificações
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        conteudo = None
        
        for encoding in encodings:
            try:
                with codecs.open(arquivo_path, 'r', encoding=encoding) as f:
                    conteudo = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if conteudo is None:
            print(f"❌ Não foi possível ler o arquivo: {arquivo_path}")
            return False
        
        # Mapeamento de caracteres problemáticos
        substituicoes = {
            # Caracteres especiais comuns
            'à': 'à',
            'á': 'á', 
            'â': 'â',
            'ã': 'ã',
            'ä': 'ä',
            'å': 'å',
            'ç': 'ç',
            'è': 'è',
            'é': 'é',
            'ê': 'ê',
            'ë': 'ë',
            'ì': 'ì',
            'í': 'í',
            'î': 'î',
            'ï': 'ï',
            'ñ': 'ñ',
            'ò': 'ò',
            'ó': 'ó',
            'ô': 'ô',
            'õ': 'õ',
            'ö': 'ö',
            'ù': 'ù',
            'ú': 'ú',
            'û': 'û',
            'ü': 'ü',
            'ý': 'ý',
            'ÿ': 'ÿ',
            
            # Caracteres específicos do português
            'À': 'À',
            'Á': 'Á',
            'Â': 'Â',
            'Ã': 'Ã',
            'Ä': 'Ä',
            'Ç': 'Ç',
            'È': 'È',
            'É': 'É',
            'Ê': 'Ê',
            'Ë': 'Ë',
            'Ì': 'Ì',
            'Í': 'Í',
            'Î': 'Î',
            'Ï': 'Ï',
            'Ñ': 'Ñ',
            'Ò': 'Ò',
            'Ó': 'Ó',
            'Ô': 'Ô',
            'Õ': 'Õ',
            'Ö': 'Ö',
            'Ù': 'Ù',
            'Ú': 'Ú',
            'Û': 'Û',
            'Ü': 'Ü',
            'Ý': 'Ý',
        }
        
        # Aplicar substituições
        conteudo_original = conteudo
        for char_antigo, char_novo in substituicoes.items():
            conteudo = conteudo.replace(char_antigo, char_novo)
        
        # Verificar se houve mudanças
        if conteudo != conteudo_original:
            # Salvar com UTF-8
            with codecs.open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f"✅ Corrigido: {arquivo_path}")
            return True
        else:
            print(f"ℹ️  Sem alterações necessárias: {arquivo_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo_path}: {e}")
        return False

def corrigir_templates():
    """
    Corrige todos os templates HTML do projeto
    """
    # Diretórios de templates
    diretorios_templates = [
        'templates',
        'militares/templates',
    ]
    
    total_arquivos = 0
    arquivos_corrigidos = 0
    
    for diretorio in diretorios_templates:
        if os.path.exists(diretorio):
            print(f"\n📁 Processando diretório: {diretorio}")
            
            # Encontrar todos os arquivos HTML
            for root, dirs, files in os.walk(diretorio):
                for file in files:
                    if file.endswith('.html'):
                        arquivo_path = os.path.join(root, file)
                        total_arquivos += 1
                        
                        if corrigir_caracteres_arquivo(arquivo_path):
                            arquivos_corrigidos += 1
    
    print(f"\n📊 Resumo:")
    print(f"   Total de arquivos processados: {total_arquivos}")
    print(f"   Arquivos corrigidos: {arquivos_corrigidos}")
    print(f"   Arquivos sem alterações: {total_arquivos - arquivos_corrigidos}")

def verificar_encoding_arquivos():
    """
    Verifica a codificação dos arquivos HTML
    """
    print("🔍 Verificando codificação dos arquivos HTML...")
    
    diretorios_templates = [
        'templates',
        'militares/templates',
    ]
    
    for diretorio in diretorios_templates:
        if os.path.exists(diretorio):
            print(f"\n📁 Verificando: {diretorio}")
            
            for root, dirs, files in os.walk(diretorio):
                for file in files:
                    if file.endswith('.html'):
                        arquivo_path = os.path.join(root, file)
                        
                        try:
                            # Tentar detectar encoding
                            with open(arquivo_path, 'rb') as f:
                                raw_data = f.read()
                            
                            # Verificar se tem BOM UTF-8
                            if raw_data.startswith(b'\xef\xbb\xbf'):
                                encoding = 'UTF-8-BOM'
                            else:
                                # Tentar decodificar com UTF-8
                                try:
                                    raw_data.decode('utf-8')
                                    encoding = 'UTF-8'
                                except UnicodeDecodeError:
                                    encoding = 'NÃO-UTF-8'
                            
                            if encoding != 'UTF-8':
                                print(f"⚠️  {arquivo_path}: {encoding}")
                            else:
                                print(f"✅ {arquivo_path}: {encoding}")
                                
                        except Exception as e:
                            print(f"❌ Erro ao verificar {arquivo_path}: {e}")

if __name__ == '__main__':
    print("🔧 Script de Correção de Caracteres nos Templates")
    print("=" * 50)
    
    # Verificar encoding primeiro
    verificar_encoding_arquivos()
    
    print("\n" + "=" * 50)
    
    # Perguntar se deve corrigir
    resposta = input("\nDeseja corrigir os problemas de codificação? (s/n): ").lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        corrigir_templates()
        print("\n✅ Processo concluído!")
    else:
        print("\n❌ Operação cancelada pelo usuário.") 