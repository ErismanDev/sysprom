#!/usr/bin/env python
"""
Script para importar dados de antiguidade do arquivo Excel para o banco de dados.
"""

import os
import sys
import django
import pandas as pd
from difflib import SequenceMatcher

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar


def similar(a, b):
    """Calcula a similaridade entre duas strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def normalizar_nome(nome):
    """Normaliza o nome para comparação"""
    # Remover espaços extras e normalizar
    nome = ' '.join(nome.split())
    # Converter para minúsculas
    return nome.lower()


def encontrar_militar_por_nome(nome_excel, militares_db):
    """Encontra o militar no banco de dados baseado no nome do Excel"""
    nome_normalizado = normalizar_nome(nome_excel)
    
    # Primeiro, tentar match exato
    for militar in militares_db:
        if normalizar_nome(militar.nome_completo) == nome_normalizado:
            return militar, 1.0
    
    # Se não encontrar, tentar match parcial
    melhor_match = None
    melhor_score = 0
    
    for militar in militares_db:
        score = similar(nome_excel, militar.nome_completo)
        if score > melhor_score and score > 0.7:  # Threshold de 70%
            melhor_score = score
            melhor_match = militar
    
    return melhor_match, melhor_score


def importar_antiguidade():
    """Importa os dados de antiguidade do Excel para o banco de dados"""
    
    # Ler o arquivo Excel
    try:
        df = pd.read_excel('Efetivo CBMEPI Atito SI Promoção.xlsx')
        print(f"✅ Arquivo Excel carregado com sucesso!")
        print(f"📊 Total de registros no Excel: {len(df)}")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        print()
    except Exception as e:
        print(f"❌ Erro ao ler o arquivo Excel: {e}")
        return
    
    # Verificar se as colunas necessárias existem
    if 'ORD' not in df.columns or 'NOME' not in df.columns:
        print("❌ Colunas 'ORD' e 'NOME' não encontradas no Excel!")
        print(f"Colunas disponíveis: {list(df.columns)}")
        return
    
    # Buscar todos os militares ativos no banco
    militares_db = list(Militar.objects.filter(situacao='AT'))
    print(f"👥 Total de militares ativos no banco: {len(militares_db)}")
    print()
    
    # Processar cada linha do Excel
    sucessos = 0
    erros = 0
    nao_encontrados = 0
    duplicatas = []
    
    print("🔄 Processando dados...")
    print("-" * 80)
    
    for index, row in df.iterrows():
        numero_antiguidade = row['ORD']
        nome_excel = row['NOME']
        
        print(f"📝 Processando: {nome_excel} (Antiguidade: {numero_antiguidade})")
        
        # Encontrar o militar correspondente
        militar, score = encontrar_militar_por_nome(nome_excel, militares_db)
        
        if militar:
            if score == 1.0:
                print(f"   ✅ Match exato encontrado: {militar.nome_completo}")
            else:
                print(f"   ⚠️  Match parcial encontrado: {militar.nome_completo} (Score: {score:.2f})")
            
            # Verificar se já tem antiguidade
            if militar.numeracao_antiguidade is not None:
                print(f"   ⚠️  Militar já possui antiguidade: {militar.numeracao_antiguidade}º")
                duplicatas.append({
                    'excel': nome_excel,
                    'banco': militar.nome_completo,
                    'antiguidade_atual': militar.numeracao_antiguidade,
                    'antiguidade_excel': numero_antiguidade
                })
                erros += 1
            else:
                # Atualizar a antiguidade
                militar.numeracao_antiguidade = numero_antiguidade
                militar.save(update_fields=['numeracao_antiguidade'])
                print(f"   ✅ Antiguidade atualizada: {numero_antiguidade}º")
                sucessos += 1
        else:
            print(f"   ❌ Militar não encontrado no banco de dados")
            nao_encontrados += 1
        
        print()
    
    # Relatório final
    print("=" * 80)
    print("📊 RELATÓRIO FINAL")
    print("=" * 80)
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros (já possuíam antiguidade): {erros}")
    print(f"🔍 Não encontrados: {nao_encontrados}")
    print(f"📋 Total processado: {len(df)}")
    print()
    
    if duplicatas:
        print("⚠️  MILITARES QUE JÁ POSSUÍAM ANTIGUIDADE:")
        print("-" * 50)
        for dup in duplicatas:
            print(f"Excel: {dup['excel']}")
            print(f"Banco: {dup['banco']}")
            print(f"Antiguidade atual: {dup['antiguidade_atual']}º")
            print(f"Antiguidade do Excel: {dup['antiguidade_excel']}º")
            print()
    
    if nao_encontrados > 0:
        print("🔍 MILITARES NÃO ENCONTRADOS NO BANCO:")
        print("-" * 40)
        for index, row in df.iterrows():
            nome_excel = row['NOME']
            militar, score = encontrar_militar_por_nome(nome_excel, militares_db)
            if not militar:
                print(f"❌ {nome_excel}")
        print()
    
    # Verificar se há militares sem antiguidade
    militares_sem_antiguidade = Militar.objects.filter(
        situacao='AT',
        numeracao_antiguidade__isnull=True
    ).count()
    
    print(f"📈 MILITARES ATIVOS SEM ANTIGUIDADE: {militares_sem_antiguidade}")
    
    if militares_sem_antiguidade > 0:
        print("Lista de militares sem antiguidade:")
        for militar in Militar.objects.filter(situacao='AT', numeracao_antiguidade__isnull=True):
            print(f"   - {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
    
    print()
    print("🎉 Importação concluída!")


if __name__ == '__main__':
    print("🚀 Iniciando importação de antiguidade do Excel...")
    print()
    importar_antiguidade() 