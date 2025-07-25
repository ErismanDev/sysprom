#!/usr/bin/env python
"""
Script final para corrigir os caracteres problemáticos restantes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, CargoFuncao, UsuarioFuncao
from django.db import transaction

def corrigir_caracteres_finais():
    """Corrige os caracteres problemáticos finais"""
    print("🔧 Corrigindo caracteres problemáticos finais...")
    print("=" * 60)
    
    # Mapeamento específico dos caracteres problemáticos encontrados
    correcoes_cargos = {
        'FunçÒo padrÒo para administradores do sistema': 'Função padrão para administradores do sistema',
        'Membro padrÒo de comissÒo de promoções': 'Membro padrão de comissão de promoções',
        'Presidente da ComissÒo de PromoçÒo de Praças': 'Presidente da Comissão de Promoção de Praças',
        'Responsável pela gestÒo de promoções': 'Responsável pela gestão de promoções',
        'Membro Nato da ComissÒo de PromoçÒo de Praças': 'Membro Nato da Comissão de Promoção de Praças',
        'Membro Efetivo da ComissÒo de PromoçÒo de Praças': 'Membro Efetivo da Comissão de Promoção de Praças',
        'Secretário da ComissÒo de PromoçÒo de Praças': 'Secretário da Comissão de Promoção de Praças',
        'Suplente da ComissÒo de PromoçÒo de Praças': 'Suplente da Comissão de Promoção de Praças',
        'Presidente da ComissÒo de PromoçÒo de Oficiais': 'Presidente da Comissão de Promoção de Oficiais',
        'Membro Nato da ComissÒo de PromoçÒo de Oficiais': 'Membro Nato da Comissão de Promoção de Oficiais',
        'Membro Efetivo da ComissÒo de PromoçÒo de Oficiais': 'Membro Efetivo da Comissão de Promoção de Oficiais',
        'Secretário da ComissÒo de PromoçÒo de Oficiais': 'Secretário da Comissão de Promoção de Oficiais',
        'Suplente da ComissÒo de PromoçÒo de Oficiais': 'Suplente da Comissão de Promoção de Oficiais',
        'Operador com acesso limitado': 'Operador com acesso limitado',
        'Acesso apenas para consulta': 'Acesso apenas para consulta',
        'Usuário com perfil administrativo geral': 'Usuário com perfil administrativo geral',
        'Diretor de Gestão de Pessoas': 'Diretor de Gestão de Pessoas',
        'Chefe da Seção de Pessoal': 'Chefe da Seção de Pessoal',
        'Chefe da Seção de Promoções': 'Chefe da Seção de Promoções',
        'Membro de Comissão': 'Membro de Comissão',
        'Gestor de Promoções': 'Gestor de Promoções',
        'Secretário da CPO': 'Secretário da CPO',
        'Secretário da CPP': 'Secretário da CPP',
        'Presidente da CPO': 'Presidente da CPO',
        'Presidente da CPP': 'Presidente da CPP'
    }
    
    # Corrigir cargos
    cargos_corrigidos = 0
    cargos = CargoFuncao.objects.all()
    
    for cargo in cargos:
        corrigido = False
        
        # Corrigir nome
        if cargo.nome in correcoes_cargos:
            cargo.nome = correcoes_cargos[cargo.nome]
            corrigido = True
        
        # Corrigir descrição
        if cargo.descricao in correcoes_cargos:
            cargo.descricao = correcoes_cargos[cargo.descricao]
            corrigido = True
        
        if corrigido:
            cargo.save()
            cargos_corrigidos += 1
            print(f"   ✅ Corrigido: {cargo.nome}")
    
    print(f"\n📊 Cargos corrigidos: {cargos_corrigidos}")
    
    # Corrigir usuários específicos
    usuarios_corrigidos = 0
    
    # Corrigir usuário com "Usuário" problemático
    try:
        usuario_problematico = User.objects.get(id=1031)
        if usuario_problematico.first_name == 'Usuário':
            usuario_problematico.first_name = 'Usuário'
            usuario_problematico.save()
            usuarios_corrigidos += 1
            print(f"   ✅ Usuário corrigido: {usuario_problematico.username}")
    except User.DoesNotExist:
        pass
    
    # Corrigir usuário com "José" problemático
    try:
        usuario_jose = User.objects.get(id=2020)
        if 'José' in usuario_jose.first_name:
            usuario_jose.first_name = 'José'
            usuario_jose.save()
            usuarios_corrigidos += 1
            print(f"   ✅ Usuário corrigido: {usuario_jose.username}")
    except User.DoesNotExist:
        pass
    
    # Corrigir usuário com "Usuário" no last_name
    try:
        usuario_lastname = User.objects.get(id=17)
        if 'Usuário' in usuario_lastname.last_name:
            usuario_lastname.last_name = 'Usuário'
            usuario_lastname.save()
            usuarios_corrigidos += 1
            print(f"   ✅ Usuário corrigido: {usuario_lastname.username}")
    except User.DoesNotExist:
        pass
    
    print(f"\n📊 Usuários corrigidos: {usuarios_corrigidos}")
    
    return cargos_corrigidos + usuarios_corrigidos

def main():
    """Função principal"""
    print("🚀 Corrigindo caracteres problemáticos finais...")
    print("=" * 60)
    
    with transaction.atomic():
        total_corrigidos = corrigir_caracteres_finais()
        
        print("\n" + "=" * 60)
        print(f"📊 TOTAL DE CORREÇÕES: {total_corrigidos}")
        
        if total_corrigidos > 0:
            print("✅ Correções aplicadas com sucesso!")
        else:
            print("✅ Nenhuma correção necessária!")
    
    # Verificação final
    print("\n🔍 Executando verificação final...")
    os.system("python verificar_encoding_sistema.py")

if __name__ == '__main__':
    main() 