# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0239_add_boletim_reservado_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escalaservico',
            name='organizacao',
            field=models.CharField(max_length=200, verbose_name='Organização'),
        ),
    ]
