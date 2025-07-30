#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Criar view militar_list otimizada
"""

def criar_view_otimizada():
    """Cria uma versão completamente otimizada da view militar_list"""
    
    view_otimizada = '''
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
    
    return view_otimizada

def aplicar_view_otimizada():
    """Aplica a view otimizada no arquivo views.py"""
    
    print("🔧 Aplicando view militar_list otimizada...")
    
    try:
        # Ler o arquivo
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fazer backup
        with open('militares/views.py.backup_view_otimizada', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Backup criado")
        
        # Encontrar e substituir a view problemática
        import re
        
        # Padrão para encontrar a view militar_list que usa sorted()
        pattern = r'@login_required\s+@requer_perm_militares_visualizar\s+def militar_list\(request\):\s*"""[^"]*"""\s*militares = Militar\.objects\.filter\(situacao=\'AT\'\)[^}]*return render\(request, \'militares/militar_list\.html\', context\)'
        
        # Nova versão otimizada
        nova_view = criar_view_otimizada()
        
        # Substituir
        novo_content = re.sub(pattern, nova_view, content, flags=re.DOTALL)
        
        if novo_content != content:
            # Salvar nova versão
            with open('militares/views.py', 'w', encoding='utf-8') as f:
                f.write(novo_content)
            print("✅ View otimizada aplicada com sucesso!")
            return True
        else:
            print("⚠️ Padrão não encontrado, tentando abordagem alternativa...")
            
            # Abordagem alternativa: substituir apenas a parte problemática
            old_pattern = r'militares = sorted\(militares, key=lambda x: \([^)]+\)\)'
            new_replacement = '''# OTIMIZAÇÃO: Usar ordenação no banco em vez de Python
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
        ).order_by('hierarquia', 'numeracao_antiguidade', 'nome_completo')'''
            
            novo_content = re.sub(old_pattern, new_replacement, content, flags=re.DOTALL)
            
            if novo_content != content:
                with open('militares/views.py', 'w', encoding='utf-8') as f:
                    f.write(novo_content)
                print("✅ Otimização aplicada com sucesso!")
                return True
            else:
                print("❌ Não foi possível aplicar a otimização")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao aplicar otimização: {e}")
        return False

if __name__ == '__main__':
    aplicar_view_otimizada() 