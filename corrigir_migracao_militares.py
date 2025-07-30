#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
import sys

# Configurações diretas
SUPABASE_CONFIG = {
    'host': 'aws-0-sa-east-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.vubnekyyfjcrswaufnla',
    'password': '2YXGdmXESoZAoPkO',
    'port': '6543',
    'options': '-c client_encoding=utf8'
}

LOCAL_CONFIG = {
    'host': 'localhost',
    'database': 'sepromcbmepi',
    'user': 'postgres',
    'password': '11322361',
    'port': '5432',
    'options': '-c client_encoding=latin1'
}

class CorrigirMigracaoMilitares:
    def __init__(self):
        self.supabase_conn = None
        self.local_conn = None
        self.log_file = f"correcao_migracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
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
            self.log(f"ERRO: {descricao}: {e}")
            conn.rollback()
            return False
    
    def formatar_valor(self, valor, campo):
        """Formata valor para SQL baseado no tipo do campo"""
        if valor is None:
            return 'NULL'
        
        # Tratar datas especificamente
        if isinstance(valor, datetime):
            return f"'{valor.strftime('%Y-%m-%d %H:%M:%S')}'"
        
        # Tratar strings
        if isinstance(valor, str):
            # Escapar aspas simples
            valor_escaped = valor.replace("'", "''")
            return f"'{valor_escaped}'"
        
        # Tratar números
        if isinstance(valor, (int, float)):
            return str(valor)
        
        # Tratar booleanos
        if isinstance(valor, bool):
            return 'TRUE' if valor else 'FALSE'
        
        # Para outros tipos, converter para string
        return f"'{str(valor).replace(chr(39), chr(39)+chr(39))}'"
    
    def corrigir_migracao_militares(self):
        """Corrige a migração dos militares"""
        self.log("INICIANDO CORRECAO DA MIGRACAO DE MILITARES")
        self.log("="*60)
        
        # Conectar aos bancos
        self.supabase_conn = self.conectar_banco(SUPABASE_CONFIG, "Supabase")
        self.local_conn = self.conectar_banco(LOCAL_CONFIG, "Local")
        
        if not self.supabase_conn or not self.local_conn:
            self.log("ERRO: Falha na conexao com os bancos")
            return False
        
        # Limpar militares existentes no Supabase
        self.log("LIMPANDO: Removendo militares existentes no Supabase...")
        self.executar_sql(self.supabase_conn, "DELETE FROM militares_militar;", "Limpar militares existentes")
        
        # Buscar militares do banco local
        cursor = self.local_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM militares_militar ORDER BY id")
        militares = cursor.fetchall()
        cursor.close()
        
        self.log(f"INFO: Total de militares para migrar: {len(militares)}")
        
        # Migrar militares em lotes menores
        lote_size = 10
        sucessos = 0
        erros = 0
        
        for i in range(0, len(militares), lote_size):
            lote = militares[i:i+lote_size]
            self.log(f"PROCESSANDO: Lote {i//lote_size + 1} ({len(lote)} militares)")
            
            for militar in lote:
                try:
                    # Construir SQL com tratamento adequado de tipos
                    campos = []
                    valores = []
                    
                    for campo, valor in militar.items():
                        if valor is not None:
                            campos.append(campo)
                            valores.append(self.formatar_valor(valor, campo))
                    
                    sql = f"""
                    INSERT INTO militares_militar ({', '.join(campos)}) 
                    VALUES ({', '.join(valores)});
                    """
                    
                    if self.executar_sql(self.supabase_conn, sql, f"Militar ID: {militar['id']}"):
                        sucessos += 1
                    else:
                        erros += 1
                        
                except Exception as e:
                    self.log(f"ERRO: Erro ao processar militar ID {militar['id']}: {e}")
                    erros += 1
            
            # Pausa entre lotes
            import time
            time.sleep(2)
        
        # Resetar sequência
        self.executar_sql(self.supabase_conn, 
                         "SELECT setval('militares_militar_id_seq', (SELECT MAX(id) FROM militares_militar));", 
                         "Resetar sequencia de militares")
        
        # Estatísticas finais
        self.log("="*60)
        self.log(f"RESULTADO: Migracao de militares concluida")
        self.log(f"SUCESSOS: {sucessos} militares migrados")
        self.log(f"ERROS: {erros} militares com erro")
        self.log(f"TOTAL: {len(militares)} militares processados")
        
        return True
    
    def associar_usuarios(self):
        """Associa usuários aos militares"""
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
        
        sucessos = 0
        for assoc in associacoes:
            sql = f"""
            UPDATE militares_militar 
            SET user_id = {assoc['user_id']} 
            WHERE id = {assoc['militar_id']};
            """
            if self.executar_sql(self.supabase_conn, sql, f"Associacao {assoc['cpf']} -> {assoc['username']}"):
                sucessos += 1
        
        self.log(f"ASSOCIACOES: {sucessos} associacoes realizadas com sucesso")
        return True
    
    def verificar_migracao(self):
        """Verifica se a migração foi bem-sucedida"""
        self.log("VERIFICANDO: Verificando migracao...")
        
        cursor = self.supabase_conn.cursor()
        
        # Verificar usuários
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        total_usuarios = cursor.fetchone()[0]
        self.log(f"INFO: Total de usuarios: {total_usuarios}")
        
        # Verificar militares
        cursor.execute("SELECT COUNT(*) FROM militares_militar")
        total_militares = cursor.fetchone()[0]
        self.log(f"INFO: Total de militares: {total_militares}")
        
        # Verificar associações
        cursor.execute("SELECT COUNT(*) FROM militares_militar WHERE user_id IS NOT NULL")
        militares_com_usuario = cursor.fetchone()[0]
        self.log(f"INFO: Militares com usuario: {militares_com_usuario}")
        
        cursor.execute("SELECT COUNT(*) FROM militares_militar WHERE user_id IS NULL")
        militares_sem_usuario = cursor.fetchone()[0]
        self.log(f"INFO: Militares sem usuario: {militares_sem_usuario}")
        
        cursor.close()
        
        return total_militares > 0
    
    def executar_correcao_completa(self):
        """Executa a correção completa"""
        try:
            # Confirmar com o usuário
            print("CORRECAO DA MIGRACAO DE MILITARES")
            print("="*50)
            print("ATENCAO: Esta operacao ira sobrescrever dados de militares no Supabase!")
            resposta = input("Deseja continuar? (s/N): ").strip().lower()
            
            if resposta != 's':
                self.log("ERRO: Operacao cancelada pelo usuario")
                return False
            
            # Executar correção
            if not self.corrigir_migracao_militares():
                return False
            
            # Associar usuários
            if not self.associar_usuarios():
                return False
            
            # Verificar resultado
            if self.verificar_migracao():
                self.log("SUCESSO: CORRECAO CONCLUIDA COM SUCESSO!")
                return True
            else:
                self.log("ERRO: Correcao falhou - verifique os logs")
                return False
                
        except Exception as e:
            self.log(f"ERRO: Erro durante a correcao: {e}")
            return False
        finally:
            if self.supabase_conn:
                self.supabase_conn.close()
            if self.local_conn:
                self.local_conn.close()
            self.log("INFO: Conexoes fechadas")

def main():
    """Função principal"""
    corretor = CorrigirMigracaoMilitares()
    sucesso = corretor.executar_correcao_completa()
    
    if sucesso:
        print("\nSUCESSO: CORRECAO CONCLUIDA COM SUCESSO!")
        print("INFO: Verifique o arquivo de log para detalhes")
    else:
        print("\nERRO: CORRECAO FALHOU!")
        print("INFO: Verifique o arquivo de log para detalhes")

if __name__ == "__main__":
    main() 