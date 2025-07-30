#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURADOR DE CREDENCIAIS
===========================

Script para configurar as credenciais diretamente no código de migração.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys

def configurar_credenciais():
    """Configura as credenciais nos scripts de migração"""
    
    print("CONFIGURADOR DE CREDENCIAIS PARA MIGRACAO")
    print("="*50)
    
    # Solicitar informações do Supabase
    print("\nCONFIGURACOES DO SUPABASE:")
    print("-" * 30)
    
    supabase_host = input("Host do Supabase (ex: db.xxxxxxxxxxxx.supabase.co): ").strip()
    if not supabase_host:
        supabase_host = "db.xxxxxxxxxxxx.supabase.co"
    
    supabase_password = input("Senha do Supabase: ").strip()
    if not supabase_password:
        print("ERRO: Senha do Supabase e obrigatoria!")
        return False
    
    # Solicitar informações do banco local
    print("\nCONFIGURACOES DO BANCO LOCAL:")
    print("-" * 30)
    
    local_password = input("Senha do banco local: ").strip()
    if not local_password:
        print("ERRO: Senha do banco local e obrigatoria!")
        return False
    
    # Atualizar o script de migração direta
    atualizar_script_migracao_direta(supabase_host, supabase_password, local_password)
    
    # Atualizar o script sem emojis
    atualizar_script_sem_emojis(supabase_host, supabase_password, local_password)
    
    print("\nSUCESSO: Credenciais configuradas!")
    print("Agora voce pode executar a migracao.")
    
    return True

def atualizar_script_migracao_direta(host, supabase_password, local_password):
    """Atualiza o script migracao_direta.py"""
    
    try:
        with open('migracao_direta.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Substituir as configurações
        conteudo = conteudo.replace('SUPABASE_HOST = "db.xxxxxxxxxxxx.supabase.co"', f'SUPABASE_HOST = "{host}"')
        conteudo = conteudo.replace('SUPABASE_PASSWORD = ""', f'SUPABASE_PASSWORD = "{supabase_password}"')
        conteudo = conteudo.replace('LOCAL_PASSWORD = ""', f'LOCAL_PASSWORD = "{local_password}"')
        
        with open('migracao_direta.py', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("OK: migracao_direta.py atualizado")
        
    except Exception as e:
        print(f"ERRO ao atualizar migracao_direta.py: {e}")

def atualizar_script_sem_emojis(host, supabase_password, local_password):
    """Atualiza o script migracao_supabase_sem_emojis.py"""
    
    try:
        with open('migracao_supabase_sem_emojis.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Substituir as configurações
        conteudo = conteudo.replace('SUPABASE_HOST = "db.xxxxxxxxxxxx.supabase.co"', f'SUPABASE_HOST = "{host}"')
        conteudo = conteudo.replace('SUPABASE_PASSWORD = ""', f'SUPABASE_PASSWORD = "{supabase_password}"')
        conteudo = conteudo.replace('LOCAL_PASSWORD = ""', f'LOCAL_PASSWORD = "{local_password}"')
        
        with open('migracao_supabase_sem_emojis.py', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("OK: migracao_supabase_sem_emojis.py atualizado")
        
    except Exception as e:
        print(f"ERRO ao atualizar migracao_supabase_sem_emojis.py: {e}")

def main():
    """Função principal"""
    if configurar_credenciais():
        print("\nPRÓXIMOS PASSOS:")
        print("1. Execute: python migracao_direta.py")
        print("2. Ou execute: python migracao_supabase_sem_emojis.py")
    else:
        print("\nERRO: Falha na configuração")

if __name__ == "__main__":
    main() 