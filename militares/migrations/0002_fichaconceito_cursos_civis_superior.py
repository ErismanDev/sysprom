# Generated by Django 4.2.7 on 2025-07-02 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="fichaconceito",
            name="cursos_civis_superior",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Superior (civil)"
            ),
        ),
    ]
