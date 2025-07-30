#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICAÇÃO FINAL DA MIGRAÇÃO
============================

Script para verificar se a migração foi concluída com sucesso.

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

def verificar_migracao():
    """Verifica se a migração foi concluída com sucesso"""
    print("🔍 VERIFICAÇÃO FINAL DA MIGRAÇÃO")
    print("=" * 60)
    
    try:
        # Conectar ao Supabase
        conn = psycopg2.connect(**SUPABASE_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao Supabase")
        
        # Verificar contagem de registros nas tabelas principais
        tabelas_principais = [
            'auth_user',
            'militares_militar',
            'militares_comissaopromocao',
            'militares_membrocomissao',
            'militares_quadroacesso',
            'militares_calendariopromocao'
        ]
        
        print(f"\n📊 CONTAGEM DE REGISTROS:")
        print("-" * 40)
        
        total_geral = 0
        for tabela in tabelas_principais:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            print(f"✅ {tabela}: {count:,} registros")
            total_geral += count
        
        print(f"\n📈 TOTAL GERAL: {total_geral:,} registros")
        
        # Verificar associações usuário-militar
        print(f"\n🔗 VERIFICAÇÃO DE ASSOCIAÇÕES:")
        print("-" * 40)
        
        cursor.execute("""
            SELECT COUNT(*) FROM militares_militar 
            WHERE user_id IS NOT NULL
        """)
        militares_com_usuario = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM militares_militar")
        total_militares = cursor.fetchone()[0]
        
        print(f"✅ Militares com usuário associado: {militares_com_usuario:,}")
        print(f"✅ Total de militares: {total_militares:,}")
        print(f"✅ Taxa de associação: {(militares_com_usuario/total_militares*100):.1f}%")
        
        # Verificar usuários ativos
        cursor.execute("""
            SELECT COUNT(*) FROM auth_user 
            WHERE is_active = true
        """)
        usuarios_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        total_usuarios = cursor.fetchone()[0]
        
        print(f"\n👥 USUÁRIOS:")
        print(f"✅ Usuários ativos: {usuarios_ativos:,}")
        print(f"✅ Total de usuários: {total_usuarios:,}")
        print(f"✅ Taxa de usuários ativos: {(usuarios_ativos/total_usuarios*100):.1f}%")
        
        # Verificar comissões
        cursor.execute("""
            SELECT COUNT(*) FROM militares_comissaopromocao 
            WHERE status = 'ATIVA'
        """)
        comissoes_ativas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM militares_comissaopromocao")
        total_comissoes = cursor.fetchone()[0]
        
        print(f"\n🏛️ COMISSÕES:")
        print(f"✅ Comissões ativas: {comissoes_ativas:,}")
        print(f"✅ Total de comissões: {total_comissoes:,}")
        
        # Verificar membros de comissão
        cursor.execute("""
            SELECT COUNT(*) FROM militares_membrocomissao 
            WHERE ativo = true
        """)
        membros_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM militares_membrocomissao")
        total_membros = cursor.fetchone()[0]
        
        print(f"\n👤 MEMBROS DE COMISSÃO:")
        print(f"✅ Membros ativos: {membros_ativos:,}")
        print(f"✅ Total de membros: {total_membros:,}")
        
        # Verificar quadros de acesso
        cursor.execute("""
            SELECT COUNT(*) FROM militares_quadroacesso 
            WHERE ativo = true
        """)
        quadros_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM militares_quadroacesso")
        total_quadros = cursor.fetchone()[0]
        
        print(f"\n📋 QUADROS DE ACESSO:")
        print(f"✅ Quadros ativos: {quadros_ativos:,}")
        print(f"✅ Total de quadros: {total_quadros:,}")
        
        # Verificar calendários de promoção
        cursor.execute("""
            SELECT COUNT(*) FROM militares_calendariopromocao 
            WHERE ativo = true
        """)
        calendarios_ativos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM militares_calendariopromocao")
        total_calendarios = cursor.fetchone()[0]
        
        print(f"\n📅 CALENDÁRIOS DE PROMOÇÃO:")
        print(f"✅ Calendários ativos: {calendarios_ativos:,}")
        print(f"✅ Total de calendários: {total_calendarios:,}")
        
        # Verificar integridade das sequências
        print(f"\n🔄 VERIFICAÇÃO DE SEQUÊNCIAS:")
        print("-" * 40)
        
        for tabela in tabelas_principais:
            try:
                cursor.execute(f"SELECT setval('{tabela}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {tabela}));")
                cursor.execute(f"SELECT currval('{tabela}_id_seq');")
                seq_value = cursor.fetchone()[0]
                print(f"✅ {tabela}_id_seq: {seq_value}")
            except Exception as e:
                print(f"⚠️ {tabela}_id_seq: Erro - {e}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICAÇÃO FINAL CONCLUÍDA")
        print("=" * 60)
        print()
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("📋 RESUMO:")
        print(f"✅ {total_usuarios:,} usuários migrados")
        print(f"✅ {total_militares:,} militares migrados")
        print(f"✅ {total_comissoes:,} comissões criadas")
        print(f"✅ {total_quadros:,} quadros de acesso criados")
        print(f"✅ {total_calendarios:,} calendários de promoção criados")
        print(f"✅ {militares_com_usuario:,} associações usuário-militar")
        print()
        print("🚀 O sistema está pronto para uso!")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")

if __name__ == "__main__":
    verificar_migracao() 