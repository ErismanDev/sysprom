#!/usr/bin/env python
"""
Script para remover usuários não vinculados aos militares
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar
from django.db import transaction
from datetime import datetime

def criar_backup_usuarios():
    """Cria backup dos usuários antes da remoção"""
    print("💾 Criando backup dos usuários...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_usuarios_antes_remocao_{timestamp}.txt"
    
    # Criar diretório se não existir
    os.makedirs("backups", exist_ok=True)
    
    usuarios_sem_militar = User.objects.filter(militar__isnull=True)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write("BACKUP DE USUÁRIOS SEM MILITAR VINCULADO\n")
        f.write("=" * 50 + "\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total de usuários: {usuarios_sem_militar.count()}\n\n")
        
        for usuario in usuarios_sem_militar:
            f.write(f"ID: {usuario.id}\n")
            f.write(f"Username: {usuario.username}\n")
            f.write(f"Nome: {usuario.get_full_name()}\n")
            f.write(f"Email: {usuario.email}\n")
            f.write(f"Ativo: {usuario.is_active}\n")
            f.write(f"Superuser: {usuario.is_superuser}\n")
            f.write(f"Staff: {usuario.is_staff}\n")
            f.write(f"Data de criação: {usuario.date_joined}\n")
            f.write("-" * 30 + "\n")
    
    print(f"   ✅ Backup criado: {backup_file}")
    return backup_file

def remover_usuarios_nao_vinculados():
    """Remove usuários não vinculados aos militares"""
    print("🗑️  Removendo usuários não vinculados aos militares...")
    print("=" * 70)
    
    # Estatísticas antes da remoção
    total_antes = User.objects.count()
    usuarios_com_militar_antes = User.objects.filter(militar__isnull=False).count()
    usuarios_sem_militar_antes = User.objects.filter(militar__isnull=True).count()
    
    print(f"📊 Estatísticas ANTES da remoção:")
    print(f"   • Total de usuários: {total_antes}")
    print(f"   • Usuários com militar: {usuarios_com_militar_antes}")
    print(f"   • Usuários sem militar: {usuarios_sem_militar_antes}")
    
    # Criar backup
    backup_file = criar_backup_usuarios()
    
    # Identificar usuários para manter (administradores e usuários com militar)
    usuarios_para_manter = []
    
    # Manter superusuários
    superusuarios = User.objects.filter(is_superuser=True)
    usuarios_para_manter.extend(superusuarios)
    print(f"\n👑 Superusuários que serão mantidos ({superusuarios.count()}):")
    for usuario in superusuarios:
        print(f"   • {usuario.username} - {usuario.get_full_name()}")
    
    # Manter usuários com militar vinculado
    usuarios_com_militar = User.objects.filter(militar__isnull=False)
    usuarios_para_manter.extend(usuarios_com_militar)
    print(f"\n👥 Usuários com militar que serão mantidos ({usuarios_com_militar.count()}):")
    
    # Mostrar alguns exemplos
    for usuario in usuarios_com_militar[:5]:
        print(f"   • {usuario.username} - {usuario.get_full_name()}")
    if usuarios_com_militar.count() > 5:
        print(f"   ... e mais {usuarios_com_militar.count() - 5} usuários")
    
    # Identificar usuários para remover
    ids_para_manter = [u.id for u in usuarios_para_manter]
    usuarios_para_remover = User.objects.exclude(id__in=ids_para_manter)
    
    print(f"\n🗑️  Usuários que serão removidos ({usuarios_para_remover.count()}):")
    
    # Mostrar alguns exemplos dos usuários que serão removidos
    for usuario in usuarios_para_remover[:10]:
        print(f"   • {usuario.username} - {usuario.get_full_name()}")
    if usuarios_para_remover.count() > 10:
        print(f"   ... e mais {usuarios_para_remover.count() - 10} usuários")
    
    # Confirmar remoção
    print(f"\n⚠️  ATENÇÃO: Esta operação irá remover {usuarios_para_remover.count()} usuários!")
    print(f"💾 Backup criado em: {backup_file}")
    
    # Executar remoção
    with transaction.atomic():
        usuarios_removidos = 0
        
        for usuario in usuarios_para_remover:
            try:
                nome_usuario = f"{usuario.username} - {usuario.get_full_name()}"
                usuario.delete()
                usuarios_removidos += 1
                print(f"   ✅ Removido: {nome_usuario}")
            except Exception as e:
                print(f"   ❌ Erro ao remover {usuario.username}: {e}")
        
        print(f"\n📊 Remoção concluída!")
        print(f"   • Usuários removidos: {usuarios_removidos}")
    
    # Estatísticas após a remoção
    total_depois = User.objects.count()
    usuarios_com_militar_depois = User.objects.filter(militar__isnull=False).count()
    usuarios_sem_militar_depois = User.objects.filter(militar__isnull=True).count()
    
    print(f"\n📊 Estatísticas DEPOIS da remoção:")
    print(f"   • Total de usuários: {total_depois}")
    print(f"   • Usuários com militar: {usuarios_com_militar_depois}")
    print(f"   • Usuários sem militar: {usuarios_sem_militar_depois}")
    print(f"   • Usuários removidos: {total_antes - total_depois}")
    
    return {
        'usuarios_removidos': usuarios_removidos,
        'total_antes': total_antes,
        'total_depois': total_depois,
        'backup_file': backup_file
    }

def main():
    """Função principal"""
    print("🚀 Removendo usuários não vinculados aos militares...")
    print("=" * 70)
    
    resultado = remover_usuarios_nao_vinculados()
    
    print(f"\n" + "=" * 70)
    print(f"✅ OPERAÇÃO CONCLUÍDA!")
    print(f"   • Usuários removidos: {resultado['usuarios_removidos']}")
    print(f"   • Total antes: {resultado['total_antes']}")
    print(f"   • Total depois: {resultado['total_depois']}")
    print(f"   • Backup: {resultado['backup_file']}")
    
    if resultado['usuarios_removidos'] > 0:
        print(f"\n🎉 Limpeza realizada com sucesso!")
        print(f"💡 Agora todos os usuários estão vinculados a militares ou são administradores")
    else:
        print(f"\n✅ Nenhum usuário foi removido!")

if __name__ == '__main__':
    main() 