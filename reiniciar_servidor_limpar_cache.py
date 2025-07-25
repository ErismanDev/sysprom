#!/usr/bin/env python
"""
Script para reiniciar o servidor e limpar cache
"""

import os
import sys
import subprocess
import time
import signal

def reiniciar_servidor():
    """Reinicia o servidor Django"""
    
    print("🔄 REINICIANDO SERVIDOR DJANGO")
    print("=" * 50)
    
    # Verificar se há processo rodando na porta 8000
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        if ':8000' in result.stdout:
            print("📡 Servidor detectado na porta 8000")
            
            # Encontrar o PID do processo
            lines = result.stdout.split('\n')
            for line in lines:
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"🔄 Encerrando processo PID: {pid}")
                        
                        try:
                            # Encerrar o processo
                            subprocess.run(['taskkill', '/PID', pid, '/F'], check=True)
                            print("✅ Processo encerrado com sucesso")
                        except subprocess.CalledProcessError:
                            print("⚠️ Não foi possível encerrar o processo automaticamente")
                            print("   Por favor, encerre manualmente o servidor Django")
        else:
            print("📡 Nenhum servidor detectado na porta 8000")
    except Exception as e:
        print(f"⚠️ Erro ao verificar processos: {e}")
    
    print()
    print("🧹 LIMPEZA DE CACHE")
    print("=" * 50)
    
    # Limpar arquivos de cache do Python
    cache_dirs = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.pytest_cache',
        '.coverage'
    ]
    
    for cache_pattern in cache_dirs:
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['del', '/s', '/q', cache_pattern], shell=True, capture_output=True)
            else:  # Linux/Mac
                subprocess.run(['find', '.', '-name', cache_pattern, '-delete'], capture_output=True)
        except Exception as e:
            pass  # Ignorar erros de limpeza
    
    print("✅ Cache limpo")
    
    print()
    print("🚀 INICIANDO NOVO SERVIDOR")
    print("=" * 50)
    
    # Iniciar novo servidor
    try:
        print("📡 Iniciando servidor Django...")
        print("🌐 URL: http://127.0.0.1:8000")
        print("⏹️ Para parar o servidor, pressione Ctrl+C")
        print()
        
        # Iniciar o servidor
        subprocess.run(['python', 'manage.py', 'runserver', '127.0.0.1:8000'])
        
    except KeyboardInterrupt:
        print("\n⏹️ Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    reiniciar_servidor() 