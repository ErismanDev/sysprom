# Generated by Django 4.2.7 on 2025-07-15 03:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("militares", "0070_auto_20250714_2315"),
    ]

    operations = [
        migrations.CreateModel(
            name="PermissaoFuncao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "modulo",
                    models.CharField(
                        choices=[
                            ("MILITARES", "Gestão de Militares"),
                            ("FICHAS_CONCEITO", "Fichas de Conceito"),
                            ("QUADROS_ACESSO", "Quadros de Acesso"),
                            ("PROMOCOES", "Promoções"),
                            ("VAGAS", "Gestão de Vagas"),
                            ("COMISSAO", "Comissão de Promoção"),
                            ("DOCUMENTOS", "Documentos"),
                            ("USUARIOS", "Gestão de Usuários"),
                            ("RELATORIOS", "Relatórios"),
                            ("CONFIGURACOES", "Configurações do Sistema"),
                        ],
                        max_length=20,
                        verbose_name="Módulo",
                    ),
                ),
                (
                    "acesso",
                    models.CharField(
                        choices=[
                            ("VISUALIZAR", "Visualizar"),
                            ("CRIAR", "Criar"),
                            ("EDITAR", "Editar"),
                            ("EXCLUIR", "Excluir"),
                            ("APROVAR", "Aprovar"),
                            ("HOMOLOGAR", "Homologar"),
                            ("GERAR_PDF", "Gerar PDF"),
                            ("IMPRIMIR", "Imprimir"),
                            ("ASSINAR", "Assinar"),
                            ("ADMINISTRAR", "Administrar"),
                        ],
                        max_length=20,
                        verbose_name="Tipo de Acesso",
                    ),
                ),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
                (
                    "observacoes",
                    models.TextField(blank=True, null=True, verbose_name="Observações"),
                ),
                (
                    "data_criacao",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Criação"
                    ),
                ),
                (
                    "data_atualizacao",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Data de Atualização"
                    ),
                ),
                (
                    "cargo_funcao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="permissoes",
                        to="militares.cargofuncao",
                        verbose_name="Cargo/Função",
                    ),
                ),
            ],
            options={
                "verbose_name": "Permissão de Função",
                "verbose_name_plural": "Permissões de Funções",
                "ordering": ["cargo_funcao__nome", "modulo", "acesso"],
                "unique_together": {("cargo_funcao", "modulo", "acesso")},
            },
        ),
        migrations.CreateModel(
            name="PerfilAcesso",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Nome do Perfil"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(blank=True, null=True, verbose_name="Descrição"),
                ),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
                (
                    "data_criacao",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Criação"
                    ),
                ),
                (
                    "data_atualizacao",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Data de Atualização"
                    ),
                ),
                (
                    "permissoes",
                    models.ManyToManyField(
                        blank=True,
                        to="militares.permissaofuncao",
                        verbose_name="Permissões",
                    ),
                ),
            ],
            options={
                "verbose_name": "Perfil de Acesso",
                "verbose_name_plural": "Perfis de Acesso",
                "ordering": ["nome"],
            },
        ),
    ]
