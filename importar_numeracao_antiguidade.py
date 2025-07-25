#!/usr/bin/env python
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def importar_numeracao_antiguidade():
    """Importa numeração de antiguidade do arquivo Excel mantendo a ordem original"""
    
    print("=== IMPORTANDO NUMERAÇÃO DE ANTIGUIDADE DO EXCEL ===\n")
    
    # Caminho do arquivo Excel
    arquivo_excel = "Efetivo CBMEPI Atito SI Promoção.xlsx"
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo não encontrado: {arquivo_excel}")
        return
    
    try:
        # Ler o arquivo Excel
        print(f"📖 Lendo arquivo: {arquivo_excel}")
        df = pd.read_excel(arquivo_excel)
        
        print(f"📊 Colunas encontradas: {list(df.columns)}")
        print(f"📊 Total de linhas: {len(df)}")
        
        # Mostrar as primeiras linhas para identificar a estrutura
        print("\n📋 Primeiras 5 linhas do arquivo:")
        print(df.head())
        
        # Identificar colunas relevantes
        colunas_nome = []
        colunas_numeracao = []
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'nome' in col_lower or 'militar' in col_lower:
                colunas_nome.append(col)
            elif 'numeração' in col_lower or 'antiguidade' in col_lower or 'numero' in col_lower or 'ord' in col_lower:
                colunas_numeracao.append(col)
        
        print(f"\n🔍 Colunas de nome identificadas: {colunas_nome}")
        print(f"🔍 Colunas de numeração identificadas: {colunas_numeracao}")
        
        if not colunas_nome:
            print("❌ Nenhuma coluna de nome identificada. Verifique o arquivo.")
            return
        
        if not colunas_numeracao:
            print("❌ Nenhuma coluna de numeração identificada. Verifique o arquivo.")
            return
        
        # Usar a primeira coluna de nome e numeração encontrada
        coluna_nome = colunas_nome[0]
        coluna_numeracao = colunas_numeracao[0]
        
        print(f"\n✅ Usando coluna de nome: {coluna_nome}")
        print(f"✅ Usando coluna de numeração: {coluna_numeracao}")
        
        # Processar cada linha mantendo a ordem do Excel
        atualizados = 0
        nao_encontrados = 0
        erros = 0
        
        print(f"\n🔄 Processando {len(df)} registros na ordem do Excel...")
        
        for index, row in df.iterrows():
            try:
                nome_excel = str(row[coluna_nome]).strip()
                numeracao_excel = row[coluna_numeracao]
                
                # Pular linhas vazias
                if pd.isna(nome_excel) or nome_excel == 'nan' or nome_excel == '':
                    continue
                
                # Converter numeração para inteiro
                if pd.isna(numeracao_excel):
                    continue
                
                try:
                    numeracao = int(numeracao_excel)
                except (ValueError, TypeError):
                    print(f"⚠️  Numeração inválida na linha {index + 2}: {numeracao_excel}")
                    continue
                
                # Buscar militar pelo nome (busca aproximada)
                militar = buscar_militar_por_nome(nome_excel)
                
                if militar:
                    # Atualizar numeração de antiguidade com o número exato do Excel
                    militar.numeracao_antiguidade = numeracao
                    militar.save(update_fields=['numeracao_antiguidade'])
                    
                    print(f"✅ Linha {index + 2}: {militar.nome_completo} -> {numeracao}º")
                    atualizados += 1
                else:
                    print(f"❌ Linha {index + 2}: Militar não encontrado: {nome_excel}")
                    nao_encontrados += 1
                    
            except Exception as e:
                print(f"❌ Erro na linha {index + 2}: {str(e)}")
                erros += 1
        
        # Resumo final
        print(f"\n=== RESUMO DA IMPORTAÇÃO ===")
        print(f"✅ Militares atualizados: {atualizados}")
        print(f"❌ Militares não encontrados: {nao_encontrados}")
        print(f"⚠️  Erros: {erros}")
        print(f"📊 Total processado: {atualizados + nao_encontrados + erros}")
        print(f"\n💡 A numeração foi importada mantendo a ordem exata do arquivo Excel!")
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo Excel: {str(e)}")

def buscar_militar_por_nome(nome_excel):
    """Busca militar por nome usando busca aproximada"""
    
    # Normalizar nome (remover acentos, maiúsculas, etc.)
    nome_normalizado = normalizar_nome(nome_excel)
    
    # Buscar todos os militares ativos
    militares = Militar.objects.filter(situacao='AT')
    
    # Tentar encontrar por nome exato primeiro
    for militar in militares:
        if normalizar_nome(militar.nome_completo) == nome_normalizado:
            return militar
    
    # Se não encontrar, tentar busca aproximada
    for militar in militares:
        nome_militar = normalizar_nome(militar.nome_completo)
        
        # Verificar se o nome do Excel está contido no nome do militar
        if nome_normalizado in nome_militar or nome_militar in nome_normalizado:
            return militar
        
        # Verificar se há pelo menos 3 palavras em comum
        palavras_excel = set(nome_normalizado.split())
        palavras_militar = set(nome_militar.split())
        
        if len(palavras_excel.intersection(palavras_militar)) >= 3:
            return militar
    
    return None

def normalizar_nome(nome):
    """Normaliza nome para comparação"""
    import unicodedata
    
    # Converter para string
    nome = str(nome)
    
    # Remover acentos
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(c for c in nome if not unicodedata.combining(c))
    
    # Converter para minúsculas
    nome = nome.lower()
    
    # Remover espaços extras
    nome = ' '.join(nome.split())
    
    return nome

if __name__ == '__main__':
    importar_numeracao_antiguidade() 