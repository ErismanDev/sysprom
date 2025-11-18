#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar backup completo do PostgreSQL para restaurar no Digital Ocean
IP: 64.23.185.235
"""
import os
import sys
import subprocess
from datetime import datetime

# Configurações do banco LOCAL
DB_NAME = "sepromcbmepi"
DB_USER = "postgres"
DB_PASSWORD = "11322361"
DB_HOST = "localhost"
DB_PORT = "5432"

# Configurações do servidor Digital Ocean
DO_HOST = "64.23.185.235"
DO_USER = "root"
DO_DB_USER = "seprom"
DO_DB_NAME = "sepromcbmepi"

# Nome do arquivo de backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backup_sepromcbmepi_completo_{timestamp}.sql"
backup_file_compressed = f"{backup_file}.gz"

print("=" * 70)
print("💾 BACKUP COMPLETO DO BANCO DE DADOS")
print("=" * 70)
print(f"📊 Banco: {DB_NAME}")
print(f"🖥️  Host: {DB_HOST}:{DB_PORT}")
print(f"👤 Usuário: {DB_USER}")
print(f"🌐 Servidor destino: {DO_HOST}")
print("=" * 70)

# Tentar encontrar pg_dump
pg_dump_path = None
possible_paths = [
    'pg_dump',  # No PATH
    r'C:\Program Files\PostgreSQL\18\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\17\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\15\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\14\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\13\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\12\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\18\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\17\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\13\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\12\bin\pg_dump.exe',
]

print("\n🔍 Procurando pg_dump...")
for path in possible_paths:
    try:
        result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            pg_dump_path = path
            print(f"✅ pg_dump encontrado: {result.stdout.strip()}")
            break
    except (FileNotFoundError, subprocess.TimeoutExpired):
        continue

if not pg_dump_path:
    print("❌ ERRO: pg_dump não encontrado!")
    print("\nLocais verificados:")
    for path in possible_paths:
        print(f"  - {path}")
    print("\n💡 Soluções:")
    print("  1. Instale o PostgreSQL Client Tools")
    print("  2. Adicione o PostgreSQL ao PATH do Windows")
    print("  3. Ou ajuste o caminho no script")
    sys.exit(1)

# Criar backup
print(f"\n📦 Criando backup completo...")
print(f"   Arquivo: {backup_file}")

try:
    # Comando pg_dump com todas as opções necessárias
    # -F p = formato texto (SQL) - melhor para restauração
    # -b = incluir blobs (imagens, arquivos)
    # -v = verbose (mostrar progresso)
    # -f = arquivo de saída
    # --no-owner = não incluir comandos de ownership (evita problemas de permissão)
    # --no-privileges = não incluir comandos de privilégios
    # --clean = incluir comandos DROP (para limpar antes de restaurar)
    # --if-exists = usar IF EXISTS nos DROP (mais seguro)
    cmd = [
        pg_dump_path,
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-F', 'p',  # Formato texto SQL
        '-b',  # Incluir blobs
        '-v',  # Verbose
        '--no-owner',  # Não incluir ownership
        '--no-privileges',  # Não incluir privilégios
        '--clean',  # Incluir DROP
        '--if-exists',  # Usar IF EXISTS
        '-f', backup_file
    ]
    
    print(f"\n⚙️  Executando pg_dump...")
    print(f"   Comando: {' '.join(cmd[:8])} ... -f {backup_file}")
    
    # Usar variável de ambiente para senha (evita prompt interativo)
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    
    result = subprocess.run(cmd, text=True, env=env, capture_output=True)
    
    if result.returncode == 0:
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(backup_file)
        size_mb = file_size / (1024 * 1024)
        
        print(f"\n✅ Backup criado com sucesso!")
        print(f"📊 Tamanho: {size_mb:.2f} MB")
        print(f"📁 Local: {os.path.abspath(backup_file)}")
        
        # Verificar se o arquivo tem conteúdo válido
        print(f"\n🔍 Validando arquivo...")
        with open(backup_file, 'r', encoding='utf-8', errors='ignore') as f:
            first_lines = f.readlines()[:10]
            content = ' '.join(first_lines)
            if any(keyword in content for keyword in ['PostgreSQL database dump', 'CREATE DATABASE', 'CREATE TABLE', 'COPY', 'INSERT']):
                print(f"✅ Arquivo válido (formato SQL PostgreSQL)")
            else:
                print(f"⚠️  Aviso: Verifique o conteúdo do arquivo")
        
        # Tentar comprimir o arquivo (opcional)
        print(f"\n🗜️  Comprimindo backup...")
        try:
            import gzip
            import shutil
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(backup_file_compressed, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = os.path.getsize(backup_file_compressed)
            compressed_size_mb = compressed_size / (1024 * 1024)
            compression_ratio = (1 - compressed_size / file_size) * 100
            
            print(f"✅ Backup comprimido!")
            print(f"📊 Tamanho comprimido: {compressed_size_mb:.2f} MB")
            print(f"📉 Compressão: {compression_ratio:.1f}%")
            print(f"📁 Arquivo: {backup_file_compressed}")
            
        except ImportError:
            print("⚠️  gzip não disponível (opcional)")
        except Exception as e:
            print(f"⚠️  Erro ao comprimir: {e}")
        
    else:
        print(f"\n❌ Erro ao criar backup!")
        print(f"   Código de retorno: {result.returncode}")
        if result.stderr:
            print(f"\n   Erro:")
            print(f"   {result.stderr}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Erro ao criar backup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Criar script de restauração
restore_script = f"restaurar_backup_do_{timestamp}.sh"
print(f"\n📝 Criando script de restauração...")

restore_script_content = f"""#!/bin/bash
# Script para restaurar backup no servidor Digital Ocean
# IP: {DO_HOST}
# Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

