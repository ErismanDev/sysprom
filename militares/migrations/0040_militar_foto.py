# Generated by Django 4.2.7 on 2025-07-05 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0039_alter_membrocomissao_cargo"),
    ]

    operations = [
        migrations.AddField(
            model_name="militar",
            name="foto",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="fotos_militares/",
                verbose_name="Foto do Militar",
            ),
        ),
    ]
