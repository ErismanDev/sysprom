#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime, date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, Militar, ComissaoPromocao

def adicionar_membros_simples():
    print("=== ADICIONANDO MEMBROS DE COMISSÕES DO SQLITE ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Buscar membros do SQLite
        cursor_sqlite.execute("""
            SELECT 
                mc.id,
                mc.tipo,
                mc.data_nomeacao,
                mc.data_termino,
                mc.ativo,
                mc.observacoes,
                mc.comissao_id,
                mc.militar_id,
                mc.usuario_id,
                u.username,
                m.nome_guerra,
                m.cpf,
                c.nome as comissao_nome,
                c.tipo as comissao_tipo
            FROM militares_membrocomissao mc
            LEFT JOIN auth_user u ON mc.usuario_id = u.id
            LEFT JOIN militares_militar m ON mc.militar_id = m.id
            LEFT JOIN militares_comissaopromocao c ON mc.comissao_id = c.id
            ORDER BY mc.id
        """)
        
        membros_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de membros encontrados no SQLite: {len(membros_sqlite)}")
        
        if len(membros_sqlite) == 0:
            print("❌ Nenhum membro encontrado no SQLite!")
            return
        
        print("\n=== ADICIONANDO MEMBROS ===")
        
        membros_adicionados = 0
        membros_erro = 0
        
        for membro in membros_sqlite:
            (id_sqlite, tipo, data_nomeacao, data_termino, ativo, observacoes,
             comissao_id_sqlite, militar_id, usuario_id, username, nome_guerra, cpf, comissao_nome, comissao_tipo) = membro
            
            print(f"\n--- Adicionando membro ID SQLite: {id_sqlite} ---")
            print(f"   Usuário: {username} (ID: {usuario_id})")
            print(f"   Militar: {nome_guerra} ({cpf}) (ID: {militar_id})")
            print(f"   Comissão: {comissao_nome} ({comissao_tipo}) (SQLite ID: {comissao_id_sqlite})")
            print(f"   Ativo: {ativo}")
            
            try:
                # Buscar usuário por username
                try:
                    usuario = User.objects.get(username=username)
                except User.DoesNotExist:
                    print(f"   ❌ Usuário {username} não encontrado no PostgreSQL")
                    membros_erro += 1
                    continue
                
                # Buscar militar por CPF
                try:
                    militar = Militar.objects.get(cpf=cpf)
                except Militar.DoesNotExist:
                    print(f"   ❌ Militar {nome_guerra} (CPF: {cpf}) não encontrado no PostgreSQL")
                    membros_erro += 1
                    continue
                
                # Buscar comissão por nome e tipo
                try:
                    comissao = ComissaoPromocao.objects.get(nome=comissao_nome, tipo=comissao_tipo)
                except ComissaoPromocao.DoesNotExist:
                    print(f"   ❌ Comissão {comissao_nome} ({comissao_tipo}) não encontrada no PostgreSQL")
                    membros_erro += 1
                    continue
                
                # Verificar se já existe este membro
                membro_existente = MembroComissao.objects.filter(
                    usuario=usuario,
                    militar=militar,
                    comissao=comissao
                ).first()
                
                if membro_existente:
                    print(f"   ⚠️ Membro já existe no PostgreSQL (ID: {membro_existente.id})")
                    # Atualizar dados
                    membro_existente.ativo = bool(ativo)
                    if data_nomeacao:
                        membro_existente.data_inicio = datetime.strptime(data_nomeacao, '%Y-%m-%d').date()
                    if data_termino:
                        membro_existente.data_fim = datetime.strptime(data_termino, '%Y-%m-%d').date()
                    membro_existente.observacoes = observacoes or ''
                    membro_existente.save()
                    print(f"   ✅ Membro atualizado")
                else:
                    # Criar novo membro
                    novo_membro = MembroComissao(
                        usuario=usuario,
                        militar=militar,
                        comissao=comissao,
                        ativo=bool(ativo),
                        observacoes=observacoes or ''
                    )
                    
                    if data_nomeacao:
                        novo_membro.data_inicio = datetime.strptime(data_nomeacao, '%Y-%m-%d').date()
                    else:
                        novo_membro.data_inicio = date.today()
                    
                    if data_termino:
                        novo_membro.data_fim = datetime.strptime(data_termino, '%Y-%m-%d').date()
                    
                    novo_membro.save()
                    print(f"   ✅ Membro criado (ID: {novo_membro.id})")
                
                membros_adicionados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao adicionar: {e}")
                membros_erro += 1
        
        conn_sqlite.close()
        
        print(f"\n=== RESUMO ===")
        print(f"Membros adicionados: {membros_adicionados}")
        print(f"Erros: {membros_erro}")
        print(f"Total processado: {len(membros_sqlite)}")
        
        # Verificar resultado final
        total_final = MembroComissao.objects.count()
        print(f"\nTotal de membros no PostgreSQL: {total_final}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    adicionar_membros_simples() 