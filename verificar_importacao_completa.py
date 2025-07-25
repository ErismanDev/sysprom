#!/usr/bin/env python
import os
import sys
import django
import sqlite3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import *

def verificar_importacao_completa():
    print("=== VERIFICANDO IMPORTAÇÃO COMPLETA ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Verificar tabelas no SQLite
        cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas_sqlite = [row[0] for row in cursor_sqlite.fetchall()]
        
        print(f"Tabelas no SQLite: {len(tabelas_sqlite)}")
        for tabela in sorted(tabelas_sqlite):
            cursor_sqlite.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor_sqlite.fetchone()[0]
            print(f"   • {tabela}: {count} registros")
        
        print(f"\n=== COMPARAÇÃO COM POSTGRESQL ===")
        
        # Contadores PostgreSQL
        print(f"PostgreSQL:")
        print(f"   • Usuários: {User.objects.count()}")
        print(f"   • Militares: {Militar.objects.count()}")
        print(f"   • Comissões: {ComissaoPromocao.objects.count()}")
        print(f"   • Membros de comissões: {MembroComissao.objects.count()}")
        print(f"   • Funções de usuários: {UsuarioFuncao.objects.count()}")
        print(f"   • Cargos/Funções: {CargoFuncao.objects.count()}")
        
        # Verificar outras tabelas importantes
        tabelas_importantes = [
            'FichaConceito',
            'Almanaque',
            'SessaoPromocao',
            'Voto',
            'Documento',
            'Notificacao',
        ]
        
        print(f"\n=== VERIFICANDO TABELAS IMPORTANTES ===")
        for tabela in tabelas_importantes:
            try:
                modelo = globals().get(tabela)
                if modelo:
                    count = modelo.objects.count()
                    print(f"   • {tabela}: {count} registros")
                else:
                    print(f"   • {tabela}: Modelo não encontrado")
            except Exception as e:
                print(f"   • {tabela}: Erro - {e}")
        
        # Verificar se há dados faltando
        print(f"\n=== VERIFICANDO DADOS FALTANDO ===")
        
        # Verificar se todos os militares têm usuários
        militares_sem_usuario = Militar.objects.filter(user__isnull=True).count()
        if militares_sem_usuario > 0:
            print(f"   ⚠️ {militares_sem_usuario} militares sem usuário")
        
        # Verificar se todos os usuários têm militares
        usuarios_sem_militar = User.objects.filter(militar__isnull=True).count()
        if usuarios_sem_militar > 0:
            print(f"   ⚠️ {usuarios_sem_militar} usuários sem militar")
        
        # Verificar comissões sem membros
        comissoes_sem_membros = ComissaoPromocao.objects.filter(membrocomissao__isnull=True).count()
        if comissoes_sem_membros > 0:
            print(f"   ⚠️ {comissoes_sem_membros} comissões sem membros")
        
        conn_sqlite.close()
        
        print(f"\n✅ VERIFICAÇÃO CONCLUÍDA")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_importacao_completa() 