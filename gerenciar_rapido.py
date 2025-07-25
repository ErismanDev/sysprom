#!/usr/bin/env python
"""
Script rápido para gerenciar permissões via web
"""
import os
import sys
import django
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao

def gerenciar_rapido():
    """Gerenciamento rápido de permissões"""
    
    print("⚡ GERENCIAMENTO RÁPIDO DE PERMISSÕES")
    print("=" * 50)
    
    # Mostrar cargos
    cargos = CargoFuncao.objects.all().order_by('id')
    print("Cargos disponíveis:")
    for cargo in cargos:
        perms_count = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
        print(f"  {cargo.id}: {cargo.nome} ({perms_count} permissões)")
    
    print("\n" + "=" * 50)
    print("COMANDOS RÁPIDOS:")
    print("  'todos' - Adicionar todas as permissões a todos os cargos")
    print("  'cargo X' - Adicionar todas as permissões ao cargo X")
    print("  'limpar X' - Limpar permissões do cargo X")
    print("  'ver X' - Verificar permissões do cargo X")
    print("  'sair' - Sair")
    print("=" * 50)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:8000"
    
    while True:
        comando = input("\nComando: ").strip().lower()
        
        if comando == 'sair':
            print("👋 Saindo...")
            break
            
        elif comando == 'todos':
            print("🎯 Adicionando todas as permissões a todos os cargos...")
            for cargo in cargos:
                print(f"  Processando: {cargo.nome}")
                adicionar_todas_permissoes(session, base_url, cargo.id)
            print("✅ Concluído!")
            
        elif comando.startswith('cargo '):
            try:
                cargo_id = int(comando.split()[1])
                print(f"➕ Adicionando todas as permissões ao cargo {cargo_id}...")
                adicionar_todas_permissoes(session, base_url, cargo_id)
            except (ValueError, IndexError):
                print("❌ Uso: 'cargo X' (onde X é o ID do cargo)")
                
        elif comando.startswith('limpar '):
            try:
                cargo_id = int(comando.split()[1])
                print(f"🗑️ Limpando permissões do cargo {cargo_id}...")
                limpar_permissoes(session, base_url, cargo_id)
            except (ValueError, IndexError):
                print("❌ Uso: 'limpar X' (onde X é o ID do cargo)")
                
        elif comando.startswith('ver '):
            try:
                cargo_id = int(comando.split()[1])
                verificar_permissoes(cargo_id)
            except (ValueError, IndexError):
                print("❌ Uso: 'ver X' (onde X é o ID do cargo)")
                
        else:
            print("❌ Comando inválido!")

def adicionar_todas_permissoes(session, base_url, cargo_id):
    """Adiciona todas as permissões a um cargo"""
    try:
        # 1. Acessar página de edição
        edit_url = f"{base_url}/militares/permissoes/cargo/{cargo_id}/editar/"
        response = session.get(edit_url)
        
        if response.status_code != 200:
            print(f"    ❌ Erro: {response.status_code}")
            return False
        
        # 2. Extrair CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_token:
            print("    ❌ CSRF token não encontrado")
            return False
        
        csrf_token = csrf_token['value']
        
        # 3. Preparar permissões
        modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
        acessos = [choice[0] for choice in PermissaoFuncao.ACESSOS_CHOICES]
        
        todas_permissoes = []
        for modulo in modulos:
            for acesso in acessos:
                todas_permissoes.append(f"{modulo}:{acesso}")
        
        # 4. Enviar formulário
        form_data = {'csrfmiddlewaretoken': csrf_token}
        for permissao in todas_permissoes:
            form_data['permissoes'] = permissao
        
        headers = {
            'Referer': edit_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        response = session.post(edit_url, data=form_data, headers=headers)
        
        if response.status_code in [200, 302]:
            cargo = CargoFuncao.objects.get(pk=cargo_id)
            total_permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
            print(f"    ✅ {total_permissoes} permissões adicionadas")
            return True
        else:
            print(f"    ❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return False

def limpar_permissoes(session, base_url, cargo_id):
    """Limpa todas as permissões de um cargo"""
    try:
        # 1. Acessar página de edição
        edit_url = f"{base_url}/militares/permissoes/cargo/{cargo_id}/editar/"
        response = session.get(edit_url)
        
        if response.status_code != 200:
            print(f"    ❌ Erro: {response.status_code}")
            return False
        
        # 2. Extrair CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_token:
            print("    ❌ CSRF token não encontrado")
            return False
        
        csrf_token = csrf_token['value']
        
        # 3. Enviar formulário vazio
        form_data = {'csrfmiddlewaretoken': csrf_token}
        
        headers = {
            'Referer': edit_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        response = session.post(edit_url, data=form_data, headers=headers)
        
        if response.status_code in [200, 302]:
            cargo = CargoFuncao.objects.get(pk=cargo_id)
            total_permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
            print(f"    ✅ {total_permissoes} permissões restantes")
            return True
        else:
            print(f"    ❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return False

def verificar_permissoes(cargo_id):
    """Verifica as permissões de um cargo"""
    try:
        cargo = CargoFuncao.objects.get(pk=cargo_id)
        permissoes = PermissaoFuncao.objects.filter(cargo_funcao=cargo)
        
        print(f"  Cargo: {cargo.nome}")
        print(f"  Total: {permissoes.count()} permissões")
        
        if permissoes.exists():
            modulos = {}
            for perm in permissoes:
                if perm.modulo not in modulos:
                    modulos[perm.modulo] = 0
                modulos[perm.modulo] += 1
            
            print("  Módulos:")
            for modulo, count in modulos.items():
                print(f"    - {modulo}: {count} permissões")
        else:
            print("  ❌ Nenhuma permissão")
            
    except CargoFuncao.DoesNotExist:
        print(f"  ❌ Cargo {cargo_id} não encontrado!")

if __name__ == "__main__":
    gerenciar_rapido() 