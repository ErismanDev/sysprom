# Generated manually to fix NOT NULL constraint

from django.db import migrations


def alterar_quantidade_para_null(apps, schema_editor):
    """Altera o campo quantidade para permitir NULL diretamente no banco"""
    with schema_editor.connection.cursor() as cursor:
        # Verificar se a coluna já permite NULL
        cursor.execute("""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'militares_requisicaoalmoxarifado' 
            AND column_name = 'quantidade'
        """)
        result = cursor.fetchone()
        
        # Se não permitir NULL, alterar
        if result and result[0] == 'NO':
            cursor.execute("""
                ALTER TABLE militares_requisicaoalmoxarifado 
                ALTER COLUMN quantidade DROP NOT NULL
            """)


def reverter_alteracao(apps, schema_editor):
    """Reverter a alteração (não necessário, mas mantido para compatibilidade)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0364_remover_validador_quantidade_requisicao"),
    ]

    operations = [
        migrations.RunPython(
            alterar_quantidade_para_null,
            reverter_alteracao
        ),
    ]
