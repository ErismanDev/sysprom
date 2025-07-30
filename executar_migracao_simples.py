#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTOR SIMPLIFICADO DE MIGRAÇÃO SUPABASE
==========================================

Script simplificado para executar a migração no PowerShell.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def log(message):
    """Registra mensagem no log"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    
    # Salvar no arquivo de log
    with open('migracao_execucao.log', 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')
    
    # Tentar imprimir (pode não funcionar no PowerShell)
    try:
        print(log_message)
        sys.stdout.flush()
    except:
        pass

def executar_script(script, descricao):
    """Executa um script Python"""
    log(f"🚀 Executando: {descricao}")
    
    try:
        # Executar com subprocess e capturar saída
        result = subprocess.run([sys.executable, script], 
                              capture_output=True, text=True, timeout=3600)
        
        # Salvar saída no log
        if result.stdout:
            log(f"Saída de {descricao}:")
            for linha in result.stdout.split('\n'):
                if linha.strip():
                    log(f"  {linha}")
        
        if result.stderr:
            log(f"Erros de {descricao}:")
            for linha in result.stderr.split('\n'):
                if linha.strip():
                    log(f"  ERRO: {linha}")
        
        if result.returncode == 0:
            log(f"✅ {descricao} - Concluído com sucesso")
            return True
        else:
            log(f"❌ {descricao} - Falhou (código: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        log(f"⏰ {descricao} - Timeout (mais de 1 hora)")
        return False
    except Exception as e:
        log(f"❌ {descricao} - Erro: {e}")
        return False

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    log("🔍 Verificando dependências...")
    
    try:
        import psycopg2
        log("✅ psycopg2-binary instalado")
    except ImportError:
        log("❌ psycopg2-binary não instalado")
        log("📦 Instalando psycopg2-binary...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'], 
                         check=True, capture_output=True)
            log("✅ psycopg2-binary instalado")
        except:
            log("❌ Falha ao instalar psycopg2-binary")
            return False
    
    try:
        import dotenv
        log("✅ python-dotenv instalado")
    except ImportError:
        log("❌ python-dotenv não instalado")
        log("📦 Instalando python-dotenv...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-dotenv'], 
                         check=True, capture_output=True)
            log("✅ python-dotenv instalado")
        except:
            log("❌ Falha ao instalar python-dotenv")
            return False
    
    return True

def verificar_arquivos():
    """Verifica se os arquivos necessários existem"""
    log("🔍 Verificando arquivos necessários...")
    
    arquivos_necessarios = [
        'migracao_supabase_3_etapas.py',
        'configurar_migracao.py',
        'backup_pre_migracao.py',
        'verificar_migracao.py'
    ]
    
    todos_ok = True
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            log(f"✅ {arquivo}")
        else:
            log(f"❌ {arquivo} - NÃO ENCONTRADO")
            todos_ok = False
    
    return todos_ok

def executar_migracao():
    """Executa a migração completa"""
    log("🚀 INICIANDO MIGRAÇÃO COMPLETA PARA SUPABASE")
    log("="*60)
    
    # Verificações iniciais
    if not verificar_dependencias():
        log("❌ Falha na verificação de dependências")
        return False
    
    if not verificar_arquivos():
        log("❌ Falha na verificação de arquivos")
        return False
    
    # Verificar se arquivo .env existe
    if not os.path.exists('.env'):
        log("📁 Arquivo .env não encontrado")
        log("🔧 Executando configuração...")
        if not executar_script('configurar_migracao.py', 'Configuração'):
            log("❌ Falha na configuração")
            return False
    
    # Executar etapas
    etapas = [
        ('backup_pre_migracao.py', 'Backup pré-migração'),
        ('migracao_supabase_3_etapas.py', 'Migração em 3 etapas'),
        ('verificar_migracao.py', 'Verificação pós-migração')
    ]
    
    resultados = []
    
    for i, (script, descricao) in enumerate(etapas):
        log(f"\n🎯 EXECUTANDO ETAPA {i+1}/3: {descricao}")
        
        resultado = executar_script(script, descricao)
        resultados.append(resultado)
        
        if not resultado:
            log(f"❌ Falha na etapa: {descricao}")
            log("🛑 Processo interrompido")
            break
        
        if i < len(etapas) - 1:
            log(f"⏸️ Pausa de 10 segundos antes da próxima etapa...")
            time.sleep(10)
    
    # Relatório final
    log("="*60)
    log("📋 RELATÓRIO FINAL")
    log("="*60)
    
    etapas_nomes = ["Backup", "Migração", "Verificação"]
    
    for i, (nome, resultado) in enumerate(zip(etapas_nomes, resultados)):
        status = "✅ OK" if resultado else "❌ FALHOU"
        log(f"Etapa {i+1}: {nome} - {status}")
    
    total_ok = sum(resultados)
    total_etapas = len(resultados)
    
    log(f"\n📊 RESUMO:")
    log(f"Etapas concluídas: {total_ok}/{total_etapas}")
    
    if total_ok == total_etapas:
        log("🎉 MIGRAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!")
        log("✅ Sistema pronto para uso em produção")
    else:
        log("⚠️ MIGRAÇÃO PARCIALMENTE CONCLUÍDA")
        log("🔍 Verifique os erros e execute novamente se necessário")
    
    log(f"\n📁 Log completo salvo em: migracao_execucao.log")
    
    return all(resultados)

def main():
    """Função principal"""
    log("🚀 EXECUTOR SIMPLIFICADO DE MIGRAÇÃO SUPABASE")
    log("="*60)
    
    # Aviso importante
    log("⚠️ ATENÇÃO: Este processo irá:")
    log("   - Fazer backup dos dados")
    log("   - Migrar todos os dados para o Supabase")
    log("   - Verificar a migração")
    log("⏱️ Tempo estimado: 30-60 minutos")
    
    # Executar migração
    sucesso = executar_migracao()
    
    if sucesso:
        log("\n🎉 MIGRAÇÃO COMPLETA CONCLUÍDA!")
        log("📋 Verifique o arquivo migracao_execucao.log para detalhes")
    else:
        log("\n❌ MIGRAÇÃO FALHOU!")
        log("📋 Verifique o arquivo migracao_execucao.log para detalhes")

if __name__ == "__main__":
    main() 