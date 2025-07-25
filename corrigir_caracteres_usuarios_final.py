#!/usr/bin/env python
"""
Script final para corrigir caracteres problemáticos restantes nos usuários
"""

import os
import sys
import django
import unicodedata
import re
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import connection

def normalizar_caracteres_avancado(texto):
    """
    Normalização avançada de caracteres especiais
    """
    if not texto:
        return texto
    
    # Converter para string se não for
    texto = str(texto)
    
    # Normalizar caracteres Unicode (NFC = composição)
    texto = unicodedata.normalize('NFC', texto)
    
    # Mapeamento específico de caracteres problemáticos encontrados
    substituicoes_especificas = {
        # Caracteres de acentuação isolados (combining characters)
        '\u0300': 'à',  # grave accent
        '\u0301': 'á',  # acute accent
        '\u0302': 'â',  # circumflex
        '\u0303': 'ã',  # tilde
        '\u0308': 'ä',  # diaeresis
        '\u0327': 'ç',  # cedilla
        
        # Caracteres corrompidos específicos encontrados
        'ß': 'ss',
        'þ': 'th',
        '·': ' ',
        '├': 'a',
        '┴': 'a',
        '╩': 'a',
        'Ò': 'O',
        'Ý': 'Y',
        'Ú': 'U',
        
        # Caracteres de controle e símbolos estranhos
        '\u00B7': ' ',  # middle dot
        '\u251C': 'a',  # box drawing
        '\u2534': 'a',  # box drawing
        '\u2569': 'a',  # box drawing
        '\u00FE': 'th', # thorn
        '\u00DD': 'Y',  # Y with acute
        '\u00DF': 'ss', # sharp s
    }
    
    # Aplicar substituições específicas
    for char_antigo, char_novo in substituicoes_especificas.items():
        texto = texto.replace(char_antigo, char_novo)
    
    # Corrigir combinações de caracteres de acentuação
    # Padrões comuns de caracteres de acentuação isolados
    padroes_acentuacao = [
        (r'a\u0300', 'à'),
        (r'a\u0301', 'á'),
        (r'a\u0302', 'â'),
        (r'a\u0303', 'ã'),
        (r'a\u0308', 'ä'),
        (r'e\u0300', 'è'),
        (r'e\u0301', 'é'),
        (r'e\u0302', 'ê'),
        (r'e\u0308', 'ë'),
        (r'i\u0300', 'ì'),
        (r'i\u0301', 'í'),
        (r'i\u0302', 'î'),
        (r'i\u0308', 'ï'),
        (r'o\u0300', 'ò'),
        (r'o\u0301', 'ó'),
        (r'o\u0302', 'ô'),
        (r'o\u0303', 'õ'),
        (r'o\u0308', 'ö'),
        (r'u\u0300', 'ù'),
        (r'u\u0301', 'ú'),
        (r'u\u0302', 'û'),
        (r'u\u0308', 'ü'),
        (r'c\u0327', 'ç'),
        (r'n\u0303', 'ñ'),
        (r'y\u0301', 'ý'),
        (r'A\u0300', 'À'),
        (r'A\u0301', 'Á'),
        (r'A\u0302', 'Â'),
        (r'A\u0303', 'Ã'),
        (r'A\u0308', 'Ä'),
        (r'E\u0300', 'È'),
        (r'E\u0301', 'É'),
        (r'E\u0302', 'Ê'),
        (r'E\u0308', 'Ë'),
        (r'I\u0300', 'Ì'),
        (r'I\u0301', 'Í'),
        (r'I\u0302', 'Î'),
        (r'I\u0308', 'Ï'),
        (r'O\u0300', 'Ò'),
        (r'O\u0301', 'Ó'),
        (r'O\u0302', 'Ô'),
        (r'O\u0303', 'Õ'),
        (r'O\u0308', 'Ö'),
        (r'U\u0300', 'Ù'),
        (r'U\u0301', 'Ú'),
        (r'U\u0302', 'Û'),
        (r'U\u0308', 'Ü'),
        (r'C\u0327', 'Ç'),
        (r'N\u0303', 'Ñ'),
        (r'Y\u0301', 'Ý'),
    ]
    
    # Aplicar padrões de acentuação
    for padrao, substituicao in padroes_acentuacao:
        texto = re.sub(padrao, substituicao, texto)
    
    # Remover caracteres de controle restantes
    texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texto)
    
    # Normalizar espaços
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    
    return texto

