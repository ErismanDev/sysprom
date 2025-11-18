import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from militares.models import Militar
from django.db import transaction


class Command(BaseCommand):
    help = 'Importa e atualiza militares a partir do arquivo CSV de backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='backups/militares_20250724_182637.csv',
            help='Caminho para o arquivo CSV'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']

        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Arquivo não encontrado: {file_path}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Iniciando importação do arquivo: {file_path}')
        )

        # Mapeamento de postos/graduações
        posto_mapping = {
            'CORONEL': 'CB',
            'TENENTE CORONEL': 'TC',
            'MAJOR': 'MJ',
            'CAPITÃO': 'CP',
            '1º TENENTE': '1T',
            '2º TENENTE': '2T',
            'ASPIRANTE': 'AS',
            'ALUNO ASPIRANTE': 'AA',
            'SUBTENENTE': 'ST',
            '1º SARGENTO': '1S',
            '2º SARGENTO': '2S',
            '3º SARGENTO': '3S',
            'CABO': 'CAB',
            'SOLDADO': 'SD',
        }

        # Mapeamento de quadros
        quadro_mapping = {
            'Combatente': 'COMB',
            'Complementar': 'COMP',
            'Engenheiro': 'ENG',
            'NVRR': 'NVRR',
        }

        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        # Tentar diferentes codificações
        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        csvfile = None
        
        for encoding in encodings:
            try:
                csvfile = open(file_path, 'r', encoding=encoding)
                # Testar se consegue ler a primeira linha
                csvfile.readline()
                csvfile.seek(0)  # Voltar ao início
                self.stdout.write(f'Arquivo aberto com codificação: {encoding}')
                break
            except UnicodeDecodeError:
                if csvfile:
                    csvfile.close()
                continue
        
        if not csvfile:
            self.stdout.write(
                self.style.ERROR('Não foi possível abrir o arquivo com nenhuma codificação conhecida')
            )
            return

        with csvfile:
            # Pular a primeira linha (cabeçalho)
            next(csvfile)
            
            reader = csv.reader(csvfile, delimiter='\t')
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    if len(row) < 14:
                        self.stdout.write(
                            self.style.WARNING(f'Linha {row_num}: Dados insuficientes - {row}')
                        )
                        stats['skipped'] += 1
                        continue

                    # Extrair dados da linha
                    matricula = row[0].strip()
                    nome_completo = row[1].strip()
                    nome_guerra = row[2].strip()
                    cpf = row[3].strip()
                    posto_graduacao = row[4].strip()
                    quadro = row[5].strip()
                    numeracao_antiguidade = row[6].strip()
                    data_nascimento = row[7].strip()
                    data_ingresso = row[8].strip()
                    data_ultima_promocao = row[9].strip()
                    email = row[10].strip()
                    telefone = row[11].strip()
                    celular = row[12].strip()
                    situacao = row[13].strip()
                    observacoes = row[14].strip() if len(row) > 14 else ''

                    # Validar dados obrigatórios
                    if not matricula or not nome_completo:
                        self.stdout.write(
                            self.style.WARNING(f'Linha {row_num}: Matrícula ou nome vazio')
                        )
                        stats['skipped'] += 1
                        continue

                    # Converter datas
                    try:
                        data_nasc = datetime.strptime(data_nascimento, '%d/%m/%Y').date() if data_nascimento else None
                    except ValueError:
                        data_nasc = None

                    try:
                        data_ing = datetime.strptime(data_ingresso, '%d/%m/%Y').date() if data_ingresso else None
                    except ValueError:
                        data_ing = None

                    try:
                        data_prom = datetime.strptime(data_ultima_promocao, '%d/%m/%Y').date() if data_ultima_promocao else None
                    except ValueError:
                        data_prom = None

                    # Converter numeração de antiguidade
                    try:
                        num_ant = int(numeracao_antiguidade) if numeracao_antiguidade else None
                    except ValueError:
                        num_ant = None

                    # Mapear posto/graduação
                    posto_codigo = posto_mapping.get(posto_graduacao, posto_graduacao)

                    # Mapear quadro
                    quadro_codigo = quadro_mapping.get(quadro, quadro)

                    # Mapear situação
                    classificacao_codigo = 'ATIVO' if situacao.upper() in ['ATIVO', 'ATIVA'] else 'INATIVO'

                    # Buscar militar existente por matrícula
                    militar = Militar.objects.filter(matricula=matricula).first()

                    if militar:
                        # Atualizar militar existente
                        if not dry_run:
                            militar.nome_completo = nome_completo
                            militar.nome_guerra = nome_guerra
                            militar.cpf = cpf
                            militar.posto_graduacao = posto_codigo
                            militar.quadro = quadro_codigo
                            militar.numeracao_antiguidade = num_ant
                            militar.data_nascimento = data_nasc
                            militar.data_ingresso = data_ing
                            militar.data_promocao_atual = data_prom
                            militar.email = email
                            militar.telefone = telefone
                            militar.celular = celular
                            militar.classificacao = classificacao_codigo
                            militar.observacoes = observacoes
                            militar.save()

                        self.stdout.write(
                            self.style.SUCCESS(f'Atualizado: {matricula} - {nome_completo}')
                        )
                        stats['updated'] += 1
                    else:
                        # Criar novo militar
                        if not dry_run:
                            Militar.objects.create(
                                matricula=matricula,
                                nome_completo=nome_completo,
                                nome_guerra=nome_guerra,
                                cpf=cpf,
                                posto_graduacao=posto_codigo,
                                quadro=quadro_codigo,
                                numeracao_antiguidade=num_ant,
                                data_nascimento=data_nasc,
                                data_ingresso=data_ing,
                                data_promocao_atual=data_prom,
                                email=email,
                                telefone=telefone,
                                celular=celular,
                                classificacao=classificacao_codigo,
                                observacoes=observacoes,
                            )

                        self.stdout.write(
                            self.style.SUCCESS(f'Criado: {matricula} - {nome_completo}')
                        )
                        stats['created'] += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Erro na linha {row_num}: {str(e)} - {row}')
                    )
                    stats['errors'] += 1

        # Relatório final
        self.stdout.write('\n' + '='*50)
        self.stdout.write('RELATÓRIO DE IMPORTAÇÃO')
        self.stdout.write('='*50)
        self.stdout.write(f'Militares criados: {stats["created"]}')
        self.stdout.write(f'Militares atualizados: {stats["updated"]}')
        self.stdout.write(f'Linhas ignoradas: {stats["skipped"]}')
        self.stdout.write(f'Erros: {stats["errors"]}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nMODO DRY-RUN: Nenhuma alteração foi feita no banco de dados')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nImportação concluída com sucesso!')
            ) 