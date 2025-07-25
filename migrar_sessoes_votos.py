#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime, date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import *

def migrar_sessoes_votos():
    print("=== MIGRANDO SESSÕES E VOTOS ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # 1. MIGRAR SESSÕES DE COMISSÃO
        print(f"\n=== MIGRANDO SESSÕES DE COMISSÃO ===")
        
        cursor_sqlite.execute("""
            SELECT 
                id,
                comissao_id,
                data_sessao,
                hora_inicio,
                hora_fim,
                local,
                tipo_sessao,
                status,
                observacoes,
                data_criacao,
                data_atualizacao
            FROM militares_sessaocomissao
            ORDER BY id
        """)
        
        sessoes_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de sessões encontradas: {len(sessoes_sqlite)}")
        
        sessoes_migradas = 0
        sessoes_erro = 0
        
        for sessao in sessoes_sqlite:
            (id_sqlite, comissao_id, data_sessao, hora_inicio, hora_fim, 
             local, tipo_sessao, status, observacoes, data_criacao, data_atualizacao) = sessao
            
            print(f"\n--- Migrando sessão ID SQLite: {id_sqlite} ---")
            
            try:
                # Buscar comissão
                try:
                    comissao = ComissaoPromocao.objects.get(id=comissao_id)
                except ComissaoPromocao.DoesNotExist:
                    print(f"   ❌ Comissão {comissao_id} não encontrada")
                    sessoes_erro += 1
                    continue
                
                # Verificar se já existe
                try:
                    sessao_existente = SessaoComissao.objects.get(id=id_sqlite)
                    print(f"   ⚠️ Sessão já existe (ID: {sessao_existente.id})")
                    # Atualizar dados
                    sessao_existente.comissao = comissao
                    if data_sessao:
                        sessao_existente.data_sessao = datetime.strptime(data_sessao, '%Y-%m-%d').date()
                    sessao_existente.hora_inicio = hora_inicio
                    sessao_existente.hora_fim = hora_fim
                    sessao_existente.local = local or ''
                    sessao_existente.tipo_sessao = tipo_sessao or 'ORDINARIA'
                    sessao_existente.status = status or 'AGENDADA'
                    sessao_existente.observacoes = observacoes or ''
                    sessao_existente.save()
                    print(f"   ✅ Sessão atualizada")
                    
                except SessaoComissao.DoesNotExist:
                    # Criar nova sessão
                    nova_sessao = SessaoComissao(
                        id=id_sqlite,
                        comissao=comissao,
                        hora_inicio=hora_inicio,
                        hora_fim=hora_fim,
                        local=local or '',
                        tipo_sessao=tipo_sessao or 'ORDINARIA',
                        status=status or 'AGENDADA',
                        observacoes=observacoes or ''
                    )
                    
                    if data_sessao:
                        nova_sessao.data_sessao = datetime.strptime(data_sessao, '%Y-%m-%d').date()
                    
                    nova_sessao.save()
                    print(f"   ✅ Sessão criada (ID: {nova_sessao.id})")
                
                sessoes_migradas += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao migrar sessão: {e}")
                sessoes_erro += 1
        
        print(f"\nSessões migradas: {sessoes_migradas}")
        print(f"Erros: {sessoes_erro}")
        
        # 2. MIGRAR VOTOS
        print(f"\n=== MIGRANDO VOTOS ===")
        
        cursor_sqlite.execute("""
            SELECT 
                id,
                sessao_id,
                militar_id,
                membro_votante_id,
                voto,
                justificativa,
                data_voto,
                data_criacao,
                data_atualizacao
            FROM militares_votodeliberacao
            ORDER BY id
        """)
        
        votos_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de votos encontrados: {len(votos_sqlite)}")
        
        votos_migrados = 0
        votos_erro = 0
        
        for voto in votos_sqlite:
            (id_sqlite, sessao_id, militar_id, membro_votante_id, voto_valor, 
             justificativa, data_voto, data_criacao, data_atualizacao) = voto
            
            print(f"\n--- Migrando voto ID SQLite: {id_sqlite} ---")
            
            try:
                # Buscar sessão
                try:
                    sessao = SessaoComissao.objects.get(id=sessao_id)
                except SessaoComissao.DoesNotExist:
                    print(f"   ❌ Sessão {sessao_id} não encontrada")
                    votos_erro += 1
                    continue
                
                # Buscar militar
                try:
                    militar = Militar.objects.get(id=militar_id)
                except Militar.DoesNotExist:
                    print(f"   ❌ Militar {militar_id} não encontrado")
                    votos_erro += 1
                    continue
                
                # Buscar membro votante
                try:
                    membro_votante = MembroComissao.objects.get(id=membro_votante_id)
                except MembroComissao.DoesNotExist:
                    print(f"   ❌ Membro votante {membro_votante_id} não encontrado")
                    votos_erro += 1
                    continue
                
                # Verificar se já existe
                try:
                    voto_existente = VotoDeliberacao.objects.get(id=id_sqlite)
                    print(f"   ⚠️ Voto já existe (ID: {voto_existente.id})")
                    # Atualizar dados
                    voto_existente.sessao = sessao
                    voto_existente.militar = militar
                    voto_existente.membro_votante = membro_votante
                    voto_existente.voto = voto_valor or 'ABSTENCAO'
                    voto_existente.justificativa = justificativa or ''
                    if data_voto:
                        voto_existente.data_voto = datetime.strptime(data_voto, '%Y-%m-%d').date()
                    voto_existente.save()
                    print(f"   ✅ Voto atualizado")
                    
                except VotoDeliberacao.DoesNotExist:
                    # Criar novo voto
                    novo_voto = VotoDeliberacao(
                        id=id_sqlite,
                        sessao=sessao,
                        militar=militar,
                        membro_votante=membro_votante,
                        voto=voto_valor or 'ABSTENCAO',
                        justificativa=justificativa or ''
                    )
                    
                    if data_voto:
                        novo_voto.data_voto = datetime.strptime(data_voto, '%Y-%m-%d').date()
                    
                    novo_voto.save()
                    print(f"   ✅ Voto criado (ID: {novo_voto.id})")
                
                votos_migrados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao migrar voto: {e}")
                votos_erro += 1
        
        print(f"\nVotos migrados: {votos_migrados}")
        print(f"Erros: {votos_erro}")
        
        conn_sqlite.close()
        
        # Verificar resultado final
        print(f"\n=== RESULTADO FINAL ===")
        total_sessoes = SessaoComissao.objects.count()
        total_votos = VotoDeliberacao.objects.count()
        print(f"Sessões no PostgreSQL: {total_sessoes}")
        print(f"Votos no PostgreSQL: {total_votos}")
        
        # Mostrar detalhes das sessões
        print(f"\n=== DETALHES DAS SESSÕES ===")
        for sessao in SessaoComissao.objects.all():
            votos_sessao = VotoDeliberacao.objects.filter(sessao=sessao).count()
            print(f"   • Sessão {sessao.id}: {sessao.comissao.nome} - {votos_sessao} votos")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    migrar_sessoes_votos() 