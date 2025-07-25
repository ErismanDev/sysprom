#!/usr/bin/env python
"""
Script para importar dados restantes com tratamento de dependências
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import *
from django.contrib.auth.models import User, Group
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session

def importar_usuarios_grupos():
    """Importa usuários e grupos"""
    
    print("🔧 Importando usuários e grupos...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar grupos e usuários
    grupos = [item for item in dados if item['model'] == 'auth.group']
    usuarios = [item for item in dados if item['model'] == 'auth.user']
    
    print(f"📊 Grupos encontrados: {len(grupos)}")
    print(f"📊 Usuários encontrados: {len(usuarios)}")
    
    # Importar grupos
    importados_grupos = 0
    for item in grupos:
        try:
            fields = item['fields']
            grupo = Group.objects.create(**fields)
            importados_grupos += 1
        except Exception as e:
            print(f"❌ Erro ao importar grupo: {e}")
    
    # Importar usuários
    importados_usuarios = 0
    for item in usuarios:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['groups', 'user_permissions']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            usuario = User.objects.create(**fields)
            importados_usuarios += 1
        except Exception as e:
            print(f"❌ Erro ao importar usuário: {e}")
    
    print(f"✅ Grupos importados: {importados_grupos}")
    print(f"✅ Usuários importados: {importados_usuarios}")
    
    return importados_grupos + importados_usuarios

def importar_comissoes():
    """Importa comissões de promoção"""
    
    print("\n🔧 Importando comissões de promoção...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar comissões
    comissoes = [item for item in dados if item['model'] == 'militares.comissaopromocao']
    
    print(f"📊 Comissões encontradas: {len(comissoes)}")
    
    # Importar comissões
    importados = 0
    for item in comissoes:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['presidente', 'secretario', 'membros']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            comissao = ComissaoPromocao.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar comissão: {e}")
    
    print(f"✅ Comissões importadas: {importados}")
    
    return importados

def importar_sessoes():
    """Importa sessões de comissão"""
    
    print("\n🔧 Importando sessões de comissão...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar sessões
    sessoes = [item for item in dados if item['model'] == 'militares.sessaocomissao']
    
    print(f"📊 Sessões encontradas: {len(sessoes)}")
    
    # Importar sessões
    importados = 0
    for item in sessoes:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['comissao', 'presidente', 'secretario', 'membros_presentes']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            sessao = SessaoComissao.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar sessão: {e}")
    
    print(f"✅ Sessões importadas: {importados}")
    
    return importados

def importar_quadros_acesso():
    """Importa quadros de acesso"""
    
    print("\n🔧 Importando quadros de acesso...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar quadros
    quadros = [item for item in dados if item['model'] == 'militares.quadroacesso']
    
    print(f"📊 Quadros encontrados: {len(quadros)}")
    
    # Importar quadros
    importados = 0
    for item in quadros:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['homologado_por', 'assinaturas']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            quadro = QuadroAcesso.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar quadro: {e}")
    
    print(f"✅ Quadros importados: {importados}")
    
    return importados

def importar_previsoes_vagas():
    """Importa previsões de vagas"""
    
    print("\n🔧 Importando previsões de vagas...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar previsões
    previsoes = [item for item in dados if item['model'] == 'militares.previsaovaga']
    
    print(f"📊 Previsões encontradas: {len(previsoes)}")
    
    # Importar previsões
    importados = 0
    for item in previsoes:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['quadro_acesso']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            previsao = PrevisaoVaga.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar previsão: {e}")
    
    print(f"✅ Previsões importadas: {importados}")
    
    return importados

def importar_vagas():
    """Importa vagas"""
    
    print("\n🔧 Importando vagas...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar vagas
    vagas = [item for item in dados if item['model'] == 'militares.vaga']
    
    print(f"📊 Vagas encontradas: {len(vagas)}")
    
    # Importar vagas
    importados = 0
    for item in vagas:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['previsao_vaga', 'militar']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            vaga = Vaga.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar vaga: {e}")
    
    print(f"✅ Vagas importadas: {importados}")
    
    return importados

def importar_modelos_ata():
    """Importa modelos de ata"""
    
    print("\n🔧 Importando modelos de ata...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar modelos
    modelos = [item for item in dados if item['model'] == 'militares.modeloata']
    
    print(f"📊 Modelos encontrados: {len(modelos)}")
    
    # Importar modelos
    importados = 0
    for item in modelos:
        try:
            fields = item['fields']
            modelo = ModeloAta.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar modelo: {e}")
    
    print(f"✅ Modelos importados: {importados}")
    
    return importados

def importar_atas_sessao():
    """Importa atas de sessão"""
    
    print("\n🔧 Importando atas de sessão...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar atas
    atas = [item for item in dados if item['model'] == 'militares.atasessao']
    
    print(f"📊 Atas encontradas: {len(atas)}")
    
    # Importar atas
    importados = 0
    for item in atas:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['sessao', 'assinaturas']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            ata = AtaSessao.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar ata: {e}")
    
    print(f"✅ Atas importadas: {importados}")
    
    return importados

def importar_presencas():
    """Importa presenças em sessões"""
    
    print("\n🔧 Importando presenças em sessões...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar presenças
    presencas = [item for item in dados if item['model'] == 'militares.presencasessao']
    
    print(f"📊 Presenças encontradas: {len(presencas)}")
    
    # Importar presenças
    importados = 0
    for item in presencas:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['sessao', 'membro']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            presenca = PresencaSessao.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar presença: {e}")
    
    print(f"✅ Presenças importadas: {importados}")
    
    return importados

def importar_documentos_sessao():
    """Importa documentos de sessão"""
    
    print("\n🔧 Importando documentos de sessão...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar documentos
    documentos = [item for item in dados if item['model'] == 'militares.documentosessao']
    
    print(f"📊 Documentos encontrados: {len(documentos)}")
    
    # Importar documentos
    importados = 0
    for item in documentos:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['sessao']
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            documento = DocumentoSessao.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar documento: {e}")
    
    print(f"✅ Documentos importados: {importados}")
    
    return importados

def importar_sessions():
    """Importa sessões do Django"""
    
    print("\n🔧 Importando sessões do Django...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar sessões
    sessions = [item for item in dados if item['model'] == 'sessions.session']
    
    print(f"📊 Sessões encontradas: {len(sessions)}")
    
    # Importar sessões
    importados = 0
    for item in sessions:
        try:
            fields = item['fields']
            session = Session.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar sessão: {e}")
    
    print(f"✅ Sessões importadas: {importados}")
    
    return importados

if __name__ == "__main__":
    print("🚀 Iniciando importação de dados restantes")
    print("=" * 50)
    
    total_importados = 0
    
    # Importar dados em ordem de dependência
    total_importados += importar_usuarios_grupos()
    total_importados += importar_comissoes()
    total_importados += importar_sessoes()
    total_importados += importar_quadros_acesso()
    total_importados += importar_previsoes_vagas()
    total_importados += importar_vagas()
    total_importados += importar_modelos_ata()
    total_importados += importar_atas_sessao()
    total_importados += importar_presencas()
    total_importados += importar_documentos_sessao()
    total_importados += importar_sessions()
    
    print(f"\n🎉 Processo concluído!")
    print(f"📊 Total de itens importados: {total_importados}") 