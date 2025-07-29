#!/usr/bin/env python3
"""
Script para forçar um novo deploy no Render
"""

import os
import subprocess
import time

def verificar_configuracao_atual():
    """Verifica se a configuração atual está correta"""
    
    print("🔍 Verificando configuração atual...")
    
    # Verificar se o pytz está no requirements.txt
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pytz' in content:
                print("✅ pytz encontrado no requirements.txt")
            else:
                print("❌ pytz não encontrado no requirements.txt")
                return False
    except FileNotFoundError:
        print("❌ requirements.txt não encontrado")
        return False
    
    # Verificar se o settings_render.py existe
    if os.path.exists('sepromcbmepi/settings_render.py'):
        print("✅ settings_render.py encontrado")
    else:
        print("❌ settings_render.py não encontrado")
        return False
    
    # Verificar se o render.yaml está correto
    try:
        with open('render.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'sepromcbmepi.settings_render' in content:
                print("✅ render.yaml configurado corretamente")
            else:
                print("❌ render.yaml não está configurado corretamente")
                return False
    except FileNotFoundError:
        print("❌ render.yaml não encontrado")
        return False
    
    return True

def forcar_deploy():
    """Força um novo deploy fazendo um commit vazio"""
    
    print("\n🚀 Forçando novo deploy no Render...")
    
    try:
        # Fazer um commit vazio para forçar o deploy
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '--allow-empty', '-m', 'Forçar deploy Render - correções pytz'], check=True)
        print("✅ Commit vazio criado")
        
        # Fazer push
        subprocess.run(['git', 'push', 'origin', 'master'], check=True)
        print("✅ Push realizado com sucesso")
        
        print("\n📋 Deploy forçado! O Render irá fazer o deploy automaticamente.")
        print("⏰ Aguarde alguns minutos e verifique o status no painel do Render.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao forçar deploy: {e}")
        return False
    
    return True

def verificar_status_git():
    """Verifica o status do git"""
    
    print("\n📊 Status do Git:")
    
    try:
        # Verificar branch atual
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        print(f"🌿 Branch atual: {result.stdout.strip()}")
        
        # Verificar status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("📝 Há alterações não commitadas")
            return False
        else:
            print("✅ Repositório limpo")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao verificar status: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Script para forçar deploy no Render")
    print("=" * 50)
    
    # Verificar configuração
    if not verificar_configuracao_atual():
        print("\n❌ Configuração incorreta. Corrija os problemas antes de continuar.")
        return
    
    # Verificar status do git
    if not verificar_status_git():
        print("\n❌ Há alterações pendentes. Faça commit antes de continuar.")
        return
    
    # Confirmar ação
    print("\n⚠️  ATENÇÃO: Isso irá forçar um novo deploy no Render.")
    resposta = input("Deseja continuar? (s/N): ").strip().lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        if forcar_deploy():
            print("\n✅ Deploy forçado com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Acesse o painel do Render")
            print("2. Monitore os logs do deploy")
            print("3. Verifique se o erro do pytz foi resolvido")
        else:
            print("\n❌ Falha ao forçar deploy")
    else:
        print("\n❌ Operação cancelada")

if __name__ == "__main__":
    main() 