#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRACAO PARA SUPABASE - SEM EMOJIS
===================================

Script de migração sem emojis para evitar problemas de codificação no Windows.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Configurações diretas (baseadas no arquivo .env)
SUPABASE_CONFIG = {
    'host': 'aws-0-sa-east-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.vubnekyyfjcrswaufnla',
    'password': '2YXGdmXESoZAoPkO',
    'port': '6543'
}

LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'sepromcbmepi',
    'user': 'postgres',
    'password': '11322361',
    'port': '5432'
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
            # Adicionar parâmetros de encoding específicos
            if nome == "Supabase":
                config['options'] = '-c client_encoding=utf8'
            else:
                config['options'] = '-c client_encoding=latin1'
            
            conn = psycopg2.connect(**config)
            self.log(f"OK: Conectado ao banco {nome}")
            return conn
        except Exception as e:
            self.log(f"ERRO: Erro ao conectar ao banco {nome}: {e}")
            return None
    
    def executar_sql(self, conn, sql, descricao):
        """Executa SQL com tratamento de erro"""
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            self.log(f"OK: {descricao} - Executado com sucesso")
            return True
        except Exception as e:
            self.log(f"ERRO: Erro em {descricao}: {e}")
            conn.rollback()
            return False
    
    def verificar_conexoes(self):
        """Verifica se as conexões estão funcionando"""
        self.log("VERIFICANDO: Verificando conexoes...")
        
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
        self.log("INICIANDO ETAPA 1: Usuarios e dados basicos")
        
        # Desabilitar triggers
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = replica;", 
                         "Desabilitar triggers")
        
        # Limpar dados existentes (se houver)
        self.executar_sql(self.supabase_conn, 
                         "DELETE FROM auth_user WHERE id > 1;", 
                         "Limpar usuarios existentes")
        
        # Inserir usuários em lotes
        cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM auth_user ORDER BY id")
        usuarios = cursor.fetchall()
        cursor.close()
        
        self.log(f"INFO: Total de usuarios para migrar: {len(usuarios)}")
        
        # Dividir em lotes de 50 usuários
        lote_size = 50
        for i in range(0, len(usuarios), lote_size):
            lote = usuarios[i:i+lote_size]
            self.log(f"PROCESSANDO: Lote {i//lote_size + 1} ({len(lote)} usuarios)")
            
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
                
                self.executar_sql(self.supabase_conn, sql, f"Usuario {usuario['username']}")
            
            # Pausa entre lotes
            import time
            time.sleep(2)
        
        # Resetar sequência
        self.executar_sql(self.supabase_conn, 
                         "SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));", 
                         "Resetar sequencia de usuarios")
        
        self.log("OK: ETAPA 1 CONCLUIDA: Usuarios migrados com sucesso")
        return True
    
    def etapa_2_militares_associacoes(self):
        """ETAPA 2: Militares e associações"""
        self.log("INICIANDO ETAPA 2: Militares e associacoes")
        
        # Limpar militares existentes
        self.executar_sql(self.supabase_conn, 
                         "DELETE FROM militares_militar;", 
                         "Limpar militares existentes")
        
        # Inserir militares em lotes
        cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM militares_militar ORDER BY id")
        militares = cursor.fetchall()
        cursor.close()
        
        self.log(f"INFO: Total de militares para migrar: {len(militares)}")
        
        # Dividir em lotes de 30 militares (mais pesados)
        lote_size = 30
        for i in range(0, len(militares), lote_size):
            lote = militares[i:i+lote_size]
            self.log(f"PROCESSANDO: Lote {i//lote_size + 1} ({len(lote)} militares)")
            
            for militar in lote:
                # Construir SQL dinamicamente para evitar problemas com campos NULL
                campos = []
                valores = []
                
                for campo, valor in militar.items():
                    if valor is not None:
                        if isinstance(valor, str):
                            valores.append(f"'{valor.replace(chr(39), chr(39)+chr(39))}'")
                        elif isinstance(valor, datetime):
                            # Formatar data sem frações de segundo para evitar problemas de sintaxe
                            valores.append(f"'{valor.strftime('%Y-%m-%d %H:%M:%S')}'")
                        else:
                            valores.append(str(valor))
                        campos.append(campo)
                
                sql = f"""
                INSERT INTO militares_militar ({', '.join(campos)}) 
                VALUES ({', '.join(valores)});
                """
                
                self.executar_sql(self.supabase_conn, sql, f"Militar {militar.get('nome', 'ID: ' + str(militar['id']))}")
            
            # Pausa maior entre lotes de militares
            import time
            time.sleep(3)
        
        # Resetar sequência
        self.executar_sql(self.supabase_conn, 
                         "SELECT setval('militares_militar_id_seq', (SELECT MAX(id) FROM militares_militar));", 
                         "Resetar sequencia de militares")
        
        # Associar usuários aos militares
        self.log("ASSOCIANDO: Associando usuarios aos militares...")
        
        cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT m.id as militar_id, m.cpf, u.id as user_id, u.username
            FROM militares_militar m
            LEFT JOIN auth_user u ON m.cpf = u.username
            WHERE u.id IS NOT NULL
        """)
        associacoes = cursor.fetchall()
        cursor.close()
        
        self.log(f"INFO: Total de associacoes para fazer: {len(associacoes)}")
        
        for assoc in associacoes:
            sql = f"""
            UPDATE militares_militar 
            SET user_id = {assoc['user_id']} 
            WHERE id = {assoc['militar_id']};
            """
            self.executar_sql(self.supabase_conn, sql, f"Associacao {assoc['cpf']} -> {assoc['username']}")
        
        self.log("OK: ETAPA 2 CONCLUIDA: Militares e associacoes migrados com sucesso")
        return True
    
    def etapa_3_dados_complementares(self):
        """ETAPA 3: Dados complementares e finalização"""
        self.log("INICIANDO ETAPA 3: Dados complementares e finalizacao")
        
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
            self.log(f"MIGRANDO: Tabela {tabela}")
            
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
                self.log(f"AVISO: Tabela {tabela} nao existe no banco local")
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
                self.log(f"INFO: Tabela {tabela} esta vazia")
                continue
            
            self.log(f"INFO: Total de registros em {tabela}: {total}")
            
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
                
                self.log(f"PROCESSANDO: Lote de {tabela} ({len(registros)} registros)")
                
                for registro in registros:
                    campos = []
                    valores = []
                    
                    for campo, valor in registro.items():
                        if valor is not None:
                            if isinstance(valor, str):
                                valores.append(f"'{valor.replace(chr(39), chr(39)+chr(39))}'")
                            else:
                                valores.append(str(valor))
                            campos.append(campo)
                    
                    sql = f"""
                    INSERT INTO {tabela} ({', '.join(campos)}) 
                    VALUES ({', '.join(valores)});
                    """
                    
                    self.executar_sql(self.supabase_conn, sql, f"{tabela} ID: {registro['id']}")
                
                offset += lote_size
                import time
                time.sleep(2)  # Pausa entre lotes
            
            # Resetar sequência
            self.executar_sql(self.supabase_conn, 
                             f"SELECT setval('{tabela}_id_seq', (SELECT MAX(id) FROM {tabela}));", 
                             f"Resetar sequencia de {tabela}")
        
        # Reabilitar triggers
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = DEFAULT;", 
                         "Reabilitar triggers")
        
        self.log("OK: ETAPA 3 CONCLUIDA: Dados complementares migrados com sucesso")
        return True
    
    def verificar_migracao(self):
        """Verifica se a migração foi bem-sucedida"""
        self.log("VERIFICANDO: Verificando migracao...")
        
        verificacoes = [
            ("Total de usuarios", "SELECT COUNT(*) FROM auth_user"),
            ("Total de militares", "SELECT COUNT(*) FROM militares_militar"),
            ("Militares com usuario", "SELECT COUNT(*) FROM militares_militar WHERE user_id IS NOT NULL"),
            ("Militares sem usuario", "SELECT COUNT(*) FROM militares_militar WHERE user_id IS NULL"),
            ("Total de comissoes", "SELECT COUNT(*) FROM militares_comissaopromocao"),
            ("Total de quadros", "SELECT COUNT(*) FROM militares_quadroacesso"),
        ]
        
        for descricao, sql in verificacoes:
            try:
                cursor = self.supabase_conn.cursor()
                cursor.execute(sql)
                resultado = cursor.fetchone()[0]
                cursor.close()
                self.log(f"INFO: {descricao}: {resultado}")
            except Exception as e:
                self.log(f"ERRO: Erro ao verificar {descricao}: {e}")
    
    def executar_migracao_completa(self):
        """Executa a migração completa em 3 etapas"""
        self.log("INICIANDO MIGRACAO COMPLETA PARA SUPABASE")
        self.log("="*60)
        
        # Verificar conexões
        if not self.verificar_conexoes():
            self.log("ERRO: Falha na verificacao de conexoes. Abortando migracao.")
            return False
        
        try:
            # Etapa 1
            if not self.etapa_1_usuarios_basicos():
                self.log("ERRO: Falha na Etapa 1. Abortando migracao.")
                return False
            
            self.log("PAUSA: Pausa de 5 segundos antes da Etapa 2...")
            import time
            time.sleep(5)
            
            # Etapa 2
            if not self.etapa_2_militares_associacoes():
                self.log("ERRO: Falha na Etapa 2. Abortando migracao.")
                return False
            
            self.log("PAUSA: Pausa de 5 segundos antes da Etapa 3...")
            time.sleep(5)
            
            # Etapa 3
            if not self.etapa_3_dados_complementares():
                self.log("ERRO: Falha na Etapa 3. Abortando migracao.")
                return False
            
            # Verificação final
            self.verificar_migracao()
            
            self.log("SUCESSO: MIGRACAO CONCLUIDA COM SUCESSO!")
            self.log("="*60)
            return True
            
        except Exception as e:
            self.log(f"ERRO: Erro durante a migracao: {e}")
            return False
        finally:
            # Fechar conexões
            if self.supabase_conn:
                self.supabase_conn.close()
            if self.local_conn:
                self.local_conn.close()
            self.log("INFO: Conexoes fechadas")

def main():
    """Função principal"""
    print("MIGRACAO PARA SUPABASE - SEM EMOJIS")
    print("="*50)
    
    # Verificar variáveis de ambiente
    if not SUPABASE_CONFIG['password']:
        print("ERRO: Variavel SUPABASE_PASSWORD nao configurada")
        print("Configure as variaveis de ambiente:")
        print("export SUPABASE_HOST=db.xxxxxxxxxxxx.supabase.co")
        print("export SUPABASE_PASSWORD=sua_senha")
        print("export LOCAL_DB_PASSWORD=sua_senha_local")
        return
    
    # Confirmar execução
    print("ATENCAO: Esta operacao ira sobrescrever dados no Supabase!")
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta != 's':
        print("ERRO: Migracao cancelada pelo usuario")
        return
    
    # Executar migração
    migracao = MigracaoSupabase()
    sucesso = migracao.executar_migracao_completa()
    
    if sucesso:
        print("\nSUCESSO: MIGRACAO CONCLUIDA COM SUCESSO!")
        print("INFO: Verifique o arquivo de log para detalhes")
    else:
        print("\nERRO: MIGRACAO FALHOU!")
        print("INFO: Verifique o arquivo de log para detalhes")

if __name__ == "__main__":
    main() 