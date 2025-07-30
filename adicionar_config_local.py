#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADICIONAR CONFIGURAÇÕES LOCAIS AO .ENV
======================================

Script para adicionar as configurações do banco local ao arquivo .env existente.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

def adicionar_config_local():
    """Adiciona configurações do banco local ao arquivo .env"""
    
    print("ADICIONANDO CONFIGURACOES LOCAIS AO .ENV")
    print("="*40)
    
    # Ler o arquivo .env atual
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            conteudo_atual = f.read()
    except Exception as e:
        print(f"ERRO ao ler arquivo .env: {e}")
        return False
    
    # Solicitar configurações do banco local
    print("\nCONFIGURACOES DO BANCO LOCAL:")
    print("-" * 30)
    
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
    
    local_port = input("Porta local (padrao: 5432): ").strip()
    if not local_port:
        local_port = "5432"
    
    # Adicionar configurações locais ao conteúdo
    config_local = f"""

# Banco Local
LOCAL_DB_HOST={local_host}
LOCAL_DB_NAME={local_db}
LOCAL_DB_USER={local_user}
LOCAL_DB_PASSWORD={local_password}
LOCAL_DB_PORT={local_port}
"""
    
    # Salvar arquivo atualizado
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(conteudo_atual + config_local)
        
        print("\nSUCESSO: Configuracoes locais adicionadas ao .env!")
        return True
        
    except Exception as e:
        print(f"ERRO ao salvar arquivo .env: {e}")
        return False

def main():
    """Função principal"""
    if adicionar_config_local():
        print("\nPRÓXIMOS PASSOS:")
        print("Execute: python migracao_supabase_sem_emojis.py")
    else:
        print("\nERRO: Falha ao adicionar configuracoes")

if __name__ == "__main__":
    main() 