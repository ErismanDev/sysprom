# Generated manually to add cargo_funcao column to AssinaturaAlmanaque

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0097_almanaquemilitar_assinaturaalmanaque'),
    ]

    operations = [
        migrations.AddField(
            model_name='assinaturaalmanaque',
            name='cargo_funcao',
            field=models.CharField(
                blank=True,
                max_length=200,
                null=True,
                verbose_name="Cargo/Função"
            ),
        ),
    ] 