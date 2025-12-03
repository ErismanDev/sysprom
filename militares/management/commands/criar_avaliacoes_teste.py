from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from militares.models import (
    TurmaEnsino, DisciplinaEnsino, AlunoEnsino, 
    AvaliacaoEnsino, NotaAvaliacao
)
import random


class Command(BaseCommand):
    help = 'Cria avaliações e notas de teste para a turma do CHOBM 2025'

    def add_arguments(self, parser):
        parser.add_argument(
            '--turma-id',
            type=int,
            help='ID da turma (se não informado, busca por CHOBM 2025)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria criado sem criar de fato',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        turma_id = options.get('turma_id')
        
        # Buscar turma
        if turma_id:
            try:
                turma = TurmaEnsino.objects.get(pk=turma_id)
            except TurmaEnsino.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Turma com ID {turma_id} não encontrada.'))
                return
        else:
            # Buscar turma CHOBM/CHO BM 2025
            turmas = TurmaEnsino.objects.filter(
                identificacao__icontains='2025'
            ).filter(
                identificacao__icontains__in=['CHO', 'CHOBM', 'CHC']
            )
            
            if not turmas.exists():
                self.stdout.write(self.style.ERROR('Nenhuma turma CHOBM 2025 encontrada.'))
                self.stdout.write('Turmas disponíveis:')
                for t in TurmaEnsino.objects.all()[:10]:
                    self.stdout.write(f'  ID: {t.pk}, Nome: {t.identificacao}')
                return
            
            turma = turmas.first()
        
        self.stdout.write(self.style.SUCCESS(f'Turma encontrada: {turma.identificacao} (ID: {turma.pk})'))
        
        # Buscar disciplinas da turma
        disciplinas = turma.disciplinas.all()
        if not disciplinas.exists():
            # Tentar buscar do curso
            if turma.curso:
                from militares.models import DisciplinaCurso
                disciplinas_curso = DisciplinaCurso.objects.filter(curso=turma.curso)
                disciplinas = [dc.disciplina for dc in disciplinas_curso]
        
        if not disciplinas:
            self.stdout.write(self.style.ERROR('Nenhuma disciplina encontrada para esta turma.'))
            return
        
        self.stdout.write(f'Disciplinas encontradas: {len(disciplinas)}')
        for disc in disciplinas:
            self.stdout.write(f'  - {disc.nome}')
        
        # Buscar alunos ativos
        alunos = AlunoEnsino.objects.filter(turma=turma, situacao='ATIVO')
        if not alunos.exists():
            self.stdout.write(self.style.ERROR('Nenhum aluno ativo encontrado nesta turma.'))
            return
        
        self.stdout.write(f'Alunos encontrados: {alunos.count()}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== MODO DRY-RUN - Nada será criado ===\n'))
        
        # Criar avaliações para cada disciplina
        data_base = timezone.now().date()
        
        for idx, disciplina in enumerate(disciplinas[:3]):  # Limitar a 3 disciplinas para teste
            self.stdout.write(f'\n--- Disciplina: {disciplina.nome} ---')
            
            # Criar 4 avaliações regulares
            for num_avaliacao in range(1, 5):
                nome_avaliacao = f'{num_avaliacao}ª Verificação de Conhecimentos'
                
                # Verificar se já existe
                avaliacao_existente = AvaliacaoEnsino.objects.filter(
                    turma=turma,
                    disciplina=disciplina,
                    nome=nome_avaliacao
                ).first()
                
                if avaliacao_existente:
                    self.stdout.write(f'  Avaliação "{nome_avaliacao}" já existe (ID: {avaliacao_existente.pk})')
                    avaliacao = avaliacao_existente
                else:
                    if not dry_run:
                        avaliacao = AvaliacaoEnsino.objects.create(
                            nome=nome_avaliacao,
                            turma=turma,
                            disciplina=disciplina,
                            tipo='VERIFICACAO',
                            data_avaliacao=data_base - timedelta(days=30 - (num_avaliacao * 7)),
                            peso=1.0,
                            nota_maxima=10.0,
                            descricao=f'{num_avaliacao}ª avaliação da disciplina {disciplina.nome}'
                        )
                        self.stdout.write(self.style.SUCCESS(f'  [OK] Criada: {nome_avaliacao} (ID: {avaliacao.pk})'))
                    else:
                        self.stdout.write(f'  [DRY-RUN] Criaria: {nome_avaliacao}')
                        avaliacao = None
                
                # Criar notas para os alunos
                if avaliacao:
                    notas_criadas = 0
                    for aluno in alunos:
                        # Verificar se já existe nota
                        nota_existente = NotaAvaliacao.objects.filter(
                            avaliacao=avaliacao,
                            aluno=aluno
                        ).first()
                        
                        if nota_existente:
                            continue
                        
                        # Gerar nota aleatória (entre 4.0 e 10.0)
                        # Alguns alunos terão notas baixas para testar recuperação
                        if random.random() < 0.3:  # 30% dos alunos terão notas baixas
                            nota = round(random.uniform(4.0, 6.5), 2)
                        else:
                            nota = round(random.uniform(6.5, 10.0), 2)
                        
                        if not dry_run:
                            NotaAvaliacao.objects.create(
                                avaliacao=avaliacao,
                                aluno=aluno,
                                nota=nota,
                                lancado_por=None  # Sistema
                            )
                            notas_criadas += 1
                        else:
                            self.stdout.write(f'    [DRY-RUN] Nota para {aluno.matricula}: {nota}')
                    
                    if not dry_run and notas_criadas > 0:
                        self.stdout.write(f'    [OK] {notas_criadas} nota(s) criada(s)')
            
            # Criar avaliação de recuperação para alguns alunos
            # Buscar alunos com média baixa (menor que 7.0)
            alunos_recuperacao = []
            for aluno in alunos:
                notas_aluno = NotaAvaliacao.objects.filter(
                    avaliacao__turma=turma,
                    avaliacao__disciplina=disciplina,
                    avaliacao__tipo='VERIFICACAO',
                    aluno=aluno
                )
                
                if notas_aluno.count() >= 4:
                    media = sum([n.nota for n in notas_aluno]) / notas_aluno.count()
                    if media < 7.0:
                        alunos_recuperacao.append(aluno)
            
            if alunos_recuperacao:
                nome_recuperacao = 'Recuperação'
                avaliacao_rec_existente = AvaliacaoEnsino.objects.filter(
                    turma=turma,
                    disciplina=disciplina,
                    tipo='RECUPERACAO',
                    nome=nome_recuperacao
                ).first()
                
                if avaliacao_rec_existente:
                    self.stdout.write(f'  Avaliação de recuperação já existe (ID: {avaliacao_rec_existente.pk})')
                    avaliacao_rec = avaliacao_rec_existente
                else:
                    if not dry_run:
                        avaliacao_rec = AvaliacaoEnsino.objects.create(
                            nome=nome_recuperacao,
                            turma=turma,
                            disciplina=disciplina,
                            tipo='RECUPERACAO',
                            data_avaliacao=data_base - timedelta(days=5),
                            peso=1.0,
                            nota_maxima=10.0,
                            descricao=f'Recuperação da disciplina {disciplina.nome}'
                        )
                        self.stdout.write(self.style.SUCCESS(f'  [OK] Criada recuperação (ID: {avaliacao_rec.pk})'))
                    else:
                        self.stdout.write(f'  [DRY-RUN] Criaria recuperação')
                        avaliacao_rec = None
                
                # Criar notas de recuperação (alguns aprovados, alguns reprovados)
                if avaliacao_rec:
                    notas_rec_criadas = 0
                    for aluno in alunos_recuperacao[:5]:  # Limitar a 5 alunos
                        nota_existente = NotaAvaliacao.objects.filter(
                            avaliacao=avaliacao_rec,
                            aluno=aluno
                        ).first()
                        
                        if nota_existente:
                            continue
                        
                        # 50% aprovados na recuperação (>= 6.0), 50% reprovados (< 6.0)
                        if random.random() < 0.5:
                            nota = round(random.uniform(6.0, 10.0), 2)
                        else:
                            nota = round(random.uniform(4.0, 5.9), 2)
                        
                        if not dry_run:
                            NotaAvaliacao.objects.create(
                                avaliacao=avaliacao_rec,
                                aluno=aluno,
                                nota=nota,
                                lancado_por=None
                            )
                            notas_rec_criadas += 1
                        else:
                            self.stdout.write(f'    [DRY-RUN] Nota de recuperação para {aluno.matricula}: {nota}')
                    
                    if not dry_run and notas_rec_criadas > 0:
                        self.stdout.write(f'    [OK] {notas_rec_criadas} nota(s) de recuperação criada(s)')
        
        self.stdout.write(self.style.SUCCESS('\n=== Processo concluído! ==='))
        if dry_run:
            self.stdout.write(self.style.WARNING('Execute sem --dry-run para criar as avaliações e notas.'))

