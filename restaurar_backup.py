#!/usr/bin/env python
"""
Script para restaurar backup JSON do sistema SEPROMCBMEPI
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from militares.models import *

def restaurar_backup_json(arquivo_backup):
    """
    Restaura o backup a partir de um arquivo JSON
    """
    print(f"Iniciando restauração do backup: {arquivo_backup}")
    
    # Ler o arquivo de backup
    with open(arquivo_backup, 'r', encoding='utf-8') as f:
        dados_backup = json.load(f)
    
    print(f"Backup carregado com sucesso. Contém {len(dados_backup)} modelos.")
    
    # Ordem de restauração (dependências)
    ordem_restauracao = [
        'contenttypes.contenttype',
        'auth.permission',
        'auth.group',
        'auth.user',
        'militares.quadro',
        'militares.cargo',
        'militares.funcao',
        'militares.militar',
        'militares.fichaconceito',
        'militares.sessao',
        'militares.comissao',
        'militares.membrocomissao',
        'militares.voto',
        'militares.permissoesimples',
        'militares.notificacao',
        'militares.almanaque',
        'militares.almanaqueassinatura',
    ]
    
    # Limpar dados existentes (exceto contenttypes e permissions)
    print("Limpando dados existentes...")
    for modelo in reversed(ordem_restauracao):
        if modelo.startswith('militares.'):
            app_label, model_name = modelo.split('.')
            try:
                model = django.apps.apps.get_model(app_label, model_name)
                count = model.objects.count()
                if count > 0:
                    print(f"  Removendo {count} registros de {modelo}")
                    model.objects.all().delete()
            except Exception as e:
                print(f"  Erro ao limpar {modelo}: {e}")
    
    # Restaurar dados
    print("Restaurando dados...")
    for modelo in ordem_restauracao:
        if modelo in dados_backup:
            app_label, model_name = modelo.split('.')
            try:
                model = django.apps.apps.get_model(app_label, model_name)
                dados_modelo = dados_backup[modelo]
                
                print(f"  Restaurando {len(dados_modelo)} registros de {modelo}")
                
                # Criar objetos em lotes
                objetos = []
                for item in dados_modelo:
                    # Remover campos que não devem ser definidos manualmente
                    campos_remover = ['id', 'created_at', 'updated_at']
                    for campo in campos_remover:
                        if campo in item:
                            del item[campo]
                    
                    try:
                        obj = model(**item)
                        objetos.append(obj)
                    except Exception as e:
                        print(f"    Erro ao criar objeto {modelo}: {e}")
                        continue
                
                # Salvar em lotes
                if objetos:
                    model.objects.bulk_create(objetos, ignore_conflicts=True)
                    print(f"    {len(objetos)} objetos criados com sucesso")
                
            except Exception as e:
                print(f"  Erro ao restaurar {modelo}: {e}")
    
    print("Restauração concluída!")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python restaurar_backup.py <arquivo_backup.json>")
        sys.exit(1)
    
    arquivo_backup = sys.argv[1]
    
    if not os.path.exists(arquivo_backup):
        print(f"Arquivo de backup não encontrado: {arquivo_backup}")
        sys.exit(1)
    
    try:
        restaurar_backup_json(arquivo_backup)
    except Exception as e:
        print(f"Erro durante a restauração: {e}")
        sys.exit(1) 