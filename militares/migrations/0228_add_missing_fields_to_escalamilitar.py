# Generated manually to add missing fields to EscalaMilitar

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0227_recreate_escalamilitar_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='escalamilitar',
            name='tipo_servico',
            field=models.CharField(choices=[('operacional', 'Operacional'), ('administrativo', 'Administrativo')], default='operacional', max_length=20, verbose_name='Tipo de Serviço'),
        ),
        migrations.AddField(
            model_name='escalamilitar',
            name='turno',
            field=models.CharField(choices=[('2h', '2 horas'), ('4h', '4 horas'), ('6h', '6 horas'), ('8h', '8 horas'), ('12h', '12 horas'), ('18h', '18 horas'), ('24h', '24 horas')], default='8h', max_length=10, verbose_name='Turno'),
        ),
        migrations.AddField(
            model_name='escalamilitar',
            name='hora_inicio',
            field=models.TimeField(default='08:00', verbose_name='Hora de Início'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='escalamilitar',
            name='hora_fim',
            field=models.TimeField(default='16:00', verbose_name='Hora de Término'),
            preserve_default=False,
        ),
    ]
