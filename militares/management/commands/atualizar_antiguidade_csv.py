import csv
from django.core.management.base import BaseCommand
from militares.models import Militar

class Command(BaseCommand):
    help = 'Atualiza o número de antiguidade dos militares conforme o arquivo CSV de backup'

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
            help='Executa sem salvar no banco'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        atualizados = 0
        nao_encontrados = 0
        with open(file_path, 'r', encoding='utf-8', errors='replace') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            for row in reader:
                matricula = row.get('Matr ula') or row.get('Matrícula')
                antiguidade = row.get('Numera  o de Antiguidade') or row.get('Numeração de Antiguidade')
                if not matricula or not antiguidade:
                    continue
                try:
                    militar = Militar.objects.get(matricula=matricula.strip())
                    if str(militar.antiguidade) != str(antiguidade.strip()):
                        self.stdout.write(f"{militar.nome_guerra} ({matricula}): {militar.antiguidade} -> {antiguidade}")
                        if not dry_run:
                            militar.antiguidade = antiguidade.strip()
                            militar.save()
                        atualizados += 1
                except Militar.DoesNotExist:
                    nao_encontrados += 1
        self.stdout.write(self.style.SUCCESS(f"{atualizados} militares atualizados."))
        if nao_encontrados:
            self.stdout.write(self.style.WARNING(f"{nao_encontrados} matrículas não encontradas no banco.")) 