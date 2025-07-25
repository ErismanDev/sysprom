#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime, date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def migrar_usuarios_funcoes():
    print("=== MIGRANDO USUÁRIOS COM FUNÇÕES ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Buscar funções de usuários do SQLite
        cursor_sqlite.execute("""
            SELECT 
                uf.id,
                uf.usuario_id,
                uf.cargo_funcao_id,
                uf.tipo_funcao,
                uf.descricao,
                uf.status,
                uf.data_inicio,
                uf.data_fim,
                uf.observacoes,
                u.username,
                cf.nome as cargo_nome
            FROM militares_usuariofuncao uf
            LEFT JOIN auth_user u ON uf.usuario_id = u.id
            LEFT JOIN militares_cargofuncao cf ON uf.cargo_funcao_id = cf.id
            ORDER BY uf.id
        """)
        
        funcoes_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de funções encontradas no SQLite: {len(funcoes_sqlite)}")
        
        if len(funcoes_sqlite) == 0:
            print("❌ Nenhuma função encontrada no SQLite!")
            return
        
        print("\n=== CRIANDO FUNÇÕES ===")
        
        funcoes_adicionadas = 0
        funcoes_erro = 0
        
        for funcao in funcoes_sqlite:
            (id_sqlite, usuario_id, cargo_funcao_id, tipo_funcao, descricao, status,
             data_inicio, data_fim, observacoes, username, cargo_nome) = funcao
            
            print(f"\n--- Criando função ID SQLite: {id_sqlite} ---")
            print(f"   Usuário: {username} (ID: {usuario_id})")
            print(f"   Cargo/Função: {cargo_nome} (ID: {cargo_funcao_id})")
            print(f"   Tipo: {tipo_funcao}")
            print(f"   Status: {status}")
            
            try:
                # Buscar usuário por username
                try:
                    usuario = User.objects.get(username=username)
                except User.DoesNotExist:
                    print(f"   ❌ Usuário {username} não encontrado no PostgreSQL")
                    funcoes_erro += 1
                    continue
                
                # Buscar ou criar cargo/função
                try:
                    cargo_funcao = CargoFuncao.objects.get(nome=cargo_nome)
                    print(f"   ✅ Cargo/Função {cargo_nome} já existe no PostgreSQL")
                except CargoFuncao.DoesNotExist:
                    print(f"   ⚠️ Cargo/Função {cargo_nome} não encontrado, criando...")
                    try:
                        cargo_funcao = CargoFuncao.objects.create(
                            nome=cargo_nome,
                            descricao=f'Cargo migrado do SQLite: {cargo_nome}',
                            ativo=True,
                            ordem=1
                        )
                        print(f"   ✅ Cargo/Função {cargo_nome} criado")
                    except Exception as e:
                        print(f"   ❌ Erro ao criar cargo/função {cargo_nome}: {e}")
                        funcoes_erro += 1
                        continue
                
                # Verificar se já existe esta função para o usuário
                funcao_existente = UsuarioFuncao.objects.filter(
                    usuario=usuario,
                    cargo_funcao=cargo_funcao
                ).first()
                
                if funcao_existente:
                    print(f"   ⚠️ Função já existe no PostgreSQL (ID: {funcao_existente.id})")
                    # Atualizar dados
                    funcao_existente.tipo_funcao = tipo_funcao or 'ADMINISTRATIVO'
                    funcao_existente.descricao = descricao or ''
                    funcao_existente.status = status or 'ATIVO'
                    if data_inicio:
                        funcao_existente.data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                    else:
                        funcao_existente.data_inicio = date.today()
                    if data_fim:
                        funcao_existente.data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                    funcao_existente.observacoes = observacoes or ''
                    funcao_existente.save()
                    print(f"   ✅ Função atualizada")
                else:
                    # Criar nova função
                    nova_funcao = UsuarioFuncao(
                        usuario=usuario,
                        cargo_funcao=cargo_funcao,
                        tipo_funcao=tipo_funcao or 'ADMINISTRATIVO',
                        descricao=descricao or '',
                        status=status or 'ATIVO',
                        observacoes=observacoes or ''
                    )
                    
                    if data_inicio:
                        nova_funcao.data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                    else:
                        nova_funcao.data_inicio = date.today()
                    
                    if data_fim:
                        nova_funcao.data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
                    
                    nova_funcao.save()
                    print(f"   ✅ Função criada (ID: {nova_funcao.id})")
                
                funcoes_adicionadas += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao adicionar: {e}")
                funcoes_erro += 1
        
        conn_sqlite.close()
        
        print(f"\n=== RESUMO ===")
        print(f"Funções adicionadas: {funcoes_adicionadas}")
        print(f"Erros: {funcoes_erro}")
        print(f"Total processado: {len(funcoes_sqlite)}")
        
        # Verificar resultado final
        total_final = UsuarioFuncao.objects.count()
        print(f"\nTotal de funções no PostgreSQL: {total_final}")
        
        # Mostrar algumas estatísticas
        print(f"\n=== ESTATÍSTICAS ===")
        usuarios_com_funcoes = User.objects.filter(funcoes__isnull=False).distinct().count()
        print(f"Usuários com funções: {usuarios_com_funcoes}")
        
        cargos_unicos = CargoFuncao.objects.count()
        print(f"Cargos/Funções únicos: {cargos_unicos}")
        
        funcoes_ativas = UsuarioFuncao.objects.filter(status='ATIVO').count()
        print(f"Funções ativas: {funcoes_ativas}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    migrar_usuarios_funcoes() 