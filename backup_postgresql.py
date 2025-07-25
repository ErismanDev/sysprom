#!/usr/bin/env python
"""
Script para fazer backup do banco de dados PostgreSQL do projeto SEPROMCBMEPI
"""
import os
import sys
import subprocess
import datetime
from pathlib import Path

# Configurações do banco de dados (baseadas no settings.py)
DB_NAME = "sepromcbmepi"
DB_USER = "postgres"
DB_PASSWORD = "postgres123"
DB_HOST = "localhost"
DB_PORT = "5432"

def criar_diretorio_backup():
    """Cria o diretório de backup se não existir"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def fazer_backup_completo():
    """Faz backup completo do banco de dados"""
    print("=== INICIANDO BACKUP DO BANCO DE DADOS POSTGRESQL ===\n")
    
    # Criar diretório de backup
    backup_dir = criar_diretorio_backup()
    
    # Gerar nome do arquivo de backup com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"sepromcbmepi_backup_{timestamp}.sql"
    backup_path = backup_dir / backup_filename
    
    print(f"📁 Diretório de backup: {backup_dir.absolute()}")
    print(f"📄 Arquivo de backup: {backup_filename}")
    print(f"🗄️  Banco de dados: {DB_NAME}")
    print(f"👤 Usuário: {DB_USER}")
    print(f"🌐 Host: {DB_HOST}:{DB_PORT}")
    print()
    
    # Comando pg_dump
    cmd = [
        "pg_dump",
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--username={DB_USER}",
        f"--dbname={DB_NAME}",
        "--verbose",
        "--clean",
        "--no-owner",
        "--no-privileges",
        f"--file={backup_path}"
    ]
    
    try:
        print("🔄 Executando backup...")
        
        # Definir variável de ambiente para senha
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        # Executar comando
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Backup concluído com sucesso!")
        print(f"📊 Tamanho do arquivo: {backup_path.stat().st_size / (1024*1024):.2f} MB")
        print(f"📍 Localização: {backup_path.absolute()}")
        
        return str(backup_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar backup:")
        print(f"   Comando: {' '.join(cmd)}")
        print(f"   Erro: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def fazer_backup_apenas_dados():
    """Faz backup apenas dos dados (sem estrutura)"""
    print("=== INICIANDO BACKUP APENAS DOS DADOS ===\n")
    
    backup_dir = criar_diretorio_backup()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"sepromcbmepi_dados_{timestamp}.sql"
    backup_path = backup_dir / backup_filename
    
    cmd = [
        "pg_dump",
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--username={DB_USER}",
        f"--dbname={DB_NAME}",
        "--data-only",
        "--verbose",
        f"--file={backup_path}"
    ]
    
    try:
        print("🔄 Executando backup dos dados...")
        
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Backup dos dados concluído!")
        print(f"📊 Tamanho do arquivo: {backup_path.stat().st_size / (1024*1024):.2f} MB")
        return str(backup_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e.stderr}")
        return None

def listar_backups_existentes():
    """Lista todos os backups existentes"""
    backup_dir = Path("backups")
    if not backup_dir.exists():
        print("📁 Nenhum backup encontrado.")
        return
    
    print("=== BACKUPS EXISTENTES ===")
    backups = list(backup_dir.glob("*.sql"))
    
    if not backups:
        print("📁 Nenhum arquivo de backup encontrado.")
        return
    
    for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True):
        size_mb = backup.stat().st_size / (1024*1024)
        mod_time = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"📄 {backup.name}")
        print(f"   📊 Tamanho: {size_mb:.2f} MB")
        print(f"   📅 Data: {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
        print()

def restaurar_backup(arquivo_backup):
    """Restaura um backup"""
    print(f"=== RESTAURANDO BACKUP: {arquivo_backup} ===\n")
    
    backup_path = Path(arquivo_backup)
    if not backup_path.exists():
        print(f"❌ Arquivo de backup não encontrado: {arquivo_backup}")
        return False
    
    cmd = [
        "psql",
        f"--host={DB_HOST}",
        f"--port={DB_PORT}",
        f"--username={DB_USER}",
        f"--dbname={DB_NAME}",
        f"--file={backup_path}"
    ]
    
    try:
        print("🔄 Restaurando backup...")
        
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Restauração concluída com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na restauração: {e.stderr}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python backup_postgresql.py [comando]")
        print("\nComandos disponíveis:")
        print("  backup          - Faz backup completo do banco")
        print("  dados           - Faz backup apenas dos dados")
        print("  listar          - Lista backups existentes")
        print("  restaurar <arquivo> - Restaura um backup")
        return
    
    comando = sys.argv[1].lower()
    
    if comando == "backup":
        fazer_backup_completo()
    elif comando == "dados":
        fazer_backup_apenas_dados()
    elif comando == "listar":
        listar_backups_existentes()
    elif comando == "restaurar":
        if len(sys.argv) < 3:
            print("❌ Especifique o arquivo de backup para restaurar")
            return
        restaurar_backup(sys.argv[2])
    else:
        print(f"❌ Comando desconhecido: {comando}")

if __name__ == "__main__":
    main() 