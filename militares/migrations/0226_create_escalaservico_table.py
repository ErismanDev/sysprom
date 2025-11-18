# Generated manually to fix EscalaServico table issue

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0225_add_escalas_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # NOTA: EscalaServico já foi criada na migração 0225_add_escalas_models
        # Apenas adicionando o unique_together que pode estar faltando
        migrations.AlterUniqueTogether(
            name='escalaservico',
            unique_together={('data', 'organizacao', 'tipo_servico')},
        ),
    ]
