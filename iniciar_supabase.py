#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Iniciar servidor Django com Supabase
"""

import os
import sys
import subprocess

print("🚀 Iniciando SEPROM CBMEPI com Supabase...")
print("=" * 50)

# Verificar se estamos no diretório correto
if not os.path.exists('manage.py'):
    print("❌ Erro: execute este script na raiz do projeto Django")
    sys.exit(1)

# Verificar se o arquivo de configuração existe
if not os.path.exists('sepromcbmepi/settings_supabase.py'):
    print("❌ Erro: arquivo sepromcbmepi/settings_supabase.py não encontrado")
    sys.exit(1)

print("✅ Configurações verificadas")
print("✅ Iniciando servidor...")
print("=" * 50)
print("📋 Informações:")
print("   • URL: http://127.0.0.1:8000")
print("   • Admin: http://127.0.0.1:8000/admin")
print("   • Usuário: admin")
print("   • Senha: admin123")
print("=" * 50)
print("🔄 Para parar o servidor, pressione Ctrl+C")
print("=" * 50)

try:
    # Iniciar o servidor Django com configurações do Supabase
    subprocess.run([
        sys.executable, 'manage.py', 'runserver', 
        '--settings=sepromcbmepi.settings_supabase',
        '--noreload'
    ])
except KeyboardInterrupt:
    print("\n🛑 Servidor parado pelo usuário")
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    sys.exit(1) 