#!/usr/bin/env python
"""
Script simples para migrar do SQLite para PostgreSQL
"""

import os
import sys
import django
import subprocess
from pathlib import Path

def main():
    print("=== MIGRAÇÃO SQLITE → POSTGRESQL ===")
    print()
    
    # 1. Verificar se PostgreSQL está instalado
    print("1. Verificando PostgreSQL...")
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL encontrado")
        else:
            print("❌ PostgreSQL não encontrado")
            print("Instale o PostgreSQL primeiro: https://www.postgresql.org/download/")
            return
    except FileNotFoundError:
        print("❌ PostgreSQL não está no PATH")
        print("Instale o PostgreSQL primeiro: https://www.postgresql.org/download/")
        return
    
    # 2. Instalar psycopg2
    print("\n2. Instalando psycopg2...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'], check=True)
        print("✅ psycopg2 instalado")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar psycopg2")
        return
    
    # 3. Fazer backup
    print("\n3. Fazendo backup do SQLite...")
    sqlite_file = Path("db.sqlite3")
    if sqlite_file.exists():
        import shutil
        shutil.copy2(sqlite_file, "db_backup.sqlite3")
        print("✅ Backup criado: db_backup.sqlite3")
    else:
        print("❌ Arquivo db.sqlite3 não encontrado")
        return
    
    # 4. Exportar dados
    print("\n4. Exportando dados do SQLite...")
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'dumpdata', 
            '--exclude', 'contenttypes', 
            '--exclude', 'auth.Permission',
            '--indent', '2',
            '-o', 'dados_sqlite.json'
        ], check=True)
        print("✅ Dados exportados para dados_sqlite.json")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao exportar dados: {e}")
        return
    
    # 5. Atualizar settings.py
    print("\n5. Atualizando settings.py...")
    settings_file = Path("sepromcbmepi/settings.py")
    
    if not settings_file.exists():
        print("❌ Arquivo settings.py não encontrado")
        return
    
    # Ler arquivo
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Configuração PostgreSQL
    postgres_config = '''DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sepromcbmepi",
        "USER": "postgres",
        "PASSWORD": "sua_senha_aqui",  # ALTERE PARA SUA SENHA
        "HOST": "localhost",
        "PORT": "5432",
    }
}'''
    
    # Substituir configuração
    import re
    pattern = r'DATABASES\s*=\s*\{[^}]*\}'
    new_content = re.sub(pattern, postgres_config, content, flags=re.DOTALL)
    
    # Salvar
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Settings.py atualizado")
    print("⚠️  IMPORTANTE: Altere a senha no arquivo settings.py!")
    
    # 6. Instruções finais
    print("\n" + "="*50)
    print("MIGRAÇÃO PREPARADA!")
    print("="*50)
    print()
    print("PRÓXIMOS PASSOS:")
    print()
    print("1. Crie o banco PostgreSQL:")
    print("   psql -U postgres")
    print("   CREATE DATABASE sepromcbmepi;")
    print("   \\q")
    print()
    print("2. Altere a senha no arquivo sepromcbmepi/settings.py")
    print()
    print("3. Execute as migrações:")
    print("   python manage.py migrate")
    print()
    print("4. Importe os dados:")
    print("   python manage.py loaddata dados_sqlite.json")
    print()
    print("5. Teste o sistema:")
    print("   python manage.py runserver")
    print()
    print("6. Se tudo funcionar, remova os arquivos antigos:")
    print("   rm db.sqlite3 dados_sqlite.json db_backup.sqlite3")

if __name__ == "__main__":
    main() 