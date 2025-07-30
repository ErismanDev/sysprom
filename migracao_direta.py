#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRACAO DIRETA PARA SUPABASE
=============================

Script direto para migrar dados para o Supabase.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys
import psycopg2
from datetime import datetime

# Configurações básicas
SUPABASE_HOST = "db.xxxxxxxxxxxx.supabase.co"  # Substitua pelo seu host
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = "2YXGdmXESoZAoPkO"  # Digite sua senha aqui
SUPABASE_PORT = "5432"

LOCAL_HOST = "localhost"
LOCAL_DB = "sepromcbmepi"
LOCAL_USER = "postgres"
LOCAL_PASSWORD = "11322361"  # Digite sua senha local aqui
LOCAL_PORT = "5432"

def log(message):
    """Registra mensagem"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    
    # Salvar no arquivo
    with open('migracao_direta.log', 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

def conectar_supabase():
    """Conecta ao Supabase"""
    try:
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            database=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            port=SUPABASE_PORT
        )
        log("Conectado ao Supabase")
        return conn
    except Exception as e:
        log(f"Erro ao conectar ao Supabase: {e}")
        return None

def conectar_local():
    """Conecta ao banco local"""
    try:
        conn = psycopg2.connect(
            host=LOCAL_HOST,
            database=LOCAL_DB,
            user=LOCAL_USER,
            password=LOCAL_PASSWORD,
            port=LOCAL_PORT
        )
        log("Conectado ao banco local")
        return conn
    except Exception as e:
        log(f"Erro ao conectar ao banco local: {e}")
        return None

def migrar_usuarios():
    """Migra usuários"""
    log("Iniciando migracao de usuarios...")
    
    supabase = conectar_supabase()
    local = conectar_local()
    
    if not supabase or not local:
        log("Erro: Nao foi possivel conectar aos bancos")
        return False
    
    try:
        # Desabilitar triggers
        cursor = supabase.cursor()
        cursor.execute("SET session_replication_role = replica;")
        supabase.commit()
        cursor.close()
        
        # Limpar usuários existentes
        cursor = supabase.cursor()
        cursor.execute("DELETE FROM auth_user WHERE id > 1;")
        supabase.commit()
        cursor.close()
        
        # Buscar usuários do banco local
        cursor = local.cursor()
        cursor.execute("SELECT * FROM auth_user ORDER BY id")
        usuarios = cursor.fetchall()
        cursor.close()
        
        log(f"Total de usuarios encontrados: {len(usuarios)}")
        
        # Migrar usuários
        cursor = supabase.cursor()
        for usuario in usuarios:
            try:
                # Construir SQL de inserção
                campos = ['id', 'password', 'last_login', 'is_superuser', 'username', 
                         'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']
                
                valores = []
                for i, campo in enumerate(campos):
                    valor = usuario[i] if i < len(usuario) else None
                    if valor is None:
                        valores.append('NULL')
                    elif isinstance(valor, str):
                        valores.append(f"'{valor.replace(chr(39), chr(39)+chr(39))}'")
                    else:
                        valores.append(str(valor))
                
                sql = f"""
                INSERT INTO auth_user ({', '.join(campos)}) 
                VALUES ({', '.join(valores)});
                """
                
                cursor.execute(sql)
                log(f"Usuario migrado: {usuario[4]}")  # username
                
            except Exception as e:
                log(f"Erro ao migrar usuario {usuario[4]}: {e}")
        
        supabase.commit()
        cursor.close()
        
        # Resetar sequência
        cursor = supabase.cursor()
        cursor.execute("SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));")
        supabase.commit()
        cursor.close()
        
        log("Migracao de usuarios concluida")
        return True
        
    except Exception as e:
        log(f"Erro na migracao de usuarios: {e}")
        return False
    finally:
        if supabase:
            supabase.close()
        if local:
            local.close()

def main():
    """Função principal"""
    print("MIGRACAO DIRETA PARA SUPABASE")
    print("="*40)
    
    # Verificar senhas
    if not SUPABASE_PASSWORD:
        print("ERRO: Configure SUPABASE_PASSWORD no script")
        return
    
    if not LOCAL_PASSWORD:
        print("ERRO: Configure LOCAL_PASSWORD no script")
        return
    
    # Confirmar execução
    print("ATENCAO: Esta operacao ira sobrescrever dados no Supabase!")
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta != 's':
        print("Migracao cancelada")
        return
    
    # Executar migração
    log("Iniciando migracao...")
    
    if migrar_usuarios():
        log("MIGRACAO CONCLUIDA COM SUCESSO!")
    else:
        log("MIGRACAO FALHOU!")

if __name__ == "__main__":
    main() 