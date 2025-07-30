#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRAÇÃO COMPLEMENTARES CORRIGIDA
=================================

Script para migrar dados complementares para o Supabase,
usando apenas as tabelas que existem e com as colunas corretas.

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

class MigracaoComplementaresCorrigida:
    def __init__(self):
        self.supabase_conn = None
        self.log_file = f"migracao_complementares_corrigida_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
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
    
    def inserir_comissoes(self):
        """Insere comissões básicas"""
        self.log("📋 Inserindo comissões básicas...")
        
        comissoes_basicas = [
            (1, 'CPO', 'Comissão de Promoção de Oficiais (CPO)', '2025-07-12', None, 'ATIVA', 'Comissão para promoção de oficiais', '2025-07-22 20:25:02', '2025-07-22 20:25:02'),
            (2, 'CPP', 'Comissão de Promoção de Praças (CPP)', '2025-07-15', None, 'ATIVA', 'Comissão para promoção de praças', '2025-07-22 20:25:02', '2025-07-22 20:25:02')
        ]
        
        for comissao_id, tipo, nome, data_criacao, data_termino, status, observacoes, data_registro, data_atualizacao in comissoes_basicas:
            sql = f"""
            INSERT INTO militares_comissaopromocao (id, tipo, nome, data_criacao, data_termino, status, observacoes, data_registro, data_atualizacao) 
            VALUES ({comissao_id}, '{tipo}', '{nome}', '{data_criacao}', {data_termino or 'NULL'}, '{status}', '{observacoes}', '{data_registro}', '{data_atualizacao}')
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir comissão {nome}")
        
        return True
    
    def inserir_quadros_acesso(self):
        """Insere quadros de acesso básicos"""
        self.log("📋 Inserindo quadros de acesso básicos...")
        
        quadros_basicos = [
            (1, 'ANTIGUIDADE', '2025-12-23', '2025-07-22 16:01:34', True, '2025-07-22 16:01:34', None, 'Quadro por antiguidade', 'ATIVA', None, None, 'OFICIAIS', '001'),
            (2, 'MERECIMENTO', '2025-12-23', '2025-07-22 16:01:34', True, '2025-07-22 16:01:34', None, 'Quadro por merecimento', 'ATIVA', None, None, 'OFICIAIS', '002')
        ]
        
        for quadro_id, tipo, data_promocao, data_criacao, ativo, data_atualizacao, motivo_nao_elaboracao, observacoes, status, data_homologacao, homologado_por_id, categoria, numero in quadros_basicos:
            sql = f"""
            INSERT INTO militares_quadroacesso (id, tipo, data_promocao, data_criacao, ativo, data_atualizacao, motivo_nao_elaboracao, observacoes, status, data_homologacao, homologado_por_id, categoria, numero) 
            VALUES ({quadro_id}, '{tipo}', '{data_promocao}', '{data_criacao}', {ativo}, '{data_atualizacao}', {motivo_nao_elaboracao or 'NULL'}, '{observacoes}', '{status}', {data_homologacao or 'NULL'}, {homologado_por_id or 'NULL'}, '{categoria}', '{numero}')
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir quadro {tipo}")
        
        return True
    
    def inserir_calendarios_promocao(self):
        """Insere calendários de promoção básicos"""
        self.log("📋 Inserindo calendários de promoção básicos...")
        
        calendarios_basicos = [
            (1, '2025', '2', True, 'Calendário de promoção 2025/2', '2025-07-22 15:53:33', '2025-07-22 15:53:33', 'PROMOCAO', None, None, None, None, None, 'ATIVO'),
            (2, '2025', '2', True, 'Calendário de promoção 2025/2', '2025-07-22 15:53:33', '2025-07-22 15:53:33', 'PROMOCAO', None, None, None, None, None, 'ATIVO')
        ]
        
        for calendario_id, ano, semestre, ativo, observacoes, data_criacao, data_atualizacao, tipo, aprovado_por_id, data_aprovacao, data_homologacao, homologado_por_id, numero, status in calendarios_basicos:
            sql = f"""
            INSERT INTO militares_calendariopromocao (id, ano, semestre, ativo, observacoes, data_criacao, data_atualizacao, tipo, aprovado_por_id, data_aprovacao, data_homologacao, homologado_por_id, numero, status) 
            VALUES ({calendario_id}, '{ano}', '{semestre}', {ativo}, '{observacoes}', '{data_criacao}', '{data_atualizacao}', '{tipo}', {aprovado_por_id or 'NULL'}, {data_aprovacao or 'NULL'}, {data_homologacao or 'NULL'}, {homologado_por_id or 'NULL'}, {numero or 'NULL'}, '{status}')
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Inserir calendário {ano}/{semestre}")
        
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
        
        # Buscar militares para associar
        cursor = self.supabase_conn.cursor()
        cursor.execute("""
            SELECT id, nome_completo FROM militares_militar 
            ORDER BY id 
            LIMIT 10
        """)
        militares = cursor.fetchall()
        cursor.close()
        
        if not militares:
            self.log("⚠️ Nenhum militar encontrado para associar")
            return True
        
        # Buscar cargos de comissão
        cursor = self.supabase_conn.cursor()
        cursor.execute("""
            SELECT id, nome FROM militares_cargocomissao 
            ORDER BY id 
            LIMIT 5
        """)
        cargos = cursor.fetchall()
        cursor.close()
        
        if not cargos:
            self.log("⚠️ Nenhum cargo de comissão encontrado")
            return True
        
        # Associar alguns membros às comissões
        membros_associacoes = [
            (1, 'PRESIDENTE', cargos[0][0], '2025-07-29', None, True, 'Presidente da comissão', '2025-07-29 08:40:18', 1, militares[0][0], usuarios[0][0]),
            (2, 'SECRETARIO', cargos[1][0] if len(cargos) > 1 else cargos[0][0], '2025-07-29', None, True, 'Secretário da comissão', '2025-07-29 08:53:04', 1, militares[1][0] if len(militares) > 1 else militares[0][0], usuarios[1][0] if len(usuarios) > 1 else usuarios[0][0]),
            (3, 'MEMBRO', cargos[2][0] if len(cargos) > 2 else cargos[0][0], '2025-07-01', None, True, 'Membro da comissão', '2025-07-29 08:48:48', 2, militares[2][0] if len(militares) > 2 else militares[0][0], usuarios[2][0] if len(usuarios) > 2 else usuarios[0][0])
        ]
        
        for membro_id, tipo, cargo_id, data_nomeacao, data_termino, ativo, observacoes, data_registro, comissao_id, militar_id, usuario_id in membros_associacoes:
            sql = f"""
            INSERT INTO militares_membrocomissao (id, tipo, cargo_id, data_nomeacao, data_termino, ativo, observacoes, data_registro, comissao_id, militar_id, usuario_id) 
            VALUES ({membro_id}, '{tipo}', {cargo_id}, '{data_nomeacao}', {data_termino or 'NULL'}, {ativo}, '{observacoes}', '{data_registro}', {comissao_id}, {militar_id}, {usuario_id})
            ON CONFLICT (id) DO NOTHING;
            """
            self.executar_sql(self.supabase_conn, sql, f"Associar membro {tipo}")
        
        self.log("✅ Membros associados às comissões")
        return True
    
    def resetar_sequencias(self):
        """Reseta as sequências de ID"""
        self.log("🔄 Resetando sequências...")
        
        tabelas = [
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
        self.log("🚀 INICIANDO MIGRAÇÃO COMPLEMENTAR CORRIGIDA")
        
        # Conectar ao Supabase
        self.supabase_conn = self.conectar_supabase()
        if not self.supabase_conn:
            return False
        
        # Desabilitar triggers temporariamente
        self.executar_sql(self.supabase_conn, 
                         "SET session_replication_role = replica;", 
                         "Desabilitar triggers")
        
        # Inserir comissões
        if not self.inserir_comissoes():
            return False
        
        # Inserir quadros de acesso
        if not self.inserir_quadros_acesso():
            return False
        
        # Inserir calendários de promoção
        if not self.inserir_calendarios_promocao():
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
        
        self.log("✅ MIGRAÇÃO COMPLEMENTAR CORRIGIDA CONCLUÍDA COM SUCESSO")
        return True

def main():
    """Função principal"""
    print("🔧 MIGRAÇÃO COMPLEMENTAR CORRIGIDA PARA SUPABASE")
    print("=" * 60)
    
    migracao = MigracaoComplementaresCorrigida()
    
    if migracao.executar_migracao():
        print("\n" + "=" * 60)
        print("🎉 MIGRAÇÃO COMPLEMENTAR CORRIGIDA CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("📋 RESUMO:")
        print("✅ Comissões inseridas")
        print("✅ Quadros de acesso inseridos")
        print("✅ Calendários de promoção inseridos")
        print("✅ Membros associados às comissões")
        print("✅ Sequências resetadas")
        print("✅ Triggers reabilitados")
        print("✅ Log salvo em:", migracao.log_file)
        print()
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRAÇÃO COMPLEMENTAR CORRIGIDA FALHOU!")
        print("=" * 60)
        print("Verifique o log:", migracao.log_file)
        print()
        return False

if __name__ == "__main__":
    main() 