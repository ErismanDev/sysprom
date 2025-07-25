#!/usr/bin/env python
"""
Script para importar dados do arquivo CSV e substituir militares e usuários existentes
"""

import os
import sys
import django
import csv
import unicodedata
import re
from datetime import datetime
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
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
    
    # Converter para maiúsculas
    texto = texto.upper()
    
    return texto.strip()

def mapear_posto_graduacao(posto_csv):
    """
    Mapeia o posto/graduação do CSV para o código do sistema
    """
    mapeamento = {
        'CORONEL': 'CB',
        'TENENTE CORONEL': 'TC',
        'MAJOR': 'MJ',
        'CAPITÃO': 'CP',
        'CAPITO': 'CP',  # Com problema de encoding
        '1º TENENTE': '1T',
        '1 TENENTE': '1T',  # Com problema de encoding
        '2º TENENTE': '2T',
        '2 TENENTE': '2T',  # Com problema de encoding
        'SUBTENENTE': 'ST',
        '1º SARGENTO': '1S',
        '1 SARGENTO': '1S',  # Com problema de encoding
        '2º SARGENTO': '2S',
        '2 SARGENTO': '2S',  # Com problema de encoding
        '3º SARGENTO': '3S',
        '3 SARGENTO': '3S',  # Com problema de encoding
        'CABO': 'CAB',
        'SOLDADO': 'SD',
    }
    
    return mapeamento.get(posto_csv.strip(), 'SD')

def mapear_quadro(quadro_csv):
    """
    Mapeia o quadro do CSV para o código do sistema
    """
    mapeamento = {
        'COMBATENTE': 'COMB',
        'COMPLEMENTAR': 'COMP',
        'ENGENHEIRO': 'ENG',
        'NVRR': 'NVRR',
    }
    
    return mapeamento.get(quadro_csv.strip(), 'COMB')

def mapear_situacao(situacao_csv):
    """
    Mapeia a situação do CSV para o código do sistema
    """
    if not situacao_csv:
        return 'AT'
    
    situacao = situacao_csv.strip().upper()
    
    mapeamento = {
        'ATIVO': 'AT',
        'INATIVO': 'IN',
        'TRANSFERIDO': 'TR',
        'APOSENTADO': 'AP',
        'EXCLUÍDO': 'EX',
        'EXCLUÍDO': 'EX',
    }
    
    return mapeamento.get(situacao, 'AT')

def parse_data(data_str):
    """
    Converte string de data para objeto date
    """
    if not data_str or data_str.strip() == '':
        return None
    
    try:
        # Tentar formato DD/MM/YYYY
        return datetime.strptime(data_str.strip(), '%d/%m/%Y').date()
    except ValueError:
        try:
            # Tentar formato YYYY-MM-DD
            return datetime.strptime(data_str.strip(), '%Y-%m-%d').date()
        except ValueError:
            print(f"⚠️  Data inválida: {data_str}")
            return None

def limpar_telefone(telefone):
    """
    Limpa e formata telefone
    """
    if not telefone:
        return ""
    
    # Remover caracteres não numéricos
    numeros = re.sub(r'[^\d]', '', telefone)
    
    if len(numeros) >= 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    
    return telefone.strip()

def limpar_cpf(cpf):
    """
    Limpa e formata CPF
    """
    if not cpf:
        return ""
    
    # Remover caracteres não numéricos
    numeros = re.sub(r'[^\d]', '', cpf)
    
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    
    return cpf.strip()

def determinar_sexo(nome_completo):
    """
    Tenta determinar o sexo baseado no nome (heurística simples)
    """
    if not nome_completo:
        return 'M'
    
    nome = nome_completo.upper()
    
    # Nomes femininos comuns
    nomes_femininos = [
        'ANA', 'MARIA', 'BEATRIZ', 'PRYCILLA', 'ELISABETH', 'HÉLIDA', 
        'GILDETH', 'ANALICE', 'MARCELLA', 'HLIDA', 'GILDETH', 'ANALICE'
    ]
    
    for nome_fem in nomes_femininos:
        if nome_fem in nome:
            return 'F'
    
    return 'M'

