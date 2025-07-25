#!/usr/bin/env python
"""
Script de Migração Automatizada: SQLite → PostgreSQL
Este script automatiza todo o processo de migração.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

def executar_comando(comando, descricao):
    """Executa um comando e mostra o resultado"""
    print(f"\n🔄 {descricao}...")
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if resultado.returncode == 0:
            print(f"✅ {descricao} - Sucesso!")
            if resultado.stdout:
                print(resultado.stdout)
        else:
            print(f"❌ {descricao} - Erro!")
            print(f"Erro: {resultado.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def verificar_postgresql():
    """Verifica se o PostgreSQL está instalado"""
    print("🔍 Verificando instalação do PostgreSQL...")
    
    # Verificar se psql está disponível
    resultado = subprocess.run("psql --version", shell=True, capture_output=True, text=True)
    if resultado.returncode != 0:
        print("❌ PostgreSQL não está instalado ou não está no PATH")
        print("📥 Por favor, instale o PostgreSQL primeiro:")
        print("   - Baixe em: https://www.postgresql.org/download/windows/")
        print("   - Execute o instalador")
        print("   - Reinicie o terminal após a instalação")
        return False
    
    print(f"✅ PostgreSQL encontrado: {resultado.stdout.strip()}")
    return True

def instalar_dependencias():
    """Instala as dependências Python necessárias"""
    return executar_comando(
        "pip install psycopg2-binary",
        "Instalando psycopg2-binary"
    )

def fazer_backup():
    """Faz backup do banco SQLite atual"""
    if os.path.exists("db.sqlite3"):
        shutil.copy("db.sqlite3", "db_backup.sqlite3")
        print("✅ Backup do SQLite criado: db_backup.sqlite3")
        return True
    else:
        print("⚠️ Arquivo db.sqlite3 não encontrado")
        return False

def criar_banco_postgresql():
    """Cria o banco de dados PostgreSQL"""
    print("🔍 Criando banco de dados PostgreSQL...")
    
    # Tentar conectar e criar o banco
    comando = "psql -U postgres -c 'CREATE DATABASE sepromcbmepi;'"
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    
    if resultado.returncode == 0:
        print("✅ Banco de dados 'sepromcbmepi' criado com sucesso!")
        return True
    elif "already exists" in resultado.stderr:
        print("✅ Banco de dados 'sepromcbmepi' já existe!")
        return True
    else:
        print(f"❌ Erro ao criar banco: {resultado.stderr}")
        print("💡 Certifique-se de que:")
        print("   - PostgreSQL está rodando")
        print("   - A senha do usuário 'postgres' está correta")
        return False

def atualizar_settings():
    """Atualiza o settings.py para usar PostgreSQL"""
    print("🔧 Atualizando configurações do Django...")
    
    settings_file = "sepromcbmepi/settings.py"
    
    # Ler o arquivo atual
    with open(settings_file, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Substituir a configuração do banco
    config_sqlite = '''DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}'''
    
    config_postgres = '''DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sepromcbmepi",
        "USER": "postgres",
        "PASSWORD": "postgres",  # Altere para sua senha real
        "HOST": "localhost",
        "PORT": "5432",
    }
}'''
    
    if config_sqlite in conteudo:
        novo_conteudo = conteudo.replace(config_sqlite, config_postgres)
        
        # Fazer backup do settings
        shutil.copy(settings_file, f"{settings_file}.backup")
        
        # Salvar o novo settings
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        
        print("✅ Settings.py atualizado para PostgreSQL")
        print("⚠️ IMPORTANTE: Altere a senha 'postgres' para sua senha real!")
        return True
    else:
        print("❌ Configuração do banco não encontrada no settings.py")
        return False

def aplicar_migracoes():
    """Aplica as migrações no PostgreSQL"""
    return executar_comando(
        "python manage.py migrate",
        "Aplicando migrações no PostgreSQL"
    )

def importar_dados():
    """Importa os dados do arquivo JSON"""
    if os.path.exists("dados_sqlite_utf8.json"):
        return executar_comando(
            "python manage.py loaddata dados_sqlite_utf8.json",
            "Importando dados do SQLite"
        )
    else:
        print("❌ Arquivo dados_sqlite_utf8.json não encontrado")
        print("💡 Execute primeiro: python exportar_dados_utf8.py")
        return False

def verificar_migracao():
    """Verifica se a migração foi bem-sucedida"""
    print("🔍 Verificando migração...")
    
    comando = '''python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()
from django.contrib.auth.models import User
from militares.models import Militar
print(f'Usuários: {User.objects.count()}')
print(f'Militares: {Militar.objects.count()}')
"'''
    
    return executar_comando(comando, "Verificando dados migrados")

def main():
    """Função principal do script"""
    print("🚀 Iniciando migração SQLite → PostgreSQL")
    print("=" * 50)
    
    # Lista de etapas
    etapas = [
        ("Verificar PostgreSQL", verificar_postgresql),
        ("Instalar dependências", instalar_dependencias),
        ("Fazer backup", fazer_backup),
        ("Criar banco PostgreSQL", criar_banco_postgresql),
        ("Atualizar settings", atualizar_settings),
        ("Aplicar migrações", aplicar_migracoes),
        ("Importar dados", importar_dados),
        ("Verificar migração", verificar_migracao),
    ]
    
    # Executar cada etapa
    for nome, funcao in etapas:
        print(f"\n{'='*20} {nome} {'='*20}")
        if not funcao():
            print(f"\n❌ Falha na etapa: {nome}")
            print("💡 Verifique os erros acima e tente novamente")
            return False
    
    print("\n🎉 Migração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Teste o sistema: python manage.py runserver")
    print("2. Acesse http://localhost:8000")
    print("3. Verifique se tudo está funcionando")
    print("4. Após confirmar, você pode remover:")
    print("   - db.sqlite3")
    print("   - dados_sqlite_utf8.json")
    print("   - db_backup.sqlite3")
    
    return True

if __name__ == "__main__":
    main() 