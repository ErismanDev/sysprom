# Generated manually for performance optimization

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0260_add_abono_planejada'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_escala_militar_militar_escala ON militares_escalamilitar (militar_id, escala_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_escala_militar_militar_escala;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_escala_data_status ON militares_escalaservico (data, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_escala_data_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_militar_voluntario_situacao ON militares_militar (voluntario_operacoes, situacao, gratificacao);",
            reverse_sql="DROP INDEX IF EXISTS idx_militar_voluntario_situacao;"
        ),
    ]
