#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Filtros hierárquicos para pesquisa de notas - apenas o próprio nível
"""

from django.db.models import Q




def aplicar_filtro_hierarquico_notas_especifico(queryset, funcao_usuario, user, origem_selecionada):
    """
    Aplicar filtro hierárquico específico baseado na origem selecionada no filtro de pesquisa
    """
    from django.db.models import Q
    from .models import Orgao, GrandeComando, Unidade, SubUnidade
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset.filter(tipo='NOTA')
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total a todas as notas
    if funcao_militar.acesso == 'TOTAL':
        return queryset.filter(tipo='NOTA')
        
    # TIPO DE ACESSO = NENHUM: Apenas notas do próprio usuário
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.filter(
            tipo='NOTA',
            criado_por=funcao_usuario.usuario
        )
    
    # Identificar o tipo de item selecionado baseado na origem
    # Formato: "Órgão | Grande Comando | Unidade | Subunidade"
    partes_origem = origem_selecionada.split(' | ')
    
    if len(partes_origem) == 1:
        # Órgão
        try:
            orgao = Orgao.objects.get(nome=partes_origem[0], ativo=True)
            return queryset.filter(tipo='NOTA', origem_publicacao__icontains=orgao.nome)
        except Orgao.DoesNotExist:
            return queryset.none()
    
    elif len(partes_origem) == 2:
        # Grande Comando
        try:
            orgao_nome = partes_origem[0]
            gc_nome = partes_origem[1]
            grande_comando = GrandeComando.objects.get(
                nome=gc_nome, 
                orgao__nome=orgao_nome, 
                ativo=True
            )
            return queryset.filter(tipo='NOTA', origem_publicacao__icontains=origem_selecionada)
        except GrandeComando.DoesNotExist:
            return queryset.none()
    
    elif len(partes_origem) == 3:
        # Unidade
        try:
            orgao_nome = partes_origem[0]
            gc_nome = partes_origem[1]
            unidade_nome = partes_origem[2]
            unidade = Unidade.objects.get(
                nome=unidade_nome,
                grande_comando__nome=gc_nome,
                grande_comando__orgao__nome=orgao_nome,
                ativo=True
            )
            return queryset.filter(tipo='NOTA', origem_publicacao__icontains=origem_selecionada)
        except Unidade.DoesNotExist:
            return queryset.none()
    
    elif len(partes_origem) == 4:
        # Subunidade
        try:
            orgao_nome = partes_origem[0]
            gc_nome = partes_origem[1]
            unidade_nome = partes_origem[2]
            subunidade_nome = partes_origem[3]
            subunidade = SubUnidade.objects.get(
                nome=subunidade_nome,
                unidade__nome=unidade_nome,
                unidade__grande_comando__nome=gc_nome,
                unidade__grande_comando__orgao__nome=orgao_nome,
                ativo=True
            )
            return queryset.filter(tipo='NOTA', origem_publicacao__icontains=origem_selecionada)
        except SubUnidade.DoesNotExist:
            return queryset.none()
    
    # Fallback: buscar por contém
    return queryset.filter(tipo='NOTA', origem_publicacao__icontains=origem_selecionada)


def obter_opcoes_filtro_hierarquico_notas(funcao_usuario, user=None):
    """
    Obtém as opções de filtro hierárquico para notas baseado no acesso da função.
    Cada nível mostra apenas suas próprias opções + descendências para filtro.
    """
    from .models import GrandeComando, Unidade, SubUnidade
    
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
        orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
        
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
        orgao_funcao = funcao_usuario.orgao
        if not orgao_funcao:
            return []
        
        organizacoes = []
        
        # 1. Órgão (próprio nível)
        organizacoes.append({
            'id': f'orgao_{orgao_funcao.id}',
            'nome': orgao_funcao.nome,
            'tipo': 'orgao',
            'nivel': 1
        })
        
        # 2. Grandes comandos (descendências)
        grandes_comandos = GrandeComando.objects.filter(orgao=orgao_funcao, ativo=True)
        for gc in grandes_comandos.order_by('nome'):
            organizacoes.append({
                'id': f'gc_{gc.id}',
                'nome': f"{orgao_funcao.nome} | {gc.nome}",
                'tipo': 'grande_comando',
                'nivel': 2
            })
        
        # 3. Unidades (descendências)
        unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
        for u in unidades.order_by('nome'):
            organizacoes.append({
                'id': f'unidade_{u.id}',
                'nome': f"{orgao_funcao.nome} | {u.grande_comando.nome} | {u.nome}",
                'tipo': 'unidade',
                'nivel': 3
            })
        
        # 4. Subunidades (descendências)
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{orgao_funcao.nome} | {s.unidade.grande_comando.nome} | {s.unidade.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 4
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando da função + suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        grande_comando_funcao = funcao_usuario.grande_comando
        if not grande_comando_funcao:
            return []
        
        organizacoes = []
        
        # 1. Grande comando (próprio nível)
        organizacoes.append({
            'id': f'gc_{grande_comando_funcao.id}',
            'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome}",
            'tipo': 'grande_comando',
            'nivel': 2
        })
        
        # 2. Unidades (descendências)
        unidades = Unidade.objects.filter(grande_comando=grande_comando_funcao, ativo=True)
        for u in unidades.order_by('nome'):
            organizacoes.append({
                'id': f'unidade_{u.id}',
                'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome} | {u.nome}",
                'tipo': 'unidade',
                'nivel': 3
            })
        
        # 3. Subunidades (descendências)
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome} | {s.unidade.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 4
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade da função + suas descendências
    elif funcao_militar.acesso == 'UNIDADE':
        unidade_funcao = funcao_usuario.unidade
        if not unidade_funcao:
            return []
        
        organizacoes = []
        
        # 1. Unidade (próprio nível)
        organizacoes.append({
            'id': f'unidade_{unidade_funcao.id}',
            'nome': f"{unidade_funcao.grande_comando.orgao.nome} | {unidade_funcao.grande_comando.nome} | {unidade_funcao.nome}",
            'tipo': 'unidade',
            'nivel': 3
        })
        
        # 2. Subunidades (descendências)
        subunidades = SubUnidade.objects.filter(unidade=unidade_funcao, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{unidade_funcao.grande_comando.orgao.nome} | {unidade_funcao.grande_comando.nome} | {unidade_funcao.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 4
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade
    elif funcao_militar.acesso == 'SUBUNIDADE':
        subunidade_funcao = funcao_usuario.sub_unidade
        if not subunidade_funcao:
            return []
        
        organizacoes = []
        
        # 1. Subunidade (próprio nível - não tem descendências)
        organizacoes.append({
            'id': f'sub_{subunidade_funcao.id}',
            'nome': f"{subunidade_funcao.unidade.grande_comando.orgao.nome} | {subunidade_funcao.unidade.grande_comando.nome} | {subunidade_funcao.unidade.nome} | {subunidade_funcao.nome}",
            'tipo': 'sub_unidade',
            'nivel': 4
        })
        
        return organizacoes
    
    return []


def obter_opcoes_filtro_hierarquico_itens_almoxarifado(funcao_usuario, user=None):
    """
    Obtém as opções de filtro hierárquico para itens do almoxarifado baseado no acesso da função.
    Cada nível mostra apenas suas próprias opções + descendências para filtro.
    """
    from .models import GrandeComando, Unidade, SubUnidade
    
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
        orgaos = Orgao.objects.filter(ativo=True).order_by('nome')
        
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
    
    # TIPO DE ACESSO = NENHUM: Sem acesso
    elif funcao_militar.acesso == 'NENHUM':
        return []
    
    # TIPO DE ACESSO = ORGAO: Acesso ao órgão da função + todas as suas descendências
    elif funcao_militar.acesso == 'ORGAO':
        orgao_funcao = funcao_usuario.orgao
        if not orgao_funcao:
            return []
        
        organizacoes = []
        
        # 1. Órgão (próprio nível)
        organizacoes.append({
            'id': f'orgao_{orgao_funcao.id}',
            'nome': orgao_funcao.nome,
            'tipo': 'orgao',
            'nivel': 1
        })
        
        # 2. Grandes comandos (descendências)
        grandes_comandos = GrandeComando.objects.filter(orgao=orgao_funcao, ativo=True)
        for gc in grandes_comandos.order_by('nome'):
            organizacoes.append({
                'id': f'gc_{gc.id}',
                'nome': f"{orgao_funcao.nome} | {gc.nome}",
                'tipo': 'grande_comando',
                'nivel': 2
            })
        
        # 3. Unidades (descendências)
        unidades = Unidade.objects.filter(grande_comando__in=grandes_comandos, ativo=True)
        for u in unidades.order_by('nome'):
            organizacoes.append({
                'id': f'unidade_{u.id}',
                'nome': f"{orgao_funcao.nome} | {u.grande_comando.nome} | {u.nome}",
                'tipo': 'unidade',
                'nivel': 3
            })
        
        # 4. Subunidades (descendências)
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{orgao_funcao.nome} | {s.unidade.grande_comando.nome} | {s.unidade.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 4
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso ao grande comando da função + suas descendências
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        grande_comando_funcao = funcao_usuario.grande_comando
        if not grande_comando_funcao:
            return []
        
        organizacoes = []
        
        # 1. Grande comando (próprio nível)
        organizacoes.append({
            'id': f'gc_{grande_comando_funcao.id}',
            'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome}",
            'tipo': 'grande_comando',
            'nivel': 2
        })
        
        # 2. Unidades (descendências)
        unidades = Unidade.objects.filter(grande_comando=grande_comando_funcao, ativo=True)
        for u in unidades.order_by('nome'):
            organizacoes.append({
                'id': f'unidade_{u.id}',
                'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome} | {u.nome}",
                'tipo': 'unidade',
                'nivel': 3
            })
        
        # 3. Subunidades (descendências)
        subunidades = SubUnidade.objects.filter(unidade__in=unidades, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{grande_comando_funcao.orgao.nome} | {grande_comando_funcao.nome} | {s.unidade.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 4
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = UNIDADE: Acesso à unidade da função + suas descendências
    elif funcao_militar.acesso == 'UNIDADE':
        unidade_funcao = funcao_usuario.unidade
        if not unidade_funcao:
            return []
        
        organizacoes = []
        
        # 1. Unidade (próprio nível)
        organizacoes.append({
            'id': f'unidade_{unidade_funcao.id}',
            'nome': f"{unidade_funcao.grande_comando.orgao.nome} | {unidade_funcao.grande_comando.nome} | {unidade_funcao.nome}",
            'tipo': 'unidade',
            'nivel': 3
        })
        
        # 2. Subunidades (descendências)
        subunidades = SubUnidade.objects.filter(unidade=unidade_funcao, ativo=True)
        for s in subunidades.order_by('nome'):
            organizacoes.append({
                'id': f'sub_{s.id}',
                'nome': f"{unidade_funcao.grande_comando.orgao.nome} | {unidade_funcao.grande_comando.nome} | {unidade_funcao.nome} | {s.nome}",
                'tipo': 'sub_unidade',
                'nivel': 4
            })
        
        return organizacoes
    
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade
    elif funcao_militar.acesso == 'SUBUNIDADE':
        subunidade_funcao = funcao_usuario.sub_unidade
        if not subunidade_funcao:
            return []
        
        organizacoes = []
        
        # 1. Subunidade (próprio nível - não tem descendências)
        organizacoes.append({
            'id': f'sub_{subunidade_funcao.id}',
            'nome': f"{subunidade_funcao.unidade.grande_comando.orgao.nome} | {subunidade_funcao.unidade.grande_comando.nome} | {subunidade_funcao.unidade.nome} | {subunidade_funcao.nome}",
            'tipo': 'sub_unidade',
            'nivel': 4
        })
        
        return organizacoes
    
    return []


def aplicar_filtro_hierarquico_notas_restritivo(queryset, funcao_usuario, user):
    """
    Aplicar filtro hierárquico restritivo para notas (apenas o próprio nível, sem descendências)
    """
    from django.db.models import Q
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset.filter(tipo='NOTA')
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total a todas as notas
    if funcao_militar.acesso == 'TOTAL':
        return queryset.filter(tipo='NOTA')
        
    # TIPO DE ACESSO = NENHUM: Apenas notas do próprio usuário
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.filter(
            tipo='NOTA',
            criado_por=funcao_usuario.usuario
        )
        
    # TIPO DE ACESSO = ORGAO: Acesso APENAS ao órgão (sem descendências)
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            orgao = funcao_usuario.orgao
            # Filtrar apenas notas que são exatamente do órgão (não contêm " | ")
            return queryset.filter(
                tipo='NOTA',
                origem_publicacao=orgao.nome
            )
        return queryset.none()
            
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso APENAS ao grande comando (sem descendências)
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            grande_comando = funcao_usuario.grande_comando
            # Filtrar apenas notas que são exatamente do grande comando
            origem_gc = f"{grande_comando.orgao.nome} | {grande_comando.nome}"
            return queryset.filter(
                tipo='NOTA',
                origem_publicacao=origem_gc
            )
        return queryset.none()
            
    # TIPO DE ACESSO = UNIDADE: Acesso APENAS à unidade (sem descendências)
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            unidade = funcao_usuario.unidade
            # Filtrar apenas notas que são exatamente da unidade
            origem_unidade = f"{unidade.grande_comando.orgao.nome} | {unidade.grande_comando.nome} | {unidade.nome}"
            return queryset.filter(
                tipo='NOTA',
                origem_publicacao=origem_unidade
            )
        return queryset.none()
            
    # TIPO DE ACESSO = SUBUNIDADE: Acesso apenas à subunidade
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            subunidade = funcao_usuario.sub_unidade
            # Filtrar apenas notas que são exatamente da subunidade
            origem_subunidade = f"{subunidade.unidade.grande_comando.orgao.nome} | {subunidade.unidade.grande_comando.nome} | {subunidade.unidade.nome} | {subunidade.nome}"
            return queryset.filter(
                tipo='NOTA',
                origem_publicacao=origem_subunidade
            )
        return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_banco_horas_restritivo(queryset, funcao_usuario, user):
    """
    Aplicar filtro hierárquico restritivo para banco de horas (apenas o próprio nível, sem descendências)
    """
    from django.db.models import Q
    from .models import Militar, Lotacao
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total a todos os dados
    if funcao_militar.acesso == 'TOTAL':
        return queryset
        
    # TIPO DE ACESSO = NENHUM: Nenhum acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
        
    # TIPO DE ACESSO = ORGAO: Acesso APENAS ao órgão (sem descendências)
    elif funcao_militar.acesso == 'ORGAO':
        if funcao_usuario.orgao:
            orgao = funcao_usuario.orgao
            # Filtrar apenas militares lotados diretamente no órgão
            militares_orgao = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__orgao=orgao,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_orgao)
        return queryset.none()
            
    # TIPO DE ACESSO = GRANDE_COMANDO: Acesso APENAS ao grande comando (sem descendências)
    elif funcao_militar.acesso == 'GRANDE_COMANDO':
        if funcao_usuario.grande_comando:
            grande_comando = funcao_usuario.grande_comando
            # Filtrar apenas militares lotados diretamente no grande comando
            militares_gc = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__grande_comando=grande_comando,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_gc)
        return queryset.none()
            
    # TIPO DE ACESSO = UNIDADE: Acesso APENAS à unidade (sem descendências)
    elif funcao_militar.acesso == 'UNIDADE':
        if funcao_usuario.unidade:
            unidade = funcao_usuario.unidade
            # Filtrar apenas militares lotados diretamente na unidade
            militares_unidade = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__unidade=unidade,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_unidade)
        return queryset.none()
            
    # TIPO DE ACESSO = SUBUNIDADE: Acesso APENAS à subunidade (sem descendências)
    elif funcao_militar.acesso == 'SUBUNIDADE':
        if funcao_usuario.sub_unidade:
            subunidade = funcao_usuario.sub_unidade
            # Filtrar apenas militares lotados diretamente na subunidade
            militares_subunidade = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__sub_unidade=subunidade,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_subunidade)
        return queryset.none()
    
    return queryset.none()


def aplicar_filtro_hierarquico_banco_horas_especifico(queryset, funcao_usuario, user, organizacao_filtro):
    """
    Aplicar filtro hierárquico específico baseado na organização selecionada no filtro
    """
    from django.db.models import Q
    from .models import Orgao, GrandeComando, Unidade, SubUnidade, Militar, Lotacao
    
    # BYPASS COMPLETO PARA SUPERUSUÁRIOS
    if user and user.is_superuser:
        return queryset
    
    if not funcao_usuario or not funcao_usuario.funcao_militar:
        return queryset.none()
    
    funcao_militar = funcao_usuario.funcao_militar
    
    # TIPO DE ACESSO = TOTAL: Acesso total a todos os dados
    if funcao_militar.acesso == 'TOTAL':
        # Aplicar filtro específico da organização selecionada
        return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
        
    # TIPO DE ACESSO = NENHUM: Nenhum acesso
    elif funcao_militar.acesso == 'NENHUM':
        return queryset.none()
    
    # Para outros tipos de acesso, verificar se a organização selecionada está dentro do escopo permitido
    if organizacao_filtro.startswith('orgao_'):
        orgao_id = organizacao_filtro.replace('orgao_', '')
        try:
            orgao = Orgao.objects.get(id=orgao_id)
            # Verificar se o usuário tem acesso a este órgão
            if funcao_militar.acesso == 'ORGAO' and funcao_usuario.orgao == orgao:
                return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
        except Orgao.DoesNotExist:
            pass
        return queryset.none()
        
    elif organizacao_filtro.startswith('gc_'):
        gc_id = organizacao_filtro.replace('gc_', '')
        try:
            grande_comando = GrandeComando.objects.get(id=gc_id)
            # Verificar se o usuário tem acesso a este grande comando
            if funcao_militar.acesso in ['ORGAO', 'GRANDE_COMANDO']:
                if funcao_militar.acesso == 'ORGAO' and funcao_usuario.orgao == grande_comando.orgao:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
                elif funcao_militar.acesso == 'GRANDE_COMANDO' and funcao_usuario.grande_comando == grande_comando:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
        except GrandeComando.DoesNotExist:
            pass
        return queryset.none()
        
    elif organizacao_filtro.startswith('unidade_'):
        unidade_id = organizacao_filtro.replace('unidade_', '')
        try:
            unidade = Unidade.objects.get(id=unidade_id)
            # Verificar se o usuário tem acesso a esta unidade
            if funcao_militar.acesso in ['ORGAO', 'GRANDE_COMANDO', 'UNIDADE']:
                if funcao_militar.acesso == 'ORGAO' and funcao_usuario.orgao == unidade.grande_comando.orgao:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
                elif funcao_militar.acesso == 'GRANDE_COMANDO' and funcao_usuario.grande_comando == unidade.grande_comando:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
                elif funcao_militar.acesso == 'UNIDADE' and funcao_usuario.unidade == unidade:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
        except Unidade.DoesNotExist:
            pass
        return queryset.none()
        
    elif organizacao_filtro.startswith('sub_'):
        sub_id = organizacao_filtro.replace('sub_', '')
        try:
            subunidade = SubUnidade.objects.get(id=sub_id)
            # Verificar se o usuário tem acesso a esta subunidade
            if funcao_militar.acesso in ['ORGAO', 'GRANDE_COMANDO', 'UNIDADE', 'SUBUNIDADE']:
                if funcao_militar.acesso == 'ORGAO' and funcao_usuario.orgao == subunidade.unidade.grande_comando.orgao:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
                elif funcao_militar.acesso == 'GRANDE_COMANDO' and funcao_usuario.grande_comando == subunidade.unidade.grande_comando:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
                elif funcao_militar.acesso == 'UNIDADE' and funcao_usuario.unidade == subunidade.unidade:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
                elif funcao_militar.acesso == 'SUBUNIDADE' and funcao_usuario.sub_unidade == subunidade:
                    return aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro)
        except SubUnidade.DoesNotExist:
            pass
        return queryset.none()
    
    return queryset.none()


def aplicar_filtro_organizacao_especifica(queryset, organizacao_filtro):
    """
    Aplicar filtro específico baseado na organização selecionada
    """
    from .models import Orgao, GrandeComando, Unidade, SubUnidade, Militar, Lotacao
    
    if organizacao_filtro.startswith('orgao_'):
        orgao_id = organizacao_filtro.replace('orgao_', '')
        try:
            orgao = Orgao.objects.get(id=orgao_id)
            # Filtrar APENAS pelo órgão específico (sem descendências)
            militares_orgao = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__orgao=orgao,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_orgao)
        except Orgao.DoesNotExist:
            pass
            
    elif organizacao_filtro.startswith('gc_'):
        gc_id = organizacao_filtro.replace('gc_', '')
        try:
            grande_comando = GrandeComando.objects.get(id=gc_id)
            # Filtrar APENAS pelo grande comando específico (sem descendências)
            militares_gc = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__grande_comando=grande_comando,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_gc)
        except GrandeComando.DoesNotExist:
            pass
            
    elif organizacao_filtro.startswith('unidade_'):
        unidade_id = organizacao_filtro.replace('unidade_', '')
        try:
            unidade = Unidade.objects.get(id=unidade_id)
            # Filtrar APENAS pela unidade específica (sem subunidades)
            militares_unidade = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__unidade=unidade,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_unidade)
        except Unidade.DoesNotExist:
            pass
            
    elif organizacao_filtro.startswith('sub_'):
        sub_id = organizacao_filtro.replace('sub_', '')
        try:
            subunidade = SubUnidade.objects.get(id=sub_id)
            # Filtrar APENAS pela subunidade específica
            militares_subunidade = Militar.objects.filter(
                classificacao='ATIVO',
                lotacoes__sub_unidade=subunidade,
                lotacoes__status='ATUAL',
                lotacoes__ativo=True
            ).distinct()
            return queryset.filter(militar__in=militares_subunidade)
        except SubUnidade.DoesNotExist:
            pass
    
    return queryset.none()
