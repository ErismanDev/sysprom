from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection


class Command(BaseCommand):
    help = 'Ajusta as sequências (SERIAL) das tabelas do app militares para evitar erro de PK duplicada.'

    def handle(self, *args, **options):
        app_config = apps.get_app_config('militares')
        with connection.cursor() as cursor:
            for model in app_config.get_models():
                try:
                    meta = model._meta
                    table = meta.db_table
                    pk = meta.pk
                    # Considerar apenas AutoField/BigAutoField
                    if not hasattr(pk, 'column'):
                        continue
                    pk_column = pk.column
                    # Obter valor máximo atual do PK
                    cursor.execute(f'SELECT MAX("{pk_column}") FROM "{table}"')
                    row = cursor.fetchone()
                    max_id = row[0] if row else None
                    # Obter o nome da sequência associada à coluna
                    cursor.execute("SELECT pg_get_serial_sequence(%s, %s)", [table, pk_column])
                    seq_row = cursor.fetchone()
                    seq_name = seq_row[0] if seq_row else None
                    if not seq_name:
                        continue
                    if max_id is None:
                        # Tabela vazia: setval para 1 e is_called = false
                        cursor.execute('SELECT setval(%s, 1, false)', [seq_name])
                        self.stdout.write(self.style.WARNING(f'{table}: sequência {seq_name} definida para 1 (tabela vazia)'))
                    else:
                        # Ajustar sequência para MAX(id)
                        cursor.execute('SELECT setval(%s, %s, true)', [seq_name, max_id])
                        self.stdout.write(self.style.SUCCESS(f'{table}: sequência {seq_name} ajustada para {max_id}'))
                except Exception as e:
                    # Ignorar tabelas que não existem (migrations pendentes) e seguir
                    self.stdout.write(self.style.WARNING(f'Saltando {model._meta.db_table}: {e.__class__.__name__}'))

        self.stdout.write(self.style.SUCCESS('Sequências ajustadas com sucesso.'))


