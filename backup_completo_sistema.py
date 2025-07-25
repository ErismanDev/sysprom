#!/usr/bin/env python3
"""
Script para criar backup completo do sistema SEPROM CBMEPI
Inclui: banco de dados, arquivos de mídia, configurações e código fonte
"""

import os
import sys
import json
import shutil
import zipfile
import datetime
import subprocess
from pathlib import Path
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def criar_backup_completo():
    """Cria backup completo do sistema"""
    
    # Data e hora atual para nomear o backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_completo_{timestamp}"
    
    print(f"🚀 Iniciando backup completo do sistema...")
    print(f"📁 Diretório de backup: {backup_dir}")
    
    # Criar diretório de backup
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        # 1. Backup do banco de dados
        print("\n📊 Fazendo backup do banco de dados...")
        backup_banco_dados(backup_dir, timestamp)
        
        # 2. Backup dos arquivos de mídia
        print("\n📁 Fazendo backup dos arquivos de mídia...")
        backup_arquivos_midia(backup_dir)
        
        # 3. Backup dos arquivos de configuração
        print("\n⚙️ Fazendo backup das configurações...")
        backup_configuracoes(backup_dir)
        
        # 4. Backup do código fonte
        print("\n💻 Fazendo backup do código fonte...")
        backup_codigo_fonte(backup_dir)
        
        # 5. Backup dos scripts e documentação
        print("\n📝 Fazendo backup de scripts e documentação...")
        backup_scripts_documentacao(backup_dir)
        
        # 6. Criar arquivo de metadados do backup
        print("\n📋 Criando metadados do backup...")
        criar_metadados_backup(backup_dir, timestamp)
        
        # 7. Criar arquivo ZIP do backup completo
        print("\n🗜️ Criando arquivo ZIP do backup...")
        criar_zip_backup(backup_dir, timestamp)
        
        print(f"\n✅ Backup completo criado com sucesso!")
        print(f"📂 Localização: {backup_dir}")
        print(f"📦 Arquivo ZIP: {backup_dir}.zip")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o backup: {str(e)}")
        return False

def backup_banco_dados(backup_dir, timestamp):
    """Faz backup do banco de dados"""
    
    # Backup usando dumpdata do Django
    db_backup_file = f"{backup_dir}/banco_dados_{timestamp}.json"
    
    try:
        # Backup de todos os modelos
        execute_from_command_line([
            'manage.py', 'dumpdata', 
            '--indent=2', 
            '--output', db_backup_file
        ])
        print(f"   ✅ Banco de dados salvo em: {db_backup_file}")
        
        # Backup específico de militares
        militares_backup_file = f"{backup_dir}/militares_{timestamp}.json"
        execute_from_command_line([
            'manage.py', 'dumpdata', 
            'militares', 
            '--indent=2', 
            '--output', militares_backup_file
        ])
        print(f"   ✅ Militares salvos em: {militares_backup_file}")
        
    except Exception as e:
        print(f"   ⚠️ Erro no backup do banco: {str(e)}")
        # Tentar backup alternativo
        backup_banco_alternativo(backup_dir, timestamp)

def backup_banco_alternativo(backup_dir, timestamp):
    """Backup alternativo do banco de dados"""
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
            
    except Exception as e:
        print(f"   ❌ Erro no backup alternativo: {str(e)}")

def backup_arquivos_midia(backup_dir):
    """Faz backup dos arquivos de mídia"""
    
    media_dir = "media"
    if os.path.exists(media_dir):
        media_backup_dir = f"{backup_dir}/media"
        shutil.copytree(media_dir, media_backup_dir)
        print(f"   ✅ Arquivos de mídia copiados para: {media_backup_dir}")
    else:
        print("   ⚠️ Diretório de mídia não encontrado")

def backup_configuracoes(backup_dir):
    """Faz backup das configurações"""
    
    config_files = [
        'sepromcbmepi/settings.py',
        'sepromcbmepi/urls.py',
        'sepromcbmepi/wsgi.py',
        'sepromcbmepi/asgi.py',
        '.pgpass'
    ]
    
    config_backup_dir = f"{backup_dir}/configuracoes"
    os.makedirs(config_backup_dir, exist_ok=True)
    
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, config_backup_dir)
            print(f"   ✅ Configuração copiada: {config_file}")
    
    # Backup de requirements se existir
    if os.path.exists('requirements.txt'):
        shutil.copy2('requirements.txt', config_backup_dir)
        print("   ✅ requirements.txt copiado")

