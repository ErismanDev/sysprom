# Generated manually to fix missing table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0383_entradaalmoxarifadoproduto_produtoalmoxarifado_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS militares_produtoalmoxarifadolocalizacao (
                id BIGSERIAL PRIMARY KEY,
                localizacao VARCHAR(200) NULL,
                data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                produto_id BIGINT NOT NULL REFERENCES militares_itemalmoxarifado(id) ON DELETE CASCADE,
                orgao_id BIGINT NULL REFERENCES militares_orgao(id) ON DELETE CASCADE,
                grande_comando_id BIGINT NULL REFERENCES militares_grandecomando(id) ON DELETE CASCADE,
                unidade_id BIGINT NULL REFERENCES militares_unidade(id) ON DELETE CASCADE,
                sub_unidade_id BIGINT NULL REFERENCES militares_subunidade(id) ON DELETE CASCADE,
                criado_por_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL
            );
            
            CREATE INDEX IF NOT EXISTS militares_p_produto_45df49_idx 
            ON militares_produtoalmoxarifadolocalizacao(produto_id, orgao_id, grande_comando_id, unidade_id, sub_unidade_id);
            
            CREATE UNIQUE INDEX IF NOT EXISTS militares_produtoalmoxarifadolocalizacao_produto_id_orgao_id_grande_comando_id_unidade_id_sub_unidade_id_uniq 
            ON militares_produtoalmoxarifadolocalizacao(produto_id, orgao_id, grande_comando_id, unidade_id, sub_unidade_id);
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS militares_produtoalmoxarifadolocalizacao CASCADE;
            """
        ),
    ]

