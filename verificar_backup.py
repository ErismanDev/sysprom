#!/usr/bin/env python
"""
Script para verificar o conteúdo do backup JSON
"""

import json

def verificar_backup(arquivo_backup):
    """
    Verifica o conteúdo do backup JSON
    """
    print(f"Verificando backup: {arquivo_backup}")
    
    # Tentar diferentes codificações
    codificacoes = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
    dados_backup = None
    
    for encoding in codificacoes:
        try:
            with open(arquivo_backup, 'r', encoding=encoding) as f:
                dados_backup = json.load(f)
            print(f"Arquivo lido com sucesso usando codificação: {encoding}")
            break
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            continue
    
    if dados_backup is None:
        print("Erro: Não foi possível ler o arquivo de backup")
        return
    
    print(f"\nBackup contém {len(dados_backup)} modelos:")
    
    # Listar todos os modelos disponíveis
    for modelo in sorted(dados_backup.keys()):
        count = len(dados_backup[modelo])
        print(f"  {modelo}: {count} registros")
    
    # Verificar especificamente modelos relacionados a militares
    modelos_militares = [k for k in dados_backup.keys() if 'militar' in k.lower()]
    if modelos_militares:
        print(f"\nModelos relacionados a militares:")
        for modelo in modelos_militares:
            count = len(dados_backup[modelo])
            print(f"  {modelo}: {count} registros")
    
    # Verificar especificamente modelos relacionados a usuários
    modelos_usuarios = [k for k in dados_backup.keys() if 'user' in k.lower()]
    if modelos_usuarios:
        print(f"\nModelos relacionados a usuários:")
        for modelo in modelos_usuarios:
            count = len(dados_backup[modelo])
            print(f"  {modelo}: {count} registros")

if __name__ == '__main__':
    arquivo_backup = 'backups/backup_completo_20250724_130613.json'
    verificar_backup(arquivo_backup) 