#!/usr/bin/env python
"""
Script para verificar problemas de encoding em todo o sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, CargoFuncao, UsuarioFuncao
from django.db import connection

def verificar_encoding_usuarios():
    """Verifica problemas de encoding nos usuários"""
    print("🔍 Verificando encoding nos usuários...")
    
    usuarios_problematicos = []
    usuarios = User.objects.all()
    
    for usuario in usuarios:
        # Verificar first_name
        if usuario.first_name and any(ord(c) > 127 for c in usuario.first_name):
            usuarios_problematicos.append({
                'tipo': 'User',
                'id': usuario.id,
                'campo': 'first_name',
                'valor_atual': usuario.first_name,
                'username': usuario.username
            })
        
        # Verificar last_name
        if usuario.last_name and any(ord(c) > 127 for c in usuario.last_name):
            usuarios_problematicos.append({
                'tipo': 'User',
                'id': usuario.id,
                'campo': 'last_name',
                'valor_atual': usuario.last_name,
                'username': usuario.username
            })
    
    print(f"   Usuários com problemas: {len(usuarios_problematicos)}")
    return usuarios_problematicos

def verificar_encoding_militares():
    """Verifica problemas de encoding nos militares"""
    print("🔍 Verificando encoding nos militares...")
    
    militares_problematicos = []
    militares = Militar.objects.all()
    
    for militar in militares:
        # Verificar nome_completo
        if militar.nome_completo and any(ord(c) > 127 for c in militar.nome_completo):
            militares_problematicos.append({
                'tipo': 'Militar',
                'id': militar.id,
                'campo': 'nome_completo',
                'valor_atual': militar.nome_completo,
                'matricula': militar.matricula
            })
        
        # Verificar outros campos se necessário
        campos_texto = ['posto', 'quadro', 'especialidade']
        for campo in campos_texto:
            valor = getattr(militar, campo, None)
            if valor and any(ord(c) > 127 for c in str(valor)):
                militares_problematicos.append({
                    'tipo': 'Militar',
                    'id': militar.id,
                    'campo': campo,
                    'valor_atual': valor,
                    'matricula': militar.matricula
                })
    
    print(f"   Militares com problemas: {len(militares_problematicos)}")
    return militares_problematicos

def verificar_encoding_cargos():
    """Verifica problemas de encoding nos cargos/funções"""
    print("🔍 Verificando encoding nos cargos/funções...")
    
    cargos_problematicos = []
    cargos = CargoFuncao.objects.all()
    
    for cargo in cargos:
        # Verificar nome
        if cargo.nome and any(ord(c) > 127 for c in cargo.nome):
            cargos_problematicos.append({
                'tipo': 'CargoFuncao',
                'id': cargo.id,
                'campo': 'nome',
                'valor_atual': cargo.nome,
                'descricao': cargo.descricao
            })
        
        # Verificar descrição
        if cargo.descricao and any(ord(c) > 127 for c in cargo.descricao):
            cargos_problematicos.append({
                'tipo': 'CargoFuncao',
                'id': cargo.id,
                'campo': 'descricao',
                'valor_atual': cargo.descricao,
                'nome': cargo.nome
            })
    
    print(f"   Cargos com problemas: {len(cargos_problematicos)}")
    return cargos_problematicos

def verificar_encoding_comissoes():
    """Verifica problemas de encoding nas comissões"""
    print("🔍 Verificando encoding nas comissões...")
    
    # Como não temos o modelo Comissao, vamos pular esta verificação
    print("   Comissões: Modelo não disponível")
    return []

def main():
    """Função principal"""
    print("🚀 Verificando problemas de encoding em todo o sistema...")
    print("=" * 70)
    
    # Verificar cada modelo
    problemas_usuarios = verificar_encoding_usuarios()
    problemas_militares = verificar_encoding_militares()
    problemas_cargos = verificar_encoding_cargos()
    problemas_comissoes = verificar_encoding_comissoes()
    
    # Resumo
    total_problemas = len(problemas_usuarios) + len(problemas_militares) + len(problemas_cargos) + len(problemas_comissoes)
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS PROBLEMAS DE ENCODING:")
    print(f"   • Usuários: {len(problemas_usuarios)} problemas")
    print(f"   • Militares: {len(problemas_militares)} problemas")
    print(f"   • Cargos/Funções: {len(problemas_cargos)} problemas")
    print(f"   • Comissões: {len(problemas_comissoes)} problemas")
    print(f"   • TOTAL: {total_problemas} problemas encontrados")
    
    if total_problemas > 0:
        print("\n📋 AMOSTRAS DE PROBLEMAS:")
        todos_problemas = problemas_usuarios + problemas_militares + problemas_cargos + problemas_comissoes
        
        for i, problema in enumerate(todos_problemas[:10]):  # Mostrar apenas os primeiros 10
            print(f"   {i+1}. {problema['tipo']} ID {problema['id']} - {problema['campo']}: '{problema['valor_atual']}'")
        
        if len(todos_problemas) > 10:
            print(f"   ... e mais {len(todos_problemas) - 10} problemas")
    else:
        print("\n✅ Nenhum problema de encoding encontrado!")
    
    return {
        'usuarios': problemas_usuarios,
        'militares': problemas_militares,
        'cargos': problemas_cargos,
        'comissoes': problemas_comissoes,
        'total': total_problemas
    }

if __name__ == '__main__':
    main() 