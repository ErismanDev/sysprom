#!/usr/bin/env python
"""
Script para importar outras tabelas do sistema (funções, cargos, permissões, etc.)
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
    CargoComissao, CargoFuncao, UsuarioFuncao, PermissaoFuncao, 
    PerfilAcesso, CalendarioPromocao, AlmanaqueMilitar, AssinaturaAlmanaque,
    QuadroAcesso, ItemQuadroAcesso, Promocao, ComissaoPromocao, 
    MembroComissao, SessaoComissao, DeliberacaoComissao, VotoDeliberacao,
    PrevisaoVaga, QuadroFixacaoVagas, ItemQuadroFixacaoVagas,
    AssinaturaQuadroFixacaoVagas, FichaConceitoOficiais, FichaConceitoPracas,
    Documento, Intersticio, NotificacaoSessao, VagaManual
)
from django.contrib.auth.models import User

def importar_outras_tabelas():
    """Importa outras tabelas do sistema"""
    
    print("🔧 Importando outras tabelas do sistema...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Mapear modelos para importar
    modelos_para_importar = {
        'militares.cargocomissao': CargoComissao,
        'militares.cargofuncao': CargoFuncao,
        'militares.usuariofuncao': UsuarioFuncao,
        'militares.permissaofuncao': PermissaoFuncao,
        'militares.perfilacesso': PerfilAcesso,
        'militares.calendariopromocao': CalendarioPromocao,
        'militares.almanaquemilitar': AlmanaqueMilitar,
        'militares.assinaturaalmanaque': AssinaturaAlmanaque,
        'militares.quadroacesso': QuadroAcesso,
        'militares.itemquadroacesso': ItemQuadroAcesso,
        'militares.promocao': Promocao,
        'militares.comissaopromocao': ComissaoPromocao,
        'militares.membrocomissao': MembroComissao,
        'militares.sessaocomissao': SessaoComissao,
        'militares.deliberacaocomissao': DeliberacaoComissao,
        'militares.votodeliberacao': VotoDeliberacao,
        'militares.previsaovaga': PrevisaoVaga,
        'militares.quadrofixacaovagas': QuadroFixacaoVagas,
        'militares.itemquadrofixacaovagas': ItemQuadroFixacaoVagas,
        'militares.assinaturaquadrofixacaovagas': AssinaturaQuadroFixacaoVagas,
        'militares.fichaconceitoficiais': FichaConceitoOficiais,
        'militares.fichaconceitopracas': FichaConceitoPracas,
        'militares.documento': Documento,
        'militares.intersticio': Intersticio,
        'militares.notificacaosessao': NotificacaoSessao,
        'militares.vagamanual': VagaManual,
    }
    
    # Filtrar dados por modelo
    dados_por_modelo = {}
    for item in dados:
        modelo = item['model']
        if modelo in modelos_para_importar:
            if modelo not in dados_por_modelo:
                dados_por_modelo[modelo] = []
            dados_por_modelo[modelo].append(item)
    
    # Estatísticas
    total_importados = 0
    erros_por_modelo = {}
    
    print(f"📊 Modelos encontrados para importar:")
    for modelo, items in dados_por_modelo.items():
        print(f"  - {modelo}: {len(items)} itens")
    
    # Importar cada modelo
    for modelo, items in dados_por_modelo.items():
        print(f"\n🔧 Importando {modelo}...")
        
        modelo_class = modelos_para_importar[modelo]
        importados = 0
        erros = []
        
        for i, item in enumerate(items, 1):
            try:
                fields = item['fields']
                
                # Remover campos que podem causar problemas
                campos_remover = ['user', 'militar', 'quadro_acesso', 'comissao', 'sessao', 
                                'deliberacao', 'previsao_vaga', 'quadro_fixacao_vagas', 
                                'almanaque', 'calendario', 'cargo_funcao', 'usuario']
                
                for campo in campos_remover:
                    if campo in fields:
                        del fields[campo]
                
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
    print(f"\n🎉 Importação concluída!")
    print(f"📊 Total de itens importados: {total_importados}")
    
    total_erros = sum(len(erros) for erros in erros_por_modelo.values())
    print(f"❌ Total de erros: {total_erros}")
    
    if total_erros > 0:
        print(f"\n📋 Erros por modelo:")
        for modelo, erros in erros_por_modelo.items():
            if erros:
                print(f"  - {modelo}: {len(erros)} erros")
                for erro in erros[:3]:  # Mostrar apenas os 3 primeiros erros
                    print(f"    * {erro}")
    
    return total_importados

def importar_fichas_conceito():
    """Importa fichas de conceito especificamente"""
    
    print("\n🔧 Importando fichas de conceito...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar fichas de conceito
    fichas_oficiais = [item for item in dados if item['model'] == 'militares.fichaconceitoficiais']
    fichas_pracas = [item for item in dados if item['model'] == 'militares.fichaconceitopracas']
    
    print(f"📊 Fichas de oficiais encontradas: {len(fichas_oficiais)}")
    print(f"📊 Fichas de praças encontradas: {len(fichas_pracas)}")
    
    # Importar fichas de oficiais
    importados_oficiais = 0
    for item in fichas_oficiais:
        try:
            fields = item['fields']
            # Remover campo militar se existir
            if 'militar' in fields:
                del fields['militar']
            
            ficha = FichaConceitoOficiais.objects.create(**fields)
            importados_oficiais += 1
        except Exception as e:
            print(f"❌ Erro ao importar ficha de oficial: {e}")
    
    # Importar fichas de praças
    importados_pracas = 0
    for item in fichas_pracas:
        try:
            fields = item['fields']
            # Remover campo militar se existir
            if 'militar' in fields:
                del fields['militar']
            
            ficha = FichaConceitoPracas.objects.create(**fields)
            importados_pracas += 1
        except Exception as e:
            print(f"❌ Erro ao importar ficha de praça: {e}")
    
    print(f"✅ Fichas de oficiais importadas: {importados_oficiais}")
    print(f"✅ Fichas de praças importadas: {importados_pracas}")
    
    return importados_oficiais + importados_pracas

def importar_documentos():
    """Importa documentos especificamente"""
    
    print("\n🔧 Importando documentos...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar documentos
    documentos = [item for item in dados if item['model'] == 'militares.documento']
    
    print(f"📊 Documentos encontrados: {len(documentos)}")
    
    # Importar documentos
    importados = 0
    for item in documentos:
        try:
            fields = item['fields']
            # Remover campos que podem causar problemas
            campos_remover = ['militar', 'ficha_conceito_oficiais', 'ficha_conceito_pracas', 
                             'conferido_por', 'assinado_por']
            
            for campo in campos_remover:
                if campo in fields:
                    del fields[campo]
            
            documento = Documento.objects.create(**fields)
            importados += 1
        except Exception as e:
            print(f"❌ Erro ao importar documento: {e}")
    
    print(f"✅ Documentos importados: {importados}")
    
    return importados

if __name__ == "__main__":
    print("🚀 Iniciando importação de outras tabelas")
    print("=" * 50)
    
    # Importar outras tabelas
    total_geral = importar_outras_tabelas()
    
    # Importar fichas de conceito
    fichas_importadas = importar_fichas_conceito()
    
    # Importar documentos
    documentos_importados = importar_documentos()
    
    print(f"\n🎉 Processo concluído!")
    print(f"📊 Total geral de itens importados: {total_geral + fichas_importadas + documentos_importados}")
    print(f"📋 Fichas de conceito: {fichas_importadas}")
    print(f"📋 Documentos: {documentos_importados}") 