import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import numpy as np

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sepromcbmepi',
    'user': 'postgres',
    'password': '11322361',
    'port': '5432'
}

def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def ler_arquivo_excel():
    """Lê o arquivo Excel com os dados dos militares"""
    try:
        arquivo_excel = "backups/Efetivo CBMEPI Atito SI Promoção 2.xlsx"
        df = pd.read_excel(arquivo_excel)
        print(f"Arquivo lido com sucesso. Total de registros: {len(df)}")
        print(f"Colunas encontradas: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Erro ao ler arquivo Excel: {e}")
        return None

def limpar_dados(df):
    """Limpa e prepara os dados do DataFrame"""
    # Remove linhas vazias
    df = df.dropna(subset=['matricula', 'nome_completo'])
    
    # Converte tipos de dados e aplica limites
    df['matricula'] = df['matricula'].astype(str).str.strip().str[:20]
    df['nome_completo'] = df['nome_completo'].astype(str).str.strip().str[:200]
    df['nome_guerra'] = df['nome_guerra'].astype(str).str.strip().str[:100]
    
    # Limpa CPF e aplica limite
    if 'cpf' in df.columns:
        df['cpf'] = df['cpf'].astype(str).str.replace(r'[^\d]', '', regex=True).str[:14]
    
    # Trata o campo sexo - pega apenas o primeiro caractere
    if 'sexo' in df.columns:
        df['sexo'] = df['sexo'].astype(str).str.strip().str[:1].str.upper()
    
    # Aplica limites para outros campos
    if 'situacao' in df.columns:
        df['situacao'] = df['situacao'].astype(str).str.strip().str[:2]
    
    if 'posto_graduacao' in df.columns:
        df['posto_graduacao'] = df['posto_graduacao'].astype(str).str.strip().str[:4]
    
    if 'quadro' in df.columns:
        df['quadro'] = df['quadro'].astype(str).str.strip().str[:10]
    
    if 'rg' in df.columns:
        df['rg'] = df['rg'].astype(str).str.strip().str[:20]
    
    if 'ÓRGÃO' in df.columns:
        df['ÓRGÃO'] = df['ÓRGÃO'].astype(str).str.strip().str[:20]
    
    if 'email' in df.columns:
        df['email'] = df['email'].astype(str).str.strip().str[:254]
    
    if 'telefone' in df.columns:
        df['telefone'] = df['telefone'].astype(str).str.strip().str[:20]
    
    if 'celular' in df.columns:
        df['celular'] = df['celular'].astype(str).str.strip().str[:20]
    
    # Converte datas
    colunas_data = ['data_nascimento', 'data_ingresso', 'data_promocao_atual']
    for col in colunas_data:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Se data_promocao_atual estiver vazia, usa data_ingresso
    if 'data_promocao_atual' in df.columns and 'data_ingresso' in df.columns:
        df['data_promocao_atual'] = df['data_promocao_atual'].fillna(df['data_ingresso'])
    
    # Preencher apto_inspecao_saude com 'S' se não existir ou estiver vazio
    if 'apto_inspecao_saude' not in df.columns:
        df['apto_inspecao_saude'] = 'S'
    else:
        df['apto_inspecao_saude'] = df['apto_inspecao_saude'].fillna('S').replace('', 'S')
    
    return df

def mapear_colunas_excel_para_banco():
    """Mapeia as colunas do Excel para as colunas do banco de dados"""
    mapeamento = {
        'matricula': 'matricula',
        'nome_completo': 'nome_completo',
        'nome_guerra': 'nome_guerra',
        'cpf': 'cpf',
        'rg': 'rg',
        'ÓRGÃO': 'orgao_expedidor',
        'data_nascimento': 'data_nascimento',
        'sexo': 'sexo',
        'quadro': 'quadro',
        'posto_graduacao': 'posto_graduacao',
        'data_ingresso': 'data_ingresso',
        'data_promocao_atual': 'data_promocao_atual',
        'situacao': 'situacao',
        'email': 'email',
        'telefone': 'telefone',
        'celular': 'celular',
        'numeracao_antiguidade': 'numeracao_antiguidade',
        'apto_inspecao_saude': 'apto_inspecao_saude'
    }
    return mapeamento

