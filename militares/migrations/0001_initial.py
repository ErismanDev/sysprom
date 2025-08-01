# Generated by Django 5.2.3 on 2025-07-02 00:21

import django.db.models.deletion
import militares.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Curso",
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
                    models.CharField(max_length=200, verbose_name="Nome do Curso"),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[("MILITAR", "Militar"), ("CIVIL", "Civil")],
                        max_length=10,
                        verbose_name="Tipo",
                    ),
                ),
                (
                    "pontuacao",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="Pontuação"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(blank=True, null=True, verbose_name="Descrição"),
                ),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
            ],
            options={
                "verbose_name": "Curso",
                "verbose_name_plural": "Cursos",
                "ordering": ["tipo", "nome"],
            },
        ),
        migrations.CreateModel(
            name="MedalhaCondecoracao",
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
                ("nome", models.CharField(max_length=200, verbose_name="Nome")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("FEDERAL", "Governo Federal"),
                            ("ESTADUAL", "Governo Estadual"),
                            ("CBMEPI", "CBMEPI"),
                        ],
                        max_length=10,
                        verbose_name="Tipo",
                    ),
                ),
                (
                    "pontuacao",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="Pontuação"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(blank=True, null=True, verbose_name="Descrição"),
                ),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
            ],
            options={
                "verbose_name": "Medalha/Condecoração",
                "verbose_name_plural": "Medalhas e Condecorações",
                "ordering": ["tipo", "nome"],
            },
        ),
        migrations.CreateModel(
            name="Militar",
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
                    "matricula",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="Matrícula"
                    ),
                ),
                (
                    "nome_completo",
                    models.CharField(max_length=200, verbose_name="Nome Completo"),
                ),
                (
                    "nome_guerra",
                    models.CharField(max_length=100, verbose_name="Nome de Guerra"),
                ),
                (
                    "cpf",
                    models.CharField(max_length=14, unique=True, verbose_name="CPF"),
                ),
                ("rg", models.CharField(max_length=20, verbose_name="RG")),
                (
                    "orgao_expedidor",
                    models.CharField(max_length=20, verbose_name="Órgão Expedidor"),
                ),
                (
                    "data_nascimento",
                    models.DateField(verbose_name="Data de Nascimento"),
                ),
                (
                    "sexo",
                    models.CharField(
                        choices=[("M", "Masculino"), ("F", "Feminino")],
                        max_length=1,
                        verbose_name="Sexo",
                    ),
                ),
                (
                    "estado_civil",
                    models.CharField(
                        choices=[
                            ("S", "Solteiro(a)"),
                            ("C", "Casado(a)"),
                            ("D", "Divorciado(a)"),
                            ("V", "Viúvo(a)"),
                            ("U", "União Estável"),
                        ],
                        max_length=1,
                        verbose_name="Estado Civil",
                    ),
                ),
                (
                    "quadro",
                    models.CharField(
                        choices=[
                            ("COMB", "Combatente"),
                            ("SAUDE", "Saúde"),
                            ("ENG", "Engenheiro"),
                            ("COMP", "Complementar"),
                        ],
                        default="COMB",
                        max_length=5,
                        verbose_name="Quadro",
                    ),
                ),
                (
                    "posto_graduacao",
                    models.CharField(
                        choices=[
                            ("CB", "Coronel"),
                            ("TC", "Tenente Coronel"),
                            ("MJ", "Major"),
                            ("CP", "Capitão"),
                            ("1T", "1º Tenente"),
                            ("2T", "2º Tenente"),
                            ("AS", "Aspirante a Oficial"),
                            ("ST", "Subtenente"),
                            ("1S", "1º Sargento"),
                            ("2S", "2º Sargento"),
                            ("3S", "3º Sargento"),
                            ("CB", "Cabo"),
                            ("SD", "Soldado"),
                        ],
                        max_length=2,
                        verbose_name="Posto/Graduação",
                    ),
                ),
                ("data_ingresso", models.DateField(verbose_name="Data de Ingresso")),
                (
                    "data_promocao_atual",
                    models.DateField(verbose_name="Data da Promoção Atual"),
                ),
                (
                    "situacao",
                    models.CharField(
                        choices=[
                            ("AT", "Ativo"),
                            ("IN", "Inativo"),
                            ("TR", "Transferido"),
                            ("AP", "Aposentado"),
                            ("EX", "Exonerado"),
                        ],
                        default="AT",
                        max_length=2,
                        verbose_name="Situação",
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="E-mail")),
                ("telefone", models.CharField(max_length=20, verbose_name="Telefone")),
                ("celular", models.CharField(max_length=20, verbose_name="Celular")),
                (
                    "data_cadastro",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Cadastro"
                    ),
                ),
                (
                    "data_atualizacao",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Data de Atualização"
                    ),
                ),
                (
                    "observacoes",
                    models.TextField(blank=True, null=True, verbose_name="Observações"),
                ),
            ],
            options={
                "verbose_name": "Militar",
                "verbose_name_plural": "Militares",
                "ordering": ["posto_graduacao", "nome_completo"],
            },
        ),
        migrations.CreateModel(
            name="FichaConceito",
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
                ("ano", models.PositiveIntegerField(verbose_name="Ano de Referência")),
                (
                    "tempo_posto",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Tempo no Posto (anos)"
                    ),
                ),
                (
                    "cursos_especializacao",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Especialização (militar)"
                    ),
                ),
                (
                    "cursos_csbm",
                    models.PositiveIntegerField(default=0, verbose_name="CSBM"),
                ),
                (
                    "cursos_cfsd",
                    models.PositiveIntegerField(default=0, verbose_name="CFSD"),
                ),
                (
                    "cursos_chc",
                    models.PositiveIntegerField(
                        default=0, verbose_name="CHC ou adaptação a Cb"
                    ),
                ),
                (
                    "cursos_chsgt",
                    models.PositiveIntegerField(
                        default=0, verbose_name="CHSGT ou adaptação a Sgt"
                    ),
                ),
                (
                    "cursos_cas",
                    models.PositiveIntegerField(default=0, verbose_name="CAS"),
                ),
                (
                    "cursos_cho",
                    models.PositiveIntegerField(default=0, verbose_name="CHO"),
                ),
                (
                    "cursos_cfo",
                    models.PositiveIntegerField(default=0, verbose_name="CFO"),
                ),
                (
                    "cursos_cao",
                    models.PositiveIntegerField(default=0, verbose_name="CAO"),
                ),
                (
                    "cursos_superior",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Superior (militar)"
                    ),
                ),
                (
                    "cursos_mestrado",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Mestrado (militar)"
                    ),
                ),
                (
                    "cursos_doutorado",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Doutorado (militar)"
                    ),
                ),
                (
                    "instrutor_cursos",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Instrutor em Cursos Militares"
                    ),
                ),
                (
                    "cursos_civis_especializacao",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Especialização (civil)"
                    ),
                ),
                (
                    "cursos_civis_mestrado",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Mestrado (civil)"
                    ),
                ),
                (
                    "cursos_civis_doutorado",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Doutorado (civil)"
                    ),
                ),
                (
                    "medalha_federal",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Medalha Federal"
                    ),
                ),
                (
                    "medalha_estadual",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Medalha Estadual"
                    ),
                ),
                (
                    "medalha_cbmepi",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Medalha CBMEPI"
                    ),
                ),
                (
                    "medalha_cremepi",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Medalha CREMEPI"
                    ),
                ),
                (
                    "elogio_individual",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Elogio Individual"
                    ),
                ),
                (
                    "elogio_coletivo",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Elogio Coletivo"
                    ),
                ),
                (
                    "punicao_repreensao",
                    models.PositiveIntegerField(default=0, verbose_name="Repreensão"),
                ),
                (
                    "punicao_detencao",
                    models.PositiveIntegerField(default=0, verbose_name="Detenção"),
                ),
                (
                    "punicao_prisao",
                    models.PositiveIntegerField(default=0, verbose_name="Prisão"),
                ),
                (
                    "falta_aproveitamento",
                    models.PositiveIntegerField(
                        default=0,
                        verbose_name="Falta de Aproveitamento em Cursos Militares",
                    ),
                ),
                (
                    "data_registro",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data do Registro"
                    ),
                ),
                (
                    "observacoes",
                    models.TextField(blank=True, null=True, verbose_name="Observações"),
                ),
                (
                    "militar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="militares.militar",
                        verbose_name="Militar",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ficha de Conceito",
                "verbose_name_plural": "Fichas de Conceito",
                "ordering": ["-ano", "militar"],
                "unique_together": {("militar", "ano")},
            },
        ),
        migrations.CreateModel(
            name="Documento",
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
                    "tipo",
                    models.CharField(
                        choices=[
                            ("DIPLOMA", "Diploma"),
                            ("CERTIFICADO", "Certificado"),
                            ("DECRETO", "Decreto"),
                            ("PORTARIA", "Portaria"),
                            ("ORDEM_SERVICO", "Ordem de Serviço"),
                            ("ELOGIO", "Elogio"),
                            ("PUNICAO", "Punição"),
                            ("OUTROS", "Outros"),
                        ],
                        max_length=15,
                        verbose_name="Tipo de Documento",
                    ),
                ),
                (
                    "titulo",
                    models.CharField(
                        max_length=200, verbose_name="Título do Documento"
                    ),
                ),
                (
                    "arquivo",
                    models.FileField(
                        upload_to=militares.models.documento_upload_path,
                        verbose_name="Arquivo",
                    ),
                ),
                (
                    "data_upload",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data do Upload"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDENTE", "Pendente de Conferência"),
                            ("APROVADO", "Aprovado"),
                            ("REJEITADO", "Rejeitado"),
                            ("ARQUIVADO", "Arquivado"),
                        ],
                        default="PENDENTE",
                        max_length=10,
                        verbose_name="Status",
                    ),
                ),
                (
                    "observacoes",
                    models.TextField(blank=True, null=True, verbose_name="Observações"),
                ),
                (
                    "data_conferencia",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Data da Conferência"
                    ),
                ),
                (
                    "conferido_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Conferido por",
                    ),
                ),
                (
                    "ficha_conceito",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="militares.fichaconceito",
                        verbose_name="Ficha de Conceito",
                    ),
                ),
                (
                    "militar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="militares.militar",
                        verbose_name="Militar",
                    ),
                ),
            ],
            options={
                "verbose_name": "Documento",
                "verbose_name_plural": "Documentos",
                "ordering": ["-data_upload"],
            },
        ),
        migrations.CreateModel(
            name="Promocao",
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
                    "posto_anterior",
                    models.CharField(
                        choices=[
                            ("CB", "Coronel"),
                            ("TC", "Tenente Coronel"),
                            ("MJ", "Major"),
                            ("CP", "Capitão"),
                            ("1T", "1º Tenente"),
                            ("2T", "2º Tenente"),
                            ("AS", "Aspirante a Oficial"),
                            ("ST", "Subtenente"),
                            ("1S", "1º Sargento"),
                            ("2S", "2º Sargento"),
                            ("3S", "3º Sargento"),
                            ("CB", "Cabo"),
                            ("SD", "Soldado"),
                        ],
                        max_length=2,
                        verbose_name="Posto Anterior",
                    ),
                ),
                (
                    "posto_novo",
                    models.CharField(
                        choices=[
                            ("CB", "Coronel"),
                            ("TC", "Tenente Coronel"),
                            ("MJ", "Major"),
                            ("CP", "Capitão"),
                            ("1T", "1º Tenente"),
                            ("2T", "2º Tenente"),
                            ("AS", "Aspirante a Oficial"),
                            ("ST", "Subtenente"),
                            ("1S", "1º Sargento"),
                            ("2S", "2º Sargento"),
                            ("3S", "3º Sargento"),
                            ("CB", "Cabo"),
                            ("SD", "Soldado"),
                        ],
                        max_length=2,
                        verbose_name="Novo Posto",
                    ),
                ),
                (
                    "criterio",
                    models.CharField(
                        choices=[
                            ("ANTIGUIDADE", "Antiguidade"),
                            ("MERECIMENTO", "Merecimento"),
                            ("POST_MORTEM", "Post Mortem"),
                            ("RESSARCIMENTO", "Ressarcimento de Preterição"),
                        ],
                        max_length=15,
                        verbose_name="Critério",
                    ),
                ),
                ("data_promocao", models.DateField(verbose_name="Data da Promoção")),
                (
                    "data_publicacao",
                    models.DateField(verbose_name="Data da Publicação"),
                ),
                (
                    "numero_ato",
                    models.CharField(max_length=50, verbose_name="Número do Ato"),
                ),
                (
                    "observacoes",
                    models.TextField(blank=True, null=True, verbose_name="Observações"),
                ),
                (
                    "data_registro",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data do Registro"
                    ),
                ),
                (
                    "militar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="militares.militar",
                        verbose_name="Militar",
                    ),
                ),
            ],
            options={
                "verbose_name": "Promoção",
                "verbose_name_plural": "Promoções",
                "ordering": ["-data_promocao"],
            },
        ),
        migrations.CreateModel(
            name="QuadroAcesso",
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
                    "tipo",
                    models.CharField(
                        choices=[
                            ("ANTIGUIDADE", "Quadro de Acesso por Antiguidade"),
                            ("MERECIMENTO", "Quadro de Acesso por Merecimento"),
                        ],
                        max_length=15,
                        verbose_name="Tipo",
                    ),
                ),
                (
                    "posto",
                    models.CharField(
                        choices=[
                            ("2T", "2º Tenente"),
                            ("1T", "1º Tenente"),
                            ("CP", "Capitão"),
                            ("MJ", "Major"),
                            ("TC", "Tenente-Coronel"),
                            ("CB", "Coronel"),
                        ],
                        max_length=2,
                        verbose_name="Posto",
                    ),
                ),
                (
                    "quadro",
                    models.CharField(
                        choices=[
                            ("COMB", "Combatente"),
                            ("SAUDE", "Saúde"),
                            ("ENG", "Engenheiro"),
                            ("COMP", "Complementar"),
                        ],
                        max_length=5,
                        verbose_name="Quadro",
                    ),
                ),
                ("data_promocao", models.DateField(verbose_name="Data da Promoção")),
                (
                    "data_criacao",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Criação"
                    ),
                ),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
            ],
            options={
                "verbose_name": "Quadro de Acesso",
                "verbose_name_plural": "Quadros de Acesso",
                "ordering": ["-data_promocao", "tipo", "posto"],
                "unique_together": {("tipo", "posto", "quadro", "data_promocao")},
            },
        ),
        migrations.CreateModel(
            name="Vaga",
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
                    "posto",
                    models.CharField(
                        choices=[
                            ("2T", "2º Tenente"),
                            ("1T", "1º Tenente"),
                            ("CP", "Capitão"),
                            ("MJ", "Major"),
                            ("TC", "Tenente-Coronel"),
                            ("CB", "Coronel"),
                        ],
                        max_length=2,
                        verbose_name="Posto",
                    ),
                ),
                (
                    "quadro",
                    models.CharField(
                        choices=[
                            ("COMB", "Combatente"),
                            ("SAUDE", "Saúde"),
                            ("ENG", "Engenheiro"),
                            ("COMP", "Complementar"),
                        ],
                        max_length=5,
                        verbose_name="Quadro",
                    ),
                ),
                (
                    "efetivo_atual",
                    models.IntegerField(default=0, verbose_name="Efetivo Atual"),
                ),
                ("efetivo_maximo", models.IntegerField(verbose_name="Efetivo Máximo")),
                (
                    "data_atualizacao",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Data de Atualização"
                    ),
                ),
            ],
            options={
                "verbose_name": "Vaga",
                "verbose_name_plural": "Vagas",
                "ordering": ["posto", "quadro"],
                "unique_together": {("posto", "quadro")},
            },
        ),
        migrations.CreateModel(
            name="ItemQuadroAcesso",
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
                ("posicao", models.IntegerField(verbose_name="Posição")),
                (
                    "pontuacao",
                    models.DecimalField(
                        decimal_places=2, max_digits=8, verbose_name="Pontuação"
                    ),
                ),
                (
                    "data_inclusao",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Inclusão"
                    ),
                ),
                (
                    "militar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="militares.militar",
                        verbose_name="Militar",
                    ),
                ),
                (
                    "quadro_acesso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="militares.quadroacesso",
                        verbose_name="Quadro de Acesso",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item do Quadro de Acesso",
                "verbose_name_plural": "Itens do Quadro de Acesso",
                "ordering": ["quadro_acesso", "posicao"],
                "unique_together": {("quadro_acesso", "militar")},
            },
        ),
    ]
