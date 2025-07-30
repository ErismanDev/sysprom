#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRIADOR DE ARQUIVO .ENV
=======================

Script para criar o arquivo .env com as configurações de migração.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
from datetime import datetime

def criar_arquivo_env():
    """Cria o arquivo .env com as configurações"""
    
    print("CRIANDO ARQUIVO .ENV")
    print("="*30)
    
    # Configurações do Supabase
    print("\nCONFIGURACOES DO SUPABASE:")
    print("-" * 20)
    
    supabase_host = input("Host do Supabase: ").strip()
    if not supabase_host:
        supabase_host = "db.xxxxxxxxxxxx.supabase.co"
    
    supabase_password = input("Senha do Supabase: ").strip()
    if not supabase_password:
        print("ERRO: Senha do Supabase e obrigatoria!")
        return False
    
    # Configurações do banco local
    print("\nCONFIGURACOES DO BANCO LOCAL:")
    print("-" * 20)
    
    local_host = input("Host local (padrao: localhost): ").strip()
    if not local_host:
        local_host = "localhost"
    
    local_db = input("Nome do banco local (padrao: sepromcbmepi): ").strip()
    if not local_db:
        local_db = "sepromcbmepi"
    
    local_user = input("Usuario local (padrao: postgres): ").strip()
    if not local_user:
        local_user = "postgres"
    
    local_password = input("Senha do banco local: ").strip()
    if not local_password:
        print("ERRO: Senha do banco local e obrigatoria!")
        return False
    
    # Criar conteúdo do arquivo .env
    conteudo = f"""# Configurações de Migração Supabase
# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Supabase
SUPABASE_HOST={supabase_host}
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD={supabase_password}
SUPABASE_PORT=5432

# Banco Local
LOCAL_DB_HOST={local_host}
LOCAL_DB_NAME={local_db}
LOCAL_DB_USER={local_user}
LOCAL_DB_PASSWORD={local_password}
LOCAL_DB_PORT=5432
"""
    
    # Salvar arquivo .env
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"\nSUCESSO: Arquivo .env criado!")
        print(f"Localizacao: {os.path.abspath('.env')}")
        
        return True
        
    except Exception as e:
        print(f"ERRO ao criar arquivo .env: {e}")
        return False

def main():
    """Função principal"""
    if criar_arquivo_env():
        print("\nPRÓXIMOS PASSOS:")
        print("1. Execute: python migracao_supabase_sem_emojis.py")
        print("2. Ou execute: python migracao_direta.py")
    else:
        print("\nERRO: Falha na criacao do arquivo .env")

if __name__ == "__main__":
    main() 