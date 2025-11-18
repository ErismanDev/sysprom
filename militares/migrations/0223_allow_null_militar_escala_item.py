# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0222_add_escalas_servico'),
    ]

    operations = [
        migrations.AlterField(
            model_name='escalaservicoitem',
            name='militar',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, to='militares.militar', verbose_name='Militar'),
        ),
    ]