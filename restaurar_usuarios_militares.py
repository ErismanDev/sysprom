#!/usr/bin/env python
"""
Script para restaurar apenas usuários e militares do backup JSON
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

def restaurar_usuarios_militares(arquivo_backup):
    """
    Restaura apenas usuários e militares do backup JSON
    """
    print(f"Iniciando restauração de usuários e militares do backup: {arquivo_backup}")
    
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
        print("Erro: Não foi possível ler o arquivo de backup com nenhuma codificação")
        return
    
    print(f"Backup carregado com sucesso. Contém {len(dados_backup)} modelos.")
    
    # Limpar dados existentes de militares e usuários
    print("Limpando dados existentes...")
    
    # Limpar militares e dados relacionados
    modelos_limpar = [
        Militar,
        FichaConceitoOficiais,
        FichaConceitoPracas,
        SessaoComissao,
        ComissaoPromocao,
        MembroComissao,
        VotoDeliberacao,
        PermissaoFuncao,
        NotificacaoSessao,
        AlmanaqueMilitar,
        AssinaturaAlmanaque,
    ]
    
    for modelo in modelos_limpar:
        try:
            count = modelo.objects.count()
            if count > 0:
                print(f"  Removendo {count} registros de {modelo.__name__}")
                modelo.objects.all().delete()
        except Exception as e:
            print(f"  Erro ao limpar {modelo.__name__}: {e}")
    
    # Limpar usuários (exceto superusuários)
    try:
        usuarios_para_remover = User.objects.filter(is_superuser=False)
        count = usuarios_para_remover.count()
        if count > 0:
            print(f"  Removendo {count} usuários não-superusuários")
            usuarios_para_remover.delete()
    except Exception as e:
        print(f"  Erro ao limpar usuários: {e}")
    
    # Restaurar dados na ordem correta
    print("Restaurando dados...")
    
    # 1. Restaurar usuários primeiro
    if 'auth.user' in dados_backup:
        print("  Restaurando usuários...")
        usuarios_data = dados_backup['auth.user']
        
        for user_data in usuarios_data:
            try:
                # Remover campos que não devem ser definidos manualmente
                campos_remover = ['id', 'last_login', 'date_joined']
                for campo in campos_remover:
                    if campo in user_data:
                        del user_data[campo]
                
                # Verificar se o usuário já existe
                username = user_data.get('username')
                if username and not User.objects.filter(username=username).exists():
                    user = User(**user_data)
                    user.save()
                    print(f"    Usuário criado: {username}")
                
            except Exception as e:
                print(f"    Erro ao criar usuário: {e}")
    
    # 2. Restaurar militares
    if 'militares.militar' in dados_backup:
        print("  Restaurando militares...")
        militares_data = dados_backup['militares.militar']
        
        for militar_data in militares_data:
            try:
                # Remover campos que não devem ser definidos manualmente
                campos_remover = ['id', 'created_at', 'updated_at']
                for campo in campos_remover:
                    if campo in militar_data:
                        del militar_data[campo]
                
                # Verificar se o militar já existe
                matricula = militar_data.get('matricula')
                if matricula and not Militar.objects.filter(matricula=matricula).exists():
                    militar = Militar(**militar_data)
                    militar.save()
                    print(f"    Militar criado: {matricula}")
                
            except Exception as e:
                print(f"    Erro ao criar militar: {e}")
    
    # 3. Restaurar fichas de conceito de oficiais
    if 'militares.fichaconceitoficiais' in dados_backup:
        print("  Restaurando fichas de conceito de oficiais...")
        fichas_data = dados_backup['militares.fichaconceitoficiais']
        
        for ficha_data in fichas_data:
            try:
                # Remover campos que não devem ser definidos manualmente
                campos_remover = ['id', 'created_at', 'updated_at']
                for campo in campos_remover:
                    if campo in ficha_data:
                        del ficha_data[campo]
                
                ficha = FichaConceitoOficiais(**ficha_data)
                ficha.save()
                
            except Exception as e:
                print(f"    Erro ao criar ficha de conceito de oficiais: {e}")
    
    # 4. Restaurar fichas de conceito de praças
    if 'militares.fichaconceitopracas' in dados_backup:
        print("  Restaurando fichas de conceito de praças...")
        fichas_data = dados_backup['militares.fichaconceitopracas']
        
        for ficha_data in fichas_data:
            try:
                # Remover campos que não devem ser definidos manualmente
                campos_remover = ['id', 'created_at', 'updated_at']
                for campo in campos_remover:
                    if campo in ficha_data:
                        del ficha_data[campo]
                
                ficha = FichaConceitoPracas(**ficha_data)
                ficha.save()
                
            except Exception as e:
                print(f"    Erro ao criar ficha de conceito de praças: {e}")
    
    # 5. Restaurar outros dados relacionados se necessário
    modelos_restaurar = [
        ('militares.sessaocomissao', SessaoComissao),
        ('militares.comissaopromocao', ComissaoPromocao),
        ('militares.membrocomissao', MembroComissao),
        ('militares.votodeliberacao', VotoDeliberacao),
        ('militares.permissaofuncao', PermissaoFuncao),
        ('militares.notificacaosessao', NotificacaoSessao),
    ]
    
    for modelo_key, modelo_class in modelos_restaurar:
        if modelo_key in dados_backup:
            print(f"  Restaurando {modelo_key}...")
            dados_modelo = dados_backup[modelo_key]
            
            for item_data in dados_modelo:
                try:
                    # Remover campos que não devem ser definidos manualmente
                    campos_remover = ['id', 'created_at', 'updated_at']
                    for campo in campos_remover:
                        if campo in item_data:
                            del item_data[campo]
                    
                    obj = modelo_class(**item_data)
                    obj.save()
                    
                except Exception as e:
                    print(f"    Erro ao criar {modelo_key}: {e}")
    
    print("Restauração de usuários e militares concluída!")
    
    # Mostrar estatísticas
    print("\nEstatísticas da restauração:")
    print(f"  Usuários: {User.objects.count()}")
    print(f"  Militares: {Militar.objects.count()}")
    print(f"  Fichas de Conceito - Oficiais: {FichaConceitoOficiais.objects.count()}")
    print(f"  Fichas de Conceito - Praças: {FichaConceitoPracas.objects.count()}")
    print(f"  Sessões: {SessaoComissao.objects.count()}")
    print(f"  Comissões: {ComissaoPromocao.objects.count()}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python restaurar_usuarios_militares.py <arquivo_backup.json>")
        sys.exit(1)
    
    arquivo_backup = sys.argv[1]
    
    if not os.path.exists(arquivo_backup):
        print(f"Arquivo de backup não encontrado: {arquivo_backup}")
        sys.exit(1)
    
    try:
        restaurar_usuarios_militares(arquivo_backup)
    except Exception as e:
        print(f"Erro durante a restauração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 