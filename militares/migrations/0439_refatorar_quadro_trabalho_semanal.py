# Generated manually for refactoring QuadroTrabalhoSemanal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0438_adicionar_quadro_trabalho_semanal'),
    ]

    operations = [
        # Criar novo modelo AulaQuadroTrabalhoSemanal primeiro
        migrations.CreateModel(
            name='AulaQuadroTrabalhoSemanal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.CharField(choices=[('SEGUNDA', 'Segunda-feira'), ('TERCA', 'Terça-feira'), ('QUARTA', 'Quarta-feira'), ('QUINTA', 'Quinta-feira'), ('SEXTA', 'Sexta-feira'), ('SABADO', 'Sábado'), ('DOMINGO', 'Domingo')], max_length=10, verbose_name='Dia da Semana')),
                ('data', models.DateField(help_text='Data específica da aula', verbose_name='Data')),
                ('hora_inicio', models.TimeField(verbose_name='Hora de Início')),
                ('hora_fim', models.TimeField(verbose_name='Hora de Término')),
                ('horas_aula', models.DecimalField(decimal_places=2, help_text='Quantidade de horas/aula (calculado automaticamente)', max_digits=5, verbose_name='Horas/Aula')),
                ('carga_horaria_total', models.DecimalField(decimal_places=2, default=0, help_text='Carga horária total da disciplina (ex: 18/20, 12/30)', max_digits=5, verbose_name='Carga Horária Total')),
                ('observacoes', models.TextField(blank=True, help_text='Observações específicas da aula (ex: PROVA, À DISPOSIÇÃO DA DEIP)', null=True, verbose_name='Observações')),
                ('ordem', models.PositiveIntegerField(default=0, help_text='Ordem de exibição no mesmo horário', verbose_name='Ordem')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aulas_quadros_trabalho_semanal', to='militares.disciplinaensino', verbose_name='Disciplina')),
                ('instrutor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aulas_quadros_trabalho_semanal', to='militares.militar', verbose_name='Instrutor')),
                ('quadro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aulas', to='militares.quadrotrabalhosemanal', verbose_name='Quadro de Trabalho Semanal')),
            ],
            options={
                'verbose_name': 'Aula do Quadro de Trabalho Semanal',
                'verbose_name_plural': 'Aulas dos Quadros de Trabalho Semanal',
                'ordering': ['quadro', 'dia_semana', 'hora_inicio', 'ordem'],
            },
        ),
        migrations.AddIndex(
            model_name='aulaquadrotrabalhosemanal',
            index=models.Index(fields=['quadro', 'dia_semana', 'hora_inicio'], name='militares_a_quadro__idx'),
        ),
        # Adicionar novos campos ao QuadroTrabalhoSemanal
        migrations.AddField(
            model_name='quadrotrabalhosemanal',
            name='numero_quadro',
            field=models.PositiveIntegerField(blank=True, help_text='Número sequencial do quadro (ex: Quadro de Trabalho Semanal Nº 5)', null=True, verbose_name='Número do Quadro'),
        ),
        migrations.AddField(
            model_name='quadrotrabalhosemanal',
            name='data_inicio_semana',
            field=models.DateField(blank=True, help_text='Data de início da semana (geralmente segunda-feira)', null=True, verbose_name='Data de Início da Semana'),
        ),
        migrations.AddField(
            model_name='quadrotrabalhosemanal',
            name='data_fim_semana',
            field=models.DateField(blank=True, help_text='Data de término da semana (geralmente sexta-feira)', null=True, verbose_name='Data de Término da Semana'),
        ),
        # Tornar data_fim_semana obrigatório após migração de dados
        migrations.RunSQL(
            sql="""
                UPDATE militares_quadrotrabalhosemanal
                SET data_fim_semana = data_inicio_semana + INTERVAL '6 days'
                WHERE data_fim_semana IS NULL AND data_inicio_semana IS NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddField(
            model_name='quadrotrabalhosemanal',
            name='local',
            field=models.CharField(blank=True, help_text='Local onde será realizado o curso (ex: Teresina/PI)', max_length=200, null=True, verbose_name='Local'),
        ),
        # Migrar dados: copiar data_semana para data_inicio_semana e calcular data_fim_semana
        migrations.RunSQL(
            sql="""
                UPDATE militares_quadrotrabalhosemanal
                SET data_inicio_semana = data_semana,
                    data_fim_semana = data_semana + INTERVAL '6 days'
                WHERE data_inicio_semana IS NULL AND data_semana IS NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Migrar dados antigos para o novo modelo AulaQuadroTrabalhoSemanal
        migrations.RunSQL(
            sql="""
                INSERT INTO militares_aulaquadrotrabalhosemanal 
                (quadro_id, disciplina_id, instrutor_id, dia_semana, data, hora_inicio, hora_fim, horas_aula, observacoes, ordem, data_criacao, data_atualizacao)
                SELECT 
                    id as quadro_id,
                    disciplina_id,
                    instrutor_id,
                    dia_semana,
                    data,
                    hora_inicio,
                    hora_fim,
                    horas_aula,
                    observacoes,
                    0 as ordem,
                    data_criacao,
                    data_atualizacao
                FROM militares_quadrotrabalhosemanal;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Remover campos antigos do QuadroTrabalhoSemanal
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='data_semana',
        ),
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='dia_semana',
        ),
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='data',
        ),
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='hora_inicio',
        ),
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='hora_fim',
        ),
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='horas_aula',
        ),
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='disciplina',
        ),
        migrations.RemoveField(
            model_name='quadrotrabalhosemanal',
            name='instrutor',
        ),
        # Atualizar unique_together
        migrations.AlterUniqueTogether(
            name='quadrotrabalhosemanal',
            unique_together={('turma', 'numero_quadro')},
        ),
        # Atualizar indexes
        migrations.AlterIndexTogether(
            name='quadrotrabalhosemanal',
            index_together=set(),
        ),
        migrations.RemoveIndex(
            model_name='quadrotrabalhosemanal',
            name='militares_q_data_717e57_idx',
        ),
        migrations.RemoveIndex(
            model_name='quadrotrabalhosemanal',
            name='militares_q_turma_i_b944c7_idx',
        ),
        migrations.AddIndex(
            model_name='quadrotrabalhosemanal',
            index=models.Index(fields=['turma', 'data_inicio_semana'], name='militares_q_turma_d_123abc_idx'),
        ),
        # Atualizar ordering
        migrations.AlterModelOptions(
            name='quadrotrabalhosemanal',
            options={'ordering': ['-data_inicio_semana', '-numero_quadro'], 'verbose_name': 'Quadro de Trabalho Semanal', 'verbose_name_plural': 'Quadros de Trabalho Semanal'},
        ),
    ]

