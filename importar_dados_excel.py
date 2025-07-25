#!/usr/bin/env python
"""
Script para importar dados do arquivo Excel e substituir militares e usuários
"""

import os
import sys
import django
import pandas as pd
import unicodedata
import re
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar
from django.db import transaction

def normalizar_caracteres(texto):
    """
    Normaliza caracteres especiais e corrige problemas de encoding
    """
    if not texto or pd.isna(texto):
        return ""
    
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

def ler_arquivo_excel(arquivo_excel):
    """
    Lê o arquivo Excel e retorna os dados
    """
    print(f"📖 Lendo arquivo Excel: {arquivo_excel}")
    
    try:
        # Ler o arquivo Excel
        df = pd.read_excel(arquivo_excel)
        
        print(f"✅ Arquivo lido com sucesso!")
        print(f"📊 Total de linhas: {len(df)}")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        
        # Mostrar primeiras linhas
        print("\n📋 Primeiras 5 linhas:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo Excel: {e}")
        return None

def mapear_colunas_excel(df):
    """
    Mapeia as colunas do Excel para os campos do modelo Militar
    """
    print("\n🔍 Mapeando colunas do Excel...")
    
    # Mapeamento de colunas (ajustar conforme necessário)
    mapeamento_colunas = {}
    
    # Verificar colunas existentes e tentar mapear automaticamente
    colunas_excel = list(df.columns)
    
    # Mapeamento automático baseado em palavras-chave
    mapeamentos_possiveis = {
        'matricula': ['matricula', 'matrícula', 'mat', 'id'],
        'nome_completo': ['nome', 'nome_completo', 'nome completo', 'nomecompleto'],
        'nome_guerra': ['nome_guerra', 'nome guerra', 'nomeguerra', 'guerra'],
        'cpf': ['cpf', 'documento'],
        'posto_graduacao': ['posto', 'graduacao', 'graduação', 'posto_graduacao', 'posto graduacao'],
        'quadro': ['quadro'],
        'data_nascimento': ['nascimento', 'data_nascimento', 'data nascimento', 'nasc'],
        'data_ingresso': ['ingresso', 'data_ingresso', 'data ingresso', 'ing'],
        'data_promocao_atual': ['promocao', 'promoção', 'data_promocao', 'data promoção'],
        'situacao': ['situacao', 'situação', 'status'],
        'email': ['email', 'e-mail'],
        'telefone': ['telefone', 'tel', 'fone'],
        'celular': ['celular', 'cel', 'mobile'],
        'observacoes': ['observacoes', 'observações', 'obs', 'comentarios'],
        'numeracao_antiguidade': ['antiguidade', 'numeracao', 'numeração', 'numero_antiguidade']
    }
    
    for campo_modelo, possiveis_nomes in mapeamentos_possiveis.items():
        for coluna_excel in colunas_excel:
            if any(nome.lower() in coluna_excel.lower() for nome in possiveis_nomes):
                mapeamento_colunas[campo_modelo] = coluna_excel
                print(f"  ✅ {campo_modelo} -> {coluna_excel}")
                break
    
    # Mostrar colunas não mapeadas
    colunas_mapeadas = list(mapeamento_colunas.values())
    colunas_nao_mapeadas = [col for col in colunas_excel if col not in colunas_mapeadas]
    
    if colunas_nao_mapeadas:
        print(f"\n⚠️  Colunas não mapeadas: {colunas_nao_mapeadas}")
    
    return mapeamento_colunas

def converter_data(data_str):
    """
    Converte string de data para objeto date
    """
    if pd.isna(data_str) or not data_str:
        return None
    
    try:
        # Se já for datetime
        if isinstance(data_str, datetime):
            return data_str.date()
        
        # Se for string, tentar converter
        if isinstance(data_str, str):
            # Tentar diferentes formatos
            formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%y', '%Y/%m/%d']
            for formato in formatos:
                try:
                    return datetime.strptime(data_str, formato).date()
                except:
                    continue
        
        # Se for timestamp do pandas
        if hasattr(data_str, 'date'):
            return data_str.date()
        
        return None
        
    except Exception as e:
        print(f"⚠️  Erro ao converter data '{data_str}': {e}")
        return None

