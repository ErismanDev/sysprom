#!/usr/bin/env python
"""
Script para alterar a senha do PostgreSQL
"""

import os
import subprocess
import sys

def alterar_senha_postgres():
    """Altera a senha do PostgreSQL"""
    
    print("🔧 Alterando senha do PostgreSQL")
    print("=" * 40)
    
    # Adicionar PostgreSQL ao PATH
    os.environ['PATH'] += ";C:\\Program Files\\PostgreSQL\\17\\bin"
    
    # Definir senha atual
    senha_atual = "Erisman@193"
    nova_senha = "postgres123"
    
    print(f"📝 Senha atual: {senha_atual}")
    print(f"🔄 Nova senha: {nova_senha}")
    
    # Comando para alterar a senha
    comando = f'psql -U postgres -c "ALTER USER postgres PASSWORD \'{nova_senha}\';"'
    
    try:
        # Executar o comando com a senha atual
        resultado = subprocess.run(
            comando,
            shell=True,
            env={'PGPASSWORD': senha_atual, 'PATH': os.environ['PATH']},
            capture_output=True,
            text=True
        )
        
        if resultado.returncode == 0:
            print("✅ Senha alterada com sucesso!")
            print("🔄 Agora você pode usar a nova senha: postgres123")
            
            # Atualizar o settings.py
            atualizar_settings()
            
        else:
            print(f"❌ Erro ao alterar senha: {resultado.stderr}")
            print("💡 Tentando método alternativo...")
            tentar_metodo_alternativo()
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("💡 Tentando método alternativo...")
        tentar_metodo_alternativo()

def tentar_metodo_alternativo():
    """Tenta método alternativo usando pgAdmin ou arquivo de configuração"""
    
    print("🔧 Método alternativo - Criando arquivo de configuração")
    
    # Criar arquivo .pgpass
    pgpass_content = "localhost:5432:sepromcbmepi:postgres:postgres123\n"
    
    try:
        # Criar diretório se não existir
        pgpass_dir = os.path.expanduser("~/.pgpass")
        if not os.path.exists(os.path.dirname(pgpass_dir)):
            os.makedirs(os.path.dirname(pgpass_dir), exist_ok=True)
        
        # Salvar arquivo .pgpass
        with open(pgpass_dir, 'w') as f:
            f.write(pgpass_content)
        
        # Definir permissões (no Windows não é necessário)
        print("✅ Arquivo .pgpass criado")
        print("🔄 Agora tente conectar novamente")
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .pgpass: {e}")

def atualizar_settings():
    """Atualiza o settings.py com a nova senha"""
    
    try:
        with open('sepromcbmepi/settings.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Substituir a senha
        import re
        padrao = r'("PASSWORD":\s*)"[^"]*"'
        nova_senha = '("PASSWORD": "postgres123")'
        novo_conteudo = re.sub(padrao, nova_senha, conteudo)
        
        with open('sepromcbmepi/settings.py', 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        
        print("✅ Settings.py atualizado com a nova senha")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar settings.py: {e}")

if __name__ == "__main__":
    alterar_senha_postgres() 