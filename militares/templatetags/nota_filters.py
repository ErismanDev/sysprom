from django import template
from militares.models import Orgao, GrandeComando, Unidade, SubUnidade

register = template.Library()

@register.filter
def split_origem(value):
    """Divide a origem da publicação em partes separadas por ' - ' e substitui siglas por nomes completos do organograma"""
    if not value:
        return []
    
    print(f"DEBUG SPLIT_ORIGEM: Valor original: '{value}'")
    parts = value.split(' - ')
    print(f"DEBUG SPLIT_ORIGEM: Partes divididas: {parts}")
    processed_parts = []
    
    for i, part in enumerate(parts):
        part = part.strip()
        print(f"DEBUG SPLIT_ORIGEM: Processando parte {i}: '{part}'")
        
        # Se contém "/", processar separadamente
        if '/' in part:
            print(f"DEBUG SPLIT_ORIGEM: Parte {i} contém '/' - processando barra")
            partes_barra = part.split('/')
            print(f"DEBUG SPLIT_ORIGEM: Partes da barra: {partes_barra}")
            if len(partes_barra) >= 2:
                # Adicionar a unidade (parte após a barra) primeiro
                unidade_texto = partes_barra[1].strip()
                unidade_nome = buscar_nome_completo(unidade_texto)
                print(f"DEBUG SPLIT_ORIGEM: Adicionando unidade: '{unidade_nome}'")
                processed_parts.append(unidade_nome)
                
                # Adicionar a subunidade (parte antes da barra) depois
                subunidade_texto = partes_barra[0].strip()
                subunidade_nome = buscar_nome_completo(subunidade_texto)
                print(f"DEBUG SPLIT_ORIGEM: Adicionando subunidade: '{subunidade_nome}'")
                processed_parts.append(subunidade_nome)
            else:
                # Se só tem uma parte após a barra, usar ela
                nome_completo = buscar_nome_completo(partes_barra[0].strip())
                print(f"DEBUG SPLIT_ORIGEM: Adicionando parte única da barra: '{nome_completo}'")
                processed_parts.append(nome_completo)
        else:
            # Processar normalmente
            nome_completo = buscar_nome_completo(part)
            print(f"DEBUG SPLIT_ORIGEM: Adicionando parte normal: '{nome_completo}'")
            processed_parts.append(nome_completo)
    
    print(f"DEBUG SPLIT_ORIGEM: Resultado final: {processed_parts}")
    return processed_parts

@register.filter
def expandir_origem_simples(value):
    """Expande apenas as siglas da origem_publicacao, mantendo a estrutura original"""
    if not value:
        return value
    
    print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Valor original: '{value}'")
    
    # Dividir por ' - ' para processar cada parte
    partes = value.split(' - ')
    partes_expandidas = []
    
    for parte in partes:
        parte = parte.strip()
        print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Processando parte: '{parte}'")
        
        # Ignorar partes que contenham "do" ou "da" (versões por extenso como "1º Subgrupamento do 3º Grupamento")
        if ' do ' in parte.lower() or ' da ' in parte.lower():
            print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Parte contém 'do'/'da' (versão por extenso) - ignorando: '{parte}'")
            continue
        
        # Se contém "/", processar separadamente
        if '/' in parte:
            print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Parte contém '/' - processando barra")
            partes_barra = parte.split('/')
            if len(partes_barra) >= 2:
                # Expandir unidade (parte após a barra)
                unidade_texto = partes_barra[1].strip()
                unidade_nome = buscar_nome_completo(unidade_texto)
                print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Unidade expandida: '{unidade_nome}'")
                
                # Expandir subunidade (parte antes da barra)
                subunidade_texto = partes_barra[0].strip()
                subunidade_nome = buscar_nome_completo(subunidade_texto)
                print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Subunidade expandida: '{subunidade_nome}'")
                
                # Verificar se a unidade já foi adicionada anteriormente
                unidade_ja_existe = False
                for parte_existente in partes_expandidas:
                    if unidade_nome in parte_existente or parte_existente in unidade_nome:
                        unidade_ja_existe = True
                        print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Unidade já existe: '{unidade_nome}' - não adicionando")
                        break
                
                # Adicionar unidade apenas se não existir
                if not unidade_ja_existe:
                    partes_expandidas.append(unidade_nome)
                    print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Adicionando unidade: '{unidade_nome}'")
                
                # Adicionar subunidade
                partes_expandidas.append(subunidade_nome)
                print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Adicionando subunidade: '{subunidade_nome}'")
                # NÃO adicionar a parte original com "/" - já adicionamos as partes separadas
            else:
                # Se só tem uma parte após a barra, expandir ela
                nome_completo = buscar_nome_completo(partes_barra[0].strip())
                print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Parte única expandida: '{nome_completo}'")
                partes_expandidas.append(nome_completo)
        else:
            # Processar normalmente
            nome_completo = buscar_nome_completo(parte)
            print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Parte normal expandida: '{nome_completo}'")
            partes_expandidas.append(nome_completo)
    
    resultado = '<br>'.join(partes_expandidas)
    print(f"DEBUG EXPANDIR_ORIGEM_SIMPLES: Resultado final: '{resultado}'")
    return resultado