set -e  # Parar em caso de erro

BACKUP_FILE="{backup_file}"
DB_NAME="{DO_DB_NAME}"
DB_USER="{DO_DB_USER}"

echo "=========================================="
echo "🔄 RESTAURANDO BACKUP NO DIGITAL OCEAN"
echo "=========================================="
echo "📁 Arquivo: $BACKUP_FILE"
echo "📊 Banco: $DB_NAME"
echo "=========================================="

# Verificar se o arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ ERRO: Arquivo de backup não encontrado: $BACKUP_FILE"
    echo "💡 Certifique-se de que o arquivo foi enviado para o servidor"
    exit 1
fi

# Parar aplicação
echo ""
echo "⏸️  Parando aplicação..."
systemctl stop seprom || echo "⚠️  Serviço seprom não encontrado ou já parado"

# Fazer backup de segurança do banco atual
echo ""
echo "💾 Fazendo backup de segurança do banco atual..."
BACKUP_SEGURANCA="/tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"
su - postgres -c "pg_dump $DB_NAME > $BACKUP_SEGURANCA" || echo "⚠️  Não foi possível fazer backup de segurança"
if [ -f "$BACKUP_SEGURANCA" ]; then
    echo "✅ Backup de segurança criado: $BACKUP_SEGURANCA"
fi

# Limpar banco atual
echo ""
echo "🧹 Limpando banco atual..."
su - postgres << EOF
psql << SQL
-- Terminar conexões ativas
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();

-- Dropar e recriar banco
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\\q
SQL
EOF

# Restaurar backup
echo ""
echo "📥 Restaurando backup..."
echo "   Isso pode levar alguns minutos dependendo do tamanho do banco..."

# Verificar se o arquivo está comprimido
if [ -f "$BACKUP_FILE.gz" ]; then
    echo "   Descomprimindo arquivo..."
    gunzip -c "$BACKUP_FILE.gz" | su - postgres -c "psql $DB_NAME"
elif [ -f "$BACKUP_FILE" ]; then
    su - postgres -c "psql $DB_NAME < $BACKUP_FILE"
else
    echo "❌ ERRO: Arquivo de backup não encontrado!"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo "✅ Backup restaurado com sucesso!"
else
    echo "❌ ERRO ao restaurar backup!"
    exit 1
fi

# Verificar restauração
echo ""
echo "🔍 Verificando restauração..."
TABLES_COUNT=$(su - postgres -c "psql $DB_NAME -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';\"")
echo "   Tabelas encontradas: $TABLES_COUNT"

# Corrigir permissões
echo ""
echo "🔧 Corrigindo permissões do banco de dados..."
su - postgres << PERMISSIONS_EOF
psql $DB_NAME << PERMISSIONS_SQL
-- Alterar owner do banco
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;

