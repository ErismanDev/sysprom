#!/usr/bin/env python
"""
Script para importar apenas os dados dos militares
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.contrib.auth.models import User

def importar_apenas_militares():
    """Importa apenas os dados dos militares"""
    
    print("🔧 Importando apenas dados dos militares...")
    
    # Ler o arquivo de dados
    with open('dados_sqlite_sem_duplicatas_20250722_154148.json', 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Filtrar apenas militares
    militares_data = [item for item in dados if item['model'] == 'militares.militar']
    
    print(f"📊 Total de militares para importar: {len(militares_data)}")
    
    militares_importados = 0
    erros = []
    
    for i, item in enumerate(militares_data, 1):
        try:
            fields = item['fields']
            
            # Criar militar sem o campo user (será criado automaticamente)
            militar_data = {k: v for k, v in fields.items() if k != 'user'}
            
            # Criar o militar
            militar = Militar.objects.create(**militar_data)
            
            militares_importados += 1
            
            if i % 10 == 0:
                print(f"✅ Importados {i}/{len(militares_data)} militares...")
                
        except Exception as e:
            erro_msg = f"Erro ao importar militar {i}: {e}"
            erros.append(erro_msg)
            print(f"❌ {erro_msg}")
            continue
    
    print(f"\n✅ Migração concluída!")
    print(f"📊 Militares importados: {militares_importados}")
    print(f"❌ Erros: {len(erros)}")
    
    if erros:
        print("\n📋 Primeiros 5 erros:")
        for erro in erros[:5]:
            print(f"  - {erro}")
    
    return militares_importados

def criar_superuser_admin():
    """Cria um superusuário admin para acesso"""
    
    print("\n🔧 Criando superusuário admin...")
    
    try:
        # Verificar se já existe
        if User.objects.filter(username='admin').exists():
            print("✅ Superusuário admin já existe!")
            return
        
        # Criar superusuário
        user = User.objects.create_superuser(
            username='admin',
            email='admin@sepromcbmepi.com',
            password='admin123'
        )
        
        print("✅ Superusuário admin criado com sucesso!")
        print("👤 Usuário: admin")
        print("🔑 Senha: admin123")
        print("⚠️ IMPORTANTE: Altere a senha após o primeiro login!")
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando migração de dados dos militares")
    print("=" * 50)
    
    # Importar militares
    total_importados = importar_apenas_militares()
    
    # Criar superusuário
    criar_superuser_admin()
    
    print("\n🎉 Processo concluído!")
    print(f"📊 Total de militares no banco: {Militar.objects.count()}")
    print("🌐 Agora você pode acessar o sistema com:")
    print("   Usuário: admin")
    print("   Senha: admin123") 