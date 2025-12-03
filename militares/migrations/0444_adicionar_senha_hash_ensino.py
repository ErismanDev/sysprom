# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0443_adicionar_colunas_ensino_faltantes'),
    ]

    operations = [
        migrations.AddField(
            model_name='alunoensino',
            name='senha_hash',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Hash da Senha'),
        ),
        migrations.AddField(
            model_name='instrutorensino',
            name='senha_hash',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Hash da Senha'),
        ),
        migrations.AddField(
            model_name='monitorensino',
            name='senha_hash',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Hash da Senha'),
        ),
    ]

