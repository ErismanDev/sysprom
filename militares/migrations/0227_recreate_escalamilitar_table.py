# Generated manually to recreate EscalaMilitar table with correct structure

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0226_create_escalaservico_table'),
    ]

    operations = [
        # Primeiro, vamos deletar a tabela existente
        migrations.DeleteModel(
            name='EscalaMilitar',
        ),
        
        # Agora vamos recriar com a estrutura correta
        migrations.CreateModel(
            name='EscalaMilitar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funcao', models.CharField(choices=[('responsavel', 'Responsável'), ('substituto', 'Substituto'), ('militar', 'Militar')], default='militar', max_length=20, verbose_name='Função')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('escala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='militares', to='militares.escalaservico', verbose_name='Escala')),
                ('militar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='militares.militar', verbose_name='Militar')),
            ],
            options={
                'verbose_name': 'Militar da Escala',
                'verbose_name_plural': 'Militares da Escala',
                'ordering': ['escala', 'funcao', 'militar__nome_completo'],
                'unique_together': {('escala', 'militar')},
            },
        ),
    ]






