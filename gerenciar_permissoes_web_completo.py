#!/usr/bin/env python
"""
Script completo para gerenciar permissões via web
"""
import os
import sys
import django
import requests
import time
from urllib.parse import urljoin

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao

class GerenciadorPermissoesWeb:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        
    def fazer_login(self, username="admin", password="admin"):
        """Faz login no sistema"""
        print("🔐 Fazendo login...")
        
        # 1. Acessar página de login
        login_url = f"{self.base_url}/login/"
        response = self.session.get(login_url)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página de login: {response.status_code}")
            return False
        
        # 2. Extrair CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input:
            print("❌ CSRF token não encontrado na página de login")
            return False
        
        self.csrf_token = csrf_input['value']
        
        # 3. Enviar dados de login
        login_data = {
            'csrfmiddlewaretoken': self.csrf_token,
            'username': username,
            'password': password,
        }
        
        headers = {
            'Referer': login_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        response = self.session.post(login_url, data=login_data, headers=headers)
        
        if response.status_code == 302 and 'militares' in response.headers.get('Location', ''):
            print("✅ Login realizado com sucesso!")
            return True
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return False
    
    def navegar_para_permissoes(self):
        """Navega para a página de gerenciamento de permissões"""
        print("🧭 Navegando para página de permissões...")
        
        permissoes_url = f"{self.base_url}/militares/permissoes/"
        response = self.session.get(permissoes_url)
        
        if response.status_code == 200:
            print("✅ Página de permissões acessada!")
            return True
        else:
            print(f"❌ Erro ao acessar página de permissões: {response.status_code}")
            return False
    
    def acessar_cargo(self, cargo_id):
        """Acessa a página de detalhes de um cargo"""
        print(f"👤 Acessando cargo ID {cargo_id}...")
        
        cargo_url = f"{self.base_url}/militares/permissoes/cargo/{cargo_id}/"
        response = self.session.get(cargo_url)
        
        if response.status_code == 200:
            print("✅ Página do cargo acessada!")
            return True
        else:
            print(f"❌ Erro ao acessar cargo: {response.status_code}")
            return False
    
    def editar_permissoes_cargo(self, cargo_id, permissoes=None):
        """Edita as permissões de um cargo"""
        print(f"✏️ Editando permissões do cargo {cargo_id}...")
        
        # 1. Acessar página de edição
        edit_url = f"{self.base_url}/militares/permissoes/cargo/{cargo_id}/editar/"
        response = self.session.get(edit_url)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página de edição: {response.status_code}")
            return False
        
        # 2. Extrair CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input:
            print("❌ CSRF token não encontrado")
            return False
        
        self.csrf_token = csrf_input['value']
        
        # 3. Preparar permissões
        if permissoes is None:
            # Usar todas as permissões possíveis
            modulos = [choice[0] for choice in PermissaoFuncao.MODULOS_CHOICES]
            acessos = [choice[0] for choice in PermissaoFuncao.ACESSOS_CHOICES]
            
            permissoes = []
            for modulo in modulos:
                for acesso in acessos:
                    permissoes.append(f"{modulo}:{acesso}")
        
        print(f"   Total de permissões: {len(permissoes)}")
        
        # 4. Preparar dados do formulário
        form_data = {
            'csrfmiddlewaretoken': self.csrf_token,
        }
        
        # Adicionar permissões ao formulário
        for permissao in permissoes:
            form_data['permissoes'] = permissao
        
        # 5. Enviar formulário
        headers = {
            'Referer': edit_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        response = self.session.post(edit_url, data=form_data, headers=headers)
        
        if response.status_code in [200, 302]:
            print("✅ Permissões atualizadas com sucesso!")
            return True
        else:
            print(f"❌ Erro ao atualizar permissões: {response.status_code}")
            return False
    
    def aplicar_perfil_cargo(self, cargo_id, perfil_id):
        """Aplica um perfil de acesso a um cargo"""
        print(f"📋 Aplicando perfil {perfil_id} ao cargo {cargo_id}...")
        
        # 1. Acessar página de aplicação de perfil
        perfil_url = f"{self.base_url}/militares/permissoes/cargo/{cargo_id}/aplicar-perfil/{perfil_id}/"
        response = self.session.get(perfil_url)
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página de perfil: {response.status_code}")
            return False
        
        # 2. Extrair CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if not csrf_input:
            print("❌ CSRF token não encontrado")
            return False
        
        self.csrf_token = csrf_input['value']
        
        # 3. Confirmar aplicação
        form_data = {
            'csrfmiddlewaretoken': self.csrf_token,
        }
        
        headers = {
            'Referer': perfil_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        response = self.session.post(perfil_url, data=form_data, headers=headers)
        
        if response.status_code in [200, 302]:
            print("✅ Perfil aplicado com sucesso!")
            return True
        else:
            print(f"❌ Erro ao aplicar perfil: {response.status_code}")
            return False
    
    def listar_cargos(self):
        """Lista todos os cargos disponíveis"""
        print("📋 Listando cargos disponíveis...")
        
        cargos = CargoFuncao.objects.all().order_by('id')
        
        print("\nCargos disponíveis:")
        print("-" * 50)
        for cargo in cargos:
            perms_count = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
            print(f"ID {cargo.id:2d}: {cargo.nome:<30} ({perms_count:3d} permissões)")
        
        return cargos
    
    def gerenciar_todos_cargos(self, aplicar_todas_permissoes=True):
        """Gerencia permissões de todos os cargos"""
        print("🎯 Gerenciando todos os cargos...")
        
        cargos = self.listar_cargos()
        
        for cargo in cargos:
            print(f"\n--- Gerenciando Cargo: {cargo.nome} (ID: {cargo.id}) ---")
            
            # Acessar cargo
            if not self.acessar_cargo(cargo.id):
                continue
            
            # Editar permissões
            if aplicar_todas_permissoes:
                self.editar_permissoes_cargo(cargo.id)
            
            time.sleep(1)  # Pausa entre operações
        
        print("\n✅ Gerenciamento de todos os cargos concluído!")

def main():
    """Função principal"""
    print("🌐 GERENCIADOR DE PERMISSÕES VIA WEB")
    print("=" * 50)
    
    # Criar gerenciador
    gerenciador = GerenciadorPermissoesWeb()
    
    # Fazer login
    if not gerenciador.fazer_login():
        print("❌ Falha no login. Verifique as credenciais.")
        return
    
    # Navegar para permissões
    if not gerenciador.navegar_para_permissoes():
        print("❌ Falha ao navegar para permissões.")
        return
    
    # Menu de opções
    while True:
        print("\n" + "=" * 50)
        print("📋 MENU DE OPÇÕES:")
        print("1. Listar cargos")
        print("2. Gerenciar cargo específico")
        print("3. Gerenciar todos os cargos")
        print("4. Aplicar perfil a cargo")
        print("5. Sair")
        print("=" * 50)
        
        opcao = input("Escolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            gerenciador.listar_cargos()
            
        elif opcao == "2":
            cargo_id = input("Digite o ID do cargo: ").strip()
            try:
                cargo_id = int(cargo_id)
                gerenciador.acessar_cargo(cargo_id)
                gerenciador.editar_permissoes_cargo(cargo_id)
            except ValueError:
                print("❌ ID inválido!")
                
        elif opcao == "3":
            aplicar = input("Aplicar todas as permissões? (s/n): ").strip().lower()
            gerenciador.gerenciar_todos_cargos(aplicar == 's')
            
        elif opcao == "4":
            cargo_id = input("Digite o ID do cargo: ").strip()
            perfil_id = input("Digite o ID do perfil: ").strip()
            try:
                cargo_id = int(cargo_id)
                perfil_id = int(perfil_id)
                gerenciador.aplicar_perfil_cargo(cargo_id, perfil_id)
            except ValueError:
                print("❌ ID inválido!")
                
        elif opcao == "5":
            print("👋 Saindo...")
            break
            
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main() 