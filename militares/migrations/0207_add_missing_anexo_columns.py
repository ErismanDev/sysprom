# Generated manually to add missing columns

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0206_fix_anexo_nota_column"),
    ]

    operations = [
        # NOTA: Todos os campos (tipo_mime, upload_por, ativo) já foram criados na migração 0205_add_anexo_nota
        # quando o modelo AnexoNota foi criado, então não precisam ser adicionados novamente
        # Mantendo a migração vazia para preservar a numeração
    ]
