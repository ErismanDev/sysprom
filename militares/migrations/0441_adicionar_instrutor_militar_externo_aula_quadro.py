# Generated manually for adding instrutor_militar and instrutor_externo to AulaQuadroTrabalhoSemanal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0440_adicionar_tipo_atividade_quadro_trabalho'),
    ]

    operations = [
        # Adicionar novos campos de instrutor
        migrations.AddField(
            model_name='aulaquadrotrabalhosemanal',
            name='instrutor_externo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='aulas_quadros_trabalho_semanal_externo',
                to='militares.instrutorensino',
                verbose_name='Instrutor (Externo)'
            ),
        ),
        migrations.AddField(
            model_name='aulaquadrotrabalhosemanal',
            name='instrutor_militar',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='aulas_quadros_trabalho_semanal_militar',
                to='militares.militar',
                verbose_name='Instrutor (Militar)'
            ),
        ),
        # Migrar dados do campo antigo 'instrutor' para 'instrutor_militar'
        migrations.RunSQL(
            sql="""
                UPDATE militares_aulaquadrotrabalhosemanal
                SET instrutor_militar_id = instrutor_id
                WHERE instrutor_id IS NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Remover o campo antigo 'instrutor'
        migrations.RemoveField(
            model_name='aulaquadrotrabalhosemanal',
            name='instrutor',
        ),
    ]


