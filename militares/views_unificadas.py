from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import QuadroAcesso
from .permissoes_sistema import requer_perm_quadros_criar

@login_required
def quadro_acesso_unificado_list(request):
    """Lista unificada de quadros de acesso (oficiais e praças)"""
    tipo_filtro = request.GET.get('tipo', 'todos')
    status_filtro = request.GET.get('status', 'todos')
    quadros = QuadroAcesso.objects.all()
    if tipo_filtro == 'oficiais':
        quadros = quadros.filter(
            Q(is_manual=False) | Q(is_manual=True, criterio_ordenacao_manual='MANUAL')
        ).exclude(
            itemquadroacesso__militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
        )
    elif tipo_filtro == 'pracas':
        quadros = quadros.filter(tipo__in=['ANTIGUIDADE', 'MERECIMENTO', 'MANUAL'])
    if status_filtro == 'elaborado':
        quadros = quadros.filter(status='ELABORADO')
    elif status_filtro == 'nao_elaborado':
        quadros = quadros.filter(status='NAO_ELABORADO')
    quadros = quadros.order_by('-data_promocao', '-data_criacao')
    quadros_processados = []
    for quadro in quadros:
        if quadro.is_manual and getattr(quadro, 'criterio_ordenacao_manual', None) in ['ANTIGUIDADE', 'MERECIMENTO']:
            quadro.tipo_quadro = 'pracas'
            itens_relevantes = quadro.itemquadroacesso_set.filter(
                militar__posto_graduacao__in=['SD', 'CAB', '3S', '2S', '1S', 'ST']
            )
        else:
            quadro.tipo_quadro = 'oficiais'
            itens_relevantes = quadro.itemquadroacesso_set.filter(
                militar__posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS', 'AA']
            )
        quadro.total_militares = itens_relevantes.count()
        quadro.tem_militares = itens_relevantes.exists()
        quadros_processados.append(quadro)
    estatisticas = {
        'total': len(quadros_processados),
        'oficiais': sum(1 for q in quadros_processados if q.tipo_quadro == 'oficiais'),
        'pracas': sum(1 for q in quadros_processados if q.tipo_quadro == 'pracas'),
        'elaborados': sum(1 for q in quadros_processados if q.status == 'ELABORADO'),
        'nao_elaborados': sum(1 for q in quadros_processados if q.status == 'NAO_ELABORADO'),
    }
    context = {
        'quadros': quadros_processados,
        'estatisticas': estatisticas,
        'filtros': {
            'tipo': tipo_filtro,
            'status': status_filtro,
        }
    }
    return render(request, 'militares/quadro_acesso_unificado_list.html', context)


@login_required
@requer_perm_quadros_criar
def gerar_quadro_acesso_unificado(request):
    """Gera quadro de acesso unificado (oficiais ou praças)"""
    try:
        from .models import InstrutorEnsino, MonitorEnsino
        militar = getattr(request.user, 'militar', None)
        if militar and (
            InstrutorEnsino.objects.filter(militar=militar, ativo=True).exists() or
            MonitorEnsino.objects.filter(militar=militar, ativo=True).exists()
        ):
            messages.error(request, 'Instrutores e monitores só podem visualizar Quadros de Acesso.')
            return redirect('militares:quadro_acesso_unificado_list')
    except Exception:
        pass
    if request.method == 'POST':
        tipo_quadro = request.POST.get('tipo_quadro')
        data_promocao = request.POST.get('data_promocao')
        if not tipo_quadro or not data_promocao:
            messages.error(request, 'Tipo de quadro e data de promoção são obrigatórios.')
            return redirect('militares:quadro_acesso_unificado_list')
        try:
            from datetime import datetime
            data_promocao = datetime.strptime(data_promocao, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Data de promoção inválida.')
            return redirect('militares:quadro_acesso_unificado_list')
        # Permitir aditamentos - o sistema de numeração automática gerencia os números únicos
        # Removida a validação que bloqueava quadros para a mesma data/tipo/categoria
        if tipo_quadro == 'pracas':
            novo_quadro = QuadroAcesso.objects.create(
                tipo='ANTIGUIDADE',
                data_promocao=data_promocao,
                status='EM_ELABORACAO'
            )
            messages.success(request, f'Quadro de acesso de praças criado para {data_promocao.strftime("%d/%m/%Y")}!')
        else:
            novo_quadro = QuadroAcesso.objects.create(
                tipo='ANTIGUIDADE',
                data_promocao=data_promocao,
                status='EM_ELABORACAO'
            )
            messages.success(request, f'Quadro de acesso de oficiais criado para {data_promocao.strftime("%d/%m/%Y")}!')
        return redirect('militares:quadro_acesso_unificado_list')
    hoje = date.today()
    proxima_data = date(hoje.year, 7, 18) if hoje < date(hoje.year, 7, 18) else date(hoje.year, 12, 25)
    context = {
        'proxima_data': proxima_data,
    }
    return render(request, 'militares/gerar_quadro_acesso_unificado.html', context) 
