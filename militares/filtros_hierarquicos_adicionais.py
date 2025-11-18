"""
Filtros hierárquicos adicionais para outras entidades do sistema.

Este módulo contém funções de filtro hierárquico para entidades que ainda não
tinham filtros implementados, como quadros de acesso, comissões, medalhas, etc.
"""

from django.db.models import Q
from .models import SubUnidade


def aplicar_filtro_hierarquico_quadros_acesso(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para quadros de acesso baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de QuadroAcesso para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Usar apenas os dados da função militar, não do usuário
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todos os quadros
        return queryset
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas quadros criados pelo próprio usuário
        return queryset.filter(criado_por=funcao_usuario.usuario)
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                Q(criado_por__militar__lotacoes__orgao=funcao_usuario.orgao,
                  criado_por__militar__lotacoes__status='ATUAL',
                  criado_por__militar__lotacoes__ativo=True) |
                Q(status__in=['APROVADO', 'HOMOLOGADO'])
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                Q(criado_por__militar__lotacoes__grande_comando=funcao_usuario.grande_comando,
                  criado_por__militar__lotacoes__status='ATUAL',
                  criado_por__militar__lotacoes__ativo=True) |
                Q(status__in=['APROVADO', 'HOMOLOGADO'])
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            return queryset.filter(
                Q(criado_por__militar__lotacoes__unidade=funcao_usuario.unidade) |
                Q(criado_por__militar__lotacoes__sub_unidade__in=subunidades),
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas pela subunidade específica
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                criado_por__militar__lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_quadros_fixacao(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para quadros de fixação de vagas baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de QuadroFixacaoVagas para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Usar apenas os dados da função militar, não do usuário
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todos os quadros
        return queryset
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas quadros criados pelo próprio usuário
        return queryset.filter(criado_por=funcao_usuario.usuario)
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                Q(criado_por__militar__lotacoes__orgao=funcao_usuario.orgao,
                  criado_por__militar__lotacoes__status='ATUAL',
                  criado_por__militar__lotacoes__ativo=True) |
                Q(status__in=['APROVADO', 'HOMOLOGADO'])
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                Q(criado_por__militar__lotacoes__grande_comando=funcao_usuario.grande_comando,
                  criado_por__militar__lotacoes__status='ATUAL',
                  criado_por__militar__lotacoes__ativo=True) |
                Q(status__in=['APROVADO', 'HOMOLOGADO'])
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            return queryset.filter(
                Q(criado_por__militar__lotacoes__unidade=funcao_usuario.unidade) |
                Q(criado_por__militar__lotacoes__sub_unidade__in=subunidades),
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas pela subunidade específica
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                criado_por__militar__lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_comissoes(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para comissões de promoção baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de ComissaoPromocao para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Usar apenas os dados da função militar, não do usuário
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todas as comissões
        return queryset
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas comissões onde o usuário é membro
        return queryset.filter(
            membros__usuario=funcao_usuario.usuario,
            membros__ativo=True
        ).distinct()
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                Q(criado_por__militar__lotacoes__orgao=funcao_usuario.orgao,
                  criado_por__militar__lotacoes__status='ATUAL',
                  criado_por__militar__lotacoes__ativo=True) |
                Q(membros__usuario=funcao_usuario.usuario, membros__ativo=True)
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                Q(criado_por__militar__lotacoes__grande_comando=funcao_usuario.grande_comando,
                  criado_por__militar__lotacoes__status='ATUAL',
                  criado_por__militar__lotacoes__ativo=True) |
                Q(membros__usuario=funcao_usuario.usuario, membros__ativo=True)
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            return queryset.filter(
                Q(criado_por__militar__lotacoes__unidade=funcao_usuario.unidade) |
                Q(criado_por__militar__lotacoes__sub_unidade__in=subunidades),
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas pela subunidade específica
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                criado_por__militar__lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                criado_por__militar__lotacoes__status='ATUAL',
                criado_por__militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_medalhas(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para medalhas e condecorações baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de MedalhaCondecoracao para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Usar apenas os dados da função militar, não do usuário
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todas as medalhas
        return queryset
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas medalhas do próprio militar
        return queryset.filter(
            militar__user=funcao_usuario.usuario
        )
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - filtrar por órgão e TODA sua descendência
        if funcao_usuario.orgao:
            return queryset.filter(
                militar__lotacoes__orgao=funcao_usuario.orgao,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        if funcao_usuario.grande_comando:
            return queryset.filter(
                militar__lotacoes__grande_comando=funcao_usuario.grande_comando,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            return queryset.filter(
                Q(militar__lotacoes__unidade=funcao_usuario.unidade) |
                Q(militar__lotacoes__sub_unidade__in=subunidades),
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas pela subunidade específica
        if funcao_usuario.sub_unidade:
            return queryset.filter(
                militar__lotacoes__sub_unidade=funcao_usuario.sub_unidade,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    return queryset.none()