def corrigir_usuarios_especificos():
    """
    Corrige usuários com problemas específicos identificados
    """
    print("🔧 Corrigindo usuários com problemas específicos...")
    
    # Lista de correções específicas baseadas nos problemas encontrados
    correcoes_especificas = [
        # ID, campo, valor_corrigido
        (1031, 'first_name', 'Usuário'),
        (32, 'last_name', 'Magalhães Silva'),
        (35, 'last_name', 'Patrício Cavalcante SEIXAS'),
        (39, 'first_name', 'Moisés'),
        (39, 'last_name', 'Andrade Fernandes CANTUÁRIO'),
        (52, 'last_name', 'José de Melo LIMA'),
        (78, 'first_name', 'José'),
        (79, 'first_name', 'José'),
        (80, 'first_name', 'José'),
        (82, 'first_name', 'Luís'),
        (87, 'last_name', 'José da Silva Santos'),
        (17, 'last_name', 'Super Usuário'),  # superusuario
        (23, 'last_name', 'Alex Gonçalves ALMENDRA'),
        (24, 'last_name', 'CHARLES Ivonor de Sousa Araújo'),
        (27, 'last_name', 'Diego FREIRE de Araújo'),
        (34, 'last_name', 'Jardson Viana FALCÃO'),
        (37, 'last_name', 'Lamartine LAVOZIA Aborgazan Barreto'),
        (38, 'last_name', 'MAYLSON Damasceno Mariscal de Araújo'),
    ]
    
    total_corrigidos = 0
    erros = []
    
    for usuario_id, campo, valor_corrigido in correcoes_especificas:
        try:
            usuario = User.objects.get(id=usuario_id)
            
            if campo == 'first_name':
                usuario.first_name = valor_corrigido
            elif campo == 'last_name':
                usuario.last_name = valor_corrigido
            
            usuario.save()
            total_corrigidos += 1
            print(f"  ✅ Usuário ID {usuario_id} - {campo} corrigido para '{valor_corrigido}'")
            
        except User.DoesNotExist:
            erro_msg = f"Usuário ID {usuario_id} não encontrado"
            erros.append(erro_msg)
            print(f"  ❌ {erro_msg}")
        except Exception as e:
            erro_msg = f"Erro ao corrigir usuário ID {usuario_id}: {e}"
            erros.append(erro_msg)
            print(f"  ❌ {erro_msg}")
    
    print(f"\n✅ Correções específicas concluídas!")
    print(f"📊 Usuários corrigidos: {total_corrigidos}")
    print(f"❌ Erros: {len(erros)}")
    
    return total_corrigidos

