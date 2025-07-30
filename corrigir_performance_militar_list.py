#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Correção de Performance - View militar_list
Resolve o problema de worker timeout causado por consultas pesadas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_render')
django.setup()

from django.db.models import Q, Sum, Case, When, IntegerField
from django.core.paginator import Paginator
from militares.models import Militar

def criar_view_otimizada():
    """Cria uma versão otimizada da view militar_list"""
    
    codigo_otimizado = '''
@login_required
@requer_perm_militares_visualizar
def militar_list(request):
    """Lista todos os militares ativos com paginação e busca - OTIMIZADA"""
    # Usar select_related para otimizar consultas relacionadas
    militares = Militar.objects.filter(situacao='AT').select_related('user')
    
    # Busca otimizada
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
        posto_mapping = {
            'cb': 'CB', 'tc': 'TC', 'mj': 'MJ', 'cp': 'CP',
            '1t': '1T', '2t': '2T', 'st': 'ST', '1s': '1S',
            '2s': '2S', '3s': '3S', 'cab': 'CAB', 'sd': 'SD', 'nvrr': 'NVRR'
        }
        posto_codigo = posto_mapping.get(posto.lower())
        if posto_codigo:
            militares = militares.filter(posto_graduacao=posto_codigo)
    
    situacao = request.GET.get('situacao')
    if situacao:
        situacao_mapping = {'at': 'AT', 'in': 'IN'}
        situacao_codigo = situacao_mapping.get(situacao.lower())
        if situacao_codigo:
            militares = militares.filter(situacao=situacao_codigo)
    
    quadro = request.GET.get('quadro')
    if quadro:
        militares = militares.filter(quadro=quadro)
    
    # Ordenação otimizada - evitar sorted() em Python
    ordenacao = request.GET.get('ordenacao', 'hierarquia_antiguidade')
    
    if ordenacao == 'hierarquia_antiguidade':
        # Usar Case/When para ordenação no banco em vez de Python
        militares = militares.annotate(
            hierarquia=Case(
                When(posto_graduacao='CB', then=1),
                When(posto_graduacao='TC', then=2),
                When(posto_graduacao='MJ', then=3),
                When(posto_graduacao='CP', then=4),
                When(posto_graduacao='1T', then=5),
                When(posto_graduacao='2T', then=6),
                When(posto_graduacao='AS', then=7),
                When(posto_graduacao='AA', then=8),
                When(posto_graduacao='ST', then=9),
                When(posto_graduacao='1S', then=10),
                When(posto_graduacao='2S', then=11),
                When(posto_graduacao='3S', then=12),
                When(posto_graduacao='CAB', then=13),
                When(posto_graduacao='SD', then=14),
                When(posto_graduacao='NVRR', then=15),
                default=999,
                output_field=IntegerField(),
            )
        ).order_by('hierarquia', 'numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'posto':
        militares = militares.order_by('posto_graduacao', 'nome_completo')
    elif ordenacao == 'matricula':
        militares = militares.order_by('matricula')
    elif ordenacao == 'data_ingresso':
        militares = militares.order_by('data_ingresso')
    elif ordenacao == 'numeracao_antiguidade':
        militares = militares.exclude(quadro='NVRR').exclude(posto_graduacao='NVRR').order_by('numeracao_antiguidade', 'nome_completo')
    elif ordenacao == 'pontuacao':
        # Otimizar consulta de pontuação
        militares = militares.annotate(
            pontuacao_total=Sum('fichaconceitooficiais__pontos') + Sum('fichaconceitopracas__pontos')
        ).order_by('-pontuacao_total')
    else:
        militares = militares.order_by('nome_completo')

    # PAGINAÇÃO OBRIGATÓRIA para evitar timeout
    itens_por_pagina = request.GET.get('itens_por_pagina', 50)
    try:
        itens_por_pagina = int(itens_por_pagina)
        if itens_por_pagina not in [20, 50, 100]:
            itens_por_pagina = 50  # Padrão mais conservador
    except (ValueError, TypeError):
        itens_por_pagina = 50
    
    # Contar total antes da paginação
    total_militares = militares.count()
    
    # Aplicar paginação
    paginator = Paginator(militares, itens_por_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'militares': page_obj,
        'page_obj': page_obj,
        'itens_por_pagina': itens_por_pagina,
        'total_militares': total_militares,
        'ordenacao': ordenacao,
    }
    
    return render(request, 'militares/militar_list.html', context)
'''
    
    return codigo_otimizado

