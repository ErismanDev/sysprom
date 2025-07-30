#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE RÁPIDO DE MIGRAÇÃO SUPABASE
==================================

Script para testar rapidamente se todos os componentes da migração
estão funcionando corretamente.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import sys
import importlib
from datetime import datetime

def testar_importacao(module_name, package_name=None):
    """Testa se um módulo pode ser importado"""
    try:
        if package_name:
            importlib.import_module(package_name)
        else:
            importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def verificar_arquivo(arquivo):
    """Verifica se um arquivo existe"""
    return os.path.exists(arquivo)

def main():
    """Função principal"""
    print("🧪 TESTE RÁPIDO DE MIGRAÇÃO SUPABASE")
    print("="*50)
    
    # Testar dependências
    print("\n📦 TESTANDO DEPENDÊNCIAS:")
    print("-" * 30)
    
    dependencias = [
        ('psycopg2', 'psycopg2-binary'),
        ('dotenv', 'python-dotenv'),
    ]
    
    todas_ok = True
    for module, package in dependencias:
        if testar_importacao(module, package):
            print(f"   ✅ {package}")
        else:
            print(f"   ❌ {package} - NÃO INSTALADO")
            todas_ok = False
    
    # Verificar arquivos
    print("\n📁 VERIFICANDO ARQUIVOS:")
    print("-" * 30)
    
    arquivos_necessarios = [
        'migracao_supabase_3_etapas.py',
        'configurar_migracao.py',
        'backup_pre_migracao.py',
        'verificar_migracao.py',
        'executar_migracao_completa.py',
        'GUIA_MIGRACAO_3_ETAPAS.md',
        'README_MIGRACAO_SUPABASE.md'
    ]
    
    for arquivo in arquivos_necessarios:
        if verificar_arquivo(arquivo):
            print(f"   ✅ {arquivo}")
        else:
            print(f"   ❌ {arquivo} - NÃO ENCONTRADO")
            todas_ok = False
    
    # Verificar arquivos de dados
    print("\n📊 VERIFICANDO ARQUIVOS DE DADOS:")
    print("-" * 30)
    
    arquivos_dados = [
        'migracao_supabase_20250729_130359.sql',
        'associacao_usuarios_20250729_130444.sql'
    ]
    
    for arquivo in arquivos_dados:
        if verificar_arquivo(arquivo):
            tamanho = os.path.getsize(arquivo)
            print(f"   ✅ {arquivo} ({tamanho} bytes)")
        else:
            print(f"   ⚠️ {arquivo} - NÃO ENCONTRADO (opcional)")
    
    # Verificar configuração
    print("\n⚙️ VERIFICANDO CONFIGURAÇÃO:")
    print("-" * 30)
    
    if verificar_arquivo('.env'):
        print("   ✅ Arquivo .env encontrado")
        
        # Verificar variáveis importantes
        with open('.env', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        variaveis_importantes = [
            'SUPABASE_HOST',
            'SUPABASE_PASSWORD',
            'LOCAL_DB_PASSWORD'
        ]
        
        for var in variaveis_importantes:
            if var in conteudo:
                print(f"   ✅ {var} configurada")
            else:
                print(f"   ❌ {var} não configurada")
                todas_ok = False
    else:
        print("   ❌ Arquivo .env não encontrado")
        print("   💡 Execute: python configurar_migracao.py")
        todas_ok = False
    
    # Testar sintaxe dos scripts
    print("\n🔍 TESTANDO SINTAXE DOS SCRIPTS:")
    print("-" * 30)
    
    scripts_para_testar = [
        'migracao_supabase_3_etapas.py',
        'configurar_migracao.py',
        'backup_pre_migracao.py',
        'verificar_migracao.py',
        'executar_migracao_completa.py'
    ]
    
    for script in scripts_para_testar:
        if verificar_arquivo(script):
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    compile(f.read(), script, 'exec')
                print(f"   ✅ {script} - Sintaxe OK")
            except SyntaxError as e:
                print(f"   ❌ {script} - Erro de sintaxe: {e}")
                todas_ok = False
        else:
            print(f"   ❌ {script} - Arquivo não encontrado")
            todas_ok = False
    
    # Relatório final
    print("\n" + "="*50)
    print("📋 RELATÓRIO FINAL")
    print("="*50)
    
    if todas_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para migração")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python executar_migracao_completa.py")
        print("2. Ou execute manualmente cada etapa")
        print("3. Monitore os logs durante a migração")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("🔍 Verifique os problemas acima")
        print("\n💡 SOLUÇÕES:")
        print("1. Instale dependências: pip install psycopg2-binary python-dotenv")
        print("2. Configure ambiente: python configurar_migracao.py")
        print("3. Verifique se todos os arquivos estão presentes")
    
    print(f"\n⏰ Teste realizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 