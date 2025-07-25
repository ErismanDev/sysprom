#!/usr/bin/env python
"""
Script para atualizar nomes e RGs dos militares conforme o arquivo Excel
"""

import os
import sys
import django
import csv
import unicodedata
import re
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.db import transaction

def normalizar_texto(texto):
    """
    Normaliza texto removendo caracteres especiais e acentos
    """
    if not texto:
        return ""
    
    # Normalizar unicode
    texto = unicodedata.normalize('NFD', texto)
    
    # Remover acentos
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    
    return texto

def limpar_cpf(cpf):
    """
    Remove caracteres especiais do CPF
    """
    if not cpf:
        return ""
    return re.sub(r'[^\d]', '', cpf)

def mapear_posto_graduacao(posto_excel):
    """
    Mapeia o posto/graduação do Excel para o formato do sistema
    """
    mapeamento = {
        'CORONEL': 'CB',
        'TENENTE CORONEL': 'TC',
        'MAJOR': 'MJ',
        'CAPITÃO': 'CP',
        '1° TENENTE': '1T',
        '1º TENENTE': '1T',
        '2° TENENTE': '2T',
        '2º TENENTE': '2T',
        'ASPIRANTE A OFICIAL': 'AS',
        'ALUNO DE ADAPTAÇÃO': 'AA',
        'SUBTENENTE': 'ST',
        '1° SARGENTO': '1S',
        '1º SARGENTO': '1S',
        '2° SARGENTO': '2S',
        '2º SARGENTO': '2S',
        '3° SARGENTO': '3S',
        '3º SARGENTO': '3S',
        'CABO': 'CAB',
        'SOLDADO': 'SD',
        'NVRR': 'NVRR'
    }
    return mapeamento.get(posto_excel.upper(), posto_excel[:4])  # Limitar a 4 caracteres se não mapeado

def mapear_quadro(quadro_excel):
    """
    Mapeia o quadro do Excel para o formato do sistema
    """
    mapeamento = {
        'COMBATENTE': 'COMB',
        'SAÚDE': 'SAUDE',
        'ENGENHEIRO': 'ENG',
        'COMPLEMENTAR': 'COMP',
        'NVRR': 'NVRR',
        'PRAÇAS': 'PRACAS'
    }
    return mapeamento.get(quadro_excel.upper(), quadro_excel)

def converter_data(data_str):
    """
    Converte data do formato dd/mm/yyyy para objeto Date
    """
    if not data_str:
        return None
    
    try:
        # Remover espaços e caracteres especiais
        data_str = data_str.strip()
        if '/' in data_str:
            dia, mes, ano = data_str.split('/')
            return datetime(int(ano), int(mes), int(dia)).date()
        else:
            return None
    except:
        return None

