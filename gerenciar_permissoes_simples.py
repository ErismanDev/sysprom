#!/usr/bin/env python
"""
Gerenciador simples de permissões via web (sem login)
"""
import os
import sys
import django
import requests
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao

def gerenciar_permissoes_web():
    """Gerencia permissões via web"""
    
    print("🌐 GERENCIADOR DE PERMISSÕES VIA WEB")
    print("=" * 50)
    
    # Configurações
    base_url = "http://127.0.0.1:8000"
    session = requests.Session()
    
    # Listar cargos
    print("📋 Cargos disponíveis:")
    cargos = CargoFuncao.objects.all().order_by('id')
    
    for cargo in cargos:
        perms_count = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
        print(f"ID {cargo.id:2d}: {cargo.nome:<30} ({perms_count:3d} permissões)")
    
    print("\n" + "=" * 50)
    print("🎯 OPÇÕES:")
    print("1. Adicionar todas as permissões a um cargo")
    print("2. Limpar permissões de um cargo")
    print("3. Aplicar todas as permissões a todos os cargos")
    print("4. Verificar permissões de um cargo")
    print("5. Sair")
    print("=" * 50)
    
    while True:
        opcao = input("\nEscolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            cargo_id = input("Digite o ID do cargo: ").strip()
            try:
                cargo_id = int(cargo_id)
                adicionar_todas_permissoes(session, base_url, cargo_id)
            except ValueError:
                print("❌ ID inválido!")
                
        elif opcao == "2":
            cargo_id = input("Digite o ID do cargo: ").strip()
            try:
                cargo_id = int(cargo_id)
                limpar_permissoes(session, base_url, cargo_id)
            except ValueError:
                print("❌ ID inválido!")
                
        elif opcao == "3":
            confirmar = input("⚠️ Isso aplicará TODAS as permissões a TODOS os cargos. Continuar? (s/n): ").strip().lower()
            if confirmar == 's':
                aplicar_todas_permissoes_todos_cargos(session, base_url)
            else:
                print("❌ Operação cancelada!")
                
        elif opcao == "4":
            cargo_id = input("Digite o ID do cargo: ").strip()
            try:
                cargo_id = int(cargo_id)
                verificar_permissoes(cargo_id)
            except ValueError:
                print("❌ ID inválido!")
                
        elif opcao == "5":
            print("👋 Saindo...")
            break
            
        else:
            print("❌ Opção inválida!")

def adicionar_todas_permissoes(session, base_url, cargo_id):
    """Adiciona todas as permissões a um cargo"""
    print(f"➕ Adicionando todas as permissões ao cargo {cargo_id}...")
    
    # 1. Acessar página de edição
    edit_url = f"{base_url}/militares/permissoes/cargo/{cargo_id}/editar/"
    response = session.get(edit_url)
    
    if response.status_code != 200:
        print(f"❌ Erro ao acessar página: {response.status_code}")
        return False
    
    # 2. Extrair CSRF token
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ CSRF token não encontrado")
        return False
    
    csrf_token = csrf_token['value']
    
    # 3. Preparar todas as permissões
    modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
    acessos = [choice[0] for choice in PermissaoFuncao.ACESSOS_CHOICES]
    
    todas_permissoes = []
    for modulo in modulos:
        for acesso in acessos:
            todas_permissoes.append(f"{modulo}:{acesso}")
    
    print(f"   Total de permissões: {len(todas_permissoes)}")
    
    # 4. Preparar dados do formulário
    form_data = {
        'csrfmiddlewaretoken': csrf_token,
    }
    
    # Adicionar permissões ao formulário
    for permissao in todas_permissoes:
        form_data['permissoes'] = permissao
    
    # 5. Enviar formulário
    headers = {
        'Referer': edit_url,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    response = session.post(edit_url, data=form_data, headers=headers)
    
    if response.status_code in [200, 302]:
        print("✅ Permissões adicionadas com sucesso!")
        
        # Verificar no banco
        cargo = CargoFuncao.objects.get(pk=cargo_id)
        total_permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
        print(f"   Total no banco: {total_permissoes}")
        
        return True
    else:
        print(f"❌ Erro ao adicionar permissões: {response.status_code}")
        return False

def limpar_permissoes(session, base_url, cargo_id):
    """Limpa todas as permissões de um cargo"""
    print(f"🗑️ Limpando permissões do cargo {cargo_id}...")
    
    # 1. Acessar página de edição
    edit_url = f"{base_url}/militares/permissoes/cargo/{cargo_id}/editar/"
    response = session.get(edit_url)
    
    if response.status_code != 200:
        print(f"❌ Erro ao acessar página: {response.status_code}")
        return False
    
    # 2. Extrair CSRF token
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if not csrf_token:
        print("❌ CSRF token não encontrado")
        return False
    
    csrf_token = csrf_token['value']
    
    # 3. Enviar formulário vazio
    form_data = {
        'csrfmiddlewaretoken': csrf_token,
    }
    
    headers = {
        'Referer': edit_url,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    response = session.post(edit_url, data=form_data, headers=headers)
    
    if response.status_code in [200, 302]:
        print("✅ Permissões removidas com sucesso!")
        
        # Verificar no banco
        cargo = CargoFuncao.objects.get(pk=cargo_id)
        total_permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
        print(f"   Total no banco: {total_permissoes}")
        
        return True
    else:
        print(f"❌ Erro ao remover permissões: {response.status_code}")
        return False

def aplicar_todas_permissoes_todos_cargos(session, base_url):
    """Aplica todas as permissões a todos os cargos"""
    print("🎯 Aplicando todas as permissões a todos os cargos...")
    
    cargos = CargoFuncao.objects.all()
    
    for cargo in cargos:
        print(f"\n--- Processando: {cargo.nome} (ID: {cargo.id}) ---")
        adicionar_todas_permissoes(session, base_url, cargo.id)
        time.sleep(1)  # Pausa entre operações
    
    print("\n✅ Processo concluído!")

def verificar_permissoes(cargo_id):
    """Verifica as permissões de um cargo"""
    print(f"🔍 Verificando permissões do cargo {cargo_id}...")
    
    try:
        cargo = CargoFuncao.objects.get(pk=cargo_id)
        permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo)
        
        print(f"Cargo: {cargo.nome}")
        print(f"Total de permissões: {permissoes.count()}")
        
        if permissoes.exists():
            print("\nPermissões:")
            for perm in permissoes[:10]:  # Mostrar apenas as 10 primeiras
                print(f"  - {perm.modulo}: {perm.acesso}")
            
            if permissoes.count() > 10:
                print(f"  ... e mais {permissoes.count() - 10} permissões")
        else:
            print("❌ Nenhuma permissão encontrada")
            
    except CargoFuncao.DoesNotExist:
        print(f"❌ Cargo ID {cargo_id} não encontrado!")

if __name__ == "__main__":
    gerenciar_permissoes_web() 