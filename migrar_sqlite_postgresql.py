#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime, date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection
from militares.models import MembroComissao, Militar, ComissaoPromocao, UsuarioFuncao, CargoFuncao

def migrar_sqlite_postgresql():
    print("=== MIGRANDO DADOS DO SQLITE PARA POSTGRESQL ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # 1. LIMPAR POSTGRESQL
        print("\n=== LIMPANDO POSTGRESQL ===")
        
        # Limpar tabelas na ordem correta (respeitando foreign keys)
        tabelas_para_limpar = [
            'militares_membrocomissao',
            'militares_usuariofuncao', 
            'militares_comissaopromocao',
            'militares_militar',
            'auth_user'
        ]
        
        with connection.cursor() as cursor:
            # Desabilitar foreign key checks temporariamente
            cursor.execute("SET session_replication_role = replica;")
            
            for tabela in tabelas_para_limpar:
                cursor.execute(f"DELETE FROM {tabela};")
                print(f"   ✅ Limpada tabela: {tabela}")
            
            # Reabilitar foreign key checks
            cursor.execute("SET session_replication_role = DEFAULT;")
        
        print("✅ PostgreSQL limpo")
        
        # 2. MIGRAR USUÁRIOS
        print("\n=== MIGRANDO USUÁRIOS ===")
        
        cursor_sqlite.execute("SELECT id, username, first_name, last_name, email, is_staff, is_superuser, is_active, date_joined FROM auth_user")
        usuarios_sqlite = cursor_sqlite.fetchall()
        
        print(f"Usuários encontrados no SQLite: {len(usuarios_sqlite)}")
        
        for usuario_data in usuarios_sqlite:
            (id_sqlite, username, first_name, last_name, email, is_staff, is_superuser, is_active, date_joined) = usuario_data
            
            try:
                # Criar usuário no PostgreSQL
                usuario = User.objects.create(
                    id=id_sqlite,
                    username=username,
                    first_name=first_name or '',
                    last_name=last_name or '',
                    email=email or '',
                    is_staff=bool(is_staff),
                    is_superuser=bool(is_superuser),
                    is_active=bool(is_active),
                    date_joined=datetime.fromisoformat(date_joined.replace('Z', '+00:00')) if date_joined else datetime.now()
                )
                print(f"   ✅ Usuário criado: {username}")
            except Exception as e:
                print(f"   ❌ Erro ao criar usuário {username}: {e}")
        
        # 3. MIGRAR CARGOS/FUNÇÕES
        print("\n=== MIGRANDO CARGOS/FUNÇÕES ===")
        
        cursor_sqlite.execute("SELECT id, nome, descricao FROM militares_cargofuncao")
        cargos_sqlite = cursor_sqlite.fetchall()
        
        print(f"Cargos encontrados no SQLite: {len(cargos_sqlite)}")
        
        for cargo_data in cargos_sqlite:
            (id_sqlite, nome, descricao) = cargo_data
            
            try:
                cargo = CargoFuncao.objects.create(
                    id=id_sqlite,
                    nome=nome,
                    descricao=descricao or ''
                )
                print(f"   ✅ Cargo criado: {nome}")
            except Exception as e:
                print(f"   ❌ Erro ao criar cargo {nome}: {e}")
        
        # 4. MIGRAR MILITARES
        print("\n=== MIGRANDO MILITARES ===")
        
        cursor_sqlite.execute("""
            SELECT id, nome_guerra, cpf, nome_completo, posto_graduacao, 
                   data_nascimento, data_incorporacao, user_id
            FROM militares_militar
        """)
        militares_sqlite = cursor_sqlite.fetchall()
        
        print(f"Militares encontrados no SQLite: {len(militares_sqlite)}")
        
        for militar_data in militares_sqlite:
            (id_sqlite, nome_guerra, cpf, nome_completo, posto_graduacao, 
             data_nascimento, data_incorporacao, user_id) = militar_data
            
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
                    data_incorporacao=datetime.strptime(data_incorporacao, '%Y-%m-%d').date() if data_incorporacao else None,
                    user=user
                )
                print(f"   ✅ Militar criado: {nome_guerra}")
            except Exception as e:
                print(f"   ❌ Erro ao criar militar {nome_guerra}: {e}")
        
        # 5. MIGRAR COMISSÕES
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
        
        # 6. MIGRAR FUNÇÕES DE USUÁRIOS
        print("\n=== MIGRANDO FUNÇÕES DE USUÁRIOS ===")
        
        cursor_sqlite.execute("""
            SELECT id, usuario_id, cargo_funcao_id, status, data_inicio, data_fim
            FROM militares_usuariofuncao
        """)
        funcoes_sqlite = cursor_sqlite.fetchall()
        
        print(f"Funções encontradas no SQLite: {len(funcoes_sqlite)}")
        
        for funcao_data in funcoes_sqlite:
            (id_sqlite, usuario_id, cargo_funcao_id, status, data_inicio, data_fim) = funcao_data
            
            try:
                # Buscar usuário e cargo
                usuario = User.objects.get(id=usuario_id)
                cargo = CargoFuncao.objects.get(id=cargo_funcao_id)
                
                funcao = UsuarioFuncao.objects.create(
                    id=id_sqlite,
                    usuario=usuario,
                    cargo_funcao=cargo,
                    status=status,
                    data_inicio=datetime.strptime(data_inicio, '%Y-%m-%d').date() if data_inicio else date.today(),
                    data_fim=datetime.strptime(data_fim, '%Y-%m-%d').date() if data_fim else None
                )
                print(f"   ✅ Função criada: {usuario.username} -> {cargo.nome}")
            except Exception as e:
                print(f"   ❌ Erro ao criar função: {e}")
        
        # 7. MIGRAR MEMBROS DE COMISSÕES
        print("\n=== MIGRANDO MEMBROS DE COMISSÕES ===")
        
        cursor_sqlite.execute("""
            SELECT id, tipo, data_nomeacao, data_termino, ativo, observacoes,
                   comissao_id, militar_id, usuario_id, cargo_id
            FROM militares_membrocomissao
        """)
        membros_sqlite = cursor_sqlite.fetchall()
        
        print(f"Membros encontrados no SQLite: {len(membros_sqlite)}")
        
        for membro_data in membros_sqlite:
            (id_sqlite, tipo, data_nomeacao, data_termino, ativo, observacoes,
             comissao_id, militar_id, usuario_id, cargo_id) = membro_data
            
            try:
                # Buscar comissão, militar e usuário
                comissao = ComissaoPromocao.objects.get(id=comissao_id)
                militar = Militar.objects.get(id=militar_id)
                usuario = User.objects.get(id=usuario_id)
                
                membro = MembroComissao.objects.create(
                    id=id_sqlite,
                    comissao=comissao,
                    militar=militar,
                    usuario=usuario,
                    ativo=bool(ativo),
                    observacoes=observacoes or '',
                    data_inicio=datetime.strptime(data_nomeacao, '%Y-%m-%d').date() if data_nomeacao else date.today(),
                    data_fim=datetime.strptime(data_termino, '%Y-%m-%d').date() if data_termino else None
                )
                print(f"   ✅ Membro criado: {usuario.username} -> {comissao.nome}")
            except Exception as e:
                print(f"   ❌ Erro ao criar membro: {e}")
        
        conn_sqlite.close()
        
        print(f"\n=== MIGRAÇÃO CONCLUÍDA ===")
        
        # Verificar resultados
        print(f"Usuários no PostgreSQL: {User.objects.count()}")
        print(f"Militares no PostgreSQL: {Militar.objects.count()}")
        print(f"Comissões no PostgreSQL: {ComissaoPromocao.objects.count()}")
        print(f"Funções no PostgreSQL: {UsuarioFuncao.objects.count()}")
        print(f"Membros no PostgreSQL: {MembroComissao.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    migrar_sqlite_postgresql() 