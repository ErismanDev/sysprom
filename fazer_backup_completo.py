#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar backup completo do banco de dados Django
"""
import os
import sys
import django
from datetime import datetime
from django.core.management import call_command

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

# Nome do arquivo de backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backup_sepromcbmepi_completo_{timestamp}.json"

print(f"📦 Criando backup completo...")
print(f"📁 Arquivo: {backup_file}")

try:
    # Criar backup completo (sem excluir nada)
    print("📊 Verificando dados antes do backup...")
    from django.contrib.auth.models import User
    from militares.models import Militar
    print(f"   Usuários: {User.objects.count()}")
    print(f"   Militares: {Militar.objects.count()}")
    
    # Forçar encoding UTF-8 no Windows
    import sys
    import io
    
    # Salvar stdout original
    original_stdout = sys.stdout
    
    # Abrir arquivo com encoding UTF-8
    with open(backup_file, 'w', encoding='utf-8', newline='') as f:
        # Redirecionar stdout para o arquivo com encoding UTF-8
        sys.stdout = io.TextIOWrapper(f.buffer, encoding='utf-8', line_buffering=True)
        
        try:
            # Criar backup
            call_command(
                'dumpdata',
                verbosity=1,
                indent=2,
                natural_foreign=True,
                natural_primary=True,
                use_base_manager=True
            )
        finally:
            # Restaurar stdout original
            sys.stdout = original_stdout
            sys.stdout.reconfigure(encoding='utf-8')
    
    # Verificar tamanho do arquivo
    file_size = os.path.getsize(backup_file)
    size_mb = file_size / (1024 * 1024)
    
    print(f"\n✅ Backup criado com sucesso!")
    print(f"📊 Tamanho: {size_mb:.2f} MB")
    print(f"📁 Local: {os.path.abspath(backup_file)}")
    
    # Verificar se o arquivo tem conteúdo e contar registros
    with open(backup_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if content.strip().startswith('['):
            print(f"✅ Arquivo válido (formato JSON correto)")
            # Contar quantos objetos foram salvos
            import json
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    print(f"📊 Total de objetos no backup: {len(data)}")
                    # Contar por tipo
                    tipos = {}
                    for item in data:
                        tipo = item.get('model', 'unknown')
                        tipos[tipo] = tipos.get(tipo, 0) + 1
                    print(f"📋 Tipos de dados salvos:")
                    for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"   - {tipo}: {count}")
            except:
                pass
        else:
            print(f"⚠️ Aviso: Formato do arquivo pode estar incorreto")
    
except Exception as e:
    print(f"\n❌ Erro ao criar backup: {e}")
    sys.exit(1)

print(f"\n💡 Próximo passo: Envie este arquivo via WinSCP para:")
print(f"   /home/seprom/sepromcbmepi/")

