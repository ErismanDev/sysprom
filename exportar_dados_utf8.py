#!/usr/bin/env python
import os
import sys
import django
import json
from datetime import datetime, date, time
from decimal import Decimal
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        elif hasattr(obj, 'isoformat'):  # Para outros tipos de data/hora
            return obj.isoformat()
        elif hasattr(obj, '__str__'):
            return str(obj)
        return super().default(obj)

def exportar_dados_utf8():
    """Exporta dados do SQLite com codificação UTF-8 adequada"""
    
    # Obter todos os modelos
    models = apps.get_models()
    
    dados_exportados = []
    
    for model in models:
        try:
            # Pular contenttypes e auth.Permission
            if model._meta.app_label == 'contenttypes' or (model._meta.app_label == 'auth' and model._meta.model_name == 'permission'):
                continue
                
            print(f"Exportando {model._meta.app_label}.{model._meta.model_name}...")
            
            # Obter todos os objetos do modelo
            objetos = model.objects.all()
            
            # Serializar cada objeto
            for obj in objetos:
                try:
                    dados_serializados = serializers.serialize('python', [obj])
                    dados_exportados.extend(dados_serializados)
                except Exception as e:
                    print(f"Erro ao serializar objeto {obj.pk} do modelo {model._meta.model_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro ao processar modelo {model._meta.model_name}: {e}")
            continue
    
    # Salvar em arquivo JSON com codificação UTF-8
    with open('dados_sqlite_utf8.json', 'w', encoding='utf-8') as f:
        json.dump(dados_exportados, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
    
    print(f"Exportação concluída! {len(dados_exportados)} objetos exportados para dados_sqlite_utf8.json")

if __name__ == '__main__':
    exportar_dados_utf8() 