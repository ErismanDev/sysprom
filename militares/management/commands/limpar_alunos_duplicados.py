from django.core.management.base import BaseCommand
from militares.models import AlunoEnsino
from django.db import transaction
import re


def normalizar_cpf(cpf):
    """Remove formatação do CPF"""
    if not cpf:
        return None
    return re.sub(r'[^0-9]', '', str(cpf))


class Command(BaseCommand):
    help = 'Identifica e remove alunos duplicados, mantendo apenas um cadastro por pessoa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria feito, sem fazer alterações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        # Agrupar alunos por identificador único
        grupos_duplicados = {}
        
        todos_alunos = AlunoEnsino.objects.all().select_related('militar', 'turma')
        
        for aluno in todos_alunos:
            # Identificar chave única baseada no tipo
            chave = None
            
            if aluno.tipo_aluno == 'BOMBEIRO' and aluno.militar:
                chave = f'BOMBEIRO_{aluno.militar.pk}'
            elif aluno.tipo_aluno == 'OUTRA_FORCA' and aluno.cpf_outra_forca:
                cpf_normalizado = normalizar_cpf(aluno.cpf_outra_forca)
                if cpf_normalizado:
                    chave = f'OUTRA_FORCA_{cpf_normalizado}'
            elif aluno.tipo_aluno == 'CIVIL' and aluno.cpf_civil:
                cpf_normalizado = normalizar_cpf(aluno.cpf_civil)
                if cpf_normalizado:
                    chave = f'CIVIL_{cpf_normalizado}'
            
            if chave:
                if chave not in grupos_duplicados:
                    grupos_duplicados[chave] = []
                grupos_duplicados[chave].append(aluno)
        
        # Filtrar apenas grupos com duplicatas
        grupos_com_duplicatas = {k: v for k, v in grupos_duplicados.items() if len(v) > 1}
        
        if not grupos_com_duplicatas:
            self.stdout.write(self.style.SUCCESS('Nenhuma duplicata encontrada!'))
            return
        
        self.stdout.write(f'\nEncontrados {len(grupos_com_duplicatas)} grupos com duplicatas\n')
        
        total_removidos = 0
        total_turmas_migradas = 0
        
        with transaction.atomic():
            for chave, alunos in grupos_com_duplicatas.items():
                # Ordenar por data de criação (mais antigo primeiro) e por completude de dados
                alunos_ordenados = sorted(
                    alunos,
                    key=lambda a: (
                        a.data_criacao if a.data_criacao else a.data_matricula,
                        -self._calcular_completude(a)  # Negativo para ordem decrescente
                    )
                )
                
                # O primeiro será mantido
                aluno_manter = alunos_ordenados[0]
                alunos_remover = alunos_ordenados[1:]
                
                self.stdout.write(f'\nGrupo: {chave}')
                self.stdout.write(f'  Manter: ID {aluno_manter.pk} - {aluno_manter.get_pessoa_nome()} (Matrícula: {aluno_manter.matricula or "N/A"})')
                
                # Primeiro, limpar todas as matrículas dos alunos que serão removidos
                for aluno_remover in alunos_remover:
                    self.stdout.write(f'  Remover: ID {aluno_remover.pk} - {aluno_remover.get_pessoa_nome()} (Matrícula: {aluno_remover.matricula or "N/A"})')
                    if not dry_run:
                        aluno_remover.matricula = None
                        aluno_remover.save()
                
                # Depois, migrar turmas e fotos
                for aluno_remover in alunos_remover:
                    # Migrar turma se necessário (apenas se o aluno mantido não tiver turma)
                    if aluno_remover.turma and not aluno_manter.turma:
                        if not dry_run:
                            aluno_manter.turma = aluno_remover.turma
                            aluno_manter.save()
                        self.stdout.write(f'    -> Turma migrada: {aluno_remover.turma.identificacao}')
                        total_turmas_migradas += 1
                    elif aluno_remover.turma and aluno_remover.turma != aluno_manter.turma:
                        # Aluno removido está em outra turma - manter ambas as referências
                        # (será tratado quando mudarmos para ManyToMany)
                        self.stdout.write(f'    -> Atencao: Aluno removido esta em turma diferente: {aluno_remover.turma.identificacao}')
                    
                    # Migrar foto se o aluno mantido não tiver
                    if aluno_remover.foto and not aluno_manter.foto:
                        if not dry_run:
                            aluno_manter.foto = aluno_remover.foto
                            aluno_manter.save()
                        self.stdout.write(f'    -> Foto migrada')
                
                # Por fim, deletar os alunos
                for aluno_remover in alunos_remover:
                    if not dry_run:
                        aluno_remover.delete()
                    total_removidos += 1
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\nDRY-RUN: Seriam removidos {total_removidos} alunos duplicados'))
            self.stdout.write(self.style.WARNING(f'DRY-RUN: Seriam migradas {total_turmas_migradas} turmas'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nRemovidos {total_removidos} alunos duplicados'))
            self.stdout.write(self.style.SUCCESS(f'Migradas {total_turmas_migradas} turmas'))
    
    def _calcular_completude(self, aluno):
        """Calcula um score de completude dos dados do aluno"""
        score = 0
        
        # Dados básicos
        if aluno.tipo_aluno == 'BOMBEIRO' and aluno.militar:
            score += 10
        elif aluno.tipo_aluno == 'OUTRA_FORCA':
            if aluno.nome_outra_forca:
                score += 5
            if aluno.cpf_outra_forca:
                score += 3
            if aluno.email_outra_forca:
                score += 1
        elif aluno.tipo_aluno == 'CIVIL':
            if aluno.nome_civil:
                score += 5
            if aluno.cpf_civil:
                score += 3
            if aluno.email_civil:
                score += 1
        
        # Dados adicionais
        if aluno.foto:
            score += 2
        if aluno.matricula:
            score += 2
        if aluno.turma:
            score += 3
        if aluno.observacoes:
            score += 1
        
        return score

