# -*- coding: utf-8 -*-
"""
Views para o Módulo de Ensino Militar
Organizado na sequência hierárquica: Curso → Turmas → Disciplinas → Instrutores → Monitores → Alunos → Aulas → Frequências → Notas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum, Case, When, Value, IntegerField
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date, datetime, time, timedelta
from django.db.models import F
from decimal import Decimal
import logging
logger = logging.getLogger('ensino.revisao')

from .models import (
    PessoaExterna, CursoEnsino, DisciplinaCurso, DisciplinaEnsino, EdicaoCurso, TurmaEnsino, 
    AlunoEnsino, InstrutorEnsino, MonitorEnsino, AulaEnsino, FrequenciaAula, 
    AproveitamentoDisciplina, AvaliacaoEnsino, NotaAvaliacao, CertificadoEnsino, 
    DocumentoAluno, DocumentoInstrutorEnsino, DocumentoMonitorEnsino, DocumentoCursoEnsino, OcorrenciaDisciplinar, EscalaInstrucao, HistoricoEscolar, 
    MaterialEscolar, CautelaMaterialEscolar, Militar, HistoricoTrocaInstrutorDisciplina, HistoricoTrocaMonitorDisciplina, POSTO_GRADUACAO_CHOICES, LinkUtilCurso,
    DocumentoDisciplinaEnsino, LinkUtilDisciplina,
    # Novos modelos ITE 01/2024
    PlanoGeralEnsino, ItemPlanoGeralEnsino, ProjetoPedagogico, PlanoCursoEstagio,
    PlanoDisciplina, PlanoPalestra, AtividadeTreinamentoCampo, AtividadeComplementarEnsino,
    TesteConhecimentosProfissionais, PlanoEstagioNivelamentoProfissional,
    RelatorioAnualDEIP, ProcessoSelecaoAlunos, InscricaoProcessoSelecao,
    RecursoProcessoSelecao, TrabalhoConclusaoCurso, PlanoSeguranca, ClassificacaoFinalCurso,
    PedidoRevisaoProva
)
from .forms_ensino import (
    PessoaExternaForm, CursoEnsinoForm, DisciplinaEnsinoForm, TurmaEnsinoForm, 
    AlunoEnsinoForm, InstrutorEnsinoForm, MonitorEnsinoForm, AulaEnsinoForm, 
    FrequenciaAulaForm, AvaliacaoEnsinoForm, NotaAvaliacaoForm, CertificadoEnsinoForm, 
    DocumentoAlunoForm, OcorrenciaDisciplinarForm, EscalaInstrucaoForm, 
    MaterialEscolarForm, CautelaMaterialEscolarForm,
    # Novos formulários ITE 01/2024
    PlanoGeralEnsinoForm, ItemPlanoGeralEnsinoForm, ProjetoPedagogicoForm, PlanoCursoEstagioForm,
    PlanoDisciplinaForm, PlanoPalestraForm, AtividadeTreinamentoCampoForm, AtividadeComplementarEnsinoForm,
    TesteConhecimentosProfissionaisForm, PlanoEstagioNivelamentoProfissionalForm,
    RelatorioAnualDEIPForm, ProcessoSelecaoAlunosForm, InscricaoProcessoSelecaoForm,
    RecursoProcessoSelecaoForm, TrabalhoConclusaoCursoForm, PlanoSegurancaForm, ClassificacaoFinalCursoForm,
    PedidoRevisaoProvaForm, DespachoInstrutorForm
)
from .permissoes_simples import tem_permissao


# ============================================================================
# FUNÇÕES AUXILIARES DE PERMISSÃO
# ============================================================================

def pode_visualizar_ensino(user):
    """Verifica se o usuário pode visualizar ensino"""
    if user.is_superuser:
        return True
    return tem_permissao(user, 'ENSINO', 'visualizar')

def pode_criar_ensino(user):
    """Verifica se o usuário pode criar ensino"""
    if user.is_superuser:
        return True
    return tem_permissao(user, 'ENSINO', 'criar')

def pode_editar_ensino(user):
    """Verifica se o usuário pode editar ensino"""
    if user.is_superuser:
        return True
    return tem_permissao(user, 'ENSINO', 'editar')

def pode_excluir_ensino(user):
    """Verifica se o usuário pode excluir ensino"""
    if user.is_superuser:
        return True
    return tem_permissao(user, 'ENSINO', 'EXCLUIR')

def _eh_usuario_master(user):
    try:
        from .models import UsuarioMaster
        return bool(user and user.is_authenticated and UsuarioMaster.objects.filter(username=user.username, ativo=True).exists())
    except Exception:
        return False

def _eh_coordenador_ou_supervisor(user):
    try:
        militar = getattr(user, 'militar', None)
        if not militar:
            return False
        from .models import TurmaEnsino
        from django.db.models import Q
        return TurmaEnsino.objects.filter(
            Q(supervisor_curso=militar) |
            Q(coordenador_curso=militar) |
            Q(supervisor_turma=militar) |
            Q(coordenador_turma=militar)
        ).exists()
    except Exception:
        return False

def _usuario_vinculado_turma(user, turma):
    try:
        if user.is_superuser or _eh_usuario_master(user):
            return True
        militar = getattr(user, 'militar', None)
        if not militar:
            return False
        return (
            turma.supervisor_curso_id == militar.id or
            turma.coordenador_curso_id == militar.id or
            turma.supervisor_turma_id == militar.id or
            turma.coordenador_turma_id == militar.id
        )
    except Exception:
        return False

def _filtrar_turmas_vinculadas(user, turmas_qs):
    try:
        if user.is_superuser or _eh_usuario_master(user):
            return turmas_qs
        militar = getattr(user, 'militar', None)
        if not militar:
            return turmas_qs
        from django.db.models import Q
        return turmas_qs.filter(
            Q(supervisor_curso=militar) |
            Q(coordenador_curso=militar) |
            Q(supervisor_turma=militar) |
            Q(coordenador_turma=militar)
        )
    except Exception:
        return turmas_qs

def _eh_coordenador_ou_supervisor_curso(user):
    try:
        militar = getattr(user, 'militar', None)
        if not militar:
            return False
        from .models import CursoEnsino
        from django.db.models import Q
        return CursoEnsino.objects.filter(
            Q(coordenador_militar=militar) |
            Q(turmas__supervisor_curso=militar) |
            Q(turmas__coordenador_curso=militar) |
            Q(turmas__supervisor_turma=militar) |
            Q(turmas__coordenador_turma=militar)
        ).distinct().exists()
    except Exception:
        return False

def _usuario_vinculado_curso(user, curso):
    try:
        if user.is_superuser or _eh_usuario_master(user):
            return True
        militar = getattr(user, 'militar', None)
        if not militar:
            return False
        if getattr(curso, 'coordenador_militar_id', None) == militar.id:
            return True
        from .models import TurmaEnsino
        return TurmaEnsino.objects.filter(
            curso_id=curso.id
        ).filter(
            Q(supervisor_curso=militar) |
            Q(coordenador_curso=militar) |
            Q(supervisor_turma=militar) |
            Q(coordenador_turma=militar)
        ).exists()
    except Exception:
        return False

def _filtrar_cursos_vinculados(user, cursos_qs):
    try:
        if user.is_superuser or _eh_usuario_master(user):
            return cursos_qs
        militar = getattr(user, 'militar', None)
        if not militar:
            return cursos_qs
        from django.db.models import Q
        return cursos_qs.filter(
            Q(coordenador_militar=militar) |
            Q(turmas__supervisor_curso=militar) |
            Q(turmas__coordenador_curso=militar) |
            Q(turmas__supervisor_turma=militar) |
            Q(turmas__coordenador_turma=militar)
        ).distinct()
    except Exception:
        return cursos_qs

def _filtrar_edicoes_vinculadas(user, edicoes_qs):
    try:
        if user.is_superuser or _eh_usuario_master(user):
            return edicoes_qs
        from .models import CursoEnsino
        cursos = _filtrar_cursos_vinculados(user, CursoEnsino.objects.all()).values_list('id', flat=True)
        return edicoes_qs.filter(curso_id__in=list(cursos))
    except Exception:
        return edicoes_qs

def _filtrar_qs_por_vinculo(user, qs, curso_field='curso', turma_field='turma'):
    try:
        if user.is_superuser or _eh_usuario_master(user):
            return qs
        militar = getattr(user, 'militar', None)
        if not militar:
            return qs.none()
        from django.db.models import Q
        filtro = (
            Q(**{f"{curso_field}__coordenador_militar": militar}) |
            Q(**{f"{turma_field}__supervisor_curso": militar}) |
            Q(**{f"{turma_field}__coordenador_curso": militar}) |
            Q(**{f"{turma_field}__supervisor_turma": militar}) |
            Q(**{f"{turma_field}__coordenador_turma": militar})
        )
        return qs.filter(filtro).distinct()
    except Exception:
        return qs

def _usuario_vinculado_obj_ensino(user, obj):
    try:
        if user.is_superuser or _eh_usuario_master(user):
            return True
        curso = getattr(obj, 'curso', None)
        turma = getattr(obj, 'turma', None)
        if curso and _usuario_vinculado_curso(user, curso):
            return True
        if turma and _usuario_vinculado_turma(user, turma):
            return True
        return False
    except Exception:
        return False

# ============================================================================
# 0. PESSOAS EXTERNAS (Auxiliar - usada por outros módulos)
# ============================================================================

@login_required
def solicitar_revisao_prova_form(request, nota_id):
    nota = get_object_or_404(NotaAvaliacao.objects.select_related('aluno', 'avaliacao'), pk=nota_id)
    aluno = nota.aluno
    if request.session.get('ensino_tipo') != 'aluno' or request.session.get('ensino_id') != aluno.pk:
        messages.error(request, 'Acesso negado.')
        return redirect('militares:ensino_login')
    if PedidoRevisaoProva.objects.filter(nota_avaliacao=nota, aluno=aluno).exists():
        messages.info(request, 'Já existe uma solicitação de revisão para esta nota.')
        return redirect('militares:ensino_dashboard_aluno')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    template_name = 'militares/ensino/revisoes/_solicitar_form_partial.html' if is_ajax else 'militares/ensino/revisoes/solicitar.html'
    from django.utils import timezone
    conhecimento = getattr(nota, 'data_lancamento', None) or timezone.now()
    prazo_limite = conhecimento
    from datetime import timedelta
    adicionados = 0
    while adicionados < 2:
        prazo_limite += timedelta(days=1)
        if prazo_limite.weekday() < 5:
            adicionados += 1
    if request.method == 'POST':
        form = PedidoRevisaoProvaForm(request.POST, nota_avaliacao=nota)
        if timezone.now() > prazo_limite:
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': 'Prazo de 2 dias úteis para solicitar revisão expirado.'}, status=400)
            messages.error(request, 'Prazo de 2 dias úteis para solicitar revisão expirado.')
            return redirect('militares:ensino_dashboard_aluno')
        if form.is_valid():
            pedido = PedidoRevisaoProva.objects.create(
                nota_avaliacao=nota,
                aluno=aluno,
                fundamentacao=form.cleaned_data['fundamentacao'],
                itens_solicitados=form.cleaned_data.get('itens_solicitados') or '',
                status='SOLICITADA',
                etapa='ALUNO_SOLICITOU'
            )
            pedido.data_conhecimento_oficial = getattr(nota, 'data_lancamento', None) or timezone.now()
            pedido.set_prazo_solicitacao()
            pedido.save()
            next_url = request.GET.get('next')
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': True, 'redirect': next_url or reverse('militares:ensino_dashboard_aluno')})
            messages.success(request, 'Revisão de prova solicitada.')
            return redirect(next_url or 'militares:ensino_dashboard_aluno')
        return render(request, 'militares/ensino/revisoes/_solicitar_form_partial.html', {'form': form, 'nota': nota, 'aluno': aluno, 'prazo_limite_solicitacao': prazo_limite})
    else:
        form = PedidoRevisaoProvaForm()
        return render(request, template_name, {'form': form, 'nota': nota, 'aluno': aluno, 'prazo_limite_solicitacao': prazo_limite})
def listar_pessoas_externas(request):
    """Lista todas as pessoas externas"""
    pessoas = PessoaExterna.objects.all()
    
    busca = request.GET.get('busca', '')
    tipo_pessoa = request.GET.get('tipo_pessoa', '')
    ativo = request.GET.get('ativo', '')
    
    if busca:
        pessoas = pessoas.filter(
            Q(nome_completo__icontains=busca) |
            Q(cpf__icontains=busca) |
            Q(email__icontains=busca) |
            Q(instituicao_origem__icontains=busca)
        )
    
    if tipo_pessoa:
        pessoas = pessoas.filter(tipo_pessoa=tipo_pessoa)
    
    if ativo == 'true':
        pessoas = pessoas.filter(ativo=True)
    elif ativo == 'false':
        pessoas = pessoas.filter(ativo=False)
    
    paginator = Paginator(pessoas, 20)
    page = request.GET.get('page')
    pessoas = paginator.get_page(page)
    
    context = {
        'pessoas': pessoas,
        'tipos_pessoa': PessoaExterna.TIPO_PESSOA_CHOICES,
    }
    return render(request, 'militares/ensino/pessoas_externas/listar.html', context)


@login_required
def criar_pessoa_externa(request):
    """Cria uma nova pessoa externa"""
    if request.method == 'POST':
        form = PessoaExternaForm(request.POST, request.FILES)
        if form.is_valid():
            pessoa = form.save()
            messages.success(request, f'Pessoa externa {pessoa.nome_completo} criada com sucesso!')
            return redirect('militares:ensino_pessoa_externa_detalhes', pk=pessoa.pk)
    else:
        form = PessoaExternaForm()
    
    return render(request, 'militares/ensino/pessoas_externas/criar.html', {'form': form})


@login_required
def editar_pessoa_externa(request, pk):
    """Edita uma pessoa externa existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar pessoas externas.')
        return redirect('militares:ensino_pessoas_externas_listar')
    
    pessoa = get_object_or_404(PessoaExterna, pk=pk)
    
    if request.method == 'POST':
        form = PessoaExternaForm(request.POST, request.FILES, instance=pessoa)
        if form.is_valid():
            pessoa = form.save()
            messages.success(request, f'Pessoa externa {pessoa.nome_completo} atualizada com sucesso!')
            return redirect('militares:ensino_pessoa_externa_detalhes', pk=pessoa.pk)
    else:
        form = PessoaExternaForm(instance=pessoa)
    
    return render(request, 'militares/ensino/pessoas_externas/editar.html', {'form': form, 'pessoa': pessoa})


@login_required
def detalhes_pessoa_externa(request, pk):
    """Detalhes completos de uma pessoa externa"""
    pessoa = get_object_or_404(PessoaExterna, pk=pk)
    
    # Verificar em quais perfis a pessoa está cadastrada
    alunos = AlunoEnsino.objects.filter(pessoa_externa=pessoa)
    # Instrutores agora são apenas militares, não pessoas externas
    instrutores = InstrutorEnsino.objects.none()
    monitores = MonitorEnsino.objects.filter(pessoa_externa=pessoa)
    
    context = {
        'pessoa': pessoa,
        'alunos': alunos,
        'instrutores': instrutores,
        'monitores': monitores,
    }
    return render(request, 'militares/ensino/pessoas_externas/detalhes.html', context)


# ============================================================================
# 6. ALUNOS (Relacionados a Turma) - Movido para depois de Turmas
# ============================================================================

@login_required
def listar_alunos(request):
    """Lista todos os alunos (militares ou externos)"""
    alunos = AlunoEnsino.objects.select_related('militar', 'pessoa_externa').all()
    # Restringir coordenadores/supervisores às turmas vinculadas
    if _eh_coordenador_ou_supervisor(request.user):
        from militares.models import TurmaEnsino
        turmas_permitidas = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.all())
        alunos = alunos.filter(turma__in=turmas_permitidas)
    
    # Filtros
    busca = request.GET.get('busca', '')
    tipo_aluno = request.GET.get('tipo_aluno', '')
    situacao = request.GET.get('situacao', '')
    
    if busca:
        alunos = alunos.filter(
            Q(militar__nome_completo__icontains=busca) |
            Q(militar__cpf__icontains=busca) |
            Q(militar__matricula__icontains=busca) |
            Q(pessoa_externa__nome_completo__icontains=busca) |
            Q(pessoa_externa__cpf__icontains=busca) |
            Q(nome_outra_forca__icontains=busca) |
            Q(cpf_outra_forca__icontains=busca) |
            Q(matricula_outra_forca__icontains=busca) |
            Q(nome_civil__icontains=busca) |
            Q(cpf_civil__icontains=busca) |
            Q(matricula__icontains=busca)
        )
    
    if tipo_aluno:
        alunos = alunos.filter(tipo_aluno=tipo_aluno)
    
    if situacao:
        alunos = alunos.filter(situacao=situacao)
    
    # Ordenação por hierarquia militar (mais antigo para mais moderno)
    try:
        ordem_hierarquica = [codigo for codigo, _nome in POSTO_GRADUACAO_CHOICES]
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(999),
            output_field=IntegerField(),
        )
        alunos = alunos.annotate(hierarquia_ordem=hierarquia_ordem).order_by(
            'hierarquia_ordem',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'pessoa_externa__nome_completo',
            'nome_civil',
            'nome_outra_forca'
        )
    except Exception:
        # Fallback: ordenar por nome caso algo falhe
        alunos = alunos.order_by('militar__nome_completo', 'pessoa_externa__nome_completo', 'nome_civil', 'nome_outra_forca')

    paginator = Paginator(alunos, 20)
    page = request.GET.get('page')
    alunos = paginator.get_page(page)
    
    context = {
        'alunos': alunos,
        'situacoes': AlunoEnsino.SITUACAO_CHOICES,
        'tipos_aluno': AlunoEnsino.TIPO_ALUNO_CHOICES,
    }
    return render(request, 'militares/ensino/alunos/listar.html', context)


@login_required
def criar_aluno(request):
    """Cria um novo aluno"""
    if request.method == 'POST':
        form = AlunoEnsinoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                aluno = form.save(commit=False)
                # Garantir que o tipo_aluno está definido
                if not aluno.tipo_aluno:
                    tipo_aluno = form.cleaned_data.get('tipo_aluno')
                    if tipo_aluno:
                        aluno.tipo_aluno = tipo_aluno
                    elif aluno.militar:
                        aluno.tipo_aluno = 'BOMBEIRO'
                    elif aluno.nome_outra_forca:
                        aluno.tipo_aluno = 'OUTRA_FORCA'
                    elif aluno.nome_civil:
                        aluno.tipo_aluno = 'CIVIL'
                
                # Garantir situação padrão
                if not aluno.situacao:
                    aluno.situacao = 'ATIVO'
                
                aluno.save()

                # Definir senha padrão como CPF (somente dígitos)
                try:
                    cpf = aluno.get_cpf()
                    if cpf:
                        cpf_digits = ''.join([c for c in cpf if c.isdigit()])
                        if cpf_digits:
                            from django.contrib.auth.hashers import make_password
                            aluno.senha_hash = make_password(cpf_digits)
                            aluno.save(update_fields=['senha_hash'])
                except Exception:
                    pass
                
                # Obter nome do aluno
                if aluno.tipo_aluno == 'BOMBEIRO' and aluno.militar:
                    nome_aluno = aluno.militar.nome_completo
                elif aluno.tipo_aluno == 'OUTRA_FORCA' and aluno.nome_outra_forca:
                    nome_aluno = aluno.nome_outra_forca
                elif aluno.tipo_aluno == 'CIVIL' and aluno.nome_civil:
                    nome_aluno = aluno.nome_civil
                else:
                    nome_aluno = 'Aluno'
                
                matricula_texto = f' ({aluno.matricula})' if aluno.matricula else ''
                messages.success(request, f'Aluno {nome_aluno}{matricula_texto} criado com sucesso!')
                return redirect('militares:ensino_aluno_detalhes', pk=aluno.pk)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao criar aluno: {str(e)}')
                messages.error(request, f'Erro ao criar aluno: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = AlunoEnsinoForm()
    
    return render(request, 'militares/ensino/alunos/criar.html', {'form': form})


@login_required
def editar_aluno(request, pk):
    """Edita um aluno existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar alunos.')
        return redirect('militares:ensino_alunos_listar')
    
    aluno = get_object_or_404(AlunoEnsino, pk=pk)
    
    if request.method == 'POST':
        form = AlunoEnsinoForm(request.POST, request.FILES, instance=aluno)
        if form.is_valid():
            aluno = form.save()
            nome_aluno = aluno.get_nome_completo() or 'Aluno'
            matricula_texto = f' ({aluno.matricula})' if aluno.matricula else ''
            messages.success(request, f'Aluno {nome_aluno}{matricula_texto} atualizado com sucesso!')
            return redirect('militares:ensino_aluno_detalhes', pk=aluno.pk)
    else:
        form = AlunoEnsinoForm(instance=aluno)
    
    return render(request, 'militares/ensino/alunos/editar.html', {'form': form, 'aluno': aluno})


@login_required
def detalhes_aluno(request, pk):
    """Detalhes completos de um aluno"""
    aluno = get_object_or_404(AlunoEnsino.objects.select_related('militar', 'pessoa_externa', 'turma'), pk=pk)
    
    # Frequências - ordenadas por data da aula, incluindo turma
    frequencias = FrequenciaAula.objects.filter(aluno=aluno).select_related('aula', 'aula__disciplina', 'aula__turma').order_by('aula__data_aula')
    
    # Aproveitamentos
    aproveitamentos = AproveitamentoDisciplina.objects.filter(aluno=aluno).select_related('disciplina', 'turma')
    
    # Notas - ordenadas por data de lançamento, incluindo turma
    notas = NotaAvaliacao.objects.filter(aluno=aluno).select_related('avaliacao', 'avaliacao__disciplina', 'avaliacao__turma').order_by('data_lancamento')
    
    # Documentos - ordenados por data de upload (mais recentes primeiro)
    documentos = DocumentoAluno.objects.filter(aluno=aluno).order_by('-data_upload')
    
    # Ocorrências - ordenadas por data de ocorrência
    ocorrencias = OcorrenciaDisciplinar.objects.filter(aluno=aluno).select_related('turma').order_by('data_ocorrencia')
    
    # Histórico - ordenado por turma e disciplina
    historico = HistoricoEscolar.objects.filter(aluno=aluno).select_related('curso', 'turma', 'disciplina').order_by('turma', 'disciplina')
    
    # Cautelas de material
    cautelas = CautelaMaterialEscolar.objects.filter(aluno=aluno).select_related('material')
    
    # Buscar todas as turmas que o aluno participou
    # 1. Turma atual (se houver)
    turmas_participadas = []
    if aluno.turma:
        turmas_participadas.append(aluno.turma)
    
    # 2. Turmas do histórico escolar
    turmas_historico = HistoricoEscolar.objects.filter(aluno=aluno).values_list('turma', flat=True).distinct()
    for turma_id in turmas_historico:
        if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
            from militares.models import TurmaEnsino
            try:
                turma = TurmaEnsino.objects.get(pk=turma_id)
                turmas_participadas.append(turma)
            except TurmaEnsino.DoesNotExist:
                pass
    
    # 3. Turmas das frequências
    turmas_frequencias = FrequenciaAula.objects.filter(aluno=aluno).values_list('aula__turma', flat=True).distinct()
    for turma_id in turmas_frequencias:
        if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
            from militares.models import TurmaEnsino
            try:
                turma = TurmaEnsino.objects.get(pk=turma_id)
                turmas_participadas.append(turma)
            except TurmaEnsino.DoesNotExist:
                pass
    
    # 4. Turmas das notas
    turmas_notas = NotaAvaliacao.objects.filter(aluno=aluno).values_list('avaliacao__turma', flat=True).distinct()
    for turma_id in turmas_notas:
        if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
            from militares.models import TurmaEnsino
            try:
                turma = TurmaEnsino.objects.get(pk=turma_id)
                turmas_participadas.append(turma)
            except TurmaEnsino.DoesNotExist:
                pass
    
    # 5. Turmas das ocorrências
    turmas_ocorrencias = OcorrenciaDisciplinar.objects.filter(aluno=aluno).values_list('turma', flat=True).distinct()
    for turma_id in turmas_ocorrencias:
        if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
            from militares.models import TurmaEnsino
            try:
                turma = TurmaEnsino.objects.get(pk=turma_id)
                turmas_participadas.append(turma)
            except TurmaEnsino.DoesNotExist:
                pass
    
    # Organizar dados por turma (como lista para facilitar no template)
    dados_por_turma_lista = []
    for turma in turmas_participadas:
        frequencias_turma = frequencias.filter(aula__turma=turma)
        notas_turma = notas.filter(avaliacao__turma=turma)
        ocorrencias_turma = ocorrencias.filter(turma=turma)
        historicos_turma = historico.filter(turma=turma)
        aproveitamentos_turma = aproveitamentos.filter(turma=turma)
        
        # Calcular resumo de frequências
        resumo_frequencias = {
            'total': frequencias_turma.count(),
            'presentes': frequencias_turma.filter(presenca='PRESENTE').count(),
            'faltas': frequencias_turma.filter(presenca='FALTA').count(),
            'faltas_justificadas': frequencias_turma.filter(presenca='FALTA_JUSTIFICADA').count(),
            'atrasos': frequencias_turma.filter(presenca='ATRASO').count(),
            'saidas_antecipadas': frequencias_turma.filter(presenca='SAIDA_ANTECIPADA').count(),
        }
        
        # Calcular notas por disciplina para este aluno nesta turma
        from militares.models import AvaliacaoEnsino
        
        avaliacoes_turma = AvaliacaoEnsino.objects.filter(turma=turma).select_related('disciplina').order_by('disciplina', 'data_avaliacao')
        
        # Buscar todas as disciplinas da turma
        disciplinas_turma = set()
        for avaliacao in avaliacoes_turma:
            disciplinas_turma.add(avaliacao.disciplina)
        
        # Adicionar disciplinas das frequências
        for frequencia in frequencias_turma:
            if frequencia.aula.disciplina:
                disciplinas_turma.add(frequencia.aula.disciplina)
        
        if not disciplinas_turma:
            disciplinas_turma = set(turma.disciplinas.all())
        
        # Estrutura para frequências por disciplina
        frequencias_por_disciplina = {}
        
        # Estrutura para notas por disciplina
        notas_por_disciplina = {}
        
        for disciplina in disciplinas_turma:
            disciplina_id = disciplina.pk
            
            # Inicializar estrutura de frequências por disciplina
            frequencias_disciplina = frequencias_turma.filter(aula__disciplina=disciplina)
            frequencias_por_disciplina[disciplina_id] = {
                'disciplina': disciplina,
                'frequencias': frequencias_disciplina,
                'total': frequencias_disciplina.count(),
                'presentes': frequencias_disciplina.filter(presenca='PRESENTE').count(),
                'faltas': frequencias_disciplina.filter(presenca='FALTA').count(),
                'faltas_justificadas': frequencias_disciplina.filter(presenca='FALTA_JUSTIFICADA').count(),
                'atrasos': frequencias_disciplina.filter(presenca='ATRASO').count(),
                'saidas_antecipadas': frequencias_disciplina.filter(presenca='SAIDA_ANTECIPADA').count(),
            }
            
            # Inicializar estrutura de notas por disciplina
            notas_por_disciplina[disciplina_id] = {
                'disciplina': disciplina,
                'dados_aluno': {
                    'notas': [None, None, None, None],  # 4 avaliações
                    'pesos': [0, 0, 0, 0],
                    'nota_recuperacao': None,
                    'media_final': None,
                    'status': None
                }
            }
        
        # Buscar todas as notas do aluno nas avaliações desta turma
        notas_avaliacoes_turma = NotaAvaliacao.objects.filter(
            avaliacao__turma=turma,
            aluno=aluno
        ).select_related('avaliacao', 'avaliacao__disciplina')
        
        # Preencher notas das avaliações
        for nota_obj in notas_avaliacoes_turma:
            disciplina_id = nota_obj.avaliacao.disciplina.pk
            
            if disciplina_id in notas_por_disciplina:
                dados_aluno = notas_por_disciplina[disciplina_id]['dados_aluno']
                
                # Se for avaliação de recuperação, armazenar separadamente com peso
                if nota_obj.avaliacao.tipo == 'RECUPERACAO':
                    dados_aluno['nota_recuperacao'] = nota_obj.nota
                    dados_aluno['peso_recuperacao'] = nota_obj.avaliacao.peso
                else:
                    # Encontrar posição da avaliação (1ª, 2ª, 3ª ou 4ª)
                    avaliacoes_disciplina = [a for a in avaliacoes_turma if a.disciplina.pk == disciplina_id and a.tipo != 'RECUPERACAO']
                    avaliacoes_disciplina_ordenadas = sorted(avaliacoes_disciplina, key=lambda x: (x.data_avaliacao if x.data_avaliacao else date.min, x.id))
                    
                    try:
                        posicao = avaliacoes_disciplina_ordenadas.index(nota_obj.avaliacao)
                        if posicao < 4:  # Máximo 4 avaliações
                            dados_aluno['notas'][posicao] = nota_obj.nota
                            dados_aluno['pesos'][posicao] = nota_obj.avaliacao.peso
                    except ValueError:
                        pass
        
        # Calcular média final e status para cada disciplina
        soma_medias_finais = 0
        disciplinas_com_media = 0
        
        for disciplina_id, dados_disciplina in notas_por_disciplina.items():
            disciplina = dados_disciplina['disciplina']
            media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
            dados_aluno = dados_disciplina['dados_aluno']
            
            notas_list = dados_aluno['notas']
            pesos_list = dados_aluno['pesos']
            nota_recuperacao = dados_aluno.get('nota_recuperacao')
            
            # Se houver nota de recuperação, usar apenas ela como média final
            # A média anterior das avaliações regulares não entra no cálculo
            if nota_recuperacao is not None:
                media_final = float(nota_recuperacao)
                dados_aluno['media_final'] = media_final  # Valor real, sem arredondamento
                
                # Determinar status baseado na nota de recuperação
                media_minima_recuperacao = float(disciplina.media_minima_recuperacao) if disciplina.media_minima_recuperacao else 6.0
                if media_final >= media_minima_recuperacao:
                    dados_aluno['status'] = 'APROVADO'  # Aprovado com recuperação
                else:
                    dados_aluno['status'] = 'REPROVADO'  # Reprovado na recuperação
                
                soma_medias_finais += media_final  # Usar valor real
                disciplinas_com_media += 1
            else:
                # Calcular média ponderada apenas das avaliações regulares
                soma_notas_pesos = 0
                soma_pesos = 0
                
                for i in range(4):
                    if notas_list[i] is not None and pesos_list[i] > 0:
                        soma_notas_pesos += float(notas_list[i]) * float(pesos_list[i])
                        soma_pesos += float(pesos_list[i])
                
                if soma_pesos > 0:
                    media_final_real = soma_notas_pesos / soma_pesos  # Valor real sem arredondamento
                    dados_aluno['media_final'] = media_final_real  # Usar valor real, sem arredondamento
                else:
                    media_final_real = None
                    dados_aluno['media_final'] = None
                
                if media_final_real is not None:
                    soma_medias_finais += media_final_real  # Usar valor real para soma geral
                    disciplinas_com_media += 1
                
                # Determinar status baseado APENAS na média final
                # IMPORTANTE: Usar o valor REAL da média (sem arredondamento) para comparação
                # Se a média final >= média mínima → Aprovado
                # Se a média final < média mínima → Recuperação
                if media_final_real is not None:
                    if media_final_real >= media_minima:
                        dados_aluno['status'] = 'APROVADO'
                    else:
                        # Média real menor que a mínima = recuperação
                        dados_aluno['status'] = 'RECUPERACAO'
                else:
                    # Sem média = recuperação
                    dados_aluno['status'] = 'RECUPERACAO'
        
        # Calcular média geral de todas as disciplinas
        media_geral_disciplinas = None
        if disciplinas_com_media > 0:
            media_geral_disciplinas = soma_medias_finais / disciplinas_com_media  # Valor real, sem arredondamento
        
        dados_por_turma_lista.append({
            'turma': turma,
            'frequencias': frequencias_turma,
            'notas': notas_turma,
            'ocorrencias': ocorrencias_turma,
            'historicos': historicos_turma,
            'aproveitamentos': aproveitamentos_turma,
            'resumo_frequencias': resumo_frequencias,
            'frequencias_por_disciplina': frequencias_por_disciplina,
            'notas_por_disciplina': notas_por_disciplina,
            'media_geral_disciplinas': media_geral_disciplinas,
        })
    
    revisoes = PedidoRevisaoProva.objects.filter(aluno=aluno).select_related('nota_avaliacao', 'nota_avaliacao__avaliacao')

    context = {
        'aluno': aluno,
        'frequencias': frequencias,
        'aproveitamentos': aproveitamentos,
        'notas': notas,
        'documentos': documentos,
        'ocorrencias': ocorrencias,
        'historico': historico,
        'cautelas': cautelas,
        'turmas_participadas': turmas_participadas,
        'dados_por_turma_lista': dados_por_turma_lista,
        'revisoes': revisoes,
    }
    return render(request, 'militares/ensino/alunos/detalhes.html', context)


@login_required
def solicitar_revisao_prova(request, nota_id):
    nota = get_object_or_404(NotaAvaliacao.objects.select_related('aluno', 'avaliacao'), pk=nota_id)
    aluno = nota.aluno
    if request.session.get('ensino_tipo') != 'aluno' or request.session.get('ensino_id') != aluno.pk:
        messages.error(request, 'Acesso negado.')
        return redirect('militares:ensino_login')
    from django.utils import timezone
    conhecimento = getattr(nota, 'data_lancamento', None) or timezone.now()
    prazo_limite = conhecimento
    from datetime import timedelta
    adicionados = 0
    while adicionados < 2:
        prazo_limite += timedelta(days=1)
        if prazo_limite.weekday() < 5:
            adicionados += 1
    if timezone.now() > prazo_limite:
        messages.error(request, 'Prazo de 2 dias úteis para solicitar revisão expirado.')
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('militares:ensino_dashboard_aluno')
    if not PedidoRevisaoProva.objects.filter(nota_avaliacao=nota, aluno=aluno).exists():
        fundamentacao = request.GET.get('fundamentacao', '')
        PedidoRevisaoProva.objects.create(
            nota_avaliacao=nota,
            aluno=aluno,
            fundamentacao=fundamentacao,
            status='SOLICITADA',
            etapa='ALUNO_SOLICITOU'
        )
        messages.success(request, 'Revisão de prova solicitada.')
        logger.info(f"PedidoRevisao criado: nota={nota.pk}, aluno={aluno.pk}, user={request.user.id}, etapa=ALUNO_SOLICITOU")
    else:
        messages.info(request, 'Já existe uma solicitação de revisão para esta nota.')
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('militares:ensino_aluno_detalhes', pk=aluno.pk)


@login_required
def ensino_despachar_revisao_para_instrutor(request, pedido_id):
    pedido = get_object_or_404(PedidoRevisaoProva.objects.select_related('nota_avaliacao__avaliacao__disciplina'), pk=pedido_id)
    tipo = request.session.get('ensino_tipo')
    if tipo == 'aluno':
        messages.error(request, 'Acesso negado.')
        return redirect('militares:ensino_login')
    disciplina = pedido.nota_avaliacao.avaliacao.disciplina
    instrutor_militar = getattr(disciplina, 'instrutor_responsavel_militar', None)
    instrutor = None
    if instrutor_militar:
        instrutor = InstrutorEnsino.objects.filter(militar=instrutor_militar, ativo=True).first()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    template_name = 'militares/ensino/revisoes/_despachar_instrutor_form_partial.html' if is_ajax else 'militares/ensino/revisoes/despachar_instrutor.html'
    if request.method == 'POST':
        form = DespachoInstrutorForm(request.POST)
        if form.is_valid():
            pedido.instrutor_responsavel = instrutor
            pedido.etapa = 'DESPACHADA_INSTRUTOR'
            pedido.status = 'EM_ANALISE'
            pedido.despacho_envio_instrutor_texto = form.cleaned_data['despacho']
            pedido.despacho_envio_instrutor_por = request.user
            pedido.despacho_envio_instrutor_data = timezone.now()
            pedido.set_prazo_instrutor()
            pedido.save()
            logger.info(f"PedidoRevisao despachado ao instrutor: pedido={pedido.pk}, instrutor={getattr(pedido.instrutor_responsavel, 'pk', None)}, user={request.user.id}")
            messages.success(request, 'Pedido despachado ao instrutor responsável.')
            next_url = request.GET.get('next')
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': True, 'redirect': next_url or reverse('militares:ensino_dashboard')})
            return redirect(next_url or 'militares:ensino_dashboard')
    else:
        form = DespachoInstrutorForm()
    return render(request, template_name, {
        'pedido': pedido,
        'disciplina': disciplina,
        'instrutor': instrutor,
        'form': form,
    })


@login_required
def instrutor_parecer_revisao(request, pedido_id):
    pedido = get_object_or_404(PedidoRevisaoProva.objects.select_related('instrutor_responsavel'), pk=pedido_id)
    if request.session.get('ensino_tipo') != 'instrutor':
        messages.error(request, 'Acesso negado.')
        return redirect('militares:ensino_login')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    template_name = 'militares/ensino/revisoes/_instrutor_parecer_form_partial.html'
    if request.method == 'POST':
        from .forms_ensino import InstrutorParecerForm
        from django.utils import timezone
        if pedido.prazo_limite_instrutor and timezone.now() > pedido.prazo_limite_instrutor:
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': 'Prazo de 3 dias úteis para parecer do instrutor expirado.'}, status=400)
            messages.error(request, 'Prazo de 3 dias úteis para parecer do instrutor expirado.')
            return redirect('militares:ensino_dashboard_instrutor')
        form = InstrutorParecerForm(request.POST, instance=pedido)
        if not form.is_valid():
            if is_ajax:
                return render(request, template_name, {'form': form, 'pedido': pedido})
            messages.error(request, '; '.join([str(e) for e in sum(form.errors.values(), [])]))
            return redirect('militares:ensino_dashboard_instrutor')
        obj = form.save(commit=False)
        obj.etapa = 'PARECER_INSTRUTOR'
        obj.status = 'DEFERIDA' if obj.parecer_instrutor == 'FAVORAVEL' else 'INDEFERIDA'
        # Atualizar nota se favorável e nova_nota informada (sem diminuir)
        if obj.parecer_instrutor == 'FAVORAVEL' and obj.nova_nota_instrutor is not None:
            try:
                nota_atual = obj.nota_avaliacao.nota
                if obj.nova_nota_instrutor is not None and (nota_atual is None or obj.nova_nota_instrutor >= nota_atual):
                    obj.nota_avaliacao.nota = obj.nova_nota_instrutor
                    obj.nota_avaliacao.save(update_fields=['nota'])
            except Exception:
                pass
        obj.save()
        obj.save()
        logger.info(f"Parecer instrutor: pedido={pedido.pk}, decisao={obj.parecer_instrutor}, user={request.user.id}")
        messages.success(request, 'Parecer do instrutor registrado.')
        next_url = request.GET.get('next')
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'redirect': next_url or reverse('militares:ensino_dashboard_instrutor')})
        return redirect(next_url or 'militares:ensino_dashboard_instrutor')
    # GET: retornar parcial do modal
    from .forms_ensino import InstrutorParecerForm
    form = InstrutorParecerForm(instance=pedido)
    return render(request, template_name, {'form': form, 'pedido': pedido})


@login_required
def aluno_recorrer_diretoria(request, pedido_id):
    pedido = get_object_or_404(PedidoRevisaoProva.objects.select_related('aluno'), pk=pedido_id)
    if request.session.get('ensino_tipo') != 'aluno' or request.session.get('ensino_id') != pedido.aluno_id:
        messages.error(request, 'Acesso negado.')
        return redirect('militares:ensino_login')
    if not (pedido.etapa == 'PARECER_INSTRUTOR' and pedido.status == 'INDEFERIDA'):
        messages.error(request, 'Este pedido não está elegível para recurso à diretoria.')
        return redirect('militares:ensino_dashboard_aluno')
    pedido.etapa = 'RECURSO_DIRETORIA'
    pedido.status = 'EM_ANALISE'
    pedido.save()
    logger.info(f"Recurso à diretoria: pedido={pedido.pk}, user={request.user.id}")
    messages.success(request, 'Recurso à diretoria registrado.')
    next_url = request.GET.get('next')
    return redirect(next_url or 'militares:ensino_dashboard_aluno')


@login_required
def aluno_reenviar_recurso(request, pedido_id):
    pedido = get_object_or_404(PedidoRevisaoProva.objects.select_related('aluno'), pk=pedido_id)
    if request.session.get('ensino_tipo') != 'aluno' or request.session.get('ensino_id') != pedido.aluno_id:
        messages.error(request, 'Acesso negado.')
        return redirect('militares:ensino_login')
    if not (pedido.etapa == 'PARECER_FINAL' and pedido.status == 'INDEFERIDA'):
        messages.error(request, 'Este pedido não está elegível para reenvio.')
        return redirect('militares:ensino_dashboard_aluno')
    nova_fundamentacao = request.POST.get('fundamentacao') or request.GET.get('fundamentacao')
    if nova_fundamentacao:
        pedido.fundamentacao = nova_fundamentacao
    pedido.status = 'SOLICITADA'
    pedido.etapa = 'ALUNO_SOLICITOU'
    pedido.instrutor_responsavel = None
    pedido.despacho_envio_instrutor_texto = None
    pedido.despacho_envio_instrutor_por = None
    pedido.despacho_envio_instrutor_data = None
    pedido.parecer_instrutor = None
    pedido.parecer_instrutor_texto = None
    pedido.parecer_final_texto = None
    pedido.comissao = None
    pedido.save()
    logger.info(f"Reenvio de recurso: pedido={pedido.pk}, user={request.user.id}")
    messages.success(request, 'Recurso reenviado para análise.')
    next_url = request.GET.get('next')
    return redirect(next_url or 'militares:ensino_dashboard')

@login_required
def ensino_nomear_comissao_revisao(request, pedido_id):
    pedido = get_object_or_404(PedidoRevisaoProva, pk=pedido_id)
    tipo = request.session.get('ensino_tipo')
    if tipo not in ['coordenador', 'supervisor']:
        messages.error(request, 'Acesso negado.')
        return redirect('militares:ensino_login')
    from .models import ComissaoPromocao
    if request.method == 'POST':
        comissao_id = request.POST.get('comissao_id')
        comissao = ComissaoPromocao.objects.filter(pk=comissao_id, status='ATIVA').first()
        if not comissao:
            messages.error(request, 'Comissão inválida.')
        else:
            pedido.comissao = comissao
            pedido.etapa = 'COMISSAO_NOMEADA'
            pedido.status = 'EM_ANALISE'
            pedido.set_prazo_comissao()
            pedido.save()
            messages.success(request, 'Comissão nomeada para análise do pedido.')
            next_url = request.GET.get('next')
            return redirect(next_url or 'militares:ensino_dashboard')
    comissoes = ComissaoPromocao.objects.filter(status='ATIVA')
    return render(request, 'militares/ensino/revisoes/nomear_comissao.html', {'pedido': pedido, 'comissoes': comissoes})


@login_required
def comissao_parecer_revisao(request, pedido_id):
    pedido = get_object_or_404(PedidoRevisaoProva, pk=pedido_id)
    # Permitir apenas membros da comissão nomeada
    from .models import MembroComissao
    membros = MembroComissao.objects.filter(comissao=pedido.comissao, ativo=True).select_related('usuario')
    usuarios_membros = set(m.usuario_id for m in membros if m.usuario_id)
    if request.user.id not in usuarios_membros:
        messages.error(request, 'Acesso negado. Você não é membro da comissão nomeada.')
        return redirect('militares:ensino_login')
    from .forms_ensino import ComissaoParecerForm
    if request.method == 'POST':
        from django.utils import timezone
        if pedido.prazo_limite_comissao and timezone.now() > pedido.prazo_limite_comissao:
            messages.error(request, 'Prazo de 8 dias úteis para parecer da comissão expirado.')
            return redirect('militares:ensino_dashboard_coordenador')
        form = ComissaoParecerForm(request.POST, instance=pedido)
        if not form.is_valid():
            messages.error(request, '; '.join([str(e) for e in sum(form.errors.values(), [])]))
            return redirect('militares:ensino_dashboard_coordenador')
        obj = form.save(commit=False)
        obj.etapa = 'PARECER_FINAL'
        # Decisão via parâmetro (mantendo compatibilidade)
        decisao = request.POST.get('decisao') or request.GET.get('decisao')
        if decisao not in ['DEFERIDA', 'INDEFERIDA']:
            messages.error(request, 'Decisão inválida.')
            return redirect('militares:ensino_dashboard_coordenador')
        obj.status = decisao
        # Atualizar nota final se informada e não reduzir
        try:
            base = obj.nota_avaliacao.nota
            if obj.nova_nota_instrutor is not None and obj.nova_nota_instrutor > (base or 0):
                base = obj.nova_nota_instrutor
            if obj.nova_nota_final is not None and (base is None or obj.nova_nota_final >= base):
                obj.nota_avaliacao.nota = obj.nova_nota_final
                obj.nota_avaliacao.save(update_fields=['nota'])
        except Exception:
            pass
        obj.save()
    else:
        decisao = request.GET.get('decisao')  # 'DEFERIDA' ou 'INDEFERIDA'
        texto = request.GET.get('texto', '')
        if decisao not in ['DEFERIDA', 'INDEFERIDA']:
            messages.error(request, 'Decisão inválida.')
            return redirect('militares:ensino_dashboard_coordenador')
        pedido.status = decisao
        pedido.etapa = 'PARECER_FINAL'
        pedido.parecer_final_texto = texto or pedido.parecer_final_texto
        pedido.save()
    logger.info(f"Parecer final comissão: pedido={pedido.pk}, decisao={decisao}, user={request.user.id}")
    messages.success(request, 'Parecer final registrado pela comissão.')
    next_url = request.GET.get('next')
    return redirect(next_url or 'militares:ensino_dashboard')


@login_required
def pedido_revisao_detalhes(request, pedido_id):
    pedido = get_object_or_404(PedidoRevisaoProva.objects.select_related(
        'nota_avaliacao__avaliacao__disciplina', 'aluno__militar', 'aluno__pessoa_externa', 'instrutor_responsavel', 'comissao'
    ), pk=pedido_id)
    return render(request, 'militares/ensino/revisoes/detalhes.html', {
        'pedido': pedido,
    })
# ============================================================================
# 4. INSTRUTORES (Relacionados a Turma e Disciplina)
# ============================================================================

@login_required
def listar_instrutores(request):
    """Lista todos os instrutores com informações sobre turmas e disciplinas"""
    from django.db.models import Count, Prefetch
    
    instrutores = InstrutorEnsino.objects.select_related('militar').filter(ativo=True)
    
    busca = request.GET.get('busca', '')
    if busca:
        instrutores = instrutores.filter(
            Q(militar__nome_completo__icontains=busca) |
            Q(militar__cpf__icontains=busca) |
            Q(nome_outra_forca__icontains=busca) |
            Q(nome_civil__icontains=busca) |
            Q(cpf_outra_forca__icontains=busca) |
            Q(cpf_civil__icontains=busca) |
            Q(habilitacoes__icontains=busca) |
            Q(especialidades__icontains=busca)
        )
    
    # Anotar com contagens de turmas e disciplinas para cada instrutor
    # Turmas onde é chefe (externo)
    turmas_chefe_externo = Prefetch(
        'turmas_chefiadas_externo',
        queryset=TurmaEnsino.objects.select_related('curso').only('id', 'identificacao', 'curso__nome').distinct()
    )
    
    # Disciplinas onde é responsável (externo)
    disciplinas_responsavel_externo = Prefetch(
        'disciplinas_responsaveis_externo',
        queryset=DisciplinaEnsino.objects.only('id', 'nome', 'codigo').distinct()
    )
    
    instrutores = instrutores.prefetch_related(turmas_chefe_externo, disciplinas_responsavel_externo)
    
    try:
        ordem_hierarquica = [codigo for codigo, _nome in POSTO_GRADUACAO_CHOICES]
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(999),
            output_field=IntegerField(),
        )
        instrutores = instrutores.annotate(hierarquia_ordem=hierarquia_ordem).order_by(
            'hierarquia_ordem',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'nome_outra_forca',
            'nome_civil'
        )
    except Exception:
        instrutores = instrutores.order_by('militar__nome_completo', 'nome_outra_forca', 'nome_civil')
    
    # Para cada instrutor, vamos buscar informações adicionais
    instrutores_com_info = []
    for instrutor in instrutores:
        # Turmas onde é chefe
        turmas_chefe = []
        if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
            # Buscar turmas onde o militar é chefe
            turmas_chefe = list(TurmaEnsino.objects.filter(
                instrutor_chefe_militar=instrutor.militar
            ).select_related('curso').only('id', 'identificacao', 'curso__nome').distinct())
        else:
            # Buscar turmas onde o instrutor externo é chefe
            turmas_chefe = list(instrutor.turmas_chefiadas_externo.all().distinct())
        
        # Disciplinas que ministra
        disciplinas_ministradas = []
        if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
            # Buscar disciplinas onde o militar é responsável
            disciplinas_ministradas = list(DisciplinaEnsino.objects.filter(
                instrutor_responsavel_militar=instrutor.militar
            ).only('id', 'nome', 'codigo').distinct())
        else:
            # Buscar disciplinas onde o instrutor externo é responsável
            disciplinas_ministradas = list(instrutor.disciplinas_responsaveis_externo.all().distinct())
        
        # Adicionar informações ao objeto instrutor
        instrutor.turmas_chefe_list = turmas_chefe
        instrutor.disciplinas_ministradas_list = disciplinas_ministradas
        
        instrutores_com_info.append(instrutor)
    
    paginator = Paginator(instrutores_com_info, 20)
    page = request.GET.get('page')
    instrutores = paginator.get_page(page)
    
    return render(request, 'militares/ensino/instrutores/listar.html', {'instrutores': instrutores})


@login_required
def criar_instrutor(request):
    """Cria um novo instrutor"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = InstrutorEnsinoForm(request.POST, request.FILES)
        if form.is_valid():
            instrutor = form.save()
            
            # Processar documentos
            documentos_upload = request.FILES.getlist('documentos[]')
            tipos_documentos = request.POST.getlist('tipos_documentos[]', [])
            titulos_documentos = request.POST.getlist('titulos_documentos[]', [])
            
            for idx, arquivo in enumerate(documentos_upload):
                if not arquivo:
                    continue
                
                try:
                    tipo_doc = tipos_documentos[idx] if idx < len(tipos_documentos) else 'OUTROS'
                    titulo_doc = titulos_documentos[idx] if idx < len(titulos_documentos) else arquivo.name
                    
                    DocumentoInstrutorEnsino.objects.create(
                        instrutor=instrutor,
                        tipo=tipo_doc,
                        titulo=titulo_doc[:200],
                        arquivo=arquivo,
                        upload_por=request.user
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Erro ao processar documento {idx}: {str(e)}')
                    continue
            
            messages.success(request, f'Instrutor {instrutor} criado com sucesso!')
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_instrutores_listar')})
            return redirect('militares:ensino_instrutores_listar')
        else:
            # Formulário com erros
            if is_ajax:
                from django.template.loader import render_to_string
                html = render_to_string('militares/ensino/instrutores/criar_modal.html', {'form': form}, request=request)
                return HttpResponse(html)
    else:
        form = InstrutorEnsinoForm()
    
    # Se for requisição AJAX, retornar apenas o formulário (versão modal)
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/instrutores/criar_modal.html', {'form': form}, request=request)
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/instrutores/criar.html', {'form': form, 'is_ajax': False})


@login_required
def detalhes_instrutor(request, pk):
    """Detalhes completos de um instrutor"""
    try:
        instrutor = get_object_or_404(
            InstrutorEnsino.objects.select_related('militar'),
            pk=pk
        )
        
        # Buscar turmas onde o instrutor é chefe (via instrutor_chefe_externo) com disciplinas
        turmas_chefe = TurmaEnsino.objects.filter(instrutor_chefe_externo=instrutor).select_related('curso').prefetch_related('disciplinas')
        
        # Se for bombeiro militar, também buscar turmas onde é chefe via militar
        if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
            turmas_chefe_militar = TurmaEnsino.objects.filter(instrutor_chefe_militar=instrutor.militar).select_related('curso').prefetch_related('disciplinas')
            # Combinar IDs das turmas
            turmas_chefe_ids = list(turmas_chefe.values_list('pk', flat=True))
            turmas_chefe_militar_ids = list(turmas_chefe_militar.values_list('pk', flat=True))
            turmas_chefe_ids = list(set(turmas_chefe_ids + turmas_chefe_militar_ids))
            turmas_chefe = TurmaEnsino.objects.filter(pk__in=turmas_chefe_ids).select_related('curso').prefetch_related('disciplinas')
        
        # Buscar turmas que têm disciplinas onde o instrutor é responsável
        # Disciplinas onde o instrutor externo é responsável
        disciplinas_instrutor = DisciplinaEnsino.objects.filter(instrutor_responsavel_externo=instrutor)
        
        # Se for bombeiro militar, também buscar disciplinas onde o militar é responsável
        if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
            disciplinas_militar = DisciplinaEnsino.objects.filter(instrutor_responsavel_militar=instrutor.militar)
            # Combinar IDs das disciplinas
            disciplinas_ids = list(disciplinas_instrutor.values_list('pk', flat=True))
            disciplinas_militar_ids = list(disciplinas_militar.values_list('pk', flat=True))
            disciplinas_ids = list(set(disciplinas_ids + disciplinas_militar_ids))
            disciplinas_instrutor = DisciplinaEnsino.objects.filter(pk__in=disciplinas_ids)
        
        # Buscar turmas que têm essas disciplinas
        turmas_disciplinas = TurmaEnsino.objects.filter(
            disciplinas__in=disciplinas_instrutor
        ).select_related('curso').prefetch_related('disciplinas').distinct()
        
        # Combinar todas as turmas (chefe + disciplinas)
        # Converter para lista de IDs para evitar problemas com querysets combinados
        turmas_ids = set()
        for turma in turmas_chefe:
            turmas_ids.add(turma.pk)
        for turma in turmas_disciplinas:
            turmas_ids.add(turma.pk)
        
        # Buscar todas as turmas únicas com prefetch
        turmas = TurmaEnsino.objects.filter(pk__in=turmas_ids).select_related('curso').prefetch_related('disciplinas')
        
        # Para cada turma, buscar as disciplinas que o instrutor ministra nela
        turmas_com_disciplinas = []
        for turma in turmas:
            # Buscar disciplinas da turma onde o instrutor é responsável
            if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
                disciplinas_turma = turma.disciplinas.filter(
                    Q(instrutor_responsavel_externo=instrutor) |
                    Q(instrutor_responsavel_militar=instrutor.militar)
                ).distinct()
            else:
                disciplinas_turma = turma.disciplinas.filter(
                    Q(instrutor_responsavel_externo=instrutor)
                ).distinct()
            
            # Adicionar atributo ao objeto turma
            turma.disciplinas_instrutor = disciplinas_turma
            turmas_com_disciplinas.append(turma)
        
        context = {
            'instrutor': instrutor,
            'turmas': turmas_com_disciplinas,
        }
        
        # Verificar se é requisição AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            html = render_to_string('militares/ensino/instrutores/detalhes_modal.html', context, request=request)
            return HttpResponse(html)
        
        return render(request, 'militares/ensino/instrutores/detalhes.html', context)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao carregar detalhes do instrutor {pk}: {str(e)}', exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import HttpResponse
            return HttpResponse(f'<div class="alert alert-danger">Erro ao carregar detalhes: {str(e)}</div>', status=500)
        raise


@login_required
def ficha_instrutor_pdf(request, pk):
    """Gera PDF da Ficha do Instrutor com todos os dados registrados - Padrão Certidão de Férias"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    from militares.models import InstrutorEnsino, TurmaEnsino, DisciplinaEnsino
    from django.db.models import Q
    import pytz
    
    instrutor = get_object_or_404(
        InstrutorEnsino.objects.select_related('militar'),
        pk=pk
    )
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos - Padrão Certidão de Férias
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA DE ENSINO, INSTRUÇÃO E PESQUISA",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>FICHA DO INSTRUTOR</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Preparar dados do instrutor
        tipo_choices = dict(InstrutorEnsino.TIPO_INSTRUTOR_CHOICES)
        tipo_display = tipo_choices.get(instrutor.tipo_instrutor, instrutor.tipo_instrutor)
        
        # Nome e identificação - inicializar variáveis
        nome_instrutor = ''
        posto_display = ''
        cpf = ''
        matricula = ''
        
        if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
            posto_display = instrutor.militar.get_posto_graduacao_display() or ''
            nome_instrutor = instrutor.militar.nome_completo or 'Não informado'
            cpf = instrutor.militar.cpf or 'Não informado'
            matricula = instrutor.militar.matricula or 'Não informado'
        elif instrutor.tipo_instrutor == 'OUTRA_FORCA':
            posto_display = instrutor.get_posto_outra_forca_display() or ''
            nome_instrutor = instrutor.nome_outra_forca or 'Não informado'
            cpf = instrutor.cpf_outra_forca or 'Não informado'
            matricula = instrutor.matricula_outra_forca or 'Não informado'
        elif instrutor.tipo_instrutor == 'CIVIL':
            nome_instrutor = instrutor.nome_civil or 'Não informado'
            cpf = instrutor.cpf_civil or 'Não informado'
            matricula = 'Não informado'
        else:
            nome_instrutor = 'Não informado'
        
        # Preparar dados pessoais organizados - DADOS BÁSICOS primeiro
        nome_completo_texto = f"{posto_display} {nome_instrutor}".strip() if posto_display else nome_instrutor
        dados_completos = []
        
        # Dados básicos de identificação
        dados_completos.append(['Nome Completo', nome_completo_texto])
        dados_completos.append(['CPF', cpf])
        dados_completos.append(['Matrícula/Identificação', matricula])
        dados_completos.append(['Tipo de Instrutor', tipo_display])
        
        if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
            email = instrutor.email_bombeiro or instrutor.militar.email or 'Não informado'
            telefone = instrutor.telefone_bombeiro or instrutor.militar.telefone or instrutor.militar.celular or 'Não informado'
            if instrutor.endereco_bombeiro or instrutor.militar.endereco:
                endereco = instrutor.endereco_bombeiro or instrutor.militar.endereco
                cidade = instrutor.cidade_bombeiro or instrutor.militar.cidade or ''
                uf = instrutor.uf_bombeiro or instrutor.militar.uf or ''
                cep = instrutor.cep_bombeiro or instrutor.militar.cep or ''
                endereco_completo = f"{endereco}"
                if cidade:
                    endereco_completo += f", {cidade}"
                if uf:
                    endereco_completo += f"/{uf}"
                if cep:
                    endereco_completo += f" - CEP: {cep}"
            else:
                endereco_completo = 'Não informado'
            # Dados de contato
            dados_completos.append(['E-mail', email])
            dados_completos.append(['Telefone', telefone])
            dados_completos.append(['Endereço', endereco_completo])
        elif instrutor.tipo_instrutor == 'OUTRA_FORCA':
            forca_armada = instrutor.get_forca_armada_display() or 'Não informado'
            instituicao = instrutor.instituicao_outra_forca or 'Não informado'
            email = instrutor.email_outra_forca or 'Não informado'
            telefone = instrutor.telefone_outra_forca or 'Não informado'
            if instrutor.endereco_outra_forca:
                endereco_completo = instrutor.endereco_outra_forca
                if instrutor.cidade_outra_forca:
                    endereco_completo += f", {instrutor.cidade_outra_forca}"
                if instrutor.uf_outra_forca:
                    endereco_completo += f"/{instrutor.uf_outra_forca}"
                if instrutor.cep_outra_forca:
                    endereco_completo += f" - CEP: {instrutor.cep_outra_forca}"
            else:
                endereco_completo = 'Não informado'
            # Dados específicos de outra força
            dados_completos.append(['Força Armada/Polícia', forca_armada])
            dados_completos.append(['Instituição/Órgão', instituicao])
            # Dados de contato
            dados_completos.append(['E-mail', email])
            dados_completos.append(['Telefone', telefone])
            dados_completos.append(['Endereço', endereco_completo])
        elif instrutor.tipo_instrutor == 'CIVIL':
            rg = instrutor.rg_civil or 'Não informado'
            data_nasc = instrutor.data_nascimento_civil.strftime('%d/%m/%Y') if instrutor.data_nascimento_civil else 'Não informado'
            formacao = instrutor.formacao_civil or 'Não informado'
            instituicao = instrutor.instituicao_civil or 'Não informado'
            email = instrutor.email_civil or 'Não informado'
            telefone = instrutor.telefone_civil or 'Não informado'
            if instrutor.endereco_civil:
                endereco_completo = instrutor.endereco_civil
                if instrutor.cidade_civil:
                    endereco_completo += f", {instrutor.cidade_civil}"
                if instrutor.uf_civil:
                    endereco_completo += f"/{instrutor.uf_civil}"
                if instrutor.cep_civil:
                    endereco_completo += f" - CEP: {instrutor.cep_civil}"
            else:
                endereco_completo = 'Não informado'
            # Dados específicos de civil
            dados_completos.append(['RG', rg])
            dados_completos.append(['Data de Nascimento', data_nasc])
            dados_completos.append(['Formação Acadêmica', formacao])
            dados_completos.append(['Instituição de Ensino', instituicao])
            # Dados de contato
            dados_completos.append(['E-mail', email])
            dados_completos.append(['Telefone', telefone])
            dados_completos.append(['Endereço', endereco_completo])
        
        # Adicionar qualificações e experiência
        if instrutor.habilitacoes:
            dados_completos.append(['Habilitações', instrutor.habilitacoes])
        if instrutor.especialidades:
            dados_completos.append(['Especialidades', instrutor.especialidades])
        if instrutor.experiencia_profissional:
            dados_completos.append(['Experiência Profissional', instrutor.experiencia_profissional])
        if instrutor.cursos_complementares:
            dados_completos.append(['Cursos Complementares', instrutor.cursos_complementares])
        if instrutor.link_lattes:
            dados_completos.append(['Currículo Lattes', instrutor.link_lattes])
        if instrutor.observacoes:
            dados_completos.append(['Observações', instrutor.observacoes])
        
        # Tabela única com todos os dados pessoais
        dados_tabela = []
        style_campo = ParagraphStyle('campo', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=0)
        style_valor = ParagraphStyle('valor', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=0)
        
        for campo, valor in dados_completos:
            # Usar Paragraph para garantir que o texto fique dentro das células
            campo_para = Paragraph(str(campo), style_campo)
            valor_para = Paragraph(str(valor), style_valor)
            dados_tabela.append([campo_para, valor_para])
        
        # Criar tabela - padrão certidão de férias
        dados_table = Table(dados_tabela, colWidths=[5*cm, 11*cm])
        dados_table.setStyle(TableStyle([
            # Alinhamento
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(dados_table)
        story.append(Spacer(1, 20))
        
        # Cidade e Data por extenso (centralizada)
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter cidade
            if militar_logado and militar_logado.cidade:
                cidade_doc = militar_logado.cidade
            else:
                cidade_doc = "Teresina"
            cidade_estado = f"{cidade_doc} - PI"
        except:
            cidade_estado = "Teresina - PI"
        
        # Data por extenso - usar timezone de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=10)))
        
        # Obter função do formulário ou função atual
        funcao_selecionada = request.GET.get('funcao', '')
        if not funcao_selecionada:
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_selecionada = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta)
        # Usar KeepTogether para manter nome e função na mesma página
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Adicionar espaço para assinatura física (reduzido para ficar mais próximo da data)
            story.append(Spacer(1, 0.5*cm))
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                nome_para = Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5))
                
                # 2ª linha: Função
                funcao_para = Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20))
                
                # Manter nome e função juntos na mesma página
                story.append(KeepTogether([nome_para, funcao_para]))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                nome_para = Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5))
                funcao_para = Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20))
                
                # Manter nome e função juntos na mesma página
                story.append(KeepTogether([nome_para, funcao_para]))
                
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Usar função selecionada do formulário
                funcao_display = funcao_selecionada
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_selecionada
            
            # Data e hora da assinatura
            agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M:%S')
            
            texto_assinatura = (
                f"Documento assinado eletronicamente por {nome_posto_quadro}, em {data_formatada} {hora_formatada}, "
                f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
            )
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[3*cm, 13*cm])
            assinatura_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizado
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
            ]))
            
            story.append(assinatura_table)
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        # Usar o instrutor como objeto para gerar o autenticador
        autenticador = gerar_autenticador_veracidade(instrutor, request, tipo_documento='ficha_instrutor')
        
        # Tabela do rodapé: QR + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        # Retornar PDF para visualização no navegador (sem download automático) - padrão QTS
        buffer.seek(0)
        nome_instrutor = ''
        if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
            nome_instrutor = instrutor.militar.nome_completo or 'Instrutor'
        elif instrutor.tipo_instrutor == 'OUTRA_FORCA':
            nome_instrutor = instrutor.nome_outra_forca or 'Instrutor'
        elif instrutor.tipo_instrutor == 'CIVIL':
            nome_instrutor = instrutor.nome_civil or 'Instrutor'
        else:
            nome_instrutor = 'Instrutor'
        
        filename = f"FICHA_INSTRUTOR_{nome_instrutor.replace(' ', '_')}_{instrutor.pk}.pdf"
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Ficha do Instrutor</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Erro ao gerar PDF da Ficha do Instrutor.</strong></p>
                <p>{str(e)}</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def ficha_aluno_pdf(request, pk):
    """Gera PDF da Ficha do Aluno com todos os dados registrados - Padrão Certidão de Férias"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    from militares.models import AlunoEnsino, TurmaEnsino
    from django.db.models import Q
    import pytz
    
    aluno = get_object_or_404(
        AlunoEnsino.objects.select_related('militar', 'turma', 'turma__curso'),
        pk=pk
    )
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos - Padrão Certidão de Férias
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA DE ENSINO, INSTRUÇÃO E PESQUISA",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal
        story.append(Paragraph("<u>FICHA DO ALUNO</u>", style_title))
        story.append(Spacer(1, 13 - 0.5*cm))
        
        # Preparar dados do aluno
        tipo_choices = dict(AlunoEnsino.TIPO_ALUNO_CHOICES)
        tipo_display = tipo_choices.get(aluno.tipo_aluno, aluno.tipo_aluno)
        situacao_choices = dict(AlunoEnsino.SITUACAO_CHOICES)
        situacao_display = situacao_choices.get(aluno.situacao, aluno.situacao)
        
        # Nome e identificação - inicializar variáveis
        nome_aluno = ''
        posto_display = ''
        cpf = ''
        matricula = ''
        
        if aluno.tipo_aluno == 'BOMBEIRO' and aluno.militar:
            posto_display = aluno.militar.get_posto_graduacao_display() or ''
            nome_aluno = aluno.militar.nome_completo or 'Não informado'
            cpf = aluno.militar.cpf or 'Não informado'
            matricula = aluno.matricula or aluno.militar.matricula or 'Não informado'
        elif aluno.tipo_aluno == 'OUTRA_FORCA':
            posto_display = aluno.get_posto_outra_forca_display() or ''
            nome_aluno = aluno.nome_outra_forca or 'Não informado'
            cpf = aluno.cpf_outra_forca or 'Não informado'
            matricula = aluno.matricula or aluno.matricula_outra_forca or 'Não informado'
        elif aluno.tipo_aluno == 'CIVIL':
            nome_aluno = aluno.nome_civil or 'Não informado'
            cpf = aluno.cpf_civil or 'Não informado'
            matricula = aluno.matricula or 'Não informado'
        else:
            nome_aluno = 'Não informado'
        
        # Preparar dados pessoais organizados - DADOS BÁSICOS primeiro
        nome_completo_texto = f"{posto_display} {nome_aluno}".strip() if posto_display else nome_aluno
        dados_completos = []
        
        # Dados básicos de identificação
        dados_completos.append(['Nome Completo', nome_completo_texto])
        dados_completos.append(['CPF', cpf])
        dados_completos.append(['Matrícula', matricula])
        dados_completos.append(['Tipo de Aluno', tipo_display])
        dados_completos.append(['Situação', situacao_display])
        
        # Turma
        if aluno.turma:
            turma_info = f"{aluno.turma.identificacao}"
            if aluno.turma.curso:
                turma_info += f" - {aluno.turma.curso.nome}"
            dados_completos.append(['Turma', turma_info])
        
        # Data de matrícula
        if aluno.data_matricula:
            dados_completos.append(['Data de Matrícula', aluno.data_matricula.strftime('%d/%m/%Y')])
        
        # Data de desligamento se houver
        if aluno.data_desligamento:
            dados_completos.append(['Data de Desligamento', aluno.data_desligamento.strftime('%d/%m/%Y')])
            if aluno.motivo_desligamento:
                dados_completos.append(['Motivo do Desligamento', aluno.motivo_desligamento])
        
        if aluno.tipo_aluno == 'BOMBEIRO' and aluno.militar:
            email = aluno.militar.email or 'Não informado'
            telefone = aluno.militar.telefone or aluno.militar.celular or 'Não informado'
            if aluno.militar.endereco:
                endereco = aluno.militar.endereco
                cidade = aluno.militar.cidade or ''
                uf = aluno.militar.uf or ''
                cep = aluno.militar.cep or ''
                endereco_completo = f"{endereco}"
                if cidade:
                    endereco_completo += f", {cidade}"
                if uf:
                    endereco_completo += f"/{uf}"
                if cep:
                    endereco_completo += f" - CEP: {cep}"
            else:
                endereco_completo = 'Não informado'
            # Dados de contato
            dados_completos.append(['E-mail', email])
            dados_completos.append(['Telefone', telefone])
            dados_completos.append(['Endereço', endereco_completo])
        elif aluno.tipo_aluno == 'OUTRA_FORCA':
            forca_armada = aluno.get_forca_armada_display() or 'Não informado'
            instituicao = aluno.instituicao_outra_forca or 'Não informado'
            email = aluno.email_outra_forca or 'Não informado'
            telefone = aluno.telefone_outra_forca or 'Não informado'
            rg = aluno.rg_outra_forca or 'Não informado'
            data_nasc = aluno.data_nascimento_outra_forca.strftime('%d/%m/%Y') if aluno.data_nascimento_outra_forca else 'Não informado'
            if aluno.endereco_outra_forca:
                endereco_completo = aluno.endereco_outra_forca
                if aluno.cidade_outra_forca:
                    endereco_completo += f", {aluno.cidade_outra_forca}"
                if aluno.uf_outra_forca:
                    endereco_completo += f"/{aluno.uf_outra_forca}"
                if aluno.cep_outra_forca:
                    endereco_completo += f" - CEP: {aluno.cep_outra_forca}"
            else:
                endereco_completo = 'Não informado'
            # Dados específicos de outra força
            dados_completos.append(['Força Armada/Polícia', forca_armada])
            dados_completos.append(['Instituição/Órgão', instituicao])
            dados_completos.append(['RG', rg])
            dados_completos.append(['Data de Nascimento', data_nasc])
            # Dados de contato
            dados_completos.append(['E-mail', email])
            dados_completos.append(['Telefone', telefone])
            dados_completos.append(['Endereço', endereco_completo])
        elif aluno.tipo_aluno == 'CIVIL':
            rg = aluno.rg_civil or 'Não informado'
            data_nasc = aluno.data_nascimento_civil.strftime('%d/%m/%Y') if aluno.data_nascimento_civil else 'Não informado'
            formacao = aluno.formacao_civil or 'Não informado'
            instituicao = aluno.instituicao_civil or 'Não informado'
            email = aluno.email_civil or 'Não informado'
            telefone = aluno.telefone_civil or 'Não informado'
            if aluno.endereco_civil:
                endereco_completo = aluno.endereco_civil
                if aluno.cidade_civil:
                    endereco_completo += f", {aluno.cidade_civil}"
                if aluno.uf_civil:
                    endereco_completo += f"/{aluno.uf_civil}"
                if aluno.cep_civil:
                    endereco_completo += f" - CEP: {aluno.cep_civil}"
            else:
                endereco_completo = 'Não informado'
            # Dados específicos de civil
            dados_completos.append(['RG', rg])
            dados_completos.append(['Data de Nascimento', data_nasc])
            dados_completos.append(['Formação Acadêmica', formacao])
            dados_completos.append(['Instituição de Ensino', instituicao])
            # Dados de contato
            dados_completos.append(['E-mail', email])
            dados_completos.append(['Telefone', telefone])
            dados_completos.append(['Endereço', endereco_completo])
        
        # TAF - Teste de Aptidão Física
        if aluno.taf_data_realizacao:
            taf_aprovado = 'Sim' if aluno.taf_aprovado else 'Não'
            taf_nota = f"{aluno.taf_nota_final}" if aluno.taf_nota_final else 'Não informado'
            dados_completos.append(['TAF - Data de Realização', aluno.taf_data_realizacao.strftime('%d/%m/%Y')])
            dados_completos.append(['TAF - Aprovado', taf_aprovado])
            dados_completos.append(['TAF - Nota Final', taf_nota])
            if aluno.taf_observacoes:
                dados_completos.append(['TAF - Observações', aluno.taf_observacoes])
        
        # PCF - Prova de Capacitação Física
        if aluno.pcf_data_realizacao:
            pcf_aprovado = 'Sim' if aluno.pcf_aprovado else 'Não'
            pcf_nota = f"{aluno.pcf_nota_final}" if aluno.pcf_nota_final else 'Não informado'
            dados_completos.append(['PCF - Data de Realização', aluno.pcf_data_realizacao.strftime('%d/%m/%Y')])
            dados_completos.append(['PCF - Aprovado', pcf_aprovado])
            dados_completos.append(['PCF - Nota Final', pcf_nota])
            if aluno.pcf_observacoes:
                dados_completos.append(['PCF - Observações', aluno.pcf_observacoes])
        
        # Capacitação Física Geral
        if aluno.capacidade_fisica_geral != 'NAO_AVALIADO':
            capacidade_choices = {
                'EXCELENTE': 'Excelente',
                'BOM': 'Bom',
                'REGULAR': 'Regular',
                'RUIM': 'Ruim',
                'NAO_AVALIADO': 'Não Avaliado'
            }
            dados_completos.append(['Capacidade Física Geral', capacidade_choices.get(aluno.capacidade_fisica_geral, aluno.capacidade_fisica_geral)])
            if aluno.data_ultima_avaliacao_fisica:
                dados_completos.append(['Data da Última Avaliação Física', aluno.data_ultima_avaliacao_fisica.strftime('%d/%m/%Y')])
            if aluno.observacoes_capacitacao_fisica:
                dados_completos.append(['Observações Capacitação Física', aluno.observacoes_capacitacao_fisica])
        
        # Observações
        if aluno.observacoes:
            dados_completos.append(['Observações', aluno.observacoes])
        
        # Tabela única com todos os dados pessoais
        dados_tabela = []
        style_campo = ParagraphStyle('campo', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=0)
        style_valor = ParagraphStyle('valor', parent=styles['Normal'], fontSize=8, fontName='Helvetica', alignment=0)
        
        for campo, valor in dados_completos:
            # Usar Paragraph para garantir que o texto fique dentro das células
            campo_para = Paragraph(str(campo), style_campo)
            valor_para = Paragraph(str(valor), style_valor)
            dados_tabela.append([campo_para, valor_para])
        
        # Criar tabela - padrão certidão de férias
        dados_table = Table(dados_tabela, colWidths=[5*cm, 11*cm])
        dados_table.setStyle(TableStyle([
            # Alinhamento
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(dados_table)
        story.append(Spacer(1, 20))
        
        # ========================================================================
        # INFORMAÇÕES ACADÊMICAS - TURMAS, NOTAS, FREQUÊNCIAS, ETC.
        # ========================================================================
        
        # Buscar todas as informações acadêmicas do aluno (mesma lógica de detalhes_aluno)
        frequencias = FrequenciaAula.objects.filter(aluno=aluno).select_related('aula', 'aula__disciplina', 'aula__turma').order_by('aula__data_aula')
        aproveitamentos = AproveitamentoDisciplina.objects.filter(aluno=aluno).select_related('disciplina', 'turma')
        notas = NotaAvaliacao.objects.filter(aluno=aluno).select_related('avaliacao', 'avaliacao__disciplina', 'avaliacao__turma').order_by('data_lancamento')
        documentos = DocumentoAluno.objects.filter(aluno=aluno).order_by('-data_upload')
        ocorrencias = OcorrenciaDisciplinar.objects.filter(aluno=aluno).select_related('turma').order_by('data_ocorrencia')
        historico = HistoricoEscolar.objects.filter(aluno=aluno).select_related('curso', 'turma', 'disciplina').order_by('turma', 'disciplina')
        cautelas = CautelaMaterialEscolar.objects.filter(aluno=aluno).select_related('material')
        
        # Buscar todas as turmas que o aluno participou
        turmas_participadas = []
        if aluno.turma:
            turmas_participadas.append(aluno.turma)
        
        # Turmas do histórico escolar
        turmas_historico = HistoricoEscolar.objects.filter(aluno=aluno).values_list('turma', flat=True).distinct()
        for turma_id in turmas_historico:
            if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
                try:
                    turma = TurmaEnsino.objects.get(pk=turma_id)
                    turmas_participadas.append(turma)
                except TurmaEnsino.DoesNotExist:
                    pass
        
        # Turmas das frequências
        turmas_frequencias = FrequenciaAula.objects.filter(aluno=aluno).values_list('aula__turma', flat=True).distinct()
        for turma_id in turmas_frequencias:
            if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
                try:
                    turma = TurmaEnsino.objects.get(pk=turma_id)
                    turmas_participadas.append(turma)
                except TurmaEnsino.DoesNotExist:
                    pass
        
        # Turmas das notas
        turmas_notas = NotaAvaliacao.objects.filter(aluno=aluno).values_list('avaliacao__turma', flat=True).distinct()
        for turma_id in turmas_notas:
            if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
                try:
                    turma = TurmaEnsino.objects.get(pk=turma_id)
                    turmas_participadas.append(turma)
                except TurmaEnsino.DoesNotExist:
                    pass
        
        # Turmas das ocorrências
        turmas_ocorrencias = OcorrenciaDisciplinar.objects.filter(aluno=aluno).values_list('turma', flat=True).distinct()
        for turma_id in turmas_ocorrencias:
            if turma_id and turma_id not in [t.pk for t in turmas_participadas]:
                try:
                    turma = TurmaEnsino.objects.get(pk=turma_id)
                    turmas_participadas.append(turma)
                except TurmaEnsino.DoesNotExist:
                    pass
        
        # Processar dados por turma
        for idx, turma in enumerate(turmas_participadas):
            # Quebrar página apenas se não for a primeira turma
            if idx > 0:
                story.append(PageBreak())
            
            # Título da turma
            turma_titulo = f"TURMA: {turma.identificacao}"
            if turma.curso:
                turma_titulo += f" - {turma.curso.nome}"
            story.append(Paragraph(turma_titulo, style_subtitle))
            story.append(Spacer(1, 10))
            
            # Informações da turma
            info_turma = []
            if turma.curso:
                info_turma.append(['Curso', turma.curso.nome])
            info_turma.append(['Identificação', turma.identificacao])
            if turma.data_inicio:
                periodo = turma.data_inicio.strftime('%d/%m/%Y')
                if turma.data_fim:
                    periodo += f" até {turma.data_fim.strftime('%d/%m/%Y')}"
                info_turma.append(['Período', periodo])
            info_turma.append(['Status', 'Ativa' if turma.ativa else 'Inativa'])
            
            if info_turma:
                info_turma_table_data = []
                for campo, valor in info_turma:
                    info_turma_table_data.append([Paragraph(str(campo), style_campo), Paragraph(str(valor), style_valor)])
                
                info_turma_table = Table(info_turma_table_data, colWidths=[5*cm, 11*cm])
                info_turma_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
                ]))
                story.append(info_turma_table)
                story.append(Spacer(1, 10))
            
            # Notas por disciplina
            frequencias_turma = frequencias.filter(aula__turma=turma)
            notas_turma = notas.filter(avaliacao__turma=turma)
            ocorrencias_turma = ocorrencias.filter(turma=turma)
            historicos_turma = historico.filter(turma=turma)
            aproveitamentos_turma = aproveitamentos.filter(turma=turma)
            
            # Buscar avaliações da turma para calcular notas
            avaliacoes_turma = AvaliacaoEnsino.objects.filter(turma=turma).select_related('disciplina').order_by('disciplina', 'data_avaliacao')
            disciplinas_turma = set()
            for avaliacao in avaliacoes_turma:
                disciplinas_turma.add(avaliacao.disciplina)
            for frequencia in frequencias_turma:
                if frequencia.aula.disciplina:
                    disciplinas_turma.add(frequencia.aula.disciplina)
            if not disciplinas_turma:
                disciplinas_turma = set(turma.disciplinas.all())
            
            # Estrutura para notas por disciplina
            notas_por_disciplina = {}
            for disciplina in disciplinas_turma:
                disciplina_id = disciplina.pk
                notas_por_disciplina[disciplina_id] = {
                    'disciplina': disciplina,
                    'dados_aluno': {
                        'notas': [None, None, None, None],
                        'pesos': [0, 0, 0, 0],
                        'nota_recuperacao': None,
                        'media_final': None,
                        'status': None
                    }
                }
            
            # Preencher notas das avaliações
            notas_avaliacoes_turma = NotaAvaliacao.objects.filter(
                avaliacao__turma=turma,
                aluno=aluno
            ).select_related('avaliacao', 'avaliacao__disciplina')
            
            for nota_obj in notas_avaliacoes_turma:
                disciplina_id = nota_obj.avaliacao.disciplina.pk
                if disciplina_id in notas_por_disciplina:
                    dados_aluno = notas_por_disciplina[disciplina_id]['dados_aluno']
                    if nota_obj.avaliacao.tipo == 'RECUPERACAO':
                        dados_aluno['nota_recuperacao'] = nota_obj.nota
                    else:
                        avaliacoes_disciplina = [a for a in avaliacoes_turma if a.disciplina.pk == disciplina_id and a.tipo != 'RECUPERACAO']
                        avaliacoes_disciplina_ordenadas = sorted(avaliacoes_disciplina, key=lambda x: (x.data_avaliacao if x.data_avaliacao else date.min, x.id))
                        try:
                            posicao = avaliacoes_disciplina_ordenadas.index(nota_obj.avaliacao)
                            if posicao < 4:
                                dados_aluno['notas'][posicao] = nota_obj.nota
                                dados_aluno['pesos'][posicao] = nota_obj.avaliacao.peso
                        except ValueError:
                            pass
            
            # Calcular média final e status
            for disciplina_id, dados_disciplina in notas_por_disciplina.items():
                disciplina = dados_disciplina['disciplina']
                media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
                dados_aluno = dados_disciplina['dados_aluno']
                notas_list = dados_aluno['notas']
                pesos_list = dados_aluno['pesos']
                nota_recuperacao = dados_aluno.get('nota_recuperacao')
                
                if nota_recuperacao is not None:
                    media_final = float(nota_recuperacao)
                    dados_aluno['media_final'] = round(media_final, 2)
                    media_minima_recuperacao = float(disciplina.media_minima_recuperacao) if disciplina.media_minima_recuperacao else 6.0
                    if media_final >= media_minima_recuperacao:
                        dados_aluno['status'] = 'APROVADO'
                    else:
                        dados_aluno['status'] = 'REPROVADO'
                else:
                    soma_notas = 0
                    soma_pesos = 0
                    for nota, peso in zip(notas_list, pesos_list):
                        if nota is not None:
                            soma_notas += float(nota) * float(peso)
                            soma_pesos += float(peso)
                    
                    if soma_pesos > 0:
                        media_final = soma_notas / soma_pesos
                        dados_aluno['media_final'] = round(media_final, 2)
                        if media_final >= media_minima:
                            dados_aluno['status'] = 'APROVADO'
                        else:
                            dados_aluno['status'] = 'REPROVADO'
            
            # Exibir notas por disciplina
            if notas_por_disciplina:
                story.append(Paragraph("NOTAS POR DISCIPLINA", style_bold))
                story.append(Spacer(1, 5))
                
                for disciplina_id, dados_disciplina in notas_por_disciplina.items():
                    disciplina = dados_disciplina['disciplina']
                    dados_aluno = dados_disciplina['dados_aluno']
                    
                    # Tabela de notas da disciplina
                    notas_table_data = [
                        [Paragraph('Disciplina', style_campo), Paragraph(disciplina.nome, style_valor)]
                    ]
                    notas_table_data.append([
                        Paragraph('1ª Avaliação', style_campo),
                        Paragraph(f"{dados_aluno['notas'][0]:.2f}" if dados_aluno['notas'][0] is not None else '-', style_valor)
                    ])
                    notas_table_data.append([
                        Paragraph('2ª Avaliação', style_campo),
                        Paragraph(f"{dados_aluno['notas'][1]:.2f}" if dados_aluno['notas'][1] is not None else '-', style_valor)
                    ])
                    notas_table_data.append([
                        Paragraph('3ª Avaliação', style_campo),
                        Paragraph(f"{dados_aluno['notas'][2]:.2f}" if dados_aluno['notas'][2] is not None else '-', style_valor)
                    ])
                    notas_table_data.append([
                        Paragraph('4ª Avaliação', style_campo),
                        Paragraph(f"{dados_aluno['notas'][3]:.2f}" if dados_aluno['notas'][3] is not None else '-', style_valor)
                    ])
                    if dados_aluno['nota_recuperacao'] is not None:
                        notas_table_data.append([
                            Paragraph('Recuperação', style_campo),
                            Paragraph(f"{dados_aluno['nota_recuperacao']:.2f}", style_valor)
                        ])
                    if dados_aluno['media_final'] is not None:
                        status_text = 'Aprovado' if dados_aluno['status'] == 'APROVADO' else 'Reprovado'
                        notas_table_data.append([
                            Paragraph('Média Final', style_campo),
                            Paragraph(f"{dados_aluno['media_final']:.2f} ({status_text})", style_valor)
                        ])
                    
                    notas_table = Table(notas_table_data, colWidths=[5*cm, 11*cm])
                    notas_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
                    ]))
                    story.append(notas_table)
                    story.append(Spacer(1, 10))
            
            # Frequências por disciplina
            frequencias_por_disciplina = {}
            for disciplina in disciplinas_turma:
                disciplina_id = disciplina.pk
                frequencias_disciplina = frequencias_turma.filter(aula__disciplina=disciplina)
                frequencias_por_disciplina[disciplina_id] = {
                    'disciplina': disciplina,
                    'frequencias': frequencias_disciplina,
                    'total': frequencias_disciplina.count(),
                    'presentes': frequencias_disciplina.filter(presenca='PRESENTE').count(),
                    'faltas': frequencias_disciplina.filter(presenca='FALTA').count(),
                    'faltas_justificadas': frequencias_disciplina.filter(presenca='FALTA_JUSTIFICADA').count(),
                    'atrasos': frequencias_disciplina.filter(presenca='ATRASO').count(),
                }
            
            if frequencias_por_disciplina:
                story.append(Paragraph("FREQUÊNCIAS POR DISCIPLINA", style_bold))
                story.append(Spacer(1, 5))
                
                for disciplina_id, dados_freq in frequencias_por_disciplina.items():
                    disciplina = dados_freq['disciplina']
                    freq_table_data = [
                        [Paragraph('Disciplina', style_campo), Paragraph(disciplina.nome, style_valor)],
                        [Paragraph('Total de Aulas', style_campo), Paragraph(str(dados_freq['total']), style_valor)],
                        [Paragraph('Presentes', style_campo), Paragraph(str(dados_freq['presentes']), style_valor)],
                        [Paragraph('Faltas', style_campo), Paragraph(str(dados_freq['faltas']), style_valor)],
                        [Paragraph('Faltas Justificadas', style_campo), Paragraph(str(dados_freq['faltas_justificadas']), style_valor)],
                        [Paragraph('Atrasos', style_campo), Paragraph(str(dados_freq['atrasos']), style_valor)],
                    ]
                    
                    freq_table = Table(freq_table_data, colWidths=[5*cm, 11*cm])
                    freq_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
                    ]))
                    story.append(freq_table)
                    story.append(Spacer(1, 10))
            
            # Histórico Escolar
            if historicos_turma:
                story.append(Paragraph("HISTÓRICO ESCOLAR", style_bold))
                story.append(Spacer(1, 5))
                
                historico_table_data = []
                # Cabeçalho com Paragraph
                historico_table_data.append([
                    Paragraph('Disciplina', style_campo),
                    Paragraph('Frequência (%)', style_campo),
                    Paragraph('Nota Final', style_campo),
                    Paragraph('Carga Horária', style_campo),
                    Paragraph('Status', style_campo),
                    Paragraph('Data Conclusão', style_campo)
                ])
                for hist in historicos_turma:
                    status_text = 'Aprovado' if hist.aprovado else 'Reprovado'
                    nota_text = f"{hist.nota_final:.2f}" if hist.nota_final else '-'
                    data_text = hist.data_conclusao.strftime('%d/%m/%Y') if hist.data_conclusao else '-'
                    historico_table_data.append([
                        Paragraph(hist.disciplina.nome, style_valor),
                        Paragraph(f"{hist.frequencia_percentual}%", style_valor),
                        Paragraph(nota_text, style_valor),
                        Paragraph(f"{hist.carga_horaria_cursada}h", style_valor),
                        Paragraph(status_text, style_valor),
                        Paragraph(data_text, style_valor)
                    ])
                
                historico_table = Table(historico_table_data, colWidths=[4*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2.5*cm])
                historico_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Cabeçalho centralizado
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # Dados centralizados
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
                ]))
                story.append(historico_table)
                story.append(Spacer(1, 10))
            
            # Aproveitamentos
            if aproveitamentos_turma:
                story.append(Paragraph("APROVEITAMENTOS", style_bold))
                story.append(Spacer(1, 5))
                
                aproveit_table_data = []
                # Cabeçalho com Paragraph
                aproveit_table_data.append([
                    Paragraph('Disciplina', style_campo),
                    Paragraph('Status', style_campo)
                ])
                for aproveitamento in aproveitamentos_turma:
                    status_text = 'Aprovado' if aproveitamento.aprovado else 'Reprovado'
                    aproveit_table_data.append([
                        Paragraph(aproveitamento.disciplina.nome, style_valor),
                        Paragraph(status_text, style_valor)
                    ])
                
                aproveit_table = Table(aproveit_table_data, colWidths=[10*cm, 6*cm])
                aproveit_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Cabeçalho centralizado
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),   # Dados alinhados à esquerda
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
                ]))
                story.append(aproveit_table)
                story.append(Spacer(1, 10))
            
            # Ocorrências
            if ocorrencias_turma:
                story.append(Paragraph("OCORRÊNCIAS DISCIPLINARES", style_bold))
                story.append(Spacer(1, 5))
                
                ocorr_table_data = []
                # Cabeçalho com Paragraph
                ocorr_table_data.append([
                    Paragraph('Data', style_campo),
                    Paragraph('Tipo', style_campo),
                    Paragraph('Descrição', style_campo)
                ])
                for ocorrencia in ocorrencias_turma:
                    data_text = ocorrencia.data_ocorrencia.strftime('%d/%m/%Y') if ocorrencia.data_ocorrencia else '-'
                    tipo_text = ocorrencia.get_tipo_display() if hasattr(ocorrencia, 'get_tipo_display') else '-'
                    desc_text = ocorrencia.descricao or '-'
                    ocorr_table_data.append([
                        Paragraph(data_text, style_valor),
                        Paragraph(tipo_text, style_valor),
                        Paragraph(desc_text, style_valor)
                    ])
                
                ocorr_table = Table(ocorr_table_data, colWidths=[3*cm, 3*cm, 10*cm])
                ocorr_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Cabeçalho centralizado
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),   # Dados alinhados à esquerda
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
                ]))
                story.append(ocorr_table)
                story.append(Spacer(1, 10))
        
        # Documentos (todas as turmas)
        if documentos:
            story.append(Spacer(1, 10))
            story.append(Paragraph("DOCUMENTOS ANEXADOS", style_subtitle))
            story.append(Spacer(1, 10))
            
            doc_table_data = []
            # Cabeçalho com Paragraph
            doc_table_data.append([
                Paragraph('Nome', style_campo),
                Paragraph('Tipo', style_campo),
                Paragraph('Data de Upload', style_campo)
            ])
            for documento in documentos[:20]:  # Limitar a 20 documentos
                data_text = documento.data_upload.strftime('%d/%m/%Y') if documento.data_upload else '-'
                doc_table_data.append([
                    Paragraph(documento.nome or '-', style_valor),
                    Paragraph(documento.tipo_documento or '-', style_valor),
                    Paragraph(data_text, style_valor)
                ])
            
            doc_table = Table(doc_table_data, colWidths=[8*cm, 4*cm, 4*cm])
            doc_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Cabeçalho centralizado
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),   # Dados alinhados à esquerda
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
            ]))
            story.append(doc_table)
            story.append(Spacer(1, 10))
        
        # Cautelas de Material
        if cautelas:
            story.append(Spacer(1, 10))
            story.append(Paragraph("CAUTELAS DE MATERIAL ESCOLAR", style_subtitle))
            story.append(Spacer(1, 10))
            
            cautela_table_data = []
            # Cabeçalho com Paragraph
            cautela_table_data.append([
                Paragraph('Material', style_campo),
                Paragraph('Quantidade', style_campo),
                Paragraph('Data de Cautela', style_campo),
                Paragraph('Data de Devolução', style_campo),
                Paragraph('Status', style_campo)
            ])
            for cautela in cautelas:
                data_cautela = cautela.data_cautela.strftime('%d/%m/%Y') if cautela.data_cautela else '-'
                data_devolucao = cautela.data_devolucao.strftime('%d/%m/%Y') if cautela.data_devolucao else '-'
                status_text = 'Devolvido' if cautela.devolvido else 'Em Cautela'
                cautela_table_data.append([
                    Paragraph(cautela.material.nome if cautela.material else '-', style_valor),
                    Paragraph(str(cautela.quantidade), style_valor),
                    Paragraph(data_cautela, style_valor),
                    Paragraph(data_devolucao, style_valor),
                    Paragraph(status_text, style_valor)
                ])
            
            cautela_table = Table(cautela_table_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm, 2*cm])
            cautela_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Cabeçalho centralizado
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),   # Dados alinhados à esquerda
                ('ALIGN', (1, 1), (1, -1), 'CENTER'), # Quantidade centralizada
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('WORDWRAP', (0, 0), (-1, -1), True),  # Quebrar texto dentro das células
            ]))
            story.append(cautela_table)
            story.append(Spacer(1, 10))
        
        # Cidade e Data por extenso (centralizada)
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter cidade
            if militar_logado and militar_logado.cidade:
                cidade_doc = militar_logado.cidade
            else:
                cidade_doc = "Teresina"
            cidade_estado = f"{cidade_doc} - PI"
        except:
            cidade_estado = "Teresina - PI"
        
        # Data por extenso - usar timezone de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=10)))
        
        # Obter função do formulário ou função atual
        funcao_selecionada = request.GET.get('funcao', '')
        if not funcao_selecionada:
            from .permissoes_hierarquicas import obter_funcao_militar_ativa
            funcao_atual_obj = obter_funcao_militar_ativa(request.user)
            funcao_selecionada = funcao_atual_obj.funcao_militar.nome if funcao_atual_obj and funcao_atual_obj.funcao_militar else "Usuário do Sistema"
        
        # Adicionar assinatura física (como se fosse para assinar com caneta)
        # Usar KeepTogether para manter nome e função na mesma página
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Adicionar espaço para assinatura física (reduzido para ficar mais próximo da data)
            story.append(Spacer(1, 0.5*cm))
            
            if militar_logado:
                nome_posto = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Linha para assinatura física - 1ª linha: Nome - Posto
                nome_para = Paragraph(nome_posto, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5))
                
                # 2ª linha: Função
                funcao_para = Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20))
                
                # Manter nome e função juntos na mesma página
                story.append(KeepTogether([nome_para, funcao_para]))
                
                # Linha para assinatura (espaço para caneta)
                story.append(Spacer(1, 0.3*cm))
            else:
                nome_usuario = request.user.get_full_name() or request.user.username
                nome_para = Paragraph(nome_usuario, ParagraphStyle('assinatura_fisica', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica-Bold', spaceAfter=5))
                funcao_para = Paragraph(funcao_selecionada, ParagraphStyle('assinatura_funcao', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20))
                
                # Manter nome e função juntos na mesma página
                story.append(KeepTogether([nome_para, funcao_para]))
                
                story.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Adicionar espaço antes da assinatura eletrônica
        story.append(Spacer(1, 0.5*cm))
        
        # Adicionar assinatura eletrônica com logo
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter informações do assinante
            if militar_logado:
                nome_posto_quadro = f"{militar_logado.nome_completo} - {militar_logado.get_posto_graduacao_display()} BM"
                
                # Usar função selecionada do formulário
                funcao_display = funcao_selecionada
            else:
                nome_posto_quadro = request.user.get_full_name() or request.user.username
                funcao_display = funcao_selecionada
            
            # Data e hora da assinatura
            agora = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
            data_formatada = agora.strftime('%d/%m/%Y')
            hora_formatada = agora.strftime('%H:%M:%S')
            
            texto_assinatura = (
                f"Documento assinado eletronicamente por {nome_posto_quadro}, em {data_formatada} {hora_formatada}, "
                f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
            )
            
            # Adicionar logo da assinatura eletrônica
            from .utils import obter_caminho_assinatura_eletronica
            logo_path = obter_caminho_assinatura_eletronica()
            
            # Tabela das assinaturas: Logo + Texto de assinatura
            assinatura_data = [
                [Image(logo_path, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
            ]
            
            assinatura_table = Table(assinatura_data, colWidths=[3*cm, 13*cm])
            assinatura_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizado
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
            ]))
            
            story.append(assinatura_table)
        except Exception as e:
            # Se houver erro, apenas adicionar espaço
            story.append(Spacer(1, 1*cm))
        
        # Rodapé com QR Code para conferência de veracidade
        story.append(Spacer(1, 0.1*cm))
        
        # Usar a função utilitária para gerar o autenticador
        from .utils import gerar_autenticador_veracidade
        # Usar o aluno como objeto para gerar o autenticador
        autenticador = gerar_autenticador_veracidade(aluno, request, tipo_documento='ficha_aluno')
        
        # Tabela do rodapé: QR + Texto de autenticação
        rodape_data = [
            [autenticador['qr_img'], Paragraph(autenticador['texto_autenticacao'], style_small)]
        ]
        
        rodape_table = Table(rodape_data, colWidths=[3*cm, 13*cm])
        rodape_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # QR centralizado
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
        ]))
        
        story.append(rodape_table)
        
        # Usar função utilitária para criar rodapé do sistema
        from .utils import criar_rodape_sistema_pdf
        add_rodape_first, add_rodape_later = criar_rodape_sistema_pdf(request)
        
        # Construir PDF com rodapé em todas as páginas
        doc.build(story, onFirstPage=add_rodape_first, onLaterPages=add_rodape_later)
        
        # Retornar PDF para visualização no navegador (sem download automático)
        buffer.seek(0)
        nome_aluno_arquivo = nome_completo_texto.replace(' ', '_')
        filename = f"FICHA_ALUNO_{nome_aluno_arquivo}_{aluno.pk}.pdf"
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - Ficha do Aluno</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Erro ao gerar PDF da Ficha do Aluno.</strong></p>
                <p>{str(e)}</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def editar_instrutor(request, pk):
    """Edita um instrutor existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar instrutores.')
        return redirect('militares:ensino_instrutores_listar')
    
    instrutor = get_object_or_404(InstrutorEnsino.objects.select_related('militar'), pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = InstrutorEnsinoForm(request.POST, request.FILES, instance=instrutor)
        if form.is_valid():
            instrutor = form.save()
            
            # Processar novos documentos
            documentos_upload = request.FILES.getlist('documentos[]')
            tipos_documentos = request.POST.getlist('tipos_documentos[]', [])
            titulos_documentos = request.POST.getlist('titulos_documentos[]', [])
            
            for idx, arquivo in enumerate(documentos_upload):
                if not arquivo:
                    continue
                
                try:
                    tipo_doc = tipos_documentos[idx] if idx < len(tipos_documentos) else 'OUTROS'
                    titulo_doc = titulos_documentos[idx] if idx < len(titulos_documentos) else arquivo.name
                    
                    DocumentoInstrutorEnsino.objects.create(
                        instrutor=instrutor,
                        tipo=tipo_doc,
                        titulo=titulo_doc[:200],
                        arquivo=arquivo,
                        upload_por=request.user
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Erro ao processar documento {idx}: {str(e)}')
                    continue
            
            # Processar remoção de documentos
            documentos_remover = request.POST.getlist('documentos_remover[]')
            if documentos_remover:
                DocumentoInstrutorEnsino.objects.filter(
                    id__in=documentos_remover,
                    instrutor=instrutor
                ).delete()
            
            messages.success(request, f'Instrutor {instrutor} atualizado com sucesso!')
            if is_ajax:
                from django.http import JsonResponse
                from django.urls import reverse
                return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_instrutores_listar')})
            return redirect('militares:ensino_instrutores_listar')
        else:
            # Form inválido - retornar erros
            if is_ajax:
                from django.template.loader import render_to_string
                from django.http import HttpResponse
                html = render_to_string('militares/ensino/instrutores/editar_modal.html', {'form': form, 'instrutor': instrutor}, request=request)
                return HttpResponse(html)
    else:
        form = InstrutorEnsinoForm(instance=instrutor)
    
    # Se for requisição AJAX, retornar apenas o formulário (versão modal)
    if is_ajax:
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        html = render_to_string('militares/ensino/instrutores/editar_modal.html', {'form': form, 'instrutor': instrutor}, request=request)
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/instrutores/editar.html', {'form': form, 'instrutor': instrutor})


@login_required
def excluir_instrutor(request, pk):
    """Exclui um instrutor"""
    instrutor = get_object_or_404(InstrutorEnsino, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            nome_instrutor = str(instrutor)
            
            # Verificar se há disciplinas, turmas ou aulas vinculadas
            disciplinas_count = DisciplinaEnsino.objects.filter(instrutor_responsavel_externo=instrutor).count()
            turmas_count = TurmaEnsino.objects.filter(instrutor_chefe_externo=instrutor).count()
            
            # Aulas - o campo instrutor em AulaEnsino é ForeignKey para Militar
            # Então só podemos buscar aulas se o instrutor for do tipo BOMBEIRO e tiver um militar associado
            aulas_count = 0
            if instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
                aulas_count = AulaEnsino.objects.filter(instrutor=instrutor.militar).count()
            
            cursos_count = CursoEnsino.objects.filter(instrutores_curso=instrutor).count()
            
            if disciplinas_count > 0 or turmas_count > 0 or aulas_count > 0 or cursos_count > 0:
                error_msg = f'Não é possível excluir o instrutor {nome_instrutor} pois ele está vinculado a disciplinas, turmas, aulas ou cursos.'
                if is_ajax:
                    return JsonResponse({'success': False, 'message': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('militares:ensino_instrutores_listar')
            
            instrutor.delete()
            messages.success(request, f'Instrutor {nome_instrutor} excluído com sucesso!')
            
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_instrutores_listar')})
            return redirect('militares:ensino_instrutores_listar')
        except Exception as e:
            error_message = str(e)
            if is_ajax:
                return JsonResponse({'success': False, 'message': f'Erro ao excluir instrutor: {error_message}'}, status=400)
            messages.error(request, f'Erro ao excluir instrutor: {error_message}')
            return redirect('militares:ensino_instrutores_listar')
    
    # GET request - retornar modal de confirmação
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/instrutores/excluir_modal.html', {'instrutor': instrutor}, request=request)
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/instrutores/excluir_confirm.html', {'instrutor': instrutor})


# ============================================================================
# 5. MONITORES (Relacionados a Turma)
# ============================================================================

@login_required
def listar_monitores(request):
    """Lista todos os monitores com informações sobre turmas e disciplinas"""
    from django.db.models import Count, Prefetch
    
    monitores = MonitorEnsino.objects.select_related('militar').filter(ativo=True)
    
    busca = request.GET.get('busca', '')
    if busca:
        monitores = monitores.filter(
            Q(militar__nome_completo__icontains=busca) |
            Q(militar__cpf__icontains=busca) |
            Q(nome_outra_forca__icontains=busca) |
            Q(nome_civil__icontains=busca) |
            Q(cpf_outra_forca__icontains=busca) |
            Q(cpf_civil__icontains=busca) |
            Q(habilitacoes__icontains=busca) |
            Q(especialidades__icontains=busca)
        )
    
    try:
        ordem_hierarquica = [codigo for codigo, _nome in POSTO_GRADUACAO_CHOICES]
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(999),
            output_field=IntegerField(),
        )
        monitores = monitores.annotate(hierarquia_ordem=hierarquia_ordem).order_by(
            'hierarquia_ordem',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'nome_outra_forca',
            'nome_civil'
        )
    except Exception:
        monitores = monitores.order_by('militar__nome_completo', 'nome_outra_forca', 'nome_civil')
    
    # Para cada monitor, buscar informações adicionais
    monitores_com_info = []
    for monitor in monitores:
        # Turmas onde o monitor atua
        turmas_monitor = []
        if monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar:
            # Buscar turmas onde o militar é monitor
            turmas_monitor = list(TurmaEnsino.objects.filter(
                monitores_militares=monitor.militar
            ).select_related('curso').only('id', 'identificacao', 'curso__nome'))
        else:
            # Buscar turmas onde o monitor externo atua
            turmas_monitor = list(TurmaEnsino.objects.filter(
                monitores_externos=monitor
            ).select_related('curso').only('id', 'identificacao', 'curso__nome'))
        
        # Disciplinas que monitora
        disciplinas_monitoradas = []
        if monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar:
            # Buscar disciplinas onde o militar é monitor
            disciplinas_monitoradas = list(DisciplinaEnsino.objects.filter(
                monitores_militares=monitor.militar
            ).only('id', 'nome', 'codigo'))
        else:
            # Buscar disciplinas onde o monitor externo atua
            disciplinas_monitoradas = list(DisciplinaEnsino.objects.filter(
                monitores_externos=monitor
            ).only('id', 'nome', 'codigo'))
        
        # Adicionar informações ao objeto monitor
        monitor.turmas_monitor_list = turmas_monitor
        monitor.disciplinas_monitoradas_list = disciplinas_monitoradas
        
        monitores_com_info.append(monitor)
    
    paginator = Paginator(monitores_com_info, 20)
    page = request.GET.get('page')
    monitores = paginator.get_page(page)
    
    return render(request, 'militares/ensino/monitores/listar.html', {'monitores': monitores})


@login_required
def criar_monitor(request):
    """Cria um novo monitor"""
    logger = logging.getLogger(__name__)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        if request.method == 'POST':
            form = MonitorEnsinoForm(request.POST, request.FILES)
            if form.is_valid():
                monitor = form.save()
                
                # Processar documentos
                documentos_upload = request.FILES.getlist('documentos[]')
                tipos_documentos = request.POST.getlist('tipos_documentos[]', [])
                titulos_documentos = request.POST.getlist('titulos_documentos[]', [])
                
                for idx, arquivo in enumerate(documentos_upload):
                    if not arquivo:
                        continue
                    
                    try:
                        tipo_doc = tipos_documentos[idx] if idx < len(tipos_documentos) else 'OUTROS'
                        titulo_doc = titulos_documentos[idx] if idx < len(titulos_documentos) else arquivo.name
                        
                        DocumentoMonitorEnsino.objects.create(
                            monitor=monitor,
                            tipo=tipo_doc,
                            titulo=titulo_doc[:200],
                            arquivo=arquivo,
                            upload_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar documento {idx}: {str(e)}')
                        continue
                
                messages.success(request, f'Monitor {monitor} criado com sucesso!')
                if is_ajax:
                    return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_monitores_listar')})
                return redirect('militares:ensino_monitores_listar')
            else:
                # Formulário com erros
                if is_ajax:
                    from django.template.loader import render_to_string
                    html = render_to_string('militares/ensino/monitores/criar_modal.html', {'form': form}, request=request)
                    return HttpResponse(html)
        else:
            form = MonitorEnsinoForm()
        
        # Se for requisição AJAX, retornar apenas o formulário (versão modal)
        if is_ajax:
            from django.template.loader import render_to_string
            html = render_to_string('militares/ensino/monitores/criar_modal.html', {'form': form}, request=request)
            return HttpResponse(html)
        
        return render(request, 'militares/ensino/monitores/criar.html', {'form': form, 'is_ajax': False})
    
    except Exception as e:
        logger.exception('Erro ao criar monitor')
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao processar a requisição: {str(e)}'
            }, status=500)
        # Para requisições não-AJAX, deixar o Django tratar o erro normalmente
        raise


@login_required
def detalhes_monitor(request, pk):
    """Detalhes completos de um monitor"""
    logger = logging.getLogger(__name__)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        monitor = get_object_or_404(
            MonitorEnsino.objects.select_related('militar'),
            pk=pk
        )
        
        # Garantir que o monitor tenha tipo_monitor (para monitores criados antes da migração)
        if not hasattr(monitor, 'tipo_monitor') or not monitor.tipo_monitor:
            # Se não tiver tipo_monitor, definir baseado no que existe
            if monitor.militar:
                monitor.tipo_monitor = 'BOMBEIRO'
            elif hasattr(monitor, 'nome_outra_forca') and monitor.nome_outra_forca:
                monitor.tipo_monitor = 'OUTRA_FORCA'
            elif hasattr(monitor, 'nome_civil') and monitor.nome_civil:
                monitor.tipo_monitor = 'CIVIL'
            else:
                monitor.tipo_monitor = 'BOMBEIRO'  # Default
            
            # Salvar o tipo_monitor no banco se foi definido
            try:
                MonitorEnsino.objects.filter(pk=monitor.pk).update(tipo_monitor=monitor.tipo_monitor)
                # Recarregar o objeto para ter o valor atualizado
                monitor.refresh_from_db()
            except Exception as e:
                logger.warning(f'Erro ao atualizar tipo_monitor do monitor {monitor.pk}: {str(e)}')
        
        # Buscar turmas onde o monitor atua (via monitores_externos) com disciplinas
        turmas = TurmaEnsino.objects.filter(monitores_externos=monitor).select_related('curso').prefetch_related('disciplinas')
        
        # Se for bombeiro militar, também buscar turmas onde atua via militar
        if monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar:
            turmas_militar = TurmaEnsino.objects.filter(monitores_militares=monitor.militar).select_related('curso').prefetch_related('disciplinas')
            turmas = (turmas | turmas_militar).distinct()
        
        # Buscar turmas que têm disciplinas onde o monitor atua
        # Disciplinas onde o monitor externo atua
        disciplinas_monitor = DisciplinaEnsino.objects.filter(monitores_externos=monitor)
        
        # Se for bombeiro militar, também buscar disciplinas onde o militar é monitor
        if monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar:
            disciplinas_militar = DisciplinaEnsino.objects.filter(monitores_militares=monitor.militar)
            disciplinas_monitor = (disciplinas_monitor | disciplinas_militar).distinct()
        
        # Buscar turmas que têm essas disciplinas
        turmas_disciplinas = TurmaEnsino.objects.filter(
            disciplinas__in=disciplinas_monitor
        ).select_related('curso').prefetch_related('disciplinas').distinct()
        
        # Combinar todas as turmas (monitor + disciplinas)
        turmas = (turmas | turmas_disciplinas).distinct()
        
        # Para cada turma, buscar as disciplinas que o monitor atua nela
        turmas_com_disciplinas = []
        for turma in turmas:
            # Buscar disciplinas da turma onde o monitor atua
            disciplinas_turma = turma.disciplinas.filter(
                Q(monitores_externos=monitor) |
                (Q(monitores_militares=monitor.militar) if monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar else Q(pk__in=[]))
            ).distinct()
            
            # Adicionar atributo ao objeto turma
            turma.disciplinas_monitor = disciplinas_turma
            turmas_com_disciplinas.append(turma)
        
        context = {
            'monitor': monitor,
            'turmas': turmas_com_disciplinas,
        }
        
        # Verificar se é requisição AJAX
        if is_ajax:
            from django.template.loader import render_to_string
            from django.http import HttpResponse, JsonResponse
            try:
                html = render_to_string('militares/ensino/monitores/detalhes_modal.html', context, request=request)
                return HttpResponse(html)
            except Exception as e:
                logger.exception('Erro ao renderizar template de detalhes do monitor')
                return JsonResponse({
                    'error': f'Erro ao carregar detalhes: {str(e)}'
                }, status=500)
        
        return render(request, 'militares/ensino/monitores/detalhes.html', context)
    
    except Exception as e:
        logger.exception('Erro ao carregar detalhes do monitor')
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({
                'error': f'Erro ao carregar detalhes: {str(e)}'
            }, status=500)
        # Para requisições não-AJAX, deixar o Django tratar o erro normalmente
        raise


@login_required
def editar_monitor(request, pk):
    """Edita um monitor existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar monitores.')
        return redirect('militares:ensino_monitores_listar')
    
    monitor = get_object_or_404(MonitorEnsino.objects.select_related('militar'), pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = MonitorEnsinoForm(request.POST, request.FILES, instance=monitor)
        if form.is_valid():
            monitor = form.save()
            
            # Processar novos documentos
            documentos_upload = request.FILES.getlist('documentos[]')
            tipos_documentos = request.POST.getlist('tipos_documentos[]', [])
            titulos_documentos = request.POST.getlist('titulos_documentos[]', [])
            
            for idx, arquivo in enumerate(documentos_upload):
                if not arquivo:
                    continue
                
                try:
                    tipo_doc = tipos_documentos[idx] if idx < len(tipos_documentos) else 'OUTROS'
                    titulo_doc = titulos_documentos[idx] if idx < len(titulos_documentos) else arquivo.name
                    
                    DocumentoMonitorEnsino.objects.create(
                        monitor=monitor,
                        tipo=tipo_doc,
                        titulo=titulo_doc[:200],
                        arquivo=arquivo,
                        upload_por=request.user
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f'Erro ao processar documento {idx}: {str(e)}')
                    continue
            
            # Processar remoção de documentos
            documentos_remover = request.POST.getlist('documentos_remover[]')
            if documentos_remover:
                DocumentoMonitorEnsino.objects.filter(
                    id__in=documentos_remover,
                    monitor=monitor
                ).delete()
            
            messages.success(request, f'Monitor {monitor} atualizado com sucesso!')
            if is_ajax:
                from django.http import JsonResponse
                from django.urls import reverse
                return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_monitores_listar')})
            return redirect('militares:ensino_monitores_listar')
        else:
            # Form inválido - retornar erros
            if is_ajax:
                from django.template.loader import render_to_string
                from django.http import HttpResponse
                html = render_to_string('militares/ensino/monitores/editar_modal.html', {'form': form, 'monitor': monitor}, request=request)
                return HttpResponse(html)
    else:
        form = MonitorEnsinoForm(instance=monitor)
    
    # Se for requisição AJAX, retornar apenas o formulário (versão modal)
    if is_ajax:
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        html = render_to_string('militares/ensino/monitores/editar_modal.html', {'form': form, 'monitor': monitor}, request=request)
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/monitores/editar.html', {'form': form, 'monitor': monitor})


@login_required
def excluir_monitor(request, pk):
    """Exclui um monitor"""
    logger = logging.getLogger(__name__)
    monitor = get_object_or_404(MonitorEnsino, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Garantir que o monitor tenha tipo_monitor (para monitores criados antes da migração)
        tipo_monitor = getattr(monitor, 'tipo_monitor', None)
        if not tipo_monitor:
            if monitor.militar:
                tipo_monitor = 'BOMBEIRO'
            elif hasattr(monitor, 'nome_outra_forca') and monitor.nome_outra_forca:
                tipo_monitor = 'OUTRA_FORCA'
            elif hasattr(monitor, 'nome_civil') and monitor.nome_civil:
                tipo_monitor = 'CIVIL'
            else:
                tipo_monitor = 'BOMBEIRO'  # Default
        
        if request.method == 'POST':
            # Verificar se há relacionamentos que impedem a exclusão
            # Usar ManyToMany corretamente
            disciplinas_count = DisciplinaEnsino.objects.filter(monitores_externos=monitor).count()
            turmas_count = TurmaEnsino.objects.filter(monitores_externos=monitor).count()
            cursos_count = CursoEnsino.objects.filter(monitores_curso=monitor).count()
            
            # Se for monitor militar (BOMBEIRO), também verificar via monitores_militares
            if tipo_monitor == 'BOMBEIRO' and monitor.militar:
                disciplinas_militar_count = DisciplinaEnsino.objects.filter(monitores_militares=monitor.militar).count()
                turmas_militar_count = TurmaEnsino.objects.filter(monitores_militares=monitor.militar).count()
                disciplinas_count += disciplinas_militar_count
                turmas_count += turmas_militar_count
            
            # Aulas - AulaEnsino não tem campo monitor, apenas instrutor
            # Não há como verificar aulas diretamente, mas podemos verificar via disciplinas
            aulas_count = 0
            if disciplinas_count > 0:
                # Contar aulas das disciplinas onde o monitor atua
                disciplinas_ids = list(DisciplinaEnsino.objects.filter(monitores_externos=monitor).values_list('id', flat=True))
                if tipo_monitor == 'BOMBEIRO' and monitor.militar:
                    disciplinas_militar_ids = list(DisciplinaEnsino.objects.filter(monitores_militares=monitor.militar).values_list('id', flat=True))
                    disciplinas_ids.extend(disciplinas_militar_ids)
                if disciplinas_ids:
                    aulas_count = AulaEnsino.objects.filter(disciplina_id__in=disciplinas_ids).count()
            
            if disciplinas_count > 0 or turmas_count > 0 or aulas_count > 0 or cursos_count > 0:
                erro_msg = f'Não é possível excluir o monitor pois ele está vinculado a: '
                erros = []
                if disciplinas_count > 0:
                    erros.append(f'{disciplinas_count} disciplina(s)')
                if turmas_count > 0:
                    erros.append(f'{turmas_count} turma(s)')
                if aulas_count > 0:
                    erros.append(f'{aulas_count} aula(s)')
                if cursos_count > 0:
                    erros.append(f'{cursos_count} curso(s)')
                erro_msg += ', '.join(erros) + '.'
                
                messages.error(request, erro_msg)
                if is_ajax:
                    return JsonResponse({'success': False, 'error': erro_msg}, status=400)
                return redirect('militares:ensino_monitores_listar')
            
            nome = str(monitor)
            monitor.delete()
            messages.success(request, f'Monitor {nome} excluído com sucesso!')
            
            if is_ajax:
                return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_monitores_listar')})
            return redirect('militares:ensino_monitores_listar')
        
        # GET - mostrar confirmação
        if is_ajax:
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            html = render_to_string('militares/ensino/monitores/excluir_modal.html', {'monitor': monitor}, request=request)
            return HttpResponse(html)
        
        return render(request, 'militares/ensino/monitores/excluir.html', {'monitor': monitor})
    
    except Exception as e:
        logger.exception('Erro ao excluir monitor')
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao processar exclusão: {str(e)}'
            }, status=500)
        messages.error(request, f'Erro ao excluir monitor: {str(e)}')
        return redirect('militares:ensino_monitores_listar')


# ============================================================================
# 0. EDIÇÕES DE CURSO (Para cursos permanentes)
# ============================================================================

@login_required
def edicoes_por_curso_json(request, curso_id):
    """Retorna edições de um curso em formato JSON"""
    from militares.models import EdicaoCurso
    
    try:
        curso = CursoEnsino.objects.get(pk=curso_id)
        if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_curso(request.user, curso):
            from django.http import JsonResponse
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        edicoes = EdicaoCurso.objects.filter(curso=curso, ativa=True).order_by('-ano', '-numero_edicao')
        
        edicoes_data = [{
            'id': edicao.pk,
            'nome': edicao.nome,
            'numero_edicao': edicao.numero_edicao,
            'ano': edicao.ano,
        } for edicao in edicoes]
        
        return JsonResponse({'edicoes': edicoes_data})
    except CursoEnsino.DoesNotExist:
        return JsonResponse({'edicoes': []}, status=404)


@login_required
def listar_edicoes(request):
    """Lista todas as edições de cursos"""
    from militares.models import EdicaoCurso
    
    edicoes = EdicaoCurso.objects.select_related('curso').all()
    edicoes = _filtrar_edicoes_vinculadas(request.user, edicoes)
    
    curso_id = request.GET.get('curso', '')
    ano = request.GET.get('ano', '')
    ativa = request.GET.get('ativa', '')
    
    if curso_id:
        edicoes = edicoes.filter(curso_id=curso_id)
    
    if ano:
        edicoes = edicoes.filter(ano=ano)
    
    if ativa == 'true':
        edicoes = edicoes.filter(ativa=True)
    elif ativa == 'false':
        edicoes = edicoes.filter(ativa=False)
    
    edicoes = edicoes.order_by('-ano', '-numero_edicao')
    
    # Buscar cursos permanentes para filtro
    cursos_permanentes = CursoEnsino.objects.filter(tipo_curso='PERMANENTE').order_by('nome')
    
    paginator = Paginator(edicoes, 20)
    page = request.GET.get('page')
    edicoes = paginator.get_page(page)
    
    context = {
        'edicoes': edicoes,
        'cursos_permanentes': cursos_permanentes,
    }
    return render(request, 'militares/ensino/edicoes/listar.html', context)


@login_required
def criar_edicao(request):
    """Cria uma nova edição de curso"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar edições.')
        return redirect('militares:ensino_edicoes_listar')
    
    from militares.models import EdicaoCurso
    from militares.forms_ensino import EdicaoCursoForm
    
    # Verificar se veio curso_id na query string
    curso_id = request.GET.get('curso', '')
    curso_pre_selecionado = None
    if curso_id:
        try:
            curso_pre_selecionado = CursoEnsino.objects.get(pk=curso_id)
        except CursoEnsino.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = EdicaoCursoForm(request.POST)
        if form.is_valid():
            try:
                edicao = form.save()
                messages.success(request, f'Edição {edicao.nome} criada com sucesso!')
                return redirect('militares:ensino_edicao_detalhes', pk=edicao.pk)
            except Exception as e:
                messages.error(request, f'Erro ao criar edição: {str(e)}')
    else:
        form = EdicaoCursoForm()
        # Pré-selecionar curso se veio na query string
        if curso_pre_selecionado:
            form.fields['curso'].initial = curso_pre_selecionado
    
    return render(request, 'militares/ensino/edicoes/criar.html', {
        'form': form,
        'curso_pre_selecionado': curso_pre_selecionado
    })


@login_required
def detalhes_edicao(request, pk):
    """Detalhes de uma edição de curso"""
    from militares.models import EdicaoCurso
    
    edicao = get_object_or_404(EdicaoCurso.objects.select_related('curso'), pk=pk)
    
    # Buscar todas as turmas desta edição
    turmas = TurmaEnsino.objects.filter(edicao=edicao).order_by('data_inicio', 'identificacao')
    
    context = {
        'edicao': edicao,
        'turmas': turmas,
    }
    return render(request, 'militares/ensino/edicoes/detalhes.html', context)


@login_required
def resultado_final_edicao(request, pk):
    """Calcula e exibe o resultado final da edição (unindo todas as turmas)"""
    from militares.models import EdicaoCurso, AlunoEnsino, AproveitamentoDisciplina
    from django.db.models import Avg, Count, Q
    from decimal import Decimal
    
    edicao = get_object_or_404(EdicaoCurso.objects.select_related('curso'), pk=pk)
    
    # Buscar todas as turmas desta edição
    turmas = TurmaEnsino.objects.filter(edicao=edicao).order_by('data_inicio', 'identificacao')
    
    # Buscar todos os alunos de todas as turmas desta edição
    alunos_edicao = AlunoEnsino.objects.filter(
        turma__edicao=edicao,
        situacao__in=['ATIVO', 'CONCLUIDO']
    ).select_related('militar', 'pessoa_externa').distinct().order_by('matricula')
    
    # Calcular resultado final para cada aluno (unindo todas as turmas)
    resultado_final_edicao_list = []
    
    for aluno in alunos_edicao:
        # Buscar todas as turmas que este aluno participou nesta edição
        turmas_aluno = TurmaEnsino.objects.filter(
            edicao=edicao,
            alunos=aluno
        )
        
        # Calcular média final do curso (MFC) - média aritmética das MGM de todas as disciplinas
        # MFC = média aritmética das MGM de todas as disciplinas do curso
        # Buscar aproveitamentos de todas as turmas da edição
        aproveitamentos = AproveitamentoDisciplina.objects.filter(
            aluno=aluno,
            disciplina__in=edicao.curso.disciplinas.all(),
            turma__in=turmas_aluno
        ).select_related('disciplina', 'turma')
        
        mgms = []
        disciplinas_info = {}
        disciplinas_aprovadas = 0
        disciplinas_reprovadas = 0
        disciplinas_em_andamento = 0
        total_disciplinas = edicao.curso.disciplinas.count()
        
        for aproveitamento in aproveitamentos:
            # Calcular MGM (Média Geral da Disciplina)
            if aproveitamento.nota_recuperacao is not None:
                # Se tem recuperação, MGM = nota de recuperação
                mgm = float(aproveitamento.nota_recuperacao)
            else:
                # Se não tem recuperação, MGM = média aritmética das VCs (Verificações de Conhecimento)
                # Buscar notas das avaliações
                from militares.models import NotaAvaliacao
                notas = NotaAvaliacao.objects.filter(
                    aluno=aluno,
                    avaliacao__disciplina=aproveitamento.disciplina,
                    avaliacao__turma__edicao=edicao
                ).exclude(avaliacao__tipo='RECUPERACAO')
                
                if notas.exists():
                    notas_valores = [float(n.nota) for n in notas if n.nota is not None]
                    if notas_valores:
                        mgm = sum(notas_valores) / len(notas_valores)
                    else:
                        mgm = 0.0
                else:
                    mgm = 0.0
            
            mgms.append(mgm)
            
            # Verificar status da disciplina
            media_minima = float(aproveitamento.disciplina.media_minima_aprovacao) if aproveitamento.disciplina.media_minima_aprovacao else 7.0
            
            if aproveitamento.aprovado:
                disciplinas_aprovadas += 1
            elif mgm > 0:
                disciplinas_reprovadas += 1
            else:
                disciplinas_em_andamento += 1

            disciplinas_info[aproveitamento.disciplina.pk] = {
                'disciplina': aproveitamento.disciplina,
                'mgm': round(mgm, 2),
                'aprovado': bool(aproveitamento.aprovado),
                'aprovado_com_recuperacao': bool(aproveitamento.aprovado_com_recuperacao),
                'nota_recuperacao': float(aproveitamento.nota_recuperacao) if aproveitamento.nota_recuperacao is not None else None,
                'nota_final': float(aproveitamento.nota_final) if aproveitamento.nota_final is not None else None,
                'frequencia_percentual': float(aproveitamento.frequencia_percentual) if aproveitamento.frequencia_percentual is not None else None,
                'status_disciplina': (
                    'APROVADO' if aproveitamento.aprovado else (
                        'APROVADO_COM_RECUPERACAO' if aproveitamento.aprovado_com_recuperacao else (
                            'REPROVADO' if mgm > 0 else 'EM_ANDAMENTO'
                        )
                    )
                ),
                'reprovado_por_faltas': False,
                'motivos_frequencia': [],
            }

        # Fallback: se não há aproveitamentos cadastrados, calcular MGM pelas notas
        if not disciplinas_info:
            from militares.models import NotaAvaliacao
            notas_qs = NotaAvaliacao.objects.filter(
                aluno=aluno,
                avaliacao__turma__edicao=edicao
            ).select_related('avaliacao', 'avaliacao__disciplina')

            notas_por_disciplina = {}
            for nota in notas_qs:
                disc = nota.avaliacao.disciplina
                did = disc.pk
                if did not in notas_por_disciplina:
                    notas_por_disciplina[did] = {
                        'disciplina': disc,
                        'notas': [],
                        'pesos': [],
                        'recuperacao': None,
                    }
                if getattr(nota.avaliacao, 'tipo', None) == 'RECUPERACAO':
                    notas_por_disciplina[did]['recuperacao'] = float(nota.nota)
                else:
                    peso = float(getattr(nota.avaliacao, 'peso', 1) or 1)
                    notas_por_disciplina[did]['notas'].append(float(nota.nota))
                    notas_por_disciplina[did]['pesos'].append(peso)

            for did, dados in notas_por_disciplina.items():
                disc = dados['disciplina']
                media_minima = float(getattr(disc, 'media_minima_aprovacao', 7.0) or 7.0)
                rec = dados['recuperacao']
                if rec is not None and rec >= 6.0:
                    mgm_calc = rec
                    status_disc = 'APROVADO_COM_RECUPERACAO'
                    aprovado = True
                    aprovado_com_recuperacao = True
                else:
                    if dados['notas']:
                        soma_pesos = sum(dados['pesos']) if dados['pesos'] else len(dados['notas'])
                        soma_ponderada = sum(n * p for n, p in zip(dados['notas'], dados['pesos']))
                        mgm_calc = soma_ponderada / soma_pesos if soma_pesos > 0 else 0.0
                    else:
                        mgm_calc = 0.0
                    aprovado = mgm_calc >= media_minima and mgm_calc > 0
                    aprovado_com_recuperacao = False
                    status_disc = 'APROVADO' if aprovado else ('REPROVADO' if mgm_calc > 0 else 'EM_ANDAMENTO')

                mgms.append(mgm_calc)
                if aprovado:
                    disciplinas_aprovadas += 1
                elif mgm_calc > 0:
                    disciplinas_reprovadas += 1
                else:
                    disciplinas_em_andamento += 1

                disciplinas_info[did] = {
                    'disciplina': disc,
                    'mgm': round(mgm_calc, 2),
                    'aprovado': aprovado,
                    'aprovado_com_recuperacao': aprovado_com_recuperacao,
                    'nota_recuperacao': rec,
                    'nota_final': None,
                    'frequencia_percentual': None,
                    'status_disciplina': status_disc,
                    'reprovado_por_faltas': False,
                    'motivos_frequencia': [],
                }
        
        # Calcular MFC (Média Final do Curso)
        mfc = sum(mgms) / len(mgms) if mgms else 0.0
        
        # Verificar se reprovou por frequência
        reprovado_por_frequencia = False
        motivos_reprovacao_frequencia = []
        reprovacao_freq_disciplina_ids = set()
        
        # Buscar frequências de todas as turmas da edição
        from militares.models import FrequenciaAula
        frequencias_edicao = FrequenciaAula.objects.filter(
            aluno=aluno,
            aula__turma__edicao=edicao
        ).select_related('aula', 'aula__disciplina')
        
        # Agrupar por disciplina
        frequencias_por_disciplina = {}
        for freq in frequencias_edicao:
            disciplina_id = freq.aula.disciplina.pk
            if disciplina_id not in frequencias_por_disciplina:
                frequencias_por_disciplina[disciplina_id] = {
                    'disciplina': freq.aula.disciplina,
                    'frequencias': []
                }
            frequencias_por_disciplina[disciplina_id]['frequencias'].append(freq)
        
        # Verificar reprovação por frequência em cada disciplina
        for disciplina_id, dados in frequencias_por_disciplina.items():
            disciplina = dados['disciplina']
            frequencias = dados['frequencias']
            
            # Calcular total de horas-aula programadas
            from datetime import datetime, timedelta
            total_horas_aula_programadas = 0.0
            horas_perdidas_nao_justificadas = 0.0
            horas_perdidas_justificadas = 0.0
            
            # Buscar todas as aulas da disciplina nas turmas da edição
            from militares.models import AulaEnsino
            aulas_disciplina = AulaEnsino.objects.filter(
                turma__edicao=edicao,
                disciplina=disciplina
            )
            
            for aula in aulas_disciplina:
                if aula.hora_inicio and aula.hora_fim:
                    inicio = datetime.combine(aula.data_aula, aula.hora_inicio)
                    fim = datetime.combine(aula.data_aula, aula.hora_fim)
                    if fim < inicio:
                        fim += timedelta(days=1)
                    duracao_minutos = (fim - inicio).total_seconds() / 60
                    horas_aula = duracao_minutos / 45.0
                    total_horas_aula_programadas += horas_aula
            
            # Calcular horas perdidas
            for freq in frequencias:
                if freq.aula:
                    if freq.aula.hora_inicio and freq.aula.hora_fim:
                        inicio = datetime.combine(freq.aula.data_aula, freq.aula.hora_inicio)
                        fim = datetime.combine(freq.aula.data_aula, freq.aula.hora_fim)
                        if fim < inicio:
                            fim += timedelta(days=1)
                        duracao_minutos = (fim - inicio).total_seconds() / 60
                        horas_aula = duracao_minutos / 45.0
                    else:
                        horas_aula = 0.0
                    
                    if freq.presenca == 'FALTA':
                        horas_perdidas_nao_justificadas += horas_aula
                    elif freq.presenca == 'FALTA_JUSTIFICADA':
                        horas_perdidas_justificadas += horas_aula
            
            # Verificar reprovação conforme ITE 17.1
            if total_horas_aula_programadas > 0:
                percentual_faltas_nao_justificadas = (horas_perdidas_nao_justificadas / total_horas_aula_programadas * 100)
                percentual_faltas_justificadas = (horas_perdidas_justificadas / total_horas_aula_programadas * 100)
                total_faltas_horas = horas_perdidas_nao_justificadas + horas_perdidas_justificadas
                percentual_total_faltas = (total_faltas_horas / total_horas_aula_programadas * 100)
                
                if (percentual_faltas_nao_justificadas > 20.0 or
                    percentual_faltas_justificadas > 30.0 or
                    percentual_total_faltas > 40.0):
                    reprovado_por_frequencia = True
                    reprovacao_freq_disciplina_ids.add(disciplina_id)
                    if percentual_faltas_nao_justificadas > 20.0:
                        motivos_reprovacao_frequencia.append(
                            f"{disciplina.nome}: Faltas não justificadas {percentual_faltas_nao_justificadas:.2f}% (limite: 20%)"
                        )
                    if percentual_faltas_justificadas > 30.0:
                        motivos_reprovacao_frequencia.append(
                            f"{disciplina.nome}: Faltas justificadas {percentual_faltas_justificadas:.2f}% (limite: 30%)"
                        )
                    if percentual_total_faltas > 40.0:
                        motivos_reprovacao_frequencia.append(
                            f"{disciplina.nome}: Total de faltas {percentual_total_faltas:.2f}% (limite: 40%)"
                        )

                    if disciplina_id in disciplinas_info:
                        disciplinas_info[disciplina_id]['reprovado_por_faltas'] = True
                        disciplinas_info[disciplina_id]['status_disciplina'] = 'REPROVADO_POR_FALTAS'
                        disciplinas_info[disciplina_id]['motivos_frequencia'] = motivos_reprovacao_frequencia[:]
        
        # Determinar status final
        if reprovado_por_frequencia:
            status_final = 'REPROVADO_POR_FALTAS'
        elif disciplinas_reprovadas > 0:
            status_final = 'REPROVADO'
        elif disciplinas_aprovadas == total_disciplinas:
            houve_recuperacao = any(di.get('aprovado_com_recuperacao') for di in disciplinas_info.values())
            status_final = 'APROVADO_2_EPOCA' if houve_recuperacao else 'APROVADO'
        else:
            status_final = 'EM_ANDAMENTO'
        
        resultado_final_edicao_list.append({
            'aluno': aluno,
            'mfc': round(mfc, 3),
            'mgms': mgms,
            'disciplinas_aprovadas': disciplinas_aprovadas,
            'disciplinas_reprovadas': disciplinas_reprovadas,
            'disciplinas_em_andamento': disciplinas_em_andamento,
            'total_disciplinas': total_disciplinas,
            'status_final': status_final,
            'reprovado_por_frequencia': reprovado_por_frequencia,
            'motivos_reprovacao_frequencia': motivos_reprovacao_frequencia,
            'turmas': turmas_aluno,
            'disciplinas': list(disciplinas_info.values()),
        })
    
    # Ordenar por MFC decrescente e desempatar por antiguidade do militar
    def _antiguidade_key(res):
        aluno = res.get('aluno')
        militar = getattr(aluno, 'militar', None)
        if militar:
            numeracao = militar.numeracao_antiguidade if militar.numeracao_antiguidade is not None else 999999
            promo_ord = militar.data_promocao_atual.toordinal() if getattr(militar, 'data_promocao_atual', None) else 99999999
            return (numeracao, promo_ord)
        return (999999, 99999999)

    last_direct_mfc = None
    for r in resultado_final_edicao_list:
        if r['status_final'] == 'APROVADO':
            if last_direct_mfc is None or r['mfc'] < last_direct_mfc:
                last_direct_mfc = r['mfc']
    if last_direct_mfc is not None:
        from decimal import Decimal
        epsilon = Decimal('0.01')
        last_direct_dec = Decimal(str(last_direct_mfc))
        segunda_epoca = [r for r in resultado_final_edicao_list if r['status_final'] == 'APROVADO_2_EPOCA']
        segunda_epoca.sort(key=lambda x: (-x['mfc'], _antiguidade_key(x)))
        for i, r in enumerate(segunda_epoca, start=1):
            ajuste = epsilon * Decimal(str(i))
            mfc_calc = Decimal(str(r['mfc']))
            mfc_ajustada = min(mfc_calc, last_direct_dec - ajuste)
            if mfc_ajustada < 0:
                mfc_ajustada = Decimal('0.00')
            r['mfc_ajustada'] = float(round(mfc_ajustada, 3))
            r['mfc'] = r['mfc_ajustada']
    resultado_final_edicao_list.sort(key=lambda x: (
        x['status_final'] not in ('APROVADO', 'APROVADO_2_EPOCA'),
        -(x.get('mfc_ajustada', x['mfc'])),
        _antiguidade_key(x)
    ))
    
    # Adicionar posição/antiguidade
    for idx, resultado in enumerate(resultado_final_edicao_list, start=1):
        resultado['antiguidade'] = idx
    
    aprovados_list = [r for r in resultado_final_edicao_list if r['status_final'] in ('APROVADO', 'APROVADO_2_EPOCA')]
    reprovados_list = [r for r in resultado_final_edicao_list if r['status_final'] in ('REPROVADO', 'REPROVADO_POR_FALTAS')]
    andamento_list = [r for r in resultado_final_edicao_list if r['status_final'] == 'EM_ANDAMENTO']
    context = {
        'edicao': edicao,
        'turmas': turmas,
        'resultado_final': resultado_final_edicao_list,
        'resultado_final_aprovados': aprovados_list,
        'resultado_final_reprovados': reprovados_list,
        'resultado_final_andamento': andamento_list,
    }
    return render(request, 'militares/ensino/edicoes/resultado_final.html', context)


@login_required
def editar_edicao(request, pk):
    """Edita uma edição de curso"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar edições.')
        return redirect('militares:ensino_edicoes_listar')
    
    from militares.models import EdicaoCurso
    from militares.forms_ensino import EdicaoCursoForm
    
    edicao = get_object_or_404(EdicaoCurso, pk=pk)
    
    if request.method == 'POST':
        form = EdicaoCursoForm(request.POST, instance=edicao)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Edição {edicao.nome} atualizada com sucesso!')
                return redirect('militares:ensino_edicao_detalhes', pk=edicao.pk)
            except Exception as e:
                messages.error(request, f'Erro ao atualizar edição: {str(e)}')
    else:
        form = EdicaoCursoForm(instance=edicao)
    
    turmas = TurmaEnsino.objects.filter(edicao=edicao).order_by('data_inicio', 'identificacao')
    return render(request, 'militares/ensino/edicoes/editar.html', {'form': form, 'edicao': edicao, 'turmas': turmas})


@login_required
def deletar_edicao(request, pk):
    """Deleta uma edição de curso"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para deletar edições.')
        return redirect('militares:ensino_edicoes_listar')
    
    from militares.models import EdicaoCurso
    
    edicao = get_object_or_404(EdicaoCurso, pk=pk)
    
    if request.method == 'POST':
        try:
            nome_edicao = edicao.nome
            edicao.delete()
            messages.success(request, f'Edição {nome_edicao} excluída com sucesso!')
            return redirect('militares:ensino_edicoes_listar')
        except Exception as e:
            messages.error(request, f'Erro ao excluir edição: {str(e)}')
            return redirect('militares:ensino_edicao_detalhes', pk=pk)
    
    return render(request, 'militares/ensino/edicoes/deletar_confirm.html', {'edicao': edicao})


# ============================================================================
# 1. CURSOS (Nível Principal)
# ============================================================================

@login_required
def listar_cursos(request):
    """Lista todos os cursos"""
    cursos = CursoEnsino.objects.all()
    if _eh_coordenador_ou_supervisor_curso(request.user):
        cursos = _filtrar_cursos_vinculados(request.user, cursos)
    
    busca = request.GET.get('busca', '')
    publico_alvo = request.GET.get('publico_alvo', '')
    ativo = request.GET.get('ativo', '')
    
    if busca:
        cursos = cursos.filter(
            Q(codigo__icontains=busca) |
            Q(nome__icontains=busca) |
            Q(finalidade__icontains=busca)
        )
    
    if publico_alvo:
        cursos = cursos.filter(publico_alvo=publico_alvo)
    
    if ativo == 'true':
        cursos = cursos.filter(ativo=True)
    elif ativo == 'false':
        cursos = cursos.filter(ativo=False)
    
    paginator = Paginator(cursos, 20)
    page = request.GET.get('page')
    cursos = paginator.get_page(page)
    
    context = {
        'cursos': cursos,
        'publicos_alvo': CursoEnsino.PUBLICO_ALVO_CHOICES,
    }
    return render(request, 'militares/ensino/cursos/listar.html', context)


@login_required
def criar_curso(request):
    """Cria um novo curso"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar cursos.')
        return redirect('militares:ensino_curso_listar')
    
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        form = CursoEnsinoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Salvar o curso usando form.save() que já trata o campo escolaridade_requerida
                curso = form.save(commit=False)
                
                # Processar disciplinas (vindas de inputs hidden)
                disciplinas_ids = request.POST.getlist('disciplinas')
                if disciplinas_ids:
                    disciplinas_para_vincular = []
                    for disciplina_id_str in disciplinas_ids:
                        if disciplina_id_str:
                            try:
                                disciplina_id = int(disciplina_id_str)
                                disciplina = DisciplinaEnsino.objects.get(pk=disciplina_id)
                                disciplinas_para_vincular.append(disciplina)
                            except (ValueError, DisciplinaEnsino.DoesNotExist):
                                continue
                    # Salvar o curso primeiro para poder vincular disciplinas
                    curso.save()
                    # Vincular disciplinas
                    curso.disciplinas.set(disciplinas_para_vincular)
                else:
                    # Salvar o curso mesmo sem disciplinas
                    curso.save()
                    # Salvar relacionamentos many-to-many se houver
                    form.save_m2m()
                
                # Processar múltiplos arquivos de ementa
                ementas_upload = request.FILES.getlist('ementa[]')
                if ementas_upload:
                    ultima_ementa = None
                    for arquivo in ementas_upload:
                        if arquivo:
                            try:
                                ultima_ementa = arquivo
                                DocumentoCursoEnsino.objects.create(
                                    curso=curso,
                                    tipo='EMENTA',
                                    titulo=f'Ementa - {arquivo.name}'[:200],
                                    arquivo=arquivo,
                                    upload_por=request.user
                                )
                            except Exception as e:
                                logger.error(f'Erro ao processar ementa: {str(e)}')
                    # Atualizar campo original com o último arquivo (compatibilidade)
                    if ultima_ementa:
                        curso.ementa = ultima_ementa
                        curso.save(update_fields=['ementa'])
                
                # Processar múltiplos arquivos de plano_curso
                planos_upload = request.FILES.getlist('plano_curso[]')
                if planos_upload:
                    ultimo_plano = None
                    for arquivo in planos_upload:
                        if arquivo:
                            try:
                                ultimo_plano = arquivo
                                DocumentoCursoEnsino.objects.create(
                                    curso=curso,
                                    tipo='PLANO_CURSO',
                                    titulo=f'Plano de Curso - {arquivo.name}'[:200],
                                    arquivo=arquivo,
                                    upload_por=request.user
                                )
                            except Exception as e:
                                logger.error(f'Erro ao processar plano de curso: {str(e)}')
                    # Atualizar campo original com o último arquivo (compatibilidade)
                    if ultimo_plano:
                        curso.plano_curso = ultimo_plano
                        curso.save(update_fields=['plano_curso'])
                
                # Processar múltiplos arquivos de plano_pedagogico
                planos_pedagogicos_upload = request.FILES.getlist('plano_pedagogico[]')
                if planos_pedagogicos_upload:
                    ultimo_plano_pedagogico = None
                    for arquivo in planos_pedagogicos_upload:
                        if arquivo:
                            try:
                                ultimo_plano_pedagogico = arquivo
                                DocumentoCursoEnsino.objects.create(
                                    curso=curso,
                                    tipo='PLANO_PEDAGOGICO',
                                    titulo=f'Plano Pedagógico - {arquivo.name}'[:200],
                                    arquivo=arquivo,
                                    upload_por=request.user
                                )
                            except Exception as e:
                                logger.error(f'Erro ao processar plano pedagógico: {str(e)}')
                    # Atualizar campo original com o último arquivo (compatibilidade)
                    if ultimo_plano_pedagogico:
                        curso.plano_pedagogico = ultimo_plano_pedagogico
                        curso.save(update_fields=['plano_pedagogico'])
                
                # Processar novos documentos (seção de documentos genéricos)
                documentos_upload = request.FILES.getlist('documentos[]')
                tipos_documentos = request.POST.getlist('tipos_documentos[]', [])
                titulos_documentos = request.POST.getlist('titulos_documentos[]', [])
                
                for idx, arquivo in enumerate(documentos_upload):
                    if not arquivo:
                        continue
                    
                    try:
                        tipo_doc = tipos_documentos[idx] if idx < len(tipos_documentos) else 'OUTROS'
                        titulo_doc = titulos_documentos[idx] if idx < len(titulos_documentos) else arquivo.name
                        
                        DocumentoCursoEnsino.objects.create(
                            curso=curso,
                            tipo=tipo_doc,
                            titulo=titulo_doc[:200],
                            arquivo=arquivo,
                            upload_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar documento {idx}: {str(e)}')
                        continue
                
                # Processar múltiplos arquivos complementares
                arquivos_complementares_upload = request.FILES.getlist('arquivos_complementares[]')
                titulos_arquivos = request.POST.getlist('arquivos_complementares_titulos[]', [])
                descricoes_arquivos = request.POST.getlist('arquivos_complementares_descricoes[]', [])
                
                for idx, arquivo in enumerate(arquivos_complementares_upload):
                    if not arquivo:
                        continue
                    
                    try:
                        titulo = titulos_arquivos[idx] if idx < len(titulos_arquivos) else arquivo.name
                        descricao = descricoes_arquivos[idx] if idx < len(descricoes_arquivos) else ''
                        
                        DocumentoCursoEnsino.objects.create(
                            curso=curso,
                            tipo='ARQUIVO_COMPLEMENTAR',
                            titulo=titulo[:200],
                            descricao=descricao,
                            arquivo=arquivo,
                            upload_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar arquivo complementar {idx}: {str(e)}')
                        continue
                
                # Processar múltiplos links úteis
                links_uteis_urls = request.POST.getlist('links_uteis_urls[]', [])
                links_uteis_titulos = request.POST.getlist('links_uteis_titulos[]', [])
                links_uteis_descricoes = request.POST.getlist('links_uteis_descricoes[]', [])
                
                for idx, url in enumerate(links_uteis_urls):
                    if not url:
                        continue
                    
                    try:
                        titulo = links_uteis_titulos[idx] if idx < len(links_uteis_titulos) else url
                        descricao = links_uteis_descricoes[idx] if idx < len(links_uteis_descricoes) else ''
                        
                        LinkUtilCurso.objects.create(
                            curso=curso,
                            titulo=titulo[:200],
                            url=url,
                            descricao=descricao,
                            criado_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar link útil {idx}: {str(e)}')
                        continue
                
                messages.success(request, f'Curso {curso.codigo} criado com sucesso!')
                return redirect('militares:ensino_curso_detalhes', pk=curso.pk)
            except Exception as e:
                logger.exception('Erro ao criar curso')
                error_message = str(e)
                messages.error(request, f'Erro ao criar curso: {error_message}')
    else:
        form = CursoEnsinoForm()
    
    return render(request, 'militares/ensino/cursos/criar.html', {'form': form})


@login_required
def disciplinas_curso_json(request, pk):
    """Retorna as disciplinas de um curso em JSON com instrutores e monitores disponíveis"""
    from militares.models import DisciplinaCurso, InstrutorEnsino, MonitorEnsino, Militar, BlocoDisciplinaTurma
    from django.http import JsonResponse
    
    curso = get_object_or_404(CursoEnsino, pk=pk)
    if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_curso(request.user, curso):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
    disciplinas_curso = DisciplinaCurso.objects.filter(curso=curso).select_related('disciplina').order_by('ordem')
    
    # Verificar se há uma turma sendo editada (parâmetro opcional)
    turma_id = request.GET.get('turma_id', None)
    blocos_existentes = {}
    if turma_id:
        try:
            blocos = BlocoDisciplinaTurma.objects.filter(turma_id=turma_id).select_related('disciplina')
            blocos_existentes = {bloco.disciplina_id: {'numero_bloco': bloco.numero_bloco, 'ordem_bloco': bloco.ordem_disciplina} for bloco in blocos}
        except (ValueError, TypeError):
            pass
    
    disciplinas_data = []
    for disc_curso in disciplinas_curso:
        disciplina = disc_curso.disciplina
        bloco_info = blocos_existentes.get(disciplina.pk, {})
        disc_data = {
            'id': disciplina.pk,
            'nome': disciplina.nome,
            'codigo': disciplina.codigo or '',
            'ordem': disc_curso.ordem or 0,
            'numero_bloco': bloco_info.get('numero_bloco', 1),
            'ordem_bloco': bloco_info.get('ordem_bloco', 1),
            'instrutor_militar_id': None,
            'instrutor_militar_nome': None,
            'instrutor_externo_id': None,
            'instrutor_externo_nome': None,
            'monitores_militares_ids': [],
            'monitores_militares_nomes': [],
            'monitores_externos_ids': [],
            'monitores_externos_nomes': [],
        }
        
        # Instrutor responsável
        # Se for militar, buscar o InstrutorEnsino correspondente
        if disciplina.instrutor_responsavel_militar:
            # Buscar o InstrutorEnsino que tem este militar
            instrutor_ensino = InstrutorEnsino.objects.filter(militar=disciplina.instrutor_responsavel_militar, ativo=True).first()
            if instrutor_ensino:
                disc_data['instrutor_militar_id'] = instrutor_ensino.pk
                disc_data['instrutor_militar_nome'] = f"{disciplina.instrutor_responsavel_militar.get_posto_graduacao_display()} {disciplina.instrutor_responsavel_militar.nome_completo}"
        elif disciplina.instrutor_responsavel_externo:
            disc_data['instrutor_externo_id'] = disciplina.instrutor_responsavel_externo.pk
            disc_data['instrutor_externo_nome'] = disciplina.instrutor_responsavel_externo.get_nome_completo()
        
        # Monitores militares - buscar os MonitorEnsino correspondentes
        for monitor_militar in disciplina.monitores_militares.all():
            monitor_ensino = MonitorEnsino.objects.filter(militar=monitor_militar, ativo=True).first()
            if monitor_ensino:
                disc_data['monitores_militares_ids'].append(monitor_ensino.pk)
                disc_data['monitores_militares_nomes'].append(f"{monitor_militar.get_posto_graduacao_display()} {monitor_militar.nome_completo}")
        
        # Monitores externos
        for monitor in disciplina.monitores_externos.all():
            disc_data['monitores_externos_ids'].append(monitor.pk)
            disc_data['monitores_externos_nomes'].append(monitor.get_nome_completo())
        
        disciplinas_data.append(disc_data)
    
    # Buscar apenas instrutores cadastrados (não todos os militares)
    instrutores_data = []
    instrutores = InstrutorEnsino.objects.filter(ativo=True).select_related('militar')
    for instrutor in instrutores:
        if instrutor.militar:
            # Instrutor militar cadastrado
            instrutores_data.append({
                'id': instrutor.pk,
                'tipo': 'MILITAR',
                'nome': f"{instrutor.militar.get_posto_graduacao_display()} {instrutor.militar.nome_completo}",
                'militar_id': instrutor.militar.pk
            })
        else:
            # Instrutor externo (civil ou outra força)
            nome = instrutor.nome_civil or instrutor.nome_outra_forca or 'Instrutor Externo'
            instrutores_data.append({
                'id': instrutor.pk,
                'tipo': 'EXTERNO',
                'nome': nome
            })
    
    # Buscar apenas monitores cadastrados (não todos os militares)
    monitores_data = []
    monitores = MonitorEnsino.objects.filter(ativo=True).select_related('militar')
    for monitor in monitores:
        if monitor.militar:
            # Monitor militar cadastrado
            monitores_data.append({
                'id': monitor.pk,
                'tipo': 'MILITAR',
                'nome': f"{monitor.militar.get_posto_graduacao_display()} {monitor.militar.nome_completo}",
                'militar_id': monitor.militar.pk
            })
        else:
            # Monitor externo (civil ou outra força)
            nome = monitor.nome_civil or monitor.nome_outra_forca or 'Monitor Externo'
            monitores_data.append({
                'id': monitor.pk,
                'tipo': 'EXTERNO',
                'nome': nome
            })
    
    return JsonResponse({
        'disciplinas': disciplinas_data,
        'instrutores': instrutores_data,
        'monitores': monitores_data
    })


@login_required
def detalhes_curso(request, pk):
    """Detalhes completos de um curso"""
    curso = get_object_or_404(
        CursoEnsino.objects.all(),
        pk=pk
    )
    if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_curso(request.user, curso):
        messages.error(request, 'Acesso negado. Você só pode acessar cursos em que está vinculado.')
        return redirect('militares:ensino_curso_listar')
    turmas = TurmaEnsino.objects.filter(curso=curso).select_related('edicao')
    
    # Disciplinas do curso através do modelo intermediário
    disciplinas_curso = DisciplinaCurso.objects.filter(curso=curso).select_related('disciplina').order_by('ordem')
    
    # Buscar edições do curso (se for permanente)
    from django.db.models import Prefetch, Count
    edicoes = EdicaoCurso.objects.filter(curso=curso).order_by('-ano', '-numero_edicao').prefetch_related(
        Prefetch(
            'turmas',
            queryset=TurmaEnsino.objects.select_related('edicao').annotate(total_alunos=Count('alunos')).order_by('data_inicio', 'identificacao')
        )
    )
    
    context = {
        'curso': curso,
        'turmas': turmas,
        'disciplinas_curso': disciplinas_curso,
        'edicoes': edicoes,
    }
    
    return render(request, 'militares/ensino/cursos/detalhes.html', context)


@login_required
def editar_curso(request, pk):
    """Edita um curso existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar cursos.')
        return redirect('militares:ensino_curso_listar')
    
    logger = logging.getLogger(__name__)
    curso = get_object_or_404(CursoEnsino, pk=pk)
    if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_curso(request.user, curso):
        messages.error(request, 'Acesso negado. Você só pode editar cursos em que está vinculado.')
        return redirect('militares:ensino_curso_listar')
    
    try:
        if request.method == 'POST':
            form = CursoEnsinoForm(request.POST, request.FILES, instance=curso)
            if not form.is_valid():
                # Coletar campos obrigatórios que estão com erro
                campos_obrigatorios_com_erro = []
                outros_erros = []
                
                # Log detalhado dos erros para debug
                logger.warning(f'Erros de validação do formulário: {form.errors}')
                
                for field_name, errors in form.errors.items():
                    field = form.fields.get(field_name)
                    if field:
                        # Obter o label do campo
                        field_label = field.label if field.label else field_name.replace('_', ' ').title()
                        
                        # Verificar se o erro indica campo obrigatório vazio
                        erro_obrigatorio = False
                        for error in errors:
                            error_str = str(error).lower()
                            # Verificar padrões comuns de erro de campo obrigatório
                            if any(palavra in error_str for palavra in ['obrigatório', 'required', 'campo', 'este campo', 'this field', 'cannot be null', 'não pode ser nulo']):
                                erro_obrigatorio = True
                                break
                        
                        if erro_obrigatorio or field.required:
                            if field_label not in campos_obrigatorios_com_erro:
                                campos_obrigatorios_com_erro.append(field_label)
                        else:
                            # Campo não obrigatório, mas tem erro
                            for error in errors:
                                outros_erros.append(f'{field_label}: {error}')
                    else:
                        # Campo não encontrado no formulário (pode ser erro não-field)
                        for error in errors:
                            outros_erros.append(f'{field_name}: {error}')
                
                # Se houver campos obrigatórios com erro, mostrar mensagem específica
                if campos_obrigatorios_com_erro:
                    mensagem_erro = f'Não foi possível salvar. Os seguintes campos obrigatórios precisam ser preenchidos: {", ".join(campos_obrigatorios_com_erro)}.'
                    messages.error(request, mensagem_erro)
                
                # Mostrar outros erros se houver
                if outros_erros:
                    for erro in outros_erros:
                        messages.error(request, erro)
            elif form.is_valid():
                try:
                    curso = form.save(commit=False)
                    
                    # Processar disciplinas (vindas de inputs hidden)
                    disciplinas_ids = request.POST.getlist('disciplinas')
                    if disciplinas_ids:
                        disciplinas_para_vincular = []
                        for disciplina_id_str in disciplinas_ids:
                            if disciplina_id_str:
                                try:
                                    disciplina_id = int(disciplina_id_str)
                                    disciplina = DisciplinaEnsino.objects.get(pk=disciplina_id)
                                    disciplinas_para_vincular.append(disciplina)
                                except (ValueError, DisciplinaEnsino.DoesNotExist):
                                    continue
                        # Salvar o curso primeiro para poder vincular disciplinas
                        curso.save()
                        # Vincular disciplinas
                        curso.disciplinas.set(disciplinas_para_vincular)
                    else:
                        # Salvar o curso mesmo sem disciplinas
                        curso.save()
                        # Se não houver disciplinas selecionadas, limpar as existentes
                        curso.disciplinas.clear()
                    
                    # Processar múltiplos arquivos de ementa
                    ementas_upload = request.FILES.getlist('ementa[]')
                    if ementas_upload:
                        ultima_ementa = None
                        for arquivo in ementas_upload:
                            if arquivo:
                                try:
                                    ultima_ementa = arquivo
                                    DocumentoCursoEnsino.objects.create(
                                        curso=curso,
                                        tipo='EMENTA',
                                        titulo=f'Ementa - {arquivo.name}'[:200],
                                        arquivo=arquivo,
                                        upload_por=request.user
                                    )
                                except Exception as e:
                                    logger.error(f'Erro ao processar ementa: {str(e)}')
                        # Atualizar campo original com o último arquivo (compatibilidade)
                        if ultima_ementa:
                            curso.ementa = ultima_ementa
                            curso.save(update_fields=['ementa'])
                    
                    # Processar múltiplos arquivos de plano_curso
                    planos_upload = request.FILES.getlist('plano_curso[]')
                    if planos_upload:
                        ultimo_plano = None
                        for arquivo in planos_upload:
                            if arquivo:
                                try:
                                    ultimo_plano = arquivo
                                    DocumentoCursoEnsino.objects.create(
                                        curso=curso,
                                        tipo='PLANO_CURSO',
                                        titulo=f'Plano de Curso - {arquivo.name}'[:200],
                                        arquivo=arquivo,
                                        upload_por=request.user
                                    )
                                except Exception as e:
                                    logger.error(f'Erro ao processar plano de curso: {str(e)}')
                        # Atualizar campo original com o último arquivo (compatibilidade)
                        if ultimo_plano:
                            curso.plano_curso = ultimo_plano
                            curso.save(update_fields=['plano_curso'])
                    
                    # Processar múltiplos arquivos de plano_pedagogico
                    planos_pedagogicos_upload = request.FILES.getlist('plano_pedagogico[]')
                    if planos_pedagogicos_upload:
                        ultimo_plano_pedagogico = None
                        for arquivo in planos_pedagogicos_upload:
                            if arquivo:
                                try:
                                    ultimo_plano_pedagogico = arquivo
                                    DocumentoCursoEnsino.objects.create(
                                        curso=curso,
                                        tipo='PLANO_PEDAGOGICO',
                                        titulo=f'Plano Pedagógico - {arquivo.name}'[:200],
                                        arquivo=arquivo,
                                        upload_por=request.user
                                    )
                                except Exception as e:
                                    logger.error(f'Erro ao processar plano pedagógico: {str(e)}')
                        # Atualizar campo original com o último arquivo (compatibilidade)
                        if ultimo_plano_pedagogico:
                            curso.plano_pedagogico = ultimo_plano_pedagogico
                            curso.save(update_fields=['plano_pedagogico'])
                    
                    # Processar novos documentos (seção de documentos genéricos)
                    documentos_upload = request.FILES.getlist('documentos[]')
                    tipos_documentos = request.POST.getlist('tipos_documentos[]', [])
                    titulos_documentos = request.POST.getlist('titulos_documentos[]', [])
                    
                    for idx, arquivo in enumerate(documentos_upload):
                        if not arquivo:
                            continue
                        
                        try:
                            tipo_doc = tipos_documentos[idx] if idx < len(tipos_documentos) else 'OUTROS'
                            titulo_doc = titulos_documentos[idx] if idx < len(titulos_documentos) else arquivo.name
                            
                            DocumentoCursoEnsino.objects.create(
                                curso=curso,
                                tipo=tipo_doc,
                                titulo=titulo_doc[:200],
                                arquivo=arquivo,
                                upload_por=request.user
                            )
                        except Exception as e:
                            logger.error(f'Erro ao processar documento {idx}: {str(e)}')
                            continue
                    
                    # Processar remoção de documentos
                    documentos_remover = request.POST.getlist('documentos_remover[]')
                    if documentos_remover:
                        DocumentoCursoEnsino.objects.filter(
                            id__in=documentos_remover,
                            curso=curso
                        ).delete()
                    
                    # Processar múltiplos arquivos complementares
                    arquivos_complementares_upload = request.FILES.getlist('arquivos_complementares[]')
                    titulos_arquivos = request.POST.getlist('arquivos_complementares_titulos[]', [])
                    descricoes_arquivos = request.POST.getlist('arquivos_complementares_descricoes[]', [])
                    
                    for idx, arquivo in enumerate(arquivos_complementares_upload):
                        if not arquivo:
                            continue
                        
                        try:
                            titulo = titulos_arquivos[idx] if idx < len(titulos_arquivos) else arquivo.name
                            descricao = descricoes_arquivos[idx] if idx < len(descricoes_arquivos) else ''
                            
                            DocumentoCursoEnsino.objects.create(
                                curso=curso,
                                tipo='ARQUIVO_COMPLEMENTAR',
                                titulo=titulo[:200],
                                descricao=descricao,
                                arquivo=arquivo,
                                upload_por=request.user
                            )
                        except Exception as e:
                            logger.error(f'Erro ao processar arquivo complementar {idx}: {str(e)}')
                            continue
                    
                    # Processar remoção de arquivos complementares
                    arquivos_complementares_remover = request.POST.getlist('arquivos_complementares_remover[]')
                    if arquivos_complementares_remover:
                        DocumentoCursoEnsino.objects.filter(
                            id__in=arquivos_complementares_remover,
                            curso=curso,
                            tipo='ARQUIVO_COMPLEMENTAR'
                        ).delete()
                    
                    # Processar múltiplos links úteis
                    links_uteis_urls = request.POST.getlist('links_uteis_urls[]', [])
                    links_uteis_titulos = request.POST.getlist('links_uteis_titulos[]', [])
                    links_uteis_descricoes = request.POST.getlist('links_uteis_descricoes[]', [])
                    
                    for idx, url in enumerate(links_uteis_urls):
                        if not url:
                            continue
                        
                        try:
                            titulo = links_uteis_titulos[idx] if idx < len(links_uteis_titulos) else url
                            descricao = links_uteis_descricoes[idx] if idx < len(links_uteis_descricoes) else ''
                            
                            LinkUtilCurso.objects.create(
                                curso=curso,
                                titulo=titulo[:200],
                                url=url,
                                descricao=descricao,
                                criado_por=request.user
                            )
                        except Exception as e:
                            logger.error(f'Erro ao processar link útil {idx}: {str(e)}')
                            continue
                    
                    # Processar remoção de links úteis
                    links_uteis_remover = request.POST.getlist('links_uteis_remover[]')
                    if links_uteis_remover:
                        LinkUtilCurso.objects.filter(
                            id__in=links_uteis_remover,
                            curso=curso
                        ).delete()
                    
                    messages.success(request, f'Curso {curso.codigo} atualizado com sucesso!')
                    return redirect('militares:ensino_curso_detalhes', pk=curso.pk)
                except Exception as e:
                    error_message = str(e)
                    logger.exception('Erro ao salvar curso')
                    messages.error(request, f'Erro ao atualizar curso: {error_message}')
        else:
            form = CursoEnsinoForm(instance=curso)
        
        # Buscar documentos existentes
        documentos_existentes = curso.documentos.all() if hasattr(curso, 'documentos') else []
        ementas_existentes = documentos_existentes.filter(tipo='EMENTA')
        planos_existentes = documentos_existentes.filter(tipo='PLANO_CURSO')
        planos_pedagogicos_existentes = documentos_existentes.filter(tipo='PLANO_PEDAGOGICO')
        
        context = {
            'form': form,
            'curso': curso,
            'documentos_existentes': documentos_existentes,
            'ementas_existentes': ementas_existentes,
            'planos_existentes': planos_existentes,
            'planos_pedagogicos_existentes': planos_pedagogicos_existentes,
        }
        
        return render(request, 'militares/ensino/cursos/editar.html', context)
    
    except Exception as e:
        logger.exception('Erro ao editar curso')
        messages.error(request, f'Erro ao editar curso: {str(e)}')
        return redirect('militares:ensino_cursos_listar')


# ============================================================================
# 2. TURMAS (Dependem de Curso)
# ============================================================================

@login_required
def listar_turmas(request):
    """Lista todas as turmas"""
    turmas = TurmaEnsino.objects.select_related('curso', 'edicao').all()
    if _eh_coordenador_ou_supervisor(request.user):
        turmas = _filtrar_turmas_vinculadas(request.user, turmas)
    
    busca = request.GET.get('busca', '')
    curso_id = request.GET.get('curso', '')
    edicao_id = request.GET.get('edicao', '')
    ativa = request.GET.get('ativa', '')
    
    if busca:
        turmas = turmas.filter(
            Q(identificacao__icontains=busca) |
            Q(curso__nome__icontains=busca) |
            Q(edicao__nome__icontains=busca)
        )
    
    if curso_id:
        turmas = turmas.filter(curso_id=curso_id)
    
    if edicao_id:
        turmas = turmas.filter(edicao_id=edicao_id)
    
    if ativa == 'true':
        turmas = turmas.filter(ativa=True)
    elif ativa == 'false':
        turmas = turmas.filter(ativa=False)
    
    # Contar alunos por turma
    turmas = turmas.annotate(total_alunos=Count('alunos'))
    
    paginator = Paginator(turmas, 20)
    page = request.GET.get('page')
    turmas = paginator.get_page(page)
    
    cursos = CursoEnsino.objects.filter(ativo=True)
    
    # Buscar edições para filtro (apenas cursos permanentes)
    edicoes = EdicaoCurso.objects.select_related('curso').filter(curso__tipo_curso='PERMANENTE').order_by('-ano', '-numero_edicao')
    
    context = {
        'turmas': turmas,
        'cursos': cursos,
        'edicoes': edicoes,
    }
    return render(request, 'militares/ensino/turmas/listar.html', context)


def gerar_matricula_aluno(turma, numero_inicial=None):
    """
    Gera uma matrícula única para o aluno baseada no nome da turma e número sequencial.
    Formato: NOME_TURMA-NUMERO_SEQUENCIAL
    
    Args:
        turma: Instância da TurmaEnsino
        numero_inicial: Número inicial para o sequencial (opcional, usado quando adicionando múltiplos alunos)
    """
    import re
    from militares.models import AlunoEnsino
    
    # Limpar o nome da turma: remover caracteres especiais, espaços, acentos
    nome_turma = turma.identificacao.upper()
    # Remover acentos e caracteres especiais
    nome_turma = re.sub(r'[àáâãäå]', 'A', nome_turma)
    nome_turma = re.sub(r'[èéêë]', 'E', nome_turma)
    nome_turma = re.sub(r'[ìíîï]', 'I', nome_turma)
    nome_turma = re.sub(r'[òóôõö]', 'O', nome_turma)
    nome_turma = re.sub(r'[ùúûü]', 'U', nome_turma)
    nome_turma = re.sub(r'[ç]', 'C', nome_turma)
    # Remover caracteres especiais e espaços, manter apenas letras, números e hífen
    nome_turma = re.sub(r'[^A-Z0-9-]', '', nome_turma)
    # Limitar tamanho para evitar matrículas muito longas
    if len(nome_turma) > 30:
        nome_turma = nome_turma[:30]
    
    # Se não foi fornecido número inicial, contar alunos existentes na turma
    if numero_inicial is None:
        alunos_turma = AlunoEnsino.objects.filter(turma=turma).count()
        numero_sequencial = alunos_turma + 1
    else:
        numero_sequencial = numero_inicial
    
    # Gerar matrícula base
    matricula = f'{nome_turma}-{numero_sequencial:04d}'
    
    # Garantir unicidade
    tentativas = 0
    while AlunoEnsino.objects.filter(matricula=matricula).exists() and tentativas < 100:
        numero_sequencial += 1
        matricula = f'{nome_turma}-{numero_sequencial:04d}'
        tentativas += 1
    
    # Se ainda não for única após 100 tentativas, adicionar sufixo único
    if AlunoEnsino.objects.filter(matricula=matricula).exists():
        import uuid
        sufixo = uuid.uuid4().hex[:4].upper()
        matricula = f'{nome_turma}-{numero_sequencial:04d}-{sufixo}'
    
    return matricula


@login_required
def criar_turma(request):
    """Cria uma nova turma"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar turmas.')
        return redirect('militares:ensino_turmas_listar')
    
    from militares.models import Militar, DisciplinaCurso, AlunoEnsino
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = TurmaEnsinoForm(request.POST)
        if form.is_valid():
            try:
                turma = form.save()
                
                # Processar alunos selecionados (IDs de AlunoEnsino)
                alunos_selecionados = request.POST.getlist('alunos_selecionados')
                alunos_selecionados_ids = [int(id) for id in alunos_selecionados if id]
                
                # Processar militares selecionados (IDs de Militar - serão criados como alunos)
                militares_selecionados = request.POST.getlist('militares_selecionados')
                militares_selecionados_ids = [int(id) for id in militares_selecionados if id]
                
                # Buscar todos os alunos atuais da turma (pode estar vazio na criação)
                alunos_atuais = AlunoEnsino.objects.filter(turma=turma)
                alunos_atuais_count = alunos_atuais.count()
                
                # Criar alunos a partir de militares selecionados
                contador_militares_criados = 0
                for militar_id in militares_selecionados_ids:
                    try:
                        militar = Militar.objects.get(pk=militar_id, classificacao='ATIVO')
                        
                        # Verificar se já existe aluno para este militar
                        aluno_existente = AlunoEnsino.objects.filter(
                            tipo_aluno='BOMBEIRO',
                            militar=militar
                        ).first()
                        
                        if aluno_existente:
                            # Se já existe aluno, adicionar à turma se não estiver
                            if aluno_existente.turma != turma:
                                numero_inicial = alunos_atuais_count + contador_militares_criados + len(alunos_selecionados_ids) + 1
                                matricula = gerar_matricula_aluno(turma, numero_inicial)
                                aluno_existente.turma = turma
                                aluno_existente.matricula = matricula
                                if aluno_existente.situacao not in ['ATIVO', 'CONCLUIDO']:
                                    aluno_existente.situacao = 'ATIVO'
                                aluno_existente.save()
                                alunos_selecionados_ids.append(aluno_existente.pk)
                                contador_militares_criados += 1
                            else:
                                # Aluno já está na turma, apenas adicionar à lista de selecionados
                                if aluno_existente.pk not in alunos_selecionados_ids:
                                    alunos_selecionados_ids.append(aluno_existente.pk)
                        else:
                            # Criar novo aluno a partir do militar
                            numero_inicial = alunos_atuais_count + contador_militares_criados + len(alunos_selecionados_ids) + 1
                            matricula = gerar_matricula_aluno(turma, numero_inicial)
                            
                            novo_aluno = AlunoEnsino.objects.create(
                                tipo_aluno='BOMBEIRO',
                                militar=militar,
                                turma=turma,
                                matricula=matricula,
                                situacao='ATIVO'
                            )
                            alunos_selecionados_ids.append(novo_aluno.pk)
                            contador_militares_criados += 1
                            messages.success(
                                request,
                                f'Bombeiro {militar.get_posto_graduacao_display()} {militar.nome_completo} foi cadastrado como aluno e adicionado à turma.'
                            )
                    except (Militar.DoesNotExist, ValueError) as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Erro ao processar militar {militar_id}: {str(e)}')
                        continue
                
                # Adicionar novos alunos
                contador_novos = 0
                for aluno_id in alunos_selecionados_ids:
                    try:
                        aluno = AlunoEnsino.objects.get(pk=aluno_id)
                        # Verificar se já existe este aluno nesta turma
                        aluno_existente = AlunoEnsino.objects.filter(pk=aluno_id, turma=turma).first()
                        if not aluno_existente:
                            # Se o aluno não tem turma, adicionar à turma e gerar matrícula
                            # Se já tem turma diferente, criar uma cópia do aluno para esta turma
                            if not aluno.turma:
                                numero_inicial = alunos_atuais_count + contador_novos + 1
                                matricula = gerar_matricula_aluno(turma, numero_inicial)
                                aluno.turma = turma
                                aluno.matricula = matricula
                                if aluno.situacao not in ['ATIVO', 'CONCLUIDO']:
                                    aluno.situacao = 'ATIVO'
                                aluno.save()
                                contador_novos += 1
                            elif aluno.turma != turma:
                                # Aluno já está em outra turma - não criar cópia
                                # Um aluno pode ter apenas um cadastro, mas pode estar em múltiplas turmas
                                # Por enquanto, apenas mover o aluno para a nova turma
                                nome_aluno = aluno.get_pessoa_nome()
                                turma_anterior = aluno.turma.identificacao if aluno.turma else 'Nenhuma'
                                messages.warning(
                                    request,
                                    f'O aluno {nome_aluno} já está na turma "{turma_anterior}". '
                                    f'Movendo para a turma "{turma.identificacao}". '
                                    f'Em breve, será possível que um aluno esteja em múltiplas turmas simultaneamente.'
                                )
                                numero_inicial = alunos_atuais_count + contador_novos + 1
                                matricula = gerar_matricula_aluno(turma, numero_inicial)
                                aluno.turma = turma
                                aluno.matricula = matricula
                                if aluno.situacao not in ['ATIVO', 'CONCLUIDO']:
                                    aluno.situacao = 'ATIVO'
                                aluno.save()
                                contador_novos += 1
                    except (AlunoEnsino.DoesNotExist, ValueError) as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Erro ao processar aluno {aluno_id}: {str(e)}')
                        continue
                
                # Remover alunos que não estão mais na lista (caso existam)
                for aluno_atual in alunos_atuais:
                    if aluno_atual.pk not in alunos_selecionados_ids:
                        # Aluno foi removido da lista, remover da turma
                        aluno_atual.turma = None
                        aluno_atual.matricula = None
                        aluno_atual.save()
                
                # Processar instrutores e monitores para cada disciplina
                disciplinas_ids_str = request.POST.get('disciplinas_ids', '')
                if not disciplinas_ids_str:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning('Nenhuma disciplina foi selecionada para a turma')
                else:
                    disciplinas_ids = disciplinas_ids_str.split(',')
                    disciplinas_para_vincular = []
                    
                    for disciplina_id_str in disciplinas_ids:
                        if not disciplina_id_str:
                            continue
                        try:
                            disciplina_id = int(disciplina_id_str)
                            disciplina = DisciplinaEnsino.objects.get(pk=disciplina_id)
                            
                            # Processar instrutor
                            instrutor_value = request.POST.get(f'disciplina_{disciplina_id}_instrutor', '').strip()
                            if instrutor_value:
                                if instrutor_value.startswith('MILITAR_'):
                                    instrutor_ensino_id = int(instrutor_value.replace('MILITAR_', ''))
                                    instrutor_ensino = InstrutorEnsino.objects.get(pk=instrutor_ensino_id)
                                    if instrutor_ensino.militar:
                                        disciplina.instrutor_responsavel_militar = instrutor_ensino.militar
                                        disciplina.instrutor_responsavel_externo = None
                                        disciplina.save(update_fields=['instrutor_responsavel_militar', 'instrutor_responsavel_externo'])
                                elif instrutor_value.startswith('EXTERNO_'):
                                    instrutor_ensino_id = int(instrutor_value.replace('EXTERNO_', ''))
                                    instrutor_ensino = InstrutorEnsino.objects.get(pk=instrutor_ensino_id)
                                    disciplina.instrutor_responsavel_externo = instrutor_ensino
                                    disciplina.instrutor_responsavel_militar = None
                                    disciplina.save(update_fields=['instrutor_responsavel_militar', 'instrutor_responsavel_externo'])
                            else:
                                # Se não houver instrutor selecionado, limpar
                                disciplina.instrutor_responsavel_militar = None
                                disciplina.instrutor_responsavel_externo = None
                                disciplina.save(update_fields=['instrutor_responsavel_militar', 'instrutor_responsavel_externo'])
                            
                            # Processar monitores militares
                            monitores_militares_ids = request.POST.getlist(f'disciplina_{disciplina_id}_monitores_militares[]')
                            monitores_militares_para_adicionar = []
                            for monitor_ensino_id_str in monitores_militares_ids:
                                try:
                                    monitor_ensino_id = int(monitor_ensino_id_str)
                                    monitor_ensino = MonitorEnsino.objects.get(pk=monitor_ensino_id)
                                    if monitor_ensino.militar:
                                        monitores_militares_para_adicionar.append(monitor_ensino.militar)
                                except (MonitorEnsino.DoesNotExist, ValueError):
                                    continue
                            
                            # Processar monitores externos
                            monitores_externos_ids = request.POST.getlist(f'disciplina_{disciplina_id}_monitores_externos[]')
                            monitores_externos_para_adicionar = []
                            for monitor_ensino_id_str in monitores_externos_ids:
                                try:
                                    monitor_ensino_id = int(monitor_ensino_id_str)
                                    monitor_ensino = MonitorEnsino.objects.get(pk=monitor_ensino_id)
                                    monitores_externos_para_adicionar.append(monitor_ensino)
                                except (MonitorEnsino.DoesNotExist, ValueError):
                                    continue
                            
                            # Atualizar monitores da disciplina
                            disciplina.monitores_militares.set(monitores_militares_para_adicionar)
                            disciplina.monitores_externos.set(monitores_externos_para_adicionar)
                            
                            # Adicionar disciplina à lista para vincular à turma
                            disciplinas_para_vincular.append(disciplina)
                            
                        except (DisciplinaEnsino.DoesNotExist, ValueError, InstrutorEnsino.DoesNotExist, MonitorEnsino.DoesNotExist) as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f'Erro ao processar disciplina {disciplina_id_str}: {str(e)}')
                            continue
                    
                    # Vincular disciplinas à turma e criar blocos
                    if disciplinas_para_vincular:
                        turma.disciplinas.set(disciplinas_para_vincular)
                        
                        # Processar blocos de disciplinas
                        from militares.models import BlocoDisciplinaTurma
                        # Limpar blocos existentes para recriar
                        BlocoDisciplinaTurma.objects.filter(turma=turma).delete()
                        
                        for disciplina in disciplinas_para_vincular:
                            disciplina_id = disciplina.pk
                            # Buscar número do bloco do POST
                            numero_bloco_str = request.POST.get(f'disciplina_{disciplina_id}_bloco', '').strip()
                            ordem_disciplina_str = request.POST.get(f'disciplina_{disciplina_id}_ordem_bloco', '1').strip()
                            
                            try:
                                numero_bloco = int(numero_bloco_str) if numero_bloco_str else 1
                                ordem_disciplina = int(ordem_disciplina_str) if ordem_disciplina_str else 1
                                
                                BlocoDisciplinaTurma.objects.create(
                                    turma=turma,
                                    disciplina=disciplina,
                                    numero_bloco=numero_bloco,
                                    ordem_disciplina=ordem_disciplina
                                )
                            except (ValueError, TypeError):
                                # Se não houver bloco definido, criar no bloco 1
                                BlocoDisciplinaTurma.objects.create(
                                    turma=turma,
                                    disciplina=disciplina,
                                    numero_bloco=1,
                                    ordem_disciplina=1
                                )
                
                messages.success(request, f'Turma {turma.identificacao} criada com sucesso!')
                
                if is_ajax:
                    from django.http import JsonResponse
                    from django.urls import reverse
                    return JsonResponse({
                        'success': True,
                        'redirect': reverse('militares:ensino_turma_detalhes', kwargs={'pk': turma.pk})
                    })
                
                return redirect('militares:ensino_turma_detalhes', pk=turma.pk)
            except Exception as e:
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'error': f'Erro ao criar turma: {str(e)}',
                        'errors': form.errors
                    }, status=400)
                messages.error(request, f'Erro ao criar turma: {str(e)}')
                # Redirecionar para a lista se não for AJAX
                return redirect('militares:ensino_turmas_listar')
        else:
            # Formulário com erros
            from militares.models import POSTO_GRADUACAO_CHOICES, InstrutorEnsino, MonitorEnsino
            # Buscar todos os alunos cadastrados (bombeiros, outras forças e civis)
            alunos_disponiveis = AlunoEnsino.objects.filter(
                Q(situacao='ATIVO') | Q(situacao='CONCLUIDO')
            ).select_related('militar', 'pessoa_externa').order_by('tipo_aluno', 'militar__posto_graduacao', 'nome_outra_forca', 'nome_civil')
            
            # Buscar militares que ainda não são alunos
            militares_ja_alunos = AlunoEnsino.objects.filter(
                tipo_aluno='BOMBEIRO',
                militar__isnull=False
            ).values_list('militar_id', flat=True)
            
            militares_nao_alunos = Militar.objects.filter(
                classificacao='ATIVO'
            ).exclude(
                pk__in=militares_ja_alunos
            ).order_by('posto_graduacao', 'nome_completo')
            
            # Manter militares para compatibilidade (mas não usar mais para seleção)
            militares = Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo')
            instrutores = InstrutorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
            monitores = MonitorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
            
            if is_ajax:
                from django.template.loader import render_to_string
                html = render_to_string('militares/ensino/turmas/criar_modal.html', {
                    'form': form,
                    'militares': militares,
                    'militares_nao_alunos': militares_nao_alunos,
                    'alunos_disponiveis': alunos_disponiveis,
                    'postos_graduacao': POSTO_GRADUACAO_CHOICES,
                    'instrutores': instrutores,
                    'monitores': monitores,
                }, request=request)
                from django.http import HttpResponse
                return HttpResponse(html)
            else:
                if is_ajax:
                    from django.template.loader import render_to_string
                    html = render_to_string('militares/ensino/turmas/criar_modal.html', {
                        'form': form,
                        'militares': militares,
                        'militares_nao_alunos': militares_nao_alunos,
                        'alunos_disponiveis': alunos_disponiveis,
                        'postos_graduacao': POSTO_GRADUACAO_CHOICES,
                        'instrutores': instrutores,
                        'monitores': monitores,
                    }, request=request)
                    from django.http import HttpResponse
                    return HttpResponse(html)
                else:
                    context = {
                        'form': form,
                        'militares': militares,
                        'militares_nao_alunos': militares_nao_alunos,
                        'alunos_disponiveis': alunos_disponiveis,
                        'postos_graduacao': POSTO_GRADUACAO_CHOICES,
                        'instrutores': instrutores,
                        'monitores': monitores,
                    }
                    return render(request, 'militares/ensino/turmas/criar.html', context)
    else:
        # GET request - sempre retornar o modal
        # Verificar se há curso_id na query string
        curso_id = request.GET.get('curso_id', '')
        edicao_id = request.GET.get('edicao_id', '')
        initial_data = {}
        if curso_id:
            initial_data['curso'] = curso_id
        if edicao_id:
            initial_data['edicao'] = edicao_id
        
        form = TurmaEnsinoForm(initial=initial_data)
        
        # Buscar todos os alunos cadastrados (bombeiros, outras forças e civis)
        alunos_disponiveis = AlunoEnsino.objects.filter(
            Q(situacao='ATIVO') | Q(situacao='CONCLUIDO')
        ).select_related('militar', 'pessoa_externa').order_by('tipo_aluno', 'militar__posto_graduacao', 'nome_outra_forca', 'nome_civil')
        
        # Buscar TODOS os militares ativos (não apenas os que não são alunos)
        # O sistema criará automaticamente como aluno se ainda não for
        # Usar list() para forçar avaliação do queryset e garantir que todos sejam carregados
        militares = list(Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo'))
        
        # Buscar militares que já são alunos (para exibir informação)
        militares_ja_alunos = AlunoEnsino.objects.filter(
            tipo_aluno='BOMBEIRO',
            militar__isnull=False
        ).values_list('militar_id', flat=True)
        
        # Criar um set para verificação rápida se militar já é aluno
        militares_ja_alunos_set = set(militares_ja_alunos)
        
        # Manter variável para compatibilidade com template (mas não usar mais para filtrar)
        # Como militares é uma lista, usar list comprehension
        militares_nao_alunos = [m for m in militares if m.pk not in militares_ja_alunos_set]
        
        # Buscar instrutores e monitores para seleção nas disciplinas
        from militares.models import POSTO_GRADUACAO_CHOICES, InstrutorEnsino, MonitorEnsino
        instrutores = InstrutorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
        monitores = MonitorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
        
        # Criar lista para verificação no template (Django templates funcionam melhor com listas)
        militares_ja_alunos_list = list(militares_ja_alunos)
        
        # Log para debug (remover em produção se necessário)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'Total de militares carregados para criar turma: {len(militares)}')
        logger.info(f'Militares que já são alunos: {len(militares_ja_alunos_list)}')
        logger.info(f'Militares que não são alunos: {len(militares_nao_alunos)}')
        
        context = {
            'form': form,
            'militares': militares,  # TODOS os militares ativos - sem filtro (lista)
            'militares_nao_alunos': militares_nao_alunos,  # Para compatibilidade
            'militares_ja_alunos': militares_ja_alunos_list,  # Lista para verificação no template
            'alunos_disponiveis': alunos_disponiveis,
            'postos_graduacao': POSTO_GRADUACAO_CHOICES,
            'instrutores': instrutores,
            'monitores': monitores,
        }
        
        if is_ajax:
            from django.template.loader import render_to_string
            html = render_to_string('militares/ensino/turmas/criar_modal.html', context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        else:
            return render(request, 'militares/ensino/turmas/criar.html', context)


@login_required
def detalhes_turma(request, pk):
    """Detalhes completos de uma turma"""
    from datetime import datetime, timedelta
    
    turma = get_object_or_404(
        TurmaEnsino.objects.select_related(
            'curso',
            'supervisor_curso',
            'coordenador_curso',
            'supervisor_turma',
            'coordenador_turma'
        ),
        pk=pk
    )
    if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
        messages.error(request, 'Acesso negado. Você só pode acessar turmas em que está vinculado.')
        return redirect('militares:ensino_turmas_listar')
    
    # Alunos (militares ou externos)
    alunos = AlunoEnsino.objects.filter(turma=turma).select_related('militar', 'pessoa_externa')
    try:
        ordem_hierarquica = [codigo for codigo, _nome in POSTO_GRADUACAO_CHOICES]
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(999),
            output_field=IntegerField(),
        )
        alunos = alunos.annotate(hierarquia_ordem=hierarquia_ordem).order_by(
            'hierarquia_ordem',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'pessoa_externa__nome_completo',
            'nome_civil',
            'nome_outra_forca'
        )
    except Exception:
        alunos = alunos.order_by('militar__nome_completo', 'pessoa_externa__nome_completo', 'nome_civil', 'nome_outra_forca')
    
    # Aulas
    aulas = AulaEnsino.objects.filter(turma=turma).select_related('disciplina', 'instrutor')
    
    # Avaliações
    avaliacoes = AvaliacaoEnsino.objects.filter(turma=turma).select_related('disciplina').order_by('disciplina', 'data_avaliacao')
    
    # Escalas
    escalas = EscalaInstrucao.objects.filter(turma=turma).select_related('instrutor', 'disciplina')
    
    # Quadros de Trabalho Semanal
    from militares.models import QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal
    from django.db.models import Prefetch
    quadros_trabalho_semanal = QuadroTrabalhoSemanal.objects.filter(
        turma=turma
    ).select_related('turma', 'turma__curso').prefetch_related(
        Prefetch('aulas', queryset=AulaQuadroTrabalhoSemanal.objects.select_related('disciplina', 'instrutor_militar', 'instrutor_externo').order_by('dia_semana', 'hora_inicio', 'ordem')),
        'assinaturas__assinado_por'
    ).order_by(
        '-data_inicio_semana', 
        '-numero_quadro',
        '-id'
    )
    
    # Estatísticas
    total_alunos = alunos.count()
    alunos_ativos = alunos.filter(situacao='ATIVO').count()
    
    # Definir listas de alunos (precisa ser antes do cálculo de frequências)
    alunos_ativos_list = alunos.filter(situacao='ATIVO').order_by('matricula')  # Para cálculos de notas (apenas ativos)
    alunos_todos_list = alunos.order_by('matricula')  # Para resultado final (todos os alunos)
    
    # Calcular frequências conforme ITE (frequência mínima de 75%)
    from militares.models import FrequenciaAula
    frequencias_turma = FrequenciaAula.objects.filter(aula__turma=turma).select_related('aluno', 'aula', 'aula__disciplina')
    
    # Calcular frequência por aluno (conforme ITE)
    # IMPORTANTE: Contar baseado em horas-aula, não em registros
    # Se em um dia há 2 horas-aula, são 2 aulas
    frequencias_por_aluno = {}
    for aluno in alunos_ativos_list:
        frequencias_aluno = frequencias_turma.filter(aluno=aluno).select_related('aula')
        
        # Calcular horas-aula totais e por tipo de presença
        total_horas_aula_aluno = 0.0
        horas_presentes_aluno = 0.0
        horas_faltas_aluno = 0.0
        horas_faltas_justificadas_aluno = 0.0
        horas_atrasos_aluno = 0.0
        horas_saidas_antecipadas_aluno = 0.0
        
        for freq in frequencias_aluno:
            if freq.aula and freq.aula.hora_inicio and freq.aula.hora_fim:
                # Calcular duração em minutos
                inicio = datetime.combine(freq.aula.data_aula, freq.aula.hora_inicio)
                fim = datetime.combine(freq.aula.data_aula, freq.aula.hora_fim)
                # Se hora_fim for anterior a hora_inicio, assumir que é no dia seguinte
                if fim < inicio:
                    fim += timedelta(days=1)
                duracao_minutos = (fim - inicio).total_seconds() / 60
                # Converter para horas-aula (1 hora-aula = 45 minutos)
                horas_aula = duracao_minutos / 45.0
                
                total_horas_aula_aluno += horas_aula
                
                # Contar horas-aula por tipo de presença
                if freq.presenca == 'PRESENTE':
                    horas_presentes_aluno += horas_aula
                elif freq.presenca == 'FALTA':
                    horas_faltas_aluno += horas_aula
                elif freq.presenca == 'FALTA_JUSTIFICADA':
                    horas_faltas_justificadas_aluno += horas_aula
                elif freq.presenca == 'ATRASO':
                    horas_atrasos_aluno += horas_aula
                elif freq.presenca == 'SAIDA_ANTECIPADA':
                    horas_saidas_antecipadas_aluno += horas_aula
        
        # Calcular percentual de frequência conforme ITE
        # Frequência = (horas presentes / total de horas-aula) * 100
        # Frequência mínima exigida: 75% (conforme ITE)
        percentual_frequencia = (horas_presentes_aluno / total_horas_aula_aluno * 100) if total_horas_aula_aluno > 0 else 0
        frequencia_minima_ite = 75.0  # ITE define frequência mínima de 75%
        frequencia_aprovada = percentual_frequencia >= frequencia_minima_ite
        
        frequencias_por_aluno[aluno.pk] = {
            'total_aulas': round(total_horas_aula_aluno, 2),  # Total de horas-aula
            'total_registros': frequencias_aluno.count(),  # Total de registros (para referência)
            'presentes': round(horas_presentes_aluno, 2),  # Horas-aula presentes
            'faltas': round(horas_faltas_aluno, 2),  # Horas-aula faltas
            'faltas_justificadas': round(horas_faltas_justificadas_aluno, 2),  # Horas-aula faltas justificadas
            'atrasos': round(horas_atrasos_aluno, 2),  # Horas-aula atrasos
            'saidas_antecipadas': round(horas_saidas_antecipadas_aluno, 2),  # Horas-aula saídas antecipadas
            'percentual': round(percentual_frequencia, 2),
            'frequencia_minima_ite': frequencia_minima_ite,
            'aprovado_frequencia': frequencia_aprovada
        }
    
    # Calcular frequência por disciplina (conforme ITE 17.1)
    # Primeiro, buscar todas as disciplinas da turma (através das avaliações ou diretamente)
    disciplinas_turma_freq = set()
    for avaliacao in avaliacoes:
        disciplinas_turma_freq.add(avaliacao.disciplina)
    
    # Se não houver avaliações, buscar disciplinas diretamente da turma
    if not disciplinas_turma_freq:
        disciplinas_turma_freq = set(turma.disciplinas.all())
    
    frequencias_por_disciplina_turma = {}
    for disciplina in disciplinas_turma_freq:
        disciplina_id = disciplina.pk
        frequencias_disciplina = frequencias_turma.filter(aula__disciplina=disciplina)
        
        # Usar carga horária da disciplina como 100% (total de horas-aula programadas)
        # Se a disciplina tem 20h/A, então 20h = 100%
        total_horas_aula_programadas = 0.0
        if disciplina.carga_horaria:
            total_horas_aula_programadas = float(disciplina.carga_horaria)
        else:
            # Fallback: calcular a partir das aulas se não houver carga horária cadastrada
            aulas_disciplina = aulas.filter(disciplina=disciplina)
            for aula in aulas_disciplina:
                if aula.hora_inicio and aula.hora_fim:
                    # Calcular duração em minutos
                    inicio = datetime.combine(aula.data_aula, aula.hora_inicio)
                    fim = datetime.combine(aula.data_aula, aula.hora_fim)
                    # Se hora_fim for anterior a hora_inicio, assumir que é no dia seguinte
                    if fim < inicio:
                        fim += timedelta(days=1)
                    duracao_minutos = (fim - inicio).total_seconds() / 60
                    # Converter para horas-aula (1 hora-aula = 45 minutos)
                    horas_aula = duracao_minutos / 45.0
                    total_horas_aula_programadas += horas_aula
        
        # Calcular estatísticas gerais da disciplina (baseado em horas-aula)
        # Contar horas-aula totais da disciplina
        total_horas_aula_disciplina = 0.0
        for aula in aulas.filter(disciplina=disciplina):
            if aula.hora_inicio and aula.hora_fim:
                inicio = datetime.combine(aula.data_aula, aula.hora_inicio)
                fim = datetime.combine(aula.data_aula, aula.hora_fim)
                if fim < inicio:
                    fim += timedelta(days=1)
                duracao_minutos = (fim - inicio).total_seconds() / 60
                horas_aula = duracao_minutos / 45.0
                total_horas_aula_disciplina += horas_aula
        total_aulas_disciplina = round(total_horas_aula_disciplina, 2)  # Total de horas-aula
        
        # Calcular frequência por aluno nesta disciplina (conforme ITE 17.1)
        # IMPORTANTE: Contar baseado em horas-aula, não em registros
        frequencias_alunos_disciplina = {}
        for aluno in alunos_ativos_list:
            frequencias_aluno_disc = frequencias_disciplina.filter(aluno=aluno).select_related('aula')
            
            # Calcular horas-aula totais e por tipo de presença
            total_horas_aula_aluno_disc = 0.0
            horas_presentes_aluno_disc = 0.0
            horas_faltas_aluno_disc = 0.0
            horas_faltas_justificadas_aluno_disc = 0.0
            horas_perdidas_nao_justificadas = 0.0
            horas_perdidas_justificadas = 0.0
            
            for freq in frequencias_aluno_disc:
                if freq.aula and freq.aula.hora_inicio and freq.aula.hora_fim:
                    # Calcular duração em minutos
                    inicio = datetime.combine(freq.aula.data_aula, freq.aula.hora_inicio)
                    fim = datetime.combine(freq.aula.data_aula, freq.aula.hora_fim)
                    # Se hora_fim for anterior a hora_inicio, assumir que é no dia seguinte
                    if fim < inicio:
                        fim += timedelta(days=1)
                    duracao_minutos = (fim - inicio).total_seconds() / 60
                    # Converter para horas-aula (1 hora-aula = 45 minutos)
                    horas_aula = duracao_minutos / 45.0
                    
                    total_horas_aula_aluno_disc += horas_aula
                    
                    # Contar horas-aula por tipo de presença
                    if freq.presenca == 'PRESENTE':
                        horas_presentes_aluno_disc += horas_aula
                    elif freq.presenca == 'FALTA':
                        horas_faltas_aluno_disc += horas_aula
                        horas_perdidas_nao_justificadas += horas_aula
                    elif freq.presenca == 'FALTA_JUSTIFICADA':
                        horas_faltas_justificadas_aluno_disc += horas_aula
                        horas_perdidas_justificadas += horas_aula
                    # ATRASO e SAIDA_ANTECIPADA são ignorados no cálculo de horas perdidas
            
            total_aulas_aluno_disc = round(total_horas_aula_aluno_disc, 2)  # Total de horas-aula
            presentes_aluno_disc = round(horas_presentes_aluno_disc, 2)  # Horas-aula presentes
            faltas_aluno_disc = round(horas_faltas_aluno_disc, 2)  # Horas-aula faltas
            faltas_justificadas_aluno_disc = round(horas_faltas_justificadas_aluno_disc, 2)  # Horas-aula faltas justificadas
            
            # Calcular percentuais conforme ITE 17.1
            percentual_faltas_nao_justificadas = (horas_perdidas_nao_justificadas / total_horas_aula_programadas * 100) if total_horas_aula_programadas > 0 else 0
            percentual_faltas_justificadas = (horas_perdidas_justificadas / total_horas_aula_programadas * 100) if total_horas_aula_programadas > 0 else 0
            total_faltas_horas = horas_perdidas_nao_justificadas + horas_perdidas_justificadas
            percentual_total_faltas = (total_faltas_horas / total_horas_aula_programadas * 100) if total_horas_aula_programadas > 0 else 0
            
            # Verificar reprovação conforme ITE 17.1
            # 17.1.1. perder mais de 20% por falta não justificada
            # 17.1.2. perder mais de 30% por falta justificada
            # 17.1.3. ultrapassar 40% do somatório de faltas justificadas e não justificadas
            reprovado_por_frequencia = (
                percentual_faltas_nao_justificadas > 20.0 or  # 17.1.1
                percentual_faltas_justificadas > 30.0 or  # 17.1.2
                percentual_total_faltas > 40.0  # 17.1.3
            )
            
            # Calcular percentual de frequência (presentes)
            # Usar horas presentes calculadas acima, não subtrair do total programado
            percentual_freq_disc = (horas_presentes_aluno_disc / total_horas_aula_programadas * 100) if total_horas_aula_programadas > 0 else 0
            
            frequencias_alunos_disciplina[aluno.pk] = {
                'total_aulas': total_aulas_aluno_disc,  # Total de horas-aula do aluno
                'total_horas_aula_programadas': round(total_horas_aula_programadas, 2),
                'horas_presentes': round(horas_presentes_aluno_disc, 2),
                'horas_perdidas_nao_justificadas': round(horas_perdidas_nao_justificadas, 2),
                'horas_perdidas_justificadas': round(horas_perdidas_justificadas, 2),
                'total_horas_faltas': round(total_faltas_horas, 2),
                'presentes': presentes_aluno_disc,  # Horas-aula presentes
                'faltas': faltas_aluno_disc,  # Horas-aula faltas
                'faltas_justificadas': faltas_justificadas_aluno_disc,  # Horas-aula faltas justificadas
                'percentual': round(percentual_freq_disc, 2),
                'percentual_faltas_nao_justificadas': round(percentual_faltas_nao_justificadas, 2),
                'percentual_faltas_justificadas': round(percentual_faltas_justificadas, 2),
                'percentual_total_faltas': round(percentual_total_faltas, 2),
                'aprovado_frequencia': not reprovado_por_frequencia,
                'reprovado_por_frequencia': reprovado_por_frequencia,
                'motivo_reprovacao': []
            }
            
            # Adicionar motivos de reprovação
            if percentual_faltas_nao_justificadas > 20.0:
                frequencias_alunos_disciplina[aluno.pk]['motivo_reprovacao'].append(
                    f"Faltas não justificadas: {percentual_faltas_nao_justificadas:.2f}% (limite: 20%)"
                )
            if percentual_faltas_justificadas > 30.0:
                frequencias_alunos_disciplina[aluno.pk]['motivo_reprovacao'].append(
                    f"Faltas justificadas: {percentual_faltas_justificadas:.2f}% (limite: 30%)"
                )
            if percentual_total_faltas > 40.0:
                frequencias_alunos_disciplina[aluno.pk]['motivo_reprovacao'].append(
                    f"Total de faltas: {percentual_total_faltas:.2f}% (limite: 40%)"
                )
        
        frequencias_por_disciplina_turma[disciplina_id] = {
            'disciplina': disciplina,
            'total_aulas': total_aulas_disciplina,
            'total_horas_aula_programadas': round(total_horas_aula_programadas, 2),
            'alunos': frequencias_alunos_disciplina
        }
    
    # Calcular notas por disciplina
    # Estrutura: notas_por_disciplina[disciplina_id][aluno_id] = {'notas': [nota1, nota2, nota3, nota4], 'media_final': X, 'status': 'APROVADO'|'RECUPERACAO'|'REPROVADO'}
    notas_por_disciplina = {}
    # Nota: alunos_ativos_list e alunos_todos_list já foram definidos acima (antes do cálculo de frequências)
    
    # Buscar todas as disciplinas da turma (através das avaliações ou diretamente)
    disciplinas_turma = set()
    for avaliacao in avaliacoes:
        disciplinas_turma.add(avaliacao.disciplina)
    
    # Se não houver avaliações, buscar disciplinas diretamente da turma
    if not disciplinas_turma:
        disciplinas_turma = set(turma.disciplinas.all())
    
    # Inicializar estrutura para todas as disciplinas da turma
    for disciplina in disciplinas_turma:
        disciplina_id = disciplina.pk
        # Verificar número de avaliações
        verificacao_avaliacoes = disciplina.verificar_numero_avaliacoes(turma=turma)
        
        # Verificar avaliações já criadas para esta disciplina nesta turma
        avaliacoes_criadas = []
        avaliacoes_existentes = AvaliacaoEnsino.objects.filter(
            turma=turma,
            disciplina=disciplina
        ).exclude(tipo='RECUPERACAO').order_by('data_avaliacao', 'id')
        
        # Para cada avaliação existente, determinar sua posição e adicionar à lista
        for avaliacao in avaliacoes_existentes:
            # Determinar posição da avaliação (1ª, 2ª, 3ª, 4ª)
            # Contar avaliações anteriores ordenadas por data
            avaliacoes_anteriores = AvaliacaoEnsino.objects.filter(
                turma=turma,
                disciplina=disciplina
            ).exclude(tipo='RECUPERACAO').filter(
                Q(data_avaliacao__lt=avaliacao.data_avaliacao) |
                Q(data_avaliacao=avaliacao.data_avaliacao, id__lt=avaliacao.id)
            ).count()
            
            posicao = avaliacoes_anteriores + 1
            if posicao <= 4 and posicao not in avaliacoes_criadas:
                avaliacoes_criadas.append(posicao)
        
        # Verificar se algum aluno tem nota de recuperação nesta disciplina
        tem_nota_recuperacao = False
        # Verificar nas notas já lançadas se há alguma nota de recuperação
        notas_recuperacao = NotaAvaliacao.objects.filter(
            avaliacao__turma=turma,
            avaliacao__disciplina=disciplina,
            avaliacao__tipo='RECUPERACAO'
        ).exists()
        if notas_recuperacao:
            tem_nota_recuperacao = True
        
        notas_por_disciplina[disciplina_id] = {
            'disciplina': disciplina,
            'verificacao_avaliacoes': verificacao_avaliacoes,
            'avaliacoes_criadas': avaliacoes_criadas,  # Lista de posições (1, 2, 3, 4) que já foram criadas
            'tem_nota_recuperacao': tem_nota_recuperacao,  # Indica se algum aluno tem nota de recuperação
            'alunos': {}
        }
        
        # Para cada aluno (ativo e desligado), inicializar estrutura
        # Nota: alunos desligados também podem ter notas e devem aparecer no resultado final
        for aluno in alunos_todos_list:
            aluno_id = aluno.pk
            notas_por_disciplina[disciplina_id]['alunos'][aluno_id] = {
                'aluno': aluno,
                'notas': [None, None, None, None],  # 4 avaliações
                'pesos': [0, 0, 0, 0],
                'nota_recuperacao': None,  # Nota de recuperação (não entra no cálculo da média)
                'media_final': None,
                'status': None
            }
    
    # Buscar todas as notas das avaliações da turma
    notas_avaliacoes = NotaAvaliacao.objects.filter(
        avaliacao__turma=turma
    ).select_related('avaliacao', 'avaliacao__disciplina', 'aluno')
    
    # Preencher notas das avaliações
    for nota_obj in notas_avaliacoes:
        disciplina_id = nota_obj.avaliacao.disciplina.pk
        aluno_id = nota_obj.aluno.pk
        
        if disciplina_id in notas_por_disciplina and aluno_id in notas_por_disciplina[disciplina_id]['alunos']:
            # Se for avaliação de recuperação, armazenar separadamente
            if nota_obj.avaliacao.tipo == 'RECUPERACAO':
                notas_por_disciplina[disciplina_id]['alunos'][aluno_id]['nota_recuperacao'] = nota_obj.nota
                notas_por_disciplina[disciplina_id]['alunos'][aluno_id]['peso_recuperacao'] = nota_obj.avaliacao.peso
            else:
                # Encontrar posição da avaliação (1ª, 2ª, 3ª ou 4ª)
                avaliacoes_disciplina = [a for a in avaliacoes if a.disciplina.pk == disciplina_id and a.tipo != 'RECUPERACAO']
                avaliacoes_disciplina_ordenadas = sorted(avaliacoes_disciplina, key=lambda x: (x.data_avaliacao if x.data_avaliacao else date.min, x.id))
                
                try:
                    posicao = avaliacoes_disciplina_ordenadas.index(nota_obj.avaliacao)
                    if posicao < 4:  # Máximo 4 avaliações
                        notas_por_disciplina[disciplina_id]['alunos'][aluno_id]['notas'][posicao] = nota_obj.nota
                        notas_por_disciplina[disciplina_id]['alunos'][aluno_id]['pesos'][posicao] = nota_obj.avaliacao.peso
                except ValueError:
                    pass
    
    # Calcular média final e status para cada aluno em cada disciplina
    # Primeiro, calcular médias de todos os alunos (sem recuperação)
    for disciplina_id, dados_disciplina in notas_por_disciplina.items():
        disciplina = dados_disciplina['disciplina']
        media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
        
        # Obter número obrigatório de avaliações baseado na carga horária
        numero_avaliacoes_obrigatorio = disciplina.calcular_numero_avaliacoes_obrigatorio()
        
        for aluno_id, dados_aluno in dados_disciplina['alunos'].items():
            notas = dados_aluno['notas']
            pesos = dados_aluno['pesos']
            nota_recuperacao = dados_aluno.get('nota_recuperacao')
            
            # Calcular MGM (Média Geral de Matéria) conforme ITE 18.2.1
            # REGRAS:
            # 1. Se houver nota de recuperação: MGM = nota de recuperação (independente de ter sido aprovado ou reprovado na recuperação)
            # 2. Se não houver nota de recuperação e tiver todas as notas obrigatórias: MGM = média aritmética das VCs obrigatórias
            #    (mesmo que seja reprovado direto, a MGM é calculada para entrar na média final do curso)
            if nota_recuperacao is not None:
                # Se houver nota de recuperação, MGM = nota de recuperação
                # (mesmo que seja reprovado na recuperação, a MGM é a nota da recuperação)
                nota_recuperacao_float = float(nota_recuperacao)
                dados_aluno['mgm'] = round(nota_recuperacao_float, 2)
            else:
                # Não tem nota de recuperação: MGM = média aritmética das VCs obrigatórias
                # Calcular média apenas com as avaliações obrigatórias (1ª, 2ª, 3ª ou 4ª conforme carga horária)
                # A MGM só é calculada quando tem TODAS as notas obrigatórias
                # IMPORTANTE: Mesmo que seja reprovado direto, a MGM é calculada para entrar na média final do curso
                verificacoes_obrigatorias = []
                for i in range(numero_avaliacoes_obrigatorio):
                    if notas[i] is not None:
                        verificacoes_obrigatorias.append(float(notas[i]))
                
                if len(verificacoes_obrigatorias) == numero_avaliacoes_obrigatorio:
                    # Todas as avaliações obrigatórias têm nota - calcular MGM
                    # Mesmo que seja reprovado direto, calcular a MGM para entrar na média final do curso
                    mgm = sum(verificacoes_obrigatorias) / len(verificacoes_obrigatorias)
                    dados_aluno['mgm'] = round(mgm, 2)
                else:
                    # Ainda não tem todas as notas obrigatórias - MGM será calculada depois ou na recuperação
                    dados_aluno['mgm'] = None
            
            # Se não houver nota de recuperação, calcular média aritmética simples das VCs obrigatórias
            # Média Final = média aritmética das verificações obrigatórias com notas
            # IMPORTANTE: A média final é calculada apenas com as notas que já foram lançadas
            # Se tem 1 avaliação obrigatória e já tem a nota da 1ª, a média é a nota da 1ª
            # Se tem 2 e já tem as 2 notas, a média é (1ª + 2ª) / 2
            # Se tem 3 e já tem as 3 notas, a média é (1ª + 2ª + 3ª) / 3
            # Se tem 4 e já tem as 4 notas, a média é (1ª + 2ª + 3ª + 4ª) / 4
            if nota_recuperacao is None:
                # Calcular média aritmética simples apenas das verificações obrigatórias que já têm nota
                verificacoes_obrigatorias_com_notas = []
                for i in range(numero_avaliacoes_obrigatorio):
                    if notas[i] is not None:
                        verificacoes_obrigatorias_com_notas.append(float(notas[i]))
                
                if verificacoes_obrigatorias_com_notas:
                    # Calcular média apenas com as avaliações obrigatórias que já têm nota
                    # Se tem 1 avaliação obrigatória e já tem a nota da 1ª, a média é a nota da 1ª
                    # Se tem 2 e já tem as 2 notas, a média é (1ª + 2ª) / 2
                    # E assim por diante
                    media_final = sum(verificacoes_obrigatorias_com_notas) / len(verificacoes_obrigatorias_com_notas)
                    dados_aluno['media_final'] = round(media_final, 2)
                else:
                    # Ainda não tem nenhuma nota das avaliações obrigatórias
                    media_final = None
                    dados_aluno['media_final'] = None
                
                # Determinar status baseado na média final da disciplina
                # Se média final >= média mínima de aprovação → APROVADO (Aprovado Direto)
                # Se média final < média mínima de aprovação → RECUPERACAO (mas ainda não fez recuperação)
                # Se ainda não tem todas as notas obrigatórias, aguardar
                dados_aluno['foi_para_recuperacao'] = False  # Inicializar como False
                if media_final is not None:
                    # Verificar se já tem todas as notas obrigatórias
                    tem_todas_notas_obrigatorias = len(verificacoes_obrigatorias_com_notas) == numero_avaliacoes_obrigatorio
                    
                    if tem_todas_notas_obrigatorias:
                        # Tem todas as notas obrigatórias - pode determinar status
                        if media_final >= media_minima:
                            dados_aluno['status'] = 'APROVADO_DIRETO'
                        else:
                            # Não alcançou a média mínima - reprovado direto (sem recuperação ainda)
                            # Mas se ainda não tem nota de recuperação, pode fazer recuperação depois
                            dados_aluno['status'] = 'REPROVADO_DIRETO'
                            dados_aluno['foi_para_recuperacao'] = True
                    else:
                        # Ainda não tem todas as notas obrigatórias - aguardar
                        # Status será determinado quando tiver todas as notas
                        dados_aluno['status'] = 'EM_ANDAMENTO'
                else:
                    # Sem notas das avaliações obrigatórias, considerar como em andamento
                    dados_aluno['status'] = 'EM_ANDAMENTO'
                
                # Status após recuperação não se aplica (ainda não fez recuperação)
                dados_aluno['status_apos_recuperacao'] = None
    
    # Agora, ajustar médias dos alunos que fizeram recuperação
    # Limitar pela menor média dos aprovados diretos em cada disciplina
    for disciplina_id, dados_disciplina in notas_por_disciplina.items():
        disciplina = dados_disciplina['disciplina']
        media_minima_recuperacao = float(disciplina.media_minima_recuperacao) if disciplina.media_minima_recuperacao else 6.0
        
        # Obter número obrigatório de avaliações baseado na carga horária
        numero_avaliacoes_obrigatorio = disciplina.calcular_numero_avaliacoes_obrigatorio()
        
        # Encontrar a menor média entre os aprovados diretos (sem recuperação) nesta disciplina
        medias_aprovados_diretos = []
        for aluno_id, dados_aluno in dados_disciplina['alunos'].items():
            nota_recuperacao = dados_aluno.get('nota_recuperacao')
            status = dados_aluno.get('status')
            media_final = dados_aluno.get('media_final')
            
            # Se não fez recuperação e está aprovado, incluir na lista
            if nota_recuperacao is None and status == 'APROVADO_DIRETO' and media_final is not None:
                medias_aprovados_diretos.append(media_final)
        
        # Menor média dos aprovados diretos (último aprovado direto)
        menor_media_aprovado_direto = min(medias_aprovados_diretos) if medias_aprovados_diretos else None
        
        # Ajustar médias dos alunos que fizeram recuperação
        for aluno_id, dados_aluno in dados_disciplina['alunos'].items():
            nota_recuperacao = dados_aluno.get('nota_recuperacao')
            notas = dados_aluno['notas']
            
            if nota_recuperacao is not None:
                # Se houver nota de recuperação, MGM = nota de recuperação
                # (conforme regra: MGM de quem ficou em recuperação = nota da recuperação)
                nota_recuperacao_float = float(nota_recuperacao)
                dados_aluno['mgm'] = round(nota_recuperacao_float, 2)
                
                # Se houver nota de recuperação:
                # - A média final continua sendo a média aritmética das VCs obrigatórias (para histórico)
                # - O status inicial continua sendo RECUPERACAO (não mudou)
                # - Adicionar status_apos_recuperacao para indicar se foi aprovado ou reprovado na 2ª época
                
                # Calcular média final das VCs obrigatórias (média aritmética simples das verificações obrigatórias com notas)
                verificacoes_obrigatorias_com_notas = []
                for i in range(numero_avaliacoes_obrigatorio):
                    if notas[i] is not None:
                        verificacoes_obrigatorias_com_notas.append(float(notas[i]))
                
                if verificacoes_obrigatorias_com_notas:
                    media_final = sum(verificacoes_obrigatorias_com_notas) / len(verificacoes_obrigatorias_com_notas)
                    dados_aluno['media_final'] = round(media_final, 2)
                else:
                    media_final = None
                    dados_aluno['media_final'] = None
                
                # Determinar status final consolidado baseado na nota de recuperação
                # Se nota de recuperação >= média mínima de recuperação → APROVADO_2_EPOCA (2ª época)
                # Se nota de recuperação < média mínima de recuperação → REPROVADO
                nota_recuperacao_float = float(nota_recuperacao)
                if nota_recuperacao_float >= media_minima_recuperacao:
                    dados_aluno['status'] = 'APROVADO_2_EPOCA'  # Aprovado na disciplina por recuperação (2ª época)
                else:
                    dados_aluno['status'] = 'REPROVADO'  # Reprovado na recuperação
                
                # Indicar que foi para recuperação (para exibir na coluna Média Final)
                dados_aluno['foi_para_recuperacao'] = True
    
    # Calcular média geral por aluno (média de todas as disciplinas)
    disciplinas_ordenadas = sorted(disciplinas_turma, key=lambda d: d.nome)
    
    alunos_medias_gerais = []
    
    # PRIMEIRO: Calcular MFC de TODOS os alunos
    # Processar TODOS os alunos para garantir que todos apareçam na seção "Média Geral"
    for aluno in alunos_todos_list:
        aluno_id = aluno.pk
        medias_disciplinas = []
        medias_por_disciplina = {}
        tem_recuperacao = False
        
        # Coletar médias de todas as disciplinas para este aluno
        # Se não tiver nota, considerar como zero
        for disciplina in disciplinas_ordenadas:
            disciplina_id = disciplina.pk
            media_disc = 0.0  # Padrão: zero se não tiver nota
            status_disc = None
            
            if disciplina_id in notas_por_disciplina:
                dados_aluno_disc = notas_por_disciplina[disciplina_id]['alunos'].get(aluno_id)
                if dados_aluno_disc:
                    # Para cálculo da MFC na relação final, usar diretamente a MGM já calculada
                    # A MGM já está corretamente calculada:
                    # - Se houver nota de recuperação: MGM = nota de recuperação (independente de ter sido aprovado ou não)
                    # - Se não houver nota de recuperação e tiver todas as notas obrigatórias: MGM = média aritmética das VCs obrigatórias
                    media_disc = dados_aluno_disc.get('mgm')
                    
                    # Se MGM não estiver disponível, tentar calcular agora
                    if media_disc is None:
                        # Verificar se há nota de recuperação
                        nota_recuperacao = dados_aluno_disc.get('nota_recuperacao')
                        if nota_recuperacao is not None:
                            # Se houver nota de recuperação, MGM = nota de recuperação (sempre)
                            media_disc = round(float(nota_recuperacao), 2)
                            dados_aluno_disc['mgm'] = media_disc
                        else:
                            # Se não houver recuperação, calcular MGM como média aritmética das VCs obrigatórias
                            # Obter número obrigatório de avaliações
                            numero_avaliacoes_obrigatorio = disciplina.calcular_numero_avaliacoes_obrigatorio()
                            notas = dados_aluno_disc.get('notas', [None, None, None, None])
                            verificacoes_obrigatorias = []
                            for i in range(numero_avaliacoes_obrigatorio):
                                if notas[i] is not None:
                                    verificacoes_obrigatorias.append(float(notas[i]))
                            
                            # Só calcular MGM se tiver todas as notas obrigatórias
                            if len(verificacoes_obrigatorias) == numero_avaliacoes_obrigatorio:
                                mgm_calculada = sum(verificacoes_obrigatorias) / len(verificacoes_obrigatorias)
                                media_disc = round(mgm_calculada, 2)
                                dados_aluno_disc['mgm'] = media_disc
                            else:
                                # Ainda não tem todas as notas obrigatórias - usar 0.0 por enquanto
                                media_disc = 0.0
                    
                    # Garantir que media_disc seja um número válido
                    if media_disc is None:
                        media_disc = 0.0
                    else:
                        media_disc = float(media_disc)
                    
                    status_disc = dados_aluno_disc.get('status')
                    # Verificar se tem recuperação (status RECUPERACAO ou APROVADO_2_EPOCA)
                    if status_disc in ['RECUPERACAO', 'APROVADO_2_EPOCA']:
                        tem_recuperacao = True
            
            # Sempre incluir a disciplina na média (mesmo que seja zero)
            medias_disciplinas.append(media_disc)
            medias_por_disciplina[disciplina_id] = {
                'media': media_disc,  # 0.0 quando não tiver nota
                'status': status_disc
            }
        
        # Calcular MFC (Média Final do Curso) conforme fórmula: MFC = MGM ÷ Total de disciplinas APROVADAS
        # IMPORTANTE: 
        # 1. Apenas disciplinas aprovadas entram no cálculo da MFC
        # 2. Disciplinas reprovadas (REPROVADO_DIRETO ou REPROVADO) NÃO entram na média final do curso
        # 3. Se o aluno foi desligado, considerar apenas disciplinas cursadas ANTES da data de desligamento
        mgms_disciplinas_aprovadas = []
        disciplinas_aprovadas_count = 0
        
        # Verificar se o aluno foi desligado
        data_desligamento = aluno.data_desligamento if hasattr(aluno, 'data_desligamento') else None
        
        for disciplina in disciplinas_ordenadas:
            disciplina_id = disciplina.pk
            if disciplina_id in notas_por_disciplina:
                dados_aluno_disc = notas_por_disciplina[disciplina_id]['alunos'].get(aluno_id)
                
                # Se o aluno foi desligado, verificar se cursou esta disciplina antes do desligamento
                disciplina_cursada_antes_desligamento = True
                if data_desligamento:
                    # Verificar se há avaliações desta disciplina com data anterior ao desligamento
                    avaliacoes_disciplina = [a for a in avaliacoes if a.disciplina.pk == disciplina_id]
                    if avaliacoes_disciplina:
                        # Verificar se há pelo menos uma avaliação antes do desligamento
                        tem_avaliacao_antes = False
                        for avaliacao in avaliacoes_disciplina:
                            if avaliacao.data_avaliacao and avaliacao.data_avaliacao <= data_desligamento:
                                tem_avaliacao_antes = True
                                break
                        disciplina_cursada_antes_desligamento = tem_avaliacao_antes
                    else:
                        # Se não houver avaliações, considerar que não cursou antes do desligamento
                        disciplina_cursada_antes_desligamento = False
                
                # Só considerar a disciplina se foi cursada antes do desligamento (ou se não foi desligado)
                if disciplina_cursada_antes_desligamento:
                    status_disc = medias_por_disciplina[disciplina_id].get('status')
                    media_disc = medias_por_disciplina[disciplina_id].get('media', 0.0)
                    
                    # Verificar se a disciplina está aprovada
                    # Apenas APROVADO_DIRETO e APROVADO_2_EPOCA entram no cálculo da MFC
                    if status_disc in ['APROVADO_DIRETO', 'APROVADO_2_EPOCA', 'APROVADO']:
                        # Garantir que seja um número válido
                        if media_disc is None:
                            media_disc = 0.0
                        mgms_disciplinas_aprovadas.append(float(media_disc))
                        disciplinas_aprovadas_count += 1
                    # Disciplinas reprovadas (REPROVADO_DIRETO, REPROVADO) NÃO entram no cálculo
        
        # Calcular MFC: soma de todas as MGM das disciplinas aprovadas dividido pelo total de disciplinas aprovadas
        if disciplinas_aprovadas_count > 0:
            media_geral = round(sum(mgms_disciplinas_aprovadas) / disciplinas_aprovadas_count, 3)
        else:
            # Se não tiver nenhuma disciplina aprovada, média geral é 0.0
            media_geral = 0.0
        
        # Verificar se teve recuperação aprovada
        teve_recuperacao_aprovada = False
        reprovado_em_alguma_disciplina = False
        for disciplina in disciplinas_ordenadas:
            disciplina_id = disciplina.pk
            if disciplina_id in medias_por_disciplina:
                status_disc = medias_por_disciplina[disciplina_id].get('status')
                if status_disc == 'APROVADO_2_EPOCA':
                    teve_recuperacao_aprovada = True
                elif status_disc == 'REPROVADO':
                    reprovado_em_alguma_disciplina = True
        
        alunos_medias_gerais.append({
            'aluno': aluno,
            'medias_por_disciplina': medias_por_disciplina,
            'media_geral': media_geral,
            'media_geral_ajustada': None,  # Será calculada depois se necessário
            'tem_recuperacao': tem_recuperacao,
            'teve_recuperacao_aprovada': teve_recuperacao_aprovada,
            'reprovado_em_alguma_disciplina': reprovado_em_alguma_disciplina
        })
    
    # Agora todos os alunos estão em alunos_medias_gerais
    # PRIMEIRO: Separar e classificar alunos aprovados diretos
    alunos_aprovados_diretos_final = []
    for dados_aluno_media in alunos_medias_gerais:
        if not dados_aluno_media['teve_recuperacao_aprovada']:
            # Verificar se todas as disciplinas foram aprovadas sem recuperação
            todas_aprovadas = True
            for disciplina in disciplinas_ordenadas:
                disciplina_id = disciplina.pk
                if disciplina_id in dados_aluno_media['medias_por_disciplina']:
                    status_disc = dados_aluno_media['medias_por_disciplina'][disciplina_id].get('status')
                    if status_disc not in ['APROVADO_DIRETO', 'APROVADO']:
                        todas_aprovadas = False
                        break
            
            if todas_aprovadas:
                alunos_aprovados_diretos_final.append(dados_aluno_media)
    
    # Ordenar aprovados diretos por MFC decrescente (maior primeiro)
    # Usar critérios de desempate: antiguidade e idade
    def get_antiguidade_classificacao(dados):
        aluno = dados['aluno']
        if aluno.militar:
            if aluno.militar.numeracao_antiguidade:
                return aluno.militar.numeracao_antiguidade
            elif aluno.militar.data_promocao_atual:
                return aluno.militar.data_promocao_atual
        return date.max
    
    def get_idade_classificacao(dados):
        aluno = dados['aluno']
        if aluno.militar and aluno.militar.data_nascimento:
            return aluno.militar.data_nascimento
        elif aluno.pessoa_externa and aluno.pessoa_externa.data_nascimento:
            return aluno.pessoa_externa.data_nascimento
        return date.max
    
    alunos_aprovados_diretos_final.sort(
        key=lambda x: (
            -x['media_geral'],  # MFC decrescente
            get_antiguidade_classificacao(x),  # Antiguidade crescente (mais antigo primeiro)
            get_idade_classificacao(x)  # Idade crescente (mais velho primeiro)
        )
    )
    
    # Encontrar a MFC do último aprovado direto (menor MFC entre os aprovados diretos)
    mfc_ultimo_aprovado_direto = None
    if alunos_aprovados_diretos_final:
        # O último na lista ordenada (menor MFC)
        mfc_ultimo_aprovado_direto = alunos_aprovados_diretos_final[-1]['media_geral']
    
    # SEGUNDO: Separar e classificar alunos aprovados em 2ª época
    alunos_aprovados_2epoca_final = []
    for dados_aluno_media in alunos_medias_gerais:
        if dados_aluno_media['teve_recuperacao_aprovada']:
            # Garantir que mfc_calculada seja um número válido
            mfc_calculada = dados_aluno_media['media_geral']
            if mfc_calculada is None:
                mfc_calculada = 0.0
            else:
                mfc_calculada = float(mfc_calculada)
            
            # Se MFC estiver zerada, tentar recalcular
            if mfc_calculada == 0.0:
                medias_disc = []
                for disciplina in disciplinas_ordenadas:
                    disciplina_id = disciplina.pk
                    if disciplina_id in dados_aluno_media['medias_por_disciplina']:
                        media_disc = dados_aluno_media['medias_por_disciplina'][disciplina_id].get('media', 0.0)
                        if media_disc is not None:
                            medias_disc.append(float(media_disc))
                        else:
                            medias_disc.append(0.0)
                    else:
                        medias_disc.append(0.0)
                
                if medias_disc and len(disciplinas_ordenadas) > 0:
                    mfc_recalculada = sum(medias_disc) / len(disciplinas_ordenadas)
                    if mfc_recalculada > 0:
                        mfc_calculada = mfc_recalculada
                        dados_aluno_media['media_geral'] = round(mfc_calculada, 3)
            
            alunos_aprovados_2epoca_final.append({
                'dados': dados_aluno_media,
                'mfc_calculada': mfc_calculada
            })
    
    # Ordenar alunos aprovados em 2ª época por MFC calculada decrescente (maior primeiro)
    alunos_aprovados_2epoca_final.sort(
        key=lambda x: (
            -x['mfc_calculada'],  # MFC calculada decrescente
            get_antiguidade_classificacao(x['dados']),  # Antiguidade crescente
            get_idade_classificacao(x['dados'])  # Idade crescente
        )
    )
    
    # Aplicar ajuste sequencial aos aprovados em 2ª época
    # Se o último aprovado direto tem MFC 6.00:
    #   1º aprovado 2ª época: 6.00 - 0.01 = 5.99
    #   2º aprovado 2ª época: 6.00 - 0.02 = 5.98
    #   3º aprovado 2ª época: 6.00 - 0.03 = 5.97
    # E assim por diante
    if mfc_ultimo_aprovado_direto is not None:
        epsilon = Decimal('0.01')
        mfc_ultimo_aprovado_direto_decimal = Decimal(str(mfc_ultimo_aprovado_direto))
        
        for indice, item in enumerate(alunos_aprovados_2epoca_final):
            dados_aluno_media = item['dados']
            mfc_calculada = Decimal(str(item['mfc_calculada']))
            
            # Calcular ajuste sequencial: 0.01 para o primeiro, 0.02 para o segundo, etc.
            ajuste_sequencial = epsilon * (indice + 1)  # 0.01, 0.02, 0.03, ...
            
            # MFC ajustada = MFC último aprovado direto - ajuste sequencial
            # Mas nunca pode ser maior que a MFC calculada do aluno
            mfc_ajustada = min(
                mfc_calculada,  # MFC calculada do aluno
                mfc_ultimo_aprovado_direto_decimal - ajuste_sequencial  # Limite baseado no último aprovado direto
            )
            
            # Garantir que não seja negativa
            if mfc_ajustada < 0:
                mfc_ajustada = Decimal('0.00')
            
            # Atualizar a média geral ajustada
            dados_aluno_media['media_geral_ajustada'] = round(float(mfc_ajustada), 3)
            # Atualizar também a media_geral para exibição e ordenação
            dados_aluno_media['media_geral'] = round(float(mfc_ajustada), 3)
    else:
        # Se não houver aprovados diretos, não aplicar ajuste
        for item in alunos_aprovados_2epoca_final:
            dados_aluno_media = item['dados']
            mfc_calculada = item['mfc_calculada']
            dados_aluno_media['media_geral_ajustada'] = round(float(mfc_calculada), 3)
    
    # Reordenar alunos_medias_gerais para exibição final
    # Primeiro os aprovados diretos (já ordenados), depois os aprovados em 2ª época (já ordenados e ajustados), depois os reprovados
    alunos_medias_gerais_final = []
    
    # Identificar IDs dos alunos já incluídos (aprovados diretos e 2ª época)
    alunos_incluidos_ids = set()
    for dados in alunos_aprovados_diretos_final:
        alunos_incluidos_ids.add(dados['aluno'].pk)
        alunos_medias_gerais_final.append(dados)
    
    for item in alunos_aprovados_2epoca_final:
        aluno_id = item['dados']['aluno'].pk
        alunos_incluidos_ids.add(aluno_id)
        alunos_medias_gerais_final.append(item['dados'])
    
    # Adicionar apenas alunos que fizeram recuperação e reprovaram
    alunos_recuperacao_reprovados_final = []
    for dados_aluno_media in alunos_medias_gerais:
        aluno_id = dados_aluno_media['aluno'].pk
        if aluno_id not in alunos_incluidos_ids:
            # Verificar se este aluno fez recuperação e reprovou
            fez_recuperacao_e_reprovou = False
            
            # Verificar nas disciplinas se tem nota de recuperação e reprovou
            for disciplina in disciplinas_ordenadas:
                disciplina_id = disciplina.pk
                if disciplina_id in notas_por_disciplina:
                    dados_aluno_disc = notas_por_disciplina[disciplina_id]['alunos'].get(aluno_id)
                    if dados_aluno_disc:
                        nota_recuperacao = dados_aluno_disc.get('nota_recuperacao')
                        status_disc = dados_aluno_disc.get('status')
                        
                        # Se tem nota de recuperação, o aluno fez recuperação
                        if nota_recuperacao is not None:
                            # Verificar se reprovou: status REPROVADO ou nota abaixo da média mínima
                            media_minima_recuperacao_disc = float(disciplina.media_minima_recuperacao) if disciplina.media_minima_recuperacao else 6.0
                            if status_disc == 'REPROVADO' or float(nota_recuperacao) < media_minima_recuperacao_disc:
                                fez_recuperacao_e_reprovou = True
                                break
            
            # Se fez recuperação e reprovou, incluir na lista
            if fez_recuperacao_e_reprovou:
                # Garantir que mfc_calculada seja um número válido
                mfc_calculada = dados_aluno_media['media_geral']
                if mfc_calculada is None:
                    mfc_calculada = 0.0
                else:
                    mfc_calculada = float(mfc_calculada)
                
                # Se MFC estiver zerada, tentar recalcular
                if mfc_calculada == 0.0:
                    medias_disc = []
                    for disciplina in disciplinas_ordenadas:
                        disciplina_id = disciplina.pk
                        if disciplina_id in dados_aluno_media['medias_por_disciplina']:
                            media_disc = dados_aluno_media['medias_por_disciplina'][disciplina_id].get('media', 0.0)
                            if media_disc is not None:
                                medias_disc.append(float(media_disc))
                            else:
                                medias_disc.append(0.0)
                        else:
                            medias_disc.append(0.0)
                    
                    if medias_disc and len(disciplinas_ordenadas) > 0:
                        mfc_recalculada = sum(medias_disc) / len(disciplinas_ordenadas)
                        if mfc_recalculada > 0:
                            mfc_calculada = mfc_recalculada
                            dados_aluno_media['media_geral'] = round(mfc_calculada, 3)
                
                alunos_recuperacao_reprovados_final.append(dados_aluno_media)
    
    # Ordenar alunos que fizeram recuperação e reprovaram por MFC decrescente
    alunos_recuperacao_reprovados_final.sort(
        key=lambda x: (
            -(x['media_geral'] if x['media_geral'] is not None else 0),  # MFC decrescente
            get_antiguidade_classificacao(x),  # Antiguidade crescente
            get_idade_classificacao(x)  # Idade crescente
        )
    )
    
    # Adicionar alunos que fizeram recuperação e reprovaram por último
    for dados in alunos_recuperacao_reprovados_final:
        alunos_medias_gerais_final.append(dados)
    
    # Substituir a lista original
    alunos_medias_gerais = alunos_medias_gerais_final
    
    # Código antigo removido - o ajuste sequencial já foi aplicado acima
    # Agora os alunos estão ordenados: primeiro aprovados diretos, depois aprovados em 2ª época
    
    # Ordenar conforme ITE 18.3:
    # a) Aprovados Direto: primeiro, ordenados por MFC decrescente
    # b) Aprovados com Recuperação: depois, ordenados por MFC ajustada decrescente (maior primeiro)
    # Alunos com média zero (sem notas) aparecem por último
    # Desempate: 1º critério = antiguidade, 2º critério = idade (mais velho fica na frente)
    def get_antiguidade_desempate(aluno):
        """Retorna critério de antiguidade para desempate"""
        if aluno.militar:
            # Para militares: usar numeração de antiguidade (menor = mais antigo) ou data de promoção (mais antiga = menor data)
            if aluno.militar.numeracao_antiguidade is not None:
                # Menor numeração = mais antigo = fica na frente
                return aluno.militar.numeracao_antiguidade
            elif aluno.militar.data_promocao_atual:
                # Data mais antiga = menor valor = fica na frente
                return aluno.militar.data_promocao_atual
            else:
                return date.max  # Sem dados de antiguidade, fica por último
        else:
            # Para pessoas externas: usar matrícula ou ID como fallback
            return 999999
    
    def get_idade_desempate(aluno):
        """Retorna data de nascimento para desempate por idade (mais velho = data mais antiga = menor valor)"""
        if aluno.militar and aluno.militar.data_nascimento:
            # Data mais antiga = mais velho = menor valor = fica na frente
            return aluno.militar.data_nascimento
        elif aluno.pessoa_externa and hasattr(aluno.pessoa_externa, 'data_nascimento') and aluno.pessoa_externa.data_nascimento:
            return aluno.pessoa_externa.data_nascimento
        else:
            return date.max  # Sem data de nascimento, fica por último
    
    # Ordenar conforme ITE 18.3:
    # a) Aprovados Direto: primeiro, ordenados por MFC decrescente
    # b) Aprovados com Recuperação: depois, ordenados por MFC ajustada decrescente (maior primeiro)
    # c) Alunos que reprovaram em alguma disciplina: por último, ordenados por MFC decrescente
    # Alunos com média zero (sem notas) aparecem por último
    # Desempate: 1º critério = antiguidade, 2º critério = idade (mais velho fica na frente)
    alunos_medias_gerais.sort(key=lambda x: (
        x['media_geral'] == 0.0,  # Alunos com média zero por último (True)
        x.get('reprovado_em_alguma_disciplina', False),  # Alunos reprovados em alguma disciplina por último
        x['teve_recuperacao_aprovada'],  # Dentro dos com média: sem recuperação primeiro (False), com recuperação depois (True)
        -x['media_geral'],  # Negativo para ordem decrescente (maior primeiro) - usa MFC ou MFC ajustada conforme o caso
        get_antiguidade_desempate(x['aluno']),  # 1º critério de desempate: antiguidade (menor = mais antigo)
        get_idade_desempate(x['aluno'])  # 2º critério de desempate: idade (data nascimento mais antiga = mais velho)
    ))
    
    # Preparar dados de recuperações para o acordeon
    # Incluir apenas alunos que REALMENTE fizeram recuperação (têm nota de recuperação ou foram para recuperação)
    alunos_recuperacao = []
    for disciplina_id, dados_disciplina in notas_por_disciplina.items():
        disciplina = dados_disciplina['disciplina']
        media_minima_disciplina = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
        # Usar média mínima de recuperação da disciplina
        media_minima_recuperacao_disc = float(disciplina.media_minima_recuperacao) if disciplina.media_minima_recuperacao else 6.0
        
        for aluno_id, dados_aluno in dados_disciplina['alunos'].items():
            nota_recuperacao = dados_aluno.get('nota_recuperacao')
            status_disc = dados_aluno.get('status')
            foi_para_recuperacao = dados_aluno.get('foi_para_recuperacao', False)
            
            # Só incluir se o aluno TEM NOTA DE RECUPERAÇÃO INSERIDA
            if nota_recuperacao is None:
                continue  # Pular alunos sem nota de recuperação
            
            aluno = dados_aluno['aluno']
            
            # Verificar se o aluno está ativo
            if aluno.situacao != 'ATIVO':
                continue  # Pular alunos não ativos
            
            media_final = dados_aluno.get('media_final')
            
            # Determinar status após recuperação
            status_apos_recuperacao = None
            if float(nota_recuperacao) >= media_minima_recuperacao_disc:
                status_apos_recuperacao = 'APROVADO_2_EPOCA'
            else:
                status_apos_recuperacao = 'REPROVADO'
            
            alunos_recuperacao.append({
                'aluno': aluno,
                'disciplina': disciplina,
                'media_final': media_final,
                'nota_recuperacao': nota_recuperacao,
                'media_minima_disciplina': media_minima_disciplina,
                'media_minima_recuperacao': media_minima_recuperacao_disc,  # Média mínima da disciplina para recuperação
                'status_apos_recuperacao': status_apos_recuperacao
            })
    
    # Ordenar recuperações por disciplina e depois por aluno
    alunos_recuperacao.sort(key=lambda x: (x['disciplina'].nome, x['aluno'].get_nome_completo() if hasattr(x['aluno'], 'get_nome_completo') else str(x['aluno'])))
    
    # Coletar IDs dos alunos que fizeram recuperação (para uso em outras seções)
    alunos_com_recuperacao_ids = set()
    for rec in alunos_recuperacao:
        alunos_com_recuperacao_ids.add(rec['aluno'].pk)
    
    # NÃO filtrar a lista principal de alunos - mostrar todos os alunos da turma
    # O filtro de recuperação será aplicado apenas nas seções específicas de recuperação
    
    # Recalcular estatísticas (todos os alunos)
    total_alunos = alunos.count()
    alunos_ativos = alunos.filter(situacao='ATIVO').count()
    
    # Agrupar recuperações por aluno para o acordeon (formato similar à média geral)
    recuperacoes_por_aluno_dict = {}
    disciplinas_com_recuperacao = set()
    
    for rec in alunos_recuperacao:
        aluno_id = rec['aluno'].pk
        disciplina_id = rec['disciplina'].pk
        disciplinas_com_recuperacao.add(rec['disciplina'])
        
        if aluno_id not in recuperacoes_por_aluno_dict:
            recuperacoes_por_aluno_dict[aluno_id] = {
                'aluno': rec['aluno'],
                'recuperacoes_por_disciplina': {}
            }
        
        recuperacoes_por_aluno_dict[aluno_id]['recuperacoes_por_disciplina'][disciplina_id] = rec
    
    # Ordenar disciplinas com recuperação
    disciplinas_recuperacao_ordenadas = sorted(disciplinas_com_recuperacao, key=lambda d: d.nome)
    
    # Preparar lista de alunos com recuperações (formato similar à média geral)
    # Apenas alunos ATIVOS e que TÊM NOTA DE RECUPERAÇÃO INSERIDA
    recuperacoes_por_aluno_lista = []
    for aluno_id, dados_aluno in recuperacoes_por_aluno_dict.items():
        aluno = dados_aluno['aluno']
        
        # Verificar se o aluno está ativo
        if aluno.situacao != 'ATIVO':
            continue  # Pular alunos não ativos
        
        # Verificar se o aluno tem pelo menos uma nota de recuperação inserida
        tem_nota_recuperacao = False
        notas_recuperacao_aluno = []
        for disciplina_id, rec in dados_aluno['recuperacoes_por_disciplina'].items():
            nota_recuperacao = rec.get('nota_recuperacao')
            if nota_recuperacao is not None:
                tem_nota_recuperacao = True
                notas_recuperacao_aluno.append(float(nota_recuperacao))
        
        # Só adicionar se tiver pelo menos uma nota de recuperação inserida
        if not tem_nota_recuperacao:
            continue  # Pular alunos sem nota de recuperação
        
        # Calcular média das recuperações
        media_recuperacoes_aluno = None
        if notas_recuperacao_aluno:
            media_recuperacoes_aluno = round(sum(notas_recuperacao_aluno) / len(notas_recuperacao_aluno), 2)
        
        recuperacoes_por_aluno_lista.append({
            'aluno': dados_aluno['aluno'],
            'recuperacoes_por_disciplina': dados_aluno['recuperacoes_por_disciplina'],
            'media_recuperacoes': media_recuperacoes_aluno
        })
    
    # Ordenar alunos por nome
    def get_nome_aluno_para_ordenacao(aluno):
        if aluno.militar:
            return aluno.militar.nome_completo
        elif aluno.pessoa_externa:
            return aluno.pessoa_externa.get_nome_completo()
        elif aluno.nome_outra_forca:
            return aluno.nome_outra_forca
        elif aluno.nome_civil:
            return aluno.nome_civil
        else:
            return str(aluno)
    
    recuperacoes_por_aluno_lista.sort(key=lambda x: get_nome_aluno_para_ordenacao(x['aluno']))
    
    # Preparar resultado final da turma (TODOS os alunos, incluindo desligados)
    resultado_final_turma = []
    total_aprovados_diretos = 0
    total_aprovados_2epoca = 0
    total_recuperacao = 0  # Alunos que estão em recuperação (sem nota ainda)
    total_reprovados = 0
    total_sem_notas = 0
    
    for aluno in alunos_todos_list:
        aluno_id = aluno.pk
        disciplinas_aprovadas = 0
        disciplinas_aprovadas_por_media = 0  # Mantido para compatibilidade, mas não será mais usado
        disciplinas_recuperacao = 0  # Contar apenas disciplinas com nota de recuperação (2ª época)
        disciplinas_reprovadas = 0
        disciplinas_sem_notas = 0
        status_final = None
        
        # Contar status por disciplina
        for disciplina in disciplinas_ordenadas:
            disciplina_id = disciplina.pk
            if disciplina_id in notas_por_disciplina:
                dados_aluno_disc = notas_por_disciplina[disciplina_id]['alunos'].get(aluno_id)
                if dados_aluno_disc:
                    status_disc = dados_aluno_disc.get('status')
                    nota_recuperacao = dados_aluno_disc.get('nota_recuperacao')
                    
                    # Se tem nota de recuperação, sempre conta como recuperação (2ª época)
                    # O status final será determinado depois verificando se foi aprovado ou reprovado na recuperação
                    if nota_recuperacao is not None:
                        disciplinas_recuperacao += 1
                    # Se não tem nota de recuperação, verificar status normal
                    elif status_disc in ['APROVADO', 'APROVADO_DIRETO']:
                        # Aprovado direto (sem recuperação)
                        disciplinas_aprovadas += 1
                    elif status_disc == 'APROVADO_2_EPOCA':
                        # Status APROVADO_2_EPOCA mas sem nota de recuperação (não deveria acontecer, mas tratar)
                        # Se chegou aqui, significa que o status foi definido mas a nota não foi encontrada
                        # Contar como recuperação para manter consistência
                        disciplinas_recuperacao += 1
                    elif status_disc == 'RECUPERACAO':
                        # Status RECUPERACAO mas sem nota ainda = não conta como recuperação, conta como reprovada
                        disciplinas_reprovadas += 1
                    elif status_disc == 'REPROVADO':
                        disciplinas_reprovadas += 1
                    else:
                        # Status desconhecido ou None, verificar se tem notas
                        if dados_aluno_disc.get('media_final') is not None:
                            # Tem nota mas status não definido, considerar como reprovado
                            disciplinas_reprovadas += 1
                        else:
                            disciplinas_sem_notas += 1
                else:
                    disciplinas_sem_notas += 1
            else:
                disciplinas_sem_notas += 1
        
        # Verificar se há disciplinas em recuperação e se o aluno foi aprovado na recuperação
        disciplinas_recuperacao_reprovadas = 0
        disciplinas_recuperacao_aprovadas = 0
        disciplinas_recuperacao_sem_nota = 0
        
        # Verificar disciplinas com nota de recuperação (2ª época) e sem nota
        for disciplina in disciplinas_ordenadas:
            disciplina_id = disciplina.pk
            if disciplina_id in notas_por_disciplina:
                dados_aluno_disc = notas_por_disciplina[disciplina_id]['alunos'].get(aluno_id)
                if dados_aluno_disc:
                    status_disc = dados_aluno_disc.get('status')
                    nota_recuperacao = dados_aluno_disc.get('nota_recuperacao')
                    
                    # Se tem nota de recuperação (2ª época), verificar se passou
                    if nota_recuperacao is not None:
                        # Buscar média mínima de recuperação da disciplina
                        media_minima_recuperacao_disc = float(disciplina.media_minima_recuperacao) if disciplina.media_minima_recuperacao else 6.0
                        
                        # Verificar se foi aprovado na 2ª época baseado no status já calculado
                        # O status já foi definido anteriormente baseado na nota de recuperação
                        if status_disc == 'APROVADO_2_EPOCA':
                            # Status já foi definido como aprovado na recuperação (nota >= média mínima)
                            disciplinas_recuperacao_aprovadas += 1
                        elif status_disc == 'REPROVADO':
                            # Status foi definido como reprovado na recuperação (nota < média mínima)
                            disciplinas_recuperacao_reprovadas += 1
                        else:
                            # Fallback: verificar diretamente pela nota se o status não foi definido
                            if float(nota_recuperacao) >= media_minima_recuperacao_disc:
                                disciplinas_recuperacao_aprovadas += 1
                            else:
                                disciplinas_recuperacao_reprovadas += 1
                    # Se status é RECUPERACAO mas não tem nota ainda, conta como sem nota
                    elif status_disc == 'RECUPERACAO':
                        disciplinas_recuperacao_sem_nota += 1
                    # Se status é APROVADO_2_EPOCA mas não tem nota de recuperação, não deveria acontecer
                    # Mas se acontecer, não contar como aprovado (precisa ter nota)
                    elif status_disc == 'APROVADO_2_EPOCA':
                        # Status indica aprovado mas não tem nota - não contar (inconsistência)
                        pass
        
        # Determinar status final do aluno
        total_disciplinas = len(disciplinas_ordenadas)
        total_com_notas = disciplinas_aprovadas + disciplinas_recuperacao + disciplinas_reprovadas
        
        # Verificar se aluno reprovou por frequência em alguma disciplina (conforme ITE 17.1)
        # IMPORTANTE: Esta verificação deve ser feita ANTES de qualquer outra, pois reprovação por frequência
        # é independente das notas e deve sobrescrever qualquer outro status
        reprovado_por_frequencia_geral = False
        motivos_reprovacao_frequencia = []
        if frequencias_por_disciplina_turma:
            for disciplina_id, dados_freq_disc in frequencias_por_disciplina_turma.items():
                if aluno.pk in dados_freq_disc.get('alunos', {}):
                    dados_freq_aluno = dados_freq_disc['alunos'][aluno.pk]
                    if dados_freq_aluno.get('reprovado_por_frequencia', False):
                        reprovado_por_frequencia_geral = True
                        disciplina_obj = dados_freq_disc.get('disciplina')
                        disciplina_nome = disciplina_obj.nome if disciplina_obj and hasattr(disciplina_obj, 'nome') else f'Disciplina {disciplina_id}'
                        motivos = dados_freq_aluno.get('motivo_reprovacao', [])
                        if motivos:
                            motivos_reprovacao_frequencia.extend([f"{disciplina_nome}: {motivo}" for motivo in motivos])
                        else:
                            motivos_reprovacao_frequencia.append(f"{disciplina_nome}: Reprovado por frequência")
        
        # Se reprovou por frequência, marcar como REPROVADO independentemente das notas
        # Esta verificação tem prioridade sobre todas as outras
        if reprovado_por_frequencia_geral:
            status_final = 'REPROVADO_POR_FALTAS'
            total_reprovados += 1
        # Se aluno está desligado, sempre considerar reprovado (não pode estar em recuperação)
        elif aluno.situacao == 'DESLIGADO':
            if total_com_notas == 0:
                # Desligado sem notas = reprovado
                status_final = 'REPROVADO'
                total_reprovados += 1
            elif disciplinas_recuperacao > 0:
                # Desligado com disciplinas em recuperação = reprovado
                status_final = 'REPROVADO'
                total_reprovados += 1
            elif disciplinas_reprovadas > 0 or disciplinas_recuperacao_reprovadas > 0:
                # Desligado com reprovações = reprovado
                status_final = 'REPROVADO'
                total_reprovados += 1
            elif disciplinas_aprovadas == total_com_notas and total_com_notas == total_disciplinas:
                # Desligado mas aprovado em todas = reprovado (desligado não pode ser aprovado)
                status_final = 'REPROVADO'
                total_reprovados += 1
            else:
                # Qualquer outro caso de desligado = reprovado
                status_final = 'REPROVADO'
                total_reprovados += 1
        # Se houver disciplinas reprovadas (sem recuperação ou reprovadas na recuperação), o aluno é reprovado
        # Mas só se não reprovou por frequência (já verificado acima)
        elif disciplinas_recuperacao_reprovadas > 0 or disciplinas_reprovadas > 0:
            status_final = 'REPROVADO'
            total_reprovados += 1
        # Se tem disciplinas com nota de recuperação (2ª época), verificar se passou
        elif disciplinas_recuperacao > 0:
            # Aluno tem nota de recuperação (2ª época) - verificar se passou
            # IMPORTANTE: Aluno só é aprovado na 2ª época se foi aprovado em TODAS as recuperações
            if disciplinas_recuperacao_reprovadas > 0:
                # Tem nota de recuperação mas reprovou em alguma = reprovado
                status_final = 'REPROVADO'
                total_reprovados += 1
            elif disciplinas_recuperacao_aprovadas == disciplinas_recuperacao and disciplinas_recuperacao_reprovadas == 0:
                # Todas as recuperações foram aprovadas = Aprovado com 2ª Época
                # Verificar se todas as disciplinas foram aprovadas (diretas + recuperações aprovadas)
                if (disciplinas_aprovadas + disciplinas_recuperacao_aprovadas) == total_disciplinas:
                    status_final = 'APROVADO_2_EPOCA'
                    total_aprovados_2epoca += 1
                else:
                    # Tem recuperações aprovadas mas ainda faltam disciplinas = EM_ANDAMENTO
                    status_final = 'EM_ANDAMENTO'
            else:
                # Tem nota de recuperação mas ainda não foi avaliado = não deve acontecer
                status_final = 'EM_ANDAMENTO'
        elif disciplinas_recuperacao_sem_nota > 0:
            # Ainda em recuperação (sem nota de recuperação lançada) - apenas para alunos ativos
            # Este é o caso que deve aparecer no card "Em Recuperação"
            status_final = 'EM_RECUPERACAO'
            total_recuperacao += 1
        elif disciplinas_aprovadas == total_disciplinas and disciplinas_recuperacao == 0:
            # Todas as disciplinas aprovadas sem recuperação = Aprovado Direto
            status_final = 'APROVADO_DIRETO'
            total_aprovados_diretos += 1
        elif total_com_notas == 0:
            # Se aluno está desligado e não tem notas, considerar reprovado
            if aluno.situacao == 'DESLIGADO':
                status_final = 'REPROVADO'
                total_reprovados += 1
            else:
                status_final = 'SEM_NOTAS'
                total_sem_notas += 1
        else:
            # Se tem todas as disciplinas com notas e nenhuma reprovada, verificar se foi direto ou 2ª época
            if total_com_notas == total_disciplinas:
                # Verificar se teve recuperação
                if disciplinas_recuperacao > 0:
                    # Se teve recuperação, verificar se todas foram aprovadas
                    if disciplinas_recuperacao_aprovadas == disciplinas_recuperacao and disciplinas_recuperacao_reprovadas == 0:
                        # Todas as recuperações foram aprovadas = Aprovado na 2ª Época
                        status_final = 'APROVADO_2_EPOCA'
                        total_aprovados_2epoca += 1
                    else:
                        # Teve recuperação mas reprovou em alguma = Reprovado
                        status_final = 'REPROVADO'
                        total_reprovados += 1
                elif disciplinas_aprovadas == total_disciplinas:
                    # Todas as disciplinas aprovadas sem recuperação = Aprovado Direto
                    status_final = 'APROVADO_DIRETO'
                    total_aprovados_diretos += 1
                else:
                    status_final = 'EM_ANDAMENTO'
            else:
                status_final = 'EM_ANDAMENTO'
        
        # Buscar média geral do aluno
        media_geral_aluno = 0.0  # Padrão: 0.0 em vez de None
        for dados_aluno_media in alunos_medias_gerais:
            # Comparar IDs dos alunos
            aluno_media_id = dados_aluno_media['aluno'].pk if hasattr(dados_aluno_media['aluno'], 'pk') else None
            if aluno_media_id == aluno_id:
                media_geral_aluno = dados_aluno_media.get('media_geral')
                # Garantir que a média seja um número válido (incluindo 0.0)
                if media_geral_aluno is not None:
                    try:
                        media_geral_aluno = float(media_geral_aluno)
                    except (ValueError, TypeError):
                        media_geral_aluno = 0.0
                else:
                    media_geral_aluno = 0.0
                break
        
        # Se não encontrou na lista, calcular agora baseado nas disciplinas usando a mesma lógica
        if media_geral_aluno == 0.0:
            # Verificar se realmente não tem média ou se precisa calcular
            encontrou_media = False
            for dados_aluno_media in alunos_medias_gerais:
                aluno_media_id = dados_aluno_media['aluno'].pk if hasattr(dados_aluno_media['aluno'], 'pk') else None
                if aluno_media_id == aluno_id:
                    encontrou_media = True
                    # Usar a média já calculada
                    media_geral_aluno = dados_aluno_media.get('media_geral', 0.0)
                    if media_geral_aluno is not None:
                        media_geral_aluno = float(media_geral_aluno)
                    else:
                        media_geral_aluno = 0.0
                    break
            
            if not encontrou_media:
                # Calcular MFC usando a mesma lógica de alunos_medias_gerais
                # MFC = média aritmética das MGM de TODAS as disciplinas
                mgms_todas_disciplinas = []
                for disciplina in disciplinas_ordenadas:
                    disciplina_id = disciplina.pk
                    if disciplina_id in notas_por_disciplina:
                        dados_aluno_disc = notas_por_disciplina[disciplina_id]['alunos'].get(aluno_id)
                        if dados_aluno_disc:
                            # Usar MGM se disponível (já calculada corretamente)
                            mgm = dados_aluno_disc.get('mgm')
                            if mgm is not None:
                                mgms_todas_disciplinas.append(float(mgm))
                            else:
                                # Calcular MGM agora seguindo a mesma lógica
                                nota_recuperacao = dados_aluno_disc.get('nota_recuperacao')
                                if nota_recuperacao is not None:
                                    # Se tem recuperação, MGM = nota de recuperação
                                    mgms_todas_disciplinas.append(float(nota_recuperacao))
                                else:
                                    # Se não tem recuperação, MGM = média aritmética das VCs
                                    notas = dados_aluno_disc.get('notas', [None, None, None, None])
                                    verificacoes = [float(n) for n in notas if n is not None]
                                    if verificacoes:
                                        mgm_calc = sum(verificacoes) / len(verificacoes)
                                        mgms_todas_disciplinas.append(mgm_calc)
                                    else:
                                        # Sem notas, usar 0.0
                                        mgms_todas_disciplinas.append(0.0)
                        else:
                            mgms_todas_disciplinas.append(0.0)
                    else:
                        mgms_todas_disciplinas.append(0.0)
                
                # Garantir que temos MGM para todas as disciplinas
                while len(mgms_todas_disciplinas) < len(disciplinas_ordenadas):
                    mgms_todas_disciplinas.append(0.0)
                
                if len(disciplinas_ordenadas) > 0:
                    media_geral_aluno = round(sum(mgms_todas_disciplinas) / len(disciplinas_ordenadas), 3)
                else:
                    media_geral_aluno = 0.0
        
        # Criar item do resultado
        item_resultado = {
            'aluno': aluno,
            'status_final': status_final,
            'media_geral': media_geral_aluno,
            'disciplinas_aprovadas': disciplinas_aprovadas,
            'disciplinas_aprovadas_por_media': 0,  # Removido - não usado mais
            'disciplinas_recuperacao': disciplinas_recuperacao,
            'disciplinas_reprovadas': disciplinas_reprovadas,
            'disciplinas_sem_notas': disciplinas_sem_notas,
            'total_disciplinas': total_disciplinas,
            'reprovado_por_frequencia': reprovado_por_frequencia_geral,
            'motivos_reprovacao_frequencia': motivos_reprovacao_frequencia
        }
        
        # IMPORTANTE: Alunos desligados NÃO entram na lista final (resultado_final_turma)
        # Mas são contados como reprovados para questão de ata
        if aluno.situacao == 'DESLIGADO':
            # Aluno desligado não entra na lista final, mas já foi contado como reprovado acima
            # Não adicionar à lista resultado_final_turma
            pass
        else:
            # Aluno não desligado - adicionar à lista final
            resultado_final_turma.append(item_resultado)
    
    # Ordenar resultado final: aprovados diretos primeiro, depois aprovados 2ª época, depois reprovados
    # Dentro de cada grupo, ordenar por média geral decrescente
    # IMPORTANTE: Alunos desligados não estão nesta lista (foram excluídos acima)
    resultado_final_turma.sort(key=lambda x: (
        x['status_final'] != 'APROVADO_DIRETO',  # Aprovados diretos primeiro
        x['status_final'] != 'APROVADO_2_EPOCA',  # Depois aprovados 2ª época
        x['status_final'] == 'REPROVADO',  # Reprovados por último
        -(float(x['media_geral']) if x['media_geral'] is not None and x['media_geral'] != 0 else 0)  # Ordenar por média decrescente
    ))
    
    # Desligamento automático removido - agora só é feito manualmente
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    context = {
        'turma': turma,
        'alunos': alunos,
        'aulas': aulas,
        'avaliacoes': avaliacoes,
        'escalas': escalas,
        'total_alunos': total_alunos,
        'alunos_ativos': alunos_ativos,
        'notas_por_disciplina': notas_por_disciplina,
        'alunos_medias_gerais': alunos_medias_gerais,
        'disciplinas_ordenadas': disciplinas_ordenadas,
        'alunos_recuperacao': alunos_recuperacao,
        'recuperacoes_por_aluno_lista': recuperacoes_por_aluno_lista,
        'disciplinas_recuperacao_ordenadas': disciplinas_recuperacao_ordenadas,
        'resultado_final_turma': resultado_final_turma,
        'total_aprovados_diretos': total_aprovados_diretos,
        'total_aprovados_2epoca': total_aprovados_2epoca,
        'total_recuperacao': total_recuperacao,
        'total_reprovados': total_reprovados,
        'total_sem_notas': total_sem_notas,
        'quadros_trabalho_semanal': quadros_trabalho_semanal,
        'frequencias_por_aluno': frequencias_por_aluno,
        'frequencias_por_disciplina_turma': frequencias_por_disciplina_turma,
        'frequencia_minima_ite': 75.0,  # Frequência mínima conforme ITE
    }
    
    # Se for requisição AJAX, retornar apenas o conteúdo do modal
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/turmas/detalhes_modal.html', context, request=request)
        from django.http import HttpResponse
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/turmas/detalhes.html', context)


@login_required
def caderneta_frequencia_disciplina(request, turma_id, disciplina_id):
    """Caderneta de frequência da disciplina - similar ao QTS"""
    from militares.models import AlunoEnsino, AulaEnsino, FrequenciaAula
    from django.db.models import Q
    from datetime import datetime, timedelta
    
    turma = get_object_or_404(TurmaEnsino, pk=turma_id)
    if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
        messages.error(request, 'Acesso negado. Você só pode acessar turmas em que está vinculado.')
        return redirect('militares:ensino_turmas_listar')
    disciplina = get_object_or_404(DisciplinaEnsino, pk=disciplina_id)
    
    # Verificar se a disciplina pertence à turma
    if disciplina not in turma.disciplinas.all():
        messages.error(request, 'Esta disciplina não pertence a esta turma.')
        return redirect('militares:ensino_turma_detalhes', pk=turma_id)
    
    # Buscar todos os alunos ativos da turma
    alunos = AlunoEnsino.objects.filter(
        turma=turma,
        situacao='ATIVO'
    ).select_related('militar', 'pessoa_externa')
    try:
        ordem_hierarquica = [codigo for codigo, _nome in POSTO_GRADUACAO_CHOICES]
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(999),
            output_field=IntegerField(),
        )
        alunos = alunos.annotate(hierarquia_ordem=hierarquia_ordem).order_by(
            'hierarquia_ordem',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'pessoa_externa__nome_completo',
            'nome_civil',
            'nome_outra_forca',
            'matricula'
        )
    except Exception:
        alunos = alunos.order_by('militar__nome_completo', 'pessoa_externa__nome_completo', 'nome_civil', 'nome_outra_forca', 'matricula')
    
    # Buscar todas as aulas da disciplina nesta turma, ordenadas por data
    aulas = AulaEnsino.objects.filter(
        turma=turma,
        disciplina=disciplina
    ).order_by('data_aula', 'hora_inicio')
    
    # Processar POST para adicionar nova data/aula ou salvar frequências
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'adicionar_aula':
            # Adicionar nova aula/data
            data_aula_str = request.POST.get('data_aula')
            hora_inicio_str = request.POST.get('hora_inicio', '08:00')
            hora_fim_str = request.POST.get('hora_fim', '09:30')
            horas_aula_str = request.POST.get('horas_aula', '')
            local = request.POST.get('local', 'Sala de Aula')
            tipo_local = request.POST.get('tipo_local', 'SALA')
            conteudo_ministrado = request.POST.get('conteudo_ministrado', '')
            observacoes = request.POST.get('observacoes', '')
            instrutor_id = request.POST.get('instrutor', '')
            
            try:
                data_aula = datetime.strptime(data_aula_str, '%Y-%m-%d').date()
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                
                # Se horas_aula foi informado, calcular hora_fim automaticamente
                if horas_aula_str:
                    try:
                        horas_aula = float(horas_aula_str)
                        if horas_aula > 0:
                            # Converter hora_inicio para datetime para calcular
                            inicio_datetime = datetime.combine(data_aula, hora_inicio)
                            # Adicionar as horas aula (convertidas para minutos)
                            # Cada hora-aula = 45 minutos
                            minutos_aula = horas_aula * 45
                            fim_datetime = inicio_datetime + timedelta(minutes=minutos_aula)
                            hora_fim = fim_datetime.time()
                        else:
                            hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()
                    except (ValueError, TypeError):
                        # Se não conseguir converter horas_aula, usar hora_fim do formulário
                        hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()
                else:
                    hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()
                
                # Validar conteúdo ministrado
                if not conteudo_ministrado or not conteudo_ministrado.strip():
                    messages.error(request, 'O campo Conteúdo Ministrado é obrigatório.')
                    return redirect('militares:ensino_caderneta_frequencia_disciplina', turma_id=turma_id, disciplina_id=disciplina_id)
                
                # Processar instrutor
                instrutor = None
                if instrutor_id:
                    try:
                        from militares.models import Militar
                        instrutor = Militar.objects.get(pk=int(instrutor_id), classificacao='ATIVO')
                    except (Militar.DoesNotExist, ValueError):
                        # Se não encontrar o instrutor, usar o padrão
                        instrutor = request.user.militar if hasattr(request.user, 'militar') else None
                else:
                    # Se não foi informado instrutor, usar o padrão da disciplina ou do usuário
                    if disciplina.instrutor_responsavel_militar:
                        instrutor = disciplina.instrutor_responsavel_militar
                    else:
                        instrutor = request.user.militar if hasattr(request.user, 'militar') else None
                
                # Verificar se já existe aula nesta data
                aula_existente = AulaEnsino.objects.filter(
                    turma=turma,
                    disciplina=disciplina,
                    data_aula=data_aula
                ).first()
                
                if aula_existente:
                    messages.warning(request, f'Já existe uma aula cadastrada para a data {data_aula.strftime("%d/%m/%Y")}.')
                else:
                    # Criar nova aula
                    aula = AulaEnsino.objects.create(
                        turma=turma,
                        disciplina=disciplina,
                        data_aula=data_aula,
                        hora_inicio=hora_inicio,
                        hora_fim=hora_fim,
                        local=local,
                        tipo_local=tipo_local,
                        conteudo_ministrado=conteudo_ministrado,
                        observacoes=observacoes if observacoes else None,
                        instrutor=instrutor
                    )
                    messages.success(request, f'Aula adicionada para {data_aula.strftime("%d/%m/%Y")}.')
                    
            except ValueError as e:
                messages.error(request, f'Erro ao processar data: {str(e)}')
        
        elif action == 'salvar_frequencias':
            # Salvar frequências de todos os alunos para todas as aulas
            aulas_ids = request.POST.getlist('aulas_ids[]')
            
            for aula_id in aulas_ids:
                try:
                    aula = AulaEnsino.objects.get(pk=aula_id, turma=turma, disciplina=disciplina)
                    
                    for aluno in alunos:
                        presenca_key = f'presenca_{aula_id}_{aluno.pk}'
                        presenca = request.POST.get(presenca_key)
                        
                        if presenca:
                            # Buscar ou criar frequência
                            frequencia, created = FrequenciaAula.objects.get_or_create(
                                aula=aula,
                                aluno=aluno,
                                defaults={'presenca': presenca}
                            )
                            
                            if not created:
                                frequencia.presenca = presenca
                                frequencia.save()
                    
                    messages.success(request, f'Frequências salvas para {aula.data_aula.strftime("%d/%m/%Y")}.')
                except AulaEnsino.DoesNotExist:
                    continue
            
            if aulas_ids:
                messages.success(request, 'Frequências salvas com sucesso!')
        
        return redirect('militares:ensino_caderneta_frequencia_disciplina', turma_id=turma_id, disciplina_id=disciplina_id)
    
    # Buscar frequências existentes
    frequencias = FrequenciaAula.objects.filter(
        aula__turma=turma,
        aula__disciplina=disciplina
    ).select_related('aula', 'aluno')
    
    # Criar dicionário de frequências para acesso rápido: frequencias_dict["aula_id_aluno_id"] = frequencia
    frequencias_dict = {}
    for freq in frequencias:
        key = f"{freq.aula.pk}_{freq.aluno.pk}"
        frequencias_dict[key] = freq
    
    # Calcular horas-aula de cada aula e acumulado progressivo
    horas_aula_por_aula = {}
    acumulado_por_aula = {}
    # Usar carga horária total informada na disciplina como horas/aula já definidas
    carga_horaria_total = int(disciplina.carga_horaria or 0)
    acumulado_total = 0.0
    
    for aula in aulas:
        # Calcular horas-aula a partir de hora_inicio e hora_fim
        if aula.hora_inicio and aula.hora_fim:
            inicio = datetime.combine(aula.data_aula, aula.hora_inicio)
            fim = datetime.combine(aula.data_aula, aula.hora_fim)
            # Se hora_fim for anterior a hora_inicio, assumir que é no dia seguinte
            if fim < inicio:
                fim += timedelta(days=1)
            duracao_minutos = (fim - inicio).total_seconds() / 60
            # Converter para horas-aula (1 hora-aula = 45 minutos)
            horas_aula = duracao_minutos / 45.0
        else:
            horas_aula = 0.0
        
        horas_aula_por_aula[aula.pk] = int(round(horas_aula))
        acumulado_total += horas_aula
        acumulado_por_aula[aula.pk] = int(round(acumulado_total))
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'alunos': alunos,
        'aulas': aulas,
        'frequencias_dict': frequencias_dict,
        'horas_aula_por_aula': horas_aula_por_aula,
        'acumulado_por_aula': acumulado_por_aula,
        'carga_horaria_total': carga_horaria_total,
    }
    
    return render(request, 'militares/ensino/turmas/caderneta_frequencia_disciplina.html', context)


@login_required
def dashboard_turma(request, pk):
    """Dashboard completo com todas as informações da turma"""
    turma = get_object_or_404(
        TurmaEnsino.objects.select_related('curso', 'supervisor_curso', 'coordenador_curso', 
                                          'supervisor_turma', 'coordenador_turma'),
        pk=pk
    )
    if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
        messages.error(request, 'Acesso negado. Você só pode acessar turmas em que está vinculado.')
        return redirect('militares:ensino_turmas_listar')
    
    # Alunos
    alunos = AlunoEnsino.objects.filter(turma=turma).select_related('militar', 'pessoa_externa').order_by('matricula')
    alunos_ativos = alunos.filter(situacao='ATIVO')
    alunos_concluidos = alunos.filter(situacao='CONCLUIDO')
    alunos_desligados = alunos.filter(situacao='DESLIGADO')
    
    # Aulas
    aulas = AulaEnsino.objects.filter(turma=turma).select_related('disciplina', 'instrutor').order_by('-data_aula', '-hora_inicio')
    total_aulas = aulas.count()
    aulas_realizadas = aulas.filter(data_aula__lte=date.today()).count()
    aulas_previstas = aulas.filter(data_aula__gt=date.today()).count()
    
    # Frequências
    frequencias = FrequenciaAula.objects.filter(aula__turma=turma).select_related('aluno', 'aula')
    total_frequencias = frequencias.count()
    frequencias_presentes = frequencias.filter(presenca='PRESENTE').count()
    frequencias_faltas = frequencias.exclude(presenca='PRESENTE').count()
    
    # Calcular frequência por aluno e adicionar como atributo ao aluno
    for aluno in alunos_ativos:
        frequencias_aluno = frequencias.filter(aluno=aluno)
        total_freq_aluno = frequencias_aluno.count()
        presentes_aluno = frequencias_aluno.filter(presenca='PRESENTE').count()
        faltas_aluno = frequencias_aluno.exclude(presenca='PRESENTE').count()
        percentual_freq = (presentes_aluno / total_freq_aluno * 100) if total_freq_aluno > 0 else 0
        # Adicionar frequência como atributo ao aluno para facilitar acesso no template
        aluno.frequencia_info = {
            'total': total_freq_aluno,
            'presentes': presentes_aluno,
            'faltas': faltas_aluno,
            'percentual': round(percentual_freq, 2)
        }
    
    # Avaliações
    avaliacoes = AvaliacaoEnsino.objects.filter(turma=turma).select_related('disciplina').order_by('disciplina', 'data_avaliacao')
    total_avaliacoes = avaliacoes.count()
    
    # Notas
    notas_avaliacoes = NotaAvaliacao.objects.filter(
        avaliacao__turma=turma
    ).select_related('avaliacao', 'avaliacao__disciplina', 'aluno')
    
    # Calcular notas por disciplina (mesma lógica da view detalhes_turma)
    notas_por_disciplina = {}
    disciplinas_turma = set(turma.disciplinas.all())
    
    for disciplina in disciplinas_turma:
        disciplina_id = disciplina.pk
        notas_por_disciplina[disciplina_id] = {
            'disciplina': disciplina,
            'alunos': {},
            'media_geral': 0,
            'aprovados': 0,
            'recuperacao': 0,
            'reprovados': 0
        }
        
        for aluno in alunos_ativos:
            aluno_id = aluno.pk
            notas_por_disciplina[disciplina_id]['alunos'][aluno_id] = {
                'aluno': aluno,
                'notas': [None, None, None, None],
                'pesos': [0, 0, 0, 0],
                'nota_recuperacao': None,
                'media_final': None,
                'status': None
            }
    
    # Preencher notas
    for nota_obj in notas_avaliacoes:
        disciplina_id = nota_obj.avaliacao.disciplina.pk
        aluno_id = nota_obj.aluno.pk
        
        if disciplina_id in notas_por_disciplina and aluno_id in notas_por_disciplina[disciplina_id]['alunos']:
            if nota_obj.avaliacao.tipo == 'RECUPERACAO':
                notas_por_disciplina[disciplina_id]['alunos'][aluno_id]['nota_recuperacao'] = nota_obj.nota
            else:
                avaliacoes_disciplina = [a for a in avaliacoes if a.disciplina.pk == disciplina_id and a.tipo != 'RECUPERACAO']
                avaliacoes_disciplina_ordenadas = sorted(avaliacoes_disciplina, key=lambda x: (x.data_avaliacao if x.data_avaliacao else date.min, x.id))
                
                try:
                    posicao = avaliacoes_disciplina_ordenadas.index(nota_obj.avaliacao)
                    if posicao < 4:
                        notas_por_disciplina[disciplina_id]['alunos'][aluno_id]['notas'][posicao] = nota_obj.nota
                        notas_por_disciplina[disciplina_id]['alunos'][aluno_id]['pesos'][posicao] = nota_obj.avaliacao.peso
                except ValueError:
                    pass
    
    # Calcular médias e status
    for disciplina_id, dados_disciplina in notas_por_disciplina.items():
        disciplina = dados_disciplina['disciplina']
        media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
        soma_medias = 0
        total_com_media = 0
        
        for aluno_id, dados_aluno in dados_disciplina['alunos'].items():
            notas = dados_aluno['notas']
            pesos = dados_aluno['pesos']
            
            soma_notas_pesos = 0
            soma_pesos = 0
            
            for i in range(4):
                if notas[i] is not None and pesos[i] > 0:
                    soma_notas_pesos += float(notas[i]) * float(pesos[i])
                    soma_pesos += float(pesos[i])
            
            if soma_pesos > 0:
                media_final = soma_notas_pesos / soma_pesos
                dados_aluno['media_final'] = round(media_final, 2)
                soma_medias += media_final
                total_com_media += 1
                
                # Verificar se todas as avaliações foram >= média mínima
                todas_aprovadas = True
                total_avaliacoes = 0
                for i in range(4):
                    if notas[i] is not None and pesos[i] > 0:
                        total_avaliacoes += 1
                        if float(notas[i]) < media_minima:
                            todas_aprovadas = False
                
                # Determinar status
                if todas_aprovadas and total_avaliacoes > 0:
                    # Aprovado: tirou média ou maior em todas as avaliações
                    dados_aluno['status'] = 'APROVADO'
                    dados_disciplina['aprovados'] += 1
                elif media_final >= media_minima:
                    # Aprovado: não tirou em todas, mas conseguiu a média final
                    dados_aluno['status'] = 'APROVADO'
                    dados_disciplina['aprovados'] += 1  # Conta como aprovado para estatísticas
                else:
                    # Recuperação: não conseguiu a média final
                    dados_aluno['status'] = 'RECUPERACAO'
                    dados_disciplina['recuperacao'] += 1
        
        if total_com_media > 0:
            dados_disciplina['media_geral'] = round(soma_medias / total_com_media, 2)
    
    # Ocorrências disciplinares
    ocorrencias = OcorrenciaDisciplinar.objects.filter(turma=turma).select_related('aluno').order_by('-data_ocorrencia')
    total_ocorrencias = ocorrencias.count()
    
    # Certificados
    certificados = CertificadoEnsino.objects.filter(turma=turma).select_related('aluno', 'curso').order_by('-data_criacao')
    total_certificados = certificados.count()
    
    # Escalas
    escalas = EscalaInstrucao.objects.filter(turma=turma).select_related('instrutor', 'disciplina').order_by('data_escala', 'hora_inicio')
    total_escalas = escalas.count()
    
    # Cautelas de material
    cautelas = CautelaMaterialEscolar.objects.filter(aluno__turma=turma).select_related('aluno', 'material')
    cautelas_pendentes = cautelas.exclude(status='DEVOLVIDO').count()
    
    # Estatísticas gerais
    total_alunos = alunos.count()
    total_alunos_ativos = alunos_ativos.count()
    total_disciplinas = disciplinas_turma.__len__()
    
    # Calcular percentual de conclusão do curso
    if turma.data_inicio and turma.data_fim:
        hoje = date.today()
        dias_totais = (turma.data_fim - turma.data_inicio).days
        
        if hoje < turma.data_inicio:
            # Curso ainda não começou
            percentual_conclusao = 0
        elif hoje > turma.data_fim:
            # Curso já terminou
            percentual_conclusao = 100
        else:
            # Curso em andamento
            dias_decorridos = (hoje - turma.data_inicio).days
            if dias_totais > 0:
                percentual_conclusao = (dias_decorridos / dias_totais * 100)
            else:
                percentual_conclusao = 0
            # Garantir que está entre 0 e 100
            percentual_conclusao = min(100, max(0, percentual_conclusao))
    else:
        percentual_conclusao = 0
    
    # Calcular percentual restante
    percentual_restante = 100 - percentual_conclusao
    
    # Calcular média geral da turma
    todas_medias = []
    for dados_disciplina in notas_por_disciplina.values():
        for dados_aluno in dados_disciplina['alunos'].values():
            if dados_aluno['media_final'] is not None:
                todas_medias.append(dados_aluno['media_final'])
    
    media_geral_turma = round(sum(todas_medias) / len(todas_medias), 3) if todas_medias else None
    
    context = {
        'turma': turma,
        'alunos': alunos,
        'alunos_ativos': alunos_ativos,
        'alunos_concluidos': alunos_concluidos,
        'alunos_desligados': alunos_desligados,
        'aulas': aulas,
        'frequencias': frequencias,
        'avaliacoes': avaliacoes,
        'notas_por_disciplina': notas_por_disciplina,
        'ocorrencias': ocorrencias,
        'certificados': certificados,
        'escalas': escalas,
        'cautelas': cautelas,
        'cautelas_pendentes': cautelas_pendentes,
        # Estatísticas
        'total_alunos': total_alunos,
        'total_alunos_ativos': total_alunos_ativos,
        'total_disciplinas': total_disciplinas,
        'total_aulas': total_aulas,
        'aulas_realizadas': aulas_realizadas,
        'aulas_previstas': aulas_previstas,
        'total_frequencias': total_frequencias,
        'frequencias_presentes': frequencias_presentes,
        'frequencias_faltas': frequencias_faltas,
        'total_avaliacoes': total_avaliacoes,
        'total_ocorrencias': total_ocorrencias,
        'total_certificados': total_certificados,
        'total_escalas': total_escalas,
        'percentual_conclusao': round(percentual_conclusao, 1),
        'percentual_restante': round(percentual_restante, 1),
        'media_geral_turma': media_geral_turma,
        'percentual_frequencia_geral': round((frequencias_presentes / total_frequencias * 100) if total_frequencias > 0 else 0, 2),
    }
    
    return render(request, 'militares/ensino/turmas/dashboard.html', context)


@login_required
def editar_turma(request, pk):
    """Edita uma turma existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar turmas.')
        return redirect('militares:ensino_turmas_listar')
    
    from militares.models import Militar, DisciplinaCurso, AlunoEnsino, POSTO_GRADUACAO_CHOICES, InstrutorEnsino, MonitorEnsino
    import uuid
    
    turma = get_object_or_404(TurmaEnsino, pk=pk)
    if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
        messages.error(request, 'Acesso negado. Você só pode editar turmas em que está vinculado.')
        return redirect('militares:ensino_turmas_listar')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        if request.method == 'POST':
            form = TurmaEnsinoForm(request.POST, instance=turma)
            if form.is_valid():
                try:
                    turma = form.save()
                    
                    # Processar alunos selecionados (IDs de AlunoEnsino)
                    alunos_selecionados = request.POST.getlist('alunos_selecionados')
                    alunos_selecionados_ids = [int(id) for id in alunos_selecionados if id]
                    
                    # Buscar todos os alunos atuais da turma
                    alunos_atuais = AlunoEnsino.objects.filter(turma=turma)
                    alunos_atuais_count = alunos_atuais.count()
                    
                    # Adicionar novos alunos
                    contador_novos = 0
                    for aluno_id in alunos_selecionados_ids:
                        try:
                            aluno = AlunoEnsino.objects.get(pk=aluno_id)
                            # Verificar se já existe este aluno nesta turma
                            aluno_existente = AlunoEnsino.objects.filter(pk=aluno_id, turma=turma).first()
                            if not aluno_existente:
                                # Se o aluno não tem turma, adicionar à turma e gerar matrícula
                                # Se já tem turma diferente, criar uma cópia do aluno para esta turma
                                if not aluno.turma:
                                    numero_inicial = alunos_atuais_count + contador_novos + 1
                                    matricula = gerar_matricula_aluno(turma, numero_inicial)
                                    aluno.turma = turma
                                    aluno.matricula = matricula
                                    if aluno.situacao not in ['ATIVO', 'CONCLUIDO']:
                                        aluno.situacao = 'ATIVO'
                                    aluno.save()
                                    contador_novos += 1
                                elif aluno.turma != turma:
                                    # Aluno já está em outra turma - não criar cópia
                                    # Um aluno pode ter apenas um cadastro, mas pode estar em múltiplas turmas
                                    # Por enquanto, apenas mover o aluno para a nova turma
                                    nome_aluno = aluno.get_pessoa_nome()
                                    turma_anterior = aluno.turma.identificacao if aluno.turma else 'Nenhuma'
                                    messages.warning(
                                        request,
                                        f'O aluno {nome_aluno} já está na turma "{turma_anterior}". '
                                        f'Movendo para a turma "{turma.identificacao}". '
                                        f'Em breve, será possível que um aluno esteja em múltiplas turmas simultaneamente.'
                                    )
                                    numero_inicial = alunos_atuais_count + contador_novos + 1
                                    matricula = gerar_matricula_aluno(turma, numero_inicial)
                                    aluno.turma = turma
                                    aluno.matricula = matricula
                                    if aluno.situacao not in ['ATIVO', 'CONCLUIDO']:
                                        aluno.situacao = 'ATIVO'
                                    aluno.save()
                                    contador_novos += 1
                        except (AlunoEnsino.DoesNotExist, ValueError) as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f'Erro ao processar aluno {aluno_id}: {str(e)}')
                            continue
                    
                    # Remover alunos que não estão mais na lista
                    for aluno_atual in alunos_atuais:
                        if aluno_atual.pk not in alunos_selecionados_ids:
                            # Aluno foi removido da lista, remover da turma
                            aluno_atual.turma = None
                            aluno_atual.matricula = None
                            aluno_atual.save()
                    
                    # Processar instrutores e monitores para cada disciplina
                    disciplinas_ids_str = request.POST.get('disciplinas_ids', '')
                    if not disciplinas_ids_str:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning('Nenhuma disciplina foi selecionada para a turma')
                    else:
                        disciplinas_ids = disciplinas_ids_str.split(',')
                        disciplinas_para_vincular = []
                        
                        for disciplina_id_str in disciplinas_ids:
                            if not disciplina_id_str:
                                continue
                            try:
                                disciplina_id = int(disciplina_id_str)
                                disciplina = DisciplinaEnsino.objects.get(pk=disciplina_id)
                                
                                # Processar instrutor
                                instrutor_value = request.POST.get(f'disciplina_{disciplina_id}_instrutor', '').strip()
                                if instrutor_value:
                                    if instrutor_value.startswith('MILITAR_'):
                                        instrutor_ensino_id = int(instrutor_value.replace('MILITAR_', ''))
                                        instrutor_ensino = InstrutorEnsino.objects.get(pk=instrutor_ensino_id)
                                        if instrutor_ensino.militar:
                                            disciplina.instrutor_responsavel_militar = instrutor_ensino.militar
                                            disciplina.instrutor_responsavel_externo = None
                                            disciplina.save(update_fields=['instrutor_responsavel_militar', 'instrutor_responsavel_externo'])
                                    elif instrutor_value.startswith('EXTERNO_'):
                                        instrutor_ensino_id = int(instrutor_value.replace('EXTERNO_', ''))
                                        instrutor_ensino = InstrutorEnsino.objects.get(pk=instrutor_ensino_id)
                                        disciplina.instrutor_responsavel_externo = instrutor_ensino
                                        disciplina.instrutor_responsavel_militar = None
                                        disciplina.save(update_fields=['instrutor_responsavel_militar', 'instrutor_responsavel_externo'])
                                else:
                                    # Se não houver instrutor selecionado, limpar
                                    disciplina.instrutor_responsavel_militar = None
                                    disciplina.instrutor_responsavel_externo = None
                                    disciplina.save(update_fields=['instrutor_responsavel_militar', 'instrutor_responsavel_externo'])
                                
                                # Processar monitores militares
                                monitores_militares_ids = request.POST.getlist(f'disciplina_{disciplina_id}_monitores_militares[]')
                                monitores_militares_para_adicionar = []
                                for monitor_ensino_id_str in monitores_militares_ids:
                                    try:
                                        monitor_ensino_id = int(monitor_ensino_id_str)
                                        monitor_ensino = MonitorEnsino.objects.get(pk=monitor_ensino_id)
                                        if monitor_ensino.militar:
                                            monitores_militares_para_adicionar.append(monitor_ensino.militar)
                                    except (MonitorEnsino.DoesNotExist, ValueError):
                                        continue
                                
                                # Processar monitores externos
                                monitores_externos_ids = request.POST.getlist(f'disciplina_{disciplina_id}_monitores_externos[]')
                                monitores_externos_para_adicionar = []
                                for monitor_ensino_id_str in monitores_externos_ids:
                                    try:
                                        monitor_ensino_id = int(monitor_ensino_id_str)
                                        monitor_ensino = MonitorEnsino.objects.get(pk=monitor_ensino_id)
                                        monitores_externos_para_adicionar.append(monitor_ensino)
                                    except (MonitorEnsino.DoesNotExist, ValueError):
                                        continue
                                
                                # Atualizar monitores da disciplina
                                disciplina.monitores_militares.set(monitores_militares_para_adicionar)
                                disciplina.monitores_externos.set(monitores_externos_para_adicionar)
                                
                                # Adicionar disciplina à lista para vincular à turma
                                disciplinas_para_vincular.append(disciplina)
                                
                            except (DisciplinaEnsino.DoesNotExist, ValueError, InstrutorEnsino.DoesNotExist, MonitorEnsino.DoesNotExist) as e:
                                import logging
                                logger = logging.getLogger(__name__)
                                logger.error(f'Erro ao processar disciplina {disciplina_id_str}: {str(e)}')
                                continue
                        
                        # Vincular disciplinas à turma
                        if disciplinas_para_vincular:
                            turma.disciplinas.set(disciplinas_para_vincular)
                            
                            # Processar blocos de disciplinas
                            from militares.models import BlocoDisciplinaTurma
                            # Limpar blocos existentes para recriar
                            BlocoDisciplinaTurma.objects.filter(turma=turma).delete()
                            
                            for disciplina in disciplinas_para_vincular:
                                disciplina_id = disciplina.pk
                                # Buscar número do bloco do POST
                                numero_bloco_str = request.POST.get(f'disciplina_{disciplina_id}_bloco', '').strip()
                                ordem_disciplina_str = request.POST.get(f'disciplina_{disciplina_id}_ordem_bloco', '1').strip()
                                
                                try:
                                    numero_bloco = int(numero_bloco_str) if numero_bloco_str else 1
                                    ordem_disciplina = int(ordem_disciplina_str) if ordem_disciplina_str else 1
                                    
                                    BlocoDisciplinaTurma.objects.create(
                                        turma=turma,
                                        disciplina=disciplina,
                                        numero_bloco=numero_bloco,
                                        ordem_disciplina=ordem_disciplina
                                    )
                                except (ValueError, TypeError):
                                    # Se não houver bloco definido, criar no bloco 1
                                    BlocoDisciplinaTurma.objects.create(
                                        turma=turma,
                                        disciplina=disciplina,
                                        numero_bloco=1,
                                        ordem_disciplina=1
                                    )
                    
                    messages.success(request, f'Turma {turma.identificacao} atualizada com sucesso!')
                    
                    if is_ajax:
                        from django.http import JsonResponse
                        from django.urls import reverse
                        return JsonResponse({
                            'success': True,
                            'redirect': reverse('militares:ensino_turma_detalhes', kwargs={'pk': turma.pk})
                        })
                    
                    return redirect('militares:ensino_turma_detalhes', pk=turma.pk)
                except Exception as e:
                    if is_ajax:
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': False,
                            'error': f'Erro ao atualizar turma: {str(e)}',
                            'errors': form.errors
                        }, status=400)
                    messages.error(request, f'Erro ao atualizar turma: {str(e)}')
            else:
                # Formulário com erros
                if is_ajax:
                    from django.template.loader import render_to_string
                    # Buscar todos os alunos cadastrados (bombeiros, outras forças e civis)
                    alunos_disponiveis = AlunoEnsino.objects.filter(
                        Q(situacao='ATIVO') | Q(situacao='CONCLUIDO')
                    ).select_related('militar', 'pessoa_externa').order_by('tipo_aluno', 'militar__posto_graduacao', 'nome_outra_forca', 'nome_civil')
                    # Manter militares para compatibilidade
                    militares = Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo')
                    instrutores = InstrutorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
                    monitores = MonitorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
                    # Buscar alunos já cadastrados na turma
                    alunos_turma = AlunoEnsino.objects.filter(turma=turma).select_related('militar', 'pessoa_externa')
                    html = render_to_string('militares/ensino/turmas/criar_modal.html', {
                        'form': form,
                        'turma': turma,
                        'militares': militares,
                        'alunos_disponiveis': alunos_disponiveis,
                        'postos_graduacao': POSTO_GRADUACAO_CHOICES,
                        'instrutores': instrutores,
                        'monitores': monitores,
                        'alunos_turma': alunos_turma,
                    }, request=request)
                    from django.http import HttpResponse
                    return HttpResponse(html)
        else:
            form = TurmaEnsinoForm(instance=turma)
        
        # Buscar todos os alunos cadastrados (bombeiros, outras forças e civis)
        alunos_disponiveis = AlunoEnsino.objects.filter(
            Q(situacao='ATIVO') | Q(situacao='CONCLUIDO')
        ).select_related('militar', 'pessoa_externa').order_by('tipo_aluno', 'militar__posto_graduacao', 'nome_outra_forca', 'nome_civil')
        
        # Manter militares para compatibilidade
        militares = Militar.objects.filter(classificacao='ATIVO').order_by('posto_graduacao', 'nome_completo')
        
        # Buscar instrutores e monitores para seleção nas disciplinas
        instrutores = InstrutorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
        monitores = MonitorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
        
        # Buscar alunos já cadastrados na turma
        alunos_turma = AlunoEnsino.objects.filter(turma=turma).select_related('militar', 'pessoa_externa')
        
        # Buscar blocos de disciplinas existentes
        from militares.models import BlocoDisciplinaTurma
        blocos_disciplinas = BlocoDisciplinaTurma.objects.filter(turma=turma).select_related('disciplina')
        blocos_dict = {bloco.disciplina_id: {'numero_bloco': bloco.numero_bloco, 'ordem_bloco': bloco.ordem_disciplina} for bloco in blocos_disciplinas}
        
        context = {
            'form': form,
            'turma': turma,
            'militares': militares,
            'alunos_disponiveis': alunos_disponiveis,
            'postos_graduacao': POSTO_GRADUACAO_CHOICES,
            'instrutores': instrutores,
            'monitores': monitores,
            'alunos_turma': alunos_turma,
            'blocos_disciplinas': blocos_dict,
        }
        
        # Se for requisição AJAX, retornar apenas o conteúdo do modal
        if is_ajax:
            from django.template.loader import render_to_string
            html = render_to_string('militares/ensino/turmas/criar_modal.html', context, request=request)
            from django.http import HttpResponse
            return HttpResponse(html)
        
        return render(request, 'militares/ensino/turmas/editar.html', context)
    
    except Exception as e:
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'error': f'Erro ao processar requisição: {str(e)}'
            }, status=500)
        messages.error(request, f'Erro ao editar turma: {str(e)}')
        return redirect('militares:ensino_turmas_listar')


@login_required
def excluir_turma(request, pk):
    """Exclui uma turma"""
    if not pode_excluir_ensino(request.user):
        messages.error(request, 'Você não tem permissão para excluir turmas.')
        return redirect('militares:ensino_turmas_listar')
    
    turma = get_object_or_404(TurmaEnsino, pk=pk)
    if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
        messages.error(request, 'Acesso negado. Você só pode excluir turmas em que está vinculado.')
        return redirect('militares:ensino_turmas_listar')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            nome_turma = turma.identificacao
            
            # Verificar se há alunos vinculados
            alunos_count = AlunoEnsino.objects.filter(turma=turma).count()
            
            # Verificar se há aulas vinculadas
            aulas_count = AulaEnsino.objects.filter(turma=turma).count()
            
            # Avisar sobre alunos e aulas vinculadas, mas permitir exclusão
            if alunos_count > 0 or aulas_count > 0:
                warning_msg = f'A turma {nome_turma} possui {alunos_count} aluno(s) e {aulas_count} aula(s) vinculada(s). '
                warning_msg += 'Os alunos serão desvinculados e as aulas serão excluídas permanentemente.'
                
                # Se for requisição AJAX, retornar aviso
                if is_ajax and request.POST.get('confirmar') != 'true':
                    return JsonResponse({
                        'success': False, 
                        'message': warning_msg,
                        'requires_confirmation': True
                    }, status=400)
            
            # Excluir a turma (as aulas serão excluídas em cascata devido ao CASCADE)
            # Os alunos serão desvinculados (SET_NULL)
            turma.delete()
            messages.success(request, f'Turma {nome_turma} excluída com sucesso!')
            
            if is_ajax:
                return JsonResponse({
                    'success': True, 
                    'redirect': reverse('militares:ensino_turmas_listar')
                })
            return redirect('militares:ensino_turmas_listar')
        except Exception as e:
            error_message = str(e)
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'message': f'Erro ao excluir turma: {error_message}'
                }, status=400)
            messages.error(request, f'Erro ao excluir turma: {error_message}')
            return redirect('militares:ensino_turmas_listar')
    
    # GET request - retornar confirmação (o modal já existe no template listar.html)
    # O modal de exclusão já está no template listar.html, então apenas redireciona
    return redirect('militares:ensino_turmas_listar')


# ============================================================================
# 3. DISCIPLINAS (Relacionadas a Curso e Turma)
# ============================================================================

@login_required
def listar_disciplinas(request):
    """Lista todas as disciplinas"""
    disciplinas = DisciplinaEnsino.objects.select_related(
        'instrutor_responsavel_militar', 'instrutor_responsavel_externo'
    ).all()
    
    busca = request.GET.get('busca', '')
    ativo = request.GET.get('ativo', '')
    
    if busca:
        disciplinas = disciplinas.filter(
            Q(codigo__icontains=busca) |
            Q(nome__icontains=busca) |
            Q(ementa__icontains=busca)
        )
    
    if ativo == 'true':
        disciplinas = disciplinas.filter(ativo=True)
    elif ativo == 'false':
        disciplinas = disciplinas.filter(ativo=False)
    
    paginator = Paginator(disciplinas, 20)
    page = request.GET.get('page')
    disciplinas = paginator.get_page(page)
    
    return render(request, 'militares/ensino/disciplinas/listar.html', {'disciplinas': disciplinas})


@login_required
def criar_disciplina(request):
    """Cria uma nova disciplina"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar disciplinas.')
        return redirect('militares:ensino_disciplinas_listar')
    
    logger = logging.getLogger(__name__)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = DisciplinaEnsinoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                disciplina = form.save()
                
                # Processar múltiplos arquivos complementares
                arquivos_complementares_upload = request.FILES.getlist('arquivos_complementares[]')
                titulos_arquivos = request.POST.getlist('arquivos_complementares_titulos[]', [])
                descricoes_arquivos = request.POST.getlist('arquivos_complementares_descricoes[]', [])
                
                for idx, arquivo in enumerate(arquivos_complementares_upload):
                    if not arquivo:
                        continue
                    
                    try:
                        titulo = titulos_arquivos[idx] if idx < len(titulos_arquivos) else arquivo.name
                        descricao = descricoes_arquivos[idx] if idx < len(descricoes_arquivos) else ''
                        
                        DocumentoDisciplinaEnsino.objects.create(
                            disciplina=disciplina,
                            tipo='ARQUIVO_COMPLEMENTAR',
                            titulo=titulo[:200],
                            descricao=descricao,
                            arquivo=arquivo,
                            upload_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar arquivo complementar {idx}: {str(e)}')
                        continue
                
                # Processar múltiplos links úteis
                links_uteis_urls = request.POST.getlist('links_uteis_urls[]', [])
                links_uteis_titulos = request.POST.getlist('links_uteis_titulos[]', [])
                links_uteis_descricoes = request.POST.getlist('links_uteis_descricoes[]', [])
                
                for idx, url in enumerate(links_uteis_urls):
                    if not url:
                        continue
                    
                    try:
                        titulo = links_uteis_titulos[idx] if idx < len(links_uteis_titulos) else url
                        descricao = links_uteis_descricoes[idx] if idx < len(links_uteis_descricoes) else ''
                        
                        LinkUtilDisciplina.objects.create(
                            disciplina=disciplina,
                            titulo=titulo[:200],
                            url=url,
                            descricao=descricao,
                            criado_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar link útil {idx}: {str(e)}')
                        continue
                
                messages.success(request, f'Disciplina {disciplina.codigo} criada com sucesso!')
                if is_ajax:
                    # Requisição AJAX - retornar JSON para redirecionamento
                    from django.http import JsonResponse
                    return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_disciplinas_listar')})
                return redirect('militares:ensino_disciplinas_listar')
            except Exception as e:
                # Erro ao salvar (ex: violação de constraint, erro de banco)
                import traceback
                error_message = str(e)
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': f'Erro ao salvar disciplina: {error_message}',
                        'errors': form.errors
                    }, status=400)
                messages.error(request, f'Erro ao criar disciplina: {error_message}')
        else:
            # Formulário com erros
            if is_ajax:
                # Retornar formulário com erros para o modal
                from django.template.loader import render_to_string
                html = render_to_string('militares/ensino/disciplinas/criar_modal.html', {'form': form}, request=request)
                from django.http import HttpResponse
                return HttpResponse(html)
    else:
        form = DisciplinaEnsinoForm()
    
    # Se for requisição AJAX, retornar apenas o formulário (versão modal)
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/disciplinas/criar_modal.html', {'form': form}, request=request)
        from django.http import HttpResponse
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/disciplinas/criar.html', {'form': form, 'is_ajax': False})


@login_required
def detalhes_disciplina(request, pk):
    """Detalhes completos de uma disciplina"""
    disciplina = get_object_or_404(DisciplinaEnsino, pk=pk)
    
    # Cursos que usam esta disciplina (através do related_name 'cursos')
    try:
        cursos = disciplina.cursos.all().select_related('coordenador_militar', 'coordenador_externo')
    except AttributeError:
        # Fallback: buscar através do modelo intermediário
        from militares.models import DisciplinaCurso
        disciplinas_curso = DisciplinaCurso.objects.filter(disciplina=disciplina).select_related('curso')
        cursos = [dc.curso for dc in disciplinas_curso]
    
    # Buscar todas as turmas que usam esta disciplina
    turmas_com_disciplina = TurmaEnsino.objects.filter(disciplinas=disciplina).select_related('curso').distinct()
    
    # Calcular notas por turma e aluno
    notas_por_turma = {}
    
    for turma in turmas_com_disciplina:
        # Buscar avaliações desta disciplina nesta turma
        avaliacoes_turma = AvaliacaoEnsino.objects.filter(
            turma=turma,
            disciplina=disciplina
        ).order_by('data_avaliacao')
        
        # Buscar alunos ativos da turma
        alunos_ativos = AlunoEnsino.objects.filter(
            turma=turma,
            situacao='ATIVO'
        ).select_related('militar', 'pessoa_externa').order_by('matricula')
        
        # Estrutura para notas por aluno
        notas_por_aluno = {}
        
        for aluno in alunos_ativos:
            notas_por_aluno[aluno.pk] = {
                'aluno': aluno,
                'notas': [None, None, None, None],
                'pesos': [0, 0, 0, 0],
                'nota_recuperacao': None,
                'nota_ids': [None, None, None, None],
                'nota_recuperacao_id': None,
                'media_final': None,
                'status': None
            }
        
        # Buscar todas as notas dos alunos nas avaliações desta disciplina nesta turma
        notas_avaliacoes = NotaAvaliacao.objects.filter(
            avaliacao__turma=turma,
            avaliacao__disciplina=disciplina
        ).select_related('avaliacao', 'aluno')
        
        # Preencher notas das avaliações
        for nota_obj in notas_avaliacoes:
            aluno_id = nota_obj.aluno.pk
            
            if aluno_id in notas_por_aluno:
                dados_aluno = notas_por_aluno[aluno_id]
                
                # Se for avaliação de recuperação, armazenar separadamente
                if nota_obj.avaliacao.tipo == 'RECUPERACAO':
                    dados_aluno['nota_recuperacao'] = nota_obj.nota
                    dados_aluno['peso_recuperacao'] = nota_obj.avaliacao.peso
                    dados_aluno['nota_recuperacao_id'] = nota_obj.pk
                else:
                    # Encontrar posição da avaliação (1ª, 2ª, 3ª ou 4ª)
                    avaliacoes_ordenadas = sorted(
                        [a for a in avaliacoes_turma if a.tipo != 'RECUPERACAO'],
                        key=lambda x: (x.data_avaliacao if x.data_avaliacao else date.min, x.id)
                    )
                    
                    try:
                        posicao = avaliacoes_ordenadas.index(nota_obj.avaliacao)
                        if posicao < 4:  # Máximo 4 avaliações
                            dados_aluno['notas'][posicao] = nota_obj.nota
                            dados_aluno['pesos'][posicao] = nota_obj.avaliacao.peso
                            dados_aluno['nota_ids'][posicao] = nota_obj.pk
                    except ValueError:
                        pass
        
        # Calcular média final e status para cada aluno
        media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
        
        for aluno_id, dados_aluno in notas_por_aluno.items():
            notas_list = dados_aluno['notas']
            pesos_list = dados_aluno['pesos']
            nota_recuperacao = dados_aluno.get('nota_recuperacao')
            
            # Se houver nota de recuperação, usar apenas ela como média final
            # A média anterior das avaliações regulares não entra no cálculo
            if nota_recuperacao is not None:
                media_final = float(nota_recuperacao)
                dados_aluno['media_final'] = round(media_final, 2)
                
                # Determinar status baseado na nota de recuperação
                media_minima_recuperacao = float(disciplina.media_minima_recuperacao) if disciplina.media_minima_recuperacao else 6.0
                if media_final >= media_minima_recuperacao:
                    dados_aluno['status'] = 'APROVADO'  # Aprovado com recuperação
                else:
                    dados_aluno['status'] = 'REPROVADO'  # Reprovado na recuperação
            else:
                # Calcular média ponderada apenas das avaliações regulares
                soma_notas_pesos = 0
                soma_pesos = 0
                
                for i in range(4):
                    if notas_list[i] is not None and pesos_list[i] > 0:
                        soma_notas_pesos += float(notas_list[i]) * float(pesos_list[i])
                        soma_pesos += float(pesos_list[i])
                
                if soma_pesos > 0:
                    media_final = soma_notas_pesos / soma_pesos
                    dados_aluno['media_final'] = round(media_final, 2)
                else:
                    media_final = None
                    dados_aluno['media_final'] = None
                
                # Verificar se todas as avaliações foram >= média mínima
                todas_aprovadas = True
                total_avaliacoes = 0
                for i in range(4):
                    if notas_list[i] is not None and pesos_list[i] > 0:
                        total_avaliacoes += 1
                        if float(notas_list[i]) < media_minima:
                            todas_aprovadas = False
                
                # Determinar status
                if todas_aprovadas and total_avaliacoes > 0:
                    # Aprovado: tirou média ou maior em todas as avaliações
                    dados_aluno['status'] = 'APROVADO'
                elif media_final is not None and media_final >= media_minima:
                    # Aprovado: não tirou em todas, mas conseguiu a média final
                    dados_aluno['status'] = 'APROVADO'
                else:
                    # Recuperação: não conseguiu a média final
                    dados_aluno['status'] = 'RECUPERACAO'
        
        # Verificar número de avaliações para esta turma
        verificacao_avaliacoes = disciplina.verificar_numero_avaliacoes(turma=turma)
        
        notas_por_turma[turma.pk] = {
            'turma': turma,
            'alunos': notas_por_aluno,
            'verificacao_avaliacoes': verificacao_avaliacoes
        }
    
    # Informações gerais sobre número de avaliações (sem turma específica)
    verificacao_geral = disciplina.verificar_numero_avaliacoes()
    
    pedidos_map = {p.nota_avaliacao_id: p for p in PedidoRevisaoProva.objects.filter(nota_avaliacao__avaliacao__disciplina=disciplina)}
    for turma_id, dados_turma in notas_por_turma.items():
        alunos_dict = dados_turma['alunos']
        for aluno_id, dados_aluno in alunos_dict.items():
            revisao_status = [None, None, None, None]
            for idx in range(4):
                nid = dados_aluno['nota_ids'][idx]
                if nid and nid in pedidos_map:
                    revisao_status[idx] = pedidos_map[nid].get_status_display()
            rec_id = dados_aluno.get('nota_recuperacao_id')
            revisao_status_rec = None
            if rec_id and rec_id in pedidos_map:
                revisao_status_rec = pedidos_map[rec_id].get_status_display()
            dados_aluno['revisao_status'] = revisao_status
            dados_aluno['revisao_status_rec'] = revisao_status_rec
    
    context = {
        'disciplina': disciplina,
        'cursos': cursos,
        'notas_por_turma': notas_por_turma,
        'verificacao_geral': verificacao_geral,
    }
    return render(request, 'militares/ensino/disciplinas/detalhes.html', context)


@login_required
def editar_disciplina(request, pk):
    """Edita uma disciplina existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar disciplinas.')
        return redirect('militares:ensino_disciplinas_listar')
    
    logger = logging.getLogger(__name__)
    disciplina = get_object_or_404(DisciplinaEnsino, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = DisciplinaEnsinoForm(request.POST, request.FILES, instance=disciplina)
        if form.is_valid():
            try:
                disciplina = form.save()
                
                # Processar múltiplos arquivos complementares
                arquivos_complementares_upload = request.FILES.getlist('arquivos_complementares[]')
                titulos_arquivos = request.POST.getlist('arquivos_complementares_titulos[]', [])
                descricoes_arquivos = request.POST.getlist('arquivos_complementares_descricoes[]', [])
                
                for idx, arquivo in enumerate(arquivos_complementares_upload):
                    if not arquivo:
                        continue
                    
                    try:
                        titulo = titulos_arquivos[idx] if idx < len(titulos_arquivos) else arquivo.name
                        descricao = descricoes_arquivos[idx] if idx < len(descricoes_arquivos) else ''
                        
                        DocumentoDisciplinaEnsino.objects.create(
                            disciplina=disciplina,
                            tipo='ARQUIVO_COMPLEMENTAR',
                            titulo=titulo[:200],
                            descricao=descricao,
                            arquivo=arquivo,
                            upload_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar arquivo complementar {idx}: {str(e)}')
                        continue
                
                # Processar remoção de arquivos complementares
                arquivos_complementares_remover = request.POST.getlist('arquivos_complementares_remover[]')
                if arquivos_complementares_remover:
                    DocumentoDisciplinaEnsino.objects.filter(
                        id__in=arquivos_complementares_remover,
                        disciplina=disciplina,
                        tipo='ARQUIVO_COMPLEMENTAR'
                    ).delete()
                
                # Processar múltiplos links úteis
                links_uteis_urls = request.POST.getlist('links_uteis_urls[]', [])
                links_uteis_titulos = request.POST.getlist('links_uteis_titulos[]', [])
                links_uteis_descricoes = request.POST.getlist('links_uteis_descricoes[]', [])
                
                for idx, url in enumerate(links_uteis_urls):
                    if not url:
                        continue
                    
                    try:
                        titulo = links_uteis_titulos[idx] if idx < len(links_uteis_titulos) else url
                        descricao = links_uteis_descricoes[idx] if idx < len(links_uteis_descricoes) else ''
                        
                        LinkUtilDisciplina.objects.create(
                            disciplina=disciplina,
                            titulo=titulo[:200],
                            url=url,
                            descricao=descricao,
                            criado_por=request.user
                        )
                    except Exception as e:
                        logger.error(f'Erro ao processar link útil {idx}: {str(e)}')
                        continue
                
                # Processar remoção de links úteis
                links_uteis_remover = request.POST.getlist('links_uteis_remover[]')
                if links_uteis_remover:
                    LinkUtilDisciplina.objects.filter(
                        id__in=links_uteis_remover,
                        disciplina=disciplina
                    ).delete()
                
                messages.success(request, f'Disciplina {disciplina.codigo} atualizada com sucesso!')
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_disciplina_detalhes', kwargs={'pk': disciplina.pk})})
                return redirect('militares:ensino_disciplina_detalhes', pk=disciplina.pk)
            except Exception as e:
                error_message = str(e)
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'success': False,
                        'message': f'Erro ao salvar disciplina: {error_message}',
                        'errors': form.errors
                    }, status=400)
                messages.error(request, f'Erro ao atualizar disciplina: {error_message}')
        else:
            if is_ajax:
                from django.template.loader import render_to_string
                html = render_to_string('militares/ensino/disciplinas/editar_modal.html', {'form': form, 'disciplina': disciplina}, request=request)
                from django.http import HttpResponse
                return HttpResponse(html)
    else:
        form = DisciplinaEnsinoForm(instance=disciplina)
    
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/disciplinas/editar_modal.html', {'form': form, 'disciplina': disciplina}, request=request)
        from django.http import HttpResponse
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/disciplinas/editar.html', {'form': form, 'disciplina': disciplina, 'is_ajax': False})


@login_required
def deletar_disciplina(request, pk):
    """Deleta uma disciplina"""
    if not pode_excluir_ensino(request.user):
        messages.error(request, 'Você não tem permissão para excluir disciplinas.')
        return redirect('militares:ensino_disciplinas_listar')
    
    disciplina = get_object_or_404(DisciplinaEnsino, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            codigo = disciplina.codigo
            # Verificar se há cursos ou turmas usando esta disciplina
            if disciplina.cursos.exists():
                error_msg = f'Não é possível excluir a disciplina {codigo} pois ela está vinculada a cursos.'
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({'success': False, 'message': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('militares:ensino_disciplinas_listar')
            
            disciplina.delete()
            messages.success(request, f'Disciplina {codigo} excluída com sucesso!')
            
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': True, 'redirect': reverse('militares:ensino_disciplinas_listar')})
            return redirect('militares:ensino_disciplinas_listar')
        except Exception as e:
            error_message = str(e)
            if is_ajax:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'message': f'Erro ao excluir disciplina: {error_message}'}, status=400)
            messages.error(request, f'Erro ao excluir disciplina: {error_message}')
            return redirect('militares:ensino_disciplinas_listar')
    
    # GET request - retornar modal de confirmação
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/disciplinas/deletar_modal.html', {'disciplina': disciplina}, request=request)
        from django.http import HttpResponse
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/disciplinas/deletar_confirm.html', {'disciplina': disciplina})


# ============================================================================
# 7. AULAS (Relacionadas a Turma e Disciplina)
# ============================================================================

@login_required
def listar_aulas(request):
    """Lista todas as aulas"""
    aulas = AulaEnsino.objects.select_related(
        'disciplina', 
        'disciplina__instrutor_responsavel_militar',
        'disciplina__instrutor_responsavel_externo',
        'turma',
        'turma__instrutor_chefe_militar',
        'turma__instrutor_chefe_externo',
        'instrutor'
    ).all()
    
    busca = request.GET.get('busca', '')
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')
    disciplina_id = request.GET.get('disciplina', '')
    data_aula = request.GET.get('data_aula', '')
    
    if busca:
        aulas = aulas.filter(
            Q(disciplina__nome__icontains=busca) |
            Q(turma__identificacao__icontains=busca) |
            Q(local__icontains=busca)
        )
    
    if turma_id:
        aulas = aulas.filter(turma_id=turma_id)
    
    if disciplina_id:
        aulas = aulas.filter(disciplina_id=disciplina_id)
    
    if data_aula:
        aulas = aulas.filter(data_aula=data_aula)
    
    paginator = Paginator(aulas, 20)
    page = request.GET.get('page')
    aulas = paginator.get_page(page)
    
    turmas = TurmaEnsino.objects.filter(ativa=True)
    disciplinas = DisciplinaEnsino.objects.filter(ativo=True)
    
    context = {
        'aulas': aulas,
        'turmas': turmas,
        'disciplinas': disciplinas,
    }
    return render(request, 'militares/ensino/aulas/listar.html', context)


@login_required
def obter_dados_turma(request, turma_id):
    """Retorna dados da turma via AJAX"""
    from django.http import JsonResponse
    try:
        turma = get_object_or_404(TurmaEnsino.objects.select_related('curso'), pk=turma_id)
        
        # Buscar instrutor chefe (militar ou externo)
        instrutor_id = None
        instrutor_nome = None
        if turma.instrutor_chefe_militar:
            instrutor_id = turma.instrutor_chefe_militar.pk
            instrutor_nome = f"{turma.instrutor_chefe_militar.get_posto_graduacao_display()} {turma.instrutor_chefe_militar.nome_completo}"
        
        # Buscar monitores militares e externos
        monitores = []
        for monitor_militar in turma.monitores_militares.all():
            monitores.append({
                'id': monitor_militar.pk,
                'nome': f"{monitor_militar.get_posto_graduacao_display()} {monitor_militar.nome_completo}",
                'tipo': 'militar'
            })
        
        for monitor_externo in turma.monitores_externos.all():
            nome_monitor = ''
            if hasattr(monitor_externo, 'get_nome_completo'):
                nome_monitor = monitor_externo.get_nome_completo()
            elif hasattr(monitor_externo, 'nome_completo'):
                nome_monitor = monitor_externo.nome_completo
            elif hasattr(monitor_externo, 'nome'):
                nome_monitor = monitor_externo.nome
            
            monitores.append({
                'id': monitor_externo.pk,
                'nome': nome_monitor,
                'tipo': 'externo'
            })
        
        # Buscar disciplinas da turma e do curso
        disciplinas = []
        disciplinas_ids = set()
        
        # Disciplinas específicas da turma
        for disciplina in turma.disciplinas.select_related('instrutor_responsavel_militar', 'instrutor_responsavel_externo').all():
            if disciplina.pk not in disciplinas_ids:
                instrutor_id = None
                if disciplina.instrutor_responsavel_militar:
                    instrutor_id = disciplina.instrutor_responsavel_militar.pk
                
                disciplinas.append({
                    'id': disciplina.pk,
                    'nome': disciplina.nome,
                    'codigo': disciplina.codigo or '',
                    'instrutor_id': instrutor_id
                })
                disciplinas_ids.add(disciplina.pk)
        
        # Também buscar disciplinas do curso (se houver)
        if turma.curso:
            from militares.models import DisciplinaCurso
            disciplinas_curso = DisciplinaCurso.objects.filter(
                curso=turma.curso
            ).select_related('disciplina', 'disciplina__instrutor_responsavel_militar', 'disciplina__instrutor_responsavel_externo')
            
            for disc_curso in disciplinas_curso:
                disciplina = disc_curso.disciplina
                # Evitar duplicatas
                if disciplina.pk not in disciplinas_ids:
                    instrutor_id = None
                    if disciplina.instrutor_responsavel_militar:
                        instrutor_id = disciplina.instrutor_responsavel_militar.pk
                    
                    disciplinas.append({
                        'id': disciplina.pk,
                        'nome': disciplina.nome,
                        'codigo': disciplina.codigo or '',
                        'instrutor_id': instrutor_id
                    })
                    disciplinas_ids.add(disciplina.pk)
        
        # Buscar avaliações da turma para determinar posições
        avaliacoes_turma = AvaliacaoEnsino.objects.filter(
            turma=turma
        ).select_related('disciplina').order_by('disciplina', 'data_avaliacao')
        
        avaliacoes_data = []
        for av in avaliacoes_turma:
            avaliacoes_data.append({
                'id': av.pk,
                'nome': av.nome,
                'disciplina_id': av.disciplina.pk,
                'data_avaliacao': av.data_avaliacao.strftime('%Y-%m-%d') if av.data_avaliacao else None,
            })
        
        data = {
            'avaliacoes': avaliacoes_data,
            'curso': {
                'id': turma.curso.pk if turma.curso else None,
                'nome': turma.curso.nome if turma.curso else None,
                'codigo': turma.curso.codigo or '' if turma.curso else ''
            } if turma.curso else None,
            'instrutor': {
                'id': instrutor_id if instrutor_id is not None else None,
                'nome': instrutor_nome if instrutor_nome else None
            },
            'monitores': monitores,
            'disciplinas': disciplinas
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def obter_alunos_turma(request, turma_id):
    """Retorna lista de alunos da turma via AJAX"""
    from django.http import JsonResponse
    from militares.models import AlunoEnsino, AvaliacaoEnsino, NotaAvaliacao, BlocoDisciplinaTurma
    from datetime import date
    
    try:
        # Verificar se é para filtrar apenas alunos em recuperação
        disciplina_id = request.GET.get('disciplina') or request.GET.get('disciplina_id')
        apenas_recuperacao_param = request.GET.get('apenas_recuperacao', '').lower()
        apenas_recuperacao = apenas_recuperacao_param in ['true', '1', 'yes']
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'obter_alunos_turma - turma_id: {turma_id}, disciplina_id: {disciplina_id}, apenas_recuperacao: {apenas_recuperacao}')
        
        alunos = AlunoEnsino.objects.filter(
            turma_id=turma_id,
            situacao='ATIVO'
        ).select_related('militar', 'pessoa_externa').order_by('matricula')
        
        # Verificação de blocos removida - todos os alunos ativos são listados
        # Apenas alunos com status DESLIGADO não receberão notas
        
        # Se for para mostrar apenas alunos em recuperação, filtrar
        if apenas_recuperacao and disciplina_id:
            try:
                from militares.models import DisciplinaEnsino
                disciplina = DisciplinaEnsino.objects.get(pk=disciplina_id)
                media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
                
                # Obter número obrigatório de avaliações baseado na carga horária
                numero_avaliacoes_obrigatorio = disciplina.calcular_numero_avaliacoes_obrigatorio()
                
                # Buscar todas as avaliações regulares (não recuperação) da disciplina e turma
                avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
                    turma_id=turma_id,
                    disciplina_id=disciplina_id
                ).exclude(tipo='RECUPERACAO').order_by('data_avaliacao', 'id')
                
                # Se não houver avaliações regulares, não há como ter recuperação
                if not avaliacoes_regulares.exists():
                    logger.info(f'Nenhuma avaliação regular encontrada para disciplina {disciplina_id}')
                    alunos = alunos.none()  # Retornar queryset vazio
                else:
                    # Calcular média de cada aluno e filtrar apenas os em recuperação
                    alunos_em_recuperacao = []
                    avaliacoes_ordenadas = list(avaliacoes_regulares)
                    logger.info(f'Encontradas {len(avaliacoes_ordenadas)} avaliações regulares. Verificando {alunos.count()} alunos.')
                    
                    for aluno in alunos:
                        # Buscar notas das avaliações regulares ordenadas por data
                        notas_avaliacoes = NotaAvaliacao.objects.filter(
                            avaliacao__in=avaliacoes_ordenadas,
                            aluno=aluno
                        ).select_related('avaliacao').order_by('avaliacao__data_avaliacao', 'avaliacao__id')
                        
                        # Organizar notas por posição (1ª, 2ª, 3ª, 4ª)
                        notas_por_posicao = [None, None, None, None]
                        for nota_obj in notas_avaliacoes:
                            try:
                                posicao = avaliacoes_ordenadas.index(nota_obj.avaliacao)
                                if posicao < 4:
                                    notas_por_posicao[posicao] = nota_obj.nota
                            except ValueError:
                                pass
                        
                        # Calcular média aritmética simples apenas das verificações obrigatórias
                        verificacoes_obrigatorias_com_notas = []
                        for i in range(numero_avaliacoes_obrigatorio):
                            if notas_por_posicao[i] is not None:
                                verificacoes_obrigatorias_com_notas.append(float(notas_por_posicao[i]))
                        
                        # Só considerar em recuperação se tiver todas as notas obrigatórias
                        if len(verificacoes_obrigatorias_com_notas) == numero_avaliacoes_obrigatorio:
                            media_final = sum(verificacoes_obrigatorias_com_notas) / len(verificacoes_obrigatorias_com_notas)
                            
                            # Verificar se está em recuperação (média final menor que a mínima)
                            if media_final < media_minima:
                                alunos_em_recuperacao.append(aluno.pk)
                                logger.debug(f'Aluno {aluno.pk} em recuperação: média {media_final:.2f} < {media_minima}')
                    
                    logger.info(f'Total de alunos em recuperação: {len(alunos_em_recuperacao)}')
                    # Filtrar apenas alunos em recuperação
                    alunos = alunos.filter(pk__in=alunos_em_recuperacao)
            except DisciplinaEnsino.DoesNotExist:
                # Se disciplina não existir, retornar queryset vazio para recuperação
                if apenas_recuperacao:
                    alunos = alunos.none()
                pass
        
        alunos_data = []
        for aluno in alunos:
            nome = ''
            if aluno.militar:
                nome = f"{aluno.militar.get_posto_graduacao_display()} {aluno.militar.nome_completo}"
            elif aluno.pessoa_externa:
                nome = aluno.pessoa_externa.nome_completo
            elif aluno.nome_outra_forca:
                nome = aluno.nome_outra_forca
            elif aluno.nome_civil:
                nome = aluno.nome_civil
            else:
                nome = str(aluno)
            
            alunos_data.append({
                'id': aluno.pk,
                'nome': nome,
                'matricula': aluno.matricula or ''
            })
        
        return JsonResponse({'alunos': alunos_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def obter_ultimo_horario_dia(request, quadro_id, dia_semana):
    """Retorna o último horário de fim do dia para preencher automaticamente o próximo horário"""
    from django.http import JsonResponse
    from militares.models import QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal
    
    try:
        quadro = get_object_or_404(QuadroTrabalhoSemanal, pk=quadro_id)
        
        # Buscar a última aula do dia ordenada por hora_fim
        ultima_aula = AulaQuadroTrabalhoSemanal.objects.filter(
            quadro=quadro,
            dia_semana=dia_semana
        ).order_by('-hora_fim', '-hora_inicio').first()
        
        if ultima_aula and ultima_aula.hora_fim:
            return JsonResponse({
                'hora_fim': ultima_aula.hora_fim.strftime('%H:%M'),
                'existe_aula': True
            })
        else:
            return JsonResponse({
                'hora_fim': None,
                'existe_aula': False
            })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)


@login_required
def obter_dados_disciplina(request, disciplina_id):
    """Retorna dados da disciplina via AJAX"""
    from django.http import JsonResponse
    from militares.models import DisciplinaEnsino
    
    # Verificar se é requisição AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Se não estiver autenticado e for AJAX, retornar JSON em vez de redirecionar
    if not request.user.is_authenticated and is_ajax:
        return JsonResponse({
            'error': 'Usuário não autenticado',
            'redirect': '/login/'
        }, status=401)
    
    try:
        disciplina = DisciplinaEnsino.objects.select_related(
            'instrutor_responsavel_militar',
            'instrutor_responsavel_externo'
        ).filter(pk=disciplina_id).first()
        
        if not disciplina:
            return JsonResponse({
                'error': 'Disciplina não encontrada',
                'disciplina_id': disciplina_id
            }, status=404)
        
        # Buscar instrutor responsável (militar ou externo)
        instrutor_id = None
        instrutor_nome = None
        instrutor_tipo = None
        instrutor_info = None
        instrutor_campo = None
        
        if disciplina.instrutor_responsavel_militar:
            instrutor_id = disciplina.instrutor_responsavel_militar.pk
            instrutor_nome = f"{disciplina.instrutor_responsavel_militar.get_posto_graduacao_display()} {disciplina.instrutor_responsavel_militar.nome_completo}"
            instrutor_tipo = 'BOMBEIRO'
            instrutor_campo = 'instrutor_militar'  # Campo do formulário a ser preenchido
        elif disciplina.instrutor_responsavel_externo:
            instrutor_externo = disciplina.instrutor_responsavel_externo
            instrutor_id = instrutor_externo.pk
            instrutor_tipo = instrutor_externo.tipo_instrutor if hasattr(instrutor_externo, 'tipo_instrutor') else 'EXTERNO'
            instrutor_campo = 'instrutor_externo'  # Campo do formulário a ser preenchido
            
            # Buscar nome completo baseado no tipo
            if hasattr(instrutor_externo, 'get_nome_completo'):
                instrutor_nome = instrutor_externo.get_nome_completo()
            else:
                instrutor_nome = str(instrutor_externo)
            
            # Se for de outra força, incluir posto
            if instrutor_tipo == 'OUTRA_FORCA' and hasattr(instrutor_externo, 'posto_outra_forca') and instrutor_externo.posto_outra_forca:
                posto = instrutor_externo.get_posto_outra_forca_display()
                instrutor_nome = f"{posto} {instrutor_nome}".strip()
            
            # Informações adicionais para exibição
            instrutor_info = {
                'tipo': instrutor_tipo,
                'nome': instrutor_nome,
                'forca_armada': getattr(instrutor_externo, 'forca_armada', None),
                'instituicao': getattr(instrutor_externo, 'instituicao_outra_forca', None) or getattr(instrutor_externo, 'instituicao_civil', None),
            }
        
        # Buscar monitores da disciplina
        monitores = []
        # Monitores militares da disciplina
        for monitor_militar in disciplina.monitores_militares.all():
            monitores.append({
                'id': monitor_militar.pk,
                'nome': f"{monitor_militar.get_posto_graduacao_display()} {monitor_militar.nome_completo}",
                'tipo': 'militar'
            })
        
        # Monitores externos da disciplina
        for monitor_externo in disciplina.monitores_externos.all():
            nome_monitor = ''
            if hasattr(monitor_externo, 'get_nome_completo'):
                nome_monitor = monitor_externo.get_nome_completo()
            elif hasattr(monitor_externo, 'nome_completo'):
                nome_monitor = monitor_externo.nome_completo
            elif hasattr(monitor_externo, 'nome'):
                nome_monitor = monitor_externo.nome
            else:
                nome_monitor = str(monitor_externo)
            
            monitores.append({
                'id': monitor_externo.pk,
                'nome': nome_monitor,
                'tipo': 'externo'
            })
        
        # Montar objeto instrutor para retorno
        instrutor_data = None
        if instrutor_id is not None:
            instrutor_data = {
                'id': instrutor_id,
                'nome': instrutor_nome,
                'tipo': instrutor_tipo,
                'campo': instrutor_campo
            }
            if instrutor_info:
                instrutor_data['info'] = instrutor_info
        
        # Buscar carga horária total da disciplina
        carga_horaria_total_disciplina = disciplina.carga_horaria_total if hasattr(disciplina, 'carga_horaria_total') else (disciplina.carga_horaria if hasattr(disciplina, 'carga_horaria') else None)
        
        # Calcular carga horária já cadastrada no quadro atual (se houver quadro_id na requisição)
        carga_horaria_cadastrada = 0
        ultima_aula_acumulado = None  # Acumulado da última aula adicionada
        quadro_id = request.GET.get('quadro_id')
        if quadro_id:
            try:
                from militares.models import QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal
                quadro = QuadroTrabalhoSemanal.objects.filter(pk=quadro_id).first()
                if quadro and quadro.turma:
                    # Buscar todos os QTS anteriores da mesma turma (ordenados por número do quadro)
                    # Isso garante que a carga horária continue de onde parou no QTS anterior
                    quadros_anteriores = QuadroTrabalhoSemanal.objects.filter(
                        turma=quadro.turma
                    ).filter(
                        Q(numero_quadro__lt=quadro.numero_quadro) | 
                        Q(numero_quadro=quadro.numero_quadro, data_inicio_semana__lt=quadro.data_inicio_semana)
                    ).order_by('numero_quadro', 'data_inicio_semana')
                    
                    # Calcular carga horária acumulada de todos os QTS anteriores
                    carga_horaria_cadastrada = 0
                    acumulado_total = 0
                    
                    # Buscar todas as aulas da disciplina em todos os QTS anteriores
                    todas_aulas_anteriores = AulaQuadroTrabalhoSemanal.objects.filter(
                        quadro__in=quadros_anteriores,
                        disciplina=disciplina,
                        tipo_atividade='AULA'
                    ).select_related('quadro').order_by('quadro__numero_quadro', 'quadro__data_inicio_semana', 'dia_semana', 'hora_inicio', 'ordem')
                    
                    # Calcular acumulado progressivo considerando todos os QTS anteriores
                    dias_semana_ordem = {'SEGUNDA': 1, 'TERCA': 2, 'QUARTA': 3, 'QUINTA': 4, 'SEXTA': 5, 'SABADO': 6, 'DOMINGO': 7}
                    
                    for aula in todas_aulas_anteriores:
                        if aula.horas_aula:
                            horas = float(aula.horas_aula)
                            carga_horaria_cadastrada += horas
                            acumulado_total += horas
                            # Armazenar o acumulado da última aula dos QTS anteriores
                            ultima_aula_acumulado = acumulado_total
                    
                    # Agora buscar aulas do QTS atual para calcular último horário e atualizar acumulado
                    aulas_quadro_atual = AulaQuadroTrabalhoSemanal.objects.filter(
                        quadro=quadro,
                        disciplina=disciplina,
                        tipo_atividade='AULA'
                    ).order_by('dia_semana', 'hora_inicio', 'ordem')
                    
                    # Adicionar aulas do QTS atual ao acumulado
                    for aula in aulas_quadro_atual:
                        if aula.horas_aula:
                            horas = float(aula.horas_aula)
                            carga_horaria_cadastrada += horas
                            acumulado_total += horas
                            # Atualizar o acumulado da última aula (incluindo QTS atual)
                            ultima_aula_acumulado = acumulado_total
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao calcular carga horária acumulada: {str(e)}', exc_info=True)
                pass
        
        # Calcular número de avaliações permitidas baseado na carga horária
        numero_avaliacoes_permitidas = disciplina.calcular_numero_avaliacoes_obrigatorio()
        
        # Verificar avaliações já criadas (se turma_id for fornecido)
        # Excluir da lista as avaliações que já foram criadas, mesmo sem notas
        avaliacoes_criadas = []
        turma_id = request.GET.get('turma_id')
        if turma_id:
            try:
                from militares.models import AvaliacaoEnsino, TurmaEnsino
                turma = TurmaEnsino.objects.get(pk=turma_id)
                
                # Buscar avaliações regulares (não recuperação) desta disciplina nesta turma
                avaliacoes_existentes = AvaliacaoEnsino.objects.filter(
                    turma=turma,
                    disciplina=disciplina
                ).exclude(tipo='RECUPERACAO').order_by('data_avaliacao', 'id')
                
                # Para cada avaliação existente, determinar sua posição e adicionar à lista
                for avaliacao in avaliacoes_existentes:
                    # Determinar posição da avaliação (1ª, 2ª, 3ª, 4ª)
                    # Contar avaliações anteriores ordenadas por data
                    avaliacoes_anteriores = AvaliacaoEnsino.objects.filter(
                        turma=turma,
                        disciplina=disciplina
                    ).exclude(tipo='RECUPERACAO').filter(
                        Q(data_avaliacao__lt=avaliacao.data_avaliacao) |
                        Q(data_avaliacao=avaliacao.data_avaliacao, id__lt=avaliacao.id)
                    ).count()
                    
                    posicao = avaliacoes_anteriores + 1
                    if posicao <= 4 and posicao not in avaliacoes_criadas:
                        avaliacoes_criadas.append(posicao)
            except (TurmaEnsino.DoesNotExist, ValueError):
                pass
        
        data = {
            'instrutor': {
                'id': instrutor_id if instrutor_id is not None else None,
                'nome': instrutor_nome if instrutor_nome else None,
                'tipo': instrutor_tipo if instrutor_tipo else None,
                'info': instrutor_info if instrutor_info else None,
                'campo': instrutor_campo  # 'instrutor_militar' ou 'instrutor_externo'
            },
            'monitores': monitores,
            'carga_horaria_total': carga_horaria_total_disciplina,
            'carga_horaria_cadastrada': round(carga_horaria_cadastrada, 2),
            'ultima_aula_acumulado': round(ultima_aula_acumulado, 2) if ultima_aula_acumulado is not None else None,
            'numero_avaliacoes_permitidas': numero_avaliacoes_permitidas,
            'carga_horaria': disciplina.carga_horaria if hasattr(disciplina, 'carga_horaria') else None,
            'avaliacoes_criadas': avaliacoes_criadas  # Lista de posições (1, 2, 3, 4) que já foram criadas
        }
        
        return JsonResponse(data)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao obter dados da disciplina {disciplina_id}: {str(e)}', exc_info=True)
        return JsonResponse({
            'error': str(e),
            'disciplina_id': disciplina_id
        }, status=400)


@login_required
def criar_aula(request):
    """Cria uma nova aula"""
    from militares.models import FrequenciaAula, AlunoEnsino, TurmaEnsino
    from datetime import datetime, timedelta
    
    if request.method == 'POST':
        form = AulaEnsinoForm(request.POST, request.FILES, user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        if form.is_valid():
            aula = form.save(commit=False)
            if _eh_coordenador_ou_supervisor(request.user) and aula.turma and not _usuario_vinculado_turma(request.user, aula.turma):
                messages.error(request, 'Acesso negado. Você só pode gerar aulas para turmas em que está vinculado.')
                return redirect('militares:ensino_aulas_listar')
            
            # Se horas_aula foi informado, calcular hora_fim automaticamente
            # (sobrescreve o valor do formulário se horas_aula foi informado)
            horas_aula_str = request.POST.get('horas_aula', '')
            if horas_aula_str and aula.hora_inicio:
                try:
                    horas_aula = float(horas_aula_str)
                    if horas_aula > 0:
                        # Calcular hora_fim: 1 hora-aula = 45 minutos
                        minutos_totais = horas_aula * 45
                        # Converter hora_inicio para datetime para calcular
                        inicio_datetime = datetime.combine(aula.data_aula, aula.hora_inicio)
                        fim_datetime = inicio_datetime + timedelta(minutes=minutos_totais)
                        aula.hora_fim = fim_datetime.time()
                except (ValueError, TypeError):
                    pass  # Se não conseguir converter, manter hora_fim como está
            
            aula.save()
            
            # Processar frequências se houver turma selecionada
            if aula.turma:
                alunos_turma = AlunoEnsino.objects.filter(turma=aula.turma, situacao='ATIVO')
                for aluno in alunos_turma:
                    presenca = request.POST.get(f'presenca_{aluno.pk}')
                    if presenca:
                        justificativa = request.POST.get(f'justificativa_{aluno.pk}', '')
                        hora_entrada_str = request.POST.get(f'hora_entrada_{aluno.pk}', '')
                        hora_saida_str = request.POST.get(f'hora_saida_{aluno.pk}', '')
                        
                        # Converter strings de hora para objetos Time
                        hora_entrada = None
                        hora_saida = None
                        if hora_entrada_str:
                            try:
                                hora_entrada = datetime.strptime(hora_entrada_str, '%H:%M').time()
                            except:
                                pass
                        if hora_saida_str:
                            try:
                                hora_saida = datetime.strptime(hora_saida_str, '%H:%M').time()
                            except:
                                pass
                        
                        # Criar frequência
                        FrequenciaAula.objects.create(
                            aula=aula,
                            aluno=aluno,
                            presenca=presenca,
                            justificativa=justificativa or None,
                            hora_entrada=hora_entrada,
                            hora_saida=hora_saida,
                        )
            
            messages.success(request, f'Aula criada com sucesso!')
            return redirect('militares:ensino_aula_detalhes', pk=aula.pk)
    else:
        form = AulaEnsinoForm(user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        
        # Pré-selecionar turma se fornecida via GET
        turma_id = request.GET.get('turma_id')
        if turma_id:
            try:
                turma = TurmaEnsino.objects.get(pk=turma_id)
                form.initial['turma'] = turma.pk
            except TurmaEnsino.DoesNotExist:
                pass
    
    return render(request, 'militares/ensino/aulas/criar.html', {'form': form})


@login_required
def editar_aula(request, pk):
    """Edita uma aula existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar aulas.')
        return redirect('militares:ensino_aulas_listar')
    
    from militares.models import FrequenciaAula, AlunoEnsino
    from datetime import datetime
    
    aula = get_object_or_404(AulaEnsino, pk=pk)
    if _eh_coordenador_ou_supervisor(request.user) and aula.turma and not _usuario_vinculado_turma(request.user, aula.turma):
        messages.error(request, 'Acesso negado. Você só pode editar aulas de turmas em que está vinculado.')
        return redirect('militares:ensino_aulas_listar')
    
    # Inicializar variáveis que serão usadas no contexto
    alunos_turma = []
    alunos_com_frequencia = []
    frequencias_dict = {}
    
    if request.method == 'POST':
        form = AulaEnsinoForm(request.POST, request.FILES, instance=aula, user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        if form.is_valid():
            aula = form.save()
            
            # Processar frequências se houver turma selecionada
            if aula.turma:
                alunos_turma = AlunoEnsino.objects.filter(turma=aula.turma, situacao='ATIVO')
                frequencias_processadas = 0
                
                for aluno in alunos_turma:
                    presenca = request.POST.get(f'presenca_{aluno.pk}')
                    
                    # Processar mesmo se presenca estiver vazio (pode ser para limpar)
                    justificativa = request.POST.get(f'justificativa_{aluno.pk}', '').strip()
                    hora_entrada_str = request.POST.get(f'hora_entrada_{aluno.pk}', '').strip()
                    hora_saida_str = request.POST.get(f'hora_saida_{aluno.pk}', '').strip()
                    
                    # Converter strings de hora para objetos Time
                    hora_entrada = None
                    hora_saida = None
                    if hora_entrada_str:
                        try:
                            hora_entrada = datetime.strptime(hora_entrada_str, '%H:%M').time()
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter hora_entrada para aluno {aluno.pk}: {e}")
                            pass
                    if hora_saida_str:
                        try:
                            hora_saida = datetime.strptime(hora_saida_str, '%H:%M').time()
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao converter hora_saida para aluno {aluno.pk}: {e}")
                            pass
                    
                    # Se presenca foi enviada, processar
                    if presenca:
                        # Buscar ou criar frequência
                        frequencia, created = FrequenciaAula.objects.get_or_create(
                            aula=aula,
                            aluno=aluno,
                            defaults={
                                'presenca': presenca,
                                'justificativa': justificativa or None,
                                'hora_entrada': hora_entrada,
                                'hora_saida': hora_saida,
                            }
                        )
                        
                        # Se já existia, atualizar
                        if not created:
                            frequencia.presenca = presenca
                            frequencia.justificativa = justificativa or None
                            frequencia.hora_entrada = hora_entrada
                            frequencia.hora_saida = hora_saida
                            frequencia.save()
                        
                        frequencias_processadas += 1
                
                print(f"Frequências processadas: {frequencias_processadas} de {alunos_turma.count()} alunos")
            
            messages.success(request, f'Aula atualizada com sucesso!')
            return redirect('militares:ensino_aula_detalhes', pk=aula.pk)
        else:
            # Formulário inválido - buscar alunos para exibir no template
            # Mostrar erros do formulário
            print(f"Formulário inválido. Erros: {form.errors}")
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            
            if aula.turma:
                alunos_turma = AlunoEnsino.objects.filter(
                    turma=aula.turma,
                    situacao='ATIVO'
                ).select_related('militar', 'pessoa_externa').order_by('matricula')
                
                frequencias_existentes = FrequenciaAula.objects.filter(aula=aula).select_related('aluno')
                frequencias_dict = {freq.aluno_id: freq for freq in frequencias_existentes}
                
                # Criar lista de alunos com suas frequências para facilitar no template
                for aluno in alunos_turma:
                    frequencia = frequencias_dict.get(aluno.pk)
                    alunos_com_frequencia.append({
                        'aluno': aluno,
                        'frequencia': frequencia
                    })
    else:
        form = AulaEnsinoForm(instance=aula)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        
        # Buscar alunos e frequências para o template
        if aula.turma:
            alunos_turma = AlunoEnsino.objects.filter(
                turma=aula.turma,
                situacao='ATIVO'
            ).select_related('militar', 'pessoa_externa').order_by('matricula')
            
            frequencias_existentes = FrequenciaAula.objects.filter(aula=aula).select_related('aluno')
            frequencias_dict = {freq.aluno_id: freq for freq in frequencias_existentes}
            
            # Criar lista de alunos com suas frequências para facilitar no template
            for aluno in alunos_turma:
                frequencia = frequencias_dict.get(aluno.pk)
                alunos_com_frequencia.append({
                    'aluno': aluno,
                    'frequencia': frequencia
                })
    
    return render(request, 'militares/ensino/aulas/editar.html', {
        'form': form, 
        'aula': aula,
        'alunos_turma': alunos_turma,
        'alunos_com_frequencia': alunos_com_frequencia,
        'frequencias_existentes': frequencias_dict,
    })


@login_required
def deletar_aula(request, pk):
    """Deleta uma aula - apenas para superusuários"""
    aula = get_object_or_404(AulaEnsino, pk=pk)
    
    # Verificar se o usuário é superusuário
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para excluir aulas. Apenas superusuários podem realizar esta ação.')
        return redirect('militares:ensino_aula_detalhes', pk=aula.pk)
    
    if request.method == 'POST':
        try:
            # Informações para mensagem
            disciplina_nome = aula.disciplina.nome if aula.disciplina else 'N/A'
            data_aula = aula.data_aula.strftime('%d/%m/%Y') if aula.data_aula else 'N/A'
            
            # Verificar se há frequências vinculadas
            frequencias_count = FrequenciaAula.objects.filter(aula=aula).count()
            
            # Deletar a aula (as frequências serão deletadas em cascata se CASCADE estiver configurado)
            aula.delete()
            
            messages.success(request, f'Aula de {disciplina_nome} do dia {data_aula} excluída com sucesso!')
            return redirect('militares:ensino_aulas_listar')
        except Exception as e:
            error_message = str(e)
            messages.error(request, f'Erro ao excluir aula: {error_message}')
            return redirect('militares:ensino_aula_detalhes', pk=aula.pk)
    
    # GET request - redirecionar para detalhes
    return redirect('militares:ensino_aula_detalhes', pk=aula.pk)


@login_required
def detalhes_aula(request, pk):
    """Detalhes completos de uma aula"""
    from militares.models import FrequenciaAula, AlunoEnsino
    
    aula = get_object_or_404(AulaEnsino, pk=pk)
    
    # Buscar todos os alunos da turma
    alunos_turma = AlunoEnsino.objects.filter(
        turma=aula.turma,
        situacao='ATIVO'
    ).select_related('militar', 'pessoa_externa').order_by('matricula')
    
    # Frequências existentes (criar um dicionário para acesso rápido)
    frequencias_existentes = FrequenciaAula.objects.filter(aula=aula).select_related('aluno')
    frequencias_dict = {freq.aluno_id: freq for freq in frequencias_existentes}
    
    # Criar lista de alunos com suas frequências para facilitar no template
    alunos_com_frequencia = []
    for aluno in alunos_turma:
        frequencia = frequencias_dict.get(aluno.pk)
        alunos_com_frequencia.append({
            'aluno': aluno,
            'frequencia': frequencia
        })
    
    # Estatísticas - contar baseado nas frequências registradas
    total_alunos = alunos_turma.count()
    
    # Contar frequências registradas (não apenas existentes, mas todas as situações)
    presentes = 0
    faltas = 0
    faltas_justificadas = 0
    atrasos = 0
    saidas_antecipadas = 0
    nao_registrados = 0
    
    for item in alunos_com_frequencia:
        if item['frequencia']:
            presenca = item['frequencia'].presenca
            if presenca == 'PRESENTE':
                presentes += 1
            elif presenca == 'FALTA':
                faltas += 1
            elif presenca == 'FALTA_JUSTIFICADA':
                faltas_justificadas += 1
            elif presenca == 'ATRASO':
                atrasos += 1
            elif presenca == 'SAIDA_ANTECIPADA':
                saidas_antecipadas += 1
        else:
            nao_registrados += 1
    
    context = {
        'aula': aula,
        'alunos_turma': alunos_turma,
        'alunos_com_frequencia': alunos_com_frequencia,
        'frequencias_existentes': frequencias_dict,
        'total_alunos': total_alunos,
        'presentes': presentes,
        'faltas': faltas,
        'faltas_justificadas': faltas_justificadas,
        'atrasos': atrasos,
        'saidas_antecipadas': saidas_antecipadas,
        'nao_registrados': nao_registrados,
        'PRESENCA_CHOICES': FrequenciaAula.PRESENCA_CHOICES,
    }
    return render(request, 'militares/ensino/aulas/detalhes.html', context)


@login_required
def registrar_chamada_aula(request, pk):
    """Registra ou atualiza a chamada (frequência) de uma aula"""
    from militares.models import FrequenciaAula, AlunoEnsino
    from django.http import JsonResponse
    from datetime import datetime
    
    aula = get_object_or_404(AulaEnsino, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if _eh_coordenador_ou_supervisor(request.user) and aula.turma and not _usuario_vinculado_turma(request.user, aula.turma):
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': 'Acesso negado. Você só pode registrar frequências em turmas em que está vinculado.'}, status=403)
        messages.error(request, 'Acesso negado. Você só pode registrar frequências em turmas em que está vinculado.')
        return redirect('militares:ensino_aulas_listar')
    
    if request.method == 'POST':
        try:
            # Processar frequências enviadas via AJAX (formato: aluno_id|presenca|justificativa|hora_entrada|hora_saida)
            frequencias_data = request.POST.getlist('frequencias[]')
            
            if frequencias_data:
                # Processar dados do formato AJAX
                for freq_data in frequencias_data:
                    parts = freq_data.split('|')
                    if len(parts) >= 2:
                        aluno_id = parts[0]
                        presenca = parts[1]
                        justificativa = parts[2] if len(parts) > 2 else ''
                        hora_entrada_str = parts[3] if len(parts) > 3 and parts[3] else None
                        hora_saida_str = parts[4] if len(parts) > 4 and parts[4] else None
                        
                        # Converter strings de hora para objetos Time
                        hora_entrada = None
                        hora_saida = None
                        if hora_entrada_str:
                            try:
                                hora_entrada = datetime.strptime(hora_entrada_str, '%H:%M').time()
                            except:
                                pass
                        if hora_saida_str:
                            try:
                                hora_saida = datetime.strptime(hora_saida_str, '%H:%M').time()
                            except:
                                pass
                        
                        try:
                            aluno = AlunoEnsino.objects.get(pk=aluno_id, turma=aula.turma)
                            
                            # Buscar ou criar frequência
                            frequencia, created = FrequenciaAula.objects.get_or_create(
                                aula=aula,
                                aluno=aluno,
                                defaults={
                                    'presenca': presenca,
                                    'justificativa': justificativa or None,
                                    'hora_entrada': hora_entrada,
                                    'hora_saida': hora_saida,
                                }
                            )
                            
                            # Se já existia, atualizar
                            if not created:
                                frequencia.presenca = presenca
                                frequencia.justificativa = justificativa or None
                                frequencia.hora_entrada = hora_entrada
                                frequencia.hora_saida = hora_saida
                                frequencia.save()
                                
                        except AlunoEnsino.DoesNotExist:
                            continue
            else:
                # Processar dados do formulário HTML direto (campos individuais)
                alunos_turma = AlunoEnsino.objects.filter(turma=aula.turma, situacao='ATIVO')
                for aluno in alunos_turma:
                    presenca = request.POST.get(f'presenca_{aluno.pk}')
                    if presenca:
                        justificativa = request.POST.get(f'justificativa_{aluno.pk}', '')
                        hora_entrada_str = request.POST.get(f'hora_entrada_{aluno.pk}', '')
                        hora_saida_str = request.POST.get(f'hora_saida_{aluno.pk}', '')
                        
                        # Converter strings de hora para objetos Time
                        hora_entrada = None
                        hora_saida = None
                        if hora_entrada_str:
                            try:
                                hora_entrada = datetime.strptime(hora_entrada_str, '%H:%M').time()
                            except:
                                pass
                        if hora_saida_str:
                            try:
                                hora_saida = datetime.strptime(hora_saida_str, '%H:%M').time()
                            except:
                                pass
                        
                        # Buscar ou criar frequência
                        frequencia, created = FrequenciaAula.objects.get_or_create(
                            aula=aula,
                            aluno=aluno,
                            defaults={
                                'presenca': presenca,
                                'justificativa': justificativa or None,
                                'hora_entrada': hora_entrada,
                                'hora_saida': hora_saida,
                            }
                        )
                        
                        # Se já existia, atualizar
                        if not created:
                            frequencia.presenca = presenca
                            frequencia.justificativa = justificativa or None
                            frequencia.hora_entrada = hora_entrada
                            frequencia.hora_saida = hora_saida
                            frequencia.save()
            
            messages.success(request, 'Chamada registrada com sucesso!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Chamada registrada com sucesso!'})
            
            return redirect('militares:ensino_aula_detalhes', pk=aula.pk)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erro ao registrar chamada: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
            return redirect('militares:ensino_aula_detalhes', pk=aula.pk)
    
    return redirect('militares:ensino_aula_detalhes', pk=aula.pk)


# ============================================================================
# 9. AVALIAÇÕES E NOTAS (Relacionadas a Turma, Disciplina e Aluno)
# ============================================================================

@login_required
def listar_avaliacoes(request):
    """Lista todas as avaliações"""
    avaliacoes = AvaliacaoEnsino.objects.select_related('disciplina', 'turma').all()
    
    busca = request.GET.get('busca', '')
    tipo = request.GET.get('tipo', '')
    turma_id = request.GET.get('turma', '')
    disciplina_id = request.GET.get('disciplina', '')
    
    if busca:
        avaliacoes = avaliacoes.filter(
            Q(nome__icontains=busca) |
            Q(descricao__icontains=busca) |
            Q(disciplina__nome__icontains=busca)
        )
    
    if tipo:
        avaliacoes = avaliacoes.filter(tipo=tipo)
    
    if turma_id:
        avaliacoes = avaliacoes.filter(turma_id=turma_id)
    if disciplina_id:
        avaliacoes = avaliacoes.filter(disciplina_id=disciplina_id)
    
    # Calcular posição de cada avaliação (1ª, 2ª, 3ª, 4ª)
    # Agrupar por turma e disciplina para otimizar queries
    avaliacoes_list = list(avaliacoes)
    
    # Criar um dicionário para cache de posições por (turma_id, disciplina_id)
    cache_posicoes = {}
    
    # Processar cada avaliação mantendo a ordem original
    avaliacoes_com_posicao = []
    for avaliacao in avaliacoes_list:
        chave = (avaliacao.turma_id, avaliacao.disciplina_id)
        
        # Se for recuperação, mostrar "Recuperação"
        if avaliacao.tipo == 'RECUPERACAO':
            posicao_texto = 'Recuperação'
        else:
            # Buscar posição do cache ou calcular
            if chave not in cache_posicoes:
                # Buscar todas as avaliações regulares (não recuperação) deste grupo, ordenadas por data
                avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
                    turma_id=avaliacao.turma_id,
                    disciplina_id=avaliacao.disciplina_id
                ).exclude(
                    tipo='RECUPERACAO'
                ).order_by('data_avaliacao', 'id')
                
                # Criar um dicionário de posições
                posicoes_dict = {}
                for idx, av in enumerate(avaliacoes_regulares, start=1):
                    posicoes_dict[av.pk] = idx
                
                cache_posicoes[chave] = posicoes_dict
            
            # Buscar posição no cache
            posicoes_dict = cache_posicoes[chave]
            posicao = posicoes_dict.get(avaliacao.pk, 0)
            
            if posicao == 0:
                # Se não encontrou, pode ser que a avaliação não esteja na lista (data None, etc)
                # Calcular manualmente
                avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
                    turma_id=avaliacao.turma_id,
                    disciplina_id=avaliacao.disciplina_id
                ).exclude(
                    tipo='RECUPERACAO'
                ).order_by('data_avaliacao', 'id')
                
                posicao = 1
                for av in avaliacoes_regulares:
                    if av.pk == avaliacao.pk:
                        break
                    posicao += 1
            
            # Formatar posição (1ª Avaliação, 2ª Avaliação, 3ª Avaliação, 4ª Avaliação)
            posicao_texto = f"{posicao}ª Avaliação"
        
        avaliacoes_com_posicao.append({
            'avaliacao': avaliacao,
            'posicao': posicao_texto
        })
    
    paginator = Paginator(avaliacoes_com_posicao, 20)
    page = request.GET.get('page')
    avaliacoes_paginadas = paginator.get_page(page)
    
    turmas = TurmaEnsino.objects.filter(ativa=True)
    is_instrutor_ensino = False
    try:
        militar = request.user.militar if hasattr(request.user, 'militar') else None
        if militar:
            from .models import InstrutorEnsino
            is_instrutor_ensino = InstrutorEnsino.objects.filter(militar=militar, ativo=True).exists()
    except Exception:
        pass
    try:
        if request.session.get('ensino_tipo') == 'instrutor':
            is_instrutor_ensino = True
    except Exception:
        pass
    
    context = {
        'avaliacoes': avaliacoes_paginadas,
        'turmas': turmas,
        'tipos': AvaliacaoEnsino.TIPO_AVALIACAO_CHOICES,
        'is_instrutor_ensino': is_instrutor_ensino,
    }
    return render(request, 'militares/ensino/avaliacoes/listar.html', context)


@login_required
def criar_avaliacao(request):
    """Cria uma nova avaliação"""
    turma_id = request.GET.get('turma_id')
    disciplina_id = None
    turma = None
    alunos = []
    posicao_avaliacao = None
    avaliacoes_existentes = []
    
    if request.method == 'POST':
        # Obter turma do POST para atualizar o queryset do formulário
        turma_post_id = request.POST.get('turma')
        
        # Criar o formulário com os dados do POST
        form = AvaliacaoEnsinoForm(request.POST, user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        
        # Se houver turma no POST, atualizar o queryset de disciplinas ANTES de validar
        if turma_post_id:
            try:
                turma_post = TurmaEnsino.objects.get(pk=turma_post_id)
                # Buscar disciplinas da turma e do curso
                disciplinas_turma = turma_post.disciplinas.all()
                disciplinas_ids = list(disciplinas_turma.values_list('pk', flat=True))
                
                if turma_post.curso:
                    from militares.models import DisciplinaCurso
                    disciplinas_curso = DisciplinaCurso.objects.filter(
                        curso=turma_post.curso
                    ).select_related('disciplina')
                    disciplinas_ids.extend([dc.disciplina.pk for dc in disciplinas_curso])
                
                # Atualizar o queryset de disciplinas no formulário
                from militares.models import DisciplinaEnsino
                form.fields['disciplina'].queryset = DisciplinaEnsino.objects.filter(
                    pk__in=disciplinas_ids
                ).distinct()
                
                # Buscar alunos da turma para exibir no template mesmo se houver erro
                alunos_queryset = AlunoEnsino.objects.filter(
                    turma=turma_post,
                    situacao='ATIVO'
                ).select_related('militar', 'pessoa_externa')
                
                # Verificar se é recuperação e filtrar alunos em recuperação
                posicao_avaliacao_post = request.POST.get('posicao_avaliacao')
                disciplina_post_id = request.POST.get('disciplina')
                
                if posicao_avaliacao_post == 'RECUPERACAO' and disciplina_post_id:
                    try:
                        disciplina_post = DisciplinaEnsino.objects.get(pk=disciplina_post_id)
                        media_minima = float(disciplina_post.media_minima_aprovacao) if disciplina_post.media_minima_aprovacao else 7.0
                        numero_avaliacoes_obrigatorio = disciplina_post.calcular_numero_avaliacoes_obrigatorio()
                        
                        # Buscar todas as avaliações regulares desta disciplina nesta turma
                        avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
                            turma=turma_post,
                            disciplina=disciplina_post
                        ).exclude(tipo='RECUPERACAO').order_by('data_avaliacao', 'id')
                        
                        # Calcular quais alunos ficaram em recuperação
                        alunos_em_recuperacao_ids = []
                        
                        for aluno in alunos_queryset:
                            # Buscar notas das avaliações regulares ordenadas por data
                            avaliacoes_ordenadas = list(avaliacoes_regulares)
                            notas_avaliacoes = NotaAvaliacao.objects.filter(
                                avaliacao__in=avaliacoes_ordenadas,
                                aluno=aluno
                            ).select_related('avaliacao').order_by('avaliacao__data_avaliacao', 'avaliacao__id')
                            
                            # Organizar notas por posição (1ª, 2ª, 3ª, 4ª)
                            notas_por_posicao = [None, None, None, None]
                            for nota_obj in notas_avaliacoes:
                                try:
                                    posicao = avaliacoes_ordenadas.index(nota_obj.avaliacao)
                                    if posicao < 4:
                                        notas_por_posicao[posicao] = nota_obj.nota
                                except ValueError:
                                    pass
                            
                            # Calcular média aritmética simples apenas das verificações obrigatórias
                            verificacoes_obrigatorias_com_notas = []
                            for i in range(numero_avaliacoes_obrigatorio):
                                if notas_por_posicao[i] is not None:
                                    verificacoes_obrigatorias_com_notas.append(float(notas_por_posicao[i]))
                            
                            # Só considerar em recuperação se tiver todas as notas obrigatórias
                            if len(verificacoes_obrigatorias_com_notas) == numero_avaliacoes_obrigatorio:
                                media_final = sum(verificacoes_obrigatorias_com_notas) / len(verificacoes_obrigatorias_com_notas)
                                
                                # Verificar se está em recuperação (média final menor que a mínima)
                                if media_final < media_minima:
                                    alunos_em_recuperacao_ids.append(aluno.pk)
                        
                        # Filtrar apenas alunos em recuperação
                        alunos_queryset = alunos_queryset.filter(pk__in=alunos_em_recuperacao_ids)
                    except DisciplinaEnsino.DoesNotExist:
                        pass
                
                # Verificação de blocos removida - todos os alunos ativos são processados
                # Apenas alunos com status DESLIGADO não receberão notas
                
                alunos = alunos_queryset.order_by('matricula')
                turma = turma_post
            except TurmaEnsino.DoesNotExist:
                pass
        
        if form.is_valid():
            try:
                # Obter posição da avaliação do formulário
                posicao_avaliacao = form.cleaned_data.get('posicao_avaliacao')
                
                # Salvar a avaliação
                avaliacao = form.save(commit=False)
                if _eh_coordenador_ou_supervisor(request.user) and avaliacao.turma and not _usuario_vinculado_turma(request.user, avaliacao.turma):
                    messages.error(request, 'Acesso negado. Você só pode gerar avaliações para turmas em que está vinculado.')
                    return redirect('militares:ensino_avaliacoes_listar')
                
                # Se for recuperação, definir o tipo como RECUPERACAO
                # Caso contrário, manter o tipo selecionado pelo usuário
                if posicao_avaliacao == 'RECUPERACAO':
                    avaliacao.tipo = 'RECUPERACAO'
                
                # Remover texto indesejado "ele se fez ouvir" se existir
                if avaliacao.nome and "ele se fez ouvir" in avaliacao.nome.lower():
                    avaliacao.nome = ""
                
                # Gerar nome automaticamente se não fornecido ou vazio
                if not avaliacao.nome or not avaliacao.nome.strip():
                    tipo_display = avaliacao.get_tipo_display()
                    tipo_verificacao_display = avaliacao.get_tipo_verificacao_display() if avaliacao.tipo_verificacao else ''
                    
                    if posicao_avaliacao == 'RECUPERACAO':
                        avaliacao.nome = f"Recuperação - {avaliacao.disciplina.nome}"
                    elif tipo_verificacao_display:
                        avaliacao.nome = f"{tipo_verificacao_display} - {tipo_display}"
                    else:
                        avaliacao.nome = f"{tipo_display} - {avaliacao.disciplina.nome}"
                
                avaliacao.save()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao salvar avaliação: {str(e)}', exc_info=True)
                messages.error(request, f'Erro ao salvar avaliação: {str(e)}')
                # Continuar para exibir o formulário com erro
                notas_preenchidas = {}
                for key, value in request.POST.items():
                    if key.startswith('nota_') and key != 'nota_maxima' and value.strip():
                        try:
                            aluno_id = int(key.replace('nota_', ''))
                            notas_preenchidas[aluno_id] = value.strip()
                        except (ValueError, AttributeError):
                            pass
                turmas = TurmaEnsino.objects.filter(ativa=True)
                context = {
                    'form': form,
                    'turmas': turmas,
                    'turma': turma,
                    'alunos': alunos,
                    'posicao_avaliacao': posicao_avaliacao,
                    'avaliacoes_existentes': avaliacoes_existentes if 'avaliacoes_existentes' in locals() else [],
                    'notas_preenchidas': notas_preenchidas,
                }
                return render(request, 'militares/ensino/avaliacoes/criar.html', context)
            
            # Processar notas se fornecidas
            turma = avaliacao.turma
            alunos = AlunoEnsino.objects.filter(turma=turma, situacao='ATIVO').select_related('militar', 'pessoa_externa')
            notas_salvas = 0
            notas_com_erro = []
            
            # Debug: verificar quais campos de nota estão no POST
            import logging
            logger = logging.getLogger(__name__)
            campos_nota = [key for key in request.POST.keys() if key.startswith('nota_') and key != 'nota_maxima']
            logger.info(f'Campos de nota encontrados no POST: {campos_nota}')
            logger.info(f'Total de campos de nota no POST: {len(campos_nota)}')
            logger.info(f'Total de alunos ativos na turma: {alunos.count()}')
            # Log de todos os campos POST para debug
            todos_campos_post = list(request.POST.keys())
            logger.info(f'Total de campos no POST: {len(todos_campos_post)}')
            logger.info(f'Primeiros 20 campos do POST: {todos_campos_post[:20]}')
            
            # Criar dicionário de IDs de alunos para busca rápida
            alunos_dict = {aluno.pk: aluno for aluno in alunos}
            
            # Processar todas as notas do POST
            for key in campos_nota:
                try:
                    aluno_id = int(key.replace('nota_', ''))
                    nota_value = request.POST.get(key, '').strip()
                    
                    if nota_value:
                        # Verificar se o aluno existe e está ativo
                        if aluno_id not in alunos_dict:
                            logger.warning(f'Aluno {aluno_id} não encontrado na lista de alunos ativos, ignorando nota')
                            continue
                        
                        aluno = alunos_dict[aluno_id]
                        
                        try:
                            nota_float = float(nota_value)
                            if nota_float < 0:
                                continue
                            if nota_float > float(avaliacao.nota_maxima):
                                notas_com_erro.append(f'{aluno.matricula}: nota {nota_float} excede o máximo {avaliacao.nota_maxima}')
                                continue
                            
                            nota_obj, created = NotaAvaliacao.objects.update_or_create(
                                avaliacao=avaliacao,
                                aluno=aluno,
                                defaults={
                                    'nota': nota_float,
                                    'lancado_por': request.user
                                }
                            )
                            notas_salvas += 1
                            logger.info(f'Nota salva: aluno={aluno.pk}, avaliacao={avaliacao.pk}, nota={nota_float}, created={created}')
                        except ValueError as e:
                            logger.error(f'Erro ao converter nota para float: {nota_value}, erro: {str(e)}')
                            notas_com_erro.append(f'{aluno.matricula}: valor inválido "{nota_value}"')
                        except Exception as e:
                            logger.error(f'Erro ao salvar nota para aluno {aluno.pk}: {str(e)}')
                            notas_com_erro.append(f'{aluno.matricula}: erro ao salvar')
                except (ValueError, KeyError) as e:
                    logger.warning(f'Erro ao processar campo de nota {key}: {str(e)}')
                    continue
            
            # Exibir mensagens de erro se houver
            if notas_com_erro:
                for erro in notas_com_erro:
                    messages.warning(request, erro)
            
            if notas_salvas > 0:
                messages.success(request, f'Avaliação {avaliacao.nome} criada e {notas_salvas} nota(s) lançada(s) com sucesso!')
            else:
                messages.success(request, f'Avaliação {avaliacao.nome} criada com sucesso!')
            
            try:
                return redirect('militares:ensino_avaliacao_detalhes', pk=avaliacao.pk)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao redirecionar após salvar avaliação: {str(e)}', exc_info=True)
                messages.error(request, f'Avaliação salva, mas houve erro ao redirecionar: {str(e)}')
                return redirect('militares:ensino_avaliacoes_listar')
        else:
            # Formulário inválido - exibir erros e manter dados
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'=== FORMULÁRIO INVÁLIDO ===')
            logger.error(f'Erros de validação do formulário: {form.errors}')
            logger.error(f'Dados do POST: {dict(request.POST)}')
            logger.error(f'Campos do formulário: {list(form.fields.keys())}')
            logger.error(f'Dados limpos: {form.cleaned_data if hasattr(form, "cleaned_data") else "N/A"}')
            logger.error(f'===========================')
            
            # Exibir mensagem de erro genérica
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            
            # Exibir erros específicos do formulário de forma mais detalhada
            erros_detalhados = []
            for field, errors in form.errors.items():
                for error in errors:
                    # Traduzir nomes de campos para português
                    field_name = field
                    field_translations = {
                        'turma': 'Turma',
                        'disciplina': 'Disciplina',
                        'tipo': 'Tipo de Avaliação',
                        'nome': 'Nome da Avaliação',
                        'data_avaliacao': 'Data da Avaliação',
                        'peso': 'Peso',
                        'nota_maxima': 'Nota Máxima',
                        'posicao_avaliacao': 'Posição da Avaliação',
                    }
                    field_display = field_translations.get(field, field.replace('_', ' ').title())
                    
                    error_msg = f'{field_display}: {error}'
                    messages.error(request, error_msg)
                    erros_detalhados.append(error_msg)
                    logger.error(f'Erro no campo {field}: {error}')
            
            # Adicionar todos os erros ao contexto para exibição detalhada
            if not erros_detalhados:
                erros_detalhados = ['Erro desconhecido ao validar o formulário']
            
            # Garantir que as variáveis estejam inicializadas mesmo com erro
            # As variáveis turma e alunos já foram definidas acima se turma_post_id existir
            # Mas precisamos garantir que avaliacoes_existentes esteja definida
            disciplina_id_post = request.POST.get('disciplina')
            if turma and disciplina_id_post:
                try:
                    disciplina = DisciplinaEnsino.objects.get(pk=disciplina_id_post)
                    avaliacoes_existentes = AvaliacaoEnsino.objects.filter(
                        turma=turma,
                        disciplina=disciplina
                    ).exclude(
                        tipo='RECUPERACAO'
                    ).order_by('data_avaliacao')
                    
                    posicao_avaliacao = avaliacoes_existentes.count() + 1
                    if posicao_avaliacao > 4:
                        posicao_avaliacao = None
                except (DisciplinaEnsino.DoesNotExist, ValueError):
                    avaliacoes_existentes = []
                    posicao_avaliacao = None
            else:
                avaliacoes_existentes = []
                posicao_avaliacao = None
            
            # Preservar valores das notas preenchidas para exibir após erro
            notas_preenchidas = {}
            for key, value in request.POST.items():
                if key.startswith('nota_') and key != 'nota_maxima' and value.strip():
                    try:
                        aluno_id = int(key.replace('nota_', ''))
                        notas_preenchidas[aluno_id] = value.strip()
                    except (ValueError, AttributeError):
                        pass
    else:
        form = AvaliacaoEnsinoForm(user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        # Pré-selecionar turma se fornecida via GET
        if turma_id:
            try:
                turma = TurmaEnsino.objects.get(pk=turma_id)
                # Passar a turma no initial para que o formulário carregue as disciplinas
                form = AvaliacaoEnsinoForm(initial={'turma': turma.pk}, user=request.user)
                
                # Buscar alunos da turma
                alunos_queryset = AlunoEnsino.objects.filter(
                    turma=turma,
                    situacao='ATIVO'
                ).select_related('militar', 'pessoa_externa')
                
                # Buscar disciplina_id se fornecido
                disciplina_id = request.GET.get('disciplina') or request.GET.get('disciplina_id')
                posicao_avaliacao_get = request.GET.get('posicao_avaliacao')
                
                if disciplina_id:
                    try:
                        disciplina = DisciplinaEnsino.objects.get(pk=disciplina_id)
                        form.initial['disciplina'] = disciplina.pk
                        
                        # Verificar se é recuperação e filtrar alunos em recuperação
                        if posicao_avaliacao_get == 'RECUPERACAO':
                            media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
                            numero_avaliacoes_obrigatorio = disciplina.calcular_numero_avaliacoes_obrigatorio()
                            
                            # Buscar todas as avaliações regulares desta disciplina nesta turma
                            avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
                                turma=turma,
                                disciplina=disciplina
                            ).exclude(tipo='RECUPERACAO').order_by('data_avaliacao', 'id')
                            
                            # Calcular quais alunos ficaram em recuperação
                            alunos_em_recuperacao_ids = []
                            
                            for aluno in alunos_queryset:
                                # Buscar notas das avaliações regulares ordenadas por data
                                avaliacoes_ordenadas = list(avaliacoes_regulares)
                                notas_avaliacoes = NotaAvaliacao.objects.filter(
                                    avaliacao__in=avaliacoes_ordenadas,
                                    aluno=aluno
                                ).select_related('avaliacao').order_by('avaliacao__data_avaliacao', 'avaliacao__id')
                                
                                # Organizar notas por posição (1ª, 2ª, 3ª, 4ª)
                                notas_por_posicao = [None, None, None, None]
                                for nota_obj in notas_avaliacoes:
                                    try:
                                        posicao = avaliacoes_ordenadas.index(nota_obj.avaliacao)
                                        if posicao < 4:
                                            notas_por_posicao[posicao] = nota_obj.nota
                                    except ValueError:
                                        pass
                                
                                # Calcular média aritmética simples apenas das verificações obrigatórias
                                verificacoes_obrigatorias_com_notas = []
                                for i in range(numero_avaliacoes_obrigatorio):
                                    if notas_por_posicao[i] is not None:
                                        verificacoes_obrigatorias_com_notas.append(float(notas_por_posicao[i]))
                                
                                # Só considerar em recuperação se tiver todas as notas obrigatórias
                                if len(verificacoes_obrigatorias_com_notas) == numero_avaliacoes_obrigatorio:
                                    media_final = sum(verificacoes_obrigatorias_com_notas) / len(verificacoes_obrigatorias_com_notas)
                                    
                                    # Verificar se está em recuperação (média final menor que a mínima)
                                    if media_final < media_minima:
                                        alunos_em_recuperacao_ids.append(aluno.pk)
                            
                            # Filtrar apenas alunos em recuperação
                            alunos_queryset = alunos_queryset.filter(pk__in=alunos_em_recuperacao_ids)
                        
                        # Verificação de blocos removida - todos os alunos ativos são listados
                        # Apenas alunos com status DESLIGADO não receberão notas
                        alunos = alunos_queryset.order_by('matricula')
                        
                        # Determinar posição da avaliação (1ª, 2ª, 3ª, 4ª)
                        # Buscar apenas avaliações regulares (não recuperação)
                        avaliacoes_existentes = AvaliacaoEnsino.objects.filter(
                            turma=turma,
                            disciplina=disciplina
                        ).exclude(
                            tipo='RECUPERACAO'
                        ).order_by('data_avaliacao')
                        
                        posicao_avaliacao = avaliacoes_existentes.count() + 1
                        if posicao_avaliacao > 4:
                            posicao_avaliacao = None  # Já tem 4 avaliações regulares
                    except DisciplinaEnsino.DoesNotExist:
                        alunos = alunos_queryset.order_by('matricula')
                else:
                    alunos = alunos_queryset.order_by('matricula')
            except TurmaEnsino.DoesNotExist:
                pass
    
    turmas = TurmaEnsino.objects.filter(ativa=True)
    
    # Garantir que notas_preenchidas esteja no contexto (vazio se não houver erro)
    if 'notas_preenchidas' not in locals():
        notas_preenchidas = {}
    
    context = {
        'form': form,
        'turmas': turmas,
        'turma': turma,
        'alunos': alunos,
        'posicao_avaliacao': posicao_avaliacao,
        'avaliacoes_existentes': avaliacoes_existentes,
        'notas_preenchidas': notas_preenchidas,
    }
    return render(request, 'militares/ensino/avaliacoes/criar.html', context)


@login_required
def detalhes_avaliacao(request, pk):
    """Detalhes completos de uma avaliação"""
    avaliacao = get_object_or_404(
        AvaliacaoEnsino.objects.select_related('disciplina', 'turma', 'turma__curso'),
        pk=pk
    )
    
    # Buscar alunos da turma
    alunos = AlunoEnsino.objects.filter(
        turma=avaliacao.turma, 
        situacao='ATIVO'
    ).select_related('militar', 'pessoa_externa')
    
    # Se for avaliação de recuperação, filtrar apenas alunos que ficaram em recuperação
    if avaliacao.tipo == 'RECUPERACAO':
        disciplina = avaliacao.disciplina
        turma = avaliacao.turma
        media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
        
        # Buscar todas as avaliações regulares desta disciplina nesta turma
        avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
            turma=turma,
            disciplina=disciplina,
            tipo__in=['AV1', 'AV2', 'AV3', 'AV4']
        ).order_by('data_avaliacao')
        
        # Buscar alunos que já receberam nota nesta avaliação de recuperação
        alunos_com_nota_recuperacao = NotaAvaliacao.objects.filter(
            avaliacao=avaliacao
        ).values_list('aluno_id', flat=True)
        
        # Calcular quais alunos ficaram em recuperação
        alunos_em_recuperacao_ids = list(alunos_com_nota_recuperacao)  # Incluir os que já têm nota
        
        for aluno in alunos:
            # Se já tem nota na recuperação, já está na lista
            if aluno.pk in alunos_em_recuperacao_ids:
                continue
                
            # Buscar notas das avaliações regulares
            notas_avaliacoes = NotaAvaliacao.objects.filter(
                avaliacao__in=avaliacoes_regulares,
                aluno=aluno
            ).select_related('avaliacao')
            
            if notas_avaliacoes.exists():
                # Calcular média ponderada
                soma_notas_pesos = 0
                soma_pesos = 0
                
                for nota_obj in notas_avaliacoes:
                    if nota_obj.nota is not None and nota_obj.avaliacao.peso > 0:
                        soma_notas_pesos += float(nota_obj.nota) * float(nota_obj.avaliacao.peso)
                        soma_pesos += float(nota_obj.avaliacao.peso)
                
                if soma_pesos > 0:
                    media_final = soma_notas_pesos / soma_pesos
                    
                    # Verificar se está em recuperação (média final menor que a mínima)
                    if media_final < media_minima:
                        alunos_em_recuperacao_ids.append(aluno.pk)
        
        # Filtrar apenas alunos em recuperação (incluindo os que já têm nota)
        alunos = alunos.filter(pk__in=alunos_em_recuperacao_ids)
    
    # Buscar notas dos alunos
    notas = NotaAvaliacao.objects.filter(
        avaliacao=avaliacao
    ).select_related('aluno', 'aluno__militar', 'aluno__pessoa_externa', 'lancado_por')
    
    notas_dict = {nota.aluno_id: nota for nota in notas}
    
    pedidos_revisao_map = {p.nota_avaliacao_id: p for p in PedidoRevisaoProva.objects.filter(nota_avaliacao__avaliacao=avaliacao)}
    alunos_com_notas = []
    for aluno in alunos:
        n = notas_dict.get(aluno.pk)
        alunos_com_notas.append({
            'aluno': aluno,
            'nota': n,
            'pedido_revisao': (pedidos_revisao_map.get(n.pk) if n else None),
        })
    
    # Calcular posição da avaliação (1ª, 2ª, 3ª, 4ª ou Recuperação)
    if avaliacao.tipo == 'RECUPERACAO':
        posicao_texto = 'Recuperação'
    else:
        # Buscar todas as avaliações regulares (não recuperação) desta disciplina nesta turma, ordenadas por data
        avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
            turma=avaliacao.turma,
            disciplina=avaliacao.disciplina
        ).exclude(
            tipo='RECUPERACAO'
        ).order_by('data_avaliacao', 'id')
        
        # Encontrar a posição da avaliação atual
        posicao = 0
        for idx, av in enumerate(avaliacoes_regulares, start=1):
            if av.pk == avaliacao.pk:
                posicao = idx
                break
        
        # Formatar posição (1ª Avaliação, 2ª Avaliação, 3ª Avaliação, 4ª Avaliação)
        if posicao > 0:
            posicao_texto = f"{posicao}ª Avaliação"
        else:
            posicao_texto = "Avaliação"
    
    context = {
        'avaliacao': avaliacao,
        'alunos_com_notas': alunos_com_notas,
        'posicao_texto': posicao_texto,
    }
    return render(request, 'militares/ensino/avaliacoes/detalhes.html', context)


@login_required
def editar_avaliacao(request, pk):
    """Edita uma avaliação existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar avaliações.')
        return redirect('militares:ensino_avaliacoes_listar')
    
    avaliacao = get_object_or_404(AvaliacaoEnsino, pk=pk)
    if _eh_coordenador_ou_supervisor(request.user) and avaliacao.turma and not _usuario_vinculado_turma(request.user, avaliacao.turma):
        messages.error(request, 'Acesso negado. Você só pode editar avaliações de turmas em que está vinculado.')
        return redirect('militares:ensino_avaliacoes_listar')
    
    if request.method == 'POST':
        form = AvaliacaoEnsinoForm(request.POST, instance=avaliacao, user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        if form.is_valid():
            avaliacao = form.save(commit=False)
            
            # Obter posição da avaliação do formulário
            posicao_avaliacao = form.cleaned_data.get('posicao_avaliacao')
            
            # Se for recuperação, definir o tipo como RECUPERACAO
            if posicao_avaliacao == 'RECUPERACAO':
                avaliacao.tipo = 'RECUPERACAO'
            
            # Remover texto indesejado "ele se fez ouvir" se existir
            if avaliacao.nome and "ele se fez ouvir" in avaliacao.nome.lower():
                avaliacao.nome = ""
            
            # Gerar nome automaticamente se não fornecido ou vazio
            if not avaliacao.nome or not avaliacao.nome.strip():
                tipo_display = avaliacao.get_tipo_display()
                tipo_verificacao_display = avaliacao.get_tipo_verificacao_display() if avaliacao.tipo_verificacao else ''
                
                if posicao_avaliacao == 'RECUPERACAO':
                    avaliacao.nome = f"Recuperação - {avaliacao.disciplina.nome}"
                elif tipo_verificacao_display:
                    avaliacao.nome = f"{tipo_verificacao_display} - {tipo_display}"
                else:
                    avaliacao.nome = f"{tipo_display} - {avaliacao.disciplina.nome}"
            
            avaliacao.save()
            messages.success(request, f'Avaliação {avaliacao.nome} atualizada com sucesso!')
            return redirect('militares:ensino_avaliacao_detalhes', pk=avaliacao.pk)
    else:
        form = AvaliacaoEnsinoForm(instance=avaliacao, user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
    
    turmas = TurmaEnsino.objects.filter(ativa=True)
    context = {
        'form': form,
        'avaliacao': avaliacao,
        'turmas': turmas,
    }
    return render(request, 'militares/ensino/avaliacoes/editar.html', context)


@login_required
def deletar_avaliacao(request, pk):
    """Deleta uma avaliação - apenas para superusuários"""
    if not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para deletar avaliações.')
        return redirect('militares:ensino_avaliacoes_listar')
    
    avaliacao = get_object_or_404(AvaliacaoEnsino, pk=pk)
    
    if request.method == 'POST':
        nome_avaliacao = avaliacao.nome
        avaliacao.delete()
        messages.success(request, f'Avaliação "{nome_avaliacao}" deletada com sucesso!')
        
        # Se for requisição AJAX, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': f'Avaliação "{nome_avaliacao}" deletada com sucesso!'})
        
        return redirect('militares:ensino_avaliacoes_listar')
    
    # Contar quantas notas estão associadas a esta avaliação
    total_notas = NotaAvaliacao.objects.filter(avaliacao=avaliacao).count()
    
    context = {
        'avaliacao': avaliacao,
        'total_notas': total_notas,
    }
    
    # Se for requisição AJAX, retornar apenas o conteúdo do modal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        html = render_to_string('militares/ensino/avaliacoes/deletar_modal.html', context, request=request)
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/avaliacoes/deletar.html', context)


@login_required
def inserir_notas_disciplina(request, turma_id, disciplina_id):
    """Interface para inserir/editar notas de uma disciplina para todos os alunos da turma"""
    turma = get_object_or_404(TurmaEnsino, pk=turma_id)
    if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
        messages.error(request, 'Acesso negado. Você só pode acessar turmas em que está vinculado.')
        return redirect('militares:ensino_turmas_listar')
    disciplina = get_object_or_404(DisciplinaEnsino, pk=disciplina_id)
    
    # Verificar se a disciplina pertence à turma
    if disciplina not in turma.disciplinas.all():
        messages.error(request, 'Esta disciplina não está associada a esta turma.')
        return redirect('militares:ensino_turma_detalhes', pk=turma.pk)
    
    # Buscar alunos ativos da turma
    alunos = list(AlunoEnsino.objects.filter(
        turma=turma,
        situacao='ATIVO'
    ).select_related('militar', 'pessoa_externa').order_by('matricula'))
    
    # Buscar avaliações da disciplina na turma (ordenadas por data, excluindo recuperação)
    avaliacoes_queryset = AvaliacaoEnsino.objects.filter(
        turma=turma,
        disciplina=disciplina
    ).exclude(tipo='RECUPERACAO').order_by('data_avaliacao', 'id')[:4]  # Máximo 4 avaliações
    
    # Converter para lista para garantir que o queryset seja avaliado
    avaliacoes = list(avaliacoes_queryset)
    
    # Buscar notas existentes apenas para as avaliações que serão exibidas
    if avaliacoes:
        avaliacoes_ids = [a.pk for a in avaliacoes]
        notas_existentes = list(NotaAvaliacao.objects.filter(
            avaliacao_id__in=avaliacoes_ids
        ).select_related('avaliacao', 'aluno'))
    else:
        notas_existentes = []
    
    # Criar dicionário: notas_dict[avaliacao_id][aluno_id] = nota_obj
    notas_dict = {}
    for avaliacao in avaliacoes:
        notas_dict[avaliacao.pk] = {}
    
    # Preencher o dicionário com as notas existentes
    for nota in notas_existentes:
        avaliacao_id = nota.avaliacao.pk
        aluno_id = nota.aluno.pk
        if avaliacao_id in notas_dict:
            notas_dict[avaliacao_id][aluno_id] = nota
    
    if request.method == 'POST':
        # Processar notas
        notas_salvas = 0
        for avaliacao in avaliacoes:
            for aluno in alunos:
                nota_value = request.POST.get(f'nota_{avaliacao.pk}_{aluno.pk}', '').strip()
                if nota_value:
                    try:
                        nota_float = float(nota_value)
                        # Validar nota máxima
                        if nota_float < 0:
                            continue
                        if nota_float > float(avaliacao.nota_maxima):
                            messages.warning(request, f'Nota {nota_float} excede a nota máxima ({avaliacao.nota_maxima}) para {avaliacao.nome}.')
                            continue
                        
                        nota, created = NotaAvaliacao.objects.update_or_create(
                            avaliacao=avaliacao,
                            aluno=aluno,
                            defaults={
                                'nota': nota_float,
                                'lancado_por': request.user
                            }
                        )
                        notas_salvas += 1
                    except ValueError:
                        pass
        
        if notas_salvas > 0:
            messages.success(request, f'{notas_salvas} nota(s) salva(s) com sucesso!')
        else:
            messages.info(request, 'Nenhuma nota foi salva.')
        
        return redirect('militares:ensino_turma_detalhes', pk=turma.pk)
    
    # Criar lista de alunos com suas notas para cada avaliação
    alunos_com_notas = []
    for aluno in alunos:
        aluno_data = {
            'aluno': aluno,
            'notas_por_avaliacao': []
        }
        for avaliacao in avaliacoes:
            nota_obj = notas_dict.get(avaliacao.pk, {}).get(aluno.pk)
            aluno_data['notas_por_avaliacao'].append({
                'avaliacao': avaliacao,
                'nota_obj': nota_obj
            })
        alunos_com_notas.append(aluno_data)
    
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'alunos_com_notas': alunos_com_notas,
        'avaliacoes': avaliacoes,
    }
    return render(request, 'militares/ensino/turmas/inserir_notas_disciplina.html', context)


@login_required
def lancar_notas(request, avaliacao_id):
    """Lança notas para uma avaliação"""
    avaliacao = get_object_or_404(AvaliacaoEnsino, pk=avaliacao_id)
    turma = avaliacao.turma
    
    # Buscar alunos da turma
    alunos_queryset = AlunoEnsino.objects.filter(
        turma=turma, 
        situacao='ATIVO'
    ).select_related('militar', 'pessoa_externa')
    
    # Se for avaliação de recuperação, filtrar apenas alunos que ficaram em recuperação
    if avaliacao.tipo == 'RECUPERACAO':
        disciplina = avaliacao.disciplina
        media_minima = float(disciplina.media_minima_aprovacao) if disciplina.media_minima_aprovacao else 7.0
        
        # Obter número obrigatório de avaliações baseado na carga horária
        numero_avaliacoes_obrigatorio = disciplina.calcular_numero_avaliacoes_obrigatorio()
        
        # Buscar todas as avaliações regulares desta disciplina nesta turma (excluindo recuperação)
        avaliacoes_regulares = AvaliacaoEnsino.objects.filter(
            turma=turma,
            disciplina=disciplina
        ).exclude(tipo='RECUPERACAO').order_by('data_avaliacao', 'id')
        
        # Buscar alunos que já receberam nota nesta avaliação de recuperação
        alunos_com_nota_recuperacao = NotaAvaliacao.objects.filter(
            avaliacao=avaliacao
        ).values_list('aluno_id', flat=True)
        
        # Calcular quais alunos ficaram em recuperação
        alunos_em_recuperacao_ids = list(alunos_com_nota_recuperacao)  # Incluir os que já têm nota
        
        for aluno in alunos_queryset:
            # Se já tem nota na recuperação, já está na lista
            if aluno.pk in alunos_em_recuperacao_ids:
                continue
                
            # Buscar notas das avaliações regulares ordenadas por data
            avaliacoes_ordenadas = list(avaliacoes_regulares)
            notas_avaliacoes = NotaAvaliacao.objects.filter(
                avaliacao__in=avaliacoes_ordenadas,
                aluno=aluno
            ).select_related('avaliacao').order_by('avaliacao__data_avaliacao', 'avaliacao__id')
            
            # Organizar notas por posição (1ª, 2ª, 3ª, 4ª)
            notas_por_posicao = [None, None, None, None]
            for nota_obj in notas_avaliacoes:
                try:
                    posicao = avaliacoes_ordenadas.index(nota_obj.avaliacao)
                    if posicao < 4:
                        notas_por_posicao[posicao] = nota_obj.nota
                except ValueError:
                    pass
            
            # Calcular média aritmética simples apenas das verificações obrigatórias
            verificacoes_obrigatorias_com_notas = []
            for i in range(numero_avaliacoes_obrigatorio):
                if notas_por_posicao[i] is not None:
                    verificacoes_obrigatorias_com_notas.append(float(notas_por_posicao[i]))
            
            # Só considerar em recuperação se tiver todas as notas obrigatórias
            if len(verificacoes_obrigatorias_com_notas) == numero_avaliacoes_obrigatorio:
                media_final = sum(verificacoes_obrigatorias_com_notas) / len(verificacoes_obrigatorias_com_notas)
                
                # Verificar se está em recuperação (média final menor que a mínima)
                if media_final < media_minima:
                    alunos_em_recuperacao_ids.append(aluno.pk)
        
        # Filtrar apenas alunos em recuperação (incluindo os que já têm nota)
        alunos_queryset = alunos_queryset.filter(pk__in=alunos_em_recuperacao_ids)
    
    try:
        ordem_hierarquica = [codigo for codigo, _nome in POSTO_GRADUACAO_CHOICES]
        hierarquia_ordem = Case(
            *[When(militar__posto_graduacao=posto, then=Value(i)) for i, posto in enumerate(ordem_hierarquica)],
            default=Value(999),
            output_field=IntegerField(),
        )
        alunos_queryset = alunos_queryset.annotate(hierarquia_ordem=hierarquia_ordem).order_by(
            'hierarquia_ordem',
            'militar__data_promocao_atual',
            'militar__numeracao_antiguidade',
            'militar__nome_completo',
            'pessoa_externa__nome_completo',
            'nome_civil',
            'nome_outra_forca'
        )
    except Exception:
        alunos_queryset = alunos_queryset.order_by(
            'militar__nome_completo',
            'pessoa_externa__nome_completo',
            'nome_civil',
            'nome_outra_forca'
        )
    alunos = list(alunos_queryset)
    
    if request.method == 'POST':
        # Processar notas
        for aluno in alunos:
            nota_value = request.POST.get(f'nota_{aluno.pk}', '').strip()
            observacoes_value = request.POST.get(f'observacoes_{aluno.pk}', '').strip()
            if nota_value:
                try:
                    nota_float = float(nota_value)
                    nota, created = NotaAvaliacao.objects.update_or_create(
                        avaliacao=avaliacao,
                        aluno=aluno,
                        defaults={
                            'nota': nota_float,
                            'observacoes': observacoes_value or None,
                            'lancado_por': request.user
                        }
                    )
                except ValueError:
                    pass
        
        messages.success(request, 'Notas lançadas com sucesso!')
        return redirect('militares:ensino_avaliacao_detalhes', pk=avaliacao.pk)
    
    # Buscar notas existentes
    notas_existentes = list(NotaAvaliacao.objects.filter(
        avaliacao=avaliacao
    ).select_related('aluno'))
    
    # Criar dicionário usando aluno.pk como chave
    notas_dict = {}
    for nota in notas_existentes:
        notas_dict[nota.aluno.pk] = nota
    
    # Criar lista de alunos com suas notas
    alunos_com_notas = []
    for aluno in alunos:
        nota_obj = notas_dict.get(aluno.pk)
        alunos_com_notas.append({
            'aluno': aluno,
            'nota_obj': nota_obj
        })
    
    
    context = {
        'avaliacao': avaliacao,
        'alunos_com_notas': alunos_com_notas,
    }
    return render(request, 'militares/ensino/avaliacoes/lancar_notas.html', context)


# ============================================================================
# CERTIFICADOS (Relacionados a Aluno, Curso e Turma)
# ============================================================================

@login_required
def listar_certificados(request):
    """Lista todos os certificados"""
    certificados = CertificadoEnsino.objects.select_related('aluno', 'curso', 'turma').all()
    
    busca = request.GET.get('busca', '')
    status = request.GET.get('status', '')
    curso_id = request.GET.get('curso', '')
    
    if busca:
        certificados = certificados.filter(
            Q(numero__icontains=busca) |
            Q(aluno__matricula__icontains=busca) |
            Q(aluno__militar__nome_completo__icontains=busca)
        )
    
    if status:
        certificados = certificados.filter(status=status)
    
    if curso_id:
        certificados = certificados.filter(curso_id=curso_id)
    
    paginator = Paginator(certificados, 20)
    page = request.GET.get('page')
    certificados = paginator.get_page(page)
    
    cursos = CursoEnsino.objects.filter(ativo=True)
    
    context = {
        'certificados': certificados,
        'cursos': cursos,
        'status_choices': CertificadoEnsino.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/certificados/listar.html', context)


# ============================================================================
# DASHBOARD E FUNÇÕES AUXILIARES
# ============================================================================

@login_required
def dashboard_ensino(request):
    """Dashboard com indicadores do ensino"""
    
    # Estatísticas gerais
    total_cursos = CursoEnsino.objects.filter(ativo=True).count()
    total_turmas = TurmaEnsino.objects.filter(ativa=True).count()
    total_alunos = AlunoEnsino.objects.filter(situacao='ATIVO').count()
    total_instrutores = InstrutorEnsino.objects.filter(ativo=True).count()
    total_monitores = MonitorEnsino.objects.filter(ativo=True).count()
    total_pessoas_externas = PessoaExterna.objects.filter(ativo=True).count()
    
    # Turmas recentes
    turmas_recentes = TurmaEnsino.objects.filter(ativa=True).order_by('-data_inicio')[:5]
    
    # Alunos por situação
    alunos_por_situacao = AlunoEnsino.objects.values('situacao').annotate(
        total=Count('id')
    )
    
    # Disciplinas mais cursadas
    disciplinas_mais_cursadas = DisciplinaEnsino.objects.annotate(
        total_turmas=Count('aulas__turma', distinct=True)
    ).order_by('-total_turmas')[:5]
    
    # Solicitações de revisão agregadas
    revisoes_qs = PedidoRevisaoProva.objects.select_related(
        'nota_avaliacao__avaliacao__disciplina', 'aluno', 'instrutor_responsavel__militar'
    )
    pedidos_solicitados = revisoes_qs.filter(etapa='ALUNO_SOLICITOU').order_by('-data_solicitacao')[:20]
    pedidos_em_instrutor = revisoes_qs.filter(etapa='DESPACHADA_INSTRUTOR').order_by('-data_atualizacao')[:20]
    pedidos_instrutor_parecer = revisoes_qs.filter(etapa='PARECER_INSTRUTOR').order_by('-data_atualizacao')[:20]
    pedidos_recurso = revisoes_qs.filter(etapa='RECURSO_DIRETORIA').order_by('-data_atualizacao')[:20]
    pedidos_comissao = revisoes_qs.filter(etapa='COMISSAO_NOMEADA').order_by('-data_atualizacao')[:20]
    pedidos_finalizados = revisoes_qs.filter(etapa='PARECER_FINAL').order_by('-data_atualizacao')[:20]
    revisoes_contagem = {
        'ALUNO_SOLICITOU': revisoes_qs.filter(etapa='ALUNO_SOLICITOU').count(),
        'DESPACHADA_INSTRUTOR': revisoes_qs.filter(etapa='DESPACHADA_INSTRUTOR').count(),
        'PARECER_INSTRUTOR': revisoes_qs.filter(etapa='PARECER_INSTRUTOR').count(),
        'RECURSO_DIRETORIA': revisoes_qs.filter(etapa='RECURSO_DIRETORIA').count(),
        'COMISSAO_NOMEADA': revisoes_qs.filter(etapa='COMISSAO_NOMEADA').count(),
        'PARECER_FINAL': revisoes_qs.filter(etapa='PARECER_FINAL').count(),
    }

    context = {
        'total_cursos': total_cursos,
        'total_turmas': total_turmas,
        'total_alunos': total_alunos,
        'total_instrutores': total_instrutores,
        'total_monitores': total_monitores,
        'total_pessoas_externas': total_pessoas_externas,
        'turmas_recentes': turmas_recentes,
        'alunos_por_situacao': alunos_por_situacao,
        'disciplinas_mais_cursadas': disciplinas_mais_cursadas,
        # Revisões
        'revisoes_contagem': revisoes_contagem,
        'pedidos_solicitados': pedidos_solicitados,
        'pedidos_em_instrutor': pedidos_em_instrutor,
        'pedidos_instrutor_parecer': pedidos_instrutor_parecer,
        'pedidos_recurso': pedidos_recurso,
        'pedidos_comissao': pedidos_comissao,
        'pedidos_finalizados': pedidos_finalizados,
    }
    return render(request, 'militares/ensino/dashboard.html', context)


@login_required
def trocar_instrutor_monitor_disciplina(request, turma_id, disciplina_id):
    """Troca de instrutor e/ou monitores de uma disciplina com histórico"""
    from django.template.loader import render_to_string
    from django.http import HttpResponse, JsonResponse
    
    turma = get_object_or_404(TurmaEnsino, pk=turma_id)
    disciplina = get_object_or_404(DisciplinaEnsino, pk=disciplina_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            # Processar troca de instrutor
            novo_instrutor_value = request.POST.get('novo_instrutor', '').strip()
            data_fim_anterior = request.POST.get('data_fim_anterior')
            data_inicio_novo = request.POST.get('data_inicio_novo')
            data_inicio_anterior = request.POST.get('data_inicio_anterior', '')
            motivo_troca = request.POST.get('motivo_troca', '')
            
            if novo_instrutor_value and data_fim_anterior and data_inicio_novo and motivo_troca:
                # Registrar histórico do instrutor anterior
                instrutor_anterior_militar = disciplina.instrutor_responsavel_militar
                instrutor_anterior_externo = disciplina.instrutor_responsavel_externo
                
                # Atualizar instrutor
                if novo_instrutor_value.startswith('MILITAR_'):
                    instrutor_ensino_id = int(novo_instrutor_value.replace('MILITAR_', ''))
                    instrutor_ensino = InstrutorEnsino.objects.get(pk=instrutor_ensino_id)
                    instrutor_novo_militar = instrutor_ensino.militar if instrutor_ensino.militar else None
                    instrutor_novo_externo = None
                elif novo_instrutor_value.startswith('EXTERNO_'):
                    instrutor_ensino_id = int(novo_instrutor_value.replace('EXTERNO_', ''))
                    instrutor_ensino = InstrutorEnsino.objects.get(pk=instrutor_ensino_id)
                    instrutor_novo_externo = instrutor_ensino
                    instrutor_novo_militar = None
                else:
                    instrutor_novo_militar = None
                    instrutor_novo_externo = None
                
                # Criar histórico
                historico = HistoricoTrocaInstrutorDisciplina.objects.create(
                    disciplina=disciplina,
                    turma=turma,
                    instrutor_anterior_militar=instrutor_anterior_militar,
                    instrutor_anterior_externo=instrutor_anterior_externo,
                    instrutor_novo_militar=instrutor_novo_militar,
                    instrutor_novo_externo=instrutor_novo_externo,
                    data_inicio_anterior=datetime.strptime(data_inicio_anterior, '%Y-%m-%d').date() if data_inicio_anterior else None,
                    data_fim_anterior=datetime.strptime(data_fim_anterior, '%Y-%m-%d').date(),
                    data_inicio_novo=datetime.strptime(data_inicio_novo, '%Y-%m-%d').date(),
                    motivo_troca=motivo_troca,
                    usuario_que_trocou=request.user
                )
                
                # Atualizar disciplina
                disciplina.instrutor_responsavel_militar = instrutor_novo_militar
                disciplina.instrutor_responsavel_externo = instrutor_novo_externo
                disciplina.save(update_fields=['instrutor_responsavel_militar', 'instrutor_responsavel_externo'])
            
            # Processar troca de monitores
            monitores_removidos_militares = request.POST.getlist('monitores_removidos_militares[]')
            monitores_removidos_externos = request.POST.getlist('monitores_removidos_externos[]')
            monitores_adicionados_militares = request.POST.getlist('monitores_adicionados_militares[]')
            monitores_adicionados_externos = request.POST.getlist('monitores_adicionados_externos[]')
            
            # Processar monitores removidos
            for monitor_id in monitores_removidos_militares:
                try:
                    monitor_militar = Militar.objects.get(pk=monitor_id)
                    data_fim_monitor = request.POST.get(f'data_fim_monitor_militar_{monitor_id}', '')
                    data_inicio_novo_monitor = request.POST.get(f'data_inicio_novo_monitor_militar_{monitor_id}', '')
                    motivo_troca_monitor = request.POST.get(f'motivo_troca_monitor_militar_{monitor_id}', '')
                    
                    if data_fim_monitor and data_inicio_novo_monitor and motivo_troca_monitor:
                        # Buscar monitor novo
                        monitor_novo_id = request.POST.get(f'monitor_novo_militar_{monitor_id}', '')
                        monitor_novo_militar = None
                        if monitor_novo_id:
                            monitor_novo_militar = Militar.objects.get(pk=monitor_novo_id)
                        
                        HistoricoTrocaMonitorDisciplina.objects.create(
                            disciplina=disciplina,
                            turma=turma,
                            monitor_anterior_militar=monitor_militar,
                            monitor_anterior_externo=None,
                            monitor_novo_militar=monitor_novo_militar,
                            monitor_novo_externo=None,
                            data_inicio_anterior=None,
                            data_fim_anterior=datetime.strptime(data_fim_monitor, '%Y-%m-%d').date(),
                            data_inicio_novo=datetime.strptime(data_inicio_novo_monitor, '%Y-%m-%d').date(),
                            motivo_troca=motivo_troca_monitor,
                            usuario_que_trocou=request.user
                        )
                        
                        # Remover monitor
                        disciplina.monitores_militares.remove(monitor_militar)
                except (Militar.DoesNotExist, ValueError):
                    continue
            
            for monitor_id in monitores_removidos_externos:
                try:
                    monitor_externo = MonitorEnsino.objects.get(pk=monitor_id)
                    data_fim_monitor = request.POST.get(f'data_fim_monitor_externo_{monitor_id}', '')
                    data_inicio_novo_monitor = request.POST.get(f'data_inicio_novo_monitor_externo_{monitor_id}', '')
                    motivo_troca_monitor = request.POST.get(f'motivo_troca_monitor_externo_{monitor_id}', '')
                    
                    if data_fim_monitor and data_inicio_novo_monitor and motivo_troca_monitor:
                        # Buscar monitor novo
                        monitor_novo_id = request.POST.get(f'monitor_novo_externo_{monitor_id}', '')
                        monitor_novo_externo = None
                        if monitor_novo_id:
                            monitor_novo_externo = MonitorEnsino.objects.get(pk=monitor_novo_id)
                        
                        HistoricoTrocaMonitorDisciplina.objects.create(
                            disciplina=disciplina,
                            turma=turma,
                            monitor_anterior_militar=None,
                            monitor_anterior_externo=monitor_externo,
                            monitor_novo_militar=None,
                            monitor_novo_externo=monitor_novo_externo,
                            data_inicio_anterior=None,
                            data_fim_anterior=datetime.strptime(data_fim_monitor, '%Y-%m-%d').date(),
                            data_inicio_novo=datetime.strptime(data_inicio_novo_monitor, '%Y-%m-%d').date(),
                            motivo_troca=motivo_troca_monitor,
                            usuario_que_trocou=request.user
                        )
                        
                        # Remover monitor
                        disciplina.monitores_externos.remove(monitor_externo)
                except (MonitorEnsino.DoesNotExist, ValueError):
                    continue
            
            # Adicionar novos monitores
            for monitor_id in monitores_adicionados_militares:
                try:
                    monitor_ensino = MonitorEnsino.objects.get(pk=monitor_id)
                    if monitor_ensino.militar:
                        disciplina.monitores_militares.add(monitor_ensino.militar)
                except (MonitorEnsino.DoesNotExist, ValueError):
                    continue
            
            for monitor_id in monitores_adicionados_externos:
                try:
                    monitor_ensino = MonitorEnsino.objects.get(pk=monitor_id)
                    disciplina.monitores_externos.add(monitor_ensino)
                except (MonitorEnsino.DoesNotExist, ValueError):
                    continue
            
            messages.success(request, f'Instrutor/Monitores da disciplina {disciplina.nome} atualizados com sucesso!')
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'redirect': reverse('militares:ensino_turma_detalhes', kwargs={'pk': turma.pk})
                })
            
            return redirect('militares:ensino_turma_detalhes', pk=turma.pk)
            
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao trocar instrutor/monitor: {str(e)}'
                }, status=400)
            messages.error(request, f'Erro ao trocar instrutor/monitor: {str(e)}')
            return redirect('militares:ensino_turma_detalhes', pk=turma.pk)
    
    # GET - Mostrar formulário
    instrutores = InstrutorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
    monitores = MonitorEnsino.objects.filter(ativo=True).select_related('militar').order_by('militar__posto_graduacao', 'militar__nome_completo')
    
    # Buscar históricos
    historicos_instrutor = HistoricoTrocaInstrutorDisciplina.objects.filter(
        disciplina=disciplina, turma=turma
    ).order_by('-data_fim_anterior')
    
    historicos_monitor = HistoricoTrocaMonitorDisciplina.objects.filter(
        disciplina=disciplina, turma=turma
    ).order_by('-data_fim_anterior')
    
    context = {
        'turma': turma,
        'disciplina': disciplina,
        'instrutores': instrutores,
        'monitores': monitores,
        'postos_graduacao': POSTO_GRADUACAO_CHOICES,
        'historicos_instrutor': historicos_instrutor,
        'historicos_monitor': historicos_monitor,
    }
    
    if is_ajax:
        html = render_to_string('militares/ensino/turmas/trocar_instrutor_monitor_modal.html', context, request=request)
        return HttpResponse(html)
    
    return render(request, 'militares/ensino/turmas/trocar_instrutor_monitor.html', context)


@login_required
def desligar_aluno(request, pk):
    """Desliga um aluno da turma com upload de documentos"""
    from militares.models import AlunoEnsino, DocumentoAluno
    from django.http import JsonResponse
    from django.urls import reverse
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import os
    
    aluno = get_object_or_404(AlunoEnsino, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            data_desligamento = request.POST.get('data_desligamento')
            motivo_desligamento = request.POST.get('motivo_desligamento', '')
            
            if not data_desligamento:
                raise ValueError('Data de desligamento é obrigatória')
            
            if not motivo_desligamento or not motivo_desligamento.strip():
                raise ValueError('Motivo/Justificativa do desligamento é obrigatório')
            
            # Atualizar dados do aluno
            aluno.situacao = 'DESLIGADO'
            aluno.data_desligamento = datetime.strptime(data_desligamento, '%Y-%m-%d').date()
            aluno.motivo_desligamento = motivo_desligamento
            aluno.save(update_fields=['situacao', 'data_desligamento', 'motivo_desligamento'])
            
            # Processar documentos anexados
            tipos_documentos = request.POST.getlist('tipo_documento[]', [])
            nomes_documentos = request.POST.getlist('nome_documento[]', [])
            arquivos_documentos = request.FILES.getlist('arquivo_documento[]', [])
            
            documentos_criados = 0
            for idx, arquivo in enumerate(arquivos_documentos):
                if not arquivo:
                    continue
                
                try:
                    # Validar tamanho do arquivo (máximo 10MB)
                    if arquivo.size > 10 * 1024 * 1024:
                        continue  # Pular arquivos muito grandes
                    
                    # Obter tipo e nome do documento
                    tipo_doc = 'OUTROS'
                    if idx < len(tipos_documentos) and tipos_documentos[idx]:
                        tipo_valido = tipos_documentos[idx]
                        tipos_validos = [choice[0] for choice in DocumentoAluno.TIPO_DOCUMENTO_CHOICES]
                        if tipo_valido in tipos_validos:
                            tipo_doc = tipo_valido
                    
                    nome_doc = arquivo.name
                    if idx < len(nomes_documentos) and nomes_documentos[idx] and nomes_documentos[idx].strip():
                        nome_doc = nomes_documentos[idx].strip()[:200]
                    
                    # Criar documento
                    DocumentoAluno.objects.create(
                        aluno=aluno,
                        tipo=tipo_doc,
                        nome=nome_doc,
                        arquivo=arquivo,
                        descricao=f'Documento anexado no desligamento do aluno em {data_desligamento}',
                        data_emissao=datetime.strptime(data_desligamento, '%Y-%m-%d').date() if data_desligamento else None
                    )
                    documentos_criados += 1
                except Exception as doc_error:
                    # Continuar com outros documentos mesmo se um falhar
                    continue
            
            mensagem = f'Aluno {aluno.matricula} desligado com sucesso!'
            if documentos_criados > 0:
                mensagem += f' {documentos_criados} documento(s) anexado(s).'
            
            messages.success(request, mensagem)
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': mensagem,
                    'documentos_criados': documentos_criados
                })
            
            return redirect('militares:ensino_turma_detalhes', pk=aluno.turma.pk if aluno.turma else None)
            
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao desligar aluno: {str(e)}'
                }, status=400)
            messages.error(request, f'Erro ao desligar aluno: {str(e)}')
            return redirect('militares:ensino_turma_detalhes', pk=aluno.turma.pk if aluno.turma else None)
    
    # GET não deve acontecer, mas se acontecer, redirecionar
    return redirect('militares:ensino_turma_detalhes', pk=aluno.turma.pk if aluno.turma else None)


@login_required
def reativar_aluno(request, pk):
    """Reativa um aluno desligado da turma"""
    from militares.models import AlunoEnsino
    from django.http import JsonResponse
    from datetime import datetime
    
    aluno = get_object_or_404(AlunoEnsino, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            data_reativacao = request.POST.get('data_reativacao')
            motivo_reativacao = request.POST.get('motivo_reativacao', '')
            
            if not data_reativacao:
                raise ValueError('Data de reativação é obrigatória')
            
            if not motivo_reativacao or not motivo_reativacao.strip():
                raise ValueError('Motivo/Justificativa da reativação é obrigatório')
            
            # Verificar se o aluno está realmente desligado
            if aluno.situacao != 'DESLIGADO':
                raise ValueError('Este aluno não está desligado. Apenas alunos desligados podem ser reativados.')
            
            # Atualizar dados do aluno
            aluno.situacao = 'ATIVO'
            aluno.data_desligamento = None
            # Salvar o motivo da reativação no campo motivo_desligamento (ou criar um campo específico se necessário)
            # Por enquanto, vamos adicionar o motivo da reativação ao motivo_desligamento existente
            motivo_anterior = aluno.motivo_desligamento or ''
            if motivo_anterior:
                aluno.motivo_desligamento = f"{motivo_anterior} | REATIVADO em {data_reativacao}: {motivo_reativacao}"
            else:
                aluno.motivo_desligamento = f"REATIVADO em {data_reativacao}: {motivo_reativacao}"
            aluno.save(update_fields=['situacao', 'data_desligamento', 'motivo_desligamento'])
            
            mensagem = f'Aluno {aluno.matricula} reativado com sucesso!'
            messages.success(request, mensagem)
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': mensagem
                })
            
            return redirect('militares:ensino_turma_detalhes', pk=aluno.turma.pk if aluno.turma else None)
            
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao reativar aluno: {str(e)}'
                }, status=400)
            messages.error(request, f'Erro ao reativar aluno: {str(e)}')
            return redirect('militares:ensino_turma_detalhes', pk=aluno.turma.pk if aluno.turma else None)
    
    # GET não deve acontecer, mas se acontecer, redirecionar
    return redirect('militares:ensino_turma_detalhes', pk=aluno.turma.pk if aluno.turma else None)


# ============================================================================
# QUADRO DE TRABALHO SEMANAL
# ============================================================================

@login_required
def listar_quadros_trabalho_semanal(request):
    """Lista todos os quadros de trabalho semanal"""
    from militares.models import QuadroTrabalhoSemanal
    from django.db.models import Q
    
    quadros = QuadroTrabalhoSemanal.objects.select_related(
        'turma', 'turma__curso'
    ).prefetch_related('aulas', 'assinaturas__assinado_por').order_by(
        '-data_inicio_semana', 
        '-numero_quadro',
        '-id'  # Ordenação por ID decrescente para mostrar os mais recentes primeiro
    )
    
    # Filtros
    turma_id = request.GET.get('turma')
    data_inicio = request.GET.get('data_inicio')
    
    if turma_id:
        quadros = quadros.filter(turma_id=turma_id)
    
    if data_inicio:
        quadros = quadros.filter(data_inicio_semana=data_inicio)
    
    # Buscar turmas para filtro
    turmas = TurmaEnsino.objects.filter(ativa=True).order_by('identificacao')
    
    context = {
        'quadros': quadros,
        'turmas': turmas,
        'turma_filtro': int(turma_id) if turma_id else None,
        'data_inicio_filtro': data_inicio,
    }
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/listar.html', context)


@login_required
def criar_quadro_trabalho_semanal(request):
    """Cria um novo quadro de trabalho semanal"""
    from militares.models import QuadroTrabalhoSemanal
    from militares.forms_ensino import QuadroTrabalhoSemanalForm
    from datetime import datetime, timedelta
    
    if request.method == 'POST':
        form = QuadroTrabalhoSemanalForm(request.POST, user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        if form.is_valid():
            quadro = form.save(commit=False)
            if _eh_coordenador_ou_supervisor(request.user) and quadro.turma and not _usuario_vinculado_turma(request.user, quadro.turma):
                messages.error(request, 'Acesso negado. Você só pode gerar QTS para turmas em que está vinculado.')
                return redirect('militares:ensino_quadros_trabalho_semanal_listar')
            quadro.save()
            # Se data_fim_semana não foi informada, calcular automaticamente (6 dias após início)
            if not quadro.data_fim_semana and quadro.data_inicio_semana:
                quadro.data_fim_semana = quadro.data_inicio_semana + timedelta(days=6)
                quadro.save()
            messages.success(request, f'Quadro de trabalho semanal Nº {quadro.numero_quadro} criado com sucesso!')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
    else:
        form = QuadroTrabalhoSemanalForm(user=request.user)
        try:
            if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                from militares.models import TurmaEnsino
                form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
        except Exception:
            pass
        # Se houver turma_id na URL, pré-selecionar
        turma_id = request.GET.get('turma')
        if turma_id:
            try:
                form.fields['turma'].initial = int(turma_id)
                # Calcular próximo número do quadro
                ultimo_quadro = QuadroTrabalhoSemanal.objects.filter(turma_id=turma_id).order_by('-numero_quadro').first()
                if ultimo_quadro:
                    form.fields['numero_quadro'].initial = ultimo_quadro.numero_quadro + 1
                else:
                    form.fields['numero_quadro'].initial = 1
            except ValueError:
                pass
    
    if _eh_coordenador_ou_supervisor(request.user):
        turmas = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True).order_by('identificacao'))
    else:
        turmas = TurmaEnsino.objects.filter(ativa=True).order_by('identificacao')
    
    context = {
        'form': form,
        'turmas': turmas,
    }
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/criar.html', context)


@login_required
def editar_quadro_trabalho_semanal(request, pk):
    """Edita um quadro de trabalho semanal existente"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar quadros de trabalho semanal.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    from militares.models import QuadroTrabalhoSemanal, AssinaturaQTS, AulaQuadroTrabalhoSemanal
    from militares.forms_ensino import QuadroTrabalhoSemanalForm
    import re
    
    quadro_original = get_object_or_404(QuadroTrabalhoSemanal, pk=pk)
    if _eh_coordenador_ou_supervisor(request.user) and quadro_original.turma and not _usuario_vinculado_turma(request.user, quadro_original.turma):
        messages.error(request, 'Acesso negado. Você só pode editar QTS de turmas em que está vinculado.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    # Verificar se o QTS foi aprovado
    assinatura_aprovacao = quadro_original.assinaturas.filter(tipo_assinatura='APROVACAO').first()
    criar_aditamento = assinatura_aprovacao is not None
    
    if criar_aditamento:
        # Se foi aprovado, só pode criar aditamento quem aprovou ou superusuário
        if not request.user.is_superuser and assinatura_aprovacao.assinado_por != request.user:
            messages.error(request, 'Este quadro de trabalho semanal foi aprovado e só pode ser editado por quem o aprovou.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro_original.pk)
        
        # Verificar se já existe algum aditamento - se sim, não pode mais editar o original
        aditamentos_existentes = QuadroTrabalhoSemanal.objects.filter(
            quadro_original=quadro_original
        ).exists()
        
        if aditamentos_existentes:
            messages.error(request, 'Este QTS já possui aditamentos. Edite o último aditamento criado.')
            # Redirecionar para o último aditamento
            ultimo_aditamento = QuadroTrabalhoSemanal.objects.filter(
                quadro_original=quadro_original
            ).order_by('-numero_aditamento').first()
            if ultimo_aditamento:
                return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=ultimo_aditamento.pk)
            return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    if request.method == 'POST':
        if criar_aditamento:
            # Criar novo QTS como aditamento
            # Determinar o próximo número de aditamento (A01, A02, etc.)
            numero_base = quadro_original.numero_quadro or quadro_original.pk
            
            # Buscar todos os aditamentos deste QTS original
            # Aditamentos têm numero_quadro que começa com o número base seguido de A
            aditamentos_existentes = QuadroTrabalhoSemanal.objects.filter(
                turma=quadro_original.turma
            ).exclude(pk=quadro_original.pk)
            
            # Verificar se há aditamentos com padrão A01, A02, etc.
            # Como numero_quadro é Integer, vamos usar uma lógica diferente:
            # Vamos criar um campo de texto para armazenar o número completo
            # Por enquanto, vamos usar o ID do QTS original como base e criar um novo
            
            # Contar quantos aditamentos já existem para este QTS
            # Vamos usar uma relação ou campo adicional, mas por enquanto vamos contar pelos que têm o mesmo numero_quadro base
            # e estão na mesma turma e têm data_inicio_semana próxima
            
            # Solução: criar um novo QTS e usar o numero_quadro como string em um campo de texto
            # Mas como numero_quadro é Integer, vamos precisar de outra abordagem
            # Vou criar o novo QTS e depois ajustar a lógica de exibição
            
            # Por enquanto, vou criar um novo QTS com numero_quadro incrementado
            # e depois vamos ajustar para mostrar A01, A02, etc. na exibição
            
            # Usar a função criar_aditamento_qts que já implementa a lógica correta
            novo_quadro, _ = criar_aditamento_qts(quadro_original, request.user)
            if not novo_quadro:
                messages.error(request, 'Erro ao criar aditamento.')
                return redirect('militares:ensino_quadros_trabalho_semanal_listar')
            
            # Aplicar as alterações do formulário ao novo QTS
            form = QuadroTrabalhoSemanalForm(request.POST, instance=novo_quadro, user=request.user)
            try:
                if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                    from militares.models import TurmaEnsino
                    form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
            except Exception:
                pass
            if form.is_valid():
                novo_quadro = form.save()
                messages.success(request, f'Aditamento criado com sucesso! O QTS original foi mantido intacto.')
                return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=novo_quadro.pk)
            else:
                # Se o formulário for inválido, deletar o QTS criado
                novo_quadro.delete()
            form = QuadroTrabalhoSemanalForm(request.POST, user=request.user)
            try:
                if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                    from militares.models import TurmaEnsino
                    form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
            except Exception:
                pass
        else:
            # Se não foi aprovado, editar normalmente
            form = QuadroTrabalhoSemanalForm(request.POST, instance=quadro_original, user=request.user)
            try:
                if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                    from militares.models import TurmaEnsino
                    form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
            except Exception:
                pass
        if form.is_valid():
            form.save()
            messages.success(request, f'Quadro de trabalho semanal atualizado com sucesso!')
            return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    else:
        if criar_aditamento:
            # Criar formulário com dados do original para criar aditamento
            form = QuadroTrabalhoSemanalForm(instance=quadro_original, user=request.user)
            try:
                if _eh_coordenador_ou_supervisor(request.user) and 'turma' in form.fields:
                    from militares.models import TurmaEnsino
                    form.fields['turma'].queryset = _filtrar_turmas_vinculadas(request.user, TurmaEnsino.objects.filter(ativa=True))
            except Exception:
                pass
        else:
            form = QuadroTrabalhoSemanalForm(instance=quadro_original, user=request.user)
    
    context = {
        'form': form,
        'quadro': quadro_original,
        'criar_aditamento': criar_aditamento,
    }
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/editar.html', context)


@login_required
def deletar_quadro_trabalho_semanal(request, pk):
    """Deleta um quadro de trabalho semanal"""
    from militares.models import QuadroTrabalhoSemanal
    
    quadro = get_object_or_404(QuadroTrabalhoSemanal, pk=pk)
    if _eh_coordenador_ou_supervisor(request.user) and quadro.turma and not _usuario_vinculado_turma(request.user, quadro.turma):
        messages.error(request, 'Acesso negado. Você só pode excluir QTS de turmas em que está vinculado.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    if request.method == 'POST':
        turma_id = quadro.turma.pk
        quadro.delete()
        messages.success(request, 'Quadro de trabalho semanal deletado com sucesso!')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    context = {
        'quadro': quadro,
    }
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/deletar.html', context)


@login_required
def quadro_trabalho_semanal_pdf(request, pk):
    """Gera PDF do Quadro de Trabalho Semanal no padrão das certidões de férias e licenças"""
    import os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from django.http import FileResponse, HttpResponse
    from militares.models import QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal
    from datetime import datetime, timedelta, date, time
    from collections import defaultdict
    from django.db.models import Q
    import pytz
    
    quadro = get_object_or_404(
        QuadroTrabalhoSemanal.objects.select_related(
            'turma', 'turma__curso'
        ).prefetch_related(
            'aulas__disciplina', 'aulas__instrutor_militar', 'aulas__instrutor_externo',
            'assinaturas__assinado_por', 'assinaturas__assinado_por__militar'
        ),
        pk=pk
    )
    
    try:
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=1.5*cm, leftMargin=1.5*cm, 
                                topMargin=0.1*cm, bottomMargin=2*cm)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=16, spaceAfter=20)
        style_subtitle = ParagraphStyle('subtitle', parent=styles['Heading2'], alignment=1, fontSize=14, spaceAfter=15)
        style_center = ParagraphStyle('center', parent=styles['Normal'], alignment=1, fontSize=12)
        style_normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11)
        style_bold = ParagraphStyle('bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
        style_just = ParagraphStyle('just', parent=styles['Normal'], alignment=4, fontSize=11)
        style_small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=6)
        
        # Logo/Brasão centralizado
        logo_path = os.path.join('staticfiles', 'logo_cbmepi.png')
        if os.path.exists(logo_path):
            story.append(Image(logo_path, width=2.5*cm, height=2.5*cm, hAlign='CENTER'))
            story.append(Spacer(1, 6))
        
        # Cabeçalho institucional
        cabecalho = [
            "GOVERNO DO ESTADO DO PIAUÍ",
            "CORPO DE BOMBEIROS MILITAR DO ESTADO DO PIAUÍ",
            "DIRETORIA DE ENSINO, INSTRUÇÃO E PESQUISA",
            "Av. Miguel Rosa, 3515 - Bairro Piçarra, Teresina/PI, CEP 64001-490",
            "Telefone: (86)3216-1264 - http://www.cbm.pi.gov.br"
        ]
        for linha in cabecalho:
            story.append(Paragraph(linha, style_center))
        story.append(Spacer(1, 12 + 0.5*cm))
        
        # Título principal centralizado
        if quadro.numero_quadro:
            if quadro.numero_aditamento:
                numero_quadro = f" Nº {quadro.numero_quadro}{quadro.numero_aditamento}"
            else:
                numero_quadro = f" Nº {quadro.numero_quadro}"
        else:
            numero_quadro = ""
        story.append(Paragraph(f"<u>QUADRO DE TRABALHO SEMANAL{numero_quadro}</u>", style_title))
        story.append(Spacer(1, 6))
        
        # Nome do curso centralizado abaixo do título
        if quadro.turma and quadro.turma.curso:
            curso_nome = quadro.turma.curso.nome or '-'
            story.append(Paragraph(curso_nome, ParagraphStyle('curso_titulo', parent=styles['Normal'], fontSize=12, alignment=1, spaceAfter=5, fontName='Helvetica-Bold')))
        
        # Turma centralizada abaixo do curso
        if quadro.turma:
            turma_texto = f"Turma: {quadro.turma.identificacao or '-'}"
            story.append(Paragraph(turma_texto, ParagraphStyle('turma_centralizada', parent=styles['Normal'], fontSize=11, alignment=1, spaceAfter=8, fontName='Helvetica')))
        
        meses_extenso = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        
        # Preparar informações - Período e Local em uma linha compacta
        info_texto_parts = []
        if quadro.data_inicio_semana and quadro.data_fim_semana:
            data_inicio = quadro.data_inicio_semana
            data_fim = quadro.data_fim_semana
            data_inicio_extenso = f"{data_inicio.day} de {meses_extenso[data_inicio.month]} de {data_inicio.year}"
            data_fim_extenso = f"{data_fim.day} de {meses_extenso[data_fim.month]} de {data_fim.year}"
            periodo_extenso = f"{data_inicio_extenso} a {data_fim_extenso}"
            info_texto_parts.append(f"<b>Período:</b> {periodo_extenso}")
        
        if quadro.local:
            info_texto_parts.append(f"<b>Local:</b> {quadro.local}")
        
        # Adicionar informações em uma linha, separadas por " | "
        if info_texto_parts:
            info_texto = " | ".join(info_texto_parts)
            story.append(Paragraph(info_texto, ParagraphStyle('info_compacta', parent=styles['Normal'], fontSize=9, alignment=0, spaceAfter=5, spaceBefore=0, leading=10)))
            story.append(Spacer(1, 10))
        
        # Buscar todas as aulas do quadro
        aulas = quadro.aulas.all().order_by('dia_semana', 'hora_inicio', 'ordem')
        
        # Calcular carga horária acumulada por disciplina (considerando QTS anteriores)
        dias_semana_ordem = {'SEGUNDA': 1, 'TERCA': 2, 'QUARTA': 3, 'QUINTA': 4, 'SEXTA': 5, 'SABADO': 6, 'DOMINGO': 7}
        
        # Buscar todos os QTS anteriores da mesma turma
        quadros_anteriores = QuadroTrabalhoSemanal.objects.filter(
            turma=quadro.turma
        ).filter(
            Q(numero_quadro__lt=quadro.numero_quadro) | 
            Q(numero_quadro=quadro.numero_quadro, data_inicio_semana__lt=quadro.data_inicio_semana)
        ).order_by('numero_quadro', 'data_inicio_semana')
        
        # Buscar todas as aulas da disciplina em todos os QTS anteriores e atual
        todas_aulas_disciplina = list(AulaQuadroTrabalhoSemanal.objects.filter(
            Q(quadro__in=quadros_anteriores) | Q(quadro=quadro),
            tipo_atividade='AULA',
            disciplina__isnull=False
        ).select_related('disciplina', 'quadro'))
        
        # Ordenar manualmente para garantir ordem correta
        todas_aulas_disciplina.sort(key=lambda a: (
            a.quadro.numero_quadro if a.quadro else 999,
            a.quadro.data_inicio_semana if a.quadro and a.quadro.data_inicio_semana else date.max,
            a.data if a.data else (a.quadro.data_inicio_semana if a.quadro and a.quadro.data_inicio_semana else date.max),
            dias_semana_ordem.get(a.dia_semana, 99),
            a.hora_inicio if a.hora_inicio else time.max,
            a.ordem or 0
        ))
        
        # Calcular acumulado progressivo por disciplina
        carga_horaria_acumulada_por_aula = {}
        acumulado_por_disciplina = {}
        
        for aula in todas_aulas_disciplina:
            disciplina_id = aula.disciplina.pk
            
            # Inicializar acumulado da disciplina se necessário
            if disciplina_id not in acumulado_por_disciplina:
                carga_total = getattr(aula.disciplina, 'carga_horaria', None) or getattr(aula.disciplina, 'carga_horaria_total', None)
                acumulado_por_disciplina[disciplina_id] = {
                    'acumulado': 0,
                    'total_disciplina': carga_total
                }
            
            # Adicionar horas da aula atual ao acumulado
            if aula.horas_aula:
                acumulado_por_disciplina[disciplina_id]['acumulado'] += float(aula.horas_aula)
            
            # Armazenar o acumulado apenas para aulas do QTS atual
            if aula.quadro_id == quadro.pk:
                carga_horaria_acumulada_por_aula[aula.pk] = {
                    'acumulado': acumulado_por_disciplina[disciplina_id]['acumulado'],
                    'total_disciplina': acumulado_por_disciplina[disciplina_id]['total_disciplina']
                }
        
        # Organizar aulas por dia da semana e horário
        dias_semana_list = ['SEGUNDA', 'TERCA', 'QUARTA', 'QUINTA', 'SEXTA', 'SABADO', 'DOMINGO']
        dias_semana_display = {
            'SEGUNDA': 'Segunda-feira',
            'TERCA': 'Terça-feira',
            'QUARTA': 'Quarta-feira',
            'QUINTA': 'Quinta-feira',
            'SEXTA': 'Sexta-feira',
            'SABADO': 'Sábado',
            'DOMINGO': 'Domingo'
        }
        
        # Calcular datas de cada dia da semana
        dias_semana_datas = {}
        if quadro.data_inicio_semana:
            data_atual = quadro.data_inicio_semana
            days_since_monday = data_atual.weekday()
            data_segunda = data_atual - timedelta(days=days_since_monday)
            
            for idx, dia in enumerate(dias_semana_list):
                dias_semana_datas[dia] = data_segunda + timedelta(days=idx)
        
        # Organizar aulas em tabela
        tabela_aulas = {}
        horarios_unicos = set()
        dias_com_dados = set()  # Dias que têm aulas ou dados
        
        for aula in aulas:
            horario_key = f"{aula.hora_inicio.strftime('%H:%M')}-{aula.hora_fim.strftime('%H:%M')}"
            if horario_key not in tabela_aulas:
                tabela_aulas[horario_key] = {dia: [] for dia in dias_semana_list}
            tabela_aulas[horario_key][aula.dia_semana].append(aula)
            horarios_unicos.add(horario_key)
            dias_com_dados.add(aula.dia_semana)  # Marcar dia como tendo dados
        
        # Classificar horários por período e ordenar
        def classificar_periodo(horario_str):
            """Classifica o horário em manhã, tarde ou noite"""
            try:
                hora_inicio_str = horario_str.split('-')[0]
                hora = int(hora_inicio_str.split(':')[0])
                if hora < 12:
                    return (0, horario_str)  # Manhã
                elif hora < 18:
                    return (1, horario_str)  # Tarde
                else:
                    return (2, horario_str)  # Noite
            except:
                return (3, horario_str)  # Erro na classificação
        
        horarios_ordenados = sorted(horarios_unicos, key=classificar_periodo)
        
        # Filtrar apenas dias que têm dados, mantendo a ordem original
        dias_com_dados_ordenados = [dia for dia in dias_semana_list if dia in dias_com_dados]
        
        # Se não houver aulas, não criar tabela
        if not dias_com_dados_ordenados:
            story.append(Paragraph("Nenhuma aula cadastrada para este quadro.", style_normal))
        else:
            # Criar tabela do quadro semanal apenas com dias que têm dados
            # Cabeçalho: Horário | Dias com dados (nome + data)
            cabecalho_horario = Paragraph('Horário<br/>(h/a)', ParagraphStyle('header', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', alignment=1))
            cabecalho_dias = []
            for dia in dias_com_dados_ordenados:
                data_dia = ''
                if quadro.data_inicio_semana and dia in dias_semana_datas:
                    data_dia_obj = dias_semana_datas[dia]
                    data_dia = data_dia_obj.strftime('%d/%m')
                cabecalho_dia = f"{dias_semana_display[dia]}<br/>{data_dia}" if data_dia else dias_semana_display[dia]
                cabecalho_dias.append(Paragraph(cabecalho_dia, ParagraphStyle('header', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', alignment=1)))
            
            quadro_data = [[cabecalho_horario] + cabecalho_dias]
            
            # Variáveis para controlar separadores
            periodo_atual = None
            ultimo_periodo = None
            linhas_separadoras = []  # Índices das linhas separadoras
            
            # Adicionar linhas por horário
            for horario in horarios_ordenados:
                # Determinar período do horário atual
                try:
                    hora_inicio_str = horario.split('-')[0]
                    hora = int(hora_inicio_str.split(':')[0])
                    if hora < 12:
                        periodo_atual = 'MANHÃ'
                    elif hora < 18:
                        periodo_atual = 'TARDE'
                    else:
                        periodo_atual = 'NOITE'
                except:
                    periodo_atual = None
                
                # Adicionar linha separadora se mudou de período (mesclando todas as colunas)
                if periodo_atual and periodo_atual != ultimo_periodo:
                    linha_separadora = [Paragraph(f"<b>{periodo_atual}</b>", ParagraphStyle('separador', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=1))]
                    # Adicionar células vazias para completar a linha (serão mescladas depois)
                    linha_separadora.extend([Paragraph("", ParagraphStyle('separador', parent=styles['Normal'], fontSize=10))] * len(dias_com_dados_ordenados))
                    quadro_data.append(linha_separadora)
                    linhas_separadoras.append(len(quadro_data) - 1)  # Guardar índice da linha separadora
                    ultimo_periodo = periodo_atual
                linha = [Paragraph(horario, ParagraphStyle('horario', parent=styles['Normal'], fontSize=8, alignment=1))]
                for dia in dias_com_dados_ordenados:
                    aulas_dia = tabela_aulas[horario][dia]
                    if aulas_dia:
                        celula_texto = []
                        for aula in aulas_dia:
                            if aula.tipo_atividade == 'AULA' and aula.disciplina:
                                texto = aula.disciplina.nome or '-'
                                
                                # Adicionar carga horária acumulada (sem a palavra "Carga:")
                                if aula.pk in carga_horaria_acumulada_por_aula:
                                    carga_info = carga_horaria_acumulada_por_aula[aula.pk]
                                    acumulado = int(carga_info['acumulado']) if carga_info['acumulado'] else 0
                                    total = int(carga_info['total_disciplina']) if carga_info['total_disciplina'] else 0
                                    if total > 0:
                                        texto += f"<br/>{acumulado}h/{total}h"
                                
                                # Adicionar horas/aula da aula atual
                                if aula.horas_aula:
                                    texto += f"<br/>({float(aula.horas_aula):.2f}h/a)"
                                
                                if aula.instrutor_militar:
                                    instrutor = aula.instrutor_militar
                                    posto = instrutor.get_posto_graduacao_display()
                                    texto += f"<br/>{posto} {instrutor.nome_completo}"
                                elif aula.instrutor_externo:
                                    texto += f"<br/>{aula.instrutor_externo.get_nome_completo()}"
                                if aula.observacoes:
                                    texto += f"<br/>({aula.observacoes})"
                                celula_texto.append(texto)
                            elif aula.tipo_atividade == 'INTERVALO':
                                celula_texto.append(f"INTERVALO<br/>{aula.descricao or ''}")
                            elif aula.tipo_atividade == 'HORARIO_VAGO':
                                celula_texto.append("HORÁRIO VAGO")
                            elif aula.tipo_atividade == 'OUTRA_ACAO':
                                celula_texto.append(f"{aula.descricao or 'OUTRA AÇÃO'}")
                        texto_celula = "<br/>".join(celula_texto) if celula_texto else "-"
                        linha.append(Paragraph(texto_celula, ParagraphStyle('celula', parent=styles['Normal'], fontSize=7, alignment=1)))
                    else:
                        linha.append(Paragraph("-", ParagraphStyle('celula', parent=styles['Normal'], fontSize=7, alignment=1)))
                quadro_data.append(linha)
            
            # Criar tabela - ajustar larguras das colunas dinamicamente (retrato A4: ~19.7cm disponível)
            num_colunas = len(dias_com_dados_ordenados)
            largura_horario = 2.0*cm
            largura_disponivel = 19.7*cm - largura_horario
            largura_coluna_dia = largura_disponivel / num_colunas if num_colunas > 0 else 2.2*cm
            col_widths = [largura_horario] + [largura_coluna_dia] * num_colunas
            
            quadro_table = Table(quadro_data, colWidths=col_widths, repeatRows=1)
            
            # Criar estilo base
            estilo_tabela = [
                # Cabeçalho
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('TOPPADDING', (0, 0), (-1, 0), 5),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                # Linhas de dados
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                ('TOPPADDING', (0, 1), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                # Bordas
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), True),
            ]
            
            # Adicionar estilos para linhas separadoras (mesclando células)
            for linha_idx in linhas_separadoras:
                estilo_tabela.extend([
                    # Mesclar todas as células da linha separadora
                    ('SPAN', (0, linha_idx), (-1, linha_idx)),
                    ('BACKGROUND', (0, linha_idx), (-1, linha_idx), colors.lightblue),
                    ('FONTNAME', (0, linha_idx), (-1, linha_idx), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, linha_idx), (-1, linha_idx), 10),
                    ('ALIGN', (0, linha_idx), (-1, linha_idx), 'CENTER'),
                    ('VALIGN', (0, linha_idx), (-1, linha_idx), 'MIDDLE'),
                    ('TOPPADDING', (0, linha_idx), (-1, linha_idx), 5),
                    ('BOTTOMPADDING', (0, linha_idx), (-1, linha_idx), 5),
                ])
            
            quadro_table.setStyle(TableStyle(estilo_tabela))
            
            story.append(quadro_table)
            story.append(Spacer(1, 20))
        
        # Cidade e Data por extenso (centralizada) - depois da tabela
        try:
            militar_logado = request.user.militar if hasattr(request.user, 'militar') else None
            
            # Obter cidade
            if militar_logado and militar_logado.cidade:
                cidade_doc = militar_logado.cidade
            else:
                cidade_doc = "Teresina"
            cidade_estado = f"{cidade_doc} - PI"
        except:
            cidade_estado = "Teresina - PI"
        
        # Data por extenso - usar timezone de Brasília
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        data_atual = timezone.now().astimezone(brasilia_tz) if timezone.is_aware(timezone.now()) else brasilia_tz.localize(timezone.now())
        
        meses_extenso_data = {
            1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
            5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
            9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
        }
        data_formatada_extenso = f"{data_atual.day} de {meses_extenso_data[data_atual.month]} de {data_atual.year}"
        data_cidade = f"{cidade_estado}, {data_formatada_extenso}."
        
        # Adicionar cidade e data centralizada
        story.append(Paragraph(data_cidade, ParagraphStyle('data_extenso', parent=styles['Normal'], alignment=1, fontSize=11, fontName='Helvetica', spaceAfter=20)))
        story.append(Spacer(1, 20))
        
        # Observações gerais (se houver)
        if quadro.observacoes:
            story.append(Paragraph("<b>Observações Gerais:</b>", style_bold))
            story.append(Paragraph(quadro.observacoes, style_normal))
            story.append(Spacer(1, 15))
        
        # Adicionar assinaturas eletrônicas (se houver)
        if quadro.assinaturas.exists():
            story.append(Spacer(1, 10))
            
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            for assinatura in quadro.assinaturas.all():
                # Obter nome completo do assinante
                if hasattr(assinatura.assinado_por, 'militar') and assinatura.assinado_por.militar:
                    militar = assinatura.assinado_por.militar
                    nome_posto_quadro = f"{militar.nome_completo} - {militar.get_posto_graduacao_display()} BM"
                else:
                    nome_posto_quadro = assinatura.assinado_por.get_full_name() or assinatura.assinado_por.username
                
                funcao_display = assinatura.funcao_assinatura or "Função não registrada"
                data_formatada = assinatura.data_assinatura.strftime('%d/%m/%Y')
                hora_formatada = assinatura.data_assinatura.strftime('%H:%M:%S')
                
                texto_assinatura = (
                    f"Documento assinado eletronicamente por {nome_posto_quadro}, em {data_formatada} {hora_formatada}, "
                    f"conforme Portaria GCG/ CBMEPI N 167 de 23 de novembro de 2021 e publicada no DOE PI N 253 de 26 de novembro de 2021"
                )
                
                # Adicionar logo da assinatura eletrônica
                from .utils import obter_caminho_assinatura_eletronica
                logo_path_assinatura = obter_caminho_assinatura_eletronica()
                
                # Tabela das assinaturas: Logo + Texto de assinatura
                assinatura_data = [
                    [Image(logo_path_assinatura, width=3.0*cm, height=2.0*cm), Paragraph(texto_assinatura, style_small)]
                ]
                
                assinatura_table = Table(assinatura_data, colWidths=[3*cm, 13.7*cm])
                assinatura_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizado
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Texto alinhado à esquerda
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BOX', (0, 0), (-1, -1), 1, colors.grey),  # Borda do retângulo
                ]))
                
                story.append(assinatura_table)
                story.append(Spacer(1, 10))  # Espaçamento entre assinaturas
        
        # Construir PDF
        doc.build(story)
        
        # Retornar PDF para visualização no navegador (sem download automático)
        buffer.seek(0)
        filename = f"QTS_{quadro.numero_quadro or quadro.pk}_{quadro.turma.identificacao if quadro.turma else 'N/A'}.pdf"
        response = FileResponse(buffer, as_attachment=False, filename=filename, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro - PDF do Quadro de Trabalho Semanal</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error-box {{ border: 2px solid #dc3545; border-radius: 5px; padding: 20px; 
                            max-width: 500px; margin: 0 auto; background-color: #f8d7da; }}
                h2 {{ color: #721c24; }}
                p {{ color: #721c24; }}
                button {{ background-color: #dc3545; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background-color: #c82333; }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>❌ Erro ao Gerar PDF</h2>
                <p><strong>Erro ao gerar PDF do Quadro de Trabalho Semanal.</strong></p>
                <p>{str(e)}</p>
                <button onclick="window.close()">Fechar</button>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500, content_type='text/html')


@login_required
def visualizar_quadro_trabalho_semanal(request, pk):
    """Visualiza um quadro de trabalho semanal completo"""
    from militares.models import QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    quadro = get_object_or_404(
        QuadroTrabalhoSemanal.objects.select_related(
            'turma', 'turma__curso'
        ).prefetch_related('aulas__disciplina', 'aulas__instrutor_militar', 'aulas__instrutor_externo', 'assinaturas__assinado_por'),
        pk=pk
    )
    
    # Buscar todas as aulas do quadro
    aulas = quadro.aulas.all().order_by('dia_semana', 'hora_inicio', 'ordem')
    
    # Organizar aulas em uma estrutura simples para o template
    # Estrutura: tabela_aulas[horario][dia] = [lista de aulas]
    tabela_aulas = {}
    horarios_unicos = set()
    dias_semana_list = ['SEGUNDA', 'TERCA', 'QUARTA', 'QUINTA', 'SEXTA', 'SABADO', 'DOMINGO']
    
    for aula in aulas:
        horario_key = f"{aula.hora_inicio.strftime('%H:%M')}-{aula.hora_fim.strftime('%H:%M')}"
        if horario_key not in tabela_aulas:
            tabela_aulas[horario_key] = {dia: [] for dia in dias_semana_list}
        tabela_aulas[horario_key][aula.dia_semana].append(aula)
        horarios_unicos.add(horario_key)
    
    # Ordenar horários
    horarios_ordenados = sorted(horarios_unicos)
    
    # Calcular datas de cada dia da semana
    dias_semana_datas = {}
    if quadro.data_inicio_semana:
        data_atual = quadro.data_inicio_semana
        # Garantir que começa na segunda
        days_since_monday = data_atual.weekday()
        data_segunda = data_atual - timedelta(days=days_since_monday)
        
        for idx, dia in enumerate(dias_semana_list):
            dias_semana_datas[dia] = data_segunda + timedelta(days=idx)
    
    # Calcular totais
    total_horas = sum([float(aula.horas_aula) for aula in aulas if aula.tipo_atividade == 'AULA'])
    total_aulas = aulas.filter(tipo_atividade='AULA').count()
    total_intervalos = aulas.filter(tipo_atividade='INTERVALO').count()
    total_horarios_vagos = aulas.filter(tipo_atividade='HORARIO_VAGO').count()
    total_outras_acoes = aulas.filter(tipo_atividade='OUTRA_ACAO').count()
    
    # Calcular carga horária acumulada progressiva por disciplina
    # Considerando todos os QTS anteriores da mesma turma para continuidade
    dias_semana_ordem = {'SEGUNDA': 1, 'TERCA': 2, 'QUARTA': 3, 'QUINTA': 4, 'SEXTA': 5, 'SABADO': 6, 'DOMINGO': 7}
    
    # Buscar todos os QTS anteriores da mesma turma
    quadros_anteriores = QuadroTrabalhoSemanal.objects.filter(
        turma=quadro.turma
    ).filter(
        Q(numero_quadro__lt=quadro.numero_quadro) | 
        Q(numero_quadro=quadro.numero_quadro, data_inicio_semana__lt=quadro.data_inicio_semana)
    ).order_by('numero_quadro', 'data_inicio_semana')
    
    # Buscar todas as aulas da disciplina em todos os QTS anteriores e atual
    todas_aulas_disciplina = list(AulaQuadroTrabalhoSemanal.objects.filter(
        Q(quadro__in=quadros_anteriores) | Q(quadro=quadro),
        tipo_atividade='AULA',
        disciplina__isnull=False
    ).select_related('disciplina', 'quadro'))
    
    # Ordenar manualmente para garantir ordem correta
    # Ordem: QTS (número, data) -> dia da semana -> hora_inicio -> ordem
    # IMPORTANTE: Para o QTS atual, usar a data real da aula (data do campo 'data') se disponível
    todas_aulas_disciplina.sort(key=lambda a: (
        a.quadro.numero_quadro if a.quadro else 999,
        a.quadro.data_inicio_semana if a.quadro and a.quadro.data_inicio_semana else date.max,
        # Para aulas do mesmo QTS, usar a data real da aula para ordenação
        a.data if a.data else (a.quadro.data_inicio_semana if a.quadro and a.quadro.data_inicio_semana else date.max),
        dias_semana_ordem.get(a.dia_semana, 99),
        a.hora_inicio if a.hora_inicio else time.max,
        a.ordem or 0
    ))
    
    # Calcular acumulado progressivo por disciplina considerando todos os QTS
    carga_horaria_acumulada_por_aula = {}
    acumulado_por_disciplina = {}
    
    for aula in todas_aulas_disciplina:
        disciplina_id = aula.disciplina.pk
        
        # Inicializar acumulado da disciplina se necessário
        if disciplina_id not in acumulado_por_disciplina:
            carga_total = getattr(aula.disciplina, 'carga_horaria', None) or getattr(aula.disciplina, 'carga_horaria_total', None)
            acumulado_por_disciplina[disciplina_id] = {
                'acumulado': 0,
                'total_disciplina': carga_total
            }
        
        # Adicionar horas da aula atual ao acumulado
        if aula.horas_aula:
            acumulado_por_disciplina[disciplina_id]['acumulado'] += float(aula.horas_aula)
        
        # Armazenar o acumulado apenas para aulas do QTS atual (para exibir no card)
        if aula.quadro_id == quadro.pk:
            carga_horaria_acumulada_por_aula[aula.pk] = {
                'acumulado': acumulado_por_disciplina[disciplina_id]['acumulado'],
                'total_disciplina': acumulado_por_disciplina[disciplina_id]['total_disciplina']
            }
    
    # Verificar assinaturas
    tem_revisao = quadro.assinaturas.filter(tipo_assinatura='REVISAO').exists()
    tem_aprovacao = quadro.assinaturas.filter(tipo_assinatura='APROVACAO').exists()
    
    context = {
        'quadro': quadro,
        'tabela_aulas': tabela_aulas,
        'horarios_ordenados': horarios_ordenados,
        'dias_semana_datas': dias_semana_datas,
        'dias_semana_list': dias_semana_list,
        'total_horas': total_horas,
        'total_aulas': total_aulas,
        'total_intervalos': total_intervalos,
        'total_horarios_vagos': total_horarios_vagos,
        'total_outras_acoes': total_outras_acoes,
        'carga_horaria_acumulada_por_aula': carga_horaria_acumulada_por_aula,
        'tem_revisao': tem_revisao,
        'tem_aprovacao': tem_aprovacao,
    }
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/visualizar.html', context)


@login_required
def visualizar_quadro_trabalho_semanal_turma(request, turma_id):
    """Visualiza os quadros de trabalho semanal de uma turma específica"""
    from militares.models import QuadroTrabalhoSemanal
    
    turma = get_object_or_404(TurmaEnsino, pk=turma_id)
    
    # Buscar todos os quadros da turma
    quadros = QuadroTrabalhoSemanal.objects.filter(
        turma=turma
    ).select_related('turma', 'turma__curso').prefetch_related('aulas').order_by('-data_inicio_semana', '-numero_quadro')
    
    context = {
        'turma': turma,
        'quadros': quadros,
    }
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/visualizar_turma.html', context)


def criar_aditamento_qts(quadro_atual, usuario, aula_especifica=None):
    """Cria um novo QTS como aditamento
    
    Lógica:
    - Se não existe nenhum aditamento, cria baseado no original
    - Se já existe aditamento, cria baseado no último aditamento (não no original)
    
    Args:
        quadro_atual: O QTS atual (pode ser original ou aditamento)
        usuario: O usuário que está criando o aditamento
        aula_especifica: (opcional) Aula específica que será modificada no aditamento
    
    Returns:
        Tupla (novo_quadro, aula_correspondente) ou (quadro_atual, aula_especifica) se não foi aprovado
    """
    from militares.models import QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal
    
    # Determinar o QTS original (se for aditamento, pegar o original)
    quadro_original = quadro_atual.quadro_original if quadro_atual.quadro_original else quadro_atual
    
    # Verificar se o usuário pode criar aditamento
    assinatura_aprovacao = quadro_original.assinaturas.filter(tipo_assinatura='APROVACAO').first()
    if not assinatura_aprovacao:
        return quadro_atual, aula_especifica  # Se não foi aprovado, retorna o atual
    
    if not usuario.is_superuser and assinatura_aprovacao.assinado_por != usuario:
        return None, None  # Usuário não tem permissão
    
    # Verificar se já existe algum aditamento
    aditamentos_existentes = QuadroTrabalhoSemanal.objects.filter(
        quadro_original=quadro_original
    ).order_by('-numero_aditamento')
    
    # Determinar qual QTS usar como base para copiar
    if aditamentos_existentes.exists():
        # Já existe aditamento - usar o último aditamento como base
        quadro_base = aditamentos_existentes.first()
        numero_aditamento_base = quadro_base.numero_aditamento or "A00"
        # Extrair número do último aditamento (ex: "A01" -> 1)
        try:
            num_ultimo = int(numero_aditamento_base.replace("A", ""))
            numero_aditamento = num_ultimo + 1
        except:
            numero_aditamento = aditamentos_existentes.count() + 1
    else:
        # Primeiro aditamento - usar o original como base
        quadro_base = quadro_original
        numero_aditamento = 1
    
    numero_aditamento_str = f"A{numero_aditamento:02d}"
    numero_base = quadro_original.numero_quadro or quadro_original.pk
    
    # Criar novo QTS copiando dados do QTS base (original ou último aditamento)
    novo_quadro = QuadroTrabalhoSemanal.objects.create(
        turma=quadro_base.turma,
        numero_quadro=numero_base,
        data_inicio_semana=quadro_base.data_inicio_semana,
        data_fim_semana=quadro_base.data_fim_semana,
        local=quadro_base.local,
        observacoes=quadro_base.observacoes,
        quadro_original=quadro_original,  # Sempre aponta para o original
        numero_aditamento=numero_aditamento_str
    )
    
    # Mapear aulas do QTS base para novas aulas para encontrar correspondência
    mapeamento_aulas = {}
    
    # Copiar todas as aulas do QTS base (original ou último aditamento)
    for aula_base in quadro_base.aulas.all():
        aula_nova = AulaQuadroTrabalhoSemanal.objects.create(
            quadro=novo_quadro,
            disciplina=aula_base.disciplina,
            instrutor_militar=aula_base.instrutor_militar,
            instrutor_externo=aula_base.instrutor_externo,
            dia_semana=aula_base.dia_semana,
            data=aula_base.data,
            hora_inicio=aula_base.hora_inicio,
            hora_fim=aula_base.hora_fim,
            horas_aula=aula_base.horas_aula,
            carga_horaria_total=aula_base.carga_horaria_total,
            observacoes=aula_base.observacoes,
            ordem=aula_base.ordem,
            tipo_atividade=aula_base.tipo_atividade,
            descricao=aula_base.descricao
        )
        # Mapear aula base para nova aula
        mapeamento_aulas[aula_base.pk] = aula_nova
    
    # Se foi fornecida uma aula específica, retornar a correspondente
    aula_correspondente = None
    if aula_especifica:
        aula_correspondente = mapeamento_aulas.get(aula_especifica.pk)
    
    return novo_quadro, aula_correspondente


@login_required
def adicionar_aula_quadro_trabalho_semanal(request, quadro_id):
    """Adiciona uma nova aula ao quadro de trabalho semanal"""
    from militares.models import QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal, AssinaturaQTS
    from militares.forms_ensino import AulaQuadroTrabalhoSemanalForm
    from django.http import JsonResponse
    
    try:
        quadro = get_object_or_404(QuadroTrabalhoSemanal, pk=quadro_id)
    except (ValueError, TypeError):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': {'quadro_id': ['ID do quadro inválido']}
            }, status=400)
        messages.error(request, 'ID do quadro inválido.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if _eh_coordenador_ou_supervisor(request.user) and quadro.turma and not _usuario_vinculado_turma(request.user, quadro.turma):
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'__all__': ['Acesso negado. Você só pode alterar QTS de turmas em que está vinculado.']}}, status=403)
        messages.error(request, 'Acesso negado. Você só pode alterar QTS de turmas em que está vinculado.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    # Verificar se o QTS foi aprovado - se sim, criar aditamento
    # Se for um aditamento, verificar se já existe outro aditamento (não pode editar aditamento se já existe outro depois)
    quadro_original = quadro.quadro_original if quadro.quadro_original else quadro
    assinatura_aprovacao = quadro_original.assinaturas.filter(tipo_assinatura='APROVACAO').first()
    
    if assinatura_aprovacao:
        # Verificar permissão
        if not request.user.is_superuser and assinatura_aprovacao.assinado_por != request.user:
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['Este quadro de trabalho semanal foi aprovado e só pode ser editado por quem o aprovou.']}
                }, status=403)
            messages.error(request, 'Este quadro de trabalho semanal foi aprovado e só pode ser editado por quem o aprovou.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Se for o original e já existe aditamento, não pode mais editar
        if not quadro.quadro_original:
            aditamentos_existentes = QuadroTrabalhoSemanal.objects.filter(
                quadro_original=quadro_original
            ).exists()
            if aditamentos_existentes:
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': ['Este QTS já possui aditamentos. Edite o último aditamento criado.']}
                    }, status=403)
                messages.error(request, 'Este QTS já possui aditamentos. Edite o último aditamento criado.')
                ultimo_aditamento = QuadroTrabalhoSemanal.objects.filter(
                    quadro_original=quadro_original
                ).order_by('-numero_aditamento').first()
                if ultimo_aditamento:
                    return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=ultimo_aditamento.pk)
                return redirect('militares:ensino_quadros_trabalho_semanal_listar')
        
        # Criar aditamento antes de adicionar a aula
        novo_quadro, _ = criar_aditamento_qts(quadro, request.user)
        if not novo_quadro:
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['Erro ao criar aditamento.']}
                }, status=500)
            messages.error(request, 'Erro ao criar aditamento.')
            return redirect('militares:ensino_quadros_trabalho_semanal_listar')
        
        quadro = novo_quadro
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        # Log dos dados recebidos para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'Dados POST recebidos: {dict(request.POST)}')
        
        form = AulaQuadroTrabalhoSemanalForm(request.POST, quadro=quadro, user=request.user)
        if form.is_valid():
            try:
                aula = form.save(commit=False)
                aula.quadro = quadro
                
                # Para intervalos, garantir que horas_aula está em minutos (não em horas)
                # Se o valor for muito pequeno (< 1), provavelmente está em horas e precisa ser convertido
                if aula.tipo_atividade == 'INTERVALO' and aula.horas_aula:
                    # Se o valor for menor que 1, provavelmente está em horas (ex: 0.5 horas = 30 minutos)
                    # Converter para minutos multiplicando por 60
                    if aula.horas_aula < 1:
                        aula.horas_aula = aula.horas_aula * 60
                    # Se o valor for maior que 60, provavelmente já está em minutos, manter como está
                
                # Processar carga_horaria_total se estiver no formato "X de Y"
                if 'carga_horaria_total' in form.cleaned_data and form.cleaned_data['carga_horaria_total']:
                    carga_str = str(form.cleaned_data['carga_horaria_total'])
                    # Extrair o número antes de "de" (ex: "2 de 20" -> 2)
                    if ' de ' in carga_str:
                        try:
                            carga_numero = float(carga_str.split(' de ')[0].strip())
                            aula.carga_horaria_total = carga_numero
                        except (ValueError, IndexError):
                            pass
                
                aula.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Aula adicionada com sucesso!',
                        'aula_id': aula.pk
                    })
                messages.success(request, 'Aula adicionada com sucesso!')
                return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao salvar aula: {str(e)}', exc_info=True)
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': {'__all__': [f'Erro ao salvar aula: {str(e)}']}
                    }, status=400)
                messages.error(request, f'Erro ao salvar aula: {str(e)}')
                # Continuar para mostrar o formulário com erros
        else:
            # Log dos erros de validação para debug
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Erros de validação do formulário: {form.errors}')
            logger.warning(f'Dados do POST: {request.POST}')
            
            if is_ajax:
                # Converter erros do formulário para um formato mais legível
                errors_dict = {}
                for field, errors in form.errors.items():
                    errors_dict[field] = errors if isinstance(errors, list) else [str(errors)]
                
                return JsonResponse({
                    'success': False,
                    'errors': errors_dict,
                    'error_message': 'Por favor, corrija os erros no formulário.',
                    'form_data': dict(request.POST)  # Para debug
                }, status=400)
            # Se não for AJAX, continuar para renderizar o formulário com erros
    
    else:
        form = AulaQuadroTrabalhoSemanalForm(quadro=quadro, user=request.user)
        # Pré-preencher data baseado no dia da semana ou data explícita
        dia_semana = request.GET.get('dia_semana')
        data_str = request.GET.get('data')
        if data_str:
            try:
                from datetime import datetime
                data_dia = datetime.strptime(data_str, '%Y-%m-%d').date()
                form.fields['data'].initial = data_dia
                if dia_semana:
                    form.fields['dia_semana'].initial = dia_semana
            except Exception:
                pass
        elif dia_semana and quadro.data_inicio_semana:
            from datetime import timedelta
            dias_semana = ['SEGUNDA', 'TERCA', 'QUARTA', 'QUINTA', 'SEXTA', 'SABADO', 'DOMINGO']
            if dia_semana in dias_semana:
                idx = dias_semana.index(dia_semana)
                days_since_monday = quadro.data_inicio_semana.weekday()
                data_dia = quadro.data_inicio_semana - timedelta(days=days_since_monday) + timedelta(days=idx)
                form.fields['data'].initial = data_dia
                form.fields['dia_semana'].initial = dia_semana
    
    context = {
        'form': form,
        'quadro': quadro,
    }
    
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/quadros_trabalho_semanal/adicionar_aula_modal.html', context, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/adicionar_aula.html', context)


@login_required
def editar_aula_quadro_trabalho_semanal(request, pk):
    """Edita uma aula do quadro de trabalho semanal"""
    from militares.models import AulaQuadroTrabalhoSemanal, AssinaturaQTS, QuadroTrabalhoSemanal
    from militares.forms_ensino import AulaQuadroTrabalhoSemanalForm
    from django.http import JsonResponse
    
    aula = get_object_or_404(AulaQuadroTrabalhoSemanal, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if _eh_coordenador_ou_supervisor(request.user) and aula.quadro and aula.quadro.turma and not _usuario_vinculado_turma(request.user, aula.quadro.turma):
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Acesso negado. Você só pode editar QTS de turmas em que está vinculado.'}, status=403)
        messages.error(request, 'Acesso negado. Você só pode editar QTS de turmas em que está vinculado.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    if not pode_editar_ensino(request.user):
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para editar aulas do quadro de trabalho semanal.'
            }, status=403)
        messages.error(request, 'Você não tem permissão para editar aulas do quadro de trabalho semanal.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    # Verificar se o QTS foi aprovado - se sim, criar aditamento
    quadro = aula.quadro
    quadro_original = quadro.quadro_original if quadro.quadro_original else quadro
    assinatura_aprovacao = quadro_original.assinaturas.filter(tipo_assinatura='APROVACAO').first()
    
    if assinatura_aprovacao:
        # Verificar permissão
        if not request.user.is_superuser and assinatura_aprovacao.assinado_por != request.user:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': 'Este quadro de trabalho semanal foi aprovado e só pode ser editado por quem o aprovou.'
                }, status=403)
            messages.error(request, 'Este quadro de trabalho semanal foi aprovado e só pode ser editado por quem o aprovou.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro.pk)
        
        # Se for o original e já existe aditamento, não pode mais editar
        if not quadro.quadro_original:
            aditamentos_existentes = QuadroTrabalhoSemanal.objects.filter(
                quadro_original=quadro_original
            ).exists()
            if aditamentos_existentes:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'error': 'Este QTS já possui aditamentos. Edite o último aditamento criado.'
                    }, status=403)
                messages.error(request, 'Este QTS já possui aditamentos. Edite o último aditamento criado.')
                ultimo_aditamento = QuadroTrabalhoSemanal.objects.filter(
                    quadro_original=quadro_original
                ).order_by('-numero_aditamento').first()
                if ultimo_aditamento:
                    return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=ultimo_aditamento.pk)
                return redirect('militares:ensino_quadros_trabalho_semanal_listar')
        
        # Criar aditamento antes de editar a aula
        novo_quadro, aula_correspondente = criar_aditamento_qts(quadro, request.user, aula)
        if not novo_quadro:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': 'Erro ao criar aditamento.'
                }, status=500)
            messages.error(request, 'Erro ao criar aditamento.')
            return redirect('militares:ensino_quadros_trabalho_semanal_listar')
        
        if not aula_correspondente:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': 'Aula não encontrada no aditamento criado.'
                }, status=404)
            messages.error(request, 'Aula não encontrada no aditamento criado.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=novo_quadro.pk)
        
        aula = aula_correspondente
        quadro = novo_quadro
    
    if request.method == 'POST':
        form = AulaQuadroTrabalhoSemanalForm(request.POST, instance=aula, quadro=aula.quadro, user=request.user)
        if form.is_valid():
            aula_atualizada = form.save(commit=False)
            
            # Para intervalos, garantir que horas_aula está em minutos (não em horas)
            # Se o valor for muito pequeno (< 1), provavelmente está em horas e precisa ser convertido
            if aula_atualizada.tipo_atividade == 'INTERVALO' and aula_atualizada.horas_aula:
                # Se o valor for menor que 1, provavelmente está em horas (ex: 0.5 horas = 30 minutos)
                # Converter para minutos multiplicando por 60
                if aula_atualizada.horas_aula < 1:
                    aula_atualizada.horas_aula = aula_atualizada.horas_aula * 60
                # Se o valor for maior que 60, provavelmente já está em minutos, manter como está
            
            # Processar carga_horaria_total se estiver no formato "X de Y"
            if 'carga_horaria_total' in form.cleaned_data and form.cleaned_data['carga_horaria_total']:
                carga_str = str(form.cleaned_data['carga_horaria_total'])
                # Extrair o número antes de "de" (ex: "2 de 20" -> 2)
                if ' de ' in carga_str:
                    try:
                        carga_numero = float(carga_str.split(' de ')[0].strip())
                        aula_atualizada.carga_horaria_total = carga_numero
                    except (ValueError, IndexError):
                        pass
            
            aula_atualizada.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Aula atualizada com sucesso!'
                })
            messages.success(request, 'Aula atualizada com sucesso!')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=aula.quadro.pk)
        else:
            # Log dos erros de validação para debug
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Erros de validação do formulário de edição: {form.errors}')
            logger.warning(f'Dados do POST: {request.POST}')
            
            if is_ajax:
                # Converter erros do formulário para um formato mais legível
                errors_dict = {}
                for field, errors in form.errors.items():
                    errors_dict[field] = errors if isinstance(errors, list) else [str(errors)]
                
                return JsonResponse({
                    'success': False,
                    'errors': errors_dict,
                    'error_message': 'Por favor, corrija os erros no formulário.',
                    'form_data': dict(request.POST)  # Para debug
                }, status=400)
    else:
        form = AulaQuadroTrabalhoSemanalForm(instance=aula, quadro=aula.quadro)
        # Para intervalos existentes, converter horas_aula de horas para minutos se necessário
        if aula.tipo_atividade == 'INTERVALO' and aula.horas_aula:
            # Se o valor for menor que 1, provavelmente está em horas (ex: 0.5 horas = 30 minutos)
            # Converter para minutos multiplicando por 60
            if aula.horas_aula < 1:
                form.initial['horas_aula'] = float(aula.horas_aula) * 60
            # Se o valor for entre 1 e 60, pode estar em horas ou minutos
            # Assumir que valores > 1 e < 60 estão em minutos se o intervalo foi criado recentemente
            # Para valores antigos, manter como está
    
    context = {
        'form': form,
        'aula': aula,
        'quadro': aula.quadro,
    }
    
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/quadros_trabalho_semanal/editar_aula_modal.html', context, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/editar_aula.html', context)


@login_required
def deletar_aula_quadro_trabalho_semanal(request, pk):
    """Deleta uma aula do quadro de trabalho semanal"""
    from militares.models import AulaQuadroTrabalhoSemanal, AssinaturaQTS, QuadroTrabalhoSemanal
    from django.http import JsonResponse
    
    aula = get_object_or_404(AulaQuadroTrabalhoSemanal, pk=pk)
    quadro = aula.quadro
    quadro_id = quadro.pk
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if _eh_coordenador_ou_supervisor(request.user) and quadro.turma and not _usuario_vinculado_turma(request.user, quadro.turma):
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Acesso negado. Você só pode editar QTS de turmas em que está vinculado.'}, status=403)
        messages.error(request, 'Acesso negado. Você só pode editar QTS de turmas em que está vinculado.')
        return redirect('militares:ensino_quadros_trabalho_semanal_listar')
    
    # Verificar se o QTS foi aprovado - se sim, criar aditamento
    quadro_original = quadro.quadro_original if quadro.quadro_original else quadro
    assinatura_aprovacao = quadro_original.assinaturas.filter(tipo_assinatura='APROVACAO').first()
    
    if assinatura_aprovacao:
        # Verificar permissão
        if not request.user.is_superuser and assinatura_aprovacao.assinado_por != request.user:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': 'Este quadro de trabalho semanal foi aprovado e só pode ser editado por quem o aprovou.'
                }, status=403)
            messages.error(request, 'Este quadro de trabalho semanal foi aprovado e só pode ser editado por quem o aprovou.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro_id)
        
        # Se for o original e já existe aditamento, não pode mais editar
        if not quadro.quadro_original:
            aditamentos_existentes = QuadroTrabalhoSemanal.objects.filter(
                quadro_original=quadro_original
            ).exists()
            if aditamentos_existentes:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'error': 'Este QTS já possui aditamentos. Edite o último aditamento criado.'
                    }, status=403)
                messages.error(request, 'Este QTS já possui aditamentos. Edite o último aditamento criado.')
                ultimo_aditamento = QuadroTrabalhoSemanal.objects.filter(
                    quadro_original=quadro_original
                ).order_by('-numero_aditamento').first()
                if ultimo_aditamento:
                    return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=ultimo_aditamento.pk)
                return redirect('militares:ensino_quadros_trabalho_semanal_listar')
        
        # Criar aditamento antes de deletar a aula
        novo_quadro, aula_correspondente = criar_aditamento_qts(quadro, request.user, aula)
        if not novo_quadro:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': 'Erro ao criar aditamento.'
                }, status=500)
            messages.error(request, 'Erro ao criar aditamento.')
            return redirect('militares:ensino_quadros_trabalho_semanal_listar')
        
        if not aula_correspondente:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': 'Aula não encontrada no aditamento criado.'
                }, status=404)
            messages.error(request, 'Aula não encontrada no aditamento criado.')
            return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=novo_quadro.pk)
        
        aula = aula_correspondente
        quadro_id = novo_quadro.pk
    
    if request.method == 'POST':
        aula.delete()
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Aula deletada com sucesso!'
            })
        messages.success(request, 'Aula deletada com sucesso!')
        return redirect('militares:ensino_quadro_trabalho_semanal_visualizar', pk=quadro_id)
    
    context = {
        'aula': aula,
    }
    
    if is_ajax:
        from django.template.loader import render_to_string
        html = render_to_string('militares/ensino/quadros_trabalho_semanal/deletar_aula_modal.html', context, request=request)
        return JsonResponse({'html': html})
    
    return render(request, 'militares/ensino/quadros_trabalho_semanal/deletar_aula.html', context)


# ============================================================================
# VIEWS PARA MODELOS ITE 01/2024
# ============================================================================

# PLANO GERAL DE ENSINO
@login_required
def listar_planos_gerais_ensino(request):
    """Lista todos os Planos Gerais de Ensino"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos gerais de ensino.')
        return redirect('militares:ensino_dashboard')
    
    planos = PlanoGeralEnsino.objects.all().order_by('-ano_exercicio')
    
    # Paginação
    paginator = Paginator(planos, 20)
    page = request.GET.get('page')
    planos = paginator.get_page(page)
    
    context = {
        'planos': planos,
    }
    return render(request, 'militares/ensino/ite/planos_gerais/listar.html', context)


@login_required
def criar_plano_geral_ensino(request):
    """Cria um novo Plano Geral de Ensino"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar planos gerais de ensino.')
        return redirect('militares:ensino_planos_gerais_listar')
    
    if request.method == 'POST':
        form = PlanoGeralEnsinoForm(request.POST)
        if form.is_valid():
            plano = form.save(commit=False)
            plano.elaborado_por = request.user
            plano.save()
            messages.success(request, 'Plano Geral de Ensino criado com sucesso!')
            return redirect('militares:ensino_planos_gerais_detalhes', pk=plano.pk)
    else:
        form = PlanoGeralEnsinoForm()
    
    context = {
        'form': form,
        'titulo': 'Criar Plano Geral de Ensino',
    }
    return render(request, 'militares/ensino/ite/planos_gerais/criar.html', context)


@login_required
def detalhes_plano_geral_ensino(request, pk):
    """Detalhes de um Plano Geral de Ensino"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos gerais de ensino.')
        return redirect('militares:ensino_dashboard')
    
    plano = get_object_or_404(PlanoGeralEnsino.objects.prefetch_related('itens'), pk=pk)
    itens = plano.itens.all()
    
    context = {
        'plano': plano,
        'itens': itens,
    }
    return render(request, 'militares/ensino/ite/planos_gerais/detalhes.html', context)


# PROJETO PEDAGÓGICO
@login_required
def listar_projetos_pedagogicos(request):
    """Lista todos os Projetos Pedagógicos"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar projetos pedagógicos.')
        return redirect('militares:ensino_dashboard')
    
    projetos = ProjetoPedagogico.objects.select_related('curso').all().order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(projetos, 20)
    page = request.GET.get('page')
    projetos = paginator.get_page(page)
    
    context = {
        'projetos': projetos,
    }
    return render(request, 'militares/ensino/ite/projetos_pedagogicos/listar.html', context)


@login_required
def criar_projeto_pedagogico(request, curso_id=None):
    """Cria um novo Projeto Pedagógico"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar projetos pedagógicos.')
        return redirect('militares:ensino_projetos_pedagogicos_listar')
    
    curso = None
    if curso_id:
        curso = get_object_or_404(CursoEnsino, pk=curso_id)
    
    if request.method == 'POST':
        form = ProjetoPedagogicoForm(request.POST, request.FILES)
        if form.is_valid():
            projeto = form.save(commit=False)
            projeto.aprovado_por = request.user
            projeto.save()
            messages.success(request, 'Projeto Pedagógico criado com sucesso!')
            return redirect('militares:ensino_projetos_pedagogicos_detalhes', pk=projeto.pk)
    else:
        initial = {}
        if curso:
            initial['curso'] = curso
        form = ProjetoPedagogicoForm(initial=initial)
    
    context = {
        'form': form,
        'curso': curso,
        'titulo': 'Criar Projeto Pedagógico',
    }
    return render(request, 'militares/ensino/ite/projetos_pedagogicos/criar.html', context)


@login_required
def detalhes_projeto_pedagogico(request, pk):
    """Detalhes de um Projeto Pedagógico"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar projetos pedagógicos.')
        return redirect('militares:ensino_dashboard')
    
    projeto = get_object_or_404(ProjetoPedagogico.objects.select_related('curso'), pk=pk)
    
    context = {
        'projeto': projeto,
    }
    return render(request, 'militares/ensino/ite/projetos_pedagogicos/detalhes.html', context)


# PLANO DE CURSO/ESTÁGIO
@login_required
def listar_planos_curso_estagio(request):
    """Lista todos os Planos de Curso/Estágio"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de curso/estágio.')
        return redirect('militares:ensino_dashboard')
    
    planos = PlanoCursoEstagio.objects.select_related(
        'projeto_pedagogico__curso', 'turma'
    ).all().order_by('-ano_edicao', '-edicao')
    
    # Paginação
    paginator = Paginator(planos, 20)
    page = request.GET.get('page')
    planos = paginator.get_page(page)
    
    context = {
        'planos': planos,
    }
    return render(request, 'militares/ensino/ite/planos_curso_estagio/listar.html', context)


@login_required
def criar_plano_curso_estagio(request, projeto_id=None):
    """Cria um novo Plano de Curso/Estágio"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar planos de curso/estágio.')
        return redirect('militares:ensino_planos_curso_estagio_listar')
    
    projeto = None
    if projeto_id:
        projeto = get_object_or_404(ProjetoPedagogico, pk=projeto_id)
    
    if request.method == 'POST':
        form = PlanoCursoEstagioForm(request.POST)
        if form.is_valid():
            plano = form.save(commit=False)
            plano.aprovado_por = request.user
            plano.save()
            messages.success(request, 'Plano de Curso/Estágio criado com sucesso!')
            return redirect('militares:ensino_planos_curso_estagio_detalhes', pk=plano.pk)
    else:
        initial = {}
        if projeto:
            initial['projeto_pedagogico'] = projeto
        form = PlanoCursoEstagioForm(initial=initial)
    
    context = {
        'form': form,
        'projeto': projeto,
        'titulo': 'Criar Plano de Curso/Estágio',
    }
    return render(request, 'militares/ensino/ite/planos_curso_estagio/criar.html', context)


@login_required
def detalhes_plano_curso_estagio(request, pk):
    """Detalhes de um Plano de Curso/Estágio"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de curso/estágio.')
        return redirect('militares:ensino_dashboard')
    
    plano = get_object_or_404(
        PlanoCursoEstagio.objects.select_related(
            'projeto_pedagogico__curso', 'turma',
            'coordenador_geral', 'coordenador_curso', 'supervisor_curso'
        ),
        pk=pk
    )
    
    context = {
        'plano': plano,
    }
    return render(request, 'militares/ensino/ite/planos_curso_estagio/detalhes.html', context)


# PROCESSO DE SELEÇÃO DE ALUNOS
@login_required
def listar_processos_selecao(request):
    """Lista todos os Processos de Seleção de Alunos"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar processos de seleção.')
        return redirect('militares:ensino_dashboard')
    
    processos = ProcessoSelecaoAlunos.objects.select_related(
        'curso', 'turma', 'homologado_por'
    ).prefetch_related('comissao_conducao_trabalhos').all().order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(processos, 20)
    page = request.GET.get('page')
    processos = paginator.get_page(page)
    
    context = {
        'processos': processos,
    }
    return render(request, 'militares/ensino/ite/processos_selecao/listar.html', context)


@login_required
def criar_processo_selecao(request, curso_id=None):
    """Cria um novo Processo de Seleção de Alunos"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar processos de seleção.')
        return redirect('militares:ensino_processos_selecao_listar')
    
    curso = None
    if curso_id:
        curso = get_object_or_404(CursoEnsino, pk=curso_id)
    
    if request.method == 'POST':
        form = ProcessoSelecaoAlunosForm(request.POST)
        if form.is_valid():
            processo = form.save()
            # Processar comissão de condução de trabalhos
            comissao_ids = request.POST.getlist('comissao_conducao_trabalhos')
            if comissao_ids:
                processo.comissao_conducao_trabalhos.set(
                    Militar.objects.filter(pk__in=comissao_ids)
                )
            messages.success(request, 'Processo de Seleção criado com sucesso!')
            return redirect('militares:ensino_processos_selecao_detalhes', pk=processo.pk)
    else:
        initial = {}
        if curso:
            initial['curso'] = curso
        form = ProcessoSelecaoAlunosForm(initial=initial)
    
    context = {
        'form': form,
        'curso': curso,
        'titulo': 'Criar Processo de Seleção de Alunos',
    }
    return render(request, 'militares/ensino/ite/processos_selecao/criar.html', context)


@login_required
def detalhes_processo_selecao(request, pk):
    """Detalhes de um Processo de Seleção de Alunos"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar processos de seleção.')
        return redirect('militares:ensino_dashboard')
    
    processo = get_object_or_404(
        ProcessoSelecaoAlunos.objects.select_related(
            'curso', 'turma', 'homologado_por'
        ).prefetch_related(
            'comissao_conducao_trabalhos', 'inscricoes__militar'
        ),
        pk=pk
    )
    inscricoes = processo.inscricoes.all().select_related('militar').order_by('classificacao', 'militar')
    
    context = {
        'processo': processo,
        'inscricoes': inscricoes,
    }
    return render(request, 'militares/ensino/ite/processos_selecao/detalhes.html', context)


# RELATÓRIO ANUAL DA DEIP
@login_required
def listar_relatorios_anuais_deip(request):
    """Lista todos os Relatórios Anuais da DEIP"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar relatórios anuais.')
        return redirect('militares:ensino_dashboard')
    
    relatorios = RelatorioAnualDEIP.objects.all().order_by('-ano_referencia')
    
    # Paginação
    paginator = Paginator(relatorios, 20)
    page = request.GET.get('page')
    relatorios = paginator.get_page(page)
    
    context = {
        'relatorios': relatorios,
    }
    return render(request, 'militares/ensino/ite/relatorios_anuais/listar.html', context)


@login_required
def criar_relatorio_anual_deip(request):
    """Cria um novo Relatório Anual da DEIP"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar relatórios anuais.')
        return redirect('militares:ensino_relatorios_anuais_listar')
    
    if request.method == 'POST':
        form = RelatorioAnualDEIPForm(request.POST, request.FILES)
        if form.is_valid():
            relatorio = form.save(commit=False)
            relatorio.elaborado_por = request.user
            relatorio.save()
            messages.success(request, 'Relatório Anual criado com sucesso!')
            return redirect('militares:ensino_relatorios_anuais_detalhes', pk=relatorio.pk)
    else:
        form = RelatorioAnualDEIPForm()
    
    context = {
        'form': form,
        'titulo': 'Criar Relatório Anual da DEIP',
    }
    return render(request, 'militares/ensino/ite/relatorios_anuais/criar.html', context)


@login_required
def detalhes_relatorio_anual_deip(request, pk):
    """Detalhes de um Relatório Anual da DEIP"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar relatórios anuais.')
        return redirect('militares:ensino_dashboard')
    
    relatorio = get_object_or_404(RelatorioAnualDEIP, pk=pk)
    
    context = {
        'relatorio': relatorio,
    }
    return render(request, 'militares/ensino/ite/relatorios_anuais/detalhes.html', context)


# TRABALHO DE CONCLUSÃO DE CURSO (TCC)
@login_required
def listar_trabalhos_conclusao_curso(request):
    """Lista todos os Trabalhos de Conclusão de Curso"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar trabalhos de conclusão de curso.')
        return redirect('militares:ensino_dashboard')
    
    tccs = TrabalhoConclusaoCurso.objects.select_related(
        'aluno', 'curso', 'turma', 'orientador_militar', 'orientador_externo'
    ).prefetch_related('banca_examinadora').all().order_by('-data_entrega')
    tccs = _filtrar_qs_por_vinculo(request.user, tccs)
    
    # Filtros
    curso_id = request.GET.get('curso')
    turma_id = request.GET.get('turma')
    status = request.GET.get('status')
    
    if curso_id:
        tccs = tccs.filter(curso_id=curso_id)
    if turma_id:
        tccs = tccs.filter(turma_id=turma_id)
    if status:
        tccs = tccs.filter(status=status)
    
    # Paginação
    paginator = Paginator(tccs, 20)
    page = request.GET.get('page')
    tccs = paginator.get_page(page)
    
    context = {
        'tccs': tccs,
        'cursos': CursoEnsino.objects.filter(ativo=True),
        'status_choices': TrabalhoConclusaoCurso.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/ite/tccs/listar.html', context)


@login_required
def criar_trabalho_conclusao_curso(request, aluno_id=None):
    """Cria um novo Trabalho de Conclusão de Curso"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar trabalhos de conclusão de curso.')
        return redirect('militares:ensino_tccs_listar')
    
    aluno = None
    if aluno_id:
        aluno = get_object_or_404(AlunoEnsino, pk=aluno_id)
        if _eh_coordenador_ou_supervisor(request.user):
            turma = getattr(aluno, 'turma', None)
            if turma and not _usuario_vinculado_turma(request.user, turma):
                messages.error(request, 'Acesso negado. Você só pode criar TCC para turmas em que está vinculado.')
                return redirect('militares:ensino_tccs_listar')
    
    if request.method == 'POST':
        form = TrabalhoConclusaoCursoForm(request.POST, request.FILES)
        if form.is_valid():
            tcc = form.save()
            # Processar banca examinadora
            banca_ids = request.POST.getlist('banca_examinadora')
            if banca_ids:
                tcc.banca_examinadora.set(
                    Militar.objects.filter(pk__in=banca_ids)
                )
            messages.success(request, 'Trabalho de Conclusão de Curso criado com sucesso!')
            return redirect('militares:ensino_tccs_detalhes', pk=tcc.pk)
    else:
        initial = {}
        if aluno:
            initial['aluno'] = aluno
            if aluno.turma:
                initial['turma'] = aluno.turma
                if aluno.turma.curso:
                    initial['curso'] = aluno.turma.curso
        form = TrabalhoConclusaoCursoForm(initial=initial)
    
    context = {
        'form': form,
        'aluno': aluno,
        'titulo': 'Criar Trabalho de Conclusão de Curso (TCC)',
    }
    return render(request, 'militares/ensino/ite/tccs/criar.html', context)


@login_required
def detalhes_trabalho_conclusao_curso(request, pk):
    """Detalhes de um Trabalho de Conclusão de Curso"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar trabalhos de conclusão de curso.')
        return redirect('militares:ensino_dashboard')
    
    tcc = get_object_or_404(
        TrabalhoConclusaoCurso.objects.select_related(
            'aluno', 'curso', 'turma', 'orientador_militar', 'orientador_externo'
        ).prefetch_related('banca_examinadora'),
        pk=pk
    )
    if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_obj_ensino(request.user, tcc):
        messages.error(request, 'Acesso negado. Você só pode acessar TCCs vinculados aos seus cursos/turmas.')
        return redirect('militares:ensino_tccs_listar')
    
    context = {
        'tcc': tcc,
    }
    return render(request, 'militares/ensino/ite/tccs/detalhes.html', context)


@login_required
def editar_trabalho_conclusao_curso(request, pk):
    """Edita um Trabalho de Conclusão de Curso"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar trabalhos de conclusão de curso.')
        return redirect('militares:ensino_tccs_listar')
    
    tcc = get_object_or_404(TrabalhoConclusaoCurso, pk=pk)
    if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_obj_ensino(request.user, tcc):
        messages.error(request, 'Acesso negado. Você só pode editar TCCs vinculados aos seus cursos/turmas.')
        return redirect('militares:ensino_tccs_listar')
    
    if request.method == 'POST':
        form = TrabalhoConclusaoCursoForm(request.POST, request.FILES, instance=tcc)
        if form.is_valid():
            tcc = form.save()
            # Processar banca examinadora
            banca_ids = request.POST.getlist('banca_examinadora')
            tcc.banca_examinadora.set(
                Militar.objects.filter(pk__in=banca_ids) if banca_ids else []
            )
            messages.success(request, 'Trabalho de Conclusão de Curso atualizado com sucesso!')
            return redirect('militares:ensino_tccs_detalhes', pk=tcc.pk)
    else:
        form = TrabalhoConclusaoCursoForm(instance=tcc)
    
    context = {
        'form': form,
        'tcc': tcc,
        'titulo': 'Editar Trabalho de Conclusão de Curso (TCC)',
    }
    return render(request, 'militares/ensino/ite/tccs/editar.html', context)


# PLANO DE SEGURANÇA
@login_required
def listar_planos_seguranca(request):
    """Lista todos os Planos de Segurança"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de segurança.')
        return redirect('militares:ensino_dashboard')
    
    planos = PlanoSeguranca.objects.select_related(
        'curso', 'turma', 'disciplina', 'aula',
        'responsavel_coordenacao', 'responsavel_supervisao', 'aprovado_por'
    ).all().order_by('-data_atividade')
    planos = _filtrar_qs_por_vinculo(request.user, planos)
    
    # Filtros
    curso_id = request.GET.get('curso')
    turma_id = request.GET.get('turma')
    status = request.GET.get('status')
    
    if curso_id:
        planos = planos.filter(curso_id=curso_id)
    if turma_id:
        planos = planos.filter(turma_id=turma_id)
    if status:
        planos = planos.filter(status=status)
    
    # Paginação
    paginator = Paginator(planos, 20)
    page = request.GET.get('page')
    planos = paginator.get_page(page)
    
    context = {
        'planos': planos,
        'cursos': CursoEnsino.objects.filter(ativo=True),
        'status_choices': PlanoSeguranca.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/ite/planos_seguranca/listar.html', context)


@login_required
def criar_plano_seguranca(request, curso_id=None, turma_id=None, disciplina_id=None, aula_id=None):
    """Cria um novo Plano de Segurança"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar planos de segurança.')
        return redirect('militares:ensino_planos_seguranca_listar')
    
    curso = turma = disciplina = aula = None
    if curso_id:
        curso = get_object_or_404(CursoEnsino, pk=curso_id)
        if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_curso(request.user, curso):
            messages.error(request, 'Acesso negado ao curso informado.')
            return redirect('militares:ensino_planos_seguranca_listar')
    if turma_id:
        turma = get_object_or_404(TurmaEnsino, pk=turma_id)
        if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
            messages.error(request, 'Acesso negado à turma informada.')
            return redirect('militares:ensino_planos_seguranca_listar')
    if disciplina_id:
        disciplina = get_object_or_404(DisciplinaEnsino, pk=disciplina_id)
    if aula_id:
        aula = get_object_or_404(AulaEnsino, pk=aula_id)
    
    if request.method == 'POST':
        form = PlanoSegurancaForm(request.POST, request.FILES)
        if form.is_valid():
            plano = form.save(commit=False)
            if not plano.aprovado_por:
                plano.aprovado_por = request.user.militar if hasattr(request.user, 'militar') else None
            plano.save()
            messages.success(request, 'Plano de Segurança criado com sucesso!')
            return redirect('militares:ensino_planos_seguranca_detalhes', pk=plano.pk)
    else:
        initial = {}
        if curso:
            initial['curso'] = curso
        if turma:
            initial['turma'] = turma
        if disciplina:
            initial['disciplina'] = disciplina
        if aula:
            initial['aula'] = aula
        form = PlanoSegurancaForm(initial=initial)
    
    context = {
        'form': form,
        'curso': curso,
        'turma': turma,
        'disciplina': disciplina,
        'aula': aula,
        'titulo': 'Criar Plano de Segurança',
    }
    return render(request, 'militares/ensino/ite/planos_seguranca/criar.html', context)


@login_required
def detalhes_plano_seguranca(request, pk):
    """Detalhes de um Plano de Segurança"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de segurança.')
        return redirect('militares:ensino_dashboard')
    
    plano = get_object_or_404(
        PlanoSeguranca.objects.select_related(
            'curso', 'turma', 'disciplina', 'aula',
            'responsavel_coordenacao', 'responsavel_supervisao', 'aprovado_por'
        ),
        pk=pk
    )
    if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_obj_ensino(request.user, plano):
        messages.error(request, 'Acesso negado. Você só pode acessar planos vinculados aos seus cursos/turmas.')
        return redirect('militares:ensino_planos_seguranca_listar')
    
    context = {
        'plano': plano,
    }
    return render(request, 'militares/ensino/ite/planos_seguranca/detalhes.html', context)


@login_required
def editar_plano_seguranca(request, pk):
    """Edita um Plano de Segurança"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para editar planos de segurança.')
        return redirect('militares:ensino_planos_seguranca_listar')
    
    plano = get_object_or_404(PlanoSeguranca, pk=pk)
    if _eh_coordenador_ou_supervisor_curso(request.user) and not _usuario_vinculado_obj_ensino(request.user, plano):
        messages.error(request, 'Acesso negado. Você só pode editar planos vinculados aos seus cursos/turmas.')
        return redirect('militares:ensino_planos_seguranca_listar')
    
    if request.method == 'POST':
        form = PlanoSegurancaForm(request.POST, request.FILES, instance=plano)
        if form.is_valid():
            plano = form.save()
            messages.success(request, 'Plano de Segurança atualizado com sucesso!')
            return redirect('militares:ensino_planos_seguranca_detalhes', pk=plano.pk)
    else:
        form = PlanoSegurancaForm(instance=plano)
    
    context = {
        'form': form,
        'plano': plano,
        'titulo': 'Editar Plano de Segurança',
    }
    return render(request, 'militares/ensino/ite/planos_seguranca/editar.html', context)


# CLASSIFICAÇÃO FINAL DO CURSO
@login_required
def listar_classificacoes_finais(request, turma_id=None):
    """Lista todas as Classificações Finais de Curso"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar classificações finais.')
        return redirect('militares:ensino_dashboard')
    
    classificacoes = ClassificacaoFinalCurso.objects.select_related(
        'aluno__militar', 'aluno__pessoa_externa', 'curso', 'turma'
    ).all()
    
    if turma_id:
        classificacoes = classificacoes.filter(turma_id=turma_id)
        turma = get_object_or_404(TurmaEnsino.objects.select_related('curso'), pk=turma_id)
        if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
            messages.error(request, 'Acesso negado à turma informada.')
            return redirect('militares:ensino_turmas_listar')
    else:
        turma = None
    
    # Ordenar: primeiro por turma, depois por classificação (1, 2, 3...)
    # Aprovados diretos primeiro, depois aprovados com recuperação
    classificacoes = classificacoes.order_by(
        'turma', 
        '-aprovado_direto',  # True (1) vem antes de False (0)
        'classificacao'
    )
    
    # Paginação
    paginator = Paginator(classificacoes, 50)
    page = request.GET.get('page')
    classificacoes = paginator.get_page(page)
    
    # Estatísticas
    total_alunos = classificacoes.paginator.count if classificacoes else 0
    total_aprovados_diretos = classificacoes.paginator.object_list.filter(aprovado_direto=True).count() if classificacoes else 0
    
    context = {
        'classificacoes': classificacoes,
        'turma': turma,
        'total_alunos': total_alunos,
        'total_aprovados_diretos': total_aprovados_diretos,
    }
    return render(request, 'militares/ensino/ite/classificacoes_finais/listar.html', context)


@login_required
def calcular_classificacao_final(request, turma_id):
    """Calcula e atualiza a classificação final de uma turma"""
    if not pode_editar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para calcular classificações finais.')
        return redirect('militares:ensino_turmas_listar')
    
    turma = get_object_or_404(TurmaEnsino.objects.select_related('curso'), pk=turma_id)
    if _eh_coordenador_ou_supervisor(request.user) and not _usuario_vinculado_turma(request.user, turma):
        messages.error(request, 'Acesso negado à turma informada.')
        return redirect('militares:ensino_turmas_listar')
    
    # Buscar todos os alunos ativos da turma
    alunos = AlunoEnsino.objects.filter(
        turma=turma,
        situacao='ATIVO'
    ).select_related('militar', 'pessoa_externa')
    
    # Buscar aproveitamentos de todas as disciplinas (aprovados e reprovados)
    aproveitamentos_aprovados = AproveitamentoDisciplina.objects.filter(
        turma=turma,
        aprovado=True
    ).select_related('aluno', 'disciplina')
    
    aproveitamentos_todos = AproveitamentoDisciplina.objects.filter(
        turma=turma
    ).select_related('aluno', 'disciplina')
    
    # Calcular MGM e MFC para cada aluno
    # Buscar todas as disciplinas do curso/turma para calcular o total
    from militares.models import DisciplinaCurso
    disciplinas_curso = []
    if turma.curso:
        disciplinas_curso = DisciplinaCurso.objects.filter(curso=turma.curso).select_related('disciplina')
        disciplinas_curso = [dc.disciplina for dc in disciplinas_curso]
    # Também incluir disciplinas diretamente da turma
    disciplinas_turma_direta = turma.disciplinas.all()
    todas_disciplinas_ids = set([d.pk for d in disciplinas_curso] + [d.pk for d in disciplinas_turma_direta])
    total_disciplinas_curso = len(todas_disciplinas_ids)
    
    classificacoes = []
    for aluno in alunos:
        # Buscar MGM de TODAS as disciplinas do aluno (aprovadas e reprovadas)
        # MFC = MGM ÷ Total de disciplinas
        aproveitamentos_aluno = aproveitamentos_todos.filter(aluno=aluno).select_related('disciplina')
        
        # Coletar todas as MGM das disciplinas do curso
        # Criar um dicionário para mapear disciplina_id -> MGM
        mgm_por_disciplina = {}
        for aproveitamento in aproveitamentos_aluno:
            if aproveitamento.disciplina_id in todas_disciplinas_ids:
                mgm = aproveitamento.media_geral_materia
                if mgm is not None:
                    mgm_por_disciplina[aproveitamento.disciplina_id] = float(mgm)
                else:
                    # Se não tem MGM, considerar como zero
                    mgm_por_disciplina[aproveitamento.disciplina_id] = 0.0
        
        # Coletar MGM de todas as disciplinas do curso (incluindo as que não têm aproveitamento = 0.0)
        # MFC = MGM ÷ Total de disciplinas
        mgms_todas = []
        for disciplina_id in todas_disciplinas_ids:
            if disciplina_id in mgm_por_disciplina:
                mgms_todas.append(mgm_por_disciplina[disciplina_id])
            else:
                # Se não tem aproveitamento nesta disciplina, considerar MGM = 0.0
                mgms_todas.append(0.0)
        
        from decimal import Decimal
        
        # Contar reprovadas verificando cada disciplina individualmente
        # Isso garante que reprovações após recuperação sejam contadas corretamente
        total_reprovadas = 0
        
        for aproveitamento in aproveitamentos_aluno:
            reprovou = False
            
            # Se não está aprovado, está reprovado
            if not aproveitamento.aprovado:
                reprovou = True
            # Se fez recuperação, verificar se passou
            elif aproveitamento.fez_recuperacao:
                # Buscar média mínima de recuperação da disciplina (padrão 6.0)
                media_minima_recuperacao = Decimal('6.0')
                if aproveitamento.disciplina and aproveitamento.disciplina.media_minima_recuperacao:
                    media_minima_recuperacao = Decimal(str(aproveitamento.disciplina.media_minima_recuperacao))
                
                # Se tem nota de recuperação e é menor que a média mínima, está reprovado
                if aproveitamento.nota_recuperacao:
                    if Decimal(str(aproveitamento.nota_recuperacao)) < media_minima_recuperacao:
                        reprovou = True
                # Se fez recuperação mas não tem nota e não está aprovado, está reprovado
                elif not aproveitamento.aprovado:
                    reprovou = True
            
            if reprovou:
                total_reprovadas += 1
        
        # Calcular MFC: MFC = MGM ÷ Total de disciplinas
        # MFC = média aritmética das MGM de todas as disciplinas do curso
        mfc = None
        if total_disciplinas_curso > 0:
            # Se não temos MGM para todas as disciplinas, usar as que temos
            if mgms_todas:
                mfc = round(sum(mgms_todas) / total_disciplinas_curso, 3)
            else:
                mfc = 0.0
        
        # Verificar se fez recuperação (apenas entre as aprovadas)
        fez_recuperacao = False
        if aproveitamentos_aprovados.filter(aluno=aluno).exists():
            fez_recuperacao = aproveitamentos_aprovados.filter(
                aluno=aluno,
                fez_recuperacao=True
            ).exists()
        
        # Criar ou atualizar classificação para TODOS os alunos, mesmo os que reprovaram em tudo
        classificacao, created = ClassificacaoFinalCurso.objects.update_or_create(
            aluno=aluno,
            curso=turma.curso,
            turma=turma,
            defaults={
                'media_final_curso': mfc,
                'aprovado_direto': not fez_recuperacao if mfc is not None else False,
                'aprovado_com_recuperacao': fez_recuperacao,
                'total_disciplinas_reprovadas': total_reprovadas,
            }
        )
        classificacoes.append(classificacao)
    
    # Separar aprovados diretos, com recuperação e reprovados
    aprovados_diretos = [c for c in classificacoes if c.aprovado_direto and c.media_final_curso is not None]
    aprovados_recuperacao = [c for c in classificacoes if c.aprovado_com_recuperacao and c.media_final_curso is not None]
    reprovados = [c for c in classificacoes if c.media_final_curso is None or c.total_disciplinas_reprovadas > 0]
    
    # Funções auxiliares para obter critérios de desempate
    def get_antiguidade_classificacao(classificacao):
        """Retorna critério de antiguidade para desempate na classificação final"""
        aluno = classificacao.aluno
        if aluno.militar:
            # Para militares: usar numeração de antiguidade (menor = mais antigo) ou data de promoção
            if aluno.militar.numeracao_antiguidade is not None:
                return aluno.militar.numeracao_antiguidade
            elif aluno.militar.data_promocao_atual:
                return aluno.militar.data_promocao_atual
            else:
                return date.max
        else:
            return 999999
    
    def get_idade_classificacao(classificacao):
        """Retorna data de nascimento para desempate por idade (mais velho = data mais antiga = menor valor)"""
        aluno = classificacao.aluno
        if aluno.militar and aluno.militar.data_nascimento:
            return aluno.militar.data_nascimento
        elif aluno.pessoa_externa and hasattr(aluno.pessoa_externa, 'data_nascimento') and aluno.pessoa_externa.data_nascimento:
            return aluno.pessoa_externa.data_nascimento
        else:
            return date.max
    
    # ITE 18.3.a) Aprovados Direto: Ordenar por MFC decrescente
    # Os alunos aprovados sem recuperação serão classificados em ordem decrescente, 
    # de acordo com a Média Final do Curso (MFC)
    # ITE 18.5: Quando houver igualdade de MFC, o desempate obedecerá à precedência hierárquica
    # Desempate: 1º critério = antiguidade, 2º critério = idade (mais velho fica na frente)
    aprovados_diretos.sort(key=lambda x: (
        -(x.media_final_curso or 0),  # Negativo para ordem decrescente (maior MFC primeiro)
        get_antiguidade_classificacao(x),  # 1º critério de desempate: precedência hierárquica (antiguidade)
        get_idade_classificacao(x)  # 2º critério de desempate: idade (data nascimento mais antiga = mais velho)
    ))
    
    # Atualizar MFC do último aprovado direto (necessário para calcular MFC ajustada)
    mfc_ultimo_direto = None
    if aprovados_diretos:
        mfc_ultimo_direto = aprovados_diretos[-1].media_final_curso
    
    # Atualizar temporariamente mfc_ultimo_aprovado_direto em todos os aprovados com recuperação
    # para permitir calcular a MFC ajustada antes de ordenar
    for classificacao in aprovados_recuperacao:
        classificacao.mfc_ultimo_aprovado_direto = mfc_ultimo_direto
    
    # ITE 18.3.b) e ITE 18.4: Aprovados com Recuperação: Ordenar por MFC AJUSTADA decrescente
    # Os alunos aprovados com recuperação também serão classificados em ordem decrescente 
    # de acordo com a MFC. No entanto, suas médias serão ajustadas de modo que não 
    # ultrapassem a MFC do último aluno aprovado direto, garantindo que permaneçam em 
    # uma classificação inferior aos aprovados sem recuperação.
    # ITE 18.4: Os discentes que incidirem em realização de recuperação (2ª época) concorrem 
    # entre si para a Classificação Final do Curso não podendo ultrapassar a classificação 
    # daqueles alunos que foram aprovados em 1ª época sem recuperação.
    # ITE 18.5: Quando houver igualdade de MFC, o desempate obedecerá à precedência hierárquica
    # Desempate: 1º critério = antiguidade, 2º critério = idade (mais velho fica na frente)
    aprovados_recuperacao.sort(key=lambda x: (
        -(float(x.calcular_mfc_ajustada() or 0)),  # Negativo para ordem decrescente - usa MFC ajustada (não ultrapassa MFC do último direto)
        get_antiguidade_classificacao(x),  # 1º critério de desempate: precedência hierárquica (antiguidade)
        get_idade_classificacao(x)  # 2º critério de desempate: idade (data nascimento mais antiga = mais velho)
    ))
    
    # Ordenar reprovados por total de disciplinas reprovadas (mais reprovadas primeiro)
    reprovados.sort(key=lambda x: x.total_disciplinas_reprovadas, reverse=True)
    
    # Atribuir classificações aos aprovados diretos (primeiro grupo)
    classificacao_num = 1
    for classificacao in aprovados_diretos:
        classificacao.classificacao = classificacao_num
        classificacao.mfc_ultimo_aprovado_direto = mfc_ultimo_direto
        # Aprovados diretos não têm MFC ajustada
        classificacao.media_final_curso_ajustada = None
        classificacao.save()
        classificacao_num += 1
    
    # Atribuir classificações para aprovados com recuperação (segundo grupo)
    for classificacao in aprovados_recuperacao:
        classificacao.classificacao = classificacao_num
        classificacao.mfc_ultimo_aprovado_direto = mfc_ultimo_direto
        # Calcular MFC ajustada para alunos em recuperação
        classificacao.media_final_curso_ajustada = classificacao.calcular_mfc_ajustada()
        classificacao.save()
        classificacao_num += 1
    
    # Alunos reprovados não recebem classificação numérica (ficam sem classificação)
    for classificacao in reprovados:
        classificacao.classificacao = None
        classificacao.mfc_ultimo_aprovado_direto = mfc_ultimo_direto
        classificacao.media_final_curso_ajustada = None
        classificacao.aprovado_direto = False
        classificacao.aprovado_com_recuperacao = False
        classificacao.save()
    
    messages.success(request, f'Classificação final calculada com sucesso! {len(classificacoes)} alunos classificados.')
    return redirect('militares:ensino_classificacoes_finais', turma_id=turma_id)


@login_required
def detalhes_classificacao_final(request, pk):
    """Detalhes de uma Classificação Final"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar classificações finais.')
        return redirect('militares:ensino_dashboard')
    
    classificacao = get_object_or_404(
        ClassificacaoFinalCurso.objects.select_related(
            'aluno', 'curso', 'turma'
        ),
        pk=pk
    )
    
    context = {
        'classificacao': classificacao,
    }
    return render(request, 'militares/ensino/ite/classificacoes_finais/detalhes.html', context)


# PLANO DE PALESTRA
@login_required
def listar_planos_palestra(request):
    """Lista todos os Planos de Palestra"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de palestra.')
        return redirect('militares:ensino_dashboard')
    
    planos = PlanoPalestra.objects.select_related(
        'curso', 'turma', 'palestrante_militar', 'palestrante_externo'
    ).all().order_by('-data_palestra')
    
    # Filtros
    curso_id = request.GET.get('curso')
    status = request.GET.get('status')
    
    if curso_id:
        planos = planos.filter(curso_id=curso_id)
    if status:
        planos = planos.filter(status=status)
    
    # Paginação
    paginator = Paginator(planos, 20)
    page = request.GET.get('page')
    planos = paginator.get_page(page)
    
    context = {
        'planos': planos,
        'cursos': CursoEnsino.objects.filter(ativo=True),
        'status_choices': PlanoPalestra.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/ite/planos_palestra/listar.html', context)


@login_required
def criar_plano_palestra(request, curso_id=None, turma_id=None):
    """Cria um novo Plano de Palestra"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar planos de palestra.')
        return redirect('militares:ensino_planos_palestra_listar')
    
    curso = turma = None
    if curso_id:
        curso = get_object_or_404(CursoEnsino, pk=curso_id)
    if turma_id:
        turma = get_object_or_404(TurmaEnsino, pk=turma_id)
    
    if request.method == 'POST':
        form = PlanoPalestraForm(request.POST)
        if form.is_valid():
            plano = form.save()
            messages.success(request, 'Plano de Palestra criado com sucesso!')
            return redirect('militares:ensino_planos_palestra_detalhes', pk=plano.pk)
    else:
        initial = {}
        if curso:
            initial['curso'] = curso
        if turma:
            initial['turma'] = turma
        form = PlanoPalestraForm(initial=initial)
    
    context = {
        'form': form,
        'curso': curso,
        'turma': turma,
        'titulo': 'Criar Plano de Palestra',
    }
    return render(request, 'militares/ensino/ite/planos_palestra/criar.html', context)


@login_required
def detalhes_plano_palestra(request, pk):
    """Detalhes de um Plano de Palestra"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de palestra.')
        return redirect('militares:ensino_dashboard')
    
    plano = get_object_or_404(
        PlanoPalestra.objects.select_related(
            'curso', 'turma', 'palestrante_militar', 'palestrante_externo'
        ),
        pk=pk
    )
    
    context = {
        'plano': plano,
    }
    return render(request, 'militares/ensino/ite/planos_palestra/detalhes.html', context)


# ATIVIDADE DE TREINAMENTO DE CAMPO (ATC)
@login_required
def listar_atividades_treinamento_campo(request):
    """Lista todas as Atividades de Treinamento de Campo"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar atividades de treinamento de campo.')
        return redirect('militares:ensino_dashboard')
    
    atcs = AtividadeTreinamentoCampo.objects.select_related(
        'curso', 'turma', 'disciplina', 'coordenador', 'supervisor'
    ).all().order_by('-data_realizacao')
    
    # Filtros
    curso_id = request.GET.get('curso')
    turma_id = request.GET.get('turma')
    status = request.GET.get('status')
    
    if curso_id:
        atcs = atcs.filter(curso_id=curso_id)
    if turma_id:
        atcs = atcs.filter(turma_id=turma_id)
    if status:
        atcs = atcs.filter(status=status)
    
    # Paginação
    paginator = Paginator(atcs, 20)
    page = request.GET.get('page')
    atcs = paginator.get_page(page)
    
    context = {
        'atcs': atcs,
        'cursos': CursoEnsino.objects.filter(ativo=True),
        'status_choices': AtividadeTreinamentoCampo.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/ite/atcs/listar.html', context)


@login_required
def criar_atividade_treinamento_campo(request, curso_id=None, turma_id=None):
    """Cria uma nova Atividade de Treinamento de Campo"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar atividades de treinamento de campo.')
        return redirect('militares:ensino_atcs_listar')
    
    curso = turma = None
    if curso_id:
        curso = get_object_or_404(CursoEnsino, pk=curso_id)
    if turma_id:
        turma = get_object_or_404(TurmaEnsino, pk=turma_id)
    
    if request.method == 'POST':
        form = AtividadeTreinamentoCampoForm(request.POST)
        if form.is_valid():
            atc = form.save()
            messages.success(request, 'Atividade de Treinamento de Campo criada com sucesso!')
            return redirect('militares:ensino_atcs_detalhes', pk=atc.pk)
    else:
        initial = {}
        if curso:
            initial['curso'] = curso
        if turma:
            initial['turma'] = turma
        form = AtividadeTreinamentoCampoForm(initial=initial)
    
    context = {
        'form': form,
        'curso': curso,
        'turma': turma,
        'titulo': 'Criar Atividade de Treinamento de Campo (ATC)',
    }
    return render(request, 'militares/ensino/ite/atcs/criar.html', context)


@login_required
def detalhes_atividade_treinamento_campo(request, pk):
    """Detalhes de uma Atividade de Treinamento de Campo"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar atividades de treinamento de campo.')
        return redirect('militares:ensino_dashboard')
    
    atc = get_object_or_404(
        AtividadeTreinamentoCampo.objects.select_related(
            'curso', 'turma', 'disciplina', 'coordenador', 'supervisor'
        ),
        pk=pk
    )
    
    context = {
        'atc': atc,
    }
    return render(request, 'militares/ensino/ite/atcs/detalhes.html', context)


# ATIVIDADE COMPLEMENTAR DE ENSINO (ACE)
@login_required
def listar_atividades_complementares(request):
    """Lista todas as Atividades Complementares de Ensino"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar atividades complementares.')
        return redirect('militares:ensino_dashboard')
    
    aces = AtividadeComplementarEnsino.objects.select_related(
        'curso', 'turma', 'responsavel'
    ).all().order_by('-data_realizacao')
    
    # Filtros
    curso_id = request.GET.get('curso')
    turma_id = request.GET.get('turma')
    tipo = request.GET.get('tipo')
    status = request.GET.get('status')
    
    if curso_id:
        aces = aces.filter(curso_id=curso_id)
    if turma_id:
        aces = aces.filter(turma_id=turma_id)
    if tipo:
        aces = aces.filter(tipo=tipo)
    if status:
        aces = aces.filter(status=status)
    
    # Paginação
    paginator = Paginator(aces, 20)
    page = request.GET.get('page')
    aces = paginator.get_page(page)
    
    context = {
        'aces': aces,
        'cursos': CursoEnsino.objects.filter(ativo=True),
        'tipo_choices': AtividadeComplementarEnsino.TIPO_CHOICES,
        'status_choices': AtividadeComplementarEnsino.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/ite/aces/listar.html', context)


@login_required
def criar_atividade_complementar(request, curso_id=None, turma_id=None):
    """Cria uma nova Atividade Complementar de Ensino"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar atividades complementares.')
        return redirect('militares:ensino_aces_listar')
    
    curso = turma = None
    if curso_id:
        curso = get_object_or_404(CursoEnsino, pk=curso_id)
    if turma_id:
        turma = get_object_or_404(TurmaEnsino, pk=turma_id)
    
    if request.method == 'POST':
        form = AtividadeComplementarEnsinoForm(request.POST)
        if form.is_valid():
            ace = form.save()
            messages.success(request, 'Atividade Complementar criada com sucesso!')
            return redirect('militares:ensino_aces_detalhes', pk=ace.pk)
    else:
        initial = {}
        if curso:
            initial['curso'] = curso
        if turma:
            initial['turma'] = turma
        form = AtividadeComplementarEnsinoForm(initial=initial)
    
    context = {
        'form': form,
        'curso': curso,
        'turma': turma,
        'titulo': 'Criar Atividade Complementar de Ensino (ACE)',
    }
    return render(request, 'militares/ensino/ite/aces/criar.html', context)


@login_required
def detalhes_atividade_complementar(request, pk):
    """Detalhes de uma Atividade Complementar de Ensino"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar atividades complementares.')
        return redirect('militares:ensino_dashboard')
    
    ace = get_object_or_404(
        AtividadeComplementarEnsino.objects.select_related(
            'curso', 'turma', 'responsavel'
        ),
        pk=pk
    )
    
    context = {
        'ace': ace,
    }
    return render(request, 'militares/ensino/ite/aces/detalhes.html', context)


# TESTE DE CONHECIMENTOS PROFISSIONAIS (TCP)
@login_required
def listar_testes_conhecimentos_profissionais(request):
    """Lista todos os Testes de Conhecimentos Profissionais"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar testes de conhecimentos profissionais.')
        return redirect('militares:ensino_dashboard')
    
    tcps = TesteConhecimentosProfissionais.objects.select_related(
        'coordenador'
    ).all().order_by('-data_aplicacao')
    
    # Filtros
    tipo = request.GET.get('tipo')
    status = request.GET.get('status')
    
    if tipo:
        tcps = tcps.filter(tipo=tipo)
    if status:
        tcps = tcps.filter(status=status)
    
    # Paginação
    paginator = Paginator(tcps, 20)
    page = request.GET.get('page')
    tcps = paginator.get_page(page)
    
    context = {
        'tcps': tcps,
        'tipo_choices': TesteConhecimentosProfissionais.TIPO_CHOICES,
        'status_choices': TesteConhecimentosProfissionais.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/ite/tcps/listar.html', context)


@login_required
def criar_teste_conhecimentos_profissionais(request):
    """Cria um novo Teste de Conhecimentos Profissionais"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar testes de conhecimentos profissionais.')
        return redirect('militares:ensino_tcps_listar')
    
    if request.method == 'POST':
        form = TesteConhecimentosProfissionaisForm(request.POST)
        if form.is_valid():
            tcp = form.save()
            messages.success(request, 'Teste de Conhecimentos Profissionais criado com sucesso!')
            return redirect('militares:ensino_tcps_detalhes', pk=tcp.pk)
    else:
        form = TesteConhecimentosProfissionaisForm()
    
    context = {
        'form': form,
        'titulo': 'Criar Teste de Conhecimentos Profissionais (TCP)',
    }
    return render(request, 'militares/ensino/ite/tcps/criar.html', context)


@login_required
def detalhes_teste_conhecimentos_profissionais(request, pk):
    """Detalhes de um Teste de Conhecimentos Profissionais"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar testes de conhecimentos profissionais.')
        return redirect('militares:ensino_dashboard')
    
    tcp = get_object_or_404(
        TesteConhecimentosProfissionais.objects.select_related('coordenador'),
        pk=pk
    )
    
    context = {
        'tcp': tcp,
    }
    return render(request, 'militares/ensino/ite/tcps/detalhes.html', context)


# PLANO DE ESTÁGIO DE NIVELAMENTO PROFISSIONAL
@login_required
def listar_planos_estagio_nivelamento(request):
    """Lista todos os Planos de Estágio de Nivelamento Profissional"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de estágio de nivelamento.')
        return redirect('militares:ensino_dashboard')
    
    planos = PlanoEstagioNivelamentoProfissional.objects.select_related(
        'coordenador', 'supervisor'
    ).all().order_by('-ano_edicao', '-edicao')
    
    # Filtros
    status = request.GET.get('status')
    if status:
        planos = planos.filter(status=status)
    
    # Paginação
    paginator = Paginator(planos, 20)
    page = request.GET.get('page')
    planos = paginator.get_page(page)
    
    context = {
        'planos': planos,
        'status_choices': PlanoEstagioNivelamentoProfissional.STATUS_CHOICES,
    }
    return render(request, 'militares/ensino/ite/planos_estagio_nivelamento/listar.html', context)


@login_required
def criar_plano_estagio_nivelamento(request):
    """Cria um novo Plano de Estágio de Nivelamento Profissional"""
    if not pode_criar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para criar planos de estágio de nivelamento.')
        return redirect('militares:ensino_planos_estagio_nivelamento_listar')
    
    if request.method == 'POST':
        form = PlanoEstagioNivelamentoProfissionalForm(request.POST)
        if form.is_valid():
            plano = form.save()
            messages.success(request, 'Plano de Estágio de Nivelamento criado com sucesso!')
            return redirect('militares:ensino_planos_estagio_nivelamento_detalhes', pk=plano.pk)
    else:
        form = PlanoEstagioNivelamentoProfissionalForm()
    
    context = {
        'form': form,
        'titulo': 'Criar Plano de Estágio de Nivelamento Profissional',
    }
    return render(request, 'militares/ensino/ite/planos_estagio_nivelamento/criar.html', context)


@login_required
def detalhes_plano_estagio_nivelamento(request, pk):
    """Detalhes de um Plano de Estágio de Nivelamento Profissional"""
    if not pode_visualizar_ensino(request.user):
        messages.error(request, 'Você não tem permissão para visualizar planos de estágio de nivelamento.')
        return redirect('militares:ensino_dashboard')
    
    plano = get_object_or_404(
        PlanoEstagioNivelamentoProfissional.objects.select_related(
            'coordenador', 'supervisor'
        ),
        pk=pk
    )
    
    context = {
        'plano': plano,
    }
    return render(request, 'militares/ensino/ite/planos_estagio_nivelamento/detalhes.html', context)