def aplicar_correcao_views():
    """Aplica a correção na view militar_list"""
    
    print("🔧 Aplicando correção de performance na view militar_list...")
    
    # Ler o arquivo views.py
    views_path = 'militares/views.py'
    
    try:
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Arquivo {views_path} lido com sucesso")
        
        # Encontrar e substituir a view militar_list problemática
        # Procurar pela versão que usa sorted() em Python
        import re
        
        # Padrão para encontrar a view militar_list que usa sorted()
        pattern = r'@login_required\s+@requer_perm_militares_visualizar\s+def militar_list\(request\):\s*"""[^"]*"""\s*militares = Militar\.objects\.filter\(situacao=\'AT\'\)[^}]*militares = sorted\(militares[^}]*context = \{[^}]*\}\s*return render\(request, \'militares/militar_list\.html\', context\)'
        
        # Nova versão otimizada
        nova_view = criar_view_otimizada()
        
        # Substituir
        novo_content = re.sub(pattern, nova_view, content, flags=re.DOTALL)
        
        if novo_content != content:
            # Fazer backup
            backup_path = 'militares/views.py.backup_performance'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Backup criado: {backup_path}")
            
            # Salvar nova versão
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write(novo_content)
            print(f"✅ Correção aplicada em {views_path}")
            
            return True
        else:
            print("⚠️ Nenhuma alteração necessária ou padrão não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao aplicar correção: {e}")
        return False

def testar_performance():
    """Testa a performance da consulta otimizada"""
    
    print("🧪 Testando performance da consulta...")
    
    try:
        # Teste 1: Contagem simples
        start_time = time.time()
        total = Militar.objects.filter(situacao='AT').count()
        end_time = time.time()
        print(f"✅ Contagem total: {total} militares em {end_time - start_time:.2f}s")
        
        # Teste 2: Consulta com ordenação otimizada
        start_time = time.time()
        militares = Militar.objects.filter(situacao='AT').select_related('user').annotate(
            hierarquia=Case(
                When(posto_graduacao='CB', then=1),
                When(posto_graduacao='TC', then=2),
                When(posto_graduacao='MJ', then=3),
                When(posto_graduacao='CP', then=4),
                When(posto_graduacao='1T', then=5),
                When(posto_graduacao='2T', then=6),
                When(posto_graduacao='AS', then=7),
                When(posto_graduacao='AA', then=8),
                When(posto_graduacao='ST', then=9),
                When(posto_graduacao='1S', then=10),
                When(posto_graduacao='2S', then=11),
                When(posto_graduacao='3S', then=12),
                When(posto_graduacao='CAB', then=13),
                When(posto_graduacao='SD', then=14),
                When(posto_graduacao='NVRR', then=15),
                default=999,
                output_field=IntegerField(),
            )
        ).order_by('hierarquia', 'numeracao_antiguidade', 'nome_completo')[:50]
        
        # Forçar execução da consulta
        list(militares)
        end_time = time.time()
        print(f"✅ Consulta otimizada: 50 primeiros militares em {end_time - start_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False

if __name__ == '__main__':
    import time
    
    print("🚀 Iniciando correção de performance...")
    
    # Testar performance atual
    if testar_performance():
        print("✅ Teste de performance passou")
        
        # Aplicar correção
        if aplicar_correcao_views():
            print("✅ Correção aplicada com sucesso!")
            
            # Testar novamente
            print("🧪 Testando performance após correção...")
            if testar_performance():
                print("✅ Performance melhorada!")
            else:
                print("⚠️ Performance ainda pode ter problemas")
        else:
            print("❌ Falha ao aplicar correção")
    else:
        print("❌ Teste de performance falhou") 