from django import template

register = template.Library()

@register.filter
def ultima_instancia_origem(origem):
    """
    Extrai a última instância da origem hierárquica.
    Ex: "Comando Geral | DGP | Seção de Promoções" -> "Seção de Promoções"
    Ex: "Comando Operacional de Bombeiros - Comando Regional do Meio-Norte - 1º Grupamento de Bombeiros Militar" -> "1º Grupamento de Bombeiros Militar"
    """
    if not origem:
        return ""
    
    # Primeiro tentar dividir por " | " (formato com pipes)
    partes = origem.split(" | ")
    if len(partes) > 1:
        return partes[-1].strip()
    
    # Se não tem pipes, tentar dividir por " - " (formato com hífens)
    partes = origem.split(" - ")
    if len(partes) > 1:
        return partes[-1].strip()
    
    # Se não tem separadores, retornar a origem completa
    return origem.strip()