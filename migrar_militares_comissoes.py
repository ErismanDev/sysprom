#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime, date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, ComissaoPromocao

def migrar_militares_comissoes():
    print("=== MIGRANDO MILITARES E COMISSÕES DO SQLITE ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # 1. MIGRAR COMISSÕES
        print("\n=== MIGRANDO COMISSÕES ===")
        
        cursor_sqlite.execute("SELECT id, nome, tipo, status, data_criacao FROM militares_comissaopromocao")
        comissoes_sqlite = cursor_sqlite.fetchall()
        
        print(f"Comissões encontradas no SQLite: {len(comissoes_sqlite)}")
        
        for comissao_data in comissoes_sqlite:
            (id_sqlite, nome, tipo, status, data_criacao) = comissao_data
            
            try:
                comissao = ComissaoPromocao.objects.create(
                    id=id_sqlite,
                    nome=nome,
                    tipo=tipo,
                    status=status,
                    data_criacao=datetime.strptime(data_criacao, '%Y-%m-%d').date() if data_criacao else date.today()
                )
                print(f"   ✅ Comissão criada: {nome}")
            except Exception as e:
                print(f"   ❌ Erro ao criar comissão {nome}: {e}")
        
        # 2. MIGRAR MILITARES
        print("\n=== MIGRANDO MILITARES ===")
        
        cursor_sqlite.execute("""
            SELECT id, nome_guerra, cpf, nome_completo, posto_graduacao, 
                   data_nascimento, user_id
            FROM militares_militar
        """)
        militares_sqlite = cursor_sqlite.fetchall()
        
        print(f"Militares encontrados no SQLite: {len(militares_sqlite)}")
        
        for militar_data in militares_sqlite:
            (id_sqlite, nome_guerra, cpf, nome_completo, posto_graduacao, 
             data_nascimento, user_id) = militar_data
            
            try:
                # Buscar usuário associado
                user = None
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        print(f"   ⚠️ Usuário ID {user_id} não encontrado para militar {nome_guerra}")
                
                militar = Militar.objects.create(
                    id=id_sqlite,
                    nome_guerra=nome_guerra,
                    cpf=cpf,
                    nome_completo=nome_completo or '',
                    posto_graduacao=posto_graduacao or '',
                    data_nascimento=datetime.strptime(data_nascimento, '%Y-%m-%d').date() if data_nascimento else None,
                    user=user
                )
                print(f"   ✅ Militar criado: {nome_guerra}")
            except Exception as e:
                print(f"   ❌ Erro ao criar militar {nome_guerra}: {e}")
        
        conn_sqlite.close()
        
        print(f"\n=== MIGRAÇÃO CONCLUÍDA ===")
        
        # Verificar resultados
        print(f"Militares no PostgreSQL: {Militar.objects.count()}")
        print(f"Comissões no PostgreSQL: {ComissaoPromocao.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    migrar_militares_comissoes() 