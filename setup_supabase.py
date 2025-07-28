#!/usr/bin/env python
"""
Script completo para configurar o Supabase no projeto SEPROM CBMEPI
"""

import os
import sys
import subprocess
from pathlib import Path

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("Verificando dependencias...")
    
    dependencias = [
        ('django', 'django'),
        ('psycopg2-binary', 'psycopg2'),
        ('dj-database-url', 'dj_database_url'),
        ('whitenoise', 'whitenoise')
    ]
    
    for nome_dep, import_name in dependencias:
        try:
            __import__(import_name)
            print(f"[OK] {nome_dep}")
        except ImportError:
            print(f"[ERRO] {nome_dep} nao encontrado")
            return False
    
    return True

def configurar_senha():
    """Solicita a senha do Supabase ao usuário"""
    print("\nConfiguracao da Senha do Supabase")
    print("=" * 50)
    
    senha = input("Digite a senha do seu banco Supabase: ").strip()
    
    if not senha:
        print("[ERRO] Senha nao pode estar vazia!")
        return None
    
    return senha

def atualizar_arquivos_configuracao(senha):
    """Atualiza os arquivos de configuração com a senha"""
    print("\nAtualizando arquivos de configuracao...")
    
    arquivos = [
        'sepromcbmepi/settings_supabase.py',
        'conectar_supabase.py',
        'migrar_para_supabase.py'
    ]
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                conteudo_atualizado = conteudo.replace('[YOUR-PASSWORD]', senha)
                
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo_atualizado)
                
                print(f"[OK] {arquivo} atualizado")
            except Exception as e:
                print(f"[ERRO] Erro ao atualizar {arquivo}: {e}")
        else:
            print(f"[AVISO] Arquivo {arquivo} nao encontrado")

def testar_conexao():
    """Testa a conexão com o Supabase"""
    print("\nTestando conexao com o Supabase...")
    
    try:
        result = subprocess.run([sys.executable, 'testar_supabase.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Conexao estabelecida com sucesso!")
            print(result.stdout)
            return True
        else:
            print("[ERRO] Falha na conexao:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao testar conexao: {e}")
        return False

def executar_migracoes():
    """Executa as migrações no Supabase"""
    print("\nExecutando migracoes...")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate',
            '--settings=sepromcbmepi.settings_supabase'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Migracoes executadas com sucesso!")
            return True
        else:
            print("[ERRO] Erro nas migracoes:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao executar migracoes: {e}")
        return False

def criar_superusuario():
    """Cria um superusuário no Supabase"""
    print("\nCriando superusuario...")
    
    try:
        # Dados do superusuário
        username = "erisman"
        email = "erisman@cbmepi.com"
        password = "admin123456"
        
        cmd = [
            sys.executable, 'manage.py', 'shell',
            '--settings=sepromcbmepi.settings_supabase',
            '-c', f'''
from django.contrib.auth.models import User
if not User.objects.filter(username="{username}").exists():
    User.objects.create_superuser("{username}", "{email}", "{password}")
    print("Superusuario criado com sucesso!")
else:
    print("Superusuario ja existe!")
'''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Superusuario criado/verificado!")
            print(f"Usuario: {username}")
            print(f"Senha: {password}")
            return True
        else:
            print("[ERRO] Erro ao criar superusuario:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao criar superusuario: {e}")
        return False

def mostrar_instrucoes_finais():
    """Mostra as instruções finais"""
    print("\nConfiguracao do Supabase concluida!")
    print("=" * 60)
    print("Proximos passos:")
    print()
    print("1. Para executar o servidor com Supabase:")
    print("   python manage.py runserver --settings=sepromcbmepi.settings_supabase")
    print()
    print("2. Para acessar o sistema:")
    print("   http://localhost:8000")
    print()
    print("3. Credenciais de login:")
    print("   Usuario: erisman")
    print("   Senha: admin123456")
    print()
    print("4. Para migrar dados do banco local:")
    print("   python migrar_para_supabase.py")
    print()
    print("5. Para testar a conexao:")
    print("   python testar_supabase.py")
    print()
    print("Documentacao completa: GUIA_SUPABASE.md")
    print()
    print("IMPORTANTE:")
    print("- Mantenha suas credenciais seguras")
    print("- Faca backup regular dos dados")
    print("- Monitore o uso do banco no dashboard do Supabase")

def main():
    """Função principal"""
    print("Configuracao do Supabase - SEPROM CBMEPI")
    print("=" * 60)
    print("Desenvolvido por: Erisman Org")
    print()
    
    # Verificar dependências
    if not verificar_dependencias():
        print("\n[ERRO] Algumas dependencias estao faltando!")
        print("Execute: pip install -r requirements.txt")
        return
    
    # Configurar senha
    senha = configurar_senha()
    if not senha:
        return
    
    # Atualizar arquivos
    atualizar_arquivos_configuracao(senha)
    
    # Testar conexão
    if not testar_conexao():
        print("\n[ERRO] Falha na conexao. Verifique suas credenciais.")
        return
    
    # Executar migrações
    if not executar_migracoes():
        print("\n[ERRO] Falha nas migracoes.")
        return
    
    # Criar superusuário
    if not criar_superusuario():
        print("\n[ERRO] Falha na criacao do superusuario.")
        return
    
    # Mostrar instruções finais
    mostrar_instrucoes_finais()

if __name__ == "__main__":
    main() 