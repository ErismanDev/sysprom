from django import template
from django.utils.safestring import mark_safe
from ..models import Publicacao

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retorna um item de um dicionário usando a chave"""
    return dictionary.get(key, key)

@register.filter
def lookup(dictionary, key):
    """Filtro para acessar um dicionário por chave"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return None

@register.filter
def split(value, arg):
    """Divide uma string em uma lista usando o separador especificado"""
    return value.split(arg)

@register.filter
def after_slash(value):
    """Retorna apenas a parte após a barra (/) se existir, senão retorna o valor original"""
    if '/' in str(value):
        return str(value).split('/')[-1].strip()
    return value

@register.filter
def sum_vagas_fixadas(queryset):
    """Soma as vagas fixadas de um queryset de itens de quadro"""
    return sum(item.vagas_fixadas for item in queryset)

@register.filter
def sum_claro(queryset):
    """Soma os valores de vagas disponíveis de um queryset de itens de quadro"""
    return sum(item.claro for item in queryset)

@register.filter
def sum_efetivo_previsto(queryset):
    """Soma os valores de efetivo previsto de um queryset de itens de quadro"""
    return sum(item.efetivo_previsto for item in queryset)

@register.filter
def multiply(value, arg):
    """Multiplica um valor por um argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_attr(obj, attr):
    """Obtém um atributo de um objeto"""
    if obj is None:
        return None
    return getattr(obj, attr, None)

@register.simple_tag(takes_context=True)
def obter_funcao_atual_usuario(context, usuario):
    request = context.get('request')
    if request and hasattr(request, 'session'):
        return request.session.get('funcao_atual_nome', 'Usuário do Sistema')
    return 'Usuário do Sistema' 

@register.filter
def posto_com_bm(posto_display):
    """
    Adiciona 'BM' após o posto se não já estiver presente
    """
    if not posto_display:
        return posto_display
    
    if "BM" not in posto_display:
        return f"{posto_display} BM"
    return posto_display

@register.filter
def nome_completo_militar(militar):
    """
    Retorna o nome completo do militar com posto e BM
    """
    if not militar:
        return ""
    
    posto = militar.get_posto_graduacao_display()
    if "BM" not in posto:
        posto = f"{posto} BM"
    
    return f"{militar.nome_completo} - {posto}" 

@register.filter
def formatar_data_assinatura(data_assinatura):
    """
    Template filter para formatar data de assinatura de forma consistente
    """
    from militares.utils import formatar_data_assinatura as formatar_data
    
    if not data_assinatura:
        return ""
    
    data_formatada, hora_formatada = formatar_data(data_assinatura)
    return f"{data_formatada} às {hora_formatada}"

@register.filter
def formatar_data_assinatura_simples(data_assinatura):
    """
    Template filter para formatar apenas a data da assinatura
    """
    from militares.utils import formatar_data_assinatura as formatar_data
    
    if not data_assinatura:
        return ""
    
    data_formatada, _ = formatar_data(data_assinatura)
    return data_formatada

@register.filter
def formatar_hora_assinatura(data_assinatura):
    """
    Template filter para formatar apenas a hora da assinatura
    """
    from militares.utils import formatar_data_assinatura as formatar_data
    
    if not data_assinatura:
        return ""
    
    _, hora_formatada = formatar_data(data_assinatura)
    return hora_formatada

@register.filter
def tem_funcao_especifica(usuario, funcoes_lista):
    """
    Verifica se o usuário tem alguma das funções especificadas na lista
    """
    from militares.permissoes_simples import tem_funcao_especial
    return tem_funcao_especial(usuario, funcoes_lista)

@register.filter
def criptografar_cpf(cpf):
    """
    Criptografa o CPF mostrando apenas os primeiros 3 dígitos e os últimos 2
    Exemplo: 123.456.789-00 -> 123.***.***-00
    """
    if not cpf:
        return cpf
    
    # Remover pontos e traços
    cpf_limpo = cpf.replace('.', '').replace('-', '')
    
    if len(cpf_limpo) != 11:
        return cpf
    
    # Retornar CPF criptografado
    return f"{cpf_limpo[:3]}.***.***-{cpf_limpo[-2:]}"

@register.simple_tag
def get_notas_boletim(numero_boletim):
    """Retorna as notas que estão incluídas em um boletim"""
    return Publicacao.objects.filter(
        tipo='NOTA',
        numero_boletim=numero_boletim
    ).order_by('numero')

@register.filter
def zeropad(value, width=2):
    """Formata número com zero à esquerda"""
    try:
        # Converter para inteiro (remove decimais)
        num = int(float(value))
        # Formatar com zero à esquerda
        return f"{num:0{width}d}"
    except (ValueError, TypeError):
        return str(value)

@register.filter
def add(value, arg):
    """Concatena dois valores como strings"""
    try:
        return str(value) + str(arg)
    except (ValueError, TypeError):
        return str(value) + str(arg) if value else str(arg) 