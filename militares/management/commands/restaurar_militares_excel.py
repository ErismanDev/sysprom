import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from militares.models import Militar
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Restaura a tabela de militares a partir do arquivo Excel na pasta backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo',
            type=str,
            default='Efetivo CBMEPI Atito SI Promoção 2.xlsx',
            help='Nome do arquivo Excel na pasta backup (padrão: Efetivo CBMEPI Atito SI Promoção 2.xlsx)'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa todos os militares existentes antes da restauração'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem salvar no banco'
        )
        parser.add_argument(
            '--sem-transacao',
            action='store_true',
            help='Processa sem transação atômica (mais lento mas mais seguro)'
        )

    def handle(self, *args, **options):
        arquivo = options['arquivo']
        limpar = options['limpar']
        dry_run = options['dry_run']
        sem_transacao = options['sem_transacao']
        
        # Caminho do arquivo
        caminho_arquivo = os.path.join('backups', arquivo)
        
        if not os.path.exists(caminho_arquivo):
            self.stdout.write(
                self.style.ERROR(f'Arquivo não encontrado: {caminho_arquivo}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando restauração a partir do arquivo: {caminho_arquivo}')
        )
        
        try:
            # Ler o arquivo Excel
            df = pd.read_excel(caminho_arquivo)
            self.stdout.write(f'Total de registros encontrados: {len(df)}')
            
            # Mostrar as colunas disponíveis
            self.stdout.write(f'Colunas disponíveis: {list(df.columns)}')
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('MODO DE TESTE - Nenhum dado será salvo no banco')
                )
                self._processar_dados_teste(df)
            else:
                if limpar:
                    self._limpar_militares_existentes()
                
                if sem_transacao:
                    self._processar_dados_sem_transacao(df)
                else:
                    with transaction.atomic():
                        self._processar_dados(df)
                
                self.stdout.write(
                    self.style.SUCCESS('Restauração concluída com sucesso!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a restauração: {str(e)}')
            )
            logger.error(f'Erro na restauração: {str(e)}', exc_info=True)

    def _limpar_militares_existentes(self):
        """Remove todos os militares existentes"""
        count = Militar.objects.count()
        Militar.objects.all().delete()
        self.stdout.write(f'Removidos {count} militares existentes')

    def _processar_dados_teste(self, df):
        """Processa os dados em modo de teste"""
        for index, row in df.iterrows():
            try:
                militar_data = self._extrair_dados_militar(row)
                self.stdout.write(f'Registro {index + 1}: {militar_data["nome_completo"]} - {militar_data["matricula"]}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro no registro {index + 1}: {str(e)}')
                )

    def _processar_dados_sem_transacao(self, df):
        """Processa os dados sem transação atômica"""
        sucessos = 0
        erros = 0
        
        for index, row in df.iterrows():
            try:
                militar_data = self._extrair_dados_militar(row)
                
                # Verificar se o militar já existe
                militar_existente = Militar.objects.filter(matricula=militar_data['matricula']).first()
                
                if militar_existente:
                    # Atualizar militar existente
                    for key, value in militar_data.items():
                        if hasattr(militar_existente, key):
                            setattr(militar_existente, key, value)
                    militar_existente.save()
                    self.stdout.write(f'Atualizado: {militar_data["nome_completo"]}')
                else:
                    # Criar novo militar
                    Militar.objects.create(**militar_data)
                    self.stdout.write(f'Criado: {militar_data["nome_completo"]}')
                
                sucessos += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro no registro {index + 1}: {str(e)}')
                )
                erros += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Processamento concluído: {sucessos} sucessos, {erros} erros')
        )

    def _processar_dados(self, df):
        """Processa os dados e salva no banco"""
        sucessos = 0
        erros = 0
        
        for index, row in df.iterrows():
            try:
                militar_data = self._extrair_dados_militar(row)
                
                # Verificar se o militar já existe
                militar_existente = Militar.objects.filter(matricula=militar_data['matricula']).first()
                
                if militar_existente:
                    # Atualizar militar existente
                    for key, value in militar_data.items():
                        if hasattr(militar_existente, key):
                            setattr(militar_existente, key, value)
                    militar_existente.save()
                    self.stdout.write(f'Atualizado: {militar_data["nome_completo"]}')
                else:
                    # Criar novo militar
                    Militar.objects.create(**militar_data)
                    self.stdout.write(f'Criado: {militar_data["nome_completo"]}')
                
                sucessos += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro no registro {index + 1}: {str(e)}')
                )
                erros += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Processamento concluído: {sucessos} sucessos, {erros} erros')
        )

    def _extrair_dados_militar(self, row):
        """Extrai e converte os dados do Excel para o formato do modelo Militar"""
        
        # Mapeamento de colunas (ajuste conforme necessário)
        mapeamento_colunas = {
            'matricula': ['Matrícula', 'MATRICULA', 'matricula'],
            'nome_completo': ['Nome Completo', 'NOME_COMPLETO', 'nome_completo', 'Nome'],
            'nome_guerra': ['Nome de Guerra', 'NOME_GUERRA', 'nome_guerra'],
            'cpf': ['CPF', 'cpf'],
            'rg': ['RG', 'rg'],
            'orgao_expedidor': ['Órgão Expedidor', 'ORGAO_EXPEDIDOR', 'orgao_expedidor'],
            'data_nascimento': ['Data de Nascimento', 'DATA_NASCIMENTO', 'data_nascimento'],
            'sexo': ['Sexo', 'SEXO', 'sexo'],
            'quadro': ['Quadro', 'QUADRO', 'quadro'],
            'posto_graduacao': ['Posto/Graduação', 'POSTO_GRADUACAO', 'posto_graduacao', 'Posto'],
            'data_ingresso': ['Data de Ingresso', 'DATA_INGRESSO', 'data_ingresso'],
            'data_promocao_atual': ['Data da Promoção Atual', 'DATA_PROMOCAO_ATUAL', 'data_promocao_atual'],
            'situacao': ['Situação', 'SITUACAO', 'situacao'],
            'email': ['E-mail', 'EMAIL', 'email'],
            'telefone': ['Telefone', 'TELEFONE', 'telefone'],
            'celular': ['Celular', 'CELULAR', 'celular'],
            'numeracao_antiguidade': ['Numeração de Antiguidade', 'NUMERACAO_ANTIGUIDADE', 'numeracao_antiguidade'],
        }
        
        dados = {}
        
        # Extrair dados usando o mapeamento
        for campo_modelo, possiveis_colunas in mapeamento_colunas.items():
            valor = None
            for coluna in possiveis_colunas:
                if coluna in row.index and pd.notna(row[coluna]):
                    valor = row[coluna]
                    break
            
            if valor is not None:
                # Converter tipos de dados
                if campo_modelo in ['data_nascimento', 'data_ingresso', 'data_promocao_atual']:
                    if isinstance(valor, str):
                        try:
                            valor = pd.to_datetime(valor).date()
                        except:
                            valor = None
                    elif hasattr(valor, 'date'):
                        valor = valor.date()
                
                elif campo_modelo == 'numeracao_antiguidade':
                    try:
                        valor = int(valor) if valor else None
                    except:
                        valor = None
                
                elif campo_modelo == 'sexo':
                    if isinstance(valor, str):
                        valor = valor.upper()[:1]  # Primeira letra
                        if valor not in ['M', 'F']:
                            valor = 'M'  # Padrão
                
                elif campo_modelo == 'posto_graduacao':
                    if isinstance(valor, str):
                        valor = valor.upper()
                        # Mapeamento de postos (ajuste conforme necessário)
                        mapeamento_postos = {
                            'CORONEL': 'CB',
                            'TENENTE CORONEL': 'TC',
                            'MAJOR': 'MJ',
                            'CAPITÃO': 'CP',
                            '1º TENENTE': '1T',
                            '2º TENENTE': '2T',
                            'ASPIRANTE': 'AS',
                            'ALUNO ADAPTAÇÃO': 'AA',
                            'NAVEGADOR': 'NVRR',
                            'SUBTENENTE': 'ST',
                            '1º SARGENTO': '1S',
                            '2º SARGENTO': '2S',
                            '3º SARGENTO': '3S',
                            'CABO': 'CAB',
                            'SOLDADO': 'SD',
                        }
                        valor = mapeamento_postos.get(valor, valor)
                
                elif campo_modelo == 'quadro':
                    if isinstance(valor, str):
                        valor = valor.upper()
                        # Mapeamento de quadros
                        mapeamento_quadros = {
                            'COMBATENTE': 'COMB',
                            'SAÚDE': 'SAUDE',
                            'ENGENHEIRO': 'ENG',
                            'COMPLEMENTAR': 'COMP',
                            'NAVEGADOR': 'NVRR',
                            'PRAÇAS': 'PRACAS',
                        }
                        valor = mapeamento_quadros.get(valor, valor)
                
                elif campo_modelo == 'situacao':
                    if isinstance(valor, str):
                        valor = valor.upper()
                        # Mapeamento de situações
                        mapeamento_situacoes = {
                            'ATIVO': 'AT',
                            'INATIVO': 'IN',
                            'TRANSFERIDO': 'TR',
                            'APOSENTADO': 'AP',
                            'EXONERADO': 'EX',
                        }
                        valor = mapeamento_situacoes.get(valor, valor)
                
                # Truncar campos de texto se necessário
                if campo_modelo in ['matricula', 'nome_completo', 'nome_guerra', 'cpf', 'rg', 'orgao_expedidor', 'email', 'telefone', 'celular']:
                    if isinstance(valor, str):
                        # Limitar tamanho conforme definido no modelo
                        limites = {
                            'matricula': 20,
                            'nome_completo': 200,
                            'nome_guerra': 100,
                            'cpf': 14,
                            'rg': 20,
                            'orgao_expedidor': 20,
                            'email': 254,  # Padrão Django
                            'telefone': 20,
                            'celular': 20,
                        }
                        if campo_modelo in limites:
                            valor = valor[:limites[campo_modelo]]
                
                dados[campo_modelo] = valor
        
        # Valores padrão para campos obrigatórios
        if 'situacao' not in dados or not dados['situacao']:
            dados['situacao'] = 'AT'
        
        if 'quadro' not in dados or not dados['quadro']:
            dados['quadro'] = 'COMB'
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['matricula', 'nome_completo', 'nome_guerra', 'cpf', 'data_nascimento', 'posto_graduacao', 'data_ingresso']
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                raise ValueError(f'Campo obrigatório não encontrado ou vazio: {campo}')
        
        return dados 