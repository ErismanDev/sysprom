#!/usr/bin/env python
"""
Script para corrigir problemas de codificação no banco de dados
"""

import os
import sys
import django
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import connection
from militares.models import *

def conectar_banco():
    """
    Conecta diretamente ao banco PostgreSQL
    """
    try:
        conn = psycopg2.connect(
            dbname="sepromcbmepi",
            user="postgres",
            password="11322361",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def verificar_caracteres_problematicos():
    """
    Verifica caracteres problemáticos em todas as tabelas
    """
    print("🔍 Verificando caracteres problemáticos no banco de dados...")
    
    conn = conectar_banco()
    if not conn:
        return
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Lista de tabelas para verificar
    tabelas = [
        'militares_militar',
        'militares_cargo',
        'militares_funcao',
        'militares_quadro',
        'militares_fichaconceito',
        'militares_sessao',
        'militares_comissao',
        'militares_membrocomissao',
        'militares_voto',
        'militares_permissoesimples',
        'militares_notificacao',
        'militares_almanaque',
        'militares_almanaqueassinatura',
        'auth_user',
        'auth_group',
    ]
    
    problemas_encontrados = []
    
    for tabela in tabelas:
        print(f"\n📋 Verificando tabela: {tabela}")
        
        try:
            # Obter estrutura da tabela
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{tabela}' 
                AND data_type IN ('character varying', 'text', 'character')
            """)
            
            colunas_texto = cursor.fetchall()
            
            for coluna in colunas_texto:
                nome_coluna = coluna['column_name']
                
                # Verificar caracteres problemáticos
                cursor.execute(f"""
                    SELECT id, "{nome_coluna}" as valor
                    FROM {tabela}
                    WHERE "{nome_coluna}" IS NOT NULL
                    AND (
                        "{nome_coluna}" ~ '[àáâãäåçèéêëìíîïñòóôõöùúûüýÿ]'
                        OR "{nome_coluna}" ~ '[ÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ]'
                        OR "{nome_coluna}" ~ '[^\x00-\x7F]'
                    )
                    LIMIT 10
                """)
                
                registros_problematicos = cursor.fetchall()
                
                if registros_problematicos:
                    print(f"  ⚠️  Coluna {nome_coluna}: {len(registros_problematicos)} registros com caracteres especiais")
                    problemas_encontrados.append({
                        'tabela': tabela,
                        'coluna': nome_coluna,
                        'registros': registros_problematicos
                    })
                else:
                    print(f"  ✅ Coluna {nome_coluna}: OK")
                    
        except Exception as e:
            print(f"  ❌ Erro ao verificar {tabela}: {e}")
    
    cursor.close()
    conn.close()
    
    return problemas_encontrados

def corrigir_caracteres_banco():
    """
    Corrige caracteres problemáticos no banco de dados
    """
    print("🔧 Corrigindo caracteres problemáticos no banco de dados...")
    
    conn = conectar_banco()
    if not conn:
        return
    
    cursor = conn.cursor()
    
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
    
    # Tabelas para corrigir
    tabelas_colunas = {
        'militares_militar': ['nome_completo', 'nome_guerra', 'observacoes'],
        'militares_cargo': ['nome', 'descricao'],
        'militares_funcao': ['nome', 'descricao'],
        'militares_quadro': ['nome', 'descricao'],
        'militares_fichaconceito': ['observacoes', 'parecer'],
        'militares_sessao': ['observacoes'],
        'militares_comissao': ['nome', 'observacoes'],
        'militares_membrocomissao': ['observacoes'],
        'militares_voto': ['justificativa', 'voto_proferido'],
        'militares_permissoesimples': ['nome', 'descricao'],
        'militares_notificacao': ['titulo', 'mensagem'],
        'militares_almanaque': ['titulo', 'observacoes'],
        'militares_almanaqueassinatura': ['cargo_funcao', 'observacoes'],
        'auth_user': ['first_name', 'last_name'],
    }
    
    total_corrigidos = 0
    
    for tabela, colunas in tabelas_colunas.items():
        print(f"\n📋 Corrigindo tabela: {tabela}")
        
        for coluna in colunas:
            try:
                # Verificar se a coluna existe
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{tabela}' 
                    AND column_name = '{coluna}'
                """)
                
                if not cursor.fetchone():
                    print(f"  ⚠️  Coluna {coluna} não existe na tabela {tabela}")
                    continue
                
                # Aplicar correções para cada caractere problemático
                for char_antigo, char_novo in substituicoes.items():
                    if char_antigo != char_novo:  # Só corrigir se for diferente
                        cursor.execute(f"""
                            UPDATE {tabela}
                            SET "{coluna}" = REPLACE("{coluna}", %s, %s)
                            WHERE "{coluna}" IS NOT NULL
                            AND "{coluna}" LIKE %s
                        """, (char_antigo, char_novo, f'%{char_antigo}%'))
                        
                        linhas_afetadas = cursor.rowcount
                        if linhas_afetadas > 0:
                            print(f"  ✅ {coluna}: {linhas_afetadas} registros corrigidos (substituído '{char_antigo}' por '{char_novo}')")
                            total_corrigidos += linhas_afetadas
                
            except Exception as e:
                print(f"  ❌ Erro ao corrigir {coluna} em {tabela}: {e}")
    
    # Commit das alterações
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n📊 Total de registros corrigidos: {total_corrigidos}")
    return total_corrigidos