def mapear_posto_graduacao(posto_str):
    """
    Mapeia string de posto/graduação para código
    """
    if pd.isna(posto_str) or not posto_str:
        return 'SD'
    
    posto_str = str(posto_str).upper().strip()
    
    mapeamento_postos = {
        'CORONEL': 'CB',
        'TC': 'TC',
        'TENENTE CORONEL': 'TC',
        'MAJOR': 'MJ',
        'CAPITAO': 'CP',
        'CAPITÃO': 'CP',
        '1º TENENTE': '1T',
        '1T': '1T',
        '2º TENENTE': '2T',
        '2T': '2T',
        'ASPIRANTE': 'AS',
        'AS': 'AS',
        'ALUNO ASPIRANTE': 'AA',
        'AA': 'AA',
        'SUBTENENTE': 'ST',
        'ST': 'ST',
        '1º SARGENTO': '1S',
        '1S': '1S',
        '2º SARGENTO': '2S',
        '2S': '2S',
        '3º SARGENTO': '3S',
        '3S': '3S',
        'CABO': 'CAB',
        'CAB': 'CAB',
        'SOLDADO': 'SD',
        'SD': 'SD',
        'NVRR': 'NVRR'
    }
    
    return mapeamento_postos.get(posto_str, 'SD')

def mapear_situacao(situacao_str):
    """
    Mapeia string de situação para código
    """
    if pd.isna(situacao_str) or not situacao_str:
        return 'AT'
    
    situacao_str = str(situacao_str).upper().strip()
    
    mapeamento_situacao = {
        'ATIVO': 'AT',
        'AT': 'AT',
        'INATIVO': 'IN',
        'IN': 'IN',
        'APOSENTADO': 'IN',
        'REFORMADO': 'IN'
    }
    
    return mapeamento_situacao.get(situacao_str, 'AT')

def mapear_quadro(quadro_str):
    """
    Mapeia string de quadro para código
    """
    if pd.isna(quadro_str) or not quadro_str:
        return 'COMBATENTE'
    
    quadro_str = str(quadro_str).upper().strip()
    
    mapeamento_quadro = {
        'COMBATENTE': 'COMBATENTE',
        'ESPECIALISTA': 'ESPECIALISTA',
        'AUXILIAR': 'AUXILIAR',
        'NVRR': 'NVRR'
    }
    
    return mapeamento_quadro.get(quadro_str, 'COMBATENTE')

def limpar_dados_existentes():
    """
    Limpa dados existentes de militares e usuários
    """
    print("\n🗑️  Limpando dados existentes...")
    
    try:
        # Contar registros existentes
        total_militares = Militar.objects.count()
        total_usuarios = User.objects.count()
        
        print(f"📊 Militares existentes: {total_militares}")
        print(f"📊 Usuários existentes: {total_usuarios}")
        
        # Confirmar limpeza
        confirmacao = input("\n⚠️  Tem certeza que deseja limpar todos os dados? (s/N): ")
        if confirmacao.lower() != 's':
            print("❌ Operação cancelada pelo usuário")
            return False
        
        # Limpar dados
        with transaction.atomic():
            # Deletar militares (isso também deletará usuários vinculados)
            Militar.objects.all().delete()
            
            # Deletar usuários restantes
            User.objects.all().delete()
        
        print("✅ Dados limpos com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")
        return False

