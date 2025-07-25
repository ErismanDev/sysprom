#!/usr/bin/env python
import os
import sys
import django
import sqlite3
from datetime import datetime, date
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def migrar_militares_completo():
    print("=== MIGRANDO MILITARES COMPLETO ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Buscar todos os militares do SQLite
        cursor_sqlite.execute("""
            SELECT 
                m.id,
                m.numeracao_antiguidade,
                m.matricula,
                m.nome_completo,
                m.nome_guerra,
                m.cpf,
                m.rg,
                m.orgao_expedidor,
                m.data_nascimento,
                m.sexo,
                m.quadro,
                m.posto_graduacao,
                m.data_ingresso,
                m.data_promocao_atual,
                m.situacao,
                m.email,
                m.telefone,
                m.celular,
                m.foto,
                m.observacoes,
                m.curso_formacao_oficial,
                m.curso_aperfeicoamento_oficial,
                m.curso_cho,
                m.nota_cho,
                m.curso_superior,
                m.pos_graduacao,
                m.curso_csbm,
                m.curso_adaptacao_oficial,
                m.curso_cfsd,
                m.curso_formacao_pracas,
                m.curso_chc,
                m.nota_chc,
                m.curso_chsgt,
                m.nota_chsgt,
                m.curso_cas,
                m.apto_inspecao_saude,
                m.data_inspecao_saude,
                m.data_validade_inspecao_saude,
                m.numeracao_antiguidade_anterior,
                m.user_id,
                u.username
            FROM militares_militar m
            LEFT JOIN auth_user u ON m.user_id = u.id
            ORDER BY m.id
        """)
        
        militares_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de militares encontrados no SQLite: {len(militares_sqlite)}")
        
        if len(militares_sqlite) == 0:
            print("❌ Nenhum militar encontrado no SQLite!")
            return
        
        print("\n=== CRIANDO MILITARES ===")
        
        militares_adicionados = 0
        militares_erro = 0
        
        for militar in militares_sqlite:
            (id_sqlite, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg,
             orgao_expedidor, data_nascimento, sexo, quadro, posto_graduacao, data_ingresso,
             data_promocao_atual, situacao, email, telefone, celular, foto, observacoes,
             curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho,
             curso_superior, pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd,
             curso_formacao_pracas, curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas,
             apto_inspecao_saude, data_inspecao_saude, data_validade_inspecao_saude,
             numeracao_antiguidade_anterior, user_id, username) = militar
            
            print(f"\n--- Criando militar ID SQLite: {id_sqlite} ---")
            print(f"   Nome: {nome_completo} ({nome_guerra})")
            print(f"   CPF: {cpf}")
            print(f"   Posto: {posto_graduacao}")
            print(f"   Usuário: {username}")
            
            try:
                # Buscar usuário por username
                try:
                    usuario = User.objects.get(username=username)
                except User.DoesNotExist:
                    print(f"   ❌ Usuário {username} não encontrado no PostgreSQL")
                    militares_erro += 1
                    continue
                
                # Verificar se já existe militar com este CPF
                try:
                    militar_existente = Militar.objects.get(cpf=cpf)
                    print(f"   ⚠️ Militar {nome_guerra} já existe no PostgreSQL (ID: {militar_existente.id})")
                    # Atualizar dados do militar existente
                    militar_existente.numeracao_antiguidade = numeracao_antiguidade
                    militar_existente.matricula = matricula or f"MIG{cpf.replace('.', '').replace('-', '')[-6:]}"
                    militar_existente.nome_completo = nome_completo or ''
                    militar_existente.nome_guerra = nome_guerra or ''
                    militar_existente.rg = rg or '1234567'
                    militar_existente.orgao_expedidor = orgao_expedidor or 'SSP'
                    militar_existente.sexo = sexo or 'M'
                    militar_existente.quadro = quadro or 'COMB'
                    militar_existente.posto_graduacao = posto_graduacao or ''
                    militar_existente.situacao = situacao or 'AT'
                    militar_existente.email = email or f'{nome_guerra.lower()}@cbmepi.gov.br'
                    militar_existente.telefone = telefone or '(86) 99999-9999'
                    militar_existente.celular = celular or '(86) 99999-9999'
                    militar_existente.observacoes = observacoes or ''
                    militar_existente.user = usuario
                    
                    # Campos de cursos
                    militar_existente.curso_formacao_oficial = bool(curso_formacao_oficial)
                    militar_existente.curso_aperfeicoamento_oficial = bool(curso_aperfeicoamento_oficial)
                    militar_existente.curso_cho = bool(curso_cho)
                    militar_existente.nota_cho = nota_cho
                    militar_existente.curso_superior = bool(curso_superior)
                    militar_existente.pos_graduacao = bool(pos_graduacao)
                    militar_existente.curso_csbm = bool(curso_csbm)
                    militar_existente.curso_adaptacao_oficial = bool(curso_adaptacao_oficial)
                    militar_existente.curso_cfsd = bool(curso_cfsd)
                    militar_existente.curso_formacao_pracas = bool(curso_formacao_pracas)
                    militar_existente.curso_chc = bool(curso_chc)
                    militar_existente.nota_chc = nota_chc
                    militar_existente.curso_chsgt = bool(curso_chsgt)
                    militar_existente.nota_chsgt = nota_chsgt
                    militar_existente.curso_cas = bool(curso_cas)
                    militar_existente.apto_inspecao_saude = bool(apto_inspecao_saude)
                    militar_existente.numeracao_antiguidade_anterior = numeracao_antiguidade_anterior
                    
                    # Datas
                    if data_nascimento:
                        militar_existente.data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
                    if data_ingresso:
                        militar_existente.data_ingresso = datetime.strptime(data_ingresso, '%Y-%m-%d').date()
                    if data_promocao_atual:
                        militar_existente.data_promocao_atual = datetime.strptime(data_promocao_atual, '%Y-%m-%d').date()
                    if data_inspecao_saude:
                        militar_existente.data_inspecao_saude = datetime.strptime(data_inspecao_saude, '%Y-%m-%d').date()
                    if data_validade_inspecao_saude:
                        militar_existente.data_validade_inspecao_saude = datetime.strptime(data_validade_inspecao_saude, '%Y-%m-%d').date()
                    
                    militar_existente.save()
                    print(f"   ✅ Militar atualizado")
                    
                except Militar.DoesNotExist:
                    # Criar novo militar
                    try:
                        novo_militar = Militar(
                            numeracao_antiguidade=numeracao_antiguidade,
                            matricula=matricula or f"MIG{cpf.replace('.', '').replace('-', '')[-6:]}",
                            nome_completo=nome_completo or '',
                            nome_guerra=nome_guerra or '',
                            cpf=cpf,
                            rg=rg or '1234567',
                            orgao_expedidor=orgao_expedidor or 'SSP',
                            sexo=sexo or 'M',
                            quadro=quadro or 'COMB',
                            posto_graduacao=posto_graduacao or '',
                            situacao=situacao or 'AT',
                            email=email or f'{nome_guerra.lower()}@cbmepi.gov.br',
                            telefone=telefone or '(86) 99999-9999',
                            celular=celular or '(86) 99999-9999',
                            observacoes=observacoes or '',
                            user=usuario,
                            # Campos de cursos
                            curso_formacao_oficial=bool(curso_formacao_oficial),
                            curso_aperfeicoamento_oficial=bool(curso_aperfeicoamento_oficial),
                            curso_cho=bool(curso_cho),
                            nota_cho=nota_cho,
                            curso_superior=bool(curso_superior),
                            pos_graduacao=bool(pos_graduacao),
                            curso_csbm=bool(curso_csbm),
                            curso_adaptacao_oficial=bool(curso_adaptacao_oficial),
                            curso_cfsd=bool(curso_cfsd),
                            curso_formacao_pracas=bool(curso_formacao_pracas),
                            curso_chc=bool(curso_chc),
                            nota_chc=nota_chc,
                            curso_chsgt=bool(curso_chsgt),
                            nota_chsgt=nota_chsgt,
                            curso_cas=bool(curso_cas),
                            apto_inspecao_saude=bool(apto_inspecao_saude),
                            numeracao_antiguidade_anterior=numeracao_antiguidade_anterior
                        )
                        
                        # Datas
                        if data_nascimento:
                            novo_militar.data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
                        else:
                            novo_militar.data_nascimento = date(1980, 1, 1)
                        
                        if data_ingresso:
                            novo_militar.data_ingresso = datetime.strptime(data_ingresso, '%Y-%m-%d').date()
                        else:
                            novo_militar.data_ingresso = date(2020, 1, 1)
                        
                        if data_promocao_atual:
                            novo_militar.data_promocao_atual = datetime.strptime(data_promocao_atual, '%Y-%m-%d').date()
                        else:
                            novo_militar.data_promocao_atual = date(2020, 1, 1)
                        
                        if data_inspecao_saude:
                            novo_militar.data_inspecao_saude = datetime.strptime(data_inspecao_saude, '%Y-%m-%d').date()
                        
                        if data_validade_inspecao_saude:
                            novo_militar.data_validade_inspecao_saude = datetime.strptime(data_validade_inspecao_saude, '%Y-%m-%d').date()
                        
                        novo_militar.save()
                        print(f"   ✅ Militar criado (ID: {novo_militar.id})")
                        
                    except Exception as e:
                        print(f"   ❌ Erro ao criar militar {nome_guerra}: {e}")
                        militares_erro += 1
                        continue
                
                militares_adicionados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao processar militar: {e}")
                militares_erro += 1
        
        conn_sqlite.close()
        
        print(f"\n=== RESUMO ===")
        print(f"Militares adicionados: {militares_adicionados}")
        print(f"Erros: {militares_erro}")
        print(f"Total processado: {len(militares_sqlite)}")
        
        # Verificar resultado final
        total_final = Militar.objects.count()
        print(f"\nTotal de militares no PostgreSQL: {total_final}")
        
        # Mostrar algumas estatísticas
        print(f"\n=== ESTATÍSTICAS ===")
        militares_ativos = Militar.objects.filter(situacao='AT').count()
        print(f"Militares ativos: {militares_ativos}")
        
        militares_inativos = Militar.objects.filter(situacao='IN').count()
        print(f"Militares inativos: {militares_inativos}")
        
        oficiais = Militar.objects.filter(quadro__in=['COMB', 'SAUDE', 'ENG', 'COMP']).count()
        print(f"Oficiais: {oficiais}")
        
        pracas = Militar.objects.filter(quadro='PRACAS').count()
        print(f"Praças: {pracas}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    migrar_militares_completo() 