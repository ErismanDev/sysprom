#!/usr/bin/env python3
"""
Script para criar backup apenas do banco de dados SEPROM CBMEPI
"""

import os
import sys
import json
import shutil
import datetime
import subprocess
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def criar_backup_banco():
    """Cria backup apenas do banco de dados"""
    
    # Data e hora atual para nomear o backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_banco_{timestamp}"
    
    print(f"🚀 Iniciando backup do banco de dados...")
    print(f"📁 Diretório de backup: {backup_dir}")
    
    # Criar diretório de backup
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        # Backup do banco de dados
        print("\n📊 Fazendo backup do banco de dados...")
        backup_banco_dados(backup_dir, timestamp)
        
        # Criar arquivo de metadados
        print("\n📋 Criando metadados do backup...")
        criar_metadados_backup(backup_dir, timestamp)
        
        print(f"\n✅ Backup do banco de dados criado com sucesso!")
        print(f"📂 Localização: {backup_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o backup: {str(e)}")
        return False

def backup_banco_dados(backup_dir, timestamp):
    """Faz backup do banco de dados"""
    
    try:
        print("   🔄 Fazendo backup do banco de dados...")
        
        # Backup específico de militares
        militares_backup_file = f"{backup_dir}/militares_{timestamp}.json"
        try:
            subprocess.run([
                'python', 'manage.py', 'dumpdata', 
                'militares', 
                '--indent=2', 
                '--output', militares_backup_file
            ], check=True, capture_output=True, text=True)
            print(f"   ✅ Militares salvos em: {militares_backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Erro no backup de militares: {e.stderr}")
        
        # Backup de auth (usuários e grupos)
        auth_backup_file = f"{backup_dir}/auth_{timestamp}.json"
        try:
            subprocess.run([
                'python', 'manage.py', 'dumpdata', 
                'auth', 
                '--indent=2', 
                '--output', auth_backup_file
            ], check=True, capture_output=True, text=True)
            print(f"   ✅ Auth (usuários/grupos) salvos em: {auth_backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Erro no backup de auth: {e.stderr}")
        
        # Backup de contenttypes
        contenttypes_backup_file = f"{backup_dir}/contenttypes_{timestamp}.json"
        try:
            subprocess.run([
                'python', 'manage.py', 'dumpdata', 
                'contenttypes', 
                '--indent=2', 
                '--output', contenttypes_backup_file
            ], check=True, capture_output=True, text=True)
            print(f"   ✅ ContentTypes salvos em: {contenttypes_backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Erro no backup de contenttypes: {e.stderr}")
        
        # Backup de sessions
        sessions_backup_file = f"{backup_dir}/sessions_{timestamp}.json"
        try:
            subprocess.run([
                'python', 'manage.py', 'dumpdata', 
                'sessions', 
                '--indent=2', 
                '--output', sessions_backup_file
            ], check=True, capture_output=True, text=True)
            print(f"   ✅ Sessions salvos em: {sessions_backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Erro no backup de sessions: {e.stderr}")
        
        # Backup alternativo usando SQL
        backup_banco_sql(backup_dir, timestamp)
        
    except Exception as e:
        print(f"   ❌ Erro geral no backup do banco: {str(e)}")
        backup_banco_sql(backup_dir, timestamp)

def backup_banco_sql(backup_dir, timestamp):
    """Backup alternativo usando SQL"""
    try:
        # Verificar se é PostgreSQL
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'postgresql' in db_engine:
            db_name = settings.DATABASES['default']['NAME']
            db_user = settings.DATABASES['default']['USER']
            db_host = settings.DATABASES['default']['HOST']
            db_port = settings.DATABASES['default']['PORT']
            
            pg_dump_file = f"{backup_dir}/postgresql_backup_{timestamp}.sql"
            
            # Comando pg_dump
            cmd = [
                'pg_dump',
                f'--host={db_host}',
                f'--port={db_port}',
                f'--username={db_user}',
                f'--dbname={db_name}',
                '--no-password',
                '--verbose',
                '--clean',
                '--no-owner',
                '--no-privileges',
                f'--file={pg_dump_file}'
            ]
            
            subprocess.run(cmd, check=True)
            print(f"   ✅ Backup PostgreSQL salvo em: {pg_dump_file}")
            
        elif 'sqlite' in db_engine:
            db_path = settings.DATABASES['default']['NAME']
            sqlite_backup_file = f"{backup_dir}/sqlite_backup_{timestamp}.db"
            shutil.copy2(db_path, sqlite_backup_file)
            print(f"   ✅ Backup SQLite salvo em: {sqlite_backup_file}")
            
    except Exception as e:
        print(f"   ❌ Erro no backup SQL: {str(e)}")

def criar_metadados_backup(backup_dir, timestamp):
    """Cria arquivo de metadados do backup"""
    
    metadados = {
        'timestamp': timestamp,
        'data_criacao': datetime.datetime.now().isoformat(),
        'sistema': 'SEPROM CBMEPI',
        'versao_django': django.get_version(),
        'python_version': sys.version,
        'sistema_operacional': os.name,
        'tipo_backup': 'apenas_banco_dados',
        'conteudo_backup': {
            'banco_dados': True,
            'arquivos_midia': False,
            'configuracoes': False,
            'codigo_fonte': False,
            'scripts_documentacao': False
        },
        'tamanho_estimado': calcular_tamanho_backup(backup_dir),
        'instrucoes_restauracao': [
            "1. Navegar até o diretório do backup",
            "2. Restaurar militares: python manage.py loaddata militares_*.json",
            "3. Restaurar auth: python manage.py loaddata auth_*.json",
            "4. Restaurar contenttypes: python manage.py loaddata contenttypes_*.json",
            "5. Restaurar sessions: python manage.py loaddata sessions_*.json",
            "6. Executar: python manage.py migrate"
        ]
    }
    
    metadados_file = f"{backup_dir}/metadados_backup.json"
    with open(metadados_file, 'w', encoding='utf-8') as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Metadados salvos em: {metadados_file}")

def calcular_tamanho_backup(backup_dir):
    """Calcula o tamanho estimado do backup"""
    
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(backup_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        # Converter para MB
        size_mb = total_size / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    except Exception as e:
        return f"Erro ao calcular: {str(e)}"

if __name__ == "__main__":
    print("🔧 Backup do Banco de Dados - SEPROM CBMEPI")
    print("=" * 50)
    
    # Executar backup
    sucesso = criar_backup_banco()
    
    if sucesso:
        print("\n🎉 Backup do banco de dados concluído com sucesso!")
        print("📋 Verifique os arquivos JSON gerados na pasta backups/")
    else:
        print("\n💥 Falha no backup!")
        sys.exit(1) 