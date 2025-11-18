# Generated manually to fix foreign key constraint

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0207_add_missing_anexo_columns"),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Remover constraint incorreta
            ALTER TABLE militares_anexonota 
            DROP CONSTRAINT IF EXISTS militares_anexonota_nota_id_5066a5fa_fk_militares_nota_id;
            
            -- Adicionar constraint correta
            ALTER TABLE militares_anexonota 
            ADD CONSTRAINT militares_anexonota_publicacao_id_fk_militares_publicacao_id
            FOREIGN KEY (publicacao_id) REFERENCES militares_publicacao(id) ON DELETE CASCADE;
            """,
            reverse_sql="""
            -- Reverter constraint
            ALTER TABLE militares_anexonota 
            DROP CONSTRAINT IF EXISTS militares_anexonota_publicacao_id_fk_militares_publicacao_id;
            
            -- NOTA: Não é possível reverter completamente pois a coluna foi renomeada de nota_id para publicacao_id
            -- na migração 0206. A constraint será recriada com o nome correto se necessário.
            """
        ),
    ]
