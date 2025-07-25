#!/usr/bin/env python
import sqlite3

def verificar_militares_membros():
    print("=== VERIFICANDO MILITARES MEMBROS DE COMISSÕES NO SQLITE ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Buscar militares que são membros de comissões
        cursor_sqlite.execute("""
            SELECT DISTINCT
                m.id,
                m.nome_guerra,
                m.cpf,
                m.nome_completo,
                m.posto_graduacao,
                m.data_nascimento,
                m.data_incorporacao,
                m.data_promocao_atual,
                m.data_ingresso
            FROM militares_militar m
            INNER JOIN militares_membrocomissao mc ON m.id = mc.militar_id
            ORDER BY m.nome_guerra
        """)
        
        militares = cursor_sqlite.fetchall()
        
        print(f"Total de militares membros de comissões: {len(militares)}")
        
        for militar in militares:
            (id_militar, nome_guerra, cpf, nome_completo, posto_graduacao, 
             data_nascimento, data_incorporacao, data_promocao_atual, data_ingresso) = militar
            
            print(f"\n--- {nome_guerra} ---")
            print(f"  ID: {id_militar}")
            print(f"  CPF: {cpf}")
            print(f"  Nome: {nome_completo}")
            print(f"  Posto: {posto_graduacao}")
            print(f"  Data Nascimento: {data_nascimento}")
            print(f"  Data Incorporação: {data_incorporacao}")
            print(f"  Data Promoção Atual: {data_promocao_atual}")
            print(f"  Data Ingresso: {data_ingresso}")
        
        conn_sqlite.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_militares_membros() 