@transaction.atomic
def importar_dados_csv():
    """
    Importa dados do arquivo CSV e substitui militares e usuários existentes
    """
    print("🚀 Iniciando importação de dados do CSV...")
    
    # Primeiro, limpar dados existentes
    print("🗑️  Limpando dados existentes...")
    
    # Deletar usuários vinculados a militares
    usuarios_para_deletar = User.objects.filter(militar__isnull=False)
    print(f"  - Deletando {usuarios_para_deletar.count()} usuários vinculados a militares")
    usuarios_para_deletar.delete()
    
    # Deletar todos os militares
    total_militares = Militar.objects.count()
    print(f"  - Deletando {total_militares} militares existentes")
    Militar.objects.all().delete()
    
    # Ler arquivo CSV
    arquivo_csv = 'backups/militares_20250724_182637.csv'
    
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo {arquivo_csv} não encontrado!")
        return False
    
    print(f"📖 Lendo arquivo: {arquivo_csv}")
    
    militares_criados = 0
    usuarios_criados = 0
    erros = []
    
    with open(arquivo_csv, 'r', encoding='utf-8', errors='ignore') as arquivo:
        leitor = csv.DictReader(arquivo, delimiter='\t')
        
        for linha_num, linha in enumerate(leitor, 2):  # Começar do 2 pois linha 1 é cabeçalho
            try:
                # Extrair dados da linha
                matricula = linha.get('Matrcula', '').strip()
                nome_completo = linha.get('Nome Completo', '').strip()
                nome_guerra = linha.get('Nome de Guerra', '').strip()
                cpf = linha.get('CPF', '').strip()
                posto_csv = linha.get('Posto/Graduao', '').strip()
                quadro_csv = linha.get('Quadro', '').strip()
                numeracao_antiguidade = linha.get('Numerao de Antiguidade', '').strip()
                data_nascimento_str = linha.get('Data de Nascimento', '').strip()
                data_ingresso_str = linha.get('Data de Ingresso', '').strip()
                data_promocao_str = linha.get('Data daltima Promoo', '').strip()
                email = linha.get('E-mail', '').strip()
                telefone = linha.get('Telefone', '').strip()
                celular = linha.get('Celular', '').strip()
                situacao_csv = linha.get('Situao', '').strip()
                observacoes = linha.get('Observaes', '').strip()
                
                # Validar dados obrigatórios
                if not matricula or not nome_completo or not cpf:
                    print(f"⚠️  Linha {linha_num}: Dados obrigatórios faltando")
                    continue
                
                # Processar dados
                posto_graduacao = mapear_posto_graduacao(posto_csv)
                quadro = mapear_quadro(quadro_csv)
                situacao = mapear_situacao(situacao_csv)
                sexo = determinar_sexo(nome_completo)
                
                # Processar datas
                data_nascimento = parse_data(data_nascimento_str)
                data_ingresso = parse_data(data_ingresso_str)
                data_promocao = parse_data(data_promocao_str)
                
                # Usar data atual se não houver data de promoção
                if not data_promocao:
                    data_promocao = timezone.now().date()
                
                # Limpar e formatar dados
                cpf_limpo = limpar_cpf(cpf)
                telefone_limpo = limpar_telefone(telefone)
                celular_limpo = limpar_telefone(celular)
                
                # Converter numeração de antiguidade
                try:
                    numeracao_int = int(numeracao_antiguidade) if numeracao_antiguidade else None
                except ValueError:
                    numeracao_int = None
                
                # Criar militar
                militar = Militar(
                    matricula=matricula,
                    nome_completo=nome_completo,
                    nome_guerra=nome_guerra,
                    cpf=cpf_limpo,
                    rg='',  # Não disponível no CSV
                    orgao_expedidor='',  # Não disponível no CSV
                    data_nascimento=data_nascimento or timezone.now().date(),
                    sexo=sexo,
                    quadro=quadro,
                    posto_graduacao=posto_graduacao,
                    data_ingresso=data_ingresso or timezone.now().date(),
                    data_promocao_atual=data_promocao,
                    situacao=situacao,
                    email=email,
                    telefone=telefone_limpo,
                    celular=celular_limpo,
                    observacoes=observacoes,
                    numeracao_antiguidade=numeracao_int
                )
                
                militar.save()
                militares_criados += 1
                
                # Criar usuário para o militar
                try:
                    username = f"militar_{matricula}"
                    email_usuario = email if email else f"{username}@cbmepi.pi.gov.br"
                    
                    # Verificar se username já existe
                    if User.objects.filter(username=username).exists():
                        username = f"{username}_{militar.pk}"
                    
                    # Separar nome em first_name e last_name
                    nomes = nome_completo.split()
                    first_name = nomes[0] if nomes else ''
                    last_name = ' '.join(nomes[1:]) if len(nomes) > 1 else ''
                    
                    # Criar usuário
                    user = User.objects.create_user(
                        username=username,
                        email=email_usuario,
                        first_name=first_name,
                        last_name=last_name,
                        password=cpf_limpo.replace('.', '').replace('-', '').replace('/', '')  # CPF como senha
                    )
                    
                    # Vincular usuário ao militar
                    militar.user = user
                    militar.save(update_fields=['user'])
                    
                    usuarios_criados += 1
                    
                except Exception as e:
                    print(f"⚠️  Erro ao criar usuário para {matricula}: {e}")
                    erros.append(f"Usuário {matricula}: {e}")
                
                # Mostrar progresso a cada 50 registros
                if militares_criados % 50 == 0:
                    print(f"  ✅ Processados {militares_criados} militares...")
                
            except Exception as e:
                print(f"❌ Erro na linha {linha_num}: {e}")
                erros.append(f"Linha {linha_num}: {e}")
                continue
    
    print("\n" + "="*60)
    print("📊 RESUMO DA IMPORTAÇÃO")
    print("="*60)
    print(f"✅ Militares criados: {militares_criados}")
    print(f"✅ Usuários criados: {usuarios_criados}")
    print(f"❌ Erros encontrados: {len(erros)}")
    
    if erros:
        print("\n📋 Primeiros 10 erros:")
        for erro in erros[:10]:
            print(f"  - {erro}")
    
    print("\n🏁 Importação concluída!")
    return True