def importar_militares_excel(df, mapeamento_colunas):
    """
    Importa militares do DataFrame do Excel
    """
    print(f"\n📥 Importando {len(df)} militares do Excel...")
    
    militares_criados = 0
    erros = 0
    
    for index, row in df.iterrows():
        try:
            # Extrair dados do Excel
            dados_militar = {}
            
            # Mapear campos básicos
            if 'matricula' in mapeamento_colunas:
                dados_militar['matricula'] = normalizar_caracteres(row[mapeamento_colunas['matricula']])
            
            if 'nome_completo' in mapeamento_colunas:
                dados_militar['nome_completo'] = normalizar_caracteres(row[mapeamento_colunas['nome_completo']])
            
            if 'nome_guerra' in mapeamento_colunas:
                dados_militar['nome_guerra'] = normalizar_caracteres(row[mapeamento_colunas['nome_guerra']])
            
            if 'cpf' in mapeamento_colunas:
                cpf = str(row[mapeamento_colunas['cpf']])
                # Limpar CPF
                cpf = re.sub(r'[^\d]', '', cpf)
                dados_militar['cpf'] = cpf
            
            if 'posto_graduacao' in mapeamento_colunas:
                dados_militar['posto_graduacao'] = mapear_posto_graduacao(row[mapeamento_colunas['posto_graduacao']])
            
            if 'quadro' in mapeamento_colunas:
                dados_militar['quadro'] = mapear_quadro(row[mapeamento_colunas['quadro']])
            
            if 'data_nascimento' in mapeamento_colunas:
                dados_militar['data_nascimento'] = converter_data(row[mapeamento_colunas['data_nascimento']])
            
            if 'data_ingresso' in mapeamento_colunas:
                dados_militar['data_ingresso'] = converter_data(row[mapeamento_colunas['data_ingresso']])
            
            if 'data_promocao_atual' in mapeamento_colunas:
                dados_militar['data_promocao_atual'] = converter_data(row[mapeamento_colunas['data_promocao_atual']])
            
            if 'situacao' in mapeamento_colunas:
                dados_militar['situacao'] = mapear_situacao(row[mapeamento_colunas['situacao']])
            
            if 'email' in mapeamento_colunas:
                dados_militar['email'] = normalizar_caracteres(row[mapeamento_colunas['email']])
            
            if 'telefone' in mapeamento_colunas:
                dados_militar['telefone'] = normalizar_caracteres(row[mapeamento_colunas['telefone']])
            
            if 'celular' in mapeamento_colunas:
                dados_militar['celular'] = normalizar_caracteres(row[mapeamento_colunas['celular']])
            
            if 'observacoes' in mapeamento_colunas:
                dados_militar['observacoes'] = normalizar_caracteres(row[mapeamento_colunas['observacoes']])
            
            if 'numeracao_antiguidade' in mapeamento_colunas:
                try:
                    num_ant = row[mapeamento_colunas['numeracao_antiguidade']]
                    if pd.notna(num_ant) and num_ant != '':
                        dados_militar['numeracao_antiguidade'] = int(num_ant)
                except:
                    pass
            
            # Validações básicas
            if not dados_militar.get('matricula'):
                print(f"  ⚠️  Linha {index + 1}: Matrícula vazia, pulando...")
                continue
            
            if not dados_militar.get('nome_completo'):
                print(f"  ⚠️  Linha {index + 1}: Nome vazio, pulando...")
                continue
            
            # Criar militar
            militar = Militar(**dados_militar)
            militar.save()
            
            # Criar usuário automaticamente
            try:
                username = f"militar_{militar.matricula}"
                email = militar.email if militar.email else f"{username}@cbmepi.pi.gov.br"
                
                # Verificar se já existe usuário com este username
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{militar.pk}"
                
                # Separar nome em first_name e last_name
                nomes = militar.nome_completo.split()
                first_name = nomes[0] if nomes else ''
                last_name = ' '.join(nomes[1:]) if len(nomes) > 1 else ''
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=militar.cpf.replace('.', '').replace('-', '').replace('/', '')  # CPF como senha inicial
                )
                
                militar.user = user
                militar.save(update_fields=['user'])
                
            except Exception as e:
                print(f"  ⚠️  Erro ao criar usuário para militar {militar.matricula}: {e}")
            
            militares_criados += 1
            
            if militares_criados % 10 == 0:
                print(f"  ✅ {militares_criados} militares importados...")
                
        except Exception as e:
            print(f"  ❌ Erro na linha {index + 1}: {e}")
            erros += 1
            continue
    
    print(f"\n✅ Importação concluída!")
    print(f"📊 Militares criados: {militares_criados}")
    print(f"❌ Erros: {erros}")
    
    return militares_criados

def main():
    """
    Função principal
    """
    print("🚀 Iniciando importação de dados do Excel...")
    print("=" * 60)
    
    # Arquivo Excel
    arquivo_excel = "Efetivo CBMEPI Atito SI Promoção.xlsx"
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo não encontrado: {arquivo_excel}")
        return
    
    # Ler arquivo Excel
    df = ler_arquivo_excel(arquivo_excel)
    if df is None:
        return
    
    # Mapear colunas
    mapeamento_colunas = mapear_colunas_excel(df)
    if not mapeamento_colunas:
        print("❌ Nenhuma coluna foi mapeada corretamente")
        return
    
    # Limpar dados existentes
    if not limpar_dados_existentes():
        return
    
    # Importar militares
    total_importados = importar_militares_excel(df, mapeamento_colunas)
    
    print("\n" + "=" * 60)
    print("🏁 Processo concluído!")
    print(f"📊 Total de militares importados: {total_importados}")

if __name__ == '__main__':
    main() 