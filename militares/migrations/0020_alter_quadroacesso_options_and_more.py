# Generated by Django 4.2.7 on 2025-07-02 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0019_remove_estado_civil_field"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="quadroacesso",
            options={
                "ordering": ["-data_promocao", "tipo"],
                "verbose_name": "Quadro de Acesso",
                "verbose_name_plural": "Quadros de Acesso",
            },
        ),
        migrations.AlterUniqueTogether(
            name="quadroacesso",
            unique_together={("tipo", "data_promocao")},
        ),
        migrations.RemoveField(
            model_name="quadroacesso",
            name="posto",
        ),
        migrations.RemoveField(
            model_name="quadroacesso",
            name="quadro",
        ),
    ]
