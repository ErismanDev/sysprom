#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRAÇÃO PARA SUPABASE - 3 ETAPAS
=================================

Este script realiza a migração dos dados para o Supabase dividida em 3 etapas:
1. Etapa 1: Usuários e dados básicos
2. Etapa 2: Militares e associações
3. Etapa 3: Dados complementares e finalização

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Configurações do Supabase
SUPABASE_CONFIG = {
    'host': os.getenv('SUPABASE_HOST', 'db.xxxxxxxxxxxx.supabase.co'),
    'database': os.getenv('SUPABASE_DB', 'postgres'),
    'user': os.getenv('SUPABASE_USER', 'postgres'),
    'password': os.getenv('SUPABASE_PASSWORD', ''),
    'port': os.getenv('SUPABASE_PORT', '5432')
}

# Configurações do banco local
LOCAL_CONFIG = {
    'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
    'database': os.getenv('LOCAL_DB_NAME', 'sepromcbmepi'),
    'user': os.getenv('LOCAL_DB_USER', 'postgres'),
    'password': os.getenv('LOCAL_DB_PASSWORD', ''),
    'port': os.getenv('LOCAL_DB_PORT', '5432')
}

class MigracaoSupabase:
    def __init__(self):
        self.supabase_conn = None
        self.local_conn = None
        self.log_file = f"migracao_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
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
    
    def etapa_1_usuarios_basicos(self):
        """ETAPA 1: Usuários e dados básicos"""
        self.log("🚀 INICIANDO ETAPA 1: Usuários e dados básicos")
        
        # Desabilitar triggers
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = replica;", 
                         "Desabilitar triggers")
        
        # Limpar dados existentes (se houver)
        self.executar_sql(self.supabase_conn, 
                         "DELETE FROM auth_user WHERE id > 1;", 
                         "Limpar usuários existentes")
        
        # Inserir usuários em lotes
        cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM auth_user ORDER BY id")
        usuarios = cursor.fetchall()
        cursor.close()
        
        self.log(f"📊 Total de usuários para migrar: {len(usuarios)}")
        
        # Dividir em lotes de 50 usuários
        lote_size = 50
        for i in range(0, len(usuarios), lote_size):
            lote = usuarios[i:i+lote_size]
            self.log(f"📦 Processando lote {i//lote_size + 1} ({len(lote)} usuários)")
            
            for usuario in lote:
                sql = f"""
                INSERT INTO auth_user (id, password, last_login, is_superuser, username, 
                                     first_name, last_name, email, is_staff, is_active, date_joined) 
                VALUES ({usuario['id']}, '{usuario['password']}', 
                        {f"'{usuario['last_login']}'" if usuario['last_login'] else 'NULL'}, 
                        {usuario['is_superuser']}, '{usuario['username']}', 
                        '{usuario['first_name']}', '{usuario['last_name']}', 
                        '{usuario['email']}', {usuario['is_staff']}, 
                        {usuario['is_active']}, '{usuario['date_joined']}');
                """
                
                self.executar_sql(self.supabase_conn, sql, f"Usuário {usuario['username']}")
            
            # Pausa entre lotes
            time.sleep(2)
        
        # Resetar sequência
        self.executar_sql(self.supabase_conn, 
                         "SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));", 
                         "Resetar sequência de usuários")
        
        self.log("✅ ETAPA 1 CONCLUÍDA: Usuários migrados com sucesso")
        return True
    
    def etapa_2_militares_associacoes(self):
        """ETAPA 2: Militares e associações"""
        self.log("🚀 INICIANDO ETAPA 2: Militares e associações")
        
        # Limpar militares existentes
        self.executar_sql(self.supabase_conn, 
                         "DELETE FROM militares_militar;", 
                         "Limpar militares existentes")
        
        # Inserir militares em lotes
        cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM militares_militar ORDER BY id")
        militares = cursor.fetchall()
        cursor.close()
        
        self.log(f"📊 Total de militares para migrar: {len(militares)}")
        
        # Dividir em lotes de 30 militares (mais pesados)
        lote_size = 30
        for i in range(0, len(militares), lote_size):
            lote = militares[i:i+lote_size]
            self.log(f"📦 Processando lote {i//lote_size + 1} ({len(lote)} militares)")
            
            for militar in lote:
                # Construir SQL dinamicamente para evitar problemas com campos NULL
                campos = []
                valores = []
                
                for campo, valor in militar.items():
                    if valor is not None:
                        if isinstance(valor, str):
                            valores.append(f"'{valor.replace("'", "''")}'")
                        else:
                            valores.append(str(valor))
                        campos.append(campo)
                
                sql = f"""
                INSERT INTO militares_militar ({', '.join(campos)}) 
                VALUES ({', '.join(valores)});
                """
                
                self.executar_sql(self.supabase_conn, sql, f"Militar {militar.get('nome', 'ID: ' + str(militar['id']))}")
            
            # Pausa maior entre lotes de militares
            time.sleep(3)
        
        # Resetar sequência
        self.executar_sql(self.supabase_conn, 
                         "SELECT setval('militares_militar_id_seq', (SELECT MAX(id) FROM militares_militar));", 
                         "Resetar sequência de militares")
        
        # Associar usuários aos militares
        self.log("🔗 Associando usuários aos militares...")
        
        cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT m.id as militar_id, m.cpf, m.nome, u.id as user_id, u.username
            FROM militares_militar m
            LEFT JOIN auth_user u ON m.cpf = u.username
            WHERE u.id IS NOT NULL
        """)
        associacoes = cursor.fetchall()
        cursor.close()
        
        self.log(f"📊 Total de associações para fazer: {len(associacoes)}")
        
        for assoc in associacoes:
            sql = f"""
            UPDATE militares_militar 
            SET user_id = {assoc['user_id']} 
            WHERE id = {assoc['militar_id']};
            """
            self.executar_sql(self.supabase_conn, sql, f"Associação {assoc['nome']} -> {assoc['username']}")
        
        self.log("✅ ETAPA 2 CONCLUÍDA: Militares e associações migrados com sucesso")
        return True
    
    def etapa_3_dados_complementares(self):
        """ETAPA 3: Dados complementares e finalização"""
        self.log("🚀 INICIANDO ETAPA 3: Dados complementares e finalização")
        
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
                continue
            
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
                continue
            
            self.log(f"📊 Total de registros em {tabela}: {total}")
            
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
                            if isinstance(valor, str):
                                valores.append(f"'{valor.replace("'", "''")}'")
                            else:
                                valores.append(str(valor))
                            campos.append(campo)
                    
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
        
        # Reabilitar triggers
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = DEFAULT;", 
                         "Reabilitar triggers")
        
        self.log("✅ ETAPA 3 CONCLUÍDA: Dados complementares migrados com sucesso")
        return True
    
    def verificar_migracao(self):
        """Verifica se a migração foi bem-sucedida"""
        self.log("🔍 Verificando migração...")
        
        verificacoes = [
            ("Total de usuários", "SELECT COUNT(*) FROM auth_user"),
            ("Total de militares", "SELECT COUNT(*) FROM militares_militar"),
            ("Militares com usuário", "SELECT COUNT(*) FROM militares_militar WHERE user_id IS NOT NULL"),
            ("Militares sem usuário", "SELECT COUNT(*) FROM militares_militar WHERE user_id IS NULL"),
            ("Total de comissões", "SELECT COUNT(*) FROM militares_comissaopromocao"),
            ("Total de quadros", "SELECT COUNT(*) FROM militares_quadroacesso"),
        ]
        
        for descricao, sql in verificacoes:
            try:
                cursor = self.supabase_conn.cursor()
                cursor.execute(sql)
                resultado = cursor.fetchone()[0]
                cursor.close()
                self.log(f"📊 {descricao}: {resultado}")
            except Exception as e:
                self.log(f"❌ Erro ao verificar {descricao}: {e}")
    
    def executar_migracao_completa(self):
        """Executa a migração completa em 3 etapas"""
        self.log("🚀 INICIANDO MIGRAÇÃO COMPLETA PARA SUPABASE")
        self.log("=" * 60)
        
        # Verificar conexões
        if not self.verificar_conexoes():
            self.log("❌ Falha na verificação de conexões. Abortando migração.")
            return False
        
        try:
            # Etapa 1
            if not self.etapa_1_usuarios_basicos():
                self.log("❌ Falha na Etapa 1. Abortando migração.")
                return False
            
            self.log("⏸️ Pausa de 5 segundos antes da Etapa 2...")
            time.sleep(5)
            
            # Etapa 2
            if not self.etapa_2_militares_associacoes():
                self.log("❌ Falha na Etapa 2. Abortando migração.")
                return False
            
            self.log("⏸️ Pausa de 5 segundos antes da Etapa 3...")
            time.sleep(5)
            
            # Etapa 3
            if not self.etapa_3_dados_complementares():
                self.log("❌ Falha na Etapa 3. Abortando migração.")
                return False
            
            # Verificação final
            self.verificar_migracao()
            
            self.log("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            self.log("=" * 60)
            return True
            
        except Exception as e:
            self.log(f"❌ Erro durante a migração: {e}")
            return False
        finally:
            # Fechar conexões
            if self.supabase_conn:
                self.supabase_conn.close()
            if self.local_conn:
                self.local_conn.close()
            self.log("🔌 Conexões fechadas")

def main():
    """Função principal"""
    print("🚀 MIGRAÇÃO PARA SUPABASE - 3 ETAPAS")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    if not SUPABASE_CONFIG['password']:
        print("❌ Variável SUPABASE_PASSWORD não configurada")
        print("Configure as variáveis de ambiente:")
        print("export SUPABASE_HOST=db.xxxxxxxxxxxx.supabase.co")
        print("export SUPABASE_PASSWORD=sua_senha")
        print("export LOCAL_DB_PASSWORD=sua_senha_local")
        return
    
    # Confirmar execução
    print("⚠️ ATENÇÃO: Esta operação irá sobrescrever dados no Supabase!")
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta != 's':
        print("❌ Migração cancelada pelo usuário")
        return
    
    # Executar migração
    migracao = MigracaoSupabase()
    sucesso = migracao.executar_migracao_completa()
    
    if sucesso:
        print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("📋 Verifique o arquivo de log para detalhes")
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("📋 Verifique o arquivo de log para detalhes")

if __name__ == "__main__":
    main() 