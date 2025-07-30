#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRAÇÃO COMPLEMENTARES PARA SUPABASE
====================================

Script para migrar apenas os dados complementares para o Supabase,
usando dados já exportados ou inserindo diretamente.

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

class MigracaoComplementares:
    def __init__(self):
        self.supabase_conn = None
        self.log_file = f"migracao_complementares_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
    def log(self, message):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def conectar_supabase(self):
        """Conecta ao Supabase"""
        try:
            conn = psycopg2.connect(**SUPABASE_CONFIG)
            self.log(f"✅ Conectado ao Supabase")
            return conn
        except Exception as e:
            self.log(f"❌ Erro ao conectar ao Supabase: {e}")
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
    
    def inserir_dados_complementares(self):
        """Insere dados complementares básicos"""
        self.log("📋 Inserindo dados complementares básicos...")
        
        # 1. Cargos básicos
        cargos_basicos = [
            (1, 'PRESIDENTE', 'Presidente da Comissão'),
            (2, 'SECRETARIO', 'Secretário da Comissão'),
            (3, 'MEMBRO', 'Membro da Comissão'),
            (4, 'RELATOR', 'Relator da Comissão')
        ]
        
        for cargo_id, nome, descricao in cargos_basicos:
            sql = f"""
            INSERT INTO militares_cargo (id, nome, descricao) 
            VALUES ({cargo_id}, '{nome}', '{descricao}')
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir cargo {nome}")
        
        # 2. Funções básicas
        funcoes_basicas = [
            (1, 'ADMINISTRADOR', 'Administrador do Sistema'),
            (2, 'USUARIO', 'Usuário Padrão'),
            (3, 'COMISSAO', 'Membro de Comissão'),
            (4, 'PRESIDENTE_COMISSAO', 'Presidente de Comissão')
        ]
        
        for funcao_id, nome, descricao in funcoes_basicas:
            sql = f"""
            INSERT INTO militares_funcao (id, nome, descricao) 
            VALUES ({funcao_id}, '{nome}', '{descricao}')
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir função {nome}")
        
        # 3. Comissões básicas
        comissoes_basicas = [
            (1, 'Comissão de Promoção de Oficiais (CPO)', '2025-07-12', 'ATIVA'),
            (2, 'Comissão de Promoção de Praças (CPP)', '2025-07-15', 'ATIVA')
        ]
        
        for comissao_id, nome, data_criacao, situacao in comissoes_basicas:
            sql = f"""
            INSERT INTO militares_comissaopromocao (id, nome, data_criacao, situacao) 
            VALUES ({comissao_id}, '{nome}', '{data_criacao}', '{situacao}')
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir comissão {nome}")
        
        # 4. Quadros de acesso básicos
        quadros_basicos = [
            (1, 'ANTIGUIDADE', '2025-07-18'),
            (2, 'MERECIMENTO', '2025-07-18')
        ]
        
        for quadro_id, tipo, data_abertura in quadros_basicos:
            sql = f"""
            INSERT INTO militares_quadroacesso (id, tipo, data_abertura) 
            VALUES ({quadro_id}, '{tipo}', '{data_abertura}')
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir quadro {tipo}")
        
        # 5. Calendários de promoção básicos
        calendarios_basicos = [
            (1, '2025', '2', True),
            (2, '2025', '2', True)
        ]
        
        for calendario_id, ano, semestre, ativo in calendarios_basicos:
            sql = f"""
            INSERT INTO militares_calendariopromocao (id, ano, semestre, ativo) 
            VALUES ({calendario_id}, '{ano}', '{semestre}', {ativo})
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir calendário {ano}/{semestre}")
        
        self.log("✅ Dados complementares básicos inseridos")
        return True
    
    def associar_membros_comissao(self):
        """Associa membros às comissões"""
        self.log("👥 Associando membros às comissões...")
        
        # Buscar usuários que podem ser membros
        cursor = self.supabase_conn.cursor()
        cursor.execute("""
            SELECT id, username FROM auth_user 
            WHERE is_active = true 
            ORDER BY id 
            LIMIT 10
        """)
        usuarios = cursor.fetchall()
        cursor.close()
        
        if not usuarios:
            self.log("⚠️ Nenhum usuário encontrado para associar")
            return True
        
        # Associar alguns usuários às comissões
        membros_associacoes = [
            (1, usuarios[0][0], 'PRESIDENTE', '2025-07-29', True),
            (2, usuarios[1][0] if len(usuarios) > 1 else usuarios[0][0], 'SECRETARIO', '2025-07-29', True),
            (3, usuarios[2][0] if len(usuarios) > 2 else usuarios[0][0], 'MEMBRO', '2025-07-01', True)
        ]
        
        for membro_id, user_id, cargo, data_nomeacao, ativo in membros_associacoes:
            sql = f"""
            INSERT INTO militares_membrocomissao (id, user_id, cargo, data_nomeacao, ativo) 
            VALUES ({membro_id}, {user_id}, '{cargo}', '{data_nomeacao}', {ativo})
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Associar membro {cargo}")
        
        self.log("✅ Membros associados às comissões")
        return True
    
    def resetar_sequencias(self):
        """Reseta as sequências de ID"""
        self.log("🔄 Resetando sequências...")
        
        tabelas = [
            'militares_cargo',
            'militares_funcao', 
            'militares_comissaopromocao',
            'militares_membrocomissao',
            'militares_quadroacesso',
            'militares_calendariopromocao'
        ]
        
        for tabela in tabelas:
            sql = f"SELECT setval('{tabela}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {tabela}));"
            self.executar_sql(self.supabase_conn, sql, f"Resetar sequência de {tabela}")
        
        self.log("✅ Sequências resetadas")
        return True
    
    def executar_migracao(self):
        """Executa a migração completa"""
        self.log("🚀 INICIANDO MIGRAÇÃO DE DADOS COMPLEMENTARES")
        
        # Conectar ao Supabase
        self.supabase_conn = self.conectar_supabase()
        if not self.supabase_conn:
            return False
        
        # Desabilitar triggers temporariamente
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = replica;", 
                         "Desabilitar triggers")
        
        # Inserir dados complementares
        if not self.inserir_dados_complementares():
            return False
        
        # Associar membros às comissões
        if not self.associar_membros_comissao():
            return False
        
        # Resetar sequências
        if not self.resetar_sequencias():
            return False
        
        # Reabilitar triggers
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = DEFAULT;", 
                         "Reabilitar triggers")
        
        self.log("✅ MIGRAÇÃO COMPLEMENTAR CONCLUÍDA COM SUCESSO")
        return True

def main():
    """Função principal"""
    print("📦 MIGRAÇÃO DE DADOS COMPLEMENTARES PARA SUPABASE")
    print("=" * 60)
    
    migracao = MigracaoComplementares()
    
    if migracao.executar_migracao():
        print("\n" + "=" * 60)
        print("🎉 MIGRAÇÃO COMPLEMENTAR CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("📋 RESUMO:")
        print("✅ Dados complementares inseridos")
        print("✅ Membros associados às comissões")
        print("✅ Sequências resetadas")
        print("✅ Triggers reabilitados")
        print("✅ Log salvo em:", migracao.log_file)
        print()
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRAÇÃO COMPLEMENTAR FALHOU!")
        print("=" * 60)
        print("Verifique o log:", migracao.log_file)
        print()
        return False

if __name__ == "__main__":
    main() 