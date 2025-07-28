#!/usr/bin/env python
"""
Script para implementar troca automática de função
Quando um usuário receber uma nova função, a função antiga de "Usuário" será automaticamente desativada
"""

import os
import sys
import django

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def implementar_troca_automatica_funcao():
    """Implementa a funcionalidade de troca automática de função"""
    
    print("🔄 IMPLEMENTANDO TROCA AUTOMÁTICA DE FUNÇÃO")
    print("=" * 60)
    
    # 1. Verificar se existe o cargo "Usuário"
    try:
        cargo_usuario = CargoFuncao.objects.get(nome='Usuário')
        print(f"✅ Cargo 'Usuário' encontrado: ID {cargo_usuario.id}")
    except CargoFuncao.DoesNotExist:
        print("❌ Cargo 'Usuário' não encontrado. Criando...")
        cargo_usuario = CargoFuncao.objects.create(
            nome='Usuário',
            descricao='Função padrão para usuários do sistema',
            ativo=True,
            ordem=999
        )
        print(f"✅ Cargo 'Usuário' criado: ID {cargo_usuario.id}")
    
    # 2. Verificar usuários com função "Usuário"
    usuarios_com_funcao_padrao = UsuarioFuncao.objects.filter(
        cargo_funcao=cargo_usuario,
        status='ATIVO'
    ).select_related('usuario')
    
    print(f"\n📋 USUÁRIOS COM FUNÇÃO 'USUÁRIO': {usuarios_com_funcao_padrao.count()}")
    
    for uf in usuarios_com_funcao_padrao:
        print(f"  - {uf.usuario.username}")
    
    # 3. Verificar usuários que têm outras funções além de "Usuário"
    usuarios_com_multiplas_funcoes = []
    
    for uf in usuarios_com_funcao_padrao:
        outras_funcoes = UsuarioFuncao.objects.filter(
            usuario=uf.usuario,
            status='ATIVO'
        ).exclude(cargo_funcao=cargo_usuario)
        
        if outras_funcoes.exists():
            usuarios_com_multiplas_funcoes.append({
                'usuario': uf.usuario,
                'funcao_usuario': uf,
                'outras_funcoes': outras_funcoes
            })
    
    print(f"\n🔄 USUÁRIOS COM MÚLTIPLAS FUNÇÕES: {len(usuarios_com_multiplas_funcoes)}")
    
    # 4. Aplicar a lógica de troca automática
    with transaction.atomic():
        for item in usuarios_com_multiplas_funcoes:
            usuario = item['usuario']
            funcao_usuario = item['funcao_usuario']
            outras_funcoes = item['outras_funcoes']
            
            print(f"\n🔄 Processando usuário: {usuario.username}")
            print(f"   Função 'Usuário': {funcao_usuario.id}")
            print(f"   Outras funções ativas: {outras_funcoes.count()}")
            
            # Desativar a função "Usuário"
            funcao_usuario.status = 'INATIVO'
            funcao_usuario.data_fim = django.utils.timezone.now().date()
            funcao_usuario.observacoes = f"Desativada automaticamente - usuário possui outras funções: {', '.join([f.nome for f in outras_funcoes])}"
            funcao_usuario.save()
            
            print(f"   ✅ Função 'Usuário' desativada")
    
    print(f"\n✅ Processo concluído!")
    print(f"   - {len(usuarios_com_multiplas_funcoes)} usuários tiveram função 'Usuário' desativada")