-- Alterar owner de todas as tabelas
DO \\\$\\\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' OWNER TO ' || quote_ident('$DB_USER');
    END LOOP;
END
\\\$\\\$;

-- Alterar owner de todas as sequences
DO \\\$\\\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
        EXECUTE 'ALTER SEQUENCE public.' || quote_ident(r.sequence_name) || ' OWNER TO ' || quote_ident('$DB_USER');
    END LOOP;
END
\\\$\\\$;

-- Conceder permissões
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;

-- Permissões padrão para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $DB_USER;
\\q
PERMISSIONS_SQL
PERMISSIONS_EOF

echo "✅ Permissões corrigidas!"

# Reiniciar aplicação
echo ""
echo "▶️  Reiniciando aplicação..."
systemctl start seprom || echo "⚠️  Serviço seprom não encontrado"

echo ""
echo "=========================================="
echo "✅ RESTAURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo "💡 Próximos passos:"
echo "   1. Verificar logs: journalctl -u seprom -f"
echo "   2. Testar aplicação: curl http://localhost/"
echo "   3. Verificar banco: su - postgres -c 'psql $DB_NAME -c \"\\dt\"'"
echo "=========================================="
"""

try:
    # Criar arquivo com quebras de linha Unix (LF) para compatibilidade Linux
    with open(restore_script, 'w', encoding='utf-8', newline='\n') as f:
        f.write(restore_script_content)
    
    # Tornar executável (no Windows não faz diferença, mas útil se copiar para Linux)
    print(f"✅ Script de restauração criado: {restore_script}")
    print(f"   💡 Nota: Se o script não executar no servidor, use os comandos em RESTAURAR_BACKUP_DO_COMANDOS.md")
    
except Exception as e:
    print(f"⚠️  Erro ao criar script de restauração: {e}")

# Instruções finais
print("\n" + "=" * 70)
print("✅ BACKUP CONCLUÍDO COM SUCESSO!")
print("=" * 70)
print("\n📋 PRÓXIMOS PASSOS:")
print("\n1️⃣  ENVIAR ARQUIVO PARA O SERVIDOR:")
print(f"   Opção A - WinSCP:")
print(f"      - Conecte ao servidor: {DO_HOST}")
print(f"      - Usuário: {DO_USER}")
print(f"      - Envie o arquivo: {backup_file}")
if os.path.exists(backup_file_compressed):
    print(f"      - Ou o arquivo comprimido: {backup_file_compressed}")
print(f"      - Para: /home/seprom/sepromcbmepi/")
print(f"\n   Opção B - PowerShell (SCP):")
if os.path.exists(backup_file_compressed):
    print(f"      scp {backup_file_compressed} {DO_USER}@{DO_HOST}:/home/seprom/sepromcbmepi/")
else:
    print(f"      scp {backup_file} {DO_USER}@{DO_HOST}:/home/seprom/sepromcbmepi/")

print(f"\n2️⃣  RESTAURAR NO SERVIDOR:")
print(f"   Opção A - Usar script automático:")
print(f"      - Envie também o arquivo: {restore_script}")
print(f"      - No servidor, execute:")
print(f"        chmod +x {restore_script}")
print(f"        ./{restore_script}")
print(f"\n   Opção B - Comandos manuais:")
print(f"      ssh {DO_USER}@{DO_HOST}")
print(f"      cd /home/seprom/sepromcbmepi")
print(f"      systemctl stop seprom")
print(f"      su - postgres -c \"psql -c 'DROP DATABASE IF EXISTS {DO_DB_NAME};'\"")
print(f"      su - postgres -c \"psql -c 'CREATE DATABASE {DO_DB_NAME} OWNER {DO_DB_USER};'\"")
if os.path.exists(backup_file_compressed):
    print(f"      gunzip -c {backup_file_compressed} | su - postgres -c \"psql {DO_DB_NAME}\"")
else:
    print(f"      su - postgres -c \"psql {DO_DB_NAME} < {backup_file}\"")
print(f"      systemctl start seprom")

print("\n" + "=" * 70)
print("💡 DICA: Sempre faça backup antes de restaurar!")
print("=" * 70)

