#!/usr/bin/env python
"""
Script para importar militares do arquivo Excel 'Efetivo CBMEPI Atito SI Promoção 2.xlsx'
para o sistema Django
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime, date
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, POSTO_GRADUACAO_CHOICES, QUADRO_CHOICES
from django.contrib.auth.models import User

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

def gerar_matricula(nome, posto):
    """Gera uma matrícula única baseada no nome e posto"""
    # Extrair iniciais do nome
    palavras = nome.split()
    if len(palavras) >= 2:
        iniciais = palavras[0][0] + palavras[-1][0]
    else:
        iniciais = nome[:2]
    
    # Gerar número baseado no posto
    numeros_posto = {
        'CB': '1000',
        'TC': '2000', 
        'MJ': '3000',
        'CP': '4000',
        '1T': '5000',
        '2T': '6000',
        'AS': '7000',
        'AA': '8000',
        'ST': '9000',
        '1S': '10000',
        '2S': '11000',
        '3S': '12000',
        'CAB': '13000',
        'SD': '14000',
    }
    
    base_numero = numeros_posto.get(posto, '15000')
    
    # Contar quantos militares já existem com este posto
    count = Militar.objects.filter(posto_graduacao=posto).count()
    
    return f"{iniciais}{base_numero}{count+1:03d}"

def gerar_cpf_fake():
    """Gera um CPF fake para fins de teste"""
    import random
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcular dígitos verificadores
    soma = sum(cpf[i] * (10 - i) for i in range(9))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    
    soma = sum(cpf[i] * (11 - i) for i in range(10))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    
    return ''.join(map(str, cpf))

def normalizar_nome(nome):
    """Normaliza o nome para exibição"""
    if pd.isna(nome):
        return ""
    
    nome = nome.strip()
    
    # Converter para título (primeira letra maiúscula)
    nome = nome.title()
    
    # Corrigir nomes comuns
    correcoes = {
        'De': 'de',
        'Da': 'da',
        'Do': 'do',
        'Das': 'das',
        'Dos': 'dos',
        'E': 'e',
        'O': 'o',
        'A': 'a',
    }
    
    palavras = nome.split()
    palavras_corrigidas = []
    
    for i, palavra in enumerate(palavras):
        if palavra.lower() in correcoes and i > 0:  # Não corrigir a primeira palavra
            palavras_corrigidas.append(correcoes[palavra.lower()])
        else:
            palavras_corrigidas.append(palavra)
    
    return ' '.join(palavras_corrigidas)

def gerar_nome_guerra(nome_completo):
    """Gera nome de guerra baseado no nome completo"""
    palavras = nome_completo.split()
    if len(palavras) >= 2:
        # Usar primeiro e último nome
        return f"{palavras[0]} {palavras[-1]}"
    else:
        return nome_completo

def importar_militares():
    """Importa militares do arquivo Excel"""
    
    # Caminho do arquivo Excel - NOVO ARQUIVO
    arquivo_excel = 'Efetivo CBMEPI Atito SI Promoção 2.xlsx'
    
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
        importados = 0
        erros = 0
        duplicados = 0
        
        print("\n🔄 Iniciando importação dos militares...")
        print("=" * 80)
        
        # Processar cada registro
        for index, row in df.iterrows():
            try:
                ordem = int(row['ORD'])
                posto_excel = str(row['POST/ GRAD']).strip()
                nome_excel = str(row['NOME']).strip()
                
                # Mapear posto do Excel para o sistema
                posto_sistema = mapear_posto_excel_para_sistema(posto_excel)
                
                # Normalizar nome
                nome_completo = normalizar_nome(nome_excel)
                
                print(f"🔍 Processando: {nome_completo} - {posto_excel} ({posto_sistema}) - Ordem: {ordem}")
                
                # Verificar se já existe um militar com este nome
                if Militar.objects.filter(nome_completo__iexact=nome_completo).exists():
                    print(f"⚠️  Duplicado: {nome_completo} já existe no sistema")
                    duplicados += 1
                    continue
                
                # Gerar dados necessários
                matricula = gerar_matricula(nome_completo, posto_sistema)
                nome_guerra = gerar_nome_guerra(nome_completo)
                cpf = gerar_cpf_fake()
                
                # Criar militar - TODOS COMO ATIVOS
                militar = Militar(
                    numeracao_antiguidade=ordem,
                    matricula=matricula,
                    nome_completo=nome_completo,
                    nome_guerra=nome_guerra,
                    cpf=cpf,
                    rg="RG123456",
                    orgao_expedidor="SSP/PI",
                    data_nascimento=date(1980, 1, 1),  # Data padrão
                    sexo='M',  # Padrão masculino
                    quadro='COMB',  # Padrão combatente
                    posto_graduacao=posto_sistema,
                    data_ingresso=date(2010, 1, 1),  # Data padrão
                    data_promocao_atual=date(2020, 1, 1),  # Data padrão
                    situacao='AT',  # TODOS ATIVOS
                    email=f"{nome_completo.lower().replace(' ', '.')}@cbmepi.pi.gov.br",
                    telefone="(86) 99999-9999",
                    celular="(86) 99999-9999",
                    apto_inspecao_saude=True,
                )
                
                militar.save()
                print(f"✅ Importado: {militar.nome_completo} - Matrícula: {matricula} - Status: ATIVO")
                importados += 1
                    
            except Exception as e:
                print(f"❌ Erro ao processar linha {index + 1}: {e}")
                erros += 1
        
        print("\n" + "=" * 80)
        print("📊 RESUMO DA IMPORTAÇÃO:")
        print(f"✅ Militares importados: {importados}")
        print(f"⚠️  Duplicados: {duplicados}")
        print(f"❌ Erros: {erros}")
        print(f"📈 Total processado: {len(df)}")
        
        if importados > 0:
            print(f"\n🔄 Reordenando numerações automaticamente...")
            total_reordenados = Militar.reordenar_todos_apos_inativacao()
            print(f"✅ Reordenação concluída: {total_reordenados} militares reordenados")
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo Excel: {e}")
        return

def mostrar_estatisticas():
    """Mostra estatísticas dos militares no sistema"""
    print("\n📊 ESTATÍSTICAS DO SISTEMA:")
    print("=" * 50)
    
    total_militares = Militar.objects.count()
    militares_ativos = Militar.objects.filter(situacao='AT').count()
    
    print(f"Total de militares: {total_militares}")
    print(f"Militares ativos: {militares_ativos}")
    
    if militares_ativos > 0:
        print("\n📈 Distribuição por posto:")
        postos = Militar.objects.filter(situacao='AT').values('posto_graduacao').annotate(
            count=django.db.models.Count('id')
        ).order_by('posto_graduacao')
        
        for posto in postos:
            nome_posto = dict(POSTO_GRADUACAO_CHOICES).get(posto['posto_graduacao'], posto['posto_graduacao'])
            print(f"  {nome_posto}: {posto['count']}")
        
        print("\n📈 Distribuição por quadro:")
        quadros = Militar.objects.filter(situacao='AT').values('quadro').annotate(
            count=django.db.models.Count('id')
        ).order_by('quadro')
        
        for quadro in quadros:
            nome_quadro = dict(QUADRO_CHOICES).get(quadro['quadro'], quadro['quadro'])
            print(f"  {nome_quadro}: {quadro['count']}")

def main():
    """Função principal"""
    print("🚀 SCRIPT DE IMPORTAÇÃO DE MILITARES - ARQUIVO 2")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Mostrar estatísticas antes da importação
    mostrar_estatisticas()
    
    # Importar militares
    importar_militares()
    
    # Mostrar estatísticas após a importação
    print("\n" + "=" * 50)
    mostrar_estatisticas()
    
    print(f"\n⏰ Finalizado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("✅ Script concluído!")

if __name__ == '__main__':
    main() 