def atualizar_militares():
    """
    Atualiza os militares com dados do arquivo Excel
    """
    print("🔄 Atualizando militares com dados do arquivo Excel...")
    print("=" * 70)
    
    # Caminho do arquivo CSV
    arquivo_csv = "backups/militares_20250724_182637.csv"
    
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        return
    
    # Estatísticas
    total_processados = 0
    total_atualizados = 0
    total_nao_encontrados = 0
    erros = []
    
    # Tentar diferentes encodings
    encodings = ['latin1', 'cp1252', 'iso-8859-1', 'utf-8']
    reader = None
    
    for encoding in encodings:
        try:
            with open(arquivo_csv, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file, delimiter='\t')
                # Testar se consegue ler a primeira linha
                next(reader)
                print(f"✅ Arquivo lido com encoding: {encoding}")
                break
        except Exception as e:
            print(f"❌ Falha com encoding {encoding}: {e}")
            continue
    
    if not reader:
        print("❌ Não foi possível ler o arquivo com nenhum encoding")
        return
    
    # Ler o arquivo novamente com o encoding correto
    with open(arquivo_csv, 'r', encoding='latin1') as file:
        reader = csv.DictReader(file, delimiter='\t')
        
        for linha in reader:
            total_processados += 1
            
            try:
                # Extrair dados da linha
                matricula = linha.get('Matrícula', '').strip()
                nome_completo = linha.get('Nome Completo', '').strip()
                nome_guerra = linha.get('Nome de Guerra', '').strip()
                cpf = linha.get('CPF', '').strip()
                posto_graduacao = linha.get('Posto/Graduação', '').strip()
                quadro = linha.get('Quadro', '').strip()
                numeracao_antiguidade = linha.get('Numeração de Antiguidade', '').strip()
                data_nascimento = linha.get('Data de Nascimento', '').strip()
                data_ingresso = linha.get('Data de Ingresso', '').strip()
                data_ultima_promocao = linha.get('Data da Última Promoção', '').strip()
                email = linha.get('E-mail', '').strip()
                telefone = linha.get('Telefone', '').strip()
                celular = linha.get('Celular', '').strip()
                situacao = linha.get('Situação', '').strip()
                observacoes = linha.get('Observações', '').strip()
                
                # Limpar CPF
                cpf_limpo = limpar_cpf(cpf)
                
                # Buscar militar por CPF ou matrícula
                militar = None
                if cpf_limpo:
                    militar = Militar.objects.filter(cpf=cpf_limpo).first()
                
                if not militar and matricula:
                    militar = Militar.objects.filter(matricula=matricula).first()
                
                if not militar:
                    total_nao_encontrados += 1
                    print(f"   ⚠️  Militar não encontrado: {matricula} - {nome_completo}")
                    continue
                
                # Verificar se há mudanças
                mudancas = []
                
                # Atualizar nome completo
                if nome_completo and militar.nome_completo != nome_completo:
                    militar.nome_completo = nome_completo
                    mudancas.append(f"Nome: '{militar.nome_completo}' → '{nome_completo}'")
                
                # Atualizar nome de guerra
                if nome_guerra and militar.nome_guerra != nome_guerra:
                    militar.nome_guerra = nome_guerra
                    mudancas.append(f"Nome de Guerra: '{militar.nome_guerra}' → '{nome_guerra}'")
                
                # Atualizar posto/graduação
                posto_mapeado = mapear_posto_graduacao(posto_graduacao)
                if posto_mapeado and militar.posto_graduacao != posto_mapeado:
                    militar.posto_graduacao = posto_mapeado
                    mudancas.append(f"Posto: '{militar.posto_graduacao}' → '{posto_mapeado}'")
                
                # Atualizar quadro
                quadro_mapeado = mapear_quadro(quadro)
                if quadro_mapeado and militar.quadro != quadro_mapeado:
                    militar.quadro = quadro_mapeado
                    mudancas.append(f"Quadro: '{militar.quadro}' → '{quadro_mapeado}'")
                
                # Atualizar numeração de antiguidade
                if numeracao_antiguidade:
                    try:
                        numeracao = int(numeracao_antiguidade)
                        if militar.numeracao_antiguidade != numeracao:
                            militar.numeracao_antiguidade = numeracao
                            mudancas.append(f"Antiguidade: {militar.numeracao_antiguidade} → {numeracao}")
                    except ValueError:
                        pass
                
                # Atualizar datas
                data_nasc = converter_data(data_nascimento)
                if data_nasc and militar.data_nascimento != data_nasc:
                    militar.data_nascimento = data_nasc
                    mudancas.append(f"Data Nascimento: {militar.data_nascimento} → {data_nasc}")
                
                data_ing = converter_data(data_ingresso)
                if data_ing and militar.data_ingresso != data_ing:
                    militar.data_ingresso = data_ing
                    mudancas.append(f"Data Ingresso: {militar.data_ingresso} → {data_ing}")
                
                data_prom = converter_data(data_ultima_promocao)
                if data_prom and militar.data_promocao_atual != data_prom:
                    militar.data_promocao_atual = data_prom
                    mudancas.append(f"Data Promoção: {militar.data_promocao_atual} → {data_prom}")
                
                # Atualizar contatos
                if email and militar.email != email:
                    militar.email = email
                    mudancas.append(f"Email: '{militar.email}' → '{email}'")
                
                if telefone and militar.telefone != telefone:
                    militar.telefone = telefone
                    mudancas.append(f"Telefone: '{militar.telefone}' → '{telefone}'")
                
                if celular and militar.celular != celular:
                    militar.celular = celular
                    mudancas.append(f"Celular: '{militar.celular}' → '{celular}'")
                
                # Atualizar situação
                if situacao:
                    situacao_mapeada = 'AT' if situacao.upper() in ['ATIVO', 'AT'] else 'IN'
                    if militar.situacao != situacao_mapeada:
                        militar.situacao = situacao_mapeada
                        mudancas.append(f"Situação: '{militar.situacao}' → '{situacao_mapeada}'")
                
                # Atualizar observações
                if observacoes and militar.observacoes != observacoes:
                    militar.observacoes = observacoes
                    mudancas.append(f"Observações atualizadas")
                
                # Salvar se houve mudanças
                if mudancas:
                    militar.save()
                    total_atualizados += 1
                    print(f"   ✅ {militar.matricula} - {militar.nome_completo}")
                    for mudanca in mudancas:
                        print(f"      • {mudanca}")
                else:
                    print(f"   ℹ️  {militar.matricula} - {militar.nome_completo} (sem mudanças)")
                
            except Exception as e:
                erro_msg = f"Erro ao processar linha {total_processados}: {e}"
                erros.append(erro_msg)
                print(f"   ❌ {erro_msg}")
    
    # Resumo final
    print(f"\n" + "=" * 70)
    print(f"📊 RESUMO DA ATUALIZAÇÃO:")
    print(f"   • Total processados: {total_processados}")
    print(f"   • Total atualizados: {total_atualizados}")
    print(f"   • Não encontrados: {total_nao_encontrados}")
    print(f"   • Erros: {len(erros)}")
    
    if erros:
        print(f"\n❌ ERROS ENCONTRADOS:")
        for erro in erros[:10]:  # Mostrar apenas os primeiros 10 erros
            print(f"   • {erro}")
        if len(erros) > 10:
            print(f"   ... e mais {len(erros) - 10} erros")
    
    return {
        'total_processados': total_processados,
        'total_atualizados': total_atualizados,
        'total_nao_encontrados': total_nao_encontrados,
        'erros': erros
    }

def main():
    """Função principal"""
    print("🚀 Atualizando militares com dados do arquivo Excel...")
    print("=" * 70)
    
    with transaction.atomic():
        resultado = atualizar_militares()
        
        print(f"\n" + "=" * 70)
        print(f"✅ OPERAÇÃO CONCLUÍDA!")
        print(f"   • Militares processados: {resultado['total_processados']}")
        print(f"   • Militares atualizados: {resultado['total_atualizados']}")
        print(f"   • Militares não encontrados: {resultado['total_nao_encontrados']}")
        print(f"   • Erros: {len(resultado['erros'])}")
        
        if resultado['total_atualizados'] > 0:
            print(f"\n🎉 Atualização realizada com sucesso!")
            print(f"💡 {resultado['total_atualizados']} militares foram atualizados")
        else:
            print(f"\nℹ️  Nenhum militar foi atualizado")

if __name__ == '__main__':
    main() 