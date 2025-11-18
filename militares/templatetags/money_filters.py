from django import template

register = template.Library()

@register.filter
def currency_br(value):
    """Formata valor como moeda brasileira (R$ 1.234,56) - mesmo formato do OrcamentoPlanejadas"""
    if value is None:
        return "R$ 0,00"
    
    try:
        # Converte para float se for string
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        # Formatação brasileira: ponto para milhares, vírgula para decimais
        valor_str = f"{value:,.2f}"
        # Substituir vírgula por ponto temporariamente, depois trocar de volta
        valor_str = valor_str.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        
        return f"R$ {valor_str}"
    except (ValueError, TypeError):
        return "R$ 0,00"

@register.filter
def number_br(value):
    """Formata número no padrão brasileiro (1.234,56) - mesmo formato do OrcamentoPlanejadas"""
    if value is None:
        return "0,00"
    
    try:
        # Converte para float se for string
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        # Formatação brasileira: ponto para milhares, vírgula para decimais
        valor_str = f"{value:,.2f}"
        # Substituir vírgula por ponto temporariamente, depois trocar de volta
        valor_str = valor_str.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        
        return valor_str
    except (ValueError, TypeError):
        return "0,00"

@register.filter
def money_br(value):
    """Formata valor como moeda brasileira (R$ 1.234,56) - alias para currency_br"""
    return currency_br(value)

@register.filter
def input_value(value):
    """Formata valor para campos de input - remove 0,00"""
    if value is None or value == 0:
        return ""
    
    try:
        # Converte para float se for string
        if isinstance(value, str):
            value = float(value.replace(',', '.'))
        
        # Se valor for zero, retorna vazio
        if value == 0:
            return ""
        
        # Formatação brasileira: ponto para milhares, vírgula para decimais
        valor_str = f"{value:,.2f}"
        # Substituir vírgula por ponto temporariamente, depois trocar de volta
        valor_str = valor_str.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
        
        return valor_str
    except (ValueError, TypeError):
        return ""