#!/usr/bin/env python3
"""
Script simples para fazer backup UTF-8 dos dados
"""

import os
import sys
import django
from datetime import datetime

def configurar_ambiente():
    """Configura o ambiente Django"""
    print("🔧 Configurando ambiente Django...")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
    
    try:
        django.setup()
        print("✅ Ambiente Django configurado")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar Django: {e}")
        return False

def fazer_backup_utf8():
    """Faz backup com codificação UTF-8 correta"""
    print("\n💾 Fazendo backup com codificação UTF-8...")
    
    try:
        from django.core.management import call_command
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_utf8_{timestamp}.json"
        
        # Fazer backup usando dumpdata com encoding UTF-8
        call_command(
            'dumpdata',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.Permission',
            '--indent', '2',
            '--output', backup_file
        )
        
        print(f"✅ Backup UTF-8 criado: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"❌ Erro ao fazer backup UTF-8: {e}")
        return None

def main():
    """Função principal"""
    print("🔧 BACKUP UTF-8 SIMPLES")
    print("=" * 30)
    
    # Configurar ambiente
    if not configurar_ambiente():
        return False
    
    # Fazer backup UTF-8
    backup_file = fazer_backup_utf8()
    if not backup_file:
        return False
    
    print("\n" + "=" * 30)
    print("✅ BACKUP UTF-8 CRIADO!")
    print("=" * 30)
    print(f"📁 Arquivo: {backup_file}")
    print()
    print("🔧 Agora execute a migração:")
    print(f"   python migrar_com_backup_utf8.py {backup_file}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Backup falhou. Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Backup interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 