# Generated by Django 4.2.7 on 2025-07-02 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0018_update_numeracao_antiguidade_manual"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="militar",
            name="estado_civil",
        ),
    ]
