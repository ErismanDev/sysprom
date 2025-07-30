#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE MIGRAÇÃO SUPABASE
================================

Script para verificar se a migração para o Supabase foi bem-sucedida,
comparando dados entre o banco local e o Supabase.

Autor: Sistema de Promoções CBMEPI
Data: 29/07/2025
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Carregar variáveis de ambiente
def carregar_env():
    """Carrega variáveis do arquivo .env"""
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith('#') and '=' in linha:
                    chave, valor = linha.split('=', 1)
                    os.environ[chave] = valor

# Configurações
carregar_env()

SUPABASE_CONFIG = {
    'host': os.getenv('SUPABASE_HOST'),
    'database': os.getenv('SUPABASE_DB'),
    'user': os.getenv('SUPABASE_USER'),
    'password': os.getenv('SUPABASE_PASSWORD'),
    'port': os.getenv('SUPABASE_PORT')
}

LOCAL_CONFIG = {
    'host': os.getenv('LOCAL_DB_HOST'),
    'database': os.getenv('LOCAL_DB_NAME'),
    'user': os.getenv('LOCAL_DB_USER'),
    'password': os.getenv('LOCAL_DB_PASSWORD'),
    'port': os.getenv('LOCAL_DB_PORT')
}

class VerificadorMigracao:
    def __init__(self):
        self.supabase_conn = None
        self.local_conn = None
        self.relatorio_file = f"relatorio_verificacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
    def log(self, message):
        """Registra mensagem no relatório"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.relatorio_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def conectar_bancos(self):
        """Conecta aos bancos de dados"""
        try:
            self.supabase_conn = psycopg2.connect(**SUPABASE_CONFIG)
            self.log("✅ Conectado ao Supabase")
            
            self.local_conn = psycopg2.connect(**LOCAL_CONFIG)
            self.log("✅ Conectado ao banco local")
            
            return True
        except Exception as e:
            self.log(f"❌ Erro ao conectar: {e}")
            return False
    
    def contar_registros(self, conn, tabela):
        """Conta registros em uma tabela"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            resultado = cursor.fetchone()[0]
            cursor.close()
            return resultado
        except Exception as e:
            self.log(f"❌ Erro ao contar {tabela}: {e}")
            return 0
    
    def verificar_tabela(self, tabela, nome_amigavel):
        """Verifica uma tabela específica"""
        self.log(f"\n📊 Verificando {nome_amigavel} ({tabela})")
        
        # Contar registros
        local_count = self.contar_registros(self.local_conn, tabela)
        supabase_count = self.contar_registros(self.supabase_conn, tabela)
        
        self.log(f"   Local: {local_count} registros")
        self.log(f"   Supabase: {supabase_count} registros")
        
        if local_count == supabase_count:
            self.log(f"   ✅ {nome_amigavel}: OK")
            return True
        else:
            self.log(f"   ❌ {nome_amigavel}: DIFERENÇA ENCONTRADA")
            return False
    
    def verificar_associacoes(self):
        """Verifica associações usuário-militar"""
        self.log(f"\n🔗 Verificando associações usuário-militar")
        
        # Local
        cursor = self.local_conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM militares_militar WHERE user_id IS NOT NULL
        """)
        local_com_usuario = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM militares_militar WHERE user_id IS NULL
        """)
        local_sem_usuario = cursor.fetchone()[0]
        cursor.close()
        
        # Supabase
        cursor = self.supabase_conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM militares_militar WHERE user_id IS NOT NULL
        """)
        supabase_com_usuario = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM militares_militar WHERE user_id IS NULL
        """)
        supabase_sem_usuario = cursor.fetchone()[0]
        cursor.close()
        
        self.log(f"   Local - Com usuário: {local_com_usuario}")
        self.log(f"   Local - Sem usuário: {local_sem_usuario}")
        self.log(f"   Supabase - Com usuário: {supabase_com_usuario}")
        self.log(f"   Supabase - Sem usuário: {supabase_sem_usuario}")
        
        if (local_com_usuario == supabase_com_usuario and 
            local_sem_usuario == supabase_sem_usuario):
            self.log(f"   ✅ Associações: OK")
            return True
        else:
            self.log(f"   ❌ Associações: DIFERENÇA ENCONTRADA")
            return False
    
    def verificar_sequencias(self):
        """Verifica se as sequências estão corretas"""
        self.log(f"\n🔢 Verificando sequências de ID")
        
        tabelas_principais = [
            'auth_user',
            'militares_militar',
            'militares_comissaopromocao',
            'militares_quadroacesso'
        ]
        
        for tabela in tabelas_principais:
            try:
                cursor = self.supabase_conn.cursor()
                cursor.execute(f"SELECT MAX(id) FROM {tabela}")
                max_id = cursor.fetchone()[0]
                
                cursor.execute(f"SELECT last_value FROM {tabela}_id_seq")
                seq_value = cursor.fetchone()[0]
                cursor.close()
                
                if max_id and seq_value:
                    if seq_value >= max_id:
                        self.log(f"   ✅ {tabela}: Sequência OK (max: {max_id}, seq: {seq_value})")
                    else:
                        self.log(f"   ⚠️ {tabela}: Sequência pode estar incorreta (max: {max_id}, seq: {seq_value})")
                else:
                    self.log(f"   ℹ️ {tabela}: Tabela vazia ou sem registros")
                    
            except Exception as e:
                self.log(f"   ❌ Erro ao verificar sequência de {tabela}: {e}")
    
    def verificar_usuarios_ativos(self):
        """Verifica usuários ativos"""
        self.log(f"\n👥 Verificando usuários ativos")
        
        # Local
        cursor = self.local_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_active = true")
        local_ativos = cursor.fetchone()[0]
        cursor.close()
        
        # Supabase
        cursor = self.supabase_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_active = true")
        supabase_ativos = cursor.fetchone()[0]
        cursor.close()
        
        self.log(f"   Local - Usuários ativos: {local_ativos}")
        self.log(f"   Supabase - Usuários ativos: {supabase_ativos}")
        
        if local_ativos == supabase_ativos:
            self.log(f"   ✅ Usuários ativos: OK")
            return True
        else:
            self.log(f"   ❌ Usuários ativos: DIFERENÇA ENCONTRADA")
            return False
    
    def verificar_dados_especificos(self):
        """Verifica dados específicos importantes"""
        self.log(f"\n🎯 Verificando dados específicos")
        
        # Verificar usuário admin
        cursor = self.supabase_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT username, is_superuser, is_staff FROM auth_user WHERE is_superuser = true")
        admins = cursor.fetchall()
        cursor.close()
        
        self.log(f"   Administradores encontrados: {len(admins)}")
        for admin in admins:
            self.log(f"   - {admin['username']} (superuser: {admin['is_superuser']}, staff: {admin['is_staff']})")
        
        # Verificar militares com CPF
        cursor = self.supabase_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM militares_militar WHERE cpf IS NOT NULL AND cpf != ''")
        militares_com_cpf = cursor.fetchone()[0]
        cursor.close()
        
        self.log(f"   Militares com CPF: {militares_com_cpf}")
        
        # Verificar comissões ativas
        cursor = self.supabase_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM militares_comissaopromocao WHERE ativa = true")
        comissoes_ativas = cursor.fetchone()[0]
        cursor.close()
        
        self.log(f"   Comissões ativas: {comissoes_ativas}")
    
    def gerar_relatorio_final(self, resultados):
        """Gera relatório final"""
        self.log(f"\n" + "="*60)
        self.log(f"📋 RELATÓRIO FINAL DE VERIFICAÇÃO")
        self.log(f"="*60)
        
        total_verificacoes = len(resultados)
        verificacoes_ok = sum(resultados)
        verificacoes_falha = total_verificacoes - verificacoes_ok
        
        self.log(f"Total de verificações: {total_verificacoes}")
        self.log(f"Verificações OK: {verificacoes_ok}")
        self.log(f"Verificações com falha: {verificacoes_falha}")
        
        if verificacoes_falha == 0:
            self.log(f"🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
            self.log(f"✅ A migração foi bem-sucedida!")
        else:
            self.log(f"⚠️ {verificacoes_falha} verificação(ões) falharam")
            self.log(f"🔍 Verifique os detalhes acima")
        
        self.log(f"\n📁 Relatório salvo em: {self.relatorio_file}")
    
    def executar_verificacao_completa(self):
        """Executa verificação completa"""
        self.log("🔍 INICIANDO VERIFICAÇÃO DE MIGRAÇÃO")
        self.log("="*60)
        
        if not self.conectar_bancos():
            return False
        
        resultados = []
        
        try:
            # Verificar tabelas principais
            tabelas_verificar = [
                ('auth_user', 'Usuários'),
                ('militares_militar', 'Militares'),
                ('militares_cargo', 'Cargos'),
                ('militares_funcao', 'Funções'),
                ('militares_comissaopromocao', 'Comissões'),
                ('militares_membrocomissao', 'Membros de Comissão'),
                ('militares_quadroacesso', 'Quadros de Acesso'),
                ('militares_documentosessao', 'Documentos de Sessão'),
                ('militares_ataassinatura', 'Assinaturas de Ata'),
                ('militares_votodeliberacao', 'Votos de Deliberação'),
                ('militares_documentocomissao', 'Documentos de Comissão'),
                ('militares_almanaque', 'Almanaques'),
                ('militares_almanaqueassinatura', 'Assinaturas de Almanaque'),
                ('militares_calendariopromocao', 'Calendários de Promoção'),
                ('militares_notificacao', 'Notificações')
            ]
            
            for tabela, nome in tabelas_verificar:
                resultado = self.verificar_tabela(tabela, nome)
                resultados.append(resultado)
            
            # Verificações específicas
            resultados.append(self.verificar_associacoes())
            resultados.append(self.verificar_usuarios_ativos())
            
            # Verificações adicionais
            self.verificar_sequencias()
            self.verificar_dados_especificos()
            
            # Relatório final
            self.gerar_relatorio_final(resultados)
            
            return True
            
        except Exception as e:
            self.log(f"❌ Erro durante verificação: {e}")
            return False
        finally:
            if self.supabase_conn:
                self.supabase_conn.close()
            if self.local_conn:
                self.local_conn.close()
            self.log("🔌 Conexões fechadas")

def main():
    """Função principal"""
    print("🔍 VERIFICADOR DE MIGRAÇÃO SUPABASE")
    print("="*50)
    
    # Verificar configurações
    if not SUPABASE_CONFIG['password'] or not LOCAL_CONFIG['password']:
        print("❌ Configurações não encontradas!")
        print("Execute primeiro: python configurar_migracao.py")
        return
    
    # Executar verificação
    verificador = VerificadorMigracao()
    sucesso = verificador.executar_verificacao_completa()
    
    if sucesso:
        print("\n🎉 Verificação concluída!")
        print("📋 Verifique o arquivo de relatório para detalhes")
    else:
        print("\n❌ Verificação falhou!")
        print("📋 Verifique o arquivo de relatório para detalhes")

if __name__ == "__main__":
    main() 