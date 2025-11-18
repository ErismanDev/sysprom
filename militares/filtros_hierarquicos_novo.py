"""
Módulo para filtros hierárquicos baseados no tipo de acesso das funções militares.

Este módulo centraliza a lógica de filtros hierárquicos para garantir consistência
em todas as views que exibem dados de militares.

SISTEMA ATUALIZADO:
- Superusuário: BYPASS COMPLETO (acesso total a tudo)
- Função militar: controle baseado apenas na função, não no usuário
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


def aplicar_filtro_hierarquico_notas(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para notas baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de Publicacao (tipo='NOTA') para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset.filter(tipo='NOTA', ativo=True)
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Usar apenas os dados da função militar, não do usuário
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todas as notas
        return queryset.filter(tipo='NOTA', ativo=True)
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas notas do próprio usuário
        return queryset.filter(
            tipo='NOTA',
            ativo=True,
            criado_por=funcao_usuario.usuario
        )
        
    elif funcao_militar.acesso == 'ORGAO':
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
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
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
            
    elif funcao_militar.acesso == 'UNIDADE':
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
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
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


def aplicar_filtro_hierarquico_documentos(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para documentos baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de Documento para filtrar
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
        # Acesso total - mostrar todos os documentos
        return queryset
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas documentos do próprio militar
        return queryset.filter(militar__user=funcao_usuario.usuario)
        
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


def aplicar_filtro_hierarquico_fichas(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para fichas de conceito baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de FichaConceito para filtrar
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
        # Acesso total - mostrar todas as fichas
        return queryset
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas fichas do próprio militar
        return queryset.filter(militar__user=funcao_usuario.usuario)
        
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
