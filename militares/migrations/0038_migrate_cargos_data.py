# Generated manually for data migration

from django.db import migrations


def migrate_cargos_data(apps, schema_editor):
    """
    Migra os dados do campo cargo (CharField) para os registros correspondentes
    em CargoComissao antes de alterar o campo para ForeignKey
    """
    MembroComissao = apps.get_model('militares', 'MembroComissao')
    CargoComissao = apps.get_model('militares', 'CargoComissao')
    
    # Mapeamento dos cargos antigos para os códigos dos novos
    cargo_mapping = {
        'COMANDANTE_GERAL': 'COMANDANTE_GERAL',
        'CHEFE_ESTADO_MAIOR': 'CHEFE_ESTADO_MAIOR', 
        'DIRETOR_PESSOAL': 'DIRETOR_PESSOAL',
        'BM1': 'BM1',
        'OFICIAL_SUPERIOR': 'OFICIAL_SUPERIOR',
    }
    
    for membro in MembroComissao.objects.all():
        # Só migrar se o valor for uma string conhecida
        if isinstance(membro.cargo, str) and membro.cargo in cargo_mapping:
            try:
                cargo_obj = CargoComissao.objects.get(codigo=cargo_mapping[membro.cargo])
                membro.cargo = str(cargo_obj.id)
                membro.save()
                print(f"Migrado cargo '{membro.cargo}' (ID: {cargo_obj.id}) para membro {membro.militar.nome_completo}")
            except CargoComissao.DoesNotExist:
                print(f"ERRO: Cargo '{cargo_mapping[membro.cargo]}' não encontrado para membro {membro.militar.nome_completo}")
        else:
            # Ignorar se já for ID ou não for cargo conhecido
            print(f"Cargo já migrado ou não reconhecido para membro {membro.militar.nome_completo}")
            continue


def reverse_migrate_cargos_data(apps, schema_editor):
    """
    Reverte a migração (não é necessário para este caso)
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0037_cargocomissao"),
    ]

    operations = [
        migrations.RunPython(migrate_cargos_data, reverse_migrate_cargos_data),
    ] 