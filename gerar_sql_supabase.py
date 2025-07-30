#!/usr/bin/env python3
"""
Script para gerar comandos SQL para migração no Supabase
"""

import os
import sys
import django
import json
from datetime import datetime

def configurar_ambiente():
    """Configura o ambiente para acessar o banco local"""
    print("🌐 Configurando ambiente local...")
    
    # Configurar variáveis de ambiente para banco local
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sepromcbmepi.settings'
    
    try:
        django.setup()
        print("✅ Ambiente local configurado")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar ambiente: {e}")
        return False

def gerar_sql_usuarios():
    """Gera SQL para inserir usuários"""
    print("\n👥 Gerando SQL para usuários...")
    
    try:
        from django.contrib.auth.models import User
        from django.db import connection
        
        # Buscar todos os usuários
        usuarios = User.objects.all()
        
        sql_usuarios = []
        sql_usuarios.append("-- ========================================")
        sql_usuarios.append("-- INSERÇÃO DE USUÁRIOS")
        sql_usuarios.append("-- ========================================")
        sql_usuarios.append("")
        
        for usuario in usuarios:
            # Escapar aspas simples
            first_name = usuario.first_name.replace("'", "''") if usuario.first_name else ""
            last_name = usuario.last_name.replace("'", "''") if usuario.last_name else ""
            email = usuario.email.replace("'", "''") if usuario.email else ""
            username = usuario.username.replace("'", "''") if usuario.username else ""
            
            sql = f"""INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
VALUES ({usuario.id}, '{usuario.password}', {f"'{usuario.last_login.isoformat()}'" if usuario.last_login else 'NULL'}, {str(usuario.is_superuser).lower()}, '{username}', '{first_name}', '{last_name}', '{email}', {str(usuario.is_staff).lower()}, {str(usuario.is_active).lower()}, '{usuario.date_joined.isoformat()}');"""
            
            sql_usuarios.append(sql)
        
        # Resetar sequência
        sql_usuarios.append("")
        sql_usuarios.append("-- Resetar sequência")
        sql_usuarios.append("SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user));")
        
        return sql_usuarios
        
    except Exception as e:
        print(f"❌ Erro ao gerar SQL de usuários: {e}")
        return []

def gerar_sql_militares():
    """Gera SQL para inserir militares"""
    print("\n🎖️ Gerando SQL para militares...")
    
    try:
        from militares.models import Militar
        from django.db import connection
        
        # Buscar todos os militares
        militares = Militar.objects.all()
        
        sql_militares = []
        sql_militares.append("-- ========================================")
        sql_militares.append("-- INSERÇÃO DE MILITARES")
        sql_militares.append("-- ========================================")
        sql_militares.append("")
        
        for militar in militares:
            # Escapar aspas simples
            nome_completo = militar.nome_completo.replace("'", "''") if militar.nome_completo else ""
            nome_guerra = militar.nome_guerra.replace("'", "''") if militar.nome_guerra else ""
            cpf = militar.cpf.replace("'", "''") if militar.cpf else ""
            rg = militar.rg.replace("'", "''") if militar.rg else ""
            orgao_expedidor = militar.orgao_expedidor.replace("'", "''") if militar.orgao_expedidor else ""
            email = militar.email.replace("'", "''") if militar.email else ""
            telefone = militar.telefone.replace("'", "''") if militar.telefone else ""
            celular = militar.celular.replace("'", "''") if militar.celular else ""
            observacoes = militar.observacoes.replace("'", "''") if militar.observacoes else ""
            
            # Tratar campos de data
            data_nascimento = f"'{militar.data_nascimento.isoformat()}'" if militar.data_nascimento else 'NULL'
            data_ingresso = f"'{militar.data_ingresso.isoformat()}'" if militar.data_ingresso else 'NULL'
            data_promocao_atual = f"'{militar.data_promocao_atual.isoformat()}'" if militar.data_promocao_atual else 'NULL'
            data_cadastro = f"'{militar.data_cadastro.isoformat()}'" if militar.data_cadastro else 'NULL'
            data_atualizacao = f"'{militar.data_atualizacao.isoformat()}'" if militar.data_atualizacao else 'NULL'
            
            # Tratar campos opcionais
            numeracao_antiguidade = str(militar.numeracao_antiguidade) if militar.numeracao_antiguidade else 'NULL'
            numeracao_antiguidade_anterior = str(militar.numeracao_antiguidade_anterior) if militar.numeracao_antiguidade_anterior else 'NULL'
            nota_cho = str(militar.nota_cho) if militar.nota_cho else 'NULL'
            nota_chc = str(militar.nota_chc) if militar.nota_chc else 'NULL'
            nota_chsgt = str(militar.nota_chsgt) if militar.nota_chsgt else 'NULL'
            data_inspecao_saude = f"'{militar.data_inspecao_saude.isoformat()}'" if militar.data_inspecao_saude else 'NULL'
            data_validade_inspecao_saude = f"'{militar.data_validade_inspecao_saude.isoformat()}'" if militar.data_validade_inspecao_saude else 'NULL'
            user_id = str(militar.user.id) if militar.user else 'NULL'
            
            sql = f"""INSERT INTO militares_militar (
    id, numeracao_antiguidade, matricula, nome_completo, nome_guerra, cpf, rg, orgao_expedidor, 
    data_nascimento, sexo, quadro, posto_graduacao, data_ingresso, data_promocao_atual, situacao, 
    email, telefone, celular, foto, data_cadastro, data_atualizacao, observacoes, 
    curso_formacao_oficial, curso_aperfeicoamento_oficial, curso_cho, nota_cho, curso_superior, 
    pos_graduacao, curso_csbm, curso_adaptacao_oficial, curso_cfsd, curso_formacao_pracas, 
    curso_chc, nota_chc, curso_chsgt, nota_chsgt, curso_cas, apto_inspecao_saude, 
    data_inspecao_saude, data_validade_inspecao_saude, numeracao_antiguidade_anterior, user_id
) VALUES (
    {militar.id}, {numeracao_antiguidade}, '{militar.matricula}', '{nome_completo}', '{nome_guerra}', 
    '{cpf}', '{rg}', '{orgao_expedidor}', {data_nascimento}, '{militar.sexo}', '{militar.quadro}', 
    '{militar.posto_graduacao}', {data_ingresso}, {data_promocao_atual}, '{militar.situacao}', 
    '{email}', '{telefone}', '{celular}', {f"'{militar.foto}'" if militar.foto else 'NULL'}, 
    {data_cadastro}, {data_atualizacao}, {f"'{observacoes}'" if observacoes else 'NULL'}, 
    {str(militar.curso_formacao_oficial).lower()}, {str(militar.curso_aperfeicoamento_oficial).lower()}, 
    {str(militar.curso_cho).lower()}, {nota_cho}, {str(militar.curso_superior).lower()}, 
    {str(militar.pos_graduacao).lower()}, {str(militar.curso_csbm).lower()}, 
    {str(militar.curso_adaptacao_oficial).lower()}, {str(militar.curso_cfsd).lower()}, 
    {str(militar.curso_formacao_pracas).lower()}, {str(militar.curso_chc).lower()}, {nota_chc}, 
    {str(militar.curso_chsgt).lower()}, {nota_chsgt}, {str(militar.curso_cas).lower()}, 
    {str(militar.apto_inspecao_saude).lower()}, {data_inspecao_saude}, {data_validade_inspecao_saude}, 
    {numeracao_antiguidade_anterior}, {user_id}
);"""
            
            sql_militares.append(sql)
        
        # Resetar sequência
        sql_militares.append("")
        sql_militares.append("-- Resetar sequência")
        sql_militares.append("SELECT setval('militares_militar_id_seq', (SELECT MAX(id) FROM militares_militar));")
        
        return sql_militares
        
    except Exception as e:
        print(f"❌ Erro ao gerar SQL de militares: {e}")
        return []

