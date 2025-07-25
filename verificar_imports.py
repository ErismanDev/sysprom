#!/usr/bin/env python
"""
Script para verificar se os imports estão funcionando corretamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

try:
    from militares.models import UsuarioFuncao
    print("✅ Import de UsuarioFuncao funcionando!")
    
    # Testar se a classe existe
    print(f"✅ Classe UsuarioFuncao encontrada: {UsuarioFuncao}")
    
    # Testar se conseguimos fazer uma query
    count = UsuarioFuncao.objects.count()
    print(f"✅ Query funcionando! Total de funções: {count}")
    
except ImportError as e:
    print(f"❌ Erro no import: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")

print("\nVerificação concluída!") 