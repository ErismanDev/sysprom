from django import template
import re

register = template.Library()

@register.filter
def fix_duplicate_year(numero):
    """
    Corrige números com ano duplicado (ex: 001/2025/2025 -> 001/2025)
    """
    if not numero:
        return numero
    
    # Regex para encontrar padrão XXX/YYYY/YYYY
    pattern = r'^(\d{3})/(\d{4})/(\d{4})$'
    match = re.match(pattern, numero)
    
    if match:
        # Se encontrou o padrão duplicado, retorna apenas XXX/YYYY
        return f"{match.group(1)}/{match.group(2)}"
    
    # Se não encontrou o padrão, retorna o número original
    return numero
