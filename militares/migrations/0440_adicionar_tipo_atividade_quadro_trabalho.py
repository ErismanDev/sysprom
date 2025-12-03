# Generated manually for adding tipo_atividade and descricao to AulaQuadroTrabalhoSemanal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0439_refatorar_quadro_trabalho_semanal'),
    ]

    operations = [
        migrations.AddField(
            model_name='aulaquadrotrabalhosemanal',
            name='tipo_atividade',
            field=models.CharField(
                choices=[
                    ('AULA', 'Aula'),
                    ('INTERVALO', 'Intervalo'),
                    ('HORARIO_VAGO', 'Horário Vago'),
                    ('OUTRA_ACAO', 'Outra Ação'),
                ],
                default='AULA',
                max_length=20,
                verbose_name='Tipo de Atividade'
            ),
        ),
        migrations.AddField(
            model_name='aulaquadrotrabalhosemanal',
            name='descricao',
            field=models.CharField(
                blank=True,
                help_text="Descrição para intervalos, horários vagos ou outras ações (ex: 'Intervalo para Almoço', 'Horário Livre', 'Reunião de Coordenação')",
                max_length=200,
                null=True,
                verbose_name='Descrição'
            ),
        ),
        migrations.AlterField(
            model_name='aulaquadrotrabalhosemanal',
            name='disciplina',
            field=models.ForeignKey(
                blank=True,
                help_text="Obrigatório apenas para tipo 'Aula'",
                null=True,
                on_delete=models.CASCADE,
                related_name='aulas_quadros_trabalho_semanal',
                to='militares.disciplinaensino',
                verbose_name='Disciplina'
            ),
        ),
    ]

