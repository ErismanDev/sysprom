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

def migrar_sessoes_votos_final():
    print("=== MIGRANDO SESSÕES E VOTOS (FINAL) ===\n")
    
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
                numero,
                tipo,
                data_sessao,
                hora_inicio,
                hora_fim,
                local,
                pauta,
                status,
                observacoes,
                data_registro,
                comissao_id
            FROM militares_sessaocomissao
            ORDER BY id
        """)
        
        sessoes_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de sessões encontradas: {len(sessoes_sqlite)}")
        
        sessoes_migradas = 0
        sessoes_erro = 0
        
        for sessao in sessoes_sqlite:
            (id_sqlite, numero, tipo, data_sessao, hora_inicio, hora_fim, 
             local, pauta, status, observacoes, data_registro, comissao_id) = sessao
            
            print(f"\n--- Migrando sessão ID SQLite: {id_sqlite} ---")
            print(f"   Número: {numero}, Tipo: {tipo}, Local: {local}")
            
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
                    sessao_existente.numero = numero
                    sessao_existente.tipo = tipo or 'ORDINARIA'
                    if data_sessao:
                        sessao_existente.data_sessao = datetime.strptime(data_sessao, '%Y-%m-%d').date()
                    sessao_existente.hora_inicio = hora_inicio
                    sessao_existente.hora_fim = hora_fim
                    sessao_existente.local = local or ''
                    sessao_existente.pauta = pauta or ''
                    sessao_existente.status = status or 'AGENDADA'
                    sessao_existente.observacoes = observacoes or ''
                    sessao_existente.save()
                    print(f"   ✅ Sessão atualizada")
                    
                except SessaoComissao.DoesNotExist:
                    # Criar nova sessão
                    nova_sessao = SessaoComissao(
                        id=id_sqlite,
                        comissao=comissao,
                        numero=numero,
                        tipo=tipo or 'ORDINARIA',
                        hora_inicio=hora_inicio,
                        hora_fim=hora_fim,
                        local=local or '',
                        pauta=pauta or '',
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
                voto,
                justificativa,
                data_registro,
                deliberacao_id,
                membro_id,
                voto_proferido,
                assinado,
                data_assinatura,
                funcao_assinatura,
                observacoes_assinatura,
                tipo_assinatura
            FROM militares_votodeliberacao
            ORDER BY id
        """)
        
        votos_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de votos encontrados: {len(votos_sqlite)}")
        
        votos_migrados = 0
        votos_erro = 0
        
        for voto in votos_sqlite:
            (id_sqlite, voto_valor, justificativa, data_registro, deliberacao_id, 
             membro_id, voto_proferido, assinado, data_assinatura, funcao_assinatura, 
             observacoes_assinatura, tipo_assinatura) = voto
            
            print(f"\n--- Migrando voto ID SQLite: {id_sqlite} ---")
            print(f"   Voto: {voto_valor}, Membro: {membro_id}, Deliberação: {deliberacao_id}")
            
            try:
                # Buscar membro votante
                try:
                    membro_votante = MembroComissao.objects.get(id=membro_id)
                except MembroComissao.DoesNotExist:
                    print(f"   ❌ Membro votante {membro_id} não encontrado")
                    votos_erro += 1
                    continue
                
                # Buscar sessão (usando deliberacao_id como sessao_id)
                try:
                    sessao = SessaoComissao.objects.get(id=deliberacao_id)
                except SessaoComissao.DoesNotExist:
                    print(f"   ❌ Sessão {deliberacao_id} não encontrada")
                    votos_erro += 1
                    continue
                
                # Verificar se já existe
                try:
                    voto_existente = VotoDeliberacao.objects.get(id=id_sqlite)
                    print(f"   ⚠️ Voto já existe (ID: {voto_existente.id})")
                    # Atualizar dados
                    voto_existente.deliberacao = sessao
                    voto_existente.membro = membro_votante
                    voto_existente.voto = voto_valor or 'ABSTENCAO'
                    voto_existente.justificativa = justificativa or ''
                    voto_existente.voto_proferido = voto_proferido or ''
                    voto_existente.assinado = bool(assinado)
                    voto_existente.funcao_assinatura = funcao_assinatura or ''
                    voto_existente.observacoes_assinatura = observacoes_assinatura or ''
                    voto_existente.tipo_assinatura = tipo_assinatura or 'VOTO'
                    if data_assinatura:
                        voto_existente.data_assinatura = datetime.strptime(data_assinatura, '%Y-%m-%d %H:%M:%S.%f')
                    voto_existente.save()
                    print(f"   ✅ Voto atualizado")
                    
                except VotoDeliberacao.DoesNotExist:
                    # Criar novo voto
                    novo_voto = VotoDeliberacao(
                        id=id_sqlite,
                        deliberacao=sessao,
                        membro=membro_votante,
                        voto=voto_valor or 'ABSTENCAO',
                        justificativa=justificativa or '',
                        voto_proferido=voto_proferido or '',
                        assinado=bool(assinado),
                        funcao_assinatura=funcao_assinatura or '',
                        observacoes_assinatura=observacoes_assinatura or '',
                        tipo_assinatura=tipo_assinatura or 'VOTO'
                    )
                    
                    if data_assinatura:
                        novo_voto.data_assinatura = datetime.strptime(data_assinatura, '%Y-%m-%d %H:%M:%S.%f')
                    
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
            votos_sessao = VotoDeliberacao.objects.filter(deliberacao=sessao).count()
            print(f"   • Sessão {sessao.id}: {sessao.comissao.nome} - {votos_sessao} votos")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    migrar_sessoes_votos_final() 