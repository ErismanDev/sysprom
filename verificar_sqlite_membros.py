#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime

def verificar_sqlite_membros():
    print("=== VERIFICANDO MEMBROS DE COMISSÕES NO SQLITE ===\n")
    
    # Caminho para o arquivo SQLite de backup
    sqlite_path = 'db_backup.sqlite3'
    
    if not os.path.exists(sqlite_path):
        print(f"❌ Arquivo {sqlite_path} não encontrado!")
        return
    
    try:
        # Conectar ao SQLite
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        print(f"✅ Conectado ao SQLite: {sqlite_path}")
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='militares_membrocomissao'")
        if not cursor.fetchone():
            print("❌ Tabela militares_membrocomissao não encontrada no SQLite!")
            return
        
        # Buscar todos os membros de comissões
        cursor.execute("""
            SELECT 
                mc.id,
                mc.usuario_id,
                mc.militar_id,
                mc.comissao_id,
                mc.ativo,
                mc.data_inicio,
                mc.data_fim,
                u.username,
                m.nome_guerra,
                m.cpf,
                c.nome as comissao_nome,
                c.tipo as comissao_tipo,
                c.status as comissao_status
            FROM militares_membrocomissao mc
            LEFT JOIN auth_user u ON mc.usuario_id = u.id
            LEFT JOIN militares_militar m ON mc.militar_id = m.id
            LEFT JOIN militares_comissaopromocao c ON mc.comissao_id = c.id
            ORDER BY mc.id
        """)
        
        membros = cursor.fetchall()
        
        print(f"Total de membros de comissões no SQLite: {len(membros)}")
        
        if len(membros) == 0:
            print("❌ Nenhum membro de comissão encontrado no SQLite!")
            return
        
        print("\n=== DETALHES DOS MEMBROS NO SQLITE ===")
        
        membros_ativos = 0
        membros_inativos = 0
        
        for membro in membros:
            (id_membro, usuario_id, militar_id, comissao_id, ativo, data_inicio, 
             data_fim, username, nome_guerra, cpf, comissao_nome, comissao_tipo, comissao_status) = membro
            
            status = "✅ ATIVO" if ativo else "❌ INATIVO"
            if ativo:
                membros_ativos += 1
            else:
                membros_inativos += 1
            
            print(f"\n--- Membro ID: {id_membro} ---")
            print(f"   Usuário: {username} (ID: {usuario_id})")
            print(f"   Militar: {nome_guerra} ({cpf}) (ID: {militar_id})")
            print(f"   Comissão: {comissao_nome} ({comissao_tipo}) (ID: {comissao_id})")
            print(f"   Status da comissão: {comissao_status}")
            print(f"   Membro ativo: {status}")
            print(f"   Data início: {data_inicio}")
            print(f"   Data fim: {data_fim}")
        
        print(f"\n=== RESUMO SQLITE ===")
        print(f"Total de membros: {len(membros)}")
        print(f"Membros ativos: {membros_ativos}")
        print(f"Membros inativos: {membros_inativos}")
        
        # Verificar comissões no SQLite
        cursor.execute("SELECT id, nome, tipo, status FROM militares_comissaopromocao")
        comissoes_sqlite = cursor.fetchall()
        
        print(f"\nComissões no SQLite: {len(comissoes_sqlite)}")
        for comissao in comissoes_sqlite:
            (id_comissao, nome, tipo, status) = comissao
            print(f"  • {nome} ({tipo}) - {status} (ID: {id_comissao})")
        
        # Verificar usuários únicos
        usuarios_unicos = set(m[1] for m in membros if m[1] is not None)
        print(f"\nUsuários únicos que são membros: {len(usuarios_unicos)}")
        
        # Verificar militares únicos
        militares_unicos = set(m[2] for m in membros if m[2] is not None)
        print(f"Militares únicos que são membros: {len(militares_unicos)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar SQLite: {e}")
        return

if __name__ == '__main__':
    verificar_sqlite_membros() 