# Generated manually to fix column name

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0205_add_anexo_nota"),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Verificar se a coluna nota_id existe antes de renomear
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_anexonota' 
                    AND column_name = 'nota_id'
                ) THEN
                    ALTER TABLE militares_anexonota RENAME COLUMN nota_id TO publicacao_id;
                ELSIF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'militares_anexonota' 
                    AND column_name = 'publicacao_id'
                ) THEN
                    -- Se nota_id não existe e publicacao_id também não, criar publicacao_id
                    ALTER TABLE militares_anexonota ADD COLUMN publicacao_id INTEGER;
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE militares_anexonota RENAME COLUMN publicacao_id TO nota_id;"
        ),
    ]