def criar_signal_troca_automatica():
    """Cria um signal para aplicar a troca automática sempre que uma nova função for criada"""
    
    print(f"\n🔧 CRIANDO SIGNAL PARA TROCA AUTOMÁTICA")
    print("=" * 60)
    
    # Criar arquivo de signals específico
    signal_content = '''#!/usr/bin/env python
"""
Signal para troca automática de função
Quando um usuário receber uma nova função, a função antiga de "Usuário" será automaticamente desativada
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UsuarioFuncao, CargoFuncao

@receiver(post_save, sender=UsuarioFuncao)
def trocar_funcao_automaticamente(sender, instance, created, **kwargs):
    """
    Signal que desativa automaticamente a função "Usuário" quando o usuário receber outras funções
    """
    if not created:  # Só executar quando uma nova função for criada
        return
    
    # Verificar se a nova função não é "Usuário"
    if instance.cargo_funcao.nome == 'Usuário':
        return
    
    # Verificar se o usuário tem função "Usuário" ativa
    try:
        cargo_usuario = CargoFuncao.objects.get(nome='Usuário')
        funcao_usuario = UsuarioFuncao.objects.filter(
            usuario=instance.usuario,
            cargo_funcao=cargo_usuario,
            status='ATIVO'
        ).first()
        
        if funcao_usuario:
            # Desativar a função "Usuário"
            funcao_usuario.status = 'INATIVO'
            funcao_usuario.data_fim = timezone.now().date()
            funcao_usuario.observacoes = f"Desativada automaticamente - usuário recebeu função: {instance.cargo_funcao.nome}"
            funcao_usuario.save()
            
            print(f"🔄 Função 'Usuário' desativada automaticamente para {instance.usuario.username}")
    
    except CargoFuncao.DoesNotExist:
        # Se não existe cargo "Usuário", não fazer nada
        pass

@receiver(post_save, sender=UsuarioFuncao)
def reativar_funcao_usuario_quando_necessario(sender, instance, created, **kwargs):
    """
    Signal que reativa a função "Usuário" quando o usuário não tem mais outras funções ativas
    """
    if created:  # Só executar quando uma função for criada
        return
    
    # Verificar se a função foi desativada
    if instance.status == 'INATIVO':
        # Verificar se o usuário ainda tem outras funções ativas
        outras_funcoes_ativas = UsuarioFuncao.objects.filter(
            usuario=instance.usuario,
            status='ATIVO'
        ).exists()
        
        if not outras_funcoes_ativas:
            # Se não tem outras funções ativas, reativar função "Usuário"
            try:
                cargo_usuario = CargoFuncao.objects.get(nome='Usuário')
                funcao_usuario, created = UsuarioFuncao.objects.get_or_create(
                    usuario=instance.usuario,
                    cargo_funcao=cargo_usuario,
                    defaults={
                        'tipo_funcao': 'OUTROS',
                        'status': 'ATIVO',
                        'data_inicio': timezone.now().date(),
                        'observacoes': 'Reativada automaticamente - usuário não possui outras funções'
                    }
                )
                
                if not created:
                    # Se já existia, reativar
                    funcao_usuario.status = 'ATIVO'
                    funcao_usuario.data_fim = None
                    funcao_usuario.observacoes = 'Reativada automaticamente - usuário não possui outras funções'
                    funcao_usuario.save()
                
                print(f"🔄 Função 'Usuário' reativada automaticamente para {instance.usuario.username}")
            
            except CargoFuncao.DoesNotExist:
                # Se não existe cargo "Usuário", não fazer nada
                pass
'''
    
    # Salvar o arquivo de signals
    with open('militares/signals_troca_funcao.py', 'w', encoding='utf-8') as f:
        f.write(signal_content)
    
    print("✅ Arquivo signals_troca_funcao.py criado")
    
    # Atualizar o arquivo __init__.py para importar os signals
    init_content = '''# Importar signals para troca automática de função
from . import signals_troca_funcao
'''
    
    with open('militares/__init__.py', 'a', encoding='utf-8') as f:
        f.write(init_content)
    
    print("✅ Signals importados no __init__.py")

def testar_troca_automatica():
    """Testa a funcionalidade de troca automática"""
    
    print(f"\n🧪 TESTANDO TROCA AUTOMÁTICA")
    print("=" * 60)
    
    # Simular criação de uma nova função para um usuário
    try:
        # Pegar um usuário que tem função "Usuário"
        cargo_usuario = CargoFuncao.objects.get(nome='Usuário')
        funcao_usuario = UsuarioFuncao.objects.filter(
            cargo_funcao=cargo_usuario,
            status='ATIVO'
        ).first()
        
        if funcao_usuario:
            usuario = funcao_usuario.usuario
            print(f"Testando com usuário: {usuario.username}")
            
            # Verificar se tem outras funções
            outras_funcoes = UsuarioFuncao.objects.filter(
                usuario=usuario,
                status='ATIVO'
            ).exclude(cargo_funcao=cargo_usuario)
            
            if outras_funcoes.exists():
                print(f"Usuário já tem outras funções: {[f.cargo_funcao.nome for f in outras_funcoes]}")
                print("Aplicando lógica de troca automática...")
                
                # Desativar função "Usuário"
                funcao_usuario.status = 'INATIVO'
                funcao_usuario.data_fim = django.utils.timezone.now().date()
                funcao_usuario.observacoes = "Teste - função desativada automaticamente"
                funcao_usuario.save()
                
                print("✅ Função 'Usuário' desativada no teste")
            else:
                print("Usuário não tem outras funções. Criando uma função de teste...")
                
                # Criar uma função de teste
                cargo_teste = CargoFuncao.objects.filter(nome__icontains='Administrador').first()
                if cargo_teste:
                    nova_funcao = UsuarioFuncao.objects.create(
                        usuario=usuario,
                        cargo_funcao=cargo_teste,
                        tipo_funcao='ADMINISTRATIVO',
                        status='ATIVO',
                        data_inicio=django.utils.timezone.now().date(),
                        observacoes='Função criada para teste de troca automática'
                    )
                    
                    print(f"✅ Nova função criada: {nova_funcao.cargo_funcao.nome}")
                    print("Agora a função 'Usuário' deve ser desativada automaticamente")
                else:
                    print("❌ Não foi possível encontrar um cargo para teste")
        else:
            print("❌ Não foi possível encontrar um usuário com função 'Usuário' para teste")
    
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == '__main__':
    print("Escolha uma opção:")
    print("1. Implementar troca automática de função")
    print("2. Criar signal para troca automática")
    print("3. Testar troca automática")
    print("4. Executar tudo")
    
    opcao = input("Opção (1-4): ").strip()
    
    if opcao == "1":
        implementar_troca_automatica_funcao()
    elif opcao == "2":
        criar_signal_troca_automatica()
    elif opcao == "3":
        testar_troca_automatica()
    elif opcao == "4":
        implementar_troca_automatica_funcao()
        criar_signal_troca_automatica()
        testar_troca_automatica()
    else:
        print("❌ Opção inválida!") 