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

def migrar_quadros_vagas():
    print("=== MIGRANDO QUADROS E VAGAS ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # 1. MIGRAR QUADROS DE ACESSO
        print(f"\n=== MIGRANDO QUADROS DE ACESSO ===")
        
        cursor_sqlite.execute("""
            SELECT 
                id,
                tipo,
                data_promocao,
                data_criacao,
                ativo,
                data_atualizacao,
                motivo_nao_elaboracao,
                observacoes,
                status,
                data_homologacao,
                homologado_por_id,
                categoria,
                numero
            FROM militares_quadroacesso
            ORDER BY id
        """)
        
        quadros_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de quadros de acesso encontrados: {len(quadros_sqlite)}")
        
        quadros_migrados = 0
        quadros_erro = 0
        
        for quadro in quadros_sqlite:
            (id_sqlite, tipo, data_promocao, data_criacao, ativo, data_atualizacao,
             motivo_nao_elaboracao, observacoes, status, data_homologacao, 
             homologado_por_id, categoria, numero) = quadro
            
            print(f"\n--- Migrando quadro ID SQLite: {id_sqlite} ---")
            print(f"   Tipo: {tipo}, Categoria: {categoria}, Número: {numero}")
            
            try:
                # Buscar usuário que homologou (se existir)
                homologado_por = None
                if homologado_por_id:
                    try:
                        homologado_por = User.objects.get(id=homologado_por_id)
                    except User.DoesNotExist:
                        print(f"   ⚠️ Usuário homologador {homologado_por_id} não encontrado")
                
                # Verificar se já existe
                try:
                    quadro_existente = QuadroAcesso.objects.get(id=id_sqlite)
                    print(f"   ⚠️ Quadro já existe (ID: {quadro_existente.id})")
                    # Atualizar dados
                    quadro_existente.numero = numero or ''
                    quadro_existente.tipo = tipo or 'ANTIGUIDADE'
                    quadro_existente.categoria = categoria or 'PRACAS'
                    if data_promocao:
                        quadro_existente.data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                    quadro_existente.status = status or 'RASCUNHO'
                    quadro_existente.motivo_nao_elaboracao = motivo_nao_elaboracao or ''
                    quadro_existente.observacoes = observacoes or ''
                    quadro_existente.homologado_por = homologado_por
                    quadro_existente.ativo = bool(ativo)
                    if data_homologacao:
                        quadro_existente.data_homologacao = datetime.strptime(data_homologacao, '%Y-%m-%d').date()
                    quadro_existente.save()
                    print(f"   ✅ Quadro atualizado")
                    
                except QuadroAcesso.DoesNotExist:
                    # Criar novo quadro
                    novo_quadro = QuadroAcesso(
                        id=id_sqlite,
                        numero=numero or '',
                        tipo=tipo or 'ANTIGUIDADE',
                        categoria=categoria or 'PRACAS',
                        status=status or 'RASCUNHO',
                        motivo_nao_elaboracao=motivo_nao_elaboracao or '',
                        observacoes=observacoes or '',
                        homologado_por=homologado_por,
                        ativo=bool(ativo)
                    )
                    
                    if data_promocao:
                        novo_quadro.data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                    if data_homologacao:
                        novo_quadro.data_homologacao = datetime.strptime(data_homologacao, '%Y-%m-%d').date()
                    
                    novo_quadro.save()
                    print(f"   ✅ Quadro criado (ID: {novo_quadro.id})")
                
                quadros_migrados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao migrar quadro: {e}")
                quadros_erro += 1
        
        print(f"\nQuadros de acesso migrados: {quadros_migrados}")
        print(f"Erros: {quadros_erro}")
        
        # 2. MIGRAR VAGAS
        print(f"\n=== MIGRANDO VAGAS ===")
        
        cursor_sqlite.execute("""
            SELECT 
                id,
                quadro,
                efetivo_atual,
                efetivo_maximo,
                data_atualizacao,
                posto
            FROM militares_vaga
            ORDER BY id
        """)
        
        vagas_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de vagas encontradas: {len(vagas_sqlite)}")
        
        vagas_migradas = 0
        vagas_erro = 0
        
        for vaga in vagas_sqlite:
            (id_sqlite, quadro, efetivo_atual, efetivo_maximo, data_atualizacao, posto) = vaga
            
            print(f"\n--- Migrando vaga ID SQLite: {id_sqlite} ---")
            print(f"   Quadro: {quadro}, Posto: {posto}, Efetivo: {efetivo_atual}/{efetivo_maximo}")
            
            try:
                # Verificar se já existe
                try:
                    vaga_existente = Vaga.objects.get(id=id_sqlite)
                    print(f"   ⚠️ Vaga já existe (ID: {vaga_existente.id})")
                    # Atualizar dados
                    vaga_existente.posto = posto or ''
                    vaga_existente.quadro = quadro or ''
                    vaga_existente.efetivo_atual = efetivo_atual or 0
                    vaga_existente.efetivo_maximo = efetivo_maximo or 0
                    vaga_existente.save()
                    print(f"   ✅ Vaga atualizada")
                    
                except Vaga.DoesNotExist:
                    # Criar nova vaga
                    nova_vaga = Vaga(
                        id=id_sqlite,
                        posto=posto or '',
                        quadro=quadro or '',
                        efetivo_atual=efetivo_atual or 0,
                        efetivo_maximo=efetivo_maximo or 0
                    )
                    
                    nova_vaga.save()
                    print(f"   ✅ Vaga criada (ID: {nova_vaga.id})")
                
                vagas_migradas += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao migrar vaga: {e}")
                vagas_erro += 1
        
        print(f"\nVagas migradas: {vagas_migradas}")
        print(f"Erros: {vagas_erro}")
        
        # 3. MIGRAR QUADROS DE FIXAÇÃO DE VAGAS
        print(f"\n=== MIGRANDO QUADROS DE FIXAÇÃO DE VAGAS ===")
        
        cursor_sqlite.execute("""
            SELECT 
                id,
                titulo,
                tipo,
                data_criacao,
                data_promocao,
                status,
                observacoes,
                data_registro,
                data_atualizacao,
                criado_por_id,
                numero
            FROM militares_quadrofixacaovagas
            ORDER BY id
        """)
        
        quadros_fixacao_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de quadros de fixação encontrados: {len(quadros_fixacao_sqlite)}")
        
        quadros_fixacao_migrados = 0
        quadros_fixacao_erro = 0
        
        for quadro_fixacao in quadros_fixacao_sqlite:
            (id_sqlite, titulo, tipo, data_criacao, data_promocao, status,
             observacoes, data_registro, data_atualizacao, criado_por_id, numero) = quadro_fixacao
            
            print(f"\n--- Migrando quadro de fixação ID SQLite: {id_sqlite} ---")
            print(f"   Título: {titulo}, Tipo: {tipo}, Número: {numero}")
            
            try:
                # Buscar usuário que criou
                criado_por = None
                if criado_por_id:
                    try:
                        criado_por = User.objects.get(id=criado_por_id)
                    except User.DoesNotExist:
                        print(f"   ⚠️ Usuário criador {criado_por_id} não encontrado")
                
                # Verificar se já existe
                try:
                    quadro_fixacao_existente = QuadroFixacaoVagas.objects.get(id=id_sqlite)
                    print(f"   ⚠️ Quadro de fixação já existe (ID: {quadro_fixacao_existente.id})")
                    # Atualizar dados
                    quadro_fixacao_existente.numero = numero or ''
                    quadro_fixacao_existente.titulo = titulo or ''
                    quadro_fixacao_existente.tipo = tipo or 'PRACAS'
                    if data_criacao:
                        quadro_fixacao_existente.data_criacao = datetime.strptime(data_criacao, '%Y-%m-%d').date()
                    if data_promocao:
                        quadro_fixacao_existente.data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                    quadro_fixacao_existente.status = status or 'RASCUNHO'
                    quadro_fixacao_existente.observacoes = observacoes or ''
                    quadro_fixacao_existente.criado_por = criado_por
                    quadro_fixacao_existente.save()
                    print(f"   ✅ Quadro de fixação atualizado")
                    
                except QuadroFixacaoVagas.DoesNotExist:
                    # Criar novo quadro de fixação
                    novo_quadro_fixacao = QuadroFixacaoVagas(
                        id=id_sqlite,
                        numero=numero or '',
                        titulo=titulo or '',
                        tipo=tipo or 'PRACAS',
                        status=status or 'RASCUNHO',
                        observacoes=observacoes or '',
                        criado_por=criado_por
                    )
                    
                    if data_criacao:
                        novo_quadro_fixacao.data_criacao = datetime.strptime(data_criacao, '%Y-%m-%d').date()
                    if data_promocao:
                        novo_quadro_fixacao.data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
                    
                    novo_quadro_fixacao.save()
                    print(f"   ✅ Quadro de fixação criado (ID: {novo_quadro_fixacao.id})")
                
                quadros_fixacao_migrados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao migrar quadro de fixação: {e}")
                quadros_fixacao_erro += 1
        
        print(f"\nQuadros de fixação migrados: {quadros_fixacao_migrados}")
        print(f"Erros: {quadros_fixacao_erro}")
        
        conn_sqlite.close()
        
        # Verificar resultado final
        print(f"\n=== RESULTADO FINAL ===")
        total_quadros = QuadroAcesso.objects.count()
        total_vagas = Vaga.objects.count()
        total_quadros_fixacao = QuadroFixacaoVagas.objects.count()
        print(f"Quadros de Acesso no PostgreSQL: {total_quadros}")
        print(f"Vagas no PostgreSQL: {total_vagas}")
        print(f"Quadros de Fixação no PostgreSQL: {total_quadros_fixacao}")
        
        # Mostrar detalhes dos quadros de acesso
        print(f"\n=== DETALHES DOS QUADROS DE ACESSO ===")
        for quadro in QuadroAcesso.objects.all():
            print(f"   • Quadro {quadro.id}: {quadro.tipo} - {quadro.categoria} - {quadro.status}")
        
        # Mostrar detalhes das vagas
        print(f"\n=== DETALHES DAS VAGAS ===")
        for vaga in Vaga.objects.all():
            print(f"   • Vaga {vaga.id}: {vaga.quadro} - {vaga.posto} - {vaga.efetivo_atual}/{vaga.efetivo_maximo}")
        
        # Mostrar detalhes dos quadros de fixação
        print(f"\n=== DETALHES DOS QUADROS DE FIXAÇÃO ===")
        for quadro in QuadroFixacaoVagas.objects.all():
            print(f"   • Quadro {quadro.id}: {quadro.titulo} - {quadro.tipo} - {quadro.status}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    migrar_quadros_vagas() 