#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTOR DE MIGRAÇÃO COMPLETA SUPABASE
======================================

Script que orquestra todo o processo de migração:
1. Configuração
2. Backup
3. Migração em 3 etapas
4. Verificação

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys
import subprocess
import time
from datetime import datetime

class ExecutorMigracaoCompleta:
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"execucao_completa_{self.timestamp}.log"
        
    def log(self, message):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def executar_script(self, script, descricao):
        """Executa um script Python"""
        self.log(f"🚀 Executando: {descricao}")
        
        try:
            result = subprocess.run([sys.executable, script], 
                                  capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                self.log(f"✅ {descricao} - Concluído com sucesso")
                return True
            else:
                self.log(f"❌ {descricao} - Falhou")
                self.log(f"Erro: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {descricao} - Timeout (mais de 1 hora)")
            return False
        except Exception as e:
            self.log(f"❌ {descricao} - Erro: {e}")
            return False
    
    def verificar_dependencias(self):
        """Verifica se as dependências estão instaladas"""
        self.log("🔍 Verificando dependências...")
        
        dependencias = ['psycopg2-binary']
        faltando = []
        
        for dep in dependencias:
            try:
                __import__(dep.replace('-', '_'))
                self.log(f"   ✅ {dep}")
            except ImportError:
                self.log(f"   ❌ {dep} - NÃO INSTALADO")
                faltando.append(dep)
        
        if faltando:
            self.log(f"📦 Instalando dependências faltantes...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + faltando, 
                             check=True, capture_output=True)
                self.log("✅ Dependências instaladas")
                return True
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Erro ao instalar dependências: {e}")
                return False
        
        return True
    
    def verificar_arquivos(self):
        """Verifica se os arquivos necessários existem"""
        self.log("🔍 Verificando arquivos necessários...")
        
        arquivos_necessarios = [
            'configurar_migracao.py',
            'migracao_supabase_3_etapas.py',
            'backup_pre_migracao.py',
            'verificar_migracao.py'
        ]
        
        todos_ok = True
        for arquivo in arquivos_necessarios:
            if os.path.exists(arquivo):
                self.log(f"   ✅ {arquivo}")
            else:
                self.log(f"   ❌ {arquivo} - NÃO ENCONTRADO")
                todos_ok = False
        
        return todos_ok
    
    def etapa_configuracao(self):
        """Etapa 1: Configuração"""
        self.log("="*60)
        self.log("📋 ETAPA 1: CONFIGURAÇÃO")
        self.log("="*60)
        
        if os.path.exists('.env'):
            self.log("📁 Arquivo .env já existe")
            resposta = input("Deseja reconfigurar? (s/N): ").strip().lower()
            if resposta != 's':
                self.log("✅ Mantendo configuração atual")
                return True
        
        return self.executar_script('configurar_migracao.py', 'Configuração')
    
    def etapa_backup(self):
        """Etapa 2: Backup"""
        self.log("="*60)
        self.log("📦 ETAPA 2: BACKUP")
        self.log("="*60)
        
        return self.executar_script('backup_pre_migracao.py', 'Backup pré-migração')
    
    def etapa_migracao(self):
        """Etapa 3: Migração"""
        self.log("="*60)
        self.log("🚀 ETAPA 3: MIGRAÇÃO")
        self.log("="*60)
        
        return self.executar_script('migracao_supabase_3_etapas.py', 'Migração em 3 etapas')
    
    def etapa_verificacao(self):
        """Etapa 4: Verificação"""
        self.log("="*60)
        self.log("🔍 ETAPA 4: VERIFICAÇÃO")
        self.log("="*60)
        
        return self.executar_script('verificar_migracao.py', 'Verificação pós-migração')
    
    def pausa_entre_etapas(self, etapa_atual, etapa_proxima):
        """Pausa entre etapas"""
        self.log(f"⏸️ Pausa entre {etapa_atual} e {etapa_proxima}")
        self.log("⏱️ Aguardando 10 segundos...")
        time.sleep(10)
    
    def executar_migracao_completa(self):
        """Executa todo o processo de migração"""
        self.log("🚀 INICIANDO MIGRAÇÃO COMPLETA PARA SUPABASE")
        self.log("="*60)
        
        # Verificações iniciais
        if not self.verificar_dependencias():
            self.log("❌ Falha na verificação de dependências")
            return False
        
        if not self.verificar_arquivos():
            self.log("❌ Falha na verificação de arquivos")
            return False
        
        # Executar etapas
        etapas = [
            ("Configuração", self.etapa_configuracao),
            ("Backup", self.etapa_backup),
            ("Migração", self.etapa_migracao),
            ("Verificação", self.etapa_verificacao)
        ]
        
        resultados = []
        
        for i, (nome_etapa, funcao_etapa) in enumerate(etapas):
            self.log(f"\n🎯 EXECUTANDO ETAPA {i+1}/4: {nome_etapa}")
            
            resultado = funcao_etapa()
            resultados.append(resultado)
            
            if not resultado:
                self.log(f"❌ Falha na etapa: {nome_etapa}")
                self.log("🛑 Processo interrompido")
                break
            
            if i < len(etapas) - 1:
                proxima_etapa = etapas[i+1][0]
                self.pausa_entre_etapas(nome_etapa, proxima_etapa)
        
        # Relatório final
        self.gerar_relatorio_final(resultados)
        
        return all(resultados)
    
    def gerar_relatorio_final(self, resultados):
        """Gera relatório final"""
        self.log("="*60)
        self.log("📋 RELATÓRIO FINAL")
        self.log("="*60)
        
        etapas_nomes = ["Configuração", "Backup", "Migração", "Verificação"]
        
        for i, (nome, resultado) in enumerate(zip(etapas_nomes, resultados)):
            status = "✅ OK" if resultado else "❌ FALHOU"
            self.log(f"Etapa {i+1}: {nome} - {status}")
        
        total_ok = sum(resultados)
        total_etapas = len(resultados)
        
        self.log(f"\n📊 RESUMO:")
        self.log(f"Etapas concluídas: {total_ok}/{total_etapas}")
        
        if total_ok == total_etapas:
            self.log("🎉 MIGRAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!")
            self.log("✅ Sistema pronto para uso em produção")
        else:
            self.log("⚠️ MIGRAÇÃO PARCIALMENTE CONCLUÍDA")
            self.log("🔍 Verifique os erros e execute novamente se necessário")
        
        self.log(f"\n📁 Log completo salvo em: {self.log_file}")

def main():
    """Função principal"""
    print("🚀 EXECUTOR DE MIGRAÇÃO COMPLETA SUPABASE")
    print("="*60)
    
    # Aviso importante
    print("⚠️ ATENÇÃO: Este processo irá:")
    print("   - Configurar conexões com os bancos")
    print("   - Fazer backup dos dados")
    print("   - Migrar todos os dados para o Supabase")
    print("   - Verificar a migração")
    print()
    print("⏱️ Tempo estimado: 30-60 minutos")
    print()
    
    # Confirmar execução
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta != 's':
        print("❌ Migração cancelada pelo usuário")
        return
    
    # Executar migração completa
    executor = ExecutorMigracaoCompleta()
    sucesso = executor.executar_migracao_completa()
    
    if sucesso:
        print("\n🎉 MIGRAÇÃO COMPLETA CONCLUÍDA!")
        print("📋 Verifique o arquivo de log para detalhes")
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("📋 Verifique o arquivo de log para detalhes")

if __name__ == "__main__":
    main() 