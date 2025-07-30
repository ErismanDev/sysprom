#!/usr/bin/env python3
"""
Script para corrigir problemas de codificação UTF-8 no backup
"""

import os
import sys
import django
import json
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
        from django.core.serializers import serialize
        from django.contrib.auth.models import User
        from militares.models import *
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_utf8_{timestamp}.json"
        
        # Lista de modelos para exportar
        modelos = [
            User,
            Militar,
            ComissaoPromocao,
            MembroComissao,
            SessaoComissao,
            QuadroAcesso,
            ItemQuadroAcesso,
            FichaConceitoOficiais,
            FichaConceitoPracas,
            Documento,
            Curso,
            MedalhaCondecoracao,
            Intersticio,
            Promocao,
            Vaga,
            PrevisaoVaga,
            CargoComissao,
            DeliberacaoComissao,
            VotoDeliberacao,
            DocumentoSessao,
            AtaSessao,
            ModeloAta,
            AssinaturaAta,
            VagaManual,
            QuadroFixacaoVagas,
            ItemQuadroFixacaoVagas,
            UsuarioFuncao,
            CargoFuncao,
            PermissaoFuncao,
            PerfilAcesso,
            CalendarioPromocao,
            ItemCalendarioPromocao,
            AssinaturaCalendarioPromocao,
            AlmanaqueMilitar,
            AssinaturaAlmanaque,
            NotificacaoSessao,
        ]
        
        # Criar arquivo de backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write('[\n')
            
            primeiro = True
            for modelo in modelos:
                try:
                    objetos = modelo.objects.all()
                    if objetos.exists():
                        print(f"📤 Exportando {modelo.__name__}: {objetos.count()} registros")
                        
                        for obj in objetos:
                            if not primeiro:
                                f.write(',\n')
                            primeiro = False
                            
                            # Serializar objeto
                            dados = serialize('json', [obj])
                            dados_json = json.loads(dados)[0]
                            
                            # Escrever no arquivo
                            f.write(json.dumps(dados_json, ensure_ascii=False, indent=2))
                            
                except Exception as e:
                    print(f"⚠️  Erro ao exportar {modelo.__name__}: {e}")
                    continue
            
            f.write('\n]')
        
        print(f"✅ Backup UTF-8 criado: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"❌ Erro ao fazer backup UTF-8: {e}")
        return None

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE BACKUP UTF-8")
    print("=" * 40)
    
    # Configurar ambiente
    if not configurar_ambiente():
        return False
    
    # Fazer backup UTF-8
    backup_file = fazer_backup_utf8()
    if not backup_file:
        return False
    
    print("\n" + "=" * 40)
    print("✅ BACKUP UTF-8 CRIADO COM SUCESSO!")
    print("=" * 40)
    print(f"📁 Arquivo: {backup_file}")
    print()
    print("🔧 Agora execute a migração:")
    print(f"   python migrar_com_backup_utf8.py {backup_file}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Correção falhou. Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Correção interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 