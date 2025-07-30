#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aplicar correção de performance na view militar_list
"""

def aplicar_correcao():
    """Aplica a correção de performance na view militar_list"""
    
    print("🔧 Aplicando correção de performance...")
    
    # Ler o arquivo views.py
    try:
        with open('militares/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Arquivo lido com sucesso")
        
        # Fazer backup
        with open('militares/views.py.backup_performance', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Backup criado")
        
        # Substituir a view problemática
        # Procurar pela linha que usa sorted() em Python
        import re
        
        # Padrão para encontrar a view que usa sorted()
        old_pattern = r'(\s+)militares = sorted\(militares, key=lambda x: \([^)]+\)\)'
        
        # Nova versão otimizada
        new_replacement = r'''\1# OTIMIZAÇÃO: Usar ordenação no banco em vez de Python
\1        militares = militares.annotate(
\1            hierarquia=Case(
\1                When(posto_graduacao='CB', then=1),
\1                When(posto_graduacao='TC', then=2),
\1                When(posto_graduacao='MJ', then=3),
\1                When(posto_graduacao='CP', then=4),
\1                When(posto_graduacao='1T', then=5),
\1                When(posto_graduacao='2T', then=6),
\1                When(posto_graduacao='AS', then=7),
\1                When(posto_graduacao='AA', then=8),
\1                When(posto_graduacao='ST', then=9),
\1                When(posto_graduacao='1S', then=10),
\1                When(posto_graduacao='2S', then=11),
\1                When(posto_graduacao='3S', then=12),
\1                When(posto_graduacao='CAB', then=13),
\1                When(posto_graduacao='SD', then=14),
\1                When(posto_graduacao='NVRR', then=15),
\1                default=999,
\1                output_field=IntegerField(),
\1            )
\1        ).order_by('hierarquia', 'numeracao_antiguidade', 'nome_completo')'''
        
        # Aplicar a substituição
        new_content = re.sub(old_pattern, new_replacement, content, flags=re.DOTALL)
        
        # Adicionar import necessário
        if 'from django.db.models import Case, When, IntegerField' not in new_content:
            # Encontrar linha de imports
            import_pattern = r'(from django\.db\.models import [^)]+)\)'
            import_replacement = r'\1, Case, When, IntegerField)'
            new_content = re.sub(import_pattern, import_replacement, new_content)
        
        # Adicionar paginação obrigatória
        # Procurar por "Sem paginação" e substituir
        pagination_pattern = r'(\s+)# Sem paginação - mostrar todos os militares\s+context = \{'
        pagination_replacement = r'''\1# PAGINAÇÃO OBRIGATÓRIA para evitar timeout
\1    itens_por_pagina = request.GET.get('itens_por_pagina', 50)
\1    try:
\1        itens_por_pagina = int(itens_por_pagina)
\1        if itens_por_pagina not in [20, 50, 100]:
\1            itens_por_pagina = 50  # Padrão mais conservador
\1    except (ValueError, TypeError):
\1        itens_por_pagina = 50
\1    
\1    # Contar total antes da paginação
\1    total_militares = militares.count()
\1    
\1    # Aplicar paginação
\1    paginator = Paginator(militares, itens_por_pagina)
\1    page_number = request.GET.get('page')
\1    page_obj = paginator.get_page(page_number)
\1    
\1    context = {'''
        
        new_content = re.sub(pagination_pattern, pagination_replacement, new_content, flags=re.DOTALL)
        
        # Atualizar context para incluir paginação
        context_pattern = r"'militares': militares,"
        context_replacement = r"'militares': page_obj,\n        'page_obj': page_obj,\n        'itens_por_pagina': itens_por_pagina,\n        'total_militares': total_militares,"
        
        new_content = re.sub(context_pattern, context_replacement, new_content)
        
        # Salvar nova versão
        with open('militares/views.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Correção aplicada com sucesso!")
        print("📋 Alterações realizadas:")
        print("   - Removida ordenação sorted() em Python")
        print("   - Adicionada ordenação Case/When no banco")
        print("   - Implementada paginação obrigatória")
        print("   - Adicionados imports necessários")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar correção: {e}")
        return False

if __name__ == '__main__':
    aplicar_correcao() 