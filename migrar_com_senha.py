#!/usr/bin/env python
"""
Script para migrar dados usando variável de ambiente PGPASSWORD
"""

import os
import subprocess
import sys

def migrar_com_senha():
    """Executa a migração definindo a senha via variável de ambiente"""
    
    print("🚀 Migração com Senha PostgreSQL")
    print("=" * 40)
    
    # Definir a senha como variável de ambiente
    os.environ['PGPASSWORD'] = 'Erisman@193'
    
    print("✅ Senha definida como variável de ambiente")
    
    # Executar migrações
    print("🔄 Aplicando migrações...")
    resultado = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                             capture_output=True, text=True)
    
    if resultado.returncode == 0:
        print("✅ Migrações aplicadas com sucesso!")
        print(resultado.stdout)
        
        # Importar dados
        print("🔄 Importando dados...")
        resultado2 = subprocess.run([sys.executable, 'manage.py', 'loaddata', 'dados_sqlite_utf8.json'], 
                                  capture_output=True, text=True)
        
        if resultado2.returncode == 0:
            print("✅ Dados importados com sucesso!")
            print(resultado2.stdout)
            
            # Verificar migração
            print("🔍 Verificando migração...")
            comando_verificacao = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()
from django.contrib.auth.models import User
from militares.models import Militar
print(f"Usuários: {User.objects.count()}")
print(f"Militares: {Militar.objects.count()}")
'''
            
            resultado3 = subprocess.run([sys.executable, '-c', comando_verificacao], 
                                      capture_output=True, text=True)
            
            if resultado3.returncode == 0:
                print("✅ Verificação concluída!")
                print(resultado3.stdout)
                print("\n🎉 Migração concluída com sucesso!")
            else:
                print("❌ Erro na verificação:")
                print(resultado3.stderr)
        else:
            print("❌ Erro ao importar dados:")
            print(resultado2.stderr)
    else:
        print("❌ Erro ao aplicar migrações:")
        print(resultado.stderr)

if __name__ == "__main__":
    migrar_com_senha() 