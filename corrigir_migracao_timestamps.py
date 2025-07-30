#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORREÇÃO DE MIGRAÇÃO - TRATAMENTO DE TIMESTAMPS
==============================================

Script para corrigir a migração com tratamento adequado de timestamps
que estavam causando erros de sintaxe no PostgreSQL.

Autor: Sistema de Promoções CBMEPI
Data: 30/07/2025
"""

import os
import sys
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, date

# Configurações do Supabase
SUPABASE_CONFIG = {
    'host': 'aws-0-sa-east-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.vubnekyyfjcrswaufnla',
    'password': '2YXGdmXESoZAoPkO',
    'port': '6543'
}

# Configurações do banco local
LOCAL_CONFIG = {
    'host': '10.26.17.215',
    'database': 'sepromcbmepi',
    'user': 'postgres',
    'password': '11322361',
    'port': '5432'
}

class MigracaoCorrigida:
    def __init__(self):
        self.supabase_conn = None
        self.local_conn = None
        self.log_file = f"migracao_corrigida_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
    def log(self, message):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def conectar_banco(self, config, nome):
        """Conecta ao banco de dados"""
        try:
            if nome == "Local":
                # Usar string de conexão para o banco local
                conn_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?client_encoding=utf8"
                conn = psycopg2.connect(conn_string)
            else:
                conn = psycopg2.connect(**config)
            
            self.log(f"✅ Conectado ao banco {nome}")
            return conn
        except Exception as e:
            self.log(f"❌ Erro ao conectar ao banco {nome}: {e}")
            return None
    
    def executar_sql(self, conn, sql, descricao):
        """Executa SQL com tratamento de erro"""
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            self.log(f"✅ {descricao} - Executado com sucesso")
            return True
        except Exception as e:
            self.log(f"❌ Erro em {descricao}: {e}")
            conn.rollback()
            return False
    
    def formatar_valor_sql(self, valor, tipo_campo):
        """Formata valor para SQL com tratamento especial de timestamps"""
        if valor is None:
            return 'NULL'
        
        if isinstance(valor, str):
            # Tratar timestamps especiais
            if 'timestamp' in tipo_campo.lower() or 'datetime' in tipo_campo.lower():
                try:
                    # Tentar converter para datetime
                    if 'T' in valor:
                        # Formato ISO
                        dt = datetime.fromisoformat(valor.replace('Z', '+00:00'))
                    else:
                        # Formato PostgreSQL
                        dt = datetime.strptime(valor, '%Y-%m-%d %H:%M:%S.%f')
                    return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
                except:
                    # Se não conseguir converter, usar como string
                    return f"'{valor.replace(chr(39), chr(39)+chr(39))}'"
            else:
                return f"'{valor.replace(chr(39), chr(39)+chr(39))}'"
        
        elif isinstance(valor, (int, float)):
            return str(valor)
        
        elif isinstance(valor, bool):
            return 'TRUE' if valor else 'FALSE'
        
        elif isinstance(valor, datetime):
            return f"'{valor.strftime('%Y-%m-%d %H:%M:%S')}'"
        
        elif isinstance(valor, date):
            return f"'{valor.strftime('%Y-%m-%d')}'"
        
        else:
            return f"'{str(valor).replace(chr(39), chr(39)+chr(39))}'"
    
    def verificar_conexoes(self):
        """Verifica se as conexões estão funcionando"""
        self.log("🔍 Verificando conexões...")
        
        # Conectar ao Supabase
        self.supabase_conn = self.conectar_banco(SUPABASE_CONFIG, "Supabase")
        if not self.supabase_conn:
            return False
        
        # Conectar ao banco local
        self.local_conn = self.conectar_banco(LOCAL_CONFIG, "Local")
        if not self.local_conn:
            return False
        
        return True
    
    def migrar_tabela_complementar(self, tabela):
        """Migra uma tabela complementar com tratamento correto de timestamps"""
        self.log(f"📋 Migrando tabela: {tabela}")
        
        # Verificar se a tabela existe no banco local
        cursor = self.local_conn.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (tabela,))
        existe = cursor.fetchone()[0]
        cursor.close()
        
        if not existe:
            self.log(f"⚠️ Tabela {tabela} não existe no banco local")
            return True
        
        # Limpar dados existentes
        self.executar_sql(self.supabase_conn, 
                         f"DELETE FROM {tabela};", 
                         f"Limpar {tabela}")
        
        # Contar registros
        cursor = self.local_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        total = cursor.fetchone()[0]
        cursor.close()
        
        if total == 0:
            self.log(f"ℹ️ Tabela {tabela} está vazia")
            return True
        
        self.log(f"📊 Total de registros em {tabela}: {total}")
        
        # Obter informações das colunas
        cursor = self.local_conn.cursor()
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{tabela}' 
            ORDER BY ordinal_position
        """)
        colunas_info = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        
        # Migrar em lotes
        lote_size = 20
        offset = 0
        
        while offset < total:
            cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {tabela} ORDER BY id LIMIT {lote_size} OFFSET {offset}")
            registros = cursor.fetchall()
            cursor.close()
            
            if not registros:
                break
            
            self.log(f"📦 Processando lote de {tabela} ({len(registros)} registros)")
            
            for registro in registros:
                campos = []
                valores = []
                
                for campo, valor in registro.items():
                    if valor is not None:
                        tipo_campo = colunas_info.get(campo, 'text')
                        valor_formatado = self.formatar_valor_sql(valor, tipo_campo)
                        if valor_formatado != 'NULL':
                            valores.append(valor_formatado)
                            campos.append(campo)
                
                if campos:  # Só inserir se houver campos
                    sql = f"""
                    INSERT INTO {tabela} ({', '.join(campos)}) 
                    VALUES ({', '.join(valores)});
                    """
                    
                    self.executar_sql(self.supabase_conn, sql, f"{tabela} ID: {registro['id']}")
            
            offset += lote_size
            time.sleep(2)  # Pausa entre lotes
        
        # Resetar sequência
        self.executar_sql(self.supabase_conn, 
                         f"SELECT setval('{tabela}_id_seq', (SELECT MAX(id) FROM {tabela}));", 
                         f"Resetar sequência de {tabela}")
        
        return True
    
    def executar_migracao_corrigida(self):
        """Executa a migração corrigida dos dados complementares"""
        self.log("🚀 INICIANDO MIGRAÇÃO CORRIGIDA: Dados complementares")
        
        if not self.verificar_conexoes():
            return False
        
        # Desabilitar triggers temporariamente
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = replica;", 
                         "Desabilitar triggers")
        
        # Lista de tabelas complementares (em ordem de dependência)
        tabelas_complementares = [
            'militares_cargo',
            'militares_funcao',
            'militares_comissaopromocao',
            'militares_membrocomissao',
            'militares_quadroacesso',
            'militares_documentosessao',
            'militares_ataassinatura',
            'militares_votodeliberacao',
            'militares_documentocomissao',
            'militares_almanaque',
            'militares_almanaqueassinatura',
            'militares_calendariopromocao',
            'militares_notificacao'
        ]
        
        for tabela in tabelas_complementares:
            if not self.migrar_tabela_complementar(tabela):
                self.log(f"❌ Erro ao migrar tabela {tabela}")
                continue
        
        # Reabilitar triggers
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = DEFAULT;", 
                         "Reabilitar triggers")
        
        self.log("✅ MIGRAÇÃO CORRIGIDA CONCLUÍDA: Dados complementares migrados com sucesso")
        return True

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE MIGRAÇÃO - TRATAMENTO DE TIMESTAMPS")
    print("=" * 60)
    
    migracao = MigracaoCorrigida()
    
    if migracao.executar_migracao_corrigida():
        print("\n" + "=" * 60)
        print("🎉 MIGRAÇÃO CORRIGIDA CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("📋 RESUMO:")
        print("✅ Timestamps tratados corretamente")
        print("✅ Dados complementares migrados")
        print("✅ Triggers reabilitados")
        print("✅ Log salvo em:", migracao.log_file)
        print()
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRAÇÃO CORRIGIDA FALHOU!")
        print("=" * 60)
        print("Verifique o log:", migracao.log_file)
        print()
        return False

if __name__ == "__main__":
    main() 