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

def migrar_dados_faltantes():
    print("=== MIGRANDO DADOS FALTANTES ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # 1. MIGRAR FICHAS DE CONCEITO
        print(f"\n=== MIGRANDO FICHAS DE CONCEITO ===")
        
        # Fichas de conceito de oficiais
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_fichaconceitooficiais")
        count_oficiais = cursor_sqlite.fetchone()[0]
        print(f"Fichas de conceito de oficiais: {count_oficiais}")
        
        # Fichas de conceito de praças
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_fichaconceitopracas")
        count_pracas = cursor_sqlite.fetchone()[0]
        print(f"Fichas de conceito de praças: {count_pracas}")
        
        # 2. MIGRAR SESSÕES DE COMISSÃO
        print(f"\n=== MIGRANDO SESSÕES DE COMISSÃO ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_sessaocomissao")
        count_sessoes = cursor_sqlite.fetchone()[0]
        print(f"Sessões de comissão: {count_sessoes}")
        
        # 3. MIGRAR VOTOS
        print(f"\n=== MIGRANDO VOTOS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_votodeliberacao")
        count_votos = cursor_sqlite.fetchone()[0]
        print(f"Votos: {count_votos}")
        
        # 4. MIGRAR DOCUMENTOS
        print(f"\n=== MIGRANDO DOCUMENTOS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_documento")
        count_documentos = cursor_sqlite.fetchone()[0]
        print(f"Documentos: {count_documentos}")
        
        # 5. MIGRAR NOTIFICAÇÕES
        print(f"\n=== MIGRANDO NOTIFICAÇÕES ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_notificacaosessao")
        count_notificacoes = cursor_sqlite.fetchone()[0]
        print(f"Notificações: {count_notificacoes}")
        
        # 6. MIGRAR ALMANAQUES
        print(f"\n=== MIGRANDO ALMANAQUES ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_almanaquemilitar")
        count_almanaques = cursor_sqlite.fetchone()[0]
        print(f"Almanaques: {count_almanaques}")
        
        # 7. MIGRAR ATAS
        print(f"\n=== MIGRANDO ATAS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_atasessao")
        count_atas = cursor_sqlite.fetchone()[0]
        print(f"Atas: {count_atas}")
        
        # 8. MIGRAR CALENDÁRIOS DE PROMOÇÃO
        print(f"\n=== MIGRANDO CALENDÁRIOS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_calendariopromocao")
        count_calendarios = cursor_sqlite.fetchone()[0]
        print(f"Calendários: {count_calendarios}")
        
        # 9. MIGRAR QUADROS DE ACESSO
        print(f"\n=== MIGRANDO QUADROS DE ACESSO ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_quadroacesso")
        count_quadros_acesso = cursor_sqlite.fetchone()[0]
        print(f"Quadros de acesso: {count_quadros_acesso}")
        
        # 10. MIGRAR QUADROS DE FIXAÇÃO DE VAGAS
        print(f"\n=== MIGRANDO QUADROS DE FIXAÇÃO ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_quadrofixacaovagas")
        count_quadros_fixacao = cursor_sqlite.fetchone()[0]
        print(f"Quadros de fixação: {count_quadros_fixacao}")
        
        # 11. MIGRAR VAGAS
        print(f"\n=== MIGRANDO VAGAS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_vaga")
        count_vagas = cursor_sqlite.fetchone()[0]
        print(f"Vagas: {count_vagas}")
        
        # 12. MIGRAR PREVISÕES DE VAGAS
        print(f"\n=== MIGRANDO PREVISÕES DE VAGAS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_previsaovaga")
        count_previsoes = cursor_sqlite.fetchone()[0]
        print(f"Previsões de vagas: {count_previsoes}")
        
        # 13. MIGRAR INTERSTÍCIOS
        print(f"\n=== MIGRANDO INTERSTÍCIOS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_intersticio")
        count_intersticios = cursor_sqlite.fetchone()[0]
        print(f"Interstícios: {count_intersticios}")
        
        # 14. MIGRAR PROMOÇÕES
        print(f"\n=== MIGRANDO PROMOÇÕES ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_promocao")
        count_promocoes = cursor_sqlite.fetchone()[0]
        print(f"Promoções: {count_promocoes}")
        
        # 15. MIGRAR PRESENÇAS EM SESSÕES
        print(f"\n=== MIGRANDO PRESENÇAS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_presencasessao")
        count_presencas = cursor_sqlite.fetchone()[0]
        print(f"Presenças: {count_presencas}")
        
        # 16. MIGRAR DELIBERAÇÕES
        print(f"\n=== MIGRANDO DELIBERAÇÕES ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_deliberacaocomissao")
        count_deliberacoes = cursor_sqlite.fetchone()[0]
        print(f"Deliberações: {count_deliberacoes}")
        
        # 17. MIGRAR MODELOS DE ATA
        print(f"\n=== MIGRANDO MODELOS DE ATA ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_modeloata")
        count_modelos = cursor_sqlite.fetchone()[0]
        print(f"Modelos de ata: {count_modelos}")
        
        # 18. MIGRAR ASSINATURAS
        print(f"\n=== MIGRANDO ASSINATURAS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_assinaturaata")
        count_assinaturas_ata = cursor_sqlite.fetchone()[0]
        print(f"Assinaturas de ata: {count_assinaturas_ata}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_assinaturaalmanaque")
        count_assinaturas_almanaque = cursor_sqlite.fetchone()[0]
        print(f"Assinaturas de almanaque: {count_assinaturas_almanaque}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_assinaturacalendariopromocao")
        count_assinaturas_calendario = cursor_sqlite.fetchone()[0]
        print(f"Assinaturas de calendário: {count_assinaturas_calendario}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_assinaturaquadroacesso")
        count_assinaturas_quadro_acesso = cursor_sqlite.fetchone()[0]
        print(f"Assinaturas de quadro de acesso: {count_assinaturas_quadro_acesso}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_assinaturaquadrofixacaovagas")
        count_assinaturas_quadro_fixacao = cursor_sqlite.fetchone()[0]
        print(f"Assinaturas de quadro de fixação: {count_assinaturas_quadro_fixacao}")
        
        # 19. MIGRAR ITENS DE QUADROS
        print(f"\n=== MIGRANDO ITENS DE QUADROS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_itemquadroacesso")
        count_itens_acesso = cursor_sqlite.fetchone()[0]
        print(f"Itens de quadro de acesso: {count_itens_acesso}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_itemquadrofixacaovagas")
        count_itens_fixacao = cursor_sqlite.fetchone()[0]
        print(f"Itens de quadro de fixação: {count_itens_fixacao}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_itemcalendariopromocao")
        count_itens_calendario = cursor_sqlite.fetchone()[0]
        print(f"Itens de calendário: {count_itens_calendario}")
        
        # 20. MIGRAR DOCUMENTOS DE SESSÃO
        print(f"\n=== MIGRANDO DOCUMENTOS DE SESSÃO ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_documentosessao")
        count_docs_sessao = cursor_sqlite.fetchone()[0]
        print(f"Documentos de sessão: {count_docs_sessao}")
        
        # 21. MIGRAR CARGOS DE COMISSÃO
        print(f"\n=== MIGRANDO CARGOS DE COMISSÃO ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_cargocomissao")
        count_cargos_comissao = cursor_sqlite.fetchone()[0]
        print(f"Cargos de comissão: {count_cargos_comissao}")
        
        # 22. MIGRAR PERFIS DE ACESSO
        print(f"\n=== MIGRANDO PERFIS DE ACESSO ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_perfilacesso")
        count_perfis = cursor_sqlite.fetchone()[0]
        print(f"Perfis de acesso: {count_perfis}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_perfilacesso_permissoes")
        count_perfis_permissoes = cursor_sqlite.fetchone()[0]
        print(f"Permissões de perfis: {count_perfis_permissoes}")
        
        # 23. MIGRAR PERMISSÕES DE FUNÇÃO
        print(f"\n=== MIGRANDO PERMISSÕES DE FUNÇÃO ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_permissaofuncao")
        count_permissoes_funcao = cursor_sqlite.fetchone()[0]
        print(f"Permissões de função: {count_permissoes_funcao}")
        
        # 24. MIGRAR MILITARES IMPORTADOS
        print(f"\n=== MIGRANDO MILITARES IMPORTADOS ===")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_militarimportado")
        count_militares_importados = cursor_sqlite.fetchone()[0]
        print(f"Militares importados: {count_militares_importados}")
        
        conn_sqlite.close()
        
        print(f"\n=== RESUMO DOS DADOS FALTANTES ===")
        print(f"Total de tabelas importantes identificadas: 24")
        print(f"Dados prontos para migração!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    migrar_dados_faltantes() 