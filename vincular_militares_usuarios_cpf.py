#!/usr/bin/env python
"""
Script para vincular militares aos usuários através do CPF
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar

def limpar_usuarios_duplicados():
    """Remove usuários duplicados antes de vincular"""
    
    print("🧹 LIMPANDO USUÁRIOS DUPLICADOS")
    print("=" * 50)
    
    # Remover usuários duplicados por username
    usuarios = User.objects.all()
    usernames_vistos = set()
    removidos = 0
    
    for usuario in usuarios.order_by('id'):
        if usuario.username in usernames_vistos:
            print(f"  - Removendo usuário duplicado: {usuario.username} (ID: {usuario.id})")
            usuario.delete()
            removidos += 1
        else:
            usernames_vistos.add(usuario.username)
    
    print(f"✅ {removidos} usuários duplicados removidos")
    return removidos

def vincular_militares_usuarios_cpf():
    """Vincula militares aos usuários através do CPF"""
    
    print("\n🔗 VINCULANDO MILITARES AOS USUÁRIOS PELO CPF")
    print("=" * 60)
    
    # Obter todos os militares
    militares = Militar.objects.all()
    print(f"📊 Total de militares: {militares.count()}")
    
    # Obter todos os usuários
    usuarios = User.objects.all()
    print(f"📊 Total de usuários: {usuarios.count()}")
    
    # Criar dicionário de usuários por CPF
    usuarios_por_cpf = {}
    for usuario in usuarios:
        # Tentar extrair CPF do username
        username = usuario.username
        
        # Se o username é um CPF (apenas números)
        if username.isdigit() and len(username) == 11:
            cpf = username
            usuarios_por_cpf[cpf] = usuario
        # Se o username tem formato militar_CPF
        elif username.startswith('militar_') and len(username) > 8:
            cpf = username[8:]  # Remove 'militar_'
            if cpf.isdigit() and len(cpf) == 11:
                usuarios_por_cpf[cpf] = usuario
    
    print(f"📊 Usuários com CPF válido: {len(usuarios_por_cpf)}")
    
    # Vincular militares aos usuários
    vinculados = 0
    nao_encontrados = 0
    sem_cpf = 0
    
    for militar in militares:
        cpf_militar = militar.cpf
        
        if not cpf_militar:
            sem_cpf += 1
            continue
        
        # Limpar CPF (remover pontos e traços)
        cpf_limpo = ''.join(filter(str.isdigit, str(cpf_militar)))
        
        if cpf_limpo in usuarios_por_cpf:
            usuario = usuarios_por_cpf[cpf_limpo]
            
            # Vincular militar ao usuário
            militar.user = usuario
            militar.save()
            
            print(f"  ✅ Vinculado: {militar.nome_completo} (CPF: {cpf_limpo}) → {usuario.username}")
            vinculados += 1
        else:
            print(f"  ❌ Não encontrado: {militar.nome_completo} (CPF: {cpf_limpo})")
            nao_encontrados += 1
    
    print(f"\n📊 RESUMO DA VINCULAÇÃO:")
    print(f"  ✅ Vinculados: {vinculados}")
    print(f"  ❌ Não encontrados: {nao_encontrados}")
    print(f"  ⚠️ Sem CPF: {sem_cpf}")
    
    return vinculados, nao_encontrados, sem_cpf

def criar_usuarios_para_militares_sem_vinculo():
    """Cria usuários para militares que não foram vinculados"""
    
    print("\n👤 CRIANDO USUÁRIOS PARA MILITARES SEM VÍNCULO")
    print("=" * 60)
    
    # Militares sem usuário vinculado
    militares_sem_usuario = Militar.objects.filter(user__isnull=True)
    print(f"📊 Militares sem usuário: {militares_sem_usuario.count()}")
    
    criados = 0
    
    for militar in militares_sem_usuario:
        cpf = militar.cpf
        
        if not cpf:
            continue
        
        # Limpar CPF
        cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
        
        if len(cpf_limpo) != 11:
            continue
        
        # Verificar se já existe usuário com este CPF
        if User.objects.filter(username=cpf_limpo).exists():
            usuario_existente = User.objects.get(username=cpf_limpo)
            militar.user = usuario_existente
            militar.save()
            print(f"  ✅ Vinculado a usuário existente: {militar.nome_completo} → {usuario_existente.username}")
        else:
            # Criar novo usuário
            try:
                username = cpf_limpo
                email = f"{cpf_limpo}@sepromcbmepi.com"
                
                usuario = User.objects.create_user(
                    username=username,
                    email=email,
                    password='militar123',  # Senha padrão
                    first_name=militar.nome_completo.split()[0] if militar.nome_completo else '',
                    last_name=' '.join(militar.nome_completo.split()[1:]) if militar.nome_completo and len(militar.nome_completo.split()) > 1 else ''
                )
                
                # Vincular ao militar
                militar.user = usuario
                militar.save()
                
                print(f"  ✅ Criado e vinculado: {militar.nome_completo} → {usuario.username}")
                criados += 1
                
            except Exception as e:
                print(f"  ❌ Erro ao criar usuário para {militar.nome_completo}: {e}")
    
    print(f"\n📊 RESUMO:")
    print(f"  ✅ Usuários criados: {criados}")
    
    return criados

def mostrar_estatisticas_finais():
    """Mostra estatísticas finais"""
    
    print("\n📊 ESTATÍSTICAS FINAIS")
    print("=" * 50)
    
    total_militares = Militar.objects.count()
    militares_com_usuario = Militar.objects.filter(user__isnull=False).count()
    militares_sem_usuario = Militar.objects.filter(user__isnull=True).count()
    
    total_usuarios = User.objects.count()
    usuarios_vinculados = User.objects.filter(militar__isnull=False).count()
    usuarios_sem_militar = total_usuarios - usuarios_vinculados
    
    print(f"🎖️ Militares:")
    print(f"  - Total: {total_militares}")
    print(f"  - Com usuário: {militares_com_usuario}")
    print(f"  - Sem usuário: {militares_sem_usuario}")
    
    print(f"\n👥 Usuários:")
    print(f"  - Total: {total_usuarios}")
    print(f"  - Vinculados a militar: {usuarios_vinculados}")
    print(f"  - Sem militar: {usuarios_sem_militar}")
    
    # Mostrar alguns exemplos
    print(f"\n👥 Exemplos de vínculos:")
    militares_vinculados = Militar.objects.filter(user__isnull=False)[:5]
    for militar in militares_vinculados:
        print(f"  - {militar.nome_completo} (CPF: {militar.cpf}) → {militar.user.username}")

def limpar_usuarios_orfos():
    """Remove usuários que não estão vinculados a nenhum militar"""
    
    print("\n🗑️ REMOVENDO USUÁRIOS ÓRFÃOS")
    print("=" * 50)
    
    # Usuários que não estão vinculados a nenhum militar
    usuarios_orfos = User.objects.filter(militar__isnull=True)
    print(f"📊 Usuários órfãos encontrados: {usuarios_orfos.count()}")
    
    # Manter o superusuário admin
    usuarios_para_remover = usuarios_orfos.exclude(username='admin')
    print(f"📊 Usuários para remover: {usuarios_para_remover.count()}")
    
    removidos = 0
    for usuario in usuarios_para_remover:
        print(f"  - Removendo: {usuario.username}")
        usuario.delete()
        removidos += 1
    
    print(f"✅ {removidos} usuários órfãos removidos")
    return removidos

if __name__ == "__main__":
    print("🚀 Iniciando vinculação de militares aos usuários pelo CPF")
    print("=" * 70)
    
    # Limpar usuários duplicados
    limpar_usuarios_duplicados()
    
    # Vincular militares aos usuários existentes
    vinculados, nao_encontrados, sem_cpf = vincular_militares_usuarios_cpf()
    
    # Criar usuários para militares sem vínculo
    criados = criar_usuarios_para_militares_sem_vinculo()
    
    # Remover usuários órfãos
    removidos = limpar_usuarios_orfos()
    
    # Mostrar estatísticas finais
    mostrar_estatisticas_finais()
    
    print(f"\n🎉 Processo concluído!")
    print(f"📊 Resumo:")
    print(f"  - Militares vinculados: {vinculados}")
    print(f"  - Usuários criados: {criados}")
    print(f"  - Usuários removidos: {removidos}") 