def inserir_militar(conn, dados):
    """Insere um militar no banco de dados"""
    try:
        cursor = conn.cursor()
        
        # Query de inserção
        query = """
        INSERT INTO militares_militar (
            matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor,
            data_nascimento, sexo, quadro, posto_graduacao, data_ingresso,
            data_promocao_atual, situacao, email, telefone, celular,
            data_cadastro, data_atualizacao, observacoes, apto_inspecao_saude,
            curso_aperfeicoamento_oficial, curso_formacao_oficial,
            data_inspecao_saude, data_validade_inspecao_saude, curso_superior,
            curso_csbm, pos_graduacao, curso_adaptacao_oficial, curso_cho,
            numeracao_antiguidade, foto, curso_cas, curso_cfsd, curso_chc,
            curso_chsgt, curso_formacao_pracas, numeracao_antiguidade_anterior,
            user_id, nota_cho, nota_chsgt, nota_chc
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # Preparar valores
        valores = (
            dados.get('matricula'),
            dados.get('nome_completo'),
            dados.get('nome_guerra'),
            dados.get('cpf'),
            dados.get('rg'),
            dados.get('orgao_expedidor'),
            dados.get('data_nascimento'),
            dados.get('sexo'),
            dados.get('quadro'),
            dados.get('posto_graduacao'),
            dados.get('data_ingresso'),
            dados.get('data_promocao_atual'),
            dados.get('situacao'),
            dados.get('email'),
            dados.get('telefone'),
            dados.get('celular'),
            datetime.now(),  # data_cadastro
            datetime.now(),  # data_atualizacao
            dados.get('observacoes'),
            dados.get('apto_inspecao_saude'),
            dados.get('curso_aperfeicoamento_oficial'),
            dados.get('curso_formacao_oficial'),
            dados.get('data_inspecao_saude'),
            dados.get('data_validade_inspecao_saude'),
            dados.get('curso_superior'),
            dados.get('curso_csbm'),
            dados.get('pos_graduacao'),
            dados.get('curso_adaptacao_oficial'),
            dados.get('curso_cho'),
            dados.get('numeracao_antiguidade'),
            None,  # foto
            dados.get('curso_cas'),
            dados.get('curso_cfsd'),
            dados.get('curso_chc'),
            dados.get('curso_chsgt'),
            dados.get('curso_formacao_pracas'),
            dados.get('numeracao_antiguidade_anterior'),
            None,  # user_id
            dados.get('nota_cho'),
            dados.get('nota_chsgt'),
            dados.get('nota_chc')
        )
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        return True
        
    except Exception as e:
        print(f"Erro ao inserir militar {dados.get('matricula')}: {e}")
        conn.rollback()
        return False

def processar_dados_excel():
    """Processa os dados do Excel e insere no banco"""
    # Ler arquivo Excel
    df = ler_arquivo_excel()
    if df is None:
        return
    
    # Limpar dados
    df = limpar_dados(df)
    
    # Mapear colunas
    mapeamento = mapear_colunas_excel_para_banco()
    
    # Conectar ao banco
    conn = conectar_banco()
    if conn is None:
        return
    
    try:
        sucessos = 0
        erros = 0
        
        for index, row in df.iterrows():
            # Preparar dados para inserção
            dados = {}
            for col_excel, col_banco in mapeamento.items():
                if col_excel in df.columns:
                    valor = row[col_excel]
                    # Tratar valores NaN
                    if pd.isna(valor):
                        valor = None
                    dados[col_banco] = valor
            
            # Inserir no banco
            if inserir_militar(conn, dados):
                sucessos += 1
            else:
                erros += 1
            
            # Mostrar progresso
            if (index + 1) % 10 == 0:
                print(f"Processados {index + 1}/{len(df)} registros...")
        
        print(f"\nProcessamento concluído!")
        print(f"Sucessos: {sucessos}")
        print(f"Erros: {erros}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("Iniciando atualização da tabela de militares...")
    processar_dados_excel()
    print("Processo finalizado!") 