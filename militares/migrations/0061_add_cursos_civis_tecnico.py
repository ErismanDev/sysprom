# Generated by Django 4.2.7 on 2025-07-10 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0060_fichaconceitooficiais_fichaconceitopracas_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="fichaconceitopracas",
            name="cursos_civis_tecnico",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Técnico (civil) - carga horária > 1000h"
            ),
        ),
    ]