def gerar_sql_outros_modelos():
    """Gera SQL para outros modelos importantes"""
    print("\n📋 Gerando SQL para outros modelos...")
    
    try:
        from militares.models import ComissaoPromocao, QuadroAcesso, CargoComissao
        from django.db import connection
        
        sql_outros = []
        sql_outros.append("-- ========================================")
        sql_outros.append("-- OUTROS MODELOS")
        sql_outros.append("-- ========================================")
        sql_outros.append("")
        
        # Cargos da Comissão
        cargos = CargoComissao.objects.all()
        if cargos.exists():
            sql_outros.append("-- Cargos da Comissão")
            for cargo in cargos:
                nome = cargo.nome.replace("'", "''") if cargo.nome else ""
                codigo = cargo.codigo.replace("'", "''") if cargo.codigo else ""
                descricao = cargo.descricao.replace("'", "''") if cargo.descricao else ""
                
                sql = f"""INSERT INTO militares_cargocomissao (id, nome, codigo, descricao, ativo, ordem, data_criacao, data_atualizacao) 
VALUES ({cargo.id}, '{nome}', '{codigo}', {f"'{descricao}'" if descricao else 'NULL'}, {str(cargo.ativo).lower()}, {cargo.ordem}, '{cargo.data_criacao.isoformat()}', '{cargo.data_atualizacao.isoformat()}');"""
                sql_outros.append(sql)
            sql_outros.append("")
        
        # Comissões de Promoção
        comissoes = ComissaoPromocao.objects.all()
        if comissoes.exists():
            sql_outros.append("-- Comissões de Promoção")
            for comissao in comissoes:
                nome = comissao.nome.replace("'", "''") if comissao.nome else ""
                descricao = comissao.descricao.replace("'", "''") if comissao.descricao else ""
                observacoes = comissao.observacoes.replace("'", "''") if comissao.observacoes else ""
                
                sql = f"""INSERT INTO militares_comissaopromocao (id, nome, descricao, data_inicio, data_fim, ativo, observacoes, data_criacao, data_atualizacao) 
VALUES ({comissao.id}, '{nome}', {f"'{descricao}'" if descricao else 'NULL'}, '{comissao.data_inicio.isoformat()}', {f"'{comissao.data_fim.isoformat()}'" if comissao.data_fim else 'NULL'}, {str(comissao.ativo).lower()}, {f"'{observacoes}'" if observacoes else 'NULL'}, '{comissao.data_criacao.isoformat()}', '{comissao.data_atualizacao.isoformat()}');"""
                sql_outros.append(sql)
            sql_outros.append("")
        
        # Quadros de Acesso
        quadros = QuadroAcesso.objects.all()
        if quadros.exists():
            sql_outros.append("-- Quadros de Acesso")
            for quadro in quadros:
                numero = quadro.numero.replace("'", "''") if quadro.numero else ""
                observacoes = quadro.observacoes.replace("'", "''") if quadro.observacoes else ""
                motivo_nao_elaboracao = quadro.motivo_nao_elaboracao.replace("'", "''") if quadro.motivo_nao_elaboracao else ""
                
                sql = f"""INSERT INTO militares_quadroacesso (id, numero, tipo, categoria, data_promocao, status, motivo_nao_elaboracao, observacoes, data_criacao, data_atualizacao, data_homologacao, homologado_por_id, ativo) 
VALUES ({quadro.id}, {f"'{numero}'" if numero else 'NULL'}, '{quadro.tipo}', '{quadro.categoria}', '{quadro.data_promocao.isoformat()}', '{quadro.status}', {f"'{motivo_nao_elaboracao}'" if motivo_nao_elaboracao else 'NULL'}, {f"'{observacoes}'" if observacoes else 'NULL'}, '{quadro.data_criacao.isoformat()}', '{quadro.data_atualizacao.isoformat()}', {f"'{quadro.data_homologacao.isoformat()}'" if quadro.data_homologacao else 'NULL'}, {str(quadro.homologado_por.id) if quadro.homologado_por else 'NULL'}, {str(quadro.ativo).lower()});"""
                sql_outros.append(sql)
            sql_outros.append("")
        
        return sql_outros
        
    except Exception as e:
        print(f"❌ Erro ao gerar SQL de outros modelos: {e}")
        return []

