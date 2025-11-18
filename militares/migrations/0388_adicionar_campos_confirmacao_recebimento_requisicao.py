# Generated manually to add missing fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0387_alter_produtoalmoxarifado_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='requisicaoalmoxarifado',
            name='data_confirmacao_recebimento',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Data de Confirmação de Recebimento'),
        ),
        migrations.AddField(
            model_name='requisicaoalmoxarifado',
            name='confirmado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requisicoes_almoxarifado_confirmadas', to=settings.AUTH_USER_MODEL, verbose_name='Confirmado por'),
        ),
    ]

