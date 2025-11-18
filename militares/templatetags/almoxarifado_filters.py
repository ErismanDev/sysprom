from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def formatar_quantidade_unidade(quantidade, unidade_medida):
    """
    Formata quantidade removendo decimais quando for UN (Unidade) e corrige plural
    Exemplos:
    - 1.00 UN -> "1 unidade"
    - 2.00 UN -> "2 unidades"
    - 1.50 KG -> "1,50 quilogramas"
    """
    if quantidade is None:
        return ""
    
    # Se unidade_medida for None ou vazio, retornar apenas a quantidade
    if not unidade_medida:
        try:
            qtd = Decimal(str(quantidade))
            if qtd == qtd.quantize(Decimal('1')):
                return str(int(qtd))
            return f"{qtd:.2f}".replace('.', ',')
        except (ValueError, TypeError):
            return str(quantidade)
    
    # Converter unidade_medida para string e normalizar (maiúsculas, sem espaços)
    unidade_str = str(unidade_medida).strip().upper() if unidade_medida else ''
    
    # Converter para Decimal se for string ou float
    try:
        qtd = Decimal(str(quantidade))
    except (ValueError, TypeError):
        return str(quantidade)
    
    # Sempre remover decimais - mostrar apenas números inteiros
    # Converter para int para remover decimais (1.00 -> 1, 2.50 -> 2)
    qtd_int = int(qtd)
    # Formatar sem decimais
    qtd_formatada = str(qtd_int)
    
    # Plural baseado na unidade
    if unidade_str == 'UN':
        unidade_display = "unidade" if qtd_int == 1 else "unidades"
    else:
        unidade_display = _get_unidade_plural(unidade_str, qtd_int)
    
    return f"{qtd_formatada} {unidade_display}"


def _get_unidade_plural(unidade_medida, quantidade):
    """
    Retorna a unidade de medida no singular ou plural conforme a quantidade
    """
    # Se unidade_medida for None ou vazio, retornar "unidade(s)"
    if not unidade_medida:
        try:
            qtd = int(float(quantidade))
            return "unidade" if qtd == 1 else "unidades"
        except (ValueError, TypeError):
            return "unidades"
    
    # Converter unidade_medida para string se necessário
    unidade_str = str(unidade_medida).strip().upper() if unidade_medida else ''
    
    # Converter quantidade para int se for Decimal
    try:
        qtd = int(float(quantidade))
    except (ValueError, TypeError):
        qtd = 1
    
    unidades = {
        'UN': ('unidade', 'unidades'),
        'KG': ('quilograma', 'quilogramas'),
        'G': ('grama', 'gramas'),
        'L': ('litro', 'litros'),
        'ML': ('mililitro', 'mililitros'),
        'M': ('metro', 'metros'),
        'CM': ('centímetro', 'centímetros'),
        'M2': ('metro quadrado', 'metros quadrados'),
        'M3': ('metro cúbico', 'metros cúbicos'),
        'CX': ('caixa', 'caixas'),
        'PC': ('peça', 'peças'),
        'RL': ('rolo', 'rolos'),
        'FD': ('fardo', 'fardos'),
        'SC': ('saco', 'sacos'),
        'OUTROS': ('unidade', 'unidades'),
    }
    
    singular, plural = unidades.get(unidade_str, ('unidade', 'unidades'))
    return singular if qtd == 1 else plural


@register.filter
def formatar_quantidade(quantidade, unidade_medida=None):
    """
    Formata quantidade removendo decimais quando for UN (Unidade)
    Se unidade_medida não for fornecida, apenas formata o número
    """
    if quantidade is None:
        return ""
    
    try:
        qtd = Decimal(str(quantidade))
    except (ValueError, TypeError):
        return str(quantidade)
    
    # Se for UN (Unidade), remover decimais
    if unidade_medida == 'UN':
        qtd_int = int(qtd)
        return str(qtd_int)
    else:
        # Para outras unidades, verificar se tem decimais significativos
        if qtd == qtd.quantize(Decimal('1')):
            return str(int(qtd))
        else:
            return f"{qtd:.2f}".replace('.', ',')