def buscar_nome_completo(part):
    """Busca o nome completo no organograma"""
    nome_completo = part  # Mantém o original por padrão
    
    # Busca no organograma por sigla ou nome
    try:
        # Busca em órgãos
        orgao = Orgao.objects.filter(sigla=part).first()
        if orgao:
            nome_completo = orgao.nome.upper()
        else:
            # Busca em grandes comandos
            gc = GrandeComando.objects.filter(sigla=part).first()
            if gc:
                nome_completo = gc.nome.upper()
            else:
                # Busca em unidades
                unidade = Unidade.objects.filter(sigla=part).first()
                if unidade:
                    nome_completo = unidade.nome.upper()
                else:
                    # Busca em subunidades - primeiro exata, depois por contém
                    subunidade = SubUnidade.objects.filter(sigla=part).first()
                    if subunidade:
                        nome_completo = subunidade.nome.upper()
                    else:
                        # Busca por contém (para casos como "1º SGBM" em "1º SGBM/3º GBM")
                        subunidade_contem = SubUnidade.objects.filter(sigla__icontains=part).first()
                        if subunidade_contem:
                            # Extrair apenas a parte relevante do nome
                            nome_completo = subunidade_contem.nome.upper()
                            # Se o nome contém "do", pegar apenas a parte antes do "do" + "DE BOMBEIROS MILITAR"
                            if ' DO ' in nome_completo:
                                parte_antes_do = nome_completo.split(' DO ')[0]
                                # Adicionar "DE BOMBEIROS MILITAR" se não tiver
                                if 'DE BOMBEIROS MILITAR' not in parte_antes_do:
                                    nome_completo = parte_antes_do + ' DE BOMBEIROS MILITAR'
                                else:
                                    nome_completo = parte_antes_do
    except:
        # Se houver erro na consulta, mantém o original em maiúsculas
        nome_completo = part.upper()
    
    return nome_completo

@register.filter
def get_origem_part(value, index):
    """Retorna uma parte específica da origem dividida com nome completo do organograma"""
    if not value:
        return ''
    parts = value.split(' - ')
    if 0 <= index < len(parts):
        part = parts[index].strip()
        
        # Busca no organograma
        try:
            # Busca em órgãos
            orgao = Orgao.objects.filter(sigla=part).first()
            if orgao:
                return orgao.nome.upper()
            
            # Busca em grandes comandos
            gc = GrandeComando.objects.filter(sigla=part).first()
            if gc:
                return gc.nome.upper()
            
            # Busca em unidades
            unidade = Unidade.objects.filter(sigla=part).first()
            if unidade:
                return unidade.nome.upper()
            
            # Busca em subunidades
            subunidade = SubUnidade.objects.filter(sigla=part).first()
            if subunidade:
                return subunidade.nome.upper()
        except:
            pass
        
        return part.upper()
    return ''


@register.filter
def lookup(dictionary, key):
    """Filtro para acessar um dicionário por chave"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return None
