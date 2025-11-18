"""
Módulo para filtros hierárquicos baseados no tipo de acesso das funções militares.

Este módulo centraliza a lógica de filtros hierárquicos para garantir consistência
em todas as views que exibem dados de militares.
"""

from django.db.models import Q
from .models import SubUnidade


def aplicar_filtro_hierarquico_militares(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de Militar para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset.filter(classificacao='ATIVO')
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Usar apenas os dados da função militar, não do usuário
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todos os militares
        return queryset.filter(classificacao='ATIVO')
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas o próprio militar
        return queryset.filter(
            classificacao='ATIVO',
            user=funcao_usuario.usuario
        )
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                classificacao='ATIVO',
                lotacoes__orgao=funcao_usuario.orgao,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                classificacao='ATIVO',
                lotacoes__grande_comando=funcao_usuario.grande_comando,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            # Buscar TODAS as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            return queryset.filter(
                Q(lotacoes__unidade=funcao_usuario.unidade) |
                Q(lotacoes__sub_unidade__in=subunidades),
                classificacao='ATIVO',
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas pela subunidade específica
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                classificacao='ATIVO',
                lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    # Se não reconhecer o tipo de acesso, retornar queryset vazio
    return queryset.none()


def aplicar_filtro_hierarquico_notas(queryset, funcao_usuario):
    """
    Aplica filtro hierárquico para notas baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de Publicacao (tipo='NOTA') para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    if funcao_usuario.nivel_acesso == 'TOTAL':
        # Acesso total - mostrar todas as notas
        return queryset.filter(tipo='NOTA', ativo=True)
        
    elif funcao_usuario.nivel_acesso == 'NENHUM':
        # Sem acesso - mostrar apenas notas do próprio usuário
        return queryset.filter(
            tipo='NOTA',
            ativo=True,
            criado_por=funcao_usuario.usuario
        )
        
    elif funcao_usuario.nivel_acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                tipo='NOTA',
                ativo=True,
                criado_por__militar__lotacoes__orgao=funcao_usuario.orgao,
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                tipo='NOTA',
                ativo=True,
                criado_por__militar__lotacoes__grande_comando=funcao_usuario.grande_comando,
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODA sua descendência
        if funcao_usuario.unidade:
            return queryset.filter(
                tipo='NOTA',
                ativo=True,
                criado_por__militar__lotacoes__unidade=funcao_usuario.unidade,
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas por subunidade
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                tipo='NOTA',
                ativo=True,
                criado_por__militar__lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_documentos(queryset, funcao_usuario):
    """
    Aplica filtro hierárquico para documentos baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de Documento para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    if funcao_usuario.nivel_acesso == 'TOTAL':
        # Acesso total - mostrar todos os documentos
        return queryset
        
    elif funcao_usuario.nivel_acesso == 'NENHUM':
        # Sem acesso - mostrar apenas documentos do próprio militar
        return queryset.filter(militar__user=funcao_usuario.usuario)
        
    elif funcao_usuario.nivel_acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                militar__lotacoes__orgao=funcao_usuario.orgao,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                militar__lotacoes__grande_comando=funcao_usuario.grande_comando,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            # Buscar TODAS as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            return queryset.filter(
                Q(militar__lotacoes__unidade=funcao_usuario.unidade) |
                Q(militar__lotacoes__sub_unidade__in=subunidades),
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas pela subunidade específica
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                militar__lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    # Se não reconhecer o tipo de acesso, retornar queryset vazio
    return queryset.none()


def aplicar_filtro_hierarquico_fichas(queryset, funcao_usuario):
    """
    Aplica filtro hierárquico para fichas de conceito baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de FichaConceito para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    if funcao_usuario.nivel_acesso == 'TOTAL':
        # Acesso total - mostrar todas as fichas
        return queryset
        
    elif funcao_usuario.nivel_acesso == 'NENHUM':
        # Sem acesso - mostrar apenas fichas do próprio militar
        return queryset.filter(militar__user=funcao_usuario.usuario)
        
    elif funcao_usuario.nivel_acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                militar__lotacoes__orgao=funcao_usuario.orgao,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                militar__lotacoes__grande_comando=funcao_usuario.grande_comando,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            # Buscar TODAS as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            return queryset.filter(
                Q(militar__lotacoes__unidade=funcao_usuario.unidade) |
                Q(militar__lotacoes__sub_unidade__in=subunidades),
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_usuario.nivel_acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas pela subunidade específica
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                militar__lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    # Se não reconhecer o tipo de acesso, retornar queryset vazio
    return queryset.none()


def obter_estatisticas_hierarquicas(funcao_usuario):
    """
    Obtém estatísticas filtradas baseadas no tipo de acesso da função militar.
    
    Args:
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        
    Returns:
        dict: Dicionário com estatísticas filtradas
    """
    from .models import Militar, Documento, FichaConceitoOficiais, FichaConceitoPracas
    from django.db.models import Count
    
    # Aplicar filtros hierárquicos
    militares_filtrados = aplicar_filtro_hierarquico_militares(Militar.objects, funcao_usuario)
    documentos_filtrados = aplicar_filtro_hierarquico_documentos(Documento.objects, funcao_usuario)
    fichas_oficiais_filtradas = aplicar_filtro_hierarquico_fichas(FichaConceitoOficiais.objects, funcao_usuario)
    fichas_pracas_filtradas = aplicar_filtro_hierarquico_fichas(FichaConceitoPracas.objects, funcao_usuario)
    
    # Calcular estatísticas
    total_militares = militares_filtrados.count()
    militares_ativos = militares_filtrados.filter(classificacao='ATIVO').count()
    militares_inativos = total_militares - militares_ativos
    
    # Contar militares que possuem ficha de conceito
    militares_com_ficha = militares_filtrados.filter(
        Q(fichaconceitooficiais__isnull=False) | Q(fichaconceitopracas__isnull=False)
    ).distinct().count()
    
    # Contar militares ativos sem ficha de conceito
    militares_sem_ficha = militares_ativos - militares_com_ficha
    
    # Estatísticas de documentos
    documentos_pendentes = documentos_filtrados.filter(status='PENDENTE').count()
    total_documentos = documentos_filtrados.count()
    
    # Estatísticas de fichas
    total_fichas = fichas_oficiais_filtradas.count() + fichas_pracas_filtradas.count()
    # Nota: Os modelos FichaConceito não têm campo 'status', apenas 'data_registro'
    fichas_aprovadas = 0  # Campo status não existe no modelo
    fichas_pendentes = total_fichas  # Considerar todas como pendentes por enquanto
    
    # Estatísticas por quadro (apenas militares ativos)
    estatisticas_quadro = militares_filtrados.filter(classificacao='ATIVO').values('quadro').annotate(
        total=Count('id')
    ).order_by('quadro')
    
    # Estatísticas por posto/graduação (apenas militares ativos)
    estatisticas_posto = militares_filtrados.filter(classificacao='ATIVO').values('posto_graduacao').annotate(
        total=Count('id')
    ).order_by('posto_graduacao')
    
    return {
        'total_militares': total_militares,
        'militares_ativos': militares_ativos,
        'militares_inativos': militares_inativos,
        'militares_com_ficha': militares_com_ficha,
        'militares_sem_ficha': militares_sem_ficha,
        'documentos_pendentes': documentos_pendentes,
        'total_documentos': total_documentos,
        'total_fichas': total_fichas,
        'fichas_aprovadas': fichas_aprovadas,
        'fichas_pendentes': fichas_pendentes,
        'estatisticas_quadro': estatisticas_quadro,
        'estatisticas_posto': estatisticas_posto,
    }
