#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURADOR DE MIGRAÇÃO SUPABASE
=================================

Script para configurar as variáveis de ambiente necessárias
para a migração do banco local para o Supabase.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys
from datetime import datetime

def criar_arquivo_env():
    """Cria arquivo .env com as configurações"""
    
    print("🔧 CONFIGURADOR DE MIGRAÇÃO SUPABASE")
    print("=" * 50)
    
    # Solicitar informações do Supabase
    print("\n📋 CONFIGURAÇÕES DO SUPABASE:")
    print("-" * 30)
    
    supabase_host = input("Host do Supabase (ex: db.xxxxxxxxxxxx.supabase.co): ").strip()
    if not supabase_host:
        supabase_host = "db.xxxxxxxxxxxx.supabase.co"
    
    supabase_password = input("Senha do Supabase: ").strip()
    if not supabase_password:
        print("❌ Senha do Supabase é obrigatória!")
        return False
    
    supabase_db = input("Nome do banco (padrão: postgres): ").strip()
    if not supabase_db:
        supabase_db = "postgres"
    
    supabase_user = input("Usuário (padrão: postgres): ").strip()
    if not supabase_user:
        supabase_user = "postgres"
    
    supabase_port = input("Porta (padrão: 5432): ").strip()
    if not supabase_port:
        supabase_port = "5432"
    
    # Solicitar informações do banco local
    print("\n📋 CONFIGURAÇÕES DO BANCO LOCAL:")
    print("-" * 30)
    
    local_host = input("Host local (padrão: localhost): ").strip()
    if not local_host:
        local_host = "localhost"
    
    local_db = input("Nome do banco local (padrão: sepromcbmepi): ").strip()
    if not local_db:
        local_db = "sepromcbmepi"
    
    local_user = input("Usuário local (padrão: postgres): ").strip()
    if not local_user:
        local_user = "postgres"
    
    local_password = input("Senha do banco local: ").strip()
    if not local_password:
        print("❌ Senha do banco local é obrigatória!")
        return False
    
    local_port = input("Porta local (padrão: 5432): ").strip()
    if not local_port:
        local_port = "5432"
    
    # Criar conteúdo do arquivo .env
    conteudo = f"""# Configurações de Migração Supabase
# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Supabase
SUPABASE_HOST={supabase_host}
SUPABASE_DB={supabase_db}
SUPABASE_USER={supabase_user}
SUPABASE_PASSWORD={supabase_password}
SUPABASE_PORT={supabase_port}

# Banco Local
LOCAL_DB_HOST={local_host}
LOCAL_DB_NAME={local_db}
LOCAL_DB_USER={local_user}
LOCAL_DB_PASSWORD={local_password}
LOCAL_DB_PORT={local_port}
"""
    
    # Salvar arquivo .env
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"\n✅ Arquivo .env criado com sucesso!")
        print(f"📁 Localização: {os.path.abspath('.env')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    dependencias = ['psycopg2-binary']
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NÃO INSTALADO")
            faltando.append(dep)
    
    if faltando:
        print(f"\n📦 Instale as dependências faltantes:")
        print(f"pip install {' '.join(faltando)}")
        return False
    
    return True

def carregar_variaveis_env():
    """Carrega variáveis do arquivo .env"""
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#') and '=' in linha:
                    chave, valor = linha.split('=', 1)
                    os.environ[chave] = valor
        print("✅ Variáveis de ambiente carregadas do arquivo .env")
        return True
    else:
        print("❌ Arquivo .env não encontrado")
        return False

def main():
    """Função principal"""
    print("🚀 CONFIGURADOR DE MIGRAÇÃO SUPABASE")
    print("=" * 50)
    
    # Verificar dependências
    if not verificar_dependencias():
        print("\n❌ Instale as dependências antes de continuar")
        return
    
    # Verificar se arquivo .env existe
    if os.path.exists('.env'):
        print("\n📁 Arquivo .env já existe!")
        resposta = input("Deseja sobrescrever? (s/N): ").strip().lower()
        if resposta != 's':
            print("✅ Mantendo configuração atual")
            carregar_variaveis_env()
            return
    
    # Criar novo arquivo .env
    if criar_arquivo_env():
        print("\n🎉 Configuração concluída!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python migracao_supabase_3_etapas.py")
        print("2. Verifique o arquivo de log gerado")
        print("3. Teste o sistema após a migração")
    else:
        print("\n❌ Falha na configuração")

if __name__ == "__main__":
    main() 