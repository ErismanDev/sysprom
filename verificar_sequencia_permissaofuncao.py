#!/usr/bin/env python
"""
Script para verificar e corrigir a sequência da tabela PermissaoFuncao
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import connection, models
from militares.models import PermissaoFuncao

def verificar_sequencia_permissaofuncao():
    """
    Verifica e corrige a sequência da tabela PermissaoFuncao
    """
    print("🔍 Verificando sequência da tabela PermissaoFuncao...")
    print("=" * 60)
    
    # 1. Verificar registros existentes
    total_registros = PermissaoFuncao.objects.count()
    print(f"📊 Total de registros na tabela: {total_registros}")
    
    if total_registros > 0:
        # Buscar o maior ID
        maior_id = PermissaoFuncao.objects.aggregate(
            models.Max('id')
        )['id__max']
        print(f"📊 Maior ID encontrado: {maior_id}")
        
        # Buscar o menor ID
        menor_id = PermissaoFuncao.objects.aggregate(
            models.Min('id')
        )['id__min']
        print(f"📊 Menor ID encontrado: {menor_id}")
        
        # Listar alguns registros para verificar
        print("\n📋 Primeiros 10 registros:")
        for i, permissao in enumerate(PermissaoFuncao.objects.order_by('id')[:10]):
            print(f"  {i+1}. ID: {permissao.id} - {permissao}")
    
    # 2. Verificar sequência no PostgreSQL
    with connection.cursor() as cursor:
        # Listar todas as sequências para encontrar a correta
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
            ORDER BY sequence_name
        """)
        sequencias = cursor.fetchall()
        
        print(f"\n🔍 Todas as sequências encontradas:")
        for seq in sequencias:
            print(f"   - {seq[0]}")
        
        # Tentar encontrar a sequência correta
        nome_sequencia = None
        for seq in sequencias:
            if 'permissaofuncao' in seq[0].lower():
                nome_sequencia = seq[0]
                break
        
        if nome_sequencia:
            print(f"\n🔧 Usando sequência: {nome_sequencia}")
            
            # Verificar o último valor da sequência
            cursor.execute(f"SELECT last_value FROM {nome_sequencia}")
            ultimo_valor = cursor.fetchone()[0]
            print(f"   Último valor: {ultimo_valor}")
            
            # 3. Verificar se há conflito
            if total_registros > 0 and maior_id:
                print(f"\n🔍 Comparando valores:")
                print(f"   Maior ID na tabela: {maior_id}")
                print(f"   Último valor da sequência: {ultimo_valor}")
                
                if ultimo_valor <= maior_id:
                    print(f"⚠️  Problema detectado: Sequência está atrás do maior ID!")
                    return corrigir_sequencia_permissaofuncao(nome_sequencia, maior_id)
                else:
                    print(f"✅ Sequência está correta!")
                    return True
        else:
            print("\n❌ Nenhuma sequência encontrada para PermissaoFuncao!")
            print("🔧 Tentando criar a sequência...")
            return criar_sequencia_permissaofuncao(maior_id)
    
    return True

def corrigir_sequencia_permissaofuncao(nome_sequencia, maior_id):
    """
    Corrige a sequência da tabela PermissaoFuncao
    """
    print(f"\n🔧 Corrigindo sequência {nome_sequencia}...")
    
    try:
        with connection.cursor() as cursor:
            # Definir o próximo valor da sequência como maior_id + 1
            novo_valor = maior_id + 1
            cursor.execute(f"SELECT setval('{nome_sequencia}', {novo_valor}, true)")
            
            # Verificar se foi corrigido
            cursor.execute(f"SELECT last_value FROM {nome_sequencia}")
            novo_ultimo_valor = cursor.fetchone()[0]
            
            print(f"✅ Sequência corrigida!")
            print(f"   Novo valor da sequência: {novo_ultimo_valor}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao corrigir sequência: {e}")
        return False

def criar_sequencia_permissaofuncao(maior_id):
    """
    Cria a sequência da tabela PermissaoFuncao se não existir
    """
    print(f"\n🔧 Criando sequência permissaofuncao...")
    
    try:
        with connection.cursor() as cursor:
            # Definir o próximo valor da sequência como maior_id + 1
            novo_valor = maior_id + 1
            cursor.execute(f"CREATE SEQUENCE IF NOT EXISTS permissaofuncao START WITH {novo_valor} INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1")
            
            # Verificar se foi criado
            cursor.execute(f"SELECT last_value FROM permissaofuncao")
            novo_ultimo_valor = cursor.fetchone()[0]
            
            print(f"✅ Sequência permissaofuncao criada!")
            print(f"   Novo valor da sequência: {novo_ultimo_valor}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar sequência: {e}")
        return False

def testar_criacao_permissao():
    """
    Testa a criação de uma nova permissão para verificar se o problema foi resolvido
    """
    print(f"\n🧪 Testando criação de nova permissão...")
    
    try:
        # Tentar criar uma permissão de teste
        permissao_teste = PermissaoFuncao.objects.create(
            modulo='TESTE',
            acesso='VISUALIZAR',
            ativo=True,
            observacoes='Permissão de teste para verificar sequência'
        )
        
        print(f"✅ Permissão de teste criada com sucesso!")
        print(f"   ID: {permissao_teste.id}")
        print(f"   Módulo: {permissao_teste.modulo}")
        print(f"   Acesso: {permissao_teste.acesso}")
        
        # Remover a permissão de teste
        permissao_teste.delete()
        print(f"🗑️  Permissão de teste removida")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar permissão de teste: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 Iniciando verificação e correção da sequência PermissaoFuncao...")
    print("=" * 60)
    
    # Verificar sequência
    if verificar_sequencia_permissaofuncao():
        print("\n✅ Verificação concluída!")
        
        # Testar criação
        if testar_criacao_permissao():
            print("\n🎉 Problema resolvido! A sequência está funcionando corretamente.")
        else:
            print("\n❌ Ainda há problemas com a sequência.")
    else:
        print("\n❌ Falha na verificação/correção da sequência.")
    
    print("\n" + "=" * 60)
    print("🏁 Processo concluído!")

if __name__ == '__main__':
    main() 