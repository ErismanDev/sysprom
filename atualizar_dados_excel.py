#!/usr/bin/env python
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

def buscar_militar_por_nome(nome_excel, militares_db):
    """
    Busca militar por nome usando similaridade
    Retorna (militar, score) ou (None, 0)
    """
    melhor_match = None
    melhor_score = 0
    
    for militar in militares_db:
        score = similar(nome_excel, militar.nome_completo)
        if score > melhor_score:
            melhor_score = score
            melhor_match = militar
    
    return melhor_match, melhor_score

def atualizar_dados_excel():
    """Atualiza dados de antiguidade e postos/graduação do arquivo Excel"""
    
    print("=== ATUALIZANDO DADOS DO EXCEL ===\n")
    
    # Caminho do arquivo Excel
    arquivo_excel = "Efetivo CBMEPI Atito SI Promoção.xlsx"
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo não encontrado: {arquivo_excel}")
        return
    
    try:
        # Ler o arquivo Excel
        print(f"📖 Lendo arquivo: {arquivo_excel}")
        df = pd.read_excel(arquivo_excel)
        
        print(f"📊 Colunas encontradas: {list(df.columns)}")
        print(f"📊 Total de linhas: {len(df)}")
        
        # Mostrar as primeiras linhas para identificar a estrutura
        print("\n📋 Primeiras 5 linhas do arquivo:")
        print(df.head())
        
        # Identificar colunas relevantes
        colunas_nome = []
        colunas_numeracao = []
        colunas_posto = []
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'nome' in col_lower or 'militar' in col_lower:
                colunas_nome.append(col)
            elif 'numeração' in col_lower or 'antiguidade' in col_lower or 'numero' in col_lower or 'ord' in col_lower:
                colunas_numeracao.append(col)
            elif 'posto' in col_lower or 'graduação' in col_lower or 'graduacao' in col_lower:
                colunas_posto.append(col)
        
        print(f"\n🔍 Colunas de nome identificadas: {colunas_nome}")
        print(f"🔍 Colunas de numeração identificadas: {colunas_numeracao}")
        print(f"🔍 Colunas de posto identificadas: {colunas_posto}")
        
        if not colunas_nome:
            print("❌ Nenhuma coluna de nome identificada. Verifique o arquivo.")
            return
        
        # Usar a primeira coluna de cada tipo encontrada
        coluna_nome = colunas_nome[0] if colunas_nome else None
        coluna_numeracao = colunas_numeracao[0] if colunas_numeracao else None
        coluna_posto = colunas_posto[0] if colunas_posto else None
        
        print(f"\n✅ Usando coluna de nome: {coluna_nome}")
        print(f"✅ Usando coluna de numeração: {coluna_numeracao}")
        print(f"✅ Usando coluna de posto: {coluna_posto}")
        
        # Buscar todos os militares ativos
        militares_db = Militar.objects.filter(situacao='AT')
        print(f"\n📊 Total de militares ativos no banco: {militares_db.count()}")
        
        # Processar cada linha
        atualizados = 0
        nao_encontrados = 0
        erros = 0
        atualizacoes_antiguidade = 0
        atualizacoes_posto = 0
        
        print(f"\n🔄 Processando {len(df)} registros...")
        
        for index, row in df.iterrows():
            try:
                nome_excel = str(row[coluna_nome]).strip() if coluna_nome else None
                
                # Pular linhas vazias
                if not nome_excel or pd.isna(nome_excel) or nome_excel == 'nan' or nome_excel == '':
                    continue
                
                # Buscar militar pelo nome
                militar, score = buscar_militar_por_nome(nome_excel, militares_db)
                
                if militar and score > 0.7:  # Threshold de 70% de similaridade
                    atualizacoes_feitas = []
                    
                    # Atualizar numeração de antiguidade se disponível
                    if coluna_numeracao:
                        numeracao_excel = row[coluna_numeracao]
                        if not pd.isna(numeracao_excel):
                            try:
                                numeracao = int(numeracao_excel)
                                if militar.numeracao_antiguidade != numeracao:
                                    militar.numeracao_antiguidade = numeracao
                                    atualizacoes_antiguidade += 1
                                    atualizacoes_feitas.append(f"antiguidade: {numeracao}º")
                            except (ValueError, TypeError):
                                print(f"⚠️  Numeração inválida na linha {index + 2}: {numeracao_excel}")
                    
                    # Atualizar posto/graduação se disponível
                    if coluna_posto:
                        posto_excel = str(row[coluna_posto]).strip() if not pd.isna(row[coluna_posto]) else None
                        if posto_excel and posto_excel != 'nan':
                            # Mapear postos do Excel para códigos do sistema
                            mapeamento_postos = {
                                'CORONEL': 'CB',
                                'TENENTE CORONEL': 'TC',
                                'MAJOR': 'MJ',
                                'CAPITÃO': 'CP',
                                'CAPITAO': 'CP',
                                '1º TENENTE': '1T',
                                '1º TEN': '1T',
                                '1T': '1T',
                                '2º TENENTE': '2T',
                                '2º TEN': '2T',
                                '2T': '2T',
                                'ASPIRANTE': 'AS',
                                'ALUNO ADAPTAÇÃO': 'AA',
                                'ALUNO ADAPTACAO': 'AA',
                                'AA': 'AA',
                                'SUBTENENTE': 'ST',
                                '1º SARGENTO': '1S',
                                '1º SGT': '1S',
                                '1S': '1S',
                                '2º SARGENTO': '2S',
                                '2º SGT': '2S',
                                '2S': '2S',
                                '3º SARGENTO': '3S',
                                '3º SGT': '3S',
                                '3S': '3S',
                                'CABO': 'CAB',
                                'SOLDADO': 'SD',
                            }
                            
                            posto_codigo = mapeamento_postos.get(posto_excel.upper())
                            if posto_codigo and militar.posto_graduacao != posto_codigo:
                                militar.posto_graduacao = posto_codigo
                                atualizacoes_posto += 1
                                atualizacoes_feitas.append(f"posto: {posto_excel}")
                    
                    # Salvar se houve alterações
                    if atualizacoes_feitas:
                        militar.save()
                        print(f"✅ Linha {index + 2}: {militar.nome_completo} - {', '.join(atualizacoes_feitas)}")
                        atualizados += 1
                    else:
                        print(f"ℹ️  Linha {index + 2}: {militar.nome_completo} - Sem alterações necessárias")
                else:
                    print(f"❌ Linha {index + 2}: Militar não encontrado: {nome_excel}")
                    nao_encontrados += 1
                    
            except Exception as e:
                print(f"❌ Erro na linha {index + 2}: {str(e)}")
                erros += 1
        
        # Resumo final
        print(f"\n=== RESUMO DA ATUALIZAÇÃO ===")
        print(f"✅ Militares atualizados: {atualizados}")
        print(f"📊 Atualizações de antiguidade: {atualizacoes_antiguidade}")
        print(f"📊 Atualizações de posto: {atualizacoes_posto}")
        print(f"❌ Militares não encontrados: {nao_encontrados}")
        print(f"⚠️  Erros: {erros}")
        print(f"📊 Total processado: {atualizados + nao_encontrados + erros}")
        
        if atualizacoes_antiguidade > 0 or atualizacoes_posto > 0:
            print(f"\n💡 Dados atualizados com sucesso!")
            print(f"💡 Reordenação automática será aplicada ao editar militares.")
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo Excel: {str(e)}")

if __name__ == "__main__":
    atualizar_dados_excel() 