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
    Aplica filtro hierárquico para militares baseado no organograma do sistema.
    
    SEGUE O ORGANOGRAMA:
    - ÓRGÃO: Acesso ao órgão + TODAS suas descendências (grandes comandos, unidades, subunidades)
    - GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências (unidades, subunidades)
    - UNIDADE: Acesso à unidade + TODAS suas subunidades
    - SUBUNIDADE: Acesso apenas à subunidade específica
    
    Args:
        queryset: QuerySet de Militar para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no organograma
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset.filter(classificacao='ATIVO')
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da lotação
    if funcao_militar.acesso == 'TOTAL':
        return queryset.filter(classificacao='ATIVO')
        
    # TIPO DE ACESSO = NENHUM: Nenhum acesso - não vê nada
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
        
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        from .models import Militar, Lotacao, GrandeComando, Unidade, SubUnidade
        
        # Buscar a lotação REAL do militar
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_atual = Lotacao.objects.filter(
                militar=militar,
                ativo=True,
                status='ATUAL'
            ).first()
            
            if lotacao_atual and lotacao_atual.orgao:
                # Buscar TODAS as descendências do órgão da lotação REAL
                grandes_comandos = GrandeComando.objects.filter(orgao=lotacao_atual.orgao, ativo=True)
                unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
                subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
                
                # Filtrar militares que estejam no órgão ou em qualquer uma de suas descendências
                filtro_base = Q()
                
                # Adicionar órgão
                filtro_base |= Q(
                    lotacoes__orgao=lotacao_atual.orgao,
                    lotacoes__status='ATUAL',
                    lotacoes__ativo=True
                )
                
                # Adicionar grandes comandos
                filtro_base |= Q(
                    lotacoes__grande_comando__in=grandes_comandos,
                    lotacoes__status='ATUAL',
                    lotacoes__ativo=True
                )
                
                # Adicionar unidades
                filtro_base |= Q(
                    lotacoes__unidade__in=unidades,
                    lotacoes__status='ATUAL',
                    lotacoes__ativo=True
                )
                
                # Adicionar subunidades
                filtro_base |= Q(
                    lotacoes__sub_unidade__in=subunidades,
                    lotacoes__status='ATUAL',
                    lotacoes__ativo=True
                )
                
                return queryset.filter(
                    classificacao='ATIVO'
                ).filter(filtro_base).distinct()
        except Militar.DoesNotExist:
            pass
        
        return queryset.none()
            
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso APENAS ao grande comando (sem descendências)
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        from .models import Militar, Lotacao
        
        # Buscar a lotação REAL do militar
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_atual = Lotacao.objects.filter(
                militar=militar,
                ativo=True,
                status='ATUAL'
            ).first()
            
            if lotacao_atual and lotacao_atual.grande_comando:
                # Filtrar APENAS militares lotados diretamente no grande comando
                return queryset.filter(
                    classificacao='ATIVO',
                    lotacoes__grande_comando=lotacao_atual.grande_comando,
                    lotacoes__status='ATUAL',
                    lotacoes__ativo=True
                ).distinct()
        except Militar.DoesNotExist:
            pass
        
        return queryset.none()
            
    # TIPO DE ACESSO = UNIDADE: Acesso APENAS à unidade (sem subunidades)
    elif funcao_militar.acesso == 'UNIDADE':
        from .models import Militar, Lotacao
        
        # Buscar a lotação REAL do militar
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_atual = Lotacao.objects.filter(
                militar=militar,
                ativo=True,
                status='ATUAL'
            ).first()
            
            if lotacao_atual and lotacao_atual.unidade:
                # Filtrar APENAS militares lotados diretamente na unidade
                return queryset.filter(
                    classificacao='ATIVO',
                    lotacoes__unidade=lotacao_atual.unidade,
                    lotacoes__status='ATUAL',
                    lotacoes__ativo=True
                ).distinct()
        except Militar.DoesNotExist:
            pass
        
        return queryset.none()
            
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        from .models import Militar, Lotacao
        
        # Buscar a lotação REAL do militar
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_atual = Lotacao.objects.filter(
                militar=militar,
                ativo=True,
                status='ATUAL'
            ).first()
            
            if lotacao_atual and lotacao_atual.sub_unidade:
                # Filtrar militares que estejam APENAS na subunidade específica da lotação REAL
                return queryset.filter(
                    classificacao='ATIVO',
                    lotacoes__sub_unidade=lotacao_atual.sub_unidade,
                    lotacoes__status='ATUAL',
                    lotacoes__ativo=True
                ).distinct()
        except Militar.DoesNotExist:
            pass
        
        return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_escala_abonar(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para escala de abonar baseado na função do usuário.
    Versão simplificada que retorna todos os militares ativos com lotação atual.
    
    Args:
        queryset: QuerySet de Militar para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado na função do usuário
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset.filter(classificacao='ATIVO')
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.filter(classificacao='ATIVO')  # Retornar todos os ativos se não tem função
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da lotação
    if funcao_militar.acesso == 'TOTAL':
        return queryset.filter(classificacao='ATIVO')
        
    # TIPO DE ACESSO = NENHUM: Nenhum acesso - não vê nada
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
        
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + todas as suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        orgao_funcao = funcao_usuario.orgao
        if not orgao_funcao:
            return queryset.none()
        
        # Buscar todas as descendências do órgão
        from .models import GrandeComando, Unidade, SubUnidade, Lotacao
        from django.db.models import Q
        
        grandes_comandos = GrandeComando.objects.filter(orgao=orgao_funcao, ativo=True)
        unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        
        # Buscar lotações atuais que pertencem ao órgão ou suas descendências
        lotacoes_orgao = Lotacao.objects.filter(
            Q(orgao=orgao_funcao) |
            Q(grande_comando__in=grandes_comandos) |
            Q(unidade__in=unidades) |
            Q(sub_unidade__in=subunidades),
            status='ATUAL',
            ativo=True
        ).select_related('militar')
        
        # Filtrar militares pelas lotações
        if lotacoes_orgao.exists():
            militares_ids = [l.militar.id for l in lotacoes_orgao]
            return queryset.filter(id__in=militares_ids)
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        grande_comando_funcao = funcao_usuario.grande_comando
        if not grande_comando_funcao:
            return queryset.none()
        
        # Buscar todas as descendências do grande comando
        from .models import Unidade, SubUnidade, Lotacao
        from django.db.models import Q
        
        unidades = Unidade.objects.filter(grande_comando=grande_comando_funcao, ativo=True)
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        
        # Buscar lotações atuais que pertencem ao grande comando ou suas descendências
        lotacoes_gc = Lotacao.objects.filter(
            Q(grande_comando=grande_comando_funcao) |
            Q(unidade__in=unidades) |
            Q(sub_unidade__in=subunidades),
            status='ATUAL',
            ativo=True
        ).select_related('militar')
        
        # Filtrar militares pelas lotações
        if lotacoes_gc.exists():
            militares_ids = [l.militar.id for l in lotacoes_gc]
            return queryset.filter(id__in=militares_ids)
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + suas descendências
    elif funcao_militar.acesso == 'UNIDADE':
        unidade_funcao = funcao_usuario.unidade
        if not unidade_funcao:
            return queryset.none()
        
        # Buscar todas as descendências da unidade
        from .models import SubUnidade, Lotacao
        from django.db.models import Q
        
        subunidades = SubUnidade.objects.filter(unidade=unidade_funcao, ativo=True)
        
        # Buscar lotações atuais que pertencem à unidade ou suas descendências
        lotacoes_unidade = Lotacao.objects.filter(
            Q(unidade=unidade_funcao) |
            Q(sub_unidade__in=subunidades),
            status='ATUAL',
            ativo=True
        ).select_related('militar')
        
        # Filtrar militares pelas lotações
        if lotacoes_unidade.exists():
            militares_ids = [l.militar.id for l in lotacoes_unidade]
            return queryset.filter(id__in=militares_ids)
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade
    elif funcao_militar.acesso == 'SUBUNIDADE':
        subunidade_funcao = funcao_usuario.sub_unidade
        if not subunidade_funcao:
            return queryset.none()
        
        # Buscar lotações atuais que pertencem à subunidade
        from .models import Lotacao
        
        lotacoes_sub = Lotacao.objects.filter(
            sub_unidade=subunidade_funcao,
            status='ATUAL',
            ativo=True
        ).select_related('militar')
        
        # Filtrar militares pelas lotações
        if lotacoes_sub.exists():
            militares_ids = [l.militar.id for l in lotacoes_sub]
            return queryset.filter(id__in=militares_ids)
        else:
            return queryset.none()
    
    # Se chegou aqui, retornar vazio por segurança
    return queryset.none()


def aplicar_filtro_hierarquico_notas_inicial(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para a lista inicial - mostra apenas notas da instância específica
    """
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - ver todas as notas
        return queryset.filter(tipo='NOTA')
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - não vê nada
        return queryset.none()
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - mostrar apenas notas do órgão específico
        orgao_usuario = None
        
        if funcao_usuario.orgao:
            orgao_usuario = funcao_usuario.orgao
        elif funcao_usuario.grande_comando:
            orgao_usuario = funcao_usuario.grande_comando.orgao
        elif funcao_usuario.unidade:
            orgao_usuario = funcao_usuario.unidade.grande_comando.orgao
        elif funcao_usuario.sub_unidade:
            orgao_usuario = funcao_usuario.sub_unidade.unidade.grande_comando.orgao
        
        if orgao_usuario:
            # Filtrar apenas por notas que sejam diretamente do órgão (não de unidades subordinadas)
            # Notas do órgão devem começar com o nome do órgão ou ter apenas o órgão
            filtro_orgao = Q(tipo='NOTA') & (
                # Órgão sozinho
                Q(origem_publicacao__iexact=orgao_usuario.nome) |
                Q(origem_publicacao__iexact=orgao_usuario.sigla) |
                # Órgão com emoji
                Q(origem_publicacao__iexact=f"{orgao_usuario.nome}") |
                # Órgão que não contenha " | " (não é hierarquia)
                Q(origem_publicacao__icontains=orgao_usuario.nome) & ~Q(origem_publicacao__icontains=" | ") |
                Q(origem_publicacao__icontains=orgao_usuario.sigla) & ~Q(origem_publicacao__icontains=" | ")
            )
            return queryset.filter(filtro_orgao)
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - mostrar apenas notas do grande comando específico
        grande_comando_usuario = None
        
        if funcao_usuario.grande_comando:
            grande_comando_usuario = funcao_usuario.grande_comando
        elif funcao_usuario.unidade:
            grande_comando_usuario = funcao_usuario.unidade.grande_comando
        elif funcao_usuario.sub_unidade:
            grande_comando_usuario = funcao_usuario.sub_unidade.unidade.grande_comando
        
        if grande_comando_usuario:
            # Filtrar por notas que sejam diretamente do grande comando
            # Pode ser o nome sozinho ou como parte de uma hierarquia
            filtro_gc = Q(tipo='NOTA') & (
                # Grande comando sozinho (sem hierarquia)
                Q(origem_publicacao__iexact=grande_comando_usuario.nome) |
                Q(origem_publicacao__iexact=grande_comando_usuario.sigla) |
                # Grande comando como último elemento da hierarquia (termina com o nome)
                Q(origem_publicacao__iendswith=f" | {grande_comando_usuario.nome}") |
                Q(origem_publicacao__iendswith=f" | {grande_comando_usuario.sigla}")
            )
            return queryset.filter(filtro_gc)
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - mostrar apenas notas da unidade específica
        unidade_usuario = None
        
        if funcao_usuario.unidade:
            unidade_usuario = funcao_usuario.unidade
        elif funcao_usuario.sub_unidade:
            unidade_usuario = funcao_usuario.sub_unidade.unidade
        
        if unidade_usuario:
            # Filtrar por notas que sejam diretamente da unidade
            # Pode ser o nome sozinho ou como parte de uma hierarquia
            filtro_unidade = Q(tipo='NOTA') & (
                # Unidade sozinha (sem hierarquia)
                Q(origem_publicacao__iexact=unidade_usuario.nome) |
                Q(origem_publicacao__iexact=unidade_usuario.sigla) |
                # Unidade como último elemento da hierarquia (termina com o nome)
                Q(origem_publicacao__iendswith=f" | {unidade_usuario.nome}") |
                Q(origem_publicacao__iendswith=f" | {unidade_usuario.sigla}")
            )
            return queryset.filter(filtro_unidade)
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - mostrar apenas notas da subunidade específica
        if funcao_usuario.sub_unidade:
            # Filtrar por notas que sejam diretamente da subunidade
            # Pode ser o nome sozinho ou como parte de uma hierarquia
            filtro_subunidade = Q(tipo='NOTA') & (
                # Subunidade sozinha (sem hierarquia)
                Q(origem_publicacao__iexact=funcao_usuario.sub_unidade.nome) |
                Q(origem_publicacao__iexact=funcao_usuario.sub_unidade.sigla) |
                # Subunidade como último elemento da hierarquia (termina com o nome)
                Q(origem_publicacao__iendswith=f" | {funcao_usuario.sub_unidade.nome}") |
                Q(origem_publicacao__iendswith=f" | {funcao_usuario.sub_unidade.sigla}")
            )
            return queryset.filter(filtro_subunidade)
        else:
            return queryset.none()
    
    return queryset.none()


def _origem_pertence_estrutura(origem, orgao, grandes_comandos, unidades, subunidades):
    """
    Verifica se uma origem pertence à estrutura hierárquica
    """
    origem_lower = origem.lower().strip()
    
    # Verificar se pertence ao órgão
    if orgao.nome.lower() in origem_lower or orgao.sigla.lower() in origem_lower:
        return True
    
    # Verificar se pertence aos grandes comandos
    for gc in grandes_comandos:
        if gc.nome.lower() in origem_lower or gc.sigla.lower() in origem_lower:
            return True
    
    # Verificar se pertence às unidades
    for u in unidades:
        if u.nome.lower() in origem_lower or u.sigla.lower() in origem_lower:
            return True
    
    # Verificar se pertence às subunidades
    for su in subunidades:
        if su.nome.lower() in origem_lower or su.sigla.lower() in origem_lower:
            return True
    
    return False


def _origem_pertence_grande_comando(origem, grande_comando, unidades, subunidades):
    """
    Verifica se uma origem pertence ao grande comando e suas descendências
    """
    origem_lower = origem.lower().strip()
    
    # Verificar se pertence ao grande comando
    if grande_comando.nome.lower() in origem_lower or grande_comando.sigla.lower() in origem_lower:
        return True
    
    # Verificar se pertence às unidades
    for u in unidades:
        if u.nome.lower() in origem_lower or u.sigla.lower() in origem_lower:
            return True
    
    # Verificar se pertence às subunidades
    for su in subunidades:
        if su.nome.lower() in origem_lower or su.sigla.lower() in origem_lower:
            return True
    
    return False


def _origem_pertence_unidade(origem, unidade, subunidades):
    """
    Verifica se uma origem pertence à unidade e suas descendências
    """
    origem_lower = origem.lower().strip()
    
    # Verificar se pertence à unidade
    if unidade.nome.lower() in origem_lower or unidade.sigla.lower() in origem_lower:
        return True
    
    # Verificar se pertence às subunidades
    for su in subunidades:
        if su.nome.lower() in origem_lower or su.sigla.lower() in origem_lower:
            return True
    
    return False


def _origem_pertence_subunidade(origem, subunidade):
    """
    Verifica se uma origem pertence à subunidade
    """
    origem_lower = origem.lower().strip()
    
    # Verificar se pertence à subunidade
    if subunidade.nome.lower() in origem_lower or subunidade.sigla.lower() in origem_lower:
        return True
    
    return False


def aplicar_filtro_hierarquico_notas(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para notas baseado na LOTACAO do militar + TIPO DE ACESSO da função.
    
    LÓGICA CORRETA:
    1. Militar tem LOTACAO (órgão, grande comando, unidade ou subunidade)
    2. Função militar tem TIPO DE ACESSO (TOTAL, ORGAO, GRANDE_COMANDO, UNIDADE, SUBUNIDADE)
    3. Acesso = TIPO DE ACESSO aplicado na LOTACAO + descendência
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total dentro da estrutura da lotação
    - ORGAO: Acesso ao órgão da lotação + toda descendência
    - GRANDE_COMANDO: Acesso ao grande comando da lotação + toda descendência
    - UNIDADE: Acesso à unidade da lotação + toda descendência  
    - SUBUNIDADE: Acesso apenas à subunidade da lotação
    
    Args:
        queryset: QuerySet de Publicacao (tipo='NOTA') para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado na lotação + tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset.filter(tipo__in=['NOTA', 'NOTA_RESERVADA'])
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total a todas as notas
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - retornar todas as notas do tipo NOTA e NOTA_RESERVADA
        return queryset.filter(tipo__in=['NOTA', 'NOTA_RESERVADA'])
        
    # TIPO DE ACESSO = NENHUM: Nenhum acesso - não vê nada
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso apenas ao órgão da função militar
    elif funcao_militar.acesso == 'ORGAO':
        # Usar o órgão da função militar, não da lotação do usuário
        if funcao_usuario.orgao:
            # Filtrar APENAS pelo órgão da função militar
            filtro_base = Q(tipo__in=['NOTA', 'NOTA_RESERVADA']) & (
                Q(origem_publicacao__iexact=funcao_usuario.orgao.nome) |
                Q(origem_publicacao__iexact=funcao_usuario.orgao.sigla)
            )
            return queryset.filter(filtro_base).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso apenas ao grande comando da função militar
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Usar o grande comando da função militar, não da lotação do usuário
        if funcao_usuario.grande_comando:
            # Filtrar APENAS pelo grande comando da função militar
            # Mostrar apenas notas que são diretamente do grande comando
            nome_gc = funcao_usuario.grande_comando.nome.strip()
            sigla_gc = funcao_usuario.grande_comando.sigla.strip()
            
            # Primeiro tentar filtro exato
            filtro_exato = Q(tipo__in=['NOTA', 'NOTA_RESERVADA']) & (
                Q(origem_publicacao__iexact=nome_gc) |
                Q(origem_publicacao__iexact=sigla_gc)
            )
            notas_exatas = queryset.filter(filtro_exato)
            
            if notas_exatas.exists():
                return notas_exatas.distinct()
            
            # Se não encontrou, tentar com espaços
            for espacos in ['       ', '      ', '     ', '    ', '   ', '  ', ' ']:
                filtro_espacos = Q(tipo__in=['NOTA', 'NOTA_RESERVADA']) & (
                    Q(origem_publicacao__iexact=f"{espacos}{nome_gc}") |
                    Q(origem_publicacao__iexact=f"{espacos}{sigla_gc}")
                )
                notas_espacos = queryset.filter(filtro_espacos)
                if notas_espacos.exists():
                    return notas_espacos.distinct()
            
            # Como último recurso, usar icontains mas filtrar manualmente
            # para incluir apenas notas que são diretamente do grande comando
            todas_notas = queryset.filter(tipo__in=['NOTA', 'NOTA_RESERVADA'])
            notas_filtradas = []
            
            for nota in todas_notas:
                origem = nota.origem_publicacao.strip()
                # Verificar se a origem é exatamente o grande comando ou começa com ele
                if (origem == nome_gc or origem == sigla_gc or 
                    origem.startswith(nome_gc + ' |') or origem.startswith(sigla_gc + ' |')):
                    notas_filtradas.append(nota.id)
            
            return queryset.filter(id__in=notas_filtradas).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso apenas à unidade da função militar
    elif funcao_militar.acesso == 'UNIDADE':
        # Usar a unidade da função militar, não da lotação do usuário
        if funcao_usuario.unidade:
            # Filtrar APENAS pela unidade da função militar
            # Usar filtro robusto para lidar com espaços e caracteres especiais
            nome_unidade = funcao_usuario.unidade.nome.strip()
            sigla_unidade = funcao_usuario.unidade.sigla.strip()
            
            # Primeiro tentar filtro exato
            filtro_exato = Q(tipo='NOTA') & (
                Q(origem_publicacao__iexact=nome_unidade) |
                Q(origem_publicacao__iexact=sigla_unidade)
            )
            notas_exatas = queryset.filter(filtro_exato)
            
            if notas_exatas.exists():
                return notas_exatas.distinct()
            
            # Se não encontrou, tentar com espaços
            for espacos in ['       ', '      ', '     ', '    ', '   ', '  ', ' ']:
                filtro_espacos = Q(tipo='NOTA') & (
                    Q(origem_publicacao__iexact=f"{espacos}{nome_unidade}") |
                    Q(origem_publicacao__iexact=f"{espacos}{sigla_unidade}")
                )
                notas_espacos = queryset.filter(filtro_espacos)
                if notas_espacos.exists():
                    return notas_espacos.distinct()
            
            # Como último recurso, usar icontains mas filtrar manualmente
            # para incluir apenas notas que são diretamente da unidade
            todas_notas = queryset.filter(tipo__in=['NOTA', 'NOTA_RESERVADA'])
            notas_filtradas = []
            
            for nota in todas_notas:
                origem = nota.origem_publicacao.strip()
                # Verificar se a origem é exatamente a unidade ou começa com ela
                if (origem == nome_unidade or origem == sigla_unidade or 
                    origem.startswith(nome_unidade + ' |') or origem.startswith(sigla_unidade + ' |')):
                    notas_filtradas.append(nota.id)
            
            return queryset.filter(id__in=notas_filtradas).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade da função militar
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Usar a subunidade da função militar, não da lotação do usuário
        if funcao_usuario.sub_unidade:
            # Filtrar APENAS pela subunidade da função militar
            # Usar filtro robusto para lidar com espaços e caracteres especiais
            nome_subunidade = funcao_usuario.sub_unidade.nome.strip()
            sigla_subunidade = funcao_usuario.sub_unidade.sigla.strip()
            
            # Primeiro tentar filtro exato
            filtro_exato = Q(tipo='NOTA') & (
                Q(origem_publicacao__iexact=nome_subunidade) |
                Q(origem_publicacao__iexact=sigla_subunidade)
            )
            notas_exatas = queryset.filter(filtro_exato)
            
            if notas_exatas.exists():
                return notas_exatas.distinct()
            
            # Se não encontrou, tentar com espaços
            for espacos in ['       ', '      ', '     ', '    ', '   ', '  ', ' ']:
                filtro_espacos = Q(tipo='NOTA') & (
                    Q(origem_publicacao__iexact=f"{espacos}{nome_subunidade}") |
                    Q(origem_publicacao__iexact=f"{espacos}{sigla_subunidade}")
                )
                notas_espacos = queryset.filter(filtro_espacos)
                if notas_espacos.exists():
                    return notas_espacos.distinct()
            
            # Como último recurso, usar icontains mas filtrar manualmente
            # para incluir apenas notas que são diretamente da subunidade
            todas_notas = queryset.filter(tipo__in=['NOTA', 'NOTA_RESERVADA'])
            notas_filtradas = []
            
            for nota in todas_notas:
                origem = nota.origem_publicacao.strip()
                # Verificar se a origem é exatamente a subunidade ou começa com ela
                if (origem == nome_subunidade or origem == sigla_subunidade or 
                    origem.startswith(nome_subunidade + ' |') or origem.startswith(sigla_subunidade + ' |')):
                    notas_filtradas.append(nota.id)
            
            return queryset.filter(id__in=notas_filtradas).distinct()
        
        return queryset.none()
    
    return queryset.none()


def obter_opcoes_filtro_hierarquico_notas(funcao_usuario, user=None):
    """
    Obtém as opções de filtro hierárquico para notas baseado no nível de acesso da função.
    
    Args:
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        dict: Dicionário com as opções de filtro disponíveis
    """
    from .models import Orgao, GrandeComando, Unidade, SubUnidade
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return {
            'orgaos': Orgao.objects.filter(ativo=True).order_by('nome'),
            'grandes_comandos': GrandeComando.objects.filter(ativo=True).order_by('nome'),
            'unidades': Unidade.objects.filter(ativo=True).order_by('nome'),
            'subunidades': SubUnidade.objects.filter(ativo=True).order_by('nome'),
        }
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return {
            'orgaos': Orgao.objects.none(),
            'grandes_comandos': GrandeComando.objects.none(),
            'unidades': Unidade.objects.none(),
            'subunidades': SubUnidade.objects.none(),
        }
    
    funcao_militar = funcao_usuario.funcao_militar
    
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todas as opções
        return {
            'orgaos': Orgao.objects.filter(ativo=True).order_by('nome'),
            'grandes_comandos': GrandeComando.objects.filter(ativo=True).order_by('nome'),
            'unidades': Unidade.objects.filter(ativo=True).order_by('nome'),
            'subunidades': SubUnidade.objects.filter(ativo=True).order_by('nome'),
        }
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - não mostrar opções
        return {
            'orgaos': Orgao.objects.none(),
            'grandes_comandos': GrandeComando.objects.none(),
            'unidades': Unidade.objects.none(),
            'subunidades': SubUnidade.objects.none(),
        }
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - mostrar apenas a estrutura de lotação do usuário
        orgao_usuario = None
        grande_comando_usuario = None
        unidade_usuario = None
        subunidade_usuario = None
        
        # Identificar a estrutura de lotação do usuário
        if funcao_usuario.orgao:
            orgao_usuario = funcao_usuario.orgao
        elif funcao_usuario.grande_comando:
            orgao_usuario = funcao_usuario.grande_comando.orgao
            grande_comando_usuario = funcao_usuario.grande_comando
        elif funcao_usuario.unidade:
            orgao_usuario = funcao_usuario.unidade.grande_comando.orgao
            grande_comando_usuario = funcao_usuario.unidade.grande_comando
            unidade_usuario = funcao_usuario.unidade
        elif funcao_usuario.sub_unidade:
            orgao_usuario = funcao_usuario.sub_unidade.unidade.grande_comando.orgao
            grande_comando_usuario = funcao_usuario.sub_unidade.unidade.grande_comando
            unidade_usuario = funcao_usuario.sub_unidade.unidade
            subunidade_usuario = funcao_usuario.sub_unidade
        
        if orgao_usuario:
            # Montar filtros baseados na estrutura real de lotação do usuário + TODAS as descendências
            orgaos = Orgao.objects.filter(id=orgao_usuario.id)
            
            # Buscar TODAS as descendências do órgão do usuário
            grandes_comandos = GrandeComando.objects.filter(orgao=orgao_usuario, ativo=True)
            unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
            subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
            
            return {
                'orgaos': orgaos,
                'grandes_comandos': grandes_comandos,
                'unidades': unidades,
                'subunidades': subunidades,
            }
        else:
            return {
                'orgaos': Orgao.objects.none(),
                'grandes_comandos': GrandeComando.objects.none(),
                'unidades': Unidade.objects.none(),
                'subunidades': SubUnidade.objects.none(),
            }
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - mostrar apenas a estrutura de lotação do usuário
        grande_comando_usuario = None
        unidade_usuario = None
        subunidade_usuario = None
        
        # Identificar a estrutura de lotação do usuário
        if funcao_usuario.grande_comando:
            grande_comando_usuario = funcao_usuario.grande_comando
        elif funcao_usuario.unidade:
            grande_comando_usuario = funcao_usuario.unidade.grande_comando
            unidade_usuario = funcao_usuario.unidade
        elif funcao_usuario.sub_unidade:
            grande_comando_usuario = funcao_usuario.sub_unidade.unidade.grande_comando
            unidade_usuario = funcao_usuario.sub_unidade.unidade
            subunidade_usuario = funcao_usuario.sub_unidade
        
        if grande_comando_usuario:
            # Montar filtros baseados na estrutura real de lotação do usuário + TODAS as descendências
            grandes_comandos = GrandeComando.objects.filter(id=grande_comando_usuario.id)
            
            # Buscar TODAS as descendências do grande comando do usuário
            unidades = Unidade.objects.filter(grande_comando=grande_comando_usuario, ativo=True)
            subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
            
            return {
                'orgaos': Orgao.objects.none(),
                'grandes_comandos': grandes_comandos,
                'unidades': unidades,
                'subunidades': subunidades,
            }
        else:
            return {
                'orgaos': Orgao.objects.none(),
                'grandes_comandos': GrandeComando.objects.none(),
                'unidades': Unidade.objects.none(),
                'subunidades': SubUnidade.objects.none(),
            }
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - mostrar apenas a estrutura de lotação do usuário
        unidade_usuario = None
        subunidade_usuario = None
        
        # Identificar a estrutura de lotação do usuário
        if funcao_usuario.unidade:
            unidade_usuario = funcao_usuario.unidade
        elif funcao_usuario.sub_unidade:
            unidade_usuario = funcao_usuario.sub_unidade.unidade
            subunidade_usuario = funcao_usuario.sub_unidade
        
        if unidade_usuario:
            # Montar filtros baseados na estrutura real de lotação do usuário + TODAS as descendências
            unidades = Unidade.objects.filter(id=unidade_usuario.id)
            
            # Buscar TODAS as descendências da unidade do usuário
            subunidades = SubUnidade.objects.filter(unidade=unidade_usuario, ativo=True)
            
            return {
                'orgaos': Orgao.objects.none(),
                'grandes_comandos': GrandeComando.objects.none(),
                'unidades': unidades,
                'subunidades': subunidades,
            }
        else:
            return {
                'orgaos': Orgao.objects.none(),
                'grandes_comandos': GrandeComando.objects.none(),
                'unidades': Unidade.objects.none(),
                'subunidades': SubUnidade.objects.none(),
            }
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - mostrar apenas a subunidade
        if funcao_usuario.sub_unidade:
            return {
                'orgaos': Orgao.objects.none(),
                'grandes_comandos': GrandeComando.objects.none(),
                'unidades': Unidade.objects.none(),
                'subunidades': SubUnidade.objects.filter(id=funcao_usuario.sub_unidade.id),
            }
        else:
            return {
                'orgaos': Orgao.objects.none(),
                'grandes_comandos': GrandeComando.objects.none(),
                'unidades': Unidade.objects.none(),
                'subunidades': SubUnidade.objects.none(),
            }
    
    return {
        'orgaos': Orgao.objects.none(),
        'grandes_comandos': GrandeComando.objects.none(),
        'unidades': Unidade.objects.none(),
        'subunidades': SubUnidade.objects.none(),
    }


def aplicar_filtro_hierarquico_escalas(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para escalas baseado na LOTACAO do militar + TIPO DE ACESSO da função.
    
    LÓGICA CORRETA (igual ao sistema de notas):
    1. Militar tem LOTACAO (órgão, grande comando, unidade ou subunidade)
    2. Função militar tem TIPO DE ACESSO (TOTAL, GRANDE_COMANDO, UNIDADE, SUBUNIDADE)
    3. Acesso = TIPO DE ACESSO aplicado na LOTACAO + descendência
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da lotação
    - GRANDE_COMANDO: Acesso ao grande comando da lotação + toda descendência
    - UNIDADE: Acesso à unidade da lotação + toda descendência  
    - SUBUNIDADE: Acesso apenas à subunidade da lotação
    
    Args:
        queryset: QuerySet de EscalaServico para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado na lotação + tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da lotação
    if funcao_militar.acesso == 'TOTAL':
        return queryset
        
    # TIPO DE ACESSO = NENHUM: Apenas escalas onde o militar está escalado
    elif funcao_militar.acesso == 'NENHUM':
        try:
            from .models import Militar, EscalaMilitar
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            escalas_militar = EscalaMilitar.objects.filter(militar=militar).values_list('escala_id', flat=True)
            return queryset.filter(id__in=escalas_militar)
        except Militar.DoesNotExist:
            return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        from .models import GrandeComando, Unidade, SubUnidade
        
        if funcao_usuario.orgao:
            # Buscar TODAS as descendências do órgão seguindo o organograma
            grandes_comandos = GrandeComando.objects.filter(orgao=funcao_usuario.orgao, ativo=True)
            unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
            subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
            
            # Filtrar escalas que sejam do órgão ou de qualquer uma de suas descendências
            filtro_base = Q()
            
            # Adicionar órgão
            filtro_base |= Q(organizacao__icontains=funcao_usuario.orgao.nome)
            
            # Adicionar grandes comandos
            for gc in grandes_comandos:
                filtro_base |= Q(organizacao__icontains=gc.nome)
            
            # Adicionar unidades
            for u in unidades:
                filtro_base |= Q(organizacao__icontains=u.nome)
            
            # Adicionar subunidades
            for s in subunidades:
                filtro_base |= Q(organizacao__icontains=s.nome)
            
            return queryset.filter(filtro_base).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        from .models import Militar, Lotacao, Unidade, SubUnidade
        
        # Buscar a lotação REAL do militar
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_atual = Lotacao.objects.filter(
                militar=militar,
                ativo=True,
                status='ATUAL'
            ).first()
            
            if lotacao_atual and lotacao_atual.grande_comando:
                # Buscar TODAS as descendências do grande comando da lotação REAL
                unidades = Unidade.objects.filter(grande_comando=lotacao_atual.grande_comando, ativo=True)
                subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
                
                # Filtrar escalas que sejam do grande comando ou de qualquer uma de suas descendências
                filtro_base = Q()
                
                # Adicionar grande comando
                filtro_base |= Q(organizacao__icontains=lotacao_atual.grande_comando.nome)
                
                # Adicionar unidades
                for u in unidades:
                    filtro_base |= Q(organizacao__icontains=u.nome)
                
                # Adicionar subunidades
                for s in subunidades:
                    filtro_base |= Q(organizacao__icontains=s.nome)
                
                return queryset.filter(filtro_base).distinct()
        except Militar.DoesNotExist:
            pass
        
        return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        from .models import SubUnidade
        
        if funcao_usuario.unidade:
            # Buscar TODAS as subunidades da unidade seguindo o organograma
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade, ativo=True)
            
            # Filtrar escalas que sejam da unidade ou de qualquer uma de suas subunidades
            filtro_base = Q()
            
            # Adicionar unidade
            filtro_base |= Q(organizacao__icontains=funcao_usuario.unidade.nome)
            
            # Adicionar subunidades
            for s in subunidades:
                filtro_base |= Q(organizacao__icontains=s.nome)
            
            return queryset.filter(filtro_base).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade da lotação
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            # Filtrar APENAS pela subunidade da lotação
            filtro_base = Q(
                organizacao__icontains=funcao_usuario.sub_unidade.nome
            )
            return queryset.filter(filtro_base).distinct()
        
        return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_lotacoes(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para lotações baseado na LOTACAO do militar + TIPO DE ACESSO da função.
    
    LÓGICA CORRETA (igual ao sistema de notas e escalas):
    1. Militar tem LOTACAO (órgão, grande comando, unidade ou subunidade)
    2. Função militar tem TIPO DE ACESSO (TOTAL, ORGAO, GRANDE_COMANDO, UNIDADE, SUBUNIDADE)
    3. Acesso = TIPO DE ACESSO aplicado na LOTACAO + descendência
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da lotação
    - ORGAO: Acesso ao órgão + TODAS suas descendências
    - GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    - UNIDADE: Acesso à unidade + TODAS suas descendências  
    - SUBUNIDADE: Acesso apenas à subunidade específica
    
    Args:
        queryset: QuerySet de Lotacao para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado na lotação + tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da lotação
    if funcao_militar.acesso == 'TOTAL':
        return queryset
        
    # TIPO DE ACESSO = NENHUM: Apenas lotações do próprio militar
    elif funcao_militar.acesso == 'NENHUM':
        try:
            from .models import Militar
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            return queryset.filter(militar=militar)
        except Militar.DoesNotExist:
            return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        # Usar a lotação da função ativa do usuário
        from .models import GrandeComando, Unidade, SubUnidade
        
        if funcao_usuario.orgao:
            # Filtrar por órgão + TODAS suas descendências
            orgao_id = funcao_usuario.orgao.id
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao_id=orgao_id, ativo=True)
            gc_ids = list(grandes_comandos.values_list('id', flat=True))
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando_id__in=gc_ids, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para toda a hierarquia
            filtro_hierarquia = Q(orgao_id=orgao_id)
            
            if gc_ids:
                filtro_hierarquia |= Q(grande_comando_id__in=gc_ids)
            if unidade_ids:
                filtro_hierarquia |= Q(unidade_id__in=unidade_ids)
            if subunidade_ids:
                filtro_hierarquia |= Q(sub_unidade_id__in=subunidade_ids)
            
            return queryset.filter(filtro_hierarquia).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        from .models import Unidade, SubUnidade
        
        if funcao_usuario.grande_comando:
            # Filtrar por grande comando + TODAS suas descendências
            gc_id = funcao_usuario.grande_comando.id
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando_id=gc_id, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para toda a hierarquia
            filtro_hierarquia = Q(grande_comando_id=gc_id)
            
            if unidade_ids:
                filtro_hierarquia |= Q(unidade_id__in=unidade_ids)
            if subunidade_ids:
                filtro_hierarquia |= Q(sub_unidade_id__in=subunidade_ids)
            
            return queryset.filter(filtro_hierarquia).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas descendências
    elif funcao_militar.acesso == 'UNIDADE':
        from .models import SubUnidade
        
        if funcao_usuario.unidade:
            # Filtrar por unidade + TODAS suas descendências
            unidade_id = funcao_usuario.unidade.id
            
            # Buscar todas as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade_id=unidade_id, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para toda a hierarquia
            filtro_hierarquia = Q(unidade_id=unidade_id)
            
            if subunidade_ids:
                filtro_hierarquia |= Q(sub_unidade_id__in=subunidade_ids)
            
            return queryset.filter(filtro_hierarquia).distinct()
        
        return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            # Filtrar apenas pela subunidade específica
            return queryset.filter(sub_unidade_id=funcao_usuario.sub_unidade.id)
        
        return queryset.none()
    
    return queryset.none()


def obter_opcoes_filtro_hierarquico_escalas_abonar(funcao_usuario, user=None):
    """
    Obtém as opções de filtro hierárquico para escalas de abonar baseado na ORGANIZAÇÃO PRINCIPAL da função.
    
    LÓGICA CORRETA:
    - A escala de abonar deve listar inicialmente da organização principal conforme o acesso da função
    - Independente de qual instância o militar está lotado, o acesso é baseado na função
    - Com filtros para as escalas das descendências
    
    Args:
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        list: Lista de organizações disponíveis para filtro baseada na função
    """
    from .models import Militar, Lotacao, GrandeComando, Unidade, SubUnidade
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return []
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return []
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total - todo o organograma
    if funcao_militar.acesso == 'TOTAL':
        from .models import Orgao
        organizacoes = []
        
        # Buscar todos os órgãos e suas hierarquias
        orgaos = Orgao.objects.filter(ativo=True).prefetch_related(
            'grandes_comandos__unidades__sub_unidades'
        ).order_by('nome')
        
        for orgao in orgaos:
            # Adicionar órgão
            organizacoes.append({
                'id': f'orgao_{orgao.id}',
                'nome': orgao.nome,
                'tipo': 'orgao',
                'nivel': 1
            })
            
            # Adicionar grandes comandos
            for gc in orgao.grandes_comandos.filter(ativo=True).order_by('nome'):
                organizacoes.append({
                    'id': f'gc_{gc.id}',
                    'nome': f"{orgao.nome} | {gc.nome}",
                    'tipo': 'grande_comando',
                    'nivel': 2
                })
                
                # Adicionar unidades
                for unidade in gc.unidades.filter(ativo=True).order_by('nome'):
                    organizacoes.append({
                        'id': f'unidade_{unidade.id}',
                        'nome': f"{orgao.nome} | {gc.nome} | {unidade.nome}",
                        'tipo': 'unidade',
                        'nivel': 3
                    })
                    
                    # Adicionar sub-unidades
                    for sub_unidade in unidade.sub_unidades.filter(ativo=True).order_by('nome'):
                        organizacoes.append({
                            'id': f'sub_{sub_unidade.id}',
                            'nome': f"{orgao.nome} | {gc.nome} | {unidade.nome} | {sub_unidade.nome}",
                            'tipo': 'sub_unidade',
                            'nivel': 4
                        })
        
        return organizacoes
    
    # TIPO DE ACESSO = NENHUM: Apenas o próprio militar
    elif funcao_militar.acesso == 'NENHUM':
        return []
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão da função + todas as suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        # Usar EXCLUSIVAMENTE o órgão da função
        orgao_funcao = funcao_usuario.orgao
        if not orgao_funcao:
            # Se não tem órgão na função, não tem acesso
            return []
        
        # Retornar organizações em ordem hierárquica (mais alto para mais baixo)
        organizacoes = []
        
        # 1. Órgão (mais alto) - APENAS o órgão principal
        organizacoes.append({
            'id': f'orgao_{orgao_funcao.id}',
            'nome': orgao_funcao.nome,
            'tipo': 'orgao',
            'nivel': 1
        })
        
        # 2. Grandes comandos - com hierarquia completa
        grandes_comandos = GrandeComando.objects.filter(orgao=orgao_funcao, ativo=True)
        for gc in grandes_comandos.order_by('nome'):
            organizacoes.append({
                'id': f'gc_{gc.id}',
                'nome': f"{orgao_funcao.nome} | {gc.nome}",
                'tipo': 'grande_comando',
                'nivel': 2
            })
        
        # 3. Unidades - com hierarquia completa
        unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
        for u in unidades.order_by('nome'):
            organizacoes.append({
                'id': f'unidade_{u.id}',
                'nome': f"{orgao_funcao.nome} | {u.grande_comando.nome} | {u.nome}",
                'tipo': 'unidade',
                'nivel': 3
            })
        
        # 4. Subunidades - com hierarquia completa
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{orgao_funcao.nome} | {s.unidade.grande_comando.nome} | {s.unidade.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 4
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando da função + todas as suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Usar EXCLUSIVAMENTE o grande comando da função
        grande_comando_funcao = funcao_usuario.grande_comando
        if not grande_comando_funcao:
            # Se não tem grande comando na função, não tem acesso
            return []
        
        # Retornar organizações em ordem hierárquica
        organizacoes = []
        
        # 1. Grande comando (mais alto) - APENAS o grande comando principal
        organizacoes.append({
            'id': f'gc_{grande_comando_funcao.id}',
            'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome}",
            'tipo': 'grande_comando',
            'nivel': 1
        })
        
        # 2. Unidades - com hierarquia completa
        unidades = Unidade.objects.filter(grande_comando=grande_comando_funcao, ativo=True)
        for u in unidades.order_by('nome'):
            organizacoes.append({
                'id': f'unidade_{u.id}',
                'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome} | {u.nome}",
                'tipo': 'unidade',
                'nivel': 2
            })
        
        # 3. Subunidades - com hierarquia completa
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome} | {s.unidade.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 3
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade da função + todas as suas descendências
    elif funcao_militar.acesso == 'UNIDADE':
        # Usar EXCLUSIVAMENTE a unidade da função
        unidade_funcao = funcao_usuario.unidade
        if not unidade_funcao:
            # Se não tem unidade na função, não tem acesso
            return []
        
        # Retornar organizações em ordem hierárquica
        organizacoes = []
        
        # 1. Unidade (mais alto) - APENAS a unidade principal
        organizacoes.append({
            'id': f'unidade_{unidade_funcao.id}',
            'nome': f"{unidade_funcao.grande_comando.orgao.nome} | {unidade_funcao.grande_comando.nome} | {unidade_funcao.nome}",
            'tipo': 'unidade',
            'nivel': 1
        })
        
        # 2. Subunidades - com hierarquia completa
        subunidades = SubUnidade.objects.filter(unidade=unidade_funcao, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{unidade_funcao.grande_comando.orgao.nome} | {unidade_funcao.grande_comando.nome} | {unidade_funcao.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 2
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso APENAS à subunidade da função
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Usar EXCLUSIVAMENTE a subunidade da função
        subunidade_funcao = funcao_usuario.sub_unidade
        if not subunidade_funcao:
            # Se não tem subunidade na função, não tem acesso
            return []
        
        if subunidade_funcao:
            # Apenas a subunidade específica com hierarquia completa
            return [{
                'id': f'sub_{subunidade_funcao.id}',
                'nome': f"{subunidade_funcao.unidade.grande_comando.orgao.nome} | {subunidade_funcao.unidade.grande_comando.nome} | {subunidade_funcao.unidade.nome} | {subunidade_funcao.nome}",
                'tipo': 'sub_unidade',
                'nivel': 1
            }]
        
        return []
    
    return []


def obter_opcoes_filtro_hierarquico_escalas(funcao_usuario, user=None):
    """
    Obtém as opções de filtro hierárquico para escalas baseado na lotação + tipo de acesso.
    
    Args:
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        list: Lista de organizações disponíveis para filtro
    """
    from .models import Militar, Lotacao, EscalaServico
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return EscalaServico.objects.exclude(
            organizacao__isnull=True
        ).exclude(
            organizacao__exact=''
        ).values_list('organizacao', flat=True).distinct().order_by('organizacao')
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return []
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total
    if funcao_militar.acesso == 'TOTAL':
        return EscalaServico.objects.exclude(
            organizacao__isnull=True
        ).exclude(
            organizacao__exact=''
        ).values_list('organizacao', flat=True).distinct().order_by('organizacao')
    
    # TIPO DE ACESSO = NENHUM: Apenas escalas onde o militar está escalado
    elif funcao_militar.acesso == 'NENHUM':
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            from .models import EscalaMilitar
            escalas_militar = EscalaMilitar.objects.filter(militar=militar).values_list('escala_id', flat=True)
            return EscalaServico.objects.filter(
                id__in=escalas_militar
            ).exclude(
                organizacao__isnull=True
            ).exclude(
                organizacao__exact=''
            ).values_list('organizacao', flat=True).distinct().order_by('organizacao')
        except Militar.DoesNotExist:
            return []
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        from .models import GrandeComando, Unidade, SubUnidade
        
        if funcao_usuario.orgao:
            # Buscar TODAS as descendências do órgão seguindo o organograma
            grandes_comandos = GrandeComando.objects.filter(orgao=funcao_usuario.orgao, ativo=True)
            unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
            subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
            
            # Retornar organizações em ordem hierárquica (mais alto para mais baixo)
            organizacoes = []
            
            # 1. Órgão (mais alto)
            organizacoes.append(funcao_usuario.orgao.nome)
            
            # 2. Grandes comandos
            for gc in grandes_comandos.order_by('nome'):
                organizacoes.append(gc.nome)
            
            # 3. Unidades
            for u in unidades.order_by('nome'):
                organizacoes.append(u.nome)
            
            # 4. Subunidades (mais baixo)
            for s in subunidades.order_by('nome'):
                organizacoes.append(s.nome)
            
            return organizacoes
        
        return []
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        from .models import Militar, Lotacao, Unidade, SubUnidade
        
        # Buscar a lotação REAL do militar
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_atual = Lotacao.objects.filter(
                militar=militar,
                ativo=True,
                status='ATUAL'
            ).first()
            
            if lotacao_atual and lotacao_atual.grande_comando:
                # Buscar TODAS as descendências do grande comando da lotação REAL
                unidades = Unidade.objects.filter(grande_comando=lotacao_atual.grande_comando, ativo=True)
                subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
                
                # Retornar organizações em ordem hierárquica (mais alto para mais baixo)
                organizacoes = []
                
                # 1. Grande comando (mais alto)
                organizacoes.append(lotacao_atual.grande_comando.nome)
                
                # 2. Unidades
                for u in unidades.order_by('nome'):
                    organizacoes.append(u.nome)
                
                # 3. Subunidades (mais baixo)
                for s in subunidades.order_by('nome'):
                    organizacoes.append(s.nome)
                
                return organizacoes
        except Militar.DoesNotExist:
            pass
        
        return []
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        from .models import SubUnidade
        
        if funcao_usuario.unidade:
            # Buscar TODAS as subunidades da unidade seguindo o organograma
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade, ativo=True)
            
            # Retornar organizações em ordem hierárquica (mais alto para mais baixo)
            organizacoes = []
            
            # 1. Unidade (mais alto)
            organizacoes.append(funcao_usuario.unidade.nome)
            
            # 2. Subunidades (mais baixo)
            for s in subunidades.order_by('nome'):
                organizacoes.append(s.nome)
            
            return organizacoes
        
        return []
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade da lotação
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            # Retornar apenas a subunidade (única opção)
            return [funcao_usuario.sub_unidade.nome]
        
        return []
    
    return []


def obter_organizacoes_para_criacao_escalas(funcao_usuario, user=None):
    """
    Obtém as organizações disponíveis para criação de escalas baseado na estrutura hierárquica.
    
    Diferente de obter_opcoes_filtro_hierarquico_escalas, esta função retorna TODAS as organizações
    disponíveis baseadas na estrutura hierárquica, não apenas as que já existem em escalas.
    
    Args:
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        list: Lista de organizações disponíveis para criação de escalas
    """
    from .models import Militar, Lotacao, Orgao, GrandeComando, Unidade, SubUnidade
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        organizacoes = []
        # Adicionar órgãos
        for orgao in Orgao.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(orgao.nome)
        # Adicionar grandes comandos
        for gc in GrandeComando.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(gc.nome)
        # Adicionar unidades
        for u in Unidade.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(u.nome)
        # Adicionar subunidades
        for s in SubUnidade.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(s.nome)
        return organizacoes
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return []
    
    funcao_militar = funcao_usuario.funcao_militar
    organizacoes = []
    
    # TIPO DE ACESSO = TOTAL: Acesso total
    if funcao_militar.acesso == 'TOTAL':
        # Adicionar órgãos
        for orgao in Orgao.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(orgao.nome)
        # Adicionar grandes comandos
        for gc in GrandeComando.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(gc.nome)
        # Adicionar unidades
        for u in Unidade.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(u.nome)
        # Adicionar subunidades
        for s in SubUnidade.objects.filter(ativo=True).order_by('nome'):
            organizacoes.append(s.nome)
        return organizacoes
    
    # TIPO DE ACESSO = NENHUM: Sem acesso para criar escalas
    elif funcao_militar.acesso == 'NENHUM':
        return []
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_funcao = Lotacao.objects.filter(
                militar=militar,
                ativo=True
            ).select_related('orgao', 'grande_comando', 'unidade').first()
            
            # Buscar o órgão da lotação (pode ser direto ou através da hierarquia)
            orgao = None
            if lotacao_funcao and lotacao_funcao.orgao:
                orgao = lotacao_funcao.orgao
            elif lotacao_funcao and lotacao_funcao.grande_comando and lotacao_funcao.grande_comando.orgao:
                orgao = lotacao_funcao.grande_comando.orgao
            elif lotacao_funcao and lotacao_funcao.unidade and lotacao_funcao.unidade.grande_comando and lotacao_funcao.unidade.grande_comando.orgao:
                orgao = lotacao_funcao.unidade.grande_comando.orgao
            
            if orgao:
                # Adicionar órgão
                organizacoes.append(orgao.nome)
                
                # Buscar TODAS as descendências do órgão
                grandes_comandos = GrandeComando.objects.filter(orgao=orgao, ativo=True)
                unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
                subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
                
                # Adicionar grandes comandos
                for gc in grandes_comandos:
                    organizacoes.append(gc.nome)
                
                # Adicionar unidades
                for u in unidades:
                    organizacoes.append(u.nome)
                
                # Adicionar subunidades
                for s in subunidades:
                    organizacoes.append(s.nome)
                
                return sorted(organizacoes)
            
            return []
        except Militar.DoesNotExist:
            return []
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_funcao = Lotacao.objects.filter(
                militar=militar,
                ativo=True
            ).select_related('grande_comando', 'unidade').first()
            
            # Buscar o grande comando da lotação (pode ser direto ou através da unidade)
            grande_comando = None
            if lotacao_funcao and lotacao_funcao.grande_comando:
                grande_comando = lotacao_funcao.grande_comando
            elif lotacao_funcao and lotacao_funcao.unidade and lotacao_funcao.unidade.grande_comando:
                grande_comando = lotacao_funcao.unidade.grande_comando
            
            if grande_comando:
                # Adicionar grande comando
                organizacoes.append(grande_comando.nome)
                
                # Buscar TODAS as descendências do grande comando
                unidades = Unidade.objects.filter(grande_comando=grande_comando, ativo=True)
                subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
                
                # Adicionar unidades
                for u in unidades:
                    organizacoes.append(u.nome)
                
                # Adicionar subunidades
                for s in subunidades:
                    organizacoes.append(s.nome)
                
                return sorted(organizacoes)
            
            return []
        except Militar.DoesNotExist:
            return []
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_funcao = Lotacao.objects.filter(
                militar=militar,
                ativo=True
            ).select_related('unidade').first()
            
            if lotacao_funcao and lotacao_funcao.unidade:
                # Adicionar unidade
                organizacoes.append(lotacao_funcao.unidade.nome)
                
                # Buscar TODAS as subunidades da unidade
                subunidades = SubUnidade.objects.filter(unidade=lotacao_funcao.unidade, ativo=True)
                
                # Adicionar subunidades
                for s in subunidades:
                    organizacoes.append(s.nome)
                
                return sorted(organizacoes)
            
            return []
        except Militar.DoesNotExist:
            return []
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade da lotação
    elif funcao_militar.acesso == 'SUBUNIDADE':
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_funcao = Lotacao.objects.filter(
                militar=militar,
                ativo=True
            ).select_related('sub_unidade').first()
            
            if lotacao_funcao and lotacao_funcao.sub_unidade:
                # Adicionar apenas a subunidade
                organizacoes.append(lotacao_funcao.sub_unidade.nome)
                return organizacoes
            
            return []
        except Militar.DoesNotExist:
            return []
    
    return []


def aplicar_filtro_hierarquico_publicacoes(queryset, funcao_usuario, user=None, tipo_publicacao=None):
    """
    Aplica filtro hierárquico para publicações baseado no tipo de acesso da função militar.
    
    Args:
        queryset: QuerySet de Publicacao para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        tipo_publicacao: Tipo específico de publicação (opcional)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        if tipo_publicacao:
            return queryset.filter(tipo=tipo_publicacao, ativo=True)
        return queryset.filter(ativo=True)
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Usar apenas os dados da função militar, não do usuário
    if funcao_militar.acesso == 'TOTAL':
        # Acesso total - mostrar todas as publicações
        if tipo_publicacao:
            return queryset.filter(tipo=tipo_publicacao, ativo=True)
        return queryset.filter(ativo=True)
        
    elif funcao_militar.acesso == 'NENHUM':
        # Sem acesso - mostrar apenas publicações do próprio usuário
        if tipo_publicacao:
            return queryset.filter(
                tipo=tipo_publicacao,
                ativo=True,
                criado_por=funcao_usuario.usuario
            )
        return queryset.filter(
            ativo=True,
            criado_por=funcao_usuario.usuario
        )
        
    elif funcao_militar.acesso == 'ORGAO':
        # Acesso ao órgão - baseado na lotação real do militar
        from .models import Militar, Lotacao
        
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_funcao = Lotacao.objects.filter(
                militar=militar,
                ativo=True
            ).select_related('orgao').first()
            
            if lotacao_funcao and lotacao_funcao.orgao:
                # Filtrar APENAS pelo órgão da lotação (nível mais alto)
                filtro_base = Q(ativo=True) & (
                    Q(origem_publicacao__icontains=lotacao_funcao.orgao.nome) |
                    Q(origem_publicacao__icontains=lotacao_funcao.orgao.sigla)
                )
                if tipo_publicacao:
                    filtro_base &= Q(tipo=tipo_publicacao)
                return queryset.filter(filtro_base).distinct()
            
            return queryset.none()
        except Militar.DoesNotExist:
            return queryset.none()
            
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        # Acesso ao grande comando - filtrar por grande comando e TODA sua descendência
        grande_comando_usuario = None
        
        # Determinar o grande comando do usuário
        if funcao_usuario.grande_comando:
            grande_comando_usuario = funcao_usuario.grande_comando
        elif funcao_usuario.unidade:
            grande_comando_usuario = funcao_usuario.unidade.grande_comando
        elif funcao_usuario.sub_unidade:
            grande_comando_usuario = funcao_usuario.sub_unidade.unidade.grande_comando
        
        if grande_comando_usuario:
            from .models import Unidade, SubUnidade
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando=grande_comando_usuario, ativo=True)
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
            
            # Filtrar por origem_publicacao contendo o grande comando ou suas unidades/subunidades
            filtro_base = Q(ativo=True) & (
                Q(origem_publicacao__icontains=grande_comando_usuario.nome) |
                Q(origem_publicacao__icontains=grande_comando_usuario.sigla)
            )
            
            # Adicionar filtros para unidades
            for u in unidades:
                filtro_base |= Q(origem_publicacao__icontains=u.nome)
                filtro_base |= Q(origem_publicacao__icontains=u.sigla)
            
            # Adicionar filtros para subunidades
            for s in subunidades:
                filtro_base |= Q(origem_publicacao__icontains=s.nome)
                filtro_base |= Q(origem_publicacao__icontains=s.sigla)
            
            if tipo_publicacao:
                filtro_base &= Q(tipo=tipo_publicacao)
            return queryset.filter(filtro_base).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'UNIDADE':
        # Acesso à unidade - filtrar por unidade e TODAS suas subunidades
        if funcao_usuario.unidade:
            from .models import SubUnidade
            subunidades = SubUnidade.objects.filter(unidade=funcao_usuario.unidade)
            
            # Filtrar por origem_publicacao contendo a unidade ou suas subunidades
            filtro_base = Q(ativo=True) & (
                Q(origem_publicacao__icontains=funcao_usuario.unidade.nome) |
                Q(origem_publicacao__icontains=funcao_usuario.unidade.sigla) |
                Q(origem_publicacao__in=[s.nome for s in subunidades]) |
                Q(origem_publicacao__in=[s.sigla for s in subunidades])
            )
            if tipo_publicacao:
                filtro_base &= Q(tipo=tipo_publicacao)
            return queryset.filter(filtro_base).distinct()
        else:
            return queryset.none()
            
    elif funcao_militar.acesso == 'SUBUNIDADE':
        # Acesso à subunidade - filtrar apenas por subunidade
        if funcao_usuario.sub_unidade:
            # Filtrar por origem_publicacao contendo a subunidade
            filtro_base = Q(ativo=True) & (
                Q(origem_publicacao__icontains=funcao_usuario.sub_unidade.nome) |
                Q(origem_publicacao__icontains=funcao_usuario.sub_unidade.sigla)
            )
            if tipo_publicacao:
                filtro_base &= Q(tipo=tipo_publicacao)
            return queryset.filter(filtro_base).distinct()
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
        # Acesso ao órgão - baseado na lotação real do militar
        from .models import Militar, Lotacao
        
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_funcao = Lotacao.objects.filter(
                militar=militar,
                ativo=True
            ).select_related('orgao').first()
            
            if lotacao_funcao and lotacao_funcao.orgao:
                # Filtrar APENAS pelo órgão da lotação (nível mais alto)
                return queryset.filter(
                    militar__lotacoes__orgao=lotacao_funcao.orgao,
                    militar__lotacoes__status='ATUAL',
                    militar__lotacoes__ativo=True
                ).distinct()
            
            return queryset.none()
        except Militar.DoesNotExist:
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
        # Acesso ao órgão - baseado na lotação real do militar
        from .models import Militar, Lotacao
        
        try:
            militar = Militar.objects.get(user=funcao_usuario.usuario)
            lotacao_funcao = Lotacao.objects.filter(
                militar=militar,
                ativo=True
            ).select_related('orgao').first()
            
            if lotacao_funcao and lotacao_funcao.orgao:
                # Filtrar APENAS pelo órgão da lotação (nível mais alto)
                return queryset.filter(
                    militar__lotacoes__orgao=lotacao_funcao.orgao,
                    militar__lotacoes__status='ATUAL',
                    militar__lotacoes__ativo=True
                ).distinct()
            
            return queryset.none()
        except Militar.DoesNotExist:
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


def aplicar_filtro_hierarquico_processos(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para processos administrativos baseado no tipo de acesso da função militar.
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da organização
    - ORGAO: Acesso ao órgão + TODAS suas descendências (grandes comandos, unidades, subunidades)
    - GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências (unidades, subunidades)
    - UNIDADE: Acesso à unidade + TODAS suas subunidades
    - SUBUNIDADE: Acesso apenas à subunidade específica
    - NENHUM: Sem acesso
    
    Args:
        queryset: QuerySet de ProcessoAdministrativo para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da organização
    if funcao_militar.acesso == 'TOTAL':
        return queryset
    
    # TIPO DE ACESSO = NENHUM: Sem acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            from .models import GrandeComando, Unidade, SubUnidade
            
            orgao_id = funcao_usuario.orgao.id
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao_id=orgao_id, ativo=True)
            gc_ids = list(grandes_comandos.values_list('id', flat=True))
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando_id__in=gc_ids, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para toda a hierarquia
            filtro_hierarquia = Q(orgao_id=orgao_id)
            
            if gc_ids:
                filtro_hierarquia |= Q(grande_comando_id__in=gc_ids)
            if unidade_ids:
                filtro_hierarquia |= Q(unidade_id__in=unidade_ids)
            if subunidade_ids:
                filtro_hierarquia |= Q(sub_unidade_id__in=subunidade_ids)
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            from .models import Unidade, SubUnidade
            
            gc_id = funcao_usuario.grande_comando.id
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando_id=gc_id, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para grande comando e suas descendências
            filtro_hierarquia = Q(grande_comando_id=gc_id)
            
            if unidade_ids:
                filtro_hierarquia |= Q(unidade_id__in=unidade_ids)
            if subunidade_ids:
                filtro_hierarquia |= Q(sub_unidade_id__in=subunidade_ids)
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            from .models import SubUnidade
            
            unidade_id = funcao_usuario.unidade.id
            
            # Buscar todas as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade_id=unidade_id, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para unidade e suas subunidades
            filtro_hierarquia = Q(unidade_id=unidade_id)
            
            if subunidade_ids:
                filtro_hierarquia |= Q(sub_unidade_id__in=subunidade_ids)
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            return queryset.filter(sub_unidade_id=funcao_usuario.sub_unidade.id)
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_entradas_almoxarifado(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para entradas do almoxarifado baseado no tipo de acesso da função militar.
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da organização
    - ORGAO: Acesso ao órgão + TODAS suas descendências (grandes comandos, unidades, subunidades)
    - GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências (unidades, subunidades)
    - UNIDADE: Acesso à unidade + TODAS suas subunidades
    - SUBUNIDADE: Acesso apenas à subunidade específica
    - NENHUM: Sem acesso
    
    Args:
        queryset: QuerySet de EntradaAlmoxarifado para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da organização
    if funcao_militar.acesso == 'TOTAL':
        return queryset
    
    # TIPO DE ACESSO = NENHUM: Sem acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            from .models import GrandeComando, Unidade, SubUnidade
            
            orgao_id = funcao_usuario.orgao.id
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao_id=orgao_id, ativo=True)
            gc_ids = list(grandes_comandos.values_list('id', flat=True))
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando_id__in=gc_ids, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para toda a hierarquia
            # Para transferências: verificar origem (de onde veio) E destino (onde está agora)
            # Para outras entradas: verificar origem ou item na hierarquia
            filtro_hierarquia = Q()
            
            # Filtro para origem (de onde veio - para transferências recebidas)
            # Incluir a instância principal (órgão) + todas as descendências
            filtro_origem = Q(orgao_origem_id=orgao_id)  # Instância principal
            if gc_ids:
                filtro_origem |= Q(grande_comando_origem_id__in=gc_ids)  # Descendências
            if unidade_ids:
                filtro_origem |= Q(unidade_origem_id__in=unidade_ids)  # Descendências
            if subunidade_ids:
                filtro_origem |= Q(sub_unidade_origem_id__in=subunidade_ids)  # Descendências
            
            # Filtro para destino (onde o produto está agora - para transferências enviadas e outras entradas)
            # Incluir a instância principal (órgão) + todas as descendências
            filtro_destino = Q(produto__orgao_id=orgao_id)  # Instância principal
            if gc_ids:
                filtro_destino |= Q(produto__grande_comando_id__in=gc_ids)  # Descendências
            if unidade_ids:
                filtro_destino |= Q(produto__unidade_id__in=unidade_ids)  # Descendências
            if subunidade_ids:
                filtro_destino |= Q(produto__sub_unidade_id__in=subunidade_ids)  # Descendências
            
            # Para transferências: verificar origem (recebidas) OU destino (enviadas)
            # Transferências recebidas: origem está na hierarquia (material chegou aqui)
            # Transferências enviadas: destino está na hierarquia (material foi enviado daqui)
            # Outras entradas: item está na hierarquia OU criado pelo usuário
            filtro_hierarquia = Q()
            
            # Para transferências: verificar origem OU destino
            filtro_transferencias = Q(tipo_entrada='TRANSFERENCIA') & (filtro_origem | filtro_destino)
            
            # Para outras entradas: verificar destino (onde o item está) OU criado pelo usuário
            filtro_outras_entradas = ~Q(tipo_entrada='TRANSFERENCIA') & (filtro_destino | Q(criado_por=user) if user else filtro_destino)
            
            # Combinar tudo
            filtro_hierarquia = filtro_transferencias | filtro_outras_entradas
            
            # Incluir também entradas criadas pelo usuário atual (para todos os tipos)
            if user:
                filtro_hierarquia |= Q(criado_por=user)
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            from .models import Unidade, SubUnidade
            
            gc_id = funcao_usuario.grande_comando.id
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando_id=gc_id, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para grande comando e suas descendências
            # Para transferências: verificar origem (de onde veio) E destino (onde está agora)
            filtro_hierarquia = Q()
            
            # Filtro para origem (de onde veio - para transferências recebidas)
            # Incluir a instância principal (grande comando) + todas as descendências
            filtro_origem = Q(grande_comando_origem_id=gc_id)  # Instância principal
            if unidade_ids:
                filtro_origem |= Q(unidade_origem_id__in=unidade_ids)  # Descendências
            if subunidade_ids:
                filtro_origem |= Q(sub_unidade_origem_id__in=subunidade_ids)  # Descendências
            
            # Filtro para destino (onde o produto está agora - para transferências enviadas e outras entradas)
            # Incluir a instância principal (grande comando) + todas as descendências
            filtro_destino = Q(produto__grande_comando_id=gc_id)  # Instância principal
            if unidade_ids:
                filtro_destino |= Q(produto__unidade_id__in=unidade_ids)  # Descendências
            if subunidade_ids:
                filtro_destino |= Q(produto__sub_unidade_id__in=subunidade_ids)  # Descendências
            
            # Para transferências: verificar origem (recebidas) OU destino (enviadas)
            filtro_transferencias = Q(tipo_entrada='TRANSFERENCIA') & (filtro_origem | filtro_destino)
            
            # Para outras entradas: verificar destino (onde o item está) OU criado pelo usuário
            filtro_outras_entradas = ~Q(tipo_entrada='TRANSFERENCIA') & (filtro_destino | Q(criado_por=user) if user else filtro_destino)
            
            # Combinar tudo
            filtro_hierarquia = filtro_transferencias | filtro_outras_entradas
            
            # Incluir também entradas criadas pelo usuário atual (para todos os tipos)
            if user:
                filtro_hierarquia |= Q(criado_por=user)
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            from .models import SubUnidade
            
            unidade_id = funcao_usuario.unidade.id
            
            # Buscar todas as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade_id=unidade_id, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para unidade e suas subunidades
            # Para transferências: verificar origem (de onde veio) E destino (onde está agora)
            filtro_hierarquia = Q()
            
            # Filtro para origem (de onde veio - para transferências recebidas)
            # Incluir a instância principal (unidade) + todas as descendências
            filtro_origem = Q(unidade_origem_id=unidade_id)  # Instância principal
            if subunidade_ids:
                filtro_origem |= Q(sub_unidade_origem_id__in=subunidade_ids)  # Descendências
            
            # Filtro para destino (onde o produto está agora - para transferências enviadas e outras entradas)
            # Incluir a instância principal (unidade) + todas as descendências
            filtro_destino = Q(produto__unidade_id=unidade_id)  # Instância principal
            if subunidade_ids:
                filtro_destino |= Q(produto__sub_unidade_id__in=subunidade_ids)  # Descendências
            
            # Para transferências: verificar origem (recebidas) OU destino (enviadas)
            filtro_transferencias = Q(tipo_entrada='TRANSFERENCIA') & (filtro_origem | filtro_destino)
            
            # Para outras entradas: verificar destino (onde o item está) OU criado pelo usuário
            filtro_outras_entradas = ~Q(tipo_entrada='TRANSFERENCIA') & (filtro_destino | Q(criado_por=user) if user else filtro_destino)
            
            # Combinar tudo
            filtro_hierarquia = filtro_transferencias | filtro_outras_entradas
            
            # Incluir também entradas criadas pelo usuário atual (para todos os tipos)
            if user:
                filtro_hierarquia |= Q(criado_por=user)
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            subunidade_id = funcao_usuario.sub_unidade.id
            
            # Filtro para origem (transferências recebidas)
            filtro_origem = Q(sub_unidade_origem_id=subunidade_id)
            
            # Filtro para destino (transferências enviadas e outras entradas)
            filtro_destino = Q(produto__sub_unidade_id=subunidade_id)
            
            # Para transferências: verificar origem (recebidas) OU destino (enviadas)
            filtro_transferencias = Q(tipo_entrada='TRANSFERENCIA') & (filtro_origem | filtro_destino)
            
            # Para outras entradas: verificar destino (onde o item está) OU criado pelo usuário
            filtro_outras_entradas = ~Q(tipo_entrada='TRANSFERENCIA') & (filtro_destino | Q(criado_por=user) if user else filtro_destino)
            
            # Combinar tudo
            filtro_hierarquia = filtro_transferencias | filtro_outras_entradas
            
            # Incluir também entradas criadas pelo usuário atual (para todos os tipos)
            if user:
                filtro_hierarquia |= Q(criado_por=user)
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_saidas_almoxarifado(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para saídas do almoxarifado baseado no tipo de acesso da função militar.
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da organização
    - ORGAO: Acesso ao órgão + TODAS suas descendências (grandes comandos, unidades, subunidades)
    - GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências (unidades, subunidades)
    - UNIDADE: Acesso à unidade + TODAS suas subunidades
    - SUBUNIDADE: Acesso apenas à subunidade específica
    - NENHUM: Sem acesso
    
    Args:
        queryset: QuerySet de SaidaAlmoxarifado para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da organização
    if funcao_militar.acesso == 'TOTAL':
        return queryset
    
    # TIPO DE ACESSO = NENHUM: Sem acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            from .models import GrandeComando, Unidade, SubUnidade
            
            orgao_id = funcao_usuario.orgao.id
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao_id=orgao_id, ativo=True)
            gc_ids = list(grandes_comandos.values_list('id', flat=True))
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando_id__in=gc_ids, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para toda a hierarquia (ORIGEM - de onde saiu)
            # Para transferências: verificar a OM requisitada na requisição OU campos de origem
            # Para outras saídas: verificar campos de origem OU OM do criador
            filtro_hierarquia = Q()
            
            # Filtro para origem (campos de origem da saída)
            filtro_origem = Q(orgao_origem_id=orgao_id)  # Instância principal
            if gc_ids:
                filtro_origem |= Q(grande_comando_origem_id__in=gc_ids)  # Descendências
            if unidade_ids:
                filtro_origem |= Q(unidade_origem_id__in=unidade_ids)  # Descendências
            if subunidade_ids:
                filtro_origem |= Q(sub_unidade_origem_id__in=subunidade_ids)  # Descendências
            
            # Filtro para transferências (via requisição OU campos de origem)
            filtro_transferencias = Q(tipo_saida='TRANSFERENCIA')
            filtro_transferencias_requisicao = (
                Q(requisicao_origem__orgao_requisitada_id=orgao_id) |
                Q(requisicao_origem__grande_comando_requisitada_id__in=gc_ids) |
                Q(requisicao_origem__unidade_requisitada_id__in=unidade_ids) |
                Q(requisicao_origem__sub_unidade_requisitada_id__in=subunidade_ids)
            )
            filtro_transferencias &= (filtro_origem | filtro_transferencias_requisicao)
            
            # Filtro para outras saídas (campos de origem OU criador)
            # Buscar usuários que pertencem à hierarquia
            from django.contrib.auth.models import User
            from .permissoes_militares import UsuarioFuncaoMilitar
            
            usuarios_hierarquia = UsuarioFuncaoMilitar.objects.filter(
                Q(orgao_id=orgao_id) |
                Q(grande_comando_id__in=gc_ids) |
                Q(unidade_id__in=unidade_ids) |
                Q(sub_unidade_id__in=subunidade_ids),
                ativo=True
            ).values_list('usuario_id', flat=True).distinct()
            
            filtro_outras_saidas = ~Q(tipo_saida='TRANSFERENCIA')
            filtro_outras_saidas_origem = filtro_origem
            if usuarios_hierarquia:
                filtro_outras_saidas_origem |= Q(criado_por_id__in=usuarios_hierarquia)
            filtro_outras_saidas &= filtro_outras_saidas_origem
            
            filtro_hierarquia = filtro_transferencias | filtro_outras_saidas
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            from .models import Unidade, SubUnidade
            
            gc_id = funcao_usuario.grande_comando.id
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando_id=gc_id, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para grande comando e suas descendências (ORIGEM - de onde saiu)
            filtro_hierarquia = Q()
            
            # Filtro para origem (campos de origem da saída)
            filtro_origem = Q(grande_comando_origem_id=gc_id)  # Instância principal
            if unidade_ids:
                filtro_origem |= Q(unidade_origem_id__in=unidade_ids)  # Descendências
            if subunidade_ids:
                filtro_origem |= Q(sub_unidade_origem_id__in=subunidade_ids)  # Descendências
            
            # Filtro para transferências (via requisição OU campos de origem)
            filtro_transferencias = Q(tipo_saida='TRANSFERENCIA')
            filtro_transferencias_requisicao = (
                Q(requisicao_origem__grande_comando_requisitada_id=gc_id) |
                Q(requisicao_origem__unidade_requisitada_id__in=unidade_ids) |
                Q(requisicao_origem__sub_unidade_requisitada_id__in=subunidade_ids)
            )
            filtro_transferencias &= (filtro_origem | filtro_transferencias_requisicao)
            
            # Filtro para outras saídas (campos de origem OU criador)
            from django.contrib.auth.models import User
            from .permissoes_militares import UsuarioFuncaoMilitar
            
            usuarios_hierarquia = UsuarioFuncaoMilitar.objects.filter(
                Q(grande_comando_id=gc_id) |
                Q(unidade_id__in=unidade_ids) |
                Q(sub_unidade_id__in=subunidade_ids),
                ativo=True
            ).values_list('usuario_id', flat=True).distinct()
            
            filtro_outras_saidas = ~Q(tipo_saida='TRANSFERENCIA')
            filtro_outras_saidas_origem = filtro_origem
            if usuarios_hierarquia:
                filtro_outras_saidas_origem |= Q(criado_por_id__in=usuarios_hierarquia)
            filtro_outras_saidas &= filtro_outras_saidas_origem
            
            filtro_hierarquia = filtro_transferencias | filtro_outras_saidas
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            from .models import SubUnidade
            
            unidade_id = funcao_usuario.unidade.id
            
            # Buscar todas as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade_id=unidade_id, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Criar filtro para unidade e suas subunidades (ORIGEM - de onde saiu)
            filtro_hierarquia = Q()
            
            # Filtro para origem (campos de origem da saída)
            filtro_origem = Q(unidade_origem_id=unidade_id)  # Instância principal
            if subunidade_ids:
                filtro_origem |= Q(sub_unidade_origem_id__in=subunidade_ids)  # Descendências
            
            # Filtro para transferências (via requisição OU campos de origem)
            filtro_transferencias = Q(tipo_saida='TRANSFERENCIA')
            filtro_transferencias_requisicao = (
                Q(requisicao_origem__unidade_requisitada_id=unidade_id) |
                Q(requisicao_origem__sub_unidade_requisitada_id__in=subunidade_ids)
            )
            filtro_transferencias &= (filtro_origem | filtro_transferencias_requisicao)
            
            # Filtro para outras saídas (campos de origem OU criador)
            from django.contrib.auth.models import User
            from .permissoes_militares import UsuarioFuncaoMilitar
            
            usuarios_hierarquia = UsuarioFuncaoMilitar.objects.filter(
                Q(unidade_id=unidade_id) |
                Q(sub_unidade_id__in=subunidade_ids),
                ativo=True
            ).values_list('usuario_id', flat=True).distinct()
            
            filtro_outras_saidas = ~Q(tipo_saida='TRANSFERENCIA')
            filtro_outras_saidas_origem = filtro_origem
            if usuarios_hierarquia:
                filtro_outras_saidas_origem |= Q(criado_por_id__in=usuarios_hierarquia)
            filtro_outras_saidas &= filtro_outras_saidas_origem
            
            filtro_hierarquia = filtro_transferencias | filtro_outras_saidas
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            subunidade_id = funcao_usuario.sub_unidade.id
            
            # Criar filtro para subunidade (ORIGEM - de onde saiu)
            filtro_hierarquia = Q()
            
            # Filtro para origem (campos de origem da saída)
            filtro_origem = Q(sub_unidade_origem_id=subunidade_id)
            
            # Filtro para transferências (via requisição OU campos de origem)
            filtro_transferencias = Q(tipo_saida='TRANSFERENCIA')
            filtro_transferencias_requisicao = Q(requisicao_origem__sub_unidade_requisitada_id=subunidade_id)
            filtro_transferencias &= (filtro_origem | filtro_transferencias_requisicao)
            
            # Filtro para outras saídas (campos de origem OU criador)
            from django.contrib.auth.models import User
            from .permissoes_militares import UsuarioFuncaoMilitar
            
            usuarios_hierarquia = UsuarioFuncaoMilitar.objects.filter(
                sub_unidade_id=subunidade_id,
                ativo=True
            ).values_list('usuario_id', flat=True).distinct()
            
            filtro_outras_saidas = ~Q(tipo_saida='TRANSFERENCIA')
            filtro_outras_saidas_origem = filtro_origem
            if usuarios_hierarquia:
                filtro_outras_saidas_origem |= Q(criado_por_id__in=usuarios_hierarquia)
            filtro_outras_saidas &= filtro_outras_saidas_origem
            
            filtro_hierarquia = filtro_transferencias | filtro_outras_saidas
            
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_itens_almoxarifado(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para itens do almoxarifado baseado no tipo de acesso da função militar.
    Filtra produtos pela OM (Organização Militar) onde foram criados OU onde têm estoque através de entradas/transferências.
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da organização
    - ORGAO: Acesso a produtos do órgão + TODAS suas descendências (grandes comandos, unidades, subunidades)
    - GRANDE_COMANDO: Acesso a produtos do grande comando + TODAS suas descendências (unidades, subunidades)
    - UNIDADE: Acesso a produtos da unidade + TODAS suas subunidades
    - SUBUNIDADE: Acesso a produtos da subunidade específica
    - NENHUM: Sem acesso
    
    IMPORTANTE: Um produto pode ter estoque em múltiplas OMs através de transferências e entradas.
    O filtro considera tanto produtos criados na hierarquia quanto produtos que têm estoque em OMs da hierarquia.
    
    Args:
        queryset: QuerySet de ProdutoAlmoxarifado para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # Verificar se a tabela de múltiplos produtos existe
    from django.db import connection, ProgrammingError
    tabela_entrada_produto_existe = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'militares_entradaalmoxarifadoproduto'
                );
            """)
            tabela_entrada_produto_existe = cursor.fetchone()[0]
    except (ProgrammingError, Exception):
        tabela_entrada_produto_existe = False
    
    # Função auxiliar para criar filtro de hierarquia de OMs
    def criar_filtro_hierarquia_om(orgao_id=None, gc_id=None, unidade_id=None, subunidade_id=None):
        """Cria filtro Q para hierarquia de OMs"""
        filtro = Q()
        
        if orgao_id:
            from .models import GrandeComando, Unidade, SubUnidade
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao_id=orgao_id, ativo=True)
            gc_ids = list(grandes_comandos.values_list('id', flat=True))
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando_id__in=gc_ids, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Filtro para OM de criação do produto
            filtro_om_criacao = Q(orgao_id=orgao_id)
            if gc_ids:
                filtro_om_criacao |= Q(grande_comando_id__in=gc_ids)
            if unidade_ids:
                filtro_om_criacao |= Q(unidade_id__in=unidade_ids)
            if subunidade_ids:
                filtro_om_criacao |= Q(sub_unidade_id__in=subunidade_ids)
            
            # Filtro para entradas (estoque) em OMs da hierarquia
            # Entradas legadas (produto direto)
            filtro_entradas_legadas = Q(
                entradas__orgao_destino_id=orgao_id,
                entradas__ativo=True
            )
            if gc_ids:
                filtro_entradas_legadas |= Q(entradas__grande_comando_destino_id__in=gc_ids, entradas__ativo=True)
            if unidade_ids:
                filtro_entradas_legadas |= Q(entradas__unidade_destino_id__in=unidade_ids, entradas__ativo=True)
            if subunidade_ids:
                filtro_entradas_legadas |= Q(entradas__sub_unidade_destino_id__in=subunidade_ids, entradas__ativo=True)
            
            # Entradas via produtos_entrada (múltiplos produtos) - apenas se a tabela existir
            filtro_entradas_produtos = Q()
            if tabela_entrada_produto_existe:
                filtro_entradas_produtos = Q(
                    entradas_produtos__entrada__orgao_destino_id=orgao_id,
                    entradas_produtos__entrada__ativo=True
                )
                if gc_ids:
                    filtro_entradas_produtos |= Q(entradas_produtos__entrada__grande_comando_destino_id__in=gc_ids, entradas_produtos__entrada__ativo=True)
                if unidade_ids:
                    filtro_entradas_produtos |= Q(entradas_produtos__entrada__unidade_destino_id__in=unidade_ids, entradas_produtos__entrada__ativo=True)
                if subunidade_ids:
                    filtro_entradas_produtos |= Q(entradas_produtos__entrada__sub_unidade_destino_id__in=subunidade_ids, entradas_produtos__entrada__ativo=True)
            
            # Combinar: produto criado na hierarquia OU tem estoque (entradas) na hierarquia
            filtro = filtro_om_criacao | filtro_entradas_legadas
            if tabela_entrada_produto_existe:
                filtro |= filtro_entradas_produtos
            
        elif gc_id:
            from .models import Unidade, SubUnidade
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando_id=gc_id, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Filtro para OM de criação do produto
            filtro_om_criacao = Q(grande_comando_id=gc_id)
            if unidade_ids:
                filtro_om_criacao |= Q(unidade_id__in=unidade_ids)
            if subunidade_ids:
                filtro_om_criacao |= Q(sub_unidade_id__in=subunidade_ids)
            
            # Filtro para entradas (estoque) em OMs da hierarquia
            filtro_entradas_legadas = Q(
                entradas__grande_comando_destino_id=gc_id,
                entradas__ativo=True
            )
            if unidade_ids:
                filtro_entradas_legadas |= Q(entradas__unidade_destino_id__in=unidade_ids, entradas__ativo=True)
            if subunidade_ids:
                filtro_entradas_legadas |= Q(entradas__sub_unidade_destino_id__in=subunidade_ids, entradas__ativo=True)
            
            # Entradas via produtos_entrada (múltiplos produtos) - apenas se a tabela existir
            filtro_entradas_produtos = Q()
            if tabela_entrada_produto_existe:
                filtro_entradas_produtos = Q(
                    entradas_produtos__entrada__grande_comando_destino_id=gc_id,
                    entradas_produtos__entrada__ativo=True
                )
                if unidade_ids:
                    filtro_entradas_produtos |= Q(entradas_produtos__entrada__unidade_destino_id__in=unidade_ids, entradas_produtos__entrada__ativo=True)
                if subunidade_ids:
                    filtro_entradas_produtos |= Q(entradas_produtos__entrada__sub_unidade_destino_id__in=subunidade_ids, entradas_produtos__entrada__ativo=True)
            
            filtro = filtro_om_criacao | filtro_entradas_legadas
            if tabela_entrada_produto_existe:
                filtro |= filtro_entradas_produtos
            
        elif unidade_id:
            from .models import SubUnidade
            
            # Buscar todas as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade_id=unidade_id, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Filtro para OM de criação do produto
            filtro_om_criacao = Q(unidade_id=unidade_id)
            if subunidade_ids:
                filtro_om_criacao |= Q(sub_unidade_id__in=subunidade_ids)
            
            # Filtro para entradas (estoque) em OMs da hierarquia
            filtro_entradas_legadas = Q(
                entradas__unidade_destino_id=unidade_id,
                entradas__ativo=True
            )
            if subunidade_ids:
                filtro_entradas_legadas |= Q(entradas__sub_unidade_destino_id__in=subunidade_ids, entradas__ativo=True)
            
            # Entradas via produtos_entrada (múltiplos produtos) - apenas se a tabela existir
            filtro_entradas_produtos = Q()
            if tabela_entrada_produto_existe:
                filtro_entradas_produtos = Q(
                    entradas_produtos__entrada__unidade_destino_id=unidade_id,
                    entradas_produtos__entrada__ativo=True
                )
                if subunidade_ids:
                    filtro_entradas_produtos |= Q(entradas_produtos__entrada__sub_unidade_destino_id__in=subunidade_ids, entradas_produtos__entrada__ativo=True)
            
            filtro = filtro_om_criacao | filtro_entradas_legadas
            if tabela_entrada_produto_existe:
                filtro |= filtro_entradas_produtos
            
        elif subunidade_id:
            # Filtro para OM de criação do produto
            filtro_om_criacao = Q(sub_unidade_id=subunidade_id)
            
            # Filtro para entradas (estoque) na subunidade
            filtro_entradas_legadas = Q(
                entradas__sub_unidade_destino_id=subunidade_id,
                entradas__ativo=True
            )
            
            # Entradas via produtos_entrada (múltiplos produtos) - apenas se a tabela existir
            filtro_entradas_produtos = Q()
            if tabela_entrada_produto_existe:
                filtro_entradas_produtos = Q(
                    entradas_produtos__entrada__sub_unidade_destino_id=subunidade_id,
                    entradas_produtos__entrada__ativo=True
                )
            
            filtro = filtro_om_criacao | filtro_entradas_legadas
            if tabela_entrada_produto_existe:
                filtro |= filtro_entradas_produtos
        
        return filtro
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da organização
    if funcao_militar.acesso == 'TOTAL':
        return queryset
    
    # TIPO DE ACESSO = NENHUM: Sem acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            filtro_hierarquia = criar_filtro_hierarquia_om(orgao_id=funcao_usuario.orgao.id)
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            filtro_hierarquia = criar_filtro_hierarquia_om(gc_id=funcao_usuario.grande_comando.id)
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            filtro_hierarquia = criar_filtro_hierarquia_om(unidade_id=funcao_usuario.unidade.id)
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            filtro_hierarquia = criar_filtro_hierarquia_om(subunidade_id=funcao_usuario.sub_unidade.id)
            return queryset.filter(filtro_hierarquia).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_afastamentos(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para afastamentos baseado na lotação do militar afastado e tipo de acesso da função militar.
    
    A lógica verifica se a lotação atual do militar do afastamento está dentro do escopo permitido
    pelo tipo de acesso da função militar do usuário.
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da organização
    - ORGAO: Acesso ao órgão + TODAS suas descendências (grandes comandos, unidades, subunidades)
    - GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências (unidades, subunidades)
    - UNIDADE: Acesso à unidade + TODAS suas subunidades
    - SUBUNIDADE: Acesso apenas à subunidade específica
    - NENHUM: Sem acesso
    
    Args:
        queryset: QuerySet de Afastamento para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado na lotação do militar afastado e tipo de acesso
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da organização
    if funcao_militar.acesso == 'TOTAL':
        return queryset
    
    # TIPO DE ACESSO = NENHUM: Sem acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            from .models import GrandeComando, Unidade, SubUnidade
            
            orgao_id = funcao_usuario.orgao.id
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao_id=orgao_id, ativo=True)
            gc_ids = list(grandes_comandos.values_list('id', flat=True))
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando_id__in=gc_ids, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Filtrar afastamentos cujo militar tem lotação atual no órgão ou suas descendências
            return queryset.filter(
                Q(militar__lotacoes__orgao_id=orgao_id) |
                Q(militar__lotacoes__grande_comando_id__in=gc_ids) |
                Q(militar__lotacoes__unidade_id__in=unidade_ids) |
                Q(militar__lotacoes__sub_unidade_id__in=subunidade_ids),
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            from .models import Unidade, SubUnidade
            
            gc_id = funcao_usuario.grande_comando.id
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando_id=gc_id, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Filtrar afastamentos cujo militar tem lotação atual no grande comando ou suas descendências
            return queryset.filter(
                Q(militar__lotacoes__grande_comando_id=gc_id) |
                Q(militar__lotacoes__unidade_id__in=unidade_ids) |
                Q(militar__lotacoes__sub_unidade_id__in=subunidade_ids),
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            from .models import SubUnidade
            
            unidade_id = funcao_usuario.unidade.id
            
            # Buscar todas as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade_id=unidade_id, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Filtrar afastamentos cujo militar tem lotação atual na unidade ou suas subunidades
            return queryset.filter(
                Q(militar__lotacoes__unidade_id=unidade_id) |
                Q(militar__lotacoes__sub_unidade_id__in=subunidade_ids),
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            subunidade_id = funcao_usuario.sub_unidade.id
            
            # Filtrar afastamentos cujo militar tem lotação atual na subunidade específica
            return queryset.filter(
                militar__lotacoes__sub_unidade_id=subunidade_id,
                militar__lotacoes__status='ATUAL',
                militar__lotacoes__ativo=True
            ).distinct()
        else:
            return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_ferias(queryset, funcao_usuario, user=None):
    """
    Aplica filtro hierárquico para férias baseado na lotação do militar e tipo de acesso da função militar.
    
    REGRAS DE ACESSO:
    - TOTAL: Acesso total independente da organização
    - ORGAO: Acesso ao órgão + TODAS suas descendências (grandes comandos, unidades, subunidades)
    - GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências (unidades, subunidades)
    - UNIDADE: Acesso à unidade + TODAS suas subunidades
    - SUBUNIDADE: Acesso apenas à subunidade específica
    - NENHUM: Sem acesso
    
    Args:
        queryset: QuerySet de Ferias para filtrar
        funcao_usuario: UsuarioFuncaoMilitar com as informações da função
        user: Usuário atual (para verificar se é superusuário)
        
    Returns:
        QuerySet filtrado baseado no tipo de acesso e lotação do militar
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total independente da organização
    if funcao_militar.acesso == 'TOTAL':
        return queryset
    
    # TIPO DE ACESSO = NENHUM: Sem acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão + TODAS suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            from .models import GrandeComando, Unidade, SubUnidade, Lotacao
            
            orgao_id = funcao_usuario.orgao.id
            
            # Buscar todos os grandes comandos do órgão
            grandes_comandos = GrandeComando.objects.filter(orgao_id=orgao_id, ativo=True)
            gc_ids = list(grandes_comandos.values_list('id', flat=True))
            
            # Buscar todas as unidades dos grandes comandos
            unidades = Unidade.objects.filter(grande_comando_id__in=gc_ids, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Buscar lotações que pertencem ao órgão ou suas descendências
            lotacoes_filtradas = Lotacao.objects.filter(
                Q(orgao_id=orgao_id) |
                Q(grande_comando_id__in=gc_ids) |
                Q(unidade_id__in=unidade_ids) |
                Q(sub_unidade_id__in=subunidade_ids),
                status='ATUAL',
                ativo=True
            )
            
            # Filtrar férias pelos militares que têm essas lotações
            militares_ids = lotacoes_filtradas.values_list('militar_id', flat=True).distinct()
            return queryset.filter(militar_id__in=militares_ids).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando + TODAS suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            from .models import Unidade, SubUnidade, Lotacao
            
            gc_id = funcao_usuario.grande_comando.id
            
            # Buscar todas as unidades do grande comando
            unidades = Unidade.objects.filter(grande_comando_id=gc_id, ativo=True)
            unidade_ids = list(unidades.values_list('id', flat=True))
            
            # Buscar todas as subunidades das unidades
            subunidades = SubUnidade.objects.filter(unidade_id__in=unidade_ids, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Buscar lotações que pertencem ao grande comando ou suas descendências
            lotacoes_filtradas = Lotacao.objects.filter(
                Q(grande_comando_id=gc_id) |
                Q(unidade_id__in=unidade_ids) |
                Q(sub_unidade_id__in=subunidade_ids),
                status='ATUAL',
                ativo=True
            )
            
            # Filtrar férias pelos militares que têm essas lotações
            militares_ids = lotacoes_filtradas.values_list('militar_id', flat=True).distinct()
            return queryset.filter(militar_id__in=militares_ids).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade + TODAS suas subunidades
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            from .models import SubUnidade, Lotacao
            
            unidade_id = funcao_usuario.unidade.id
            
            # Buscar todas as subunidades da unidade
            subunidades = SubUnidade.objects.filter(unidade_id=unidade_id, ativo=True)
            subunidade_ids = list(subunidades.values_list('id', flat=True))
            
            # Buscar lotações que pertencem à unidade ou suas subunidades
            lotacoes_filtradas = Lotacao.objects.filter(
                Q(unidade_id=unidade_id) |
                Q(sub_unidade_id__in=subunidade_ids),
                status='ATUAL',
                ativo=True
            )
            
            # Filtrar férias pelos militares que têm essas lotações
            militares_ids = lotacoes_filtradas.values_list('militar_id', flat=True).distinct()
            return queryset.filter(militar_id__in=militares_ids).distinct()
        else:
            return queryset.none()
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade específica
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            from .models import Lotacao
            
            subunidade_id = funcao_usuario.sub_unidade.id
            
            # Buscar lotações que pertencem à subunidade
            lotacoes_filtradas = Lotacao.objects.filter(
                sub_unidade_id=subunidade_id,
                status='ATUAL',
                ativo=True
            )
            
            # Filtrar férias pelos militares que têm essas lotações
            militares_ids = lotacoes_filtradas.values_list('militar_id', flat=True).distinct()
            return queryset.filter(militar_id__in=militares_ids).distinct()
        else:
            return queryset.none()
    
    return queryset.none()
