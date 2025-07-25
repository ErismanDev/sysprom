#!/usr/bin/env python
"""
Script para adicionar função padrão aos usuários sem funções vinculadas
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import CargoFuncao, UsuarioFuncao
from django.db import transaction

def criar_backup_usuarios_sem_funcao():
    """
    Cria backup dos usuários sem função antes da operação
    """
    print("💾 Criando backup dos usuários sem função...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_usuarios_sem_funcao_{timestamp}.txt"
    
    # Criar diretório se não existir
    os.makedirs("backups", exist_ok=True)
    
    usuarios_sem_funcao = User.objects.filter(funcoes__isnull=True)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(f"# Backup de Usuários Sem Função - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"# Total de usuários: {usuarios_sem_funcao.count()}\n\n")
        
        for usuario in usuarios_sem_funcao:
            f.write(f"Username: {usuario.username}\n")
            f.write(f"Nome: {usuario.get_full_name()}\n")
            f.write(f"Email: {usuario.email}\n")
            f.write(f"Status: {'Ativo' if usuario.is_active else 'Inativo'}\n")
            f.write(f"Superusuário: {'Sim' if usuario.is_superuser else 'Não'}\n")
            f.write(f"Staff: {'Sim' if usuario.is_staff else 'Não'}\n")
            
            if hasattr(usuario, 'militar') and usuario.militar:
                f.write(f"Militar: {usuario.militar.nome_completo}\n")
                f.write(f"Posto: {usuario.militar.posto_graduacao}\n")
            else:
                f.write(f"Militar: Nenhum\n")
            
            f.write("-" * 50 + "\n")
    
    print(f"✅ Backup criado: {backup_file}")
    return backup_file

def adicionar_funcao_padrao():
    """
    Adiciona função padrão aos usuários sem funções
    """
    print("🔧 Adicionando função padrão aos usuários...")
    print("=" * 60)
    
    # Buscar usuários sem funções
    usuarios_sem_funcao = User.objects.filter(funcoes__isnull=True)
    
    # Buscar função padrão (Usuário - ID: 8)
    try:
        funcao_padrao = CargoFuncao.objects.get(id=8)  # "Usuário" - Acesso apenas para consulta
        print(f"✅ Função padrão encontrada: {funcao_padrao.nome}")
    except CargoFuncao.DoesNotExist:
        print("❌ Função padrão não encontrada!")
        return False
    
    print(f"📊 Total de usuários sem função: {usuarios_sem_funcao.count()}")
    print()
    
    # Contadores
    sucessos = 0
    erros = 0
    usuarios_processados = []
    
    with transaction.atomic():
        for usuario in usuarios_sem_funcao:
            try:
                # Verificar se já tem a função
                if UsuarioFuncao.objects.filter(usuario=usuario, cargo_funcao=funcao_padrao).exists():
                    print(f"⚠️  Usuário {usuario.username} já tem a função {funcao_padrao.nome}")
                    continue
                
                # Criar relação UsuarioFuncao com todos os campos obrigatórios
                UsuarioFuncao.objects.create(
                    usuario=usuario,
                    cargo_funcao=funcao_padrao,
                    tipo_funcao='OPERACIONAL',  # Campo obrigatório
                    status='ATIVO',  # Campo obrigatório
                    data_inicio=datetime.now().date(),
                    descricao='Função padrão atribuída automaticamente'
                )
                
                usuarios_processados.append({
                    'username': usuario.username,
                    'nome': usuario.get_full_name(),
                    'funcao': funcao_padrao.nome
                })
                
                sucessos += 1
                
                if sucessos % 50 == 0:  # Mostrar progresso a cada 50 usuários
                    print(f"✅ Processados: {sucessos} usuários...")
                
            except Exception as e:
                print(f"❌ Erro ao processar usuário {usuario.username}: {e}")
                erros += 1
    
    print()
    print("=" * 60)
    print("📋 **RESULTADO DA OPERAÇÃO:**")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros: {erros}")
    print(f"📊 Total processado: {sucessos + erros}")
    
    if usuarios_processados:
        print()
        print("👥 **PRIMEIROS 10 USUÁRIOS PROCESSADOS:**")
        for i, info in enumerate(usuarios_processados[:10], 1):
            print(f"  {i}. {info['username']} - {info['nome']} → {info['funcao']}")
    
    return sucessos > 0

def verificar_resultado():
    """
    Verifica o resultado da operação
    """
    print("\n🔍 Verificando resultado da operação...")
    print("=" * 50)
    
    # Verificar usuários sem função
    usuarios_sem_funcao = User.objects.filter(funcoes__isnull=True)
    
    # Verificar usuários com função padrão
    funcao_padrao = CargoFuncao.objects.get(id=8)
    usuarios_com_funcao_padrao = UsuarioFuncao.objects.filter(cargo_funcao=funcao_padrao)
    
    print(f"📊 Usuários sem função: {usuarios_sem_funcao.count()}")
    print(f"📊 Usuários com função padrão: {usuarios_com_funcao_padrao.count()}")
    
    if usuarios_sem_funcao.exists():
        print("\n❌ **USUÁRIOS AINDA SEM FUNÇÃO:**")
        for usuario in usuarios_sem_funcao[:5]:  # Mostrar apenas os primeiros 5
            print(f"  • {usuario.username} - {usuario.get_full_name()}")
        if usuarios_sem_funcao.count() > 5:
            print(f"  ... e mais {usuarios_sem_funcao.count() - 5} usuários")
    else:
        print("\n✅ Todos os usuários agora têm função!")

def main():
    """
    Função principal
    """
    print("🚀 Iniciando adição de função padrão aos usuários...")
    print("=" * 70)
    
    # Criar backup
    backup_file = criar_backup_usuarios_sem_funcao()
    print()
    
    # Adicionar função padrão
    sucesso = adicionar_funcao_padrao()
    print()
    
    # Verificar resultado
    verificar_resultado()
    print()
    
    print("=" * 70)
    if sucesso:
        print("✅ Operação concluída com sucesso!")
        print(f"💾 Backup salvo em: {backup_file}")
    else:
        print("❌ Operação falhou!")

if __name__ == '__main__':
    main() 