def verificar_encoding_banco():
    """
    Verifica a codificação do banco de dados
    """
    print("🔍 Verificando codificação do banco de dados...")
    
    conn = conectar_banco()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Verificar encoding do banco
        cursor.execute("SHOW server_encoding;")
        server_encoding = cursor.fetchone()[0]
        
        cursor.execute("SHOW client_encoding;")
        client_encoding = cursor.fetchone()[0]
        
        cursor.execute("SELECT datname, pg_encoding_to_char(encoding) as encoding FROM pg_database WHERE datname = 'sepromcbmepi';")
        db_encoding = cursor.fetchone()
        
        print(f"📊 Codificação do banco:")
        print(f"   Server encoding: {server_encoding}")
        print(f"   Client encoding: {client_encoding}")
        print(f"   Database encoding: {db_encoding[1] if db_encoding else 'N/A'}")
        
        if server_encoding != 'UTF8' or client_encoding != 'UTF8':
            print("⚠️  ATENÇÃO: O banco não está configurado para UTF-8!")
        else:
            print("✅ Banco configurado corretamente para UTF-8")
            
    except Exception as e:
        print(f"❌ Erro ao verificar encoding: {e}")
    
    cursor.close()
    conn.close()

def backup_antes_correcao():
    """
    Cria um backup antes de fazer as correções
    """
    print("💾 Criando backup antes das correções...")
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_antes_correcao_caracteres_{timestamp}.sql"
    
    try:
        # Criar diretório de backup se não existir
        os.makedirs("backups", exist_ok=True)
        
        # Comando para criar backup
        cmd = f'pg_dump -h localhost -U postgres -d sepromcbmepi > "{backup_file}"'
        
        # Definir senha como variável de ambiente
        os.environ['PGPASSWORD'] = '11322361'
        
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Backup criado: {backup_file}")
            return True
        else:
            print(f"❌ Erro ao criar backup: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Script de Correção de Caracteres no Banco de Dados")
    print("=" * 60)
    
    # Verificar encoding do banco
    verificar_encoding_banco()
    
    print("\n" + "=" * 60)
    
    # Verificar caracteres problemáticos
    problemas = verificar_caracteres_problematicos()
    
    if problemas:
        print(f"\n⚠️  Encontrados {len(problemas)} problemas de caracteres")
        
        # Perguntar se deve corrigir
        resposta = input("\nDeseja corrigir os problemas de caracteres? (s/n): ").lower()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            # Criar backup antes da correção
            if backup_antes_correcao():
                # Corrigir caracteres
                total_corrigidos = corrigir_caracteres_banco()
                print(f"\n✅ Correção concluída! {total_corrigidos} registros corrigidos.")
            else:
                print("\n❌ Backup não foi criado. Correção cancelada por segurança.")
        else:
            print("\n❌ Operação cancelada pelo usuário.")
    else:
        print("\n✅ Nenhum problema de caracteres encontrado no banco de dados!") 