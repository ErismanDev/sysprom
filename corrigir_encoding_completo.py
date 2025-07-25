#!/usr/bin/env python
"""
Script para corrigir todos os problemas de encoding no sistema
"""

import os
import sys
import django
import unicodedata
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, CargoFuncao, UsuarioFuncao
from django.db import transaction

def normalizar_texto(texto):
    """
    Normaliza texto removendo caracteres especiais e acentos
    """
    if not texto:
        return ""
    
    # Normalizar unicode
    texto = unicodedata.normalize('NFD', texto)
    
    # Remover acentos
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    
    return texto

def corrigir_caractere_especial(texto):
    """
    Corrige caracteres especiais comuns
    """
    if not texto:
        return texto
    
    # Mapeamento de caracteres corrompidos para corretos
    correcoes = {
        'ß': 'á',
        'Ò': 'ã',
        'þ': 'ç',
        '§': 'õ',
        'Û': 'ú',
        'Ü': 'ü',
        'Ý': 'ý',
        'Þ': 'þ',
        'à': 'à',
        'á': 'á',
        'â': 'â',
        'ã': 'ã',
        'ä': 'ä',
        'å': 'å',
        'ç': 'ç',
        'è': 'è',
        'é': 'é',
        'ê': 'ê',
        'ë': 'ë',
        'ì': 'ì',
        'í': 'í',
        'î': 'î',
        'ï': 'ï',
        'ñ': 'ñ',
        'ò': 'ò',
        'ó': 'ó',
        'ô': 'ô',
        'õ': 'õ',
        'ö': 'ö',
        'ù': 'ù',
        'ú': 'ú',
        'û': 'û',
        'ü': 'ü',
        'ý': 'ý',
        'ÿ': 'ÿ',
        'À': 'À',
        'Á': 'Á',
        'Â': 'Â',
        'Ã': 'Ã',
        'Ä': 'Ä',
        'Ç': 'Ç',
        'È': 'È',
        'É': 'É',
        'Ê': 'Ê',
        'Ë': 'Ë',
        'Ì': 'Ì',
        'Í': 'Í',
        'Î': 'Î',
        'Ï': 'Ï',
        'Ñ': 'Ñ',
        'Ò': 'Ò',
        'Ó': 'Ó',
        'Ô': 'Ô',
        'Õ': 'Õ',
        'Ö': 'Ö',
        'Ù': 'Ù',
        'Ú': 'Ú',
        'Û': 'Û',
        'Ü': 'Ü',
        'Ý': 'Ý'
    }
    
    texto_corrigido = texto
    for caractere_errado, caractere_correto in correcoes.items():
        texto_corrigido = texto_corrigido.replace(caractere_errado, caractere_correto)
    
    return texto_corrigido

def corrigir_encoding_usuarios():
    """Corrige problemas de encoding nos usuários"""
    print("🔧 Corrigindo encoding nos usuários...")
    
    usuarios_corrigidos = 0
    usuarios = User.objects.all()
    
    for usuario in usuarios:
        corrigido = False
        
        # Corrigir first_name
        if usuario.first_name:
            nome_corrigido = corrigir_caractere_especial(usuario.first_name)
            if nome_corrigido != usuario.first_name:
                usuario.first_name = nome_corrigido
                corrigido = True
        
        # Corrigir last_name
        if usuario.last_name:
            sobrenome_corrigido = corrigir_caractere_especial(usuario.last_name)
            if sobrenome_corrigido != usuario.last_name:
                usuario.last_name = sobrenome_corrigido
                corrigido = True
        
        if corrigido:
            usuario.save()
            usuarios_corrigidos += 1
    
    print(f"   ✅ {usuarios_corrigidos} usuários corrigidos")
    return usuarios_corrigidos

def corrigir_encoding_cargos():
    """Corrige problemas de encoding nos cargos/funções"""
    print("🔧 Corrigindo encoding nos cargos/funções...")
    
    cargos_corrigidos = 0
    cargos = CargoFuncao.objects.all()
    
    for cargo in cargos:
        corrigido = False
        
        # Corrigir nome
        if cargo.nome:
            nome_corrigido = corrigir_caractere_especial(cargo.nome)
            if nome_corrigido != cargo.nome:
                cargo.nome = nome_corrigido
                corrigido = True
        
        # Corrigir descrição
        if cargo.descricao:
            descricao_corrigida = corrigir_caractere_especial(cargo.descricao)
            if descricao_corrigida != cargo.descricao:
                cargo.descricao = descricao_corrigida
                corrigido = True
        
        if corrigido:
            cargo.save()
            cargos_corrigidos += 1
    
    print(f"   ✅ {cargos_corrigidos} cargos corrigidos")
    return cargos_corrigidos

def corrigir_encoding_militares():
    """Corrige problemas de encoding nos militares"""
    print("🔧 Corrigindo encoding nos militares...")
    
    militares_corrigidos = 0
    militares = Militar.objects.all()
    
    for militar in militares:
        corrigido = False
        
        # Corrigir nome_completo
        if militar.nome_completo:
            nome_corrigido = corrigir_caractere_especial(militar.nome_completo)
            if nome_corrigido != militar.nome_completo:
                militar.nome_completo = nome_corrigido
                corrigido = True
        
        # Corrigir outros campos
        campos_texto = ['posto', 'quadro', 'especialidade']
        for campo in campos_texto:
            valor = getattr(militar, campo, None)
            if valor:
                valor_corrigido = corrigir_caractere_especial(str(valor))
                if valor_corrigido != str(valor):
                    setattr(militar, campo, valor_corrigido)
                    corrigido = True
        
        if corrigido:
            militar.save()
            militares_corrigidos += 1
    
    print(f"   ✅ {militares_corrigidos} militares corrigidos")
    return militares_corrigidos

def main():
    """Função principal"""
    print("🚀 Corrigindo problemas de encoding em todo o sistema...")
    print("=" * 70)
    
    with transaction.atomic():
        # Corrigir cada modelo
        usuarios_corrigidos = corrigir_encoding_usuarios()
        cargos_corrigidos = corrigir_encoding_cargos()
        militares_corrigidos = corrigir_encoding_militares()
        
        total_corrigidos = usuarios_corrigidos + cargos_corrigidos + militares_corrigidos
        
        print("\n" + "=" * 70)
        print("📊 RESUMO DAS CORREÇÕES:")
        print(f"   • Usuários corrigidos: {usuarios_corrigidos}")
        print(f"   • Cargos/Funções corrigidos: {cargos_corrigidos}")
        print(f"   • Militares corrigidos: {militares_corrigidos}")
        print(f"   • TOTAL: {total_corrigidos} registros corrigidos")
        
        if total_corrigidos > 0:
            print("\n✅ Correções aplicadas com sucesso!")
        else:
            print("\n✅ Nenhuma correção necessária!")
    
    # Verificação final
    print("\n🔍 Executando verificação final...")
    os.system("python verificar_encoding_sistema.py")

if __name__ == '__main__':
    main() 