def gerar_arquivo_sql():
    """Gera o arquivo SQL completo"""
    print("\n📝 Gerando arquivo SQL...")
    
    try:
        # Configurar ambiente
        if not configurar_ambiente():
            return False
        
        # Gerar SQL para cada modelo
        sql_usuarios = gerar_sql_usuarios()
        sql_militares = gerar_sql_militares()
        sql_outros = gerar_sql_outros_modelos()
        
        # Combinar todos os SQLs
        sql_completo = []
        sql_completo.append("-- ========================================")
        sql_completo.append("-- MIGRAÇÃO PARA SUPABASE")
        sql_completo.append(f"-- Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        sql_completo.append("-- ========================================")
        sql_completo.append("")
        sql_completo.append("-- Desabilitar triggers temporariamente")
        sql_completo.append("SET session_replication_role = replica;")
        sql_completo.append("")
        
        # Adicionar SQLs
        sql_completo.extend(sql_usuarios)
        sql_completo.append("")
        sql_completo.extend(sql_militares)
        sql_completo.append("")
        sql_completo.extend(sql_outros)
        
        # Reabilitar triggers
        sql_completo.append("")
        sql_completo.append("-- Reabilitar triggers")
        sql_completo.append("SET session_replication_role = DEFAULT;")
        sql_completo.append("")
        sql_completo.append("-- Verificar dados inseridos")
        sql_completo.append("SELECT 'Usuários' as tabela, COUNT(*) as total FROM auth_user;")
        sql_completo.append("SELECT 'Militares' as tabela, COUNT(*) as total FROM militares_militar;")
        sql_completo.append("SELECT 'Comissões' as tabela, COUNT(*) as total FROM militares_comissaopromocao;")
        sql_completo.append("SELECT 'Quadros' as tabela, COUNT(*) as total FROM militares_quadroacesso;")
        
        # Salvar arquivo
        nome_arquivo = f"migracao_supabase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_completo))
        
        print(f"✅ Arquivo SQL gerado: {nome_arquivo}")
        print(f"📊 Total de linhas SQL: {len(sql_completo)}")
        
        # Mostrar instruções
        print("\n" + "=" * 60)
        print("📋 INSTRUÇÕES PARA MIGRAÇÃO:")
        print("=" * 60)
        print("1. Acesse o painel do Supabase")
        print("2. Vá para SQL Editor")
        print("3. Abra o arquivo gerado")
        print("4. Cole todo o conteúdo no editor SQL")
        print("5. Execute o script")
        print("6. Verifique se os dados foram inseridos corretamente")
        print()
        print("⚠️  IMPORTANTE:")
        print("- Faça backup antes de executar")
        print("- Execute em ambiente de teste primeiro")
        print("- Verifique as constraints e foreign keys")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar arquivo SQL: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 GERADOR DE SQL PARA SUPABASE")
    print("=" * 60)
    
    if gerar_arquivo_sql():
        print("\n🎉 Geração de SQL concluída com sucesso!")
        return True
    else:
        print("\n❌ Falha na geração do SQL")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Operação falhou. Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 