#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Militar

@login_required
def militar_list_simples(request):
    """Lista todos os militares ativos com paginação e hierarquia"""
    militares = Militar.objects.filter(situacao='AT')
    
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
            'at': 'AT',
            'in': 'IN'
        }
        situacao_codigo = situacao_mapping.get(situacao.lower())
        if situacao_codigo:
            militares = militares.filter(situacao=situacao_codigo)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
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
        # Adicionar os filtros aplicados ao contexto
        'query': query,
        'posto_filtro': posto,
        'situacao_filtro': situacao,
        'quadro_filtro': quadro,
    }
    
    return render(request, 'militares/militar_list.html', context) 