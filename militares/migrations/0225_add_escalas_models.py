# Generated manually

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0224_remove_escalas_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EscalaServico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Data da Escala')),
                ('organizacao', models.CharField(max_length=100, verbose_name='Organização')),
                ('tipo_servico', models.CharField(choices=[('operacional', 'Operacional'), ('administrativo', 'Administrativo')], max_length=20, verbose_name='Tipo de Serviço')),
                ('turno', models.CharField(choices=[('2h', '2 horas'), ('4h', '4 horas'), ('6h', '6 horas'), ('8h', '8 horas'), ('12h', '12 horas'), ('18h', '18 horas'), ('24h', '24 horas')], max_length=10, verbose_name='Turno')),
                ('hora_inicio', models.TimeField(verbose_name='Hora de Início')),
                ('hora_fim', models.TimeField(verbose_name='Hora de Término')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('ativa', 'Ativa'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')], default='pendente', max_length=20, verbose_name='Status')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Escala de Serviço',
                'verbose_name_plural': 'Escalas de Serviço',
                'ordering': ['-data', 'organizacao', 'hora_inicio'],
            },
        ),
        # NOTA: EscalaMilitar será recriada na migração 0227_recreate_escalamilitar_table
        # Se a tabela já existe, ela será removida e recriada na migração 0227
        migrations.RunSQL(
            sql="""
            -- Verificar se EscalaMilitar já existe e não criar se existir
            -- A migração 0227 vai recriar esta tabela de qualquer forma
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'militares_escalamilitar'
                ) THEN
                    -- Criar tabela apenas se não existir
                    CREATE TABLE militares_escalamilitar (
                        id BIGSERIAL PRIMARY KEY,
                        funcao VARCHAR(20) NOT NULL DEFAULT 'militar',
                        observacoes TEXT,
                        data_criacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        escala_id BIGINT NOT NULL,
                        militar_id BIGINT NOT NULL
                    );
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AddConstraint(
            model_name='escalaservico',
            constraint=models.UniqueConstraint(fields=('data', 'organizacao', 'tipo_servico'), name='unique_escala_data_org_tipo'),
        ),
        migrations.AddConstraint(
            model_name='escalamilitar',
            constraint=models.UniqueConstraint(fields=('escala', 'militar'), name='unique_escala_militar'),
        ),
    ]
