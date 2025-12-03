# Generated manually

from django.db import migrations, models
import django.db.models.deletion
from datetime import datetime


def criar_edicoes_para_turmas_sem_edicao(apps, schema_editor):
    """Cria edições padrão para turmas que não têm edição"""
    TurmaEnsino = apps.get_model('militares', 'TurmaEnsino')
    EdicaoCurso = apps.get_model('militares', 'EdicaoCurso')
    CursoEnsino = apps.get_model('militares', 'CursoEnsino')
    
    # Buscar todas as turmas sem edição
    turmas_sem_edicao = TurmaEnsino.objects.filter(edicao__isnull=True)
    
    # Agrupar por curso
    cursos_com_turmas_sem_edicao = {}
    for turma in turmas_sem_edicao:
        curso_id = turma.curso_id
        if curso_id not in cursos_com_turmas_sem_edicao:
            cursos_com_turmas_sem_edicao[curso_id] = []
        cursos_com_turmas_sem_edicao[curso_id].append(turma)
    
    # Para cada curso, criar uma edição padrão e atribuir às turmas
    for curso_id, turmas in cursos_com_turmas_sem_edicao.items():
        try:
            curso = CursoEnsino.objects.get(pk=curso_id)
            
            # Determinar o ano mais comum entre as turmas ou usar o ano atual
            anos = [turma.data_inicio.year for turma in turmas if turma.data_inicio]
            ano_edicao = max(set(anos), key=anos.count) if anos else datetime.now().year
            
            # Verificar se já existe uma edição padrão para este curso e ano
            edicao_existente = EdicaoCurso.objects.filter(
                curso_id=curso_id,
                ano=ano_edicao,
                nome__icontains='Edição Padrão'
            ).first()
            
            if not edicao_existente:
                # Criar edição padrão
                numero_edicao = EdicaoCurso.objects.filter(
                    curso_id=curso_id
                ).count() + 1
                
                # Determinar data de início (menor data entre as turmas)
                datas_inicio = [turma.data_inicio for turma in turmas if turma.data_inicio]
                data_inicio_edicao = min(datas_inicio) if datas_inicio else datetime.now().date()
                
                # Determinar data de fim (maior data entre as turmas)
                datas_fim = [turma.data_fim for turma in turmas if turma.data_fim]
                data_fim_edicao = max(datas_fim) if datas_fim else None
                
                edicao = EdicaoCurso.objects.create(
                    curso_id=curso_id,
                    numero_edicao=numero_edicao,
                    nome=f'Edição Padrão {ano_edicao}',
                    ano=ano_edicao,
                    data_inicio=data_inicio_edicao,
                    data_fim=data_fim_edicao,
                    ativa=True,
                    observacoes='Edição criada automaticamente para turmas existentes sem edição'
                )
            else:
                edicao = edicao_existente
            
            # Atribuir edição às turmas
            for turma in turmas:
                turma.edicao = edicao
                turma.save()
                
        except CursoEnsino.DoesNotExist:
            # Se o curso não existir, pular
            continue


def reverter_edicoes_obrigatorias(apps, schema_editor):
    """Reverter: tornar edição opcional novamente"""
    # Não precisa fazer nada, a migration reversa já remove a obrigatoriedade
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('militares', '0452_adicionar_edicao_curso'),
    ]

    operations = [
        # Primeiro, criar edições para turmas sem edição
        migrations.RunPython(
            criar_edicoes_para_turmas_sem_edicao,
            reverter_edicoes_obrigatorias
        ),
        # Depois, tornar o campo obrigatório
        migrations.AlterField(
            model_name='turmaensino',
            name='edicao',
            field=models.ForeignKey(
                help_text='Edição do curso - OBRIGATÓRIO: Todas as turmas devem estar dentro de uma edição',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='turmas',
                to='militares.edicaocurso',
                verbose_name='Edição'
            ),
        ),
    ]
