# -*- coding: utf-8 -*-
"""
Views para Dashboards Iniciais do Módulo de Ensino
Páginas iniciais específicas para Alunos, Instrutores, Supervisores e Coordenadores
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.contrib import messages

from .models import (
    AlunoEnsino, InstrutorEnsino, MonitorEnsino, TurmaEnsino, AulaEnsino, FrequenciaAula,
    NotaAvaliacao, AvaliacaoEnsino, QuadroTrabalhoSemanal, AulaQuadroTrabalhoSemanal,
    Militar, PessoaExterna, PedidoRevisaoProva
)


def identificar_tipo_usuario_ensino(user):
    """
    Identifica o tipo de usuário no módulo de ensino
    Retorna: 'aluno', 'instrutor', 'supervisor', 'coordenador' ou None
    """
    if not user or not user.is_authenticated:
        return None
    
    # Verificar se é aluno
    try:
        militar = user.militar if hasattr(user, 'militar') else None
        if militar:
            aluno = AlunoEnsino.objects.filter(
                militar=militar,
                situacao='ATIVO'
            ).first()
            if aluno:
                return 'aluno'
    except:
        pass
    
    # Verificar se é instrutor
    try:
        if militar:
            instrutor = InstrutorEnsino.objects.filter(
                militar=militar,
                ativo=True
            ).first()
            if instrutor:
                return 'instrutor'
    except:
        pass
    
    # Verificar se é supervisor ou coordenador
    try:
        if militar:
            # Verificar supervisor de curso
            supervisor_curso = TurmaEnsino.objects.filter(
                supervisor_curso=militar
            ).exists()
            
            # Verificar supervisor de turma
            supervisor_turma = TurmaEnsino.objects.filter(
                supervisor_turma=militar
            ).exists()
            
            # Verificar coordenador de curso
            coordenador_curso = TurmaEnsino.objects.filter(
                coordenador_curso=militar
            ).exists()
            
            # Verificar coordenador de turma
            coordenador_turma = TurmaEnsino.objects.filter(
                coordenador_turma=militar
            ).exists()
            
            # Prioridade: coordenador > supervisor
            if coordenador_curso or coordenador_turma:
                return 'coordenador'
            elif supervisor_curso or supervisor_turma:
                return 'supervisor'
    except:
        pass
    
    return None


@login_required(login_url='militares:ensino_login')
def dashboard_aluno(request):
    """Dashboard inicial para alunos"""
    try:
        # Verificar se é login do módulo de ensino através da sessão
        ensino_tipo = request.session.get('ensino_tipo')
        ensino_id = request.session.get('ensino_id')
        
        if ensino_tipo == 'aluno' and ensino_id:
            # Buscar aluno através do ID da sessão
            aluno = AlunoEnsino.objects.filter(
                pk=ensino_id,
                situacao='ATIVO'
            ).select_related('turma', 'turma__curso').first()
        else:
            # Tentar buscar através do militar (para compatibilidade)
            militar = request.user.militar if hasattr(request.user, 'militar') else None
            if not militar:
                messages.warning(request, 'Você não possui perfil de militar cadastrado.')
                request.session['ensino_login_bypass_auto'] = True
                request.session.pop('ensino_tipo', None)
                request.session.pop('ensino_id', None)
                return redirect('login')
            
            # Buscar aluno ativo
            aluno = AlunoEnsino.objects.filter(
                militar=militar,
                situacao='ATIVO'
            ).select_related('turma', 'turma__curso').first()
        
        if not aluno:
            messages.info(request, 'Você não está matriculado em nenhuma turma ativa.')
            request.session['ensino_login_bypass_auto'] = True
            request.session.pop('ensino_tipo', None)
            request.session.pop('ensino_id', None)
            return redirect('login')
        
        turma = aluno.turma
        
        if not turma:
            # Aluno sem turma: retornar dashboard básico com dados vazios
            context = {
                'aluno': aluno,
                'turma': None,
                'total_aulas': 0,
                'aulas_realizadas': 0,
                'aulas_previstas': 0,
                'total_frequencias': 0,
                'frequencias_presentes': 0,
                'frequencias_faltas': 0,
                'percentual_frequencia': 0,
                'total_notas': 0,
                'media_geral': 0,
                'proximas_aulas': AulaEnsino.objects.none(),
                'avaliacoes_pendentes': AvaliacaoEnsino.objects.none(),
                'quadros_trabalho': QuadroTrabalhoSemanal.objects.none(),
                'disciplinas_info': [],
            }
            return render(request, 'militares/ensino/dashboards/dashboard_aluno.html', context)
        
        # Estatísticas do aluno com turma
        aulas_turma = AulaEnsino.objects.filter(turma=turma)
        total_aulas = aulas_turma.count()
        aulas_realizadas = aulas_turma.filter(data_aula__lte=date.today()).count()
        aulas_previstas = aulas_turma.filter(data_aula__gt=date.today()).count()
        
        frequencias = FrequenciaAula.objects.filter(
            aluno=aluno,
            aula__turma=turma
        ).select_related('aula')
        total_frequencias = frequencias.count()
        frequencias_presentes = frequencias.filter(presenca='PRESENTE').count()
        frequencias_faltas = frequencias.exclude(presenca='PRESENTE').count()
        percentual_frequencia = (frequencias_presentes / total_frequencias * 100) if total_frequencias > 0 else 0
        
        notas = NotaAvaliacao.objects.filter(
            aluno=aluno,
            avaliacao__turma=turma
        ).select_related('avaliacao', 'avaliacao__disciplina')
        total_notas = notas.count()
        media_geral = notas.aggregate(media=Avg('nota'))['media'] or 0
        
        proximas_aulas = aulas_turma.filter(
            data_aula__gte=date.today(),
            data_aula__lte=date.today() + timedelta(days=7)
        ).select_related('disciplina', 'instrutor').order_by('data_aula', 'hora_inicio')[:5]
        
        avaliacoes_pendentes = AvaliacaoEnsino.objects.filter(
            turma=turma,
            data_avaliacao__gte=date.today()
        ).select_related('disciplina').order_by('data_avaliacao')[:5]
        
        quadros_trabalho = QuadroTrabalhoSemanal.objects.filter(
            turma=turma
        ).order_by('-data_inicio_semana', '-numero_quadro')[:5]
        
        disciplinas_turma = turma.disciplinas.all().order_by('nome')

        revisoes_aluno = PedidoRevisaoProva.objects.filter(
            aluno=aluno
        ).select_related('nota_avaliacao__avaliacao__disciplina').order_by('-data_solicitacao')
        
        disciplinas_info = []
        for disciplina in disciplinas_turma:
            aulas_disciplina = aulas_turma.filter(disciplina=disciplina)
            total_aulas_disciplina = aulas_disciplina.count()
            aulas_realizadas_disciplina = aulas_disciplina.filter(data_aula__lte=date.today()).count()
            
            frequencias_disciplina = frequencias.filter(aula__disciplina=disciplina)
            total_freq_disciplina = frequencias_disciplina.count()
            presentes_disciplina = frequencias_disciplina.filter(presenca='PRESENTE').count()
            faltas_disciplina = frequencias_disciplina.exclude(presenca='PRESENTE').count()
            percentual_freq_disciplina = (presentes_disciplina / total_freq_disciplina * 100) if total_freq_disciplina > 0 else 0
            
            notas_disciplina = notas.filter(avaliacao__disciplina=disciplina)
            # Montar itens de notas com id e status/etapa de revisão
            notas_validas = [n for n in notas_disciplina if n.nota is not None]
            nota_ids_list = [n.pk for n in notas_validas]
            revisoes_qs = PedidoRevisaoProva.objects.filter(nota_avaliacao_id__in=nota_ids_list)
            revisoes_map = {
                p.nota_avaliacao_id: {
                    'status': p.get_status_display(),
                    'etapa': p.etapa,
                    'id': p.id,
                    'fundamentacao': p.fundamentacao,
                    'data_solicitacao': p.data_solicitacao,
                    'data_atualizacao': p.data_atualizacao,
                    'despacho_envio_instrutor_texto': p.despacho_envio_instrutor_texto,
                    'despacho_envio_instrutor_por': getattr(p.despacho_envio_instrutor_por, 'username', None),
                    'despacho_envio_instrutor_data': p.despacho_envio_instrutor_data,
                    'parecer_instrutor_texto': p.parecer_instrutor_texto,
                    'parecer_final_texto': p.parecer_final_texto,
                }
                for p in revisoes_qs
            }
            notas_items = [
                {
                    'valor': n.nota,
                    'nota_id': n.pk,
                    'pedido_revisao_status': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['status']) or None,
                    'pedido_revisao_etapa': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['etapa']) or None,
                    'pedido_revisao_id': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['id']) or None,
                    'pedido_revisao_fundamentacao': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['fundamentacao']) or None,
                    'pedido_revisao_data_solicitacao': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['data_solicitacao']) or None,
                    'pedido_revisao_data_atualizacao': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['data_atualizacao']) or None,
                    'pedido_revisao_despacho_instrutor_texto': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['despacho_envio_instrutor_texto']) or None,
                    'pedido_revisao_despacho_instrutor_por': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['despacho_envio_instrutor_por']) or None,
                    'pedido_revisao_despacho_instrutor_data': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['despacho_envio_instrutor_data']) or None,
                    'pedido_revisao_parecer_instrutor_texto': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['parecer_instrutor_texto']) or None,
                    'pedido_revisao_parecer_final_texto': (revisoes_map.get(n.pk) and revisoes_map.get(n.pk)['parecer_final_texto']) or None,
                }
                for n in notas_validas
            ]
            notas_list = [n['valor'] for n in notas_items]
            media_disciplina = sum(notas_list) / len(notas_list) if notas_list else None
            
            avaliacoes_disciplina = AvaliacaoEnsino.objects.filter(
                turma=turma,
                disciplina=disciplina
            ).order_by('data_avaliacao')
            
            media_ponderada = None
            if notas_disciplina.exists():
                soma_ponderada = 0
                soma_pesos = 0
                for nota_obj in notas_disciplina:
                    if nota_obj.nota is not None and nota_obj.avaliacao.peso:
                        peso = float(nota_obj.avaliacao.peso)
                        soma_ponderada += float(nota_obj.nota) * peso
                        soma_pesos += peso
                if soma_pesos > 0:
                    media_ponderada = soma_ponderada / soma_pesos
            
            status_disciplina = None
            if media_ponderada is not None:
                if media_ponderada >= 7.0:
                    status_disciplina = 'APROVADO'
                elif media_ponderada >= 5.0:
                    status_disciplina = 'RECUPERACAO'
                else:
                    status_disciplina = 'REPROVADO'
            
            disciplinas_info.append({
                'disciplina': disciplina,
                'total_aulas': total_aulas_disciplina,
                'aulas_realizadas': aulas_realizadas_disciplina,
                'total_frequencias': total_freq_disciplina,
                'frequencias_presentes': presentes_disciplina,
                'frequencias_faltas': faltas_disciplina,
                'percentual_frequencia': round(percentual_freq_disciplina, 2),
                'notas': notas_list,
                'notas_items': notas_items,
                'media': round(media_ponderada, 2) if media_ponderada else None,
                'media_simples': round(media_disciplina, 2) if media_disciplina else None,
                'total_avaliacoes': avaliacoes_disciplina.count(),
                'avaliacoes': avaliacoes_disciplina,
                'status': status_disciplina,
            })
        
        context = {
            'aluno': aluno,
            'turma': turma,
            'total_aulas': total_aulas,
            'aulas_realizadas': aulas_realizadas,
            'aulas_previstas': aulas_previstas,
            'total_frequencias': total_frequencias,
            'frequencias_presentes': frequencias_presentes,
            'frequencias_faltas': frequencias_faltas,
            'percentual_frequencia': round(percentual_frequencia, 2),
            'total_notas': total_notas,
            'media_geral': round(media_geral, 2),
            'proximas_aulas': proximas_aulas,
            'avaliacoes_pendentes': avaliacoes_pendentes,
            'quadros_trabalho': quadros_trabalho,
            'disciplinas_info': disciplinas_info,
            'revisoes_aluno': revisoes_aluno,
        }
        
        return render(request, 'militares/ensino/dashboards/dashboard_aluno.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar dashboard: {str(e)}')
        # Se for usuário do ensino, redirecionar para login do ensino
        if request.session.get('ensino_tipo'):
            return redirect('militares:ensino_login')
        return redirect('militares:home')


@login_required(login_url='militares:ensino_login')
def dashboard_instrutor(request):
    """Dashboard inicial para instrutores"""
    try:
        # Verificar se é login do módulo de ensino através da sessão
        ensino_tipo = request.session.get('ensino_tipo')
        ensino_id = request.session.get('ensino_id')
        
        militar = None
        
        if ensino_tipo in ['instrutor', 'monitor'] and ensino_id:
            # Buscar instrutor ou monitor conforme tipo armazenado na sessão
            if ensino_tipo == 'instrutor':
                instrutor = InstrutorEnsino.objects.filter(
                    pk=ensino_id,
                    ativo=True
                ).first()
                if instrutor and instrutor.tipo_instrutor == 'BOMBEIRO' and instrutor.militar:
                    militar = instrutor.militar
            else:
                # Login de monitor: não tentar carregar como InstrutorEnsino usando o ID do monitor
                monitor = MonitorEnsino.objects.filter(
                    pk=ensino_id,
                    ativo=True
                ).first()
                # Se for monitor bombeiro, obter o militar vinculado para estatísticas compatíveis
                if monitor and monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar:
                    militar = monitor.militar
        else:
            # Tentar buscar através do militar (para compatibilidade)
            militar = request.user.militar if hasattr(request.user, 'militar') else None
            if not militar:
                messages.warning(request, 'Você não possui perfil de militar cadastrado.')
                return redirect('militares:ensino_login')
            
            # Buscar instrutor ativo
            instrutor = InstrutorEnsino.objects.filter(
                militar=militar,
                ativo=True
            ).first()
        
        # Se não é instrutor, mas é monitor autenticado, permitir acesso ao dashboard com escopo de monitor
        if not instrutor and request.session.get('ensino_tipo') == 'monitor':
            # Construir visão básica para monitores
            turmas = TurmaEnsino.objects.none()
            aulas_proximas = AulaEnsino.objects.none()
            aulas_realizadas = AulaEnsino.objects.none()
            total_aulas = 0
            aulas_este_mes = 0
            disciplinas = []

            # Obter turmas onde o monitor atua
            monitor_id = request.session.get('ensino_id')
            monitor = MonitorEnsino.objects.filter(pk=monitor_id, ativo=True).first()
            if monitor:
                if monitor.tipo_monitor == 'BOMBEIRO' and monitor.militar:
                    turmas = TurmaEnsino.objects.filter(
                        monitores_militares=monitor.militar
                    ).distinct().select_related('curso')[:10]
                else:
                    turmas = TurmaEnsino.objects.filter(
                        monitores_externos=monitor
                    ).distinct().select_related('curso')[:10]

            context = {
                'instrutor': None,
                'turmas': turmas,
                'aulas_proximas': aulas_proximas,
                'aulas_realizadas': aulas_realizadas,
                'total_aulas': total_aulas,
                'aulas_este_mes': aulas_este_mes,
                'disciplinas': disciplinas,
            }
            return render(request, 'militares/ensino/dashboards/dashboard_instrutor.html', context)

        if not instrutor:
            messages.info(request, 'Você não está cadastrado como instrutor ativo.')
            return redirect('militares:ensino_login')
        
        # Turmas onde o instrutor atua (através das disciplinas)
        if militar:
            turmas = TurmaEnsino.objects.filter(
                disciplinas__instrutor_responsavel_militar=militar
            ).distinct().select_related('curso')[:10]
            
            # Aulas do instrutor (próximas 30 dias)
            aulas_proximas = AulaEnsino.objects.filter(
                instrutor=militar,
                data_aula__gte=date.today(),
                data_aula__lte=date.today() + timedelta(days=30)
            ).select_related('turma', 'disciplina').order_by('data_aula', 'hora_inicio')[:10]
            
            # Aulas realizadas (últimos 30 dias)
            aulas_realizadas = AulaEnsino.objects.filter(
                instrutor=militar,
                data_aula__gte=date.today() - timedelta(days=30),
                data_aula__lt=date.today()
            ).select_related('turma', 'disciplina').order_by('-data_aula', '-hora_inicio')[:10]
            
            # Estatísticas
            total_aulas = AulaEnsino.objects.filter(instrutor=militar).count()
            aulas_este_mes = AulaEnsino.objects.filter(
                instrutor=militar,
                data_aula__year=date.today().year,
                data_aula__month=date.today().month
            ).count()
            
            # Disciplinas que o instrutor leciona
            from .models import DisciplinaEnsino
            disciplinas = DisciplinaEnsino.objects.filter(
                instrutor_responsavel_militar=militar
            ).distinct()[:10]

            # Estatísticas por (turma, disciplina) para auxiliar visualização no app
            stats_disc_turma = {}
            for turma in turmas:
                for disciplina in turma.disciplinas.all():
                    if disciplina.instrutor_responsavel_militar == militar:
                        chave = f"{turma.pk}-{disciplina.pk}"
                        total_aulas_disc = AulaEnsino.objects.filter(
                            turma=turma,
                            disciplina=disciplina,
                            instrutor=militar
                        ).count()
                        proximas_aulas_disc = AulaEnsino.objects.filter(
                            turma=turma,
                            disciplina=disciplina,
                            instrutor=militar,
                            data_aula__gte=date.today(),
                            data_aula__lte=date.today() + timedelta(days=30)
                        ).count()
                        total_avaliacoes_disc = AvaliacaoEnsino.objects.filter(
                            turma=turma,
                            disciplina=disciplina
                        ).count()
                        total_qts_turma = QuadroTrabalhoSemanal.objects.filter(
                            turma=turma
                        ).count()
                        proximos_qts_turma = QuadroTrabalhoSemanal.objects.filter(
                            turma=turma,
                            data_inicio_semana__gte=date.today(),
                            data_inicio_semana__lte=date.today() + timedelta(days=30)
                        ).count()
                        stats_disc_turma[chave] = {
                            'aulas_total': total_aulas_disc,
                            'aulas_proximas': proximas_aulas_disc,
                            'avaliacoes_total': total_avaliacoes_disc,
                            'qts_total': total_qts_turma,
                            'qts_proximos': proximos_qts_turma,
                        }
            # Quadros de Trabalho Semanal das turmas onde o instrutor leciona
            quadros_trabalho_instrutor = QuadroTrabalhoSemanal.objects.filter(
                turma__in=turmas
            ).order_by('-data_inicio_semana', '-numero_quadro')[:10]
        else:
            # Para instrutores sem militar, retornar dados vazios
            turmas = TurmaEnsino.objects.none()
            aulas_proximas = AulaEnsino.objects.none()
            aulas_realizadas = AulaEnsino.objects.none()
            total_aulas = 0
            aulas_este_mes = 0
            disciplinas = []
            stats_disc_turma = {}
            quadros_trabalho_instrutor = []
        
        # Pedidos de revisão atribuídos ao instrutor ou sem atribuição mas da sua disciplina
        from django.utils import timezone
        pedidos_qs = PedidoRevisaoProva.objects.filter(
            instrutor_responsavel=instrutor,
            status='EM_ANALISE'
        )
        proximas_24h = pedidos_qs.filter(
            prazo_limite_instrutor__isnull=False,
            prazo_limite_instrutor__lte=timezone.now() + timedelta(hours=24)
        ).count()
        pedidos_instrutor = pedidos_qs.select_related('nota_avaliacao__avaliacao__disciplina', 'aluno')[:20]
        context = {
            'instrutor': instrutor,
            'turmas': turmas,
            'aulas_proximas': aulas_proximas,
            'aulas_realizadas': aulas_realizadas,
            'total_aulas': total_aulas,
            'aulas_este_mes': aulas_este_mes,
            'disciplinas': disciplinas,
            'pedidos_revisao_instrutor': pedidos_instrutor,
            'stats_disc_turma': stats_disc_turma,
            'quadros_trabalho_instrutor': quadros_trabalho_instrutor,
            'alertas_pedidos_vencendo_24h': proximas_24h,
        }
        
        return render(request, 'militares/ensino/dashboards/dashboard_instrutor.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar dashboard: {str(e)}')
        # Se for usuário do ensino, redirecionar para login do ensino
        if request.session.get('ensino_tipo'):
            return redirect('militares:ensino_login')
        return redirect('militares:home')


@login_required(login_url='militares:ensino_login')
def dashboard_supervisor(request):
    """Dashboard inicial para supervisores"""
    try:
        militar = request.user.militar if hasattr(request.user, 'militar') else None
        if not militar:
            messages.warning(request, 'Você não possui perfil de militar cadastrado.')
            return redirect('militares:home')
        
        # Turmas onde o militar é supervisor
        turmas_supervisor_curso = TurmaEnsino.objects.filter(
            supervisor_curso=militar
        ).select_related('curso')
        
        turmas_supervisor_turma = TurmaEnsino.objects.filter(
            supervisor_turma=militar
        ).select_related('curso')
        
        turmas = (turmas_supervisor_curso | turmas_supervisor_turma).distinct()
        
        # Mesmo sem turmas atribuídas, manter o dashboard para permitir gestão de revisões
        # (métricas relacionadas a turmas podem aparecer vazias)
        
        # Estatísticas gerais
        total_turmas = turmas.count()
        turmas_ativas = turmas.filter(ativa=True).count()
        
        # Alunos nas turmas
        total_alunos = AlunoEnsino.objects.filter(
            turma__in=turmas,
            situacao='ATIVO'
        ).count()
        
        # Aulas nas turmas
        total_aulas = AulaEnsino.objects.filter(
            turma__in=turmas
        ).count()
        
        aulas_este_mes = AulaEnsino.objects.filter(
            turma__in=turmas,
            data_aula__year=date.today().year,
            data_aula__month=date.today().month
        ).count()
        
        # Frequência média das turmas
        frequencias = FrequenciaAula.objects.filter(
            aula__turma__in=turmas
        )
        total_frequencias = frequencias.count()
        frequencias_presentes = frequencias.filter(presenca='PRESENTE').count()
        percentual_frequencia = (frequencias_presentes / total_frequencias * 100) if total_frequencias > 0 else 0
        
        # Próximas atividades (próximos 7 dias)
        proximas_aulas = AulaEnsino.objects.filter(
            turma__in=turmas,
            data_aula__gte=date.today(),
            data_aula__lte=date.today() + timedelta(days=7)
        ).select_related('turma', 'disciplina', 'instrutor').order_by('data_aula', 'hora_inicio')[:10]
        
        # Quadros de trabalho semanal
        quadros_trabalho = QuadroTrabalhoSemanal.objects.filter(
            turma__in=turmas
        ).order_by('-data_inicio_semana', '-numero_quadro')[:10]
        
        from .models import PedidoRevisaoProva
        # Filtros por curso e disciplina (GET)
        curso_id = request.GET.get('curso_id')
        disciplina_id = request.GET.get('disciplina_id')
        # Opções de curso e disciplina baseadas nas turmas do supervisor
        if turmas.exists():
            cursos_opcoes = list(
                turmas.values('curso_id', 'curso__nome').distinct().order_by('curso__nome')
            )
            disciplinas_opcoes = list(
                AvaliacaoEnsino.objects.filter(turma__in=turmas)
                .values('disciplina_id', 'disciplina__nome').distinct().order_by('disciplina__nome')
            )
            base_qs = PedidoRevisaoProva.objects.filter(
                nota_avaliacao__avaliacao__turma__in=turmas
            )
        else:
            # Sem turmas atribuídas, listar pedidos do ensino inteiros
            cursos_opcoes = list(
                AvaliacaoEnsino.objects.values('turma__curso_id', 'turma__curso__nome').distinct().order_by('turma__curso__nome')
            )
            # Normalizar chaves para uso no template
            for c in cursos_opcoes:
                c['curso_id'] = c.pop('turma__curso_id')
                c['curso__nome'] = c.pop('turma__curso__nome')
            disciplinas_opcoes = list(
                AvaliacaoEnsino.objects.values('disciplina_id', 'disciplina__nome').distinct().order_by('disciplina__nome')
            )
            base_qs = PedidoRevisaoProva.objects.all()
        if curso_id:
            base_qs = base_qs.filter(nota_avaliacao__avaliacao__turma__curso_id=curso_id)
        if disciplina_id:
            base_qs = base_qs.filter(nota_avaliacao__avaliacao__disciplina_id=disciplina_id)
        pedidos_revisao_para_despacho = base_qs.filter(etapa='ALUNO_SOLICITOU')\
            .select_related('nota_avaliacao__avaliacao__disciplina', 'aluno')[:20]
        from django.utils import timezone
        revisoes_contagem = {
            'ALUNO_SOLICITOU': base_qs.filter(etapa='ALUNO_SOLICITOU').count(),
            'DESPACHADA_INSTRUTOR': base_qs.filter(etapa='DESPACHADA_INSTRUTOR').count(),
            'PARECER_INSTRUTOR': base_qs.filter(etapa='PARECER_INSTRUTOR').count(),
            'RECURSO_DIRETORIA': base_qs.filter(etapa='RECURSO_DIRETORIA').count(),
            'COMISSAO_NOMEADA': base_qs.filter(etapa='COMISSAO_NOMEADA').count(),
            'PARECER_FINAL': base_qs.filter(etapa='PARECER_FINAL').count(),
        }
        alertas_revisoes = {
            'instrutor_vencendo_24h': base_qs.filter(
                etapa='DESPACHADA_INSTRUTOR',
                prazo_limite_instrutor__isnull=False,
                prazo_limite_instrutor__lte=timezone.now() + timedelta(hours=24)
            ).count(),
            'comissao_vencendo_24h': base_qs.filter(
                etapa='COMISSAO_NOMEADA',
                prazo_limite_comissao__isnull=False,
                prazo_limite_comissao__lte=timezone.now() + timedelta(hours=24)
            ).count(),
        }
        context = {
            'turmas': turmas[:10],
            'total_turmas': total_turmas,
            'turmas_ativas': turmas_ativas,
            'total_alunos': total_alunos,
            'total_aulas': total_aulas,
            'aulas_este_mes': aulas_este_mes,
            'percentual_frequencia': round(percentual_frequencia, 2),
            'proximas_aulas': proximas_aulas,
            'quadros_trabalho': quadros_trabalho,
            'pedidos_revisao_para_despacho': pedidos_revisao_para_despacho,
            'revisoes_contagem': revisoes_contagem,
            'revisoes_alertas': alertas_revisoes,
            'cursos_opcoes': cursos_opcoes,
            'disciplinas_opcoes': disciplinas_opcoes,
            'curso_id': curso_id,
            'disciplina_id': disciplina_id,
        }
        
        return render(request, 'militares/ensino/dashboards/dashboard_supervisor.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar dashboard: {str(e)}')
        # Se for usuário do ensino, redirecionar para login do ensino
        if request.session.get('ensino_tipo'):
            return redirect('militares:ensino_login')
        return redirect('militares:home')


@login_required(login_url='militares:ensino_login')
def dashboard_coordenador(request):
    """Dashboard inicial para coordenadores"""
    try:
        militar = request.user.militar if hasattr(request.user, 'militar') else None
        if not militar:
            messages.warning(request, 'Você não possui perfil de militar cadastrado.')
            return redirect('militares:home')
        
        # Turmas onde o militar é coordenador
        turmas_coordenador_curso = TurmaEnsino.objects.filter(
            coordenador_curso=militar
        ).select_related('curso')
        
        turmas_coordenador_turma = TurmaEnsino.objects.filter(
            coordenador_turma=militar
        ).select_related('curso')
        
        turmas = (turmas_coordenador_curso | turmas_coordenador_turma).distinct()
        
        # Mesmo sem turmas atribuídas, manter o dashboard para permitir gestão de revisões
        # (métricas relacionadas a turmas podem aparecer vazias)
        
        # Estatísticas gerais
        total_turmas = turmas.count()
        turmas_ativas = turmas.filter(ativa=True).count()
        
        # Alunos nas turmas
        total_alunos = AlunoEnsino.objects.filter(
            turma__in=turmas,
            situacao='ATIVO'
        ).count()
        
        alunos_concluidos = AlunoEnsino.objects.filter(
            turma__in=turmas,
            situacao='CONCLUIDO'
        ).count()
        
        # Aulas nas turmas
        total_aulas = AulaEnsino.objects.filter(
            turma__in=turmas
        ).count()
        
        aulas_este_mes = AulaEnsino.objects.filter(
            turma__in=turmas,
            data_aula__year=date.today().year,
            data_aula__month=date.today().month
        ).count()
        
        # Frequência média das turmas
        frequencias = FrequenciaAula.objects.filter(
            aula__turma__in=turmas
        )
        total_frequencias = frequencias.count()
        frequencias_presentes = frequencias.filter(presenca='PRESENTE').count()
        percentual_frequencia = (frequencias_presentes / total_frequencias * 100) if total_frequencias > 0 else 0
        
        # Média geral de notas
        notas = NotaAvaliacao.objects.filter(
            avaliacao__turma__in=turmas
        )
        media_geral = notas.aggregate(media=Avg('nota'))['media'] or 0
        
        # Próximas atividades (próximos 7 dias)
        proximas_aulas = AulaEnsino.objects.filter(
            turma__in=turmas,
            data_aula__gte=date.today(),
            data_aula__lte=date.today() + timedelta(days=7)
        ).select_related('turma', 'disciplina', 'instrutor').order_by('data_aula', 'hora_inicio')[:10]
        
        # Avaliações pendentes
        avaliacoes_pendentes = AvaliacaoEnsino.objects.filter(
            turma__in=turmas,
            data_avaliacao__gte=date.today()
        ).select_related('turma', 'disciplina').order_by('data_avaliacao')[:10]
        
        # Quadros de trabalho semanal
        quadros_trabalho = QuadroTrabalhoSemanal.objects.filter(
            turma__in=turmas
        ).order_by('-data_inicio_semana', '-numero_quadro')[:10]
        
        from .models import PedidoRevisaoProva
        # Filtros por curso e disciplina (GET)
        curso_id = request.GET.get('curso_id')
        disciplina_id = request.GET.get('disciplina_id')
        if turmas.exists():
            cursos_opcoes = list(
                turmas.values('curso_id', 'curso__nome').distinct().order_by('curso__nome')
            )
            disciplinas_opcoes = list(
                AvaliacaoEnsino.objects.filter(turma__in=turmas)
                .values('disciplina_id', 'disciplina__nome').distinct().order_by('disciplina__nome')
            )
            base_qs = PedidoRevisaoProva.objects.filter(
                nota_avaliacao__avaliacao__turma__in=turmas
            )
        else:
            cursos_opcoes = list(
                AvaliacaoEnsino.objects.values('turma__curso_id', 'turma__curso__nome').distinct().order_by('turma__curso__nome')
            )
            for c in cursos_opcoes:
                c['curso_id'] = c.pop('turma__curso_id')
                c['curso__nome'] = c.pop('turma__curso__nome')
            disciplinas_opcoes = list(
                AvaliacaoEnsino.objects.values('disciplina_id', 'disciplina__nome').distinct().order_by('disciplina__nome')
            )
            base_qs = PedidoRevisaoProva.objects.all()
        if curso_id:
            base_qs = base_qs.filter(nota_avaliacao__avaliacao__turma__curso_id=curso_id)
        if disciplina_id:
            base_qs = base_qs.filter(nota_avaliacao__avaliacao__disciplina_id=disciplina_id)
        pedidos_recurso_diretoria = base_qs.filter(etapa='RECURSO_DIRETORIA')\
            .select_related('nota_avaliacao__avaliacao__disciplina', 'aluno')[:20]
        from django.utils import timezone
        revisoes_contagem = {
            'ALUNO_SOLICITOU': base_qs.filter(etapa='ALUNO_SOLICITOU').count(),
            'DESPACHADA_INSTRUTOR': base_qs.filter(etapa='DESPACHADA_INSTRUTOR').count(),
            'PARECER_INSTRUTOR': base_qs.filter(etapa='PARECER_INSTRUTOR').count(),
            'RECURSO_DIRETORIA': base_qs.filter(etapa='RECURSO_DIRETORIA').count(),
            'COMISSAO_NOMEADA': base_qs.filter(etapa='COMISSAO_NOMEADA').count(),
            'PARECER_FINAL': base_qs.filter(etapa='PARECER_FINAL').count(),
        }
        alertas_revisoes = {
            'instrutor_vencendo_24h': base_qs.filter(
                etapa='DESPACHADA_INSTRUTOR',
                prazo_limite_instrutor__isnull=False,
                prazo_limite_instrutor__lte=timezone.now() + timedelta(hours=24)
            ).count(),
            'comissao_vencendo_24h': base_qs.filter(
                etapa='COMISSAO_NOMEADA',
                prazo_limite_comissao__isnull=False,
                prazo_limite_comissao__lte=timezone.now() + timedelta(hours=24)
            ).count(),
        }
        context = {
            'turmas': turmas[:10],
            'total_turmas': total_turmas,
            'turmas_ativas': turmas_ativas,
            'total_alunos': total_alunos,
            'alunos_concluidos': alunos_concluidos,
            'total_aulas': total_aulas,
            'aulas_este_mes': aulas_este_mes,
            'percentual_frequencia': round(percentual_frequencia, 2),
            'media_geral': round(media_geral, 2),
            'proximas_aulas': proximas_aulas,
            'avaliacoes_pendentes': avaliacoes_pendentes,
            'quadros_trabalho': quadros_trabalho,
            'pedidos_recurso_diretoria': pedidos_recurso_diretoria,
            'revisoes_contagem': revisoes_contagem,
            'revisoes_alertas': alertas_revisoes,
            'cursos_opcoes': cursos_opcoes,
            'disciplinas_opcoes': disciplinas_opcoes,
            'curso_id': curso_id,
            'disciplina_id': disciplina_id,
        }
        
        return render(request, 'militares/ensino/dashboards/dashboard_coordenador.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar dashboard: {str(e)}')
        # Se for usuário do ensino, redirecionar para login do ensino
        if request.session.get('ensino_tipo'):
            return redirect('militares:ensino_login')
        return redirect('militares:home')

            
