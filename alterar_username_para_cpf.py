#!/usr/bin/env python
"""
Script para alterar o username dos usuários militares para usar o CPF
"""

import os
import sys
import django
import re
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar
from django.db import transaction

def limpar_cpf(cpf):
    """
    Remove pontuação do CPF para usar como username
    """
    if not cpf:
        return ""
    
    # Remover caracteres não numéricos
    return re.sub(r'[^\d]', '', cpf)

def alterar_username_para_cpf():
    """
    Altera o username dos usuários militares para usar o CPF
    """
    print("🚀 Iniciando alteração de username para CPF...")
    
    # Buscar todos os militares com usuário vinculado
    militares_com_usuario = Militar.objects.filter(user__isnull=False)
    
    print(f"📊 Total de militares com usuário: {militares_com_usuario.count()}")
    
    alteracoes_realizadas = 0
    erros = []
    cpfs_duplicados = []
    
    for militar in militares_com_usuario:
        try:
            # Limpar CPF (remover pontuação)
            cpf_limpo = limpar_cpf(militar.cpf)
            
            if not cpf_limpo:
                print(f"⚠️  Militar {militar.matricula}: CPF vazio ou inválido")
                continue
            
            # Verificar se já existe usuário com este CPF
            usuario_existente = User.objects.filter(username=cpf_limpo).exclude(pk=militar.user.pk).first()
            
            if usuario_existente:
                print(f"⚠️  CPF {cpf_limpo} já está em uso pelo usuário {usuario_existente.username}")
                cpfs_duplicados.append({
                    'cpf': cpf_limpo,
                    'militar_atual': militar.matricula,
                    'usuario_conflitante': usuario_existente.username
                })
                continue
            
            # Verificar se o username atual já é o CPF
            if militar.user.username == cpf_limpo:
                print(f"✅ Militar {militar.matricula}: Username já é o CPF")
                continue
            
            # Alterar username
            username_anterior = militar.user.username
            militar.user.username = cpf_limpo
            militar.user.save(update_fields=['username'])
            
            print(f"✅ Militar {militar.matricula}: {username_anterior} → {cpf_limpo}")
            alteracoes_realizadas += 1
            
        except Exception as e:
            print(f"❌ Erro ao alterar militar {militar.matricula}: {e}")
            erros.append(f"Militar {militar.matricula}: {e}")
    
    print("\n" + "="*60)
    print("📊 RESUMO DA ALTERAÇÃO")
    print("="*60)
    print(f"✅ Alterações realizadas: {alteracoes_realizadas}")
    print(f"⚠️  CPFs duplicados encontrados: {len(cpfs_duplicados)}")
    print(f"❌ Erros encontrados: {len(erros)}")
    
    if cpfs_duplicados:
        print("\n📋 CPFs duplicados:")
        for duplicado in cpfs_duplicados[:10]:  # Mostrar apenas os primeiros 10
            print(f"  - CPF {duplicado['cpf']}: Militar {duplicado['militar_atual']} vs {duplicado['usuario_conflitante']}")
    
    if erros:
        print("\n📋 Primeiros 10 erros:")
        for erro in erros[:10]:
            print(f"  - {erro}")
    
    return alteracoes_realizadas, len(cpfs_duplicados), len(erros)

def verificar_alteracoes():
    """
    Verifica se as alterações foram aplicadas corretamente
    """
    print("\n🔍 Verificando alterações...")
    
    militares_com_usuario = Militar.objects.filter(user__isnull=False)
    usuarios_com_cpf = 0
    usuarios_com_matricula = 0
    
    for militar in militares_com_usuario:
        cpf_limpo = limpar_cpf(militar.cpf)
        username_atual = militar.user.username
        
        if username_atual == cpf_limpo:
            usuarios_com_cpf += 1
        elif username_atual.startswith('militar_'):
            usuarios_com_matricula += 1
    
    print(f"📊 Usuários com CPF como username: {usuarios_com_cpf}")
    print(f"📊 Usuários ainda com matrícula como username: {usuarios_com_matricula}")
    
    # Mostrar alguns exemplos
    print("\n📋 Exemplos de usernames:")
    for militar in militares_com_usuario[:5]:
        print(f"  - {militar.matricula}: {militar.user.username} ({militar.nome_completo})")

def criar_relatorio_usuarios():
    """
    Cria um relatório com os dados dos usuários para facilitar o acesso
    """
    print("\n📋 Criando relatório de usuários...")
    
    militares_com_usuario = Militar.objects.filter(user__isnull=False).order_by('matricula')
    
    relatorio = []
    relatorio.append("MATRÍCULA,CPF,USERNAME,NOME_COMPLETO,POSTO,EMAIL,SENHA")
    
    for militar in militares_com_usuario:
        cpf_limpo = limpar_cpf(militar.cpf)
        senha = cpf_limpo  # CPF sem pontuação como senha
        
        linha = [
            militar.matricula,
            militar.cpf,
            militar.user.username,
            militar.nome_completo,
            militar.get_posto_graduacao_display(),
            militar.email or f"{militar.user.username}@cbmepi.pi.gov.br",
            senha
        ]
        
        # Escapar vírgulas nos campos
        linha = [f'"{campo}"' if ',' in str(campo) else str(campo) for campo in linha]
        relatorio.append(','.join(linha))
    
    # Salvar relatório
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_relatorio = f"relatorio_usuarios_{timestamp}.csv"
    
    with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
        f.write('\n'.join(relatorio))
    
    print(f"✅ Relatório salvo em: {arquivo_relatorio}")
    return arquivo_relatorio

def main():
    """
    Função principal
    """
    print("🚀 ALTERAÇÃO DE USERNAME PARA CPF")
    print("="*60)
    
    # Confirmar com o usuário
    resposta = input("⚠️  ATENÇÃO: Este script irá alterar o username de todos os usuários militares para usar o CPF!\nDeseja continuar? (s/N): ")
    
    if resposta.lower() != 's':
        print("❌ Operação cancelada pelo usuário.")
        return
    
    # Fazer backup antes de alterar
    print("\n💾 Fazendo backup dos dados atuais...")
    from django.core import serializers
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/backup_antes_alteracao_username_{timestamp}.json"
    
    try:
        # Backup de usuários
        usuarios_data = serializers.serialize('json', User.objects.filter(militar__isnull=False))
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(usuarios_data)
        print(f"✅ Backup salvo em: {backup_file}")
    except Exception as e:
        print(f"⚠️  Erro ao fazer backup: {e}")
    
    # Executar alterações
    with transaction.atomic():
        alteracoes, duplicados, erros = alterar_username_para_cpf()
    
    # Verificar alterações
    verificar_alteracoes()
    
    # Criar relatório
    arquivo_relatorio = criar_relatorio_usuarios()
    
    print("\n" + "="*60)
    if alteracoes > 0:
        print("🎉 Alteração realizada com sucesso!")
        print(f"📊 {alteracoes} usernames alterados para CPF")
        print(f"📋 Relatório disponível em: {arquivo_relatorio}")
    else:
        print("ℹ️  Nenhuma alteração necessária ou todos os usernames já são CPF")
    
    if duplicados > 0:
        print(f"⚠️  {duplicados} CPFs duplicados encontrados - verificar manualmente")

if __name__ == '__main__':
    main() 