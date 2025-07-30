#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAR ESTRUTURA SUPABASE
============================

Script para verificar quais tabelas e colunas existem no Supabase.

Autor: Sistema de Promoções CBMEPI
Data: 30/07/2025
"""

import psycopg2
from datetime import datetime

# Configurações do Supabase
SUPABASE_CONFIG = {
    'host': 'aws-0-sa-east-1.pooler.supabase.com',
    'database': 'postgres',
    'user': 'postgres.vubnekyyfjcrswaufnla',
    'password': '2YXGdmXESoZAoPkO',
    'port': '6543'
}

def verificar_estrutura():
    """Verifica a estrutura das tabelas no Supabase"""
    print("🔍 VERIFICANDO ESTRUTURA DO SUPABASE")
    print("=" * 60)
    
    try:
        # Conectar ao Supabase
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao Supabase")
        
        # Listar todas as tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'militares_%'
            ORDER BY table_name
        """)
        
        tabelas = cursor.fetchall()
        
        print(f"\n📋 TABELAS ENCONTRADAS ({len(tabelas)}):")
        print("-" * 40)
        
        for tabela in tabelas:
            nome_tabela = tabela[0]
            print(f"✅ {nome_tabela}")
            
            # Verificar colunas da tabela
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{nome_tabela}'
                ORDER BY ordinal_position
            """)
            
            colunas = cursor.fetchall()
            print(f"   Colunas ({len(colunas)}):")
            
            for coluna in colunas:
                nome_coluna, tipo, nullable, default = coluna
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"     - {nome_coluna}: {tipo} {nullable_str}{default_str}")
            
            print()
        
        # Verificar tabelas que deveriam existir
        tabelas_esperadas = [
            'militares_cargo',
            'militares_funcao',
            'militares_comissaopromocao',
            'militares_membrocomissao',
            'militares_quadroacesso',
            'militares_calendariopromocao'
        ]
        
        tabelas_existentes = [t[0] for t in tabelas]
        
        print("🔍 VERIFICAÇÃO DE TABELAS ESPERADAS:")
        print("-" * 40)
        
        for tabela in tabelas_esperadas:
            if tabela in tabelas_existentes:
                print(f"✅ {tabela} - EXISTE")
            else:
                print(f"❌ {tabela} - NÃO EXISTE")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICAÇÃO CONCLUÍDA")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_estrutura() 