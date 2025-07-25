#!/usr/bin/env python
"""
Script para verificar apenas caracteres realmente corrompidos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, CargoFuncao, UsuarioFuncao

def verificar_caracteres_corrompidos():
    """Verifica apenas caracteres realmente corrompidos"""
    print("🔍 Verificando caracteres realmente corrompidos...")
    print("=" * 60)
    
    # Caracteres que indicam corrupção real
    caracteres_corrompidos = ['ß', 'Ò', 'þ', '§', 'Û', 'Ü', 'Ý', 'Þ']
    
    problemas_encontrados = []
    
    # Verificar usuários
    print("🔍 Verificando usuários...")
    usuarios = User.objects.all()
    for usuario in usuarios:
        if usuario.first_name and any(c in usuario.first_name for c in caracteres_corrompidos):
            problemas_encontrados.append({
                'tipo': 'User',
                'id': usuario.id,
                'campo': 'first_name',
                'valor': usuario.first_name,
                'username': usuario.username
            })
        
        if usuario.last_name and any(c in usuario.last_name for c in caracteres_corrompidos):
            problemas_encontrados.append({
                'tipo': 'User',
                'id': usuario.id,
                'campo': 'last_name',
                'valor': usuario.last_name,
                'username': usuario.username
            })
    
    # Verificar cargos
    print("🔍 Verificando cargos...")
    cargos = CargoFuncao.objects.all()
    for cargo in cargos:
        if cargo.nome and any(c in cargo.nome for c in caracteres_corrompidos):
            problemas_encontrados.append({
                'tipo': 'CargoFuncao',
                'id': cargo.id,
                'campo': 'nome',
                'valor': cargo.nome,
                'descricao': cargo.descricao
            })
        
        if cargo.descricao and any(c in cargo.descricao for c in caracteres_corrompidos):
            problemas_encontrados.append({
                'tipo': 'CargoFuncao',
                'id': cargo.id,
                'campo': 'descricao',
                'valor': cargo.descricao,
                'nome': cargo.nome
            })
    
    # Verificar militares
    print("🔍 Verificando militares...")
    militares = Militar.objects.all()
    for militar in militares:
        if militar.nome_completo and any(c in militar.nome_completo for c in caracteres_corrompidos):
            problemas_encontrados.append({
                'tipo': 'Militar',
                'id': militar.id,
                'campo': 'nome_completo',
                'valor': militar.nome_completo,
                'matricula': militar.matricula
            })
    
    print(f"\n📊 PROBLEMAS REAIS ENCONTRADOS: {len(problemas_encontrados)}")
    
    if problemas_encontrados:
        print("\n📋 Detalhes dos problemas:")
        for i, problema in enumerate(problemas_encontrados[:10]):
            print(f"   {i+1}. {problema['tipo']} ID {problema['id']} - {problema['campo']}: '{problema['valor']}'")
        
        if len(problemas_encontrados) > 10:
            print(f"   ... e mais {len(problemas_encontrados) - 10} problemas")
    else:
        print("\n✅ Nenhum caractere corrompido encontrado!")
    
    return problemas_encontrados

def verificar_cargos_finais():
    """Verifica o estado final dos cargos"""
    print("\n🔍 Verificando estado final dos cargos...")
    print("=" * 60)
    
    cargos = CargoFuncao.objects.all().order_by('nome')
    print("📋 Lista completa dos cargos:")
    
    for cargo in cargos:
        print(f"   • {cargo.nome}")
        if cargo.descricao:
            print(f"     Descrição: {cargo.descricao}")
    
    print(f"\n📊 Total de cargos: {cargos.count()}")

def main():
    """Função principal"""
    problemas = verificar_caracteres_corrompidos()
    verificar_cargos_finais()
    
    if not problemas:
        print("\n🎉 SISTEMA LIVRE DE CARACTERES CORROMPIDOS!")
    else:
        print(f"\n⚠️  Ainda existem {len(problemas)} problemas de encoding")

if __name__ == '__main__':
    main() 