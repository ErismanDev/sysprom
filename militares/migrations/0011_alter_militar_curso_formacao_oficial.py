# Generated by Django 5.2.3 on 2025-07-02 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0010_militar_curso_adaptacao_oficial_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="militar",
            name="curso_formacao_oficial",
            field=models.BooleanField(
                default=False,
                verbose_name="Possui Curso de Formação de Oficial Bombeiro Militar (CFO)",
            ),
        ),
    ]
