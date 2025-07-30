#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKUP PRÉ-MIGRAÇÃO SUPABASE
============================

Script para fazer backup do banco local e Supabase antes da migração.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import psycopg2
import json
from datetime import datetime
import subprocess
import sys

# Carregar variáveis de ambiente
def carregar_env():
    """Carrega variáveis do arquivo .env"""
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#') and '=' in linha:
                    chave, valor = linha.split('=', 1)
                    os.environ[chave] = valor

carregar_env()

SUPABASE_CONFIG = {
    'host': os.getenv('SUPABASE_HOST'),
    'database': os.getenv('SUPABASE_DB'),
    'user': os.getenv('SUPABASE_USER'),
    'password': os.getenv('SUPABASE_PASSWORD'),
    'port': os.getenv('SUPABASE_PORT')
}

LOCAL_CONFIG = {
    'host': os.getenv('LOCAL_DB_HOST'),
    'database': os.getenv('LOCAL_DB_NAME'),
    'user': os.getenv('LOCAL_DB_USER'),
    'password': os.getenv('LOCAL_DB_PASSWORD'),
    'port': os.getenv('LOCAL_DB_PORT')
}

class BackupPreMigracao:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = f"backups_pre_migracao_{self.timestamp}"
        
    def log(self, message):
        """Registra mensagem"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def criar_diretorio_backup(self):
        """Cria diretório para backups"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            self.log(f"✅ Diretório de backup criado: {self.backup_dir}")
            return True
        except Exception as e:
            self.log(f"❌ Erro ao criar diretório: {e}")
            return False
    
    def backup_banco_local(self):
        """Faz backup do banco local"""
        self.log("📦 Iniciando backup do banco local...")
        
        try:
            # Comando pg_dump
            cmd = [
                'pg_dump',
                f'--host={LOCAL_CONFIG["host"]}',
                f'--port={LOCAL_CONFIG["port"]}',
                f'--username={LOCAL_CONFIG["user"]}',
                f'--dbname={LOCAL_CONFIG["database"]}',
                '--format=custom',
                '--verbose',
                f'--file={self.backup_dir}/backup_local_{self.timestamp}.dump'
            ]
            
            # Definir variável de ambiente para senha
            env = os.environ.copy()
            env['PGPASSWORD'] = LOCAL_CONFIG['password']
            
            # Executar comando
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Backup do banco local concluído")
                return True
            else:
                self.log(f"❌ Erro no backup local: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao fazer backup local: {e}")
            return False
    
    def backup_supabase(self):
        """Faz backup do Supabase"""
        self.log("📦 Iniciando backup do Supabase...")
        
        try:
            # Comando pg_dump
            cmd = [
                'pg_dump',
                f'--host={SUPABASE_CONFIG["host"]}',
                f'--port={SUPABASE_CONFIG["port"]}',
                f'--username={SUPABASE_CONFIG["user"]}',
                f'--dbname={SUPABASE_CONFIG["database"]}',
                '--format=custom',
                '--verbose',
                f'--file={self.backup_dir}/backup_supabase_{self.timestamp}.dump'
            ]
            
            # Definir variável de ambiente para senha
            env = os.environ.copy()
            env['PGPASSWORD'] = SUPABASE_CONFIG['password']
            
            # Executar comando
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Backup do Supabase concluído")
                return True
            else:
                self.log(f"❌ Erro no backup Supabase: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Erro ao fazer backup Supabase: {e}")
            return False
    
    def backup_dados_json(self):
        """Faz backup dos dados em formato JSON"""
        self.log("📦 Iniciando backup em JSON...")
        
        try:
            # Conectar ao banco local
            conn = psycopg2.connect(**LOCAL_CONFIG)
            cursor = conn.cursor()
            
            # Lista de tabelas principais
            tabelas = [
                'auth_user',
                'militares_militar',
                'militares_cargo',
                'militares_funcao',
                'militares_comissaopromocao',
                'militares_membrocomissao',
                'militares_quadroacesso'
            ]
            
            dados_backup = {}
            
            for tabela in tabelas:
                self.log(f"   Exportando {tabela}...")
                
                cursor.execute(f"SELECT * FROM {tabela}")
                colunas = [desc[0] for desc in cursor.description]
                registros = cursor.fetchall()
                
                dados_tabela = []
                for registro in registros:
                    linha = {}
                    for i, valor in enumerate(registro):
                        if isinstance(valor, datetime):
                            linha[colunas[i]] = valor.isoformat()
                        else:
                            linha[colunas[i]] = valor
                    dados_tabela.append(linha)
                
                dados_backup[tabela] = {
                    'colunas': colunas,
                    'registros': dados_tabela,
                    'total': len(dados_tabela)
                }
            
            cursor.close()
            conn.close()
            
            # Salvar arquivo JSON
            arquivo_json = f"{self.backup_dir}/dados_backup_{self.timestamp}.json"
            with open(arquivo_json, 'w', encoding='utf-8') as f:
                json.dump(dados_backup, f, ensure_ascii=False, indent=2)
            
            self.log("✅ Backup JSON concluído")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro no backup JSON: {e}")
            return False
    
    def criar_relatorio_backup(self):
        """Cria relatório do backup"""
        self.log("📋 Criando relatório de backup...")
        
        try:
            relatorio = f"""
RELATÓRIO DE BACKUP PRÉ-MIGRAÇÃO
================================

Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Diretório: {self.backup_dir}

ARQUIVOS GERADOS:
- backup_local_{self.timestamp}.dump (Backup completo do banco local)
- backup_supabase_{self.timestamp}.dump (Backup completo do Supabase)
- dados_backup_{self.timestamp}.json (Dados principais em JSON)

CONFIGURAÇÕES:
Banco Local:
- Host: {LOCAL_CONFIG['host']}
- Database: {LOCAL_CONFIG['database']}
- User: {LOCAL_CONFIG['user']}

Supabase:
- Host: {SUPABASE_CONFIG['host']}
- Database: {SUPABASE_CONFIG['database']}
- User: {SUPABASE_CONFIG['user']}

INSTRUÇÕES:
1. Mantenha estes arquivos em local seguro
2. Use os arquivos .dump para restauração completa
3. Use o arquivo .json para verificação de dados
4. Execute a migração apenas após confirmar os backups

PRÓXIMOS PASSOS:
1. Verifique se todos os arquivos foram criados
2. Teste a restauração em ambiente de desenvolvimento
3. Execute a migração: python migracao_supabase_3_etapas.py
4. Verifique a migração: python verificar_migracao.py

---
Gerado automaticamente pelo sistema de backup
"""
            
            arquivo_relatorio = f"{self.backup_dir}/relatorio_backup_{self.timestamp}.txt"
            with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
                f.write(relatorio)
            
            self.log("✅ Relatório de backup criado")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao criar relatório: {e}")
            return False
    
    def verificar_arquivos_backup(self):
        """Verifica se os arquivos de backup foram criados"""
        self.log("🔍 Verificando arquivos de backup...")
        
        arquivos_esperados = [
            f"backup_local_{self.timestamp}.dump",
            f"backup_supabase_{self.timestamp}.dump",
            f"dados_backup_{self.timestamp}.json",
            f"relatorio_backup_{self.timestamp}.txt"
        ]
        
        todos_ok = True
        for arquivo in arquivos_esperados:
            caminho = os.path.join(self.backup_dir, arquivo)
            if os.path.exists(caminho):
                tamanho = os.path.getsize(caminho)
                self.log(f"   ✅ {arquivo} ({tamanho} bytes)")
            else:
                self.log(f"   ❌ {arquivo} - NÃO ENCONTRADO")
                todos_ok = False
        
        return todos_ok
    
    def executar_backup_completo(self):
        """Executa backup completo"""
        self.log("🚀 INICIANDO BACKUP PRÉ-MIGRAÇÃO")
        self.log("="*50)
        
        # Verificar configurações
        if not SUPABASE_CONFIG['password'] or not LOCAL_CONFIG['password']:
            self.log("❌ Configurações não encontradas!")
            self.log("Execute primeiro: python configurar_migracao.py")
            return False
        
        # Criar diretório
        if not self.criar_diretorio_backup():
            return False
        
        # Fazer backups
        sucessos = []
        
        sucessos.append(self.backup_banco_local())
        sucessos.append(self.backup_supabase())
        sucessos.append(self.backup_dados_json())
        sucessos.append(self.criar_relatorio_backup())
        
        # Verificar arquivos
        sucessos.append(self.verificar_arquivos_backup())
        
        # Resultado final
        total_sucessos = sum(sucessos)
        total_operacoes = len(sucessos)
        
        self.log(f"\n📊 RESUMO DO BACKUP:")
        self.log(f"Operações realizadas: {total_sucessos}/{total_operacoes}")
        
        if total_sucessos == total_operacoes:
            self.log("🎉 BACKUP CONCLUÍDO COM SUCESSO!")
            self.log(f"📁 Arquivos salvos em: {self.backup_dir}")
            return True
        else:
            self.log("⚠️ BACKUP PARCIALMENTE CONCLUÍDO")
            self.log("🔍 Verifique os erros acima")
            return False

def main():
    """Função principal"""
    print("BACKUP PRE-MIGRACAO SUPABASE")
    print("="*50)
    
    # Confirmar execução
    print("ATENCAO: Este processo fara backup dos bancos de dados!")
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta != 's':
        print("ERRO: Backup cancelado pelo usuario")
        return
    
    # Executar backup
    backup = BackupPreMigracao()
    sucesso = backup.executar_backup_completo()
    
    if sucesso:
        print("\nSUCESSO: Backup concluido com sucesso!")
        print("INFO: Voce pode agora executar a migracao com seguranca")
    else:
        print("\nERRO: Backup falhou!")
        print("INFO: Verifique os erros antes de prosseguir")

if __name__ == "__main__":
    main() 