def corrigir_caracteres_automatico():
    """
    Corrige caracteres automaticamente usando normalização avançada
    """
    print("🔧 Aplicando correção automática de caracteres...")
    
    usuarios = User.objects.all()
    total_corrigidos = 0
    erros = []
    
    for usuario in usuarios:
        try:
            alterado = False
            
            # Corrigir first_name
            if usuario.first_name:
                nome_original = usuario.first_name
                nome_corrigido = normalizar_caracteres_avancado(nome_original)
                if nome_original != nome_corrigido:
                    usuario.first_name = nome_corrigido
                    alterado = True
            
            # Corrigir last_name
            if usuario.last_name:
                nome_original = usuario.last_name
                nome_corrigido = normalizar_caracteres_avancado(nome_original)
                if nome_original != nome_corrigido:
                    usuario.last_name = nome_corrigido
                    alterado = True
            
            # Corrigir username (com cuidado para não duplicar)
            if usuario.username:
                username_original = usuario.username
                username_corrigido = normalizar_caracteres_avancado(username_original)
                if username_original != username_corrigido:
                    # Verificar se o username corrigido já existe
                    if User.objects.filter(username=username_corrigido).exclude(id=usuario.id).exists():
                        print(f"  ⚠️  Usuário ID {usuario.id}: username '{username_corrigido}' já existe, mantendo original")
                    else:
                        usuario.username = username_corrigido
                        alterado = True
            
            # Corrigir email
            if usuario.email:
                email_original = usuario.email
                email_corrigido = normalizar_caracteres_avancado(email_original)
                if email_original != email_corrigido:
                    # Verificar se o email corrigido já existe
                    if User.objects.filter(email=email_corrigido).exclude(id=usuario.id).exists():
                        print(f"  ⚠️  Usuário ID {usuario.id}: email '{email_corrigido}' já existe, mantendo original")
                    else:
                        usuario.email = email_corrigido
                        alterado = True
            
            if alterado:
                usuario.save()
                total_corrigidos += 1
                print(f"  ✅ Usuário ID {usuario.id} ({usuario.username}) corrigido automaticamente")
                
        except Exception as e:
            erro_msg = f"Erro ao corrigir usuário ID {usuario.id}: {e}"
            erros.append(erro_msg)
            print(f"  ❌ {erro_msg}")
            continue
    
    print(f"\n✅ Correção automática concluída!")
    print(f"📊 Usuários corrigidos: {total_corrigidos}")
    print(f"❌ Erros: {len(erros)}")
    
    return total_corrigidos

def verificar_resultado_final():
    """
    Verifica o resultado final após todas as correções
    """
    print("🔍 Verificando resultado final...")
    
    usuarios = User.objects.all()
    caracteres_problematicos = []
    
    for usuario in usuarios:
        nome_completo = usuario.get_full_name()
        
        # Verificar se há caracteres problemáticos
        for i, char in enumerate(nome_completo):
            if ord(char) > 127:  # Caracteres não-ASCII
                # Verificar se é um caractere válido (acentos, cedilha, etc.)
                if char not in 'àáâãäåçèéêëìíîïñòóôõöùúûüýÿÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝ':
                    caracteres_problematicos.append({
                        'usuario_id': usuario.id,
                        'username': usuario.username,
                        'nome_completo': nome_completo,
                        'caractere_problematico': char,
                        'posicao': i
                    })
    
    print(f"📊 Total de usuários verificados: {len(usuarios)}")
    print(f"⚠️  Usuários com caracteres problemáticos restantes: {len(caracteres_problematicos)}")
    
    if caracteres_problematicos:
        print("\n📋 Usuários com problemas restantes:")
        for i, problema in enumerate(caracteres_problematicos[:10]):
            print(f"  {i+1}. ID {problema['usuario_id']} - {problema['username']}")
            print(f"     Nome: '{problema['nome_completo']}'")
            print(f"     Caractere problemático: '{problema['caractere_problematico']}' na posição {problema['posicao']}")
    else:
        print("✅ Nenhum caractere problemático restante encontrado!")
    
    return caracteres_problematicos

def main():
    """
    Função principal
    """
    print("🚀 Iniciando correção final de caracteres na tabela de usuários...")
    print("=" * 70)
    
    # Aplicar correções específicas
    corrigir_usuarios_especificos()
    print()
    
    # Aplicar correção automática
    corrigir_caracteres_automatico()
    print()
    
    # Verificar resultado final
    problemas_restantes = verificar_resultado_final()
    print()
    
    print("=" * 70)
    print("🏁 Processo de correção final concluído!")
    
    if not problemas_restantes:
        print("✅ Todos os problemas de caracteres foram corrigidos com sucesso!")
    else:
        print(f"⚠️  Ainda restam {len(problemas_restantes)} problemas de caracteres")
        print("💡 Recomendação: Verificar manualmente os casos restantes")

if __name__ == '__main__':
    main() 