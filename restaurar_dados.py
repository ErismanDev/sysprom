#!/usr/bin/env python
"""
Script para restaurar dados do backup do SEPROM
"""
import os
import django
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from militares.models import *

def conectar_banco():
    """Conecta ao banco de dados"""
    return psycopg2.connect(
        host="localhost",
        database="sepromcbmepi",
        user="postgres",
        password="11322361"
    )

def restaurar_usuarios():
    """Restaura usuários do backup"""
    print("Restaurando usuários...")
    conn = conectar_banco()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Buscar usuários no backup
        cur.execute("SELECT * FROM auth_user")
        usuarios = cur.fetchall()
        
        for usuario_data in usuarios:
            if not User.objects.filter(username=usuario_data['username']).exists():
                User.objects.create_user(
                    username=usuario_data['username'],
                    email=usuario_data['email'],
                    password='senha123',  # Senha padrão
                    first_name=usuario_data['first_name'],
                    last_name=usuario_data['last_name'],
                    is_staff=usuario_data['is_staff'],
                    is_superuser=usuario_data['is_superuser'],
                    is_active=usuario_data['is_active'],
                    date_joined=usuario_data['date_joined']
                )
                print(f"Usuário criado: {usuario_data['username']}")
        
        print(f"Total de usuários restaurados: {len(usuarios)}")
        
    except Exception as e:
        print(f"Erro ao restaurar usuários: {e}")
    finally:
        cur.close()
        conn.close()

def restaurar_militares():
    """Restaura militares do backup"""
    print("Restaurando militares...")
    conn = conectar_banco()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Buscar militares no backup
        cur.execute("SELECT * FROM militares_militar")
        militares = cur.fetchall()
        
        for militar_data in militares:
            if not Militar.objects.filter(id=militar_data['id']).exists():
                Militar.objects.create(
                    id=militar_data['id'],
                    nome=militar_data['nome'],
                    cpf=militar_data['cpf'],
                    rg=militar_data['rg'],
                    data_nascimento=militar_data['data_nascimento'],
                    posto=militar_data['posto'],
                    quadro=militar_data['quadro'],
                    data_ingresso=militar_data['data_ingresso'],
                    data_promocao_atual=militar_data['data_promocao_atual'],
                    apto_inspecao_saude=militar_data['apto_inspecao_saude'],
                    curso_superior=militar_data['curso_superior'],
                    curso_csbm=militar_data['curso_csbm'],
                    pos_graduacao=militar_data['pos_graduacao'],
                    curso_adaptacao_oficial=militar_data['curso_adaptacao_oficial'],
                    curso_formacao_oficial=militar_data['curso_formacao_oficial'],
                    curso_cho=militar_data['curso_cho'],
                    curso_cas=militar_data['curso_cas'],
                    curso_cfsd=militar_data['curso_cfsd'],
                    curso_chc=militar_data['curso_chc'],
                    curso_chsgt=militar_data['curso_chsgt'],
                    curso_formacao_pracas=militar_data['curso_formacao_pracas'],
                    nota_cho=militar_data['nota_cho'],
                    nota_chc=militar_data['nota_chc'],
                    foto=militar_data['foto'],
                    data_ultima_promocao_almanaque=militar_data['data_ultima_promocao_almanaque']
                )
                print(f"Militar criado: {militar_data['nome']}")
        
        print(f"Total de militares restaurados: {len(militares)}")
        
    except Exception as e:
        print(f"Erro ao restaurar militares: {e}")
    finally:
        cur.close()
        conn.close()

def main():
    """Função principal"""
    print("Iniciando restauração de dados...")
    
    # Restaurar dados básicos
    restaurar_usuarios()
    restaurar_militares()
    
    print("Restauração concluída!")

if __name__ == "__main__":
    main() 