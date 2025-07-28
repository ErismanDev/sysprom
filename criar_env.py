#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar o arquivo .env automaticamente
"""

import os

def criar_arquivo_env():
    """Cria o arquivo .env com as configurações do Supabase"""
    
    conteudo_env = """# Supabase
SUPABASE_HOST=aws-0-sa-east-1.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres.vubnekyyfjcrswaufnla
SUPABASE_PASSWORD=2YXGdmXESoZAoPkO

# Django
SECRET_KEY=django-insecure-sua-chave-secreta-aqui-mude-esta-chave-em-producao
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
"""
    
    # Caminho do arquivo .env
    env_path = '.env'
    
    # Verificar se o arquivo já existe
    if os.path.exists(env_path):
        print(f"⚠️  Arquivo {env_path} já existe!")
        resposta = input("Deseja sobrescrever? (s/n): ").lower()
        if resposta != 's':
            print("Operação cancelada.")
            return
    
    try:
        # Criar o arquivo .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(conteudo_env)
        
        print(f"✅ Arquivo {env_path} criado com sucesso!")
        print("📋 Conteúdo do arquivo:")
        print("-" * 50)
        print(conteudo_env)
        print("-" * 50)
        print("🔒 IMPORTANTE:")
        print("   • O arquivo .env contém informações sensíveis")
        print("   • Certifique-se de que está no .gitignore")
        print("   • Mude a SECRET_KEY em produção")
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo {env_path}: {e}")

if __name__ == "__main__":
    print("🔧 Criando arquivo .env...")
    criar_arquivo_env() 