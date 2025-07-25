#!/usr/bin/env python
"""
Script para atualizar a numeração de antiguidade dos militares
baseado no arquivo Excel 'Efetivo CBMEPI Atito SI Promoção.xlsx'
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar

def mapear_posto_excel_para_sistema(posto_excel):
    """Mapeia os postos do Excel para os códigos do sistema"""
    mapeamento = {
        'CORONEL': 'CB',
        'TENENTE-CORONEL': 'TC',
        'MAJOR': 'MJ',
        'CAPITÃO': 'CP',
        '1º TENENTE': '1T',
        '2º TENENTE': '2T',
        'ASPIRANTE A OFICIAL': 'AS',
        'ALUNO DE ADAPTAÇÃO': 'AA',
        'SUBTENENTE': 'ST',
        '1º SARGENTO': '1S',
        '2º SARGENTO': '2S',
        '3º SARGENTO': '3S',
        'CABO': 'CAB',
        'SOLDADO': 'SD',
    }
    return mapeamento.get(posto_excel.upper().strip(), posto_excel)

def normalizar_nome(nome):
    """Normaliza o nome para comparação"""
    if pd.isna(nome):
        return ""
    return nome.strip().upper()

def atualizar_antiguidade():
    """Atualiza a numeração de antiguidade baseada no arquivo Excel"""
    
    # Caminho do arquivo Excel
    arquivo_excel = 'backups/Efetivo CBMEPI Atito SI Promoção.xlsx'
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo não encontrado: {arquivo_excel}")
        return
    
    try:
        # Ler o arquivo Excel
        print(f"📖 Lendo arquivo Excel: {arquivo_excel}")
        df = pd.read_excel(arquivo_excel)
        
        print(f"📊 Colunas encontradas: {df.columns.tolist()}")
        print(f"📈 Total de registros: {len(df)}")
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['ORD', 'POST/ GRAD', 'NOME']
        for coluna in colunas_necessarias:
            if coluna not in df.columns:
                print(f"❌ Coluna necessária não encontrada: {coluna}")
                return
        
        # Limpar dados
        df = df.dropna(subset=['NOME'])  # Remover linhas sem nome
        df = df[df['ORD'].notna()]  # Remover linhas sem ordem
        
        print(f"📋 Registros válidos após limpeza: {len(df)}")
        
        # Contadores
        atualizados = 0
        nao_encontrados = 0
        erros = 0
        
        print("\n🔄 Iniciando atualização da antiguidade...")
        print("=" * 80)
        
        # Processar cada registro
        for index, row in df.iterrows():
            try:
                ordem = int(row['ORD'])
                posto_excel = str(row['POST/ GRAD']).strip()
                nome_excel = normalizar_nome(row['NOME'])
                
                # Mapear posto do Excel para o sistema
                posto_sistema = mapear_posto_excel_para_sistema(posto_excel)
                
                print(f"🔍 Processando: {nome_excel} - {posto_excel} ({posto_sistema}) - Ordem: {ordem}")
                
                # Buscar militar no sistema
                militares_encontrados = Militar.objects.filter(
                    situacao='AT',
                    posto_graduacao=posto_sistema
                )
                
                # Tentar encontrar por nome (comparação aproximada)
                militar_encontrado = None
                for militar in militares_encontrados:
                    nome_sistema = normalizar_nome(militar.nome_completo)
                    if nome_excel in nome_sistema or nome_sistema in nome_excel:
                        militar_encontrado = militar
                        break
                
                if militar_encontrado:
                    # Verificar se a antiguidade mudou
                    antiguidade_anterior = militar_encontrado.numeracao_antiguidade
                    
                    if antiguidade_anterior != ordem:
                        militar_encontrado.numeracao_antiguidade = ordem
                        militar_encontrado.save(update_fields=['numeracao_antiguidade'])
                        print(f"✅ Atualizado: {militar_encontrado.nome_completo} - Antiguidade: {antiguidade_anterior} → {ordem}")
                        atualizados += 1
                    else:
                        print(f"ℹ️  Sem alteração: {militar_encontrado.nome_completo} - Antiguidade: {ordem}")
                else:
                    print(f"❌ Não encontrado: {nome_excel} ({posto_excel})")
                    nao_encontrados += 1
                    
            except Exception as e:
                print(f"❌ Erro ao processar linha {index + 1}: {e}")
                erros += 1
        
        print("\n" + "=" * 80)
        print("📊 RESUMO DA ATUALIZAÇÃO:")
        print(f"✅ Militares atualizados: {atualizados}")
        print(f"❌ Militares não encontrados: {nao_encontrados}")
        print(f"⚠️  Erros: {erros}")
        print(f"📈 Total processado: {len(df)}")
        
        if nao_encontrados > 0:
            print(f"\n⚠️  ATENÇÃO: {nao_encontrados} militares não foram encontrados no sistema.")
            print("   Verifique se os nomes e postos estão corretos no arquivo Excel.")
        
        # Reordenar automaticamente após a atualização
        print("\n🔄 Reordenando numerações automaticamente...")
        total_reordenados = Militar.reordenar_todos_apos_inativacao()
        print(f"✅ Reordenação concluída: {total_reordenados} militares reordenados")
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo Excel: {e}")
        return

def mostrar_militares_sem_antiguidade():
    """Mostra militares que não têm numeração de antiguidade"""
    print("\n🔍 MILITARES SEM NUMERAÇÃO DE ANTIGUIDADE:")
    print("=" * 60)
    
    militares_sem_antiguidade = Militar.objects.filter(
        situacao='AT',
        numeracao_antiguidade__isnull=True
    ).order_by('posto_graduacao', 'nome_completo')
    
    if militares_sem_antiguidade.exists():
        for militar in militares_sem_antiguidade:
            print(f"❌ {militar.nome_completo} - {militar.get_posto_graduacao_display()} - {militar.get_quadro_display()}")
        print(f"\n📊 Total: {militares_sem_antiguidade.count()} militares sem antiguidade")
    else:
        print("✅ Todos os militares ativos têm numeração de antiguidade!")

def main():
    """Função principal"""
    print("🚀 SCRIPT DE ATUALIZAÇÃO DE ANTIGUIDADE")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Mostrar militares sem antiguidade antes da atualização
    mostrar_militares_sem_antiguidade()
    
    # Atualizar antiguidade
    atualizar_antiguidade()
    
    # Mostrar militares sem antiguidade após a atualização
    print("\n" + "=" * 50)
    mostrar_militares_sem_antiguidade()
    
    print(f"\n⏰ Finalizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("✅ Script concluído!")

if __name__ == '__main__':
    main() 