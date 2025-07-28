#!/usr/bin/env python
"""
Script para adicionar permissões de teste para os novos módulos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, PermissaoFuncao

def adicionar_permissoes_teste():
    """Adiciona permissões de teste para os novos módulos"""
    
    print("🔧 ADICIONANDO PERMISSÕES DE TESTE")
    print("=" * 60)
    
    # Buscar o cargo de teste
    cargo = CargoFuncao.objects.filter(nome__icontains='teste').first()
    if not cargo:
        print("❌ Cargo de teste não encontrado")
        return
    
    print(f"✅ Cargo encontrado: {cargo.nome}")
    
    # Novos módulos para adicionar permissões
    novos_modulos = [
        'ALMANAQUES',
        'CALENDARIOS', 
        'NOTIFICACOES',
        'MODELOS_ATA',
        'CARGOS_COMISSAO',
        'QUADROS_FIXACAO',
        'ASSINATURAS',
        'ESTATISTICAS',
        'EXPORTACAO',
        'IMPORTACAO',
        'BACKUP',
        'AUDITORIA',
        'DASHBOARD',
        'BUSCA',
        'AJAX',
        'API',
        'SESSAO',
        'FUNCAO',
        'PERFIL',
        'SISTEMA'
    ]
    
    # Tipos de acesso para adicionar
    acessos = ['VISUALIZAR', 'CRIAR', 'EDITAR']
    
    # Contar permissões existentes
    permissoes_existentes = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
    print(f"📊 Permissões existentes: {permissoes_existentes}")
    
    # Adicionar permissões para novos módulos
    permissoes_criadas = 0
    for modulo in novos_modulos:
        for acesso in acessos:
            # Verificar se já existe
            permissao_existente = PermissaoFuncao.objects.filter(
                cargo_funcao=cargo,
                modulo=modulo,
                acesso=acesso
            ).first()
            
            if not permissao_existente:
                permissao = PermissaoFuncao.objects.create(
                    cargo_funcao=cargo,
                    modulo=modulo,
                    acesso=acesso,
                    ativo=True
                )
                permissoes_criadas += 1
                print(f"   ✅ Criada permissão: {modulo} - {acesso}")
    
    # Contar permissões finais
    permissoes_finais = PermissaoFuncao.objects.filter(cargo_funcao=cargo).count()
    
    print("=" * 60)
    print(f"📊 Permissões criadas: {permissoes_criadas}")
    print(f"📊 Total de permissões: {permissoes_finais}")
    print("🎮 Agora acesse /militares/cargos/1/ para ver os novos módulos!")

if __name__ == "__main__":
    adicionar_permissoes_teste() 