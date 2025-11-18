from django import template
import re

register = template.Library()

@register.filter
def status(queryset, status_value):
    """Filtra um queryset por status"""
    return queryset.filter(status=status_value)

@register.filter
def lotacao_resumida(lotacao_completa):
    """
    Extrai apenas a última parte da hierarquia da lotação:
    - Se lotado no órgão: mostra o órgão
    - Se lotado no grande comando: mostra o grande comando  
    - Se lotado na unidade: mostra a unidade
    - Se lotado na subunidade: mostra a subunidade
    
    Exemplo: "1º SGBM/1º GBM | CBMEPI | 1º SGBM | 1º GBM" -> "1º GBM"
    """
    if not lotacao_completa:
        return ""
    
    # Dividir por "|" e pegar a última parte (mais específica)
    partes = lotacao_completa.strip().split('|')
    if len(partes) > 0:
        return partes[-1].strip()
    
    return lotacao_completa
