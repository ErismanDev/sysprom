#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Militar, Lotacao, Orgao, GrandeComando, Unidade, SubUnidade
from .permissoes_sistema import tem_permissao
from militares.signals import atualizar_situacao_militar_automaticamente

@login_required
def militar_list_simples(request):
    """Lista todos os militares ativos com paginação (excluindo NVRR)"""
    # Obter queryset base - todos os militares ativos, EXCETO NVRR
    militares = Militar.objects.filter(classificacao='ATIVO').exclude(quadro='NVRR')
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Filtros
    posto = request.GET.get('posto')
    if posto:
        # Mapear os valores do frontend para os códigos do banco
        posto_mapping = {
            'cb': 'CB',
            'tc': 'TC', 
            'mj': 'MJ',
            'cp': 'CP',
            '1t': '1T',
            '2t': '2T',
            'st': 'ST',
            '1s': '1S',
            '2s': '2S',
            '3s': '3S',
            'cab': 'CAB',
            'sd': 'SD',
            'nvrr': 'NVRR'
        }
        posto_codigo = posto_mapping.get(posto.lower())
        if posto_codigo:
            militares = militares.filter(posto_graduacao=posto_codigo)
    
    situacao = request.GET.get('situacao')
    if situacao:
        situacao_mapping = {
            'at': 'ATIVO',
            'in': 'INATIVO'
        }
        situacao_codigo = situacao_mapping.get(situacao.lower())
        if situacao_codigo:
            militares = militares.filter(classificacao=situacao_codigo)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Filtro por estrutura organizacional
    estrutura = request.GET.get('estrutura')
    if estrutura:
        # Decodificar o filtro de estrutura
        if estrutura.startswith('orgao_'):
            orgao_id = estrutura.replace('orgao_', '')
            militares = militares.filter(
                lotacoes__orgao_id=orgao_id,
                lotacoes__ativo=True,
                lotacoes__status='ATUAL'
            ).distinct()
        elif estrutura.startswith('gc_'):
            gc_id = estrutura.replace('gc_', '')
            militares = militares.filter(
                lotacoes__grande_comando_id=gc_id,
                lotacoes__ativo=True,
                lotacoes__status='ATUAL'
            ).distinct()
        elif estrutura.startswith('unidade_'):
            unidade_id = estrutura.replace('unidade_', '')
            militares = militares.filter(
                lotacoes__unidade_id=unidade_id,
                lotacoes__ativo=True,
                lotacoes__status='ATUAL'
            ).distinct()
        elif estrutura.startswith('sub_unidade_'):
            sub_unidade_id = estrutura.replace('sub_unidade_', '')
            militares = militares.filter(
                lotacoes__sub_unidade_id=sub_unidade_id,
                lotacoes__ativo=True,
                lotacoes__status='ATUAL'
            ).distinct()
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
        'NVRR': 15,  # NVRR - tratado separadamente
    }
    
    # Ordenar por hierarquia de postos e depois por antiguidade
    militares = sorted(militares, key=lambda x: (
        hierarquia_postos.get(x.posto_graduacao, 999),
        # Para Subtenentes (ST), ordenar por CHO primeiro (True vem antes de False)
        (x.posto_graduacao == 'ST' and not x.curso_cho, x.posto_graduacao == 'ST' and x.curso_cho),
        x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
        x.nome_completo
    ))
    
    # Adicionar lotação atual para cada militar
    for militar in militares:
        militar.lotacao_atual_obj = militar.lotacao_atual()
    
    # Paginação
    itens_por_pagina = request.GET.get('itens_por_pagina', 20)
    try:
        itens_por_pagina = int(itens_por_pagina)
        if itens_por_pagina not in [20, 50, 100]:
            itens_por_pagina = 20
    except (ValueError, TypeError):
        itens_por_pagina = 20
    
    paginator = Paginator(militares, itens_por_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Buscar lotações organizadas por estrutura organizacional
    lotacoes_por_estrutura = {}
    
    # Buscar lotações ativas com estrutura organizacional
    lotacoes_com_estrutura = Lotacao.objects.filter(
        ativo=True
    ).select_related('orgao', 'grande_comando', 'unidade', 'sub_unidade').order_by('lotacao')
    
    # Organizar por estrutura
    for lotacao in lotacoes_com_estrutura:
        if lotacao.orgao:
            if lotacao.orgao not in lotacoes_por_estrutura:
                lotacoes_por_estrutura[lotacao.orgao] = {}
            
            if lotacao.grande_comando:
                if lotacao.grande_comando not in lotacoes_por_estrutura[lotacao.orgao]:
                    lotacoes_por_estrutura[lotacao.orgao][lotacao.grande_comando] = {}
                
                if lotacao.unidade:
                    if lotacao.unidade not in lotacoes_por_estrutura[lotacao.orgao][lotacao.grande_comando]:
                        lotacoes_por_estrutura[lotacao.orgao][lotacao.grande_comando][lotacao.unidade] = []
                    
                    if lotacao.sub_unidade:
                        # Verificar se já existe esta sub-unidade
                        sub_unidade_existe = False
                        for item in lotacoes_por_estrutura[lotacao.orgao][lotacao.grande_comando][lotacao.unidade]:
                            if item['sub_unidade'] == lotacao.sub_unidade:
                                item['lotacoes'].append(lotacao)
                                sub_unidade_existe = True
                                break
                        
                        if not sub_unidade_existe:
                            lotacoes_por_estrutura[lotacao.orgao][lotacao.grande_comando][lotacao.unidade].append({
                                'sub_unidade': lotacao.sub_unidade,
                                'lotacoes': [lotacao]
                            })
    
    # Buscar lotações sem estrutura organizacional (para compatibilidade)
    lotacoes_sem_estrutura = Lotacao.objects.filter(
        ativo=True,
        orgao__isnull=True
    ).order_by('lotacao')
    
    context = {
        'militares': page_obj,
        'page_obj': page_obj,
        'itens_por_pagina': itens_por_pagina,
        'total_militares': len(militares),
        'total_geral': Militar.objects.filter(classificacao='ATIVO').count(),
        # Contagens por quadro para estatísticas
        'total_comb': Militar.objects.filter(classificacao='ATIVO', quadro='COMB').count(),
        'total_eng': Militar.objects.filter(classificacao='ATIVO', quadro='ENG').count(),
        'total_comp': Militar.objects.filter(classificacao='ATIVO', quadro='COMP').count(),
        'total_pracas': Militar.objects.filter(classificacao='ATIVO', quadro='PRACAS').count(),
        # Adicionar os filtros aplicados ao contexto
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
        'estrutura_filtro': estrutura,
        'lotacoes_por_estrutura': lotacoes_por_estrutura,
        'lotacoes_sem_estrutura': lotacoes_sem_estrutura,
        'pode_reordenar_antiguidade': tem_permissao(request.user, 'MILITARES', 'REORDENAR_ANTIGUIDADE'),
        'nivel_acesso': 'TOTAL',  # Todos os usuários têm acesso total aos militares
        'nivel_usuario': 'TOTAL',  # Todos os usuários têm acesso total aos militares
    }
    
    # Obter estrutura pré-selecionada baseada na lotação do usuário
    estrutura_pre_selecionada = None
    nome_estrutura_pre_selecionada = ""
    
    if not estrutura:  # Se não há filtro de estrutura aplicado
        from .permissoes_militares import obter_sessao_ativa_usuario
        sessao = obter_sessao_ativa_usuario(request.user)
        if sessao and sessao.funcao_militar_usuario:
            uf = sessao.funcao_militar_usuario
            
            # Determinar a estrutura baseada no nível de acesso
            if context['nivel_acesso'] == 'SUBUNIDADE' and uf.sub_unidade:
                estrutura_pre_selecionada = f"sub_unidade_{uf.sub_unidade.id}"
                nome_estrutura_pre_selecionada = f" {uf.sub_unidade.nome}"
            elif context['nivel_acesso'] == 'UNIDADE' and uf.unidade:
                estrutura_pre_selecionada = f"unidade_{uf.unidade.id}"
                nome_estrutura_pre_selecionada = f" {uf.unidade.nome}"
            elif context['nivel_acesso'] == 'GRANDE_COMANDO' and uf.grande_comando:
                estrutura_pre_selecionada = f"gc_{uf.grande_comando.id}"
                nome_estrutura_pre_selecionada = f" {uf.grande_comando.nome}"
            elif context['nivel_acesso'] == 'ORGAO' and uf.orgao:
                estrutura_pre_selecionada = f"orgao_{uf.orgao.id}"
                nome_estrutura_pre_selecionada = f" {uf.orgao.nome}"
            
            # Atualizar contexto com estrutura pré-selecionada
            if estrutura_pre_selecionada:
                context['estrutura_filtro'] = estrutura_pre_selecionada
                context['estrutura_pre_selecionada'] = estrutura_pre_selecionada
                context['nome_estrutura_pre_selecionada'] = nome_estrutura_pre_selecionada
    
    return render(request, 'militares/militar_list.html', context)

@login_required
def lotacao_autocomplete(request):
    """View AJAX para autocomplete de lotações"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Buscar lotações que contenham o termo de busca
    lotacoes = Lotacao.objects.filter(
        ativo=True,
        lotacao__icontains=query
    ).select_related('orgao', 'grande_comando', 'unidade', 'sub_unidade')[:10]
    
    results = []
    for lotacao in lotacoes:
        # Construir nome hierárquico
        nome_hierarquico = lotacao.lotacao
        if lotacao.sub_unidade:
            nome_hierarquico = f"{lotacao.sub_unidade.nome_completo} - {lotacao.lotacao}"
        elif lotacao.unidade:
            nome_hierarquico = f"{lotacao.unidade.nome_completo} - {lotacao.lotacao}"
        elif lotacao.grande_comando:
            nome_hierarquico = f"{lotacao.grande_comando.nome_completo} - {lotacao.lotacao}"
        elif lotacao.orgao:
            nome_hierarquico = f"{lotacao.orgao.nome_completo} - {lotacao.lotacao}"
        
        results.append({
            'id': lotacao.id,
            'nome': lotacao.lotacao,
            'nome_hierarquico': nome_hierarquico,
            'orgao': lotacao.orgao.nome_completo if lotacao.orgao else '',
            'grande_comando': lotacao.grande_comando.nome_completo if lotacao.grande_comando else '',
            'unidade': lotacao.unidade.nome_completo if lotacao.unidade else '',
            'sub_unidade': lotacao.sub_unidade.nome_completo if lotacao.sub_unidade else ''
        })
    
    return JsonResponse({'results': results})

@login_required
def nvrr_list(request):
    """Lista apenas militares NVRR (Não computado no efetivo)"""
    # Obter queryset base - apenas NVRR ativos
    militares = Militar.objects.filter(classificacao='ATIVO', quadro='NVRR')
    
    # Busca
    query = request.GET.get('q')
    if query:
        militares = militares.filter(
            Q(nome_completo__icontains=query) |
            Q(nome_guerra__icontains=query) |
            Q(matricula__icontains=query) |
            Q(cpf__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Definir a hierarquia dos postos (do mais alto para o mais baixo)
    hierarquia_postos = {
        'CB': 1,   # Coronel
        'TC': 2,   # Tenente Coronel
        'MJ': 3,   # Major
        'CP': 4,   # Capitão
        '1T': 5,   # 1º Tenente
        '2T': 6,   # 2º Tenente
        'AS': 7,   # Aspirante a Oficial
        'AA': 8,   # Aluno de Adaptação
        'ST': 9,  # Subtenente
        '1S': 10,  # 1º Sargento
        '2S': 11,  # 2º Sargento
        '3S': 12,  # 3º Sargento
        'CAB': 13,  # Cabo
        'SD': 14,  # Soldado
        'NVRR': 15,  # NVRR - tratado separadamente
    }
    
    # Ordenar por hierarquia de postos e depois por antiguidade
    militares = sorted(militares, key=lambda x: (
        hierarquia_postos.get(x.posto_graduacao, 999),
        # Para Subtenentes (ST), ordenar por CHO primeiro (True vem antes de False)
        (x.posto_graduacao == 'ST' and not x.curso_cho, x.posto_graduacao == 'ST' and x.curso_cho),
        x.numeracao_antiguidade or 999999,  # Militares sem antiguidade vão para o final
        x.nome_completo
    ))
    
    # Adicionar lotação atual para cada militar
    for militar in militares:
        militar.lotacao_atual_obj = militar.lotacao_atual()
    
    # Paginação
    itens_por_pagina = request.GET.get('itens_por_pagina', 20)
    try:
        itens_por_pagina = int(itens_por_pagina)
        if itens_por_pagina not in [20, 50, 100]:
            itens_por_pagina = 20
    except (ValueError, TypeError):
        itens_por_pagina = 20
    
    paginator = Paginator(militares, itens_por_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'militares': page_obj,
        'page_obj': page_obj,
        'itens_por_pagina': itens_por_pagina,
        'total_militares': len(militares),
        'total_geral': Militar.objects.filter(classificacao='ATIVO', quadro='NVRR').count(),
        'query': query,
        'pode_reordenar_antiguidade': tem_permissao(request.user, 'MILITARES', 'REORDENAR_ANTIGUIDADE'),
        'nvrr_only': True,  # Flag para identificar que é lista apenas de NVRR
    }
    
    return render(request, 'militares/militar_list.html', context)


@login_required
@require_http_methods(["POST"])
def sincronizar_situacoes_militares(request):
    """Sincroniza as situações de todos os militares baseado em afastamentos, férias e licenças ativas"""
    if not request.user.is_superuser:
        messages.error(request, 'Apenas superusuários podem sincronizar as situações dos militares.')
        return redirect('militares:militar_list')
    
    try:
        from django.db.models import Q
        from datetime import date
        from .models import Afastamento, Ferias, LicencaEspecial
        
        hoje = date.today()
        
        # 1. Encerrar afastamentos vencidos (status ATIVO com data_fim_prevista < hoje)
        afastamentos_vencidos = Afastamento.objects.filter(
            status='ATIVO',
            data_fim_prevista__lt=hoje,
            data_fim_real__isnull=True
        )
        
        total_afastamentos_encerrados = 0
        for afastamento in afastamentos_vencidos:
            afastamento.status = 'ENCERRADO'
            afastamento.data_fim_real = afastamento.data_fim_prevista
            afastamento.save(update_fields=['status', 'data_fim_real'])
            total_afastamentos_encerrados += 1
        
        # 2. Atualizar férias vencidas
        ferias_vencidas = Ferias.objects.filter(
            status='GOZANDO',
            data_fim__lt=hoje
        )
        
        total_ferias_atualizadas = 0
        for ferias in ferias_vencidas:
            ferias.status = 'GOZADA'
            ferias.save(update_fields=['status'])
            total_ferias_atualizadas += 1
        
        # 3. Sincronizar situações dos militares
        militares_ativos = Militar.objects.filter(classificacao='ATIVO')
        total_atualizados = 0
        
        for militar in militares_ativos:
            # Verificar se há afastamentos ativos até hoje
            # Considerar ativo apenas se:
            # - data_inicio <= hoje
            # - status != CANCELADO
            # - (data_fim_real >= hoje) OU (data_fim_prevista >= hoje E data_fim_real is null)
            # Se data_fim_prevista < hoje e data_fim_real is null, não considerar como ativo
            afastamentos_ativos = Afastamento.objects.filter(
                militar=militar
            ).exclude(status='CANCELADO').filter(
                data_inicio__lte=hoje
            ).filter(
                Q(data_fim_real__gte=hoje) | 
                Q(data_fim_prevista__gte=hoje, data_fim_real__isnull=True) |
                Q(data_fim_prevista__isnull=True, data_fim_real__isnull=True)
            )
            
            # Verificar se há férias ativas até hoje
            # Considerar ativo apenas se data_fim >= hoje
            # Se data_fim < hoje, não considerar como ativo (mesmo que status seja GOZANDO)
            ferias_ativas = Ferias.objects.filter(
                militar=militar
            ).exclude(status__in=['CANCELADA', 'REPROGRAMADA', 'GOZADA']).filter(
                data_inicio__lte=hoje,
                data_fim__gte=hoje
            ).filter(
                status__in=['GOZANDO', 'PLANEJADA']
            )
            
            # Verificar se há licenças especiais ativas até hoje
            # Considerar ativo apenas se (data_fim >= hoje OU data_fim is null)
            # Se data_fim < hoje, não considerar como ativo
            licencas_ativas = LicencaEspecial.objects.filter(
                militar=militar
            ).exclude(status='CANCELADA').filter(
                data_inicio__lte=hoje
            ).filter(
                Q(data_fim__gte=hoje) | 
                Q(data_fim__isnull=True)
            )
            
            # Determinar qual situação o militar deveria ter
            situacao_esperada = None
            
            if afastamentos_ativos.exists():
                primeiro_afastamento = afastamentos_ativos.order_by('data_inicio').first()
                situacao_esperada = primeiro_afastamento.tipo_afastamento
            elif ferias_ativas.exists():
                situacao_esperada = 'AFASTAMENTO_FERIAS'
            elif licencas_ativas.exists():
                situacao_esperada = 'AFASTAMENTO_LICENCA_ESPECIAL'
            else:
                situacao_esperada = 'PRONTO'
            
            # Atualizar situação se necessário
            if militar.situacao != situacao_esperada:
                militar.situacao = situacao_esperada
                militar.save(update_fields=['situacao'])
                total_atualizados += 1
        
        # Montar mensagem de sucesso
        mensagem_parts = []
        if total_afastamentos_encerrados > 0:
            mensagem_parts.append(f'{total_afastamentos_encerrados} afastamento(s) encerrado(s)')
        if total_ferias_atualizadas > 0:
            mensagem_parts.append(f'{total_ferias_atualizadas} férias atualizada(s)')
        if total_atualizados > 0:
            mensagem_parts.append(f'{total_atualizados} militar(es) com situação atualizada')
        
        if mensagem_parts:
            mensagem = 'Sincronização concluída: ' + ', '.join(mensagem_parts) + '.'
        else:
            mensagem = 'Sincronização concluída. Nenhuma alteração necessária.'
        
        messages.success(request, mensagem)
    except Exception as e:
        messages.error(request, f'Erro ao sincronizar situações: {str(e)}')
    
    return redirect('militares:militar_list') 