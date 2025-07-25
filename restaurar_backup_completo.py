#!/usr/bin/env python
"""
Script para restaurar backup completo do sistema SEPROMCBMEPI
Formato: Django dumpdata (lista de objetos)
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

def restaurar_backup_completo(arquivo_backup):
    """
    Restaura o backup completo no formato Django dumpdata
    """
    print(f"Iniciando restauração completa do backup: {arquivo_backup}")
    
    # Ler o arquivo de backup
    try:
        with open(arquivo_backup, 'r', encoding='utf-16') as f:
            dados_backup = json.load(f)
        print(f"Backup carregado com sucesso. Contém {len(dados_backup)} objetos.")
    except Exception as e:
        print(f"Erro ao ler backup: {e}")
        return
    
    # Limpar todos os dados existentes
    print("Limpando dados existentes...")
    
    # Ordem de limpeza (dependências)
    modelos_limpar = [
        # Modelos de militares
        AssinaturaAlmanaque,
        AlmanaqueMilitar,
        ItemCalendarioPromocao,
        AssinaturaCalendarioPromocao,
        CalendarioPromocao,
        AssinaturaQuadroFixacaoVagas,
        ItemQuadroFixacaoVagas,
        QuadroFixacaoVagas,
        VagaManual,
        NotificacaoSessao,
        ItemQuadroAcesso,
        QuadroAcesso,
        Promocao,
        Vaga,
        PrevisaoVaga,
        Documento,
        FichaConceitoPracas,
        FichaConceitoOficiais,
        Intersticio,
        Militar,
        
        # Modelos de comissão
        VotoDeliberacao,
        DeliberacaoComissao,
        MembroComissao,
        SessaoComissao,
        ComissaoPromocao,
        
        # Modelos de usuários e permissões
        UsuarioFuncao,
        PermissaoFuncao,
        PerfilAcesso,
        CargoFuncao,
        CargoComissao,
        
        # Modelos Django
        User,
        Group,
        Permission,
        ContentType,
    ]
    
    for modelo in modelos_limpar:
        try:
            count = modelo.objects.count()
            if count > 0:
                print(f"  Removendo {count} registros de {modelo.__name__}")
                modelo.objects.all().delete()
        except Exception as e:
            print(f"  Erro ao limpar {modelo.__name__}: {e}")
    
    # Restaurar dados
    print("Restaurando dados...")
    
    # Contadores
    contadores = {}
    
    for item in dados_backup:
        try:
            model_name = item['model']
            pk = item['pk']
            fields = item['fields']
            
            # Obter o modelo
            app_label, model_name_short = model_name.split('.')
            model = django.apps.apps.get_model(app_label, model_name_short)
            
            # Contar por modelo
            if model_name not in contadores:
                contadores[model_name] = 0
            
            # Criar o objeto
            obj = model(pk=pk, **fields)
            obj.save()
            contadores[model_name] += 1
            
            # Mostrar progresso a cada 100 objetos
            if sum(contadores.values()) % 100 == 0:
                print(f"  Restaurados {sum(contadores.values())} objetos...")
                
        except Exception as e:
            print(f"  Erro ao restaurar {item.get('model', 'desconhecido')}: {e}")
            continue
    
    print("Restauração concluída!")
    
    # Mostrar estatísticas
    print("\nEstatísticas da restauração:")
    for model_name, count in sorted(contadores.items()):
        if count > 0:
            print(f"  {model_name}: {count} objetos")
    
    # Estatísticas finais
    print(f"\nTotal de objetos restaurados: {sum(contadores.values())}")
    print(f"Usuários no sistema: {User.objects.count()}")
    print(f"Militares no sistema: {Militar.objects.count()}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python restaurar_backup_completo.py <arquivo_backup.json>")
        sys.exit(1)
    
    arquivo_backup = sys.argv[1]
    
    if not os.path.exists(arquivo_backup):
        print(f"Arquivo de backup não encontrado: {arquivo_backup}")
        sys.exit(1)
    
    try:
        restaurar_backup_completo(arquivo_backup)
    except Exception as e:
        print(f"Erro durante a restauração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 