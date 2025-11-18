# Generated manually to fix PermissaoFuncao model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0161_remove_cargofuncao_table"),
    ]

    operations = [
        # NOTA: O campo funcao_militar já foi criado na migração 0140_update_acesso_choices
        # quando o modelo PermissaoFuncao foi criado, então não precisa ser adicionado novamente
        migrations.AlterModelOptions(
            name="permissaofuncao",
            options={
                "ordering": ["funcao_militar__nome", "modulo", "acesso"],
                "verbose_name": "Permissão de Função",
                "verbose_name_plural": "Permissões de Funções",
            },
        ),
    ]