def backup_codigo_fonte(backup_dir):
    """Faz backup do código fonte"""
    
    # Diretórios do código fonte
    source_dirs = [
        'militares',
        'sepromcbmepi',
        'templates',
        'static'
    ]
    
    source_backup_dir = f"{backup_dir}/codigo_fonte"
    os.makedirs(source_backup_dir, exist_ok=True)
    
    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, f"{source_backup_dir}/{source_dir}")
            print(f"   ✅ Código fonte copiado: {source_dir}")

def backup_scripts_documentacao(backup_dir):
    """Faz backup de scripts e documentação"""
    
    # Arquivos de script
    script_files = [f for f in os.listdir('.') if f.endswith('.py') and f != 'backup_completo_sistema.py']
    
    # Diretórios de documentação
    doc_dirs = ['docs', 'scripts']
    
    scripts_backup_dir = f"{backup_dir}/scripts_documentacao"
    os.makedirs(scripts_backup_dir, exist_ok=True)
    
    # Copiar scripts
    for script_file in script_files:
        shutil.copy2(script_file, scripts_backup_dir)
        print(f"   ✅ Script copiado: {script_file}")
    
    # Copiar diretórios de documentação
    for doc_dir in doc_dirs:
        if os.path.exists(doc_dir):
            shutil.copytree(doc_dir, f"{scripts_backup_dir}/{doc_dir}")
            print(f"   ✅ Documentação copiada: {doc_dir}")

def criar_metadados_backup(backup_dir, timestamp):
    """Cria arquivo de metadados do backup"""
    
    metadados = {
        'timestamp': timestamp,
        'data_criacao': datetime.datetime.now().isoformat(),
        'sistema': 'SEPROM CBMEPI',
        'versao_django': django.get_version(),
        'python_version': sys.version,
        'conteudo_backup': {
            'banco_dados': True,
            'arquivos_midia': True,
            'configuracoes': True,
            'codigo_fonte': True,
            'scripts_documentacao': True
        },
        'tamanho_estimado': calcular_tamanho_backup(backup_dir),
        'instrucoes_restauracao': [
            "1. Extrair o arquivo ZIP do backup",
            "2. Restaurar o banco de dados usando: python manage.py loaddata banco_dados_*.json",
            "3. Copiar arquivos de mídia para o diretório media/",
            "4. Verificar configurações em configuracoes/",
            "5. Executar: python manage.py migrate",
            "6. Executar: python manage.py collectstatic"
        ]
    }
    
    metadados_file = f"{backup_dir}/metadados_backup.json"
    with open(metadados_file, 'w', encoding='utf-8') as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Metadados salvos em: {metadados_file}")

def calcular_tamanho_backup(backup_dir):
    """Calcula o tamanho estimado do backup"""
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(backup_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    
    # Converter para MB
    size_mb = total_size / (1024 * 1024)
    return f"{size_mb:.2f} MB"

def criar_zip_backup(backup_dir, timestamp):
    """Cria arquivo ZIP do backup completo"""
    
    zip_filename = f"{backup_dir}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, backup_dir)
                zipf.write(file_path, arcname)
    
    print(f"   ✅ Arquivo ZIP criado: {zip_filename}")
    
    # Remover diretório temporário
    shutil.rmtree(backup_dir)
    print(f"   🗑️ Diretório temporário removido")

def verificar_espaco_disco():
    """Verifica se há espaço suficiente no disco"""
    
    # Verificar espaço disponível (aproximado)
    try:
        statvfs = os.statvfs('.')
        free_space = statvfs.f_frsize * statvfs.f_bavail
        free_space_gb = free_space / (1024**3)
        
        print(f"💾 Espaço livre disponível: {free_space_gb:.2f} GB")
        
        if free_space_gb < 1.0:  # Menos de 1GB
            print("⚠️ Aviso: Pouco espaço em disco disponível!")
            return False
        
        return True
        
    except Exception as e:
        print(f"⚠️ Não foi possível verificar espaço em disco: {str(e)}")
        return True

if __name__ == "__main__":
    print("🔧 Sistema de Backup Completo - SEPROM CBMEPI")
    print("=" * 50)
    
    # Verificar espaço em disco
    if not verificar_espaco_disco():
        print("❌ Espaço insuficiente para backup. Abortando...")
        sys.exit(1)
    
    # Executar backup
    sucesso = criar_backup_completo()
    
    if sucesso:
        print("\n🎉 Backup concluído com sucesso!")
        print("📋 Verifique o arquivo ZIP gerado na pasta backups/")
    else:
        print("\n💥 Falha no backup!")
        sys.exit(1) 