def verificar_importacao():
    """
    Verifica se a importação foi bem-sucedida
    """
    print("\n🔍 Verificando importação...")
    
    total_militares = Militar.objects.count()
    total_usuarios = User.objects.count()
    usuarios_com_militar = User.objects.filter(militar__isnull=False).count()
    
    print(f"📊 Total de militares: {total_militares}")
    print(f"📊 Total de usuários: {total_usuarios}")
    print(f"📊 Usuários vinculados a militares: {usuarios_com_militar}")
    
    # Verificar alguns militares
    print("\n📋 Primeiros 5 militares importados:")
    for militar in Militar.objects.all()[:5]:
        print(f"  - {militar.matricula}: {militar.nome_completo} ({militar.get_posto_graduacao_display()})")
        if militar.user:
            print(f"    Usuário: {militar.user.username}")
    
    return total_militares > 0

def main():
    """
    Função principal
    """
    print("🚀 SCRIPT DE IMPORTAÇÃO DE DADOS CSV")
    print("="*60)
    
    # Confirmar com o usuário
    resposta = input("⚠️  ATENÇÃO: Este script irá DELETAR todos os militares e usuários existentes!\nDeseja continuar? (s/N): ")
    
    if resposta.lower() != 's':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    # Fazer backup antes de importar
    print("\n💾 Fazendo backup dos dados atuais...")
    from django.core import serializers
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_antes_importacao_{timestamp}.json"
    
    try:
        # Backup de militares
        militares_data = serializers.serialize('json', Militar.objects.all())
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(militares_data)
        print(f"✅ Backup salvo em: {backup_file}")
    except Exception as e:
        print(f"⚠️  Erro ao fazer backup: {e}")
    
    # Importar dados
    sucesso = importar_dados_csv()
    
    if sucesso:
        verificar_importacao()
        print("\n🎉 Importação realizada com sucesso!")
    else:
        print("\n❌ Erro na importação!")

if __name__ == '__main__':
    main() 