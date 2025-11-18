from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def build_pagination_url(page_number, request):
    """
    Constrói URL de paginação preservando todos os parâmetros de filtro
    """
    params = request.GET.copy()
    params['page'] = page_number
    return '?' + urlencode(params)

@register.inclusion_tag('militares/pagination_numbers.html', takes_context=True)
def pagination_numbers(context, page_obj, window=3):
    """
    Renderiza os números de página com reticências
    """
    # Verificar se page_obj é válido
    if not hasattr(page_obj, 'number') or not hasattr(page_obj, 'paginator'):
        return {
            'page_obj': None,
            'page_range': [],
            'show_ellipsis_before': False,
            'show_ellipsis_after': False,
            'request': context.get('request'),
        }
    
    current = page_obj.number
    total = page_obj.paginator.num_pages
    
    # Calcular range de páginas
    if total <= 7:  # Se há 7 ou menos páginas, mostrar todas
        page_range = list(range(1, total + 1))
        show_ellipsis_before = False
        show_ellipsis_after = False
    else:
        # Calcular range central
        start = max(1, current - window)
        end = min(total, current + window)
        
        # Ajustar se estiver muito próximo do início ou fim
        if start <= 3:
            start = 1
            end = min(7, total)
        elif end >= total - 2:
            start = max(1, total - 6)
            end = total
        
        page_range = list(range(start, end + 1))
        show_ellipsis_before = current > window + 2
        show_ellipsis_after = current < total - window - 1
    
    return {
        'page_obj': page_obj,
        'page_range': page_range,
        'show_ellipsis_before': show_ellipsis_before,
        'show_ellipsis_after': show_ellipsis_after,
        'request': context['request'],
    }
