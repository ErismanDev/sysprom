#!/usr/bin/env python
"""
Script para importar tabelas simples sem dependências complexas
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import (
    CargoComissao, CargoFuncao, CalendarioPromocao, AlmanaqueMilitar,
    Intersticio, VagaManual
)

def importar_tabelas_simples():
    """Importa tabelas simples sem dependências complexas"""
    
    print("🔧 Importando tabelas simples...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Tabelas simples para importar
    tabelas_simples = {
        'militares.cargocomissao': CargoComissao,
        'militares.cargofuncao': CargoFuncao,
        'militares.calendariopromocao': CalendarioPromocao,
        'militares.almanaquemilitar': AlmanaqueMilitar,
        'militares.intersticio': Intersticio,
        'militares.vagamanual': VagaManual,
    }
    
    # Filtrar dados por modelo
    dados_por_modelo = {}
    for item in dados:
        modelo = item['model']
        if modelo in tabelas_simples:
            if modelo not in dados_por_modelo:
                dados_por_modelo[modelo] = []
            dados_por_modelo[modelo].append(item)
    
    # Estatísticas
    total_importados = 0
    erros_por_modelo = {}
    
    print(f"📊 Tabelas simples encontradas:")
    for modelo, items in dados_por_modelo.items():
        print(f"  - {modelo}: {len(items)} itens")
    
    # Importar cada modelo
    for modelo, items in dados_por_modelo.items():
        print(f"\n🔧 Importando {modelo}...")
        
        modelo_class = tabelas_simples[modelo]
        importados = 0
        erros = []
        
        for i, item in enumerate(items, 1):
            try:
                fields = item['fields']
                
                # Criar objeto
                obj = modelo_class.objects.create(**fields)
                importados += 1
                
                if i % 10 == 0:
                    print(f"  ✅ {i}/{len(items)} importados...")
                    
            except Exception as e:
                erro_msg = f"Erro no item {i}: {e}"
                erros.append(erro_msg)
                print(f"  ❌ {erro_msg}")
                continue
        
        total_importados += importados
        erros_por_modelo[modelo] = erros
        
        print(f"  ✅ {modelo}: {importados}/{len(items)} importados")
        if erros:
            print(f"  ❌ {len(erros)} erros")
    
    # Relatório final
    print(f"\n🎉 Importação de tabelas simples concluída!")
    print(f"📊 Total de itens importados: {total_importados}")
    
    total_erros = sum(len(erros) for erros in erros_por_modelo.values())
    print(f"❌ Total de erros: {total_erros}")
    
    if total_erros > 0:
        print(f"\n📋 Erros por modelo:")
        for modelo, erros in erros_por_modelo.items():
            if erros:
                print(f"  - {modelo}: {len(erros)} erros")
    
    return total_importados

def importar_cargos_funcoes():
    """Importa cargos e funções especificamente"""
    
    print("\n🔧 Importando cargos e funções...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar cargos e funções
    cargos_comissao = [item for item in dados if item['model'] == 'militares.cargocomissao']
    cargos_funcao = [item for item in dados if item['model'] == 'militares.cargofuncao']
    
    print(f"📊 Cargos de comissão encontrados: {len(cargos_comissao)}")
    print(f"📊 Cargos de função encontrados: {len(cargos_funcao)}")
    
    # Importar cargos de comissão
    importados_comissao = 0
    for item in cargos_comissao:
        try:
            fields = item['fields']
            cargo = CargoComissao.objects.create(**fields)
            importados_comissao += 1
        except Exception as e:
            print(f"❌ Erro ao importar cargo de comissão: {e}")
    
    # Importar cargos de função
    importados_funcao = 0
    for item in cargos_funcao:
        try:
            fields = item['fields']
            cargo = CargoFuncao.objects.create(**fields)
            importados_funcao += 1
        except Exception as e:
            print(f"❌ Erro ao importar cargo de função: {e}")
    
    print(f"✅ Cargos de comissão importados: {importados_comissao}")
    print(f"✅ Cargos de função importados: {importados_funcao}")
    
    return importados_comissao + importados_funcao

def importar_calendarios_almanaques():
    """Importa calendários e almanaques"""
    
    print("\n🔧 Importando calendários e almanaques...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar calendários e almanaques
    calendarios = [item for item in dados if item['model'] == 'militares.calendariopromocao']
    almanaques = [item for item in dados if item['model'] == 'militares.almanaquemilitar']
    
    print(f"📊 Calendários encontrados: {len(calendarios)}")
    print(f"📊 Almanaques encontrados: {len(almanaques)}")
    
    # Importar calendários
    importados_calendarios = 0
    for item in calendarios:
        try:
            fields = item['fields']
            calendario = CalendarioPromocao.objects.create(**fields)
            importados_calendarios += 1
        except Exception as e:
            print(f"❌ Erro ao importar calendário: {e}")
    
    # Importar almanaques
    importados_almanaques = 0
    for item in almanaques:
        try:
            fields = item['fields']
            almanaque = AlmanaqueMilitar.objects.create(**fields)
            importados_almanaques += 1
        except Exception as e:
            print(f"❌ Erro ao importar almanaque: {e}")
    
    print(f"✅ Calendários importados: {importados_calendarios}")
    print(f"✅ Almanaques importados: {importados_almanaques}")
    
    return importados_calendarios + importados_almanaques

if __name__ == "__main__":
    print("🚀 Iniciando importação de tabelas simples")
    print("=" * 50)
    
    # Importar tabelas simples
    total_geral = importar_tabelas_simples()
    
    # Importar cargos e funções
    cargos_importados = importar_cargos_funcoes()
    
    # Importar calendários e almanaques
    calendarios_importados = importar_calendarios_almanaques()
    
    print(f"\n🎉 Processo concluído!")
    print(f"📊 Total geral de itens importados: {total_geral + cargos_importados + calendarios_importados}")
    print(f"📋 Cargos e funções: {cargos_importados}")
    print(f"📋 Calendários e almanaques: {calendarios_importados}") 