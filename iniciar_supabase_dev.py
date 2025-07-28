#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Iniciar servidor Django de desenvolvimento com Supabase
"""

import os
import sys
import subprocess

print("🚀 Iniciando SEPROM CBMEPI (Desenvolvimento) com Supabase...")
print("=" * 60)

# Verificar se estamos no diretório correto
if not os.path.exists('manage.py'):
    print("❌ Erro: execute este script na raiz do projeto Django")
    sys.exit(1)

# Verificar se o arquivo de configuração existe
if not os.path.exists('sepromcbmepi/settings_supabase.py'):
    print("❌ Erro: arquivo sepromcbmepi/settings_supabase.py não encontrado")
    sys.exit(1)

print("✅ Configurações verificadas")
print("✅ Iniciando servidor de desenvolvimento...")
print("=" * 60)
print("📋 Informações de Acesso:")
print("   • URL Principal: http://127.0.0.1:8000")
print("   • URL Admin: http://127.0.0.1:8000/admin")
print("   • Usuário Admin: admin")
print("   • Senha Admin: admin123")
print("=" * 60)
print("⚠️  IMPORTANTE:")
print("   • Use HTTP (não HTTPS) para acessar o servidor")
print("   • URL correta: http://127.0.0.1:8000")
print("   • Não use: https://127.0.0.1:8000")
print("=" * 60)
print("🔄 Para parar o servidor, pressione Ctrl+C")
print("=" * 60)

try:
    # Iniciar o servidor Django com configurações do Supabase
    subprocess.run([
        sys.executable, 'manage.py', 'runserver', 
        '--settings=sepromcbmepi.settings_supabase',
        '127.0.0.1:8000'
    ])
except KeyboardInterrupt:
    print("\n🛑 Servidor parado pelo usuário")
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    sys.exit(1) 